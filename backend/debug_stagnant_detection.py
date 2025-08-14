#!/usr/bin/env python3
"""
Debug script for StagnantPalletsEvaluator detection logic

Based on the analysis, the StagnantPalletsEvaluator should detect:
- OLD001: HOLA2_RECV-2 (12h old) → Should trigger
- OLD002: RECEIVING (10h old)    → Should trigger  
- NEW001: 001A (2h old)         → Should NOT trigger

But it's currently finding 0 anomalies.
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Rule, Location
from rule_engine import RuleEngine, StagnantPalletsEvaluator

def create_test_data():
    """Create test data that should trigger stagnant pallet detection"""
    now = datetime.now()
    
    test_data = [
        {
            'pallet_id': 'OLD001',
            'location': 'HOLA2_RECV-2',
            'creation_date': now - timedelta(hours=12),  # 12 hours old
            'receipt_number': 'REC001',
            'description': 'Test Product 1'
        },
        {
            'pallet_id': 'OLD002', 
            'location': 'RECEIVING',
            'creation_date': now - timedelta(hours=10),  # 10 hours old
            'receipt_number': 'REC002',
            'description': 'Test Product 2'
        },
        {
            'pallet_id': 'NEW001',
            'location': '001A',
            'creation_date': now - timedelta(hours=2),   # 2 hours old
            'receipt_number': 'REC003', 
            'description': 'Test Product 3'
        }
    ]
    
    return pd.DataFrame(test_data)

def debug_location_types(inventory_df):
    """Debug location type assignment"""
    with app.app_context():
        print("=== LOCATION TYPE ASSIGNMENT DEBUG ===")
        
        evaluator = StagnantPalletsEvaluator(app=app)
        df_with_types = evaluator._assign_location_types(inventory_df.copy())
        
        print(f"Original columns: {list(inventory_df.columns)}")
        print(f"After assignment columns: {list(df_with_types.columns)}")
        
        for _, row in df_with_types.iterrows():
            print(f"Pallet {row['pallet_id']}: {row['location']} -> {row['location_type']}")
        
        return df_with_types

def debug_database_locations():
    """Debug database locations to understand mapping issues"""
    with app.app_context():
        print("\n=== DATABASE LOCATIONS DEBUG ===")
        
        all_locations = Location.query.all()
        print(f"Total locations in database: {len(all_locations)}")
        
        receiving_locations = [loc for loc in all_locations if 'RECV' in loc.code.upper() or loc.code.upper() == 'RECEIVING']
        print(f"Receiving-type locations: {len(receiving_locations)}")
        
        for loc in receiving_locations[:10]:  # Show first 10
            print(f"  - {loc.code} (type: {loc.location_type}, pattern: {loc.pattern})")
        
        # Check specific test locations
        test_locations = ['HOLA2_RECV-2', 'RECEIVING', '001A']
        for test_loc in test_locations:
            loc = Location.query.filter_by(code=test_loc).first()
            if loc:
                print(f"Found {test_loc}: type={loc.location_type}, active={loc.is_active}")
            else:
                print(f"NOT FOUND: {test_loc}")

def debug_rule_conditions():
    """Debug the rule conditions for STAGNANT_PALLETS"""
    with app.app_context():
        print("\n=== RULE CONDITIONS DEBUG ===")
        
        stagnant_rule = Rule.query.filter_by(rule_type='STAGNANT_PALLETS').first()
        if stagnant_rule:
            print(f"Rule ID: {stagnant_rule.id}")
            print(f"Rule Name: {stagnant_rule.name}")
            print(f"Conditions: {stagnant_rule.conditions}")
            print(f"Priority: {stagnant_rule.priority}")
            print(f"Active: {stagnant_rule.is_active}")
        else:
            print("No STAGNANT_PALLETS rule found!")

def run_full_debug():
    """Run complete debug of stagnant detection"""
    with app.app_context():
        print("STAGNANT PALLETS DETECTION DEBUG")
        print("=" * 50)
        
        # Step 1: Create test data
        print("\n1. Creating test data...")
        test_df = create_test_data()
        print(f"Test data shape: {test_df.shape}")
        print(test_df[['pallet_id', 'location', 'creation_date']])
        
        # Step 2: Debug database locations
        debug_database_locations()
        
        # Step 3: Debug rule conditions
        debug_rule_conditions()
        
        # Step 4: Debug location type assignment
        df_with_types = debug_location_types(test_df)
        
        # Step 5: Test rule evaluation
        print("\n=== RULE EVALUATION DEBUG ===")
        rule_engine = RuleEngine(db.session, app=app)
        stagnant_rule = Rule.query.filter_by(rule_type='STAGNANT_PALLETS').first()
        
        if stagnant_rule:
            print(f"Evaluating rule: {stagnant_rule.name}")
            result = rule_engine.evaluate_rule(stagnant_rule, df_with_types)
            
            print(f"Rule execution successful: {result.success}")
            print(f"Anomalies found: {len(result.anomalies)}")
            print(f"Execution time: {result.execution_time_ms}ms")
            
            if result.error_message:
                print(f"Error: {result.error_message}")
            
            for i, anomaly in enumerate(result.anomalies):
                print(f"  Anomaly {i+1}: {anomaly}")
        else:
            print("No STAGNANT_PALLETS rule found!")
        
        # Step 6: Manual evaluation for debugging
        print("\n=== MANUAL EVALUATION DEBUG ===")
        evaluator = StagnantPalletsEvaluator(app=app)
        
        # Parse conditions manually
        if stagnant_rule:
            import json
            conditions = json.loads(stagnant_rule.conditions) if stagnant_rule.conditions else {}
            print(f"Parsed conditions: {conditions}")
            
            time_threshold_hours = conditions.get('time_threshold_hours', 6)
            location_types = conditions.get('location_types', ['RECEIVING'])
            
            print(f"Time threshold: {time_threshold_hours} hours")
            print(f"Target location types: {location_types}")
            
            # Check each pallet manually
            now = datetime.now()
            for _, pallet in df_with_types.iterrows():
                time_diff = now - pallet['creation_date']
                age_hours = time_diff.total_seconds() / 3600
                location_type = pallet['location_type']
                
                should_trigger = (
                    age_hours > time_threshold_hours and 
                    location_type in location_types
                )
                
                print(f"Pallet {pallet['pallet_id']}: age={age_hours:.1f}h, type='{location_type}', should_trigger={should_trigger}")

if __name__ == '__main__':
    run_full_debug()