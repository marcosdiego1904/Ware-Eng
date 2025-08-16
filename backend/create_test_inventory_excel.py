#!/usr/bin/env python3
"""
Create comprehensive test inventory Excel file for warehouse rule testing.
"""
import pandas as pd
from datetime import datetime, timedelta
import os

def create_test_inventory():
    """Create comprehensive test inventory data"""
    
    # Base timestamp for calculations (current time - we'll subtract hours to create test scenarios)
    base_time = datetime.now()
    
    # Test data with intentional anomalies
    test_data = []
    
    # RULE 1 TEST: STAGNANT_PALLETS (10h threshold in RECEIVING)
    # These should trigger (>10 hours old)
    test_data.extend([
        {'pallet_id': 'STAGNANT001', 'location': 'RECV-01', 'creation_date': base_time - timedelta(hours=15), 'receipt_number': 'REC1001', 'description': 'Standard Product A', 'location_type': 'RECEIVING'},
        {'pallet_id': 'STAGNANT002', 'location': 'RECV-01', 'creation_date': base_time - timedelta(hours=14), 'receipt_number': 'REC1002', 'description': 'Standard Product B', 'location_type': 'RECEIVING'},
        {'pallet_id': 'STAGNANT003', 'location': 'RECV-01', 'creation_date': base_time - timedelta(hours=13), 'receipt_number': 'REC1003', 'description': 'Standard Product C', 'location_type': 'RECEIVING'},
        {'pallet_id': 'STAGNANT004', 'location': 'RECV-02', 'creation_date': base_time - timedelta(hours=16), 'receipt_number': 'REC1004', 'description': 'Standard Product D', 'location_type': 'RECEIVING'},
        {'pallet_id': 'STAGNANT005', 'location': 'RECV-02', 'creation_date': base_time - timedelta(hours=18), 'receipt_number': 'REC1005', 'description': 'Standard Product E', 'location_type': 'RECEIVING'},
    ])
    
    # Rule 1 - Should NOT trigger (under 10h)
    test_data.extend([
        {'pallet_id': 'NORMAL001', 'location': 'RECV-01', 'creation_date': base_time - timedelta(hours=8), 'receipt_number': 'REC2001', 'description': 'Normal Product F', 'location_type': 'RECEIVING'},
        {'pallet_id': 'NORMAL002', 'location': 'RECV-02', 'creation_date': base_time - timedelta(hours=7), 'receipt_number': 'REC2002', 'description': 'Normal Product G', 'location_type': 'RECEIVING'},
        {'pallet_id': 'NORMAL003', 'location': 'RECV-01', 'creation_date': base_time - timedelta(hours=6), 'receipt_number': 'REC2003', 'description': 'Normal Product H', 'location_type': 'RECEIVING'},
    ])
    
    # Rule 1 - Should NOT trigger (wrong location type)
    test_data.extend([
        {'pallet_id': 'FINAL001', 'location': '01-01-001-A', 'creation_date': base_time - timedelta(hours=20), 'receipt_number': 'REC3001', 'description': 'Final Product A', 'location_type': 'STORAGE'},
        {'pallet_id': 'FINAL002', 'location': '01-01-001-B', 'creation_date': base_time - timedelta(hours=25), 'receipt_number': 'REC3002', 'description': 'Final Product B', 'location_type': 'STORAGE'},
    ])
    
    # RULE 2 TEST: UNCOORDINATED_LOTS (80% completion threshold)
    # Lot REC4000 - 10 pallets total, 9 in final storage (90%), 1 straggler in receiving
    lot_time = base_time - timedelta(hours=12)
    test_data.extend([
        {'pallet_id': 'LOT001', 'location': '01-02-010-A', 'creation_date': lot_time, 'receipt_number': 'REC4000', 'description': 'Batch Product 1', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT002', 'location': '01-02-011-A', 'creation_date': lot_time, 'receipt_number': 'REC4000', 'description': 'Batch Product 2', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT003', 'location': '01-02-012-A', 'creation_date': lot_time, 'receipt_number': 'REC4000', 'description': 'Batch Product 3', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT004', 'location': '01-02-013-A', 'creation_date': lot_time, 'receipt_number': 'REC4000', 'description': 'Batch Product 4', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT005', 'location': '01-02-014-A', 'creation_date': lot_time, 'receipt_number': 'REC4000', 'description': 'Batch Product 5', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT006', 'location': '01-02-015-A', 'creation_date': lot_time, 'receipt_number': 'REC4000', 'description': 'Batch Product 6', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT007', 'location': '01-02-016-A', 'creation_date': lot_time, 'receipt_number': 'REC4000', 'description': 'Batch Product 7', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT008', 'location': '01-02-017-A', 'creation_date': lot_time, 'receipt_number': 'REC4000', 'description': 'Batch Product 8', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT009', 'location': '01-02-018-A', 'creation_date': lot_time, 'receipt_number': 'REC4000', 'description': 'Batch Product 9', 'location_type': 'STORAGE'},
        {'pallet_id': 'STRAGGLER001', 'location': 'RECV-01', 'creation_date': lot_time, 'receipt_number': 'REC4000', 'description': 'Batch Product 10 - Straggler', 'location_type': 'RECEIVING'},
    ])
    
    # Lot REC5000 - 5 pallets total, 3 in final storage (60%), should NOT trigger
    lot_time2 = base_time - timedelta(hours=10)
    test_data.extend([
        {'pallet_id': 'LOT011', 'location': '02-01-001-A', 'creation_date': lot_time2, 'receipt_number': 'REC5000', 'description': 'Batch Product 11', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT012', 'location': '02-01-002-A', 'creation_date': lot_time2, 'receipt_number': 'REC5000', 'description': 'Batch Product 12', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT013', 'location': '02-01-003-A', 'creation_date': lot_time2, 'receipt_number': 'REC5000', 'description': 'Batch Product 13', 'location_type': 'STORAGE'},
        {'pallet_id': 'LOT014', 'location': 'RECV-02', 'creation_date': lot_time2, 'receipt_number': 'REC5000', 'description': 'Batch Product 14', 'location_type': 'RECEIVING'},
        {'pallet_id': 'LOT015', 'location': 'RECV-02', 'creation_date': lot_time2, 'receipt_number': 'REC5000', 'description': 'Batch Product 15', 'location_type': 'RECEIVING'},
    ])
    
    # RULE 3 TEST: OVERCAPACITY
    # RECV-01 overcapacity (capacity 10) - add more pallets to existing ones
    over_time = base_time - timedelta(hours=5)
    test_data.extend([
        {'pallet_id': 'OVER001', 'location': 'RECV-01', 'creation_date': over_time, 'receipt_number': 'REC6001', 'description': 'Overcapacity Test 1', 'location_type': 'RECEIVING'},
        {'pallet_id': 'OVER002', 'location': 'RECV-01', 'creation_date': over_time, 'receipt_number': 'REC6002', 'description': 'Overcapacity Test 2', 'location_type': 'RECEIVING'},
        {'pallet_id': 'OVER003', 'location': 'RECV-01', 'creation_date': over_time, 'receipt_number': 'REC6003', 'description': 'Overcapacity Test 3', 'location_type': 'RECEIVING'},
        {'pallet_id': 'OVER004', 'location': 'RECV-01', 'creation_date': over_time, 'receipt_number': 'REC6004', 'description': 'Overcapacity Test 4', 'location_type': 'RECEIVING'},
        {'pallet_id': 'OVER005', 'location': 'RECV-01', 'creation_date': over_time, 'receipt_number': 'REC6005', 'description': 'Overcapacity Test 5', 'location_type': 'RECEIVING'},
    ])
    
    # Storage location overcapacity (assuming 2 pallet capacity)
    test_data.extend([
        {'pallet_id': 'OVER006', 'location': '03-01-001-A', 'creation_date': over_time, 'receipt_number': 'REC6006', 'description': 'Storage Overcapacity 1', 'location_type': 'STORAGE'},
        {'pallet_id': 'OVER007', 'location': '03-01-001-A', 'creation_date': over_time, 'receipt_number': 'REC6007', 'description': 'Storage Overcapacity 2', 'location_type': 'STORAGE'},
        {'pallet_id': 'OVER008', 'location': '03-01-001-A', 'creation_date': over_time, 'receipt_number': 'REC6008', 'description': 'Storage Overcapacity 3', 'location_type': 'STORAGE'},
        {'pallet_id': 'OVER009', 'location': '03-01-001-A', 'creation_date': over_time, 'receipt_number': 'REC6009', 'description': 'Storage Overcapacity 4', 'location_type': 'STORAGE'},
    ])
    
    # RULE 4 TEST: INVALID_LOCATION
    invalid_time = base_time - timedelta(hours=3)
    test_data.extend([
        {'pallet_id': 'INVALID001', 'location': 'BADLOC-99', 'creation_date': invalid_time, 'receipt_number': 'REC7001', 'description': 'Invalid Location Test 1', 'location_type': 'UNKNOWN'},
        {'pallet_id': 'INVALID002', 'location': 'UNDEFINED-X', 'creation_date': invalid_time, 'receipt_number': 'REC7002', 'description': 'Invalid Location Test 2', 'location_type': 'UNKNOWN'},
        {'pallet_id': 'INVALID003', 'location': 'MISTAKE-LOC', 'creation_date': invalid_time, 'receipt_number': 'REC7003', 'description': 'Invalid Location Test 3', 'location_type': 'UNKNOWN'},
    ])
    
    # RULE 5 TEST: AISLE_STUCK_PALLETS (4h threshold, AISLE* pattern)
    # Should trigger (>4 hours)
    aisle_time = base_time - timedelta(hours=6)
    test_data.extend([
        {'pallet_id': 'AISLE001', 'location': 'AISLE-NORTH', 'creation_date': aisle_time, 'receipt_number': 'REC8001', 'description': 'Aisle Stuck Test 1', 'location_type': 'TRANSITIONAL'},
        {'pallet_id': 'AISLE002', 'location': 'AISLE-SOUTH', 'creation_date': aisle_time - timedelta(hours=1), 'receipt_number': 'REC8002', 'description': 'Aisle Stuck Test 2', 'location_type': 'TRANSITIONAL'},
        {'pallet_id': 'AISLE003', 'location': 'AISLE-CENTRAL', 'creation_date': aisle_time - timedelta(hours=2), 'receipt_number': 'REC8003', 'description': 'Aisle Stuck Test 3', 'location_type': 'TRANSITIONAL'},
    ])
    
    # AISLE locations - should NOT trigger (under 4h)
    aisle_time_ok = base_time - timedelta(hours=2)
    test_data.extend([
        {'pallet_id': 'AISLE004', 'location': 'AISLE-EAST', 'creation_date': aisle_time_ok, 'receipt_number': 'REC8004', 'description': 'Aisle Normal Test 1', 'location_type': 'TRANSITIONAL'},
        {'pallet_id': 'AISLE005', 'location': 'AISLE-WEST', 'creation_date': aisle_time_ok + timedelta(hours=1), 'receipt_number': 'REC8005', 'description': 'Aisle Normal Test 2', 'location_type': 'TRANSITIONAL'},
    ])
    
    # RULE 7 TEST: DATA_INTEGRITY
    # Duplicate pallet IDs
    dup_time = base_time - timedelta(hours=4)
    test_data.extend([
        {'pallet_id': 'DUPLICATE001', 'location': '04-01-001-A', 'creation_date': dup_time, 'receipt_number': 'REC9001', 'description': 'Data Integrity Test 1', 'location_type': 'STORAGE'},
        {'pallet_id': 'DUPLICATE001', 'location': '04-01-002-A', 'creation_date': dup_time, 'receipt_number': 'REC9002', 'description': 'Data Integrity Test 1 Duplicate', 'location_type': 'STORAGE'},
    ])
    
    # Additional normal pallets for realistic dataset
    normal_time = base_time - timedelta(hours=2)
    test_data.extend([
        {'pallet_id': 'NORMAL004', 'location': '01-03-001-A', 'creation_date': normal_time, 'receipt_number': 'REC2004', 'description': 'Normal Product I', 'location_type': 'STORAGE'},
        {'pallet_id': 'NORMAL005', 'location': '01-03-002-B', 'creation_date': normal_time, 'receipt_number': 'REC2005', 'description': 'Normal Product J', 'location_type': 'STORAGE'},
        {'pallet_id': 'NORMAL006', 'location': '01-03-003-C', 'creation_date': normal_time, 'receipt_number': 'REC2006', 'description': 'Normal Product K', 'location_type': 'STORAGE'},
        {'pallet_id': 'NORMAL007', 'location': '02-02-001-A', 'creation_date': normal_time, 'receipt_number': 'REC2007', 'description': 'Normal Product L', 'location_type': 'STORAGE'},
        {'pallet_id': 'NORMAL008', 'location': '02-02-002-B', 'creation_date': normal_time, 'receipt_number': 'REC2008', 'description': 'Normal Product M', 'location_type': 'STORAGE'},
        {'pallet_id': 'NORMAL009', 'location': '02-02-003-C', 'creation_date': normal_time, 'receipt_number': 'REC2009', 'description': 'Normal Product N', 'location_type': 'STORAGE'},
        {'pallet_id': 'NORMAL010', 'location': '03-02-001-A', 'creation_date': normal_time, 'receipt_number': 'REC2010', 'description': 'Normal Product O', 'location_type': 'STORAGE'},
    ])
    
    # Staging area pallets
    stage_time = base_time - timedelta(hours=1)
    test_data.extend([
        {'pallet_id': 'STAGE001', 'location': 'STAGE-01', 'creation_date': stage_time, 'receipt_number': 'REC3010', 'description': 'Staging Product 1', 'location_type': 'STAGING'},
        {'pallet_id': 'STAGE002', 'location': 'STAGE-01', 'creation_date': stage_time, 'receipt_number': 'REC3011', 'description': 'Staging Product 2', 'location_type': 'STAGING'},
        {'pallet_id': 'STAGE003', 'location': 'STAGE-02', 'creation_date': stage_time, 'receipt_number': 'REC3012', 'description': 'Staging Product 3', 'location_type': 'STAGING'},
    ])
    
    # Dock area pallets  
    dock_time = base_time - timedelta(minutes=30)
    test_data.extend([
        {'pallet_id': 'DOCK001', 'location': 'DOCK-01', 'creation_date': dock_time, 'receipt_number': 'REC4010', 'description': 'Dock Product 1', 'location_type': 'DOCK'},
        {'pallet_id': 'DOCK002', 'location': 'DOCK-02', 'creation_date': dock_time, 'receipt_number': 'REC4011', 'description': 'Dock Product 2', 'location_type': 'DOCK'},
    ])
    
    return test_data

