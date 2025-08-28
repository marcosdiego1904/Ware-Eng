#!/usr/bin/env python3
"""
Debug why only one special location shows in production despite creating multiple
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig, Location
from virtual_compatibility_layer import get_compatibility_manager

def debug_missing_locations():
    """Debug the single location issue"""
    print("DEBUGGING PRODUCTION SPECIAL LOCATIONS ISSUE")
    print("=" * 60)
    
    with app.app_context():
        # Check database type
        db_url = app.config.get('DATABASE_URL', 'sqlite')
        db_type = 'PostgreSQL' if 'postgresql' in db_url else 'SQLite'
        print(f"Database: {db_type}")
        
        # Test with the warehouse from the screenshot (assuming it's USER_MARCOS9)
        # You can change this to match your actual warehouse ID
        warehouse_id = 'USER_MARCOS9'
        
        print(f"\nDebugging warehouse: {warehouse_id}")
        print("-" * 40)
        
        # Step 1: Check warehouse config
        config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
        if not config:
            print("ERROR: No warehouse config found!")
            return
            
        print(f"Warehouse Config Found: {config.warehouse_name}")
        
        # Step 2: Check special areas in config
        receiving = config.get_receiving_areas()
        staging = config.get_staging_areas()
        dock = config.get_dock_areas()
        
        print(f"\nConfig Special Areas:")
        print(f"  Receiving areas: {len(receiving)} - {[area.get('code') for area in receiving]}")
        print(f"  Staging areas: {len(staging)} - {[area.get('code') for area in staging]}")
        print(f"  Dock areas: {len(dock)} - {[area.get('code') for area in dock]}")
        
        total_config_special = len(receiving) + len(staging) + len(dock)
        print(f"  Total in config: {total_config_special}")
        
        if total_config_special <= 1:
            print("ISSUE FOUND: Your config only has 1 or 0 special areas!")
            print("This explains why you only see 1 location.")
            print("You need to add more special areas to your warehouse config.")
            return
        
        # Step 3: Check virtual engine
        compat_manager = get_compatibility_manager()
        is_virtual = compat_manager.is_virtual_warehouse(warehouse_id)
        print(f"\nVirtual warehouse detected: {is_virtual}")
        
        if not is_virtual:
            print("ERROR: Warehouse not detected as virtual!")
            return
            
        # Step 4: Test virtual engine directly
        config_dict = config.to_dict()
        from virtual_location_engine import VirtualLocationEngine
        engine = VirtualLocationEngine(config_dict)
        
        print(f"\nVirtual Engine Analysis:")
        print(f"  Special areas in engine: {len(engine.special_areas)}")
        
        for code, info in engine.special_areas.items():
            print(f"    {code}: {info['location_type']} - Zone: {info['zone']}")
        
        # Step 5: Test location retrieval
        locations = compat_manager.get_all_warehouse_locations(warehouse_id)
        special_locs = [
            loc for loc in locations 
            if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL']
        ]
        
        print(f"\nRetrieved Locations:")
        print(f"  Total locations: {len(locations)}")
        print(f"  Special locations: {len(special_locs)}")
        
        for loc in special_locs:
            print(f"    {loc['code']} ({loc['location_type']}) - Zone: {loc['zone']} - Source: {loc.get('source')}")
        
        # Step 6: Check if pagination is cutting off results
        if len(locations) == 100:
            print("WARNING: Exactly 100 locations retrieved - might be pagination limit!")
        
        # Step 7: Check physical locations (in case of mixed mode)
        physical_special = Location.query.filter(
            Location.warehouse_id == warehouse_id,
            Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL'])
        ).all()
        
        print(f"\nPhysical Special Locations in DB:")
        print(f"  Count: {len(physical_special)}")
        for loc in physical_special:
            print(f"    {loc.code} ({loc.location_type}) - Physical")

def test_location_creation():
    """Test creating a new special location to see if it appears"""
    print("\n" + "=" * 60)
    print("TEST: Creating a new special location")
    print("=" * 60)
    
    with app.app_context():
        warehouse_id = 'USER_MARCOS9'  # Change this to your warehouse ID
            
        config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
        if not config:
            print("No config found")
            return
        
        # Add a test staging area to config
        staging_areas = config.get_staging_areas()
        test_area = {
            'code': 'STAGE-TEST',
            'type': 'STAGING', 
            'capacity': 8,
            'zone': 'STAGING'
        }
        
        if not any(area.get('code') == 'STAGE-TEST' for area in staging_areas):
            staging_areas.append(test_area)
            config.set_staging_areas(staging_areas)
            db.session.commit()
            print("Added STAGE-TEST to config")
        else:
            print("STAGE-TEST already exists in config")
        
        # Test if it appears in virtual engine
        compat_manager = get_compatibility_manager()
        locations = compat_manager.get_all_warehouse_locations(warehouse_id)
        test_loc = [loc for loc in locations if loc.get('code') == 'STAGE-TEST']
        
        if test_loc:
            print("SUCCESS: STAGE-TEST appears in virtual locations!")
        else:
            print("PROBLEM: STAGE-TEST not found in virtual locations")

if __name__ == "__main__":
    debug_missing_locations()
    
    print("\n" + "=" * 60)
    print("Testing location creation automatically...")
    test_location_creation()