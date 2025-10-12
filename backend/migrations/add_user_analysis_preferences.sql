-- ========================================================================
-- PostgreSQL Migration: Add User Analysis Preferences and Limits
-- ========================================================================
-- Purpose: Add missing columns to the "user" table in production PostgreSQL
--
-- Missing columns:
--   1. clear_previous_anomalies (BOOLEAN) - User preference for clearing anomalies
--   2. show_clear_warning (BOOLEAN) - Whether to show warning modal
--   3. max_reports (INTEGER) - Maximum analysis reports per user
--   4. max_templates (INTEGER) - Maximum warehouse templates per user
--
-- This migration is IDEMPOTENT - safe to run multiple times
-- ========================================================================

-- Start transaction for atomic execution
BEGIN;

-- ========================================================================
-- 1. Add clear_previous_anomalies column
-- ========================================================================
DO $$
BEGIN
    -- Check if column exists before adding
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'user'
        AND column_name = 'clear_previous_anomalies'
    ) THEN
        ALTER TABLE "user"
        ADD COLUMN clear_previous_anomalies BOOLEAN NOT NULL DEFAULT TRUE;

        RAISE NOTICE 'Added column: clear_previous_anomalies';
    ELSE
        RAISE NOTICE 'Column clear_previous_anomalies already exists, skipping...';
    END IF;
END $$;

-- ========================================================================
-- 2. Add show_clear_warning column
-- ========================================================================
DO $$
BEGIN
    -- Check if column exists before adding
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'user'
        AND column_name = 'show_clear_warning'
    ) THEN
        ALTER TABLE "user"
        ADD COLUMN show_clear_warning BOOLEAN NOT NULL DEFAULT TRUE;

        RAISE NOTICE 'Added column: show_clear_warning';
    ELSE
        RAISE NOTICE 'Column show_clear_warning already exists, skipping...';
    END IF;
END $$;

-- ========================================================================
-- 3. Add max_reports column
-- ========================================================================
DO $$
BEGIN
    -- Check if column exists before adding
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'user'
        AND column_name = 'max_reports'
    ) THEN
        ALTER TABLE "user"
        ADD COLUMN max_reports INTEGER NOT NULL DEFAULT 5;

        RAISE NOTICE 'Added column: max_reports';
    ELSE
        RAISE NOTICE 'Column max_reports already exists, skipping...';
    END IF;
END $$;

-- ========================================================================
-- 4. Add max_templates column
-- ========================================================================
DO $$
BEGIN
    -- Check if column exists before adding
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'user'
        AND column_name = 'max_templates'
    ) THEN
        ALTER TABLE "user"
        ADD COLUMN max_templates INTEGER NOT NULL DEFAULT 5;

        RAISE NOTICE 'Added column: max_templates';
    ELSE
        RAISE NOTICE 'Column max_templates already exists, skipping...';
    END IF;
END $$;

-- ========================================================================
-- 5. Add column comments for documentation
-- ========================================================================
COMMENT ON COLUMN "user".clear_previous_anomalies IS
    'User preference: whether to automatically clear previous anomalies on new analysis';

COMMENT ON COLUMN "user".show_clear_warning IS
    'User preference: whether to show warning modal before clearing anomalies';

COMMENT ON COLUMN "user".max_reports IS
    'Maximum number of analysis reports allowed per user (database efficiency limit)';

COMMENT ON COLUMN "user".max_templates IS
    'Maximum number of warehouse templates allowed per user (database efficiency limit)';

-- ========================================================================
-- 6. Verification queries
-- ========================================================================
-- Display schema verification
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'user'
    AND column_name IN (
        'clear_previous_anomalies',
        'show_clear_warning',
        'max_reports',
        'max_templates'
    );

    RAISE NOTICE '================================================';
    RAISE NOTICE 'Migration verification: % out of 4 columns exist', col_count;
    RAISE NOTICE '================================================';

    IF col_count = 4 THEN
        RAISE NOTICE 'SUCCESS: All 4 columns have been added successfully!';
    ELSE
        RAISE WARNING 'WARNING: Only % columns exist. Expected 4.', col_count;
    END IF;
END $$;

-- Commit transaction
COMMIT;

-- ========================================================================
-- Post-migration verification query
-- ========================================================================
-- Run this manually after migration to verify:
--
-- SELECT
--     column_name,
--     data_type,
--     column_default,
--     is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'user'
-- AND column_name IN (
--     'clear_previous_anomalies',
--     'show_clear_warning',
--     'max_reports',
--     'max_templates'
-- )
-- ORDER BY column_name;
-- ========================================================================
