"""
Template Management API
Handles warehouse template creation, sharing, and application
"""

import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import and_, or_
from functools import wraps
from database import db
from models import WarehouseTemplate, WarehouseConfig, Location
from core_models import User

# Create the template API blueprint
template_bp = Blueprint('template_api', __name__, url_prefix='/api/v1/templates')

# Import auth decorator from app.py
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

def generate_locations_from_template(template, warehouse_id, current_user):
    """Generate warehouse locations from template configuration"""
    created_locations = []
    
    try:
        # Generate storage locations using the model's class method
        for aisle in range(1, template.num_aisles + 1):
            for rack in range(1, template.racks_per_aisle + 1):
                for position in range(1, template.positions_per_rack + 1):
                    for level_idx in range(template.levels_per_position):
                        level = template.level_names[level_idx] if level_idx < len(template.level_names) else f'L{level_idx + 1}'
                        
                        location = Location.create_from_structure(
                            warehouse_id=warehouse_id,
                            aisle_num=aisle,
                            rack_num=rack,
                            position_num=position,
                            level=level,
                            pallet_capacity=template.default_pallet_capacity,
                            zone='GENERAL',
                            location_type='STORAGE',
                            created_by=current_user.id
                        )
                        
                        db.session.add(location)
                        created_locations.append(location)

        # Generate special areas from template
        special_area_configs = [
            (template.receiving_areas_template, 'RECEIVING', 'DOCK', 10),
            (template.staging_areas_template, 'STAGING', 'STAGING', 5),
            (template.dock_areas_template, 'DOCK', 'DOCK', 2)
        ]

        for areas_template, loc_type, zone, default_cap in special_area_configs:
            if not areas_template: continue
            try:
                areas = json.loads(areas_template) if isinstance(areas_template, str) else areas_template
                for idx, area_data in enumerate(areas):
                    base_code = area_data.get('code', f'{loc_type}_{idx+1}')
                    code = f"{warehouse_id}_{base_code}"

                    location = Location(
                        code=code,
                        location_type=loc_type,
                        capacity=area_data.get('capacity', default_cap),
                        pallet_capacity=area_data.get('capacity', default_cap),
                        zone=area_data.get('zone', zone),
                        warehouse_id=warehouse_id,
                        created_by=current_user.id
                    )
                    db.session.add(location)
                    created_locations.append(location)
            except (json.JSONDecodeError, TypeError) as e:
                current_app.logger.warning(f"Skipping invalid special area JSON for {loc_type}: {e}")
                pass

        return created_locations
        
    except Exception as e:
        current_app.logger.error(f"Error generating locations from template: {str(e)}")
        # Rollback in case of partial creation
        db.session.rollback()
        return []

