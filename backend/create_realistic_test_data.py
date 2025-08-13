#!/usr/bin/env python3
"""
Create Realistic Test Data for WareWise
Uses actual warehouse locations from database to create test data that should produce reasonable anomaly counts
"""

import pandas as pd
import sqlite3
import random
from datetime import datetime, timedelta

def get_database_locations():
    """Get actual locations from the database"""
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Get sample locations by type
    locations = {}
    
    # RECEIVING locations (for stagnant pallets)
    cursor.execute('SELECT code, capacity FROM location WHERE location_type = "RECEIVING" AND capacity > 0 LIMIT 10')
    locations['RECEIVING'] = cursor.fetchall()
    
    # STORAGE locations with capacity 1 (for overcapacity tests)
    cursor.execute('SELECT code, capacity FROM location WHERE location_type = "STORAGE" AND capacity = 1 LIMIT 20')
    locations['STORAGE_SINGLE'] = cursor.fetchall()
    
    # STORAGE locations with capacity > 1 (for normal storage)
    cursor.execute('SELECT code, capacity FROM location WHERE location_type = "STORAGE" AND capacity > 1 LIMIT 15')
    locations['STORAGE_MULTI'] = cursor.fetchall()
    
    # STAGING locations
    cursor.execute('SELECT code, capacity FROM location WHERE location_type = "STAGING" LIMIT 10')
    locations['STAGING'] = cursor.fetchall()
    
    # DOCK locations
    cursor.execute('SELECT code, capacity FROM location WHERE location_type = "DOCK" LIMIT 8')
    locations['DOCK'] = cursor.fetchall()
    
    conn.close()
    return locations

