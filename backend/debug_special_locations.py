#!/usr/bin/env python3
"""
Debug script to check special locations in templates and applied warehouses
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseTemplate, Location, WarehouseConfig

def debug_templates():
    with app.app_context():
        print("=== DEBUGGING SPECIAL LOCATIONS ===\n")
        
        # Check templates
        print("1. CHECKING TEMPLATES:")
        templates = WarehouseTemplate.query.limit(5).all()
        if not templates:
            print("   No templates found!")
            return
        
        for template in templates:
            print(f"   Template: {template.name} (ID: {template.id})")
            print(f"   Code: {template.template_code}")
            print(f"   Receiving areas raw: {template.receiving_areas_template}")
            print(f"   Staging areas raw: {template.staging_areas_template}")
            print(f"   Dock areas raw: {template.dock_areas_template}")
            
            try:
                receiving = template.get_receiving_areas_template()
                staging = template.get_staging_areas_template()
                dock = template.get_dock_areas_template()
                print(f"   Parsed - Receiving: {len(receiving)}, Staging: {len(staging)}, Dock: {len(dock)}")
                if receiving:
                    print(f"     Receiving areas: {receiving}")
                if staging:
                    print(f"     Staging areas: {staging}")
                if dock:
                    print(f"     Dock areas: {dock}")
            except Exception as e:
                print(f"   ERROR parsing special areas: {e}")
            print()
        
        # Check warehouse configs
        print("\n2. CHECKING WAREHOUSE CONFIGS:")
        configs = WarehouseConfig.query.limit(3).all()
        for config in configs:
            print(f"   Config: {config.warehouse_name} (ID: {config.id})")
            print(f"   Warehouse ID: {config.warehouse_id}")
            print(f"   Receiving areas: {config.receiving_areas}")
            print(f"   Staging areas: {config.staging_areas}")
            print(f"   Dock areas: {config.dock_areas}")
            print()
        
        # Check actual locations with new ordering
        print("\n3. CHECKING LOCATIONS WITH NEW ORDERING:")
        
        # Test the new ordering - same as API
        locations_ordered = Location.query.filter_by(warehouse_id='DEFAULT').order_by(
            db.case(
                (Location.location_type == 'RECEIVING', 1),
                (Location.location_type == 'STAGING', 2), 
                (Location.location_type == 'DOCK', 3),
                (Location.location_type == 'STORAGE', 4),
                else_=5
            ).asc(),
            Location.aisle_number.asc().nulls_last(),
            Location.rack_number.asc().nulls_last(),
            Location.position_number.asc().nulls_last(),
            Location.level.asc().nulls_last(),
            Location.code.asc()
        ).limit(20).all()
        
        print(f"   First 20 locations with new ordering:")
        for i, loc in enumerate(locations_ordered, 1):
            print(f"     {i:2d}. {loc.code} ({loc.location_type}) - Zone: {loc.zone}")
        
        special_locations = Location.query.filter(
            Location.warehouse_id == 'DEFAULT',
            Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
        ).all()
        print(f"\n   Total special area locations: {len(special_locations)}")
        
        for loc in special_locations:
            print(f"     - {loc.code} ({loc.location_type}) - Zone: {loc.zone}, Capacity: {loc.capacity}")
        
        if not special_locations:
            print("     No special area locations found!")

if __name__ == "__main__":
    debug_templates()