def main():
    """Create and save the test inventory Excel file"""
    
    print("Creating comprehensive test inventory dataset...")
    
    # Create test data
    test_data = create_test_inventory()
    
    # Convert to DataFrame
    df = pd.DataFrame(test_data)
    
    # Format creation_date properly
    df['creation_date'] = pd.to_datetime(df['creation_date'])
    
    # Save to Excel
    output_path = os.path.join(os.path.dirname(__file__), 'data', 'test_inventory_report.xlsx')
    df.to_excel(output_path, index=False, engine='openpyxl')
    
    print(f"[SUCCESS] Test inventory created: {output_path}")
    print(f"[INFO] Total pallets: {len(df)}")
    print(f"[INFO] Timestamp range: {df['creation_date'].min()} to {df['creation_date'].max()}")
    
    # Print expected anomalies summary
    print("\n[EXPECTED ANOMALIES]:")
    print("Rule 1 (STAGNANT_PALLETS): 5 anomalies (STAGNANT001-005)")
    print("Rule 2 (UNCOORDINATED_LOTS): 1 anomaly (STRAGGLER001 from lot REC4000)")
    print("Rule 3 (OVERCAPACITY): Multiple anomalies (RECV-01 and storage locations)")
    print("Rule 4 (INVALID_LOCATION): 3 anomalies (INVALID001-003)")
    print("Rule 5 (AISLE_STUCK_PALLETS): 3 anomalies (AISLE001-003)")
    print("Rule 7 (DATA_INTEGRITY): 1 anomaly (DUPLICATE001)")
    
    return output_path

if __name__ == "__main__":
    main()