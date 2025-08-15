#!/usr/bin/env python3
"""
Create comprehensive inventory test file for 2×2×16×3 warehouse
Tests all rule scenarios with realistic data
"""

import pandas as pd
from datetime import datetime, timedelta
import random
import string

def generate_pallet_id():
    """Generate realistic pallet ID"""
    return f"PLT-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

def generate_receipt_number():
    """Generate realistic receipt number"""
    return f"RCP-{random.randint(100000, 999999)}"

def create_test_inventory():
    """Create comprehensive test inventory for warehouse testing"""
    
    # Warehouse structure: 2 aisles × 2 racks × 16 positions × 3 levels (ABC)
    # Special areas: RECV-01, RECV-02, STAGE-01, DOCK-01
    
    inventory_data = []
    current_time = datetime.now()
    
    print("Creating test inventory for 2×2×16×3 warehouse...")
    
    # 1. FORGOTTEN PALLETS ALERT TEST (13 expected anomalies)
    # Pallets in RECEIVING areas for too long (>6 hours)
    print("Adding forgotten pallets in RECEIVING...")
    forgotten_pallets = [
        ('RECV-01', 48), ('RECV-01', 72), ('RECV-01', 24), ('RECV-01', 12),
        ('RECV-01', 96), ('RECV-02', 36), ('RECV-02', 48), ('RECV-02', 18),
        ('RECV-02', 120), ('RECV-02', 8), ('RECV-02', 144), ('RECV-02', 168),
        ('RECV-02', 192)  # 13 pallets total
    ]
    
    for location, hours_old in forgotten_pallets:
        creation_date = current_time - timedelta(hours=hours_old)
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': location,
            'creation_date': creation_date.strftime('%Y-%m-%d'),
            'receipt_number': generate_receipt_number(),
            'description': 'Electronics - Components',
            'location_type': 'RECEIVING',
            'warehouse_id': 'USER_TESTF',
            'warehouse_name': 'Central Distribution Center',
            'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 2. OVERCAPACITY ALERT TEST (8 expected anomalies)
    # Each position has capacity of 1 pallet per level, so 2+ pallets = overcapacity
    print("Adding overcapacity scenarios...")
    overcapacity_positions = [
        ('01-01-001A', 3), ('01-01-002B', 2), ('01-02-003C', 2),
        ('02-01-004A', 4), ('02-01-005B', 2), ('02-02-006C', 2),
        ('01-01-007A', 2), ('02-02-008B', 3)  # 8 positions with excess pallets
    ]
    
    for base_location, pallet_count in overcapacity_positions:
        for i in range(pallet_count):
            creation_date = current_time - timedelta(days=random.randint(1, 30))
            inventory_data.append({
                'pallet_id': generate_pallet_id(),
                'location': base_location,
                'creation_date': creation_date.strftime('%Y-%m-%d'),
                'receipt_number': generate_receipt_number(),
                'description': 'Home & Garden - Tools',
                'location_type': 'STORAGE',
                'warehouse_id': 'USER_TESTF',
                'warehouse_name': 'Central Distribution Center',
                'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # 3. INVALID LOCATIONS TEST (5 expected anomalies)
    print("Adding invalid locations...")
    invalid_locations = ['INVALID-01', 'ERROR-404', 'MISSING-LOC', 'BAD-ZONE', 'FAKE-001']
    
    for location in invalid_locations:
        creation_date = current_time - timedelta(days=random.randint(1, 10))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': location,
            'creation_date': creation_date.strftime('%Y-%m-%d'),
            'receipt_number': generate_receipt_number(),
            'description': 'Lost Items',
            'location_type': 'STORAGE',
            'warehouse_id': 'USER_TESTF',
            'warehouse_name': 'Central Distribution Center',
            'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 4. INCOMPLETE LOTS ALERT TEST (Depends on receipt grouping)
    # Create incomplete lots in RECEIVING
    print("Adding incomplete lot scenarios...")
    incomplete_receipts = ['RCP-INCOMPLETE-1', 'RCP-INCOMPLETE-2']
    
    # First incomplete lot: only 2 pallets of what should be 5+
    for i in range(2):
        creation_date = current_time - timedelta(hours=random.randint(12, 48))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': 'RECV-01',
            'creation_date': creation_date.strftime('%Y-%m-%d'),
            'receipt_number': 'RCP-INCOMPLETE-1',
            'description': 'Clothing - Seasonal',
            'location_type': 'RECEIVING',
            'warehouse_id': 'USER_TESTF',
            'warehouse_name': 'Central Distribution Center',
            'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Second incomplete lot: only 3 pallets of what should be 6+
    for i in range(3):
        creation_date = current_time - timedelta(hours=random.randint(12, 48))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': 'RECV-02',
            'creation_date': creation_date.strftime('%Y-%m-%d'),
            'receipt_number': 'RCP-INCOMPLETE-2',
            'description': 'Sports - Equipment',
            'location_type': 'RECEIVING',
            'warehouse_id': 'USER_TESTF',
            'warehouse_name': 'Central Distribution Center',
            'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 5. NORMAL VALID INVENTORY
    print("Adding normal valid inventory...")
    
    # Fill some storage locations with normal pallets
    normal_locations = [
        '01-01-009A', '01-01-010B', '01-01-011C', '01-02-009A', '01-02-010B',
        '02-01-009A', '02-01-010B', '02-01-011C', '02-02-009A', '02-02-010B',
        '01-01-012A', '01-02-012B', '02-01-012C', '02-02-012A', '01-01-013B',
        '01-02-013C', '02-01-013A', '02-02-013B', '01-01-014C', '01-02-014A'
    ]
    
    descriptions = [
        'Electronics - Components', 'Home & Garden - Tools', 'Clothing - Apparel',
        'Sports - Equipment', 'Books - Literature', 'Toys - Educational',
        'Health - Supplements', 'Automotive - Parts'
    ]
    
    for location in normal_locations:
        creation_date = current_time - timedelta(days=random.randint(1, 60))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': location,
            'creation_date': creation_date.strftime('%Y-%m-%d'),
            'receipt_number': generate_receipt_number(),
            'description': random.choice(descriptions),
            'location_type': 'STORAGE',
            'warehouse_id': 'USER_TESTF',
            'warehouse_name': 'Central Distribution Center',
            'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 6. STAGING AREA PALLETS (should be fine, no specific rules for staging)
    print("Adding staging area pallets...")
    for i in range(3):
        creation_date = current_time - timedelta(hours=random.randint(1, 4))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': 'STAGE-01',
            'creation_date': creation_date.strftime('%Y-%m-%d'),
            'receipt_number': generate_receipt_number(),
            'description': 'Outbound - Ready',
            'location_type': 'STAGING',
            'warehouse_id': 'USER_TESTF',
            'warehouse_name': 'Central Distribution Center',
            'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(inventory_data)
    
    print(f"\nInventory Summary:")
    print(f"Total pallets: {len(df)}")
    print(f"Location distribution:")
    print(df['location'].value_counts().head(10))
    
    # Save to Excel
    filename = 'TestWarehouse_RuleValidation_Inventory.xlsx'
    df.to_excel(filename, index=False)
    print(f"\nSaved inventory to: {filename}")
    
    return df

def print_expected_anomalies():
    """Print expected anomaly counts for each rule"""
    print("\n" + "="*60)
    print("EXPECTED ANOMALY COUNTS")
    print("="*60)
    
    print("1. Forgotten Pallets Alert (VERY HIGH)")
    print("   - Rule: Pallets in RECEIVING/TRANSITIONAL > 6 hours")
    print("   - Expected: 13 anomalies")
    print("   - Locations: RECV-01 (5 pallets), RECV-02 (8 pallets)")
    
    print("\n2. Incomplete Lots Alert (VERY HIGH)")
    print("   - Rule: Receipt completion < 80% in RECEIVING")
    print("   - Expected: Variable (depends on algorithm)")
    print("   - Test receipts: RCP-INCOMPLETE-1 (2 pallets), RCP-INCOMPLETE-2 (3 pallets)")
    
    print("\n3. Overcapacity Alert (HIGH)")
    print("   - Rule: More than 1 pallet per position (capacity = 1)")
    print("   - Expected: 8 anomalies")
    print("   - Affected positions with 2+ pallets each")
    
    print("\n4. Invalid Locations Alert (HIGH)")
    print("   - Rule: Locations not in warehouse database")
    print("   - Expected: 5 anomalies")
    print("   - Invalid locations: INVALID-01, ERROR-404, MISSING-LOC, BAD-ZONE, FAKE-001")
    
    print("\n5. AISLE Stuck Pallets (HIGH)")
    print("   - Rule: Pallets in AISLE* locations > 4 hours")
    print("   - Expected: 0 anomalies (no AISLE locations in test)")
    
    print("\n6. Scanner Error Detection (HIGH)")
    print("   - Rule: Duplicate scans, impossible locations")
    print("   - Expected: 0 anomalies (clean test data)")
    
    print("\n7. Location Type Mismatches (HIGH)")
    print("   - Rule: Location type consistency validation")
    print("   - Expected: 0 anomalies (consistent test data)")
    
    print("\nTOTAL EXPECTED ANOMALIES: ~26-30")
    print("(13 forgotten + 0-5 incomplete lots + 8 overcapacity + 5 invalid locations)")

if __name__ == "__main__":
    # Create the test inventory
    df = create_test_inventory()
    
    # Print expected results
    print_expected_anomalies()
    
    print(f"\n{'='*60}")
    print("TEST FILE READY")
    print("="*60)
    print("File: TestWarehouse_RuleValidation_Inventory.xlsx")
    print("Ready to upload and test against your warehouse rules!")