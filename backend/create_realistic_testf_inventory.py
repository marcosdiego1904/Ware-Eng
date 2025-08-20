#!/usr/bin/env python3
"""
Create realistic test inventory for USER_TESTF warehouse
With minimal but strategic overcapacity violations (only 2)
"""
import pandas as pd
from datetime import datetime, timedelta

def create_realistic_testf_inventory():
    """Create realistic test inventory with minimal overcapacity for USER_TESTF warehouse"""
    
    # Base timestamp
    now = datetime.now()
    
    inventory_data = []
    
    # === STAGNANT PALLETS IN RECEIVING (Rule 1 Test) ===
    # Just a few critical delays
    inventory_data.extend([
        ["TESTF_CRITICAL_001", "RECV-01", "Emergency pallet stuck 4 days", "LOT_TESTF_001", now - timedelta(days=4), "GENERAL", "AMBIENT"],
        ["TESTF_HIGH_001", "RECV-01", "High priority delayed 2 days", "LOT_TESTF_002", now - timedelta(days=2), "GENERAL", "AMBIENT"],
        ["TESTF_MEDIUM_001", "RECV-01", "Medium delay 15h", "LOT_TESTF_003", now - timedelta(hours=15), "GENERAL", "AMBIENT"],
    ])
    
    # === STRATEGIC OVERCAPACITY VIOLATIONS (Rule 3 Test) - ONLY 2 ===
    
    # 1. RECV-01 moderate overcapacity (capacity: 10, adding 12 pallets = 2 excess)
    for i in range(1, 13):  # 12 pallets in 10-capacity location
        inventory_data.append([
            f"TESTF_RECV_OVER_{i:03d}", "RECV-01", f"Receiving overcap {i}", "LOT_RECV_BUSY", 
            now - timedelta(hours=2), "GENERAL", "AMBIENT"
        ])
    
    # 2. Single storage location with double occupancy (capacity: 1, adding 2 pallets = 1 excess)
    inventory_data.extend([
        ["TESTF_STORAGE_OVER_001", "01-01-025A", "Storage double occupancy 1", "LOT_STORAGE_OVER", now - timedelta(hours=6), "GENERAL", "AMBIENT"],
        ["TESTF_STORAGE_OVER_002", "01-01-025A", "Storage double occupancy 2", "LOT_STORAGE_OVER", now - timedelta(hours=6), "GENERAL", "AMBIENT"],
    ])
    
    # === NORMAL RECEIVING OPERATIONS ===
    # RECV-02 normal usage (within capacity)
    for i in range(1, 8):  # 7 pallets in 10-capacity location (normal)
        inventory_data.append([
            f"TESTF_RECV2_{i:03d}", "RECV-02", "Normal receiving flow", "LOT_NORMAL_R2",
            now - timedelta(minutes=30), "GENERAL", "AMBIENT"
        ])
    
    # === STAGING OPERATIONS (Normal) ===
    for i in range(1, 4):  # 3 pallets in 5-capacity location (normal)
        inventory_data.append([
            f"TESTF_STAGE_{i:03d}", "STAGE-01", "Normal staging flow", "LOT_STAGING_NORMAL",
            now - timedelta(hours=1), "GENERAL", "AMBIENT"
        ])
    
    # === AISLE STUCK PALLETS (Rule 5 Test) ===
    # Just a couple stuck pallets
    aisle_stuck_data = [
        ["TESTF_AISLE_STUCK_001", "AISLE-01", "Aisle stuck 2 days", now - timedelta(days=2)],
        ["TESTF_AISLE_STUCK_002", "AISLE-02", "Aisle stuck 8h", now - timedelta(hours=8)],
    ]
    
    for pallet_id, location, desc, timestamp in aisle_stuck_data:
        inventory_data.append([
            pallet_id, location, desc, "LOT_AISLE_ISSUES", timestamp, "GENERAL", "AMBIENT"
        ])
    
    # === DOCK USAGE (Normal) ===
    inventory_data.extend([
        ["TESTF_DOCK_001", "DOCK-01", "Normal dock usage", "LOT_DOCK_NORMAL", now - timedelta(minutes=15), "GENERAL", "AMBIENT"],
    ])
    
    # === STORAGE LOCATIONS (Normal operations) ===
    # Test different levels (A, B, C, D) at various positions
    storage_normal = [
        ["TESTF_STORAGE_001", "01-01-001A", "Storage level A"],
        ["TESTF_STORAGE_002", "01-01-001B", "Storage level B"],
        ["TESTF_STORAGE_003", "01-01-002A", "Storage pos 2"],
        ["TESTF_STORAGE_004", "01-01-010A", "Storage pos 10"],
        ["TESTF_STORAGE_005", "01-01-020A", "Storage pos 20"],
        ["TESTF_STORAGE_006", "01-01-030A", "Storage pos 30"],
        ["TESTF_STORAGE_007", "01-01-040A", "Storage pos 40"],
        ["TESTF_STORAGE_008", "01-01-050A", "Storage pos 50"],
        ["TESTF_STORAGE_009", "01-01-058A", "Storage pos 58 (last)"],
    ]
    
    for pallet_id, location, desc in storage_normal:
        inventory_data.append([
            pallet_id, location, desc, "LOT_STORAGE_NORMAL", now - timedelta(hours=4), "GENERAL", "AMBIENT"
        ])
    
    # === INVALID LOCATIONS (Rule 4 Test) - Just a few critical ones ===
    invalid_locations = [
        ["TESTF_INVALID_001", "INVALID-LOCATION-001", "Test invalid location"],
        ["TESTF_INVALID_002", "99-99-099Z", "Test out of range aisle"],
        ["TESTF_INVALID_003", "01-01-001E", "Test invalid level (only A-D)"],
    ]
    
    for pallet_id, location, desc in invalid_locations:
        inventory_data.append([
            pallet_id, location, desc, "LOT_INVALID", now - timedelta(hours=8), "GENERAL", "AMBIENT"
        ])
    
    # === SCANNER ERRORS (Rule 7 Test) ===
    # Single duplicate pallet ID
    inventory_data.extend([
        ["TESTF_DUPLICATE_001", "01-01-015A", "Duplicate scan test", "LOT_DUPLICATE", now - timedelta(hours=3), "GENERAL", "AMBIENT"],
        ["TESTF_DUPLICATE_001", "01-01-016A", "Same pallet, different location", "LOT_DUPLICATE", now - timedelta(hours=3), "GENERAL", "AMBIENT"],
    ])
    
    # === INCOMPLETE LOTS (Rule 2 Test) ===
    # 80% of lot in final storage, 1 straggler in receiving
    inventory_data.extend([
        ["TESTF_INCOMPLETE_STRAGGLER", "RECV-01", "Lot straggler", "LOT_INCOMPLETE_TEST", now - timedelta(hours=16), "GENERAL", "AMBIENT"],
        ["TESTF_INCOMPLETE_FINAL_001", "01-01-035A", "Lot in final storage 1", "LOT_INCOMPLETE_TEST", now - timedelta(hours=16), "GENERAL", "AMBIENT"],
        ["TESTF_INCOMPLETE_FINAL_002", "01-01-035B", "Lot in final storage 2", "LOT_INCOMPLETE_TEST", now - timedelta(hours=16), "GENERAL", "AMBIENT"],
        ["TESTF_INCOMPLETE_FINAL_003", "01-01-035C", "Lot in final storage 3", "LOT_INCOMPLETE_TEST", now - timedelta(hours=16), "GENERAL", "AMBIENT"],
        ["TESTF_INCOMPLETE_FINAL_004", "01-01-035D", "Lot in final storage 4", "LOT_INCOMPLETE_TEST", now - timedelta(hours=16), "GENERAL", "AMBIENT"],
    ])
    
    # === NORMAL OPERATIONS (Healthy workflow) ===
    inventory_data.extend([
        ["TESTF_NORMAL_FLOW_001", "RECV-02", "Normal flow start", "LOT_NORMAL_FLOW", now - timedelta(minutes=45), "GENERAL", "AMBIENT"],
        ["TESTF_NORMAL_FLOW_002", "STAGE-01", "Normal flow stage", "LOT_NORMAL_FLOW", now - timedelta(minutes=15), "GENERAL", "AMBIENT"],
        ["TESTF_NORMAL_FLOW_003", "01-01-045A", "Normal flow final", "LOT_NORMAL_FLOW", now, "GENERAL", "AMBIENT"],
    ])
    
    # Create DataFrame
    columns = ['Pallet ID', 'Location', 'Description', 'Receipt Number', 'Creation Date', 'Product Type', 'Temperature Requirement']
    df = pd.DataFrame(inventory_data, columns=columns)
    
    # Save to Excel
    output_file = 'realistic_testf_inventory.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"[SUCCESS] Created realistic test inventory: {output_file}")
    print(f"[DATA] Total records: {len(df)}")
    print(f"[DATA] Unique locations: {df['Location'].nunique()}")
    print(f"[DATA] Lots included: {df['Receipt Number'].nunique()}")
    
    # Summary of intentional anomalies
    print(f"\n[ANOMALIES] STRATEGIC ANOMALIES FOR TESTING:")
    print(f"   • Stagnant pallets in RECEIVING: 3 (critical, high, medium)")
    print(f"   • Overcapacity violations: ONLY 2 locations")
    print(f"     - RECV-01: 15 pallets / 10 capacity (moderate)")
    print(f"     - 01-01-025A: 2 pallets / 1 capacity (double occupancy)")
    print(f"   • Aisle stuck pallets: 2 pallets beyond 4h threshold")
    print(f"   • Invalid locations: 3 different format tests")
    print(f"   • Scanner errors: 1 duplicate pallet ID")
    print(f"   • Incomplete lots: 1 straggler in 5-pallet lot")
    print(f"   • Normal operations: {len([x for x in inventory_data if 'NORMAL' in x[3]])} pallets in healthy workflow")
    
    return df

if __name__ == "__main__":
    create_realistic_testf_inventory()