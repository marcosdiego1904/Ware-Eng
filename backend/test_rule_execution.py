#!/usr/bin/env python3
"""
Test script to diagnose the rule execution issue in WareWise
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from datetime import datetime
from rule_engine import RuleEngine
from models import Rule, db
from app import app

def test_rule_execution_with_debug_data():
    """Test rule execution with debug_stagnant.xlsx to identify anomaly source"""
    
    with app.app_context():
        print("=== WAREBASE RULE EXECUTION DIAGNOSIS ===")
        print()
        
        # Load test data
        print("Loading test data...")
        df = pd.read_excel('debug_stagnant.xlsx')
        
        # Rename columns to match expected format
        column_mapping = {
            'Pallet ID': 'pallet_id',
            'Location': 'location', 
            'Receipt Number': 'receipt_number',
            'Description': 'description',
            'Quantity': 'quantity',
            'Weight (lbs)': 'weight',
            'Created Date': 'creation_date',
            'SKU': 'sku'
        }
        df = df.rename(columns=column_mapping)
        
        print("Test data loaded:")
        for i, row in df.iterrows():
            hours_old = (datetime.now() - row['creation_date']).total_seconds()/3600
            print(f"  {row['pallet_id']}: {row['location']} ({hours_old:.1f}h old)")
        print()
        
        # Initialize rule engine
        print("Initializing rule engine...")
        rule_engine = RuleEngine(db.session, app)
        
        # Get all active rules
        active_rules = rule_engine.load_active_rules()
        print(f"Found {len(active_rules)} active rules")
        print()
        
        # Evaluate all rules and track results
        print("=== RULE-BY-RULE EXECUTION ===")
        total_anomalies = 0
        rule_results = {}
        
        for rule in active_rules:
            result = rule_engine.evaluate_rule(rule, df)
            anomaly_count = len(result.anomalies)
            total_anomalies += anomaly_count
            
            rule_results[rule.id] = {
                'name': rule.name,
                'type': rule.rule_type,
                'priority': rule.priority,
                'anomaly_count': anomaly_count,
                'success': result.success,
                'execution_time': result.execution_time_ms,
                'anomalies': result.anomalies
            }
            
            status = "OK" if result.success else "FAIL"
            if anomaly_count > 0:
                print(f"{status} Rule {rule.id}: {rule.name} ({rule.rule_type})")
                print(f"    Priority: {rule.priority}")
                print(f"    Anomalies: {anomaly_count}")
                print(f"    Execution time: {result.execution_time_ms}ms")
                
                # Show specific anomalies
                for anomaly in result.anomalies:
                    print(f"      - {anomaly['pallet_id']} in {anomaly['location']}: {anomaly['anomaly_type']}")
                    print(f"        Details: {anomaly['details']}")
                print()
            elif not result.success:
                print(f"{status} Rule {rule.id}: {rule.name} - FAILED")
                print(f"    Error: {result.error_message}")
                print()
        
        print("=== SUMMARY ===")
        print(f"Total anomalies found: {total_anomalies}")
        print()
        
        # Group by rule type
        stagnant_rules = []
        invalid_location_rules = []
        other_rules = []
        
        for rule_id, result in rule_results.items():
            if result['anomaly_count'] > 0:
                if result['type'] == 'STAGNANT_PALLETS':
                    stagnant_rules.append((rule_id, result))
                elif result['type'] == 'INVALID_LOCATION':
                    invalid_location_rules.append((rule_id, result))
                else:
                    other_rules.append((rule_id, result))
        
        print(f"STAGNANT_PALLETS rules with anomalies: {len(stagnant_rules)}")
        for rule_id, result in stagnant_rules:
            print(f"  Rule {rule_id}: {result['name']} - {result['anomaly_count']} anomalies")
        
        print(f"INVALID_LOCATION rules with anomalies: {len(invalid_location_rules)}")
        for rule_id, result in invalid_location_rules:
            print(f"  Rule {rule_id}: {result['name']} - {result['anomaly_count']} anomalies")
        
        print(f"Other rules with anomalies: {len(other_rules)}")
        for rule_id, result in other_rules:
            print(f"  Rule {rule_id}: {result['name']} ({result['type']}) - {result['anomaly_count']} anomalies")
        
        print()
        print("=== EXPECTED VS ACTUAL ===")
        print("Expected: 2 stagnant pallet anomalies (OLD001, OLD002)")
        print(f"Actual: {total_anomalies} total anomalies")
        
        expected_anomalies = 2
        if total_anomalies != expected_anomalies:
            print(f"ISSUE CONFIRMED: Expected {expected_anomalies}, got {total_anomalies}")
            
            if len(stagnant_rules) > 1:
                print(f"   Root cause: {len(stagnant_rules)} overlapping STAGNANT_PALLETS rules")
                print(f"   Each rule is detecting the same 2 pallets, creating duplicates")
            
            if len(invalid_location_rules) > 0:
                print(f"   Secondary issue: {len(invalid_location_rules)} INVALID_LOCATION rules despite valid locations")
        else:
            print("No issues detected")

if __name__ == "__main__":
    test_rule_execution_with_debug_data()