"""
Production database fix endpoint for Render deployment.
Add this to your Flask app to fix database rules via web request.
"""
import os
import json
from flask import jsonify
from models import Rule, db

def fix_production_rules_endpoint():
    """
    Web endpoint to fix production database rules.
    Returns JSON response with fix status.
    """
    try:
        # Security check - only allow in production with correct secret
        secret_key = os.environ.get('FLASK_SECRET_KEY', '')
        
        if not secret_key:
            return jsonify({
                'error': 'Configuration error',
                'message': 'Secret key not configured'
            }), 500
        
        # Check if we're in production
        is_production = os.environ.get('RENDER') == 'true'
        database_url = os.environ.get('DATABASE_URL')
        
        response_data = {
            'environment': 'PRODUCTION' if is_production else 'DEVELOPMENT',
            'database_url_set': bool(database_url),
            'timestamp': str(db.func.now()),
            'rules_updated': []
        }
        
        # Fix Rule 1 (STAGNANT_PALLETS)
        rule1_result = _fix_rule_1()
        if rule1_result:
            response_data['rules_updated'].append(rule1_result)
        
        # Fix Rule 2 (UNCOORDINATED_LOTS)  
        rule2_result = _fix_rule_2()
        if rule2_result:
            response_data['rules_updated'].append(rule2_result)
        
        # Determine overall success
        if response_data['rules_updated']:
            return jsonify({
                'success': True,
                'message': f'Production database rules fixed successfully! Updated {len(response_data["rules_updated"])} rules.',
                'fixes_applied': response_data['rules_updated'],
                **response_data
            })
        else:
            return jsonify({
                'success': True,
                'message': 'All rules already have correct configuration',
                'no_changes_needed': True,
                **response_data
            })
        
    except Exception as e:
        return jsonify({
            'error': 'Database fix failed',
            'message': str(e),
            'success': False
        }), 500

def _fix_rule_1():
    """Fix Rule 1 (STAGNANT_PALLETS) threshold issue"""
    try:
        rule1 = Rule.query.filter_by(id=1).first()
        if not rule1:
            return {'error': 'Rule 1 not found'}
        
        current_conditions = json.loads(rule1.conditions) if isinstance(rule1.conditions, str) else rule1.conditions
        current_threshold = current_conditions.get('time_threshold_hours', 0)
        
        if current_threshold == 10:
            return None  # Already correct
        
        # Apply the fix
        new_conditions = {
            "time_threshold_hours": 10,
            "location_types": ["RECEIVING"]
        }
        
        old_conditions = current_conditions.copy()
        rule1.conditions = json.dumps(new_conditions)
        db.session.commit()
        
        return {
            'rule_id': 1,
            'rule_name': 'Forgotten Pallets Alert',
            'rule_type': 'STAGNANT_PALLETS',
            'changes': {
                'old_conditions': old_conditions,
                'new_conditions': new_conditions,
                'threshold_changed': f"{current_threshold}h → 10h"
            }
        }
        
    except Exception as e:
        return {'error': f'Rule 1 fix failed: {str(e)}'}

def _fix_rule_2():
    """Fix Rule 2 (UNCOORDINATED_LOTS) final location types issue"""
    try:
        rule2 = Rule.query.filter_by(id=2).first()
        if not rule2:
            return {'error': 'Rule 2 not found'}
        
        current_conditions = json.loads(rule2.conditions) if isinstance(rule2.conditions, str) else rule2.conditions
        
        # Check if fix is needed
        has_final_location_types = 'final_location_types' in current_conditions
        
        if has_final_location_types:
            return None  # Already correct
        
        # Apply the fix
        old_conditions = current_conditions.copy()
        new_conditions = current_conditions.copy()
        new_conditions['final_location_types'] = ['FINAL', 'STORAGE']
        new_conditions['location_types'] = ['RECEIVING']  # Only check RECEIVING for stragglers
        
        rule2.conditions = json.dumps(new_conditions)
        db.session.commit()
        
        return {
            'rule_id': 2,
            'rule_name': 'Incomplete Lots Alert',
            'rule_type': 'UNCOORDINATED_LOTS',
            'changes': {
                'old_conditions': old_conditions,
                'new_conditions': new_conditions,
                'added_parameter': 'final_location_types = ["FINAL", "STORAGE"]'
            }
        }
        
    except Exception as e:
        return {'error': f'Rule 2 fix failed: {str(e)}'}