#!/usr/bin/env python3
"""
Quick analysis script to examine Excel location formats
"""
import pandas as pd
import sys
import os

def analyze_excel_locations(file_path):
    """Analyze location formats in Excel files"""
    try:
        print(f"\nAnalyzing: {os.path.basename(file_path)}")
        print("=" * 50)
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        print(f"Total rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Find location column
        location_col = None
        for col in df.columns:
            if 'location' in col.lower():
                location_col = col
                break
        
        if location_col:
            print(f"\nLocation column: '{location_col}'")
            
            # Get unique locations
            locations = df[location_col].dropna().unique()
            print(f"Unique locations: {len(locations)}")
            
            # Show sample locations
            print(f"\nSample locations (first 20):")
            for i, loc in enumerate(locations[:20]):
                print(f"  {i+1:2d}. '{loc}'")
            
            # Analyze location patterns
            print(f"\nLocation Pattern Analysis:")
            
            # Count by pattern length
            lengths = {}
            for loc in locations:
                loc_str = str(loc)
                length = len(loc_str)
                lengths[length] = lengths.get(length, 0) + 1
            
            print(f"Location lengths: {dict(sorted(lengths.items()))}")
            
            # Analyze formats
            formats = {
                'with_dashes': 0,
                'with_underscores': 0,
                'with_letters': 0,
                'with_numbers': 0,
                'with_prefixes': 0
            }
            
            prefix_patterns = set()
            
            for loc in locations:
                loc_str = str(loc)
                if '-' in loc_str:
                    formats['with_dashes'] += 1
                if '_' in loc_str:
                    formats['with_underscores'] += 1
                if any(c.isalpha() for c in loc_str):
                    formats['with_letters'] += 1
                if any(c.isdigit() for c in loc_str):
                    formats['with_numbers'] += 1
                    
                # Check for prefixes
                if '_' in loc_str:
                    prefix = loc_str.split('_')[0]
                    if len(prefix) > 0:
                        formats['with_prefixes'] += 1
                        prefix_patterns.add(prefix)
            
            print(f"Format analysis: {formats}")
            
            if prefix_patterns:
                print(f"Prefix patterns found: {sorted(prefix_patterns)}")
                
            # Show examples by format
            print(f"\nFormat Examples:")
            dash_examples = [loc for loc in locations if '-' in str(loc)][:5]
            underscore_examples = [loc for loc in locations if '_' in str(loc)][:5]
            
            if dash_examples:
                print(f"With dashes: {dash_examples}")
            if underscore_examples:
                print(f"With underscores: {underscore_examples}")
            
        else:
            print("ERROR: No location column found!")
            
    except Exception as e:
        print(f"ERROR analyzing {file_path}: {e}")

def main():
    """Main function to analyze all Excel files"""
    excel_files = [
        "CentralDC_Realistic_Inventory.xlsx",
        "LargeWarehouse_Inventory.xlsx", 
        "FakeCorp_Final_Inventory.xlsx",
        "test_inventory.xlsx"
    ]
    
    for file_name in excel_files:
        file_path = f"C:\\Users\\juanb\\Documents\\Diego\\Projects\\ware2\\{file_name}"
        if os.path.exists(file_path):
            analyze_excel_locations(file_path)
        else:
            print(f"WARNING: File not found: {file_path}")

if __name__ == "__main__":
    main()