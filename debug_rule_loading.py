#!/usr/bin/env python3
"""
Debug script to investigate rule loading issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

import sqlite3
import pandas as pd
from datetime import datetime

def check_database_rules():
    """Check what rules are in the database"""
    print("=== DATABASE RULES CHECK ===")
    
    db_path = os.path.join('backend', 'instance', 'database.db')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all rules
    cursor.execute('''
        SELECT id, name, is_active, rule_type, conditions, priority, is_default 
        FROM rule 
        ORDER BY id
    ''')
    
    rules = cursor.fetchall()
    print(f"Total rules in database: {len(rules)}")
    print()
    
    active_rules = []
    for rule in rules:
        rule_id, name, is_active, rule_type, conditions, priority, is_default = rule
        status = "ACTIVE" if is_active else "INACTIVE"
        default_status = "DEFAULT" if is_default else "CUSTOM"
        print(f"Rule #{rule_id}: {name}")
        print(f"   Status: {status} | Type: {rule_type} | Priority: {priority} | {default_status}")
        print(f"   Conditions: {conditions}")
        
        if is_active:
            active_rules.append(rule_id)
        print()
    
    print(f"Active rule IDs: {active_rules}")
    conn.close()
    return active_rules

def test_rule_engine():
    """Test the rule engine loading"""
    print("=== RULE ENGINE TEST ===")
    
    try:
        # Set up Flask app context
        from app import app, db
        from rule_engine import RuleEngine
        from models import Rule
        
        with app.app_context():
            print("Flask app context established")
            
            # Create rule engine
            engine = RuleEngine(db.session)
            print("RuleEngine created")
            
            # Load rules
            rules = engine.load_active_rules()
            print(f"Rule engine loaded {len(rules)} rules:")
            
            for rule in rules:
                print(f"  Rule #{rule.id}: {rule.name}")
                print(f"    Conditions: {rule.conditions}")
                print(f"    Active: {rule.is_active}")
                print()
            
            # Test with sample data
            sample_data = pd.DataFrame({
                'item_id': ['PAL001', 'PAL002'],
                'location': ['RECEIVING-A1', 'TRANSITIONAL-B2'], 
                'creation_date': [datetime.now(), datetime.now()],
                'item_description': ['Test Item 1', 'Test Item 2']
            })
            
            print("Testing rule evaluation with sample data...")
            results = engine.evaluate_all_rules(sample_data)
            print(f"Evaluation returned {len(results)} results:")
            
            for result in results:
                print(f"  Rule #{result.rule_id}: Success={result.success}, Anomalies={len(result.anomalies)}")
                if not result.success:
                    print(f"    Error: {result.error_message}")
    
    except Exception as e:
        print(f"Error testing rule engine: {e}")
        import traceback
        traceback.print_exc()

def check_rule_1_specifically():
    """Check Rule #1 specifically"""
    print("=== RULE #1 SPECIFIC CHECK ===")
    
    try:
        from app import app, db
        from models import Rule
        
        with app.app_context():
            rule1 = Rule.query.get(1)
            if rule1:
                print(f"Rule #1 found in database:")
                print(f"  Name: {rule1.name}")
                print(f"  Active: {rule1.is_active}")
                print(f"  Conditions: {rule1.conditions}")
                print(f"  Type: {rule1.rule_type}")
                print(f"  Priority: {rule1.priority}")
                print(f"  Is Default: {rule1.is_default}")
            else:
                print("Rule #1 not found in database!")
                
    except Exception as e:
        print(f"Error checking Rule #1: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting comprehensive rule loading debug...")
    print()
    
    # Check database directly
    active_rules = check_database_rules()
    print()
    
    # Test rule engine
    test_rule_engine()
    print()
    
    # Check Rule #1 specifically
    check_rule_1_specifically()
    
    print("\nDebug complete.")