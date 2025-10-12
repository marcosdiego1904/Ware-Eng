"""
Quick script to deprecate Rule 8 (Location Mapping Errors)
Run from backend/ directory: python deprecate_rule8.py
"""

import sys
sys.path.insert(0, 'src')

from app import app, db
from src.models import Rule
from datetime import datetime
import json

def deprecate_rule8():
    """Deprecate Rule 8"""

    with app.app_context():
        print("\n" + "="*60)
        print("DEPRECATING RULE 8 (Location Mapping Errors)")
        print("="*60)

        # Find Rule 8
        rule8 = Rule.query.filter_by(rule_type='LOCATION_MAPPING_ERROR').first()

        if not rule8:
            print("\n⚠️  Rule 8 (LOCATION_MAPPING_ERROR) not found in database.")
            print("    Either it doesn't exist or was already deleted.")
            return False

        print(f"\n✓ Found Rule 8: '{rule8.name}'")
        print(f"  Current Status: {'Active' if rule8.is_active else 'Inactive'}")
        print(f"  Rule ID: {rule8.id}")

        # Update rule to be deprecated
        rule8.is_active = False
        rule8.name = "[DEPRECATED] Location Type Mismatches"
        rule8.description = """⚠️ DEPRECATED - This rule is no longer necessary.

**Why Deprecated:**
- Real-world inventory reports don't include 'location_type' column
- WareWise auto-detects location types from location codes
- This rule caused 15 false positives in testing
- Only catches manual data entry errors (extremely rare)

**Recommendation:** Leave disabled and rely on auto-detection.

Deprecated: 2025-01-09"""

        # Update parameters
        try:
            params = rule8.get_parameters()
            params['_deprecated'] = True
            params['_deprecated_date'] = '2025-01-09'
            rule8.set_parameters(params)
        except:
            pass

        # Update priority
        rule8.priority = 'LOW'
        rule8.updated_at = datetime.utcnow()

        # Commit
        try:
            db.session.commit()

            print("\n✅ SUCCESS: Rule 8 has been deprecated!")
            print("\nChanges Applied:")
            print(f"  - is_active: True → False")
            print(f"  - name: Updated with [DEPRECATED] prefix")
            print(f"  - description: Added deprecation notice")
            print(f"  - priority: → LOW")

            print("\n" + "="*60)
            print("RULE 8 DEPRECATION COMPLETE")
            print("="*60)
            print("\n📝 Expected anomaly count: 35 → 30 (6 active rules)")
            print("\n")

            return True

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = deprecate_rule8()
    sys.exit(0 if success else 1)
