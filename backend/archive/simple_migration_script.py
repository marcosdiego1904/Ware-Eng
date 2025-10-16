"""
Simple migration script that you can run locally to create SQL commands
These commands can then be executed via any PostgreSQL client or API endpoint
"""

def generate_migration_sql():
    """Generate the SQL commands needed for production migration"""
    
    # Step 1: Create table
    create_table = """
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
"""

    # Step 2: Migrate users
    migrate_users = """
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
"""

    # Step 3: Verification
    verify = """
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
"""

    # Complete script
    complete_script = f"""
-- ========================================
-- WareWise: Warehouse Context Migration
-- ========================================
-- This script creates the UserWarehouseAccess table and migrates users
-- Run this in your PostgreSQL database console

{create_table}

{migrate_users}

{verify}

-- ========================================
-- Migration Complete!
-- ========================================
-- After running this, your long-term warehouse architecture will be active
-- Users will be mapped: testf -> USER_TESTF, marcos9 -> USER_MARCOS9, etc.
"""

    return complete_script

if __name__ == "__main__":
    script = generate_migration_sql()
    
    # Save to file
    with open('production_migration.sql', 'w') as f:
        f.write(script)
    
    print("=" * 60)
    print("🚀 WAREHOUSE MIGRATION SQL GENERATED")
    print("=" * 60)
    print("\nFile saved: production_migration.sql")
    print("\nCopy and paste the SQL below into your PostgreSQL console:")
    print("=" * 60)
    print(script)
    print("=" * 60)
    print("\n✅ After running this SQL, your production system will have:")
    print("   • UserWarehouseAccess table created")
    print("   • All users mapped to their warehouses")
    print("   • Long-term architecture activated")
    print("   • No more temporal fixes needed")
    print("   • Enterprise-grade warehouse resolution")