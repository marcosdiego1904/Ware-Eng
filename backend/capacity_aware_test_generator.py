#!/usr/bin/env python3
"""
Capacity-Aware Test Data Generator for DEFAULT1 Warehouse
Creates 800 pallets with CONTROLLED overcapacity violations (not hundreds!)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_warehouse_locations():
    """Generate all valid location codes for DEFAULT1 warehouse with capacity info"""
    
    # Storage locations: 4 aisles × 2 racks × 29 positions × 4 levels (ABCD)
    # CAPACITY = 1 pallet per location
    storage_locations = []
    
    for aisle in range(1, 5):  # Aisles 1-4
        for rack in range(1, 3):  # Racks 1-2
            for position in range(1, 30):  # Positions 1-29
                for level in ['A', 'B', 'C', 'D']:  # Levels A-D
                    location = f"{aisle}-{rack:02d}-{position:02d}{level}"
                    storage_locations.append(location)
    
    # Special locations with their specific capacities
    special_locations = {
        'RECV-01': 10,      # RECEIVING, capacity 10
        'RECV-02': 10,      # RECEIVING, capacity 10  
        'STAGE-01': 5,      # STAGING, capacity 5
        'DOCK-01': 2,       # DOCK, capacity 2
        'AISLE-01': 10,     # TRANSITIONAL, capacity 10
        'AISLE-02': 10,     # TRANSITIONAL, capacity 10
        'AISLE-03': 10,     # TRANSITIONAL, capacity 10
        'AISLE-04': 10      # TRANSITIONAL, capacity 10
    }
    
    return storage_locations, special_locations

def create_capacity_aware_test_dataset():
    """Create 800 pallets with CONTROLLED overcapacity violations"""
    
    storage_locations, special_locations = generate_warehouse_locations()
    all_special_locs = list(special_locations.keys())
    
    print(f"Available storage locations: {len(storage_locations)} (capacity: 1 each)")
    print(f"Available special locations: {len(all_special_locs)} (various capacities)")
    
    pallets = []
    base_date = datetime.now() - timedelta(hours=3)
    pallet_counter = 1
    used_storage_locations = set()  # Track used storage locations to respect capacity=1
    
    # Standard product categories
    standard_products = [
        'GENERAL MERCHANDISE', 'ELECTRONICS EQUIPMENT', 'AUTOMOTIVE COMPONENTS',
        'HOUSEHOLD APPLIANCES', 'INDUSTRIAL MACHINERY', 'OFFICE FURNITURE',
        'SEASONAL DECORATIONS', 'TEXTILE MATERIALS', 'SPORTING EQUIPMENT',
        'CONSTRUCTION TOOLS', 'MEDICAL SUPPLIES', 'FOOD PACKAGING'
    ]
    
    restricted_products = [
        'HAZMAT CHEMICALS', 'FLAMMABLE SOLVENTS', 'CORROSIVE ACIDS',
        'TOXIC PESTICIDES', 'EXPLOSIVE MATERIALS', 'RADIOACTIVE ISOTOPES'
    ]
    
    # RULE 1: STAGNANT_PALLETS (5 anomalies)
    # Use RECV-01 and RECV-02 (capacity 10 each, so safe)
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
    
    # RULE 2: UNCOORDINATED_LOTS (5 anomalies)
    # Create lot with 20 total pallets: 15 completed + 5 stragglers = 75% completion
    lot_receipt = 'R-UNCOORD-LOT-001'
    
    # 15 completed pallets - use unique storage locations
    for i in range(15):
        # Get unique storage location
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        storage_location = random.choice(available_storage[:100])  # Use first 100 for variety
        used_storage_locations.add(storage_location)
        
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': lot_receipt,
            'description': 'COORDINATED ELECTRONICS',
            'location': storage_location,
            'creation_date': base_date - timedelta(hours=2)
        })
        pallet_counter += 1
    
    # 5 stragglers in RECV-01 (safe, capacity=10)
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': lot_receipt,
            'description': 'COORDINATED ELECTRONICS',
            'location': 'RECV-01',
            'creation_date': base_date - timedelta(hours=2)
        })
        pallet_counter += 1
    
    # RULE 3: OVERCAPACITY (5 CONTROLLED violations)
    # Strategy: Create specific violations in designated storage locations
    # Select 5 storage locations for intentional 2-pallet violations
    overcap_storage_locations = ['1-01-01A', '2-02-15B', '3-01-20C', '4-02-10D', '1-02-25A']
    
    print("Creating CONTROLLED overcapacity violations:")
    for i, location in enumerate(overcap_storage_locations):
        # Add 2 pallets to each location (capacity=1, so both will be flagged)
        for j in range(2):
            pallets.append({
                'pallet_id': f'P{pallet_counter:06d}',
                'receipt_number': f'R-OVERCAP-{i:03d}-{j}',
                'description': random.choice(standard_products),
                'location': location,
                'creation_date': base_date + timedelta(minutes=i*10 + j*5)
            })
            pallet_counter += 1
        used_storage_locations.add(location)  # Mark as used
        print(f"  {location}: 2 pallets (capacity: 1) = 1 excess")
    
    # RULE 4: INVALID_LOCATION (5 anomalies)
    invalid_locations = [
        'INVALID-ZONE-X', 'UNDEFINED-AREA-99', 'TEMP-LOCATION-ABC',
        'GHOST-STORAGE-404', 'ERROR-LOCATION-XXX'
    ]
    
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-INVALID-{i:03d}',
            'description': random.choice(standard_products),
            'location': invalid_locations[i],
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # RULE 5: LOCATION_SPECIFIC_STAGNANT (5 anomalies)
    # Use AISLE locations (capacity=10 each, so safe)
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
    
    # RULE 6: DATA_INTEGRITY (5 anomalies)
    # 3 duplicate pallet IDs + 2 impossible locations
    
    # 3 duplicate pairs
    for i in range(3):
        original_id = f'P{pallet_counter:06d}'
        
        # Original pallet - use unique storage location
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        storage_location = random.choice(available_storage)
        used_storage_locations.add(storage_location)
        
        pallets.append({
            'pallet_id': original_id,
            'receipt_number': f'R-ORIGINAL-{i:03d}',
            'description': random.choice(standard_products),
            'location': storage_location,
            'creation_date': base_date
        })
        pallet_counter += 1
        
        # Duplicate scan (same pallet_id, different location)
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        dup_location = random.choice(available_storage)
        used_storage_locations.add(dup_location)
        
        pallets.append({
            'pallet_id': original_id,  # Same ID = duplicate
            'receipt_number': f'R-DUPLICATE-{i:03d}',
            'description': random.choice(standard_products),
            'location': dup_location,
            'creation_date': base_date + timedelta(minutes=45)
        })
        # Don't increment counter for duplicate
    
    # 2 impossible locations
    impossible_locations = [
        '@#$%INVALID!@#$%^&*()', 
        '12345678901234567890IMPOSSIBLY_LONG_LOCATION_NAME'
    ]
    
    for i in range(2):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-IMPOSSIBLE-{i:03d}',
            'description': random.choice(standard_products),
            'location': impossible_locations[i],
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # RULE 7: MISSING_LOCATION (5 anomalies)
    missing_values = [None, '', 'NAN', pd.NA, '   ']
    
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-MISSING-LOC-{i:03d}',
            'description': random.choice(standard_products),
            'location': missing_values[i],
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # RULE 8: PRODUCT_INCOMPATIBILITY (5 anomalies)
    # Use unique storage locations for hazmat violations
    for i in range(5):
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        storage_location = random.choice(available_storage)
        used_storage_locations.add(storage_location)
        
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-HAZMAT-VIOLATION-{i:03d}',
            'description': restricted_products[i],
            'location': storage_location,  # Regular storage (not hazmat zone)
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # CAPACITY-AWARE DISTRIBUTION: Remaining pallets
    current_count = len(pallets)
    remaining_pallets = 800 - current_count
    
    print(f"\\nCurrent pallets: {current_count}")
    print(f"Remaining pallets needed: {remaining_pallets}")
    print(f"Used storage locations so far: {len(used_storage_locations)}")
    print(f"Available unique storage locations: {len(storage_locations) - len(used_storage_locations)}")
    
    # Distribute remaining pallets using MOSTLY unique storage locations
    receipt_base = 3000
    
    for i in range(remaining_pallets):
        # Use unique storage locations for capacity=1 compliance
        available_storage = [loc for loc in storage_locations if loc not in used_storage_locations]
        
        if available_storage:
            # Use unique storage location
            storage_location = random.choice(available_storage)
            used_storage_locations.add(storage_location)
        else:
            # If we run out of unique locations, use special locations (higher capacity)
            # This should rarely happen with 928 storage locations available
            storage_location = random.choice(all_special_locs)
        
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-{receipt_base + (i // 10):04d}',
            'description': random.choice(standard_products),
            'location': storage_location,
            'creation_date': base_date + timedelta(minutes=random.randint(-180, 180))
        })
        pallet_counter += 1
    
    return pd.DataFrame(pallets)

def validate_capacity_compliance(df):
    """Validate that we have controlled overcapacity (not hundreds)"""
    
    print("\\n=== CAPACITY COMPLIANCE VALIDATION ===")
    
    location_counts = df['location'].value_counts()
    
    # Count overcapacity violations
    storage_overcap = 0
    special_overcap = 0
    
    # Special location capacities
    special_capacities = {
        'RECV-01': 10, 'RECV-02': 10, 'STAGE-01': 5, 'DOCK-01': 2,
        'AISLE-01': 10, 'AISLE-02': 10, 'AISLE-03': 10, 'AISLE-04': 10
    }
    
    # Check storage locations (capacity=1)
    for location, count in location_counts.items():
        if location not in special_capacities and count > 1:
            storage_overcap += count  # Each pallet in overcapacity location
    
    # Check special locations
    for location, capacity in special_capacities.items():
        count = location_counts.get(location, 0)
        if count > capacity:
            special_overcap += (count - capacity)  # Only excess pallets
    
    total_overcap_pallets = storage_overcap + special_overcap
    
    print(f"Storage overcapacity violations: {storage_overcap} pallets")
    print(f"Special location overcapacity: {special_overcap} pallets") 
    print(f"Total expected overcapacity anomalies: ~{total_overcap_pallets}")
    print(f"Target: ~10-15 anomalies (vs 444 in previous test)")
    
    # Show overcapacity locations
    print("\\nOvercapacity locations:")
    for location, count in location_counts.items():
        if location in special_capacities:
            capacity = special_capacities[location]
            if count > capacity:
                print(f"  {location}: {count}/{capacity} pallets (OVERCAP)")
        elif count > 1:
            print(f"  {location}: {count}/1 pallets (OVERCAP)")
    
    return total_overcap_pallets

def main():
    """Generate capacity-aware test dataset"""
    
    print("=== GENERATING CAPACITY-AWARE DEFAULT1 WAREHOUSE TEST DATASET ===")
    print("Strategy: Controlled overcapacity violations (not random distribution)")
    
    # Generate the dataset
    df = create_capacity_aware_test_dataset()
    
    # Validate capacity compliance
    expected_overcap = validate_capacity_compliance(df)
    
    # Format timestamps for Excel
    df['creation_date'] = df['creation_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Save to Excel
    output_file = 'test2.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\\nDataset saved to: {output_file}")
    print(f"Total records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Final summary
    print("\\n=== CONTROLLED ANOMALY SUMMARY ===")
    print("Each rule has exactly 5 anomalies:")
    print("- STAGNANT_PALLETS: 5 pallets in RECV locations")
    print("- UNCOORDINATED_LOTS: 5 stragglers from 20-pallet lot")
    print("- OVERCAPACITY: 10 pallets in 5 storage locations (2 each)")
    print("- INVALID_LOCATION: 5 pallets in undefined locations") 
    print("- LOCATION_SPECIFIC_STAGNANT: 5 pallets in AISLE locations")
    print("- DATA_INTEGRITY: 5 issues (3 duplicates + 2 impossible)")
    print("- MISSING_LOCATION: 5 pallets with null/empty locations")
    print("- PRODUCT_INCOMPATIBILITY: 5 restricted products")
    
    expected_total = 5 * 8 + 5  # 8 rules x 5 each + 5 extra for duplicates
    print(f"\\nExpected total anomalies: ~{expected_total}")
    print(f"Expected overcapacity anomalies: ~10 (not 444!)")
    
    return df

if __name__ == "__main__":
    df = main()
    print("\\n=== SAMPLE DATA (First 15 records) ===")
    for i, row in df.head(15).iterrows():
        print(f"{i+1:2d}. {row.pallet_id} | {row.receipt_number:20s} | {row.description:25s} | {row.location:15s}")