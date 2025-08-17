#!/usr/bin/env python3
"""
Debug USER_TESTF warehouse locations
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_user_testf_locations():
    """Debug what locations exist in USER_TESTF warehouse"""
    
    from app import app, db
    from models import Location
    
    with app.app_context():
        # Get all USER_TESTF locations
        user_testf_locations = db.session.query(Location).filter_by(warehouse_id='USER_TESTF').all()
        
        print(f"USER_TESTF warehouse has {len(user_testf_locations)} locations:")
        
        # Group by type
        by_type = {}
        for location in user_testf_locations:
            location_type = location.location_type or 'UNKNOWN'
            if location_type not in by_type:
                by_type[location_type] = []
            by_type[location_type].append(location.code)
        
        for location_type, codes in by_type.items():
            print(f"\n{location_type} ({len(codes)} locations):")
            for code in sorted(codes)[:10]:  # Show first 10
                print(f"  {code}")
            if len(codes) > 10:
                print(f"  ... and {len(codes) - 10} more")
        
        # Sample inventory locations from test file
        test_inventory_locations = [
            "02-1-011B", "01-1-007B", "01-1-019A", "02-1-003B", "01-1-004C",
            "02-1-021A", "01-1-014C", "01-1-001C", "RECV-01", "STAGE-01"
        ]
        
        print(f"\nChecking sample inventory locations against USER_TESTF:")
        for inv_loc in test_inventory_locations:
            # Check exact match
            exact_match = db.session.query(Location).filter_by(
                warehouse_id='USER_TESTF', 
                code=inv_loc
            ).first()
            
            if exact_match:
                print(f"  {inv_loc}: EXACT MATCH")
            else:
                # Check for similar locations (with normalization)
                from rule_engine import RuleEngine
                rule_engine = RuleEngine(db.session)
                variants = rule_engine._normalize_position_format(inv_loc)
                
                found_variants = []
                for variant in variants:
                    variant_match = db.session.query(Location).filter_by(
                        warehouse_id='USER_TESTF',
                        code=variant
                    ).first()
                    if variant_match:
                        found_variants.append(variant)
                
                if found_variants:
                    print(f"  {inv_loc}: VARIANT MATCHES -> {found_variants}")
                else:
                    print(f"  {inv_loc}: NO MATCH")

if __name__ == '__main__':
    debug_user_testf_locations()