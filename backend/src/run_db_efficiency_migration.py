"""
Database Efficiency Migration Runner
Automatically detects database type (SQLite/PostgreSQL) and runs appropriate migrations
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from core_models import User, InvitationCode
from sqlalchemy import text, inspect

def detect_database_type():
    """Detect if we're using SQLite or PostgreSQL"""
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'postgresql' in db_uri.lower():
        return 'postgresql'
    elif 'sqlite' in db_uri.lower():
        return 'sqlite'
    else:
        return 'unknown'

def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def table_exists(table_name):
    """Check if a table exists"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def migrate_user_limits():
    """Add max_reports and max_templates columns to user table"""
    print("\n=== Migrating User Limits ===")

    try:
        db_type = detect_database_type()
        print(f"Database type: {db_type}")

        # Check if columns already exist
        has_max_reports = column_exists('user', 'max_reports')
        has_max_templates = column_exists('user', 'max_templates')

        if has_max_reports and has_max_templates:
            print("[OK] User limit columns already exist - skipping")
            return True

        print("Adding user limit columns...")

        if db_type == 'sqlite':
            # SQLite syntax
            if not has_max_reports:
                db.session.execute(text(
                    "ALTER TABLE user ADD COLUMN max_reports INTEGER DEFAULT 5 NOT NULL"
                ))
                print("  [OK] Added max_reports column")

            if not has_max_templates:
                db.session.execute(text(
                    "ALTER TABLE user ADD COLUMN max_templates INTEGER DEFAULT 5 NOT NULL"
                ))
                print("  [OK] Added max_templates column")

        elif db_type == 'postgresql':
            # PostgreSQL syntax
            if not has_max_reports:
                db.session.execute(text(
                    "ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS max_reports INTEGER DEFAULT 5 NOT NULL"
                ))
                print("  [OK] Added max_reports column")

            if not has_max_templates:
                db.session.execute(text(
                    "ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS max_templates INTEGER DEFAULT 5 NOT NULL"
                ))
                print("  [OK] Added max_templates column")

        db.session.commit()
        print("[OK] User limits migration completed successfully")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error migrating user limits: {e}")
        return False

def migrate_invitation_system():
    """Create invitation_code table"""
    print("\n=== Migrating Invitation System ===")

    try:
        # Check if table already exists
        if table_exists('invitation_code'):
            print("[OK] Invitation code table already exists - skipping")
            return True

        print("Creating invitation_code table...")

        # Use SQLAlchemy to create the table (works for both databases)
        db.create_all()

        print("[OK] Invitation system migration completed successfully")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error migrating invitation system: {e}")
        return False

def verify_migrations():
    """Verify that migrations were successful"""
    print("\n=== Verifying Migrations ===")

    try:
        # Check user columns
        user = User.query.first()
        if user:
            print(f"[OK] User limits: max_reports={user.max_reports}, max_templates={user.max_templates}")
        else:
            print("[WARN] No users found to verify (this is OK for new databases)")

        # Check invitation table
        invitation_count = InvitationCode.query.count()
        print(f"[OK] Invitation codes table: {invitation_count} invitations")

        print("\n[OK] All migrations verified successfully!")
        return True

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False

def create_initial_invitation():
    """Create an initial invitation code for bootstrapping"""
    print("\n=== Creating Bootstrap Invitation ===")

    try:
        # Check if any invitations exist
        if InvitationCode.query.count() > 0:
            print("[OK] Invitations already exist - skipping bootstrap")
            return True

        # Create a bootstrap invitation with multiple uses
        bootstrap_code = "BOOTSTRAP2025"
        invitation = InvitationCode(
            code=bootstrap_code,
            created_by=None,  # System-generated
            max_uses=10,  # Allow 10 initial users
            notes="Bootstrap invitation for initial users"
        )

        db.session.add(invitation)
        db.session.commit()

        print(f"[OK] Bootstrap invitation created: {bootstrap_code}")
        print(f"  Max uses: {invitation.max_uses}")
        print(f"  Share this code with initial users!")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error creating bootstrap invitation: {e}")
        return False

def main():
    """Run all migrations"""
    print("=" * 60)
    print("DATABASE EFFICIENCY MIGRATION")
    print("=" * 60)

    with app.app_context():
        # Run migrations
        user_limits_ok = migrate_user_limits()
        invitation_ok = migrate_invitation_system()

        if user_limits_ok and invitation_ok:
            # Verify migrations
            verification_ok = verify_migrations()

            if verification_ok:
                # Create bootstrap invitation
                create_initial_invitation()

                print("\n" + "=" * 60)
                print("[SUCCESS] ALL MIGRATIONS COMPLETED SUCCESSFULLY!")
                print("=" * 60)
                print("\nNext steps:")
                print("1. Test template creation (should be limited to 5 per user)")
                print("2. Test registration with invitation code")
                print("3. Check monitoring endpoint: GET /api/v1/admin/db-stats")
                print("=" * 60)
                return 0
            else:
                print("\n[ERROR] Verification failed - please check errors above")
                return 1
        else:
            print("\n[ERROR] Migration failed - please check errors above")
            return 1

if __name__ == '__main__':
    sys.exit(main())
