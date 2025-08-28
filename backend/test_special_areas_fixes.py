#!/usr/bin/env python3
"""
Test script to validate special areas fixes
This script demonstrates that the special locations feature now works correctly
"""

import sys
import json

sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig
from virtual_compatibility_layer import get_compatibility_manager

def test_data_consistency():
    """Test that duplicate special areas have been cleaned up"""
    print("=== TESTING DATA CONSISTENCY ===")
    
    with app.app_context():
        configs = WarehouseConfig.query.all()
        issues_found = 0
        
        for config in configs:
            # Check for duplicates in receiving areas
            if config.receiving_areas:
                try:
                    receiving_areas = json.loads(config.receiving_areas) if isinstance(config.receiving_areas, str) else config.receiving_areas
                    codes = [area.get('code') for area in receiving_areas if isinstance(area, dict)]
                    unique_codes = set(codes)
                    
                    if len(codes) != len(unique_codes):
                        print(f"[ERROR] Duplicate receiving areas in {config.warehouse_id}: {codes}")
                        issues_found += 1
                    
                except Exception as e:
                    print(f"[ERROR] Could not parse receiving areas for {config.warehouse_id}: {e}")
                    issues_found += 1
            
            # Similar checks for staging and dock areas...
            if config.staging_areas:
                try:
                    staging_areas = json.loads(config.staging_areas) if isinstance(config.staging_areas, str) else config.staging_areas
                    codes = [area.get('code') for area in staging_areas if isinstance(area, dict)]
                    unique_codes = set(codes)
                    
                    if len(codes) != len(unique_codes):
                        print(f"[ERROR] Duplicate staging areas in {config.warehouse_id}: {codes}")
                        issues_found += 1
                        
                except Exception as e:
                    print(f"[ERROR] Could not parse staging areas for {config.warehouse_id}: {e}")
                    issues_found += 1
        
        if issues_found == 0:
            print("[SUCCESS] No duplicate special areas found - data consistency fixed!")
        else:
            print(f"[FAILURE] Found {issues_found} data consistency issues")
        
        return issues_found == 0

def test_virtual_location_generation():
    """Test that virtual locations are generated correctly for special areas"""
    print("\n=== TESTING VIRTUAL LOCATION GENERATION ===")
    
    with app.app_context():
        # Test USER_MARCOS9 warehouse
        config = WarehouseConfig.query.filter_by(warehouse_id='USER_MARCOS9').first()
        
        if not config:
            print("[ERROR] USER_MARCOS9 warehouse not found")
            return False
        
        print(f"Testing warehouse: {config.warehouse_name}")
        
        # Get virtual locations
        compat_manager = get_compatibility_manager()
        virtual_locs = compat_manager.get_all_warehouse_locations('USER_MARCOS9')
        
        # Count special areas
        special_areas = [loc for loc in virtual_locs if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK']]
        
        print(f"Total virtual locations: {len(virtual_locs)}")
        print(f"Special areas generated: {len(special_areas)}")
        
        # Validate special areas match configuration
        expected_special_areas = 0
        if config.receiving_areas:
            receiving_areas = json.loads(config.receiving_areas) if isinstance(config.receiving_areas, str) else config.receiving_areas
            expected_special_areas += len(receiving_areas)
        
        if config.staging_areas:
            staging_areas = json.loads(config.staging_areas) if isinstance(config.staging_areas, str) else config.staging_areas
            expected_special_areas += len(staging_areas)
        
        if config.dock_areas:
            dock_areas = json.loads(config.dock_areas) if isinstance(config.dock_areas, str) else config.dock_areas
            expected_special_areas += len(dock_areas)
        
        print(f"Expected special areas: {expected_special_areas}")
        print(f"Generated special areas: {len(special_areas)}")
        
        if len(special_areas) == expected_special_areas:
            print("[SUCCESS] Virtual location generation matches configuration!")
            
            # Show details
            for area in special_areas:
                print(f"  - {area.get('code')} ({area.get('location_type')}) - Capacity: {area.get('capacity')}")
            
            return True
        else:
            print("[FAILURE] Special area count mismatch!")
            return False

def test_no_unexpected_areas():
    """Test that automatic transitional areas are not created unexpectedly"""
    print("\n=== TESTING NO UNEXPECTED AREAS ===")
    
    with app.app_context():
        config = WarehouseConfig.query.filter_by(warehouse_id='USER_MARCOS9').first()
        
        if not config:
            print("[ERROR] USER_MARCOS9 warehouse not found")
            return False
        
        compat_manager = get_compatibility_manager()
        virtual_locs = compat_manager.get_all_warehouse_locations('USER_MARCOS9')
        
        # Check for unexpected transitional/aisle areas
        transitional_areas = [loc for loc in virtual_locs if loc.get('location_type') == 'TRANSITIONAL']
        
        print(f"Transitional/AISLE areas found: {len(transitional_areas)}")
        
        if len(transitional_areas) == 0:
            print("[SUCCESS] No unexpected transitional areas created!")
            return True
        else:
            print("[FAILURE] Found unexpected transitional areas:")
            for area in transitional_areas:
                print(f"  - {area.get('code')} ({area.get('location_type')})")
            return False

def test_zone_standardization():
    """Test that zone assignments are standardized"""
    print("\n=== TESTING ZONE STANDARDIZATION ===")
    
    with app.app_context():
        config = WarehouseConfig.query.filter_by(warehouse_id='USER_MARCOS9').first()
        
        if not config:
            print("[ERROR] USER_MARCOS9 warehouse not found")
            return False
        
        issues_found = 0
        
        # Check receiving areas
        if config.receiving_areas:
            receiving_areas = json.loads(config.receiving_areas) if isinstance(config.receiving_areas, str) else config.receiving_areas
            for area in receiving_areas:
                if area.get('zone') != 'RECEIVING':
                    print(f"[ERROR] Receiving area {area.get('code')} has wrong zone: {area.get('zone')}")
                    issues_found += 1
        
        # Check staging areas
        if config.staging_areas:
            staging_areas = json.loads(config.staging_areas) if isinstance(config.staging_areas, str) else config.staging_areas
            for area in staging_areas:
                if area.get('zone') != 'STAGING':
                    print(f"[ERROR] Staging area {area.get('code')} has wrong zone: {area.get('zone')}")
                    issues_found += 1
        
        # Check dock areas
        if config.dock_areas:
            dock_areas = json.loads(config.dock_areas) if isinstance(config.dock_areas, str) else config.dock_areas
            for area in dock_areas:
                if area.get('zone') != 'DOCK':
                    print(f"[ERROR] Dock area {area.get('code')} has wrong zone: {area.get('zone')}")
                    issues_found += 1
        
        if issues_found == 0:
            print("[SUCCESS] All zones are properly standardized!")
            return True
        else:
            print(f"[FAILURE] Found {issues_found} zone standardization issues")
            return False

def main():
    """Run all tests and provide summary"""
    print("SPECIAL AREAS FIXES VALIDATION")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Data Consistency", test_data_consistency),
        ("Virtual Location Generation", test_virtual_location_generation),  
        ("No Unexpected Areas", test_no_unexpected_areas),
        ("Zone Standardization", test_zone_standardization)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n[SUCCESS] All special areas fixes are working correctly!")
    else:
        print(f"\n[WARNING] {failed} test(s) failed - additional fixes may be needed")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)