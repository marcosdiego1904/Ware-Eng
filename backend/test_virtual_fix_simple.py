#!/usr/bin/env python3
"""
Simple test to verify virtual special locations fix is working
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig
from virtual_compatibility_layer import get_compatibility_manager

def test_virtual_special_fix():
    """Test the key fix - virtual special locations consistency"""
    print("VIRTUAL SPECIAL LOCATIONS FIX TEST")
    print("=" * 50)
    
    with app.app_context():
        compat_manager = get_compatibility_manager()
        
        # Test a warehouse we know works
        warehouse_id = 'USER_MARCOS9'
        
        print(f"Testing warehouse: {warehouse_id}")
        print("-" * 30)
        
        # Check virtual detection
        is_virtual = compat_manager.is_virtual_warehouse(warehouse_id)
        print(f"Virtual detected: {is_virtual}")
        
        if not is_virtual:
            print("ERROR: Warehouse should be virtual!")
            return False
        
        # Get all locations
        locations = compat_manager.get_all_warehouse_locations(warehouse_id)
        print(f"Total locations: {len(locations)}")
        
        # Filter special locations
        special_locations = [
            loc for loc in locations 
            if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK']
        ]
        
        print(f"Special locations: {len(special_locations)}")
        print("Special location details:")
        
        success = True
        for loc in special_locations:
            source = loc.get('source', 'unknown')
            print(f"  - {loc['code']} ({loc['location_type']}) Source: {source}")
            
            # KEY TEST: All special locations should be virtual
            if not source.startswith('virtual'):
                print(f"    ERROR: {loc['code']} has non-virtual source: {source}")
                success = False
            else:
                print(f"    OK: Virtual special location working correctly")
        
        print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
        print(f"Key Fix: {'WORKING' if success else 'NEEDS ATTENTION'}")
        
        return success

if __name__ == "__main__":
    success = test_virtual_special_fix()
    if success:
        print("\nCONCLUSION: Virtual special locations architecture fix is working!")
        print("Special locations are now consistently treated as virtual locations.")
    else:
        print("\nCONCLUSION: Fix needs attention - some locations still using physical sources.")