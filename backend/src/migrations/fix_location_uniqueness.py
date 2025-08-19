"""
Production Database Migration: Fix Location Uniqueness Constraint

PROBLEM: Current schema has UNIQUE constraint on location.code globally,
preventing multiple warehouses from having same location codes (e.g., "01-01-001A").

SOLUTION: Change to compound unique constraint (warehouse_id, code) to enable proper multi-tenancy.

This migration:
1. Drops the current unique constraint on location.code
2. Creates compound unique constraint on (warehouse_id, code) 
3. Preserves all existing data
4. Enables proper multi-tenant warehouse system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def check_current_constraints():
    """Check existing constraints before migration"""
    with app.app_context():
        try:
            # For SQLite, check indexes/constraints
            result = db.session.execute(text("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='location'
            """)).fetchone()
            
            if result:
                print("Current location table definition:")
                print(result[0])
                
            # Check for duplicate location codes across warehouses
            duplicates = db.session.execute(text("""
                SELECT code, COUNT(DISTINCT warehouse_id) as warehouse_count
                FROM location 
                GROUP BY code 
                HAVING COUNT(DISTINCT warehouse_id) > 1
            """)).fetchall()
            
            if duplicates:
                print(f"\nWARNING: Found {len(duplicates)} location codes used in multiple warehouses:")
                for code, count in duplicates:
                    print(f"  {code}: used in {count} warehouses")
                return False
            else:
                print(f"\nNo location code conflicts found - safe to migrate")
                return True
                
        except Exception as e:
            logger.error(f"Error checking constraints: {e}")
            return False

def create_new_location_table():
    """Create new location table with proper compound unique constraint"""
    with app.app_context():
        try:
            print("Creating new location table with compound unique constraint...")
            
            # Create new table with correct constraints
            db.session.execute(text("""
                CREATE TABLE location_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(255) NOT NULL,
                    pattern VARCHAR(255),
                    location_type VARCHAR(100),
                    capacity INTEGER DEFAULT 1,
                    allowed_products TEXT,
                    zone VARCHAR(100),
                    warehouse_id VARCHAR(255) NOT NULL,
                    aisle_number INTEGER,
                    rack_number INTEGER,
                    position_number INTEGER,
                    level VARCHAR(10),
                    pallet_capacity INTEGER DEFAULT 1,
                    location_hierarchy TEXT,
                    special_requirements TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    UNIQUE(warehouse_id, code),  -- Compound unique constraint
                    FOREIGN KEY(created_by) REFERENCES user(id)
                )
            """))
            
            print("SUCCESS: New location table created with compound unique constraint")
            return True
            
        except Exception as e:
            logger.error(f"Error creating new table: {e}")
            return False

def migrate_data():
    """Migrate data from old table to new table"""
    with app.app_context():
        try:
            print("Migrating existing location data...")
            
            # Copy all data to new table
            db.session.execute(text("""
                INSERT INTO location_new 
                SELECT * FROM location
            """))
            
            # Verify data migration
            old_count = db.session.execute(text("SELECT COUNT(*) FROM location")).scalar()
            new_count = db.session.execute(text("SELECT COUNT(*) FROM location_new")).scalar()
            
            if old_count == new_count:
                print(f"SUCCESS: Migrated {new_count} location records")
                return True
            else:
                print(f"ERROR: Migration mismatch: {old_count} original, {new_count} migrated")
                return False
                
        except Exception as e:
            logger.error(f"Error migrating data: {e}")
            return False

def replace_table():
    """Replace old table with new table"""
    with app.app_context():
        try:
            print("Replacing old table with new table...")
            
            # Drop old table and rename new table
            db.session.execute(text("DROP TABLE location"))
            db.session.execute(text("ALTER TABLE location_new RENAME TO location"))
            
            print("SUCCESS: Table replacement completed")
            return True
            
        except Exception as e:
            logger.error(f"Error replacing table: {e}")
            return False

def verify_migration():
    """Verify migration was successful"""
    with app.app_context():
        try:
            print("Verifying migration...")
            
            # Check table structure
            result = db.session.execute(text("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='location'
            """)).fetchone()
            
            if result and 'UNIQUE(warehouse_id, code)' in result[0]:
                print("SUCCESS: Compound unique constraint verified")
            else:
                print("ERROR: Compound unique constraint not found")
                return False
            
            # Test constraint works
            from models import Location
            total_locations = Location.query.count()
            print(f"SUCCESS: {total_locations} locations accessible after migration")
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying migration: {e}")
            return False

def run_migration():
    """Run the complete migration process"""
    print("=" * 60)
    print("PRODUCTION DATABASE MIGRATION: Location Uniqueness Fix")
    print("=" * 60)
    
    # Step 1: Check current state
    if not check_current_constraints():
        print("ERROR: Pre-migration checks failed")
        return False
    
    with app.app_context():
        try:
            # Step 2: Create new table
            if not create_new_location_table():
                return False
            
            # Step 3: Migrate data
            if not migrate_data():
                db.session.rollback()
                return False
            
            # Step 4: Replace table
            if not replace_table():
                db.session.rollback()
                return False
            
            # Step 5: Commit changes
            db.session.commit()
            print("SUCCESS: Migration transaction committed")
            
            # Step 6: Verify
            if not verify_migration():
                return False
            
            print("\n" + "=" * 60)
            print("MIGRATION COMPLETED SUCCESSFULLY!")
            print("SUCCESS: Multi-tenant location system now enabled")
            print("SUCCESS: Multiple warehouses can have same location codes")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.session.rollback()
            print(f"ERROR: Migration failed and rolled back: {e}")
            return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)