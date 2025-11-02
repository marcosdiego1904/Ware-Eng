-- Add is_admin column to user table
-- Run this SQL script in your PostgreSQL database

-- Add the column if it doesn't exist
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE NOT NULL;

-- Set your admin user to is_admin = TRUE
-- Replace 'marcos1904' with your actual admin username
UPDATE "user" SET is_admin = TRUE WHERE username = 'marcos1904';

-- Verify the change
SELECT id, username, is_admin FROM "user" WHERE username = 'marcos1904';
