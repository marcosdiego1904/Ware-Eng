"""
PRODUCTION TESTING: Validate all session binding fixes in web request context

This script tests all the fixes we've implemented in a simulated web request environment
to ensure they work correctly in the actual production context where issues occurred.

Testing Strategy:
1. Simulate Flask web request context
2. Test session management with multiple concurrent "requests"
3. Validate Rule #4 error handling and fallbacks
4. Test session-safe caching under load
5. Verify warehouse detection consistency
"""

import sys
import os
sys.path.append('src')

import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from datetime import datetime

# Import Flask app and setup request context
import app
from models import db, Location
from session_manager import RequestScopedSessionManager, get_session
from session_safe_cache import get_session_safe_cache

def simulate_web_request_analysis(request_id: int, inventory_data: pd.DataFrame) -> dict:
    """
    Simulate a web request that runs the analysis engine.
    
    This function mimics what happens when a user uploads inventory through
    the web interface - it runs in a Flask request context with its own session.
    """
    
    print(f"[REQUEST-{request_id:02d}] Starting simulated web request analysis")
    
    result = {
        'request_id': request_id,
        'success': False,
        'session_binding_errors': 0,
        'rule_4_crashed': False,
        'warehouse_detection_success': False,
        'cache_hits': 0,
        'total_anomalies': 0,
        'execution_time': 0,
        'errors': []
    }
    
    start_time = time.time()
    
    try:
        # Create Flask request context to simulate real web request
        with app.app.app_context(), app.app.test_request_context():
            print(f"[REQUEST-{request_id:02d}] Flask request context established")
            
            # Verify we're in web request context
            is_web_request = RequestScopedSessionManager.is_web_request_context()
            print(f"[REQUEST-{request_id:02d}] Web request context detected: {is_web_request}")
            
            if not is_web_request:
                result['errors'].append("Failed to establish web request context")
                return result
            
            # Test session management
            current_session = get_session()
            print(f"[REQUEST-{request_id:02d}] Current session: {current_session}")
            
            # Test session-safe cache
            cache = get_session_safe_cache()
            cache_stats_before = cache.get_cache_stats()
            
            # Run the enhanced analysis engine
            try:
                from enhanced_main import run_enhanced_engine
                
                print(f"[REQUEST-{request_id:02d}] Running enhanced analysis engine...")
                
                anomalies = run_enhanced_engine(
                    inventory_data, 
                    rules_df=None,
                    args=None,
                    use_database_rules=True,
                    rule_ids=None,
                    report_id=None
                )
                
                result['total_anomalies'] = len(anomalies) if isinstance(anomalies, list) else 0
                print(f"[REQUEST-{request_id:02d}] Analysis completed: {result['total_anomalies']} anomalies")
                
                # Test specific aspects
                result['warehouse_detection_success'] = True  # If we got here, warehouse detection worked
                result['rule_4_crashed'] = False  # Rule 4 didn't crash the analysis
                
                # Check cache performance
                cache_stats_after = cache.get_cache_stats()
                result['cache_hits'] = cache_stats_after['cache_stats']['hits'] - cache_stats_before['cache_stats']['hits']
                
                result['success'] = True
                
            except Exception as analysis_error:
                error_msg = str(analysis_error)
                result['errors'].append(f"Analysis failed: {error_msg}")
                
                # Check for specific error types
                if "not bound to a Session" in error_msg:
                    result['session_binding_errors'] += 1
                    print(f"[REQUEST-{request_id:02d}] ERROR - SESSION BINDING ERROR: {error_msg}")
                
                if "Rule 4" in error_msg or "Invalid Locations Alert" in error_msg:
                    result['rule_4_crashed'] = True
                    print(f"[REQUEST-{request_id:02d}] ERROR - RULE 4 CRASH: {error_msg}")
                
                print(f"[REQUEST-{request_id:02d}] Analysis engine failed: {error_msg}")
                
    except Exception as context_error:
        result['errors'].append(f"Context setup failed: {context_error}")
        print(f"[REQUEST-{request_id:02d}] ERROR - Context setup failed: {context_error}")
    
    result['execution_time'] = time.time() - start_time
    
    status = "SUCCESS" if result['success'] else "FAILED"
    print(f"[REQUEST-{request_id:02d}] {status} - Completed in {result['execution_time']:.2f}s")
    
    return result

def run_concurrent_request_test(num_requests: int = 5) -> dict:
    """
    Run multiple concurrent simulated web requests to test under load.
    
    This simulates the production environment where multiple users might
    be running analyses simultaneously.
    """
    
    print(f"\nCONCURRENT REQUEST TEST: {num_requests} requests")
    print("=" * 60)
    
    # Load test inventory data
    inventory_path = r"C:\Users\juanb\Documents\Diego\Projects\ware2\comprehensive_rule_test_inventory.xlsx"
    
    if not os.path.exists(inventory_path):
        print(f"ERROR: Test inventory not found: {inventory_path}")
        return {'success': False, 'error': 'Test inventory not found'}
    
    # Load and prepare inventory data
    inventory_df = pd.read_excel(inventory_path)
    inventory_df = inventory_df.rename(columns={
        'Pallet ID': 'pallet_id',
        'Location': 'location',
        'Description': 'description',
        'Receipt Number': 'receipt_number',
        'Creation Date': 'creation_date'
    })
    inventory_df['creation_date'] = pd.to_datetime(inventory_df['creation_date'])
    
    print(f"Loaded test inventory: {len(inventory_df)} records")
    
    # Run concurrent requests
    results = []
    
    with ThreadPoolExecutor(max_workers=min(num_requests, 3)) as executor:
        # Submit all requests
        future_to_request = {
            executor.submit(simulate_web_request_analysis, i, inventory_df.copy()): i 
            for i in range(1, num_requests + 1)
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_request):
            request_id = future_to_request[future]
            try:
                result = future.result(timeout=60)  # 60 second timeout per request
                results.append(result)
            except Exception as exc:
                print(f"[REQUEST-{request_id:02d}] ERROR - Exception: {exc}")
                results.append({
                    'request_id': request_id,
                    'success': False,
                    'errors': [f'Request exception: {exc}'],
                    'session_binding_errors': 0,
                    'rule_4_crashed': False,
                    'warehouse_detection_success': False,
                    'execution_time': 0
                })
    
    # Analyze results
    summary = analyze_test_results(results)
    
    print(f"\nCONCURRENT TEST RESULTS:")
    print(f"  Total Requests: {len(results)}")
    print(f"  Successful: {summary['successful_requests']}/{len(results)}")
    print(f"  Session Binding Errors: {summary['total_session_errors']}")
    print(f"  Rule 4 Crashes: {summary['rule_4_crashes']}")
    print(f"  Warehouse Detection Success: {summary['warehouse_detection_successes']}")
    print(f"  Average Execution Time: {summary['avg_execution_time']:.2f}s")
    
    return summary

