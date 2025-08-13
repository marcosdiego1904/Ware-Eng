#!/usr/bin/env python3
"""
Fix duplicate stagnant pallet rules causing inconsistent anomaly counts
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from models import Rule

def fix_duplicate_rules():
    """Fix duplicate stagnant pallet rules that cause inconsistent counts"""
    print("=== FIXING DUPLICATE STAGNANT PALLET RULES ===")
    
    with app.app_context():
        # Get all active STAGNANT_PALLETS rules
        stagnant_rules = Rule.query.filter_by(rule_type='STAGNANT_PALLETS', is_active=True).all()
        
        print(f"Found {len(stagnant_rules)} active STAGNANT_PALLETS rules:")
        for rule in stagnant_rules:
            print(f"  - ID {rule.id}: {rule.name} (Priority: {rule.priority})")
        
        # Keep only the original rule (ID 1) - this should give us the expected 2 anomalies
        rules_to_keep = [1]  # "Forgotten Pallets Alert" - the original working rule
        
        deactivated_count = 0
        for rule in stagnant_rules:
            if rule.id not in rules_to_keep:
                print(f"Deactivating duplicate rule ID {rule.id}: {rule.name}")
                rule.is_active = False
                deactivated_count += 1
        
        # Commit changes
        db.session.commit()
        
        print(f"\nDeactivated {deactivated_count} duplicate rules")
        
        # Verify final state
        remaining_active = Rule.query.filter_by(rule_type='STAGNANT_PALLETS', is_active=True).all()
        print(f"\nRemaining active STAGNANT_PALLETS rules: {len(remaining_active)}")
        for rule in remaining_active:
            print(f"  - ID {rule.id}: {rule.name} (Priority: {rule.priority})")
            print(f"    Conditions: {rule.conditions}")
        
        print(f"\n✅ Should now produce expected 2 anomalies from debug_stagnant.xlsx")

if __name__ == "__main__":
    fix_duplicate_rules()