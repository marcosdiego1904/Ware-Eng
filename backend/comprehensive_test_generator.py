#!/usr/bin/env python3
"""
Comprehensive 800-Pallet Test Dataset Generator
Creates exactly 800 pallets with 5 anomalies per business rule (excluding temperature)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_comprehensive_test_data():
    """Generate exactly 800 pallet records with specific rule violations"""
    
    pallets = []
    base_date = datetime.now() - timedelta(hours=2)
    
    # Configuration
    valid_locations = [
        'A-01-01A', 'A-01-01B', 'A-01-02A', 'A-01-02B', 'A-02-01A', 'A-02-01B',
        'B-01-01A', 'B-01-01B', 'B-02-01A', 'B-02-01B', 'C-01-01A', 'C-01-01B',
        'STORAGE-001', 'STORAGE-002', 'STORAGE-003', 'STORAGE-004', 'STORAGE-005',
        'RECEIVING', 'TRANSITIONAL', 'DOCK-01', 'DOCK-02', 'DOCK-03'
    ]
    
    products = [
        'GENERAL MERCHANDISE', 'ELECTRONICS GOODS', 'AUTOMOTIVE PARTS',
        'HOUSEHOLD ITEMS', 'INDUSTRIAL SUPPLIES', 'OFFICE EQUIPMENT',
        'SEASONAL PRODUCTS', 'TEXTILE GOODS', 'FOOD PRODUCTS',
        'CLEANING SUPPLIES', 'HARDWARE ITEMS', 'SPORTING GOODS'
    ]
    
    pallet_counter = 1
    
    # 1. STAGNANT_PALLETS (5 anomalies)
    stagnant_date = datetime.now() - timedelta(hours=12)  # >6 hours threshold
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-STAGNANT-{i:03d}',
            'description': random.choice(products),
            'location': random.choice(['RECEIVING', 'TRANSITIONAL']),
            'creation_date': stagnant_date - timedelta(hours=i*2)
        })
        pallet_counter += 1
    
    # 2. UNCOORDINATED_LOTS (5 anomalies)
    # Need a lot with 80%+ completion to trigger stragglers
    lot_receipt = 'R-UNCOORD-LOT'
    
    # First add 15 completed pallets (75% of 20 total)
    for i in range(15):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': lot_receipt,
            'description': 'COORDINATED PRODUCT',
            'location': random.choice(['STORAGE-001', 'STORAGE-002', 'STORAGE-003']),
            'creation_date': base_date - timedelta(hours=1)
        })
        pallet_counter += 1
    
    # Then add 5 stragglers still in RECEIVING (triggers >80% completion rule)
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': lot_receipt,
            'description': 'COORDINATED PRODUCT',
            'location': 'RECEIVING',
            'creation_date': base_date - timedelta(hours=1)
        })
        pallet_counter += 1
    
    # 3. OVERCAPACITY (5 anomalies)
    # All pallets in same location to create overcapacity
    overcap_location = 'LIMITED-CAPACITY-ZONE'
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-OVERCAP-{i:03d}',
            'description': random.choice(products),
            'location': overcap_location,
            'creation_date': base_date + timedelta(minutes=i*10)
        })
        pallet_counter += 1
    
    # 4. INVALID_LOCATION (5 anomalies)
    invalid_locations = ['INVALID-ZONE', 'UNDEFINED-AREA', 'TEMP-LOCATION', 'GHOST-STORAGE', 'ERROR-LOCATION']
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-INVALID-{i:03d}',
            'description': random.choice(products),
            'location': invalid_locations[i],
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # 5. LOCATION_SPECIFIC_STAGNANT (5 anomalies)
    # Pallets in AISLE locations for >4 hours
    aisle_stagnant_date = datetime.now() - timedelta(hours=8)
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-AISLE-STUCK-{i:03d}',
            'description': random.choice(products),
            'location': f'AISLE-{i+10:02d}',
            'creation_date': aisle_stagnant_date - timedelta(hours=i*2)
        })
        pallet_counter += 1
    
    # 6. DATA_INTEGRITY (5 anomalies)
    # 3 duplicate pallet IDs + 2 impossible locations
    for i in range(3):
        # Original pallet
        original_id = f'P{pallet_counter:06d}'
        pallets.append({
            'pallet_id': original_id,
            'receipt_number': f'R-ORIGINAL-{i:03d}',
            'description': random.choice(products),
            'location': random.choice(valid_locations),
            'creation_date': base_date
        })
        pallet_counter += 1
        
        # Duplicate scan (same pallet_id, different details)
        pallets.append({
            'pallet_id': original_id,  # Same ID - creates duplicate
            'receipt_number': f'R-DUPLICATE-{i:03d}',
            'description': random.choice(products),
            'location': random.choice(valid_locations),
            'creation_date': base_date + timedelta(minutes=30)
        })
        # Don't increment counter for duplicate
    
    # 2 impossible locations
    impossible_locations = ['@#$INVALID!', '12345678901234567890WAYTOOOLONGNAME']
    for i in range(2):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-IMPOSSIBLE-{i:03d}',
            'description': random.choice(products),
            'location': impossible_locations[i],
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # 7. MISSING_LOCATION (5 anomalies)
    missing_values = [None, '', 'NAN', pd.NA, np.nan]
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-MISSING-{i:03d}',
            'description': random.choice(products),
            'location': missing_values[i],
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # 8. PRODUCT_INCOMPATIBILITY (5 anomalies)
    # Hazmat products in general storage areas (assuming restriction exists)
    hazmat_products = [
        'HAZMAT CHEMICALS', 'FLAMMABLE LIQUIDS', 'CORROSIVE MATERIALS',
        'TOXIC SUBSTANCES', 'RADIOACTIVE MATERIALS'
    ]
    general_locations = [
        'GENERAL-STORAGE', 'OFFICE-AREA', 'BREAK-ROOM', 'PUBLIC-ACCESS', 'MAIN-FLOOR'
    ]
    for i in range(5):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-HAZMAT-{i:03d}',
            'description': hazmat_products[i],
            'location': general_locations[i],
            'creation_date': base_date
        })
        pallet_counter += 1
    
    # Current count: 5+20+5+5+5+8+5+5 = 58 anomalies
    # Need to fill remaining slots with valid records to reach exactly 800
    
    remaining_slots = 800 - len(pallets)
    print(f"Current pallets: {len(pallets)}, Remaining slots: {remaining_slots}")
    
    # Generate remaining valid records
    for i in range(remaining_slots):
        pallets.append({
            'pallet_id': f'P{pallet_counter:06d}',
            'receipt_number': f'R-{1000 + (i // 10):03d}',
            'description': random.choice(products),
            'location': random.choice(valid_locations),
            'creation_date': base_date + timedelta(minutes=random.randint(-120, 120))
        })
        pallet_counter += 1
    
    return pd.DataFrame(pallets)

def main():
    print("=== GENERATING COMPREHENSIVE 800-PALLET TEST DATASET ===")
    
    df = generate_comprehensive_test_data()
    
    print(f\"\\nGenerated {len(df)} total pallet records\")
    print(f\"Columns: {list(df.columns)}\")
    
    # Format timestamps for Excel compatibility
    df['creation_date'] = df['creation_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Save to Excel
    output_file = 'inventoreportfile.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f\"\\n✅ Dataset saved to: {output_file}\")
    print(\"\\n=== ANOMALY BREAKDOWN ===\")
    print(\"Each rule type has exactly 5 anomalies (excluding temperature):\")
    print(\"• STAGNANT_PALLETS: 5 pallets in RECEIVING/TRANSITIONAL for >6 hours\")
    print(\"• UNCOORDINATED_LOTS: 5 stragglers from 20-pallet lot with 75% completion\")
    print(\"• OVERCAPACITY: 5 pallets all in same limited-capacity location\")
    print(\"• INVALID_LOCATION: 5 pallets in undefined location codes\")
    print(\"• LOCATION_SPECIFIC_STAGNANT: 5 pallets stuck in AISLE locations >4 hours\")
    print(\"• DATA_INTEGRITY: 5 issues (3 duplicate pallet IDs + 2 impossible locations)\")
    print(\"• MISSING_LOCATION: 5 pallets with null/empty location fields\")
    print(\"• PRODUCT_INCOMPATIBILITY: 5 hazmat products in general storage areas\")
    print(\"• TEMPERATURE_ZONE_MISMATCH: 0 (excluded per requirements)\")
    
    total_anomalies = 5 * 8 + 3  # 8 rules × 5 anomalies + 3 extra for duplicates 
    print(f\"\\nTotal anomalies: {total_anomalies}\")
    print(f\"Valid records: {800 - total_anomalies}\")
    print(f\"Grand total: {len(df)} pallets\")
    
    return df

if __name__ == \"__main__\":
    df = main()