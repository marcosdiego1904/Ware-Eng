#!/usr/bin/env python3
"""
Debug DEFAULT warehouse and what's causing the mismatch
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_default_warehouse():
    """Debug what's in DEFAULT warehouse"""
    
    from app import app, db
    from models import Location
    
    with app.app_context():
        # Get DEFAULT warehouse locations
        default_locations = db.session.query(Location).filter_by(warehouse_id='DEFAULT').all()
        
        print(f"DEFAULT warehouse has {len(default_locations)} locations")
        
        # Show some examples
        print("\nSample DEFAULT locations:")
        for i, location in enumerate(default_locations[:20]):
            print(f"  {location.code} ({location.location_type})")
        
        if len(default_locations) > 20:
            print(f"  ... and {len(default_locations) - 20} more")
        
        # Check if USER_TESTF structure matches what we expect
        print(f"\nUSER_TESTF warehouse structure check:")
        user_testf_locations = db.session.query(Location).filter_by(warehouse_id='USER_TESTF').all()
        
        # Based on your structure: 2 aisles × 1 racks × 25 positions × 3 levels
        expected_storage_locations = 2 * 1 * 25 * 3  # = 150 storage locations
        
        storage_locations = [loc for loc in user_testf_locations if loc.location_type == 'STORAGE']
        
        print(f"Expected storage locations: {expected_storage_locations}")
        print(f"Actual storage locations: {len(storage_locations)}")
        
        # Check the pattern
        print(f"\nStorage location patterns:")
        patterns = {}
        for loc in storage_locations[:10]:
            code = loc.code
            # Extract pattern (aisle-rack-position-level)
            if '-' in code:
                parts = code.split('-')
                if len(parts) >= 2:
                    pattern = f"{parts[0]}-{parts[1]}-XXX"
                    patterns[pattern] = patterns.get(pattern, 0) + 1
        
        for pattern, count in patterns.items():
            print(f"  {pattern}: {count} locations")
        
        # The real issue: Check what specific locations from the inventory are NOT in USER_TESTF
        print(f"\n=== INVENTORY MISMATCH ANALYSIS ===")
        
        # Sample problematic inventory locations (based on the production output)
        sample_inventory = [
            "02-1-016B", "01-1-011A", "01-1-008B", "02-1-017C", "01-1-022C",
            "FAKE-AREA", "UNKNOWN-99", "BADLOC-01", "02-01-023A"
        ]
        
        print(f"Checking problematic inventory locations:")
        
        for inv_loc in sample_inventory:
            user_testf_match = db.session.query(Location).filter_by(
                warehouse_id='USER_TESTF',
                code=inv_loc
            ).first()
            
            default_match = db.session.query(Location).filter_by(
                warehouse_id='DEFAULT',
                code=inv_loc
            ).first()
            
            status = []
            if user_testf_match:
                status.append("USER_TESTF")
            if default_match:
                status.append("DEFAULT")
            if not status:
                status.append("NOT_FOUND")
            
            print(f"  {inv_loc}: {', '.join(status)}")

if __name__ == '__main__':
    debug_default_warehouse()