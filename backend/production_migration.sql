
-- ========================================
-- WareWise: Warehouse Context Migration
-- ========================================
-- This script creates the UserWarehouseAccess table and migrates users
-- Run this in your PostgreSQL database console


-- Step 1: Create UserWarehouseAccess table
CREATE TABLE IF NOT EXISTS user_warehouse_access (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    warehouse_id VARCHAR(50) NOT NULL,
    access_level VARCHAR(20) DEFAULT 'ADMIN',
    is_default BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, warehouse_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_warehouse ON user_warehouse_access(user_id, warehouse_id);
CREATE INDEX IF NOT EXISTS idx_user_default ON user_warehouse_access(user_id, is_default);



-- Step 2: Migrate existing users to warehouse access
INSERT INTO user_warehouse_access (user_id, warehouse_id, access_level, is_default)
SELECT 
    u.id, 
    CASE 
        WHEN LOWER(u.username) = 'testf' THEN 'USER_TESTF'
        WHEN LOWER(u.username) = 'marcos9' THEN 'USER_MARCOS9'
        WHEN LOWER(u.username) = 'hola2' THEN 'USER_HOLA2'
        WHEN LOWER(u.username) = 'hola3' THEN 'USER_HOLA3'
        WHEN LOWER(u.username) = 'marcos10' THEN 'USER_MARCOS10'
        ELSE 'USER_' || UPPER(u.username)
    END,
    'ADMIN',
    true
FROM "user" u
WHERE NOT EXISTS (
    SELECT 1 FROM user_warehouse_access uwa 
    WHERE uwa.user_id = u.id
);



-- Step 3: Verify migration results
SELECT 
    u.username,
    uwa.warehouse_id,
    uwa.access_level,
    uwa.is_default,
    uwa.created_at
FROM "user" u
JOIN user_warehouse_access uwa ON u.id = uwa.user_id
ORDER BY u.username;


-- ========================================
-- Migration Complete!
-- ========================================
-- After running this, your long-term warehouse architecture will be active
-- Users will be mapped: testf -> USER_TESTF, marcos9 -> USER_MARCOS9, etc.
