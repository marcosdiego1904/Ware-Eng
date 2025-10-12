-- ============================================================================
-- COMPREHENSIVE PRODUCTION SCHEMA SYNC
-- Adds all missing columns from development to production PostgreSQL
-- Safe to run multiple times (uses IF NOT EXISTS)
-- ============================================================================

BEGIN;

-- ============================================================================
-- USER TABLE
-- ============================================================================
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS clear_previous_anomalies BOOLEAN DEFAULT true NOT NULL;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS show_clear_warning BOOLEAN DEFAULT true NOT NULL;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS max_reports INTEGER DEFAULT 100 NOT NULL;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS max_templates INTEGER DEFAULT 50 NOT NULL;

-- ============================================================================
-- ANALYSIS_REPORT TABLE
-- ============================================================================
ALTER TABLE analysis_report ADD COLUMN IF NOT EXISTS inventory_count INTEGER;
ALTER TABLE analysis_report ADD COLUMN IF NOT EXISTS warehouse_id VARCHAR(50);
ALTER TABLE analysis_report ADD COLUMN IF NOT EXISTS template_id INTEGER;

-- ============================================================================
-- LOCATION TABLE
-- ============================================================================
ALTER TABLE location ADD COLUMN IF NOT EXISTS unit_type VARCHAR(50) DEFAULT 'pallets';
ALTER TABLE location ADD COLUMN IF NOT EXISTS is_tracked BOOLEAN DEFAULT true;

-- ============================================================================
-- WAREHOUSE_CONFIG TABLE
-- ============================================================================
ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS location_format_config TEXT;
ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_confidence FLOAT DEFAULT 0.0;
ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_examples TEXT;
ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_learned_date TIMESTAMP;
ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS max_position_digits INTEGER DEFAULT 6;

-- ============================================================================
-- WAREHOUSE_TEMPLATE TABLE
-- ============================================================================
ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS location_format_config TEXT;
ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS format_confidence FLOAT DEFAULT 0.0;
ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS format_examples TEXT;
ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS format_learned_date TIMESTAMP;
ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS max_position_digits INTEGER DEFAULT 6;

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify user table
SELECT 'user table columns:' as info;
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'user'
AND column_name IN ('clear_previous_anomalies', 'show_clear_warning', 'max_reports', 'max_templates')
ORDER BY column_name;

-- Verify analysis_report table
SELECT 'analysis_report table columns:' as info;
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'analysis_report'
AND column_name IN ('inventory_count', 'warehouse_id', 'template_id')
ORDER BY column_name;

-- Verify location table
SELECT 'location table columns:' as info;
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'location'
AND column_name IN ('unit_type', 'is_tracked')
ORDER BY column_name;

-- Verify warehouse_config table
SELECT 'warehouse_config table columns:' as info;
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'warehouse_config'
AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date', 'max_position_digits')
ORDER BY column_name;

-- Verify warehouse_template table
SELECT 'warehouse_template table columns:' as info;
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'warehouse_template'
AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date', 'max_position_digits')
ORDER BY column_name;

SELECT '✅ Schema sync complete!' as status;