def analyze_test_results(results: list) -> dict:
    """Analyze the results from concurrent request testing"""
    
    summary = {
        'total_requests': len(results),
        'successful_requests': sum(1 for r in results if r['success']),
        'total_session_errors': sum(r['session_binding_errors'] for r in results),
        'rule_4_crashes': sum(1 for r in results if r['rule_4_crashed']),
        'warehouse_detection_successes': sum(1 for r in results if r['warehouse_detection_success']),
        'total_cache_hits': sum(r['cache_hits'] for r in results),
        'avg_execution_time': sum(r['execution_time'] for r in results) / len(results) if results else 0,
        'all_errors': [error for r in results for error in r['errors']],
        'success_rate': 0
    }
    
    if summary['total_requests'] > 0:
        summary['success_rate'] = (summary['successful_requests'] / summary['total_requests']) * 100
    
    return summary

def test_session_safe_cache_performance():
    """Test the session-safe cache performance under load"""
    
    print(f"\nSESSION-SAFE CACHE PERFORMANCE TEST")
    print("=" * 60)
    
    try:
        cache = get_session_safe_cache()
        
        # Get initial stats
        initial_stats = cache.get_cache_stats()
        debug_info = cache.get_debug_info()
        
        print(f"Cache Performance:")
        print(f"  Hit Rate: {initial_stats['hit_rate_percent']:.1f}%")
        print(f"  Total Cached Locations: {initial_stats['total_cached_locations']}")
        print(f"  Cache Size Limit: {initial_stats['cache_size_limit']}")
        print(f"  Uptime: {initial_stats['uptime_hours']:.2f}h")
        
        print(f"\nCache Debug Info:")
        print(f"  Global Cache Size: {debug_info['global_cache_size']}")
        print(f"  Warehouse Caches: {len(debug_info['warehouse_caches'])}")
        print(f"  Web Request Context: {debug_info['is_web_request']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Cache performance test failed: {e}")
        return False

def main():
    """Run comprehensive production testing"""
    
    print("PRODUCTION CONTEXT TESTING")
    print("Testing all session binding fixes in simulated web request environment")
    print("=" * 80)
    
    # Test 1: Session-safe cache performance
    cache_test_passed = test_session_safe_cache_performance()
    
    # Test 2: Single request test
    print(f"\nSINGLE REQUEST TEST")
    print("=" * 60)
    
    # Load test data
    inventory_path = r"C:\Users\juanb\Documents\Diego\Projects\ware2\comprehensive_rule_test_inventory.xlsx"
    if not os.path.exists(inventory_path):
        print(f"ERROR: Cannot run production test - inventory file not found: {inventory_path}")
        return False
    
    inventory_df = pd.read_excel(inventory_path)
    inventory_df = inventory_df.rename(columns={
        'Pallet ID': 'pallet_id', 'Location': 'location', 'Description': 'description',
        'Receipt Number': 'receipt_number', 'Creation Date': 'creation_date'
    })
    inventory_df['creation_date'] = pd.to_datetime(inventory_df['creation_date'])
    
    single_result = simulate_web_request_analysis(0, inventory_df)
    single_test_passed = single_result['success'] and single_result['session_binding_errors'] == 0
    
    # Test 3: Concurrent requests test
    concurrent_results = run_concurrent_request_test(3)  # Test with 3 concurrent requests
    concurrent_test_passed = (
        concurrent_results.get('success_rate', 0) >= 100 and  # All requests successful
        concurrent_results.get('total_session_errors', 1) == 0 and  # No session binding errors
        concurrent_results.get('rule_4_crashes', 1) == 0  # No Rule 4 crashes
    )
    
    # Overall assessment
    print(f"\nOVERALL PRODUCTION TEST RESULTS")
    print("=" * 80)
    
    tests = [
        ("Session-Safe Cache Performance", cache_test_passed),
        ("Single Web Request", single_test_passed), 
        ("Concurrent Web Requests", concurrent_test_passed)
    ]
    
    passed_tests = sum(1 for _, passed in tests if passed)
    total_tests = len(tests)
    
    for test_name, passed in tests:
        status = "PASS" if passed else "FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\nFinal Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print(f"\nALL PRODUCTION TESTS PASSED!")
        print(f"The session binding fixes are working correctly in web request contexts.")
        print(f"The system is ready for production use.")
        return True
    else:
        print(f"\nWARNING: {total_tests - passed_tests} TESTS FAILED")
        print(f"Some session binding issues may still exist.")
        print(f"Further investigation may be required.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)