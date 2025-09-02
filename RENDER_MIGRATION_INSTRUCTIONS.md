# Smart Configuration Migration - Render PostgreSQL

## 🎯 Quick Migration via API Endpoint

I've added a special admin endpoint to your application that will run the PostgreSQL migration for you.

### Step 1: Deploy Your Updated Code

Make sure your latest code (with the hotfix and admin endpoint) is deployed to Render.

### Step 2: Check Migration Status

First, check if the migration is needed:

```bash
curl https://your-app.onrender.com/api/admin/migration-status
```

### Step 3: Run the Migration

Run the migration using the admin endpoint:

```bash
curl -X POST https://your-app.onrender.com/api/admin/migrate-smart-config \
  -H "X-Admin-Key: smart-config-migration-2024"
```

**Replace `your-app.onrender.com` with your actual Render app URL.**

### Step 4: Verify Success

You should get a response like:

```json
{
  "success": true,
  "message": "Smart Configuration migration completed successfully",
  "database_type": "postgresql",
  "columns_added": 4,
  "steps": [
    "Database type detected: POSTGRESQL",
    "Found 0/4 Smart Configuration columns",
    "Step 1: Added column location_format_config",
    "Step 2: Added column format_confidence", 
    "Step 3: Added column format_examples",
    "Step 4: Added column format_learned_date",
    "Updated X existing templates with default values",
    "Created location_format_history table",
    "✓ Smart Configuration migration completed successfully!"
  ]
}
```

## 🔧 Alternative Methods (if API doesn't work)

### Method A: Render Dashboard SQL Console

1. Go to your Render Dashboard
2. Click your PostgreSQL database service
3. Look for "Connect" or "Console" tab
4. Run this SQL:

```sql
-- Add Smart Configuration columns
ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS location_format_config TEXT;
ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS format_confidence FLOAT;
ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS format_examples TEXT;
ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS format_learned_date TIMESTAMP;

-- Update existing templates
UPDATE warehouse_template 
SET format_confidence = 0.0, format_learned_date = created_at
WHERE format_confidence IS NULL;

-- Verify
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'warehouse_template' 
AND column_name LIKE '%format%';
```

### Method B: External Database Connection

1. **Get connection details** from Render dashboard:
   - Go to PostgreSQL service
   - Copy "External Database URL"

2. **Use pgAdmin or DBeaver:**
   - Install pgAdmin (free PostgreSQL GUI)
   - Connect using the External Database URL
   - Run the SQL from Method A

3. **Use psql command line:**
   ```bash
   psql "your-external-database-url-from-render"
   ```
   Then run the SQL commands.

## ✅ After Migration Success

1. **Remove the hotfix** from your code:
   - Edit `backend/src/models.py`
   - Remove `, nullable=True` from the 4 Smart Configuration columns
   - Remove the `# SMART_CONFIG_HOTFIX_APPLIED` comment

2. **Test your application:**
   - Templates tab should load without errors
   - Template creation should show Smart Configuration step
   - Inventory uploads should work with format normalization

3. **Disable the admin endpoint** (security):
   - Comment out or remove the admin endpoint registration in `app.py`
   - Or change the `ADMIN_MIGRATION_KEY` environment variable

## 🚨 Troubleshooting

**If the API endpoint returns 401 Unauthorized:**
- Make sure you're using the correct admin key: `smart-config-migration-2024`
- Or check if `ADMIN_MIGRATION_KEY` environment variable is set differently

**If migration fails:**
- Check your application logs on Render
- Try the direct SQL method instead
- The migration is designed to be safe to run multiple times

**If you get connection errors:**
- Ensure your app is deployed and running on Render
- Check that the database service is active
- Verify the External Database URL in Render dashboard

## 🎉 Success Indicators

✅ **API returns success: true**  
✅ **Templates tab loads without errors**  
✅ **4 new columns visible in database schema**  
✅ **Smart Configuration features working**

The easiest method is the **API endpoint approach** - try that first! 🚀