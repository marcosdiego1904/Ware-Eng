#!/usr/bin/env python3
"""
Test Specific File Script
Analyzes the comprehensive_inventory_test.xlsx file specifically
"""

import os
import sys
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from enhanced_main import run_enhanced_engine

def analyze_file():
    print("ANALYZING: comprehensive_inventory_test.xlsx")
    print("="*60)
    
    file_path = "backend/data/comprehensive_inventory_test.xlsx"
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found at {file_path}")
        return
    
    try:
        # Read the file
        print("1. Reading file...")
        df = pd.read_excel(file_path)
        print(f"   Loaded {len(df)} rows")
        
        # Show basic info
        print(f"\n2. File Structure:")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}")
        
        print(f"\n3. Column Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. '{col}'")
        
        # Show first few rows
        print(f"\n4. First 5 rows:")
        print(df.head().to_string())
        
        # Check required columns
        required_cols = ['pallet_id', 'location', 'creation_date', 'receipt_number', 'description']
        print(f"\n5. Required Column Check:")
        missing_cols = []
        for col in required_cols:
            if col in df.columns:
                print(f"   + {col}: FOUND")
            else:
                print(f"   - {col}: MISSING")
                missing_cols.append(col)
        
        if missing_cols:
            print(f"\n   ERROR: Missing required columns: {missing_cols}")
            print("   The analysis cannot work without these columns.")
            return
        
        # Check creation_date format
        print(f"\n6. Creation Date Analysis:")
        creation_dates = df['creation_date'].dropna()
        if len(creation_dates) > 0:
            print(f"   Sample dates:")
            for i, date in enumerate(creation_dates.head(3)):
                print(f"   - {date} (type: {type(date)})")
            
            # Check if dates are parsed correctly
            if pd.api.types.is_datetime64_any_dtype(df['creation_date']):
                print("   + Dates are in datetime format")
                
                # Check age of pallets
                now = datetime.now()
                if hasattr(creation_dates.iloc[0], 'to_pydatetime'):
                    oldest = creation_dates.min().to_pydatetime()
                    newest = creation_dates.max().to_pydatetime()
                else:
                    oldest = creation_dates.min()
                    newest = creation_dates.max()
                
                oldest_hours = (now - oldest).total_seconds() / 3600
                newest_hours = (now - newest).total_seconds() / 3600
                
                print(f"   Age range: {oldest_hours:.1f}h to {newest_hours:.1f}h old")
                
                if oldest_hours < 6:
                    print("   WARNING: All pallets are less than 6 hours old!")
                    print("   This means 'Forgotten Pallets' rule won't trigger.")
                else:
                    print(f"   + Some pallets are old enough ({oldest_hours:.1f}h > 6h)")
            else:
                print("   - Dates are NOT in datetime format")
                print("   Attempting to convert...")
                try:
                    df['creation_date'] = pd.to_datetime(df['creation_date'])
                    print("   + Conversion successful")
                except:
                    print("   - Conversion failed")
                    return
        
        # Check locations
        print(f"\n7. Location Analysis:")
        unique_locations = df['location'].value_counts()
        print(f"   Unique locations ({len(unique_locations)}):")
        for loc, count in unique_locations.head(10).items():
            print(f"   - '{loc}': {count} pallets")
        
        # Now test with the enhanced engine
        print(f"\n8. Running Analysis with Enhanced Engine:")
        print("   " + "="*50)
        
        with app.app_context():
            try:
                anomalies = run_enhanced_engine(
                    df,
                    use_database_rules=True,
                    rule_ids=None
                )
                
                print(f"\n   RESULT: {len(anomalies)} anomalies found")
                
                if anomalies:
                    print(f"\n   Anomalies by type:")
                    anomaly_types = {}
                    for anomaly in anomalies:
                        atype = anomaly.get('anomaly_type', 'Unknown')
                        anomaly_types[atype] = anomaly_types.get(atype, 0) + 1
                    
                    for atype, count in anomaly_types.items():
                        print(f"   - {atype}: {count}")
                    
                    print(f"\n   First 10 anomalies:")
                    for i, anomaly in enumerate(anomalies[:10], 1):
                        print(f"   {i}. {anomaly.get('pallet_id')}: {anomaly.get('anomaly_type')}")
                        print(f"      Location: {anomaly.get('location')}")
                        print(f"      Priority: {anomaly.get('priority')}")
                        print(f"      Details: {anomaly.get('details')}")
                        print()
                else:
                    print("\n   NO ANOMALIES FOUND")
                    print("\n   Possible reasons:")
                    print("   1. All pallets are too recent (< 6 hours old)")
                    print("   2. All locations are valid and within capacity")
                    print("   3. No lots are near completion with stragglers")
                    print("   4. Data format issues")
                
            except Exception as e:
                print(f"\n   ERROR running analysis: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"ERROR reading file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_file()