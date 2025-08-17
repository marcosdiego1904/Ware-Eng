#!/usr/bin/env python3
"""
Instructions to add diagnostic endpoint to your Flask app
"""

print("""
=== STEP 1: ADD DIAGNOSTIC ENDPOINT TO YOUR FLASK APP ===

Add these lines to your app.py file:

1. Import the diagnostic blueprint (add this near the other imports):
   
   from diagnostic_api import diagnostic_bp

2. Register the blueprint (add this after the other register_blueprint calls around line 1394):
   
   app.register_blueprint(diagnostic_bp)
   print("Diagnostic API registered successfully")

That's it! After adding these two lines and restarting your Flask app, you'll have the diagnostic endpoints available.

=== STEP 2: TEST THE DIAGNOSTIC ENDPOINT ===

Once you've deployed the updated app to production, you can test it by visiting:

https://your-production-domain.com/api/v1/diagnostic/warehouse-detection-issue

Or using curl:

curl https://your-production-domain.com/api/v1/diagnostic/warehouse-detection-issue

=== STEP 3: INTERPRET THE RESULTS ===

The endpoint will return JSON with:
- database_type: Should show "postgresql" in production
- warehouses: List of all warehouses found
- default_warehouse_issue: Shows if DEFAULT warehouse exists
- warehouse_detection_test: Shows what warehouse is detected
- analysis: Summary of issues found

=== STEP 4: APPLY THE FIX (if needed) ===

If issues are found, you can apply the fix by calling:

POST https://your-production-domain.com/api/v1/diagnostic/fix-default-warehouse
Content-Type: application/json
{"confirm": true}

=== ALTERNATIVE: SIMPLE TEST ENDPOINT ===

If you prefer, I can create a simple test endpoint that just checks the basic warehouse info without the full diagnostic.
""")

# Also create a simple version for testing
def create_simple_test_endpoint():
    return '''
# Add this simple endpoint to your app.py for quick testing:

@app.route('/api/v1/test/warehouse-info', methods=['GET'])
def test_warehouse_info():
    """Simple endpoint to check warehouse information"""
    try:
        from models import Location
        from database import db
        
        # Get warehouse counts
        warehouses = db.session.query(Location.warehouse_id).distinct().all()
        warehouse_info = {}
        
        for (warehouse_id,) in warehouses:
            count = db.session.query(Location).filter_by(warehouse_id=warehouse_id).count()
            warehouse_info[warehouse_id] = count
        
        # Check for DEFAULT specifically
        default_count = db.session.query(Location).filter_by(warehouse_id='DEFAULT').count()
        
        return jsonify({
            'database_type': db.engine.dialect.name,
            'warehouses': warehouse_info,
            'default_warehouse_exists': default_count > 0,
            'default_warehouse_count': default_count,
            'likely_issue': default_count > 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''

if __name__ == '__main__':
    print(create_simple_test_endpoint())