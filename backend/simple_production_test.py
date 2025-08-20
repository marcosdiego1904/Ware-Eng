"""
SIMPLE PRODUCTION TEST: Validate session binding fixes in web request context

Tests the core fixes in a simulated Flask web request environment.
"""

import sys
import os
sys.path.append('src')

import pandas as pd
from datetime import datetime

# Import Flask app and setup request context
import app
from models import db, Location
from session_manager import RequestScopedSessionManager, get_session
from session_safe_cache import get_session_safe_cache

def test_single_web_request():
    """Test analysis in simulated Flask web request context"""
    
    print("PRODUCTION CONTEXT TEST")
    print("=" * 50)
    print("Testing session binding fixes in web request context...")
    
    try:
        # Load test inventory
        inventory_path = r"C:\Users\juanb\Documents\Diego\Projects\ware2\comprehensive_rule_test_inventory.xlsx"
        
        if not os.path.exists(inventory_path):
            print(f"ERROR: Test inventory not found: {inventory_path}")
            return False
        
        print(f"Loading test inventory: {inventory_path}")
        inventory_df = pd.read_excel(inventory_path)
        
        # Prepare data
        inventory_df = inventory_df.rename(columns={
            'Pallet ID': 'pallet_id', 'Location': 'location', 
            'Description': 'description', 'Receipt Number': 'receipt_number',
            'Creation Date': 'creation_date'
        })
        inventory_df['creation_date'] = pd.to_datetime(inventory_df['creation_date'])
        
        print(f"Loaded {len(inventory_df)} records")
        
        # Test in Flask request context
        with app.app.app_context(), app.app.test_request_context():
            print("Flask request context established")
            
            # Verify web request context
            is_web_request = RequestScopedSessionManager.is_web_request_context()
            print(f"Web request context: {is_web_request}")
            
            if not is_web_request:
                print("FAILED: Could not establish web request context")
                return False
            
            # Test session management
            current_session = get_session()
            print(f"Current session: {current_session}")
            
            # Test session-safe cache
            cache = get_session_safe_cache()
            cache.invalidate_request_cache()
            initial_stats = cache.get_cache_stats()
            print(f"Cache initialized - Hit rate: {initial_stats['hit_rate_percent']:.1f}%")
            
            # Run enhanced analysis
            try:
                from enhanced_main import run_enhanced_engine
                
                print("Running enhanced analysis engine...")
                
                start_time = datetime.now()
                anomalies = run_enhanced_engine(
                    inventory_df,
                    rules_df=None,
                    args=None, 
                    use_database_rules=True,
                    rule_ids=None,
                    report_id=None
                )
                execution_time = (datetime.now() - start_time).total_seconds()
                
                anomaly_count = len(anomalies) if isinstance(anomalies, list) else 0
                
                print(f"Analysis completed in {execution_time:.2f}s")
                print(f"Anomalies found: {anomaly_count}")
                
                # Check cache performance
                final_stats = cache.get_cache_stats()
                cache_hits = final_stats['cache_stats']['hits'] - initial_stats['cache_stats']['hits']
                print(f"Cache hits during analysis: {cache_hits}")
                
                print("SUCCESS: Analysis completed without session binding errors!")
                return True
                
            except Exception as e:
                error_msg = str(e)
                print(f"ERROR: Analysis failed: {error_msg}")
                
                if "not bound to a Session" in error_msg:
                    print("CRITICAL: Session binding error still present!")
                
                if "Rule 4" in error_msg or "Invalid Locations Alert" in error_msg:
                    print("CRITICAL: Rule 4 still crashing!")
                
                return False
                
    except Exception as e:
        print(f"ERROR: Production test failed: {e}")
        return False

def test_location_service_in_context():
    """Test location service specifically in web request context"""
    
    print("\nLOCATION SERVICE CONTEXT TEST")
    print("=" * 50)
    
    try:
        with app.app.app_context(), app.app.test_request_context():
            print("Testing location service in web request context...")
            
            from location_service import get_location_matcher
            
            location_matcher = get_location_matcher()
            
            # Test finding various location types
            test_locations = ['RECV-01', 'AISLE-01', '01-01-001A', 'INVALID-LOC']
            
            for location_code in test_locations:
                try:
                    location = location_matcher.find_location(location_code, 'USER_TESTF')
                    
                    if location:
                        # Test session binding by accessing properties
                        location_id = location.id
                        location_code_db = location.code
                        warehouse_id = location.warehouse_id
                        
                        print(f"  FOUND: {location_code} -> {location_code_db} (ID: {location_id}, Warehouse: {warehouse_id})")
                    else:
                        print(f"  NOT FOUND: {location_code} (expected for invalid locations)")
                        
                except Exception as e:
                    print(f"  ERROR: {location_code} -> {e}")
                    if "not bound to a Session" in str(e):
                        print("    CRITICAL: Session binding error in location service!")
                        return False
            
            print("SUCCESS: Location service working in web request context!")
            return True
            
    except Exception as e:
        print(f"ERROR: Location service test failed: {e}")
        return False

def main():
    """Run production context tests"""
    
    print("PRODUCTION FIXES VALIDATION")
    print("Testing all session binding fixes in web request context")
    print("=" * 60)
    
    # Test 1: Location service in web request context
    location_test_passed = test_location_service_in_context()
    
    # Test 2: Full analysis in web request context  
    analysis_test_passed = test_single_web_request()
    
    # Results
    print("\nTEST RESULTS")
    print("=" * 60)
    
    tests = [
        ("Location Service Web Context", location_test_passed),
        ("Full Analysis Web Context", analysis_test_passed)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS: All production fixes are working correctly!")
        print("The system should now handle web requests without session binding errors.")
        return True
    else:
        print(f"\nFAILED: {total - passed} tests failed.")
        print("Some session binding issues may still exist.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)