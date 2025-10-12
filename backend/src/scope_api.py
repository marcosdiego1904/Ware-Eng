"""
Scope Management API for Unit-Agnostic Warehouse Intelligence
Handles warehouse scope configuration, excluded patterns, and unit type management
"""

import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import and_, or_
from functools import wraps
from database import db
from models import WarehouseScopeConfig, Location
from core_models import User
from services.simple_scope_service import SimpleScopeService, validate_scope_configuration

# Create the scope management API blueprint
scope_bp = Blueprint('scope_api', __name__, url_prefix='/api/v1/scope')

# Import auth decorator (following same pattern as other APIs)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            import jwt
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user_obj = User.query.get(current_user_id)
            if not current_user_obj:
                return jsonify({'error': 'User not found'}), 401
        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(current_user_obj, *args, **kwargs)
    return decorated

@scope_bp.route('/config/<warehouse_id>', methods=['GET'])
@token_required
def get_scope_config(current_user, warehouse_id):
    """
    Get warehouse scope configuration

    Returns:
        JSON with scope configuration including excluded patterns and default unit type
    """
    try:
        # Initialize scope service
        scope_service = SimpleScopeService(warehouse_id)
        scope_summary = scope_service.get_scope_summary()

        return jsonify({
            'success': True,
            'warehouse_id': warehouse_id,
            'scope_config': scope_summary
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get scope configuration: {str(e)}'
        }), 500

@scope_bp.route('/config/<warehouse_id>', methods=['PUT'])
@token_required
def update_scope_config(current_user, warehouse_id):
    """
    Update warehouse scope configuration

    Expected JSON payload:
    {
        "excluded_patterns": ["BOX-*", "ITEM-*"],
        "default_unit_type": "pallets"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        excluded_patterns = data.get('excluded_patterns', [])
        default_unit_type = data.get('default_unit_type', 'pallets')

        # Validate the scope configuration
        validation_result = validate_scope_configuration(excluded_patterns)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': 'Invalid scope configuration',
                'validation_issues': validation_result['issues']
            }), 400

        # Validate unit type
        valid_unit_types = ['pallets', 'boxes', 'items', 'cases', 'mixed']
        if default_unit_type not in valid_unit_types:
            return jsonify({
                'success': False,
                'error': f'Invalid unit type. Must be one of: {valid_unit_types}'
            }), 400

        # Find or create scope configuration
        scope_config = WarehouseScopeConfig.query.filter_by(warehouse_id=warehouse_id).first()

        if scope_config:
            # Update existing configuration
            scope_config.excluded_patterns = excluded_patterns
            scope_config.default_unit_type = default_unit_type
            scope_config.updated_at = datetime.utcnow()
        else:
            # Create new configuration
            scope_config = WarehouseScopeConfig(
                warehouse_id=warehouse_id,
                excluded_patterns=excluded_patterns,
                default_unit_type=default_unit_type
            )
            db.session.add(scope_config)

        db.session.commit()

        # Clear cache to reflect changes
        scope_service = SimpleScopeService(warehouse_id)
        scope_service.clear_cache()

        return jsonify({
            'success': True,
            'message': 'Scope configuration updated successfully',
            'warehouse_id': warehouse_id,
            'excluded_patterns': excluded_patterns,
            'default_unit_type': default_unit_type
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to update scope configuration: {str(e)}'
        }), 500

@scope_bp.route('/validate-patterns', methods=['POST'])
@token_required
def validate_patterns(current_user):
    """
    Validate exclusion patterns without saving

    Expected JSON payload:
    {
        "patterns": ["BOX-*", "ITEM-*"]
    }
    """
    try:
        data = request.get_json()
        if not data or 'patterns' not in data:
            return jsonify({'success': False, 'error': 'No patterns provided'}), 400

        patterns = data['patterns']
        validation_result = validate_scope_configuration(patterns)

        return jsonify({
            'success': True,
            'validation_result': validation_result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to validate patterns: {str(e)}'
        }), 500

@scope_bp.route('/preview/<warehouse_id>', methods=['POST'])
@token_required
def preview_scope_filtering(current_user, warehouse_id):
    """
    Preview how scope filtering would affect a sample of locations

    Expected JSON payload:
    {
        "sample_locations": ["A-01", "BOX-001", "RECV-01", "ITEM-123"],
        "excluded_patterns": ["BOX-*", "ITEM-*"]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        sample_locations = data.get('sample_locations', [])
        excluded_patterns = data.get('excluded_patterns', [])

        if not sample_locations:
            return jsonify({'success': False, 'error': 'No sample locations provided'}), 400

        # Validate patterns
        validation_result = validate_scope_configuration(excluded_patterns)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': 'Invalid patterns',
                'validation_issues': validation_result['issues']
            }), 400

        # Create temporary scope service to test filtering
        scope_service = SimpleScopeService(warehouse_id)

        # Test each location against the patterns
        preview_results = []
        for location in sample_locations:
            is_excluded = any(
                scope_service._is_location_excluded(location, [pattern])
                for pattern in excluded_patterns
            )

            preview_results.append({
                'location': location,
                'excluded': is_excluded,
                'status': 'excluded' if is_excluded else 'included'
            })

        # Summary statistics
        excluded_count = sum(1 for result in preview_results if result['excluded'])
        included_count = len(preview_results) - excluded_count

        return jsonify({
            'success': True,
            'warehouse_id': warehouse_id,
            'excluded_patterns': excluded_patterns,
            'preview_results': preview_results,
            'summary': {
                'total_locations': len(sample_locations),
                'included_locations': included_count,
                'excluded_locations': excluded_count
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to preview scope filtering: {str(e)}'
        }), 500

@scope_bp.route('/location/<warehouse_id>/<location_code>', methods=['GET'])
@token_required
def get_location_info(current_user, warehouse_id, location_code):
    """
    Get detailed information about a specific location's scope status and unit type

    Returns location capacity, unit type, and scope inclusion status
    """
    try:
        # Initialize scope service
        scope_service = SimpleScopeService(warehouse_id)

        # Get location information
        is_in_scope = scope_service.is_location_in_scope(location_code)
        unit_type = scope_service.get_location_unit_type(location_code)
        capacity = scope_service.get_location_capacity(location_code)

        return jsonify({
            'success': True,
            'warehouse_id': warehouse_id,
            'location_code': location_code,
            'in_scope': is_in_scope,
            'unit_type': unit_type,
            'capacity': capacity,
            'scope_status': 'included' if is_in_scope else 'excluded'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get location information: {str(e)}'
        }), 500