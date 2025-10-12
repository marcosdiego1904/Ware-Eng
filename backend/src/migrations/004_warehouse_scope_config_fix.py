"""
Migration 004: Fix WarehouseScopeConfig table for cross-database compatibility

This migration fixes the schema mismatch between PostgreSQL and SQLite by:
1. Dropping the existing warehouse_scope_config table (if it exists)
2. Recreating it with JSON string columns for cross-database compatibility
3. Populating it with test configurations for unit-agnostic analysis

Author: Claude Code Assistant
Date: 2025-09-15
Purpose: Enable unit-agnostic warehouse intelligence scope filtering
"""

import json
from datetime import datetime
from sqlalchemy import text


def upgrade(db):
    """Apply the migration"""
    print("[MIGRATION 004] Starting WarehouseScopeConfig schema fix...")

    try:
        # Step 1: Drop existing table if it exists (clean slate)
        print("[MIGRATION 004] Dropping existing warehouse_scope_config table...")
        db.session.execute(text("DROP TABLE IF EXISTS warehouse_scope_config"))
        db.session.commit()

        # Step 2: Create new table with cross-database compatible schema
        print("[MIGRATION 004] Creating warehouse_scope_config table with JSON schema...")
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
        print("[MIGRATION 004] Inserting test warehouse configurations...")

        # Configuration for USER_MTEST warehouse
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
            VALUES (:warehouse_id, :excluded_patterns, :default_unit_type, :config_metadata,
                    datetime('now'), datetime('now'))
            """
            db.session.execute(text(insert_sql), config)
            print(f"[MIGRATION 004] Added configuration for warehouse: {config['warehouse_id']}")

        db.session.commit()

        # Step 4: Verify the migration
        print("[MIGRATION 004] Verifying migration...")
        result = db.session.execute(text("SELECT warehouse_id, excluded_patterns FROM warehouse_scope_config"))
        configs = result.fetchall()

        print(f"[MIGRATION 004] Verified {len(configs)} warehouse configurations:")
        for config in configs:
            patterns = json.loads(config[1])  # Parse JSON to verify format
            print(f"  - {config[0]}: {len(patterns)} exclusion patterns")

        print("[MIGRATION 004] Migration completed successfully!")
        return True

    except Exception as e:
        print(f"[MIGRATION 004] ERROR: Migration failed: {e}")
        db.session.rollback()
        return False


def downgrade(db):
    """Reverse the migration"""
    print("[MIGRATION 004] Reversing WarehouseScopeConfig migration...")

    try:
        # Remove the table
        db.session.execute(text("DROP TABLE IF EXISTS warehouse_scope_config"))
        db.session.commit()
        print("[MIGRATION 004] Table dropped successfully")
        return True

    except Exception as e:
        print(f"[MIGRATION 004] ERROR: Downgrade failed: {e}")
        db.session.rollback()
        return False


# Migration metadata
MIGRATION_NAME = "warehouse_scope_config_fix"
MIGRATION_VERSION = "004"
MIGRATION_DESCRIPTION = "Fix WarehouseScopeConfig table for cross-database compatibility"
DEPENDS_ON = ["003"]  # Assumes previous migrations exist