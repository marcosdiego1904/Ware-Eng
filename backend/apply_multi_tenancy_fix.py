"""
Apply Multi-Tenancy Fix - Production-Ready

Non-interactive version that can be run in production environments.
Removes old single-column unique constraint and ensures compound constraint exists.
"""

import os
import sys
from sqlalchemy import text

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db

def apply_fix():
    """Apply the multi-tenancy constraint fix"""
    print("="*60)
    print("APPLYING MULTI-TENANCY FIX")
    print("="*60)

    with app.app_context():
        try:
            # Drop the old single-column unique constraint
            print("\n[1/3] Dropping old 'location_code_key' constraint...")
            db.session.execute(text("""
                ALTER TABLE location DROP CONSTRAINT IF EXISTS location_code_key;
            """))
            db.session.commit()
            print("[OK] Old constraint dropped")

            # Drop any unique index on code column alone
            print("\n[2/3] Dropping any unique index on 'code' column...")
            db.session.execute(text("""
                DROP INDEX IF EXISTS ix_location_code;
            """))
            db.session.commit()
            print("[OK] Unique index dropped (if existed)")

            # Ensure compound unique constraint exists
            print("\n[3/3] Ensuring compound unique constraint exists...")
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
            print("[SUCCESS] MULTI-TENANCY FIX APPLIED")
            print("="*60)
            print("\nUsers can now create locations with the same code")
            print("in different warehouses without conflicts.")
            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n[FAIL] ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("\nLocation Multi-Tenancy Constraint Fix")
    print("-" * 60)

    success = apply_fix()
    sys.exit(0 if success else 1)
