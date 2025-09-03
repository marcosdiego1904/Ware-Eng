-- =====================================================
-- Smart Configuration Migration for PostgreSQL
-- =====================================================
-- Execute this script in your Render PostgreSQL dashboard
-- to add Smart Configuration columns to warehouse_config

-- Add Smart Configuration columns to warehouse_config table
ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS location_format_config TEXT;
ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_confidence FLOAT DEFAULT 0.0;
ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_examples TEXT;
ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_learned_date TIMESTAMP;

-- Set default values for existing rows
UPDATE warehouse_config 
SET format_confidence = 0.0 
WHERE format_confidence IS NULL;

-- Verify the migration
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'warehouse_config'
AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
ORDER BY column_name;

-- Show success message
SELECT 'Smart Configuration migration completed successfully!' as status;