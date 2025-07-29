#!/usr/bin/env python3
"""
Test API Call Script
Simulates the exact API call that the frontend makes
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from argparse import Namespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from enhanced_main import run_enhanced_engine
from app import load_enhanced_engine

def test_with_different_mappings():
    print("TESTING DIFFERENT COLUMN MAPPINGS")
    print("="*60)
    
    file_path = "backend/data/comprehensive_inventory_test.xlsx"
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found at {file_path}")
        return
    
    with app.app_context():
        # Load enhanced engine
        load_enhanced_engine()
        
        # Read the original file
        original_df = pd.read_excel(file_path)
        print(f"Original file columns: {list(original_df.columns)}")
        print(f"Original shape: {original_df.shape}")
        
        # Test different mapping scenarios that might come from the frontend
        test_mappings = [
            # Scenario 1: Perfect mapping (should work)
            {
                'name': 'Perfect Mapping',
                'mapping': {
                    'pallet_id': 'pallet_id',
                    'location': 'location', 
                    'creation_date': 'creation_date',
                    'receipt_number': 'receipt_number',
                    'description': 'description'
                }
            },
            # Scenario 2: No mapping (identity) - frontend might send this
            {
                'name': 'Identity Mapping',
                'mapping': {}
            },
            # Scenario 3: Empty strings mapping - common frontend bug
            {
                'name': 'Empty String Mapping',
                'mapping': {
                    'pallet_id': '',
                    'location': '',
                    'creation_date': '',
                    'receipt_number': '',
                    'description': ''
                }
            },
            # Scenario 4: Reversed mapping - another common bug
            {
                'name': 'Reversed Mapping',
                'mapping': {
                    'pallet_id': 'pallet_id',
                    'receipt_number': 'location',
                    'description': 'creation_date', 
                    'location': 'receipt_number',
                    'creation_date': 'description'
                }
            }
        ]
        
        for scenario in test_mappings:
            print(f"\n" + "="*50)
            print(f"TESTING: {scenario['name']}")
            print(f"Mapping: {scenario['mapping']}")
            print("="*50)
            
            try:
                # Apply the mapping like the API does
                test_df = original_df.copy()
                if scenario['mapping']:
                    test_df.rename(columns=scenario['mapping'], inplace=True)
                
                print(f"After mapping columns: {list(test_df.columns)}")
                
                # Check for required columns
                required_cols = ['pallet_id', 'location', 'creation_date', 'receipt_number', 'description']
                missing_cols = [col for col in required_cols if col not in test_df.columns]
                if missing_cols:
                    print(f"MISSING COLUMNS: {missing_cols}")
                    print("This would cause the analysis to fail!")
                    continue
                
                # Convert dates like the API does
                if 'creation_date' in test_df.columns:
                    test_df['creation_date'] = pd.to_datetime(test_df['creation_date'])
                    print(f"Date conversion successful")
                
                # Show first row
                print(f"First row after processing:")
                print(test_df.head(1).to_string())
                
                # Run the analysis
                args = Namespace(debug=False, floating_time=8, straggler_ratio=0.85, stuck_ratio=0.80, stuck_time=6)
                
                anomalies = run_enhanced_engine(
                    test_df,
                    None,  # rules_df not needed for database rules
                    args,
                    use_database_rules=True,
                    rule_ids=None
                )
                
                print(f"RESULT: {len(anomalies)} anomalies found")
                
                if anomalies:
                    print("First 3 anomalies:")
                    for i, anomaly in enumerate(anomalies[:3], 1):
                        print(f"  {i}. {anomaly.get('pallet_id')}: {anomaly.get('anomaly_type')}")
                else:
                    print("NO ANOMALIES - This mapping breaks the analysis!")
                
            except Exception as e:
                print(f"ERROR with this mapping: {e}")
                import traceback
                traceback.print_exc()

def test_frontend_mapping_format():
    """Test the exact format that might come from the frontend"""
    print(f"\n" + "="*60)
    print("TESTING FRONTEND MAPPING FORMATS")
    print("="*60)
    
    # These are common formats that might come from a frontend form
    frontend_formats = [
        '{"pallet_id":"pallet_id","location":"location","creation_date":"creation_date","receipt_number":"receipt_number","description":"description"}',
        '{}',  # Empty mapping
        '{"0":"pallet_id","1":"location","2":"creation_date","3":"receipt_number","4":"description"}',  # Index-based
        None,  # No mapping sent
    ]
    
    for i, mapping_str in enumerate(frontend_formats, 1):
        print(f"\nFormat {i}: {mapping_str}")
        
        try:
            if mapping_str is None:
                print("  No mapping provided - would cause API error")
                continue
                
            mapping = json.loads(mapping_str)
            print(f"  Parsed mapping: {mapping}")
            
            # This is what the API would do
            if not mapping:
                print("  Empty mapping - columns would remain unchanged")
            else:
                print(f"  Would rename columns using: {mapping}")
                
        except json.JSONDecodeError as e:
            print(f"  JSON decode error: {e}")

if __name__ == "__main__":
    test_with_different_mappings()
    test_frontend_mapping_format()