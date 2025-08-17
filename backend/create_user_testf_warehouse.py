#!/usr/bin/env python3
"""
Create USER_TESTF warehouse and locations for testing
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location

def create_user_testf_warehouse():
    """Create USER_TESTF warehouse with all required locations"""
    
    with app.app_context():
        print("Creating USER_TESTF warehouse locations...")
        
        # Check if already exists
        existing = db.session.query(Location).filter(
            Location.warehouse_id == 'USER_TESTF'
        ).count()
        
        if existing > 0:
            print(f"USER_TESTF already has {existing} locations. Skipping creation.")
            return
        
        locations_to_create = []
        
        # First, delete any existing conflicting locations
        print("Checking for and removing any existing conflicts...")
        conflicting_codes = ['RECV-01', 'RECV-02', 'STAGE-01', 'DOCK-01', 'AISLE-01', 'AISLE-02']
        for code in conflicting_codes:
            existing = db.session.query(Location).filter(Location.code == code).first()
            if existing:
                print(f"  Removing existing {code} from warehouse {existing.warehouse_id}")
                db.session.delete(existing)
        
        # Remove any existing storage positions that might conflict
        existing_storage = db.session.query(Location).filter(
            Location.code.like('__-__-___?')
        ).all()
        if existing_storage:
            print(f"  Removing {len(existing_storage)} existing storage positions")
            for loc in existing_storage:
                db.session.delete(loc)
        
        db.session.commit()
        print("Conflicts resolved.")
        
        # Special areas (6 locations) - includes both location_type and zone
        special_areas = [
            ('RECV-01', 'RECEIVING', 'RECEIVING', 10),
            ('RECV-02', 'RECEIVING', 'RECEIVING', 10), 
            ('STAGE-01', 'STAGING', 'STAGING', 5),
            ('DOCK-01', 'DOCK', 'DOCK', 2),
            ('AISLE-01', 'TRANSITIONAL', 'GENERAL', 10),
            ('AISLE-02', 'TRANSITIONAL', 'GENERAL', 10),
        ]
        
        for code, location_type, zone, capacity in special_areas:
            location = Location(
                warehouse_id='USER_TESTF',
                code=code,
                location_type=location_type,
                zone=zone,
                pallet_capacity=capacity,
                is_active=True
            )
            locations_to_create.append(location)
        
        # Storage positions (150 locations: 2 aisles × 1 rack × 25 positions × 3 levels)
        for aisle in range(1, 3):  # 01, 02
            for rack in range(1, 2):  # 01 
                for position in range(1, 26):  # 001-025
                    for level in ['A', 'B', 'C']:
                        code = f"{aisle:02d}-{rack:02d}-{position:03d}{level}"
                        location = Location(
                            warehouse_id='USER_TESTF',
                            code=code,
                            location_type='STORAGE',
                            zone='STORAGE',
                            pallet_capacity=2,  # 2 pallets per level
                            is_active=True
                        )
                        locations_to_create.append(location)
        
        # Bulk insert all locations
        print(f"Creating {len(locations_to_create)} locations...")
        db.session.add_all(locations_to_create)
        db.session.commit()
        
        # Verify creation
        total_created = db.session.query(Location).filter(
            Location.warehouse_id == 'USER_TESTF'
        ).count()
        
        print(f"✅ Successfully created {total_created} locations for USER_TESTF warehouse")
        
        # Show breakdown
        special_count = db.session.query(Location).filter(
            Location.warehouse_id == 'USER_TESTF',
            Location.code.in_(['RECV-01', 'RECV-02', 'STAGE-01', 'DOCK-01', 'AISLE-01', 'AISLE-02'])
        ).count()
        
        storage_count = db.session.query(Location).filter(
            Location.warehouse_id == 'USER_TESTF',
            Location.code.like('__-__-___*')
        ).count()
        
        print(f"  - Special areas: {special_count}")
        print(f"  - Storage positions: {storage_count}")

if __name__ == '__main__':
    create_user_testf_warehouse()