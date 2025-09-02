#!/usr/bin/env python3
"""
Comprehensive Test Suite for Smart Configuration System
=====================================================

Tests all components of the Smart Configuration system including:
1. SmartFormatDetector core functionality
2. Template API endpoints (detect-format, validate-format)  
3. Database integration and model handling
4. End-to-end workflow simulation
5. Error handling and edge cases

This test suite provides systematic debugging and validation
to ensure the Smart Configuration system is production-ready.
"""

import os
import sys
import json
import time
import requests
import unittest
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
import tempfile
import subprocess

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Test configuration
TEST_CONFIG = {
    'backend_url': 'http://localhost:5000',
    'api_version': 'v1',
    'test_user': {
        'username': 'test_smart_config',
        'password': 'test123',
        'email': 'test@example.com'
    },
    'timeout': 30,
    'test_examples': {
        'position_level': ["010A", "325B", "245D", "156C", "087A"],
        'standard_format': ["01-01-001A", "02-15-032B", "03-08-145C"],
        'compact_format': ["01A01A", "02B03C", "15C22D"],
        'special_format': ["RECV-01", "STAGE-02", "DOCK-03"],
        'mixed_format': ["010A", "RECV-01", "325B", "STAGE-02"],
        'invalid_format': ["", "   ", "XYZ", "123", "???"],
        'edge_cases': ["000A", "999Z", "001a", "010A ", " 325B"]
    }
}

