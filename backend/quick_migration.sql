-- Quick Migration: Add Missing User Columns
-- Run this directly in your PostgreSQL client or psql
-- Safe to run multiple times (idempotent)

BEGIN;

-- Add clear_previous_anomalies column
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS clear_previous_anomalies BOOLEAN DEFAULT true NOT NULL;

-- Add show_clear_warning column
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS show_clear_warning BOOLEAN DEFAULT true NOT NULL;

-- Add max_reports column
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS max_reports INTEGER DEFAULT 100 NOT NULL;

-- Add max_templates column
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS max_templates INTEGER DEFAULT 50 NOT NULL;

COMMIT;

-- Verify the migration
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'user'
AND column_name IN ('clear_previous_anomalies', 'show_clear_warning', 'max_reports', 'max_templates')
ORDER BY column_name;
