-- Migration: Create invitation_code table
-- Purpose: Implement invitation-only registration system
-- This migration provides TWO versions: SQLite and PostgreSQL

-- ========================================
-- SECTION 1: SQLite Version
-- ========================================
-- Use this version for local development with SQLite
-- Uncomment the lines below for SQLite:

/*
CREATE TABLE IF NOT EXISTS invitation_code (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    created_by INTEGER,
    used_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    max_uses INTEGER DEFAULT 1 NOT NULL,
    current_uses INTEGER DEFAULT 0 NOT NULL,
    expires_at TIMESTAMP,
    notes VARCHAR(255),
    FOREIGN KEY (created_by) REFERENCES user(id),
    FOREIGN KEY (used_by) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_invitation_code ON invitation_code(code);
CREATE INDEX IF NOT EXISTS idx_invitation_code_active ON invitation_code(code, is_active);
CREATE INDEX IF NOT EXISTS idx_invitation_created_by ON invitation_code(created_by);
*/

-- ========================================
-- SECTION 2: PostgreSQL Version
-- ========================================
-- Use this version for production with PostgreSQL
-- Uncomment the lines below for PostgreSQL:

/*
CREATE TABLE IF NOT EXISTS invitation_code (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    created_by INTEGER REFERENCES "user"(id),
    used_by INTEGER REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    max_uses INTEGER DEFAULT 1 NOT NULL,
    current_uses INTEGER DEFAULT 0 NOT NULL,
    expires_at TIMESTAMP,
    notes VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_invitation_code ON invitation_code(code);
CREATE INDEX IF NOT EXISTS idx_invitation_code_active ON invitation_code(code, is_active);
CREATE INDEX IF NOT EXISTS idx_invitation_created_by ON invitation_code(created_by);

-- PostgreSQL-specific comments
COMMENT ON TABLE invitation_code IS 'Invitation codes for controlling user registration';
COMMENT ON COLUMN invitation_code.code IS 'Unique invitation code string';
COMMENT ON COLUMN invitation_code.max_uses IS 'Maximum number of times this code can be used';
COMMENT ON COLUMN invitation_code.current_uses IS 'Number of times this code has been used';
COMMENT ON COLUMN invitation_code.expires_at IS 'Optional expiration date for the invitation';
*/

-- ========================================
-- INSTRUCTIONS
-- ========================================
-- 1. For SQLite (local development):
--    - Uncomment SECTION 1 (lines 10-27)
--    - Run: sqlite3 instance/database.db < migrations/create_invitation_codes.sql
--
-- 2. For PostgreSQL (production):
--    - Uncomment SECTION 2 (lines 33-56)
--    - Connect to your PostgreSQL database
--    - Run: psql -d your_database < migrations/create_invitation_codes.sql
--
-- 3. Or use SQLAlchemy:
--    - The models are already defined in core_models.py
--    - Run: python -c "from app import app, db; app.app_context().push(); db.create_all()"

-- ========================================
-- Verification queries
-- ========================================
-- After migration, verify the table was created:
-- SELECT * FROM invitation_code LIMIT 5;
--
-- Test creating an invitation (manual):
-- INSERT INTO invitation_code (code, created_by, max_uses) VALUES ('TEST123ABC', 1, 5);
