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
        
        # Find and fix Rule ID 1
        rule1 = Rule.query.filter_by(id=1).first()
        if not rule1:
            return jsonify({
                'error': 'Rule not found',
                'message': 'Rule ID 1 (Forgotten Pallets Alert) not found in database',
                **response_data
            }), 404
        
        # Get current conditions
        current_conditions = json.loads(rule1.conditions) if isinstance(rule1.conditions, str) else rule1.conditions
        
        # Check if fix is needed
        current_threshold = current_conditions.get('time_threshold_hours', 0)
        
        if current_threshold == 10:
            return jsonify({
                'success': True,
                'message': 'Rule already has correct configuration',
                'rule_id': rule1.id,
                'rule_name': rule1.name,
                'current_threshold': current_threshold,
                'no_changes_needed': True,
                **response_data
            })
        
        # Apply the fix
        new_conditions = {
            "time_threshold_hours": 10,
            "location_types": ["RECEIVING"]
        }
        
        # Store old conditions for reporting
        old_conditions = current_conditions.copy()
        
        # Update the rule
        rule1.conditions = json.dumps(new_conditions)
        db.session.commit()
        
        # Verify the update
        updated_rule = Rule.query.filter_by(id=1).first()
        updated_conditions = json.loads(updated_rule.conditions) if isinstance(updated_rule.conditions, str) else updated_rule.conditions
        
        return jsonify({
            'success': True,
            'message': 'Production database rules fixed successfully!',
            'rule_id': rule1.id,
            'rule_name': rule1.name,
            'changes': {
                'old_conditions': old_conditions,
                'new_conditions': updated_conditions,
                'threshold_changed': f"{current_threshold}h → 10h"
            },
            'next_steps': [
                'Test with a new inventory analysis',
                'Verify debug output shows 10-hour threshold',
                'Confirm pallets are only flagged after 10 hours in RECEIVING'
            ],
            **response_data
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Database fix failed',
            'message': str(e),
            'success': False
        }), 500