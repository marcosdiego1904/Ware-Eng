#!/usr/bin/env python3
"""
Debug script to check location type assignments for our test data
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from rule_engine import RuleEngine
import pandas as pd

def debug_location_types():
    """Debug location type assignments"""
    print("=== DEBUGGING LOCATION TYPE ASSIGNMENTS ===")
    
    with app.app_context():
        # Load the debug file
        df = pd.read_excel("debug_stagnant.xlsx")
        
        # Normalize columns like the rule engine does
        rule_engine = RuleEngine(db, app)
        df_normalized = rule_engine._normalize_dataframe_columns(df)
        
        print("Original data:")
        for idx, row in df_normalized.iterrows():
            pallet_id = row['pallet_id']
            location = row['location']
            created_date = row['creation_date']
            print(f"  {pallet_id}: {location} (created: {created_date})")
        
        # Get the stagnant evaluator to test location type assignment
        stagnant_evaluator = rule_engine.evaluators['STAGNANT_PALLETS']
        
        # Assign location types
        df_with_types = stagnant_evaluator._assign_location_types(df_normalized)
        
        print("\nAfter location type assignment:")
        for idx, row in df_with_types.iterrows():
            pallet_id = row['pallet_id']
            location = row['location']
            location_type = row['location_type']
            created_date = row['creation_date']
            print(f"  {pallet_id}: {location} -> {location_type} (created: {created_date})")
        
        # Check if HOLA2_RECV-2 and RECEIVING are being classified as RECEIVING type
        print("\nLocation type analysis:")
        receiving_pallets = df_with_types[df_with_types['location_type'] == 'RECEIVING']
        print(f"Pallets in RECEIVING locations: {len(receiving_pallets)}")
        for idx, row in receiving_pallets.iterrows():
            print(f"  - {row['pallet_id']}: {row['location']}")
        
        return df_with_types

if __name__ == "__main__":
    debug_location_types()