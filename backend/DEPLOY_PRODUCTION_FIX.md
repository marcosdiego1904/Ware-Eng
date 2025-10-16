# 🚨 PRODUCTION FIX: Multi-Tenancy Location Constraint

## The Problem

Users are getting this error when creating locations:
```
duplicate key value violates unique constraint "location_code_key"
DETAIL: Key (code)=(W-01) already exists.
```

This happens because the production database has an old constraint that enforces global uniqueness on location codes. User A creating "W-01" prevents User B from creating "W-01" in their own warehouse.

---

## The Solution

We need to run a SQL script on the production database to remove the old constraint and ensure the compound (per-warehouse) constraint exists.

---

## 🎯 Option 1: Direct SQL Fix (Fastest - 30 seconds)

### Using Render Dashboard (Recommended)

1. **Go to your Render database dashboard**
   - Navigate to https://dashboard.render.com
   - Select your PostgreSQL database
   - Click "Connect" → "External Connection" to get connection details

2. **Connect via psql or pgAdmin**
   ```bash
   psql <your-production-database-url>
   ```

3. **Run the fix script**
   ```bash
   \i PRODUCTION_FIX_MULTI_TENANCY.sql
   ```

   Or copy-paste the SQL directly:
   ```sql
   BEGIN;

   -- Drop old single-column unique constraint
   ALTER TABLE location DROP CONSTRAINT IF EXISTS location_code_key;

   -- Drop any unique index on code column alone
   DROP INDEX IF EXISTS ix_location_code;

   -- Ensure compound unique constraint exists
   DO $$
   BEGIN
       IF NOT EXISTS (
           SELECT 1 FROM pg_constraint
           WHERE conname = 'uq_location_warehouse_code'
       ) THEN
           ALTER TABLE location
           ADD CONSTRAINT uq_location_warehouse_code
           UNIQUE (warehouse_id, code);
       END IF;
   END $$;

   COMMIT;
   ```

4. **Verify the fix**
   ```sql
   SELECT conname, conkey
   FROM pg_constraint
   WHERE conrelid = 'location'::regclass
     AND contype = 'u';
   ```

   **Expected output:**
   - Should show `uq_location_warehouse_code` with keys [warehouse_id, code]
   - Should NOT show `location_code_key`

---

## 🎯 Option 2: Deploy Python Script (Alternative)

If you prefer using the Python script:

1. **Push code to production**
   ```bash
   git push origin main
   ```

2. **SSH into your Render instance or run via console**
   ```bash
   python apply_multi_tenancy_fix.py
   ```

---

## ✅ Verification Steps

After applying the fix, test that multi-tenancy works:

1. **Login as User A**
   - Create location "W-01" in their warehouse
   - Should succeed ✅

2. **Login as User B**
   - Create location "W-01" in their warehouse
   - Should succeed ✅ (this would have failed before)

3. **Verify isolation**
   - User A should only see their "W-01"
   - User B should only see their "W-01"
   - Both locations coexist happily in different warehouses

---

## 🔍 What This Fix Does

### Before (Broken):
```
Database Constraints:
1. location_code_key: code UNIQUE globally ❌
2. uq_location_warehouse_code: (warehouse_id, code) UNIQUE per warehouse ✅

Result: BOTH enforced → User B can't create "W-01" if User A has it
```

### After (Fixed):
```
Database Constraints:
1. uq_location_warehouse_code: (warehouse_id, code) UNIQUE per warehouse ✅

Result: ONLY compound constraint → Users can have same code in different warehouses
```

---

## 🛡️ Safety

This fix is **completely safe** because:

✅ Uses `DROP CONSTRAINT IF EXISTS` - won't fail if already applied
✅ Wrapped in transaction (BEGIN/COMMIT) - atomic operation
✅ Doesn't modify any data - only changes constraints
✅ Backward compatible - code already expects compound constraint
✅ Already tested successfully in development database

---

## ⏱️ Downtime

**Zero downtime** - this is a metadata-only operation that takes milliseconds. No need to stop the application.

---

## 🆘 Rollback (Unlikely to Need)

If you need to rollback (you won't), you can restore the old constraint:

```sql
BEGIN;

-- Restore old global constraint (NOT RECOMMENDED)
ALTER TABLE location ADD CONSTRAINT location_code_key UNIQUE (code);

COMMIT;
```

**But don't do this** - it will break multi-tenancy again.

---

## 📊 Expected Timeline

- **SQL execution**: < 1 second
- **Verification**: < 30 seconds
- **Total downtime**: 0 seconds

---

## 🎉 After This Fix

Users will be able to:
- ✅ Create locations with any code they want
- ✅ Not worry about conflicts with other users
- ✅ Have full warehouse isolation
- ✅ Use bulk location creation without errors

---

## 📞 Support

If you encounter any issues:

1. Check that you're connected to the production database
2. Verify you have ALTER TABLE permissions
3. Look for any errors in the output
4. If stuck, the Python script has more detailed logging

---

**Recommended Action**: Use Option 1 (Direct SQL) - it's fastest and most reliable.

**Time Required**: 30 seconds

**Risk Level**: Very Low (metadata-only change)

**Urgency**: High (blocking user operations)
