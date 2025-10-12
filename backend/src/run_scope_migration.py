#!/usr/bin/env python3
"""
Run Warehouse Scope Configuration Migration

This script runs the database migration to fix the WarehouseScopeConfig table
for cross-database compatibility and enables unit-agnostic analysis.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from database import db


def run_scope_migration():
    """Run the warehouse scope configuration migration"""

    print("WAREHOUSE SCOPE CONFIGURATION MIGRATION")
    print("=" * 50)

    # Create Flask app with database configuration
    app = Flask(__name__)

    # Configure database path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    instance_path = os.path.join(project_root, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'database.db')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    print(f"Database path: {db_path}")

    # Initialize database
    db.init_app(app)

    with app.app_context():
        try:
            # Import and run the migration
            from migrations.warehouse_scope_config_fix_004 import upgrade

            print("Running migration upgrade...")
            success = upgrade(db)

            if success:
                print()
                print("=" * 50)
                print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
                print("✓ WarehouseScopeConfig table is now ready for unit-agnostic analysis")
                print("✓ Test configurations added for USER_MTEST and USER_MTEST1")
                print("=" * 50)
                return True
            else:
                print()
                print("=" * 50)
                print("✗ MIGRATION FAILED!")
                print("✗ Check the error messages above for details")
                print("=" * 50)
                return False

        except ImportError:
            # Migration file not found, run inline migration
            print("Migration file not found, running inline migration...")
            return run_inline_migration(db)
        except Exception as e:
            print(f"ERROR: Migration failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False


def run_inline_migration(db):
    """Run the migration inline if the file is not found"""
    import json
    from sqlalchemy import text

    try:
        print("[INLINE MIGRATION] Starting WarehouseScopeConfig schema fix...")

        # Step 1: Drop existing table
        print("[INLINE MIGRATION] Dropping existing warehouse_scope_config table...")
        db.session.execute(text("DROP TABLE IF EXISTS warehouse_scope_config"))
        db.session.commit()

        # Step 2: Create new table
        print("[INLINE MIGRATION] Creating warehouse_scope_config table...")
        create_table_sql = """
        CREATE TABLE warehouse_scope_config (
            warehouse_id VARCHAR(50) PRIMARY KEY,
            excluded_patterns TEXT DEFAULT '[]',
            default_unit_type VARCHAR(50) DEFAULT 'pallets',
            config_metadata TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        db.session.execute(text(create_table_sql))
        db.session.commit()

        # Step 3: Insert test configurations
        print("[INLINE MIGRATION] Inserting test configurations...")
        test_configs = [
            {
                'warehouse_id': 'USER_MTEST',
                'excluded_patterns': '["BOX-*", "ITEM-*", "TEMP*"]',
                'default_unit_type': 'pallet',
                'config_metadata': '{"version": "1.0", "description": "Unit-agnostic test configuration", "test_mode": true}'
            },
            {
                'warehouse_id': 'USER_MTEST1',
                'excluded_patterns': '["BOX-*", "ITEM-*", "TEMP*"]',
                'default_unit_type': 'pallet',
                'config_metadata': '{"version": "1.0", "description": "Unit-agnostic test configuration for USER_MTEST1", "test_mode": true}'
            }
        ]

        for config in test_configs:
            insert_sql = """
            INSERT INTO warehouse_scope_config
            (warehouse_id, excluded_patterns, default_unit_type, config_metadata, created_at, updated_at)
            VALUES (:warehouse_id, :excluded_patterns, :default_unit_type, :config_metadata, datetime('now'), datetime('now'))
            """
            db.session.execute(text(insert_sql), config)
            print(f"[INLINE MIGRATION] Added configuration for warehouse: {config['warehouse_id']}")

        db.session.commit()

        # Step 4: Verify
        print("[INLINE MIGRATION] Verifying migration...")
        result = db.session.execute(text("SELECT warehouse_id, excluded_patterns FROM warehouse_scope_config"))
        configs = result.fetchall()

        print(f"[INLINE MIGRATION] Verified {len(configs)} warehouse configurations:")
        for config in configs:
            patterns = json.loads(config[1])
            print(f"  - {config[0]}: {len(patterns)} exclusion patterns")

        print("[INLINE MIGRATION] Migration completed successfully!")
        return True

    except Exception as e:
        print(f"[INLINE MIGRATION] ERROR: {e}")
        db.session.rollback()
        return False


if __name__ == "__main__":
    success = run_scope_migration()
    sys.exit(0 if success else 1)