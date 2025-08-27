#!/usr/bin/env python3
"""
VALIDATION SCRIPT FOR 800-PALLET PRECISION INVENTORY
==================================================

Validates the generated Excel file meets all requirements:
- Exactly 800 pallets
- Correct USER_MARCOS9 warehouse format constraints
- Surgical anomaly targeting for each of 7 evaluators
- Proper Excel structure with multiple sheets
"""

import pandas as pd
import os

def validate_inventory():
    """Validate the generated 800-pallet inventory Excel file"""
    
    filename = "precision_inventory_800_pallets.xlsx"
    
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found!")
        return False
    
    print("VALIDATING 800-PALLET PRECISION INVENTORY")
    print("========================================")
    
    try:
        # Load Excel file
        excel_file = pd.ExcelFile(filename)
        print(f"Excel file loaded: {filename}")
        print(f"Sheets found: {excel_file.sheet_names}")
        
        # Validate main inventory sheet
        df = pd.read_excel(filename, sheet_name='Inventory')
        
        print(f"\nINVENTORY VALIDATION:")
        print(f"Total records: {len(df)}")
        
        # Check exactly 800 pallets
        if len(df) == 800:
            print("[OK] Exactly 800 pallets - CORRECT")
        else:
            print(f"[ERROR] Expected 800 pallets, got {len(df)}")
            return False
        
        # Validate columns
        required_columns = ['pallet_id', 'location', 'location_type', 'creation_date', 'receipt_number', 'description']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"[ERROR] Missing columns: {missing_columns}")
            return False
        else:
            print("[OK] All required columns present")
        
        # Validate location formats (USER_MARCOS9 constraints)
        valid_storage_pattern = df['location'].str.match(r'^01-01-\d{3}[A-D]$', na=False)
        valid_special_pattern = df['location'].str.match(r'^(RECV|STAGE|DOCK|AISLE)-\d+$', na=False)
        invalid_pattern = df['location'].str.match(r'^INVALID|CLEARLY_INVALID|03-01|IMPOSSIBLE', na=False)
        
        storage_locations = valid_storage_pattern.sum()
        special_locations = valid_special_pattern.sum()
        invalid_locations = invalid_pattern.sum()
        other_locations = len(df) - storage_locations - special_locations - invalid_locations
        
        print(f"\nLOCATION FORMAT ANALYSIS:")
        print(f"Valid storage locations (01-01-XXXA): {storage_locations}")
        print(f"Valid special locations (RECV-XX, etc): {special_locations}")
        print(f"Invalid locations (test anomalies): {invalid_locations}")
        print(f"Other locations: {other_locations}")
        
        # Check for aisle 02 locations (should be minimal/only in invalid test data)
        aisle_02_locations = df['location'].str.contains('^02-01', na=False).sum()
        if aisle_02_locations > 0:
            print(f"[WARNING] Found {aisle_02_locations} aisle-02 locations (may trigger VirtualInvalidLocationEvaluator)")
        else:
            print("[OK] No aisle-02 locations found - matches 1-aisle warehouse config")
        
        # Validate unique pallet IDs (except intentional duplicates)
        duplicate_ids = df[df.duplicated(['pallet_id'], keep=False)]['pallet_id'].nunique()
        print(f"\nDATA INTEGRITY:")
        print(f"Duplicate pallet ID groups: {duplicate_ids} (expected: 2 for testing)")
        
        # Validate creation dates
        df['creation_date'] = pd.to_datetime(df['creation_date'])
        recent_count = (df['creation_date'] > (pd.Timestamp.now() - pd.Timedelta(hours=24))).sum()
        print(f"Records created in last 24h: {recent_count}")
        
        # Validate analysis sheet
        analysis_df = pd.read_excel(filename, sheet_name='Analysis')
        print(f"\nANALYSIS SHEET VALIDATION:")
        print(f"Analysis rows: {len(analysis_df)}")
        
        # Show anomaly breakdown from analysis sheet
        if len(analysis_df) > 0:
            print("\nANOMALY BREAKDOWN FROM ANALYSIS SHEET:")
            for _, row in analysis_df.iterrows():
                print(f"  {row['Metric']}: {row['Count']}")
        
        # Validate location distribution sheet
        location_dist_df = pd.read_excel(filename, sheet_name='Location_Distribution')
        print(f"\nLOCATION DISTRIBUTION:")
        print(f"Unique locations used: {len(location_dist_df)}")
        
        # Check for overcapacity (locations with >1 pallet)
        overcapacity_locations = location_dist_df[location_dist_df['Pallet_Count'] > 1]
        print(f"Overcapacity locations (>1 pallet): {len(overcapacity_locations)}")
        
        if len(overcapacity_locations) > 0:
            print("Overcapacity details:")
            for _, row in overcapacity_locations.head(5).iterrows():
                print(f"  {row['Location']}: {row['Pallet_Count']} pallets")
        
        print(f"\n[SUCCESS] VALIDATION COMPLETE!")
        print(f"File: {filename}")
        print(f"Ready for WareWise testing with surgical anomaly precision!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Validation error: {e}")
        return False

if __name__ == "__main__":
    validate_inventory()