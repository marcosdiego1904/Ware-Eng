"""
Database Migration: Add warehouse_config_id to Location table

This migration implements template-location binding by adding a foreign key
relationship between Location and WarehouseConfig.

WHAT THIS FIXES:
- Special locations created via "Add Special Location" button are now bound to the active template
- When switching templates, only locations for that template are shown
- No more "global" locations bleeding across templates

MIGRATION STRATEGY:
1. Add warehouse_config_id column (nullable)
2. Backfill existing locations with active config for each user
3. Create foreign key constraint
4. Add index for performance
"""

import os
import sys
from sqlalchemy import text

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location, WarehouseConfig

def check_current_state():
    """Check if migration is needed"""
    print("\n" + "="*60)
    print("CHECKING CURRENT STATE")
    print("="*60)

    with app.app_context():
        # Check if column already exists
        result = db.session.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'location'
            AND column_name = 'warehouse_config_id';
        """))

        exists = result.fetchone() is not None

        if exists:
            print("\n[INFO] warehouse_config_id column already exists")

            # Check how many locations have it set
            total = db.session.execute(text("SELECT COUNT(*) FROM location")).scalar()
            with_config = db.session.execute(text(
                "SELECT COUNT(*) FROM location WHERE warehouse_config_id IS NOT NULL"
            )).scalar()

            print(f"  Total locations: {total}")
            print(f"  With config_id: {with_config}")
            print(f"  Without config_id (orphaned): {total - with_config}")

            return True
        else:
            print("\n[INFO] warehouse_config_id column does NOT exist - migration needed")

            # Show current location count
            total = db.session.execute(text("SELECT COUNT(*) FROM location")).scalar()
            print(f"  Total locations to migrate: {total}")

            return False

def add_column():
    """Add warehouse_config_id column"""
    print("\n" + "="*60)
    print("STEP 1: ADDING warehouse_config_id COLUMN")
    print("="*60)

    with app.app_context():
        try:
            print("\n[1/2] Adding column (nullable)...")
            db.session.execute(text("""
                ALTER TABLE location
                ADD COLUMN warehouse_config_id INTEGER;
            """))
            db.session.commit()
            print("[OK] Column added successfully")

            print("\n[2/2] Adding index for performance...")
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_location_warehouse_config_id
                ON location(warehouse_config_id);
            """))
            db.session.commit()
            print("[OK] Index created successfully")

            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n[FAIL] Error adding column: {e}")
            return False

def backfill_data():
    """Backfill existing locations with warehouse_config_id"""
    print("\n" + "="*60)
    print("STEP 2: BACKFILLING EXISTING LOCATIONS")
    print("="*60)

    with app.app_context():
        try:
            # Get all unique (warehouse_id, created_by) combinations
            locations_to_update = db.session.execute(text("""
                SELECT DISTINCT warehouse_id, created_by
                FROM location
                WHERE warehouse_config_id IS NULL
            """)).fetchall()

            print(f"\n[INFO] Found {len(locations_to_update)} unique warehouse-user combinations")

            updated_count = 0
            orphaned_count = 0

            for warehouse_id, created_by in locations_to_update:
                # Find active config for this warehouse and user
                config = WarehouseConfig.query.filter_by(
                    warehouse_id=warehouse_id,
                    created_by=created_by,
                    is_active=True
                ).first()

                if config:
                    # Update all locations for this warehouse-user combo
                    result = db.session.execute(text("""
                        UPDATE location
                        SET warehouse_config_id = :config_id
                        WHERE warehouse_id = :warehouse_id
                        AND created_by = :created_by
                        AND warehouse_config_id IS NULL
                    """), {
                        'config_id': config.id,
                        'warehouse_id': warehouse_id,
                        'created_by': created_by
                    })

                    count = result.rowcount
                    updated_count += count
                    print(f"  [OK] Linked {count} locations to config '{config.warehouse_name}' (id={config.id})")
                else:
                    # No active config found - count orphaned locations
                    result = db.session.execute(text("""
                        SELECT COUNT(*)
                        FROM location
                        WHERE warehouse_id = :warehouse_id
                        AND created_by = :created_by
                        AND warehouse_config_id IS NULL
                    """), {
                        'warehouse_id': warehouse_id,
                        'created_by': created_by
                    })

                    count = result.scalar()
                    orphaned_count += count
                    print(f"  [WARNING] {count} locations for warehouse '{warehouse_id}' (user={created_by}) have no active config")

            db.session.commit()

            print(f"\n[SUMMARY]")
            print(f"  Locations updated: {updated_count}")
            print(f"  Orphaned locations: {orphaned_count}")

            if orphaned_count > 0:
                print(f"\n[INFO] Orphaned locations will remain with warehouse_config_id=NULL")
                print(f"       They will be accessible but not bound to a specific template")

            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n[FAIL] Error during backfill: {e}")
            import traceback
            traceback.print_exc()
            return False