@template_bp.route('', methods=['GET'])
@token_required
def list_templates(current_user):
    """
    List available templates
    Query parameters:
    - scope: 'my' (user's templates), 'public' (public templates), 'all' (both)
    - page: Page number
    - per_page: Items per page
    - search: Search in template names and descriptions
    """
    try:
        scope = request.args.get('scope', 'all')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        search = request.args.get('search')
        
        # Build query based on scope
        if scope == 'my':
            query = WarehouseTemplate.query.filter_by(created_by=current_user.id, is_active=True)
        elif scope == 'public':
            query = WarehouseTemplate.query.filter_by(is_public=True, is_active=True)
        else:  # 'all'
            query = WarehouseTemplate.query.filter(
                and_(
                    WarehouseTemplate.is_active == True,
                    or_(
                        WarehouseTemplate.created_by == current_user.id,
                        WarehouseTemplate.is_public == True
                    )
                )
            )
        
        # Apply search filter if provided
        if search:
            search_filter = or_(
                WarehouseTemplate.name.ilike(f'%{search}%'),
                WarehouseTemplate.description.ilike(f'%{search}%'),
                WarehouseTemplate.template_code.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Order by usage count and creation date
        query = query.order_by(
            WarehouseTemplate.usage_count.desc(),
            WarehouseTemplate.created_at.desc()
        )
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        templates = pagination.items
        
        # Get summary statistics
        my_templates_count = WarehouseTemplate.query.filter_by(
            created_by=current_user.id, 
            is_active=True
        ).count()
        public_templates_count = WarehouseTemplate.query.filter_by(
            is_public=True, 
            is_active=True
        ).count()
        
        return jsonify({
            'templates': [template.to_dict() for template in templates],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'summary': {
                'my_templates': my_templates_count,
                'public_templates': public_templates_count,
                'scope': scope
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list templates: {str(e)}'}), 500

@template_bp.route('/<int:template_id>', methods=['GET'])
@token_required
def get_template(current_user, template_id):
    """Get a specific template by ID"""
    try:
        template = WarehouseTemplate.query.get_or_404(template_id)
        
        # Check access permissions
        if not template.is_public and template.created_by != current_user.id:
            return jsonify({'error': 'Access denied to private template'}), 403
        
        return jsonify({'template': template.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Template not found: {str(e)}'}), 404

@template_bp.route('/by-code/<string:template_code>', methods=['GET'])
@token_required
def get_template_by_code(current_user, template_code):
    """Get template by shareable code"""
    try:
        template = WarehouseTemplate.query.filter_by(
            template_code=template_code, 
            is_active=True
        ).first_or_404()
        
        # Public templates or own templates are accessible
        if not template.is_public and template.created_by != current_user.id:
            return jsonify({'error': 'Access denied to private template'}), 403
        
        return jsonify({'template': template.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Template not found with code: {template_code}'}), 404

@template_bp.route('', methods=['POST'])
@token_required
def create_template(current_user):
    """
    Create a new template
    Can create from scratch or from existing warehouse config
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No template data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'num_aisles', 'racks_per_aisle', 'positions_per_rack']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create template
        template = WarehouseTemplate(
            name=data['name'],
            description=data.get('description'),
            num_aisles=int(data['num_aisles']),
            racks_per_aisle=int(data['racks_per_aisle']),
            positions_per_rack=int(data['positions_per_rack']),
            levels_per_position=int(data.get('levels_per_position', 4)),
            level_names=data.get('level_names', 'ABCD'),
            default_pallet_capacity=int(data.get('default_pallet_capacity', 1)),
            bidimensional_racks=data.get('bidimensional_racks', False),
            based_on_config_id=data.get('based_on_config_id'),
            is_public=data.get('is_public', False),
            created_by=current_user.id
        )
        
        # Set special areas templates if provided
        if 'receiving_areas_template' in data:
            template.set_receiving_areas_template(data['receiving_areas_template'])
        
        # Generate unique template code
        template.generate_template_code()
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'message': 'Template created successfully',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create template: {str(e)}'}), 500

@template_bp.route('/from-config', methods=['POST'])
@token_required
def create_template_from_config(current_user):
    """Create template from existing warehouse configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if 'config_id' not in data or 'template_name' not in data:
            return jsonify({'error': 'Missing config_id or template_name'}), 400
        
        # Get the source configuration
        config = WarehouseConfig.query.get_or_404(data['config_id'])
        
        # Check if user has access to this config
        if config.created_by != current_user.id:
            return jsonify({'error': 'Access denied to warehouse configuration'}), 403
        
        # Create template from config
        template = WarehouseTemplate.create_from_config(
            config=config,
            name=data['template_name'],
            description=data.get('template_description'),
            is_public=data.get('is_public', False)
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'message': 'Template created from configuration successfully',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create template from config: {str(e)}'}), 500

@template_bp.route('/<int:template_id>', methods=['PUT'])
@token_required
def update_template(current_user, template_id):
    """Update an existing template"""
    try:
        template = WarehouseTemplate.query.get_or_404(template_id)
        
        # Check ownership
        if template.created_by != current_user.id:
            return jsonify({'error': 'Access denied. You can only update your own templates'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        updatable_fields = [
            'name', 'description', 'num_aisles', 'racks_per_aisle', 'positions_per_rack',
            'levels_per_position', 'level_names', 'default_pallet_capacity',
            'bidimensional_racks', 'is_public'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field in ['num_aisles', 'racks_per_aisle', 'positions_per_rack', 
                           'levels_per_position', 'default_pallet_capacity']:
                    setattr(template, field, int(data[field]))
                elif field in ['bidimensional_racks', 'is_public']:
                    setattr(template, field, bool(data[field]))
                else:
                    setattr(template, field, data[field])
        
        # Update special areas templates
        if 'receiving_areas_template' in data:
            template.set_receiving_areas_template(data['receiving_areas_template'])
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Template updated successfully',
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update template: {str(e)}'}), 500

@template_bp.route('/<int:template_id>', methods=['DELETE'])
@token_required
def delete_template(current_user, template_id):
    """Delete a template (soft delete)"""
    try:
        template = WarehouseTemplate.query.get_or_404(template_id)
        
        # Check ownership
        if template.created_by != current_user.id:
            return jsonify({'error': 'Access denied. You can only delete your own templates'}), 403
        
        # Soft delete
        template.is_active = False
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Template deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete template: {str(e)}'}), 500

@template_bp.route('/<int:template_id>/apply', methods=['POST'])
@token_required
def apply_template(current_user, template_id):
    """Apply template to create new warehouse configuration"""
    try:
        template = WarehouseTemplate.query.get_or_404(template_id)
        
        # Check access permissions
        if not template.is_public and template.created_by != current_user.id:
            return jsonify({'error': 'Access denied to private template'}), 403
        
        data = request.get_json() or {}
        
        # Generate unique warehouse ID
        warehouse_id = data.get('warehouse_id', f'WAREHOUSE_{current_user.id}_{int(datetime.utcnow().timestamp())}')
        warehouse_name = data.get('warehouse_name', f'Warehouse from {template.name}')
        
        # Check if warehouse already exists
        existing_config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
        
        if existing_config:
            # Update existing warehouse configuration
            config = existing_config
            # Clear existing locations before generating new ones (bulk delete for efficiency)
            Location.query.filter_by(warehouse_id=warehouse_id).delete()
            
            # Flush deletions to ensure they complete before creating new locations
            db.session.flush()
        else:
            # Create new warehouse configuration
            config = WarehouseConfig(warehouse_id=warehouse_id, created_by=current_user.id)
            db.session.add(config)
        
        # Copy template configuration
        config.warehouse_name = warehouse_name
        config.num_aisles = template.num_aisles
        config.racks_per_aisle = template.racks_per_aisle
        config.positions_per_rack = template.positions_per_rack
        config.levels_per_position = template.levels_per_position
        config.level_names = template.level_names
        config.default_pallet_capacity = template.default_pallet_capacity
        config.bidimensional_racks = template.bidimensional_racks
        config.receiving_areas = template.receiving_areas_template
        config.staging_areas = template.staging_areas_template
        config.dock_areas = template.dock_areas_template
        config.updated_at = datetime.utcnow()
        
        # Override with any custom parameters
        if 'customizations' in data:
            customizations = data['customizations']
            for field, value in customizations.items():
                if hasattr(config, field):
                    setattr(config, field, value)
        
        db.session.commit()
        
        # Generate locations if requested
        generate_locations = data.get('generate_locations', True)
        locations_created = 0
        created_locations = []
        
        if generate_locations:
            # Generate warehouse locations from template
            created_locations = generate_locations_from_template(template, warehouse_id, current_user)
            locations_created = len(created_locations)
        
        # Increment template usage count
        template.increment_usage()
        
        return jsonify({
            'message': 'Template applied successfully',
            'warehouse_id': warehouse_id,
            'configuration': config.to_dict(),
            'template_code': template.template_code,
            'locations_created': locations_created,
            'storage_locations': len([loc for loc in created_locations if loc.location_type == 'STORAGE']) if generate_locations else 0,
            'special_areas': len([loc for loc in created_locations if loc.location_type != 'STORAGE']) if generate_locations else 0
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to apply template: {str(e)}'}), 500

@template_bp.route('/apply-by-code', methods=['POST'])
@token_required
def apply_template_by_code(current_user):
    """Apply template using shareable code"""
    try:
        data = request.get_json()
        
        if not data or 'template_code' not in data:
            return jsonify({'error': 'Missing template_code'}), 400
        
        template_code = data['template_code']
        template = WarehouseTemplate.query.filter_by(
            template_code=template_code, 
            is_active=True
        ).first()
        
        if not template:
            return jsonify({'error': f'Template not found with code: {template_code}'}), 404
        
        # Check access permissions
        if not template.is_public and template.created_by != current_user.id:
            return jsonify({'error': 'Access denied to private template'}), 403
        
        # Use the same logic as apply_template but with the found template
        # Generate unique warehouse ID or check if provided one is available
        warehouse_id = data.get('warehouse_id')
        if not warehouse_id:
            warehouse_id = f'WAREHOUSE_{current_user.id}_{int(datetime.utcnow().timestamp())}'
        
        # Check if warehouse_id already exists
        existing_config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
        warehouse_name = data.get('warehouse_name', f'Warehouse from {template.name}')
        
        if existing_config:
            # Update existing warehouse configuration
            config = existing_config
            config.warehouse_name = warehouse_name
            config.num_aisles = template.num_aisles
            config.racks_per_aisle = template.racks_per_aisle
            config.positions_per_rack = template.positions_per_rack
            config.levels_per_position = template.levels_per_position
            config.level_names = template.level_names
            config.default_pallet_capacity = template.default_pallet_capacity
            config.bidimensional_racks = template.bidimensional_racks
            config.receiving_areas = template.receiving_areas_template
            config.staging_areas = template.staging_areas_template
            config.dock_areas = template.dock_areas_template
            config.updated_at = datetime.utcnow()
            
            # Clear existing locations before generating new ones (bulk delete for efficiency)
            Location.query.filter_by(warehouse_id=warehouse_id).delete()
            
            # Flush deletions to ensure they complete before creating new locations
            db.session.flush()
            
        else:
            # Create new warehouse configuration from template
            config = WarehouseConfig(
                warehouse_id=warehouse_id,
                warehouse_name=warehouse_name,
                num_aisles=template.num_aisles,
                racks_per_aisle=template.racks_per_aisle,
                positions_per_rack=template.positions_per_rack,
                levels_per_position=template.levels_per_position,
                level_names=template.level_names,
                default_pallet_capacity=template.default_pallet_capacity,
                bidimensional_racks=template.bidimensional_racks,
                receiving_areas=template.receiving_areas_template,
                staging_areas=template.staging_areas_template,
                dock_areas=template.dock_areas_template,
                created_by=current_user.id
            )
            
            db.session.add(config)
        db.session.flush()  # Ensure config is saved before generating locations
        
        # Generate warehouse locations from template
        created_locations = generate_locations_from_template(template, warehouse_id, current_user)
        
        db.session.commit()
        
        # Debug: Check if locations were actually created
        created_count = Location.query.filter_by(warehouse_id=warehouse_id, is_active=True).count()
        print(f"DEBUG: After template application, found {created_count} active locations for warehouse {warehouse_id}")
        
        # Increment template usage count
        template.increment_usage()
        
        return jsonify({
            'message': f'Template {template_code} applied successfully',
            'warehouse_id': warehouse_id,
            'configuration': config.to_dict(),
            'template': template.to_dict(),
            'locations_created': len(created_locations),
            'storage_locations': len([loc for loc in created_locations if loc.location_type == 'STORAGE']),
            'special_areas': len([loc for loc in created_locations if loc.location_type != 'STORAGE'])
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to apply template by code: {str(e)}'}), 500

@template_bp.route('/<int:template_id>/preview', methods=['GET'])
@token_required
def preview_template(current_user, template_id):
    """Preview what a template would create"""
    try:
        template = WarehouseTemplate.query.get_or_404(template_id)
        
        # Check access permissions
        if not template.is_public and template.created_by != current_user.id:
            return jsonify({'error': 'Access denied to private template'}), 403
        
        # Calculate totals
        total_storage_locations = (template.num_aisles * template.racks_per_aisle * 
                                 template.positions_per_rack * template.levels_per_position)
        total_capacity = total_storage_locations * template.default_pallet_capacity
        
        # Add receiving areas capacity
        receiving_areas = template.get_receiving_areas_template()
        receiving_capacity = sum(area.get('capacity', 0) for area in receiving_areas)
        
        # Generate sample location codes
        sample_locations = []
        for position in range(1, min(6, template.positions_per_rack + 1)):
            for level_idx in range(min(2, template.levels_per_position)):
                level = template.level_names[level_idx] if level_idx < len(template.level_names) else f'L{level_idx + 1}'
                code = f"{position:03d}{level}"
                sample_locations.append({
                    'code': code,
                    'full_address': f"Aisle 1, Rack 1, Position {position:03d}{level}"
                })
        
        preview = {
            'template': template.to_dict(),
            'calculations': {
                'total_storage_locations': total_storage_locations,
                'total_storage_capacity': total_capacity,
                'receiving_capacity': receiving_capacity,
                'total_capacity': total_capacity + receiving_capacity
            },
            'sample_locations': sample_locations,
            'special_areas': {
                'receiving': receiving_areas
            }
        }
        
        return jsonify({'preview': preview}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate template preview: {str(e)}'}), 500

@template_bp.route('/popular', methods=['GET'])
@token_required
def get_popular_templates(current_user):
    """Get most popular public templates"""
    try:
        limit = min(int(request.args.get('limit', 10)), 20)
        
        templates = WarehouseTemplate.query.filter_by(
            is_public=True, 
            is_active=True
        ).order_by(
            WarehouseTemplate.usage_count.desc(),
            WarehouseTemplate.created_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'templates': [template.to_dict() for template in templates],
            'count': len(templates)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get popular templates: {str(e)}'}), 500

# Register error handlers
@template_bp.errorhandler(404)
def template_not_found(error):
    return jsonify({'error': 'Template not found'}), 404

@template_bp.errorhandler(403)
def template_access_denied(error):
    return jsonify({'error': 'Access denied'}), 403

@template_bp.errorhandler(409)
def template_conflict(error):
    return jsonify({'error': 'Template conflict'}), 409

@template_bp.errorhandler(500)
def template_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500