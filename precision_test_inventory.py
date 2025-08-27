#!/usr/bin/env python3
"""
PRECISION TEST INVENTORY GENERATOR FOR WAREWISE SYSTEM
=====================================================

Creates surgical test data targeting each evaluator with precise thresholds
based on actual system behavior analysis from debug logs:
- 247 total anomalies: 195 overcapacity, 30 stagnant, 15 invalid, etc.

Each anomaly is designed to trigger exactly ONE evaluator's logic.
"""

import pandas as pd
from datetime import datetime, timedelta
import csv

def generate_precision_inventory():
    """Generate precision test data with surgical anomaly targeting"""
    
    data = []
    now = datetime.now()
    
    print("TARGET: GENERATING PRECISION TEST INVENTORY")
    print("=====================================")
    
    # ===================================================================
    # 1. STAGNANT PALLETS EVALUATOR - Time threshold logic
    # ===================================================================
    print("1. StagnantPalletsEvaluator: time_threshold_hours=10, location_types=['RECEIVING']")
    
    # ANOMALY: Exactly 11 hours in RECEIVING (triggers 10h threshold)
    stagnant_time = now - timedelta(hours=11)
    data.append({
        'pallet_id': 'STAG_001',
        'location': 'RECEIVING_01',
        'location_type': 'RECEIVING',
        'creation_date': stagnant_time.strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_SINGLE_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    # CONTROL: Exactly 9 hours in RECEIVING (safe - under threshold)
    safe_time = now - timedelta(hours=9)
    data.append({
        'pallet_id': 'SAFE_001',
        'location': 'RECEIVING_02', 
        'location_type': 'RECEIVING',
        'creation_date': safe_time.strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_SINGLE_002',
        'description': 'STANDARD_PRODUCT'
    })
    
    # ===================================================================
    # 2. UNCOORDINATED LOTS EVALUATOR - Completion threshold logic
    # ===================================================================  
    print("2. UncoordinatedLotsEvaluator: completion_threshold=0.8")
    
    # SETUP: 5-pallet lot with 4 in STORAGE (80% completion = threshold)
    lot_receipt = 'RCT_LOT_001'
    
    # 4 pallets in STORAGE (final location) - 80% completion
    for i in range(4):
        data.append({
            'pallet_id': f'LOT_STORED_{i+1:03d}',
            'location': f'STORAGE_{i+1:02d}',
            'location_type': 'STORAGE',
            'creation_date': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': lot_receipt,
            'description': 'STANDARD_PRODUCT'
        })
    
    # ANOMALY: 1 pallet still in RECEIVING (straggler - triggers rule)
    data.append({
        'pallet_id': 'LOT_STRAGGLER_001',
        'location': 'RECEIVING_03',
        'location_type': 'RECEIVING', 
        'creation_date': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': lot_receipt,
        'description': 'STANDARD_PRODUCT'
    })
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. VIRTUAL INVALID LOCATION EVALUATOR - Location validation
    # ═══════════════════════════════════════════════════════════════════
    print("3️⃣  VirtualInvalidLocationEvaluator: canonical location service")
    
    # ANOMALY: Clearly invalid location format
    data.append({
        'pallet_id': 'INVALID_001',
        'location': 'CLEARLY_INVALID_LOC_999',
        'location_type': 'UNKNOWN',
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_INVALID_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    # CONTROL: Valid location format (matches expected pattern)
    data.append({
        'pallet_id': 'VALID_001',
        'location': 'A01-02-03',  # Standard aisle-row-position format
        'location_type': 'STORAGE',
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_VALID_001', 
        'description': 'STANDARD_PRODUCT'
    })
    
    # ═══════════════════════════════════════════════════════════════════
    # 4. OVERCAPACITY EVALUATOR - Statistical analysis logic
    # ═══════════════════════════════════════════════════════════════════
    print("4️⃣  OvercapacityEvaluator: capacity limits with statistical analysis")
    
    # ANOMALY: Location with exactly 2 pallets (capacity=1, obvious violation)
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
    
    # CONTROL: Location with exactly 1 pallet (capacity=1, perfect fit)
    data.append({
        'pallet_id': 'PERFECT_001',
        'location': 'PERFECT_LOCATION_01',
        'location_type': 'STORAGE', 
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_PERFECT_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    # ═══════════════════════════════════════════════════════════════════
    # 5. LOCATION SPECIFIC STAGNANT EVALUATOR - Pattern matching logic
    # ═══════════════════════════════════════════════════════════════════
    print("5️⃣  LocationSpecificStagnantEvaluator: location_pattern='AISLE*', time_threshold_hours=4")
    
    # ANOMALY: 5 hours in AISLE location (exceeds 4h threshold)
    aisle_stagnant_time = now - timedelta(hours=5)
    data.append({
        'pallet_id': 'AISLE_STAG_001',
        'location': 'AISLE_A_01',  # Matches AISLE* pattern
        'location_type': 'TRANSITIONAL',
        'creation_date': aisle_stagnant_time.strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_AISLE_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    # CONTROL: 3 hours in AISLE location (safe - under threshold) 
    aisle_safe_time = now - timedelta(hours=3)
    data.append({
        'pallet_id': 'AISLE_SAFE_001',
        'location': 'AISLE_B_02',  # Matches AISLE* pattern
        'location_type': 'TRANSITIONAL',
        'creation_date': aisle_safe_time.strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_AISLE_002',
        'description': 'STANDARD_PRODUCT'
    })
    
    # ═══════════════════════════════════════════════════════════════════
    # 6. DATA INTEGRITY EVALUATOR - Duplicate detection logic
    # ═══════════════════════════════════════════════════════════════════
    print("6️⃣  DataIntegrityEvaluator: check_duplicate_scans=true")
    
    # ANOMALY: Duplicate pallet ID (triggers duplicate scan detection)
    duplicate_pallet_id = 'DUPLICATE_SCAN_001'
    data.append({
        'pallet_id': duplicate_pallet_id,
        'location': 'RECEIVING_04',
        'location_type': 'RECEIVING',
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_DUP_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    data.append({
        'pallet_id': duplicate_pallet_id,  # DUPLICATE - triggers anomaly
        'location': 'STORAGE_99', 
        'location_type': 'STORAGE',
        'creation_date': (now - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_DUP_002',
        'description': 'STANDARD_PRODUCT'
    })
    
    # ANOMALY: Impossible location (very long, triggers check_impossible_locations)
    data.append({
        'pallet_id': 'IMPOSSIBLE_001',
        'location': 'THIS_IS_AN_IMPOSSIBLY_LONG_LOCATION_CODE_THAT_CLEARLY_INDICATES_SYSTEM_ERROR_OR_CORRUPTION',
        'location_type': 'UNKNOWN',
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_IMPOSSIBLE_001', 
        'description': 'STANDARD_PRODUCT'
    })
    
    # ═══════════════════════════════════════════════════════════════════
    # 7. LOCATION MAPPING ERROR EVALUATOR - Pattern consistency
    # ═══════════════════════════════════════════════════════════════════
    print("7️⃣  LocationMappingErrorEvaluator: validate_location_types=true")
    
    # ANOMALY: Location type mismatch (location suggests storage, type says receiving)
    data.append({
        'pallet_id': 'MAPPING_ERROR_001',
        'location': 'STORAGE_A_01_01',  # Clearly storage location
        'location_type': 'RECEIVING',    # But typed as receiving - inconsistency
        'creation_date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'receipt_number': 'RCT_MAPPING_001',
        'description': 'STANDARD_PRODUCT'
    })
    
    # ═══════════════════════════════════════════════════════════════════
    # CONTROL RECORDS - Clean data to validate non-triggering behavior
    # ═══════════════════════════════════════════════════════════════════
    print("🔍 CONTROL RECORDS: Clean data for validation")
    
    # Perfect operational records (should trigger NO anomalies)
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

def create_location_setup():
    """Create necessary location records for capacity testing"""
    print("\n📍 REQUIRED LOCATION SETUP:")
    print("=" * 40)
    print("CREATE THESE LOCATIONS IN YOUR DATABASE:")
    print("- TINY_LOCATION_01 (capacity: 1) → For overcapacity test")
    print("- PERFECT_LOCATION_01 (capacity: 1) → For capacity control")
    print("- All STORAGE_CLEAN_XX locations (capacity: 10+)")
    print("=" * 40)

def main():
    """Generate and save precision test inventory"""
    
    # Generate test data
    data = generate_precision_inventory()
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save as CSV
    output_file = 'precision_test_inventory.csv'
    df.to_csv(output_file, index=False)
    
    # Save as Excel
    excel_file = 'precision_test_inventory.xlsx' 
    df.to_excel(excel_file, index=False)
    
    # Create location setup guide
    create_location_setup()
    
    # Summary report
    print(f"\n✅ PRECISION TEST INVENTORY GENERATED")
    print(f"====================================")
    print(f"📊 Total Records: {len(data)}")
    print(f"📁 CSV File: {output_file}")
    print(f"📁 Excel File: {excel_file}")
    print(f"\n🎯 EXPECTED ANOMALY TRIGGERS:")
    print(f"├── 1 × StagnantPalletsEvaluator (STAG_001: 11h in RECEIVING)")
    print(f"├── 1 × UncoordinatedLotsEvaluator (LOT_STRAGGLER_001: 80% lot completion)")
    print(f"├── 1 × VirtualInvalidLocationEvaluator (INVALID_001: bad format)")
    print(f"├── 1 × OvercapacityEvaluator (TINY_LOCATION_01: 2 pallets, capacity 1)")
    print(f"├── 1 × LocationSpecificStagnantEvaluator (AISLE_STAG_001: 5h in AISLE*)")
    print(f"├── 3 × DataIntegrityEvaluator (2 duplicates + 1 impossible location)")
    print(f"└── 1 × LocationMappingErrorEvaluator (MAPPING_ERROR_001: type mismatch)")
    print(f"\n📈 Total Expected Anomalies: 8")
    print(f"🔍 Control Records: {len([r for r in data if 'CLEAN' in r['pallet_id'] or 'SAFE' in r['pallet_id']])}")

if __name__ == "__main__":
    main()