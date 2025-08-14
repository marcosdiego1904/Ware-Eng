#!/usr/bin/env python3
"""
FakeCorp Distribution Center - Final Test Inventory
Uses EXACT location codes from the database debug output
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_final_inventory():
    """Create test inventory using EXACT database location codes"""
    
    inventory_data = []
    
    # From debug output, we know exact locations that exist:
    # Sample locations: ['USER_01-01-001A(USER_MARCOS9)', ...]
    # The actual codes are: USER_01-01-001A, USER_01-01-001B, etc.
    
    # === SCENARIO 1: STAGNANT PALLETS (4 pallets in existing receiving) ===
    # We need to use receiving locations that actually exist in the DB
    # The debug showed warehouse IDs like: USER_MARCOS9, USER_HOLA2, USER_HOLA3, USER_TESTF
    # Let's try locations we know might exist based on the pattern
    
    existing_receiving_locations = [
        'RECEIVING',  # Simple receiving (might exist in DEFAULT warehouse)
        'USER_HOLA2_RECEIVING',  # Based on warehouse IDs from debug
        'USER_HOLA3_RECEIVING',
        'USER_MARCOS9_RECEIVING'
    ]
    
    for i, receiving_loc in enumerate(existing_receiving_locations):
        inventory_data.append({
            'Pallet ID': f'STAG{i:03d}',
            'Location': receiving_loc,
            'Receipt Number': f'REC{i}',
            'Description': 'Bosch Brake Pads - BRAKE',
            'Creation Date': (datetime.now() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 25,
            'Weight': 800
        })
    
    # === SCENARIO 2: OVERCAPACITY (3 pallets in known storage location) ===
    # From debug: USER_01-01-001A(USER_MARCOS9) -> code is USER_01-01-001A
    overcapacity_location = 'USER_01-01-001A'
    
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
    
    # === SCENARIO 3: LOT STRAGGLERS (6 stored + 2 in receiving) ===
    lot_id = 'LOT001'
    
    # 6 stored pallets in USER_MARCOS9 storage locations (based on debug pattern)
    storage_locations = [
        'USER_01-01-002A',
        'USER_01-01-002B', 
        'USER_01-01-003A',
        'USER_01-01-003B',
        'USER_01-01-004A',
        'USER_01-01-004B'
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
    
    # 2 stragglers in receiving (use simple RECEIVING that might exist)
    for i in range(2):
        inventory_data.append({
            'Pallet ID': f'STR{i:03d}',
            'Location': 'RECEIVING',  # Try simple receiving location
            'Receipt Number': lot_id,
            'Description': 'Continental Timing Belt - ENGINE',
            'Creation Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 40,
            'Weight': 750
        })
    
    # === SCENARIO 4: TEMPERATURE VIOLATIONS (3 pallets) ===
    temp_locations = [
        'USER_01-01-005A',
        'USER_01-01-005B', 
        'USER_01-01-006A'
    ]
    
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
    
    # === SCENARIO 5: LOCATION ERRORS (3 pallets - intentionally invalid) ===
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
    
    # === NORMAL INVENTORY (12 pallets in existing storage) ===
    products = [
        'Bosch Spark Plugs - ENGINE',
        'Valeo Clutch Kit - TRANSMISSION', 
        'Continental Brake Discs - BRAKE',
        'OEM Shock Absorber - SUSPENSION',
        'Denso Battery - ELECTRICAL'
    ]
    
    # Use storage locations that likely exist based on debug pattern
    normal_locations = [
        'USER_01-01-007A', 'USER_01-01-007B', 'USER_01-01-008A', 'USER_01-01-008B',
        'USER_01-01-009A', 'USER_01-01-009B', 'USER_01-01-010A', 'USER_01-01-010B',
        'USER_01-01-011A', 'USER_01-01-011B', 'USER_01-01-012A', 'USER_01-01-012B'
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
    
    # === SPECIAL AREAS (3 pallets in basic locations) ===
    # Use simple location names that are more likely to exist
    special_pallets = [
        {'location': 'STAGING', 'desc': 'Quality Check'},
        {'location': 'DOCK01', 'desc': 'Ready to Ship'},
        {'location': 'RECEIVING', 'desc': 'Just Arrived'}
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
    """Generate and save the final inventory report"""
    print("FakeCorp Distribution Center - Final Test Inventory")
    print("=" * 54)
    
    print("Creating inventory with exact database location codes...")
    inventory_data = create_final_inventory()
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Save to Excel file
    output_file = 'FakeCorp_Final_Inventory.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\nFinal inventory report generated!")
    print(f"File: {output_file}")
    print(f"Total pallets: {len(inventory_data)}")
    
    print(f"\nUsing Mixed Location Approaches:")
    print(f"   - USER_ prefixed: USER_01-01-001A, USER_HOLA2_RECEIVING")
    print(f"   - Simple names: RECEIVING, STAGING, DOCK01")
    print(f"   - Intentional invalids: INVALID-XYZ, 99-99-999-Z, (empty)")
    
    print(f"\nThis test will reveal:")
    print(f"   - Which location format your DB actually uses")
    print(f"   - How many false positives remain")
    print(f"   - Whether location-type mapping works for stagnant pallets")
    
    print(f"\nUpload {output_file} and check the debug output!")

if __name__ == "__main__":
    main()