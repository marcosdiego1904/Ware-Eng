#!/usr/bin/env python3
"""
Test whether aisle locations should be created by default
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig, Location

def check_existing_aisle_locations():
    """Check if any physical aisle locations exist in the database"""
    print("CHECKING FOR EXISTING AISLE LOCATIONS")
    print("=" * 40)
    
    with app.app_context():
        # Check for physical AISLE locations
        aisle_locations = Location.query.filter(
            Location.code.like('AISLE%')
        ).all()
        
        print(f"Physical AISLE locations found: {len(aisle_locations)}")
        for loc in aisle_locations[:5]:
            print(f"  - {loc.code} ({loc.location_type}) in {loc.warehouse_id}")
        
        # Check for TRANSITIONAL type locations
        transitional_locations = Location.query.filter(
            Location.location_type == 'TRANSITIONAL'
        ).all()
        
        print(f"\nPhysical TRANSITIONAL locations found: {len(transitional_locations)}")
        for loc in transitional_locations[:5]:
            print(f"  - {loc.code} ({loc.location_type}) in {loc.warehouse_id}")
        
        # Check configs to see if any have aisle-related special areas
        configs = WarehouseConfig.query.all()
        aisle_in_configs = 0
        
        for config in configs:
            receiving = config.get_receiving_areas()
            staging = config.get_staging_areas() 
            dock = config.get_dock_areas()
            
            all_areas = receiving + staging + dock
            aisle_codes = [area['code'] for area in all_areas if 'AISLE' in area.get('code', '')]
            
            if aisle_codes:
                aisle_in_configs += 1
                print(f"  Config {config.warehouse_id} has AISLE codes: {aisle_codes}")
        
        print(f"\nConfigs with AISLE special areas: {aisle_in_configs}")
        
        return len(aisle_locations) > 0 or aisle_in_configs > 0

def test_with_aisle_flag():
    """Test virtual engine with aisle flag enabled"""
    print("\nTESTING WITH AISLE FLAG ENABLED")
    print("=" * 40)
    
    with app.app_context():
        config = WarehouseConfig.query.first()
        if not config:
            print("No config found")
            return
            
        config_dict = config.to_dict()
        config_dict['auto_create_aisle_areas'] = True  # Enable flag
        
        print(f"Testing with warehouse: {config.warehouse_id}")
        print(f"Number of aisles: {config_dict.get('num_aisles', 0)}")
        
        from virtual_location_engine import VirtualLocationEngine
        engine = VirtualLocationEngine(config_dict)
        
        print(f"Special areas with aisle flag: {len(engine.special_areas)}")
        aisle_areas = {k: v for k, v in engine.special_areas.items() if 'AISLE' in k}
        
        print(f"AISLE areas generated: {len(aisle_areas)}")
        for code, info in aisle_areas.items():
            print(f"  - {code}: {info}")

if __name__ == "__main__":
    has_existing = check_existing_aisle_locations()
    test_with_aisle_flag()
    
    print(f"\nCONCLUSION:")
    if has_existing:
        print("- Existing AISLE locations found - should enable auto_create_aisle_areas by default")
    else:
        print("- No existing AISLE locations - may be optional feature")
        print("- But user expects them, so should probably enable by default")