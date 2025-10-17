#!/usr/bin/env python3
"""
Emergency fix for missing exclusion_rules column
This script fixes the transaction error by handling each column separately
"""

import os
import sys
from sqlalchemy import text

# Add the backend src directory to the path
backend_src = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_src)

from app import app
from database import db

def add_exclusion_rules_column():
    """Add exclusion_rules column using PostgreSQL-specific syntax"""

    print("Checking rule table schema...")

    try:
        with db.engine.connect() as conn:
            # Use DO block for PostgreSQL to handle column existence check
            sql = text("""
                DO $$
                BEGIN
                    -- Check if exclusion_rules column exists
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'rule'
                        AND column_name = 'exclusion_rules'
                    ) THEN
                        -- Add the column
                        ALTER TABLE rule ADD COLUMN exclusion_rules TEXT;
                        RAISE NOTICE 'Added exclusion_rules column to rule table';
                    ELSE
                        RAISE NOTICE 'exclusion_rules column already exists';
                    END IF;

                    -- Check if precedence_level column exists
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'rule'
                        AND column_name = 'precedence_level'
                    ) THEN
                        -- Add the column
                        ALTER TABLE rule ADD COLUMN precedence_level INTEGER DEFAULT 4;
                        RAISE NOTICE 'Added precedence_level column to rule table';
                    ELSE
                        RAISE NOTICE 'precedence_level column already exists';
                    END IF;
                END $$;
            """)

            conn.execute(sql)
            conn.commit()
            print("[OK] Column check and creation completed successfully")

            # Verify the columns exist
            verify_sql = text("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = 'rule'
                AND column_name IN ('exclusion_rules', 'precedence_level')
                ORDER BY column_name;
            """)

            result = conn.execute(verify_sql)
            columns = result.fetchall()

            print("\n[VERIFICATION] Columns in rule table:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")

            return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    """Run the fix"""
    print("="*60)
    print("Emergency Fix: Adding Missing exclusion_rules Column")
    print("="*60)

    with app.app_context():
        success = add_exclusion_rules_column()

        if success:
            print("\n" + "="*60)
            print("[SUCCESS] Migration completed successfully!")
            print("="*60)
            print("\nYou can now run your analysis without errors.")
        else:
            print("\n" + "="*60)
            print("[FAILED] Migration failed!")
            print("="*60)
            print("\nPlease check the error messages above.")

if __name__ == "__main__":
    main()
