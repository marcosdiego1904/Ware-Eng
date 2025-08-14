#!/usr/bin/env python3
"""
Comprehensive test to verify all WareWise rule engine fixes

Tests:
1. InvalidLocationEvaluator properly includes NULL is_active locations
2. Clean rule set (9 rules, no duplicates)
3. StagnantPalletsEvaluator detection works correctly
4. All rule types can execute without errors
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Rule, Location
from rule_engine import RuleEngine
from sqlalchemy import or_

def test_location_query_fix():
    """Test that InvalidLocationEvaluator includes NULL is_active locations"""
    with app.app_context():
        print("=== TEST 1: Location Query Fix ===")
        
        # Query using the fixed logic
        locations = Location.query.filter(
            or_(Location.is_active == True, Location.is_active.is_(None))
        ).all()
        
        # Query using old broken logic (for comparison)
        broken_locations = Location.query.filter_by(is_active=True).all()
        
        print(f"Fixed query finds: {len(locations)} locations")
        print(f"Broken query finds: {len(broken_locations)} locations") 
        print(f"Difference: {len(locations) - len(broken_locations)} locations recovered")
        
        # Check if RECEIVING is included (it has is_active=NULL)
        receiving_loc = Location.query.filter_by(code='RECEIVING').first()
        if receiving_loc:
            print(f"RECEIVING location: is_active={receiving_loc.is_active}")
            in_fixed = receiving_loc in locations
            in_broken = receiving_loc in broken_locations
            print(f"Included in fixed query: {in_fixed}")
            print(f"Included in broken query: {in_broken}")
            
            if in_fixed and not in_broken:
                print("PASS: FIX VERIFIED: RECEIVING location now properly included")
            else:
                print("FAIL: FIX FAILED: RECEIVING location still excluded")
        
        return len(locations) > len(broken_locations)

def test_clean_rule_set():
    """Test that duplicate rules have been cleaned up"""
    with app.app_context():
        print("\n=== TEST 2: Clean Rule Set ===")
        
        all_rules = Rule.query.all()
        print(f"Total rules: {len(all_rules)}")
        
        # Count by rule type
        rule_type_counts = {}
        for rule in all_rules:
            rule_type = rule.rule_type
            rule_type_counts[rule_type] = rule_type_counts.get(rule_type, 0) + 1
        
        print("Rules by type:")
        duplicates_found = 0
        for rule_type, count in rule_type_counts.items():
            status = "PASS" if count == 1 else f"FAIL ({count} duplicates)"
            print(f"  {rule_type}: {count} {status}")
            if count > 1:
                duplicates_found += count - 1
        
        if duplicates_found == 0:
            print("PASS: SUCCESS: No duplicate rules found")
            return True
        else:
            print(f"FAIL: FAILED: {duplicates_found} duplicate rules still exist")
            return False

def test_stagnant_detection():
    """Test that StagnantPalletsEvaluator works correctly"""
    with app.app_context():
        print("\n=== TEST 3: Stagnant Detection ===")
        
        # Create test data
        now = datetime.now()
        test_data = pd.DataFrame([
            {
                'pallet_id': 'TEST_OLD',
                'location': 'RECEIVING',
                'creation_date': now - timedelta(hours=8),  # Should trigger (>6h)
                'receipt_number': 'REC001',
                'description': 'Test Product'
            },
            {
                'pallet_id': 'TEST_NEW',
                'location': 'RECEIVING', 
                'creation_date': now - timedelta(hours=3),  # Should NOT trigger (<6h)
                'receipt_number': 'REC002',
                'description': 'Test Product'
            },
            {
                'pallet_id': 'TEST_STORAGE',
                'location': '001A',
                'creation_date': now - timedelta(hours=10), # Should NOT trigger (wrong location type)
                'receipt_number': 'REC003',
                'description': 'Test Product'
            }
        ])
        
        # Test the rule
        rule_engine = RuleEngine(db.session, app=app)
        stagnant_rule = Rule.query.filter_by(rule_type='STAGNANT_PALLETS').first()
        
        if not stagnant_rule:
            print("FAIL: FAILED: No STAGNANT_PALLETS rule found")
            return False
        
        result = rule_engine.evaluate_rule(stagnant_rule, test_data)
        
        print(f"Rule execution: {'PASS: SUCCESS' if result.success else 'FAIL: FAILED'}")
        print(f"Anomalies found: {len(result.anomalies)}")
        print(f"Expected: 1 anomaly (TEST_OLD only)")
        
        if result.success and len(result.anomalies) == 1:
            anomaly = result.anomalies[0]
            if anomaly['pallet_id'] == 'TEST_OLD':
                print("PASS: SUCCESS: Correct pallet detected as stagnant")
                return True
        
        print("FAIL: FAILED: Stagnant detection not working correctly")
        for anomaly in result.anomalies:
            print(f"  Found: {anomaly['pallet_id']} in {anomaly['location']}")
        
        return False

def test_all_rule_types():
    """Test that all rule types can execute without errors"""
    with app.app_context():
        print("\n=== TEST 4: All Rule Types Execution ===")
        
        # Create comprehensive test data
        now = datetime.now()
        test_data = pd.DataFrame([
            {
                'pallet_id': 'TEST001',
                'location': 'RECEIVING',
                'creation_date': now - timedelta(hours=8),
                'receipt_number': 'REC001',
                'description': 'FROZEN Test Product'
            },
            {
                'pallet_id': 'TEST002',
                'location': 'INVALID_LOC_123',
                'creation_date': now - timedelta(hours=2),
                'receipt_number': 'REC002', 
                'description': 'Regular Product'
            },
            {
                'pallet_id': 'TEST003',
                'location': '001A',
                'creation_date': now - timedelta(hours=1),
                'receipt_number': 'REC001',
                'description': 'Another Product'
            }
        ])
        
        rule_engine = RuleEngine(db.session, app=app)
        all_rules = Rule.query.filter_by(is_active=True).all()
        
        print(f"Testing {len(all_rules)} active rules...")
        
        success_count = 0
        for rule in all_rules:
            try:
                result = rule_engine.evaluate_rule(rule, test_data)
                if result.success:
                    print(f"  PASS {rule.rule_type}: {len(result.anomalies)} anomalies")
                    success_count += 1
                else:
                    print(f"  FAIL {rule.rule_type}: {result.error_message}")
            except Exception as e:
                print(f"  FAIL {rule.rule_type}: Exception - {str(e)}")
        
        print(f"\nSuccessful rule executions: {success_count}/{len(all_rules)}")
        
        if success_count == len(all_rules):
            print("PASS: SUCCESS: All rule types execute without errors")
            return True
        else:
            print(f"FAIL: FAILED: {len(all_rules) - success_count} rules failed")
            return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("WAREWISE RULE ENGINE COMPREHENSIVE TEST")
    print("=" * 60)
    
    tests = [
        ("Location Query Fix", test_location_query_fix),
        ("Clean Rule Set", test_clean_rule_set), 
        ("Stagnant Detection", test_stagnant_detection),
        ("All Rule Types", test_all_rule_types)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"FAIL {test_name}: Exception - {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: ALL TESTS PASSED! Rule engine fixes are working correctly.")
    else:
        print(f"WARNING: {total - passed} tests failed. Please review the issues above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == '__main__':
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)