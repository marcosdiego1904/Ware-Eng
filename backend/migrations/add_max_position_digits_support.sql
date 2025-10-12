-- Migration: Add Extended Position Digits Support
-- Adds max_position_digits column to warehouse_config and warehouse_template tables
-- for enterprise-scale warehouse support (locations like 1230A, 9999C, etc.)

BEGIN;

-- Add max_position_digits column to warehouse_config table
ALTER TABLE warehouse_config 
ADD COLUMN IF NOT EXISTS max_position_digits INTEGER DEFAULT 6;

-- Add max_position_digits column to warehouse_template table  
ALTER TABLE warehouse_template
ADD COLUMN IF NOT EXISTS max_position_digits INTEGER DEFAULT 6;

-- Update existing records to have the default value of 6 (supports up to 999999)
UPDATE warehouse_config 
SET max_position_digits = 6 
WHERE max_position_digits IS NULL;

UPDATE warehouse_template
SET max_position_digits = 6
WHERE max_position_digits IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN warehouse_config.max_position_digits IS 'Maximum digits allowed in position field for location codes (1-6, default: 6 = 999999 max)';
COMMENT ON COLUMN warehouse_template.max_position_digits IS 'Maximum digits allowed in position field for location codes (1-6, default: 6 = 999999 max)';

-- Create index for performance on frequently queried field
CREATE INDEX IF NOT EXISTS idx_warehouse_config_position_digits ON warehouse_config(max_position_digits);
CREATE INDEX IF NOT EXISTS idx_warehouse_template_position_digits ON warehouse_template(max_position_digits);

-- Verify the migration
SELECT 
    'warehouse_config' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE max_position_digits = 6) as records_with_default_value,
    MIN(max_position_digits) as min_digits,
    MAX(max_position_digits) as max_digits
FROM warehouse_config
UNION ALL
SELECT 
    'warehouse_template' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE max_position_digits = 6) as records_with_default_value,
    MIN(max_position_digits) as min_digits,
    MAX(max_position_digits) as max_digits
FROM warehouse_template;

COMMIT;

-- Show migration completion status
SELECT 'Extended Position Digits migration completed successfully' as status;
SELECT 'Default max_position_digits = 6 (supports locations up to 999999A)' as configuration;
SELECT 'Existing warehouses can now handle enterprise-scale location codes like 1230A, 5678B, etc.' as enhancement;