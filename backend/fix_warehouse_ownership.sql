-- Fix Multi-Tenancy: Update warehouse configs and locations to belong to correct users
-- Run this in PostgreSQL production database

-- Step 1: Show current warehouse configs without owners
SELECT
    id,
    warehouse_id,
    warehouse_name,
    created_by,
    created_at
FROM warehouse_config
WHERE created_by IS NULL OR created_by NOT IN (SELECT id FROM "user")
ORDER BY created_at DESC;

-- Step 2: Show current users
SELECT id, username FROM "user" ORDER BY id;

-- Step 3: UPDATE WAREHOUSE CONFIGS
-- Replace YOUR_USER_ID with your actual user ID from Step 2
-- If you have multiple users, run this command once for each user with their warehouses

-- Example: If your user ID is 1, and you own warehouse 'DEFAULT' or 'USER_YOURNAME'
-- UPDATE warehouse_config
-- SET created_by = 1
-- WHERE warehouse_id IN ('DEFAULT', 'USER_YOURNAME') AND (created_by IS NULL OR created_by != 1);

-- Step 4: UPDATE LOCATIONS to match warehouse config owner
-- This ensures locations belong to the same user as the warehouse config
-- UPDATE location loc
-- SET created_by = wc.created_by
-- FROM warehouse_config wc
-- WHERE loc.warehouse_id = wc.warehouse_id
-- AND loc.created_by != wc.created_by;

-- Step 5: Verify the fix
SELECT
    wc.warehouse_id,
    wc.warehouse_name,
    wc.created_by as config_owner,
    u.username as owner_name,
    COUNT(DISTINCT loc.id) as location_count
FROM warehouse_config wc
LEFT JOIN "user" u ON wc.created_by = u.id
LEFT JOIN location loc ON loc.warehouse_id = wc.warehouse_id AND loc.created_by = wc.created_by
GROUP BY wc.warehouse_id, wc.warehouse_name, wc.created_by, u.username
ORDER BY wc.created_at DESC;

-- INSTRUCTIONS:
-- 1. Run Step 1 to see warehouse configs without owners
-- 2. Run Step 2 to see your user ID
-- 3. Uncomment and modify Step 3, replacing YOUR_USER_ID and warehouse IDs
-- 4. Run Step 3 to assign warehouse configs to your user
-- 5. Uncomment and run Step 4 to sync location ownership
-- 6. Run Step 5 to verify everything is correct
