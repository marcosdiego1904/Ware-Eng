#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend/src'))

def test_aisle_validation():
    """Test AISLE location validation logic"""
    print("=== AISLE VALIDATION DEBUG ===")
    
    # Simulate the exact logic from InvalidLocationEvaluator
    import sqlite3
    
    db_path = './backend/instance/database.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the exact query from InvalidLocationEvaluator
    cursor.execute("""
        SELECT code, warehouse_id, is_active, pattern
        FROM location 
        WHERE is_active = 1 OR is_active IS NULL
    """)
    locations = cursor.fetchall()
    
    print(f"Total locations from query: {len(locations)}")
    
    # Build the validation sets exactly like the code does
    valid_locations = set()
    valid_patterns = []
    
    for loc_row in locations:
        loc_code = loc_row[0]
        loc_pattern = loc_row[3]
        
        # Add exact database code (line 1067 in rule_engine.py)
        valid_locations.add(loc_code)
        
        if loc_pattern:
            valid_patterns.append(loc_pattern)
    
    print(f"Valid locations set size: {len(valid_locations)}")
    
    # Check if AISLE locations are in the set
    aisle_locations = ['AISLE-A', 'AISLE-B', 'AISLETEST']
    print("\nChecking AISLE locations in valid_locations set:")
    
    for aisle in aisle_locations:
        if aisle in valid_locations:
            print(f"[FOUND] {aisle} - in valid_locations")
        else:
            print(f"[NOT FOUND] {aisle} - NOT in valid_locations")
    
    # Manual verification - get AISLE locations directly from database
    cursor.execute("SELECT code FROM location WHERE code LIKE '%AISLE%'")
    db_aisle_locations = [row[0] for row in cursor.fetchall()]
    
    print(f"\nDirect database AISLE locations: {db_aisle_locations}")
    
    # Test the exact validation logic
    print("\nTesting validation logic:")
    test_locations = ['AISLE-A', 'AISLE-B', 'AISLETEST', 'BADLOC-01']
    
    for test_loc in test_locations:
        # Direct lookup (step 1 in validation)
        is_valid_direct = test_loc in valid_locations
        print(f"{test_loc}: Direct lookup = {is_valid_direct}")
    
    conn.close()

if __name__ == "__main__":
    test_aisle_validation()