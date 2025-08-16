#!/usr/bin/env python3
"""
Check current database rule configuration
"""
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import app, db
    from models import Rule
    
    print("Checking Database Rule Configuration...")
    print("=" * 50)
    
    with app.app_context():
        # Check Rule ID 1 specifically
        rule1 = Rule.query.get(1)
        if rule1:
            print(f"Rule {rule1.id}: {rule1.name}")
            print(f"Type: {rule1.rule_type}")
            print(f"Active: {rule1.is_active}")
            print(f"Priority: {rule1.priority}")
            
            # Parse conditions
            conditions = json.loads(rule1.conditions) if isinstance(rule1.conditions, str) else rule1.conditions
            print(f"Conditions: {json.dumps(conditions, indent=2)}")
            
            # Check specifically for time_threshold_hours
            if 'time_threshold_hours' in conditions:
                print(f"\n[CRITICAL] Time threshold: {conditions['time_threshold_hours']} hours")
            else:
                print(f"\n[ERROR] No time_threshold_hours found in conditions!")
        else:
            print("[ERROR] Rule ID 1 not found!")
            
        # Show all STAGNANT_PALLETS rules
        print(f"\nAll STAGNANT_PALLETS rules:")
        stagnant_rules = Rule.query.filter_by(rule_type='STAGNANT_PALLETS').all()
        for rule in stagnant_rules:
            conditions = json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions
            threshold = conditions.get('time_threshold_hours', 'NOT SET')
            print(f"  Rule {rule.id}: {rule.name} - Threshold: {threshold}h - Active: {rule.is_active}")
            
except Exception as e:
    print(f"[ERROR] {e}")