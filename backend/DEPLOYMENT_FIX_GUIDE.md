# Emergency Deployment Fix Guide
## Production Stabilization Complete

**Date:** 2025-10-16
**Status:** ✅ Production STABLE (emergency rollback deployed)
**Issue:** Code deployed with columns that don't exist in production database

---

## What Just Happened

### The Problem
You deployed code to production that referenced two new database columns:
1. `location.warehouse_config_id` - For template-location binding
2. `rule.precedence_level` - For rule priority ordering

But these columns **don't exist** in the production database because migrations weren't run first.

### The Error
```
psycopg2.errors.UndefinedColumn: column location.warehouse_config_id does not exist
psycopg2.errors.UndefinedColumn: column rule.precedence_level does not exist
```

### The Fix (COMPLETED)
✅ Commented out both columns in `models.py`
✅ Committed changes
✅ Pushed to production
✅ Production is now stable

**Commit:** `58aaa8f - EMERGENCY: Comment out precedence_level and warehouse_config_id columns`

---

## Root Cause

### Development vs Production Mismatch

**Development (SQLite):**
- ✅ Migrations run locally
- ✅ Columns exist in database
- ✅ Code works perfectly

**Production (PostgreSQL):**
- ❌ Migrations NOT run
- ❌ Columns don't exist
- ❌ Code breaks with "column does not exist" errors

**The Mistake:**
Deployed code **before** running database migrations. This breaks the fundamental rule:

> **ALWAYS run database migrations BEFORE deploying code that uses new columns**

---

## Current State

### Models.py Status

**Commented Out (Production-Safe):**

```python
# In Location model (line 278):
# TEMPLATE BINDING: Temporarily commented out until migration runs on production
# warehouse_config_id = db.Column(db.Integer, db.ForeignKey('warehouse_config.id'))

# In Location model relationship (line 300):
# warehouse_config = db.relationship('WarehouseConfig', foreign_keys=[warehouse_config_id], backref='locations')

# In Location indexes (lines 315-316):
# db.Index('idx_location_warehouse_config', 'warehouse_config_id'),
# db.Index('idx_location_config_type', 'warehouse_config_id', 'location_type'),

# In Location.to_dict() (lines 433-434):
# 'warehouse_config_id': self.warehouse_config_id,
# 'warehouse_config_name': self.warehouse_config.warehouse_name if self.warehouse_config else None,

# In Rule model (line 70):
# MIGRATION REQUIRED: Temporarily commented out until migration runs on production
# precedence_level = db.Column(db.Integer, default=4)

# In Rule model methods (lines 107-115):
# def get_precedence_name(self):
#     """Get human-readable precedence level name"""
#     ...
```

### Migration Scripts Status

**✅ Ready to Run:**
- `backend/add_warehouse_config_id_to_locations.py` - Tested locally (100% success)

**❌ Not Created Yet:**
- `backend/add_precedence_level_to_rules.py` - Needs to be created

---

## Next Steps - Proper Deployment

### Step 1: Create Missing Migration

Create `backend/add_precedence_level_to_rules.py`:

```python
"""
Migration: Add precedence_level column to Rule table
"""
from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        # Add column
        db.session.execute(text("""
            ALTER TABLE rule
            ADD COLUMN IF NOT EXISTS precedence_level INTEGER DEFAULT 4;
        """))

        # Add index
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_rule_precedence
            ON rule(precedence_level);
        """))

        db.session.commit()
        print("✅ Migration completed successfully!")

if __name__ == '__main__':
    run_migration()
```

### Step 2: Test Migrations Locally

```bash
# Test precedence_level migration
cd backend
python add_precedence_level_to_rules.py

# Verify it works
python run_server.py
```

### Step 3: Run Migrations on Production Database

**CRITICAL:** Do this BEFORE uncommenting code!

```bash
# Option A: Run migration scripts directly on production
python backend/add_warehouse_config_id_to_locations.py
python backend/add_precedence_level_to_rules.py

# Option B: Connect to production database and run SQL
psql your-production-database-url
-- Then run the SQL from the migration scripts
```

### Step 4: Verify Migrations Succeeded

```sql
-- Check warehouse_config_id column exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'location' AND column_name = 'warehouse_config_id';

-- Expected: 1 row showing column exists

-- Check precedence_level column exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'rule' AND column_name = 'precedence_level';

-- Expected: 1 row showing column exists

-- Check data
SELECT COUNT(*) as total, COUNT(warehouse_config_id) as with_config
FROM location;

SELECT COUNT(*) as total, COUNT(precedence_level) as with_precedence
FROM rule;
```

