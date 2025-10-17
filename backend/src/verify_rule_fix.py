#!/usr/bin/env python3
"""
Quick verification that the exclusion_rules column fix worked
Tests that we can query rules without errors
"""

import os
import sys

# Add the backend src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import Rule

def verify_rule_queries():
    """Test that we can query rules without database errors"""

    print("="*60)
    print("Testing Rule Queries After Migration Fix")
    print("="*60)

    with app.app_context():
        try:
            # This is the exact query that was failing before
            print("\n[TEST 1] Querying active rules with order by priority...")
            rules = Rule.query.filter_by(is_active=True).order_by(
                Rule.priority.desc()
            ).all()

            print(f"[OK] Successfully queried {len(rules)} active rules")

            # Test accessing exclusion_rules on a rule
            if rules:
                print(f"\n[TEST 2] Accessing exclusion_rules field on first rule...")
                first_rule = rules[0]
                print(f"  Rule name: {first_rule.name}")
                print(f"  Rule type: {first_rule.rule_type}")
                print(f"  Priority: {first_rule.priority}")
                print(f"  Precedence level: {first_rule.precedence_level}")

                # Try to get exclusion rules (should work now)
                exclusion_rules = first_rule.get_exclusion_rules()
                print(f"  Exclusion rules: {exclusion_rules}")
                print("[OK] Successfully accessed exclusion_rules field")

            # List all rules for reference
            print(f"\n[SUMMARY] All active rules in database:")
            for i, rule in enumerate(rules, 1):
                precedence = rule.precedence_level if rule.precedence_level else "Not set"
                print(f"  {i}. [{rule.id}] {rule.name} (Priority: {rule.priority}, Precedence: {precedence})")

            print("\n" + "="*60)
            print("[SUCCESS] All tests passed!")
            print("="*60)
            print("\nThe database schema issue has been resolved.")
            print("You can now run inventory analysis without errors.")

            return True

        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            print("\n" + "="*60)
            print("[FAILED] Verification failed")
            print("="*60)
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    verify_rule_queries()
