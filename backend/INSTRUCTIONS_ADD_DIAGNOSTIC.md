# Step-by-Step Instructions: Add Diagnostic Endpoint

## Step 1: Add the Diagnostic Blueprint

Add this code to your `app.py` file after the existing blueprint registrations (around line 1395):

```python
# Register Diagnostic API (for production database debugging)
try:
    from diagnostic_api import diagnostic_bp
    app.register_blueprint(diagnostic_bp)
    print("Diagnostic API registered successfully")
except ImportError as e:
    print(f"Diagnostic API not available: {e}")
```

## Step 2: Deploy to Production

After adding the code above:
1. Save the `app.py` file
2. Deploy your updated backend to production (however you normally deploy)
3. The diagnostic endpoints will be available at `/api/v1/diagnostic/`

## Step 3: Test the Diagnostic Endpoint

Once deployed, visit this URL in your browser or use curl:

**Endpoint:** `https://your-production-domain.com/api/v1/diagnostic/warehouse-detection-issue`

**Example URLs:**
- If using Vercel: `https://ware-eng.vercel.app/api/v1/diagnostic/warehouse-detection-issue`
- If using Heroku: `https://your-app.herokuapp.com/api/v1/diagnostic/warehouse-detection-issue`

## Step 4: Interpret Results

The diagnostic will return JSON like this:

### ✅ **Good Result (No Issues):**
```json
{
  "success": true,
  "summary": {
    "database_type": "postgresql",
    "warehouses_found": ["USER_TESTF"],
    "issues_count": 0,
    "fix_needed": false
  }
}
```

### ❌ **Problem Result (DEFAULT Warehouse Found):**
```json
{
  "success": true,
  "summary": {
    "database_type": "postgresql", 
    "warehouses_found": ["USER_TESTF", "DEFAULT"],
    "issues_count": 2,
    "fix_needed": true
  },
  "diagnostic_data": {
    "analysis": {
      "issues_found": [
        "DEFAULT warehouse exists with 133 locations",
        "Wrong warehouse detected: DEFAULT instead of USER_TESTF"
      ]
    }
  }
}
```

## Step 5: Apply Fix (If Needed)

If issues are found, you can fix them by making a POST request:

**Endpoint:** `https://your-production-domain.com/api/v1/diagnostic/fix-default-warehouse`

**Method:** POST
**Headers:** `Content-Type: application/json`
**Body:** `{"confirm": true}`

**Using curl:**
```bash
curl -X POST https://your-production-domain.com/api/v1/diagnostic/fix-default-warehouse \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

## Alternative: Simple Test Endpoint

If you prefer a simpler approach, you can add this single endpoint to your `app.py` instead:

```python
@app.route('/api/v1/test/warehouse-check', methods=['GET'])
def test_warehouse_check():
    """Simple warehouse check endpoint"""
    try:
        from models import Location
        from database import db
        
        # Get warehouse counts
        warehouses = db.session.query(Location.warehouse_id).distinct().all()
        warehouse_counts = {}
        
        for (warehouse_id,) in warehouses:
            count = db.session.query(Location).filter_by(warehouse_id=warehouse_id).count()
            warehouse_counts[warehouse_id] = count
        
        # Check for DEFAULT specifically
        default_count = db.session.query(Location).filter_by(warehouse_id='DEFAULT').count()
        
        return jsonify({
            'database_type': db.engine.dialect.name,
            'warehouses': warehouse_counts,
            'has_default_warehouse': default_count > 0,
            'default_count': default_count,
            'issue_detected': default_count > 0,
            'fix_needed': default_count > 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

Then visit: `https://your-domain.com/api/v1/test/warehouse-check`

## Expected Results

After running the diagnostic, you should see one of these scenarios:

### Scenario A: Clean Database ✅
- Only USER_TESTF warehouse exists
- No DEFAULT warehouse found
- Warehouse detection works correctly

### Scenario B: Contaminated Database ❌
- Both USER_TESTF and DEFAULT warehouses exist
- DEFAULT has many locations (causing the 133/156 match issue)
- Fix needed: Remove DEFAULT warehouse

Let me know what the diagnostic shows, and I'll guide you through the next steps!