#!/usr/bin/env python3
"""
Fix script to create missing dock locations for DEFAULT warehouse
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseTemplate, Location, WarehouseConfig

def fix_missing_dock_locations():
    with app.app_context():
        print("=== FIXING MISSING DOCK LOCATIONS ===\n")
        
        # Get DEFAULT warehouse config
        config = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').first()
        if not config:
            print("No DEFAULT warehouse config found!")
            return
        
        print(f"Warehouse Config: {config.warehouse_name}")
        
        # Get dock areas from config
        dock_areas = config.get_dock_areas()
        print(f"Dock areas in config: {dock_areas}")
        
        if not dock_areas:
            print("No dock areas defined in config")
            return
        
        # Check which dock locations already exist
        existing_dock_locations = Location.query.filter(
            Location.warehouse_id == config.warehouse_id,
            Location.location_type == 'DOCK'
        ).all()
        
        existing_codes = [loc.code for loc in existing_dock_locations]
        print(f"Existing dock locations: {existing_codes}")
        
        # Create missing dock locations
        created_count = 0
        for area in dock_areas:
            expected_code = area['code']
            
            if expected_code not in existing_codes:
                print(f"Creating missing dock location: {expected_code}")
                
                location = Location(
                    code=expected_code,
                    location_type='DOCK',
                    capacity=area.get('capacity', 2),
                    pallet_capacity=area.get('capacity', 2),
                    zone=area.get('zone', 'DOCK'),
                    warehouse_id=config.warehouse_id,
                    created_by=1  # Assuming user ID 1 exists
                )
                
                db.session.add(location)
                created_count += 1
            else:
                print(f"Dock location already exists: {expected_code}")
        
        if created_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully created {created_count} missing dock locations")
        else:
            print(f"\n✅ No dock locations needed to be created")
        
        # Verify the fix
        print(f"\n=== VERIFICATION ===")
        all_special_locations = Location.query.filter(
            Location.warehouse_id == config.warehouse_id,
            Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
        ).all()
        
        print(f"Total special locations now: {len(all_special_locations)}")
        for loc in all_special_locations:
            print(f"  {loc.code} ({loc.location_type}) - Zone: {loc.zone}, Capacity: {loc.capacity}")

if __name__ == "__main__":
    fix_missing_dock_locations()