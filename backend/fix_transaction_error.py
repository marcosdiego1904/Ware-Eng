"""
Fix PostgreSQL Transaction Error - Orphaned Location Records
This script identifies and fixes location records with invalid user references
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import text
from database import db
from core_models import User
from models import Location
from app import app

def diagnose_orphaned_locations():
    """Identify locations with invalid user references"""
    print("\n" + "="*70)
    print("DIAGNOSING ORPHANED LOCATION RECORDS")
    print("="*70 + "\n")

    with app.app_context():
        # Query to find orphaned locations using raw SQL
        query = text("""
            SELECT
                l.id,
                l.code,
                l.warehouse_id,
                l.location_type,
                l.created_by,
                u.username as creator_name
            FROM location l
            LEFT JOIN "user" u ON l.created_by = u.id
            WHERE l.warehouse_id = 'DEFAULT'
            AND u.id IS NULL
            LIMIT 100
        """)

        try:
            result = db.session.execute(query)
            orphaned = result.fetchall()

            if orphaned:
                print(f"⚠️  FOUND {len(orphaned)} ORPHANED LOCATION RECORDS\n")
                print("Location ID | Code        | Type       | Invalid User ID")
                print("-" * 70)
                for loc in orphaned[:10]:  # Show first 10
                    print(f"{loc.id:11} | {loc.code:11} | {loc.location_type:10} | {loc.created_by}")

                if len(orphaned) > 10:
                    print(f"... and {len(orphaned) - 10} more orphaned records")

                return len(orphaned)
            else:
                print("✅ No orphaned location records found!")
                return 0

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during diagnosis: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def find_valid_user():
    """Find a valid user to assign orphaned locations to"""
    with app.app_context():
        try:
            # Try to find the first active user
            user = User.query.filter_by(is_active=True).order_by(User.created_at.asc()).first()

            if user:
                print(f"\n✅ Found valid user: {user.username} (ID: {user.id})")
                return user.id
            else:
                print("\n❌ No active users found in database!")
                return None

        except Exception as e:
            print(f"❌ Error finding valid user: {str(e)}")
            return None

def fix_orphaned_locations(target_user_id):
    """Update orphaned locations to use a valid user"""
    print("\n" + "="*70)
    print("FIXING ORPHANED LOCATION RECORDS")
    print("="*70 + "\n")

    with app.app_context():
        try:
            # Use raw SQL to update orphaned records
            update_query = text("""
                UPDATE location
                SET created_by = :user_id
                WHERE created_by NOT IN (SELECT id FROM "user")
            """)

            result = db.session.execute(update_query, {'user_id': target_user_id})
            db.session.commit()

            updated_count = result.rowcount
            print(f"✅ Updated {updated_count} orphaned location records")
            print(f"   All orphaned locations now assigned to user ID: {target_user_id}\n")

            return updated_count

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during fix: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def verify_fix():
    """Verify that no orphaned records remain"""
    print("\n" + "="*70)
    print("VERIFYING FIX")
    print("="*70 + "\n")

    with app.app_context():
        try:
            query = text("""
                SELECT COUNT(*) as orphaned_count
                FROM location l
                LEFT JOIN "user" u ON l.created_by = u.id
                WHERE u.id IS NULL
            """)

            result = db.session.execute(query)
            count = result.fetchone()[0]

            if count == 0:
                print("✅ SUCCESS! No orphaned location records remain.\n")
                return True
            else:
                print(f"⚠️  WARNING: Still found {count} orphaned records.\n")
                return False

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during verification: {str(e)}")
            return False

def main():
    """Main execution flow"""
    print("\n" + "="*70)
    print("POSTGRESQL TRANSACTION ERROR FIX")
    print("="*70)
    print("This script will fix orphaned location records causing transaction errors\n")

    # Step 1: Diagnose
    orphaned_count = diagnose_orphaned_locations()

    if orphaned_count is None:
        print("\n❌ DIAGNOSTIC FAILED - Cannot proceed")
        return 1

    if orphaned_count == 0:
        print("\n✅ NO ISSUES FOUND - Nothing to fix")
        return 0

    # Step 2: Find valid user
    target_user_id = find_valid_user()

    if target_user_id is None:
        print("\n❌ CANNOT FIND VALID USER - Cannot proceed")
        return 1

    # Step 3: Confirm fix
    print(f"\nReady to update {orphaned_count} orphaned location records.")
    print(f"They will be assigned to user ID: {target_user_id}")

    response = input("\nProceed with fix? (yes/no): ").strip().lower()

    if response != 'yes':
        print("\n⏸️  FIX CANCELLED - No changes made")
        return 0

    # Step 4: Apply fix
    updated_count = fix_orphaned_locations(target_user_id)

    if updated_count is None:
        print("\n❌ FIX FAILED")
        return 1

    # Step 5: Verify
    success = verify_fix()

    if success:
        print("="*70)
        print("TRANSACTION ERROR FIX COMPLETE")
        print("="*70)
        print("\n🎉 You can now restart your backend server.")
        print("   The transaction errors should be resolved.\n")
        return 0
    else:
        print("\n⚠️  FIX PARTIALLY SUCCESSFUL - Some issues may remain")
        return 1

if __name__ == '__main__':
    exit(main())
