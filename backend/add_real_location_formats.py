#!/usr/bin/env python3
"""
Add the real location formats used in production data to USER_TESTF warehouse
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location

def add_real_location_formats():
    """Add real location formats to USER_TESTF warehouse for better matching"""
    
    with app.app_context():
        print("=== ADDING REAL LOCATION FORMATS TO USER_TESTF ===")
        
        # Real location formats from production inventory (non-zero-padded rack numbers)
        real_location_formats = []
        
        # Generate storage locations with format: 01-1-001A (rack number not zero-padded)
        print("Creating storage locations with real format (01-1-001A)...")
        for aisle in range(1, 3):  # 01, 02
            for rack in range(1, 2):  # 1 (not zero-padded)
                for position in range(1, 26):  # 001-025
                    for level in ['A', 'B', 'C']:
                        code = f"{aisle:02d}-{rack}-{position:03d}{level}"
                        
                        # Check if already exists
                        existing = db.session.query(Location).filter_by(code=code).first()
                        if not existing:
                            location = Location(
                                warehouse_id='USER_TESTF',
                                code=code,
                                location_type='STORAGE',
                                zone='STORAGE',
                                aisle_number=aisle,
                                rack_number=rack,
                                position_number=position,
                                level=level,
                                pallet_capacity=2,
                                is_active=True
                            )
                            real_location_formats.append(location)
        
        # Add some special receiving locations that appear in real data
        special_locations = [
            ('RECV-01', 'RECEIVING', 'RECEIVING', 10),
            ('RECV-02', 'RECEIVING', 'RECEIVING', 10),
            ('RCV-001', 'RECEIVING', 'RECEIVING', 10),  # Alternative format
            ('RCV-002', 'RECEIVING', 'RECEIVING', 10),
            ('RCV-003', 'RECEIVING', 'RECEIVING', 10),
            ('RCV-004', 'RECEIVING', 'RECEIVING', 10),
            ('RCV-005', 'RECEIVING', 'RECEIVING', 10),
        ]
        
        print("Adding alternative receiving location formats...")
        for code, location_type, zone, capacity in special_locations:
            existing = db.session.query(Location).filter_by(code=code).first()
            if not existing:
                location = Location(
                    warehouse_id='USER_TESTF',
                    code=code,
                    location_type=location_type,
                    zone=zone,
                    pallet_capacity=capacity,
                    is_active=True
                )
                real_location_formats.append(location)
        
        # Bulk insert all new locations
        if real_location_formats:
            print(f"Adding {len(real_location_formats)} new location formats...")
            db.session.add_all(real_location_formats)
            db.session.commit()
            print("Successfully added new location formats!")
        else:
            print("No new locations to add - all formats already exist")
        
        # Verify final state
        total_user_testf = db.session.query(Location).filter(
            Location.warehouse_id == 'USER_TESTF'
        ).count()
        
        print(f"\nFinal USER_TESTF warehouse size: {total_user_testf} locations")
        
        # Test with real inventory locations
        real_inventory_locations = [
            '02-1-011B', '01-1-007B', '01-1-019A', '02-1-003B', 
            '01-1-004C', '02-1-021A', '01-1-014C', '01-1-001C',
            'RECV-01', 'RECV-02', 'RCV-001', 'AISLE-01', 'AISLE-02'
        ]
        
        print(f"\nTesting match with real inventory locations...")
        matching_count = db.session.query(Location).filter(
            Location.warehouse_id == 'USER_TESTF',
            Location.code.in_(real_inventory_locations)
        ).count()
        
        match_score = matching_count / len(real_inventory_locations)
        print(f"Match score: {matching_count}/{len(real_inventory_locations)} = {match_score:.1%}")
        
        if match_score > 0.8:
            print("✅ Excellent match! USER_TESTF should now be properly detected.")
        elif match_score > 0.5:
            print("✅ Good match! This should improve warehouse detection.")
        else:
            print("⚠️  Still low match - may need more location format variants.")

if __name__ == '__main__':
    add_real_location_formats()