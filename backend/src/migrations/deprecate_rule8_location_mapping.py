"""
Migration: Deprecate Rule 8 (Location Mapping Errors)
Date: 2025-01-09
Reason: Real-world inventory reports don't include location_type column.
        System auto-detects location types from location codes.
        This rule caused false positives in testing and is unnecessary.

This migration:
1. Sets Rule 8 (LOCATION_MAPPING_ERROR) to is_active = False
2. Updates description to explain deprecation
3. Adds deprecation note to rule parameters
"""

from database import db
from models import Rule
from datetime import datetime
import json

def deprecate_rule8():
    """Deprecate Rule 8 (Location Mapping Errors)"""

    print("\n" + "="*60)
    print("DEPRECATING RULE 8 (Location Mapping Errors)")
    print("="*60)

    # Find Rule 8
    rule8 = Rule.query.filter_by(rule_type='LOCATION_MAPPING_ERROR').first()

    if not rule8:
        print("\n⚠️  Rule 8 (LOCATION_MAPPING_ERROR) not found in database.")
        print("    This might be a fresh installation or the rule was already deleted.")
        return False

    print(f"\n✓ Found Rule 8: '{rule8.name}'")
    print(f"  Current Status: {'Active' if rule8.is_active else 'Inactive'}")
    print(f"  Rule ID: {rule8.id}")

    # Update rule to be deprecated
    rule8.is_active = False
    rule8.name = "[DEPRECATED] Location Type Mismatches"
    rule8.description = """
⚠️ DEPRECATED - This rule is no longer necessary or recommended.

**Why Deprecated?**
Real-world inventory reports typically do NOT include a 'location_type' column.
Modern WMS systems only export location codes. WareWise's Virtual Location Engine
correctly auto-detects location types from location code patterns using deterministic
pattern matching.

**Issues with This Rule:**
- Caused 15 false positives in testing when location_type column was present
- Real-world reports don't include location_type column
- Auto-detection from location codes is more accurate and consistent
- Only catches manual data entry errors (extremely rare in practice)

**When to Use (Rare Cases Only):**
Only enable this rule if your inventory system:
1. Exports a manual 'location_type' column in CSV files
2. Has a history of location type classification errors
3. Does NOT rely on WareWise's auto-detection system

**Recommendation:** Leave this rule disabled and rely on auto-detection.

**Deprecated Date:** 2025-01-09
**Alternative:** Use Virtual Location Engine's auto-detection (enabled by default)
""".strip()

    # Update parameters to include deprecation notice
    try:
        params = rule8.get_parameters()
        params['_deprecated'] = True
        params['_deprecated_date'] = '2025-01-09'
        params['_deprecation_reason'] = 'Real-world reports do not include location_type column; auto-detection is more accurate'
        rule8.set_parameters(params)
    except Exception as e:
        print(f"\n⚠️  Warning: Could not update parameters: {e}")

    # Update priority to LOW (since it's deprecated)
    rule8.priority = 'LOW'

    # Commit changes
    try:
        rule8.updated_at = datetime.utcnow()
        db.session.commit()

        print("\n✅ SUCCESS: Rule 8 has been deprecated")
        print("\nChanges Applied:")
        print(f"  - is_active: True → False")
        print(f"  - name: 'Location Type Mismatches' → '[DEPRECATED] Location Type Mismatches'")
        print(f"  - description: Updated with deprecation notice")
        print(f"  - priority: {rule8.priority} → LOW")
        print(f"  - parameters: Added deprecation metadata")

        print("\n" + "="*60)
        print("RULE 8 DEPRECATION COMPLETE")
        print("="*60)
        print("\n📝 Note: Users can still manually enable this rule if needed,")
        print("   but it will be disabled by default and clearly marked as deprecated.")
        print("\n")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: Failed to commit changes: {e}")
        db.session.rollback()
        return False


def verify_deprecation():
    """Verify that Rule 8 was deprecated correctly"""

    print("\n" + "-"*60)
    print("VERIFICATION: Checking Rule 8 Status")
    print("-"*60)

    rule8 = Rule.query.filter_by(rule_type='LOCATION_MAPPING_ERROR').first()

    if not rule8:
        print("\n⚠️  Rule 8 not found in database")
        return False

    print(f"\nRule 8 Status:")
    print(f"  Name: {rule8.name}")
    print(f"  Active: {rule8.is_active}")
    print(f"  Priority: {rule8.priority}")
    print(f"  Updated: {rule8.updated_at}")

    # Check if deprecation was successful
    if not rule8.is_active and '[DEPRECATED]' in rule8.name:
        print("\n✅ Verification PASSED: Rule 8 is properly deprecated")
        return True
    else:
        print("\n❌ Verification FAILED: Rule 8 deprecation incomplete")
        return False


def run_migration():
    """Main migration entry point"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  MIGRATION: Deprecate Rule 8 (Location Mapping Errors)".ljust(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")

    # Run deprecation
    success = deprecate_rule8()

    if not success:
        print("\n❌ Migration failed. No changes were committed.")
        return False

    # Verify deprecation
    verified = verify_deprecation()

    if verified:
        print("\n✅ Migration completed successfully!")
        print("\nNext Steps:")
        print("  1. Rule 8 is now inactive by default")
        print("  2. Test inventory generator (v2.0) no longer injects Rule 8 anomalies")
        print("  3. Expected anomaly count reduced from 35 to 30")
        print("  4. Users can still manually enable Rule 8 if needed (not recommended)")
        return True
    else:
        print("\n⚠️  Migration completed but verification failed")
        print("   Please check the database manually")
        return False


if __name__ == '__main__':
    """
    Run this migration standalone

    Usage:
        cd backend/src
        python migrations/deprecate_rule8_location_mapping.py
    """

    # Initialize Flask app context
    try:
        from app import app
        with app.app_context():
            run_migration()
    except ImportError:
        print("\n❌ ERROR: Could not import Flask app")
        print("   Make sure you're running from backend/src directory")
        print("\n   Usage:")
        print("     cd backend/src")
        print("     python migrations/deprecate_rule8_location_mapping.py")
