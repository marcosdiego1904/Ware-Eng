#!/usr/bin/env python3
"""
Debug script to analyze current database state and active rules
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from models import Rule, Location
import json

def analyze_database_state():
    """Analyze current database state"""
    print("=== DATABASE STATE ANALYSIS ===")
    
    # Use app context
    with app.app_context():
        # Get all rules
        all_rules = Rule.query.all()
        active_rules = Rule.query.filter_by(is_active=True).all()
        
        print(f"Total rules in database: {len(all_rules)}")
        print(f"Active rules: {len(active_rules)}")
        
        # Breakdown by rule type
        rule_types = {}
        for rule in active_rules:
            rule_type = rule.rule_type
            if rule_type not in rule_types:
                rule_types[rule_type] = []
            rule_types[rule_type].append(rule)
        
        print("\n=== ACTIVE RULES BREAKDOWN ===")
        for rule_type, type_rules in rule_types.items():
            print(f"\n{rule_type}: {len(type_rules)} rules")
            for rule in type_rules:
                print(f"  - ID {rule.id}: {rule.name}")
                print(f"    Priority: {rule.priority}")
                print(f"    Conditions: {json.dumps(rule.conditions, indent=6)}")
        
        # Get locations sample
        locations = Location.query.limit(10).all()
        print(f"\n=== LOCATIONS SAMPLE ===")
        print(f"First 10 locations:")
        for loc in locations:
            print(f"  - {loc.code}: type={loc.location_type}")
        
        return rule_types

if __name__ == "__main__":
    analyze_database_state()