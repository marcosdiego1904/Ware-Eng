#!/usr/bin/env python3
"""
PostgreSQL User Preferences Migration Runner
============================================

This script safely migrates the production PostgreSQL database to add
missing user preference and limit columns.

Missing columns being added:
- clear_previous_anomalies (BOOLEAN, default TRUE)
- show_clear_warning (BOOLEAN, default TRUE)
- max_reports (INTEGER, default 5)
- max_templates (INTEGER, default 5)

Usage:
    python run_user_preferences_migration.py

Features:
- Pre-flight validation
- Automatic database connection from environment
- Idempotent migration (safe to run multiple times)
- Comprehensive error handling
- Rollback on failure
- Post-migration verification
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def run_migration():
    """Execute the user preferences migration with comprehensive error handling"""

    print("=" * 80)
    print("PostgreSQL User Preferences Migration")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Import database connection
    try:
        from database import db
        from flask import Flask
        from dotenv import load_dotenv

        # Load environment variables
        load_dotenv()

        print("[1/6] Environment and imports loaded successfully")

    except ImportError as e:
        print(f"ERROR: Failed to import required modules: {e}")
        print("Make sure you're running from the backend directory")
        return False

    # Create Flask app for database context
    try:
        app = Flask(__name__)

        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')

        if not database_url:
            print("ERROR: DATABASE_URL environment variable not set")
            print("Please set DATABASE_URL in your .env file or environment")
            return False

        # Handle Heroku postgres:// -> postgresql:// conversion
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize database with app
        db.init_app(app)

        print(f"[2/6] Database connection configured")
        print(f"      Database: {database_url.split('@')[1] if '@' in database_url else 'configured'}")

    except Exception as e:
        print(f"ERROR: Failed to configure database: {e}")
        return False

    # Read migration SQL file
    try:
        migration_file = project_root / 'migrations' / 'add_user_analysis_preferences.sql'

        if not migration_file.exists():
            print(f"ERROR: Migration file not found: {migration_file}")
            return False

        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()

        print(f"[3/6] Migration SQL loaded from: {migration_file.name}")

    except Exception as e:
        print(f"ERROR: Failed to read migration file: {e}")
        return False

    # Pre-flight checks
    try:
        with app.app_context():
            # Test database connection
            result = db.session.execute(db.text("SELECT version();"))
            version = result.scalar()
            print(f"[4/6] Database connection verified")
            print(f"      PostgreSQL version: {version}")

            # Check if user table exists
            result = db.session.execute(db.text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'user'
                );
            """))

            if not result.scalar():
                print("ERROR: 'user' table does not exist in the database")
                return False

            # Check current columns
            result = db.session.execute(db.text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'user'
                AND column_name IN (
                    'clear_previous_anomalies',
                    'show_clear_warning',
                    'max_reports',
                    'max_templates'
                )
                ORDER BY column_name;
            """))

            existing_columns = [row[0] for row in result]

            print(f"[5/6] Pre-flight checks completed")
            print(f"      Existing columns: {len(existing_columns)} out of 4")

            if existing_columns:
                print(f"      Already present: {', '.join(existing_columns)}")

            if len(existing_columns) == 4:
                print()
                print("INFO: All columns already exist. Migration not needed.")
                print("      Run verification query to confirm column definitions.")
                return True

            missing_columns = set(['clear_previous_anomalies', 'show_clear_warning',
                                  'max_reports', 'max_templates']) - set(existing_columns)
            print(f"      Will add: {', '.join(missing_columns)}")

    except Exception as e:
        print(f"ERROR: Pre-flight checks failed: {e}")
        return False

    # Execute migration
    try:
        with app.app_context():
            print()
            print("[6/6] Executing migration...")
            print("-" * 80)

            # Execute the migration SQL (it's wrapped in a transaction)
            db.session.execute(db.text(migration_sql))
            db.session.commit()

            print("-" * 80)
            print()
            print("SUCCESS: Migration executed successfully!")

    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        print("      Database changes have been rolled back automatically")
        return False

    # Post-migration verification
    try:
        with app.app_context():
            print()
            print("Post-Migration Verification")
            print("-" * 80)

            # Verify all columns exist
            result = db.session.execute(db.text("""
                SELECT
                    column_name,
                    data_type,
                    column_default,
                    is_nullable
                FROM information_schema.columns
                WHERE table_name = 'user'
                AND column_name IN (
                    'clear_previous_anomalies',
                    'show_clear_warning',
                    'max_reports',
                    'max_templates'
                )
                ORDER BY column_name;
            """))

            columns = result.fetchall()

            if len(columns) == 4:
                print("All 4 columns verified successfully:")
                print()
                for col in columns:
                    col_name, data_type, default, nullable = col
                    print(f"  {col_name:30} {data_type:15} DEFAULT {default:20} NULL: {nullable}")
                print()
                print("VERIFICATION PASSED")
            else:
                print(f"WARNING: Only {len(columns)} out of 4 columns found")
                return False

            # Count users
            result = db.session.execute(db.text("SELECT COUNT(*) FROM \"user\";"))
            user_count = result.scalar()
            print(f"Total users in database: {user_count}")
            print(f"All users will have default values applied")

    except Exception as e:
        print(f"ERROR: Post-migration verification failed: {e}")
        return False

    print()
    print("=" * 80)
    print("Migration completed successfully!")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return True


def print_verification_query():
    """Print the manual verification query for reference"""
    print()
    print("Manual Verification Query (optional):")
    print("-" * 80)
    print("""
SELECT
    id,
    username,
    clear_previous_anomalies,
    show_clear_warning,
    max_reports,
    max_templates
FROM "user"
LIMIT 10;
""")
    print("-" * 80)


if __name__ == '__main__':
    print()
    print("IMPORTANT: This script will modify your production PostgreSQL database")
    print("           Ensure you have a recent backup before proceeding.")
    print()

    # Safety check - require explicit confirmation in production
    if os.environ.get('PRODUCTION') == 'true':
        response = input("You are running in PRODUCTION mode. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled by user")
            sys.exit(0)

    try:
        success = run_migration()

        if success:
            print_verification_query()
            sys.exit(0)
        else:
            print()
            print("Migration failed. Please review errors above and try again.")
            sys.exit(1)

    except KeyboardInterrupt:
        print()
        print("Migration cancelled by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print()
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
