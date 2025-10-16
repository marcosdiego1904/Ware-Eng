#!/usr/bin/env python3
"""
Direct PostgreSQL Smart Configuration Migration

This script connects directly to PostgreSQL using psycopg2 and applies
the Smart Configuration columns without using Flask app configuration.
"""

import sys
import os
from datetime import datetime

def run_direct_postgresql_migration():
    """Apply Smart Configuration migration directly using psycopg2"""
    print("=" * 70)
    print("DIRECT POSTGRESQL SMART CONFIGURATION MIGRATION")
    print("=" * 70)
    
    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        print("ERROR: psycopg2 not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
        from psycopg2 import sql
    
    # PostgreSQL connection string from Render
    connection_url = "postgresql://ware_eng_db_user:fqvKdOGZEt1CGIeLF4J1AG8RTtCv0Zdu@dpg-d23244fg127c73fga10g-a.ohio-postgres.render.com/ware_eng_db?sslmode=require"
    
    print("Connecting to PostgreSQL using connection string...")
    
    try:
        # Connect to PostgreSQL using connection string
        connection = psycopg2.connect(connection_url)
        cursor = connection.cursor()
        
        print("Connected to PostgreSQL successfully!")
        
        # Check current schema
        print("\nChecking current warehouse_config schema...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'warehouse_config'
            ORDER BY ordinal_position
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        smart_config_columns = [
            'location_format_config',
            'format_confidence', 
            'format_examples',
            'format_learned_date'
        ]
        
        missing_columns = [col for col in smart_config_columns if col not in existing_columns]
        
        if not missing_columns:
            print("SUCCESS: All Smart Configuration columns already exist!")
            return True
        
        print(f"Missing columns: {missing_columns}")
        print("\nApplying migration...")
        
        # Apply the migration with PostgreSQL-specific syntax
        migration_sql = [
            "ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS location_format_config TEXT",
            "ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_confidence FLOAT DEFAULT 0.0",
            "ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_examples TEXT",
            "ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_learned_date TIMESTAMP",
            "UPDATE warehouse_config SET format_confidence = 0.0 WHERE format_confidence IS NULL"
        ]
        
        for sql_statement in migration_sql:
            try:
                print(f"Executing: {sql_statement[:50]}...")
                cursor.execute(sql_statement)
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"Column already exists (skipping): {sql_statement}")
                else:
                    raise e
        
        connection.commit()
        print("\nSUCCESS: PostgreSQL migration completed!")
        
        # Verify the migration
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'warehouse_config'
            AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
            ORDER BY column_name
        """)
        
        updated_columns = [row[0] for row in cursor.fetchall()]
        
        print("\nVerification:")
        for col in smart_config_columns:
            status = "EXISTS" if col in updated_columns else "MISSING"
            print(f"  {col}: {status}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check database connection parameters")
        print("2. Verify PostgreSQL server is running")
        print("3. Check network connectivity")
        return False

if __name__ == "__main__":
    success = run_direct_postgresql_migration()
    if success:
        print(f"\nNext steps:")
        print("1. Restart your application servers")
        print("2. Run: python apply_smart_config_to_warehouse.py DEFAULT")
        print("3. Test your rule engine")
    else:
        print(f"\nFailed to apply migration. Check the errors above.")
        sys.exit(1)