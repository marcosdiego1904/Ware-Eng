#!/usr/bin/env python3
"""
Test script to verify the unified virtual location architecture
Tests that special locations are handled consistently as virtual locations
"""

import sys
import os
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig
from virtual_compatibility_layer import get_compatibility_manager

def test_virtual_special_locations():
    """Test that special locations are properly generated as virtual locations"""
    print("TESTING UNIFIED VIRTUAL LOCATION ARCHITECTURE")
    print("=" * 60)
    
    with app.app_context():
        # Get compatibility manager
        compat_manager = get_compatibility_manager()
        
        # Test with a known warehouse that has special areas configured
        # You can replace this with any warehouse ID that exists in your system
        test_warehouses = ['USER_MARCOS9', 'USER_TESTF', 'DEFAULT']
        
        for warehouse_id in test_warehouses:
            print(f"\nTesting warehouse: {warehouse_id}")
            print("-" * 40)
            
            # Check if warehouse is detected as virtual
            is_virtual = compat_manager.is_virtual_warehouse(warehouse_id)
            print(f"   Is Virtual: {is_virtual}")
            
            if not is_virtual:
                print(f"   WARNING: Warehouse {warehouse_id} not detected as virtual - skipping")
                continue
            
            # Get warehouse config to see what special areas should exist
            config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            if not config:
                print(f"   ❌ No config found for {warehouse_id}")
                continue
            
            print(f"   Config found: {config.warehouse_name}")
            
            # Parse special areas from config
            expected_special_areas = []
            if config.receiving_areas:
                receiving = config.receiving_areas if isinstance(config.receiving_areas, list) else []
                expected_special_areas.extend([area.get('code') for area in receiving if isinstance(area, dict)])
            
            if config.staging_areas:
                staging = config.staging_areas if isinstance(config.staging_areas, list) else []
                expected_special_areas.extend([area.get('code') for area in staging if isinstance(area, dict)])
            
            if config.dock_areas:
                dock = config.dock_areas if isinstance(config.dock_areas, list) else []
                expected_special_areas.extend([area.get('code') for area in dock if isinstance(area, dict)])
            
            print(f"   Expected special areas: {expected_special_areas}")
            
            # Get all virtual locations
            try:
                all_locations = compat_manager.get_all_warehouse_locations(warehouse_id)
                print(f"   Total virtual locations retrieved: {len(all_locations)}")
                
                # Filter special locations
                special_locations = [
                    loc for loc in all_locations 
                    if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL']
                ]
                
                print(f"   Virtual special locations found: {len(special_locations)}")
                
                # Check each special location
                for special_loc in special_locations:
                    print(f"     OK: {special_loc['code']} ({special_loc['location_type']}) - "
                          f"Zone: {special_loc['zone']}, "
                          f"Source: {special_loc.get('source', 'unknown')}")
                
                # Verify consistency
                virtual_special_codes = [loc['code'] for loc in special_locations]
                
                missing_special = set(expected_special_areas) - set(virtual_special_codes)
                unexpected_special = set(virtual_special_codes) - set(expected_special_areas)
                
                if not missing_special and not unexpected_special:
                    print(f"   SUCCESS: Perfect match! All special areas consistent")
                else:
                    if missing_special:
                        print(f"   WARNING: Missing special areas: {missing_special}")
                    if unexpected_special:
                        print(f"   WARNING: Unexpected special areas: {unexpected_special}")
                
            except Exception as e:
                print(f"   ERROR: Error getting virtual locations: {e}")

def test_special_location_api():
    """Test the location API specifically for special locations"""
    print(f"\nTESTING LOCATION API FOR SPECIAL AREAS")
    print("-" * 60)
    
    with app.app_context():
        # Import the location API function directly
        from location_api import _get_virtual_locations
        from core_models import User
        
        # Get a test user (you may need to adjust this)
        test_user = User.query.first()
        if not test_user:
            print("   ERROR: No test user found")
            return
        
        test_warehouses = ['USER_MARCOS9', 'DEFAULT']
        
        for warehouse_id in test_warehouses:
            print(f"\n   Testing API for warehouse: {warehouse_id}")
            
            try:
                # Test getting all locations
                response_data = _get_virtual_locations(
                    test_user, warehouse_id, 
                    location_type=None, zone=None, is_active=None, 
                    aisle_number=None, search=None, page=1, per_page=100
                )
                
                if isinstance(response_data, tuple):
                    response_data = response_data[0].get_json()
                
                total_locations = len(response_data.get('locations', []))
                print(f"     Total locations from API: {total_locations}")
                
                # Test getting only special locations
                special_response = _get_virtual_locations(
                    test_user, warehouse_id, 
                    location_type='RECEIVING', zone=None, is_active=None, 
                    aisle_number=None, search=None, page=1, per_page=100
                )
                
                if isinstance(special_response, tuple):
                    special_response = special_response[0].get_json()
                
                receiving_locations = len(special_response.get('locations', []))
                print(f"     RECEIVING locations from API: {receiving_locations}")
                
                # Show details of special locations
                special_locations = [
                    loc for loc in response_data.get('locations', [])
                    if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK']
                ]
                
                print(f"     Special locations details:")
                for loc in special_locations[:5]:  # Show first 5
                    print(f"       - {loc['code']} ({loc['location_type']}) "
                          f"Source: {loc.get('source', 'unknown')}")
                
            except Exception as e:
                print(f"     ERROR: API test error: {e}")

def main():
    """Run all tests"""
    print("STARTING UNIFIED VIRTUAL LOCATION TESTS")
    print("=" * 60)
    
    # Test 1: Virtual location generation
    test_virtual_special_locations()
    
    # Test 2: API consistency
    test_special_location_api()
    
    print(f"\nTESTS COMPLETED")
    print("=" * 60)
    print("Check the output above for:")
    print("   - Special areas being generated as virtual locations")
    print("   - Consistent location types and sources")
    print("   - API returning expected special locations")
    print("   - Any missing or unexpected special areas")

if __name__ == "__main__":
    main()