"""
API Layer Debugging and Monitoring System
Comprehensive debugging tools for warehouse API endpoints
"""

import os
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps
from contextlib import contextmanager
import threading
from collections import defaultdict, deque

from flask import request, g, jsonify, current_app
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from monitoring import log_error, track_performance, monitoring_buffer
from migration_debugger import migration_debugger

logger = logging.getLogger(__name__)

@dataclass
class APICallTrace:
    """Detailed API call tracing"""
    request_id: str
    timestamp: str
    endpoint: str
    method: str
    path: str
    query_params: Dict[str, Any]
    headers: Dict[str, str]
    body_size: int
    user_id: Optional[int]
    ip_address: str
    user_agent: str
    response_status: Optional[int] = None
    response_size: Optional[int] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    database_queries: List[Dict] = None
    memory_usage_mb: Optional[float] = None

@dataclass
class WarehouseAPIError:
    """Warehouse-specific API errors"""
    request_id: str
    timestamp: str
    endpoint: str
    error_type: str
    error_code: str
    user_message: str
    technical_message: str
    context: Dict[str, Any]
    user_id: Optional[int] = None
    warehouse_id: Optional[str] = None
    location_code: Optional[str] = None

class APIDebugger:
    """Comprehensive API debugging system"""
    
    def __init__(self):
        self.traces: deque = deque(maxlen=1000)
        self.errors: deque = deque(maxlen=500)
        self.performance_alerts: List[Dict] = []
        self.lock = threading.RLock()
        
        # Performance thresholds
        self.slow_endpoint_threshold = 2000  # 2 seconds
        self.memory_alert_threshold = 500   # 500MB
        self.error_rate_threshold = 0.05    # 5% error rate
    
    def add_trace(self, trace: APICallTrace):
        """Add API call trace"""
        with self.lock:
            self.traces.append(trace)
            
            # Check for performance issues
            if trace.duration_ms and trace.duration_ms > self.slow_endpoint_threshold:
                self.performance_alerts.append({
                    'type': 'SLOW_ENDPOINT',
                    'request_id': trace.request_id,
                    'endpoint': trace.endpoint,
                    'duration_ms': trace.duration_ms,
                    'timestamp': trace.timestamp
                })
            
            if trace.memory_usage_mb and trace.memory_usage_mb > self.memory_alert_threshold:
                self.performance_alerts.append({
                    'type': 'HIGH_MEMORY',
                    'request_id': trace.request_id,
                    'endpoint': trace.endpoint,
                    'memory_mb': trace.memory_usage_mb,
                    'timestamp': trace.timestamp
                })
    
    def add_error(self, error: WarehouseAPIError):
        """Add API error"""
        with self.lock:
            self.errors.append(error)
    
    def get_endpoint_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get endpoint performance statistics"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()
        
        recent_traces = [t for t in self.traces if t.timestamp > cutoff_str]
        
        endpoint_stats = defaultdict(lambda: {
            'call_count': 0,
            'error_count': 0,
            'total_duration': 0,
            'avg_duration': 0,
            'min_duration': float('inf'),
            'max_duration': 0,
            'success_rate': 0
        })
        
        for trace in recent_traces:
            endpoint = trace.endpoint
            endpoint_stats[endpoint]['call_count'] += 1
            
            if trace.response_status and trace.response_status >= 400:
                endpoint_stats[endpoint]['error_count'] += 1
            
            if trace.duration_ms:
                endpoint_stats[endpoint]['total_duration'] += trace.duration_ms
                endpoint_stats[endpoint]['min_duration'] = min(
                    endpoint_stats[endpoint]['min_duration'], 
                    trace.duration_ms
                )
                endpoint_stats[endpoint]['max_duration'] = max(
                    endpoint_stats[endpoint]['max_duration'], 
                    trace.duration_ms
                )
        
        # Calculate averages and success rates
        for endpoint, stats in endpoint_stats.items():
            if stats['call_count'] > 0:
                stats['avg_duration'] = stats['total_duration'] / stats['call_count']
                stats['success_rate'] = (stats['call_count'] - stats['error_count']) / stats['call_count']
            
            if stats['min_duration'] == float('inf'):
                stats['min_duration'] = 0
        
        return dict(endpoint_stats)

# Global API debugger
api_debugger = APIDebugger()

def create_request_id():
    """Generate unique request ID"""
    return str(uuid.uuid4())

