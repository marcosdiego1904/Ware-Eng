"""
COMPREHENSIVE TEST: Verify all critical fixes

This script tests the fixes we've implemented:
1. SQLAlchemy session binding fix
2. Missing special areas addition
3. Rule #4 (Invalid Locations Alert) functionality
4. Warehouse detection system functionality

Tests using the corrected inventory data to ensure everything works properly.
"""

import sys
import os
sys.path.append('src')

# Import the Flask app directly
import app
from models import db, Location, Rule
import pandas as pd
from datetime import datetime

def test_session_binding_fix():
    """Test that session binding issues are resolved"""
    print("=" * 60)
    print("TEST 1: SESSION BINDING FIX VERIFICATION")
    print("=" * 60)
    
    try:
        from location_service import get_location_matcher, get_inventory_validator
        
        location_matcher = get_location_matcher()
        inventory_validator = get_inventory_validator()
        
        # Test with various location codes that would cause binding issues
        test_locations = ['RECV-01', 'AISLE-01', '01-01-001A', 'invalid-location']
        
        print("Testing location matching with session binding protection...")
        
        for location_code in test_locations:
            try:
                location = location_matcher.find_location(location_code, 'USER_TESTF')
                if location:
                    # Try to access properties to ensure session binding works
                    _ = location.id
                    _ = location.code
                    _ = location.warehouse_id
                    print(f"  ✓ {location_code}: Found and session-bound (ID: {location.id})")
                else:
                    print(f"  - {location_code}: Not found (expected for invalid locations)")
                    
            except Exception as e:
                print(f"  ✗ {location_code}: Session binding error: {e}")
                return False
                
        print("SUCCESS: Session binding fix verified!")
        return True
        
    except Exception as e:
        print(f"ERROR: Session binding test failed: {e}")
        return False

def test_special_areas_present():
    """Test that required special areas are present in database"""
    print("\n" + "=" * 60)
    print("TEST 2: SPECIAL AREAS PRESENCE VERIFICATION")
    print("=" * 60)
    
    with app.app.app_context():
        required_areas = ['RECV-01', 'RECV-02', 'AISLE-01', 'AISLE-02']
        warehouse_id = 'USER_TESTF'
        
        print(f"Checking special areas in warehouse: {warehouse_id}")
        
        missing_areas = []
        found_areas = []
        
        for area_code in required_areas:
            location = Location.query.filter_by(
                warehouse_id=warehouse_id,
                code=area_code
            ).first()
            
            if location:
                print(f"  ✓ {area_code}: Present (Type: {location.location_type}, Capacity: {location.pallet_capacity})")
                found_areas.append(area_code)
            else:
                print(f"  ✗ {area_code}: MISSING")
                missing_areas.append(area_code)
        
        if missing_areas:
            print(f"ERROR: Missing areas: {missing_areas}")
            return False
        else:
            print("SUCCESS: All special areas are present!")
            return True

