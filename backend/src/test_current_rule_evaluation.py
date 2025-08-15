#!/usr/bin/env python3
"""
Test the current rule evaluation to identify the caching issue
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, '.')

from app import app
from models import Rule
from database import db
from rule_engine import RuleEngine

def test_rule_1_evaluation():
    """Test Rule #1 evaluation with a simple case"""
    
    with app.app_context():
        print("=== TESTING RULE #1 EVALUATION ===\n")
        
        # Create test data - one pallet that should be flagged with 10h threshold
        test_data = pd.DataFrame({
            'pallet_id': ['TEST_12H'],
            'location': ['RECV-01'],
            'creation_date': [datetime.now() - timedelta(hours=12)],
            'receipt_number': ['TEST_RECEIPT'],
            'description': ['Test Product'],
            'location_type': ['RECEIVING']
        })
        
        print("Test setup:")
        print(f"  Pallet: TEST_12H")
        print(f"  Location: RECV-01 (RECEIVING)")
        print(f"  Age: 12 hours")
        print()
        
        # Check Rule #1 in database
        rule1 = Rule.query.get(1)
        print("Rule #1 database state:")
        print(f"  ID: {rule1.id}")
        print(f"  Name: {rule1.name}")
        print(f"  Conditions: {rule1.conditions}")
        print(f"  Parsed: {rule1.get_conditions()}")
        print()
        
        conditions = rule1.get_conditions()
        threshold = conditions.get('time_threshold_hours', 6)
        location_types = conditions.get('location_types', ['RECEIVING'])
        
        print("Expected behavior:")
        print(f"  Threshold: {threshold} hours")
        print(f"  Location types: {location_types}")
        print(f"  Should be flagged: {12 > threshold and 'RECEIVING' in location_types}")
        print()
        
        # Test with rule engine
        print("Rule engine evaluation:")
        rule_engine = RuleEngine(db.session, app)
        
        # Load rules and check what Rule #1 looks like
        rules = rule_engine.load_active_rules()
        rule1_from_engine = next((r for r in rules if r.id == 1), None)
        
        print(f"  Rule #1 from engine: {rule1_from_engine.get_conditions()}")
        
        # Evaluate
        results = rule_engine.evaluate_all_rules(test_data, rule_ids=[1])
        
        if results:
            result = results[0]
            print(f"  Execution success: {result.success}")
            print(f"  Anomalies found: {len(result.anomalies)}")
            print(f"  Execution time: {result.execution_time_ms}ms")
            
            if result.anomalies:
                for anomaly in result.anomalies:
                    print(f"    Anomaly: {anomaly.get('pallet_id')} - {anomaly.get('issue_description')}")
            
            if result.error_message:
                print(f"  Error: {result.error_message}")
        
        print()
        return results

def test_all_active_rules():
    """Test loading all active rules"""
    
    with app.app_context():
        print("=== TESTING ALL ACTIVE RULES LOADING ===\n")
        
        rule_engine = RuleEngine(db.session, app)
        rules = rule_engine.load_active_rules()
        
        print(f"Total active rules loaded: {len(rules)}")
        print()
        
        for rule in rules:
            print(f"Rule {rule.id}: {rule.name}")
            print(f"  Type: {rule.rule_type}")
            print(f"  Priority: {rule.priority}")
            print(f"  Conditions: {rule.conditions}")
            print()
        
        # Check if Rule #10 is in the list
        rule10 = next((r for r in rules if r.id == 10), None)
        if rule10:
            print("✓ Rule #10 found in active rules")
        else:
            print("✗ Rule #10 NOT found in active rules")
        
        return rules

if __name__ == "__main__":
    print("RULE EVALUATION DEBUGGING")
    print("=" * 50)
    
    # Test all rule loading
    rules = test_all_active_rules()
    
    # Test Rule #1 specifically  
    results = test_rule_1_evaluation()
    
    print("\nCONCLUSIONS:")
    print("=" * 50)
    
    if len(rules) == 9:
        print("✓ All 9 rules loaded correctly")
    else:
        print(f"✗ Expected 9 rules, got {len(rules)}")
    
    if results and len(results) > 0:
        result = results[0]
        if result.success:
            print("✓ Rule #1 evaluation successful")
            # With 12h pallet and 10h threshold, should be flagged
            if len(result.anomalies) > 0:
                print("✓ Pallet correctly flagged (12h > 10h threshold)")
            else:
                print("✗ Pallet should have been flagged but wasn't")
        else:
            print(f"✗ Rule #1 evaluation failed: {result.error_message}")
    else:
        print("✗ No evaluation results returned")