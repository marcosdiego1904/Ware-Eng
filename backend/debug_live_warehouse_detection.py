#!/usr/bin/env python3
"""
Debug warehouse detection in live context by calling the exact same code path
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location
from rule_engine import RuleEngine

def debug_live_warehouse_detection():
    """Debug warehouse detection using same context as live app"""
    
    with app.app_context():
        print("=== DEBUGGING LIVE WAREHOUSE DETECTION ===")
        
        # Check current database file being used
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        print(f"Database URI: {db_uri}")
        
        # Check total locations in the current database context
        total_locations = db.session.query(Location).count()
        print(f"Total locations in current context: {total_locations}")
        
        # Sample inventory locations from the real user request  
        inventory_locations = [
            '02-1-011B', '01-1-007B', '01-1-019A', '02-1-003B', 
            '01-1-004C', '02-1-021A', '01-1-014C', '01-1-001C',
            'RECV-01', 'RECV-02', 'STAGE-01', 'AISLE-01', 'AISLE-02'
        ]
        
        print(f"\nTesting with {len(inventory_locations)} inventory locations")
        
        # Initialize rule engine exactly like the live application does
        rule_engine = RuleEngine(db.session)
        
        # Call the warehouse detection method directly
        print("\n=== CALLING RULE ENGINE WAREHOUSE DETECTION ===")
        warehouse_context = rule_engine._detect_warehouse_context(inventory_locations)
        
        print(f"Detected warehouse: {warehouse_context['warehouse_id']}")
        print(f"Match score: {warehouse_context['match_score']:.2%}")
        print(f"Total inventory locations: {warehouse_context['total_inventory_locations']}")
        print(f"Matching locations: {warehouse_context['matching_locations']}")
        
        # Also run the direct SQL query to see what it finds
        print("\n=== DIRECT SQL QUERY RESULTS ===")
        from sqlalchemy import func, or_, case
        
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
        
        print("Direct query results:")
        for warehouse_id, total_locations, matching_locations in warehouse_matches:
            if matching_locations and matching_locations > 0:
                score = matching_locations / len(inventory_locations)
                print(f"  {warehouse_id}: {matching_locations}/{len(inventory_locations)} = {score:.2%} (total: {total_locations})")
            else:
                print(f"  {warehouse_id}: 0/{len(inventory_locations)} = 0% (total: {total_locations})")

if __name__ == '__main__':
    debug_live_warehouse_detection()