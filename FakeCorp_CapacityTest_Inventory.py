#!/usr/bin/env python3
"""
FakeCorp Distribution Center - Capacity Test Inventory
Focused test for overcapacity rule validation
"""

import pandas as pd
from datetime import datetime, timedelta

def create_capacity_test_inventory():
    """Create test inventory to validate overcapacity rule"""
    
    inventory_data = []
    
    # From debug: database locations like USER_02-01-042A, USER_03-02-012A_1, 01-01-017C
    
    # === SCENARIO 1: TRUE OVERCAPACITY (6 pallets in same location) ===
    overcapacity_location = 'USER_02-01-042A'
    
    for i in range(6):
        inventory_data.append({
            'Pallet ID': f'OVER{i:03d}',
            'Location': overcapacity_location,
            'Receipt Number': f'OVER{i}',
            'Description': 'OEM Oil Filter - ENGINE',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 30,
            'Weight': 600
        })
    
    # === SCENARIO 2: NORMAL CAPACITY (1-2 pallets per location) ===
    normal_locations = [
        'USER_03-02-012A_1',
        'USER_02-02-009C', 
        'USER_01-01-016B_2',
        '01-01-017C',
        '04-01-016D'
    ]
    
    for i, location in enumerate(normal_locations):
        # 1 pallet per location (should NOT trigger overcapacity)
        inventory_data.append({
            'Pallet ID': f'NORM{i:03d}',
            'Location': location,
            'Receipt Number': f'NORM{i}',
            'Description': 'Bosch Spark Plugs - ENGINE',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 25,
            'Weight': 500
        })
    
    # === SCENARIO 3: BORDERLINE CAPACITY (3 pallets in one location) ===
    borderline_location = 'USER_01-01-008B'
    
    for i in range(3):
        inventory_data.append({
            'Pallet ID': f'BORD{i:03d}',
            'Location': borderline_location,
            'Receipt Number': f'BORD{i}',
            'Description': 'Continental Brake Discs - BRAKE',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 35,
            'Weight': 700
        })
    
    # === SCENARIO 4: INVALID LOCATIONS (should not affect overcapacity) ===
    invalid_locations = [
        {'id': 'INV001', 'location': 'INVALID-XYZ'},
        {'id': 'INV002', 'location': ''}
    ]
    
    for error in invalid_locations:
        inventory_data.append({
            'Pallet ID': error['id'],
            'Location': error['location'],
            'Receipt Number': error['id'],
            'Description': 'Denso Alternator - ELECTRICAL',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 15,
            'Weight': 500
        })
    
    return inventory_data

def main():
    """Generate and save the capacity test inventory"""
    print("FakeCorp Distribution Center - Capacity Test Inventory")
    print("=" * 55)
    
    print("Creating focused overcapacity test...")
    inventory_data = create_capacity_test_inventory()
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Save to Excel file
    output_file = 'FakeCorp_CapacityTest_Inventory.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\nCapacity test inventory generated!")
    print(f"File: {output_file}")
    print(f"Total pallets: {len(inventory_data)}")
    
    print(f"\nTest Structure:")
    print(f"   - TRUE Overcapacity: 6 pallets at USER_02-01-042A")
    print(f"   - Normal Capacity: 1 pallet each at 5 locations")
    print(f"   - Borderline: 3 pallets at USER_01-01-008B")
    print(f"   - Invalid Locations: 2 pallets (should not trigger overcapacity)")
    
    print(f"\nExpected Results:")
    print(f"   - Overcapacity: 6 pallets (only at USER_02-01-042A)")
    print(f"   - Invalid Locations: 2 pallets")
    print(f"   - Total: 8 anomalies (massive improvement from 23!)")
    
    print(f"\nUpload {output_file} to test the overcapacity fix!")

if __name__ == "__main__":
    main()