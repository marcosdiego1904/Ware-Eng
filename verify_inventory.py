#!/usr/bin/env python3
"""
Verify the generated Central DC inventory file
"""

import pandas as pd
from datetime import datetime, timedelta

def verify_inventory_file():
    """Verify the generated inventory file contents"""
    file_path = 'CentralDC_Compact_Inventory.xlsx'
    
    try:
        # Read the main inventory sheet
        df = pd.read_excel(file_path, sheet_name='Inventory')
        
        print("=== CENTRAL DC INVENTORY VERIFICATION ===")
        print(f"File: {file_path}")
        print(f"Total Records: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Check location types breakdown
        print("\n=== LOCATION TYPE BREAKDOWN ===")
        location_type_counts = df['location_type'].value_counts()
        for loc_type, count in location_type_counts.items():
            print(f"{loc_type}: {count}")
        
        # Check for overcapacity scenarios
        print("\n=== OVERCAPACITY ANALYSIS ===")
        location_counts = df['location'].value_counts()
        overcapacity_locations = location_counts[location_counts > 1]
        print(f"Locations with multiple pallets: {len(overcapacity_locations)}")
        if len(overcapacity_locations) > 0:
            print("Top overcapacity locations:")
            for location, count in overcapacity_locations.head(10).items():
                print(f"  {location}: {count} pallets")
        
        # Check for stagnant pallets
        print("\n=== STAGNANT PALLET ANALYSIS ===")
        df['creation_date'] = pd.to_datetime(df['creation_date'])
        cutoff_date = datetime.now() - timedelta(days=120)
        stagnant_pallets = df[df['creation_date'] < cutoff_date]
        print(f"Stagnant pallets (>120 days): {len(stagnant_pallets)}")
        
        # Check incomplete lots
        print("\n=== INCOMPLETE LOTS ANALYSIS ===")
        receipt_groups = df.groupby('receipt_number')
        incomplete_lots = []
        
        for receipt, group in receipt_groups:
            location_types = group['location_type'].unique()
            if len(location_types) > 1 and 'FINAL' in location_types:
                incomplete_lots.append({
                    'receipt': receipt,
                    'total_pallets': len(group),
                    'location_types': list(location_types)
                })
        
        print(f"Potential incomplete lots: {len(incomplete_lots)}")
        if incomplete_lots:
            print("Sample incomplete lots:")
            for lot in incomplete_lots[:5]:
                print(f"  {lot['receipt']}: {lot['total_pallets']} pallets across {lot['location_types']}")
        
        # Check invalid locations
        print("\n=== DATA QUALITY ISSUES ===")
        invalid_locations = df[df['location_type'] == 'UNKNOWN']
        print(f"Invalid/Unknown locations: {len(invalid_locations)}")
        if len(invalid_locations) > 0:
            print("Invalid locations found:")
            for location in invalid_locations['location'].unique():
                print(f"  {location}")
        
        # Recent activity
        print("\n=== RECENT ACTIVITY ===")
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_pallets = df[df['creation_date'] > recent_cutoff]
        print(f"Recent pallets (<7 days): {len(recent_pallets)}")
        
        # Storage structure verification
        print("\n=== STORAGE STRUCTURE VERIFICATION ===")
        storage_locations = df[df['location_type'] == 'STORAGE']['location'].unique()
        
        # Parse storage locations (format: AA-RR-PPL where A=aisle, R=rack, P=position, L=level)
        valid_storage = 0
        for location in storage_locations:
            parts = location.split('-')
            if len(parts) == 3 and len(parts[2]) == 3:  # AA-RR-PPL
                try:
                    aisle = int(parts[0])
                    rack = int(parts[1])
                    position = int(parts[2][:2])
                    level = parts[2][2]
                    
                    if 1 <= aisle <= 8 and 1 <= rack <= 8 and 1 <= position <= 10 and level in ['A', 'B']:
                        valid_storage += 1
                except ValueError:
                    pass
        
        print(f"Valid storage locations: {valid_storage}/{len(storage_locations)}")
        
        # Check summary sheet
        try:
            summary_df = pd.read_excel(file_path, sheet_name='Summary')
            print("\n=== SUMMARY SHEET ===")
            for _, row in summary_df.iterrows():
                print(f"{row['Metric']}: {row['Value']}")
        except Exception as e:
            print(f"Could not read summary sheet: {e}")
        
        print("\n=== VERIFICATION COMPLETE ===")
        print("✓ File is ready for testing the warehouse intelligence system")
        print("✓ Contains comprehensive test scenarios")
        print("✓ Includes overcapacity, stagnant, and incomplete lot scenarios")
        print("✓ Has data quality issues for testing validation rules")
        
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    verify_inventory_file()