#!/usr/bin/env python3
"""
Debug warehouse scoring issue
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_warehouse_scoring():
    """Debug why warehouse scoring is not working correctly"""
    
    from app import app, db
    from rule_engine import RuleEngine
    
    with app.app_context():
        rule_engine = RuleEngine(db.session)
        
        # Test with a small subset that we know should match USER_TESTF
        test_locations = [
            "02-1-011B", "01-1-007B", "01-1-019A", "02-1-003B", "01-1-004C",
            "RECV-01", "STAGE-01", "DOCK-01", "AISLE-01", "AISLE-02"
        ]
        
        test_df = pd.DataFrame({'location': test_locations})
        
        print(f"Testing warehouse detection with {len(test_locations)} known USER_TESTF locations:")
        for loc in test_locations:
            print(f"  {loc}")
        
        print("\n=== STEP-BY-STEP DEBUGGING ===")
        
        # Step 1: Check unique locations
        unique_locations = test_df['location'].unique()
        print(f"\nStep 1: Unique locations: {len(unique_locations)}")
        
        # Step 2: Generate variants
        print(f"\nStep 2: Generating location variants...")
        all_variants = []
        for location in unique_locations:
            variants = rule_engine._normalize_position_format(location)
            all_variants.extend(variants)
            print(f"  {location} -> {len(variants)} variants: {variants}")
        
        print(f"Total variants generated: {len(all_variants)}")
        
        # Step 3: Manual warehouse scoring
        print(f"\nStep 3: Manual warehouse scoring for USER_TESTF...")
        
        from models import Location
        
        # Get all USER_TESTF locations
        user_testf_locations = db.session.query(Location.code).filter_by(warehouse_id='USER_TESTF').all()
        user_testf_codes = {loc.code for loc in user_testf_locations}
        print(f"USER_TESTF has {len(user_testf_codes)} total locations")
        
        # Check matches
        matched_variants = []
        for variant in all_variants:
            if variant in user_testf_codes:
                matched_variants.append(variant)
                print(f"  MATCH: {variant}")
        
        print(f"\nMatched variants: {len(matched_variants)} out of {len(all_variants)}")
        print(f"Match percentage: {len(matched_variants) / len(unique_locations) * 100:.1f}%")
        
        # Step 4: Check what the actual detection returns
        print(f"\nStep 4: Running actual warehouse detection...")
        detection_result = rule_engine._detect_warehouse_context(test_df)
        
        print(f"Detection result: {detection_result}")
        
        # Step 5: Debug the scoring function specifically
        print(f"\nStep 5: Debugging warehouse scoring...")
        warehouses = db.session.query(Location.warehouse_id).distinct().all()
        
        for (warehouse_id,) in warehouses:
            warehouse_locations = db.session.query(Location.code).filter_by(warehouse_id=warehouse_id).all()
            warehouse_codes = {loc.code for loc in warehouse_locations}
            
            matches = sum(1 for variant in all_variants if variant in warehouse_codes)
            coverage = matches / len(unique_locations) if unique_locations else 0
            
            print(f"  {warehouse_id}: {matches}/{len(unique_locations)} = {coverage:.1%} coverage")

if __name__ == '__main__':
    debug_warehouse_scoring()