def test_warehouse_detection():
    """Test warehouse detection system with corrected inventory"""
    print("\n" + "=" * 60)
    print("TEST 3: WAREHOUSE DETECTION SYSTEM")
    print("=" * 60)
    
    try:
        # Load the corrected inventory file  
        inventory_path = r"C:\Users\juanb\Documents\Diego\Projects\ware2\inventoryreport_corrected.xlsx"
        
        if not os.path.exists(inventory_path):
            print(f"ERROR: Inventory file not found: {inventory_path}")
            return False
            
        print(f"Loading inventory from: {inventory_path}")
        inventory_df = pd.read_excel(inventory_path)
        
        print(f"Inventory loaded: {len(inventory_df)} records")
        print(f"Columns: {list(inventory_df.columns)}")
        
        # Map columns for rule engine compatibility
        column_mapping = {
            'pallet_id': 'Pallet ID',
            'location': 'Location', 
            'description': 'Description',
            'receipt_number': 'Receipt Number',
            'creation_date': 'Creation Date'
        }
        
        # Rename columns
        rename_dict = {v: k for k, v in column_mapping.items()}
        inventory_df = inventory_df.rename(columns=rename_dict)
        
        # Convert creation_date to datetime
        inventory_df['creation_date'] = pd.to_datetime(inventory_df['creation_date'])
        
        # Test warehouse detection using rule engine method
        with app.app.app_context():
            from rule_engine import RuleEngine
            
            rule_engine = RuleEngine(db.session, app.app)
            
            # Test warehouse detection
            print("Testing warehouse detection...")
            context = rule_engine.detect_warehouse_context(inventory_df)
            
            print(f"Warehouse Detection Results:")
            print(f"  Warehouse ID: {context.get('warehouse_id')}")
            print(f"  Confidence: {context.get('confidence')}")
            print(f"  Coverage: {context.get('coverage', 0):.1f}%")
            
            if context.get('warehouse_id') == 'USER_TESTF' and context.get('coverage', 0) > 50:
                print("SUCCESS: Warehouse detection working properly!")
                return True
            else:
                print("WARNING: Warehouse detection may have issues")
                return False
                
    except Exception as e:
        print(f"ERROR: Warehouse detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rule_4_functionality():
    """Test Rule #4 (Invalid Locations Alert) functionality"""
    print("\n" + "=" * 60)
    print("TEST 4: RULE #4 INVALID LOCATIONS ALERT")
    print("=" * 60)
    
    try:
        # Load the corrected inventory file  
        inventory_path = r"C:\Users\juanb\Documents\Diego\Projects\ware2\inventoryreport_corrected.xlsx"
        
        if not os.path.exists(inventory_path):
            print(f"ERROR: Inventory file not found: {inventory_path}")
            return False
            
        inventory_df = pd.read_excel(inventory_path)
        
        # Map columns for rule engine compatibility
        rename_dict = {'Pallet ID': 'pallet_id', 'Location': 'location', 
                       'Description': 'description', 'Receipt Number': 'receipt_number',
                       'Creation Date': 'creation_date'}
        inventory_df = inventory_df.rename(columns=rename_dict)
        inventory_df['creation_date'] = pd.to_datetime(inventory_df['creation_date'])
        
        with app.app.app_context():
            from rule_engine import RuleEngine, InvalidLocationEvaluator
            
            # Get Rule #4
            rule_4 = Rule.query.filter_by(id=4).first()
            if not rule_4:
                print("ERROR: Rule #4 not found in database")
                return False
                
            print(f"Testing Rule #4: {rule_4.name}")
            
            # Test the evaluator directly
            evaluator = InvalidLocationEvaluator(app.app)
            
            # Get warehouse context
            rule_engine = RuleEngine(db.session, app.app)
            context = rule_engine.detect_warehouse_context(inventory_df)
            
            print(f"Using warehouse context: {context}")
            
            # Evaluate the rule
            anomalies = evaluator.evaluate(rule_4, inventory_df, context)
            
            print(f"Rule #4 Results:")
            print(f"  Anomalies found: {len(anomalies)}")
            
            # Show some example anomalies
            for i, anomaly in enumerate(anomalies[:5]):  # Show first 5
                print(f"    {i+1}. {anomaly.get('pallet_id', 'Unknown')}: {anomaly.get('message', 'No message')}")
            
            if len(anomalies) > 5:
                print(f"    ... and {len(anomalies) - 5} more")
            
            print("SUCCESS: Rule #4 executed without session binding errors!")
            return True
            
    except Exception as e:
        print(f"ERROR: Rule #4 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("COMPREHENSIVE FIX VERIFICATION")
    print("Testing all critical fixes implemented...")
    
    tests = [
        ("Session Binding Fix", test_session_binding_fix),
        ("Special Areas Present", test_special_areas_present), 
        ("Warehouse Detection", test_warehouse_detection),
        ("Rule #4 Functionality", test_rule_4_functionality)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL FIXES VERIFIED SUCCESSFULLY!")
        print("The WareWise system should now work properly with your corrected inventory data.")
        return True
    else:
        print(f"\n⚠️ {total - passed} TESTS FAILED")
        print("Some issues may still need attention.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)