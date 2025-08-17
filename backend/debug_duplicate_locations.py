#!/usr/bin/env python3
"""
Debug duplicate location codes across warehouses
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_duplicate_locations():
    """Debug if there are duplicate location codes across warehouses"""
    
    from app import app, db
    from models import Location
    from sqlalchemy import func
    
    with app.app_context():
        # Find location codes that exist in multiple warehouses
        duplicates = db.session.query(
            Location.code,
            func.count(func.distinct(Location.warehouse_id)).label('warehouse_count'),
            func.group_concat(func.distinct(Location.warehouse_id)).label('warehouses')
        ).group_by(Location.code).having(
            func.count(func.distinct(Location.warehouse_id)) > 1
        ).all()
        
        print(f"Found {len(duplicates)} location codes that exist in multiple warehouses:")
        
        for code, warehouse_count, warehouses in duplicates[:20]:
            print(f"  {code}: {warehouse_count} warehouses ({warehouses})")
        
        if len(duplicates) > 20:
            print(f"  ... and {len(duplicates) - 20} more duplicates")
        
        # Check specific warehouse contents
        print(f"\n=== WAREHOUSE CONTENTS ANALYSIS ===")
        
        warehouses = db.session.query(Location.warehouse_id).distinct().all()
        
        for (warehouse_id,) in warehouses:
            locations = db.session.query(Location.code).filter_by(warehouse_id=warehouse_id).all()
            location_codes = [loc.code for loc in locations]
            
            print(f"\n{warehouse_id}: {len(location_codes)} locations")
            
            # Sample a few codes
            sample_codes = location_codes[:10]
            print(f"  Sample: {sample_codes}")
            
            # Check for problematic patterns like DEFAULT_ prefixes
            defaulty_codes = [code for code in location_codes if 'DEFAULT' in code or code.startswith('WH')]
            if defaulty_codes:
                print(f"  Problematic codes: {defaulty_codes[:5]}")
        
        # Test the exact scenario from production
        print(f"\n=== PRODUCTION SCENARIO TEST ===")
        
        # Sample locations from the production log that caused issues
        problem_locations = [
            "02-1-016B", "01-1-011A", "02-1-011B", "01-1-007B", "01-1-019A",
            "FAKE-AREA", "UNKNOWN-99", "BADLOC-01"
        ]
        
        print(f"Testing problem locations from production:")
        
        for loc in problem_locations:
            matches = db.session.query(Location.warehouse_id, Location.code).filter_by(code=loc).all()
            if matches:
                warehouse_list = [match.warehouse_id for match in matches]
                print(f"  {loc}: {warehouse_list}")
            else:
                print(f"  {loc}: NOT_FOUND")

if __name__ == '__main__':
    debug_duplicate_locations()