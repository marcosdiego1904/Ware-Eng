#!/usr/bin/env python3
"""
Debug all warehouses in database
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_all_warehouses():
    """Debug all warehouses and their locations"""
    
    from app import app, db
    from models import Location
    
    with app.app_context():
        # Get all warehouses
        warehouses = db.session.query(Location.warehouse_id).distinct().all()
        
        print(f"Found {len(warehouses)} warehouses in database:")
        
        for (warehouse_id,) in warehouses:
            locations = db.session.query(Location).filter_by(warehouse_id=warehouse_id).all()
            
            by_type = {}
            for location in locations:
                location_type = location.location_type or 'UNKNOWN'
                by_type[location_type] = by_type.get(location_type, 0) + 1
            
            print(f"\n{warehouse_id}: {len(locations)} total locations")
            for location_type, count in by_type.items():
                print(f"  {location_type}: {count}")
            
            # Show first few location codes
            sample_codes = [loc.code for loc in locations[:5]]
            print(f"  Sample codes: {sample_codes}")
        
        # Now let's manually trace what happens in warehouse detection
        print(f"\n=== TRACING WAREHOUSE DETECTION BUG ===")
        
        # Create a small test that should definitely match USER_TESTF
        test_locations = ["RECV-01", "STAGE-01", "DOCK-01"]
        
        from rule_engine import RuleEngine
        import pandas as pd
        
        rule_engine = RuleEngine(db.session)
        test_df = pd.DataFrame({'location': test_locations})
        
        print(f"Testing with obvious USER_TESTF locations: {test_locations}")
        
        # Enable verbose debugging
        result = rule_engine._detect_warehouse_context(test_df)
        
        print(f"Result: {result}")

if __name__ == '__main__':
    debug_all_warehouses()