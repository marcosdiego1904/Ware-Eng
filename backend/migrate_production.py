#!/usr/bin/env python3
"""
Production Database Migration Script
Creates tables and seeds default rules on production PostgreSQL database
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from seed_default_rules import create_default_categories, create_default_rules, create_basic_locations

def migrate_production():
    print("PRODUCTION DATABASE MIGRATION")
    print("="*50)
    
    with app.app_context():
        try:
            # Check if we're in production mode
            database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
            print(f"Database URL: {database_url[:50]}...")
            
            if 'postgresql' not in database_url:
                print("WARNING: Not connecting to PostgreSQL - are you sure this is production?")
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    print("Migration cancelled.")
                    return
            
            print("\n1. Creating database tables...")
            db.create_all()
            print("   Tables created successfully")
            
            print("\n2. Creating rule categories...")
            categories = create_default_categories()
            print(f"   Created {len(categories)} categories")
            
            print("\n3. Creating default rules...")
            rules = create_default_rules(categories)
            print(f"   Created {len(rules)} rules")
            
            print("\n4. Creating basic locations...")
            locations = create_basic_locations()
            print(f"   Created {len(locations)} locations")
            
            print("\n" + "="*50)
            print("PRODUCTION MIGRATION COMPLETED SUCCESSFULLY!")
            print("Your production database now has all required tables and rules.")
            print("="*50)
            
        except Exception as e:
            print(f"ERROR during migration: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    migrate_production()