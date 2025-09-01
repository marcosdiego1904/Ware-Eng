#!/usr/bin/env python3
"""
Check Database Schema to find the correct table structure
"""

import sys
import os
import sqlite3

def check_database_schema():
    """Check the database schema to find rule tables"""
    
    print("Checking Database Schema")
    print("=" * 30)
    
    # Check all database files
    db_files = [
        'backend/instance/warehouse.db',
        'instance/warehouse_rules.db', 
        'backend/warehouse.db',
        'instance/database.db',
        'backend/instance/database.db'
    ]
    
    for db_path in db_files:
        full_path = os.path.join(os.path.dirname(__file__), db_path)
        if os.path.exists(full_path):
            print(f"\\nChecking {db_path}:")
            try:
                conn = sqlite3.connect(full_path)
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                if tables:
                    print(f"  Tables: {', '.join([t[0] for t in tables])}")
                    
                    # Look for rule-related tables
                    for table_name, in tables:
                        if 'rule' in table_name.lower() or 'overcapacity' in table_name.lower():
                            print(f"\\n  Table '{table_name}' schema:")
                            cursor.execute(f"PRAGMA table_info({table_name});")
                            columns = cursor.fetchall()
                            for col in columns:
                                print(f"    {col[1]} ({col[2]})")
                            
                            # Show sample data
                            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                            rows = cursor.fetchall()
                            if rows:
                                print(f"\\n  Sample data from '{table_name}':")
                                for i, row in enumerate(rows):
                                    print(f"    Row {i+1}: {row}")
                else:
                    print("  No tables found")
                
                conn.close()
            except sqlite3.Error as e:
                print(f"  Error: {e}")
        else:
            print(f"\\n{db_path}: File not found")

if __name__ == "__main__":
    check_database_schema()