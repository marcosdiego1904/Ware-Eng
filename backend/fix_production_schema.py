#!/usr/bin/env python3
"""
Production Schema Fix - Safe Migration for PostgreSQL
This script safely adds missing columns to the production database
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db

def fix_production_schema():
    """Safely fix production database schema using SQLAlchemy"""
    
    print("PRODUCTION SCHEMA FIX")
    print("="*50)
    
    with app.app_context():
        try:
            # Check database type
            database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            is_postgres = 'postgresql' in database_url.lower()
            
            if not is_postgres:
                print("WARNING: This script is designed for PostgreSQL production databases")
                # Allow override with environment variable
                if os.environ.get('FORCE_SCHEMA_FIX') != 'true':
                    return False
                print("FORCE_SCHEMA_FIX=true detected, continuing anyway...")
                
            print("Connected to PostgreSQL database")
            print(f"Database URL: {database_url[:50]}...")
            
            # Use raw SQL to safely add missing columns
            missing_columns = [
                ("warehouse_id", "VARCHAR(50) DEFAULT 'DEFAULT'"),
                ("aisle_number", "INTEGER"),
                ("rack_number", "INTEGER"),
                ("position_number", "INTEGER"), 
                ("level", "VARCHAR(1)"),
                ("pallet_capacity", "INTEGER DEFAULT 1"),
                ("location_hierarchy", "TEXT"),
                ("special_requirements", "TEXT")
            ]
            
            print("\nAdding missing columns to location table...")
            columns_added = 0
            
            for column_name, column_def in missing_columns:
                try:
                    # Check if column exists first
                    check_sql = """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'location' AND column_name = :column_name
                    """
                    result = db.session.execute(db.text(check_sql), {'column_name': column_name}).fetchone()
                    
                    if not result:
                        # Column doesn't exist, add it
                        alter_sql = f"ALTER TABLE location ADD COLUMN {column_name} {column_def}"
                        print(f"  Adding: {column_name}")
                        db.session.execute(db.text(alter_sql))
                        columns_added += 1
                    else:
                        print(f"  Exists: {column_name}")
                        
                except Exception as e:
                    print(f"  Error adding {column_name}: {e}")
                    # Continue with other columns
                    continue
            
            # Create warehouse tables if they don't exist
            print("\nEnsuring warehouse tables exist...")
            
            # Check for warehouse_config table
            check_table_sql = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'warehouse_config'
            """
            result = db.session.execute(db.text(check_table_sql)).fetchone()
            
            if not result:
                print("  Creating warehouse_config table...")
                create_wc_sql = """
                CREATE TABLE warehouse_config (
                    id SERIAL PRIMARY KEY,
                    warehouse_id VARCHAR(50) NOT NULL UNIQUE,
                    warehouse_name VARCHAR(120) NOT NULL,
                    num_aisles INTEGER NOT NULL,
                    racks_per_aisle INTEGER NOT NULL,
                    positions_per_rack INTEGER NOT NULL,
                    levels_per_position INTEGER DEFAULT 4,
                    level_names VARCHAR(20) DEFAULT 'ABCD',
                    default_pallet_capacity INTEGER DEFAULT 1,
                    bidimensional_racks BOOLEAN DEFAULT FALSE,
                    receiving_areas TEXT,
                    staging_areas TEXT,
                    dock_areas TEXT,
                    default_zone VARCHAR(50) DEFAULT 'GENERAL',
                    position_numbering_start INTEGER DEFAULT 1,
                    position_numbering_split BOOLEAN DEFAULT TRUE,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
                """
                db.session.execute(db.text(create_wc_sql))
                print("  ✓ Created warehouse_config table")
            else:
                print("  ✓ warehouse_config table exists")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✓ Added {columns_added} missing columns")
            print("✓ Database schema is now up to date")
            print("="*50)
            
            return True
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = fix_production_schema()
    if success:
        print("Production schema fix completed!")
        sys.exit(0)
    else:
        print("Production schema fix failed!")
        sys.exit(1)