#!/usr/bin/env python3
"""
FakeCorp Distribution Center - Fixed Test Inventory Report
Uses correct location formats that match the database
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_fixed_inventory():
    """Create test inventory using actual database location formats"""
    
    inventory_data = []
    
    # === SCENARIO 1: STAGNANT PALLETS (4 pallets in RECEIVING) ===
    for i in range(4):
        inventory_data.append({
            'Pallet ID': f'STAG{i:03d}',
            'Location': 'RECEIVING',  # Using actual database location
            'Receipt Number': f'REC{i}',
            'Description': 'Bosch Brake Pads - BRAKE',
            'Creation Date': (datetime.now() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 25,
            'Weight': 800
        })
    
    # === SCENARIO 2: OVERCAPACITY (3 pallets in same storage location) ===
    for i in range(3):
        inventory_data.append({
            'Pallet ID': f'OVER{i:03d}',
            'Location': '001A',  # Using actual database format
            'Receipt Number': f'OVER{i}',
            'Description': 'OEM Oil Filter - ENGINE',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 30,
            'Weight': 600
        })
    
    # === SCENARIO 3: LOT STRAGGLERS (6 stored + 2 in receiving) ===
    lot_id = 'LOT001'
    
    # 6 stored pallets in valid storage locations
    storage_locations = ['002A', '002B', '003A', '003B', '004A', '004B']
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
    
    # 2 stragglers in receiving
    for i in range(2):
        inventory_data.append({
            'Pallet ID': f'STR{i:03d}',
            'Location': 'RECEIVING',  # Using actual database location
            'Receipt Number': lot_id,
            'Description': 'Continental Timing Belt - ENGINE',
            'Creation Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 40,
            'Weight': 750
        })
    
    # === SCENARIO 4: TEMPERATURE VIOLATIONS (3 pallets) ===
    temp_locations = ['005A', '005B', '006A']
    for i, location in enumerate(temp_locations):
        inventory_data.append({
            'Pallet ID': f'TEMP{i:03d}',
            'Location': location,
            'Receipt Number': f'TEMP{i}',
            'Description': 'FROZEN Rubber Seals - BODY',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 20,
            'Weight': 400
        })
    
    # === SCENARIO 5: LOCATION ERRORS (3 pallets) ===
    location_errors = [
        {'id': 'MISS001', 'location': '', 'desc': 'Missing Location'},
        {'id': 'INV001', 'location': 'INVALID-XYZ', 'desc': 'Invalid Location'},
        {'id': 'INV002', 'location': '99-99-999-Z', 'desc': 'Non-existent Location'}
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
    
    # === NORMAL INVENTORY (12 pallets in valid storage locations) ===
    products = [
        'Bosch Spark Plugs - ENGINE',
        'Valeo Clutch Kit - TRANSMISSION', 
        'Continental Brake Discs - BRAKE',
        'OEM Shock Absorber - SUSPENSION',
        'Denso Battery - ELECTRICAL'
    ]
    
    # Use valid storage locations from database
    normal_locations = ['007A', '007B', '008A', '008B', '009A', '009B', 
                       '010A', '010B', '011A', '011B', '012A', '012B']
    
    for i, location in enumerate(normal_locations):
        inventory_data.append({
            'Pallet ID': f'NORM{i:03d}',
            'Location': location,
            'Receipt Number': f'NORM{i//4}',  # Group in lots of 4
            'Description': products[i % len(products)],
            'Creation Date': (datetime.now() - timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': random.randint(20, 50),
            'Weight': random.randint(500, 1000)
        })
    
    # === SPECIAL AREAS (3 pallets in valid special locations) ===
    special_pallets = [
        {'location': 'STAGING', 'desc': 'Quality Check'},
        {'location': 'DOCK01', 'desc': 'Ready to Ship'},
        {'location': 'RECEIVING', 'desc': 'Just Arrived'}  # Additional receiving pallet
    ]
    
    for i, special in enumerate(special_pallets):
        inventory_data.append({
            'Pallet ID': f'SPEC{i:03d}',
            'Location': special['location'],
            'Receipt Number': f'SPEC{i}',
            'Description': f'Bosch ECU - ELECTRICAL ({special["desc"]})',
            'Creation Date': (datetime.now() - timedelta(hours=i+1)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 25,
            'Weight': 600
        })
    
    return inventory_data

def main():
    """Generate and save the fixed inventory report"""
    print("FakeCorp Distribution Center - Fixed Test Inventory")
    print("=" * 52)
    
    print("Generating corrected test inventory...")
    inventory_data = create_fixed_inventory()
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Save to Excel file
    output_file = 'FakeCorp_Fixed_Inventory.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\nFixed inventory report generated!")
    print(f"File: {output_file}")
    print(f"Total pallets: {len(inventory_data)}")
    
    # Summary
    print(f"\nTest Scenarios (Using Valid Locations):")
    print(f"   - Stagnant Pallets: 4 (10+ hours in RECEIVING)")
    print(f"   - Overcapacity: 3 (same location 001A)")  
    print(f"   - Lot Stragglers: 2 (8 total in LOT001)")
    print(f"   - Temperature Violations: 3 (frozen in general storage)")
    print(f"   - Location Errors: 3 (missing/invalid locations)")
    print(f"   - Normal Inventory: 12 (valid storage locations)")
    print(f"   - Special Areas: 3 (STAGING, DOCK01, RECEIVING)")
    
    print(f"\nLocation Format Used:")
    print(f"   - Storage: 001A, 002B, 003A, etc.")
    print(f"   - Receiving: RECEIVING")
    print(f"   - Special: STAGING, DOCK01, DOCK02")
    
    print(f"\nExpected Anomalies:")
    print(f"   - Stagnant: ~7 (4 old + 2 stragglers + 1 spec in RECEIVING)")
    print(f"   - Overcapacity: 3 (multiple in 001A)")
    print(f"   - Invalid Locations: 3 (MISS001, INV001, INV002)")
    print(f"   - Total Expected: ~13 anomalies")
    
    print(f"\nUpload {output_file} to test with proper location matching!")

if __name__ == "__main__":
    main()