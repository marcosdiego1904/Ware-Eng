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
from virtual_template_integration import get_virtual_template_manager

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
        # Batch storage locations generation for better performance
        storage_locations_batch = []
        
        # Generate storage locations using batch processing
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
                        
                        storage_locations_batch.append(location)
                        created_locations.append(location)
        
        # Bulk add storage locations in batches of 1000 for optimal performance
        batch_size = 1000
        for i in range(0, len(storage_locations_batch), batch_size):
            batch = storage_locations_batch[i:i + batch_size]
            db.session.bulk_save_objects(batch)
            db.session.flush()  # Flush each batch to avoid memory issues

        # Generate special areas from template with improved performance
        special_area_configs = [
            (template.receiving_areas_template, 'RECEIVING', 'DOCK', 10),
            (template.staging_areas_template, 'STAGING', 'STAGING', 5),
            (template.dock_areas_template, 'DOCK', 'DOCK', 2)
        ]
        
        # FIXED: Generate AISLE locations for Rule #5 (stuck pallets detection)
        # Create one AISLE location per aisle for transitional pallet tracking
        aisle_locations_data = []
        for aisle_num in range(1, template.num_aisles + 1):
            aisle_locations_data.append({
                'code': f'AISLE-{aisle_num:02d}',
                'capacity': 10,  # Temporary capacity for pallets in transit
                'zone': 'GENERAL'
            })
        
        # Add AISLE locations to special area configs
        special_area_configs.append((json.dumps(aisle_locations_data), 'TRANSITIONAL', 'GENERAL', 10))

        special_locations_batch = []
        
        # Get all existing location codes in one query for conflict checking
        existing_codes = set()
        if warehouse_id != 'DEFAULT':
            existing_locations = Location.query.with_entities(Location.code).all()
            existing_codes = {code[0] for code in existing_locations}

        for areas_template, loc_type, zone, default_cap in special_area_configs:
            if not areas_template: continue
            try:
                areas = json.loads(areas_template) if isinstance(areas_template, str) else areas_template
                for idx, area_data in enumerate(areas):
                    base_code = area_data.get('code', f'{loc_type}_{idx+1}')
                    
                    # Use clean location codes for special areas (no prefixes needed)
                    unique_code = base_code  # Keep original code clean
                    
                    # Check for conflicts and add suffix if needed (using cached codes)
                    attempt = 0
                    original_code = unique_code
                    while unique_code in existing_codes:
                        attempt += 1
                        unique_code = f"{original_code}_{attempt}"
                    
                    # Add to cache to avoid future conflicts in this batch
                    existing_codes.add(unique_code)

                    location = Location(
                        code=unique_code,
                        location_type=loc_type,
                        capacity=area_data.get('capacity', default_cap),
                        pallet_capacity=area_data.get('capacity', default_cap),
                        zone=area_data.get('zone', zone),
                        warehouse_id=warehouse_id,
                        created_by=current_user.id
                    )
                    special_locations_batch.append(location)
                    created_locations.append(location)
            except (json.JSONDecodeError, TypeError) as e:
                current_app.logger.warning(f"Skipping invalid special area JSON for {loc_type}: {e}")
                pass
        
        # Bulk add special locations
        if special_locations_batch:
            db.session.bulk_save_objects(special_locations_batch)
            db.session.flush()

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
        
        if 'staging_areas_template' in data:
            template.set_staging_areas_template(data['staging_areas_template'])
        
        if 'dock_areas_template' in data:
            template.set_dock_areas_template(data['dock_areas_template'])
        
        # Set location format configuration if provided
        location_format_data = data.get('location_format')
        if location_format_data:
            try:
                # Handle format configuration from detect-format API
                if 'format_config' in location_format_data:
                    format_config = location_format_data['format_config']
                    template.set_location_format_config(format_config)
                    template.format_confidence = location_format_data.get('confidence', format_config.get('confidence'))
                    
                    # Set examples if provided
                    examples = location_format_data.get('examples', format_config.get('examples', []))
                    if examples:
                        template.set_format_examples(examples)
                
                # Handle direct format configuration
                elif 'examples' in location_format_data:
                    # Auto-detect format from examples
                    from smart_format_detector import SmartFormatDetector
                    
                    detector = SmartFormatDetector()
                    detection_result = detector.detect_format(location_format_data['examples'])
                    
                    if detection_result.get('detected_pattern'):
                        warehouse_context = {
                            'template_name': data['name'],
                            'template_description': data.get('description')
                        }
                        format_config = detector.create_format_config(detection_result, warehouse_context)
                        
                        template.set_location_format_config(format_config)
                        template.format_confidence = detection_result.get('confidence')
                        template.set_format_examples(location_format_data['examples'])
                        
                        current_app.logger.info(f"Auto-detected location format for template '{data['name']}': "
                                              f"{format_config.get('pattern_type')} with {detection_result.get('confidence', 0):.2%} confidence")
                
            except Exception as e:
                current_app.logger.warning(f"Failed to set location format for template '{data['name']}': {e}")
                # Don't fail template creation if format detection fails
        
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
            if isinstance(data['receiving_areas_template'], str):
                # If it's a JSON string, use it directly
                template.receiving_areas_template = data['receiving_areas_template']
            else:
                # If it's a list, convert to JSON
                template.set_receiving_areas_template(data['receiving_areas_template'])
        
        if 'staging_areas_template' in data:
            if isinstance(data['staging_areas_template'], str):
                template.staging_areas_template = data['staging_areas_template']
            else:
                template.set_staging_areas_template(data['staging_areas_template'])
        
        if 'dock_areas_template' in data:
            if isinstance(data['dock_areas_template'], str):
                template.dock_areas_template = data['dock_areas_template']
            else:
                template.set_dock_areas_template(data['dock_areas_template'])
        
        # Update location format configuration if provided
        location_format_data = data.get('location_format')
        if location_format_data:
            try:
                # Handle format configuration from detect-format API
                if 'format_config' in location_format_data:
                    format_config = location_format_data['format_config']
                    template.set_location_format_config(format_config)
                    template.format_confidence = location_format_data.get('confidence', format_config.get('confidence'))
                    
                    # Set examples if provided
                    examples = location_format_data.get('examples', format_config.get('examples', []))
                    if examples:
                        template.set_format_examples(examples)
                
                # Handle direct format configuration
                elif 'examples' in location_format_data:
                    # Auto-detect format from examples
                    from smart_format_detector import SmartFormatDetector
                    
                    detector = SmartFormatDetector()
                    detection_result = detector.detect_format(location_format_data['examples'])
                    
                    if detection_result.get('detected_pattern'):
                        warehouse_context = {
                            'template_name': template.name,
                            'template_id': template.id,
                            'update_operation': True
                        }
                        format_config = detector.create_format_config(detection_result, warehouse_context)
                        
                        template.set_location_format_config(format_config)
                        template.format_confidence = detection_result.get('confidence')
                        template.set_format_examples(location_format_data['examples'])
                        
                        current_app.logger.info(f"Updated location format for template '{template.name}' (ID {template.id}): "
                                              f"{format_config.get('pattern_type')} with {detection_result.get('confidence', 0):.2%} confidence")
                
                # Handle clear format request
                elif location_format_data.get('clear_format', False):
                    template.set_location_format_config(None)
                    template.format_confidence = None
                    template.set_format_examples([])
                    current_app.logger.info(f"Cleared location format for template '{template.name}' (ID {template.id})")
                
            except Exception as e:
                current_app.logger.warning(f"Failed to update location format for template '{template.name}': {e}")
                # Don't fail template update if format processing fails
        
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
    """Apply template to create new warehouse configuration with virtual locations"""
    try:
        template = WarehouseTemplate.query.get_or_404(template_id)
        
        # Check access permissions
        if not template.is_public and template.created_by != current_user.id:
            return jsonify({'error': 'Access denied to private template'}), 403
        
        data = request.get_json() or {}
        
        # Generate unique warehouse ID
        warehouse_id = data.get('warehouse_id', f'WAREHOUSE_{current_user.id}_{int(datetime.utcnow().timestamp())}')
        warehouse_name = data.get('warehouse_name', f'Warehouse from {template.name}')
        
        # VIRTUAL LOCATIONS: Use feature flag to control rollout
        use_virtual_locations = data.get('use_virtual_locations', True)
        
        print(f"[TEMPLATE_API] Applying template {template_id} with virtual_locations={use_virtual_locations}")
        
        # Get virtual template manager
        virtual_manager = get_virtual_template_manager()
        
        # Apply template with virtual or legacy mode
        if use_virtual_locations:
            result = virtual_manager.apply_template_with_virtual_locations(
                template, warehouse_id, warehouse_name, current_user, 
                customizations=data.get('customizations')
            )
        else:
            result = virtual_manager.apply_template_legacy_mode(
                template, warehouse_id, warehouse_name, current_user,
                customizations=data.get('customizations')
            )
        
        return jsonify({
            'message': f'Template applied successfully using {result["creation_method"]}',
            'warehouse_id': result['warehouse_id'],
            'configuration': result['configuration'],
            'template_code': result['template_code'],
            'locations_created': result.get('locations_created', 0),
            'virtual_locations_available': result.get('virtual_locations_available', 0),
            'storage_locations': result.get('storage_locations', 0),
            'special_areas': result.get('special_areas', 0),
            'virtual_location_summary': result.get('virtual_location_summary', {}),
            'creation_method': result['creation_method']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        
        # CRITICAL UX IMPROVEMENT: Provide user-friendly error messages
        error_message = str(e)
        
        # Check for duplicate key constraint violation (most common template issue)
        if 'duplicate key value violates unique constraint' in error_message and 'location_code_key' in error_message:
            # Extract the location code from the error message
            import re
            location_match = re.search(r"Key \(code\)=\(([^)]+)\)", error_message)
            location_code = location_match.group(1) if location_match else "unknown location"
            
            return jsonify({
                'error': 'Template Application Conflict',
                'error_type': 'duplicate_locations',
                'message': f'Template contains locations that already exist in this warehouse.',
                'details': {
                    'conflicting_location': location_code,
                    'explanation': f'Location "{location_code}" already exists in your warehouse. Templates cannot create duplicate location codes.',
                    'solutions': [
                        {
                            'option': 'replace',
                            'title': 'Replace Existing Locations',
                            'description': 'Apply template and replace existing locations with new configuration',
                            'action': 'The system will delete existing locations and create new ones from your template'
                        },
                        {
                            'option': 'rename',
                            'title': 'Rename Template Locations', 
                            'description': 'Edit your template to use different location names',
                            'action': 'Change location codes in template (e.g., RECV-01 → RECV-NEW1)'
                        },
                        {
                            'option': 'cancel',
                            'title': 'Cancel Application',
                            'description': 'Keep existing locations unchanged',
                            'action': 'No changes will be made to your warehouse'
                        }
                    ]
                },
                'user_friendly': True
            }), 409  # 409 Conflict is more appropriate than 500
        
        # Check for other common database errors
        elif 'permission denied' in error_message.lower():
            return jsonify({
                'error': 'Permission Error',
                'message': 'You do not have permission to modify this warehouse configuration.',
                'user_friendly': True
            }), 403
        
        elif 'connection' in error_message.lower() or 'timeout' in error_message.lower():
            return jsonify({
                'error': 'Database Connection Issue',
                'message': 'Unable to connect to the warehouse database. Please try again in a moment.',
                'user_friendly': True
            }), 503
        
        # For other errors, provide a generic user-friendly message but log the technical details
        import logging
        logging.error(f"Template application failed for user {current_user.id}: {error_message}")
        
        return jsonify({
            'error': 'Template Application Failed',
            'message': 'An unexpected error occurred while applying the template. Please contact support if this continues.',
            'user_friendly': True,
            'support_info': 'Include template name and timestamp when contacting support'
        }), 500

# Duplicate function removed - using updated original function below

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
        
        # Generate warehouse ID
        warehouse_id = data.get('warehouse_id')
        if not warehouse_id:
            warehouse_id = f'WAREHOUSE_{current_user.id}_{int(datetime.utcnow().timestamp())}'
        
        warehouse_name = data.get('warehouse_name', f'Warehouse from {template.name}')
        
        # VIRTUAL LOCATIONS: Default to true for new template applications
        use_virtual_locations = data.get('use_virtual_locations', True)
        
        print(f"[TEMPLATE_API] Applying template {template_code} with virtual_locations={use_virtual_locations}")
        
        # Get virtual template manager
        virtual_manager = get_virtual_template_manager()
        
        # Apply template with virtual or legacy mode
        if use_virtual_locations:
            result = virtual_manager.apply_template_with_virtual_locations(
                template, warehouse_id, warehouse_name, current_user, 
                customizations=data.get('customizations')
            )
        else:
            result = virtual_manager.apply_template_legacy_mode(
                template, warehouse_id, warehouse_name, current_user,
                customizations=data.get('customizations')
            )
        
        return jsonify({
            'message': f'Template {template_code} applied successfully using {result["creation_method"]}',
            'warehouse_id': result['warehouse_id'],
            'configuration': result['configuration'],
            'template_code': result['template_code'],
            'locations_created': result.get('locations_created', 0),
            'virtual_locations_available': result.get('virtual_locations_available', 0),
            'storage_locations': result.get('storage_locations', 0),
            'special_areas': result.get('special_areas', 0),
            'virtual_location_summary': result.get('virtual_location_summary', {}),
            'creation_method': result['creation_method']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        
        # CRITICAL UX IMPROVEMENT: Provide user-friendly error messages (same as apply endpoint)
        error_message = str(e)
        
        # Check for duplicate key constraint violation (most common template issue)
        if 'duplicate key value violates unique constraint' in error_message and 'location_code_key' in error_message:
            # Extract the location code from the error message
            import re
            location_match = re.search(r"Key \(code\)=\(([^)]+)\)", error_message)
            location_code = location_match.group(1) if location_match else "unknown location"
            
            return jsonify({
                'error': 'Template Application Conflict',
                'error_type': 'duplicate_locations',
                'message': f'Template contains locations that already exist in this warehouse.',
                'details': {
                    'conflicting_location': location_code,
                    'explanation': f'Location "{location_code}" already exists in your warehouse. Templates cannot create duplicate location codes.',
                    'solutions': [
                        {
                            'option': 'replace',
                            'title': 'Replace Existing Locations',
                            'description': 'Apply template and replace existing locations with new configuration',
                            'action': 'The system will delete existing locations and create new ones from your template'
                        },
                        {
                            'option': 'rename',
                            'title': 'Rename Template Locations', 
                            'description': 'Edit your template to use different location names',
                            'action': 'Change location codes in template (e.g., RECV-01 → RECV-NEW1)'
                        },
                        {
                            'option': 'cancel',
                            'title': 'Cancel Application',
                            'description': 'Keep existing locations unchanged',
                            'action': 'No changes will be made to your warehouse'
                        }
                    ]
                },
                'user_friendly': True
            }), 409  # 409 Conflict is more appropriate than 500
        
        # For other errors, provide a generic user-friendly message but log the technical details
        import logging
        logging.error(f"Template application by code failed for user {current_user.id}: {error_message}")
        
        return jsonify({
            'error': 'Template Application Failed',
            'message': 'An unexpected error occurred while applying the template. Please contact support if this continues.',
            'user_friendly': True,
            'support_info': 'Include template code and timestamp when contacting support'
        }), 500

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


@template_bp.route('/detect-format', methods=['POST'])
@token_required
def detect_location_format(current_user):
    """
    Detect location format from user-provided examples
    
    This endpoint analyzes location examples and returns the detected format pattern
    with confidence scoring and canonical conversion examples. Used during template
    creation to automatically configure location formats.
    
    Expected JSON payload:
    {
        "examples": ["010A", "325B", "245D"],
        "warehouse_context": {  // Optional
            "name": "Main Warehouse",
            "description": "Distribution center"
        }
    }
    
    Returns:
    {
        "success": true,
        "detection_result": {
            "detected_pattern": {...},
            "confidence": 0.95,
            "canonical_examples": [...],
            "analysis_summary": "...",
            "recommendations": [...]
        },
        "format_config": {...}  // Ready for database storage
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON payload required'}), 400
        
        examples = data.get('examples', [])
        warehouse_context = data.get('warehouse_context', {})
        
        # Validate examples
        if not examples:
            return jsonify({'error': 'Location examples are required'}), 400
        
        if not isinstance(examples, list):
            return jsonify({'error': 'Examples must be provided as an array'}), 400
        
        if len(examples) > 50:  # Reasonable limit
            return jsonify({'error': 'Too many examples provided (max 50)'}), 400
        
        # Clean examples
        cleaned_examples = []
        for example in examples:
            if isinstance(example, str) and example.strip():
                cleaned_examples.append(example.strip())
        
        if not cleaned_examples:
            return jsonify({'error': 'No valid location examples provided'}), 400
        
        # Import and use SmartFormatDetector
        from smart_format_detector import SmartFormatDetector
        
        detector = SmartFormatDetector()
        detection_result = detector.detect_format(cleaned_examples)
        
        # Create format configuration for storage
        format_config = detector.create_format_config(detection_result, warehouse_context)
        
        # Validate the configuration
        validation = detector.validate_format_config(format_config)
        
        response = {
            'success': True,
            'detection_result': detection_result,
            'format_config': format_config,
            'validation': validation,
            'input_summary': {
                'original_example_count': len(examples),
                'cleaned_example_count': len(cleaned_examples),
                'examples_used': cleaned_examples[:10]  # Show first 10 for reference
            }
        }
        
        # Add performance metadata
        response['metadata'] = {
            'detector_version': '1.0.0',
            'processing_timestamp': datetime.utcnow().isoformat(),
            'user_id': current_user.id,
            'patterns_analyzed': len(detection_result.get('all_patterns', []))
        }
        
        return jsonify(response), 200
    
    except ImportError as e:
        return jsonify({
            'error': 'SmartFormatDetector not available',
            'details': str(e)
        }), 500
    
    except Exception as e:
        current_app.logger.error(f"Format detection failed: {e}")
        return jsonify({
            'error': 'Format detection failed',
            'details': str(e)
        }), 500


@template_bp.route('/validate-format', methods=['POST'])
@token_required
def validate_location_format(current_user):
    """
    Validate a location format configuration
    
    This endpoint validates format configurations and provides feedback
    on compatibility with the canonical location system.
    
    Expected JSON payload:
    {
        "format_config": {...}  // Format configuration to validate
    }
    
    Returns:
    {
        "success": true,
        "validation": {
            "valid": true,
            "errors": [],
            "warnings": []
        },
        "compatibility_check": {...}
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON payload required'}), 400
        
        format_config = data.get('format_config')
        if not format_config:
            return jsonify({'error': 'format_config is required'}), 400
        
        # Import SmartFormatDetector for validation
        from smart_format_detector import SmartFormatDetector
        
        detector = SmartFormatDetector()
        validation = detector.validate_format_config(format_config)
        
        # Perform additional compatibility checks with canonical system
        from location_service import get_canonical_service
        canonical_service = get_canonical_service()
        
        compatibility_check = {
            'canonical_service_available': True,
            'pattern_type': format_config.get('pattern_type', 'unknown'),
            'can_convert_to_canonical': False,
            'sample_conversions': []
        }
        
        # Test conversion with sample examples if available
        examples = format_config.get('examples', [])
        if examples:
            sample_conversions = []
            for example in examples[:3]:  # Test first 3 examples
                try:
                    canonical = canonical_service.to_canonical(example)
                    sample_conversions.append({
                        'original': example,
                        'canonical': canonical,
                        'success': canonical != example or canonical in canonical_service.special_locations
                    })
                except Exception as e:
                    sample_conversions.append({
                        'original': example,
                        'canonical': None,
                        'success': False,
                        'error': str(e)
                    })
            
            compatibility_check['sample_conversions'] = sample_conversions
            compatibility_check['can_convert_to_canonical'] = any(conv['success'] for conv in sample_conversions)
        
        response = {
            'success': True,
            'validation': validation,
            'compatibility_check': compatibility_check,
            'metadata': {
                'validation_timestamp': datetime.utcnow().isoformat(),
                'user_id': current_user.id
            }
        }
        
        return jsonify(response), 200
    
    except ImportError as e:
        return jsonify({
            'error': 'Validation services not available',
            'details': str(e)
        }), 500
    
    except Exception as e:
        current_app.logger.error(f"Format validation failed: {e}")
        return jsonify({
            'error': 'Format validation failed',
            'details': str(e)
        }), 500


@template_bp.route('/format-evolution', methods=['GET'])
@token_required
def get_format_evolution_history(current_user):
    """
    Get format evolution history for user's templates
    
    Query parameters:
    - template_id: Filter by specific template (optional)
    - status: 'pending', 'approved', 'rejected', 'all' (default: 'pending')
    - limit: Number of results to return (default: 20)
    """
    try:
        from models import LocationFormatHistory, WarehouseTemplate
        
        template_id = request.args.get('template_id', type=int)
        status = request.args.get('status', 'pending')
        limit = min(int(request.args.get('limit', 20)), 100)
        
        # Build query
        query = LocationFormatHistory.query.join(WarehouseTemplate).filter(
            WarehouseTemplate.created_by == current_user.id,
            WarehouseTemplate.is_active == True
        )
        
        # Filter by template if specified
        if template_id:
            query = query.filter(LocationFormatHistory.warehouse_template_id == template_id)
        
        # Filter by status
        if status == 'pending':
            query = query.filter(
                LocationFormatHistory.user_confirmed == False,
                LocationFormatHistory.reviewed_at.is_(None)
            )
        elif status == 'approved':
            query = query.filter(
                LocationFormatHistory.user_confirmed == True,
                LocationFormatHistory.applied == True
            )
        elif status == 'rejected':
            query = query.filter(
                LocationFormatHistory.user_confirmed == False,
                LocationFormatHistory.reviewed_at.is_not(None)
            )
        # 'all' - no additional filter
        
        # Order by detection date (newest first) and apply limit
        evolutions = query.order_by(
            LocationFormatHistory.detected_at.desc()
        ).limit(limit).all()
        
        # Get summary statistics
        stats = {
            'total_evolutions': LocationFormatHistory.query.join(WarehouseTemplate).filter(
                WarehouseTemplate.created_by == current_user.id
            ).count(),
            'pending_evolutions': LocationFormatHistory.query.join(WarehouseTemplate).filter(
                WarehouseTemplate.created_by == current_user.id,
                LocationFormatHistory.user_confirmed == False,
                LocationFormatHistory.reviewed_at.is_(None)
            ).count()
        }
        
        return jsonify({
            'evolutions': [evolution.to_dict() for evolution in evolutions],
            'stats': stats,
            'query_info': {
                'template_id': template_id,
                'status': status,
                'limit': limit,
                'results_count': len(evolutions)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get format evolution history: {e}")
        return jsonify({
            'error': 'Failed to get format evolution history',
            'details': str(e)
        }), 500


@template_bp.route('/format-evolution/<int:evolution_id>/review', methods=['POST'])
@token_required
def review_format_evolution(current_user, evolution_id):
    """
    Review and approve/reject a format evolution
    
    Expected JSON payload:
    {
        "approved": true/false,
        "notes": "Optional user notes"
    }
    """
    try:
        from models import LocationFormatHistory, WarehouseTemplate
        from format_evolution_tracker import FormatEvolutionTracker
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON payload required'}), 400
        
        approved = data.get('approved')
        if approved is None:
            return jsonify({'error': 'approved field is required'}), 400
        
        # Get the evolution record
        evolution = LocationFormatHistory.query.get_or_404(evolution_id)
        
        # Check ownership - user must own the template
        if evolution.warehouse_template.created_by != current_user.id:
            return jsonify({'error': 'Access denied to this format evolution'}), 403
        
        # Check if already reviewed
        if evolution.reviewed_at is not None:
            return jsonify({
                'error': 'This format evolution has already been reviewed',
                'reviewed_at': evolution.reviewed_at.isoformat(),
                'reviewer': evolution.reviewer.username if evolution.reviewer else None
            }), 409
        
        # Apply the review decision
        tracker = FormatEvolutionTracker(evolution.warehouse_template)
        success = tracker.apply_evolution(evolution_id, current_user.id, bool(approved))
        
        if not success:
            return jsonify({'error': 'Failed to apply evolution decision'}), 500
        
        # Log the action
        action = 'approved' if approved else 'rejected'
        current_app.logger.info(f"User {current_user.id} {action} format evolution {evolution_id}")
        
        # Refresh the evolution object to get updated data
        db.session.refresh(evolution)
        
        response_data = {
            'message': f'Format evolution {action} successfully',
            'evolution': evolution.to_dict(),
            'action': action
        }
        
        # If approved and applied, include updated template info
        if approved and evolution.applied:
            response_data['template_updated'] = True
            response_data['new_format'] = evolution.warehouse_template.get_location_format_config()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to review format evolution {evolution_id}: {e}")
        return jsonify({
            'error': 'Failed to review format evolution',
            'details': str(e)
        }), 500


@template_bp.route('/format-evolution/check', methods=['POST'])
@token_required
def check_format_evolution(current_user):
    """
    Manually trigger format evolution check on location examples
    
    This is useful for testing or when users want to preview potential
    evolution before it's detected during inventory upload.
    
    Expected JSON payload:
    {
        "template_id": 123,
        "location_examples": ["010A", "325B", "RECV-01", ...]
    }
    """
    try:
        from models import WarehouseTemplate
        from format_evolution_tracker import FormatEvolutionTracker
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON payload required'}), 400
        
        template_id = data.get('template_id')
        location_examples = data.get('location_examples', [])
        
        if not template_id:
            return jsonify({'error': 'template_id is required'}), 400
        
        if not location_examples or not isinstance(location_examples, list):
            return jsonify({'error': 'location_examples must be a non-empty list'}), 400
        
        # Get the template
        template = WarehouseTemplate.query.get_or_404(template_id)
        
        # Check ownership
        if template.created_by != current_user.id:
            return jsonify({'error': 'Access denied to this template'}), 403
        
        # Run evolution check
        tracker = FormatEvolutionTracker(template, evolution_threshold=0.6)  # Lower threshold for manual check
        candidates = tracker.check_for_evolution(location_examples)
        
        # Format response
        evolution_preview = []
        for candidate in candidates:
            evolution_preview.append({
                'change_type': candidate.change_type,
                'description': candidate.change_description,
                'confidence_score': candidate.confidence_score,
                'affected_count': candidate.affected_count,
                'new_pattern_type': candidate.new_pattern_type,
                'sample_locations': candidate.sample_locations[:5]  # Show first 5
            })
        
        return jsonify({
            'template_id': template_id,
            'template_name': template.name,
            'current_format': template.get_location_format_config(),
            'evolution_candidates': evolution_preview,
            'candidates_found': len(candidates),
            'analysis_info': {
                'location_count': len(location_examples),
                'evolution_threshold': 0.6
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to check format evolution: {e}")
        return jsonify({
            'error': 'Failed to check format evolution',
            'details': str(e)
        }), 500


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