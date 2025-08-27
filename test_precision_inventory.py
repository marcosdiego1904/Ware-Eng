#!/usr/bin/env python3
"""
PRECISION INVENTORY TEST RUNNER
Tests the precision inventory against WareWise system
"""

import pandas as pd
import requests
import os
import json
import time

def test_precision_inventory():
    """Test the precision inventory file against the system"""
    
    print("TESTING PRECISION INVENTORY AGAINST WAREWISE")
    print("============================================")
    
    # Check if files exist
    csv_file = 'precision_test_inventory.csv'
    excel_file = 'precision_test_inventory.xlsx'
    
    if not os.path.exists(csv_file):
        print(f"ERROR: {csv_file} not found. Run precision_test_inventory_simple.py first.")
        return
    
    # Read the test data
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} test records from {csv_file}")
    
    # Display summary
    print("\\nTEST DATA SUMMARY:")
    print("==================")
    
    anomaly_targets = [
        "STAG_001 (11h in RECEIVING - should trigger StagnantPalletsEvaluator)",
        "LOT_STRAGGLER_001 (80% lot complete - should trigger UncoordinatedLotsEvaluator)", 
        "INVALID_001 (invalid location - should trigger VirtualInvalidLocationEvaluator)",
        "OVER_001 & OVER_002 (2 pallets in capacity-1 location - should trigger OvercapacityEvaluator)",
        "AISLE_STAG_001 (5h in AISLE* - should trigger LocationSpecificStagnantEvaluator)",
        "DUPLICATE_SCAN_001 (duplicate pallet - should trigger DataIntegrityEvaluator)",
        "IMPOSSIBLE_001 (impossible location - should trigger DataIntegrityEvaluator)",
        "MAPPING_ERROR_001 (type mismatch - should trigger LocationMappingErrorEvaluator)"
    ]
    
    print("Expected Anomalies:")
    for i, target in enumerate(anomaly_targets, 1):
        print(f"  {i}. {target}")
    
    # Control records that should NOT trigger
    control_records = df[df['pallet_id'].str.contains('CLEAN|SAFE')]['pallet_id'].tolist()
    print(f"\\nControl Records (should NOT trigger): {len(control_records)}")
    for record in control_records[:3]:  # Show first 3
        print(f"  - {record}")
    if len(control_records) > 3:
        print(f"  ... and {len(control_records) - 3} more")
    
    print(f"\\nEXPECTED RESULT: 8 total anomalies detected")
    print(f"File ready for testing: {csv_file}")
    print(f"Excel version: {excel_file}")
    
    # Show sample records for verification
    print("\\nSAMPLE RECORDS FOR VERIFICATION:")
    print("=================================")
    
    # Show the stagnant pallet record
    stagnant = df[df['pallet_id'] == 'STAG_001'].iloc[0]
    print(f"Stagnant Test Record:")
    print(f"  Pallet: {stagnant['pallet_id']}")
    print(f"  Location: {stagnant['location']} ({stagnant['location_type']})")
    print(f"  Created: {stagnant['creation_date']} (should be ~11h ago)")
    
    # Show the overcapacity records
    over_records = df[df['location'] == 'TINY_LOCATION_01']
    print(f"\\nOvercapacity Test Records ({len(over_records)} pallets in TINY_LOCATION_01):")
    for _, record in over_records.iterrows():
        print(f"  Pallet: {record['pallet_id']} in {record['location']}")
    print(f"  NOTE: TINY_LOCATION_01 must have capacity=1 in database!")
    
    # Show the duplicate record
    duplicates = df[df['pallet_id'] == 'DUPLICATE_SCAN_001']
    print(f"\\nDuplicate Test Records ({len(duplicates)} records with same pallet_id):")
    for _, record in duplicates.iterrows():
        print(f"  Pallet: {record['pallet_id']} in {record['location']}")
    
    print(f"\\n" + "="*60)
    print(f"READY FOR TESTING")
    print(f"Upload {csv_file} to WareWise system to validate evaluator behavior")
    print(f"Expected: 8 anomalies total from surgical targeting")
    print(f"="*60)

def analyze_test_results(expected_anomalies=8):
    """Helper function to analyze test results after running"""
    print(f"\\nANALYZING TEST RESULTS")
    print(f"======================")
    print(f"Expected anomalies: {expected_anomalies}")
    print(f"\\nIf you see different numbers, check:")
    print(f"1. TINY_LOCATION_01 exists with capacity=1")
    print(f"2. Time thresholds match evaluator configuration")
    print(f"3. Location patterns are recognized")
    print(f"4. All rule types are active")

if __name__ == "__main__":
    test_precision_inventory()
    analyze_test_results()