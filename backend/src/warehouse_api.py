"""
Warehouse Configuration API
Handles warehouse setup wizard and configuration management
"""

import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import and_, or_
from functools import wraps
from database import db
from models import WarehouseConfig, WarehouseTemplate, Location, User

# Create the warehouse configuration API blueprint
warehouse_bp = Blueprint('warehouse_api', __name__, url_prefix='/api/v1/warehouse')

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

@warehouse_bp.route('/config', methods=['GET'])
@token_required
def get_warehouse_config(current_user):
    """Get current warehouse configuration"""
    try:
        warehouse_id = request.args.get('warehouse_id', 'DEFAULT')
        config = WarehouseConfig.query.filter_by(
            warehouse_id=warehouse_id, 
            is_active=True
        ).first()
        
        if not config:
            return jsonify({'error': 'No warehouse configuration found'}), 404
        
        return jsonify({'config': config.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve configuration: {str(e)}'}), 500

@warehouse_bp.route('/config', methods=['POST'])
@token_required
def create_warehouse_config(current_user):
    """Create new warehouse configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No configuration data provided'}), 400
        
        # Validate required fields
        required_fields = ['warehouse_id', 'warehouse_name', 'num_aisles', 'racks_per_aisle', 'positions_per_rack']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if warehouse config already exists
        existing = WarehouseConfig.query.filter_by(warehouse_id=data['warehouse_id']).first()
        if existing:
            return jsonify({'error': f'Configuration for warehouse {data["warehouse_id"]} already exists'}), 409
        
        # Create configuration
        config = WarehouseConfig(
            warehouse_id=data['warehouse_id'],
            warehouse_name=data['warehouse_name'],
            num_aisles=int(data['num_aisles']),
            racks_per_aisle=int(data['racks_per_aisle']),
            positions_per_rack=int(data['positions_per_rack']),
            levels_per_position=int(data.get('levels_per_position', 4)),
            level_names=data.get('level_names', 'ABCD'),
            default_pallet_capacity=int(data.get('default_pallet_capacity', 1)),
            bidimensional_racks=data.get('bidimensional_racks', False),
            default_zone=data.get('default_zone', 'GENERAL'),
            position_numbering_start=int(data.get('position_numbering_start', 1)),
            position_numbering_split=data.get('position_numbering_split', True),
            created_by=current_user.id
        )
        
        # Set special areas if provided
        if 'receiving_areas' in data:
            config.set_receiving_areas(data['receiving_areas'])
        
        if 'staging_areas' in data:
            config.set_staging_areas(data['staging_areas'])
            
        if 'dock_areas' in data:
            config.set_dock_areas(data['dock_areas'])
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify({
            'message': 'Warehouse configuration created successfully',
            'config': config.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create configuration: {str(e)}'}), 500

@warehouse_bp.route('/config/<int:config_id>', methods=['PUT'])
@token_required
def update_warehouse_config(current_user, config_id):
    """Update existing warehouse configuration"""
    try:
        config = WarehouseConfig.query.get_or_404(config_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update basic fields
        updatable_fields = [
            'warehouse_name', 'num_aisles', 'racks_per_aisle', 'positions_per_rack',
            'levels_per_position', 'level_names', 'default_pallet_capacity',
            'bidimensional_racks', 'default_zone', 'position_numbering_start',
            'position_numbering_split'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field in ['num_aisles', 'racks_per_aisle', 'positions_per_rack', 
                           'levels_per_position', 'default_pallet_capacity', 'position_numbering_start']:
                    setattr(config, field, int(data[field]))
                elif field == 'bidimensional_racks':
                    setattr(config, field, bool(data[field]))
                else:
                    setattr(config, field, data[field])
        
        # Update special areas
        if 'receiving_areas' in data:
            config.set_receiving_areas(data['receiving_areas'])
        
        if 'staging_areas' in data:
            config.set_staging_areas(data['staging_areas'])
            
        if 'dock_areas' in data:
            config.set_dock_areas(data['dock_areas'])
        
        config.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'config': config.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update configuration: {str(e)}'}), 500

@warehouse_bp.route('/setup', methods=['POST'])
@token_required
def setup_warehouse(current_user):
    """
    Complete warehouse setup wizard - creates config and generates locations
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No setup data provided'}), 400
        
        warehouse_id = data.get('warehouse_id', f'WAREHOUSE_{current_user.id}_{int(datetime.utcnow().timestamp())}')
        
        # Step 1: Create or update warehouse configuration
        config_data = data.get('configuration', {})
        config_data['warehouse_id'] = warehouse_id
        
        # Check if config already exists
        existing_config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
        
        if existing_config and not data.get('force_recreate', False):
            return jsonify({
                'error': f'Warehouse {warehouse_id} already exists. Use force_recreate=true to override.'
            }), 409
        
        if existing_config:
            # Update existing config
            config = existing_config
            for field, value in config_data.items():
                if hasattr(config, field):
                    setattr(config, field, value)
            config.updated_at = datetime.utcnow()
        else:
            # Create new config
            config = WarehouseConfig(
                warehouse_id=warehouse_id,
                warehouse_name=config_data.get('warehouse_name', f'Warehouse {warehouse_id}'),
                num_aisles=int(config_data.get('num_aisles', 4)),
                racks_per_aisle=int(config_data.get('racks_per_aisle', 2)),
                positions_per_rack=int(config_data.get('positions_per_rack', 50)),
                levels_per_position=int(config_data.get('levels_per_position', 4)),
                level_names=config_data.get('level_names', 'ABCD'),
                default_pallet_capacity=int(config_data.get('default_pallet_capacity', 1)),
                bidimensional_racks=config_data.get('bidimensional_racks', False),
                default_zone=config_data.get('default_zone', 'GENERAL'),
                position_numbering_start=int(config_data.get('position_numbering_start', 1)),
                position_numbering_split=config_data.get('position_numbering_split', True),
                created_by=current_user.id
            )
            
            db.session.add(config)
        
        # Set special areas
        receiving_areas = data.get('receiving_areas', [
            {'code': 'RECEIVING', 'type': 'RECEIVING', 'capacity': 10, 'zone': 'DOCK'}
        ])
        config.set_receiving_areas(receiving_areas)
        
        if 'staging_areas' in data:
            config.set_staging_areas(data['staging_areas'])
            
        if 'dock_areas' in data:
            config.set_dock_areas(data['dock_areas'])
        
        db.session.commit()
        
        # Step 2: Generate locations if requested
        generate_locations = data.get('generate_locations', True)
        created_locations = []
        
        if generate_locations:
            # Clear existing locations if force recreate
            if data.get('force_recreate', False):
                Location.query.filter_by(warehouse_id=warehouse_id).delete()
            
            # Generate storage locations
            for aisle in range(1, config.num_aisles + 1):
                for rack in range(1, config.racks_per_aisle + 1):
                    # Calculate position range for this rack
                    if config.position_numbering_split and config.racks_per_aisle == 2:
                        if rack == 1:
                            start_pos = config.position_numbering_start
                            end_pos = config.positions_per_rack // 2
                        else:
                            start_pos = (config.positions_per_rack // 2) + 1
                            end_pos = config.positions_per_rack
                    else:
                        start_pos = config.position_numbering_start
                        end_pos = config.positions_per_rack
                    
                    for position in range(start_pos, end_pos + 1):
                        for level_idx in range(config.levels_per_position):
                            level = config.level_names[level_idx] if level_idx < len(config.level_names) else f'L{level_idx + 1}'
                            
                            location = Location.create_from_structure(
                                warehouse_id=warehouse_id,
                                aisle_num=aisle,
                                rack_num=rack,
                                position_num=position,
                                level=level,
                                pallet_capacity=config.default_pallet_capacity,
                                zone=config.default_zone,
                                location_type='STORAGE',
                                created_by=current_user.id
                            )
                            
                            db.session.add(location)
                            created_locations.append(location)
            
            # Create special areas
            for area in receiving_areas:
                location = Location(
                    code=area['code'],
                    location_type=area['type'],
                    capacity=area.get('capacity', 10),
                    pallet_capacity=area.get('capacity', 10),
                    zone=area.get('zone', 'DOCK'),
                    warehouse_id=warehouse_id,
                    created_by=current_user.id
                )
                
                if 'special_requirements' in area:
                    location.set_special_requirements(area['special_requirements'])
                
                db.session.add(location)
                created_locations.append(location)
            
            # Create staging areas
            for area in config.get_staging_areas():
                location = Location(
                    code=area['code'],
                    location_type=area['type'],
                    capacity=area.get('capacity', 5),
                    pallet_capacity=area.get('capacity', 5),
                    zone=area.get('zone', 'STAGING'),
                    warehouse_id=warehouse_id,
                    created_by=current_user.id
                )
                
                db.session.add(location)
                created_locations.append(location)
            
            db.session.commit()
        
        # Step 3: Create template if requested
        create_template = data.get('create_template', False)
        template = None
        
        if create_template:
            template_name = data.get('template_name', f'{config.warehouse_name} Template')
            template_description = data.get('template_description')
            is_public = data.get('template_is_public', False)
            
            template = WarehouseTemplate.create_from_config(
                config=config,
                name=template_name,
                description=template_description,
                is_public=is_public
            )
            
            db.session.add(template)
            db.session.commit()
        
        # Prepare response
        response_data = {
            'message': 'Warehouse setup completed successfully',
            'warehouse_id': warehouse_id,
            'configuration': config.to_dict(),
            'locations_created': len(created_locations),
            'total_capacity': config.calculate_total_capacity()
        }
        
        if template:
            response_data['template'] = template.to_dict()
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Warehouse setup failed: {str(e)}'}), 500

@warehouse_bp.route('/validate', methods=['POST'])
@token_required
def validate_warehouse_config(current_user):
    """Validate warehouse configuration before setup"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'calculations': {}
        }
        
        # Validate required fields
        required_fields = ['num_aisles', 'racks_per_aisle', 'positions_per_rack']
        for field in required_fields:
            if field not in data:
                validation_result['errors'].append(f'Missing required field: {field}')
            elif not isinstance(data[field], int) or data[field] < 1:
                validation_result['errors'].append(f'{field} must be a positive integer')
        
        if validation_result['errors']:
            validation_result['valid'] = False
            return jsonify(validation_result), 400
        
        # Calculate warehouse statistics
        num_aisles = int(data['num_aisles'])
        racks_per_aisle = int(data['racks_per_aisle'])
        positions_per_rack = int(data['positions_per_rack'])
        levels_per_position = int(data.get('levels_per_position', 4))
        pallet_capacity = int(data.get('default_pallet_capacity', 1))
        
        total_storage_locations = num_aisles * racks_per_aisle * positions_per_rack * levels_per_position
        total_storage_capacity = total_storage_locations * pallet_capacity
        
        # Add receiving areas capacity
        receiving_areas = data.get('receiving_areas', [])
        receiving_capacity = sum(area.get('capacity', 0) for area in receiving_areas)
        
        total_capacity = total_storage_capacity + receiving_capacity
        
        validation_result['calculations'] = {
            'total_storage_locations': total_storage_locations,
            'total_storage_capacity': total_storage_capacity,
            'receiving_capacity': receiving_capacity,
            'total_capacity': total_capacity,
            'estimated_setup_time_minutes': max(1, total_storage_locations // 1000)  # Rough estimate
        }
        
        # Validate reasonable limits
        if total_storage_locations > 50000:
            validation_result['warnings'].append('Very large warehouse (50k+ locations). Setup may take several minutes.')
        elif total_storage_locations > 10000:
            validation_result['warnings'].append('Large warehouse (10k+ locations). Setup may take 1-2 minutes.')
        
        if num_aisles > 20:
            validation_result['warnings'].append('Many aisles (20+). Consider if this matches your actual layout.')
        
        if positions_per_rack > 200:
            validation_result['warnings'].append('High positions per rack (200+). Verify this is correct.')
        
        # Validate level names
        level_names = data.get('level_names', 'ABCD')
        if len(level_names) < levels_per_position:
            validation_result['warnings'].append(f'Level names "{level_names}" shorter than levels_per_position ({levels_per_position})')
        
        return jsonify(validation_result), 200
        
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500

@warehouse_bp.route('/preview', methods=['POST'])
@token_required
def preview_warehouse_setup(current_user):
    """Preview warehouse setup without creating anything"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract configuration
        num_aisles = int(data.get('num_aisles', 4))
        racks_per_aisle = int(data.get('racks_per_aisle', 2))
        positions_per_rack = int(data.get('positions_per_rack', 50))
        levels_per_position = int(data.get('levels_per_position', 4))
        level_names = data.get('level_names', 'ABCD')
        position_numbering_split = data.get('position_numbering_split', True)
        
        # Generate sample location codes
        sample_locations = []
        
        # Sample from first aisle, first rack
        aisle = 1
        rack = 1
        
        if position_numbering_split and racks_per_aisle == 2:
            start_pos = 1
            end_pos = min(5, positions_per_rack // 2)  # Show first 5 positions
        else:
            start_pos = 1
            end_pos = min(5, positions_per_rack)
        
        for position in range(start_pos, end_pos + 1):
            for level_idx in range(min(levels_per_position, 2)):  # Show first 2 levels
                level = level_names[level_idx] if level_idx < len(level_names) else f'L{level_idx + 1}'
                code = f"{position:03d}{level}"
                full_address = f"Aisle {aisle}, Rack {rack}, Position {position:03d}{level}"
                
                sample_locations.append({
                    'code': code,
                    'full_address': full_address,
                    'aisle': aisle,
                    'rack': rack,
                    'position': position,
                    'level': level
                })
        
        # Calculate totals
        total_storage_locations = num_aisles * racks_per_aisle * positions_per_rack * levels_per_position
        
        # Add special areas
        receiving_areas = data.get('receiving_areas', [])
        staging_areas = data.get('staging_areas', [])
        
        preview = {
            'warehouse_structure': {
                'num_aisles': num_aisles,
                'racks_per_aisle': racks_per_aisle,
                'positions_per_rack': positions_per_rack,
                'levels_per_position': levels_per_position,
                'level_names': level_names
            },
            'sample_locations': sample_locations,
            'totals': {
                'storage_locations': total_storage_locations,
                'receiving_areas': len(receiving_areas),
                'staging_areas': len(staging_areas),
                'total_locations': total_storage_locations + len(receiving_areas) + len(staging_areas)
            },
            'special_areas': {
                'receiving': receiving_areas,
                'staging': staging_areas
            }
        }
        
        return jsonify({'preview': preview}), 200
        
    except Exception as e:
        return jsonify({'error': f'Preview generation failed: {str(e)}'}), 500

@warehouse_bp.route('/list', methods=['GET'])
@token_required
def list_warehouses(current_user):
    """List all warehouse configurations for the current user"""
    try:
        configs = WarehouseConfig.query.filter_by(
            created_by=current_user.id, 
            is_active=True
        ).order_by(WarehouseConfig.created_at.desc()).all()
        
        warehouses = []
        for config in configs:
            # Get location count for this warehouse
            location_count = Location.query.filter_by(
                warehouse_id=config.warehouse_id, 
                is_active=True
            ).count()
            
            warehouse_info = config.to_dict()
            warehouse_info['location_count'] = location_count
            warehouses.append(warehouse_info)
        
        return jsonify({
            'warehouses': warehouses,
            'total_count': len(warehouses)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list warehouses: {str(e)}'}), 500

# Register error handlers
@warehouse_bp.errorhandler(404)
def config_not_found(error):
    return jsonify({'error': 'Warehouse configuration not found'}), 404

@warehouse_bp.errorhandler(409)
def config_conflict(error):
    return jsonify({'error': 'Warehouse configuration already exists'}), 409

@warehouse_bp.errorhandler(500)
def warehouse_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500