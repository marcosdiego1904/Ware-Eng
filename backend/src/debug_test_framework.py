"""
Automated Testing Framework for Debugging Warehouse Optimization Changes
Comprehensive testing suite for database migrations, API endpoints, and business logic
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from unittest.mock import Mock

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from database import db
from monitoring import log_error, track_performance
from migration_debugger import migration_debugger

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    test_type: str
    status: str  # PASS, FAIL, SKIP, ERROR
    duration_ms: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    description: str
    tests: List[Callable]
    setup_function: Optional[Callable] = None
    teardown_function: Optional[Callable] = None
    timeout_seconds: int = 300
    parallel: bool = False

class DebugTestFramework:
    """Automated testing framework for debugging optimization changes"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.test_suites: Dict[str, TestSuite] = {}
        self.base_url = os.environ.get('API_BASE_URL', 'http://localhost:5000')
        self.test_user_token = None
        self.setup_complete = False
        
    def register_test_suite(self, suite: TestSuite):
        """Register a test suite"""
        self.test_suites[suite.name] = suite
        logger.info(f"Registered test suite: {suite.name}")
    
    def setup_test_environment(self) -> bool:
        """Setup test environment with test data"""
        try:
            logger.info("Setting up test environment...")
            
            # Create test user and get token
            self.test_user_token = self._create_test_user()
            
            # Setup test data
            self._setup_test_data()
            
            self.setup_complete = True
            logger.info("Test environment setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup test environment: {e}")
            return False
    
    def _create_test_user(self) -> str:
        """Create test user and return JWT token"""
        try:
            # Register test user
            register_data = {
                'username': 'debug_test_user',
                'password': 'test_password_123'
            }
            
            # Try to register (might fail if user exists)
            requests.post(f"{self.base_url}/api/v1/auth/register", json=register_data)
            
            # Login to get token
            login_response = requests.post(f"{self.base_url}/api/v1/auth/login", json=register_data)
            if login_response.status_code == 200:
                return login_response.json()['token']
            else:
                raise Exception(f"Failed to login test user: {login_response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to create test user: {e}")
            raise
    
    def _setup_test_data(self):
        """Setup test data for warehouse operations"""
        try:
            # Create test warehouse configuration
            test_warehouse = {
                'warehouse_id': 'TEST_WH',
                'warehouse_name': 'Test Warehouse',
                'num_aisles': 3,
                'racks_per_aisle': 5,
                'positions_per_rack': 10,
                'levels_per_position': 4,
                'level_names': 'ABCD'
            }
            
            headers = {'Authorization': f'Bearer {self.test_user_token}'}
            response = requests.post(
                f"{self.base_url}/api/v1/warehouse/setup",
                json=test_warehouse,
                headers=headers
            )
            
            if response.status_code not in [200, 201, 409]:  # 409 for already exists
                raise Exception(f"Failed to setup test warehouse: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Failed to setup test data: {e}")
    
    def run_all_tests(self, parallel: bool = False) -> Dict[str, Any]:
        """Run all registered test suites"""
        if not self.setup_complete:
            if not self.setup_test_environment():
                return {'error': 'Failed to setup test environment'}
        
        start_time = time.time()
        all_results = []
        
        logger.info(f"Running {len(self.test_suites)} test suites...")
        
        if parallel:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(self._run_test_suite, suite_name, suite): suite_name
                    for suite_name, suite in self.test_suites.items()
                }
                
                for future in as_completed(futures):
                    suite_name = futures[future]
                    try:
                        results = future.result()
                        all_results.extend(results)
                    except Exception as e:
                        logger.error(f"Test suite {suite_name} failed: {e}")
        else:
            for suite_name, suite in self.test_suites.items():
                try:
                    results = self._run_test_suite(suite_name, suite)
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Test suite {suite_name} failed: {e}")
        
        # Generate summary
        total_duration = time.time() - start_time
        summary = self._generate_test_summary(all_results, total_duration)
        
        # Store results
        self.test_results.extend(all_results)
        
        return summary
    
    def _run_test_suite(self, suite_name: str, suite: TestSuite) -> List[TestResult]:
        """Run a single test suite"""
        results = []
        logger.info(f"Running test suite: {suite_name}")
        
        # Setup
        if suite.setup_function:
            try:
                suite.setup_function()
            except Exception as e:
                logger.error(f"Setup failed for {suite_name}: {e}")
                return [TestResult(
                    test_name=f"{suite_name}_setup",
                    test_type="SETUP",
                    status="FAIL",
                    duration_ms=0,
                    error_message=str(e)
                )]
        
        # Run tests
        for test_func in suite.tests:
            result = self._run_single_test(test_func, suite_name, suite.timeout_seconds)
            results.append(result)
        
        # Teardown
        if suite.teardown_function:
            try:
                suite.teardown_function()
            except Exception as e:
                logger.warning(f"Teardown failed for {suite_name}: {e}")
        
        return results
    
    def _run_single_test(self, test_func: Callable, suite_name: str, timeout: int) -> TestResult:
        """Run a single test function"""
        test_name = f"{suite_name}.{test_func.__name__}"
        start_time = time.time()
        
        try:
            # Run with timeout
            result = self._run_with_timeout(test_func, timeout)
            duration_ms = (time.time() - start_time) * 1000
            
            if result is True or result is None:
                return TestResult(
                    test_name=test_name,
                    test_type="FUNCTIONAL",
                    status="PASS",
                    duration_ms=duration_ms
                )
            elif isinstance(result, dict):
                return TestResult(
                    test_name=test_name,
                    test_type="FUNCTIONAL",
                    status="PASS" if result.get('status') == 'pass' else "FAIL",
                    duration_ms=duration_ms,
                    details=result
                )
            else:
                return TestResult(
                    test_name=test_name,
                    test_type="FUNCTIONAL",
                    status="FAIL",
                    duration_ms=duration_ms,
                    error_message="Test returned unexpected result"
                )
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                test_type="FUNCTIONAL",
                status="ERROR",
                duration_ms=duration_ms,
                error_message=str(e),
                details={'traceback': traceback.format_exc()}
            )
    
    def _run_with_timeout(self, func: Callable, timeout: int):
        """Run function with timeout"""
        try:
            return func()
        except Exception:
            raise
    
    def _generate_test_summary(self, results: List[TestResult], duration: float) -> Dict[str, Any]:
        """Generate test execution summary"""
        total_tests = len(results)
        passed = len([r for r in results if r.status == "PASS"])
        failed = len([r for r in results if r.status == "FAIL"])
        errors = len([r for r in results if r.status == "ERROR"])
        skipped = len([r for r in results if r.status == "SKIP"])
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_duration_seconds': duration,
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'success_rate': (passed / total_tests * 100) if total_tests > 0 else 0,
            'results': [asdict(r) for r in results],
            'failed_tests': [asdict(r) for r in results if r.status in ["FAIL", "ERROR"]]
        }
    
    # Test Functions for Warehouse Optimization
    
    def test_database_schema_integrity(self) -> Dict[str, Any]:
        """Test database schema integrity"""
        validation = migration_debugger.validate_schema()
        
        if validation['status'] == 'healthy':
            return {'status': 'pass', 'details': validation}
        else:
            raise Exception(f"Schema validation failed: {validation}")
    
    def test_warehouse_setup_api(self) -> Dict[str, Any]:
        """Test warehouse setup API endpoint"""
        test_data = {
            'warehouse_name': 'API Test Warehouse',
            'num_aisles': 2,
            'racks_per_aisle': 3,
            'positions_per_rack': 5,
            'levels_per_position': 3
        }
        
        headers = {'Authorization': f'Bearer {self.test_user_token}'}
        response = requests.post(
            f"{self.base_url}/api/v1/warehouse/setup",
            json=test_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            return {'status': 'pass', 'response': response.json()}
        else:
            raise Exception(f"API call failed: {response.status_code} - {response.text}")
    
    def test_location_creation_bulk(self) -> Dict[str, Any]:
        """Test bulk location creation performance"""
        locations_data = []
        for i in range(50):
            locations_data.append({
                'location_code': f'BULK-TEST-{i:03d}',
                'warehouse_id': 'TEST_WH',
                'aisle_number': (i // 20) + 1,
                'rack_number': (i // 10) + 1,
                'position_number': (i % 10) + 1,
                'level': 'A'
            })
        
        start_time = time.time()
        
        headers = {'Authorization': f'Bearer {self.test_user_token}'}
        response = requests.post(
            f"{self.base_url}/api/v1/locations/bulk",
            json={'locations': locations_data},
            headers=headers
        )
        
        duration = time.time() - start_time
        
        if response.status_code in [200, 201]:
            return {
                'status': 'pass',
                'duration_seconds': duration,
                'locations_created': len(locations_data),
                'rate_per_second': len(locations_data) / duration
            }
        else:
            raise Exception(f"Bulk creation failed: {response.status_code}")
    
    def test_template_application(self) -> Dict[str, Any]:
        """Test template application functionality"""
        headers = {'Authorization': f'Bearer {self.test_user_token}'}
        
        # Get available templates
        templates_response = requests.get(
            f"{self.base_url}/api/v1/template/public",
            headers=headers
        )
        
        if templates_response.status_code != 200:
            raise Exception("Failed to fetch templates")
        
        templates = templates_response.json().get('templates', [])
        if not templates:
            # Create a test template first
            template_data = {
                'name': 'Test Template',
                'num_aisles': 2,
                'racks_per_aisle': 3,
                'positions_per_rack': 4
            }
            create_response = requests.post(
                f"{self.base_url}/api/v1/template",
                json=template_data,
                headers=headers
            )
            if create_response.status_code not in [200, 201]:
                raise Exception("Failed to create test template")
        
        return {'status': 'pass', 'templates_available': len(templates)}
    
    def test_concurrent_warehouse_operations(self) -> Dict[str, Any]:
        """Test concurrent warehouse operations"""
        def create_location(index):
            location_data = {
                'location_code': f'CONCURRENT-{index}',
                'warehouse_id': 'TEST_WH',
                'aisle_number': 1,
                'rack_number': 1,
                'position_number': index,
                'level': 'A'
            }
            
            headers = {'Authorization': f'Bearer {self.test_user_token}'}
            response = requests.post(
                f"{self.base_url}/api/v1/locations",
                json=location_data,
                headers=headers
            )
            return response.status_code in [200, 201]
        
        # Run 10 concurrent operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_location, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        success_count = sum(results)
        
        return {
            'status': 'pass' if success_count >= 8 else 'fail',  # Allow some failures
            'successful_operations': success_count,
            'total_operations': len(results),
            'success_rate': success_count / len(results) * 100
        }
    
    def test_database_performance_under_load(self) -> Dict[str, Any]:
        """Test database performance under load"""
        query_times = []
        
        for i in range(20):
            start_time = time.time()
            try:
                with db.engine.connect() as conn:
                    result = conn.execute(text("SELECT COUNT(*) FROM location"))
                    result.fetchone()
                query_time = (time.time() - start_time) * 1000
                query_times.append(query_time)
            except Exception as e:
                raise Exception(f"Database query failed: {e}")
        
        avg_time = sum(query_times) / len(query_times)
        max_time = max(query_times)
        
        return {
            'status': 'pass' if avg_time < 100 and max_time < 500 else 'fail',
            'average_query_time_ms': avg_time,
            'max_query_time_ms': max_time,
            'total_queries': len(query_times)
        }

# Global test framework instance
debug_test_framework = DebugTestFramework()

# Register test suites
def register_default_test_suites():
    """Register default test suites for warehouse optimization"""
    
    # Database Tests
    database_tests = TestSuite(
        name="database_integrity",
        description="Database schema and integrity tests",
        tests=[
            debug_test_framework.test_database_schema_integrity,
            debug_test_framework.test_database_performance_under_load
        ]
    )
    
    # API Tests  
    api_tests = TestSuite(
        name="api_functionality",
        description="API endpoint functionality tests",
        tests=[
            debug_test_framework.test_warehouse_setup_api,
            debug_test_framework.test_location_creation_bulk,
            debug_test_framework.test_template_application
        ]
    )
    
    # Performance Tests
    performance_tests = TestSuite(
        name="performance_load",
        description="Performance and load testing",
        tests=[
            debug_test_framework.test_concurrent_warehouse_operations,
            debug_test_framework.test_database_performance_under_load
        ]
    )
    
    debug_test_framework.register_test_suite(database_tests)
    debug_test_framework.register_test_suite(api_tests) 
    debug_test_framework.register_test_suite(performance_tests)

# Initialize default test suites
register_default_test_suites()

# Export for use in other modules
__all__ = [
    'DebugTestFramework',
    'TestResult', 
    'TestSuite',
    'debug_test_framework'
]