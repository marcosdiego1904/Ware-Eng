#!/usr/bin/env python3
"""
DEFAULT1 Warehouse Test Data Generator
Creates 800 pallets with 6 anomalies per rule for comprehensive testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

def generate_warehouse_locations():
    """Generate all valid location codes for DEFAULT1 warehouse"""
    
    # Storage locations: 4 aisles × 2 racks × 29 positions × 4 levels (ABCD)
    storage_locations = []
    
    for aisle in range(1, 5):  # Aisles 1-4
        for rack in range(1, 3):  # Racks 1-2
            for position in range(1, 30):  # Positions 1-29
                for level in ['A', 'B', 'C', 'D']:  # Levels A-D
                    location = f"{aisle}-{rack:02d}-{position:02d}{level}"
                    storage_locations.append(location)
    
    # Special locations from warehouse layout
    special_locations = [
        'RECV-01',      # RECEIVING, capacity 10
        'RECV-02',      # RECEIVING, capacity 10  
        'STAGE-01',     # STAGING, capacity 5
        'DOCK-01',      # DOCK, capacity 2
        'AISLE-01',     # TRANSITIONAL, capacity 10
        'AISLE-02',     # TRANSITIONAL, capacity 10
        'AISLE-03',     # TRANSITIONAL, capacity 10
        'AISLE-04'      # TRANSITIONAL, capacity 10
    ]
    
    return storage_locations, special_locations

def generate_product_categories():
    """Define product categories and restrictions"""
    
    standard_products = [
        'GENERAL MERCHANDISE',
        'ELECTRONICS EQUIPMENT', 
        'AUTOMOTIVE COMPONENTS',
        'HOUSEHOLD APPLIANCES',
        'INDUSTRIAL MACHINERY',
        'OFFICE FURNITURE',
        'SEASONAL DECORATIONS',
        'TEXTILE MATERIALS',
        'SPORTING EQUIPMENT',
        'CONSTRUCTION TOOLS',
        'MEDICAL SUPPLIES',
        'FOOD PACKAGING'
    ]
    
    restricted_products = [
        'HAZMAT CHEMICALS',
        'FLAMMABLE SOLVENTS', 
        'CORROSIVE ACIDS',
        'TOXIC PESTICIDES',
        'EXPLOSIVE MATERIALS',
        'RADIOACTIVE ISOTOPES'
    ]
    
    return standard_products, restricted_products

def create_default1_test_dataset():
    """Create 800 pallet test dataset with 6 anomalies per rule"""
    
    storage_locations, special_locations = generate_warehouse_locations()
    standard_products, restricted_products = generate_product_categories()
    all_valid_locations = storage_locations + special_locations
    
    print(f"Generated {len(storage_locations)} storage locations + {len(special_locations)} special locations")
    print(f"Total valid locations: {len(all_valid_locations)}")
    
    pallets = []
    base_date = datetime.now() - timedelta(hours=3)
    pallet_counter = 1
    
    # RULE 1: STAGNANT_PALLETS (6 anomalies)
    # Threshold: 6 hours in RECEIVING/STAGING locations
    stagnant_date = datetime.now() - timedelta(hours=10)  # 10 hours ago (>6 threshold)
    stagnant_locations = ['RECV-01', 'RECV-02', 'STAGE-01']
    
    for i in range(6):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-STAGNANT-{i:03d}',
            'description': random.choice(standard_products),
            'location': random.choice(stagnant_locations),
            'creation_date': stagnant_date - timedelta(hours=i*2)
        })
        pallet_counter += 1
    
    # RULE 2: UNCOORDINATED_LOTS (6 anomalies)
    # 80% completion threshold - create lot with 24 total pallets (20 completed + 6 stragglers = 83% completion)
    lot_receipt = 'R-UNCOORD-LOT-001'
    
    # First create 18 completed pallets in storage (75% of 24)
    for i in range(18):
        storage_location = random.choice(storage_locations[:100])  # Use variety of storage locations
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': lot_receipt,
            'description': 'COORDINATED ELECTRONICS',
            'location': storage_location,
            'creation_date': base_date - timedelta(hours=2)
        })
        pallet_counter += 1
    
    # Then create 6 stragglers still in receiving (triggers >80% completion rule)
    for i in range(6):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': lot_receipt,
            'description': 'COORDINATED ELECTRONICS',
            'location': random.choice(['RECV-01', 'RECV-02']),
            'creation_date': base_date - timedelta(hours=2)
        })
        pallet_counter += 1
    
    # RULE 3: OVERCAPACITY (6 anomalies)
    # DOCK-01 has capacity of 2, so 6 pallets creates overcapacity
    for i in range(6):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-OVERCAP-{i:03d}',
            'description': random.choice(standard_products),
            'location': 'DOCK-01',  # Capacity 2, so 6 pallets = overcapacity
            'creation_date': base_date + timedelta(minutes=i*15)
        })
        pallet_counter += 1
    
    # RULE 4: INVALID_LOCATION (6 anomalies)
    invalid_locations = [
        'INVALID-ZONE-X',
        'UNDEFINED-AREA-99', 
        'TEMP-LOCATION-ABC',
        'GHOST-STORAGE-404',
        'ERROR-LOCATION-XXX',
        'NONEXISTENT-DOCK'
    ]
    
    for i in range(6):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-INVALID-{i:03d}',
            'description': random.choice(standard_products),
            'location': invalid_locations[i],
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # RULE 5: LOCATION_SPECIFIC_STAGNANT (6 anomalies) 
    # Threshold: 4 hours in AISLE locations
    aisle_stagnant_date = datetime.now() - timedelta(hours=8)  # 8 hours ago (>4 threshold)
    aisle_locations = ['AISLE-01', 'AISLE-02', 'AISLE-03', 'AISLE-04']
    
    for i in range(6):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-AISLE-STUCK-{i:03d}',
            'description': random.choice(standard_products),
            'location': aisle_locations[i % len(aisle_locations)],
            'creation_date': aisle_stagnant_date - timedelta(hours=i*3)
        })
        pallet_counter += 1
    
    # RULE 6: DATA_INTEGRITY (6 anomalies total)
    # 4 duplicate pallet IDs + 2 impossible locations
    
    # Create 4 duplicate pairs
    for i in range(4):
        original_id = f'P{pallet_counter:06d}'
        # Original pallet
        pallets.append({
            'pallet_id': original_id,
            'receipt_number': f'R-ORIGINAL-{i:03d}',
            'description': random.choice(standard_products),
            'location': random.choice(all_valid_locations),
            'creation_date': base_date
        })
        pallet_counter += 1
        
        # Duplicate scan (same pallet_id)
        pallets.append({
            'pallet_id': original_id,  # Same ID = duplicate
            'receipt_number': f'R-DUPLICATE-{i:03d}',
            'description': random.choice(standard_products),
            'location': random.choice(all_valid_locations),
            'creation_date': base_date + timedelta(minutes=45)
        })
        # Don't increment counter for duplicate
    
    # 2 impossible locations
    impossible_locations = [
        '@#$%INVALID!@#$%^&*()',
        '12345678901234567890IMPOSSIBLY_LONG_LOCATION_NAME_THAT_EXCEEDS_LIMITS'
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
    
    # RULE 7: MISSING_LOCATION (6 anomalies)
    missing_values = [None, '', 'NAN', pd.NA, np.nan, '   ']  # Various null representations
    
    for i in range(6):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-MISSING-LOC-{i:03d}',
            'description': random.choice(standard_products),
            'location': missing_values[i],
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # RULE 8: PRODUCT_INCOMPATIBILITY (6 anomalies)
    # Restricted products in general storage areas
    general_storage_locations = [
        '1-01-01A',   # Regular storage racks  
        '2-01-05B',
        '3-02-10C', 
        '4-01-15D',
        'RECV-01',    # Receiving area (not for hazmat)
        'STAGE-01'    # Staging area (not for hazmat)
    ]
    
    for i in range(6):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-HAZMAT-VIOLATION-{i:03d}',
            'description': restricted_products[i],  # Hazmat products
            'location': general_storage_locations[i],  # Wrong zones
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # Calculate remaining pallets needed
    total_anomalies = 6 + 24 + 6 + 6 + 6 + 10 + 6 + 6  # 70 total anomalies
    remaining_pallets = 800 - len(pallets)
    
    print(f"Current pallets: {len(pallets)}")
    print(f"Remaining needed: {remaining_pallets}")
    
    # Generate remaining valid records
    receipt_base = 2000
    for i in range(remaining_pallets):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-{receipt_base + (i // 12):04d}',  # ~12 pallets per receipt
            'description': random.choice(standard_products),
            'location': random.choice(all_valid_locations),
            'creation_date': base_date + timedelta(minutes=random.randint(-180, 180))
        })
        pallet_counter += 1
    
    return pd.DataFrame(pallets)

def main():
    """Generate and save the DEFAULT1 warehouse test dataset"""
    
    print("=== GENERATING DEFAULT1 WAREHOUSE TEST DATASET ===")
    print("Warehouse: DEFAULT1 (4 aisles × 2 racks × 29 positions × 4 levels)")
    print("Target: 800 pallets with 6 anomalies per rule")
    
    # Generate the dataset
    df = create_default1_test_dataset()
    
    # Format timestamps for Excel
    df['creation_date'] = df['creation_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Save to Excel
    output_file = 'test1.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\nDataset saved to: {output_file}")
    print(f"Total records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Anomaly breakdown
    print("\n=== ANOMALY BREAKDOWN ===")
    print("Each rule has exactly 6 anomalies:")
    print("- STAGNANT_PALLETS: 6 pallets in RECV/STAGE for >6 hours")
    print("- UNCOORDINATED_LOTS: 6 stragglers from 24-pallet lot (75% completion)")
    print("- OVERCAPACITY: 6 pallets in DOCK-01 (capacity: 2)")
    print("- INVALID_LOCATION: 6 pallets in undefined location codes")
    print("- LOCATION_SPECIFIC_STAGNANT: 6 pallets stuck in AISLE locations >4 hours")
    print("- DATA_INTEGRITY: 6 issues (4 duplicate pallet IDs + 2 impossible locations)")
    print("- MISSING_LOCATION: 6 pallets with null/empty locations")
    print("- PRODUCT_INCOMPATIBILITY: 6 restricted products in general areas")
    print("- TEMPERATURE_ZONE_MISMATCH: 0 (excluded)")
    
    total_anomalies = 6 * 8 + 2  # 8 rules × 6 anomalies + 2 extra for duplicates
    print(f"\nTotal anomalies: {total_anomalies}")
    print(f"Valid records: {len(df) - total_anomalies}")
    
    return df

if __name__ == "__main__":
    df = main()
    print("\n=== SAMPLE DATA (First 20 records) ===")
    for i, row in df.head(20).iterrows():
        print(f"{i+1:2d}. {row.pallet_id} | {row.receipt_number:20s} | {row.description:25s} | {row.location:15s} | {row.creation_date}")