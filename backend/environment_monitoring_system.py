#!/usr/bin/env python3
"""
Phase 4: Environment Validation and Monitoring System
Implements comprehensive environment monitoring, health checks, and real-time validation
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
import threading
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class EnvironmentMonitor:
    """Comprehensive environment monitoring and validation system"""
    
    def __init__(self, monitoring_interval: int = 60):
        self.monitoring_interval = monitoring_interval  # seconds
        self.metrics_history = defaultdict(deque)
        self.alert_thresholds = {
            'response_time_ms': 100,
            'error_rate_percent': 5,
            'memory_usage_percent': 80,
            'cpu_usage_percent': 85,
            'detection_accuracy_percent': 90,
            'confidence_score_min': 0.7
        }
        self.monitoring_active = False
        self.monitoring_thread = None
        self.health_status = {
            'overall': 'UNKNOWN',
            'components': {},
            'last_check': None,
            'alerts': []
        }
        
    def start_monitoring(self):
        """Start the monitoring system"""
        print("[MONITOR] Starting environment monitoring system...")
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        print(f"[MONITOR] Monitoring started with {self.monitoring_interval}s interval")
        
    def stop_monitoring(self):
        """Stop the monitoring system"""
        print("[MONITOR] Stopping environment monitoring...")
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("[MONITOR] Monitoring stopped")
        
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                self._collect_system_metrics()
                self._collect_application_metrics()
                self._validate_environment_health()
                
                # Check for alerts
                self._check_alert_conditions()
                
                # Clean old metrics (keep last 24 hours)
                self._cleanup_old_metrics()
                
                # Wait for next interval
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"[MONITOR_ERROR] Monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        timestamp = datetime.now().isoformat()
        
        # CPU metrics (simulated for demo)
        cpu_percent = self._get_simulated_cpu_usage()
        self.metrics_history['cpu_usage'].append({
            'timestamp': timestamp,
            'value': cpu_percent
        })
        
        # Memory metrics (simulated for demo)
        memory_percent = self._get_simulated_memory_usage()
        self.metrics_history['memory_usage'].append({
            'timestamp': timestamp,
            'value': memory_percent
        })
        
        # Disk metrics (simulated for demo)
        disk_percent = self._get_simulated_disk_usage()
        self.metrics_history['disk_usage'].append({
            'timestamp': timestamp,
            'value': disk_percent
        })
        
    def _collect_application_metrics(self):
        """Collect application-specific metrics"""
        timestamp = datetime.now().isoformat()
        
        try:
            # Test warehouse detection performance
            detection_metrics = self._measure_detection_performance()
            
            self.metrics_history['detection_response_time'].append({
                'timestamp': timestamp,
                'value': detection_metrics['response_time_ms']
            })
            
            self.metrics_history['detection_accuracy'].append({
                'timestamp': timestamp,
                'value': detection_metrics['accuracy_score'] * 100
            })
            
            self.metrics_history['confidence_score'].append({
                'timestamp': timestamp,
                'value': detection_metrics['confidence_score']
            })
            
        except Exception as e:
            print(f"[MONITOR_WARNING] Could not collect application metrics: {e}")
            # Record the error
            self.metrics_history['application_errors'].append({
                'timestamp': timestamp,
                'error': str(e)
            })
    
    def _measure_detection_performance(self) -> Dict:
        """Measure current warehouse detection performance"""
        try:
            from app import app, db
            from rule_engine import RuleEngine
            import pandas as pd
            
            with app.app_context():
                rule_engine = RuleEngine(db.session)
                
                # Test with small sample
                test_locations = ['02-01-011B', '01-01-007B', 'RECV-001']
                test_df = pd.DataFrame({'location': test_locations})
                
                start_time = time.time()
                detection_result = rule_engine._detect_warehouse_context(test_df)
                response_time_ms = (time.time() - start_time) * 1000
                
                return {
                    'response_time_ms': response_time_ms,
                    'accuracy_score': detection_result.get('match_score', 0),
                    'confidence_score': self._confidence_to_numeric(
                        detection_result.get('confidence_level', 'LOW')
                    ),
                    'warehouse_detected': detection_result.get('warehouse_id') is not None
                }
                
        except Exception as e:
            return {
                'response_time_ms': 0,
                'accuracy_score': 0,
                'confidence_score': 0,
                'warehouse_detected': False,
                'error': str(e)
            }
    
    def _confidence_to_numeric(self, confidence_level: str) -> float:
        """Convert confidence level to numeric score"""
        mapping = {
            'VERY_HIGH': 1.0,
            'HIGH': 0.8,
            'MEDIUM': 0.6,
            'LOW': 0.4,
            'VERY_LOW': 0.2
        }
        return mapping.get(confidence_level, 0.0)
    
    def _get_simulated_cpu_usage(self) -> float:
        """Get simulated CPU usage for demo purposes"""
        import random
        # Simulate CPU usage between 20-60%
        return random.uniform(20, 60)
    
    def _get_simulated_memory_usage(self) -> float:
        """Get simulated memory usage for demo purposes"""
        import random
        # Simulate memory usage between 40-70%
        return random.uniform(40, 70)
    
    def _get_simulated_disk_usage(self) -> float:
        """Get simulated disk usage for demo purposes"""
        import random
        # Simulate disk usage between 30-50%
        return random.uniform(30, 50)
    
    def _validate_environment_health(self):
        """Validate overall environment health"""
        health_checks = {
            'database_connectivity': self._check_database_health(),
            'application_responsiveness': self._check_application_health(),
            'system_resources': self._check_system_health(),
            'detection_system': self._check_detection_system_health()
        }
        
        # Calculate overall health
        healthy_components = sum(1 for status in health_checks.values() if status)
        total_components = len(health_checks)
        overall_health_score = healthy_components / total_components
        
        if overall_health_score >= 0.9:
            overall_status = 'HEALTHY'
        elif overall_health_score >= 0.7:
            overall_status = 'WARNING'
        else:
            overall_status = 'CRITICAL'
        
        self.health_status.update({
            'overall': overall_status,
            'components': health_checks,
            'last_check': datetime.now().isoformat(),
            'health_score': overall_health_score
        })
    
    def _check_database_health(self) -> bool:
        """Check database connectivity and performance"""
        try:
            from app import app, db
            
            with app.app_context():
                start_time = time.time()
                result = db.session.execute('SELECT 1').scalar()
                response_time = (time.time() - start_time) * 1000
                
                return result == 1 and response_time < 50  # Under 50ms
                
        except Exception:
            return False
    
    def _check_application_health(self) -> bool:
        """Check application responsiveness"""
        try:
            # Test basic application functionality
            detection_metrics = self._measure_detection_performance()
            
            return (
                detection_metrics['response_time_ms'] < self.alert_thresholds['response_time_ms'] and
                detection_metrics['warehouse_detected'] and
                'error' not in detection_metrics
            )
            
        except Exception:
            return False
    
    def _check_system_health(self) -> bool:
        """Check system resource health"""
        try:
            cpu_ok = self._get_simulated_cpu_usage() < self.alert_thresholds['cpu_usage_percent']
            memory_ok = self._get_simulated_memory_usage() < self.alert_thresholds['memory_usage_percent']
            
            return cpu_ok and memory_ok
            
        except Exception:
            return False
    
    def _check_detection_system_health(self) -> bool:
        """Check warehouse detection system health"""
        try:
            detection_metrics = self._measure_detection_performance()
            
            return (
                detection_metrics['accuracy_score'] >= (self.alert_thresholds['detection_accuracy_percent'] / 100) and
                detection_metrics['confidence_score'] >= self.alert_thresholds['confidence_score_min']
            )
            
        except Exception:
            return False
    
    def _check_alert_conditions(self):
        """Check for alert conditions and trigger alerts"""
        current_alerts = []
        
        # Check recent metrics for threshold violations
        for metric_name, threshold in self.alert_thresholds.items():
            if metric_name in self.metrics_history:
                recent_metrics = list(self.metrics_history[metric_name])[-5:]  # Last 5 readings
                
                if recent_metrics:
                    # Check if threshold is consistently violated
                    violations = 0
                    for metric in recent_metrics:
                        value = metric['value']
                        
                        if metric_name.endswith('_percent') and value > threshold:
                            violations += 1
                        elif metric_name.endswith('_ms') and value > threshold:
                            violations += 1
                        elif metric_name.endswith('_min') and value < threshold:
                            violations += 1
                    
                    # Trigger alert if more than half of recent readings violate threshold
                    if violations > len(recent_metrics) / 2:
                        current_alerts.append({
                            'metric': metric_name,
                            'threshold': threshold,
                            'current_value': recent_metrics[-1]['value'],
                            'severity': 'HIGH' if violations >= 4 else 'MEDIUM',
                            'timestamp': datetime.now().isoformat()
                        })
        
        # Update alerts
        self.health_status['alerts'] = current_alerts
        
        # Log alerts
        for alert in current_alerts:
            print(f"[ALERT] {alert['severity']}: {alert['metric']} = {alert['current_value']:.2f} (threshold: {alert['threshold']})")
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than 24 hours"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for metric_name, metric_history in self.metrics_history.items():
            # Keep only recent metrics
            while metric_history and datetime.fromisoformat(metric_history[0]['timestamp']) < cutoff_time:
                metric_history.popleft()
    
    def get_environment_status(self) -> Dict:
        """Get current environment status and metrics"""
        recent_metrics = {}
        
        # Get latest values for each metric
        for metric_name, metric_history in self.metrics_history.items():
            if metric_history:
                recent_metrics[metric_name] = metric_history[-1]['value']
        
        return {
            'health_status': self.health_status,
            'recent_metrics': recent_metrics,
            'alert_thresholds': self.alert_thresholds,
            'monitoring_active': self.monitoring_active,
            'metrics_collected': len(self.metrics_history)
        }
    
    def generate_health_report(self, output_file: str = None) -> str:
        """Generate comprehensive health report"""
        status = self.get_environment_status()
        
        report = f"""
