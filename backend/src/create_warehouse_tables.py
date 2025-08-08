#!/usr/bin/env python3
"""
Create warehouse management tables for both SQLite and PostgreSQL
This script creates the missing WarehouseConfig and WarehouseTemplate tables
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import app
from database import db
from models import WarehouseConfig, WarehouseTemplate
from core_models import User

def create_warehouse_tables():
    """Create warehouse management tables"""
    
    print("Creating warehouse management tables...")
    
    with app.app_context():
        try:
            # Check database type
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            is_postgres = 'postgresql' in db_uri.lower()
            print(f"Database type: {'PostgreSQL' if is_postgres else 'SQLite'}")
            print(f"Database URI: {db_uri}")
            
            # Create all tables (this should create missing tables)
            print("Creating tables with db.create_all()...")
            db.create_all()
            print("Tables created successfully")
            
            # Test the tables by trying to count records
            try:
                config_count = db.session.execute(db.text("SELECT COUNT(*) FROM warehouse_config")).scalar()
                template_count = db.session.execute(db.text("SELECT COUNT(*) FROM warehouse_template")).scalar()
                print(f"warehouse_config table: {config_count} records")
                print(f"warehouse_template table: {template_count} records")
            except Exception as e:
                print(f"Error accessing tables: {e}")
                # Tables don't exist, create them manually
                return create_tables_manually()
            
            # Create default warehouse config if none exists
            if config_count == 0:
                print("Creating default warehouse configuration...")
                
                # Get first user for created_by
                user = User.query.first()
                if not user:
                    print("No users found, creating test user first...")
                    test_user = User(username='admin')
                    test_user.set_password('admin123')
                    db.session.add(test_user)
                    db.session.commit()
                    user = test_user
                
                config = WarehouseConfig(
                    warehouse_id='DEFAULT',
                    warehouse_name='Default Warehouse',
                    num_aisles=4,
                    racks_per_aisle=2,
                    positions_per_rack=50,
                    levels_per_position=4,
                    level_names='ABCD',
                    default_pallet_capacity=1,
                    bidimensional_racks=False,
                    default_zone='GENERAL',
                    position_numbering_start=1,
                    position_numbering_split=True,
                    created_by=user.id
                )
                
                # Set default receiving areas
                config.set_receiving_areas([
                    {'code': 'RECEIVING', 'type': 'RECEIVING', 'capacity': 10, 'zone': 'DOCK'}
                ])
                
                db.session.add(config)
                db.session.commit()
                print("Default warehouse configuration created")
            
            print("Warehouse tables setup completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error creating warehouse tables: {str(e)}")
            return False

def create_tables_manually():
    """Manually create tables using raw SQL for both SQLite and PostgreSQL"""
    
    print("Creating tables manually with raw SQL...")
    
    try:
        # Check database type
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        is_postgres = 'postgresql' in db_uri.lower()
        
        # SQL for creating warehouse_config table
        if is_postgres:
            warehouse_config_sql = """
            CREATE TABLE IF NOT EXISTS warehouse_config (
                id SERIAL PRIMARY KEY,
                warehouse_id VARCHAR(50) NOT NULL,
                warehouse_name VARCHAR(200) NOT NULL,
                num_aisles INTEGER NOT NULL,
                racks_per_aisle INTEGER NOT NULL,
                positions_per_rack INTEGER NOT NULL,
                levels_per_position INTEGER NOT NULL,
                level_names VARCHAR(20) DEFAULT 'ABCD',
                default_pallet_capacity INTEGER DEFAULT 1,
                bidimensional_racks BOOLEAN DEFAULT FALSE,
                receiving_areas TEXT,
                staging_areas TEXT,
                dock_areas TEXT,
                default_zone VARCHAR(50) DEFAULT 'GENERAL',
                position_numbering_start INTEGER DEFAULT 1,
                position_numbering_split BOOLEAN DEFAULT TRUE,
                total_storage_locations INTEGER,
                total_capacity INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES "user"(id),
                UNIQUE(warehouse_id)
            )
            """
            
            warehouse_template_sql = """
            CREATE TABLE IF NOT EXISTS warehouse_template (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                template_code VARCHAR(20) UNIQUE NOT NULL,
                configuration TEXT NOT NULL,
                is_public BOOLEAN DEFAULT FALSE,
                usage_count INTEGER DEFAULT 0,
                created_by INTEGER REFERENCES "user"(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:
            # SQLite
            warehouse_config_sql = """
            CREATE TABLE IF NOT EXISTS warehouse_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                warehouse_id TEXT NOT NULL,
                warehouse_name TEXT NOT NULL,
                num_aisles INTEGER NOT NULL,
                racks_per_aisle INTEGER NOT NULL,
                positions_per_rack INTEGER NOT NULL,
                levels_per_position INTEGER NOT NULL,
                level_names TEXT DEFAULT 'ABCD',
                default_pallet_capacity INTEGER DEFAULT 1,
                bidimensional_racks BOOLEAN DEFAULT 0,
                receiving_areas TEXT,
                staging_areas TEXT,
                dock_areas TEXT,
                default_zone TEXT DEFAULT 'GENERAL',
                position_numbering_start INTEGER DEFAULT 1,
                position_numbering_split BOOLEAN DEFAULT 1,
                total_storage_locations INTEGER,
                total_capacity INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES user(id),
                UNIQUE(warehouse_id)
            )
            """
            
            warehouse_template_sql = """
            CREATE TABLE IF NOT EXISTS warehouse_template (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                template_code TEXT UNIQUE NOT NULL,
                configuration TEXT NOT NULL,
                is_public BOOLEAN DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                created_by INTEGER REFERENCES user(id),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        
        # Execute the SQL
        print("Creating warehouse_config table...")
        db.session.execute(db.text(warehouse_config_sql))
        
        print("Creating warehouse_template table...")
        db.session.execute(db.text(warehouse_template_sql))
        
        db.session.commit()
        print("Tables created successfully with raw SQL")
        
        return True
        
    except Exception as e:
        print(f"Error creating tables manually: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = create_warehouse_tables()
    if success:
        print("Warehouse tables creation completed successfully!")
        sys.exit(0)
    else:
        print("Warehouse tables creation failed!")
        sys.exit(1)