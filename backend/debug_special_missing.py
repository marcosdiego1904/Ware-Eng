#!/usr/bin/env python3
"""
Debug why special areas exist in virtual engine but don't appear in location list
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig
from virtual_compatibility_layer import get_compatibility_manager

def debug_missing_special_areas():
    """Debug why special areas are missing from location list"""
    print("DEBUGGING MISSING SPECIAL AREAS")
    print("=" * 40)
    
    with app.app_context():
        compat_manager = get_compatibility_manager()
        
        # Test with TEST_WAREHOUSE_001 which has the issue
        warehouse_id = 'TEST_WAREHOUSE_001'
        
        print(f"Testing warehouse: {warehouse_id}")
        
        # Get config 
        config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
        if not config:
            print("Config not found!")
            return
            
        config_dict = config.to_dict()
        print(f"Special areas in config: {config_dict.get('receiving_areas')}")
        
        # Create virtual engine directly
        from virtual_location_engine import VirtualLocationEngine
        engine = VirtualLocationEngine(config_dict)
        
        print(f"Special areas in engine: {len(engine.special_areas)}")
        for code, info in engine.special_areas.items():
            print(f"  Engine has: {code} -> {info}")
        
        # Get warehouse summary
        summary = engine.get_warehouse_summary()
        print(f"Warehouse summary special areas: {summary.get('special_areas_list')}")
        
        # Test each special area individually
        for code in engine.special_areas.keys():
            props = engine.get_location_properties(code)
            print(f"  Properties for {code}: {props}")
        
        # Now test through compatibility manager
        print("\nTesting through compatibility manager:")
        locations = compat_manager.get_all_warehouse_locations(warehouse_id)
        print(f"Total locations from compat manager: {len(locations)}")
        
        special_locs = [loc for loc in locations if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK']]
        print(f"Special locations from compat manager: {len(special_locs)}")
        
        for loc in special_locs:
            print(f"  Compat manager has: {loc['code']} ({loc['location_type']}) source: {loc.get('source')}")
        
        # Check if the issue is in _get_all_virtual_locations
        print("\nTesting _get_all_virtual_locations directly:")
        try:
            virtual_locs = compat_manager._get_all_virtual_locations(engine, limit=1000)
            print(f"Virtual locations from _get_all_virtual_locations: {len(virtual_locs)}")
            
            virtual_special = [loc for loc in virtual_locs if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK']]
            print(f"Virtual special from direct method: {len(virtual_special)}")
            
            for loc in virtual_special:
                print(f"  Direct method has: {loc['code']} ({loc['location_type']})")
                
        except Exception as e:
            print(f"Error testing _get_all_virtual_locations: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_missing_special_areas()