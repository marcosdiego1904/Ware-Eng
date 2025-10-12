-- Migration: Add user resource limits
-- Purpose: Add max_reports and max_templates columns to control database growth per user
-- Compatible with both SQLite and PostgreSQL

-- Add max_reports column (default 5)
ALTER TABLE user ADD COLUMN max_reports INTEGER DEFAULT 5 NOT NULL;

-- Add max_templates column (default 5)
ALTER TABLE user ADD COLUMN max_templates INTEGER DEFAULT 5 NOT NULL;

-- PostgreSQL-only comments (SQLite will ignore these lines)
-- COMMENT ON COLUMN user.max_reports IS 'Maximum number of analysis reports allowed per user';
-- COMMENT ON COLUMN user.max_templates IS 'Maximum number of warehouse templates allowed per user';

-- Verification query (run this after migration to verify)
-- SELECT id, username, max_reports, max_templates FROM user LIMIT 5;
