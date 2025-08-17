#!/usr/bin/env python3
"""
Diagnostic API - Add this to your Flask app to diagnose production database
"""

from flask import Blueprint, jsonify, request
from models import Location, WarehouseConfig
from database import db
import pandas as pd

# Create blueprint for diagnostic endpoints
diagnostic_bp = Blueprint('diagnostic', __name__, url_prefix='/api/v1/diagnostic')

@diagnostic_bp.route('/warehouse-detection-issue', methods=['GET'])
def diagnose_warehouse_detection_issue():
    """
    Diagnostic endpoint to check warehouse detection issues
    Call this from production: GET /api/v1/diagnostic/warehouse-detection-issue
    """
    try:
        diagnostic_data = {}
        
        # Step 1: Check database type and warehouses
        diagnostic_data['database_type'] = db.engine.dialect.name
        diagnostic_data['database_url'] = str(db.engine.url)[:50] + "..."
        
        # Step 2: Warehouse inventory
        warehouses = db.session.query(Location.warehouse_id).distinct().all()
        warehouse_info = {}
        
        for (warehouse_id,) in warehouses:
            locations = db.session.query(Location).filter_by(warehouse_id=warehouse_id).all()
            sample_codes = [loc.code for loc in locations[:5]]
            
            # Count by type
            type_counts = {}
            for loc in locations:
                loc_type = loc.location_type or 'UNKNOWN'
                type_counts[loc_type] = type_counts.get(loc_type, 0) + 1
            
            warehouse_info[warehouse_id] = {
                'total_locations': len(locations),
                'location_types': type_counts,
                'sample_codes': sample_codes
            }
        
        diagnostic_data['warehouses'] = warehouse_info
        
        # Step 3: Check for the specific issue
        default_count = db.session.query(Location).filter_by(warehouse_id='DEFAULT').count()
        diagnostic_data['default_warehouse_issue'] = {
            'has_default_warehouse': default_count > 0,
            'default_location_count': default_count
        }
        
        # Step 4: Test specific locations
        test_locations = ["02-1-011B", "01-1-007B", "RECV-01", "STAGE-01", "DOCK-01"]
        location_test = {}
        
        for loc in test_locations:
            matches = db.session.query(Location.warehouse_id).filter_by(code=loc).all()
            warehouses_with_loc = [m.warehouse_id for m in matches]
            location_test[loc] = warehouses_with_loc
        
        diagnostic_data['location_existence_test'] = location_test
        
        # Step 5: Test warehouse detection
        try:
            from rule_engine import RuleEngine
            
            rule_engine = RuleEngine(db.session)
            test_df = pd.DataFrame({'location': test_locations})
            
            detection_result = rule_engine._detect_warehouse_context(test_df)
            
            diagnostic_data['warehouse_detection_test'] = {
                'detected_warehouse': detection_result.get('warehouse_id'),
                'confidence_level': detection_result.get('confidence_level'),
                'match_score': detection_result.get('match_score', 0),
                'detailed_scores': detection_result.get('detailed_scores', [])
            }
            
        except Exception as e:
            diagnostic_data['warehouse_detection_test'] = {
                'error': str(e)
            }
        
        # Step 6: Analysis and recommendations
        issues_found = []
        
        if default_count > 0:
            issues_found.append(f"DEFAULT warehouse exists with {default_count} locations")
        
        detected_warehouse = diagnostic_data.get('warehouse_detection_test', {}).get('detected_warehouse')
        if detected_warehouse != 'USER_TESTF':
            issues_found.append(f"Wrong warehouse detected: {detected_warehouse} instead of USER_TESTF")
        
        diagnostic_data['analysis'] = {
            'issues_found': issues_found,
            'root_cause': "DEFAULT warehouse interference" if default_count > 0 else "Unknown",
            'fix_needed': len(issues_found) > 0
        }
        
        return jsonify({
            'success': True,
            'diagnostic_data': diagnostic_data,
            'summary': {
                'database_type': diagnostic_data['database_type'],
                'warehouses_found': list(warehouse_info.keys()),
                'issues_count': len(issues_found),
                'fix_needed': len(issues_found) > 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@diagnostic_bp.route('/fix-default-warehouse', methods=['POST'])
def fix_default_warehouse():
    """
    Fix the DEFAULT warehouse issue
    Call this from production: POST /api/v1/diagnostic/fix-default-warehouse
    """
    try:
        # Check if user confirmed the fix
        confirm = request.json.get('confirm', False) if request.json else False
        
        if not confirm:
            return jsonify({
                'success': False,
                'error': 'Confirmation required. Send {"confirm": true} to proceed with fix.'
            }), 400
        
        fixes_applied = []
        
        # Remove DEFAULT warehouse locations
        default_locations = db.session.query(Location).filter_by(warehouse_id='DEFAULT').all()
        
        if default_locations:
            sample_codes = [loc.code for loc in default_locations[:5]]
            
            deleted_count = db.session.query(Location).filter_by(warehouse_id='DEFAULT').delete()
            
            fixes_applied.append(f"Deleted {deleted_count} DEFAULT warehouse locations")
            fixes_applied.append(f"Sample deleted codes: {sample_codes}")
        
        # Remove DEFAULT warehouse config
        default_config = db.session.query(WarehouseConfig).filter_by(warehouse_id='DEFAULT').first()
        if default_config:
            db.session.delete(default_config)
            fixes_applied.append("Deleted DEFAULT warehouse configuration")
        
        db.session.commit()
        
        # Test detection after fix
        test_locations = ["02-1-011B", "01-1-007B", "RECV-01", "STAGE-01"]
        
        try:
            from rule_engine import RuleEngine
            
            rule_engine = RuleEngine(db.session)
            test_df = pd.DataFrame({'location': test_locations})
            detection_result = rule_engine._detect_warehouse_context(test_df)
            
            after_fix_test = {
                'detected_warehouse': detection_result.get('warehouse_id'),
                'confidence_level': detection_result.get('confidence_level'),
                'match_score': detection_result.get('match_score', 0)
            }
            
        except Exception as e:
            after_fix_test = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'fixes_applied': fixes_applied,
            'after_fix_test': after_fix_test,
            'message': 'DEFAULT warehouse cleanup completed'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500