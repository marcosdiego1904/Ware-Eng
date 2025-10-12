-- PostgreSQL Transaction Error Diagnostic Script
-- Run this in your PostgreSQL database to identify orphaned location records

-- Step 1: Check for locations with invalid user references
SELECT
    'Orphaned Locations' as issue_type,
    COUNT(*) as count,
    STRING_AGG(l.code, ', ') as affected_codes
FROM location l
LEFT JOIN "user" u ON l.created_by = u.id
WHERE l.warehouse_id = 'DEFAULT'
AND u.id IS NULL;

-- Step 2: Find all locations for warehouse DEFAULT with their user status
SELECT
    l.id,
    l.code,
    l.warehouse_id,
    l.location_type,
    l.created_by,
    u.username as creator_name,
    CASE
        WHEN u.id IS NULL THEN 'ORPHANED - No User'
        ELSE 'OK'
    END as status
FROM location l
LEFT JOIN "user" u ON l.created_by = u.id
WHERE l.warehouse_id = 'DEFAULT'
ORDER BY l.created_at DESC
LIMIT 50;

-- Step 3: Count locations by warehouse and user status
SELECT
    l.warehouse_id,
    COUNT(*) as total_locations,
    COUNT(u.id) as valid_user_refs,
    COUNT(*) - COUNT(u.id) as orphaned_refs
FROM location l
LEFT JOIN "user" u ON l.created_by = u.id
GROUP BY l.warehouse_id
ORDER BY orphaned_refs DESC;

-- Step 4: Find a valid user ID to use for fixing orphaned records
SELECT
    id as user_id,
    username,
    email,
    created_at
FROM "user"
WHERE is_active = true
ORDER BY created_at ASC
LIMIT 5;

-- ===================================================================
-- FIXES (Uncomment ONE of these options after reviewing diagnostic output)
-- ===================================================================

-- OPTION A: Update orphaned locations to use the first valid user
-- Replace <USER_ID> with a valid user ID from Step 4
-- UPDATE location
-- SET created_by = <USER_ID>
-- WHERE created_by NOT IN (SELECT id FROM "user");

-- OPTION B: Delete orphaned locations (USE WITH CAUTION)
-- DELETE FROM location
-- WHERE created_by NOT IN (SELECT id FROM "user");

-- ===================================================================
-- VERIFICATION: Run this after applying a fix
-- ===================================================================
-- SELECT COUNT(*) as remaining_orphaned
-- FROM location l
-- LEFT JOIN "user" u ON l.created_by = u.id
-- WHERE u.id IS NULL;
