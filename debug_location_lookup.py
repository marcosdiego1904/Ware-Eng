#!/usr/bin/env python3
"""
Debug location lookup mechanism
"""
import sys
import os
sys.path.append('backend/src')

from models import db, Location
from app import app
import pandas as pd

def debug_location_lookup():
    """Debug how the Invalid Locations rule looks up locations"""
    
    with app.app_context():
        # Check what's actually in the database
        total_locations = Location.query.count()
        print(f"Total locations in database: {total_locations}")
        
        # Sample of database locations
        sample_locs = Location.query.limit(10).all()
        print("\n=== DATABASE SAMPLE ===")
        for loc in sample_locs:
            print(f"ID: {loc.id}, Code: '{loc.code}', Type: {loc.location_type}")
            
        # Check specific test locations
        test_locations = ['02-06-03A', '04-04-06B', 'RCV-001', 'FINAL-006', 'INVALID-LOC']
        print("\n=== TEST LOCATION LOOKUP ===")
        for test_loc in test_locations:
            found = Location.query.filter_by(code=test_loc).first()
            if found:
                print(f"✓ {test_loc} -> Found: ID={found.id}, Type={found.location_type}")
            else:
                print(f"✗ {test_loc} -> NOT FOUND")
                
        # Check what the rule engine is actually doing
        # Let's simulate the location validation logic
        print("\n=== SIMULATING RULE LOGIC ===")
        
        # Get all valid location codes like the rule does
        all_valid_locations = set()
        for location in Location.query.all():
            all_valid_locations.add(location.code)
            
        print(f"Valid location codes in set: {len(all_valid_locations)}")
        
        # Test our locations against this set
        for test_loc in test_locations:
            is_valid = test_loc in all_valid_locations
            print(f"{test_loc}: {'VALID' if is_valid else 'INVALID'}")
            
        # Check if there are any whitespace or encoding issues
        print("\n=== ENCODING CHECK ===")
        for test_loc in test_locations[:3]:
            found = Location.query.filter_by(code=test_loc).first()
            if found:
                print(f"'{test_loc}' -> DB code: '{found.code}' (len={len(found.code)})")
                print(f"Codes equal: {test_loc == found.code}")
                print(f"Codes repr: {repr(test_loc)} vs {repr(found.code)}")

if __name__ == "__main__":
    debug_location_lookup()