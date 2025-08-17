-- Clean Production Database - Remove DEFAULT Warehouse
-- Run this in production PostgreSQL to fix warehouse detection issues

-- Step 1: Check current warehouse distribution
SELECT 
    warehouse_id,
    COUNT(*) as location_count,
    COUNT(DISTINCT location_type) as location_types
FROM location 
GROUP BY warehouse_id 
ORDER BY warehouse_id;

-- Step 2: Show sample DEFAULT warehouse locations (if any)
SELECT 
    warehouse_id,
    code,
    location_type,
    zone
FROM location 
WHERE warehouse_id = 'DEFAULT'
LIMIT 10;

-- Step 3: BACKUP DEFAULT warehouse data (optional - for safety)
-- CREATE TABLE location_backup_default AS 
-- SELECT * FROM location WHERE warehouse_id = 'DEFAULT';

-- Step 4: Remove DEFAULT warehouse locations
-- UNCOMMENT THE FOLLOWING LINES AFTER REVIEWING THE DATA ABOVE:

-- DELETE FROM location WHERE warehouse_id = 'DEFAULT';

-- Step 5: Remove DEFAULT warehouse configuration (if exists)
-- DELETE FROM warehouse_config WHERE warehouse_id = 'DEFAULT';

-- Step 6: Verify cleanup
SELECT 
    warehouse_id,
    COUNT(*) as location_count
FROM location 
GROUP BY warehouse_id 
ORDER BY warehouse_id;

-- Step 7: Test specific locations that should be in USER_TESTF
SELECT 
    code,
    warehouse_id,
    location_type
FROM location 
WHERE code IN ('02-1-011B', '01-1-007B', 'RECV-01', 'STAGE-01', 'DOCK-01')
ORDER BY code;