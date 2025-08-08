"""
Location Management API
Provides CRUD operations and bulk management for warehouse locations
"""

import json
from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_required
from sqlalchemy import and_, or_
from functools import wraps
from database import db
from models import Location, WarehouseConfig, User

# Create the location API blueprint
location_bp = Blueprint('location_api', __name__, url_prefix='/api/v1/locations')

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

@location_bp.route('', methods=['GET'])
@token_required
def get_locations(current_user):
    """
    Get all locations with optional filtering and pagination
    Query parameters:
    - warehouse_id: Filter by warehouse
    - location_type: Filter by type (RECEIVING, STORAGE, STAGING, DOCK)
    - zone: Filter by zone
    - is_active: Filter by active status
    - aisle_number: Filter by aisle
    - page: Page number (default: 1)
    - per_page: Items per page (default: 50)
    - search: Search in location codes and patterns
    """
    try:
        # Get query parameters
        warehouse_id = request.args.get('warehouse_id', 'DEFAULT')
        location_type = request.args.get('location_type')
        zone = request.args.get('zone')
        is_active = request.args.get('is_active')
        aisle_number = request.args.get('aisle_number')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)  # Max 100 per page
        
        # Build query
        query = Location.query.filter_by(warehouse_id=warehouse_id)
        
        if location_type:
            query = query.filter_by(location_type=location_type)
        
        if zone:
            query = query.filter_by(zone=zone)
            
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
            
        if aisle_number:
            query = query.filter_by(aisle_number=int(aisle_number))
            
        if search:
            search_filter = or_(
                Location.code.ilike(f'%{search}%'),
                Location.pattern.ilike(f'%{search}%'),
                Location.zone.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Order by hierarchy for storage locations, then by code
        query = query.order_by(
            Location.aisle_number.asc().nulls_last(),
            Location.rack_number.asc().nulls_last(),
            Location.position_number.asc().nulls_last(),
            Location.level.asc().nulls_last(),
            Location.code.asc()
        )
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        locations = pagination.items
        
        # Get summary statistics
        total_locations = Location.query.filter_by(warehouse_id=warehouse_id, is_active=True).count()
        storage_locations = Location.query.filter_by(
            warehouse_id=warehouse_id, 
            location_type='STORAGE', 
            is_active=True
        ).count()
        total_capacity = db.session.query(db.func.sum(Location.pallet_capacity)).filter_by(
            warehouse_id=warehouse_id, 
            is_active=True
        ).scalar() or 0
        
        return jsonify({
            'locations': [location.to_dict() for location in locations],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'summary': {
                'total_locations': total_locations,
                'storage_locations': storage_locations,
                'total_capacity': total_capacity,
                'warehouse_id': warehouse_id
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve locations: {str(e)}'}), 500

@location_bp.route('/<int:location_id>', methods=['GET'])
@token_required
def get_location(current_user, location_id):
    """Get a specific location by ID"""
    try:
        location = Location.query.get_or_404(location_id)
        return jsonify({'location': location.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'Location not found: {str(e)}'}), 404

@location_bp.route('', methods=['POST'])
@token_required
def create_location(current_user):
    """
    Create a new location
    Request body should contain location data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['code', 'location_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if location code already exists
        existing = Location.query.filter_by(code=data['code']).first()
        if existing:
            return jsonify({'error': f'Location with code {data["code"]} already exists'}), 409
        
        # Create location
        location = Location(
            code=data['code'],
            pattern=data.get('pattern'),
            location_type=data['location_type'],
            capacity=data.get('capacity', 1),
            zone=data.get('zone', 'GENERAL'),
            warehouse_id=data.get('warehouse_id', 'DEFAULT'),
            aisle_number=data.get('aisle_number'),
            rack_number=data.get('rack_number'),
            position_number=data.get('position_number'),
            level=data.get('level'),
            pallet_capacity=data.get('pallet_capacity', 1),
            created_by=current_user.id
        )
        
        # Set JSON fields if provided
        if 'allowed_products' in data:
            location.set_allowed_products(data['allowed_products'])
        
        if 'location_hierarchy' in data:
            location.set_location_hierarchy(data['location_hierarchy'])
            
        if 'special_requirements' in data:
            location.set_special_requirements(data['special_requirements'])
        
        db.session.add(location)
        db.session.commit()
        
        return jsonify({
            'message': 'Location created successfully',
            'location': location.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create location: {str(e)}'}), 500

@location_bp.route('/<int:location_id>', methods=['PUT'])
@token_required
def update_location(current_user, location_id):
    """Update an existing location"""
    try:
        location = Location.query.get_or_404(location_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if code is being changed and if it conflicts
        if 'code' in data and data['code'] != location.code:
            existing = Location.query.filter_by(code=data['code']).first()
            if existing:
                return jsonify({'error': f'Location with code {data["code"]} already exists'}), 409
        
        # Update fields
        updatable_fields = [
            'code', 'pattern', 'location_type', 'capacity', 'zone', 
            'warehouse_id', 'aisle_number', 'rack_number', 'position_number', 
            'level', 'pallet_capacity', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(location, field, data[field])
        
        # Update JSON fields
        if 'allowed_products' in data:
            location.set_allowed_products(data['allowed_products'])
        
        if 'location_hierarchy' in data:
            location.set_location_hierarchy(data['location_hierarchy'])
            
        if 'special_requirements' in data:
            location.set_special_requirements(data['special_requirements'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Location updated successfully',
            'location': location.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update location: {str(e)}'}), 500

@location_bp.route('/<int:location_id>', methods=['DELETE'])
@token_required
def delete_location(current_user, location_id):
    """Delete a location (soft delete by setting is_active=False)"""
    try:
        location = Location.query.get_or_404(location_id)
        
        # Soft delete by setting is_active to False
        location.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Location deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete location: {str(e)}'}), 500

@location_bp.route('/bulk', methods=['POST'])
@token_required
def bulk_create_locations(current_user):
    """
    Create multiple locations in bulk
    Request body: {'locations': [location_data_array]}
    """
    try:
        data = request.get_json()
        
        if not data or 'locations' not in data:
            return jsonify({'error': 'No locations data provided'}), 400
        
        locations_data = data['locations']
        if not isinstance(locations_data, list):
            return jsonify({'error': 'Locations must be an array'}), 400
        
        created_locations = []
        errors = []
        
        for i, location_data in enumerate(locations_data):
            try:
                # Validate required fields
                if 'code' not in location_data or 'location_type' not in location_data:
                    errors.append(f'Location {i + 1}: Missing required fields (code, location_type)')
                    continue
                
                # Check for duplicate codes
                existing = Location.query.filter_by(code=location_data['code']).first()
                if existing:
                    errors.append(f'Location {i + 1}: Code {location_data["code"]} already exists')
                    continue
                
                # Create location
                location = Location(
                    code=location_data['code'],
                    pattern=location_data.get('pattern'),
                    location_type=location_data['location_type'],
                    capacity=location_data.get('capacity', 1),
                    zone=location_data.get('zone', 'GENERAL'),
                    warehouse_id=location_data.get('warehouse_id', 'DEFAULT'),
                    aisle_number=location_data.get('aisle_number'),
                    rack_number=location_data.get('rack_number'),
                    position_number=location_data.get('position_number'),
                    level=location_data.get('level'),
                    pallet_capacity=location_data.get('pallet_capacity', 1),
                    created_by=current_user.id
                )
                
                # Set JSON fields if provided
                if 'allowed_products' in location_data:
                    location.set_allowed_products(location_data['allowed_products'])
                
                if 'location_hierarchy' in location_data:
                    location.set_location_hierarchy(location_data['location_hierarchy'])
                    
                if 'special_requirements' in location_data:
                    location.set_special_requirements(location_data['special_requirements'])
                
                db.session.add(location)
                created_locations.append(location)
                
            except Exception as e:
                errors.append(f'Location {i + 1}: {str(e)}')
        
        if created_locations:
            db.session.commit()
        
        return jsonify({
            'message': f'Bulk operation completed. Created {len(created_locations)} locations.',
            'created_count': len(created_locations),
            'error_count': len(errors),
            'errors': errors,
            'created_locations': [loc.to_dict() for loc in created_locations]
        }), 201 if created_locations else 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Bulk operation failed: {str(e)}'}), 500

@location_bp.route('/generate', methods=['POST'])
@token_required
def generate_warehouse_locations(current_user):
    """
    Generate locations from warehouse configuration
    Request body should contain warehouse structure parameters
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No configuration provided'}), 400
        
        # Required configuration parameters
        required_params = ['warehouse_id', 'num_aisles', 'racks_per_aisle', 'positions_per_rack']
        for param in required_params:
            if param not in data:
                return jsonify({'error': f'Missing required parameter: {param}'}), 400
        
        warehouse_id = data['warehouse_id']
        num_aisles = int(data['num_aisles'])
        racks_per_aisle = int(data['racks_per_aisle'])
        positions_per_rack = int(data['positions_per_rack'])
        levels_per_position = int(data.get('levels_per_position', 4))
        level_names = data.get('level_names', 'ABCD')
        pallet_capacity = int(data.get('pallet_capacity', 1))
        zone = data.get('zone', 'GENERAL')
        position_numbering_split = data.get('position_numbering_split', True)
        
        # Check if warehouse already has locations
        existing_count = Location.query.filter_by(warehouse_id=warehouse_id, is_active=True).count()
        if existing_count > 0 and not data.get('force_recreate', False):
            return jsonify({
                'error': f'Warehouse {warehouse_id} already has {existing_count} locations. Use force_recreate=true to override.'
            }), 409
        
        # Generate storage locations
        created_locations = []
        errors = []
        
        for aisle in range(1, num_aisles + 1):
            for rack in range(1, racks_per_aisle + 1):
                # Calculate position range for this rack
                if position_numbering_split and racks_per_aisle == 2:
                    # Split positions between racks: Rack 1 gets 1-50, Rack 2 gets 51-100
                    if rack == 1:
                        start_pos = 1
                        end_pos = positions_per_rack // 2
                    else:
                        start_pos = (positions_per_rack // 2) + 1
                        end_pos = positions_per_rack
                else:
                    # All racks have same position range
                    start_pos = 1
                    end_pos = positions_per_rack
                
                for position in range(start_pos, end_pos + 1):
                    for level_idx in range(levels_per_position):
                        level = level_names[level_idx] if level_idx < len(level_names) else f'L{level_idx + 1}'
                        
                        try:
                            # Create location using the class method
                            location = Location.create_from_structure(
                                warehouse_id=warehouse_id,
                                aisle_num=aisle,
                                rack_num=rack,
                                position_num=position,
                                level=level,
                                pallet_capacity=pallet_capacity,
                                zone=zone,
                                location_type='STORAGE',
                                created_by=current_user.id
                            )
                            
                            db.session.add(location)
                            created_locations.append(location)
                            
                        except Exception as e:
                            errors.append(f'Aisle {aisle}, Rack {rack}, Position {position:03d}{level}: {str(e)}')
        
        # Create special areas if specified
        special_areas = data.get('special_areas', [])
        for area in special_areas:
            try:
                location = Location(
                    code=area['code'],
                    location_type=area['type'],
                    capacity=area.get('capacity', 10),
                    pallet_capacity=area.get('capacity', 10),
                    zone=area.get('zone', 'RECEIVING'),
                    warehouse_id=warehouse_id,
                    created_by=current_user.id
                )
                
                if 'special_requirements' in area:
                    location.set_special_requirements(area['special_requirements'])
                
                db.session.add(location)
                created_locations.append(location)
                
            except Exception as e:
                errors.append(f'Special area {area.get("code", "unknown")}: {str(e)}')
        
        if created_locations:
            db.session.commit()
        
        # Calculate statistics
        total_storage = sum(1 for loc in created_locations if loc.location_type == 'STORAGE')
        total_capacity = sum(loc.pallet_capacity for loc in created_locations)
        
        return jsonify({
            'message': f'Generated {len(created_locations)} locations for warehouse {warehouse_id}',
            'created_count': len(created_locations),
            'storage_locations': total_storage,
            'total_capacity': total_capacity,
            'error_count': len(errors),
            'errors': errors
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to generate locations: {str(e)}'}), 500

@location_bp.route('/export', methods=['GET'])
@token_required
def export_locations(current_user):
    """Export locations data for download"""
    try:
        warehouse_id = request.args.get('warehouse_id', 'DEFAULT')
        format_type = request.args.get('format', 'json')  # json or csv
        
        locations = Location.query.filter_by(warehouse_id=warehouse_id, is_active=True).all()
        
        if format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'code', 'location_type', 'capacity', 'zone', 'aisle_number', 
                'rack_number', 'position_number', 'level', 'pallet_capacity'
            ])
            
            # Data
            for location in locations:
                writer.writerow([
                    location.code,
                    location.location_type,
                    location.capacity,
                    location.zone,
                    location.aisle_number or '',
                    location.rack_number or '',
                    location.position_number or '',
                    location.level or '',
                    location.pallet_capacity
                ])
            
            from flask import make_response
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=warehouse_{warehouse_id}_locations.csv'
            return response
            
        else:  # JSON format
            return jsonify({
                'warehouse_id': warehouse_id,
                'export_date': str(datetime.utcnow()),
                'total_locations': len(locations),
                'locations': [location.to_dict() for location in locations]
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@location_bp.route('/validate', methods=['POST'])
@token_required
def validate_locations(current_user):
    """Validate location data before creation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        locations_data = data.get('locations', [])
        validation_results = []
        
        for i, location_data in enumerate(locations_data):
            result = {
                'index': i,
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check required fields
            if 'code' not in location_data:
                result['errors'].append('Missing required field: code')
            elif Location.query.filter_by(code=location_data['code']).first():
                result['errors'].append(f'Location code {location_data["code"]} already exists')
            
            if 'location_type' not in location_data:
                result['errors'].append('Missing required field: location_type')
            
            # Check capacity values
            capacity = location_data.get('capacity', 1)
            if capacity < 1 or capacity > 100:
                result['warnings'].append('Unusual capacity value (should be 1-100)')
            
            # Check hierarchical structure consistency
            hierarchy_fields = ['aisle_number', 'rack_number', 'position_number', 'level']
            has_hierarchy = any(field in location_data for field in hierarchy_fields)
            
            if has_hierarchy:
                missing_hierarchy = [field for field in hierarchy_fields if field not in location_data]
                if missing_hierarchy:
                    result['warnings'].append(f'Incomplete hierarchy structure. Missing: {missing_hierarchy}')
            
            result['valid'] = len(result['errors']) == 0
            validation_results.append(result)
        
        valid_count = sum(1 for r in validation_results if r['valid'])
        
        return jsonify({
            'validation_results': validation_results,
            'summary': {
                'total_locations': len(locations_data),
                'valid_locations': valid_count,
                'invalid_locations': len(locations_data) - valid_count,
                'overall_valid': valid_count == len(locations_data)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500

# Register error handlers
@location_bp.errorhandler(404)
def location_not_found(error):
    return jsonify({'error': 'Location not found'}), 404

@location_bp.errorhandler(409)
def location_conflict(error):
    return jsonify({'error': 'Location already exists'}), 409

@location_bp.errorhandler(500)
def location_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500