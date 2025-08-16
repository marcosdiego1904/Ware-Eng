#!/usr/bin/env python3
"""
Debug rule loading and execution
"""
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import app, db
    from models import Rule
    
    print("DEBUGGING RULE LOADING ISSUE...")
    print("=" * 60)
    
    with app.app_context():
        # Check all active rules that affect RECEIVING or TRANSITIONAL
        print("1. ALL ACTIVE RULES:")
        print("-" * 30)
        active_rules = Rule.query.filter_by(is_active=True).all()
        for rule in active_rules:
            conditions = json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions
            print(f"Rule {rule.id}: {rule.name}")
            print(f"  Type: {rule.rule_type}")
            print(f"  Conditions: {json.dumps(conditions, indent=4)}")
            print()
            
        print("2. RULES AFFECTING 'RECEIVING' OR 'TRANSITIONAL':")
        print("-" * 50)
        for rule in active_rules:
            conditions = json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions
            location_types = conditions.get('location_types', [])
            if 'RECEIVING' in location_types or 'TRANSITIONAL' in location_types:
                threshold = conditions.get('time_threshold_hours', 'NOT SET')
                print(f"Rule {rule.id}: {rule.name}")
                print(f"  Location Types: {location_types}")
                print(f"  Threshold: {threshold}h")
                print(f"  Type: {rule.rule_type}")
                print()
                
        print("3. CHECKING FOR DUPLICATE/CONFLICTING RULES:")
        print("-" * 45)
        stagnant_rules = Rule.query.filter_by(rule_type='STAGNANT_PALLETS', is_active=True).all()
        print(f"Found {len(stagnant_rules)} active STAGNANT_PALLETS rules:")
        for rule in stagnant_rules:
            conditions = json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions
            location_types = conditions.get('location_types', [])
            threshold = conditions.get('time_threshold_hours', 'NOT SET')
            print(f"  Rule {rule.id}: {threshold}h for {location_types}")
            
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()