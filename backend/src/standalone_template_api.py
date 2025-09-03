"""
Standalone Template Creation API
Enables users to create warehouse templates without requiring existing warehouse configurations
"""

import json
import string
import random
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import and_, or_
from functools import wraps
from database import db
from models import WarehouseTemplate
from core_models import User

# Create the standalone template API blueprint
standalone_template_bp = Blueprint('standalone_template_api', __name__, url_prefix='/api/v1/standalone-templates')

# Auth decorator
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

def generate_template_code(name, num_aisles, racks_per_aisle):
    """Generate a unique template code"""
    # Create prefix from name or use generic
    if name:
        name_part = ''.join(c.upper() for c in name if c.isalpha())[:3]
        if len(name_part) < 3:
            name_part = name_part.ljust(3, 'X')
    else:
        name_part = 'TPL'
    
    # Structure part
    structure_part = f"{num_aisles}A{racks_per_aisle}R"
    
    # Random suffix
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    return f"{name_part}-{structure_part}-{suffix}"

@standalone_template_bp.route('/create', methods=['POST'])
@token_required
def create_standalone_template(current_user):
    """
    Create a new warehouse template from scratch (without existing warehouse config)
    """
    try:
        data = request.get_json()
        
        # Required fields
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Template name is required'}), 400
            
        # Structure configuration
        num_aisles = data.get('num_aisles', 4)
        racks_per_aisle = data.get('racks_per_aisle', 2)
        positions_per_rack = data.get('positions_per_rack', 50)
        levels_per_position = data.get('levels_per_position', 4)
        
        # Validate structure
        if any(val <= 0 for val in [num_aisles, racks_per_aisle, positions_per_rack, levels_per_position]):
            return jsonify({'error': 'All structure values must be greater than 0'}), 400
            
        # Optional fields
        description = data.get('description', '')
        level_names = data.get('level_names', 'ABCD')[:levels_per_position]
        default_pallet_capacity = max(1, data.get('default_pallet_capacity', 1))
        bidimensional_racks = data.get('bidimensional_racks', False)
        
        # Special areas (optional)
        receiving_areas = data.get('receiving_areas', [])
        staging_areas = data.get('staging_areas', [])
        dock_areas = data.get('dock_areas', [])
        
        # Enhanced privacy fields (if using enhanced system)
        visibility = data.get('visibility', 'PRIVATE')  # PRIVATE, COMPANY, PUBLIC
        category = data.get('category', 'CUSTOM')
        industry = data.get('industry', '')
        tags = data.get('tags', [])
        
        # Smart Location Format Configuration
        format_config = data.get('format_config')
        format_pattern_name = data.get('format_pattern_name', '')
        format_examples = data.get('format_examples', [])
        format_confidence = 1.0  # Set high confidence for user-configured formats
        
        # Legacy compatibility
        is_public = (visibility == 'PUBLIC')
        
        # Generate unique template code
        template_code = generate_template_code(name, num_aisles, racks_per_aisle)
        
        # Ensure template code is unique
        attempts = 0
        while WarehouseTemplate.query.filter_by(template_code=template_code).first() and attempts < 10:
            template_code = generate_template_code(name, num_aisles, racks_per_aisle)
            attempts += 1
            
        if attempts >= 10:
            return jsonify({'error': 'Failed to generate unique template code'}), 500
        
        # Create the template
        template = WarehouseTemplate(
            name=name,
            description=description,
            template_code=template_code,
            num_aisles=num_aisles,
            racks_per_aisle=racks_per_aisle,
            positions_per_rack=positions_per_rack,
            levels_per_position=levels_per_position,
            level_names=level_names,
            default_pallet_capacity=default_pallet_capacity,
            bidimensional_racks=bidimensional_racks,
            # Special areas as JSON
            receiving_areas_template=json.dumps(receiving_areas) if receiving_areas else None,
            staging_areas_template=json.dumps(staging_areas) if staging_areas else None,
            dock_areas_template=json.dumps(dock_areas) if dock_areas else None,
            # Smart Location Format Configuration
            location_format_config=json.dumps(format_config) if format_config else None,
            format_confidence=format_confidence if format_config else 0.0,
            format_examples=json.dumps(format_examples) if format_examples else None,
            format_learned_date=datetime.utcnow() if format_config else None,
            # Privacy settings
            is_public=is_public,
            created_by=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            usage_count=0
        )
        
        # Add enhanced fields if available
        if hasattr(template, 'visibility'):
            template.visibility = visibility
        if hasattr(template, 'template_category'):
            template.template_category = category
        if hasattr(template, 'industry_category'):
            template.industry_category = industry
        if hasattr(template, 'tags'):
            template.tags = json.dumps(tags) if tags else None
        
        db.session.add(template)
        db.session.commit()
        
        # Return the created template
        template_dict = {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'template_code': template.template_code,
            'num_aisles': template.num_aisles,
            'racks_per_aisle': template.racks_per_aisle,
            'positions_per_rack': template.positions_per_rack,
            'levels_per_position': template.levels_per_position,
            'level_names': template.level_names,
            'default_pallet_capacity': template.default_pallet_capacity,
            'bidimensional_racks': template.bidimensional_racks,
            'is_public': template.is_public,
            'visibility': getattr(template, 'visibility', 'PRIVATE'),
            'category': getattr(template, 'template_category', 'CUSTOM'),
            'industry': getattr(template, 'industry_category', ''),
            'tags': json.loads(getattr(template, 'tags', '[]') or '[]'),
            'created_by': template.created_by,
            'creator_username': current_user.username,
            'created_at': template.created_at.isoformat(),
            'updated_at': template.updated_at.isoformat(),
            'usage_count': template.usage_count,
            # Calculate totals
            'total_storage_locations': num_aisles * racks_per_aisle * positions_per_rack * levels_per_position,
            'total_capacity': num_aisles * racks_per_aisle * positions_per_rack * levels_per_position * default_pallet_capacity
        }
        
        return jsonify({
            'message': 'Template created successfully',
            'template': template_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating standalone template: {str(e)}")
        return jsonify({'error': f'Failed to create template: {str(e)}'}), 500

@standalone_template_bp.route('/validate', methods=['POST'])
@token_required  
def validate_template_data(current_user):
    """
    Validate template configuration without creating it
    """
    try:
        data = request.get_json()
        
        errors = []
        warnings = []
        
        # Validate required fields
        if not data.get('name', '').strip():
            errors.append('Template name is required')
            
        # Validate structure
        num_aisles = data.get('num_aisles', 0)
        racks_per_aisle = data.get('racks_per_aisle', 0)
        positions_per_rack = data.get('positions_per_rack', 0)
        levels_per_position = data.get('levels_per_position', 0)
        
        if num_aisles <= 0:
            errors.append('Number of aisles must be greater than 0')
        if racks_per_aisle <= 0:
            errors.append('Racks per aisle must be greater than 0')
        if positions_per_rack <= 0:
            errors.append('Positions per rack must be greater than 0')
        if levels_per_position <= 0:
            errors.append('Levels per position must be greater than 0')
            
        # Calculate and validate totals
        total_locations = num_aisles * racks_per_aisle * positions_per_rack * levels_per_position
        if total_locations > 100000:  # Reasonable limit
            warnings.append(f'This template will create {total_locations:,} locations, which may take time to generate')
        elif total_locations > 50000:
            warnings.append(f'Large template: {total_locations:,} locations will be created')
            
        # Validate level names
        level_names = data.get('level_names', 'ABCD')
        if len(level_names) < levels_per_position:
            warnings.append(f'Level names "{level_names}" has fewer characters than levels ({levels_per_position})')
            
        # Validate capacity
        default_pallet_capacity = data.get('default_pallet_capacity', 1)
        if default_pallet_capacity < 1:
            errors.append('Default pallet capacity must be at least 1')
        elif default_pallet_capacity > 10:
            warnings.append(f'High capacity of {default_pallet_capacity} pallets per level')
            
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'calculated_totals': {
                'storage_locations': total_locations,
                'storage_capacity': total_locations * default_pallet_capacity,
                'estimated_setup_time_minutes': max(1, total_locations // 1000)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error validating template data: {str(e)}")
        return jsonify({'error': 'Validation failed'}), 500

@standalone_template_bp.route('/generate-code', methods=['POST'])
@token_required
def generate_preview_code(current_user):
    """
    Generate a preview of what the template code would be (without creating template)
    """
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        num_aisles = data.get('num_aisles', 4)
        racks_per_aisle = data.get('racks_per_aisle', 2)
        
        code = generate_template_code(name, num_aisles, racks_per_aisle)
        
        # Check if code already exists
        exists = WarehouseTemplate.query.filter_by(template_code=code).first() is not None
        
        return jsonify({
            'template_code': code,
            'already_exists': exists,
            'format_explanation': {
                'prefix': f"First 3 letters from name or 'TPL'",
                'structure': f"{num_aisles}A{racks_per_aisle}R (Aisles x Racks)",
                'suffix': "4-character random identifier"
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating preview code: {str(e)}")
        return jsonify({'error': 'Failed to generate code preview'}), 500

@standalone_template_bp.route('/categories', methods=['GET'])
@token_required
def get_template_categories(current_user):
    """
    Get available template categories and industries
    """
    try:
        categories = [
            {'value': 'MANUFACTURING', 'label': 'Manufacturing', 'description': 'Industrial production warehouses'},
            {'value': 'RETAIL', 'label': 'Retail Distribution', 'description': 'Retail distribution centers'},
            {'value': 'FOOD_BEVERAGE', 'label': 'Food & Beverage', 'description': 'Cold chain and food storage'},
            {'value': 'PHARMA', 'label': 'Pharmaceutical', 'description': 'Controlled environment storage'},
            {'value': 'AUTOMOTIVE', 'label': 'Automotive', 'description': 'Parts and assembly storage'},
            {'value': 'ECOMMERCE', 'label': 'E-commerce', 'description': 'Fulfillment centers'},
            {'value': 'CUSTOM', 'label': 'Custom', 'description': 'User-defined template'}
        ]
        
        industries = [
            'Electronics', 'Textiles', 'Chemicals', 'Machinery', 'Consumer Goods',
            'Aerospace', 'Medical Devices', 'Books & Media', 'Furniture', 'Other'
        ]
        
        return jsonify({
            'categories': categories,
            'industries': industries
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting categories: {str(e)}")
        return jsonify({'error': 'Failed to get categories'}), 500