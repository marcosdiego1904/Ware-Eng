#!/usr/bin/env python3
"""
Add endpoint to fix the DEFAULT warehouse issue in production
"""

# Add this endpoint to your app.py file:

FIX_ENDPOINT_CODE = '''
@app.route('/api/v1/fix/remove-default-warehouse', methods=['POST'])
def fix_remove_default_warehouse():
    """Remove DEFAULT warehouse to fix warehouse detection"""
    try:
        from models import Location, WarehouseConfig
        from database import db
        
        # Get confirmation from request
        data = request.get_json() if request.is_json else {}
        confirm = data.get('confirm', False)
        
        if not confirm:
            return jsonify({
                'error': 'Confirmation required',
                'message': 'Send {"confirm": true} to proceed with DEFAULT warehouse removal',
                'warning': 'This will delete 1734 DEFAULT warehouse locations'
            }), 400
        
        fixes_applied = []
        
        # Step 1: Count and sample DEFAULT locations before deletion
        default_locations = db.session.query(Location).filter_by(warehouse_id='DEFAULT').all()
        total_count = len(default_locations)
        sample_codes = [loc.code for loc in default_locations[:5]]
        
        fixes_applied.append(f"Found {total_count} DEFAULT locations to remove")
        fixes_applied.append(f"Sample codes: {sample_codes}")
        
        # Step 2: Remove DEFAULT warehouse locations
        if default_locations:
            deleted_count = db.session.query(Location).filter_by(warehouse_id='DEFAULT').delete()
            fixes_applied.append(f"Deleted {deleted_count} DEFAULT warehouse locations")
        
        # Step 3: Remove DEFAULT warehouse configuration (if exists)
        default_config = db.session.query(WarehouseConfig).filter_by(warehouse_id='DEFAULT').first()
        if default_config:
            db.session.delete(default_config)
            fixes_applied.append("Deleted DEFAULT warehouse configuration")
        
        # Step 4: Commit changes
        db.session.commit()
        fixes_applied.append("All changes committed to database")
        
        # Step 5: Verify the fix
        remaining_default = db.session.query(Location).filter_by(warehouse_id='DEFAULT').count()
        
        # Step 6: Test warehouse detection after fix
        test_locations = ["02-1-011B", "01-1-007B", "RECV-01", "STAGE-01"]
        
        try:
            from rule_engine import RuleEngine
            import pandas as pd
            
            rule_engine = RuleEngine(db.session)
            test_df = pd.DataFrame({'location': test_locations})
            detection_result = rule_engine._detect_warehouse_context(test_df)
            
            after_fix_test = {
                'detected_warehouse': detection_result.get('warehouse_id'),
                'confidence_level': detection_result.get('confidence_level'),
                'match_score': detection_result.get('match_score', 0),
                'detailed_scores': detection_result.get('detailed_scores', [])
            }
            
        except Exception as e:
            after_fix_test = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'fixes_applied': fixes_applied,
            'verification': {
                'remaining_default_locations': remaining_default,
                'fix_successful': remaining_default == 0
            },
            'warehouse_detection_test': after_fix_test,
            'message': 'DEFAULT warehouse cleanup completed successfully' if remaining_default == 0 else 'Cleanup partially completed'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to remove DEFAULT warehouse'
        }), 500
'''

print("Add this endpoint to your app.py file:")
print(FIX_ENDPOINT_CODE)