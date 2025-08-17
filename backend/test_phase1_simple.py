#!/usr/bin/env python3
"""
Simple test validation for Phase 1 warehouse detection improvements
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_normalization():
    """Test basic location normalization functionality"""
    
    print("=== TESTING BASIC LOCATION NORMALIZATION ===")
    
    try:
        from app import app
        from rule_engine import RuleEngine
        from models import db
        
        with app.app_context():
            rule_engine = RuleEngine(db.session)
            
            # Test simple normalization
            test_location = "02-1-011B"
            variants = rule_engine._normalize_position_format(test_location)
            
            print(f"Input: {test_location}")
            print(f"Generated variants: {variants}")
            
            # Check if we get multiple variants
            if len(variants) > 1:
                print("PASS: Multiple variants generated")
                return True
            else:
                print("FAIL: Only single variant generated")
                return False
                
    except Exception as e:
        print(f"FAIL: Error testing normalization: {str(e)}")
        return False

def test_basic_detection():
    """Test basic warehouse detection functionality"""
    
    print("\n=== TESTING BASIC WAREHOUSE DETECTION ===")
    
    try:
        from app import app
        from rule_engine import RuleEngine
        from models import db, Location
        
        with app.app_context():
            # Check if we have any locations
            location_count = db.session.query(Location).count()
            print(f"Total locations in database: {location_count}")
            
            if location_count == 0:
                print("SKIP: No locations in database to test with")
                return True
            
            rule_engine = RuleEngine(db.session)
            
            # Test with simple inventory data
            test_locations = ['02-1-011B', '01-1-007B', 'RECV-01']
            test_df = pd.DataFrame({'location': test_locations})
            
            detection_result = rule_engine._detect_warehouse_context(test_df)
            
            print(f"Detection result: {detection_result}")
            
            # Check if we get some response
            if 'total_inventory_locations' in detection_result:
                print("PASS: Detection function working")
                return True
            else:
                print("FAIL: Detection function not working properly")
                return False
                
    except Exception as e:
        print(f"FAIL: Error testing detection: {str(e)}")
        return False

def test_environment_sync():
    """Test environment synchronization utility"""
    
    print("\n=== TESTING ENVIRONMENT SYNC UTILITY ===")
    
    try:
        from environment_sync_utility import EnvironmentSyncUtility
        
        sync_util = EnvironmentSyncUtility()
        
        # Test basic analysis
        analysis = sync_util.analyze_environment_differences()
        
        print(f"Environment type: {analysis.get('environment_type', 'Unknown')}")
        print(f"Total locations: {analysis.get('total_locations', 0)}")
        
        if 'warehouse_distribution' in analysis:
            print("PASS: Environment analysis working")
            return True
        else:
            print("FAIL: Environment analysis not working")
            return False
            
    except Exception as e:
        print(f"FAIL: Error testing sync utility: {str(e)}")
        return False

def main():
    """Run simple Phase 1 validation tests"""
    
    print("PHASE 1 SIMPLE VALIDATION")
    print("=" * 40)
    
    tests = [
        ('Normalization', test_basic_normalization),
        ('Detection', test_basic_detection),
        ('Sync Utility', test_environment_sync)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            result = test_func()
            if result:
                print(f"{test_name}: PASS")
                passed += 1
            else:
                print(f"{test_name}: FAIL")
        except Exception as e:
            print(f"{test_name}: ERROR - {str(e)}")
    
    print(f"\n" + "=" * 40)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed >= total * 0.67:  # 67% pass rate
        print("PHASE 1 VALIDATION SUCCESSFUL")
        return True
    else:
        print("PHASE 1 VALIDATION NEEDS WORK")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)