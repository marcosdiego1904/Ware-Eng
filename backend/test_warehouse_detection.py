#!/usr/bin/env python3
"""
Test the fixed warehouse auto-detection algorithm
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location
from sqlalchemy import func, or_

def test_warehouse_detection():
    # Simulate the inventory locations from our test file
    inventory_locations = [
        'RECV-01', 'RECV-02', 'STAGE-01', 'DOCK-01', 'AISLE-01', 'AISLE-02',
        '01-01-001A', '01-01-002A', '01-01-003A', '02-01-001A', '02-01-002A'  # Sample storage positions
    ]

    with app.app_context():
        print('=== TESTING FIXED WAREHOUSE AUTO-DETECTION ===')
        
        # Use the FIXED query (the one we corrected in rule_engine.py)
        from sqlalchemy import case
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
        
        print(f'Testing with {len(inventory_locations)} inventory locations')
        print('Warehouse matching results:')
        best_match = None
        best_score = 0
        
        for warehouse_id, total_locations, matching_locations in warehouse_matches:
            if matching_locations and matching_locations > 0:
                score = matching_locations / len(inventory_locations)
                print(f'  {warehouse_id}: {matching_locations}/{len(inventory_locations)} locations matched = {score:.1%} (total: {total_locations})')
                if score > best_score:
                    best_score = score
                    best_match = warehouse_id
            else:
                print(f'  {warehouse_id}: 0/{len(inventory_locations)} locations matched = 0% (total: {total_locations})')
        
        print(f'\nBest match: {best_match} with {best_score:.1%} score')
        
        if best_match == 'USER_TESTF' and best_score == 1.0:
            print('✅ SUCCESS: Warehouse auto-detection working perfectly!')
            print('The rules engine will now correctly use USER_TESTF warehouse')
            return True
        else:
            print('❌ ERROR: Warehouse auto-detection still has issues')
            return False

if __name__ == '__main__':
    test_warehouse_detection()