def add_foreign_key():
    """Add foreign key constraint"""
    print("\n" + "="*60)
    print("STEP 3: ADDING FOREIGN KEY CONSTRAINT")
    print("="*60)

    with app.app_context():
        try:
            print("\n[INFO] Creating foreign key constraint...")
            print("       This links location.warehouse_config_id -> warehouse_config.id")

            db.session.execute(text("""
                ALTER TABLE location
                ADD CONSTRAINT fk_location_warehouse_config
                FOREIGN KEY (warehouse_config_id)
                REFERENCES warehouse_config(id)
                ON DELETE SET NULL;
            """))
            db.session.commit()

            print("[OK] Foreign key constraint created successfully")
            print("     ON DELETE SET NULL: If config deleted, locations remain but become orphaned")

            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n[FAIL] Error adding foreign key: {e}")
            return False

def verify_migration():
    """Verify the migration worked"""
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)

    with app.app_context():
        # Check column exists
        result = db.session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'location'
            AND column_name = 'warehouse_config_id';
        """))

        column_info = result.fetchone()

        if column_info:
            print(f"\n[OK] Column exists: {column_info[0]} ({column_info[1]})")
            print(f"     Nullable: {column_info[2]}")
        else:
            print("\n[FAIL] Column not found!")
            return False

        # Check foreign key
        result = db.session.execute(text("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'location'
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name = 'fk_location_warehouse_config';
        """))

        fk_exists = result.fetchone() is not None

        if fk_exists:
            print("[OK] Foreign key constraint exists")
        else:
            print("[WARNING] Foreign key constraint not found")

        # Check index
        result = db.session.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'location'
            AND indexname = 'idx_location_warehouse_config_id';
        """))

        idx_exists = result.fetchone() is not None

        if idx_exists:
            print("[OK] Performance index exists")
        else:
            print("[WARNING] Performance index not found")

        # Check data distribution
        result = db.session.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(warehouse_config_id) as with_config,
                COUNT(*) - COUNT(warehouse_config_id) as without_config
            FROM location;
        """))

        stats = result.fetchone()

        print(f"\n[DATA DISTRIBUTION]")
        print(f"  Total locations: {stats[0]}")
        print(f"  With config_id: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
        print(f"  Orphaned: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")

        return True

if __name__ == '__main__':
    print("""
===============================================================
  Database Migration: Add warehouse_config_id to Location
===============================================================
    """)

    try:
        # Check if migration already done
        already_exists = check_current_state()

        if already_exists:
            response = input("\nColumn already exists. Proceed anyway to backfill/verify? (y/N): ")
            if response.lower() != 'y':
                print("\nMigration cancelled by user")
                sys.exit(0)

        # Step 1: Add column
        if not already_exists:
            input("\n[STEP 1] Press Enter to add warehouse_config_id column...")
            if not add_column():
                print("\n[FAIL] Migration aborted at step 1")
                sys.exit(1)

        # Step 2: Backfill data
        input("\n[STEP 2] Press Enter to backfill existing locations...")
        if not backfill_data():
            print("\n[FAIL] Migration aborted at step 2")
            sys.exit(1)

        # Step 3: Add foreign key
        if not already_exists:
            input("\n[STEP 3] Press Enter to add foreign key constraint...")
            if not add_foreign_key():
                print("\n[FAIL] Migration aborted at step 3")
                sys.exit(1)

        # Verify
        print("\n" + "="*60)
        verify_migration()
        print("="*60)

        print("\n[SUCCESS] Migration completed successfully!")
        print("\nNext steps:")
        print("  1. Update Location model in models.py")
        print("  2. Update location_api.py to use warehouse_config_id")
        print("  3. Update frontend to show template context")
        print("  4. Test location creation and template switching")

    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FATAL ERROR]: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
