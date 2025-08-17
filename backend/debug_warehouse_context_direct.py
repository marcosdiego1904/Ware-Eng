#!/usr/bin/env python3
"""
Debug warehouse context by calling the exact SQL query that the logs show
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location

def debug_warehouse_context_direct():
    """Debug the warehouse context detection directly"""
    
    with app.app_context():
        print("=== DEBUGGING WAREHOUSE CONTEXT DETECTION ===")
        
        # Check current database file being used
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        print(f"Database URI: {db_uri}")
        
        # Check total locations in the current database context
        total_locations = db.session.query(Location).count()
        print(f"Total locations in current context: {total_locations}")
        
        # Get all warehouses
        warehouses = db.session.query(
            Location.warehouse_id,
            db.func.count(Location.id).label('count')
        ).group_by(Location.warehouse_id).all()
        
        print("\nWarehouse distribution:")
        for warehouse_id, count in warehouses:
            print(f"  {warehouse_id}: {count} locations")
        
        # Sample real inventory locations that produced the DEFAULT detection
        inventory_locations = [
            '02-1-011B', '01-1-007B', '01-1-019A', '02-1-003B', 
            '01-1-004C', '02-1-021A', '01-1-014C', '01-1-001C',
            '02-1-016B', '02-1-003B', '02-1-025B', '01-1-022C',
            'RECV-01', 'RECV-02', 'STAGE-01', 'AISLE-01', 'AISLE-02'
        ]
        
        print(f"\nTesting with {len(inventory_locations)} inventory locations")
        print("Sample locations:", inventory_locations[:5])
        
        # Run the exact SQL query from the rule engine
        from sqlalchemy import func, or_, case
        
        print("\n=== RUNNING WAREHOUSE MATCHING QUERY ===")
        warehouse_matches = db.session.query(
            Location.warehouse_id,
            func.count(Location.id).label('total_locations'),
            func.sum(
                case(
                    (Location.code.in_(inventory_locations), 1),
                    else_=0
                )
            ).label('matching_locations')
        ).filter(
            or_(Location.is_active == True, Location.is_active.is_(None))
        ).group_by(Location.warehouse_id).all()
        
        print("Warehouse matching results:")
        best_match = None
        best_score = 0
        
        for warehouse_id, total_locations, matching_locations in warehouse_matches:
            if matching_locations and matching_locations > 0:
                score = matching_locations / len(inventory_locations)
                print(f"  {warehouse_id}: {matching_locations}/{len(inventory_locations)} locations matched = {score:.1%} (total: {total_locations})")
                if score > best_score:
                    best_score = score
                    best_match = warehouse_id
            else:
                print(f"  {warehouse_id}: 0/{len(inventory_locations)} locations matched = 0% (total: {total_locations})")
        
        print(f"\nBest match: {best_match} with {best_score:.1%} score")
        
        # Check which specific locations are matching
        print(f"\n=== LOCATION MATCHING DETAILS ===")
        for warehouse_id, _, _ in warehouse_matches:
            print(f"\n{warehouse_id} warehouse locations:")
            matching_locs = db.session.query(Location.code).filter(
                Location.warehouse_id == warehouse_id,
                Location.code.in_(inventory_locations)
            ).all()
            
            if matching_locs:
                print(f"  Matching locations: {[loc.code for loc in matching_locs]}")
            else:
                print(f"  No matching locations found")

if __name__ == '__main__':
    debug_warehouse_context_direct()