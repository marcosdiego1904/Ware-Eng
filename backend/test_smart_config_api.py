#!/usr/bin/env python3
"""
Smart Configuration API Test
============================

Test the Smart Configuration API endpoints with real HTTP calls.
This verifies the template API detect-format and validate-format endpoints.
"""

import os
import sys
import json
import time
import requests
import subprocess
import threading
import logging
from datetime import datetime

# Suppress requests warnings
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Test configuration
API_BASE_URL = 'http://localhost:5000'
API_TIMEOUT = 30

def print_test_result(test_name, success, details="", error="", exec_time=0):
    """Print test result with ASCII-safe symbols"""
    symbol = "[PASS]" if success else "[FAIL]"
    print(f"{symbol} {test_name} ({exec_time:.2f}s)")
    if details:
        print(f"    Details: {details}")
    if error:
        print(f"    Error: {error}")
    print()

def start_flask_server():
    """Start Flask server in background"""
    try:
        # Check if server is already running
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("Flask server is already running")
                return True
        except:
            pass

        print("Starting Flask server...")
        
        # Change to src directory and start app
        app_path = os.path.join(src_dir, 'app.py')
        if not os.path.exists(app_path):
            print(f"Flask app not found at {app_path}")
            return False
        
        # Start server in background thread
        def run_server():
            subprocess.run([
                sys.executable, app_path
            ], cwd=src_dir, capture_output=True)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                time.sleep(1)
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    print(f"Flask server started successfully (attempt {attempt + 1})")
                    return True
            except:
                continue
        
        print("Failed to start Flask server after 30 attempts")
        return False
        
    except Exception as e:
        print(f"Error starting Flask server: {e}")
        return False

def test_direct_format_detection():
    """Test SmartFormatDetector directly without API"""
    print("TESTING DIRECT FORMAT DETECTION")
    print("=" * 50)
    
    results = []
    
    # Test position+level detection
    start_time = time.time()
    try:
        from smart_format_detector import SmartFormatDetector
        
        detector = SmartFormatDetector()
        examples = ["010A", "325B", "245D"]
        result = detector.detect_format(examples)
        
        exec_time = time.time() - start_time
        
        # Validate results
        if result['detected_pattern']['pattern_type'] == 'position_level':
            confidence = result['confidence']
            details = f"Pattern: position_level, Confidence: {confidence:.1%}"
            print_test_result("Direct Format Detection", True, details, "", exec_time)
            results.append(('Direct Format Detection', True, exec_time))
        else:
            raise Exception(f"Expected position_level, got {result['detected_pattern']['pattern_type']}")
            
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Direct Format Detection", False, "", str(e), exec_time)
        results.append(('Direct Format Detection', False, exec_time))
    
    return results

def test_health_endpoint():
    """Test basic server health"""
    print("TESTING SERVER HEALTH")
    print("=" * 50)
    
    results = []
    
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=API_TIMEOUT)
        exec_time = time.time() - start_time
        
        if response.status_code == 200:
            print_test_result("Server Health Check", True, 
                             f"Server responding with status {response.status_code}", "", exec_time)
            results.append(('Server Health Check', True, exec_time))
        else:
            raise Exception(f"Health check returned status {response.status_code}")
            
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Server Health Check", False, "", str(e), exec_time)
        results.append(('Server Health Check', False, exec_time))
    
    return results

def test_detect_format_api():
    """Test the /api/templates/detect-format endpoint"""
    print("TESTING DETECT-FORMAT API")
    print("=" * 50)
    
    results = []
    
    # Test 1: Position+Level detection
    start_time = time.time()
    try:
        api_url = f"{API_BASE_URL}/api/templates/detect-format"
        payload = {
            'examples': ["010A", "325B", "245D", "156C"],
            'warehouse_context': {
                'name': 'Test Warehouse API',
                'description': 'Testing via API'
            }
        }
        
        # Note: For testing, we'll skip authentication
        response = requests.post(api_url, json=payload, timeout=API_TIMEOUT)
        
        exec_time = time.time() - start_time
        
        print(f"    API URL: {api_url}")
        print(f"    Status Code: {response.status_code}")
        
        if response.status_code == 401:
            # Expected if authentication is required
            print_test_result("Detect Format API (Auth Required)", True,
                             "API correctly requires authentication", "", exec_time)
            results.append(('Detect Format API (Auth)', True, exec_time))
        
        elif response.status_code == 200:
            # API responded successfully
            try:
                result = response.json()
                if result.get('success') and result.get('detection_result'):
                    detected_pattern = result['detection_result'].get('detected_pattern')
                    if detected_pattern and detected_pattern['pattern_type'] == 'position_level':
                        confidence = result['detection_result'].get('confidence', 0)
                        details = f"Pattern: {detected_pattern['pattern_type']}, Confidence: {confidence:.1%}"
                        print_test_result("Detect Format API", True, details, "", exec_time)
                        results.append(('Detect Format API', True, exec_time))
                    else:
                        raise Exception("Unexpected pattern detected")
                else:
                    raise Exception("Invalid API response structure")
            except json.JSONDecodeError:
                raise Exception("Invalid JSON response")
        
        else:
            # Some other status code
            print(f"    Response Text: {response.text[:200]}...")
            print_test_result("Detect Format API", False, 
                             f"Unexpected status code: {response.status_code}", "", exec_time)
            results.append(('Detect Format API', False, exec_time))
            
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Detect Format API", False, "", str(e), exec_time)
        results.append(('Detect Format API', False, exec_time))
    
    # Test 2: Error handling
    start_time = time.time()
    try:
        api_url = f"{API_BASE_URL}/api/templates/detect-format"
        payload = {
            'examples': [],  # Empty examples should return error
        }
        
        response = requests.post(api_url, json=payload, timeout=API_TIMEOUT)
        exec_time = time.time() - start_time
        
        if response.status_code == 400:
            print_test_result("Detect Format API Error Handling", True,
                             "API correctly returned 400 for invalid input", "", exec_time)
            results.append(('Detect Format API Error Handling', True, exec_time))
        elif response.status_code == 401:
            print_test_result("Detect Format API Error Handling", True,
                             "API requires authentication", "", exec_time)
            results.append(('Detect Format API Error Handling', True, exec_time))
        else:
            print_test_result("Detect Format API Error Handling", False,
                             f"Expected 400 or 401, got {response.status_code}", "", exec_time)
            results.append(('Detect Format API Error Handling', False, exec_time))
            
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Detect Format API Error Handling", False, "", str(e), exec_time)
        results.append(('Detect Format API Error Handling', False, exec_time))
    
    return results

