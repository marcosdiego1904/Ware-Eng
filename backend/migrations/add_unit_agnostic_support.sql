-- Migration: Add Unit-Agnostic Warehouse Intelligence Support
-- Date: September 14, 2025
-- Author: Lead Backend Developer

-- Step 1: Add unit_type and tracking columns to existing location table
ALTER TABLE location ADD COLUMN unit_type VARCHAR(50) DEFAULT 'pallets';
ALTER TABLE location ADD COLUMN is_tracked BOOLEAN DEFAULT TRUE;

-- Step 2: Add constraints for data integrity
ALTER TABLE location ADD CONSTRAINT chk_unit_type
    CHECK (unit_type IN ('pallets', 'boxes', 'items', 'cases', 'mixed'));

-- Step 3: Create warehouse scope configuration table
CREATE TABLE warehouse_scope_config (
    warehouse_id INTEGER PRIMARY KEY REFERENCES warehouse_config(warehouse_id),
    excluded_patterns TEXT[] DEFAULT '{}',
    default_unit_type VARCHAR(50) DEFAULT 'pallets',
    config_metadata JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 4: Add performance indexes
CREATE INDEX idx_location_tracking ON location(warehouse_id, is_tracked, unit_type);
CREATE INDEX idx_warehouse_scope_config_warehouse_id ON warehouse_scope_config(warehouse_id);

-- Step 5: Create default scope configurations for existing warehouses
INSERT INTO warehouse_scope_config (warehouse_id, excluded_patterns, default_unit_type)
SELECT DISTINCT wc.warehouse_id, '{}', 'pallets'
FROM warehouse_config wc
WHERE wc.warehouse_id NOT IN (SELECT warehouse_id FROM warehouse_scope_config WHERE warehouse_id IS NOT NULL);

-- Step 6: Update existing locations to be tracked with pallet unit type
UPDATE location
SET unit_type = 'pallets', is_tracked = TRUE
WHERE unit_type IS NULL OR is_tracked IS NULL;

-- Verification queries (for manual testing)
-- SELECT COUNT(*) FROM location WHERE unit_type = 'pallets';
-- SELECT COUNT(*) FROM warehouse_scope_config;
-- SELECT warehouse_id, excluded_patterns, default_unit_type FROM warehouse_scope_config LIMIT 5;