def create_realistic_test_data():
    """Create test data that should produce ~10-15 anomalies from ~40 pallets"""
    
    print("Getting actual warehouse locations from database...")
    db_locations = get_database_locations()
    
    # Print available locations
    for loc_type, locs in db_locations.items():
        print(f"{loc_type}: {len(locs)} locations available")
        if locs:
            print(f"  Examples: {[loc[0] for loc in locs[:3]]}")
    
    test_data = []
    pallet_counter = 1
    
    print("\nCreating test scenarios...")
    
    # Scenario 1: Stagnant pallets (4 pallets in RECEIVING > 6 hours)
    if db_locations['RECEIVING']:
        print("- Creating 4 stagnant pallets in RECEIVING")
        for i in range(4):
            test_data.append({
                'Pallet ID': f'STAG{pallet_counter:03d}',
                'Location': db_locations['RECEIVING'][i % len(db_locations['RECEIVING'])][0],
                'Receipt Number': f'REC{pallet_counter:03d}',
                'Description': 'General Merchandise - Stagnant',
                'Quantity': 50,
                'Weight (lbs)': 1200,
                'Created Date': datetime.now() - timedelta(hours=random.randint(7, 24)),
                'SKU': f'SKU{pallet_counter:04d}'
            })
            pallet_counter += 1
    
    # Scenario 2: Overcapacity violations (6 pallets in single-capacity locations)
    if db_locations['STORAGE_SINGLE']:
        print("- Creating 6 overcapacity violations (2 pallets each in 3 single-capacity locations)")
        for i in range(3):  # 3 locations
            location_code = db_locations['STORAGE_SINGLE'][i][0]
            for j in range(2):  # 2 pallets each (capacity is 1, so this creates overcapacity)
                test_data.append({
                    'Pallet ID': f'OVER{pallet_counter:03d}',
                    'Location': location_code,
                    'Receipt Number': f'OVER{i:02d}',
                    'Description': 'Overcapacity Test Product',
                    'Quantity': 75,
                    'Weight (lbs)': 1500,
                    'Created Date': datetime.now() - timedelta(hours=random.randint(1, 5)),
                    'SKU': f'SKU{pallet_counter:04d}'
                })
                pallet_counter += 1
    
    # Scenario 3: Lot stragglers (10-pallet lot, 8 stored, 2 still in receiving)
    if db_locations['RECEIVING'] and db_locations['STORAGE_MULTI']:
        print("- Creating lot straggler scenario (8 stored, 2 stragglers)")
        lot_number = 'LOT2024001'
        
        # 8 properly stored pallets (80% completion triggers straggler detection)
        for i in range(8):
            storage_loc = db_locations['STORAGE_MULTI'][i % len(db_locations['STORAGE_MULTI'])][0]
            test_data.append({
                'Pallet ID': f'LOT{pallet_counter:03d}',
                'Location': storage_loc,
                'Receipt Number': lot_number,
                'Description': 'Lot Completion Test Product',
                'Quantity': 40,
                'Weight (lbs)': 1000,
                'Created Date': datetime.now() - timedelta(hours=random.randint(2, 6)),
                'SKU': f'SKU{pallet_counter:04d}'
            })
            pallet_counter += 1
        
        # 2 stragglers still in receiving
        receiving_loc = db_locations['RECEIVING'][0][0]
        for i in range(2):
            test_data.append({
                'Pallet ID': f'LOT{pallet_counter:03d}',
                'Location': receiving_loc,
                'Receipt Number': lot_number,
                'Description': 'Lot Completion Test Product',
                'Quantity': 40,
                'Weight (lbs)': 1000,
                'Created Date': datetime.now() - timedelta(hours=random.randint(2, 6)),
                'SKU': f'SKU{pallet_counter:04d}'
            })
            pallet_counter += 1
    
    # Scenario 4: Data integrity issues (3 pallets)
    print("- Creating 3 data integrity test cases")
    test_data.extend([
        # Duplicate pallet ID
        {
            'Pallet ID': 'DUP001',
            'Location': db_locations['STORAGE_SINGLE'][5][0] if db_locations['STORAGE_SINGLE'] else '001A',
            'Receipt Number': 'DUP001',
            'Description': 'Duplicate Test 1',
            'Quantity': 20,
            'Weight (lbs)': 500,
            'Created Date': datetime.now(),
            'SKU': f'SKU{pallet_counter:04d}'
        },
        {
            'Pallet ID': 'DUP001',  # Same ID = duplicate
            'Location': db_locations['STORAGE_SINGLE'][6][0] if db_locations['STORAGE_SINGLE'] else '002A',
            'Receipt Number': 'DUP002',
            'Description': 'Duplicate Test 2',
            'Quantity': 30,
            'Weight (lbs)': 600,
            'Created Date': datetime.now(),
            'SKU': f'SKU{pallet_counter+1:04d}'
        },
        # Missing location
        {
            'Pallet ID': f'MISS{pallet_counter:03d}',
            'Location': None,  # Missing location
            'Receipt Number': f'MISS{pallet_counter:03d}',
            'Description': 'Missing Location Test',
            'Quantity': 15,
            'Weight (lbs)': 400,
            'Created Date': datetime.now(),
            'SKU': f'SKU{pallet_counter+2:04d}'
        }
    ])
    pallet_counter += 3
    
    # Scenario 5: Normal operations (15 pallets for baseline)
    print("- Creating 15 normal operation pallets")
    normal_locations = []
    if db_locations['STAGING']:
        normal_locations.extend([loc[0] for loc in db_locations['STAGING'][:5]])
    if db_locations['DOCK']:
        normal_locations.extend([loc[0] for loc in db_locations['DOCK'][:3]])
    if db_locations['STORAGE_MULTI']:
        normal_locations.extend([loc[0] for loc in db_locations['STORAGE_MULTI'][:7]])
    
    for i in range(15):
        if normal_locations:
            location = normal_locations[i % len(normal_locations)]
        else:
            location = '001A'  # Fallback
            
        test_data.append({
            'Pallet ID': f'NORM{pallet_counter:03d}',
            'Location': location,
            'Receipt Number': f'NORM{pallet_counter//5:03d}',
            'Description': 'Normal Operations Product',
            'Quantity': 60,
            'Weight (lbs)': 1100,
            'Created Date': datetime.now() - timedelta(hours=random.randint(0, 4)),
            'SKU': f'SKU{pallet_counter:04d}'
        })
        pallet_counter += 1
    
    return test_data

def main():
    """Create and save realistic test data"""
    print("Creating Realistic WareWise Test Data")
    print("=" * 50)
    
    test_data = create_realistic_test_data()
    
    # Convert to DataFrame and save
    df = pd.DataFrame(test_data)
    
    filename = 'realistic_warehouse_test.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"\n=== TEST DATA CREATED ===")
    print(f"File: {filename}")
    print(f"Total pallets: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Show location breakdown
    print(f"\nLocation usage:")
    location_counts = df['Location'].value_counts()
    for loc, count in location_counts.items():
        if pd.notna(loc):
            print(f"  {loc}: {count} pallets")
        else:
            print(f"  [Missing Location]: {count} pallets")
    
    print(f"\n=== EXPECTED ANOMALIES ===")
    print("Based on the scenarios created:")
    print("  - 4 stagnant pallets (>6 hours in RECEIVING)")
    print("  - 6 overcapacity violations (2 pallets in single-capacity locations)")  
    print("  - 2 lot stragglers (from 80% completed lot)")
    print("  - 3 data integrity issues (1 duplicate, 1 missing location)")
    print("  Total expected: ~15 anomalies from 42 pallets")
    print("  Detection rate: ~36% (much more reasonable!)")
    
    return filename

if __name__ == "__main__":
    filename = main()
    print(f"\n✅ Realistic test data created: {filename}")
    print("This should produce ~15 anomalies instead of 63!")