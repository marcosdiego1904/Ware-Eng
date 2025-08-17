#!/usr/bin/env python3
"""
Debug the exact production scenario
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_production_scenario():
    """Recreate the exact production scenario and trace the issue"""
    
    from app import app, db
    from rule_engine import RuleEngine
    from models import Location
    
    with app.app_context():
        # First check what warehouses exist BEFORE we start
        print("=== BEFORE TEST ===")
        warehouses_before = db.session.query(Location.warehouse_id).distinct().all()
        print(f"Warehouses before test: {[w[0] for w in warehouses_before]}")
        
        # Count locations per warehouse before
        for (warehouse_id,) in warehouses_before:
            count = db.session.query(Location).filter_by(warehouse_id=warehouse_id).count()
            print(f"  {warehouse_id}: {count} locations")
        
        # Create a realistic inventory scenario (similar to production)
        # Mix of USER_TESTF locations and some that don't exist
        inventory_data = [
            # USER_TESTF locations that should match
            "02-1-011B", "01-1-007B", "01-1-019A", "02-1-003B", "01-1-004C",
            "RECV-01", "STAGE-01", "DOCK-01", "AISLE-01", "AISLE-02",
            
            # More USER_TESTF locations
            "02-1-016B", "01-1-011A", "01-1-008B", "02-1-017C", "01-1-022C",
            "02-01-023A", "01-01-024B", "02-01-024A",
            
            # Non-existent locations (like in production test)
            "FAKE-AREA", "UNKNOWN-99", "BADLOC-01", "INVALID-LOC-01",
            "TEST-ERROR", "MISSING-LOC"
        ]
        
        # Add many more realistic locations to get closer to the 156 from production
        for i in range(1, 26):  # Add 25 more positions per aisle
            for level in ['A', 'B', 'C']:
                inventory_data.extend([
                    f"01-1-{i:03d}{level}",
                    f"02-1-{i:03d}{level}"
                ])
        
        # Add some receiving/staging that should also match
        for i in range(1, 20):
            inventory_data.extend([
                f"RECV-{i:02d}",
                f"STAGE-{i:02d}"
            ])
        
        print(f"\nCreated test inventory with {len(inventory_data)} locations")
        print(f"Sample locations: {inventory_data[:10]}")
        
        # Create DataFrame like in production
        test_df = pd.DataFrame({'location': inventory_data})
        
        print(f"\n=== RUNNING WAREHOUSE DETECTION ===")
        
        # Run the detection
        rule_engine = RuleEngine(db.session)
        detection_result = rule_engine._detect_warehouse_context(test_df)
        
        print(f"Detection result: {detection_result}")
        
        # Check what warehouses exist AFTER the test
        print(f"\n=== AFTER TEST ===")
        warehouses_after = db.session.query(Location.warehouse_id).distinct().all()
        print(f"Warehouses after test: {[w[0] for w in warehouses_after]}")
        
        # Count locations per warehouse after
        for (warehouse_id,) in warehouses_after:
            count = db.session.query(Location).filter_by(warehouse_id=warehouse_id).count()
            print(f"  {warehouse_id}: {count} locations")
        
        # Check if any new warehouses were created
        warehouses_before_set = {w[0] for w in warehouses_before}
        warehouses_after_set = {w[0] for w in warehouses_after}
        
        new_warehouses = warehouses_after_set - warehouses_before_set
        if new_warehouses:
            print(f"\nNEW WAREHOUSES CREATED: {new_warehouses}")
            
            # Show what locations were added to new warehouses
            for warehouse_id in new_warehouses:
                new_locations = db.session.query(Location.code).filter_by(warehouse_id=warehouse_id).all()
                location_codes = [loc.code for loc in new_locations]
                print(f"  {warehouse_id} new locations: {location_codes[:10]}")
        else:
            print(f"\nNo new warehouses were created")
        
        # Manual verification: check specific locations that caused the issue
        print(f"\n=== MANUAL VERIFICATION ===")
        problem_locations = ["FAKE-AREA", "UNKNOWN-99", "BADLOC-01"]
        
        for loc in problem_locations:
            matches = db.session.query(Location.warehouse_id, Location.code).filter_by(code=loc).all()
            if matches:
                print(f"  {loc} found in: {[m.warehouse_id for m in matches]}")
            else:
                print(f"  {loc}: still not found")

if __name__ == '__main__':
    debug_production_scenario()