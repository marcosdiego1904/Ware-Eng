"""
Production Monitoring and Debugging System
Comprehensive error tracking, performance monitoring, and debugging tools
"""

import os
import json
import time
import logging
import traceback
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import threading
from collections import deque, defaultdict
import psutil
import weakref

from flask import request, g, current_app
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from database import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global monitoring state
_monitoring_state = {
    'enabled': os.environ.get('MONITORING_ENABLED', 'true').lower() == 'true',
    'debug_mode': os.environ.get('DEBUG_MONITORING', 'false').lower() == 'true',
    'performance_tracking': os.environ.get('PERFORMANCE_TRACKING', 'true').lower() == 'true'
}

@dataclass
class ErrorEvent:
    """Error event data structure"""
    timestamp: str
    error_type: str
    error_message: str
    stack_trace: str
    context: Dict[str, Any]
    severity: str
    user_id: Optional[int] = None
    request_id: Optional[str] = None
    component: str = 'backend'
    
    def to_dict(self):
        return asdict(self)

@dataclass 
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: str
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any]
    component: str = 'backend'
    
    def to_dict(self):
        return asdict(self)

@dataclass
class DatabaseEvent:
    """Database operation event"""
    timestamp: str
    query: str
    duration_ms: float
    table_name: Optional[str] = None
    operation: str = 'SELECT'
    row_count: int = 0
    error: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)

class MonitoringBuffer:
    """Thread-safe buffer for monitoring events"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.errors = deque(maxlen=max_size)
        self.performance = deque(maxlen=max_size)
        self.database = deque(maxlen=max_size)
        self.api_calls = deque(maxlen=max_size)
        self.lock = threading.RLock()
    
    def add_error(self, event: ErrorEvent):
        with self.lock:
            self.errors.append(event)
    
    def add_performance(self, metric: PerformanceMetric):
        with self.lock:
            self.performance.append(metric)
    
    def add_database_event(self, event: DatabaseEvent):
        with self.lock:
            self.database.append(event)
    
    def add_api_call(self, call_data: Dict[str, Any]):
        with self.lock:
            self.api_calls.append(call_data)
    
    def get_recent_errors(self, limit: int = 100) -> List[ErrorEvent]:
        with self.lock:
            return list(self.errors)[-limit:]
    
    def get_recent_performance(self, limit: int = 100) -> List[PerformanceMetric]:
        with self.lock:
            return list(self.performance)[-limit:]
    
    def get_recent_database_events(self, limit: int = 100) -> List[DatabaseEvent]:
        with self.lock:
            return list(self.database)[-limit:]
    
    def clear_old_data(self, hours: int = 24):
        """Clear events older than specified hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()
        
        with self.lock:
            self.errors = deque([e for e in self.errors if e.timestamp > cutoff_str], 
                             maxlen=self.max_size)
            self.performance = deque([p for p in self.performance if p.timestamp > cutoff_str], 
                                  maxlen=self.max_size)
            self.database = deque([d for d in self.database if d.timestamp > cutoff_str], 
                                maxlen=self.max_size)

# Global monitoring buffer
monitoring_buffer = MonitoringBuffer()

class PerformanceTracker:
    """Context manager for tracking performance"""
    
    def __init__(self, metric_name: str, context: Dict[str, Any] = None):
        self.metric_name = metric_name
        self.context = context or {}
        self.start_time = None
        self.start_memory = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (time.time() - self.start_time) * 1000
            current_memory = psutil.Process().memory_info().rss
            memory_diff = current_memory - self.start_memory
            
            # Add performance metric
            metric = PerformanceMetric(
                timestamp=datetime.utcnow().isoformat(),
                metric_name=self.metric_name,
                value=duration,
                unit='ms',
                context={
                    **self.context,
                    'memory_delta_mb': memory_diff / (1024 * 1024),
                    'current_memory_mb': current_memory / (1024 * 1024)
                }
            )
            
            if _monitoring_state['performance_tracking']:
                monitoring_buffer.add_performance(metric)
                
            # Log slow operations
            if duration > 1000:  # > 1 second
                logger.warning(f"Slow operation: {self.metric_name} took {duration:.2f}ms")