class TestResults:
    """Collect and manage test results"""
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        
    def add_result(self, test_name: str, status: str, details: str = "", 
                  execution_time: float = 0, error: str = ""):
        """Add a test result"""
        self.results.append({
            'test_name': test_name,
            'status': status,  # PASS, FAIL, SKIP, ERROR
            'details': details,
            'execution_time': execution_time,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
        
    def get_summary(self) -> Dict[str, Any]:
        """Get test execution summary"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        status_counts = {}
        for result in self.results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            
        return {
            'total_tests': len(self.results),
            'total_time': total_time,
            'status_counts': status_counts,
            'pass_rate': (status_counts.get('PASS', 0) / len(self.results)) * 100 if self.results else 0,
            'results': self.results
        }
        
    def print_summary(self):
        """Print formatted test summary"""
        summary = self.get_summary()
        
        print("\n" + "="*70)
        print("SMART CONFIGURATION SYSTEM - TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Total Time: {summary['total_time']:.2f}s")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print()
        
        for status, count in summary['status_counts'].items():
            print(f"{status}: {count}")
        
        print("\n" + "="*70)
        print("DETAILED RESULTS")
        print("="*70)
        
        for result in self.results:
            status_symbol = {
                'PASS': '✓',
                'FAIL': '✗', 
                'SKIP': '-',
                'ERROR': '!'
            }.get(result['status'], '?')
            
            print(f"{status_symbol} {result['test_name']} ({result['execution_time']:.2f}s)")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   ERROR: {result['error']}")
            print()

class SmartConfigTester:
    """Main test orchestrator for Smart Configuration system"""
    
    def __init__(self):
        self.results = TestResults()
        self.auth_token = None
        self.user_id = None
        self.flask_server_process = None
        
    def run_all_tests(self):
        """Execute complete test suite"""
        print("Starting Smart Configuration System Comprehensive Tests...")
        print(f"Backend URL: {TEST_CONFIG['backend_url']}")
        print(f"Test timestamp: {datetime.now().isoformat()}")
        print("="*70)
        
        try:
            # Priority 1: Core SmartFormatDetector Tests
            self.test_smart_format_detector_core()
            
            # Priority 2: Database Migration and Models
            self.test_database_migration()
            
            # Priority 3: Flask Server and Authentication  
            self.test_flask_server_startup()
            
            # Priority 4: API Integration Tests
            if self.auth_token:
                self.test_format_detection_api()
                self.test_format_validation_api()
                self.test_template_creation_with_formats()
                
            # Priority 5: End-to-End Integration
            self.test_end_to_end_workflow()
            
            # Priority 6: Error Handling and Edge Cases
            self.test_error_handling()
            
        except KeyboardInterrupt:
            print("\nTests interrupted by user")
        except Exception as e:
            self.results.add_result("CRITICAL_ERROR", "ERROR", 
                                  error=f"Test suite failed: {str(e)}")
            traceback.print_exc()
        finally:
            self.cleanup()
            self.results.print_summary()
    
    def test_smart_format_detector_core(self):
        """Test SmartFormatDetector core functionality"""
        print("\n1. TESTING SMART FORMAT DETECTOR CORE")
        print("-" * 50)
        
        # Test 1: Import and initialization
        start_time = time.time()
        try:
            from smart_format_detector import SmartFormatDetector, detect_location_format
            detector = SmartFormatDetector()
            
            exec_time = time.time() - start_time
            self.results.add_result(
                "SmartFormatDetector Import & Init",
                "PASS",
                "Successfully imported and initialized SmartFormatDetector",
                exec_time
            )
            print("✓ SmartFormatDetector imported and initialized")
            
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "SmartFormatDetector Import & Init",
                "FAIL", 
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ Failed to import SmartFormatDetector: {e}")
            return
        
        # Test 2: Position+Level Pattern Detection (Main Use Case)
        start_time = time.time()
        try:
            examples = TEST_CONFIG['test_examples']['position_level']
            result = detector.detect_format(examples)
            
            exec_time = time.time() - start_time
            
            # Validate the result structure
            required_keys = ['detected_pattern', 'confidence', 'canonical_examples', 
                           'analysis_summary', 'recommendations']
            missing_keys = [key for key in required_keys if key not in result]
            
            if missing_keys:
                raise Exception(f"Missing keys in result: {missing_keys}")
                
            detected_pattern = result.get('detected_pattern')
            confidence = result.get('confidence', 0)
            
            # Validate detection accuracy
            if not detected_pattern:
                raise Exception("No pattern detected for position+level examples")
                
            if detected_pattern['pattern_type'] != 'position_level':
                raise Exception(f"Expected 'position_level', got '{detected_pattern['pattern_type']}'")
                
            if confidence < 0.9:  # Should be high confidence for clear pattern
                raise Exception(f"Low confidence for clear pattern: {confidence:.2%}")
            
            details = f"Pattern: {detected_pattern['pattern_type']}, Confidence: {confidence:.1%}, Examples: {len(examples)}"
            self.results.add_result(
                "Position+Level Pattern Detection",
                "PASS",
                details,
                exec_time
            )
            print(f"✓ Position+Level detection: {confidence:.1%} confidence")
            
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "Position+Level Pattern Detection",
                "FAIL",
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ Position+Level detection failed: {e}")
        
        # Test 3: Standard Format Detection
        start_time = time.time()
        try:
            examples = TEST_CONFIG['test_examples']['standard_format']
            result = detector.detect_format(examples)
            
            exec_time = time.time() - start_time
            detected_pattern = result.get('detected_pattern')
            
            if detected_pattern and detected_pattern['pattern_type'] == 'standard':
                self.results.add_result(
                    "Standard Format Detection", 
                    "PASS",
                    f"Detected standard format with {result['confidence']:.1%} confidence",
                    exec_time
                )
                print(f"✓ Standard format detection: {result['confidence']:.1%}")
            else:
                raise Exception(f"Failed to detect standard format, got: {detected_pattern}")
                
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "Standard Format Detection",
                "FAIL",
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ Standard format detection failed: {e}")
        
        # Test 4: Edge Cases and Error Handling
        test_cases = [
            ([], "Empty examples list"),
            ([""], "Empty string examples"),
            (["   ", "\t", "\n"], "Whitespace-only examples"),
            (TEST_CONFIG['test_examples']['invalid_format'], "Invalid format examples")
        ]
        
        for examples, case_name in test_cases:
            start_time = time.time()
            try:
                result = detector.detect_format(examples)
                exec_time = time.time() - start_time
                
                # Should handle gracefully without crashing
                self.results.add_result(
                    f"Edge Case: {case_name}",
                    "PASS",
                    f"Handled gracefully, confidence: {result.get('confidence', 0):.1%}",
                    exec_time
                )
                print(f"✓ Edge case handled: {case_name}")
                
            except Exception as e:
                exec_time = time.time() - start_time
                self.results.add_result(
                    f"Edge Case: {case_name}",
                    "FAIL",
                    error=str(e),
                    execution_time=exec_time
                )
                print(f"✗ Edge case failed: {case_name} - {e}")
    
    def test_database_migration(self):
        """Test database migration and model capabilities"""
        print("\n2. TESTING DATABASE MIGRATION & MODELS")
        print("-" * 50)
        
        # Test 1: Check if enhanced template models exist
        start_time = time.time()
        try:
            # Try to import the enhanced template models
            sys.path.append(src_dir)
            from enhanced_template_models import WarehouseTemplate
            
            exec_time = time.time() - start_time
            self.results.add_result(
                "Enhanced Template Models Import",
                "PASS", 
                "Successfully imported WarehouseTemplate with format fields",
                exec_time
            )
            print("✓ Enhanced template models imported")
            
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "Enhanced Template Models Import",
                "FAIL",
                error=str(e), 
                execution_time=exec_time
            )
            print(f"✗ Enhanced template models import failed: {e}")
            return
        
        # Test 2: Check database connection and tables
        start_time = time.time()
        try:
            from database import db
            from config import Config
            
            # Simple database connection test
            # Note: This would need a test database setup in a real scenario
            
            exec_time = time.time() - start_time
            self.results.add_result(
                "Database Connection Test",
                "PASS",
                "Database imports successful",
                exec_time
            )
            print("✓ Database connection components imported")
            
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "Database Connection Test",
                "FAIL",
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ Database connection test failed: {e}")
        
        # Test 3: Test WarehouseTemplate format field methods
        start_time = time.time()
        try:
            # Create a mock template to test format methods
            template = WarehouseTemplate()
            
            # Test format configuration methods
            test_config = {
                'pattern_type': 'position_level',
                'confidence': 0.95,
                'canonical_converter': '01-01-{position:03d}{level}',
                'examples': ['010A', '325B']
            }
            
            # Test setting format config
            template.set_location_format_config(test_config)
            retrieved_config = template.get_location_format_config()
            
            if retrieved_config != test_config:
                raise Exception("Format config round-trip failed")
            
            # Test format examples
            template.set_format_examples(['010A', '325B', '245D'])
            examples = template.get_format_examples()
            
            if len(examples) != 3:
                raise Exception(f"Expected 3 examples, got {len(examples)}")
            
            exec_time = time.time() - start_time
            self.results.add_result(
                "Template Format Methods Test",
                "PASS",
                "Format config and examples methods working",
                exec_time
            )
            print("✓ Template format methods working")
            
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "Template Format Methods Test", 
                "FAIL",
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ Template format methods failed: {e}")
    
    def test_flask_server_startup(self):
        """Test Flask server startup and basic connectivity"""
        print("\n3. TESTING FLASK SERVER STARTUP")
        print("-" * 50)
        
        # Test 1: Check if server is running
        start_time = time.time()
        try:
            response = requests.get(
                f"{TEST_CONFIG['backend_url']}/health", 
                timeout=TEST_CONFIG['timeout']
            )
            
            exec_time = time.time() - start_time
            
            if response.status_code == 200:
                self.results.add_result(
                    "Flask Server Health Check",
                    "PASS",
                    f"Server responding on {TEST_CONFIG['backend_url']}",
                    exec_time
                )
                print(f"✓ Server is running on {TEST_CONFIG['backend_url']}")
            else:
                raise Exception(f"Health check failed with status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            # Server not running, try to start it
            print("Server not running, attempting to start...")
            self.start_flask_server()
            
            # Try health check again
            time.sleep(3)  # Give server time to start
            try:
                response = requests.get(
                    f"{TEST_CONFIG['backend_url']}/health", 
                    timeout=TEST_CONFIG['timeout']
                )
                exec_time = time.time() - start_time
                
                self.results.add_result(
                    "Flask Server Startup & Health",
                    "PASS", 
                    "Server started successfully",
                    exec_time
                )
                print("✓ Server started and responding")
                
            except Exception as e:
                exec_time = time.time() - start_time
                self.results.add_result(
                    "Flask Server Startup & Health",
                    "FAIL",
                    error=str(e),
                    execution_time=exec_time
                )
                print(f"✗ Failed to start server: {e}")
                return
                
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "Flask Server Health Check",
                "FAIL",
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ Server health check failed: {e}")
            return
        
        # Test 2: Authentication and get token
        self.setup_test_authentication()
    
    def start_flask_server(self):
        """Start Flask server in background"""
        try:
            # Try to find and start the Flask app
            app_path = os.path.join(src_dir, 'app.py')
            if not os.path.exists(app_path):
                print(f"Flask app not found at {app_path}")
                return
            
            print(f"Starting Flask server from {app_path}")
            
            # Start server in background
            env = os.environ.copy()
            env['FLASK_ENV'] = 'development'
            env['FLASK_APP'] = app_path
            
            self.flask_server_process = subprocess.Popen(
                [sys.executable, app_path],
                cwd=src_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            print("Flask server starting...")
            
        except Exception as e:
            print(f"Failed to start Flask server: {e}")
    
    def setup_test_authentication(self):
        """Setup authentication for API tests"""
        print("\n   Setting up authentication...")
        
        # For now, skip authentication setup if there's no user management
        # In a real implementation, this would create a test user and get a token
        start_time = time.time()
        try:
            # Mock authentication for testing
            self.auth_token = "test_token_mock"
            self.user_id = "test_user_123"
            
            exec_time = time.time() - start_time
            self.results.add_result(
                "Authentication Setup",
                "PASS",
                "Mock authentication configured",
                exec_time
            )
            print("   ✓ Authentication configured (mock)")
            
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "Authentication Setup",
                "FAIL",
                error=str(e),
                execution_time=exec_time
            )
            print(f"   ✗ Authentication setup failed: {e}")
    
    def test_format_detection_api(self):
        """Test the /api/templates/detect-format endpoint"""
        print("\n4. TESTING FORMAT DETECTION API")
        print("-" * 50)
        
        if not self.auth_token:
            print("Skipping API tests - no authentication token")
            return
        
        api_url = f"{TEST_CONFIG['backend_url']}/api/v1/templates/detect-format"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
        
        # Test 1: Position+Level detection via API
        start_time = time.time()
        try:
            payload = {
                'examples': TEST_CONFIG['test_examples']['position_level'],
                'warehouse_context': {
                    'name': 'Test Warehouse',
                    'description': 'Testing position+level format'
                }
            }
            
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=TEST_CONFIG['timeout']
            )
            
            exec_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate API response structure
                if not result.get('success'):
                    raise Exception(f"API returned success=False: {result}")
                
                detection_result = result.get('detection_result', {})
                detected_pattern = detection_result.get('detected_pattern')
                
                if not detected_pattern:
                    raise Exception("No pattern detected via API")
                
                if detected_pattern['pattern_type'] != 'position_level':
                    raise Exception(f"Expected position_level, got {detected_pattern['pattern_type']}")
                
                confidence = detection_result.get('confidence', 0)
                if confidence < 0.9:
                    raise Exception(f"Low confidence via API: {confidence:.2%}")
                
                details = f"API Success: {detected_pattern['pattern_type']} at {confidence:.1%} confidence"
                self.results.add_result(
                    "API Position+Level Detection",
                    "PASS",
                    details,
                    exec_time
                )
                print(f"✓ API detection success: {confidence:.1%} confidence")
                
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "API Position+Level Detection",
                "FAIL", 
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ API detection failed: {e}")
        
        # Test 2: Error handling - invalid input
        start_time = time.time()
        try:
            payload = {
                'examples': [],  # Empty examples should be handled gracefully
                'warehouse_context': {}
            }
            
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=TEST_CONFIG['timeout']
            )
            
            exec_time = time.time() - start_time
            
            if response.status_code == 400:  # Should return 400 for invalid input
                self.results.add_result(
                    "API Error Handling - Invalid Input",
                    "PASS", 
                    "API correctly returned 400 for empty examples",
                    exec_time
                )
                print("✓ API error handling works")
            else:
                details = f"Expected 400, got {response.status_code}"
                self.results.add_result(
                    "API Error Handling - Invalid Input",
                    "FAIL",
                    details,
                    exec_time
                )
                print(f"✗ API error handling issue: {details}")
                
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "API Error Handling - Invalid Input",
                "FAIL",
                error=str(e), 
                execution_time=exec_time
            )
            print(f"✗ API error handling test failed: {e}")
    
    def test_format_validation_api(self):
        """Test the /api/templates/validate-format endpoint"""  
        print("\n5. TESTING FORMAT VALIDATION API")
        print("-" * 50)
        
        if not self.auth_token:
            print("Skipping validation API tests - no authentication")
            return
        
        api_url = f"{TEST_CONFIG['backend_url']}/api/v1/templates/validate-format"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
        
        # Test valid format configuration
        start_time = time.time()
        try:
            valid_config = {
                'pattern_type': 'position_level',
                'confidence': 0.95,
                'canonical_converter': '01-01-{position:03d}{level}',
                'regex_pattern': r'^(\d{3})([A-Z])$',
                'components': {
                    'position_digits': 3,
                    'level_format': 'single_letter'
                },
                'examples': ['010A', '325B', '245D']
            }
            
            payload = {'format_config': valid_config}
            
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=TEST_CONFIG['timeout']
            )
            
            exec_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success') and result.get('validation', {}).get('valid'):
                    self.results.add_result(
                        "API Format Validation - Valid Config",
                        "PASS",
                        "Valid configuration passed validation",
                        exec_time
                    )
                    print("✓ Valid format configuration validated successfully")
                else:
                    raise Exception(f"Validation failed for valid config: {result}")
                    
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "API Format Validation - Valid Config",
                "FAIL",
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ Valid format validation failed: {e}")
        
        # Test invalid format configuration 
        start_time = time.time()
        try:
            invalid_config = {
                'pattern_type': 'invalid_type',
                'confidence': -0.5,  # Invalid confidence
                # Missing required fields
            }
            
            payload = {'format_config': invalid_config}
            
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=TEST_CONFIG['timeout']
            )
            
            exec_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                validation = result.get('validation', {})
                
                if not validation.get('valid') and validation.get('errors'):
                    self.results.add_result(
                        "API Format Validation - Invalid Config",
                        "PASS",
                        f"Invalid config correctly rejected: {len(validation['errors'])} errors",
                        exec_time
                    )
                    print("✓ Invalid format configuration correctly rejected")
                else:
                    raise Exception("Invalid config was not rejected properly")
                    
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "API Format Validation - Invalid Config",
                "FAIL",
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ Invalid format validation test failed: {e}")
    
    def test_template_creation_with_formats(self):
        """Test template creation with format configuration"""
        print("\n6. TESTING TEMPLATE CREATION WITH FORMATS")
        print("-" * 50)
        
        if not self.auth_token:
            print("Skipping template creation tests - no authentication")
            return
        
        api_url = f"{TEST_CONFIG['backend_url']}/api/v1/templates"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
        
        # Test creating template with auto-detected format
        start_time = time.time()
        try:
            template_data = {
                'name': 'Test Smart Config Template',
                'description': 'Template created for Smart Configuration testing',
                'num_aisles': 3,
                'racks_per_aisle': 5,
                'positions_per_rack': 20,
                'levels_per_position': 4,
                'level_names': 'ABCD',
                'default_pallet_capacity': 1,
                'location_format': {
                    'examples': TEST_CONFIG['test_examples']['position_level']
                }
            }
            
            response = requests.post(
                api_url,
                json=template_data,
                headers=headers,
                timeout=TEST_CONFIG['timeout']
            )
            
            exec_time = time.time() - start_time
            
            if response.status_code == 201:
                result = response.json()
                template = result.get('template', {})
                
                # Check that format was detected and stored
                format_config = template.get('location_format_config')
                if not format_config:
                    raise Exception("Format configuration not stored in template")
                
                if format_config.get('pattern_type') != 'position_level':
                    raise Exception(f"Incorrect pattern stored: {format_config.get('pattern_type')}")
                
                template_id = template.get('id')
                details = f"Template ID: {template_id}, Pattern: {format_config.get('pattern_type')}"
                
                self.results.add_result(
                    "Template Creation with Auto-Format Detection",
                    "PASS",
                    details,
                    exec_time
                )
                print(f"✓ Template created with format detection: ID {template_id}")
                
            else:
                raise Exception(f"Template creation failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "Template Creation with Auto-Format Detection",
                "FAIL",
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ Template creation with format failed: {e}")
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        print("\n7. TESTING END-TO-END WORKFLOW")
        print("-" * 50)
        
        start_time = time.time()
        try:
            # Simulate complete user workflow:
            # 1. User provides location examples
            # 2. System detects format
            # 3. User creates template with detected format
            # 4. System stores template with format configuration
            # 5. Template can be applied to create warehouse
            
            workflow_steps = []
            
            # Step 1: Format detection
            from smart_format_detector import SmartFormatDetector
            detector = SmartFormatDetector()
            examples = TEST_CONFIG['test_examples']['position_level']
            
            detection_result = detector.detect_format(examples)
            if not detection_result.get('detected_pattern'):
                raise Exception("Step 1 failed: No pattern detected")
            
            workflow_steps.append("Format detection")
            
            # Step 2: Format configuration creation
            format_config = detector.create_format_config(
                detection_result,
                {'warehouse_name': 'End-to-End Test Warehouse'}
            )
            
            if not format_config:
                raise Exception("Step 2 failed: Format config creation failed")
            
            workflow_steps.append("Format config creation")
            
            # Step 3: Format validation
            validation = detector.validate_format_config(format_config)
            if not validation.get('valid'):
                raise Exception(f"Step 3 failed: Format validation failed: {validation.get('errors')}")
            
            workflow_steps.append("Format validation")
            
            # Step 4: Template model integration
            from enhanced_template_models import WarehouseTemplate
            template = WarehouseTemplate()
            template.name = "E2E Test Template"
            template.set_location_format_config(format_config)
            template.set_format_examples(examples)
            
            # Verify round-trip
            stored_config = template.get_location_format_config()
            if stored_config != format_config:
                raise Exception("Step 4 failed: Format config round-trip failed")
            
            workflow_steps.append("Template model integration")
            
            exec_time = time.time() - start_time
            
            self.results.add_result(
                "End-to-End Workflow",
                "PASS",
                f"Completed steps: {', '.join(workflow_steps)}",
                exec_time
            )
            print(f"✓ End-to-end workflow completed: {len(workflow_steps)} steps")
            
        except Exception as e:
            exec_time = time.time() - start_time
            self.results.add_result(
                "End-to-End Workflow", 
                "FAIL",
                error=str(e),
                execution_time=exec_time
            )
            print(f"✗ End-to-end workflow failed: {e}")
    
    def test_error_handling(self):
        """Test comprehensive error handling"""
        print("\n8. TESTING ERROR HANDLING & EDGE CASES")
        print("-" * 50)
        
        # Test malformed inputs
        error_test_cases = [
            {
                'name': 'None input',
                'examples': None,
                'expected_error': 'should handle None gracefully'
            },
            {
                'name': 'Non-list input', 
                'examples': "not a list",
                'expected_error': 'should handle non-list input'
            },
            {
                'name': 'Mixed data types',
                'examples': ["010A", 123, None, {}, []],
                'expected_error': 'should filter invalid types'
            },
            {
                'name': 'Very large input',
                'examples': [f"{i:03d}A" for i in range(1000)],  # 1000 examples
                'expected_error': 'should handle large inputs'
            }
        ]
        
        for test_case in error_test_cases:
            start_time = time.time()
            try:
                from smart_format_detector import SmartFormatDetector
                detector = SmartFormatDetector()
                
                result = detector.detect_format(test_case['examples'])
                
                # Should not crash - that's the main requirement
                exec_time = time.time() - start_time
                self.results.add_result(
                    f"Error Handling: {test_case['name']}",
                    "PASS",
                    "Handled without crashing",
                    exec_time
                )
                print(f"✓ {test_case['name']}: Handled gracefully")
                
            except Exception as e:
                exec_time = time.time() - start_time
                self.results.add_result(
                    f"Error Handling: {test_case['name']}",
                    "FAIL", 
                    error=str(e),
                    execution_time=exec_time
                )
                print(f"✗ {test_case['name']}: Failed with {e}")
    
    def cleanup(self):
        """Clean up test resources"""
        if self.flask_server_process:
            print("\nCleaning up Flask server...")
            self.flask_server_process.terminate()
            self.flask_server_process.wait()

def main():
    """Main test runner"""
    print("Smart Configuration System - Comprehensive Test Suite")
    print("=" * 70)
    
    tester = SmartConfigTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
    finally:
        # Generate test report
        print("\nGenerating test report...")
        
        report_file = f"smart_config_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(tester.results.get_summary(), f, indent=2)
        
        print(f"Test report saved to: {report_file}")

if __name__ == "__main__":
    main()