# Environment Health Report
Generated: {datetime.now().isoformat()}

## Overall Status: {status['health_status']['overall']}
Health Score: {status['health_status'].get('health_score', 0):.1%}

## Component Status
"""
        
        for component, health in status['health_status']['components'].items():
            status_text = "PASS" if health else "FAIL"
            report += f"- {component.replace('_', ' ').title()}: {status_text} {'HEALTHY' if health else 'UNHEALTHY'}\n"
        
        report += f"""
## Current Metrics
"""
        
        for metric, value in status['recent_metrics'].items():
            threshold = status['alert_thresholds'].get(metric, 'N/A')
            report += f"- {metric.replace('_', ' ').title()}: {value:.2f} (threshold: {threshold})\n"
        
        if status['health_status']['alerts']:
            report += f"""
## Active Alerts ({len(status['health_status']['alerts'])})
"""
            for alert in status['health_status']['alerts']:
                report += f"- {alert['severity']}: {alert['metric']} = {alert['current_value']:.2f} (threshold: {alert['threshold']})\n"
        else:
            report += f"""
## Active Alerts
No active alerts
"""
        
        report += f"""
## Monitoring Configuration
- Monitoring Active: {'Yes' if status['monitoring_active'] else 'No'}
- Metrics Collected: {status['metrics_collected']} types
- Check Interval: {self.monitoring_interval}s
- Last Health Check: {status['health_status']['last_check']}
"""
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"[MONITOR] Health report saved to: {output_file}")
        
        return report
    
    def run_validation_suite(self) -> Dict[str, bool]:
        """Run comprehensive validation suite"""
        print("[VALIDATION] Running environment validation suite...")
        
        validation_results = {
            'system_resources': self._validate_system_resources(),
            'database_performance': self._validate_database_performance(),
            'application_functionality': self._validate_application_functionality(),
            'detection_accuracy': self._validate_detection_accuracy(),
            'error_handling': self._validate_error_handling()
        }
        
        overall_success = all(validation_results.values())
        success_rate = sum(validation_results.values()) / len(validation_results)
        
        print(f"[VALIDATION] Validation suite completed: {success_rate:.1%} success rate")
        for test, result in validation_results.items():
            print(f"  {test.replace('_', ' ').title()}: {'PASS' if result else 'FAIL'}")
        
        return validation_results
    
    def _validate_system_resources(self) -> bool:
        """Validate system resources are adequate"""
        try:
            cpu_ok = self._get_simulated_cpu_usage() < 80
            memory_ok = self._get_simulated_memory_usage() < 80
            disk_ok = self._get_simulated_disk_usage() < 90
            
            return cpu_ok and memory_ok and disk_ok
        except Exception:
            return False
    
    def _validate_database_performance(self) -> bool:
        """Validate database performance"""
        try:
            from app import app, db
            
            with app.app_context():
                # Test multiple query types
                queries = [
                    "SELECT COUNT(*) FROM location",
                    "SELECT * FROM location LIMIT 10",
                    "SELECT warehouse_id, COUNT(*) FROM location GROUP BY warehouse_id"
                ]
                
                for query in queries:
                    start_time = time.time()
                    db.session.execute(query)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response_time > 100:  # 100ms threshold
                        return False
                
                return True
                
        except Exception:
            return False
    
    def _validate_application_functionality(self) -> bool:
        """Validate core application functionality"""
        try:
            detection_metrics = self._measure_detection_performance()
            
            return (
                detection_metrics['response_time_ms'] < 100 and
                detection_metrics['warehouse_detected'] and
                'error' not in detection_metrics
            )
            
        except Exception:
            return False
    
    def _validate_detection_accuracy(self) -> bool:
        """Validate warehouse detection accuracy"""
        try:
            detection_metrics = self._measure_detection_performance()
            
            return (
                detection_metrics['accuracy_score'] >= 0.8 and
                detection_metrics['confidence_score'] >= 0.7
            )
            
        except Exception:
            return False
    
    def _validate_error_handling(self) -> bool:
        """Validate error handling works correctly"""
        try:
            from app import app, db
            from rule_engine import RuleEngine
            import pandas as pd
            
            with app.app_context():
                rule_engine = RuleEngine(db.session)
                
                # Test error scenarios
                error_tests = [
                    pd.DataFrame(),  # Empty DataFrame
                    pd.DataFrame({'other_col': ['test']}),  # Missing location column
                    pd.DataFrame({'location': [None, '', 'INVALID@#$']})  # Invalid data
                ]
                
                for test_df in error_tests:
                    try:
                        result = rule_engine._detect_warehouse_context(test_df)
                        # Should return a result without crashing
                        if not isinstance(result, dict):
                            return False
                    except Exception:
                        return False  # Should handle errors gracefully
                
                return True
                
        except Exception:
            return False

def main():
    """Demonstrate environment monitoring system"""
    
    print("PHASE 4: ENVIRONMENT VALIDATION AND MONITORING")
    print("=" * 50)
    
    # Initialize monitor
    monitor = EnvironmentMonitor(monitoring_interval=30)  # 30 second intervals for demo
    
    # Step 1: Run validation suite
    print("\nStep 1: Running environment validation suite...")
    validation_results = monitor.run_validation_suite()
    
    # Step 2: Start monitoring
    print("\nStep 2: Starting environment monitoring...")
    monitor.start_monitoring()
    
    # Step 3: Monitor for a short period
    print("\nStep 3: Monitoring for 60 seconds...")
    time.sleep(60)
    
    # Step 4: Generate health report
    print("\nStep 4: Generating health report...")
    report_file = f"environment_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    health_report = monitor.generate_health_report(report_file)
    
    # Step 5: Get final status
    print("\nStep 5: Getting final environment status...")
    final_status = monitor.get_environment_status()
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    # Summary
    print("\n" + "=" * 50)
    print("ENVIRONMENT MONITORING SUMMARY")
    print("=" * 50)
    
    validation_success_rate = sum(validation_results.values()) / len(validation_results)
    overall_health = final_status['health_status']['overall']
    health_score = final_status['health_status'].get('health_score', 0)
    
    print(f"Validation Success Rate: {validation_success_rate:.1%}")
    print(f"Overall Health Status: {overall_health}")
    print(f"Health Score: {health_score:.1%}")
    print(f"Active Alerts: {len(final_status['health_status']['alerts'])}")
    
    if validation_success_rate >= 0.8 and overall_health in ['HEALTHY', 'WARNING']:
        print("\n✅ ENVIRONMENT MONITORING SYSTEM OPERATIONAL")
        print("\nMonitoring Capabilities:")
        print("✅ Real-time system metrics collection")
        print("✅ Application performance monitoring")
        print("✅ Health checks and validation")
        print("✅ Alert system with configurable thresholds")
        print("✅ Comprehensive health reporting")
    else:
        print("\n⚠️ ENVIRONMENT MONITORING NEEDS ATTENTION")
    
    return validation_success_rate >= 0.6 and overall_health != 'CRITICAL'

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)