def track_performance(metric_name: str, context: Dict[str, Any] = None):
    """Decorator for tracking function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_context = {
                'function': func.__name__,
                'module': func.__module__,
                **(context or {})
            }
            
            with PerformanceTracker(metric_name, func_context):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def log_error(error: Exception, context: Dict[str, Any] = None, severity: str = 'ERROR'):
    """Log error with full context"""
    if not _monitoring_state['enabled']:
        return
    
    error_event = ErrorEvent(
        timestamp=datetime.utcnow().isoformat(),
        error_type=type(error).__name__,
        error_message=str(error),
        stack_trace=traceback.format_exc(),
        context=context or {},
        severity=severity,
        user_id=getattr(g, 'current_user_id', None),
        request_id=getattr(g, 'request_id', None)
    )
    
    monitoring_buffer.add_error(error_event)
    
    # Log to standard logging
    if severity in ['CRITICAL', 'ERROR']:
        logger.error(f"{error_event.error_type}: {error_event.error_message}")
        if _monitoring_state['debug_mode']:
            logger.error(f"Stack trace: {error_event.stack_trace}")

def monitor_api_call(func):
    """Decorator to monitor API calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        request_id = getattr(g, 'request_id', None)
        
        call_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': request.endpoint,
            'method': request.method,
            'path': request.path,
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr,
            'request_id': request_id,
            'status_code': None,
            'duration_ms': None,
            'error': None
        }
        
        try:
            result = func(*args, **kwargs)
            call_data['status_code'] = getattr(result, 'status_code', 200)
            return result
            
        except Exception as e:
            call_data['error'] = str(e)
            call_data['status_code'] = 500
            log_error(e, {
                'endpoint': request.endpoint,
                'method': request.method,
                'path': request.path
            })
            raise
            
        finally:
            call_data['duration_ms'] = (time.time() - start_time) * 1000
            monitoring_buffer.add_api_call(call_data)
            
    return wrapper

# Database monitoring
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track database query start time"""
    if _monitoring_state['performance_tracking']:
        context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track database query completion"""
    if not _monitoring_state['performance_tracking']:
        return
        
    if hasattr(context, '_query_start_time'):
        duration_ms = (time.time() - context._query_start_time) * 1000
        
        # Extract table name from query
        table_name = None
        operation = 'UNKNOWN'
        
        statement_upper = statement.upper().strip()
        if statement_upper.startswith('SELECT'):
            operation = 'SELECT'
            if ' FROM ' in statement_upper:
                parts = statement_upper.split(' FROM ')[1].split()
                if parts:
                    table_name = parts[0].split('.')[0]  # Remove schema if present
        elif statement_upper.startswith('INSERT'):
            operation = 'INSERT'
            if ' INTO ' in statement_upper:
                parts = statement_upper.split(' INTO ')[1].split()
                if parts:
                    table_name = parts[0].split('.')[0]
        elif statement_upper.startswith('UPDATE'):
            operation = 'UPDATE'
            parts = statement_upper.split('UPDATE')[1].strip().split()
            if parts:
                table_name = parts[0].split('.')[0]
        elif statement_upper.startswith('DELETE'):
            operation = 'DELETE'
            if ' FROM ' in statement_upper:
                parts = statement_upper.split(' FROM ')[1].split()
                if parts:
                    table_name = parts[0].split('.')[0]
        
        db_event = DatabaseEvent(
            timestamp=datetime.utcnow().isoformat(),
            query=statement[:500] if len(statement) > 500 else statement,  # Truncate long queries
            duration_ms=duration_ms,
            table_name=table_name,
            operation=operation,
            row_count=cursor.rowcount if hasattr(cursor, 'rowcount') else 0
        )
        
        monitoring_buffer.add_database_event(db_event)
        
        # Log slow queries
        if duration_ms > 500:  # > 500ms
            logger.warning(f"Slow query ({duration_ms:.2f}ms): {statement[:200]}...")

