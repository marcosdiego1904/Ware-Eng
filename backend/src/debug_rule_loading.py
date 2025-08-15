#!/usr/bin/env python3
"""
Debug script to test rule loading and verify there's no caching issues
"""

import sys
import os
import json

# Add current directory to path for imports
sys.path.insert(0, '.')

from app import app
from models import Rule
from database import db
from rule_engine import RuleEngine

def test_rule_loading():
    """Test rule loading through different methods"""
    
    with app.app_context():
        print("=== TESTING RULE LOADING METHODS ===\n")
        
        # Method 1: Direct database query
        print("1. DIRECT DATABASE QUERY:")
        rule1_direct = Rule.query.get(1)
        if rule1_direct:
            print(f"   Name: {rule1_direct.name}")
            print(f"   Conditions: {rule1_direct.conditions}")
            print(f"   Parsed: {rule1_direct.get_conditions()}")
        print()
        
        # Method 2: Rule engine loading
        print("2. RULE ENGINE LOADING:")
        rule_engine = RuleEngine(db.session, app)
        rules = rule_engine.load_active_rules()
        rule1_engine = next((r for r in rules if r.id == 1), None)
        if rule1_engine:
            print(f"   Name: {rule1_engine.name}")
            print(f"   Conditions: {rule1_engine.conditions}")
            print(f"   Parsed: {rule1_engine.get_conditions()}")
        print()
        
        # Method 3: Fresh session query
        print("3. FRESH SESSION QUERY:")
        with db.session.begin():
            rule1_fresh = db.session.get(Rule, 1)
            if rule1_fresh:
                print(f"   Name: {rule1_fresh.name}")
                print(f"   Conditions: {rule1_fresh.conditions}")
                print(f"   Parsed: {rule1_fresh.get_conditions()}")
        print()
        
        # Method 4: Test the exact query from enhanced_main.py
        print("4. ENHANCED_MAIN.PY STYLE QUERY:")
        specific_rules = Rule.query.filter(Rule.id.in_([1]), Rule.is_active == True).all()
        if specific_rules:
            rule1_specific = specific_rules[0]
            print(f"   Name: {rule1_specific.name}")
            print(f"   Conditions: {rule1_specific.conditions}")
            print(f"   Parsed: {rule1_specific.get_conditions()}")
        print()
        
        # Check if conditions are consistent
        conditions_direct = rule1_direct.get_conditions() if rule1_direct else {}
        conditions_engine = rule1_engine.get_conditions() if rule1_engine else {}
        
        print("=== CONSISTENCY CHECK ===")
        print(f"Direct query conditions: {conditions_direct}")
        print(f"Engine loaded conditions: {conditions_engine}")
        print(f"Conditions match: {conditions_direct == conditions_engine}")
        
        if conditions_direct != conditions_engine:
            print("WARNING: INCONSISTENT CONDITIONS DETECTED!")
            return False
        else:
            print("SUCCESS: All loading methods return consistent conditions")
            return True

def test_rule_evaluation():
    """Test rule evaluation with minimal data"""
    
    import pandas as pd
    from datetime import datetime, timedelta
    
    with app.app_context():
        print("\n=== TESTING RULE EVALUATION ===\n")
        
        # Create minimal test data
        test_data = pd.DataFrame({
            'pallet_id': ['TEST001'],
            'location': ['RECV-01'],
            'creation_date': [datetime.now() - timedelta(hours=12)],
            'receipt_number': ['TEST_RECEIPT'],
            'description': ['Test Product'],
            'location_type': ['RECEIVING']
        })
        
        print(f"Test data shape: {test_data.shape}")
        print(f"Test pallet age: 12 hours")
        print()
        
        # Test with rule engine
        rule_engine = RuleEngine(db.session, app)
        results = rule_engine.evaluate_all_rules(test_data, rule_ids=[1])
        
        for result in results:
            print(f"Rule {result.rule_id} evaluation:")
            print(f"   Success: {result.success}")
            print(f"   Anomalies found: {len(result.anomalies)}")
            print(f"   Execution time: {result.execution_time_ms}ms")
            
            if result.error_message:
                print(f"   Error: {result.error_message}")
                
            # Get the actual rule to see what conditions were used
            rule = Rule.query.get(result.rule_id)
            if rule:
                conditions = rule.get_conditions()
                print(f"   Rule conditions used: {conditions}")
                
                # Manual check: should this pallet be flagged?
                threshold = conditions.get('time_threshold_hours', 6)
                location_types = conditions.get('location_types', ['RECEIVING'])
                print(f"   Should be flagged: 12h > {threshold}h and RECEIVING in {location_types}")
                
                expected_flagged = 12 > threshold and 'RECEIVING' in location_types
                actually_flagged = len(result.anomalies) > 0
                print(f"   Expected flagged: {expected_flagged}")
                print(f"   Actually flagged: {actually_flagged}")
                print(f"   Evaluation correct: {expected_flagged == actually_flagged}")

if __name__ == "__main__":
    print("RULE LOADING AND EVALUATION DEBUG")
    print("=" * 50)
    
    success = test_rule_loading()
    test_rule_evaluation()
    
    if not success:
        print("\nERROR: Rule loading inconsistency detected!")
        sys.exit(1)
    else:
        print("\nSUCCESS: Rule loading appears consistent")