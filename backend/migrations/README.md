# Database Migrations

This directory contains SQL migration scripts for the warehouse intelligence application.

## Current Migration

### User Analysis Preferences & Limits (2025-10-12)

**Status:** Ready for Production
**File:** `add_user_analysis_preferences.sql`

Adds 4 missing columns to the `user` table:
- `clear_previous_anomalies` (BOOLEAN, default TRUE)
- `show_clear_warning` (BOOLEAN, default TRUE)
- `max_reports` (INTEGER, default 5)
- `max_templates` (INTEGER, default 5)

**Issue Fixed:**
```
psycopg2.errors.UndefinedColumn: column user.clear_previous_anomalies does not exist
```

---

## Quick Start

### Before You Begin
1. **Backup your database** (MANDATORY)
2. Run pre-flight checks:
   ```bash
   python ../preflight_check.py
   ```

### Apply Migration

**Option 1: Automated (Recommended)**
```bash
cd backend
python run_user_preferences_migration.py
```

**Option 2: Direct SQL**
```bash
psql $DATABASE_URL -f migrations/add_user_analysis_preferences.sql
```

---

## Migration Features

All migrations in this directory follow best practices:

- ✅ **Idempotent:** Safe to run multiple times
- ✅ **Transactional:** Automatic rollback on error
- ✅ **Zero-Downtime:** Non-blocking operations
- ✅ **Verified:** Built-in verification checks
- ✅ **Documented:** Inline comments and external docs

---

## Other Migrations

### Historical Migrations

- `add_smart_configuration_columns.sql` - Smart location format detection
- `add_max_position_digits_support.sql` - Enterprise warehouse support
- `add_unit_agnostic_support.sql` - Unit-agnostic inventory tracking
- `add_inventory_count_to_reports.sql` - Report inventory counts
- `add_user_limits.sql` - User resource limits (partial - superseded by current)
- `create_invitation_codes.sql` - Invitation-only registration

### Migration Order

If applying all migrations from scratch:
1. `create_invitation_codes.sql`
2. `add_user_limits.sql` (or use `add_user_analysis_preferences.sql`)
3. `add_inventory_count_to_reports.sql`
4. `add_unit_agnostic_support.sql`
5. `add_max_position_digits_support.sql`
6. `add_smart_configuration_columns.sql`
7. `add_user_analysis_preferences.sql` (current)

---

## Tools

### Pre-Flight Checker
Validates environment before migration:
```bash
python backend/preflight_check.py
```

### Schema Validator
Checks for schema drift across all models:
```bash
python backend/check_schema_mismatch.py
```

### Migration Runner
Automated migration with comprehensive checks:
```bash
python backend/run_user_preferences_migration.py
```

---

## Documentation

- **Quick Start:** `../MIGRATION_QUICK_START.md`
- **Complete Guide:** `../PRODUCTION_MIGRATION_GUIDE.md`
- **Summary:** `../../PRODUCTION_DATABASE_MIGRATION_SUMMARY.md`

---

## Support

For issues or questions:
1. Check pre-flight results
2. Review migration logs
3. Consult troubleshooting guide
4. Run schema validator

---

## Best Practices

When creating new migrations:

1. **Make them idempotent**
   ```sql
   DO $$
   BEGIN
       IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'table' AND column_name = 'column') THEN
           ALTER TABLE table ADD COLUMN column TYPE;
       END IF;
   END $$;
   ```

2. **Wrap in transactions**
   ```sql
   BEGIN;
   -- migration code
   COMMIT;
   ```

3. **Add verification**
   ```sql
   DO $$
   BEGIN
       RAISE NOTICE 'Verification: ...';
   END $$;
   ```

4. **Include documentation**
   - Purpose of migration
   - Columns being added/modified
   - Default values and rationale
   - Rollback instructions

5. **Test on staging first**
   - Verify on development
   - Test on staging
   - Then apply to production

---

## PostgreSQL Compatibility

All migrations are designed for PostgreSQL 9.5+
Tested on: PostgreSQL 12, 13, 14, 15, 16

Some migrations have SQLite fallback versions for development.

---

## Safety Checklist

Before running any migration in production:

- [ ] Database backup created
- [ ] Pre-flight checks passed
- [ ] Migration script reviewed
- [ ] Staging environment tested (if available)
- [ ] Team notified
- [ ] Low-traffic window scheduled (optional)
- [ ] Rollback plan ready

---

Last Updated: 2025-10-12
