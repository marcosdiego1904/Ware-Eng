#!/usr/bin/env python3
"""
Simple Production Migration Script - Add Missing User Columns
Applies the migration to add user analysis preference columns.
Windows-compatible, no fancy Unicode characters.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def apply_migration():
    """Apply the user preferences migration to production database."""

    print("=" * 80)
    print("USER PREFERENCES MIGRATION")
    print("=" * 80)
    print()

    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL environment variable not set!")
        print()
        print("Please set DATABASE_URL to your PostgreSQL connection string:")
        print("Example: postgresql://user:password@host:port/database")
        return False

    # Mask password in output
    safe_url = database_url
    if '@' in database_url and ':' in database_url:
        parts = database_url.split('@')
        if len(parts) == 2:
            before_at = parts[0]
            if ':' in before_at:
                user_pass = before_at.split('://')[-1]
                user = user_pass.split(':')[0]
                safe_url = database_url.replace(user_pass, f"{user}:***")

    print(f"[INFO] Connecting to: {safe_url}")
    print()

    try:
        # Create engine
        engine = create_engine(database_url)

        # Test connection
        print("[STEP 1] Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"[OK] Connected to PostgreSQL: {version[:50]}...")
        print()

        # Check current schema
        print("[STEP 2] Checking current user table schema...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'user'
                ORDER BY ordinal_position
            """))
            columns = {row[0]: row for row in result.fetchall()}
            print(f"[OK] Found {len(columns)} columns in user table")

            # Check which columns are missing
            required_columns = {
                'clear_previous_anomalies': 'boolean',
                'show_clear_warning': 'boolean',
                'max_reports': 'integer',
                'max_templates': 'integer'
            }

            missing_columns = []
            for col_name, col_type in required_columns.items():
                if col_name not in columns:
                    missing_columns.append(col_name)
                    print(f"[MISSING] Column '{col_name}' not found")
                else:
                    print(f"[EXISTS] Column '{col_name}' already exists")
        print()

        if not missing_columns:
            print("[SUCCESS] All required columns already exist!")
            print("No migration needed.")
            return True

        # Apply migration
        print(f"[STEP 3] Adding {len(missing_columns)} missing column(s)...")
        print()

        migration_sql = """
        -- Add missing columns to user table
        DO $$
        BEGIN
            -- Add clear_previous_anomalies column
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='user' AND column_name='clear_previous_anomalies'
            ) THEN
                ALTER TABLE "user" ADD COLUMN clear_previous_anomalies BOOLEAN DEFAULT true NOT NULL;
                RAISE NOTICE 'Added column: clear_previous_anomalies';
            END IF;

            -- Add show_clear_warning column
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='user' AND column_name='show_clear_warning'
            ) THEN
                ALTER TABLE "user" ADD COLUMN show_clear_warning BOOLEAN DEFAULT true NOT NULL;
                RAISE NOTICE 'Added column: show_clear_warning';
            END IF;

            -- Add max_reports column
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='user' AND column_name='max_reports'
            ) THEN
                ALTER TABLE "user" ADD COLUMN max_reports INTEGER DEFAULT 100 NOT NULL;
                RAISE NOTICE 'Added column: max_reports';
            END IF;

            -- Add max_templates column
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='user' AND column_name='max_templates'
            ) THEN
                ALTER TABLE "user" ADD COLUMN max_templates INTEGER DEFAULT 50 NOT NULL;
                RAISE NOTICE 'Added column: max_templates';
            END IF;
        END $$;
        """

        with engine.begin() as conn:
            print("[EXECUTING] Running migration SQL...")
            conn.execute(text(migration_sql))
            print("[OK] Migration executed successfully")
        print()

        # Verify migration
        print("[STEP 4] Verifying migration...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'user'
                AND column_name IN (
                    'clear_previous_anomalies',
                    'show_clear_warning',
                    'max_reports',
                    'max_templates'
                )
                ORDER BY column_name
            """))

            verified_columns = list(result.fetchall())
            if len(verified_columns) == 4:
                print("[OK] All 4 columns verified:")
                for col in verified_columns:
                    print(f"  - {col[0]} ({col[1]})")
            else:
                print(f"[WARNING] Expected 4 columns, found {len(verified_columns)}")
        print()

        # Test a query
        print("[STEP 5] Testing user query...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, username, clear_previous_anomalies,
                       show_clear_warning, max_reports, max_templates
                FROM "user"
                LIMIT 1
            """))
            user = result.fetchone()
            if user:
                print(f"[OK] Successfully queried user table")
                print(f"  Sample user: {user[1]}")
                print(f"  clear_previous_anomalies: {user[2]}")
                print(f"  show_clear_warning: {user[3]}")
                print(f"  max_reports: {user[4]}")
                print(f"  max_templates: {user[5]}")
            else:
                print("[INFO] No users in database yet (this is okay)")
        print()

        print("=" * 80)
        print("[SUCCESS] MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Test login at your frontend: https://ware-eng.vercel.app/auth")
        print("2. Check production logs to confirm no more errors")
        print("3. Monitor for any other issues")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 80)
        print("[ERROR] MIGRATION FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        print("The database was not modified (transaction rolled back).")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)
