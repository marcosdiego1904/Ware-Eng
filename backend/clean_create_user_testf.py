#!/usr/bin/env python3
"""
Clean database and create USER_TESTF warehouse properly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location

def clean_and_create_user_testf():
    """Clean database and create USER_TESTF warehouse with all required locations"""
    
    with app.app_context():
        print("=== CLEANING DATABASE ===")
        
        # Delete ALL existing locations to start fresh
        deleted_count = db.session.query(Location).delete()
        db.session.commit()
        print(f"Deleted {deleted_count} existing locations")
        
        print("\n=== CREATING USER_TESTF WAREHOUSE ===")
        
        locations_to_create = []
        
        # Special areas (6 locations)
        special_areas = [
            ('RECV-01', 'RECEIVING', 'RECEIVING', 10),
            ('RECV-02', 'RECEIVING', 'RECEIVING', 10), 
            ('STAGE-01', 'STAGING', 'STAGING', 5),
            ('DOCK-01', 'DOCK', 'DOCK', 2),
            ('AISLE-01', 'TRANSITIONAL', 'GENERAL', 10),
            ('AISLE-02', 'TRANSITIONAL', 'GENERAL', 10),
        ]
        
        print("Creating special areas...")
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
            print(f"  {code} ({location_type}, capacity: {capacity})")
        
        # Storage positions (150 locations: 2 aisles × 1 rack × 25 positions × 3 levels)
        print("Creating storage positions...")
        storage_count = 0
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
                            aisle_number=aisle,
                            rack_number=rack,
                            position_number=position,
                            level=level,
                            pallet_capacity=2,  # 2 pallets per level
                            is_active=True
                        )
                        locations_to_create.append(location)
                        storage_count += 1
        
        print(f"  {storage_count} storage positions created")
        
        # Bulk insert all locations
        print(f"\nInserting {len(locations_to_create)} locations into database...")
        db.session.add_all(locations_to_create)
        db.session.commit()
        
        # Verify creation
        total_created = db.session.query(Location).filter(
            Location.warehouse_id == 'USER_TESTF'
        ).count()
        
        print(f"\n✅ SUCCESS: Created {total_created} locations for USER_TESTF warehouse")
        
        # Show breakdown
        special_count = db.session.query(Location).filter(
            Location.warehouse_id == 'USER_TESTF',
            Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL'])
        ).count()
        
        storage_count_verify = db.session.query(Location).filter(
            Location.warehouse_id == 'USER_TESTF',
            Location.location_type == 'STORAGE'
        ).count()
        
        print(f"  - Special areas: {special_count}")
        print(f"  - Storage positions: {storage_count_verify}")
        print(f"  - Total capacity: {special_count * 8 + storage_count_verify * 2} pallets")
        
        print("\n=== VERIFICATION ===")
        # Test specific locations from our test file
        test_locations = ['RECV-01', 'RECV-02', 'AISLE-01', 'AISLE-02', '01-01-001A', '02-01-025C']
        for code in test_locations:
            loc = db.session.query(Location).filter(Location.code == code).first()
            if loc:
                print(f"✅ {code}: {loc.location_type} in {loc.warehouse_id} (capacity: {loc.pallet_capacity})")
            else:
                print(f"❌ {code}: NOT FOUND")

if __name__ == '__main__':
    clean_and_create_user_testf()