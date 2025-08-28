#!/usr/bin/env python3
"""
Generate test inventory Excel file for overcapacity rule testing
Warehouse: test123 (USER_MARCOS9)
Structure: 2 aisles × 2 racks × 25 positions × 3 levels = 300 locations
Each location capacity = 1 pallet
"""

import pandas as pd
import random
from datetime import datetime, timedelta

def generate_test_inventory():
    """Generate test inventory with clear overcapacity violations"""
    
    inventory_data = []
    pallet_counter = 1
    
    # Define warehouse structure
    aisles = [1, 2]
    racks = [1, 2] 
    positions = list(range(1, 26))  # 1-25
    levels = ['A', 'B', 'C']
    
    print("Generating overcapacity test inventory...")
    print("Warehouse: test123 (USER_MARCOS9)")
    print("Structure: 2 aisles × 2 racks × 25 positions × 3 levels")
    print("Default capacity: 1 pallet per location")
    
    # Scenario 1: Clear violations - Multiple pallets in same locations
    violation_scenarios = [
        # Major violations (easy to spot)
        ('01-01-001A', 8),  # 8 pallets in 1 location = 8 violations
        ('01-01-002B', 6),  # 6 pallets in 1 location = 6 violations  
        ('01-02-003C', 5),  # 5 pallets in 1 location = 5 violations
        ('02-01-004A', 4),  # 4 pallets in 1 location = 4 violations
        ('02-02-005B', 3),  # 3 pallets in 1 location = 3 violations
        ('01-01-006C', 3),  # 3 pallets in 1 location = 3 violations
        
        # Minor violations (2 pallets each)
        ('01-02-007A', 2),  # 2 pallets = 2 violations
        ('02-01-008B', 2),  # 2 pallets = 2 violations  
        ('02-02-009C', 2),  # 2 pallets = 2 violations
        ('01-01-010A', 2),  # 2 pallets = 2 violations
        ('01-02-011B', 2),  # 2 pallets = 2 violations
    ]
    
    total_expected_violations = sum(count for _, count in violation_scenarios)
    print(f"Expected violations: {total_expected_violations}")
    
    # Create violation pallets
    for location, pallet_count in violation_scenarios:
        for i in range(pallet_count):
            inventory_data.append({
                'pallet_id': f'VIO{pallet_counter:03d}',
                'location': location,
                'description': f'Test Product {pallet_counter}',
                'Quantity': random.randint(10, 50),
                'Weight_KG': random.randint(100, 500),
                'creation_date': datetime.now() - timedelta(hours=random.randint(1, 24)),
                'Status': 'ACTIVE',
                'receipt_number': f'REC{random.randint(1000, 9999)}',
                'Supplier': f'Supplier{random.randint(1, 10)}',
                'Zone': 'STORAGE'
            })
            pallet_counter += 1
    
    # Scenario 2: Normal locations (1 pallet each - no violations)
    normal_locations = [
        '01-01-012C', '01-02-013A', '02-01-014B', '02-02-015C',
        '01-01-016A', '01-02-017B', '02-01-018C', '02-02-019A',
        '01-01-020B', '01-02-021C', '02-01-022A', '02-02-023B',
        '01-01-024C', '01-02-025A', '02-01-001B', '02-02-002C',
        '01-01-003B', '01-02-004C', '02-01-005A', '02-02-006C'
    ]
    
    for location in normal_locations:
        inventory_data.append({
            'pallet_id': f'NOR{pallet_counter:03d}',
            'location': location,
            'description': f'Normal Product {pallet_counter}',
            'Quantity': random.randint(10, 50),
            'Weight_KG': random.randint(100, 500),
            'creation_date': datetime.now() - timedelta(hours=random.randint(1, 24)),
            'Status': 'ACTIVE',
            'receipt_number': f'REC{random.randint(1000, 9999)}',
            'Supplier': f'Supplier{random.randint(1, 10)}',
            'Zone': 'STORAGE'
        })
        pallet_counter += 1
    
    # Scenario 3: Special areas (should be fine)
    special_areas = ['RECEIVING', 'DOCK-01', 'STAGE-01']
    for area in special_areas:
        for i in range(3):  # 3 pallets each in special areas
            inventory_data.append({
                'pallet_id': f'SPC{pallet_counter:03d}',
                'location': area,
                'description': f'Incoming Product {pallet_counter}',
                'Quantity': random.randint(10, 50),
                'Weight_KG': random.randint(100, 500),
                'creation_date': datetime.now() - timedelta(minutes=random.randint(30, 120)),
                'Status': 'RECEIVING',
                'receipt_number': f'REC{random.randint(1000, 9999)}',
                'Supplier': f'Supplier{random.randint(1, 10)}',
                'Zone': 'INBOUND'
            })
            pallet_counter += 1
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(inventory_data)
    
    print(f"\nInventory Summary:")
    print(f"Total pallets: {len(df)}")
    print(f"Unique locations: {df['location'].nunique()}")
    
    # Show violation analysis
    print(f"\nViolation Analysis:")
    location_counts = df['location'].value_counts()
    violations = 0
    violation_locations = 0
    
    for location, count in location_counts.items():
        if location not in ['RECEIVING', 'DOCK-01', 'STAGE-01']:  # Skip special areas
            if count > 1:
                violations += count
                violation_locations += 1
                print(f"  {location}: {count} pallets (VIOLATION - {count} anomalies expected)")
    
    print(f"\nExpected Results:")
    print(f"- Storage locations in violation: {violation_locations}")
    print(f"- Total anomalies expected: {violations}")
    print(f"- Normal locations: {len([l for l, c in location_counts.items() if c == 1 and l not in ['RECEIVING', 'DOCK-01', 'STAGE-01']])}")
    
    # Save to Excel
    excel_filename = 'overcapacity_test_inventory.xlsx'
    df.to_excel(excel_filename, index=False)
    
    print(f"\n✅ Excel file created: {excel_filename}")
    print(f"Ready for testing in USER_MARCOS9 warehouse!")
    
    return df, violations

if __name__ == "__main__":
    df, expected_violations = generate_test_inventory()
    print(f"\n📊 TESTING INSTRUCTIONS:")
    print(f"1. Upload 'overcapacity_test_inventory.xlsx' to your app")
    print(f"2. Make sure warehouse is set to 'USER_MARCOS9'")  
    print(f"3. Run overcapacity rule analysis")
    print(f"4. Expected result: {expected_violations} overcapacity anomalies")
    print(f"5. All anomalies should be type 'Overcapacity' (NOT 'Smart Overcapacity')")
    print(f"6. No statistical fields should appear in results")