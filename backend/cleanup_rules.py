#!/usr/bin/env python3
"""
Clean up duplicate and test rules from WareWise database
Keep only the 8 default rules as designed
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from models import Rule

def cleanup_duplicate_rules():
    """Remove test/duplicate rules and keep only the 8 default rules"""
    
    print("WareWise Rule Cleanup")
    print("=" * 50)
    
    with app.app_context():
        # Get all rules
        all_rules = Rule.query.all()
        print(f"Total rules in database: {len(all_rules)}")
        
        # Show current rules
        print("\nCurrent rules:")
        for rule in all_rules:
            status = "DEFAULT" if rule.is_default else "CUSTOM"
            active = "ACTIVE" if rule.is_active else "INACTIVE"
            print(f"  {rule.id}: {rule.name} ({rule.rule_type}) [{status}] [{active}]")
        
        # Define the 8 default rules that should remain
        default_rules = {
            "Forgotten Pallets Alert",
            "Incomplete Lots Alert", 
            "Overcapacity Alert",
            "Invalid Locations Alert",
            "AISLE Stuck Pallets",
            "Cold Chain Violations",
            "Scanner Error Detection",
            "Location Type Mismatches"
        }
        
        print(f"\nExpected default rules: {len(default_rules)}")
        for rule_name in sorted(default_rules):
            print(f"  - {rule_name}")
        
        # Find rules to deactivate (keep defaults active, deactivate others)
        rules_to_deactivate = []
        rules_to_keep = []
        
        for rule in all_rules:
            if rule.name in default_rules:
                rules_to_keep.append(rule)
                # Ensure default rules are active and marked as default
                if not rule.is_active:
                    rule.is_active = True
                    print(f"  ✓ Activating default rule: {rule.name}")
                if not rule.is_default:
                    rule.is_default = True
                    print(f"  ✓ Marking as default: {rule.name}")
            else:
                rules_to_deactivate.append(rule)
        
        print(f"\n=== CLEANUP PLAN ===")
        print(f"Rules to keep active: {len(rules_to_keep)}")
        for rule in rules_to_keep:
            print(f"  ✓ {rule.name}")
        
        print(f"\nRules to deactivate: {len(rules_to_deactivate)}")
        for rule in rules_to_deactivate:
            print(f"  ❌ {rule.name} (ID: {rule.id})")
        
        # Confirm cleanup
        if rules_to_deactivate:
            print(f"\nDeactivating {len(rules_to_deactivate)} non-default rules...")
            for rule in rules_to_deactivate:
                rule.is_active = False
                print(f"  ❌ Deactivated: {rule.name}")
            
            # Commit changes
            db.session.commit()
            print(f"\n✅ Database updated successfully!")
        else:
            print(f"\n✅ No rules need deactivation - database is clean!")
        
        # Final verification
        print(f"\n=== FINAL STATE ===")
        active_rules = Rule.query.filter_by(is_active=True).all()
        print(f"Active rules: {len(active_rules)}")
        
        by_category = {}
        for rule in active_rules:
            category = rule.category.name if rule.category else 'UNKNOWN'
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rule)
        
        for category, rules in by_category.items():
            print(f"\n{category}:")
            for rule in rules:
                print(f"  - {rule.name} ({rule.priority})")
        
        print(f"\n🎯 SUCCESS: WareWise now has {len(active_rules)} active rules (expected: 8)")
        
        if len(active_rules) == 8:
            print("✅ Perfect! You now have exactly the 8 default rules.")
        elif len(active_rules) < 8:
            print("⚠️  Warning: Fewer than 8 rules active. Some defaults may be missing.")
        else:
            print(f"⚠️  Warning: {len(active_rules)} active rules. May need further cleanup.")

if __name__ == "__main__":
    cleanup_duplicate_rules()