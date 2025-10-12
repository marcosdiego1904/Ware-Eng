-- Migration: Add inventory_count field to analysis_report table
-- Purpose: Store the total number of pallets/items from uploaded inventory files
--          to enable accurate warehouse space utilization calculations

-- SQLite syntax (compatible with PostgreSQL)
ALTER TABLE analysis_report ADD COLUMN inventory_count INTEGER;

-- Add comment explaining the field
-- Note: SQLite doesn't support COMMENT ON COLUMN, but PostgreSQL does
-- For PostgreSQL:
-- COMMENT ON COLUMN analysis_report.inventory_count IS 'Total number of pallets/items in the uploaded inventory file';
