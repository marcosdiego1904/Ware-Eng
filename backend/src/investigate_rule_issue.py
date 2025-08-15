#!/usr/bin/env python3
"""
Investigate why Rule #1 isn't updating and why rules are missing
"""

import sys
import os
import json

# Add current directory to path for imports
sys.path.insert(0, '.')

from app import app
from models import Rule, RuleCategory
from database import db
from rule_engine import RuleEngine

def investigate_rule_loading():
    """Investigate rule loading issues"""
    
    with app.app_context():
        print("=== RULE LOADING INVESTIGATION ===\n")
        
        # Check all rules in database
        print("1. ALL RULES IN DATABASE:")
        all_rules = Rule.query.order_by(Rule.id).all()
        for rule in all_rules:
            print(f"   Rule {rule.id}: {rule.name}")
            print(f"      Active: {rule.is_active}")
            print(f"      Type: {rule.rule_type}")
            print(f"      Category ID: {rule.category_id}")
            print(f"      Conditions: {rule.conditions}")
            print()
        
        # Check rule engine loading
        print("2. RULE ENGINE LOADING:")
        engine = RuleEngine(db.session, app)
        loaded_rules = engine.load_active_rules()
        
        print(f"   Total loaded: {len(loaded_rules)}")
        for rule in loaded_rules:
            print(f"   Rule {rule.id}: {rule.name}")
            print(f"      Conditions: {rule.conditions}")
        print()
        
        # Check for missing rules
        print("3. MISSING RULES ANALYSIS:")
        db_rule_ids = {rule.id for rule in all_rules if rule.is_active}
        loaded_rule_ids = {rule.id for rule in loaded_rules}
        missing_ids = db_rule_ids - loaded_rule_ids
        
        print(f"   Database active rule IDs: {sorted(db_rule_ids)}")
        print(f"   Loaded rule IDs: {sorted(loaded_rule_ids)}")
        print(f"   Missing rule IDs: {sorted(missing_ids)}")
        
        if missing_ids:
            print("\n   MISSING RULES DETAILS:")
            for rule_id in missing_ids:
                rule = Rule.query.get(rule_id)
                print(f"   Rule {rule_id}: {rule.name}")
                print(f"      Active: {rule.is_active}")
                print(f"      Category ID: {rule.category_id}")
                
                # Check if category exists
                if rule.category_id:
                    category = RuleCategory.query.get(rule.category_id)
                    if category:
                        print(f"      Category: {category.name} (active: {category.is_active})")
                    else:
                        print(f"      Category: NOT FOUND for ID {rule.category_id}")
                print()
        
        # Test Rule #1 specifically
        print("4. RULE #1 SPECIFIC TEST:")
        rule1_db = Rule.query.get(1)
        rule1_loaded = next((r for r in loaded_rules if r.id == 1), None)
        
        print(f"   Database Rule #1:")
        print(f"      Conditions: {rule1_db.conditions}")
        print(f"      Parsed: {rule1_db.get_conditions()}")
        
        if rule1_loaded:
            print(f"   Loaded Rule #1:")
            print(f"      Conditions: {rule1_loaded.conditions}")
            print(f"      Parsed: {rule1_loaded.get_conditions()}")
            
            # Check if they match
            db_conditions = rule1_db.get_conditions()
            loaded_conditions = rule1_loaded.get_conditions()
            print(f"      Match: {db_conditions == loaded_conditions}")
            
            if db_conditions != loaded_conditions:
                print(f"      MISMATCH DETECTED!")
                print(f"      DB threshold: {db_conditions.get('time_threshold_hours')}")
                print(f"      Loaded threshold: {loaded_conditions.get('time_threshold_hours')}")
                print(f"      DB location_types: {db_conditions.get('location_types')}")
                print(f"      Loaded location_types: {loaded_conditions.get('location_types')}")
        else:
            print("   Rule #1 NOT FOUND in loaded rules!")

def check_database_connection():
    """Check if we're using the right database"""
    
    with app.app_context():
        print("\n=== DATABASE CONNECTION CHECK ===\n")
        
        # Check database URL
        print(f"Database URL: {db.engine.url}")
        
        # Check if we can write and read back
        print("\nTesting database write/read:")
        
        # Get Rule #1
        rule1 = Rule.query.get(1)
        original_description = rule1.description
        
        # Update description temporarily
        test_description = f"TEST_UPDATE_{datetime.now().timestamp()}"
        rule1.description = test_description
        db.session.commit()
        
        # Read it back
        rule1_fresh = Rule.query.get(1)
        print(f"   Original description: {original_description}")
        print(f"   Test description: {test_description}")
        print(f"   Read back: {rule1_fresh.description}")
        print(f"   Write/Read successful: {rule1_fresh.description == test_description}")
        
        # Restore original
        rule1.description = original_description
        db.session.commit()
        
        print("   Restored original description")

if __name__ == "__main__":
    from datetime import datetime
    
    print("RULE CONFIGURATION INVESTIGATION")
    print("=" * 50)
    
    investigate_rule_loading()
    check_database_connection()
    
    print("\nNEXT STEPS:")
    print("1. Check if missing rules have invalid category references")
    print("2. Verify database transaction isolation")
    print("3. Check if application is using different database in production")