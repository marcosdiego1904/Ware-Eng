#!/usr/bin/env python3
"""
PostgreSQL Migration Script - Add Missing Location Columns
This script adds the warehouse structure columns to the existing location table in PostgreSQL
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app

def get_db_connection():
    """Get direct PostgreSQL connection from Flask app config"""
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    if not database_url or 'postgresql' not in database_url:
        raise ValueError("PostgreSQL database URL not found in configuration")
    
    # Parse the database URL
    parsed = urlparse(database_url)
    
    # Create connection parameters
    conn_params = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path[1:]  # Remove leading '/'
    }
    
    return psycopg2.connect(**conn_params)

def get_existing_columns(cursor, table_name):
    """Get existing columns in the table"""
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    return [row[0] for row in cursor.fetchall()]

def add_location_columns_postgres():
    """Add missing columns to location table in PostgreSQL"""
    
    print("Adding missing columns to location table (PostgreSQL)...")
    
    with app.app_context():
        try:
            # Connect to PostgreSQL database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            print("Connected to PostgreSQL database")
            
            # Get existing columns
            existing_columns = get_existing_columns(cursor, 'location')
            print(f"Existing columns: {existing_columns}")
            
            # Define new columns to add (PostgreSQL syntax)
            new_columns = [
                ("warehouse_id", "VARCHAR(50) DEFAULT 'DEFAULT'"),
                ("aisle_number", "INTEGER"),
                ("rack_number", "INTEGER"), 
                ("position_number", "INTEGER"),
                ("level", "VARCHAR(1)"),
                ("pallet_capacity", "INTEGER DEFAULT 1"),
                ("location_hierarchy", "TEXT"),
                ("special_requirements", "TEXT"),
                ("is_active", "BOOLEAN DEFAULT TRUE"),
                ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ("created_by", "INTEGER REFERENCES \"user\"(id)")
            ]
            
            # Add missing columns
            columns_added = 0
            for column_name, column_def in new_columns:
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE location ADD COLUMN {column_name} {column_def}"
                        print(f"Adding column: {column_name}")
                        print(f"SQL: {sql}")
                        cursor.execute(sql)
                        columns_added += 1
                        print(f"✓ Added {column_name}")
                    except psycopg2.Error as e:
                        if "already exists" in str(e):
                            print(f"Column {column_name} already exists")
                        else:
                            print(f"Error adding column {column_name}: {e}")
                            # Don't fail completely, continue with other columns
                else:
                    print(f"Column {column_name} already exists")
            
            # Commit changes
            conn.commit()
            print(f"\n✓ Successfully added {columns_added} new columns to location table")
            
            # Verify the changes
            updated_columns = get_existing_columns(cursor, 'location')
            print(f"Updated columns: {updated_columns}")
            
            # Also check if we need to create warehouse_config table
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name IN ('warehouse_config', 'warehouse_template')
            """)
            warehouse_tables = [row[0] for row in cursor.fetchall()]
            
            if 'warehouse_config' not in warehouse_tables:
                print("\nCreating warehouse_config table...")
                create_warehouse_config_sql = """
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
                    created_by INTEGER REFERENCES "user"(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
                """
                cursor.execute(create_warehouse_config_sql)
                print("✓ Created warehouse_config table")
            
            if 'warehouse_template' not in warehouse_tables:
                print("Creating warehouse_template table...")
                create_warehouse_template_sql = """
                CREATE TABLE warehouse_template (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(120) NOT NULL,
                    description TEXT,
                    template_code VARCHAR(20) UNIQUE,
                    num_aisles INTEGER NOT NULL,
                    racks_per_aisle INTEGER NOT NULL,
                    positions_per_rack INTEGER NOT NULL,
                    levels_per_position INTEGER DEFAULT 4,
                    level_names VARCHAR(20) DEFAULT 'ABCD',
                    default_pallet_capacity INTEGER DEFAULT 1,
                    bidimensional_racks BOOLEAN DEFAULT FALSE,
                    receiving_areas_template TEXT,
                    staging_areas_template TEXT,
                    dock_areas_template TEXT,
                    based_on_config_id INTEGER REFERENCES warehouse_config(id),
                    is_public BOOLEAN DEFAULT FALSE,
                    usage_count INTEGER DEFAULT 0,
                    created_by INTEGER REFERENCES "user"(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
                """
                cursor.execute(create_warehouse_template_sql)
                print("✓ Created warehouse_template table")
            
            conn.commit()
            conn.close()
            
            print("\n" + "="*60)
            print("✓ POSTGRESQL MIGRATION COMPLETED SUCCESSFULLY!")
            print("The location table now has all required warehouse columns.")
            print("The warehouse_config and warehouse_template tables are ready.")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"ERROR during migration: {e}")
            import traceback
            traceback.print_exc()
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False

if __name__ == "__main__":
    success = add_location_columns_postgres()
    if success:
        print("PostgreSQL migration completed successfully!")
        sys.exit(0)
    else:
        print("PostgreSQL migration failed!")
        sys.exit(1)