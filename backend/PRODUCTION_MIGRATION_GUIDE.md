# Production Database Migration Guide
## User Analysis Preferences & Limits

**Date:** 2025-10-12
**Migration Type:** Schema Addition (Non-Breaking)
**Risk Level:** LOW
**Estimated Downtime:** 0 seconds (zero-downtime migration)

---

## Executive Summary

The production PostgreSQL database is missing 4 columns that exist in the development SQLite database, causing authentication failures when the application attempts to query these columns.

### Missing Columns:
1. `clear_previous_anomalies` (BOOLEAN) - User preference for clearing previous anomalies
2. `show_clear_warning` (BOOLEAN) - Whether to show warning modal
3. `max_reports` (INTEGER) - Maximum analysis reports per user
4. `max_templates` (INTEGER) - Maximum warehouse templates per user

### Error Being Fixed:
```
psycopg2.errors.UndefinedColumn: column user.clear_previous_anomalies does not exist
LINE 1: ...name, "user".password_hash AS user_password_hash, "user".cle...
```

---

## Files Provided

### 1. Migration SQL Script
**File:** `backend/migrations/add_user_analysis_preferences.sql`

- Pure PostgreSQL migration script
- Idempotent (safe to run multiple times)
- Wrapped in transaction with automatic rollback on error
- Includes column comments for documentation
- Built-in verification checks

### 2. Python Migration Runner
**File:** `backend/run_user_preferences_migration.py`

- Automated migration execution
- Pre-flight validation
- Post-migration verification
- Comprehensive error handling
- Production safety checks

---

## Pre-Migration Checklist

- [ ] **Backup database** (MANDATORY - no exceptions)
- [ ] Verify `DATABASE_URL` environment variable is set
- [ ] Ensure PostgreSQL version is 9.5+ (ideally 12+)
- [ ] Confirm user table exists and has active users
- [ ] Review migration SQL script
- [ ] Schedule migration during low-traffic period (optional but recommended)
- [ ] Notify team of migration schedule

---

## Migration Methods

You can apply this migration using either method:

### Method 1: Python Script (Recommended)

**Advantages:**
- Automated pre-flight checks
- Built-in verification
- Clear success/failure reporting
- Safe for production use

**Steps:**

```bash
# 1. Navigate to backend directory
cd backend

# 2. Ensure environment is configured
# Make sure .env file has DATABASE_URL or set it:
export DATABASE_URL="postgresql://user:password@host:port/database"

# 3. Run migration script
python run_user_preferences_migration.py
```

**Expected Output:**
```
================================================================================
PostgreSQL User Preferences Migration
================================================================================
Started at: 2025-10-12 10:30:00

[1/6] Environment and imports loaded successfully
[2/6] Database connection configured
      Database: your-database-host/database-name
[3/6] Migration SQL loaded from: add_user_analysis_preferences.sql
[4/6] Database connection verified
      PostgreSQL version: PostgreSQL 14.5 on ...
[5/6] Pre-flight checks completed
      Existing columns: 0 out of 4
      Will add: clear_previous_anomalies, show_clear_warning, max_reports, max_templates

[6/6] Executing migration...
--------------------------------------------------------------------------------
NOTICE:  Added column: clear_previous_anomalies
NOTICE:  Added column: show_clear_warning
NOTICE:  Added column: max_reports
NOTICE:  Added column: max_templates
NOTICE:  ================================================
NOTICE:  Migration verification: 4 out of 4 columns exist
NOTICE:  ================================================
NOTICE:  SUCCESS: All 4 columns have been added successfully!
--------------------------------------------------------------------------------

SUCCESS: Migration executed successfully!

Post-Migration Verification
--------------------------------------------------------------------------------
All 4 columns verified successfully:

  clear_previous_anomalies       boolean         DEFAULT true                 NO
  max_reports                    integer         DEFAULT 5                    NO
  max_templates                  integer         DEFAULT 5                    NO
  show_clear_warning             boolean         DEFAULT true                 NO

VERIFICATION PASSED
Total users in database: 15
All users will have default values applied

================================================================================
Migration completed successfully!
Finished at: 2025-10-12 10:30:02
================================================================================
```

---

### Method 2: Direct SQL Execution

**Use this method if:**
- Python environment is not available
- Direct database access is preferred
- Running via database management tool (pgAdmin, psql, etc.)

**Steps:**

```bash
# Using psql command line
psql $DATABASE_URL -f backend/migrations/add_user_analysis_preferences.sql

# Or connect to database and run:
\i backend/migrations/add_user_analysis_preferences.sql
```

**Expected Output:**
```
BEGIN
NOTICE:  Added column: clear_previous_anomalies
NOTICE:  Added column: show_clear_warning
NOTICE:  Added column: max_reports
NOTICE:  Added column: max_templates
NOTICE:  ================================================
NOTICE:  Migration verification: 4 out of 4 columns exist
NOTICE:  ================================================
NOTICE:  SUCCESS: All 4 columns have been added successfully!
COMMIT
```

---

## Post-Migration Verification

### Automatic Verification
The migration includes automatic verification. If using the Python script, verification is included.

### Manual Verification (Optional)

Run these queries to manually verify the migration:

```sql
-- 1. Verify columns exist with correct definitions
SELECT
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'user'
AND column_name IN (
    'clear_previous_anomalies',
    'show_clear_warning',
    'max_reports',
    'max_templates'
)
ORDER BY column_name;

-- Expected result: 4 rows with:
-- clear_previous_anomalies | boolean | true | NO
-- show_clear_warning       | boolean | true | NO
-- max_reports              | integer | 5    | NO
-- max_templates            | integer | 5    | NO
```

