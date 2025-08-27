#!/usr/bin/env python3
"""
PRECISION TEST INVENTORY GENERATOR FOR WAREWISE SYSTEM
Creates surgical test data targeting each evaluator with precise thresholds
"""

import pandas as pd
from datetime import datetime, timedelta

def generate_precision_inventory():
    data = []
    now = datetime.now()
    
    print("GENERATING PRECISION TEST INVENTORY")
    print("===================================")
    
    # 1. STAGNANT PALLETS EVALUATOR - 10 hour threshold
    print("1. StagnantPalletsEvaluator: 10h threshold in RECEIVING")
    stagnant_time = now - timedelta(hours=11)  # 11 hours ago - triggers rule
    data.append({
        'pallet_id': 'STAG_001',
        'location': 'RECEIVING_01',
        'location_type': 'RECEIVING',
        'creation_date': stagnant_time.strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_SINGLE_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    # Control - safe record
    safe_time = now - timedelta(hours=9)  # 9 hours - safe
    data.append({
        'pallet_id': 'SAFE_001',
        'location': 'RECEIVING_02',
        'location_type': 'RECEIVING', 
        'creation_date': safe_time.strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_SINGLE_002',
        'description': 'STANDARD_PRODUCT'
    })
    
    # 2. UNCOORDINATED LOTS EVALUATOR - 80% completion threshold
    print("2. UncoordinatedLotsEvaluator: 80% completion threshold")
    lot_receipt = 'RCT_LOT_001'
    
    # 4 pallets in STORAGE (80% of 5-pallet lot)
    for i in range(4):
        data.append({
            'pallet_id': f'LOT_STORED_{i+1:03d}',
            'location': f'STORAGE_{i+1:02d}',
            'location_type': 'STORAGE',
            'creation_date': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': lot_receipt,
            'description': 'STANDARD_PRODUCT'
        })
    
    # 1 straggler in RECEIVING - triggers rule
    data.append({
        'pallet_id': 'LOT_STRAGGLER_001',
        'location': 'RECEIVING_03',
        'location_type': 'RECEIVING',
        'creation_date': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': lot_receipt,
        'description': 'STANDARD_PRODUCT'
    })
    
    # 3. INVALID LOCATION EVALUATOR
    print("3. VirtualInvalidLocationEvaluator: location validation")
    data.append({
        'pallet_id': 'INVALID_001',
        'location': 'CLEARLY_INVALID_LOC_999',
        'location_type': 'UNKNOWN',
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_INVALID_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    # 4. OVERCAPACITY EVALUATOR
    print("4. OvercapacityEvaluator: capacity violations")
    data.append({
        'pallet_id': 'OVER_001',
        'location': 'TINY_LOCATION_01',
        'location_type': 'STORAGE',
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_OVER_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    data.append({
        'pallet_id': 'OVER_002',
        'location': 'TINY_LOCATION_01',  # Same location - creates overcapacity
        'location_type': 'STORAGE',
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_OVER_002',
        'description': 'STANDARD_PRODUCT'
    })
    
    # 5. LOCATION SPECIFIC STAGNANT - AISLE pattern, 4 hour threshold
    print("5. LocationSpecificStagnantEvaluator: AISLE* pattern, 4h threshold")
    aisle_stagnant_time = now - timedelta(hours=5)  # 5 hours - exceeds 4h threshold
    data.append({
        'pallet_id': 'AISLE_STAG_001',
        'location': 'AISLE_A_01',
        'location_type': 'TRANSITIONAL',
        'creation_date': aisle_stagnant_time.strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_AISLE_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    # 6. DATA INTEGRITY EVALUATOR
    print("6. DataIntegrityEvaluator: duplicate and integrity checks")
    
    # Duplicate pallet ID
    duplicate_id = 'DUPLICATE_SCAN_001'
    data.append({
        'pallet_id': duplicate_id,
        'location': 'RECEIVING_04',
        'location_type': 'RECEIVING',
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_DUP_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    data.append({
        'pallet_id': duplicate_id,  # DUPLICATE - triggers rule
        'location': 'STORAGE_99',
        'location_type': 'STORAGE',
        'creation_date': (now - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_DUP_002',
        'description': 'STANDARD_PRODUCT'
    })
    
    # Impossible location
    data.append({
        'pallet_id': 'IMPOSSIBLE_001',
        'location': 'IMPOSSIBLY_LONG_LOCATION_CODE_INDICATING_SYSTEM_ERROR',
        'location_type': 'UNKNOWN',
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_IMPOSSIBLE_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    # 7. LOCATION MAPPING ERROR EVALUATOR
    print("7. LocationMappingErrorEvaluator: type consistency")
    data.append({
        'pallet_id': 'MAPPING_ERROR_001',
        'location': 'STORAGE_A_01_01',  # Clearly storage location
        'location_type': 'RECEIVING',    # But typed as receiving - inconsistency
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_MAPPING_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    # CONTROL RECORDS - Clean data
    print("CONTROL: Adding clean records")
    for i in range(5):
        data.append({
            'pallet_id': f'CLEAN_{i+1:03d}',
            'location': f'STORAGE_CLEAN_{i+1:02d}',
            'location_type': 'STORAGE',
            'creation_date': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': f'RCT_CLEAN_{i+1:03d}',
            'description': 'STANDARD_PRODUCT'
        })
    
    return data

def main():
    # Generate test data
    data = generate_precision_inventory()
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save files
    csv_file = 'precision_test_inventory.csv'
    excel_file = 'precision_test_inventory.xlsx'
    
    df.to_csv(csv_file, index=False)
    df.to_excel(excel_file, index=False, engine='openpyxl')
    
    # Summary
    print(f"\\nSUCCESS: Generated {len(data)} test records")
    print(f"Files created: {csv_file}, {excel_file}")
    print("\\nEXPECTED ANOMALIES:")
    print("- 1 x StagnantPalletsEvaluator (11h in RECEIVING)")
    print("- 1 x UncoordinatedLotsEvaluator (80% lot completion)")
    print("- 1 x VirtualInvalidLocationEvaluator (invalid format)")
    print("- 1 x OvercapacityEvaluator (2 pallets in 1-capacity location)")
    print("- 1 x LocationSpecificStagnantEvaluator (5h in AISLE*)")
    print("- 2 x DataIntegrityEvaluator (1 duplicate + 1 impossible location)")
    print("- 1 x LocationMappingErrorEvaluator (type mismatch)")
    print("\\nTotal expected anomalies: 8")
    print("\\nREQUIRED DATABASE SETUP:")
    print("- Create location 'TINY_LOCATION_01' with capacity=1")
    print("- Ensure AISLE_A_01 exists in location database")

if __name__ == "__main__":
    main()