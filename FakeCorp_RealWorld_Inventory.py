#!/usr/bin/env python3
"""
FakeCorp Distribution Center - Real World Test Inventory
Uses actual location formats from the database
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_realworld_inventory():
    """Create test inventory using actual database location formats"""
    
    inventory_data = []
    
    # Based on debug output, the database has locations like:
    # USER_01-01-001A(USER_MARCOS9), USER_HOLA3_RECEIVING, etc.
    # Let's use existing warehouse contexts and location patterns
    
    # === SCENARIO 1: STAGNANT PALLETS (4 pallets in USER receiving areas) ===
    user_receiving_locations = [
        'USER_HOLA2_RECEIVING',
        'USER_HOLA3_RECEIVING', 
        'USER_MARCOS9_RECEIVING',
        'USER_TESTF_RECEIVING'
    ]
    
    for i, receiving_loc in enumerate(user_receiving_locations):
        inventory_data.append({
            'Pallet ID': f'STAG{i:03d}',
            'Location': receiving_loc,
            'Receipt Number': f'REC{i}',
            'Description': 'Bosch Brake Pads - BRAKE',
            'Creation Date': (datetime.now() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 25,
            'Weight': 800
        })
    
    # === SCENARIO 2: OVERCAPACITY (3 pallets in same USER storage location) ===
    # Use existing USER_MARCOS9 storage locations
    overcapacity_location = 'USER_01-01-001A'  # Should match USER_01-01-001A(USER_MARCOS9)
    
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
    
    # 6 stored pallets in USER_MARCOS9 storage locations
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
    
    # 2 stragglers in receiving
    for i in range(2):
        inventory_data.append({
            'Pallet ID': f'STR{i:03d}',
            'Location': 'USER_HOLA2_RECEIVING',  # Use existing receiving location
            'Receipt Number': lot_id,
            'Description': 'Continental Timing Belt - ENGINE',
            'Creation Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 40,
            'Weight': 750
        })
    
    # === SCENARIO 4: TEMPERATURE VIOLATIONS (3 pallets in general storage) ===
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
    
    # === NORMAL INVENTORY (12 pallets in valid USER storage locations) ===
    products = [
        'Bosch Spark Plugs - ENGINE',
        'Valeo Clutch Kit - TRANSMISSION', 
        'Continental Brake Discs - BRAKE',
        'OEM Shock Absorber - SUSPENSION',
        'Denso Battery - ELECTRICAL'
    ]
    
    # Use various USER storage locations
    normal_locations = [
        'USER_01-01-007A', 'USER_01-01-007B', 'USER_01-01-008A', 'USER_01-01-008B',
        'USER_01-01-009A', 'USER_01-01-009B', 'USER_01-01-010A', 'USER_01-01-010B',
        'USER_01-01-011A', 'USER_01-01-011B', 'USER_01-01-012A', 'USER_01-01-012B'
    ]
    
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
    
    # === SPECIAL AREAS (3 pallets in valid USER special locations) ===
    # Based on debug output, special areas might be like USER_HOLA2_STAGING, etc.
    special_pallets = [
        {'location': 'USER_HOLA3_STAGING', 'desc': 'Quality Check'},
        {'location': 'USER_MARCOS9_DOCK', 'desc': 'Ready to Ship'},
        {'location': 'USER_TESTF_RECEIVING', 'desc': 'Just Arrived'}
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
    """Generate and save the real-world inventory report"""
    print("FakeCorp Distribution Center - Real World Test Inventory")
    print("=" * 58)
    
    print("Generating inventory with actual database location formats...")
    inventory_data = create_realworld_inventory()
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Save to Excel file
    output_file = 'FakeCorp_RealWorld_Inventory.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\nReal-world inventory report generated!")
    print(f"File: {output_file}")
    print(f"Total pallets: {len(inventory_data)}")
    
    # Summary
    print(f"\nTest Scenarios (Using Real Database Locations):")
    print(f"   - Stagnant Pallets: 4 (10+ hours in USER_*_RECEIVING)")
    print(f"   - Overcapacity: 3 (same location USER_01-01-001A)")  
    print(f"   - Lot Stragglers: 2 (8 total in LOT001)")
    print(f"   - Temperature Violations: 3 (frozen in general storage)")
    print(f"   - Location Errors: 3 (missing/invalid locations)")
    print(f"   - Normal Inventory: 12 (valid USER storage locations)")
    print(f"   - Special Areas: 3 (USER staging/dock areas)")
    
    print(f"\nLocation Format Used:")
    print(f"   - Storage: USER_01-01-001A, USER_01-01-002B, etc.")
    print(f"   - Receiving: USER_HOLA2_RECEIVING, USER_MARCOS9_RECEIVING")
    print(f"   - Special: USER_HOLA3_STAGING, USER_MARCOS9_DOCK")
    
    print(f"\nExpected Anomalies:")
    print(f"   - Stagnant: ~6 (4 old + 2 stragglers in receiving)")
    print(f"   - Overcapacity: 3 (multiple in USER_01-01-001A)")
    print(f"   - Invalid Locations: 3 (MISS001, INV001, INV002)")
    print(f"   - Total Expected: ~12 anomalies (instead of 45!)")
    
    print(f"\nUpload {output_file} - should now properly validate locations!")

if __name__ == "__main__":
    main()