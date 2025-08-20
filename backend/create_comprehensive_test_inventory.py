"""
COMPREHENSIVE RULE TESTING INVENTORY GENERATOR

Creates a strategic test inventory file designed to trigger all default rules
(except temperature rules) based on the USER_TESTF warehouse template.

Warehouse Template:
- 1 aisle × 1 rack × 55 positions × 4 levels (220 storage locations)
- Special areas: RECV-01(10), RECV-02(10), STAGE-01(5), DOCK-01(2), AISLE-01(10), AISLE-02(10)
- Location format: 01-01-001A through 01-01-055D

Strategic Anomalies to Test:
1. STAGNANT_PALLETS: Pallets stuck in receiving for various time periods
2. UNCOORDINATED_LOTS: Incomplete lot transfers with stragglers
3. OVERCAPACITY: Locations exceeding their capacity limits
4. INVALID_LOCATION: Pallets in non-existent or malformed locations
5. LOCATION_SPECIFIC_STAGNANT: Pallets stuck in aisles too long
6. DATA_INTEGRITY: Duplicate scans, bad characters, impossible locations
7. LOCATION_MAPPING_ERROR: Pattern inconsistencies and zone mismatches
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

def generate_comprehensive_test_inventory():
    """Generate comprehensive test inventory with strategic anomalies"""
    
    print("COMPREHENSIVE RULE TESTING INVENTORY GENERATOR")
    print("=" * 60)
    print("Creating strategic anomalies to test all default rules...")
    
    # Base timestamp for creating time-based anomalies
    now = datetime.now()
    
    inventory_data = []
    
    # =========================================================================
    # RULE 1: STAGNANT_PALLETS (Forgotten Pallets Alert)
    # Test pallets stuck in RECEIVING areas beyond threshold (10 hours)
    # =========================================================================
    print("Creating STAGNANT_PALLETS test cases...")
    
    stagnant_cases = [
        # Critical cases (>48h in receiving)
        {"pallet_id": "STAGNANT_CRITICAL_001", "location": "RECV-01", "hours_ago": 72, "lot": "LOT_STAGNANT_001"},
        {"pallet_id": "STAGNANT_CRITICAL_002", "location": "RECV-01", "hours_ago": 48, "lot": "LOT_STAGNANT_001"},
        {"pallet_id": "STAGNANT_CRITICAL_003", "location": "RECV-02", "hours_ago": 96, "lot": "LOT_STAGNANT_002"},
        
        # High priority cases (24-48h)
        {"pallet_id": "STAGNANT_HIGH_001", "location": "RECV-01", "hours_ago": 36, "lot": "LOT_STAGNANT_003"},
        {"pallet_id": "STAGNANT_HIGH_002", "location": "RECV-02", "hours_ago": 30, "lot": "LOT_STAGNANT_003"},
        
        # Medium priority cases (12-24h)
        {"pallet_id": "STAGNANT_MED_001", "location": "RECV-01", "hours_ago": 18, "lot": "LOT_STAGNANT_004"},
        {"pallet_id": "STAGNANT_MED_002", "location": "RECV-02", "hours_ago": 15, "lot": "LOT_STAGNANT_004"},
        
        # Boundary test (just over threshold)
        {"pallet_id": "STAGNANT_BOUNDARY", "location": "RECV-01", "hours_ago": 11, "lot": "LOT_STAGNANT_005"},
        
        # Good cases (under threshold - should not trigger)
        {"pallet_id": "GOOD_RECEIVING_001", "location": "RECV-01", "hours_ago": 8, "lot": "LOT_GOOD_001"},
        {"pallet_id": "GOOD_RECEIVING_002", "location": "RECV-02", "hours_ago": 5, "lot": "LOT_GOOD_001"},
    ]
    
    for case in stagnant_cases:
        creation_time = now - timedelta(hours=case["hours_ago"])
        inventory_data.append({
            "Pallet ID": case["pallet_id"],
            "Location": case["location"],
            "Description": f"Test item for stagnant detection ({case['hours_ago']}h old)",
            "Receipt Number": case["lot"],
            "Creation Date": creation_time,
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        })
    
    # =========================================================================
    # RULE 2: UNCOORDINATED_LOTS (Incomplete Lots Alert)  
    # Test lots with partial completion and stragglers
    # =========================================================================
    print("Creating UNCOORDINATED_LOTS test cases...")
    
    # Lot with 80% completion + stragglers (should trigger)
    lot_incomplete = "LOT_INCOMPLETE_001"
    
    # 4 pallets properly moved to storage (80% of 5 total)
    for i in range(1, 5):
        inventory_data.append({
            "Pallet ID": f"LOT_INCOMPLETE_MOVED_{i:03d}",
            "Location": f"01-01-{i:03d}A",
            "Description": f"Properly moved pallet {i}",
            "Receipt Number": lot_incomplete,
            "Creation Date": now - timedelta(hours=24),
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        })
    
    # 1 straggler left in receiving (should be detected)
    inventory_data.append({
        "Pallet ID": "LOT_INCOMPLETE_STRAGGLER",
        "Location": "RECV-01",
        "Description": "Straggler pallet left behind in receiving",
        "Receipt Number": lot_incomplete,
        "Creation Date": now - timedelta(hours=24),
        "Product Type": "GENERAL", 
        "Temperature Requirement": "AMBIENT"
    })
    
    # Lot with mixed completion (66% - should not trigger 80% threshold)
    lot_mixed = "LOT_MIXED_001"
    
    # 2 pallets moved to storage (66% of 3 total)
    for i in range(5, 7):
        inventory_data.append({
            "Pallet ID": f"LOT_MIXED_MOVED_{i:03d}",
            "Location": f"01-01-{i:03d}B",
            "Description": f"Mixed lot moved pallet {i}",
            "Receipt Number": lot_mixed,
            "Creation Date": now - timedelta(hours=12),
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        })
    
    # 1 pallet still in staging (normal - should not trigger)
    inventory_data.append({
        "Pallet ID": "LOT_MIXED_STAGING",
        "Location": "STAGE-01", 
        "Description": "Pallet in normal staging process",
        "Receipt Number": lot_mixed,
        "Creation Date": now - timedelta(hours=12),
        "Product Type": "GENERAL",
        "Temperature Requirement": "AMBIENT"
    })
    
    # =========================================================================
    # RULE 3: OVERCAPACITY (Overcapacity Alert)
    # Test locations exceeding their capacity limits
    # =========================================================================
    print("Creating OVERCAPACITY test cases...")
    
    # RECV-01 overcapacity (capacity=10, put 12 pallets)
    for i in range(1, 13):
        inventory_data.append({
            "Pallet ID": f"OVERCAP_RECV01_{i:03d}",
            "Location": "RECV-01",
            "Description": f"Receiving overcapacity pallet {i}",
            "Receipt Number": "LOT_OVERCAP_RECV",
            "Creation Date": now - timedelta(hours=2),
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        })
    
    # Storage location overcapacity (capacity=1, put 3 pallets)
    storage_overcap_location = "01-01-010A"
    for i in range(1, 4):
        inventory_data.append({
            "Pallet ID": f"OVERCAP_STORAGE_{i:03d}",
            "Location": storage_overcap_location,
            "Description": f"Storage overcapacity pallet {i}",
            "Receipt Number": "LOT_OVERCAP_STORAGE",
            "Creation Date": now - timedelta(hours=6),
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        })
    
    # STAGE-01 overcapacity (capacity=5, put 7 pallets) 
    for i in range(1, 8):
        inventory_data.append({
            "Pallet ID": f"OVERCAP_STAGE_{i:03d}",
            "Location": "STAGE-01",
            "Description": f"Staging overcapacity pallet {i}",
            "Receipt Number": "LOT_OVERCAP_STAGE",
            "Creation Date": now - timedelta(hours=4),
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        })
    
    # Normal capacity usage (should not trigger)
    inventory_data.append({
        "Pallet ID": "NORMAL_CAP_001",
        "Location": "01-01-015A",
        "Description": "Normal capacity usage",
        "Receipt Number": "LOT_NORMAL",
        "Creation Date": now - timedelta(hours=3),
        "Product Type": "GENERAL", 
        "Temperature Requirement": "AMBIENT"
    })
    
    # =========================================================================
    # RULE 4: INVALID_LOCATION (Invalid Locations Alert)
    # Test pallets in non-existent or malformed locations
    # =========================================================================
    print("Creating INVALID_LOCATION test cases...")
    
    invalid_location_cases = [
        # Completely invalid locations
        {"pallet_id": "INVALID_LOC_001", "location": "NONEXISTENT-999", "desc": "Completely invalid location"},
        {"pallet_id": "INVALID_LOC_002", "location": "BADFORMAT@#$", "desc": "Invalid characters in location"},
        {"pallet_id": "INVALID_LOC_003", "location": "ZONE-MISSING-001", "desc": "Non-existent zone"},
        
        # Out of range but valid format
        {"pallet_id": "INVALID_RANGE_001", "location": "01-01-999Z", "desc": "Out of range position"},
        {"pallet_id": "INVALID_RANGE_002", "location": "99-99-001A", "desc": "Out of range aisle/rack"},
        
        # Malformed but similar to valid
        {"pallet_id": "INVALID_FORMAT_001", "location": "1-1-1", "desc": "Missing level designation"},
        {"pallet_id": "INVALID_FORMAT_002", "location": "01-01-001", "desc": "Missing level letter"},
        
        # Edge case: empty/null location (pandas will handle as NaN)
        {"pallet_id": "INVALID_EMPTY_001", "location": "", "desc": "Empty location"},
        {"pallet_id": "INVALID_NULL_001", "location": None, "desc": "Null location"},
    ]
    
    for case in invalid_location_cases:
        inventory_data.append({
            "Pallet ID": case["pallet_id"],
            "Location": case["location"],
            "Description": case["desc"],
            "Receipt Number": "LOT_INVALID",
            "Creation Date": now - timedelta(hours=1),
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        })
    
    # =========================================================================
    # RULE 5: LOCATION_SPECIFIC_STAGNANT (AISLE Stuck Pallets)
    # Test pallets stuck in transitional areas (AISLE*) beyond threshold (4 hours)
    # =========================================================================
    print("Creating LOCATION_SPECIFIC_STAGNANT test cases...")
    
    aisle_stagnant_cases = [
        # Critical aisle stagnation (>24h)
        {"pallet_id": "AISLE_STUCK_001", "location": "AISLE-01", "hours_ago": 48, "desc": "Critical aisle stagnation"},
        {"pallet_id": "AISLE_STUCK_002", "location": "AISLE-02", "hours_ago": 36, "desc": "High aisle stagnation"},
        
        # Medium aisle stagnation (8-24h)
        {"pallet_id": "AISLE_STUCK_003", "location": "AISLE-01", "hours_ago": 12, "desc": "Medium aisle stagnation"},
        {"pallet_id": "AISLE_STUCK_004", "location": "AISLE-02", "hours_ago": 8, "desc": "Low aisle stagnation"},
        
        # Boundary test (just over threshold)
        {"pallet_id": "AISLE_BOUNDARY", "location": "AISLE-01", "hours_ago": 5, "desc": "Boundary aisle test"},
        
        # Normal aisle usage (under threshold - should not trigger)
        {"pallet_id": "AISLE_NORMAL_001", "location": "AISLE-01", "hours_ago": 2, "desc": "Normal aisle transit"},
        {"pallet_id": "AISLE_NORMAL_002", "location": "AISLE-02", "hours_ago": 1, "desc": "Quick aisle transit"},
    ]
    
    for case in aisle_stagnant_cases:
        creation_time = now - timedelta(hours=case["hours_ago"])
        inventory_data.append({
            "Pallet ID": case["pallet_id"],
            "Location": case["location"], 
            "Description": case["desc"],
            "Receipt Number": f"LOT_AISLE_{case['hours_ago']}H",
            "Creation Date": creation_time,
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        })
    
    # =========================================================================
    # RULE 7: DATA_INTEGRITY (Scanner Error Detection) 
    # Test duplicate scans, impossible locations, data quality issues
    # =========================================================================
    print("Creating DATA_INTEGRITY test cases...")
    
    # Duplicate scan detection
    duplicate_time = now - timedelta(minutes=30)
    inventory_data.extend([
        {
            "Pallet ID": "DUPLICATE_SCAN_001",
            "Location": "01-01-020A",
            "Description": "First scan of duplicate",
            "Receipt Number": "LOT_DUPLICATE",
            "Creation Date": duplicate_time,
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        },
        {
            "Pallet ID": "DUPLICATE_SCAN_001",  # Same pallet ID - should trigger duplicate detection
            "Location": "01-01-020B",           # Different location
            "Description": "Duplicate scan of same pallet",
            "Receipt Number": "LOT_DUPLICATE",
            "Creation Date": duplicate_time + timedelta(minutes=5),
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        }
    ])
    
    # Bad character detection
    inventory_data.append({
        "Pallet ID": "BAD_CHARS_001@#$%",  # Invalid characters in pallet ID
        "Location": "01-01-021A",
        "Description": "Pallet with bad characters in ID",
        "Receipt Number": "LOT_BAD_CHARS",
        "Creation Date": now - timedelta(minutes=15),
        "Product Type": "GENERAL",
        "Temperature Requirement": "AMBIENT"
    })
    
    # Extremely long pallet ID (testing length limits)
    inventory_data.append({
        "Pallet ID": "EXTREMELY_LONG_PALLET_ID_THAT_EXCEEDS_REASONABLE_LENGTH_LIMITS_AND_SHOULD_BE_FLAGGED_AS_SCANNER_ERROR_001",
        "Location": "01-01-022A",
        "Description": "Pallet with unreasonably long ID",
        "Receipt Number": "LOT_LONG_ID",
        "Creation Date": now - timedelta(minutes=10),
        "Product Type": "GENERAL", 
        "Temperature Requirement": "AMBIENT"
    })
    
    # =========================================================================
    # NORMAL OPERATIONS (Control Group)
    # Add normal, properly functioning inventory items
    # =========================================================================
    print("Creating normal operations control group...")
    
    # Normal storage operations
    normal_locations = [
        "01-01-025A", "01-01-025B", "01-01-025C", "01-01-025D",
        "01-01-030A", "01-01-030B", "01-01-035A", "01-01-035B",
        "01-01-040A", "01-01-040B", "01-01-045A", "01-01-045B"
    ]
    
    for i, location in enumerate(normal_locations, 1):
        inventory_data.append({
            "Pallet ID": f"NORMAL_OPS_{i:03d}",
            "Location": location,
            "Description": f"Normal warehouse operations item {i}",
            "Receipt Number": f"LOT_NORMAL_{(i-1)//4 + 1:03d}",  # Group into lots of 4
            "Creation Date": now - timedelta(hours=random.randint(1, 8)),
            "Product Type": random.choice(["GENERAL", "FOOD", "ELECTRONICS"]),
            "Temperature Requirement": "AMBIENT"
        })
    
    # Normal staging and dock operations
    staging_dock_operations = [
        {"pallet_id": "STAGE_NORMAL_001", "location": "STAGE-01", "hours_ago": 2},
        {"pallet_id": "STAGE_NORMAL_002", "location": "STAGE-01", "hours_ago": 1},
        {"pallet_id": "DOCK_NORMAL_001", "location": "DOCK-01", "hours_ago": 0.5},
        {"pallet_id": "DOCK_NORMAL_002", "location": "DOCK-01", "hours_ago": 0.25},
    ]
    
    for op in staging_dock_operations:
        creation_time = now - timedelta(hours=op["hours_ago"])
        inventory_data.append({
            "Pallet ID": op["pallet_id"],
            "Location": op["location"],
            "Description": "Normal staging/dock operations",
            "Receipt Number": "LOT_NORMAL_FLOW",
            "Creation Date": creation_time,
            "Product Type": "GENERAL",
            "Temperature Requirement": "AMBIENT"
        })
    
    # =========================================================================
    # GENERATE FINAL DATASET
    # =========================================================================
    print(f"\nGenerating final dataset with {len(inventory_data)} records...")
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Add some data variety
    df['Product Type'] = df['Product Type'].fillna('GENERAL')
    df['Temperature Requirement'] = df['Temperature Requirement'].fillna('AMBIENT')
    
    # Ensure proper datetime formatting
    df['Creation Date'] = pd.to_datetime(df['Creation Date'])
    
    # Summary statistics
    print(f"\nINVENTORY SUMMARY:")
    print(f"Total Records: {len(df)}")
    print(f"Unique Locations: {df['Location'].nunique()}")
    print(f"Unique Lots: {df['Receipt Number'].nunique()}")
    print(f"Date Range: {df['Creation Date'].min()} to {df['Creation Date'].max()}")
    
    # Location distribution
    print(f"\nLOCATION DISTRIBUTION:")
    location_counts = df['Location'].value_counts()
    for location, count in location_counts.head(10).items():
        print(f"  {location}: {count} pallets")
    if len(location_counts) > 10:
        print(f"  ... and {len(location_counts) - 10} more locations")
    
    # Expected anomaly counts by rule
    print(f"\nEXPECTED ANOMALY TRIGGERS:")
    print(f"  Rule 1 (Stagnant Pallets): ~8 anomalies (pallets >10h in receiving)")
    print(f"  Rule 2 (Incomplete Lots): ~1 anomaly (LOT_INCOMPLETE_001 straggler)")
    print(f"  Rule 3 (Overcapacity): ~22 anomalies (RECV-01: 12/10, Storage: 3/1, Stage: 7/5)")
    print(f"  Rule 4 (Invalid Locations): ~9 anomalies (various invalid formats)")
    print(f"  Rule 5 (Aisle Stagnant): ~5 anomalies (pallets >4h in aisles)")
    print(f"  Rule 7 (Data Integrity): ~3 anomalies (duplicates, bad chars, long IDs)")
    print(f"  Rule 8 (Location Mapping): ~0 anomalies (all locations follow valid patterns)")
    
    return df

def main():
    """Generate and save comprehensive test inventory"""
    
    # Generate the test inventory
    test_inventory = generate_comprehensive_test_inventory()
    
    # Save to Excel file
    output_path = r"C:\Users\juanb\Documents\Diego\Projects\ware2\comprehensive_rule_test_inventory.xlsx"
    
    print(f"\nSaving test inventory to: {output_path}")
    test_inventory.to_excel(output_path, index=False)
    
    print(f"\nSUCCESS: Comprehensive test inventory created!")
    print(f"File: {output_path}")
    print(f"Records: {len(test_inventory)}")
    print(f"\nThis inventory is designed to comprehensively test all default rules")
    print(f"and validate the rule engine's ability to detect warehouse anomalies.")
    
    return output_path

if __name__ == "__main__":
    main()