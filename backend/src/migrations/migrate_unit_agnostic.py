#!/usr/bin/env python3
"""
Migration script for Unit-Agnostic Warehouse Intelligence
Applies database schema changes and migrates existing data safely
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import text

# Add the src directory to the path so we can import our models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import app, db
from models import Location, WarehouseConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """Execute the unit-agnostic migration"""

    logger.info("Starting Unit-Agnostic Warehouse Intelligence migration...")

    try:
        with app.app_context():
            # Step 1: Add new columns to location table
            logger.info("Step 1: Adding unit_type and is_tracked columns to location table...")

            # Check if columns already exist
            result = db.engine.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'location' AND column_name IN ('unit_type', 'is_tracked')
            """))

            existing_columns = [row[0] for row in result]

            if 'unit_type' not in existing_columns:
                db.engine.execute(text("ALTER TABLE location ADD COLUMN unit_type VARCHAR(50) DEFAULT 'pallets'"))
                logger.info("✓ Added unit_type column")
            else:
                logger.info("✓ unit_type column already exists")

            if 'is_tracked' not in existing_columns:
                db.engine.execute(text("ALTER TABLE location ADD COLUMN is_tracked BOOLEAN DEFAULT TRUE"))
                logger.info("✓ Added is_tracked column")
            else:
                logger.info("✓ is_tracked column already exists")

            # Step 2: Add constraints
            logger.info("Step 2: Adding data integrity constraints...")
            try:
                db.engine.execute(text("""
                    ALTER TABLE location ADD CONSTRAINT chk_unit_type
                    CHECK (unit_type IN ('pallets', 'boxes', 'items', 'cases', 'mixed'))
                """))
                logger.info("✓ Added unit_type constraint")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("✓ unit_type constraint already exists")
                else:
                    raise

            # Step 3: Create warehouse_scope_config table
            logger.info("Step 3: Creating warehouse_scope_config table...")

            # Check if table exists
            result = db.engine.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name = 'warehouse_scope_config'
            """))

            if not result.fetchone():
                db.engine.execute(text("""
                    CREATE TABLE warehouse_scope_config (
                        warehouse_id INTEGER PRIMARY KEY REFERENCES warehouse_config(warehouse_id),
                        excluded_patterns TEXT[] DEFAULT '{}',
                        default_unit_type VARCHAR(50) DEFAULT 'pallets',
                        config_metadata JSON DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                logger.info("✓ Created warehouse_scope_config table")
            else:
                logger.info("✓ warehouse_scope_config table already exists")

            # Step 4: Create indexes
            logger.info("Step 4: Creating performance indexes...")
            try:
                db.engine.execute(text("""
                    CREATE INDEX idx_location_tracking
                    ON location(warehouse_id, is_tracked, unit_type)
                """))
                logger.info("✓ Created location tracking index")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("✓ Location tracking index already exists")
                else:
                    logger.warning(f"Could not create location tracking index: {e}")

            # Step 5: Seed default configurations
            logger.info("Step 5: Creating default scope configurations...")

            # Get all warehouse IDs
            warehouses = db.engine.execute(text("SELECT DISTINCT warehouse_id FROM warehouse_config")).fetchall()

            for warehouse in warehouses:
                warehouse_id = warehouse[0]

                # Check if scope config already exists
                existing = db.engine.execute(text("""
                    SELECT warehouse_id FROM warehouse_scope_config
                    WHERE warehouse_id = :warehouse_id
                """), warehouse_id=warehouse_id).fetchone()

                if not existing:
                    db.engine.execute(text("""
                        INSERT INTO warehouse_scope_config (warehouse_id, excluded_patterns, default_unit_type)
                        VALUES (:warehouse_id, '{}', 'pallets')
                    """), warehouse_id=warehouse_id)
                    logger.info(f"✓ Created default scope config for warehouse {warehouse_id}")

            # Step 6: Update existing locations
            logger.info("Step 6: Updating existing location records...")

            updated_count = db.engine.execute(text("""
                UPDATE location
                SET unit_type = 'pallets', is_tracked = TRUE
                WHERE unit_type IS NULL OR is_tracked IS NULL
            """)).rowcount

            logger.info(f"✓ Updated {updated_count} location records")

            # Step 7: Verification
            logger.info("Step 7: Verifying migration results...")

            location_count = db.engine.execute(text("SELECT COUNT(*) FROM location")).scalar()
            tracked_count = db.engine.execute(text("SELECT COUNT(*) FROM location WHERE is_tracked = TRUE")).scalar()
            scope_config_count = db.engine.execute(text("SELECT COUNT(*) FROM warehouse_scope_config")).scalar()

            logger.info(f"✓ Total locations: {location_count}")
            logger.info(f"✓ Tracked locations: {tracked_count}")
            logger.info(f"✓ Scope configurations: {scope_config_count}")

            # Commit all changes
            db.session.commit()
            logger.info("✅ Migration completed successfully!")

            return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        db.session.rollback()
        return False

def rollback_migration():
    """Rollback the migration if needed"""

    logger.info("Rolling back Unit-Agnostic migration...")

    try:
        with app.app_context():
            # Drop the scope config table
            db.engine.execute(text("DROP TABLE IF EXISTS warehouse_scope_config"))

            # Remove the new columns
            db.engine.execute(text("ALTER TABLE location DROP COLUMN IF EXISTS unit_type"))
            db.engine.execute(text("ALTER TABLE location DROP COLUMN IF EXISTS is_tracked"))

            # Drop indexes
            db.engine.execute(text("DROP INDEX IF EXISTS idx_location_tracking"))

            db.session.commit()
            logger.info("✅ Rollback completed successfully!")

    except Exception as e:
        logger.error(f"❌ Rollback failed: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Unit-Agnostic Migration Script')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')

    args = parser.parse_args()

    if args.rollback:
        rollback_migration()
    elif args.dry_run:
        logger.info("DRY RUN - Migration steps that would be executed:")
        logger.info("1. Add unit_type and is_tracked columns to location table")
        logger.info("2. Add data integrity constraints")
        logger.info("3. Create warehouse_scope_config table")
        logger.info("4. Create performance indexes")
        logger.info("5. Create default scope configurations for existing warehouses")
        logger.info("6. Update existing location records")
        logger.info("Use --rollback to undo these changes")
    else:
        success = run_migration()
        sys.exit(0 if success else 1)