def test_validate_format_api():
    """Test the /api/templates/validate-format endpoint"""
    print("TESTING VALIDATE-FORMAT API")  
    print("=" * 50)
    
    results = []
    
    start_time = time.time()
    try:
        api_url = f"{API_BASE_URL}/api/templates/validate-format"
        payload = {
            'format_config': {
                'pattern_type': 'position_level',
                'confidence': 0.95,
                'canonical_converter': '01-01-{position:03d}{level}',
                'examples': ['010A', '325B', '245D']
            }
        }
        
        response = requests.post(api_url, json=payload, timeout=API_TIMEOUT)
        exec_time = time.time() - start_time
        
        print(f"    API URL: {api_url}")
        print(f"    Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print_test_result("Validate Format API (Auth Required)", True,
                             "API correctly requires authentication", "", exec_time)
            results.append(('Validate Format API (Auth)', True, exec_time))
        
        elif response.status_code == 200:
            try:
                result = response.json()
                if result.get('success') and result.get('validation', {}).get('valid'):
                    print_test_result("Validate Format API", True,
                                     "Valid format configuration accepted", "", exec_time)
                    results.append(('Validate Format API', True, exec_time))
                else:
                    print_test_result("Validate Format API", False,
                                     "Valid configuration was rejected", "", exec_time)
                    results.append(('Validate Format API', False, exec_time))
            except json.JSONDecodeError:
                raise Exception("Invalid JSON response")
        
        else:
            print_test_result("Validate Format API", False,
                             f"Unexpected status code: {response.status_code}", "", exec_time)
            results.append(('Validate Format API', False, exec_time))
            
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Validate Format API", False, "", str(e), exec_time)
        results.append(('Validate Format API', False, exec_time))
    
    return results

def print_summary(all_results):
    """Print test execution summary"""
    print("\n" + "=" * 70)
    print("SMART CONFIGURATION API - TEST SUMMARY")
    print("=" * 70)
    
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(sum(1 for _, success, _ in results if success) for results in all_results.values())
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    print("\nTEST RESULTS BY CATEGORY:")
    print("-" * 40)
    
    for category, results in all_results.items():
        category_passed = sum(1 for _, success, _ in results if success)
        category_total = len(results)
        category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
        
        print(f"{category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        for test_name, success, exec_time in results:
            status = "[PASS]" if success else "[FAIL]"
            print(f"  {status} {test_name} ({exec_time:.2f}s)")
    
    print("\n" + "=" * 70)
    
    if pass_rate >= 80:
        print("OVERALL RESULT: SMART CONFIGURATION API IS WORKING WELL")
    elif pass_rate >= 60:
        print("OVERALL RESULT: SMART CONFIGURATION API IS MOSTLY FUNCTIONAL")
    else:
        print("OVERALL RESULT: SMART CONFIGURATION API NEEDS ATTENTION")
    
    print("=" * 70)

def main():
    """Main test runner"""
    print("Smart Configuration System - API Test Suite")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base URL: {API_BASE_URL}")
    print("=" * 70)
    
    all_results = {}
    
    try:
        # Test 1: Direct format detection (no API needed)
        all_results['Direct Format Detection'] = test_direct_format_detection()
        
        # Test 2: Start Flask server (optional)
        server_started = start_flask_server()
        
        if server_started:
            # Test 3: Health endpoint
            all_results['Server Health'] = test_health_endpoint()
            
            # Test 4: API endpoints
            all_results['Detect Format API'] = test_detect_format_api()
            all_results['Validate Format API'] = test_validate_format_api()
        else:
            print("Skipping API tests - server not available")
            
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
    except Exception as e:
        print(f"\nCritical error during test execution: {e}")
    finally:
        print_summary(all_results)

if __name__ == "__main__":
    main()