"""
User Reset API - Allows users to clean up their own data
"""
from flask import Blueprint, jsonify, request, current_app
from functools import wraps
from database import db
from models import WarehouseTemplate, WarehouseConfig, Location
from core_models import User
import jwt

user_reset_bp = Blueprint('user_reset', __name__, url_prefix='/api/v1/user')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user_obj = User.query.get(current_user_id)
            if not current_user_obj:
                return jsonify({'error': 'User not found'}), 401
        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(current_user_obj, *args, **kwargs)
    return decorated

@user_reset_bp.route('/reset-templates', methods=['POST'])
@token_required
def reset_user_templates(current_user):
    """
    Reset all templates for the current user
    This deactivates all user templates (soft delete)
    """
    try:
        # Count current active templates
        active_count = WarehouseTemplate.query.filter_by(
            created_by=current_user.id,
            is_active=True
        ).count()

        # Soft delete all user templates
        templates = WarehouseTemplate.query.filter_by(
            created_by=current_user.id,
            is_active=True
        ).all()

        deactivated_count = 0
        for template in templates:
            template.is_active = False
            deactivated_count += 1

        db.session.commit()

        print(f"[USER_RESET] User {current_user.username} (ID={current_user.id}) reset {deactivated_count} templates")

        return jsonify({
            'success': True,
            'message': f'Successfully reset {deactivated_count} templates',
            'templates_deactivated': deactivated_count,
            'previous_count': active_count
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to reset templates: {str(e)}'
        }), 500

@user_reset_bp.route('/cleanup-default-warehouse', methods=['POST'])
@token_required
def cleanup_default_warehouse(current_user):
    """
    Clean up warehouses associated with DEFAULT that belong to this user
    This helps fix the issue where templates were created with DEFAULT warehouse_id
    """
    try:
        username = current_user.username
        user_warehouse_id = f'USER_{username.upper()}'

        # Check if user-specific warehouse already exists
        existing_warehouse = WarehouseConfig.query.filter_by(
            warehouse_id=user_warehouse_id
        ).first()

        if existing_warehouse and existing_warehouse.created_by != current_user.id:
            return jsonify({
                'success': False,
                'error': f'Warehouse {user_warehouse_id} already exists and belongs to another user'
            }), 409

        # Find DEFAULT warehouse config created by this user
        default_configs = WarehouseConfig.query.filter_by(
            warehouse_id='DEFAULT',
            created_by=current_user.id
        ).all()

        if not default_configs:
            return jsonify({
                'success': True,
                'message': 'No DEFAULT warehouse configs found for your user',
                'warehouses_found': 0
            }), 200

        # Delete DEFAULT warehouses owned by this user
        deleted_count = 0
        for config in default_configs:
            # Also delete associated locations
            Location.query.filter_by(
                warehouse_id='DEFAULT',
                created_by=current_user.id
            ).delete()

            db.session.delete(config)
            deleted_count += 1

        db.session.commit()

        print(f"[USER_CLEANUP] User {current_user.username} cleaned up {deleted_count} DEFAULT warehouse configs")

        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} DEFAULT warehouse configurations',
            'warehouses_deleted': deleted_count,
            'recommended_next_step': 'Create a new template to set up your user-specific warehouse'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to cleanup: {str(e)}'
        }), 500

@user_reset_bp.route('/status', methods=['GET'])
@token_required
def get_user_status(current_user):
    """
    Get current user's data status
    """
    try:
        username = current_user.username
        user_id = current_user.id

        # Count templates
        active_templates = WarehouseTemplate.query.filter_by(
            created_by=user_id,
            is_active=True
        ).count()

        inactive_templates = WarehouseTemplate.query.filter_by(
            created_by=user_id,
            is_active=False
        ).count()

        # Count warehouse configs
        user_warehouses = WarehouseConfig.query.filter_by(
            created_by=user_id
        ).all()

        warehouse_summary = []
        for wh in user_warehouses:
            location_count = Location.query.filter_by(
                warehouse_id=wh.warehouse_id,
                created_by=user_id
            ).count()

            warehouse_summary.append({
                'warehouse_id': wh.warehouse_id,
                'warehouse_name': wh.warehouse_name,
                'locations': location_count,
                'created_at': wh.created_at.isoformat() if wh.created_at else None
            })

        # Check for DEFAULT warehouse issue
        has_default_issue = any(wh['warehouse_id'] == 'DEFAULT' for wh in warehouse_summary)

        return jsonify({
            'user': {
                'id': user_id,
                'username': username
            },
            'templates': {
                'active': active_templates,
                'inactive': inactive_templates,
                'total': active_templates + inactive_templates,
                'limit': 5,
                'remaining': max(0, 5 - active_templates)
            },
            'warehouses': warehouse_summary,
            'issues': {
                'has_default_warehouse': has_default_issue,
                'recommended_warehouse_id': f'USER_{username.upper()}'
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get status: {str(e)}'
        }), 500
