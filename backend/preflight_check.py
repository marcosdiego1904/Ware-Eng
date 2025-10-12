#!/usr/bin/env python3
"""
Pre-Flight Migration Checklist
===============================

Run this script BEFORE applying the migration to verify that your
environment is ready and identify any potential issues.

Usage:
    python preflight_check.py

This script will:
1. Check database connectivity
2. Verify PostgreSQL version
3. Check permissions
4. Identify missing columns
5. Estimate migration impact
6. Provide go/no-go recommendation
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))


def print_header(title):
    """Print a formatted section header"""
    print()
    print("=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_check(name, status, details=""):
    """Print a check result"""
    symbols = {"pass": "✅", "fail": "❌", "warn": "⚠️", "info": "ℹ️"}
    symbol = symbols.get(status, "•")
    print(f"{symbol} {name}")
    if details:
        for line in details.split('\n'):
            if line.strip():
                print(f"   {line}")


def run_preflight_checks():
    """Run comprehensive pre-flight checks"""

    print_header("PRE-FLIGHT MIGRATION CHECKLIST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    checks_passed = 0
    checks_failed = 0
    checks_warned = 0

    # Check 1: Environment Setup
    print_header("1. Environment Setup")

    try:
        from dotenv import load_dotenv
        load_dotenv()
        print_check("Environment variables", "pass", ".env file loaded")
        checks_passed += 1
    except Exception as e:
        print_check("Environment variables", "fail", f"Could not load .env: {e}")
        checks_failed += 1

    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Mask password in output
        safe_url = database_url
        if '@' in safe_url:
            parts = safe_url.split('@')
            if ':' in parts[0]:
                user_pass = parts[0].split('//')[-1]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    safe_url = safe_url.replace(user_pass, f"{user}:***")

        print_check("DATABASE_URL", "pass", f"Set to: {safe_url}")
        checks_passed += 1
    else:
        print_check("DATABASE_URL", "fail", "Environment variable not set")
        checks_failed += 1
        return False

    # Check 2: Import Dependencies
    print_header("2. Dependencies")

    try:
        from database import db
        from flask import Flask
        print_check("Flask imports", "pass", "Flask and database modules available")
        checks_passed += 1
    except ImportError as e:
        print_check("Flask imports", "fail", f"Missing dependencies: {e}")
        checks_failed += 1
        return False

    try:
        import psycopg2
        print_check("PostgreSQL driver", "pass", f"psycopg2 version {psycopg2.__version__}")
        checks_passed += 1
    except ImportError:
        print_check("PostgreSQL driver", "fail", "psycopg2 not installed")
        checks_failed += 1
        return False

    # Check 3: Database Connection
    print_header("3. Database Connectivity")

    try:
        app = Flask(__name__)

        # Handle Heroku postgres:// -> postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        with app.app_context():
            # Test connection
            result = db.session.execute(db.text("SELECT 1;"))
            result.scalar()
            print_check("Database connection", "pass", "Successfully connected to database")
            checks_passed += 1

            # Get PostgreSQL version
            result = db.session.execute(db.text("SELECT version();"))
            version = result.scalar()
            version_short = version.split(',')[0] if ',' in version else version[:50]

            # Check if version is adequate (9.5+)
            if 'PostgreSQL' in version:
                version_num = version.split('PostgreSQL ')[1].split('.')[0]
                if int(version_num) >= 9:
                    print_check("PostgreSQL version", "pass", version_short)
                    checks_passed += 1
                else:
                    print_check("PostgreSQL version", "warn",
                              f"{version_short}\nVersion 9.5+ recommended")
                    checks_warned += 1
            else:
                print_check("PostgreSQL version", "warn", version_short)
                checks_warned += 1

    except Exception as e:
        print_check("Database connection", "fail", f"Connection error: {e}")
        checks_failed += 1
        return False

    # Check 4: Table Existence
    print_header("4. Database Schema")

    try:
        with app.app_context():
            # Check if user table exists
            result = db.session.execute(db.text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'user'
                );
            """))

            if result.scalar():
                print_check("'user' table", "pass", "Table exists in database")
                checks_passed += 1
            else:
                print_check("'user' table", "fail", "Table does not exist")
                checks_failed += 1
                return False

            # Count users
            result = db.session.execute(db.text('SELECT COUNT(*) FROM "user";'))
            user_count = result.scalar()
            print_check("User count", "info", f"{user_count} users in database")

    except Exception as e:
        print_check("Table verification", "fail", f"Error: {e}")
        checks_failed += 1
        return False

    # Check 5: Missing Columns
    print_header("5. Missing Columns Analysis")

    try:
        with app.app_context():
            required_columns = [
                'clear_previous_anomalies',
                'show_clear_warning',
                'max_reports',
                'max_templates'
            ]

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
            missing_columns = set(required_columns) - set(existing_columns)

            if not missing_columns:
                print_check("Column status", "pass",
                          "All 4 columns already exist\nMigration not needed")
                checks_passed += 1
            else:
                print_check("Column status", "warn",
                          f"Missing {len(missing_columns)} columns:\n" +
                          "\n".join(f"  - {col}" for col in missing_columns) +
                          "\nMigration required")
                checks_warned += 1

    except Exception as e:
        print_check("Column analysis", "fail", f"Error: {e}")
        checks_failed += 1
        return False

    # Check 6: Permissions
    print_header("6. Database Permissions")

    try:
        with app.app_context():
            # Check ALTER TABLE permission
            result = db.session.execute(db.text("""
                SELECT has_table_privilege(current_user, 'user', 'UPDATE');
            """))

            has_permission = result.scalar()
            if has_permission:
                print_check("ALTER TABLE permission", "pass",
                          "User has required permissions")
                checks_passed += 1
            else:
                print_check("ALTER TABLE permission", "fail",
                          "User lacks ALTER TABLE permission")
                checks_failed += 1
                return False

    except Exception as e:
        print_check("Permission check", "warn",
                  f"Could not verify permissions: {e}\nProceed with caution")
        checks_warned += 1

    # Check 7: Migration Files
    print_header("7. Migration Files")

    migration_file = project_root / 'migrations' / 'add_user_analysis_preferences.sql'
    if migration_file.exists():
        size = migration_file.stat().st_size
        print_check("Migration SQL", "pass",
                  f"File exists: {migration_file.name} ({size} bytes)")
        checks_passed += 1
    else:
        print_check("Migration SQL", "fail",
                  f"File not found: {migration_file}")
        checks_failed += 1
        return False

    runner_file = project_root / 'run_user_preferences_migration.py'
    if runner_file.exists():
        print_check("Migration runner", "pass",
                  f"File exists: {runner_file.name}")
        checks_passed += 1
    else:
        print_check("Migration runner", "warn",
                  "Runner script not found (optional)")
        checks_warned += 1

    # Check 8: Backup Recommendation
    print_header("8. Backup Status")

    print_check("Backup recommendation", "info",
              "⚠️  Have you created a database backup?\n" +
              "This is MANDATORY before running any migration.\n" +
              "Even though this migration is safe, backups are essential.")

    # Summary
    print_header("PRE-FLIGHT SUMMARY")

    print()
    print(f"  Checks Passed:  {checks_passed} ✅")
    print(f"  Checks Failed:  {checks_failed} ❌")
    print(f"  Warnings:       {checks_warned} ⚠️")
    print()

    if checks_failed == 0:
        if missing_columns:
            print("  🟢 GO - Environment is ready for migration")
            print()
            print("  Next steps:")
            print("  1. Create database backup (MANDATORY)")
            print("  2. Run: python run_user_preferences_migration.py")
            print("     OR: psql $DATABASE_URL -f migrations/add_user_analysis_preferences.sql")
            print()
        else:
            print("  🟡 Migration not needed - all columns already exist")
            print()
            print("  Your database schema is already up to date.")
            print()
    else:
        print("  🔴 NO-GO - Fix issues above before proceeding")
        print()
        print("  Critical issues must be resolved before migration.")
        print("  Review the failed checks above.")
        print()

    print("=" * 80)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    return checks_failed == 0


if __name__ == '__main__':
    try:
        success = run_preflight_checks()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print()
        print("Pre-flight check cancelled by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print()
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
