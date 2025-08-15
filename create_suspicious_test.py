#!/usr/bin/env python3
"""
Create targeted test for suspicious Overcapacity and Incomplete Lots scenarios
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

def create_suspicious_test():
    """Create test inventory with extreme overcapacity and incomplete lots"""
    
    inventory_data = []
    current_time = datetime.now()
    
    print("Creating SUSPICIOUS test scenarios...")
    
    # 1. EXTREME OVERCAPACITY TEST - Way beyond any reasonable capacity
    print("Adding EXTREME overcapacity scenarios...")
    
    # Put 15+ pallets in single storage positions (way beyond 5 default capacity)
    extreme_overcapacity = [
        ('01-01-001A', 15),  # 15 pallets in one position - clearly overcapacity
        ('01-01-002B', 12),  # 12 pallets in one position
        ('01-02-003C', 20),  # 20 pallets in one position - extreme
        ('02-01-004A', 18),  # 18 pallets in one position
        ('02-02-005B', 25),  # 25 pallets in one position - ridiculous overcapacity
    ]
    
    for location, pallet_count in extreme_overcapacity:
        for i in range(pallet_count):
            creation_date = current_time - timedelta(days=random.randint(1, 30))
            inventory_data.append({
                'pallet_id': generate_pallet_id(),
                'location': location,
                'creation_date': creation_date.strftime('%Y-%m-%d'),
                'receipt_number': generate_receipt_number(),
                'description': f'Stacked Item {i+1}',
                'location_type': 'STORAGE',
                'warehouse_id': 'USER_TESTF',
                'warehouse_name': 'Central Distribution Center',
                'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # 2. EXTREME INCOMPLETE LOTS TEST - Clear incomplete scenarios
    print("Adding EXTREME incomplete lot scenarios...")
    
    # Create clearly incomplete lots in RECEIVING with single pallets
    # These should trigger incomplete lot alerts
    incomplete_lot_receipts = [
        'RCP-SOLO-001',    # Only 1 pallet - clearly incomplete
        'RCP-SOLO-002',    # Only 1 pallet - clearly incomplete  
        'RCP-PARTIAL-001', # Only 1 pallet - clearly incomplete
        'RCP-TINY-001',    # Only 1 pallet - clearly incomplete
        'RCP-SINGLE-001'   # Only 1 pallet - clearly incomplete
    ]
    
    # Add single pallets for each incomplete receipt
    for receipt_id in incomplete_lot_receipts:
        creation_date = current_time - timedelta(hours=random.randint(24, 72))  # Old enough to be flagged
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': 'RECV-01',
            'creation_date': creation_date.strftime('%Y-%m-%d'),
            'receipt_number': receipt_id,
            'description': 'Incomplete Shipment Item',
            'location_type': 'RECEIVING',
            'warehouse_id': 'USER_TESTF',
            'warehouse_name': 'Central Distribution Center',
            'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Also add a "normal" multi-pallet receipt for comparison
    normal_receipt = 'RCP-NORMAL-001'
    for i in range(8):  # 8 pallets - should be considered complete
        creation_date = current_time - timedelta(hours=random.randint(1, 12))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': 'RECV-02',
            'creation_date': creation_date.strftime('%Y-%m-%d'),
            'receipt_number': normal_receipt,
            'description': 'Complete Shipment Item',
            'location_type': 'RECEIVING',
            'warehouse_id': 'USER_TESTF',
            'warehouse_name': 'Central Distribution Center',
            'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 3. Add some normal inventory for statistical baseline
    print("Adding baseline normal inventory...")
    
    # Add normal single pallets in various locations
    normal_locations = [
        '01-01-006A', '01-01-007B', '01-01-008C', '01-02-006A', '01-02-007B',
        '02-01-006A', '02-01-007B', '02-01-008C', '02-02-006A', '02-02-007B',
        '01-01-009A', '01-02-009B', '02-01-009C', '02-02-009A', '01-01-010B'
    ]
    
    descriptions = [
        'Electronics - Components', 'Home & Garden - Tools', 'Clothing - Apparel',
        'Sports - Equipment', 'Books - Literature', 'Automotive - Parts'
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
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(inventory_data)
    
    print(f"\nSuspicious Test Inventory Summary:")
    print(f"Total pallets: {len(df)}")
    print(f"\nPallets per location (top 10):")
    counts = df['location'].value_counts()
    print(counts.head(10))
    
    print(f"\nPallets per receipt (focusing on test receipts):")
    receipt_counts = df['receipt_number'].value_counts()
    test_receipts = receipt_counts[receipt_counts.index.str.contains('SOLO|PARTIAL|TINY|SINGLE|NORMAL')]
    print(test_receipts)
    
    # Save to Excel
    filename = 'SuspiciousRules_Test_Inventory.xlsx'
    df.to_excel(filename, index=False)
    print(f"\nSaved suspicious test inventory to: {filename}")
    
    return df

def print_expected_suspicious_results():
    """Print what we expect to find in this extreme test"""
    print("\n" + "="*70)
    print("EXPECTED RESULTS FOR SUSPICIOUS TEST")
    print("="*70)
    
    print("🔴 EXTREME OVERCAPACITY SCENARIOS:")
    print("   - 01-01-001A: 15 pallets (capacity ~5) = 3x overcapacity")
    print("   - 01-01-002B: 12 pallets (capacity ~5) = 2.4x overcapacity") 
    print("   - 01-02-003C: 20 pallets (capacity ~5) = 4x overcapacity")
    print("   - 02-01-004A: 18 pallets (capacity ~5) = 3.6x overcapacity")
    print("   - 02-02-005B: 25 pallets (capacity ~5) = 5x overcapacity")
    print("   EXPECTED: Should trigger overcapacity alerts (5 locations)")
    
    print("\n🟡 EXTREME INCOMPLETE LOTS:")
    print("   - RCP-SOLO-001: 1 pallet only")
    print("   - RCP-SOLO-002: 1 pallet only")
    print("   - RCP-PARTIAL-001: 1 pallet only") 
    print("   - RCP-TINY-001: 1 pallet only")
    print("   - RCP-SINGLE-001: 1 pallet only")
    print("   - RCP-NORMAL-001: 8 pallets (complete)")
    print("   EXPECTED: Should trigger incomplete lot alerts for 5 single-pallet receipts")
    
    print("\n🟢 BASELINE INVENTORY:")
    print("   - 15 normal locations with 1 pallet each")
    print("   - Should provide statistical baseline for comparison")
    
    print("\nTOTAL EXPECTED ANOMALIES:")
    print("- Overcapacity: 90+ pallets (from 5 extreme locations)")
    print("- Incomplete Lots: 5 receipts") 
    print("- Others: As usual (invalid locations, etc.)")

if __name__ == "__main__":
    # Create the suspicious test inventory
    df = create_suspicious_test()
    
    # Print expected results
    print_expected_suspicious_results()
    
    print(f"\n{'='*70}")
    print("SUSPICIOUS TEST FILE READY")
    print("="*70)
    print("File: SuspiciousRules_Test_Inventory.xlsx")
    print("This should DEFINITELY trigger Overcapacity and Incomplete Lots alerts!")
    print("If these rules still show 0 anomalies, then we found a real issue.")