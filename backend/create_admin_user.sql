-- Create admin and pilot users directly in PostgreSQL
-- This is a backup method if the Python script didn't connect to prod DB

-- First, let's just promote an existing user to admin
-- Replace 'marcos9' with the username you want to make admin
UPDATE "user" SET is_admin = TRUE WHERE username = 'marcos9';

-- Verify the change
SELECT id, username, is_admin FROM "user" WHERE is_admin = TRUE;

-- If you want to create a completely new admin user with a specific password,
-- you'll need to generate a password hash using Python/Werkzeug
-- For now, just promote an existing user
