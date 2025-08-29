"""
API endpoint for user-specific warehouse detection
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import WarehouseConfig
from database import db

user_warehouse_bp = Blueprint('user_warehouse', __name__)

@user_warehouse_bp.route('/api/v1/user/warehouse', methods=['GET'])
@login_required
def get_user_warehouse():
    """Get the primary warehouse for the current user"""
    try:
        user_id = current_user.id
        username = current_user.username
        
        # Strategy 1: Look for warehouses created by this user
        user_created_warehouses = WarehouseConfig.query.filter_by(created_by=user_id).all()
        
        # Strategy 2: Look for username-based warehouse patterns
        possible_patterns = [
            f'USER_{username.upper()}',
            f'USER_{username}',
            f'{username.upper()}',
            username,
        ]
        
        pattern_warehouses = []
        for pattern in possible_patterns:
            warehouse = WarehouseConfig.query.filter_by(warehouse_id=pattern).first()
            if warehouse:
                pattern_warehouses.append(warehouse)
        
        # Combine and prioritize results
        all_user_warehouses = []
        
        # Add created warehouses first (highest priority)
        for warehouse in user_created_warehouses:
            # CRITICAL FIX: Count physical special location records, not config JSON
            from models import Location
            special_count = Location.query.filter(
                Location.warehouse_id == warehouse.warehouse_id,
                Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
            ).count()
            
            all_user_warehouses.append({
                'warehouse_id': warehouse.warehouse_id,
                'warehouse_name': warehouse.warehouse_name,
                'special_areas_count': special_count,
                'created_by_user': True,
                'pattern_match': False,
                'priority': 1
            })
        
        # Add pattern matches (lower priority)
        for warehouse in pattern_warehouses:
            if warehouse not in user_created_warehouses:  # Avoid duplicates
                # CRITICAL FIX: Count physical special location records, not config JSON
                from models import Location
                special_count = Location.query.filter(
                    Location.warehouse_id == warehouse.warehouse_id,
                    Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
                ).count()
                
                all_user_warehouses.append({
                    'warehouse_id': warehouse.warehouse_id,
                    'warehouse_name': warehouse.warehouse_name,
                    'special_areas_count': special_count,
                    'created_by_user': False,
                    'pattern_match': True,
                    'priority': 2
                })
        
        # Sort by priority, then by special areas count (descending)
        all_user_warehouses.sort(key=lambda x: (x['priority'], -x['special_areas_count']))
        
        # Determine primary warehouse
        if all_user_warehouses:
            primary_warehouse = all_user_warehouses[0]
            
            return jsonify({
                'success': True,
                'primary_warehouse': primary_warehouse['warehouse_id'],
                'primary_warehouse_name': primary_warehouse['warehouse_name'],
                'special_areas_count': primary_warehouse['special_areas_count'],
                'all_user_warehouses': all_user_warehouses,
                'detection_method': 'user_created' if primary_warehouse['created_by_user'] else 'pattern_match'
            })
        else:
            # No user-specific warehouses found, use DEFAULT
            default_warehouse = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').first()
            if default_warehouse:
                # CRITICAL FIX: Count physical special location records, not config JSON
                from models import Location
                special_count = Location.query.filter(
                    Location.warehouse_id == 'DEFAULT',
                    Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
                ).count()
                
                return jsonify({
                    'success': True,
                    'primary_warehouse': 'DEFAULT',
                    'primary_warehouse_name': default_warehouse.warehouse_name,
                    'special_areas_count': special_count,
                    'all_user_warehouses': [],
                    'detection_method': 'fallback_default',
                    'message': 'No user-specific warehouses found, using DEFAULT'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No warehouses found for user and DEFAULT warehouse does not exist',
                    'primary_warehouse': None
                })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to determine user warehouse: {str(e)}',
            'primary_warehouse': 'DEFAULT'  # Safe fallback
        }), 500

@user_warehouse_bp.route('/api/v1/user/warehouses', methods=['GET'])
@login_required
def get_all_user_warehouses():
    """Get all warehouses accessible to the current user"""
    try:
        user_id = current_user.id
        username = current_user.username
        
        # Get all warehouses created by user
        user_warehouses = WarehouseConfig.query.filter_by(created_by=user_id).all()
        
        # Add DEFAULT warehouse if it exists
        default_warehouse = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').first()
        
        result = []
        
        for warehouse in user_warehouses:
            special_count = (len(warehouse.get_receiving_areas()) + 
                           len(warehouse.get_staging_areas()) + 
                           len(warehouse.get_dock_areas()))
            
            result.append({
                'warehouse_id': warehouse.warehouse_id,
                'warehouse_name': warehouse.warehouse_name,
                'special_areas_count': special_count,
                'is_default': False,
                'created_by_user': True
            })
        
        if default_warehouse and default_warehouse not in user_warehouses:
            special_count = (len(default_warehouse.get_receiving_areas()) + 
                           len(default_warehouse.get_staging_areas()) + 
                           len(default_warehouse.get_dock_areas()))
            
            result.append({
                'warehouse_id': 'DEFAULT',
                'warehouse_name': default_warehouse.warehouse_name,
                'special_areas_count': special_count,
                'is_default': True,
                'created_by_user': False
            })
        
        return jsonify({
            'success': True,
            'warehouses': result,
            'total_count': len(result)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get user warehouses: {str(e)}',
            'warehouses': []
        }), 500