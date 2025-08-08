# Production Schema Fix Guide

## Problem
Your PostgreSQL database on Render is missing the newer warehouse-related columns that were added to the `location` table model. This causes errors like:

```
column location.warehouse_id does not exist
```

## Solution
Run the schema migration script to add the missing columns to your production database.

## Steps to Fix Production Database

### Option 1: Run via Render Console (Recommended)

1. **Open Render Dashboard**
   - Go to your Render service dashboard
   - Navigate to the "Shell" or "Console" tab

2. **Run the Migration Script**
   ```bash
   cd /opt/render/project/src/backend
   python fix_production_schema.py
   ```

3. **Verify the Fix**
   - The script will show which columns were added
   - Test your warehouse setup functionality

### Option 2: Deploy and Run Automatically

Add this to your `backend/run_server.py` or startup script (temporary):

```python
# Add this at startup (remove after running once)
try:
    from fix_production_schema import fix_production_schema
    print("Running production schema fix...")
    fix_production_schema()
    print("Schema fix completed")
except Exception as e:
    print(f"Schema fix failed: {e}")
```

### Option 3: Manual SQL Commands

If you have direct database access, run these SQL commands:

```sql
-- Add missing columns to location table
ALTER TABLE location ADD COLUMN IF NOT EXISTS warehouse_id VARCHAR(50) DEFAULT 'DEFAULT';
ALTER TABLE location ADD COLUMN IF NOT EXISTS aisle_number INTEGER;
ALTER TABLE location ADD COLUMN IF NOT EXISTS rack_number INTEGER;
ALTER TABLE location ADD COLUMN IF NOT EXISTS position_number INTEGER;
ALTER TABLE location ADD COLUMN IF NOT EXISTS level VARCHAR(1);
ALTER TABLE location ADD COLUMN IF NOT EXISTS pallet_capacity INTEGER DEFAULT 1;
ALTER TABLE location ADD COLUMN IF NOT EXISTS location_hierarchy TEXT;
ALTER TABLE location ADD COLUMN IF NOT EXISTS special_requirements TEXT;

-- Create warehouse_config table if it doesn't exist
CREATE TABLE IF NOT EXISTS warehouse_config (
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
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

## Files Created

1. **`fix_production_schema.py`** - Safe migration script using SQLAlchemy
2. **`migrate_location_columns_postgres.py`** - Direct PostgreSQL migration (advanced)

## What the Script Does

1. **Checks Database Type** - Ensures it's running on PostgreSQL
2. **Adds Missing Columns** - Safely adds warehouse-related columns to `location` table:
   - `warehouse_id` (default: 'DEFAULT')
   - `aisle_number`, `rack_number`, `position_number`, `level`
   - `pallet_capacity` (default: 1)
   - `location_hierarchy`, `special_requirements`
3. **Creates Warehouse Tables** - Ensures `warehouse_config` table exists
4. **Safe Execution** - Won't break existing data, skips existing columns

## After Running the Fix

Your warehouse setup should work without SQL errors. You'll be able to:
- ✅ Create warehouse configurations
- ✅ Set up warehouse layouts (aisles, racks, positions)
- ✅ Manage locations with hierarchical structure
- ✅ Use all warehouse features without database errors

## Verification

After running the script, test by:
1. Going to your warehouse setup page
2. Clicking "Create warehouse"
3. The operation should complete without SQL errors

## Rollback (if needed)

If something goes wrong, the added columns can be removed with:
```sql
ALTER TABLE location DROP COLUMN IF EXISTS warehouse_id;
ALTER TABLE location DROP COLUMN IF EXISTS aisle_number;
-- etc.
```

But this is generally not needed as the script is safe and non-destructive.