class MonitoringDashboard:
    """Dashboard for monitoring data"""
    
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        """Get current system health metrics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent()
        
        # Database connection test
        db_healthy = True
        db_error = None
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as e:
            db_healthy = False
            db_error = str(e)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'process_id': process.pid,
            'memory': {
                'rss_mb': memory_info.rss / (1024 * 1024),
                'vms_mb': memory_info.vms / (1024 * 1024),
                'percent': process.memory_percent()
            },
            'cpu_percent': cpu_percent,
            'database': {
                'healthy': db_healthy,
                'error': db_error
            },
            'monitoring': {
                'enabled': _monitoring_state['enabled'],
                'debug_mode': _monitoring_state['debug_mode'],
                'performance_tracking': _monitoring_state['performance_tracking']
            }
        }
    
    @staticmethod
    def get_error_summary(hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()
        
        recent_errors = [e for e in monitoring_buffer.get_recent_errors() 
                        if e.timestamp > cutoff_str]
        
        error_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for error in recent_errors:
            error_counts[error.error_type] += 1
            severity_counts[error.severity] += 1
        
        return {
            'total_errors': len(recent_errors),
            'error_types': dict(error_counts),
            'severity_breakdown': dict(severity_counts),
            'recent_errors': [e.to_dict() for e in recent_errors[-10:]]
        }
    
    @staticmethod
    def get_performance_summary(hours: int = 24) -> Dict[str, Any]:
        """Get performance summary"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()
        
        recent_metrics = [m for m in monitoring_buffer.get_recent_performance() 
                         if m.timestamp > cutoff_str]
        
        # Group by metric name
        metric_groups = defaultdict(list)
        for metric in recent_metrics:
            metric_groups[metric.metric_name].append(metric.value)
        
        summary = {}
        for name, values in metric_groups.items():
            summary[name] = {
                'count': len(values),
                'avg': sum(values) / len(values) if values else 0,
                'min': min(values) if values else 0,
                'max': max(values) if values else 0,
                'recent': values[-10:] if len(values) > 10 else values
            }
        
        return {
            'metric_summary': summary,
            'total_metrics': len(recent_metrics)
        }
    
    @staticmethod
    def get_database_summary(hours: int = 24) -> Dict[str, Any]:
        """Get database performance summary"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()
        
        recent_events = [e for e in monitoring_buffer.get_recent_database_events() 
                        if e.timestamp > cutoff_str]
        
        table_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'avg_time': 0})
        operation_stats = defaultdict(int)
        slow_queries = []
        
        for event in recent_events:
            if event.table_name:
                table_stats[event.table_name]['count'] += 1
                table_stats[event.table_name]['total_time'] += event.duration_ms
            
            operation_stats[event.operation] += 1
            
            if event.duration_ms > 500:  # Slow query threshold
                slow_queries.append(event.to_dict())
        
        # Calculate averages
        for table_name, stats in table_stats.items():
            if stats['count'] > 0:
                stats['avg_time'] = stats['total_time'] / stats['count']
        
        return {
            'total_queries': len(recent_events),
            'table_statistics': dict(table_stats),
            'operation_breakdown': dict(operation_stats),
            'slow_queries': slow_queries[-20:],  # Last 20 slow queries
            'avg_query_time': sum(e.duration_ms for e in recent_events) / len(recent_events) if recent_events else 0
        }

# Monitoring API endpoints will be added to app.py
def create_monitoring_endpoints(app):
    """Create monitoring API endpoints"""
    
    @app.route('/api/v1/monitoring/health')
    def monitoring_health():
        """System health check"""
        return MonitoringDashboard.get_system_health()
    
    @app.route('/api/v1/monitoring/errors')
    def monitoring_errors():
        """Error monitoring dashboard"""
        hours = request.args.get('hours', 24, type=int)
        return MonitoringDashboard.get_error_summary(hours)
    
    @app.route('/api/v1/monitoring/performance')
    def monitoring_performance():
        """Performance monitoring dashboard"""
        hours = request.args.get('hours', 24, type=int)
        return MonitoringDashboard.get_performance_summary(hours)
    
    @app.route('/api/v1/monitoring/database')
    def monitoring_database():
        """Database performance monitoring"""
        hours = request.args.get('hours', 24, type=int)
        return MonitoringDashboard.get_database_summary(hours)
    
    @app.route('/api/v1/monitoring/clear')
    def monitoring_clear():
        """Clear monitoring data (admin only)"""
        if not _monitoring_state['debug_mode']:
            return {'error': 'Not authorized'}, 403
            
        monitoring_buffer.clear_old_data(0)  # Clear all data
        return {'message': 'Monitoring data cleared'}

# Background cleanup task
def start_monitoring_cleanup():
    """Start background cleanup task"""
    def cleanup_task():
        while True:
            try:
                time.sleep(3600)  # Run every hour
                monitoring_buffer.clear_old_data(24)  # Keep 24 hours
                logger.info("Monitoring data cleanup completed")
            except Exception as e:
                logger.error(f"Monitoring cleanup error: {e}")
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()

# Initialize monitoring
if _monitoring_state['enabled']:
    logger.info("Production monitoring system initialized")
    start_monitoring_cleanup()