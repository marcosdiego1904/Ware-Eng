#!/usr/bin/env python3
"""
Cleanup duplicate stagnant pallet rules to get the expected 2 anomalies
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from models import Rule

def cleanup_duplicate_rules():
    """Deactivate duplicate/test stagnant pallet rules"""
    print("=== CLEANING UP DUPLICATE STAGNANT PALLET RULES ===")
    
    with app.app_context():
        # Get all active STAGNANT_PALLETS rules
        stagnant_rules = Rule.query.filter_by(rule_type='STAGNANT_PALLETS', is_active=True).all()
        
        print(f"Found {len(stagnant_rules)} active STAGNANT_PALLETS rules:")
        for rule in stagnant_rules:
            print(f"  - ID {rule.id}: {rule.name} (Priority: {rule.priority})")
        
        # Keep only the most important rule: "Forgotten Pallets Alert" (ID 1, VERY_HIGH)
        # Deactivate test/debug rules that are duplicates
        rules_to_deactivate = [
            10, # "Test Rule Creation" 
            11, # "Find Forgotten Pallets" (duplicate name with different ID)
            12, # "Debug Test Rule"
            14, # "Find Forgotten Pallets" (another duplicate)
            # Keep 15,16,17 as they have different exclusion logic and currently produce 0 anomalies
        ]
        
        print(f"\nDeactivating duplicate rules: {rules_to_deactivate}")
        
        deactivated_count = 0
        for rule_id in rules_to_deactivate:
            rule = Rule.query.filter_by(id=rule_id).first()
            if rule and rule.is_active:
                rule.is_active = False
                print(f"  OK Deactivated Rule ID {rule_id}: {rule.name}")
                deactivated_count += 1
            else:
                print(f"  - Rule ID {rule_id} not found or already inactive")
        
        # Commit changes
        db.session.commit()
        
        print(f"\nDeactivated {deactivated_count} duplicate rules")
        
        # Verify final state
        remaining_active = Rule.query.filter_by(rule_type='STAGNANT_PALLETS', is_active=True).all()
        print(f"\nRemaining active STAGNANT_PALLETS rules: {len(remaining_active)}")
        for rule in remaining_active:
            print(f"  - ID {rule.id}: {rule.name} (Priority: {rule.priority})")
            print(f"    Conditions: {rule.conditions}")

if __name__ == "__main__":
    cleanup_duplicate_rules()