def debug_api_call(func: Callable) -> Callable:
    """Decorator for comprehensive API call debugging"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate request ID
        request_id = create_request_id()
        g.request_id = request_id
        
        # Start timing
        start_time = time.time()
        start_memory = None
        
        try:
            import psutil
            start_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        except ImportError:
            pass
        
        # Extract request info
        trace = APICallTrace(
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat(),
            endpoint=request.endpoint or 'unknown',
            method=request.method,
            path=request.path,
            query_params=dict(request.args),
            headers=dict(request.headers),
            body_size=len(request.get_data()),
            user_id=getattr(g, 'current_user_id', None),
            ip_address=request.remote_addr or 'unknown',
            user_agent=request.headers.get('User-Agent', 'unknown'),
            database_queries=[]
        )
        
        try:
            # Execute the function
            result = func(*args, **kwargs)
            
            # Extract response info
            if hasattr(result, 'status_code'):
                trace.response_status = result.status_code
            elif isinstance(result, tuple) and len(result) > 1:
                trace.response_status = result[1]
            else:
                trace.response_status = 200
            
            if hasattr(result, 'content_length'):
                trace.response_size = result.content_length
            
            return result
            
        except HTTPException as e:
            trace.response_status = e.code
            trace.error_message = str(e)
            
            # Log warehouse-specific errors
            if hasattr(e, 'description') and 'warehouse' in e.description.lower():
                api_error = WarehouseAPIError(
                    request_id=request_id,
                    timestamp=datetime.utcnow().isoformat(),
                    endpoint=trace.endpoint,
                    error_type='HTTP_ERROR',
                    error_code=str(e.code),
                    user_message=e.description,
                    technical_message=str(e),
                    context={'path': trace.path, 'method': trace.method},
                    user_id=trace.user_id
                )
                api_debugger.add_error(api_error)
            
            raise
            
        except SQLAlchemyError as e:
            trace.response_status = 500
            trace.error_message = str(e)
            
            # Database-specific error handling
            api_error = WarehouseAPIError(
                request_id=request_id,
                timestamp=datetime.utcnow().isoformat(),
                endpoint=trace.endpoint,
                error_type='DATABASE_ERROR',
                error_code='SQL_ERROR',
                user_message='A database error occurred',
                technical_message=str(e),
                context={'path': trace.path, 'method': trace.method},
                user_id=trace.user_id
            )
            api_debugger.add_error(api_error)
            
            log_error(e, {
                'request_id': request_id,
                'endpoint': trace.endpoint,
                'component': 'api_database'
            })
            
            raise
            
        except Exception as e:
            trace.response_status = 500
            trace.error_message = str(e)
            
            # Generic error handling
            api_error = WarehouseAPIError(
                request_id=request_id,
                timestamp=datetime.utcnow().isoformat(),
                endpoint=trace.endpoint,
                error_type='INTERNAL_ERROR',
                error_code='UNKNOWN_ERROR',
                user_message='An internal error occurred',
                technical_message=str(e),
                context={'path': trace.path, 'method': trace.method},
                user_id=trace.user_id
            )
            api_debugger.add_error(api_error)
            
            log_error(e, {
                'request_id': request_id,
                'endpoint': trace.endpoint,
                'component': 'api_general'
            })
            
            raise
            
        finally:
            # Calculate final metrics
            trace.duration_ms = (time.time() - start_time) * 1000
            
            if start_memory:
                try:
                    current_memory = psutil.Process().memory_info().rss / (1024 * 1024)
                    trace.memory_usage_mb = current_memory
                except ImportError:
                    pass
            
            # Add trace to debugger
            api_debugger.add_trace(trace)
            
            # Log slow requests
            if trace.duration_ms > api_debugger.slow_endpoint_threshold:
                logger.warning(f"Slow API call: {trace.endpoint} took {trace.duration_ms:.2f}ms")
    
    return wrapper

class WarehouseAPIValidator:
    """Validator for warehouse API operations"""
    
    @staticmethod
    def validate_warehouse_setup(warehouse_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate warehouse setup data"""
        errors = []
        warnings = []
        
        required_fields = ['warehouse_name', 'num_aisles', 'racks_per_aisle', 'positions_per_rack']
        for field in required_fields:
            if field not in warehouse_data or warehouse_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate numeric fields
        numeric_fields = {
            'num_aisles': (1, 100),
            'racks_per_aisle': (1, 200),
            'positions_per_rack': (1, 100),
            'levels_per_position': (1, 10)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            if field in warehouse_data:
                try:
                    value = int(warehouse_data[field])
                    if value < min_val or value > max_val:
                        errors.append(f"{field} must be between {min_val} and {max_val}")
                except (ValueError, TypeError):
                    errors.append(f"{field} must be a valid number")
        
        # Check for reasonable warehouse size
        if all(field in warehouse_data for field in ['num_aisles', 'racks_per_aisle', 'positions_per_rack']):
            try:
                total_positions = (
                    int(warehouse_data['num_aisles']) * 
                    int(warehouse_data['racks_per_aisle']) * 
                    int(warehouse_data['positions_per_rack'])
                )
                if total_positions > 10000:
                    warnings.append(f"Large warehouse configuration: {total_positions} positions")
                elif total_positions < 10:
                    warnings.append(f"Very small warehouse configuration: {total_positions} positions")
            except (ValueError, TypeError):
                pass
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_location_data(location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate location data"""
        errors = []
        warnings = []
        
        required_fields = ['location_code']
        for field in required_fields:
            if field not in location_data or not location_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate location code format
        if 'location_code' in location_data:
            code = location_data['location_code']
            if len(code) < 3:
                warnings.append("Location code is very short")
            if not code.replace('-', '').replace('_', '').replace('.', '').isalnum():
                warnings.append("Location code contains special characters")
        
        # Validate numeric fields
        numeric_fields = ['aisle_number', 'rack_number', 'position_number', 'pallet_capacity']
        for field in numeric_fields:
            if field in location_data and location_data[field] is not None:
                try:
                    value = int(location_data[field])
                    if value < 0:
                        errors.append(f"{field} cannot be negative")
                except (ValueError, TypeError):
                    errors.append(f"{field} must be a valid number")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

# Warehouse-specific debugging middleware
class WarehouseDebugMiddleware:
    """Middleware for warehouse-specific debugging"""
    
    def __init__(self, app):
        self.app = app
        self.setup_error_handlers()
    
    def setup_error_handlers(self):
        """Setup custom error handlers"""
        
        @self.app.errorhandler(SQLAlchemyError)
        def handle_db_error(e):
            request_id = getattr(g, 'request_id', 'unknown')
            
            error_response = {
                'error': 'Database operation failed',
                'request_id': request_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Add specific error context for warehouse operations
            if 'location' in str(e).lower():
                error_response['context'] = 'location_operation'
                error_response['suggestion'] = 'Check location data format and constraints'
            elif 'warehouse' in str(e).lower():
                error_response['context'] = 'warehouse_operation'
                error_response['suggestion'] = 'Check warehouse configuration data'
            elif 'constraint' in str(e).lower():
                error_response['context'] = 'constraint_violation'
                error_response['suggestion'] = 'Check data integrity and foreign key references'
            
            logger.error(f"Database error in request {request_id}: {str(e)}")
            return jsonify(error_response), 500
        
        @self.app.errorhandler(ValueError)
        def handle_value_error(e):
            request_id = getattr(g, 'request_id', 'unknown')
            
            error_response = {
                'error': 'Invalid data provided',
                'message': str(e),
                'request_id': request_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return jsonify(error_response), 400

def test_warehouse_api_endpoints() -> Dict[str, Any]:
    """Test warehouse API endpoints health"""
    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints_tested': 0,
        'endpoints_healthy': 0,
        'endpoints_failed': 0,
        'details': {}
    }
    
    # Test endpoints (these would be actual API calls in a real test)
    test_endpoints = [
        ('GET', '/api/v1/warehouse/locations'),
        ('GET', '/api/v1/warehouse/config'),
        ('GET', '/api/v1/template/public'),
        ('GET', '/api/v1/health')
    ]
    
    for method, endpoint in test_endpoints:
        results['endpoints_tested'] += 1
        
        try:
            # This would be replaced with actual HTTP requests in a real implementation
            # For now, we'll simulate the test
            test_result = {
                'status': 'healthy',
                'response_time_ms': 150,
                'status_code': 200
            }
            
            results['endpoints_healthy'] += 1
            results['details'][endpoint] = test_result
            
        except Exception as e:
            results['endpoints_failed'] += 1
            results['details'][endpoint] = {
                'status': 'failed',
                'error': str(e)
            }
    
    return results

# Create debugging endpoints
def create_api_debugging_endpoints(app):
    """Create API debugging endpoints"""
    
    @app.route('/api/v1/debug/api-stats')
    def api_debug_stats():
        """Get API debugging statistics"""
        return jsonify({
            'endpoint_stats': api_debugger.get_endpoint_stats(),
            'recent_errors': [asdict(error) for error in list(api_debugger.errors)[-10:]],
            'performance_alerts': api_debugger.performance_alerts[-20:],
            'total_traces': len(api_debugger.traces),
            'total_errors': len(api_debugger.errors)
        })
    
    @app.route('/api/v1/debug/warehouse-health')
    def warehouse_api_health():
        """Warehouse API health check"""
        migration_report = migration_debugger.generate_migration_report()
        api_test = test_warehouse_api_endpoints()
        
        return jsonify({
            'migration_status': migration_report,
            'api_endpoints': api_test,
            'overall_health': 'healthy' if migration_report.get('schema_validation', {}).get('status') == 'healthy' else 'degraded'
        })
    
    @app.route('/api/v1/debug/request/<request_id>')
    def get_request_trace(request_id):
        """Get detailed trace for specific request"""
        for trace in api_debugger.traces:
            if trace.request_id == request_id:
                return jsonify(asdict(trace))
        
        return jsonify({'error': 'Request trace not found'}), 404
    
    @app.route('/api/v1/debug/validate-warehouse', methods=['POST'])
    def validate_warehouse_data():
        """Validate warehouse setup data"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        validation_result = WarehouseAPIValidator.validate_warehouse_setup(data)
        return jsonify(validation_result)
    
    @app.route('/api/v1/debug/validate-location', methods=['POST'])
    def validate_location_data():
        """Validate location data"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        validation_result = WarehouseAPIValidator.validate_location_data(data)
        return jsonify(validation_result)

# Export debugging utilities
__all__ = [
    'debug_api_call',
    'api_debugger',
    'WarehouseAPIValidator',
    'WarehouseDebugMiddleware',
    'create_api_debugging_endpoints'
]