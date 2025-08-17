# Add this code to your app.py file:

@app.route('/api/v1/test/warehouse-check', methods=['GET'])
def test_warehouse_check():
    """Simple warehouse check endpoint - diagnose production PostgreSQL issue"""
    try:
        from models import Location
        from database import db
        
        # Get all warehouses and their counts
        warehouses = db.session.query(Location.warehouse_id).distinct().all()
        warehouse_counts = {}
        
        for (warehouse_id,) in warehouses:
            count = db.session.query(Location).filter_by(warehouse_id=warehouse_id).count()
            warehouse_counts[warehouse_id] = count
        
        # Check specifically for DEFAULT warehouse
        default_count = db.session.query(Location).filter_by(warehouse_id='DEFAULT').count()
        
        # Test a few known locations
        test_locations = ["02-1-011B", "01-1-007B", "RECV-01"]
        location_test = {}
        
        for loc in test_locations:
            matches = db.session.query(Location.warehouse_id).filter_by(code=loc).all()
            location_test[loc] = [m.warehouse_id for m in matches]
        
        return jsonify({
            'database_type': db.engine.dialect.name,
            'warehouses': warehouse_counts,
            'has_default_warehouse': default_count > 0,
            'default_count': default_count,
            'issue_detected': default_count > 0,
            'location_test': location_test,
            'diagnosis': 'DEFAULT warehouse found - this is the issue!' if default_count > 0 else 'Clean database - no DEFAULT warehouse',
            'fix_needed': default_count > 0
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'database_type': 'unknown'
        }), 500