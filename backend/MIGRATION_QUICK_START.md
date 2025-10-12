# Quick Start: Production Database Migration

## Problem
Authentication failing with error:
```
psycopg2.errors.UndefinedColumn: column user.clear_previous_anomalies does not exist
```

## Solution
Add 4 missing columns to PostgreSQL `user` table.

---

## Option 1: Automated (Recommended)

```bash
cd backend
python run_user_preferences_migration.py
```

**That's it!** The script will:
- Validate database connection
- Check existing columns
- Apply migration safely
- Verify success
- Report results

---

## Option 2: Manual SQL

```bash
psql $DATABASE_URL -f backend/migrations/add_user_analysis_preferences.sql
```

---

## Verify Success

```sql
-- Should return 4 rows
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'user'
AND column_name IN (
    'clear_previous_anomalies',
    'show_clear_warning',
    'max_reports',
    'max_templates'
);
```

---

## Safety Features

- **Idempotent:** Safe to run multiple times
- **Transactional:** Auto-rollback on error
- **Zero-Downtime:** No table locks
- **No Data Loss:** Only adds columns

---

## Before You Run

1. **Backup database** (mandatory)
2. Set `DATABASE_URL` environment variable
3. Run from `backend/` directory

---

## Expected Runtime

- **Small database (<1000 users):** 1-2 seconds
- **Large database (>10000 users):** 2-5 seconds

---

## Need Help?

See full documentation: `PRODUCTION_MIGRATION_GUIDE.md`

---

## Columns Being Added

| Column | Type | Default | Purpose |
|--------|------|---------|---------|
| `clear_previous_anomalies` | BOOLEAN | TRUE | Auto-clear old anomalies |
| `show_clear_warning` | BOOLEAN | TRUE | Show warning modal |
| `max_reports` | INTEGER | 5 | Report limit per user |
| `max_templates` | INTEGER | 5 | Template limit per user |

All existing users will get these default values automatically.
