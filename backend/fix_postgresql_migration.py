#!/usr/bin/env python3
"""
Fix PostgreSQL Smart Configuration Migration

This script directly applies the Smart Configuration columns to PostgreSQL
by connecting to the production database and running the migration SQL.
"""

import sys
import os
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def fix_postgresql_migration():
    """Apply Smart Configuration migration directly to PostgreSQL"""
    print("=" * 70)
    print("FIXING POSTGRESQL SMART CONFIGURATION MIGRATION")
    print("=" * 70)
    
    # Force PostgreSQL connection
    os.environ['DATABASE_URL'] = "postgresql://ware_eng_db_user:fqvKdOGZEt1CGIeLF4J1AG8RTtCv0Zdu@dpg-d23244fg127c73fga10g-a.ohio-postgres.render.com/ware_eng_db"
    print(f"Setting DATABASE_URL to PostgreSQL connection")
    
    try:
        from app import app, db
        from sqlalchemy import text
        
        # Force the app to use PostgreSQL by overriding the config
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
        
        with app.app_context():
            engine_name = db.engine.dialect.name
            print(f"Connected to database: {engine_name}")
            
            if engine_name != 'postgresql':
                print(f"WARNING: Expected PostgreSQL, but connected to {engine_name}")
                print("Make sure your DATABASE_URL environment variable points to PostgreSQL")
                return False
            
            # Check current schema
            print("\nChecking current warehouse_config schema...")
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('warehouse_config')
            column_names = [col['name'] for col in columns]
            
            smart_config_columns = [
                'location_format_config',
                'format_confidence', 
                'format_examples',
                'format_learned_date'
            ]
            
            missing_columns = [col for col in smart_config_columns if col not in column_names]
            
            if not missing_columns:
                print("SUCCESS: All Smart Configuration columns already exist!")
                return True
            
            print(f"Missing columns: {missing_columns}")
            print("\nApplying migration...")
            
            # Apply the migration with PostgreSQL-specific syntax
            migration_sql = [
                "ALTER TABLE warehouse_config ADD COLUMN location_format_config TEXT",
                "ALTER TABLE warehouse_config ADD COLUMN format_confidence FLOAT DEFAULT 0.0",
                "ALTER TABLE warehouse_config ADD COLUMN format_examples TEXT",
                "ALTER TABLE warehouse_config ADD COLUMN format_learned_date TIMESTAMP",
                "UPDATE warehouse_config SET format_confidence = 0.0 WHERE format_confidence IS NULL"
            ]
            
            for sql in migration_sql:
                try:
                    print(f"Executing: {sql[:50]}...")
                    db.session.execute(text(sql))
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"Column already exists (skipping): {sql.split()[5]}")
                    else:
                        raise e
            
            db.session.commit()
            print("\nSUCCESS: PostgreSQL migration completed!")
            
            # Verify the migration
            updated_columns = inspector.get_columns('warehouse_config')
            updated_column_names = [col['name'] for col in updated_columns]
            
            print("\nVerification:")
            for col in smart_config_columns:
                status = "EXISTS" if col in updated_column_names else "MISSING"
                print(f"  {col}: {status}")
            
            return True
            
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure your DATABASE_URL points to PostgreSQL")
        print("2. Check database connection permissions")
        print("3. Verify PostgreSQL server is running")
        return False

if __name__ == "__main__":
    success = fix_postgresql_migration()
    if success:
        print(f"\nNext steps:")
        print("1. Restart your application servers")
        print("2. Run: python apply_smart_config_to_warehouse.py DEFAULT")
        print("3. Test your rule engine")
    else:
        print(f"\nFailed to apply migration. Check the errors above.")
        sys.exit(1)