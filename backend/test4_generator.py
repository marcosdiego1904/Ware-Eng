#!/usr/bin/env python3
"""
Test4 Generator - Scaled warehouse with 1050 pallets and 10 anomalies per rule
Updated warehouse: 4×2×46×4 = 1,472 storage locations + 9 special areas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_updated_warehouse_locations():
    """Generate locations for updated DEFAULT1 warehouse (4×2×46×4)"""
    
    # Updated storage locations: 4 aisles × 2 racks × 46 positions × 4 levels
    storage_locations = []
    
    for aisle in range(1, 5):  # Aisles 1-4
        for rack in range(1, 3):  # Racks 1-2
            for position in range(1, 47):  # Positions 1-46 (increased from 29)
                for level in ['A', 'B', 'C', 'D']:  # Levels A-D
                    location = f"{aisle}-{rack:02d}-{position:02d}{level}"
                    storage_locations.append(location)
    
    # Updated special locations (added DOCK-02)
    special_locations = {
        'RECV-01': 10,      # RECEIVING, capacity 10
        'RECV-02': 10,      # RECEIVING, capacity 10  
        'STAGE-01': 5,      # STAGING, capacity 5
        'DOCK-01': 2,       # DOCK, capacity 2
        'DOCK-02': 2,       # DOCK, capacity 2 (new)
        'AISLE-01': 10,     # TRANSITIONAL, capacity 10
        'AISLE-02': 10,     # TRANSITIONAL, capacity 10
        'AISLE-03': 10,     # TRANSITIONAL, capacity 10
        'AISLE-04': 10      # TRANSITIONAL, capacity 10
    }
    
    print(f"Generated warehouse layout:")
    print(f"  Storage locations: {len(storage_locations)} (4×2×46×4)")
    print(f"  Special locations: {len(special_locations)}")
    print(f"  Total locations: {len(storage_locations) + len(special_locations)}")
    
    return storage_locations, special_locations

def create_test4_dataset():
    """Create 1050 pallets with 10 anomalies per rule"""
    
    storage_locations, special_locations = generate_updated_warehouse_locations()
    all_special_locs = list(special_locations.keys())
    
    pallets = []
    base_date = datetime.now() - timedelta(hours=3)
    pallet_counter = 1
    used_storage_locations = set()
    
    # Product categories
    standard_products = [
        'GENERAL MERCHANDISE', 'ELECTRONICS EQUIPMENT', 'AUTOMOTIVE COMPONENTS',
        'HOUSEHOLD APPLIANCES', 'INDUSTRIAL MACHINERY', 'OFFICE FURNITURE',
        'SEASONAL DECORATIONS', 'TEXTILE MATERIALS', 'SPORTING EQUIPMENT',
        'CONSTRUCTION TOOLS', 'MEDICAL SUPPLIES', 'FOOD PACKAGING',
        'CLEANING SUPPLIES', 'HARDWARE ITEMS', 'GARDEN EQUIPMENT'
    ]
    
    restricted_products = [
        'HAZMAT CHEMICALS', 'FLAMMABLE SOLVENTS', 'CORROSIVE ACIDS',
        'TOXIC PESTICIDES', 'EXPLOSIVE MATERIALS', 'RADIOACTIVE ISOTOPES',
        'COMPRESSED GASES', 'OXIDIZING AGENTS', 'BIOLOGICAL HAZARDS',
        'INFECTIOUS SUBSTANCES'
    ]
    
    print(f"\\n=== CREATING 1050-PALLET DATASET WITH 10 ANOMALIES PER RULE ===")
    
    # RULE 1: STAGNANT_PALLETS (10 anomalies)
    print(f"\\n1. STAGNANT_PALLETS: Creating 10 anomalies")
    stagnant_date = datetime.now() - timedelta(hours=15)  # >10 hours threshold
    stagnant_locations = ['RECV-01', 'RECV-02', 'STAGE-01']
    
    for i in range(10):
        location = random.choice(stagnant_locations)
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-STAGNANT-{i:03d}',
            'description': random.choice(standard_products),
            'location': location,
            'creation_date': stagnant_date - timedelta(hours=i*2)
        })
        pallet_counter += 1
    
    # RULE 2: UNCOORDINATED_LOTS (10 anomalies) - Need >80% completion
    print(f"2. UNCOORDINATED_LOTS: Creating lot with >80% completion")
    lot_receipt = 'R-UNCOORD-LOT-001'
    total_lot_size = 50  # Large lot
    completed_pallets = 42  # 84% completion (42/50 = 84% > 80%)
    straggler_pallets = 8   # But only 10 will be flagged as stragglers
    actual_stragglers = 2   # Additional stragglers beyond the 8
    
    print(f"  Lot size: {total_lot_size} pallets")  
    print(f"  Completed: {completed_pallets} pallets (84% completion)")
    print(f"  Stragglers: {straggler_pallets + actual_stragglers} pallets in receiving")
    print(f"  Expected anomalies: 10 (stragglers)")
    
    # Create completed pallets in storage locations
    for i in range(completed_pallets):
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        storage_location = random.choice(available_storage[:100])
        used_storage_locations.add(storage_location)
        
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': lot_receipt,
            'description': 'COORDINATED ELECTRONICS',
            'location': storage_location,
            'creation_date': base_date - timedelta(hours=2)
        })
        pallet_counter += 1
    
    # Create 10 straggler pallets in receiving
    for i in range(straggler_pallets + actual_stragglers):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': lot_receipt,
            'description': 'COORDINATED ELECTRONICS',
            'location': 'RECV-01' if i % 2 == 0 else 'RECV-02',
            'creation_date': base_date - timedelta(hours=2)
        })
        pallet_counter += 1
    
    # RULE 3: OVERCAPACITY (10 anomalies) - 5 locations with 2 pallets each
    print(f"3. OVERCAPACITY: Creating 10 controlled violations")
    overcap_locations = [
        '1-01-01A', '1-02-20B', '2-01-30C', '2-02-40D', '3-01-15A',
        '3-02-35B', '4-01-10C', '4-02-25D', '1-01-45A', '2-02-05B'
    ]
    
    # Create 2 pallets in first 5 locations (10 pallets total)
    for i in range(5):
        location = overcap_locations[i]
        for j in range(2):
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
    
    # RULE 4: INVALID_LOCATION (10 anomalies)
    print(f"4. INVALID_LOCATION: Creating 10 invalid locations")
    invalid_locations = [
        'INVALID-ZONE-X', 'UNDEFINED-AREA-99', 'TEMP-LOCATION-ABC',
        'GHOST-STORAGE-404', 'ERROR-LOCATION-XXX', 'FAKE-AREA-123',
        'NONEXISTENT-DOCK', 'MYSTERY-ZONE-888', 'PHANTOM-LOC-666', 'VOID-STORAGE-000'
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
    
    # RULE 5: LOCATION_SPECIFIC_STAGNANT (10 anomalies) - AISLE locations >4 hours
    print(f"5. LOCATION_SPECIFIC_STAGNANT: Creating 10 AISLE violations")
    aisle_stagnant_date = datetime.now() - timedelta(hours=10)
    aisle_locations = ['AISLE-01', 'AISLE-02', 'AISLE-03', 'AISLE-04']
    
    for i in range(10):
        location = aisle_locations[i % len(aisle_locations)]
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-AISLE-STUCK-{i:03d}',
            'description': random.choice(standard_products),
            'location': location,
            'creation_date': aisle_stagnant_date - timedelta(hours=i*2)
        })
        pallet_counter += 1
    
    # RULE 6: DATA_INTEGRITY (10 anomalies) - 7 duplicates + 3 impossible
    print(f"6. DATA_INTEGRITY: Creating 7 duplicate pairs + 3 impossible locations")
    
    # Create 5 duplicate pairs (10 total duplicate detections expected)
    for i in range(5):
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
    
    # 3 impossible locations  
    impossible_locations = [
        '@#$%INVALID!@#$%^&*()', 
        '12345678901234567890IMPOSSIBLY_LONG_LOCATION_NAME',
        'SPECIAL!@#$CHARS&*()LOCATION'
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
    
    # RULE 7: MISSING_LOCATION (10 anomalies)
    print(f"7. MISSING_LOCATION: Creating 10 missing/null locations")
    missing_values = [None, '', 'NAN', pd.NA, '   ', np.nan, 'NULL', 'null', ' ', '\\t']
    
    for i in range(10):
        missing_val = missing_values[i] if i < len(missing_values) else None
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-MISSING-LOC-{i:03d}',
            'description': random.choice(standard_products),
            'location': missing_val,
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # RULE 8: PRODUCT_INCOMPATIBILITY (10 anomalies)
    print(f"8. PRODUCT_INCOMPATIBILITY: Creating 10 hazmat violations")
    for i in range(10):
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        storage_location = random.choice(available_storage)
        used_storage_locations.add(storage_location)
        
        hazmat_product = restricted_products[i % len(restricted_products)]
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-HAZMAT-VIOLATION-{i:03d}',
            'description': hazmat_product,
            'location': storage_location,  # Regular storage (not hazmat zone)
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # CAPACITY-AWARE DISTRIBUTION: Remaining pallets
    current_count = len(pallets)
    remaining_pallets = 1050 - current_count
    
    print(f"\\n=== DISTRIBUTION SUMMARY ===")
    print(f"Current pallets: {current_count}")
    print(f"Remaining pallets needed: {remaining_pallets}")
    print(f"Used storage locations: {len(used_storage_locations)}")
    print(f"Available unique storage locations: {len(storage_locations) - len(used_storage_locations)}")
    
    # Distribute remaining pallets using mostly unique storage locations
    receipt_base = 5000
    
    for i in range(remaining_pallets):
        # Use unique storage locations for capacity=1 compliance
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        
        if available_storage:
            # Use unique storage location
            storage_location = random.choice(available_storage)
            used_storage_locations.add(storage_location)
        else:
            # Use special locations if we run out (should not happen with 1,472 locations)
            storage_location = random.choice(all_special_locs)
        
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-{receipt_base + (i // 12):04d}',
            'description': random.choice(standard_products),
            'location': storage_location,
            'creation_date': base_date + timedelta(minutes=random.randint(-300, 300))
        })
        pallet_counter += 1
    
    return pd.DataFrame(pallets)

def validate_test4_dataset(df):
    """Validate the test4 dataset for controlled anomalies"""
    
    print(f"\\n=== DATASET VALIDATION ===")
    print(f"Total records: {len(df)}")
    
    # Check lot completion percentage
    lot_pallets = df[df['receipt_number'] == 'R-UNCOORD-LOT-001']
    in_receiving = len(lot_pallets[lot_pallets['location'].str.contains('RECV', na=False)])
    in_storage = len(lot_pallets) - in_receiving
    completion_pct = (in_storage / len(lot_pallets) * 100) if len(lot_pallets) > 0 else 0
    
    print(f"\\nUNCOORDINATED_LOTS validation:")
    print(f"  Total lot pallets: {len(lot_pallets)}")
    print(f"  In storage: {in_storage}")
    print(f"  In receiving: {in_receiving}")
    print(f"  Completion: {completion_pct:.1f}% (should be >80%)")
    
    # Check overcapacity
    location_counts = df['location'].value_counts()
    special_locs = ['RECV-01', 'RECV-02', 'STAGE-01', 'DOCK-01', 'DOCK-02', 'AISLE-01', 'AISLE-02', 'AISLE-03', 'AISLE-04']
    overcap_storage = 0
    overcap_locations = []
    
    for location, count in location_counts.items():
        if location not in special_locs and count > 1:
            overcap_storage += count
            overcap_locations.append((location, count))
    
    print(f"\\nOvercapacity validation:")
    print(f"  Storage locations with >1 pallet: {len(overcap_locations)}")
    print(f"  Expected overcapacity anomalies: ~{overcap_storage}")
    print(f"  Locations:")
    for loc, count in overcap_locations:
        print(f"    {loc}: {count} pallets")

def main():
    """Generate test4 dataset"""
    
    print("=== GENERATING test4.xlsx: 1050 PALLETS WITH 10 ANOMALIES PER RULE ===")
    
    df = create_test4_dataset()
    
    # Validate the dataset
    validate_test4_dataset(df)
    
    # Format timestamps
    df['creation_date'] = df['creation_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Save to Excel
    output_file = 'test4.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\\nDataset saved to: {output_file}")
    print(f"Total records: {len(df)}")
    
    print(f"\\n=== EXPECTED RESULTS ===")
    print(f"Expected total anomalies: ~80-90")
    print(f"  - STAGNANT_PALLETS: 10")
    print(f"  - UNCOORDINATED_LOTS: 10") 
    print(f"  - OVERCAPACITY: 10")
    print(f"  - INVALID_LOCATION: 10")
    print(f"  - LOCATION_SPECIFIC_STAGNANT: 10")
    print(f"  - DATA_INTEGRITY: 10-13 (5 duplicates + 3 impossible)")
    print(f"  - MISSING_LOCATION: 10")
    print(f"  - PRODUCT_INCOMPATIBILITY: 10")
    
    return df

if __name__ == "__main__":
    df = main()
    print("\\n=== SAMPLE DATA (First 10 records) ===")
    for i, row in df.head(10).iterrows():
        print(f"{i+1:2d}. {row.pallet_id} | {row.receipt_number:20s} | {row.description:25s} | {row.location:15s}")