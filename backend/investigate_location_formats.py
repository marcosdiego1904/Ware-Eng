#!/usr/bin/env python3
"""
Investigate location formats in different warehouses
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location

def investigate_location_formats():
    """Investigate location formats across warehouses"""
    
    with app.app_context():
        print("=== WAREHOUSE LOCATION FORMAT INVESTIGATION ===")
        
        # Get warehouse distribution
        warehouses = db.session.query(
            Location.warehouse_id,
            db.func.count(Location.id).label('count')
        ).group_by(Location.warehouse_id).all()
        
        print("\nWarehouse Distribution:")
        for warehouse_id, count in warehouses:
            print(f"  {warehouse_id}: {count} locations")
        
        # Sample DEFAULT warehouse locations
        print("\nDEFAULT Warehouse Sample Locations:")
        default_locations = db.session.query(Location.code).filter(
            Location.warehouse_id == 'DEFAULT'
        ).limit(10).all()
        
        for location in default_locations:
            print(f"  {location.code}")
        
        # Sample USER_TESTF warehouse locations  
        print("\nUSER_TESTF Warehouse Sample Locations:")
        user_testf_locations = db.session.query(Location.code).filter(
            Location.warehouse_id == 'USER_TESTF'
        ).limit(10).all()
        
        for location in user_testf_locations:
            print(f"  {location.code}")
        
        # Check for specific patterns in real inventory
        real_inventory_locations = [
            '02-1-011B', '01-1-007B', '01-1-019A', '02-1-003B', 
            '01-1-004C', '02-1-021A', '01-1-014C'
        ]
        
        print(f"\nReal Inventory Location Validation:")
        for loc_code in real_inventory_locations:
            # Check in DEFAULT
            default_match = db.session.query(Location).filter(
                Location.warehouse_id == 'DEFAULT',
                Location.code == loc_code
            ).first()
            
            # Check in USER_TESTF
            user_testf_match = db.session.query(Location).filter(
                Location.warehouse_id == 'USER_TESTF', 
                Location.code == loc_code
            ).first()
            
            print(f"  {loc_code}:")
            print(f"    DEFAULT: {'FOUND' if default_match else 'NOT FOUND'}")
            print(f"    USER_TESTF: {'FOUND' if user_testf_match else 'NOT FOUND'}")

if __name__ == '__main__':
    investigate_location_formats()