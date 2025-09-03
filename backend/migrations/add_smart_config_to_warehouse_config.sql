-- Smart Configuration System - WarehouseConfig Migration
-- Adds Smart Configuration columns to warehouse_config table

-- Add Smart Configuration columns to warehouse_config table
ALTER TABLE warehouse_config 
ADD COLUMN IF NOT EXISTS location_format_config TEXT;

ALTER TABLE warehouse_config 
ADD COLUMN IF NOT EXISTS format_confidence FLOAT DEFAULT 0.0;

ALTER TABLE warehouse_config 
ADD COLUMN IF NOT EXISTS format_examples TEXT;

ALTER TABLE warehouse_config 
ADD COLUMN IF NOT EXISTS format_learned_date TIMESTAMP;

-- Add comments for documentation
COMMENT ON COLUMN warehouse_config.location_format_config IS 'JSON configuration from SmartFormatDetector for location format parsing';
COMMENT ON COLUMN warehouse_config.format_confidence IS 'Detection confidence score (0.0-1.0) for the location format';
COMMENT ON COLUMN warehouse_config.format_examples IS 'JSON array of original user examples used for format detection';
COMMENT ON COLUMN warehouse_config.format_learned_date IS 'When the location format was detected/learned';

-- Update any existing configs to have default values
UPDATE warehouse_config 
SET format_confidence = 0.0
WHERE format_confidence IS NULL;

-- Verify migration
SELECT 
    'Smart Configuration WarehouseConfig migration completed' as status,
    COUNT(*) as existing_configs_updated
FROM warehouse_config 
WHERE format_confidence IS NOT NULL;