```sql
-- 2. Verify all users have default values
SELECT
    id,
    username,
    clear_previous_anomalies,
    show_clear_warning,
    max_reports,
    max_templates
FROM "user"
LIMIT 10;

-- Expected: All users should have:
-- clear_previous_anomalies: true
-- show_clear_warning: true
-- max_reports: 5
-- max_templates: 5
```

```sql
-- 3. Count affected users
SELECT COUNT(*) as total_users FROM "user";

-- All users will have the new columns with default values
```

---

## Testing Authentication

After migration, test that authentication works correctly:

```bash
# Test login endpoint
curl -X POST https://your-api-url/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Expected: 200 OK with JWT token
# The error "column user.clear_previous_anomalies does not exist" should be GONE
```

---

## Rollback Plan

### If Migration Fails:
The migration is wrapped in a transaction and will automatically rollback on any error. No manual rollback needed.

### If Need to Manually Remove Columns:
**WARNING:** Only do this if absolutely necessary and you understand the implications.

```sql
-- DANGER: This will drop data. Only use for emergency rollback.
BEGIN;

ALTER TABLE "user" DROP COLUMN IF EXISTS clear_previous_anomalies;
ALTER TABLE "user" DROP COLUMN IF EXISTS show_clear_warning;
ALTER TABLE "user" DROP COLUMN IF EXISTS max_reports;
ALTER TABLE "user" DROP COLUMN IF EXISTS max_templates;

COMMIT;
```

---

## What Changed?

### Before Migration:
```sql
CREATE TABLE "user" (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(200)
    -- Missing 4 columns here
);
```

### After Migration:
```sql
CREATE TABLE "user" (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(200),
    clear_previous_anomalies BOOLEAN NOT NULL DEFAULT TRUE,
    show_clear_warning BOOLEAN NOT NULL DEFAULT TRUE,
    max_reports INTEGER NOT NULL DEFAULT 5,
    max_templates INTEGER NOT NULL DEFAULT 5
);
```

---

## Impact Analysis

### User Impact:
- **Downtime:** ZERO - This is a non-breaking schema addition
- **Data Loss:** NONE - No existing data is modified or removed
- **Performance:** Negligible impact (adding columns to small user table)

### Application Impact:
- **Before Migration:** Authentication FAILS with column not found error
- **After Migration:** Authentication WORKS normally
- **Compatibility:** The application code already expects these columns

### Default Values Applied:
- All existing users get `clear_previous_anomalies = TRUE`
- All existing users get `show_clear_warning = TRUE`
- All existing users get `max_reports = 5`
- All existing users get `max_templates = 5`

---

## Migration Details

### Column Specifications:

1. **clear_previous_anomalies**
   - Type: BOOLEAN
   - Default: TRUE
   - Nullable: NO
   - Purpose: User preference for clearing previous anomalies on new analysis

2. **show_clear_warning**
   - Type: BOOLEAN
   - Default: TRUE
   - Nullable: NO
   - Purpose: Whether to show warning modal before clearing anomalies

3. **max_reports**
   - Type: INTEGER
   - Default: 5
   - Nullable: NO
   - Purpose: Database efficiency limit - max analysis reports per user

4. **max_templates**
   - Type: INTEGER
   - Default: 5
   - Nullable: NO
   - Purpose: Database efficiency limit - max warehouse templates per user

---

## Troubleshooting

### Error: "DATABASE_URL environment variable not set"
**Solution:** Set the DATABASE_URL environment variable:
```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

### Error: "Migration file not found"
**Solution:** Ensure you're running from the correct directory:
```bash
cd backend
python run_user_preferences_migration.py
```

### Error: "relation 'user' does not exist"
**Solution:** Verify you're connected to the correct database with:
```sql
SELECT current_database();
\dt user
```

### Error: "column already exists"
**Solution:** This is normal! The migration is idempotent. If columns already exist, the migration will skip them safely.

### Error: "permission denied"
**Solution:** Ensure your database user has ALTER TABLE permissions:
```sql
GRANT ALTER ON TABLE "user" TO your_db_user;
```

---

## Best Practices Followed

This migration follows database administration best practices:

- **Idempotent:** Safe to run multiple times
- **Transactional:** Wrapped in BEGIN/COMMIT with automatic rollback
- **Verified:** Includes pre-flight and post-migration checks
- **Documented:** Comprehensive inline comments and external documentation
- **Defensive:** Checks for existence before adding columns
- **Logged:** RAISE NOTICE statements for operational visibility
- **Safe Defaults:** All columns have sensible default values
- **Non-Breaking:** Adds columns without modifying existing schema
- **Zero-Downtime:** No table locks or data modifications

---

## Support

### If Migration Fails:
1. Review the error message carefully
2. Check the Troubleshooting section above
3. Verify database connection and permissions
4. Review database logs for additional context
5. The transaction will automatically rollback - no corruption possible

### If Authentication Still Fails After Migration:
1. Verify all 4 columns exist (see Manual Verification section)
2. Check application logs for different error messages
3. Restart application servers to ensure new schema is detected
4. Verify SQLAlchemy models match database schema

---

## Post-Migration Tasks

After successful migration:

- [ ] Verify authentication works (test login)
- [ ] Monitor application logs for any errors
- [ ] Update team on successful migration
- [ ] Document migration timestamp in change log
- [ ] Mark this migration as completed in tracking system
- [ ] Keep backup for 7 days before deletion

---

## Questions?

This migration has been designed to be as safe and automated as possible. The Python runner includes extensive checks and will clearly report success or failure.

**Remember:** Always backup before any database modification!
