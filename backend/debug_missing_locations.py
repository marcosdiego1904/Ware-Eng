#!/usr/bin/env python3
"""
Debug script to find missing special locations
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseTemplate, Location, WarehouseConfig

def debug_missing_locations():
    with app.app_context():
        print("=== DEBUGGING MISSING SPECIAL LOCATIONS ===\n")
        
        # Get DEFAULT warehouse config
        config = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').first()
        if not config:
            print("No DEFAULT warehouse config found!")
            return
        
        print(f"Warehouse Config: {config.warehouse_name} (ID: {config.id})")
        print(f"Warehouse ID: {config.warehouse_id}")
        
        # Check what special areas should exist according to config
        receiving_areas = config.get_receiving_areas()
        staging_areas = config.get_staging_areas()
        dock_areas = config.get_dock_areas()
        
        print(f"\nSPECIAL AREAS IN CONFIG:")
        print(f"  Receiving areas: {len(receiving_areas)} - {receiving_areas}")
        print(f"  Staging areas: {len(staging_areas)} - {staging_areas}")
        print(f"  Dock areas: {len(dock_areas)} - {dock_areas}")
        
        expected_locations = []
        for area in receiving_areas:
            expected_locations.append(f"{config.warehouse_id}_{area['code']}" if area['code'] != area['code'] else area['code'])
        for area in staging_areas:
            expected_locations.append(f"{config.warehouse_id}_{area['code']}" if area['code'] != area['code'] else area['code'])
        for area in dock_areas:
            expected_locations.append(f"{config.warehouse_id}_{area['code']}" if area['code'] != area['code'] else area['code'])
        
        print(f"\nEXPECTED LOCATION CODES: {expected_locations}")
        
        # Check what actually exists in database
        actual_special_locations = Location.query.filter(
            Location.warehouse_id == config.warehouse_id,
            Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
        ).all()
        
        actual_codes = [loc.code for loc in actual_special_locations]
        print(f"ACTUAL LOCATION CODES: {actual_codes}")
        
        print(f"\nCOMPARISON:")
        missing_codes = []
        for expected in expected_locations:
            if expected not in actual_codes:
                missing_codes.append(expected)
                print(f"  MISSING: {expected}")
        
        extra_codes = []
        for actual in actual_codes:
            if actual not in expected_locations:
                extra_codes.append(actual)
                print(f"  EXTRA: {actual}")
        
        if not missing_codes and not extra_codes:
            print("  All locations match!")
        
        print(f"\nSUMMARY:")
        print(f"  Expected: {len(expected_locations)} special areas")
        print(f"  Found: {len(actual_special_locations)} special areas")
        print(f"  Missing: {len(missing_codes)} locations")
        print(f"  Extra: {len(extra_codes)} locations")
        
        # Show details of existing locations
        print(f"\nDETAILS OF EXISTING SPECIAL LOCATIONS:")
        for loc in actual_special_locations:
            print(f"  {loc.code} ({loc.location_type}) - Zone: {loc.zone}, Capacity: {loc.capacity}")

if __name__ == "__main__":
    debug_missing_locations()