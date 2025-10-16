-- ============================================================================
-- PRODUCTION FIX: Multi-Tenancy Location Constraint
-- ============================================================================
--
-- PROBLEM: Old 'location_code_key' constraint prevents users from creating
--          locations with the same code in different warehouses.
--
-- ERROR: duplicate key value violates unique constraint "location_code_key"
--        DETAIL: Key (code)=(W-01) already exists.
--
-- SOLUTION: Drop the old global constraint, keep only the compound constraint
--           that properly isolates warehouses.
--
-- ============================================================================

BEGIN;

-- Step 1: Drop old single-column unique constraint
ALTER TABLE location DROP CONSTRAINT IF EXISTS location_code_key;

-- Step 2: Drop any unique index on code column alone
DROP INDEX IF EXISTS ix_location_code;

-- Step 3: Ensure compound unique constraint exists (per-warehouse uniqueness)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_location_warehouse_code'
    ) THEN
        ALTER TABLE location
        ADD CONSTRAINT uq_location_warehouse_code
        UNIQUE (warehouse_id, code);
    END IF;
END $$;

-- Verify the fix
SELECT
    'SUCCESS: Multi-tenancy constraint fix applied' AS status,
    COUNT(*) FILTER (WHERE conname = 'uq_location_warehouse_code') AS compound_constraint_exists,
    COUNT(*) FILTER (WHERE conname = 'location_code_key') AS old_constraint_exists
FROM pg_constraint
WHERE conrelid = 'location'::regclass
  AND contype = 'u';

COMMIT;

-- ============================================================================
-- EXPECTED OUTPUT:
--   status: SUCCESS: Multi-tenancy constraint fix applied
--   compound_constraint_exists: 1
--   old_constraint_exists: 0
-- ============================================================================
