"""
Simple script to deprecate Rule 8 via database update
Run from backend/: python deprecate_rule8_simple.py
"""

import sqlite3
import os
from datetime import datetime
import json

def deprecate_rule8():
    """Deprecate Rule 8 using direct SQL"""

    # Database path
    db_path = os.path.join('instance', 'database.db')

    if not os.path.exists(db_path):
        print(f"\n[ERROR] Database not found at {db_path}")
        print("        Make sure you're running from the backend/ directory")
        return False

    print("\n" + "="*60)
    print("DEPRECATING RULE 8 (Location Mapping Errors)")
    print("="*60)

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Find Rule 8
        cursor.execute("""
            SELECT id, name, is_active, priority, description, parameters
            FROM rule
            WHERE rule_type = 'LOCATION_MAPPING_ERROR'
        """)

        rule = cursor.fetchone()

        if not rule:
            print("\n[WARNING] Rule 8 (LOCATION_MAPPING_ERROR) not found in database.")
            conn.close()
            return False

        rule_id, name, is_active, priority, description, parameters = rule

        print(f"\n[OK] Found Rule 8:")
        print(f"  ID: {rule_id}")
        print(f"  Name: {name}")
        print(f"  Active: {bool(is_active)}")
        print(f"  Priority: {priority}")

        # Prepare update
        new_name = "[DEPRECATED] Location Type Mismatches"
        new_description = """[DEPRECATED] This rule is no longer necessary.

**Why Deprecated:**
- Real-world inventory reports don't include 'location_type' column
- WareWise auto-detects location types from location codes
- This rule caused 15 false positives in testing
- Only catches manual data entry errors (extremely rare)

**Recommendation:** Leave disabled and rely on auto-detection.

Deprecated: 2025-01-09"""

        # Update parameters
        try:
            params = json.loads(parameters) if parameters else {}
        except:
            params = {}

        params['_deprecated'] = True
        params['_deprecated_date'] = '2025-01-09'
        new_parameters = json.dumps(params)

        # Update rule
        cursor.execute("""
            UPDATE rule
            SET is_active = 0,
                name = ?,
                description = ?,
                priority = 'LOW',
                parameters = ?,
                updated_at = ?
            WHERE id = ?
        """, (new_name, new_description, new_parameters, datetime.utcnow(), rule_id))

        conn.commit()

        print("\n[SUCCESS] Rule 8 has been deprecated!")
        print("\nChanges Applied:")
        print(f"  - is_active: 1 -> 0 (False)")
        print(f"  - name: '{name}' -> '{new_name}'")
        print(f"  - description: Updated with deprecation notice")
        print(f"  - priority: '{priority}' -> 'LOW'")
        print(f"  - parameters: Added deprecation metadata")

        # Verify
        cursor.execute("""
            SELECT name, is_active, priority
            FROM rule
            WHERE id = ?
        """, (rule_id,))

        updated_rule = cursor.fetchone()
        print("\n[OK] Verification:")
        print(f"  Name: {updated_rule[0]}")
        print(f"  Active: {bool(updated_rule[1])}")
        print(f"  Priority: {updated_rule[2]}")

        conn.close()

        print("\n" + "="*60)
        print("RULE 8 DEPRECATION COMPLETE")
        print("="*60)
        print("\n[NOTE] Expected anomaly count: 35 -> 30 (6 active rules)")
        print("       Test generator v2.0 will skip Rule 8 anomalies")
        print("\n")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        if 'conn' in locals():
            conn.close()
        return False


if __name__ == '__main__':
    import sys
    success = deprecate_rule8()
    sys.exit(0 if success else 1)
