#!/usr/bin/env python3
"""
Debug Test Data Generator - Fixes UNCOORDINATED_LOTS threshold and adds logging
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def create_debug_test_dataset():
    """Create test dataset with proper 80%+ completion and debug logging"""
    
    pallets = []
    base_date = datetime.now() - timedelta(hours=3)
    pallet_counter = 1
    
    # Generate storage and special locations
    storage_locations = []
    for aisle in range(1, 5):
        for rack in range(1, 3):
            for position in range(1, 30):
                for level in ['A', 'B', 'C', 'D']:
                    location = f"{aisle}-{rack:02d}-{position:02d}{level}"
                    storage_locations.append(location)
    
    special_locations = {
        'RECV-01': 10, 'RECV-02': 10, 'STAGE-01': 5, 'DOCK-01': 2,
        'AISLE-01': 10, 'AISLE-02': 10, 'AISLE-03': 10, 'AISLE-04': 10
    }
    
    standard_products = [
        'GENERAL MERCHANDISE', 'ELECTRONICS EQUIPMENT', 'AUTOMOTIVE COMPONENTS',
        'HOUSEHOLD APPLIANCES', 'INDUSTRIAL MACHINERY', 'OFFICE FURNITURE'
    ]
    
    restricted_products = [
        'HAZMAT CHEMICALS', 'FLAMMABLE SOLVENTS', 'CORROSIVE ACIDS',
        'TOXIC PESTICIDES', 'EXPLOSIVE MATERIALS'
    ]
    
    used_storage_locations = set()
    
    print("=== CREATING DEBUG TEST DATASET ===")
    
    # RULE 1: STAGNANT_PALLETS (5 anomalies) - unchanged
    stagnant_date = datetime.now() - timedelta(hours=12)
    for i in range(5):
        location = 'RECV-01' if i < 3 else 'RECV-02'
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-STAGNANT-{i:03d}',
            'description': random.choice(standard_products),
            'location': location,
            'creation_date': stagnant_date - timedelta(hours=i*2)
        })
        pallet_counter += 1
    
    # RULE 2: UNCOORDINATED_LOTS - FIXED FOR 80%+ COMPLETION
    lot_receipt = 'R-UNCOORD-LOT-001'
    total_lot_size = 25  # Increased from 20
    
    print(f"\\n=== UNCOORDINATED_LOTS SETUP ===")
    print(f"Creating lot: {lot_receipt}")
    print(f"Total lot size: {total_lot_size} pallets")
    
    # Strategy: 21 completed + 4 stragglers = 84% completion (>80%)
    completed_pallets = 21
    straggler_pallets = 4
    
    print(f"Completed pallets (storage): {completed_pallets}")
    print(f"Straggler pallets (receiving): {straggler_pallets}")
    print(f"Completion percentage: {(completed_pallets / total_lot_size * 100):.1f}% (should trigger >80% rule)")
    
    # Create completed pallets in storage locations
    for i in range(completed_pallets):
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        storage_location = random.choice(available_storage[:50])
        used_storage_locations.add(storage_location)
        
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': lot_receipt,
            'description': 'COORDINATED ELECTRONICS',
            'location': storage_location,
            'creation_date': base_date - timedelta(hours=2)
        })
        pallet_counter += 1
    
    # Create straggler pallets in receiving
    for i in range(straggler_pallets):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': lot_receipt,
            'description': 'COORDINATED ELECTRONICS',
            'location': 'RECV-01',  # Stragglers in receiving
            'creation_date': base_date - timedelta(hours=2)
        })
        pallet_counter += 1
    
    # RULE 3: OVERCAPACITY - Exactly 5 controlled violations (2 pallets each)
    print(f"\\n=== OVERCAPACITY SETUP ===")
    overcap_locations = ['1-01-01A', '2-02-15B', '3-01-20C', '4-02-10D', '1-02-25A']
    
    for i, location in enumerate(overcap_locations):
        for j in range(2):  # 2 pallets per location (capacity=1)
            pallets.append({
                'pallet_id': f'P{pallet_counter:06d}',
                'receipt_number': f'R-OVERCAP-{i:03d}-{j}',
                'description': random.choice(standard_products),
                'location': location,
                'creation_date': base_date + timedelta(minutes=i*10 + j*5)
            })
            pallet_counter += 1
        used_storage_locations.add(location)
        print(f"  {location}: 2 pallets (capacity: 1)")
    
    # RULE 4: INVALID_LOCATION - Exactly 5 invalid locations
    print(f"\\n=== INVALID_LOCATION SETUP ===")
    invalid_locations = [
        'INVALID-ZONE-X',
        'UNDEFINED-AREA-99', 
        'TEMP-LOCATION-ABC',
        'GHOST-STORAGE-404',
        'ERROR-LOCATION-XXX'
    ]
    
    for i, location in enumerate(invalid_locations):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-INVALID-{i:03d}',
            'description': random.choice(standard_products),
            'location': location,
            'creation_date': base_date
        })
        pallet_counter += 1
        print(f"  {location}: Invalid location")
    
    # RULE 5: LOCATION_SPECIFIC_STAGNANT - Exactly 5 in AISLE locations
    aisle_stagnant_date = datetime.now() - timedelta(hours=8)
    aisle_locations = ['AISLE-01', 'AISLE-02', 'AISLE-03', 'AISLE-04', 'AISLE-01']
    
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-AISLE-STUCK-{i:03d}',
            'description': random.choice(standard_products),
            'location': aisle_locations[i],
            'creation_date': aisle_stagnant_date - timedelta(hours=i*2)
        })
        pallet_counter += 1
    
    # RULE 6: DATA_INTEGRITY - Exactly 5 issues (3 duplicates + 2 impossible)
    print(f"\\n=== DATA_INTEGRITY SETUP ===")
    
    # Create exactly 3 duplicate pallet pairs
    for i in range(3):
        original_id = f'P{pallet_counter:06d}'
        
        # Original pallet
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        storage_location1 = random.choice(available_storage)
        used_storage_locations.add(storage_location1)
        
        pallets.append({
            'pallet_id': original_id,
            'receipt_number': f'R-ORIGINAL-{i:03d}',
            'description': random.choice(standard_products),
            'location': storage_location1,
            'creation_date': base_date
        })
        pallet_counter += 1
        
        # Duplicate scan
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        storage_location2 = random.choice(available_storage)
        used_storage_locations.add(storage_location2)
        
        pallets.append({
            'pallet_id': original_id,  # Same ID = duplicate
            'receipt_number': f'R-DUPLICATE-{i:03d}',
            'description': random.choice(standard_products),
            'location': storage_location2,
            'creation_date': base_date + timedelta(minutes=30)
        })
        print(f"  Duplicate: {original_id} in {storage_location1} and {storage_location2}")
        # Don't increment counter for duplicate
    
    # Exactly 2 impossible locations
    impossible_locations = [
        '@#$%INVALID!@#$%^&*()', 
        '12345678901234567890IMPOSSIBLY_LONG_LOCATION_NAME'
    ]
    
    for i, location in enumerate(impossible_locations):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-IMPOSSIBLE-{i:03d}',
            'description': random.choice(standard_products),
            'location': location,
            'creation_date': base_date
        })
        pallet_counter += 1
        print(f"  Impossible location: {location}")
    
    # RULE 7: MISSING_LOCATION - Exactly 5 missing
    missing_values = [None, '', 'NAN', pd.NA, '   ']
    
    for i, missing_val in enumerate(missing_values):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-MISSING-LOC-{i:03d}',
            'description': random.choice(standard_products),
            'location': missing_val,
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # RULE 8: PRODUCT_INCOMPATIBILITY - Exactly 5 hazmat violations
    for i in range(5):
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        storage_location = random.choice(available_storage)
        used_storage_locations.add(storage_location)
        
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-HAZMAT-VIOLATION-{i:03d}',
            'description': restricted_products[i],
            'location': storage_location,
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # Fill remaining pallets with unique storage locations
    current_count = len(pallets)
    remaining_pallets = 800 - current_count
    
    print(f"\\n=== DISTRIBUTION SUMMARY ===")
    print(f"Current pallets: {current_count}")
    print(f"Remaining pallets needed: {remaining_pallets}")
    print(f"Used storage locations: {len(used_storage_locations)}")
    
    receipt_base = 4000
    for i in range(remaining_pallets):
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        
        if available_storage:
            storage_location = random.choice(available_storage)
            used_storage_locations.add(storage_location)
        else:
            # Use special locations if we run out
            storage_location = random.choice(list(special_locations.keys()))
        
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-{receipt_base + (i // 10):04d}',
            'description': random.choice(standard_products),
            'location': storage_location,
            'creation_date': base_date + timedelta(minutes=random.randint(-180, 180))
        })
        pallet_counter += 1
    
    return pd.DataFrame(pallets)

def main():
    """Generate debug test dataset with corrected thresholds"""
    
    print("=== GENERATING DEBUG TEST DATASET (test3.xlsx) ===")
    
    df = create_debug_test_dataset()
    
    # Format timestamps
    df['creation_date'] = df['creation_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Save to Excel
    output_file = 'test3.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\\nDataset saved to: {output_file}")
    print(f"Total records: {len(df)}")
    
    # Validate UNCOORDINATED_LOTS setup
    lot_pallets = df[df['receipt_number'] == 'R-UNCOORD-LOT-001']
    in_receiving = len(lot_pallets[lot_pallets['location'].str.contains('RECV', na=False)])
    in_storage = len(lot_pallets) - in_receiving
    completion_pct = (in_storage / len(lot_pallets) * 100) if len(lot_pallets) > 0 else 0
    
    print(f"\\n=== FINAL VALIDATION ===")
    print(f"UNCOORDINATED_LOTS lot:")
    print(f"  Total pallets: {len(lot_pallets)}")
    print(f"  In storage: {in_storage}")
    print(f"  In receiving: {in_receiving}") 
    print(f"  Completion: {completion_pct:.1f}% (should trigger >=80% rule)")
    
    return df

if __name__ == "__main__":
    df = main()