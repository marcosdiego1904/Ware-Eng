"""
Create Admin and Pilot Users for Analytics Pilot Program

This script creates:
1. Admin user with access to pilot analytics dashboard
2. Pilot user for testing the application

Usage:
    python create_pilot_users.py
"""

import os
import sys
import logging

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_users(admin_username, admin_password, pilot_username, pilot_password,
                pilot_max_reports=10, pilot_max_templates=10):
    """
    Create admin and pilot users

    Args:
        admin_username: Username for admin account
        admin_password: Password for admin account
        pilot_username: Username for pilot user
        pilot_password: Password for pilot user
        pilot_max_reports: Max reports pilot user can create
        pilot_max_templates: Max templates pilot user can create
    """
    try:
        # Import database and models
        from database import db
        from core_models import User

        # Create Flask app to get db context
        from flask import Flask
        from dotenv import load_dotenv

        load_dotenv()

        app = Flask(__name__)

        # Database configuration
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # Fix postgres:// to postgresql:// for SQLAlchemy
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        else:
            # Fallback to SQLite for development
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'

        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize db with app
        db.init_app(app)

        with app.app_context():
            # Check if users already exist
            existing_admin = User.query.filter_by(username=admin_username).first()
            existing_pilot = User.query.filter_by(username=pilot_username).first()

            if existing_admin:
                logger.warning(f"Admin user '{admin_username}' already exists. Updating is_admin flag...")
                existing_admin.is_admin = True
                db.session.commit()
                print(f"[INFO] Updated existing user '{admin_username}' to admin")
            else:
                # Create admin user
                admin_user = User()
                admin_user.username = admin_username
                admin_user.set_password(admin_password)
                admin_user.is_admin = True
                admin_user.max_reports = 999  # Unlimited for admin
                admin_user.max_templates = 999

                db.session.add(admin_user)
                db.session.commit()

                logger.info(f"Created admin user: {admin_username}")
                print(f"[SUCCESS] Admin user '{admin_username}' created successfully")
                print(f"  - Username: {admin_username}")
                print(f"  - is_admin: True")
                print(f"  - Access: Pilot Analytics Dashboard")

            if existing_pilot:
                logger.warning(f"Pilot user '{pilot_username}' already exists. Skipping creation...")
                print(f"[INFO] Pilot user '{pilot_username}' already exists")
            else:
                # Create pilot user
                pilot_user = User()
                pilot_user.username = pilot_username
                pilot_user.set_password(pilot_password)
                pilot_user.is_admin = False
                pilot_user.max_reports = pilot_max_reports
                pilot_user.max_templates = pilot_max_templates

                db.session.add(pilot_user)
                db.session.commit()

                logger.info(f"Created pilot user: {pilot_username}")
                print(f"[SUCCESS] Pilot user '{pilot_username}' created successfully")
                print(f"  - Username: {pilot_username}")
                print(f"  - is_admin: False")
                print(f"  - Max Reports: {pilot_max_reports}")
                print(f"  - Max Templates: {pilot_max_templates}")

            print("\n[SUCCESS] User setup completed!")
            print("\nNext steps:")
            print("1. Admin user can access: /admin/pilot-analytics")
            print("2. Pilot user can use the app normally")
            print("3. All activity will be tracked in analytics")

            return True

    except Exception as e:
        logger.error(f"User creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n[ERROR] User creation failed. Check logs for details.")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Pilot Analytics User Setup")
    print("=" * 60)
    print()

    # Get admin user details
    print("ADMIN USER SETUP")
    print("-" * 60)
    admin_username = input("Enter admin username: ").strip()
    admin_password = input("Enter admin password: ").strip()

    print()

    # Get pilot user details
    print("PILOT USER SETUP")
    print("-" * 60)
    pilot_username = input("Enter pilot username: ").strip()
    pilot_password = input("Enter pilot password: ").strip()

    # Optional: resource limits
    pilot_max_reports_input = input("Max reports for pilot user (default 10): ").strip()
    pilot_max_reports = int(pilot_max_reports_input) if pilot_max_reports_input else 10

    pilot_max_templates_input = input("Max templates for pilot user (default 10): ").strip()
    pilot_max_templates = int(pilot_max_templates_input) if pilot_max_templates_input else 10

    print()
    print("=" * 60)
    print("Creating users...")
    print("=" * 60)
    print()

    # Create users
    success = create_users(
        admin_username=admin_username,
        admin_password=admin_password,
        pilot_username=pilot_username,
        pilot_password=pilot_password,
        pilot_max_reports=pilot_max_reports,
        pilot_max_templates=pilot_max_templates
    )

    if success:
        print("\n" + "=" * 60)
        print("User credentials saved securely in database")
        print("=" * 60)
