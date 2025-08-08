#!/usr/bin/env python3
"""
Add new columns to existing location table
This script adds the warehouse structure columns to the existing location table
"""

import os
import sys
import sqlite3

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import app
from database import db

def add_location_columns():
    """Add missing columns to location table"""
    
    print("Adding missing columns to location table...")
    
    with app.app_context():
        try:
            # Get database file path
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            print(f"Database path: {db_path}")
            
            # Connect to SQLite database directly
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get current table schema
            cursor.execute("PRAGMA table_info(location)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            print(f"Existing columns: {existing_columns}")
            
            # Define new columns to add
            new_columns = [
                ("warehouse_id", "TEXT DEFAULT 'DEFAULT'"),
                ("aisle_number", "INTEGER"),
                ("rack_number", "INTEGER"),
                ("position_number", "INTEGER"),
                ("level", "TEXT"),
                ("pallet_capacity", "INTEGER DEFAULT 1"),
                ("location_hierarchy", "TEXT"),
                ("special_requirements", "TEXT"),
                ("is_active", "BOOLEAN DEFAULT 1"),
                ("created_at", "DATETIME"),
                ("created_by", "INTEGER")
            ]
            
            # Add missing columns
            columns_added = 0
            for column_name, column_def in new_columns:
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE location ADD COLUMN {column_name} {column_def}"
                        print(f"Adding column: {column_name}")
                        cursor.execute(sql)
                        columns_added += 1
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e):
                            print(f"Warning: Could not add column {column_name}: {e}")
                else:
                    print(f"Column {column_name} already exists")
            
            # Commit changes
            conn.commit()
            
            print(f"Successfully added {columns_added} new columns to location table")
            
            # Verify the changes
            cursor.execute("PRAGMA table_info(location)")
            updated_columns = [column[1] for column in cursor.fetchall()]
            print(f"Updated columns: {updated_columns}")
            
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error adding columns: {str(e)}")
            return False

if __name__ == "__main__":
    success = add_location_columns()
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)