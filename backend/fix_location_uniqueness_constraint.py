"""
Fix Location Uniqueness Constraint for Multi-Tenancy

This script removes the old single-column unique constraint on location.code
and ensures only the compound (warehouse_id, code) constraint exists.

Run this once to fix the production database.
"""

import os
import sys
from sqlalchemy import text, inspect

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location

def check_constraints():
    """Check what constraints exist on the location table"""
    print("\n" + "="*60)
    print("CHECKING EXISTING CONSTRAINTS")
    print("="*60)

    with app.app_context():
        inspector = inspect(db.engine)
        constraints = inspector.get_unique_constraints('location')

        print(f"\nFound {len(constraints)} unique constraints on 'location' table:")
        for constraint in constraints:
            print(f"  - {constraint['name']}: {constraint['column_names']}")

        # Also check indexes
        indexes = inspector.get_indexes('location')
        unique_indexes = [idx for idx in indexes if idx.get('unique')]

        if unique_indexes:
            print(f"\nFound {len(unique_indexes)} unique indexes:")
            for idx in unique_indexes:
                print(f"  - {idx['name']}: {idx['column_names']}")

        return constraints, unique_indexes

def fix_constraints():
    """Remove old single-column constraint and ensure compound constraint exists"""
    print("\n" + "="*60)
    print("FIXING LOCATION UNIQUENESS CONSTRAINTS")
    print("="*60)

    with app.app_context():
        try:
            # Drop the old single-column unique constraint
            print("\n[1/3] Dropping old 'location_code_key' constraint...")
            db.session.execute(text("""
                ALTER TABLE location DROP CONSTRAINT IF EXISTS location_code_key;
            """))
            db.session.commit()
            print("[OK] Old constraint dropped successfully")

            # Also drop any unique index on code column alone
            print("\n[2/3] Dropping any unique index on 'code' column...")
            db.session.execute(text("""
                DROP INDEX IF EXISTS ix_location_code;
            """))
            db.session.commit()
            print("[OK] Unique index dropped (if it existed)")

            # Ensure compound unique constraint exists
            print("\n[3/3] Creating compound unique constraint (if not exists)...")
            db.session.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint
                        WHERE conname = 'uq_location_warehouse_code'
                    ) THEN
                        ALTER TABLE location
                        ADD CONSTRAINT uq_location_warehouse_code
                        UNIQUE (warehouse_id, code);
                    END IF;
                END $$;
            """))
            db.session.commit()
            print("[OK] Compound unique constraint ensured")

            print("\n" + "="*60)
            print("[OK] CONSTRAINTS FIXED SUCCESSFULLY")
            print("="*60)

        except Exception as e:
            db.session.rollback()
            print(f"\n[FAIL] ERROR: {e}")
            raise

def verify_fix():
    """Verify that the fix worked"""
    print("\n" + "="*60)
    print("VERIFYING FIX")
    print("="*60)

    with app.app_context():
        # Check constraints again
        constraints, unique_indexes = check_constraints()

        # Verify expectations
        print("\n[OK] VERIFICATION:")

        # Should have compound constraint
        compound_exists = any(
            set(c['column_names']) == {'warehouse_id', 'code'}
            for c in constraints
        )
        print(f"  {'[OK]' if compound_exists else '[FAIL]'} Compound constraint (warehouse_id, code) exists")

        # Should NOT have single-column constraint on 'code'
        single_code_exists = any(
            c['column_names'] == ['code']
            for c in constraints
        )
        print(f"  {'[FAIL]' if single_code_exists else '[OK]'} Single-column constraint on 'code' does NOT exist")

        # Should NOT have unique index on 'code' alone
        single_code_index = any(
            idx['column_names'] == ['code']
            for idx in unique_indexes
        )
        print(f"  {'[FAIL]' if single_code_index else '[OK]'} Unique index on 'code' does NOT exist")

        if compound_exists and not single_code_exists and not single_code_index:
            print("\n[SUCCESS] SUCCESS! Multi-tenancy is now properly enforced.")
            print("   Users can now create locations with the same code in different warehouses.")
            return True
        else:
            print("\n[WARNING]  WARNING: Verification failed. Manual intervention may be needed.")
            return False

def test_multi_tenancy():
    """Test that multi-tenancy works"""
    print("\n" + "="*60)
    print("TESTING MULTI-TENANCY")
    print("="*60)

    with app.app_context():
        try:
            # Try creating same location code in two different warehouses
            test_code = "TEST-MULTI-01"

            # Clean up any existing test locations
            Location.query.filter_by(code=test_code).delete()
            db.session.commit()

            print(f"\n[1/2] Creating location '{test_code}' in warehouse 'TEST_WAREHOUSE_A'...")
            loc1 = Location(
                code=test_code,
                warehouse_id='TEST_WAREHOUSE_A',
                location_type='STORAGE',
                capacity=1,
                created_by=1  # Assumes user ID 1 exists
            )
            db.session.add(loc1)
            db.session.commit()
            print("[OK] Location created successfully")

            print(f"\n[2/2] Creating location '{test_code}' in warehouse 'TEST_WAREHOUSE_B'...")
            loc2 = Location(
                code=test_code,
                warehouse_id='TEST_WAREHOUSE_B',
                location_type='STORAGE',
                capacity=1,
                created_by=1
            )
            db.session.add(loc2)
            db.session.commit()
            print("[OK] Location created successfully")

            # Clean up test data
            print("\n[Cleanup] Removing test locations...")
            Location.query.filter_by(code=test_code).delete()
            db.session.commit()

            print("\n[SUCCESS] MULTI-TENANCY TEST PASSED!")
            print("   Same location code can exist in different warehouses.")
            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n[FAIL] MULTI-TENANCY TEST FAILED: {e}")
            return False

if __name__ == '__main__':
    print("""
===============================================================
  Location Multi-Tenancy Constraint Fix

  This script fixes the database schema to properly support
  multi-tenancy by removing the old single-column unique
  constraint on 'code' and ensuring the compound constraint
  (warehouse_id, code) is in place.
===============================================================
    """)

    try:
        # Step 1: Check current state
        check_constraints()

        # Step 2: Fix constraints
        input("\nPress Enter to apply the fix (or Ctrl+C to cancel)...")
        fix_constraints()

        # Step 3: Verify fix
        if verify_fix():
            # Step 4: Test multi-tenancy
            input("\nPress Enter to run multi-tenancy test (or Ctrl+C to skip)...")
            test_multi_tenancy()

        print("\n" + "="*60)
        print("ALL DONE!")
        print("="*60)
        print("\nYou can now:")
        print("  1. Deploy this fix to production")
        print("  2. Users will be able to create locations with the same code")
        print("     in different warehouses without conflicts")
        print()

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
