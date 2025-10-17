-- Fix missing exclusion_rules column in rule table
-- This script adds the exclusion_rules column that was missing from the database
-- Safe to run multiple times (uses IF NOT EXISTS check)

-- Add exclusion_rules column if it doesn't exist
DO $$
BEGIN
    -- Check if exclusion_rules column exists
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'rule'
        AND column_name = 'exclusion_rules'
    ) THEN
        -- Add the column
        ALTER TABLE rule ADD COLUMN exclusion_rules TEXT;
        RAISE NOTICE 'Added exclusion_rules column to rule table';
    ELSE
        RAISE NOTICE 'exclusion_rules column already exists';
    END IF;

    -- Check if precedence_level column exists (should already exist based on error)
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'rule'
        AND column_name = 'precedence_level'
    ) THEN
        -- Add the column
        ALTER TABLE rule ADD COLUMN precedence_level INTEGER DEFAULT 4;
        RAISE NOTICE 'Added precedence_level column to rule table';
    ELSE
        RAISE NOTICE 'precedence_level column already exists';
    END IF;
END $$;

-- Verify the columns exist
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'rule'
AND column_name IN ('exclusion_rules', 'precedence_level')
ORDER BY column_name;