### Step 5: Uncomment Code in models.py

Only after migrations succeed on production, uncomment all the commented sections:

```python
# Uncomment in Location model:
warehouse_config_id = db.Column(db.Integer, db.ForeignKey('warehouse_config.id'))
warehouse_config = db.relationship('WarehouseConfig', foreign_keys=[warehouse_config_id], backref='locations')
# ... indexes ...
# ... to_dict() fields ...

# Uncomment in Rule model:
precedence_level = db.Column(db.Integer, default=4)
def get_precedence_name(self):
    # ... method body ...
```

### Step 6: Test Locally Again

```bash
python backend/run_server.py
# Verify no errors
# Test location creation
# Test rule queries
```

### Step 7: Deploy to Production

```bash
git add backend/src/models.py
git commit -m "Restore warehouse_config_id and precedence_level columns

Migrations have been run on production database.
Safe to restore these columns now.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"
git push
```

### Step 8: Monitor Production

- Watch logs for any errors
- Test location creation
- Test template switching
- Verify rules load correctly

---

## The Correct Deployment Sequence

**Always follow this order:**

```
1. Write migration script
2. Test migration locally
3. Commit migration script
4. Run migration on production database
5. VERIFY migration succeeded
6. Write/uncomment code that uses new columns
7. Test locally with new columns
8. Deploy code to production
9. Monitor production
```

**NEVER skip steps or change the order!**

---

## Why This Happened

### Common Mistake
It's easy to forget that development and production databases are separate:

- **Development**: You run migrations frequently, database is up-to-date
- **Production**: Migrations must be run explicitly, database can be behind

### The Solution
Always think of deployment as TWO steps:
1. **Database migration** (run SQL on production database)
2. **Code deployment** (push code to production servers)

And they MUST happen in that order!

---

## Prevention

### Before Every Deployment
Ask yourself:
1. Did I add any new database columns?
2. If yes, did I run migrations on production?
3. Did I verify the migrations succeeded?

### Use a Checklist

```markdown
## Pre-Deployment Checklist
- [ ] No new database columns
  OR
- [ ] New columns added
  - [ ] Migration script created
  - [ ] Migration tested locally
  - [ ] Migration run on production
  - [ ] Migration verified (SELECT column_name...)
- [ ] Code tested locally
- [ ] Ready to deploy
```

---

## Migration Scripts Reference

### Location: warehouse_config_id
**File:** `backend/add_warehouse_config_id_to_locations.py`
**Status:** ✅ Ready to run
**Tested:** Yes (34 locations, 100% success locally)

### Rule: precedence_level
**File:** `backend/add_precedence_level_to_rules.py`
**Status:** ⚠️ Needs to be created
**Template:** See Step 1 above

---

## Rollback Plan

If you need to rollback after uncommenting code:

```bash
# Quick rollback - revert to current stable state
git revert HEAD
git push

# Manual rollback - comment out columns again
# (Same process we just completed)
```

If you need to remove columns from database:

```sql
-- WARNING: Only in emergency, data loss will occur
ALTER TABLE location DROP COLUMN IF EXISTS warehouse_config_id;
ALTER TABLE rule DROP COLUMN IF EXISTS precedence_level;
```

---

## Key Takeaways

1. **Database First, Code Second** - Always run migrations before deploying code
2. **Verify Everything** - Never assume migrations worked, always verify
3. **Test Locally** - Both migrations and code should work in development first
4. **Production is Different** - What works in development isn't automatically in production
5. **Comment Out is Better Than Breaking** - When in doubt, comment out and stabilize

---

## Current Status Summary

✅ **Production:** STABLE (columns commented out)
⏳ **Next Action:** Create precedence_level migration script
⏳ **Then:** Run both migrations on production
⏳ **Then:** Uncomment columns and deploy

**You're safe to wait and plan the proper deployment now.** Production is working, users can use the app, and you can do the migrations properly during a maintenance window or low-traffic period.

---

## Questions?

**Q: Can I just run the migrations now and uncomment immediately?**
A: Yes, but test locally first to make sure both migrations work properly.

**Q: Will running migrations cause downtime?**
A: No, adding nullable columns with defaults is a zero-downtime operation.

**Q: What if a migration fails?**
A: The migration scripts use transactions, so they'll automatically rollback. Your database will be unchanged.

**Q: Can I skip the precedence_level migration?**
A: Only if you don't need that feature. But the column is already in the code, so you'll need to either run the migration or remove references to it.

Remember: **Take your time, test thoroughly, and follow the sequence!**
