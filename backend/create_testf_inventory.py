#!/usr/bin/env python3
"""
Create comprehensive test inventory for USER_TESTF warehouse
Based on new warehouse template: 1×1×58×4 structure
"""
import pandas as pd
from datetime import datetime, timedelta

def create_testf_test_inventory():
    """Create test inventory with intentional anomalies for USER_TESTF warehouse"""
    
    # Base timestamp
    now = datetime.now()
    
    inventory_data = []
    
    # === STAGNANT PALLETS IN RECEIVING (Rule 1 Test) ===
    # Critical delays (>72h)
    inventory_data.extend([
        ["TESTF_CRITICAL_001", "RECV-01", "Emergency pallet stuck 5 days", "LOT_TESTF_001", now - timedelta(days=5), "GENERAL", "AMBIENT"],
        ["TESTF_CRITICAL_002", "RECV-01", "Critical delay 4 days", "LOT_TESTF_001", now - timedelta(days=4), "GENERAL", "AMBIENT"],
        ["TESTF_CRITICAL_003", "RECV-01", "Major delay 3 days", "LOT_TESTF_001", now - timedelta(days=3), "GENERAL", "AMBIENT"],
    ])
    
    # High priority delays (24-72h)
    inventory_data.extend([
        ["TESTF_HIGH_001", "RECV-01", "High priority delayed 2 days", "LOT_TESTF_002", now - timedelta(days=2), "GENERAL", "AMBIENT"],
        ["TESTF_HIGH_002", "RECV-01", "High priority delayed 1.5 days", "LOT_TESTF_002", now - timedelta(hours=36), "GENERAL", "AMBIENT"],
    ])
    
    # Medium delays (12-24h)
    inventory_data.extend([
        ["TESTF_MEDIUM_001", "RECV-01", "Medium delay 20h", "LOT_TESTF_003", now - timedelta(hours=20), "GENERAL", "AMBIENT"],
        ["TESTF_BOUNDARY_001", "RECV-01", "Boundary test 11h", "LOT_TESTF_003", now - timedelta(hours=11), "GENERAL", "AMBIENT"],
    ])
    
    # === OVERCAPACITY ALERTS (Rule 3 Test) ===
    # RECV-01 overcapacity (capacity: 10, adding 11+ pallets)
    for i in range(1, 13):  # 12 pallets in 10-capacity location
        inventory_data.append([
            f"TESTF_OVERCAP_R1_{i:03d}", "RECV-01", f"Overcap test {i}", "LOT_OVERCAP_RECV", 
            now - timedelta(hours=1), "GENERAL", "AMBIENT"
        ])
    
    # RECV-02 normal usage (within capacity)
    for i in range(1, 4):  # 3 pallets in 10-capacity location
        inventory_data.append([
            f"TESTF_RECV2_{i:03d}", "RECV-02", "Normal receiving flow", "LOT_NORMAL_R2",
            now - timedelta(minutes=30), "GENERAL", "AMBIENT"
        ])
    
    # STAGE-01 overcapacity (capacity: 5, adding 7 pallets)
    for i in range(1, 8):  # 7 pallets in 5-capacity location
        inventory_data.append([
            f"TESTF_STAGE_OVERCAP_{i:03d}", "STAGE-01", f"Stage overcapacity {i}", "LOT_STAGE_OVER",
            now - timedelta(hours=2), "GENERAL", "AMBIENT"
        ])
    
    # === AISLE STUCK PALLETS (Rule 5 Test) ===
    # Pallets stuck in AISLE locations beyond 4-hour threshold
    aisle_stuck_data = [
        ["TESTF_AISLE_STUCK_001", "AISLE-01", "Aisle stuck 3 days", now - timedelta(days=3)],
        ["TESTF_AISLE_STUCK_002", "AISLE-01", "Aisle stuck 2 days", now - timedelta(days=2)],
        ["TESTF_AISLE_STUCK_003", "AISLE-02", "Aisle stuck 1 day", now - timedelta(days=1)],
        ["TESTF_AISLE_STUCK_004", "AISLE-02", "Aisle stuck 12h", now - timedelta(hours=12)],
        ["TESTF_AISLE_STUCK_005", "AISLE-01", "Aisle stuck 6h", now - timedelta(hours=6)],
    ]
    
    for pallet_id, location, desc, timestamp in aisle_stuck_data:
        inventory_data.append([
            pallet_id, location, desc, "LOT_AISLE_ISSUES", timestamp, "GENERAL", "AMBIENT"
        ])
    
    # === DOCK USAGE (Normal) ===
    inventory_data.extend([
        ["TESTF_DOCK_NORMAL_001", "DOCK-01", "Normal dock usage", "LOT_DOCK_NORMAL", now - timedelta(minutes=15), "GENERAL", "AMBIENT"],
        ["TESTF_DOCK_NORMAL_002", "DOCK-01", "Normal dock usage", "LOT_DOCK_NORMAL", now - timedelta(minutes=15), "GENERAL", "AMBIENT"],
    ])
    
    # === STORAGE LOCATIONS (Test warehouse structure) ===
    # Test different levels (A, B, C, D) at position 001
    storage_levels = [
        ["TESTF_STORAGE_001", "01-01-001A", "Storage level A"],
        ["TESTF_STORAGE_002", "01-01-001B", "Storage level B"],
        ["TESTF_STORAGE_003", "01-01-001C", "Storage level C"],
        ["TESTF_STORAGE_004", "01-01-001D", "Storage level D"],
    ]
    
    for pallet_id, location, desc in storage_levels:
        inventory_data.append([
            pallet_id, location, desc, "LOT_STORAGE_001", now - timedelta(hours=4), "GENERAL", "AMBIENT"
        ])
    
    # Test different positions across the 58-position range
    storage_positions = [
        ["TESTF_STORAGE_005", "01-01-002A", "Storage pos 2"],
        ["TESTF_STORAGE_006", "01-01-003A", "Storage pos 3"], 
        ["TESTF_STORAGE_007", "01-01-010A", "Storage pos 10"],
        ["TESTF_STORAGE_008", "01-01-020A", "Storage pos 20"],
        ["TESTF_STORAGE_009", "01-01-030A", "Storage pos 30"],
        ["TESTF_STORAGE_010", "01-01-040A", "Storage pos 40"],
        ["TESTF_STORAGE_011", "01-01-050A", "Storage pos 50"],
        ["TESTF_STORAGE_012", "01-01-058A", "Storage pos 58 (last)"],
    ]
    
    for pallet_id, location, desc in storage_positions:
        inventory_data.append([
            pallet_id, location, desc, "LOT_STORAGE_SPREAD", now - timedelta(hours=4), "GENERAL", "AMBIENT"
        ])
    
    # Storage location overcapacity (2 pallets in 1-capacity location)
    inventory_data.extend([
        ["TESTF_STORAGE_OVER_001", "01-01-005A", "Storage overcap test 1", "LOT_STORAGE_OVER", now - timedelta(hours=6), "GENERAL", "AMBIENT"],
        ["TESTF_STORAGE_OVER_002", "01-01-005A", "Storage overcap test 2", "LOT_STORAGE_OVER", now - timedelta(hours=6), "GENERAL", "AMBIENT"],
    ])
    
    # === INVALID LOCATIONS (Rule 4 Test) ===
    invalid_locations = [
        ["TESTF_INVALID_001", "INVALID-LOCATION-001", "Test invalid location"],
        ["TESTF_INVALID_002", "BADFORMAT@#$", "Test bad format"],
        ["TESTF_INVALID_003", "99-99-099Z", "Test out of range aisle"],
        ["TESTF_INVALID_004", "01-02-001A", "Test invalid rack (max: 1)"],
        ["TESTF_INVALID_005", "02-01-001A", "Test invalid aisle (max: 1)"],
        ["TESTF_INVALID_006", "01-01-059A", "Test beyond max position (max: 58)"],
        ["TESTF_INVALID_007", "01-01-001E", "Test invalid level (only A-D)"],
    ]
    
    for pallet_id, location, desc in invalid_locations:
        inventory_data.append([
            pallet_id, location, desc, "LOT_INVALID", now - timedelta(hours=8), "GENERAL", "AMBIENT"
        ])
    
    # === SCANNER ERRORS (Rule 7 Test) ===
    # Duplicate pallet ID in different locations
    inventory_data.extend([
        ["TESTF_DUPLICATE_001", "01-01-015A", "Duplicate scan test", "LOT_DUPLICATE", now - timedelta(hours=3), "GENERAL", "AMBIENT"],
        ["TESTF_DUPLICATE_001", "01-01-016A", "Duplicate pallet different location", "LOT_DUPLICATE", now - timedelta(hours=3), "GENERAL", "AMBIENT"],
    ])
    
    # === INCOMPLETE LOTS (Rule 2 Test) ===
    # 80% of lot in final storage, 1 straggler in receiving
    inventory_data.extend([
        ["TESTF_INCOMPLETE_STRAGGLER", "RECV-01", "Incomplete lot straggler", "LOT_INCOMPLETE_TEST", now - timedelta(hours=16), "GENERAL", "AMBIENT"],
        ["TESTF_INCOMPLETE_FINAL_001", "01-01-025A", "Incomplete lot in final", "LOT_INCOMPLETE_TEST", now - timedelta(hours=16), "GENERAL", "AMBIENT"],
        ["TESTF_INCOMPLETE_FINAL_002", "01-01-025B", "Incomplete lot in final", "LOT_INCOMPLETE_TEST", now - timedelta(hours=16), "GENERAL", "AMBIENT"],
        ["TESTF_INCOMPLETE_FINAL_003", "01-01-025C", "Incomplete lot in final", "LOT_INCOMPLETE_TEST", now - timedelta(hours=16), "GENERAL", "AMBIENT"],
        ["TESTF_INCOMPLETE_FINAL_004", "01-01-025D", "Incomplete lot in final", "LOT_INCOMPLETE_TEST", now - timedelta(hours=16), "GENERAL", "AMBIENT"],
    ])
    
    # === COLD CHAIN VIOLATIONS (Rule 6 Test) ===
    inventory_data.extend([
        ["TESTF_COLD_VIOLATION_001", "AISLE-01", "Frozen in ambient zone", "LOT_COLD_TEST", now - timedelta(hours=8), "FROZEN", "FROZEN"],
        ["TESTF_COLD_VIOLATION_002", "01-01-035A", "Refrigerated in ambient", "LOT_COLD_TEST", now - timedelta(hours=8), "REFRIGERATED", "REFRIGERATED"],
    ])
    
    # === NORMAL OPERATIONS (No violations) ===
    inventory_data.extend([
        ["TESTF_NORMAL_FLOW_001", "RECV-01", "Normal flow start", "LOT_NORMAL_FLOW", now - timedelta(minutes=45), "GENERAL", "AMBIENT"],
        ["TESTF_NORMAL_FLOW_002", "STAGE-01", "Normal flow stage", "LOT_NORMAL_FLOW", now - timedelta(minutes=15), "GENERAL", "AMBIENT"],
        ["TESTF_NORMAL_FLOW_003", "01-01-045A", "Normal flow final", "LOT_NORMAL_FLOW", now, "GENERAL", "AMBIENT"],
    ])
    
    # === EDGE CASES ===
    edge_cases = [
        ["TESTF_EDGE_CASE_001", "01-01-001F", "Level beyond ABCD", "LOT_EDGE_CASES"],
        ["TESTF_EDGE_CASE_002", "00-01-001A", "Zero aisle test", "LOT_EDGE_CASES"],
        ["TESTF_EDGE_CASE_003", "01-00-001A", "Zero rack test", "LOT_EDGE_CASES"],
        ["TESTF_EDGE_CASE_004", "01-01-000A", "Zero position test", "LOT_EDGE_CASES"],
    ]
    
    for pallet_id, location, desc, lot in edge_cases:
        inventory_data.append([
            pallet_id, location, desc, lot, now - timedelta(hours=2), "GENERAL", "AMBIENT"
        ])
    
    # Create DataFrame
    columns = ['Pallet ID', 'Location', 'Description', 'Receipt Number', 'Creation Date', 'Product Type', 'Temperature Requirement']
    df = pd.DataFrame(inventory_data, columns=columns)
    
    # Save to Excel
    output_file = 'testf_warehouse_test_inventory.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"[SUCCESS] Created test inventory: {output_file}")
    print(f"[DATA] Total records: {len(df)}")
    print(f"[DATA] Unique locations: {df['Location'].nunique()}")
    print(f"[DATA] Lots included: {df['Receipt Number'].nunique()}")
    
    # Summary of intentional anomalies
    print(f"\n[ANOMALIES] INTENTIONAL ANOMALIES FOR RULE TESTING:")
    print(f"   • Stagnant pallets in RECEIVING: {len([x for x in inventory_data if 'RECV-01' in x[1] and any(t in x[0] for t in ['CRITICAL', 'HIGH', 'MEDIUM', 'BOUNDARY'])])}")
    print(f"   • Overcapacity violations: RECV-01 (12/10), STAGE-01 (7/5), Storage (2/1)")
    print(f"   • Aisle stuck pallets: 5 pallets beyond 4h threshold")
    print(f"   • Invalid locations: 7 different invalid format tests")
    print(f"   • Scanner errors: 1 duplicate pallet ID")
    print(f"   • Incomplete lots: 1 straggler in 5-pallet lot")
    print(f"   • Cold chain violations: 2 pallets in wrong temperature zones")
    print(f"   • Edge cases: 4 boundary condition tests")
    
    return df

if __name__ == "__main__":
    create_testf_test_inventory()