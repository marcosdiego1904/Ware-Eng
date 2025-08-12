"""
Deployment Health Check System
Comprehensive health monitoring for production deployment with automated rollback triggers
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
import traceback
import threading
from enum import Enum
import requests
from urllib.parse import urljoin

from sqlalchemy import text
from database import db
from monitoring import log_error, track_performance, monitoring_buffer
from migration_debugger import migration_debugger
from debug_test_framework import debug_test_framework

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class DeploymentPhase(Enum):
    PRE_DEPLOYMENT = "pre_deployment"
    DEPLOYMENT = "deployment"  
    POST_DEPLOYMENT = "post_deployment"
    MONITORING = "monitoring"
    ROLLBACK = "rollback"

@dataclass
class HealthCheckResult:
    """Health check result"""
    check_name: str
    status: HealthStatus
    message: str
    timestamp: str
    duration_ms: float
    details: Optional[Dict[str, Any]] = None
    critical: bool = False

@dataclass 
class DeploymentMetric:
    """Deployment health metric"""
    metric_name: str
    current_value: float
    baseline_value: Optional[float]
    threshold: float
    status: HealthStatus
    timestamp: str

@dataclass
class RollbackTrigger:
    """Rollback trigger condition"""
    name: str
    condition: str
    threshold: float
    triggered: bool
    trigger_time: Optional[str] = None
    reason: Optional[str] = None

class DeploymentHealthChecker:
    """Comprehensive deployment health monitoring"""
    
    def __init__(self):
        self.health_checks: List[Callable] = []
        self.rollback_triggers: List[RollbackTrigger] = []
        self.baseline_metrics: Dict[str, float] = {}
        self.current_phase = DeploymentPhase.MONITORING
        self.deployment_start_time: Optional[datetime] = None
        self.health_history: List[HealthCheckResult] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Configuration
        self.check_interval = int(os.environ.get('HEALTH_CHECK_INTERVAL', '30'))  # seconds
        self.rollback_enabled = os.environ.get('AUTO_ROLLBACK_ENABLED', 'false').lower() == 'true'
        self.frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        self.api_base_url = os.environ.get('API_BASE_URL', 'http://localhost:5000')
        
        # Setup default checks and triggers
        self._setup_default_checks()
        self._setup_default_rollback_triggers()
    
    def _setup_default_checks(self):
        """Setup default health checks"""
        self.health_checks = [
            self.check_database_connectivity,
            self.check_api_endpoints,
            self.check_warehouse_operations,
            self.check_frontend_connectivity,
            self.check_system_resources,
            self.check_error_rates,
            self.check_response_times
        ]
    
    def _setup_default_rollback_triggers(self):
        """Setup default rollback triggers"""
        self.rollback_triggers = [
            RollbackTrigger(
                name="high_error_rate",
                condition="error_rate > threshold",
                threshold=0.1,  # 10% error rate
                triggered=False
            ),
            RollbackTrigger(
                name="database_connectivity_failure",
                condition="database_failures > threshold",
                threshold=3,  # 3 consecutive failures
                triggered=False
            ),
            RollbackTrigger(
                name="slow_response_times",
                condition="avg_response_time > threshold",
                threshold=5000,  # 5 seconds
                triggered=False
            ),
            RollbackTrigger(
                name="memory_exhaustion",
                condition="memory_usage > threshold",
                threshold=95,  # 95% memory usage
                triggered=False
            ),
            RollbackTrigger(
                name="warehouse_operation_failures",
                condition="warehouse_failure_rate > threshold",
                threshold=0.5,  # 50% failure rate
                triggered=False
            )
        ]
    
    def start_deployment_monitoring(self, phase: DeploymentPhase = DeploymentPhase.DEPLOYMENT):
        """Start deployment health monitoring"""
        self.current_phase = phase
        self.deployment_start_time = datetime.utcnow()
        self.is_monitoring = True
        
        logger.info(f"Starting deployment health monitoring - Phase: {phase.value}")
        
        # Establish baseline metrics
        if phase == DeploymentPhase.PRE_DEPLOYMENT:
            self._establish_baseline_metrics()
        
        # Start monitoring thread
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_deployment_monitoring(self):
        """Stop deployment health monitoring"""
        self.is_monitoring = False
        self.current_phase = DeploymentPhase.MONITORING
        logger.info("Stopped deployment health monitoring")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        consecutive_failures = 0
        
        while self.is_monitoring:
            try:
                # Run all health checks
                results = self._run_all_health_checks()
                
                # Process results
                healthy_checks = len([r for r in results if r.status == HealthStatus.HEALTHY])
                total_checks = len(results)
                health_percentage = (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
                
                # Check for rollback triggers
                if self.rollback_enabled and self.current_phase in [DeploymentPhase.DEPLOYMENT, DeploymentPhase.POST_DEPLOYMENT]:
                    self._check_rollback_triggers(results)
                
                # Log health status
                overall_status = self._determine_overall_status(results)
                logger.info(f"Health check complete - Status: {overall_status.value}, Healthy: {healthy_checks}/{total_checks}")
                
                # Handle consecutive failures
                if overall_status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                    consecutive_failures += 1
                    if consecutive_failures >= 3:
                        logger.error(f"Multiple consecutive health check failures: {consecutive_failures}")
                        if self.rollback_enabled:
                            self._trigger_emergency_rollback("consecutive_health_failures")
                else:
                    consecutive_failures = 0
                
                # Store results
                self.health_history.extend(results)
                
                # Keep only last 1000 results
                if len(self.health_history) > 1000:
                    self.health_history = self.health_history[-1000:]
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                consecutive_failures += 1
                time.sleep(self.check_interval)
    
    def _run_all_health_checks(self) -> List[HealthCheckResult]:
        """Run all registered health checks"""
        results = []
        
        for check_func in self.health_checks:
            start_time = time.time()
            try:
                result = check_func()
                if isinstance(result, HealthCheckResult):
                    results.append(result)
                else:
                    # Convert dict result to HealthCheckResult
                    status = HealthStatus.HEALTHY if result.get('healthy', False) else HealthStatus.UNHEALTHY
                    results.append(HealthCheckResult(
                        check_name=check_func.__name__,
                        status=status,
                        message=result.get('message', 'Check completed'),
                        timestamp=datetime.utcnow().isoformat(),
                        duration_ms=(time.time() - start_time) * 1000,
                        details=result
                    ))
            except Exception as e:
                results.append(HealthCheckResult(
                    check_name=check_func.__name__,
                    status=HealthStatus.CRITICAL,
                    message=f"Check failed: {str(e)}",
                    timestamp=datetime.utcnow().isoformat(),
                    duration_ms=(time.time() - start_time) * 1000,
                    critical=True
                ))
                log_error(e, {'health_check': check_func.__name__})
        
        return results
    
    def _determine_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """Determine overall health status"""
        if not results:
            return HealthStatus.UNHEALTHY
        
        critical_failures = len([r for r in results if r.status == HealthStatus.CRITICAL])
        unhealthy_checks = len([r for r in results if r.status == HealthStatus.UNHEALTHY])
        degraded_checks = len([r for r in results if r.status == HealthStatus.DEGRADED])
        
        if critical_failures > 0:
            return HealthStatus.CRITICAL
        elif unhealthy_checks > len(results) * 0.3:  # > 30% unhealthy
            return HealthStatus.UNHEALTHY
        elif degraded_checks > len(results) * 0.5:  # > 50% degraded
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def _establish_baseline_metrics(self):
        """Establish baseline performance metrics"""
        logger.info("Establishing baseline metrics...")
        
        try:
            # Database query performance
            start_time = time.time()
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_response_time = (time.time() - start_time) * 1000
            self.baseline_metrics['database_response_time'] = db_response_time
            
            # API response times
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_base_url}/api/v1/health", timeout=10)
                if response.status_code == 200:
                    api_response_time = (time.time() - start_time) * 1000
                    self.baseline_metrics['api_response_time'] = api_response_time
            except Exception:
                pass
            
            logger.info(f"Baseline metrics established: {self.baseline_metrics}")
            
        except Exception as e:
            logger.error(f"Failed to establish baseline metrics: {e}")
    
    # Health Check Functions
    
    def check_database_connectivity(self) -> HealthCheckResult:
        """Check database connectivity and performance"""
        start_time = time.time()
        
        try:
            with db.engine.connect() as conn:
                # Test basic connectivity
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                
                # Test warehouse tables
                tables_to_check = ['location', 'warehouse_config', 'rule', 'rule_category']
                for table in tables_to_check:
                    conn.execute(text(f"SELECT COUNT(*) FROM {table} LIMIT 1"))
            
            duration = (time.time() - start_time) * 1000
            
            # Compare with baseline
            status = HealthStatus.HEALTHY
            if 'database_response_time' in self.baseline_metrics:
                if duration > self.baseline_metrics['database_response_time'] * 3:
                    status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                check_name="database_connectivity",
                status=status,
                message=f"Database responsive ({duration:.1f}ms)",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=duration,
                details={'response_time_ms': duration}
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="database_connectivity",
                status=HealthStatus.CRITICAL,
                message=f"Database connection failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000,
                critical=True
            )
    
    def check_api_endpoints(self) -> HealthCheckResult:
        """Check critical API endpoints"""
        start_time = time.time()
        
        endpoints_to_check = [
            '/api/v1/health',
            '/api/v1/warehouse/locations',
            '/api/v1/template/public'
        ]
        
        failed_endpoints = []
        slow_endpoints = []
        total_response_time = 0
        
        for endpoint in endpoints_to_check:
            try:
                url = urljoin(self.api_base_url, endpoint)
                response = requests.get(url, timeout=10)
                
                if response.status_code >= 400:
                    failed_endpoints.append(f"{endpoint} ({response.status_code})")
                
                # Check response time
                if hasattr(response, 'elapsed'):
                    endpoint_time = response.elapsed.total_seconds() * 1000
                    total_response_time += endpoint_time
                    
                    if endpoint_time > 2000:  # > 2 seconds
                        slow_endpoints.append(f"{endpoint} ({endpoint_time:.0f}ms)")
                
            except Exception as e:
                failed_endpoints.append(f"{endpoint} (error: {str(e)})")
        
        duration = (time.time() - start_time) * 1000
        avg_response_time = total_response_time / len(endpoints_to_check) if endpoints_to_check else 0
        
        if failed_endpoints:
            status = HealthStatus.CRITICAL if len(failed_endpoints) > len(endpoints_to_check) / 2 else HealthStatus.UNHEALTHY
            message = f"Failed endpoints: {', '.join(failed_endpoints)}"
        elif slow_endpoints:
            status = HealthStatus.DEGRADED
            message = f"Slow endpoints: {', '.join(slow_endpoints)}"
        else:
            status = HealthStatus.HEALTHY
            message = f"All API endpoints responsive (avg: {avg_response_time:.1f}ms)"
        
        return HealthCheckResult(
            check_name="api_endpoints",
            status=status,
            message=message,
            timestamp=datetime.utcnow().isoformat(),
            duration_ms=duration,
            details={
                'failed_endpoints': failed_endpoints,
                'slow_endpoints': slow_endpoints,
                'avg_response_time_ms': avg_response_time
            }
        )
    
    def check_warehouse_operations(self) -> HealthCheckResult:
        """Check warehouse-specific operations"""
        start_time = time.time()
        
        try:
            # Run a subset of warehouse tests
            test_results = debug_test_framework.run_all_tests(parallel=False)
            
            success_rate = test_results.get('success_rate', 0)
            failed_tests = test_results.get('failed', 0)
            
            if success_rate >= 90:
                status = HealthStatus.HEALTHY
                message = f"Warehouse operations healthy ({success_rate:.1f}% success rate)"
            elif success_rate >= 70:
                status = HealthStatus.DEGRADED  
                message = f"Warehouse operations degraded ({success_rate:.1f}% success rate)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Warehouse operations failing ({success_rate:.1f}% success rate)"
            
            return HealthCheckResult(
                check_name="warehouse_operations",
                status=status,
                message=message,
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000,
                details={
                    'success_rate': success_rate,
                    'failed_tests': failed_tests,
                    'test_results': test_results
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="warehouse_operations",
                status=HealthStatus.CRITICAL,
                message=f"Warehouse operations test failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000,
                critical=True
            )
    
    def check_frontend_connectivity(self) -> HealthCheckResult:
        """Check frontend connectivity"""
        start_time = time.time()
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            duration = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status = HealthStatus.HEALTHY
                message = f"Frontend accessible ({duration:.1f}ms)"
            else:
                status = HealthStatus.DEGRADED
                message = f"Frontend returned {response.status_code}"
            
            return HealthCheckResult(
                check_name="frontend_connectivity",
                status=status,
                message=message,
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=duration
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="frontend_connectivity",
                status=HealthStatus.DEGRADED,  # Not critical for backend operations
                message=f"Frontend connection failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def check_system_resources(self) -> HealthCheckResult:
        """Check system resource usage"""
        start_time = time.time()
        
        try:
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status based on usage
            issues = []
            status = HealthStatus.HEALTHY
            
            if cpu_percent > 90:
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
                status = HealthStatus.DEGRADED
            
            if memory.percent > 90:
                issues.append(f"High memory usage: {memory.percent:.1f}%")
                status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else HealthStatus.UNHEALTHY
            
            if disk.percent > 95:
                issues.append(f"Low disk space: {disk.percent:.1f}% used")
                status = HealthStatus.UNHEALTHY
            
            message = f"System resources OK (CPU: {cpu_percent:.1f}%, RAM: {memory.percent:.1f}%)"
            if issues:
                message = f"Resource issues: {', '.join(issues)}"
            
            return HealthCheckResult(
                check_name="system_resources",
                status=status,
                message=message,
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000,
                details={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                }
            )
            
        except ImportError:
            return HealthCheckResult(
                check_name="system_resources",
                status=HealthStatus.DEGRADED,
                message="psutil not available - cannot check system resources",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return HealthCheckResult(
                check_name="system_resources",
                status=HealthStatus.DEGRADED,
                message=f"Resource check failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def check_error_rates(self) -> HealthCheckResult:
        """Check application error rates"""
        start_time = time.time()
        
        try:
            # Get recent errors from monitoring buffer
            recent_errors = monitoring_buffer.get_recent_errors(limit=100)
            
            # Calculate error rate over last 10 minutes
            cutoff_time = datetime.utcnow() - timedelta(minutes=10)
            cutoff_str = cutoff_time.isoformat()
            
            recent_error_count = len([e for e in recent_errors if e.timestamp > cutoff_str])
            
            # Estimate request count (this would be better with actual metrics)
            estimated_requests = 100  # Placeholder
            error_rate = recent_error_count / estimated_requests if estimated_requests > 0 else 0
            
            if error_rate > 0.1:  # > 10%
                status = HealthStatus.UNHEALTHY
                message = f"High error rate: {error_rate * 100:.1f}%"
            elif error_rate > 0.05:  # > 5%
                status = HealthStatus.DEGRADED
                message = f"Elevated error rate: {error_rate * 100:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Error rate normal: {error_rate * 100:.1f}%"
            
            return HealthCheckResult(
                check_name="error_rates",
                status=status,
                message=message,
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000,
                details={
                    'error_rate': error_rate,
                    'recent_errors': recent_error_count,
                    'estimated_requests': estimated_requests
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="error_rates",
                status=HealthStatus.DEGRADED,
                message=f"Error rate check failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def check_response_times(self) -> HealthCheckResult:
        """Check API response times"""
        start_time = time.time()
        
        try:
            # Get recent performance metrics
            recent_metrics = monitoring_buffer.get_recent_performance(limit=50)
            
            if not recent_metrics:
                return HealthCheckResult(
                    check_name="response_times",
                    status=HealthStatus.DEGRADED,
                    message="No performance metrics available",
                    timestamp=datetime.utcnow().isoformat(),
                    duration_ms=(time.time() - start_time) * 1000
                )
            
            # Calculate average response time
            response_times = [m.value for m in recent_metrics if m.unit == 'ms']
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            if avg_response_time > 5000:  # > 5 seconds
                status = HealthStatus.UNHEALTHY
                message = f"Very slow response times: {avg_response_time:.0f}ms avg"
            elif avg_response_time > 2000:  # > 2 seconds
                status = HealthStatus.DEGRADED
                message = f"Slow response times: {avg_response_time:.0f}ms avg"
            else:
                status = HealthStatus.HEALTHY
                message = f"Response times normal: {avg_response_time:.0f}ms avg"
            
            return HealthCheckResult(
                check_name="response_times",
                status=status,
                message=message,
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000,
                details={
                    'avg_response_time_ms': avg_response_time,
                    'max_response_time_ms': max_response_time,
                    'metric_count': len(response_times)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="response_times",
                status=HealthStatus.DEGRADED,
                message=f"Response time check failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def _check_rollback_triggers(self, results: List[HealthCheckResult]):
        """Check if any rollback triggers should be activated"""
        for trigger in self.rollback_triggers:
            if trigger.triggered:
                continue
            
            should_trigger = False
            reason = ""
            
            # Check specific trigger conditions
            if trigger.name == "high_error_rate":
                error_check = next((r for r in results if r.check_name == "error_rates"), None)
                if error_check and error_check.details:
                    error_rate = error_check.details.get('error_rate', 0)
                    if error_rate > trigger.threshold:
                        should_trigger = True
                        reason = f"Error rate {error_rate * 100:.1f}% exceeds {trigger.threshold * 100:.1f}%"
            
            elif trigger.name == "database_connectivity_failure":
                db_check = next((r for r in results if r.check_name == "database_connectivity"), None)
                if db_check and db_check.status == HealthStatus.CRITICAL:
                    should_trigger = True
                    reason = "Database connectivity critical failure"
            
            elif trigger.name == "slow_response_times":
                response_check = next((r for r in results if r.check_name == "response_times"), None)
                if response_check and response_check.details:
                    avg_time = response_check.details.get('avg_response_time_ms', 0)
                    if avg_time > trigger.threshold:
                        should_trigger = True
                        reason = f"Average response time {avg_time:.0f}ms exceeds {trigger.threshold:.0f}ms"
            
            elif trigger.name == "warehouse_operation_failures":
                warehouse_check = next((r for r in results if r.check_name == "warehouse_operations"), None)
                if warehouse_check and warehouse_check.details:
                    success_rate = warehouse_check.details.get('success_rate', 100) / 100
                    failure_rate = 1 - success_rate
                    if failure_rate > trigger.threshold:
                        should_trigger = True
                        reason = f"Warehouse operation failure rate {failure_rate * 100:.1f}% exceeds {trigger.threshold * 100:.1f}%"
            
            if should_trigger:
                trigger.triggered = True
                trigger.trigger_time = datetime.utcnow().isoformat()
                trigger.reason = reason
                
                logger.critical(f"ROLLBACK TRIGGER ACTIVATED: {trigger.name} - {reason}")
                
                if self.rollback_enabled:
                    self._initiate_rollback(trigger)
    
    def _initiate_rollback(self, trigger: RollbackTrigger):
        """Initiate deployment rollback"""
        logger.critical(f"INITIATING DEPLOYMENT ROLLBACK due to trigger: {trigger.name}")
        
        self.current_phase = DeploymentPhase.ROLLBACK
        
        # Here you would integrate with your deployment system
        # For example, calling a webhook, updating a deployment config, etc.
        
        rollback_webhook = os.environ.get('ROLLBACK_WEBHOOK_URL')
        if rollback_webhook:
            try:
                rollback_data = {
                    'trigger': trigger.name,
                    'reason': trigger.reason,
                    'timestamp': trigger.trigger_time,
                    'health_status': 'critical'
                }
                
                response = requests.post(rollback_webhook, json=rollback_data, timeout=30)
                if response.status_code == 200:
                    logger.info("Rollback webhook called successfully")
                else:
                    logger.error(f"Rollback webhook failed: {response.status_code}")
            except Exception as e:
                logger.error(f"Failed to call rollback webhook: {e}")
    
    def _trigger_emergency_rollback(self, reason: str):
        """Trigger emergency rollback"""
        emergency_trigger = RollbackTrigger(
            name="emergency_rollback",
            condition="manual_trigger",
            threshold=0,
            triggered=True,
            trigger_time=datetime.utcnow().isoformat(),
            reason=reason
        )
        
        self._initiate_rollback(emergency_trigger)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        if not self.health_history:
            return {
                'status': 'unknown',
                'message': 'No health checks performed yet',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        recent_results = self.health_history[-len(self.health_checks):]
        overall_status = self._determine_overall_status(recent_results)
        
        triggered_rollbacks = [t for t in self.rollback_triggers if t.triggered]
        
        return {
            'overall_status': overall_status.value,
            'deployment_phase': self.current_phase.value,
            'monitoring_active': self.is_monitoring,
            'deployment_start_time': self.deployment_start_time.isoformat() if self.deployment_start_time else None,
            'health_checks': [asdict(r) for r in recent_results],
            'rollback_triggers': [asdict(t) for t in triggered_rollbacks],
            'baseline_metrics': self.baseline_metrics,
            'timestamp': datetime.utcnow().isoformat()
        }

# Global health checker instance
deployment_health_checker = DeploymentHealthChecker()

# Export for use in other modules
__all__ = [
    'DeploymentHealthChecker',
    'HealthStatus',
    'DeploymentPhase', 
    'HealthCheckResult',
    'deployment_health_checker'
]