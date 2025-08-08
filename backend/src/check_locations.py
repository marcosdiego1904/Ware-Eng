#!/usr/bin/env python3
"""
Check existing location codes in database
"""

import sqlite3

def check_existing_locations():
    """Check what location codes already exist"""
    
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Get all location codes
    cursor.execute('SELECT code, warehouse_id, location_type, aisle_number, rack_number, position_number, level FROM location ORDER BY code')
    locations = cursor.fetchall()
    
    print(f"Found {len(locations)} existing locations:")
    print("Code\t\tWarehouse\tType\t\tAisle\tRack\tPos\tLevel")
    print("-" * 70)
    
    for loc in locations:
        code, warehouse_id, loc_type, aisle, rack, pos, level = loc
        print(f"{code:<10}\t{warehouse_id:<10}\t{loc_type:<10}\t{aisle or 'N/A'}\t{rack or 'N/A'}\t{pos or 'N/A'}\t{level or 'N/A'}")
    
    conn.close()

if __name__ == "__main__":
    check_existing_locations()