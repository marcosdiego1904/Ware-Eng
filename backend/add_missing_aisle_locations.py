#!/usr/bin/env python3
"""
Add missing AISLE locations for existing warehouses
This fixes warehouses that were created without AISLE locations
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig, Location


def add_missing_aisle_locations():
    """Add AISLE locations for warehouses that are missing them"""
    with app.app_context():
        print("=== ADDING MISSING AISLE LOCATIONS ===\n")
        
        configs = WarehouseConfig.query.all()
        total_created = 0
        
        for config in configs:
            if not config.num_aisles or config.num_aisles <= 0:
                continue
                
            print(f"Checking warehouse: {config.warehouse_name} ({config.warehouse_id})")
            print(f"  Configured aisles: {config.num_aisles}")
            
            # Check existing AISLE locations
            existing_aisle_locs = Location.query.filter(
                Location.warehouse_id == config.warehouse_id,
                Location.code.like('AISLE%')
            ).all()
            
            print(f"  Existing AISLE locations: {len(existing_aisle_locs)}")
            
            if len(existing_aisle_locs) >= config.num_aisles:
                print(f"  [OK] Already has sufficient AISLE locations")
                continue
            
            # Create missing AISLE locations
            created_for_warehouse = 0
            for aisle_num in range(1, config.num_aisles + 1):
                aisle_code = f'AISLE-{aisle_num:02d}'
                
                # Check if this specific AISLE location already exists
                existing = Location.query.filter_by(
                    warehouse_id=config.warehouse_id,
                    code=aisle_code
                ).first()
                
                if existing:
                    print(f"    [EXISTS] {aisle_code}")
                    continue
                
                # Create the AISLE location
                aisle_location = Location(
                    code=aisle_code,
                    location_type='TRANSITIONAL',
                    capacity=10,  # Temporary capacity for pallets in transit
                    pallet_capacity=10,
                    zone='GENERAL',
                    warehouse_id=config.warehouse_id,
                    created_by=config.created_by,
                    is_active=True
                )
                
                db.session.add(aisle_location)
                created_for_warehouse += 1
                print(f"    [CREATED] {aisle_code} (TRANSITIONAL)")
            
            if created_for_warehouse > 0:
                try:
                    db.session.commit()
                    total_created += created_for_warehouse
                    print(f"  [SUCCESS] Created {created_for_warehouse} AISLE locations")
                except Exception as e:
                    db.session.rollback()
                    print(f"  [ERROR] Failed to create AISLE locations: {e}")
            else:
                print(f"  [SKIP] No new AISLE locations needed")
            
            print()
        
        print(f"=== SUMMARY ===")
        print(f"Total AISLE locations created: {total_created}")
        print(f"Processed {len(configs)} warehouse configurations")
        
        if total_created > 0:
            print(f"\n[SUCCESS] AISLE locations fix completed!")
            print(f"AISLE locations should now appear in the Special Areas Management UI")
        else:
            print(f"\n[INFO] No AISLE locations needed to be created")


if __name__ == "__main__":
    add_missing_aisle_locations()