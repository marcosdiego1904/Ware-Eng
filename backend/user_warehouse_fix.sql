-- CRITICAL SECURITY FIX: Add user-warehouse association
-- This fixes the multi-tenancy security issue

-- Option 1: Add warehouse_id to User model (Simple approach)
ALTER TABLE user ADD COLUMN warehouse_id VARCHAR(50);

-- Option 2: Create many-to-many relationship (Advanced approach)  
CREATE TABLE user_warehouse (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user(id) ON DELETE CASCADE,
    warehouse_id VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'ANALYST',  -- ADMIN, ANALYST, VIEWER
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, warehouse_id)
);

-- Update existing users to associate them with their warehouses
-- This will need to be done based on your current user-warehouse mapping