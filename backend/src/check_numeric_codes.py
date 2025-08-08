#!/usr/bin/env python3
"""
Check for locations with numeric+letter codes like 001A
"""

import sqlite3
import re

def check_numeric_codes():
    """Check for numeric+letter location codes"""
    
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Get all location codes
    cursor.execute('SELECT code, warehouse_id, location_type FROM location')
    locations = cursor.fetchall()
    
    # Filter for codes matching pattern like 001A
    numeric_pattern = re.compile(r'^\d{3}[A-Z]$')
    numeric_codes = []
    
    for code, warehouse_id, loc_type in locations:
        if numeric_pattern.match(code):
            numeric_codes.append((code, warehouse_id, loc_type))
    
    print(f"Found {len(numeric_codes)} locations with numeric+letter codes:")
    
    if numeric_codes:
        print("Code\tWarehouse\tType")
        print("-" * 30)
        for code, warehouse_id, loc_type in numeric_codes:
            print(f"{code}\t{warehouse_id}\t{loc_type}")
    else:
        print("No locations with numeric+letter codes found")
    
    # Also check for any location that might conflict with 001A specifically
    cursor.execute('SELECT code, warehouse_id, location_type FROM location WHERE code = ?', ('001A',))
    conflict = cursor.fetchone()
    
    if conflict:
        print(f"\nDirect conflict found: {conflict}")
    else:
        print(f"\nNo direct conflict with '001A' found")
    
    conn.close()

if __name__ == "__main__":
    check_numeric_codes()