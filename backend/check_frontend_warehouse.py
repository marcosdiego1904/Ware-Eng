#!/usr/bin/env python3
"""
Check which warehouse the frontend is actually using
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig

def find_warehouse_with_receiving_location():
    """Find which warehouse has a RECEIVING location that matches the screenshot"""
    print("FINDING WAREHOUSE WITH 'RECEIVING' LOCATION")
    print("=" * 50)
    
    with app.app_context():
        # Look for warehouses with special areas
        configs = WarehouseConfig.query.all()
        print(f"Total warehouse configs: {len(configs)}")
        
        matches = []
        
        for config in configs:
            receiving_areas = config.get_receiving_areas()
            staging_areas = config.get_staging_areas()
            dock_areas = config.get_dock_areas()
            
            # Check if any area has code 'RECEIVING' (like in screenshot)
            all_areas = receiving_areas + staging_areas + dock_areas
            receiving_codes = [area.get('code') for area in all_areas if 'RECEIV' in area.get('code', '')]
            
            if receiving_codes:
                matches.append({
                    'warehouse_id': config.warehouse_id,
                    'warehouse_name': config.warehouse_name,
                    'receiving_codes': receiving_codes,
                    'total_special': len(all_areas)
                })
                
                print(f"\nWarehouse: {config.warehouse_id} ({config.warehouse_name})")
                print(f"  Receiving codes: {receiving_codes}")
                print(f"  Total special areas: {len(all_areas)}")
                
                # Show all special area codes
                if len(all_areas) > 0:
                    all_codes = [area.get('code') for area in all_areas]
                    print(f"  All special codes: {all_codes}")
        
        print(f"\nFound {len(matches)} warehouses with RECEIVING areas")
        
        # Look specifically for one with only 1 special area (matching screenshot)
        single_area_warehouses = [m for m in matches if m['total_special'] == 1]
        if single_area_warehouses:
            print(f"\nWarehouses with exactly 1 special area (like your screenshot):")
            for w in single_area_warehouses:
                print(f"  - {w['warehouse_id']}: {w['receiving_codes']}")
        
        return matches

def test_specific_warehouse(warehouse_id):
    """Test a specific warehouse to see what locations it should show"""
    print(f"\nTESTING SPECIFIC WAREHOUSE: {warehouse_id}")
    print("-" * 40)
    
    with app.app_context():
        from virtual_compatibility_layer import get_compatibility_manager
        
        config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
        if not config:
            print("No config found")
            return
            
        print(f"Config: {config.warehouse_name}")
        
        # Check if virtual
        compat_manager = get_compatibility_manager()
        is_virtual = compat_manager.is_virtual_warehouse(warehouse_id)
        print(f"Virtual: {is_virtual}")
        
        if is_virtual:
            locations = compat_manager.get_all_warehouse_locations(warehouse_id)
            special_locs = [
                loc for loc in locations 
                if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL']
            ]
            
            print(f"Special locations: {len(special_locs)}")
            for loc in special_locs:
                print(f"  - {loc['code']} ({loc['location_type']}) - Zone: {loc['zone']}")

if __name__ == "__main__":
    warehouses = find_warehouse_with_receiving_location()
    
    # Test the most likely candidates
    print(f"\n{'='*60}")
    print("TESTING LIKELY CANDIDATES:")
    
    # Test USER_MARCOS9 first (from previous tests)
    test_specific_warehouse('USER_MARCOS9')
    
    # Test any single-area warehouses
    single_area_warehouses = []
    with app.app_context():
        configs = WarehouseConfig.query.all()
        for config in configs:
            receiving = config.get_receiving_areas()
            staging = config.get_staging_areas()
            dock = config.get_dock_areas()
            total = len(receiving) + len(staging) + len(dock)
            if total == 1:
                single_area_warehouses.append(config.warehouse_id)
    
    for warehouse_id in single_area_warehouses[:3]:  # Test first 3
        test_specific_warehouse(warehouse_id)