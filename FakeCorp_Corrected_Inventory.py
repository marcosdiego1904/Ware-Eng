#!/usr/bin/env python3
"""
FakeCorp Distribution Center - Corrected Test Inventory
Uses EXACT location formats from database debug output
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_corrected_inventory():
    """Create test inventory using exact database location patterns"""
    
    inventory_data = []
    
    # From debug output: ['USER_02-01-042A', 'USER_03-02-012A_1', '01-01-017C', etc.]
    # Database has USER_ prefixed locations and non-prefixed locations
    # NO RECEIVING locations exist in database!
    
    # === SCENARIO 1: STAGNANT PALLETS (4 pallets in valid storage) ===
    # Since RECEIVING locations don't exist, use regular storage locations
    # but make them old to trigger stagnant rules
    stagnant_locations = [
        'USER_02-01-042A',
        'USER_03-02-012A', 
        '01-01-017C',
        'USER_01-01-008B'
    ]
    
    for i, location in enumerate(stagnant_locations):
        inventory_data.append({
            'Pallet ID': f'STAG{i:03d}',
            'Location': location,
            'Receipt Number': f'REC{i}',
            'Description': 'Bosch Brake Pads - BRAKE',
            'Creation Date': (datetime.now() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 25,
            'Weight': 800
        })
    
    # === SCENARIO 2: OVERCAPACITY (3 pallets in same location) ===
    overcapacity_location = 'USER_02-01-042A'  # Use existing location from debug
    
    for i in range(3):
        inventory_data.append({
            'Pallet ID': f'OVER{i:03d}',
            'Location': overcapacity_location,
            'Receipt Number': f'OVER{i}',
            'Description': 'OEM Oil Filter - ENGINE',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 30,
            'Weight': 600
        })
    
    # === SCENARIO 3: LOT STRAGGLERS (6 stored + 2 in different locations) ===
    lot_id = 'LOT001'
    
    # 6 stored pallets in various USER locations
    storage_locations = [
        'USER_02-02-009C',
        'USER_01-01-016B', 
        'USER_02-02-023C',
        'USER_01-02-015A',
        'USER_03-02-012A_1',
        'USER_01-01-008B'
    ]
    
    for i, location in enumerate(storage_locations):
        inventory_data.append({
            'Pallet ID': f'LOT{i:03d}',
            'Location': location,
            'Receipt Number': lot_id,
            'Description': 'Continental Timing Belt - ENGINE',
            'Creation Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 40,
            'Weight': 750
        })
    
    # 2 stragglers in different locations
    for i in range(2):
        inventory_data.append({
            'Pallet ID': f'STR{i:03d}',
            'Location': 'USER_02-02-007C',  # Use existing location
            'Receipt Number': lot_id,
            'Description': 'Continental Timing Belt - ENGINE',
            'Creation Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 40,
            'Weight': 750
        })
    
    # === SCENARIO 4: LOCATION ERRORS (3 pallets - intentionally invalid) ===
    location_errors = [
        {'id': 'MISS001', 'location': '', 'desc': 'Missing Location'},
        {'id': 'INV001', 'location': 'INVALID-XYZ', 'desc': 'Invalid Location'},
        {'id': 'INV002', 'location': 'RECEIVING', 'desc': 'Non-existent RECEIVING'}
    ]
    
    for error in location_errors:
        inventory_data.append({
            'Pallet ID': error['id'],
            'Location': error['location'],
            'Receipt Number': error['id'],
            'Description': f'Denso Alternator - ELECTRICAL ({error["desc"]})',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 15,
            'Weight': 500
        })
    
    # === NORMAL INVENTORY (12 pallets in existing database locations) ===
    products = [
        'Bosch Spark Plugs - ENGINE',
        'Valeo Clutch Kit - TRANSMISSION', 
        'Continental Brake Discs - BRAKE',
        'OEM Shock Absorber - SUSPENSION',
        'Denso Battery - ELECTRICAL'
    ]
    
    # Use locations that exist in database (from debug sample)
    normal_locations = [
        'USER_02-01-042A', 'USER_03-02-012A_1', 'USER_02-02-009C', 'USER_02-02-007C_2',
        'USER_01-01-016B_2', 'USER_01-01-008B', '04-01-016D', '01-01-017C',
        'USER_02-02-023C_2', 'USER_01-02-015A', 'USER_02-01-042A', 'USER_03-02-012A'
    ]
    
    for i, location in enumerate(normal_locations):
        inventory_data.append({
            'Pallet ID': f'NORM{i:03d}',
            'Location': location,
            'Receipt Number': f'NORM{i//4}',
            'Description': products[i % len(products)],
            'Creation Date': (datetime.now() - timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': random.randint(20, 50),
            'Weight': random.randint(500, 1000)
        })
    
    return inventory_data

def main():
    """Generate and save the corrected inventory report"""
    print("FakeCorp Distribution Center - Corrected Test Inventory")
    print("=" * 58)
    
    print("Creating inventory using EXACT database location formats...")
    inventory_data = create_corrected_inventory()
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Save to Excel file
    output_file = 'FakeCorp_Corrected_Inventory.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\nCorrected inventory report generated!")
    print(f"File: {output_file}")
    print(f"Total pallets: {len(inventory_data)}")
    
    print(f"\nUsing ONLY Database Locations:")
    print(f"   - USER_ prefixed: USER_02-01-042A, USER_03-02-012A_1")
    print(f"   - Non-prefixed: 01-01-017C, 04-01-016D")
    print(f"   - NO RECEIVING locations (they don't exist in DB)")
    
    print(f"\nExpected Results:")
    print(f"   - Invalid Locations: 3 (empty, INVALID-XYZ, RECEIVING)")
    print(f"   - Overcapacity: 6 (3 at USER_02-01-042A + overlap)")
    print(f"   - All other locations should be VALID")
    print(f"   - Target: ~9 total anomalies")
    
    print(f"\nUpload {output_file} to test the corrected normalization!")

if __name__ == "__main__":
    main()