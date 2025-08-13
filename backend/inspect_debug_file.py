#!/usr/bin/env python3
"""
Inspect debug_stagnant.xlsx to understand the actual data structure
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def inspect_debug_file():
    """Inspect the debug_stagnant.xlsx file"""
    print("=== INSPECTING DEBUG_STAGNANT.XLSX ===")
    
    try:
        df = pd.read_excel("debug_stagnant.xlsx")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        print("\n=== FULL DATA CONTENT ===")
        for idx, row in df.iterrows():
            print(f"\nRow {idx + 1}:")
            for col in df.columns:
                print(f"  {col}: {row[col]}")
        
        print("\n=== DATA TYPES ===")
        print(df.dtypes)
        
        print("\n=== NULL VALUES ===")
        print(df.isnull().sum())
        
        # Try to understand what the expected format should be
        print("\n=== EXPECTED FORMAT ANALYSIS ===")
        print("Based on the rule engine errors, the expected columns should be:")
        print("- 'pallet_id' (lowercase)")
        print("- 'location' (lowercase)")
        print("- Some timestamp column for stagnant detection")
        
        return df
        
    except Exception as e:
        print(f"Error reading file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_debug_file()