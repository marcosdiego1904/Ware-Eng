#!/usr/bin/env python3
"""
Script to clean up duplicate rules in WareWise database

This script identifies and removes duplicate rules, keeping only the essential 8 expected rules.
"""

import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Rule, RuleCategory

def analyze_current_rules(app):
    """Analyze current rule situation"""
    with app.app_context():
        all_rules = Rule.query.all()
        print(f"\n=== CURRENT RULE ANALYSIS ===")
        print(f"Total rules in database: {len(all_rules)}")
        
        # Group by rule type
        rule_types = {}
        for rule in all_rules:
            rule_type = rule.rule_type
            if rule_type not in rule_types:
                rule_types[rule_type] = []
            rule_types[rule_type].append(rule)
        
        print(f"\nRules by type:")
        for rule_type, rules in rule_types.items():
            print(f"  {rule_type}: {len(rules)} rules")
            for rule in rules:
                status = "ACTIVE" if rule.is_active else "INACTIVE"
                print(f"    - ID {rule.id}: '{rule.name}' ({status})")
        
        # Identify duplicates
        duplicates = []
        for rule_type, rules in rule_types.items():
            if len(rules) > 1:
                duplicates.extend(rules[1:])  # Keep first, mark others as duplicates
        
        print(f"\nDuplicate rules identified: {len(duplicates)}")
        return all_rules, duplicates

def cleanup_rules(app, dry_run=True):
    """Clean up duplicate rules"""
    with app.app_context():
        all_rules, duplicates = analyze_current_rules(app)
        
        if not duplicates:
            print("No duplicate rules found!")
            return
        
        print(f"\n=== CLEANUP PLAN ===")
        print(f"Rules to remove: {len(duplicates)}")
        
        for rule in duplicates:
            print(f"  - ID {rule.id}: '{rule.name}' ({rule.rule_type})")
        
        if dry_run:
            print("\n[DRY RUN] No changes made. Use --execute to apply changes.")
            return
        
        # Execute cleanup
        print(f"\n=== EXECUTING CLEANUP ===")
        for rule in duplicates:
            print(f"Deleting rule ID {rule.id}: '{rule.name}'")
            db.session.delete(rule)
        
        db.session.commit()
        print(f"Successfully removed {len(duplicates)} duplicate rules!")
        
        # Verify cleanup
        remaining_rules = Rule.query.all()
        print(f"Remaining rules: {len(remaining_rules)}")

def main():
    """Main cleanup function"""
    dry_run = '--execute' not in sys.argv
    
    print("WareWise Rule Cleanup Tool")
    print("=" * 50)
    
    if dry_run:
        print("Running in DRY RUN mode. Use --execute to apply changes.")
    else:
        print("EXECUTING CHANGES!")
    
    # Analyze and cleanup using existing app
    cleanup_rules(app, dry_run)
    
    print(f"\n=== SUMMARY ===")
    if dry_run:
        print("Analysis complete. Run with --execute to apply changes.")
    else:
        print("Cleanup complete! Database now has clean rule set.")

if __name__ == '__main__':
    main()
