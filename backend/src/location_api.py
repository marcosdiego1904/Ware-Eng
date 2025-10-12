"""
Location Management API
Provides CRUD operations and bulk management for warehouse locations
"""

import json
import re
from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_required
from sqlalchemy import and_, or_
from functools import wraps
from database import db
from models import Location, WarehouseConfig
from core_models import User
from virtual_compatibility_layer import get_compatibility_manager

# Create the location API blueprint
location_bp = Blueprint('location_api', __name__, url_prefix='/api/v1/locations')

def _normalize_location_code(location_code: str) -> str:
    """
    Normalize location codes by removing user prefixes and standardizing format
    
    Examples:
    - "ALICE_A-01-01A" -> "A-01-01A"
    - "USER_BOB_001A" -> "001A" 
    - "WH01_RECEIVING" -> "RECEIVING"
    - "A-01-01A" -> "A-01-01A" (unchanged)
    """
    if not location_code:
        return location_code
        
    code = str(location_code).strip().upper()
    
    # Remove common warehouse/user prefixes
    prefixes_to_remove = [
        # User-specific warehouse prefixes (USER_USERNAME_)
        r'^USER_[A-Z0-9]+_',
        # Simplified user prefixes (USERNAME_)  
        r'^[A-Z]{2,10}_',  # 2-10 letter username prefixes
        # Warehouse prefixes (WH01_, WH_)
        r'^WH\d*_',
        # Default warehouse prefixes
        r'^DEFAULT_',
    ]
    
    for prefix_pattern in prefixes_to_remove:
        code = re.sub(prefix_pattern, '', code)
        
    return code

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
    Get all locations with support for both physical and virtual locations
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
        
        # Only log on first page requests to reduce spam
        if page == 1:
            print(f"[LOCATION_API] Request for warehouse_id={warehouse_id}, page={page}, per_page={per_page}")
        
        # Get compatibility manager to handle virtual/physical locations
        compat_manager = get_compatibility_manager()
        
        # Check if this is a virtual warehouse
        is_virtual = compat_manager.is_virtual_warehouse(warehouse_id)
        if page == 1:
            print(f"[LOCATION_API] Warehouse {warehouse_id} is virtual: {is_virtual}")
        
        if is_virtual:
            return _get_virtual_locations(current_user, warehouse_id, location_type, zone, 
                                        is_active, aisle_number, search, page, per_page)
        else:
            return _get_physical_locations(current_user, warehouse_id, location_type, zone, 
                                         is_active, aisle_number, search, page, per_page)
        
        
    except Exception as e:
        print(f"[LOCATION_API] Error: {str(e)}")
        return jsonify({'error': f'Failed to retrieve locations: {str(e)}'}), 500

def _get_physical_locations(current_user, warehouse_id, location_type, zone, is_active, aisle_number, search, page, per_page):
    """Handle physical location queries (original database logic)"""
    try:
        if page == 1:
            print(f"[LOCATION_API] Getting physical locations for warehouse {warehouse_id}")
        
        # Build query - CRITICAL: Filter by user to ensure data isolation
        query = Location.query.filter_by(
            warehouse_id=warehouse_id,
            created_by=current_user.id  # Essential: Only show user's own locations
        )
        
        if location_type:
            query = query.filter_by(location_type=location_type)
        
        if zone:
            query = query.filter_by(zone=zone)
            
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
            
        if aisle_number:
            query = query.filter_by(aisle_number=int(aisle_number))
            
        if search:
            # Enhanced search with location code normalization
            search_term = search.strip()
            
            # Standard search filters
            search_filter = or_(
                Location.code.ilike(f'%{search_term}%'),
                Location.pattern.ilike(f'%{search_term}%'),
                Location.zone.ilike(f'%{search_term}%')
            )
            
            # Add normalized code matching for better search results
            normalized_search = _normalize_location_code(search_term)
            
            if normalized_search != search_term:
                # Get all locations and check normalized matches
                all_locations = Location.query.filter_by(
                    warehouse_id=warehouse_id,
                    created_by=current_user.id
                ).all()
                
                matching_ids = []
                for loc in all_locations:
                    normalized_db_code = _normalize_location_code(loc.code)
                    if (normalized_search in normalized_db_code or 
                        normalized_db_code in normalized_search or
                        normalized_search == normalized_db_code):
                        matching_ids.append(loc.id)
                
                if matching_ids:
                    search_filter = or_(search_filter, Location.id.in_(matching_ids))
            
            query = query.filter(search_filter)
        
        # Order by location type
        query = query.order_by(
            db.case(
                (Location.location_type == 'RECEIVING', 1),
                (Location.location_type == 'STAGING', 2), 
                (Location.location_type == 'DOCK', 3),
                (Location.location_type == 'STORAGE', 4),
                else_=5
            ).asc(),
            Location.aisle_number.asc().nulls_last(),
            Location.rack_number.asc().nulls_last(),
            Location.position_number.asc().nulls_last(),
            Location.level.asc().nulls_last(),
            Location.code.asc()
        )
        
        # Debug info (only for first page to reduce spam)
        if page == 1:
            try:
                total_for_warehouse = Location.query.filter_by(
                    warehouse_id=warehouse_id,
                    created_by=current_user.id
                ).count()
                print(f"DEBUG: Total physical locations in warehouse {warehouse_id} for user {current_user.id}: {total_for_warehouse}")
            except Exception as debug_error:
                # CRITICAL FIX: Debug query failed - rollback transaction and continue
                print(f"DEBUG: Count query failed (non-critical): {str(debug_error)}")
                db.session.rollback()
                # Continue with main query despite debug failure
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        locations = pagination.items
        if page == 1:
            print(f"DEBUG: Physical query returned {len(locations)} locations")
        
        # Get summary statistics - CRITICAL: Filter by created_by for multi-tenancy
        total_locations = Location.query.filter_by(
            warehouse_id=warehouse_id,
            is_active=True,
            created_by=current_user.id
        ).count()
        storage_locations = Location.query.filter_by(
            warehouse_id=warehouse_id,
            location_type='STORAGE',
            is_active=True,
            created_by=current_user.id
        ).count()
        total_capacity = db.session.query(db.func.sum(Location.pallet_capacity)).filter(
            and_(
                Location.warehouse_id == warehouse_id,
                Location.is_active == True,
                Location.created_by == current_user.id
            )
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
            },
            'location_source': 'physical'
        }), 200
        
    except Exception as e:
        # CRITICAL FIX: Always rollback failed transactions in PostgreSQL
        db.session.rollback()
        print(f"[LOCATION_API] Physical locations error: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace for debugging
        return jsonify({'error': f'Failed to retrieve physical locations: {str(e)}'}), 500

def _get_virtual_locations(current_user, warehouse_id, location_type, zone, is_active, aisle_number, search, page, per_page):
    """Handle virtual location queries using compatibility manager"""
    try:
        # Only log on first page requests to reduce spam
        if page == 1:
            print(f"[LOCATION_API] Getting virtual locations for warehouse {warehouse_id}")
        
        # Get compatibility manager
        compat_manager = get_compatibility_manager()
        
        # Get all virtual locations for the warehouse (with safety limit)
        all_locations = compat_manager.get_all_warehouse_locations(warehouse_id)
        if page == 1:
            print(f"[LOCATION_API] Retrieved {len(all_locations)} virtual locations")
        
        if not all_locations:
            print(f"[LOCATION_API] No virtual locations found - warehouse may not be properly configured")
            return jsonify({
                'locations': [],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'pages': 0,
                    'has_next': False,
                    'has_prev': False
                },
                'summary': {
                    'total_locations': 0,
                    'storage_locations': 0,
                    'total_capacity': 0,
                    'warehouse_id': warehouse_id
                },
                'location_source': 'virtual',
                'warning': 'No virtual locations configured for this warehouse'
            }), 200
        
        # Apply filters to virtual locations
        filtered_locations = all_locations
        
        if location_type:
            filtered_locations = [loc for loc in filtered_locations if loc.get('location_type') == location_type]
            if page == 1:
                print(f"[LOCATION_API] After location_type filter ({location_type}): {len(filtered_locations)} locations")
        
        if zone:
            filtered_locations = [loc for loc in filtered_locations if loc.get('zone') == zone]
            if page == 1:
                print(f"[LOCATION_API] After zone filter ({zone}): {len(filtered_locations)} locations")
            
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            filtered_locations = [loc for loc in filtered_locations if loc.get('is_active', True) == is_active_bool]
            if page == 1:
                print(f"[LOCATION_API] After is_active filter ({is_active}): {len(filtered_locations)} locations")
            
        if aisle_number:
            aisle_num = int(aisle_number)
            filtered_locations = [loc for loc in filtered_locations if loc.get('aisle_number') == aisle_num]
            if page == 1:
                print(f"[LOCATION_API] After aisle_number filter ({aisle_number}): {len(filtered_locations)} locations")
            
        if search:
            search_term = search.strip().upper()
            search_results = []
            for loc in filtered_locations:
                code = str(loc.get('code', '')).upper()
                if (search_term in code or 
                    search_term in str(loc.get('zone', '')).upper()):
                    search_results.append(loc)
            filtered_locations = search_results
            if page == 1:
                print(f"[LOCATION_API] After search filter ('{search}'): {len(filtered_locations)} locations")
        
        # Sort virtual locations (special areas first, then storage)
        def sort_key(loc):
            type_priority = {
                'RECEIVING': 1,
                'STAGING': 2, 
                'DOCK': 3,
                'TRANSITIONAL': 4,  # CRITICAL FIX: Include AISLE locations in high priority
                'STORAGE': 5
            }
            return (
                type_priority.get(loc.get('location_type', 'STORAGE'), 5),
                loc.get('aisle_number') or 0,
                loc.get('rack_number') or 0,
                loc.get('position_number') or 0,
                loc.get('level', '') or '',
                loc.get('code', '')
            )
        
        filtered_locations.sort(key=sort_key)
        
        # Apply pagination to filtered results
        total_filtered = len(filtered_locations)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_locations = filtered_locations[start_index:end_index]
        
        if page == 1:
            print(f"[LOCATION_API] Pagination: showing {len(paginated_locations)} of {total_filtered} locations (page {page})")
        
        # Calculate summary statistics
        total_locations = len(all_locations)
        storage_locations = len([loc for loc in all_locations if loc.get('location_type') == 'STORAGE'])
        total_capacity = sum(loc.get('capacity', 1) for loc in all_locations)
        
        # Debug: Show location types in response (only for first page to reduce spam)
        if page == 1:
            location_types = {}
            for loc in paginated_locations:
                loc_type = loc.get('location_type', 'UNKNOWN')
                location_types[loc_type] = location_types.get(loc_type, 0) + 1
            print(f"DEBUG: Virtual location types in response: {location_types}")
            
            special_areas = [loc.get('code') for loc in paginated_locations if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL']]
            print(f"DEBUG: Virtual special areas in response: {special_areas}")
        
        # Calculate pagination info
        total_pages = (total_filtered + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return jsonify({
            'locations': paginated_locations,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_filtered,
                'pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            },
            'summary': {
                'total_locations': total_locations,
                'storage_locations': storage_locations,
                'total_capacity': total_capacity,
                'warehouse_id': warehouse_id
            },
            'location_source': 'virtual'
        }), 200
        
    except Exception as e:
        print(f"[LOCATION_API] Virtual locations error: {str(e)}")
        return jsonify({'error': f'Failed to retrieve virtual locations: {str(e)}'}), 500

@location_bp.route('/<int:location_id>', methods=['GET'])
@token_required
def get_location(current_user, location_id):
    """Get a specific location by ID"""
    try:
        # CRITICAL: Ensure user can only access their own locations
        location = Location.query.filter_by(
            id=location_id,
            created_by=current_user.id
        ).first_or_404()
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
        
        # Check if location code already exists (PostgreSQL case-sensitive issue)
        # PostgreSQL is case-sensitive, so check both exact and normalized versions
        code = data['code'].upper().strip()  # Normalize the code
        existing = Location.query.filter(
            (Location.code == data['code']) | 
            (Location.code == code)
        ).first()
        if existing:
            return jsonify({'error': f'Location with code {data["code"]} already exists'}), 409
        
        # Use normalized code
        data['code'] = code
        
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
        
        # Add better error handling for PostgreSQL
        try:
            db.session.add(location)
            db.session.flush()  # Flush to catch constraint violations before commit
            db.session.commit()
            
            return jsonify({
                'message': 'Location created successfully',
                'location': location.to_dict()
            }), 201
            
        except Exception as commit_error:
            db.session.rollback()
            # Check for common PostgreSQL constraint violations
            error_msg = str(commit_error)
            if 'unique constraint' in error_msg.lower() or 'duplicate key' in error_msg.lower():
                return jsonify({'error': f'Location code {data["code"]} already exists'}), 409
            elif 'foreign key' in error_msg.lower():
                return jsonify({'error': 'Invalid warehouse_id or user reference'}), 400
            else:
                return jsonify({'error': f'Database error: {error_msg}'}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create location: {str(e)}'}), 500

@location_bp.route('/<int:location_id>', methods=['PUT'])
@token_required
def update_location(current_user, location_id):
    """Update an existing location"""
    try:
        # CRITICAL: Ensure user can only update their own locations
        location = Location.query.filter_by(
            id=location_id,
            created_by=current_user.id
        ).first_or_404()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if code is being changed and if it conflicts within user's locations
        if 'code' in data and data['code'] != location.code:
            existing = Location.query.filter_by(
                code=data['code'],
                warehouse_id=location.warehouse_id,
                created_by=current_user.id
            ).first()
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
        # CRITICAL: Ensure user can only delete their own locations
        location = Location.query.filter_by(
            id=location_id,
            created_by=current_user.id
        ).first_or_404()
        
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
                
                # Check for duplicate codes within user's locations
                existing = Location.query.filter_by(
                    code=location_data['code'],
                    warehouse_id=location_data.get('warehouse_id', 'DEFAULT'),
                    created_by=current_user.id
                ).first()
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

@location_bp.route('/bulk-range', methods=['POST'])
@token_required
def bulk_create_location_range(current_user):
    """
    Create a range of sequential special locations (e.g., W-01 to W-15)
    Request body: {
        'prefix': 'W-',
        'start_number': 1,
        'end_number': 15,
        'use_leading_zeros': true,
        'location_type': 'TRANSITIONAL',
        'zone': 'W',
        'pallet_capacity': 10,
        'warehouse_id': 'DEFAULT',
        'special_requirements': {},
        'allowed_products': []
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['prefix', 'start_number', 'end_number', 'location_type', 'pallet_capacity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Extract parameters
        prefix = str(data['prefix']).strip().upper()  # Normalize to uppercase
        start_number = int(data['start_number'])
        end_number = int(data['end_number'])
        use_leading_zeros = data.get('use_leading_zeros', True)
        location_type = data['location_type']
        zone = data.get('zone', prefix.replace('-', '').replace('_', '')).upper()  # Normalize zone to uppercase
        pallet_capacity = int(data['pallet_capacity'])
        warehouse_id = data.get('warehouse_id', 'DEFAULT')
        special_requirements = data.get('special_requirements', {})
        allowed_products = data.get('allowed_products', [])

        # Validate inputs
        if not prefix:
            return jsonify({'error': 'Prefix cannot be empty'}), 400

        if len(prefix) > 10:
            return jsonify({'error': 'Prefix must be 10 characters or less'}), 400

        if start_number >= end_number:
            return jsonify({'error': 'Start number must be less than end number'}), 400

        # Calculate range size
        range_size = end_number - start_number + 1

        if range_size > 100:
            return jsonify({
                'error': f'Range too large ({range_size} locations). Maximum: 100 locations per batch',
                'suggestion': f'Create {prefix}{start_number} to {prefix}{start_number + 99}, then {prefix}{start_number + 100} to {prefix}{end_number}'
            }), 400

        if pallet_capacity < 1 or pallet_capacity > 1000:
            return jsonify({'error': 'Pallet capacity must be between 1 and 1000'}), 400

        # Validate location type
        valid_types = ['RECEIVING', 'STORAGE', 'STAGING', 'DOCK', 'TRANSITIONAL']
        if location_type not in valid_types:
            return jsonify({'error': f'Invalid location type. Must be one of: {valid_types}'}), 400

        # Auto-detect padding width
        if use_leading_zeros:
            padding_width = len(str(end_number))
        else:
            padding_width = 0

        # Generate location codes and check for duplicates
        location_codes = []
        duplicates = []

        for num in range(start_number, end_number + 1):
            if use_leading_zeros:
                code = f"{prefix}{str(num).zfill(padding_width)}"
            else:
                code = f"{prefix}{num}"

            location_codes.append(code)

            # Check if location already exists
            existing = Location.query.filter_by(
                warehouse_id=warehouse_id,
                code=code,
                created_by=current_user.id
            ).first()

            if existing:
                duplicates.append(code)

        # If duplicates found, return warning
        if duplicates:
            return jsonify({
                'error': 'Duplicate locations detected',
                'duplicates': duplicates,
                'total_duplicates': len(duplicates),
                'message': f'{len(duplicates)} location(s) already exist. Please remove them first or use different codes.'
            }), 409

        # Create locations
        created_locations = []
        errors = []

        print(f"[BULK_RANGE] Creating {len(location_codes)} locations: {location_codes[:5]}{'...' if len(location_codes) > 5 else ''}")

        for i, code in enumerate(location_codes):
            try:
                location = Location(
                    code=code,
                    location_type=location_type,
                    capacity=pallet_capacity,
                    pallet_capacity=pallet_capacity,
                    zone=zone,
                    warehouse_id=warehouse_id,
                    created_by=current_user.id,
                    is_active=True
                )

                # Set JSON fields if provided
                if special_requirements:
                    location.set_special_requirements(special_requirements)

                if allowed_products:
                    location.set_allowed_products(allowed_products)

                db.session.add(location)
                created_locations.append(location)

            except Exception as e:
                errors.append(f'{code}: {str(e)}')
                print(f"[BULK_RANGE] Error creating {code}: {str(e)}")

        # Commit all locations
        if created_locations:
            try:
                db.session.commit()
                print(f"[BULK_RANGE] Successfully committed {len(created_locations)} locations")
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'error': f'Database commit failed: {str(e)}',
                    'created_count': 0,
                    'errors': errors
                }), 500

        # Calculate summary
        total_capacity = len(created_locations) * pallet_capacity

        return jsonify({
            'message': f'Successfully created {len(created_locations)} location(s)',
            'created_count': len(created_locations),
            'skipped_count': 0,
            'error_count': len(errors),
            'errors': errors,
            'warnings': [],
            'created_locations': [loc.to_dict() for loc in created_locations],
            'summary': {
                'total_capacity': total_capacity,
                'location_codes': location_codes,
                'prefix': prefix,
                'start_number': start_number,
                'end_number': end_number,
                'location_type': location_type,
                'zone': zone,
                'pallet_capacity': pallet_capacity
            }
        }), 201

    except ValueError as e:
        return jsonify({'error': f'Invalid number format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"[BULK_RANGE] Unexpected error: {str(e)}")
        return jsonify({'error': f'Bulk range operation failed: {str(e)}'}), 500

@location_bp.route('/bulk-range/preview', methods=['POST'])
@token_required
def preview_location_range(current_user):
    """
    Preview location codes that would be generated without creating them
    Request body: Same as bulk-range endpoint
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract parameters
        prefix = str(data.get('prefix', '')).strip().upper()  # Normalize to uppercase
        start_number = int(data.get('start_number', 1))
        end_number = int(data.get('end_number', 10))
        use_leading_zeros = data.get('use_leading_zeros', True)
        warehouse_id = data.get('warehouse_id', 'DEFAULT')
        pallet_capacity = int(data.get('pallet_capacity', 1))

        # Basic validation
        if not prefix:
            return jsonify({'error': 'Prefix is required'}), 400

        if start_number >= end_number:
            return jsonify({'error': 'Start number must be less than end number'}), 400

        # Calculate range size
        range_size = end_number - start_number + 1

        # Auto-detect padding width
        if use_leading_zeros:
            padding_width = len(str(end_number))
        else:
            padding_width = 0

        # Generate preview codes
        location_codes = []
        duplicates = []

        for num in range(start_number, end_number + 1):
            if use_leading_zeros:
                code = f"{prefix}{str(num).zfill(padding_width)}"
            else:
                code = f"{prefix}{num}"

            location_codes.append(code)

            # Check if location already exists
            existing = Location.query.filter_by(
                warehouse_id=warehouse_id,
                code=code,
                created_by=current_user.id
            ).first()

            if existing:
                duplicates.append(code)

        # Generate warnings
        warnings = []

        if range_size > 100:
            warnings.append(f'Range too large ({range_size} locations). Maximum: 100 locations per batch')

        if range_size > 50:
            warnings.append(f'Creating {range_size} locations may take a moment')

        if duplicates:
            warnings.append(f'{len(duplicates)} location(s) already exist and will need to be handled')

        # Capacity warnings
        if pallet_capacity > 50:
            warnings.append(f'Very high capacity ({pallet_capacity} pallets). Please verify this is correct.')

        return jsonify({
            'location_codes': location_codes,
            'duplicates': duplicates,
            'warnings': warnings,
            'summary': {
                'total_locations': len(location_codes),
                'total_new': len(location_codes) - len(duplicates),
                'total_duplicates': len(duplicates),
                'total_capacity': (len(location_codes) - len(duplicates)) * pallet_capacity,
                'prefix': prefix,
                'padding_width': padding_width
            }
        }), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid number format: {str(e)}'}), 400
    except Exception as e:
        print(f"[BULK_RANGE_PREVIEW] Error: {str(e)}")
        return jsonify({'error': f'Preview failed: {str(e)}'}), 500

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
        
        # Check if warehouse already has locations for this user
        existing_count = Location.query.filter_by(
            warehouse_id=warehouse_id,
            is_active=True,
            created_by=current_user.id
        ).count()
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
        
        # CRITICAL: Only export user's own locations
        locations = Location.query.filter_by(
            warehouse_id=warehouse_id, 
            is_active=True,
            created_by=current_user.id
        ).all()
        
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
            elif Location.query.filter_by(
                code=location_data['code'],
                created_by=current_user.id
            ).first():
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

# Location Classification Correction Endpoints

@location_bp.route('/classification/correct', methods=['POST'])
@login_required
def correct_location_classification():
    """
    Submit a correction for location type classification
    Enables users to improve system accuracy through feedback
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['warehouse_id', 'location_code', 'corrected_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400

        warehouse_id = data['warehouse_id']
        location_code = data['location_code']
        corrected_type = data['corrected_type']

        # Validate corrected_type
        valid_types = ['RECEIVING', 'STORAGE', 'TRANSITIONAL', 'STAGING', 'DOCK', 'AISLE', 'SPECIAL']
        if corrected_type not in valid_types:
            return jsonify({'error': f'Invalid location type. Must be one of: {valid_types}'}), 400

        # Import here to avoid circular imports
        from models import LocationClassificationCorrection

        # Check if correction already exists for this user
        existing_correction = LocationClassificationCorrection.query.filter_by(
            warehouse_id=warehouse_id,
            location_code=location_code,
            corrected_by=current_user.id
        ).first()

        if existing_correction:
            # Update existing correction
            existing_correction.corrected_type = corrected_type
            existing_correction.original_type = data.get('original_type')
            existing_correction.original_confidence = data.get('original_confidence')
            existing_correction.original_method = data.get('original_method')
            existing_correction.correction_reason = data.get('correction_reason')
            existing_correction.is_active = True

            # Update context if provided
            if data.get('correction_context'):
                existing_correction.set_correction_context(data['correction_context'])

            # Extract and update pattern
            existing_correction.location_pattern = existing_correction.extract_pattern()

            correction = existing_correction
        else:
            # Create new correction
            correction = LocationClassificationCorrection(
                warehouse_id=warehouse_id,
                location_code=location_code,
                corrected_type=corrected_type,
                original_type=data.get('original_type'),
                original_confidence=data.get('original_confidence'),
                original_method=data.get('original_method'),
                correction_reason=data.get('correction_reason'),
                corrected_by=current_user.id
            )

            # Set context if provided
            if data.get('correction_context'):
                correction.set_correction_context(data['correction_context'])

            # Extract pattern for learning
            correction.location_pattern = correction.extract_pattern()

            db.session.add(correction)

        db.session.commit()

        return jsonify({
            'success': True,
            'correction': correction.to_dict(),
            'message': f'Classification correction saved for {location_code}'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save correction: {str(e)}'}), 500


@location_bp.route('/classification/corrections', methods=['GET'])
@login_required
def get_classification_corrections():
    """
    Get classification corrections for a warehouse
    Supports filtering by location, type, and user
    """
    try:
        warehouse_id = request.args.get('warehouse_id')
        if not warehouse_id:
            return jsonify({'error': 'warehouse_id parameter required'}), 400

        # Import here to avoid circular imports
        from models import LocationClassificationCorrection

        # Build query
        query = LocationClassificationCorrection.query.filter_by(
            warehouse_id=warehouse_id,
            is_active=True
        )

        # Apply filters
        if request.args.get('location_code'):
            query = query.filter_by(location_code=request.args.get('location_code'))

        if request.args.get('corrected_type'):
            query = query.filter_by(corrected_type=request.args.get('corrected_type'))

        if request.args.get('corrected_by'):
            query = query.filter_by(corrected_by=request.args.get('corrected_by'))

        # Order by most recent first
        corrections = query.order_by(LocationClassificationCorrection.created_at.desc()).all()

        # Calculate summary statistics
        total_corrections = len(corrections)
        type_distribution = {}
        method_distribution = {}

        for correction in corrections:
            # Count by corrected type
            type_distribution[correction.corrected_type] = type_distribution.get(
                correction.corrected_type, 0) + 1

            # Count by original method
            if correction.original_method:
                method_distribution[correction.original_method] = method_distribution.get(
                    correction.original_method, 0) + 1

        return jsonify({
            'corrections': [correction.to_dict() for correction in corrections],
            'summary': {
                'total_corrections': total_corrections,
                'type_distribution': type_distribution,
                'method_distribution': method_distribution,
                'most_corrected_locations': [
                    correction.location_code for correction in corrections[:10]
                ]
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get corrections: {str(e)}'}), 500


@location_bp.route('/classification/test', methods=['POST'])
@login_required
def test_location_classification():
    """
    Test the enhanced location classification system
    Useful for debugging and validation
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        locations = data.get('locations', [])
        if not locations:
            return jsonify({'error': 'No locations provided for testing'}), 400

        warehouse_context = {
            'warehouse_id': data.get('warehouse_id', 'DEFAULT')
        }

        # Import classifier
        from enhanced_location_classifier import EnhancedLocationClassifier

        # Initialize classifier
        classifier = EnhancedLocationClassifier(db_session=db)

        # Test each location
        results = {}
        for location in locations:
            try:
                result = classifier.classify_location(
                    location=location,
                    warehouse_context=warehouse_context
                )
                results[location] = {
                    'location_type': result.location_type,
                    'confidence': result.confidence,
                    'method': result.method,
                    'reasoning': result.reasoning
                }
            except Exception as e:
                results[location] = {
                    'error': str(e),
                    'location_type': 'ERROR',
                    'confidence': 0.0,
                    'method': 'error',
                    'reasoning': f'Classification failed: {str(e)}'
                }

        # Generate summary
        summary = classifier.get_classification_summary({
            location: type(
                'MockResult',
                (),
                {
                    'location_type': result['location_type'],
                    'confidence': result['confidence'],
                    'method': result['method']
                }
            )() for location, result in results.items() if 'error' not in result
        })

        return jsonify({
            'test_results': results,
            'summary': summary,
            'warehouse_context': warehouse_context
        }), 200

    except Exception as e:
        return jsonify({'error': f'Classification test failed: {str(e)}'}), 500


@location_bp.route('/classification/bulk-correct', methods=['POST'])
@login_required
def bulk_correct_classifications():
    """
    Apply corrections to multiple locations at once
    Useful for batch learning from user feedback
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        corrections = data.get('corrections', [])
        if not corrections:
            return jsonify({'error': 'No corrections provided'}), 400

        warehouse_id = data.get('warehouse_id')
        if not warehouse_id:
            return jsonify({'error': 'warehouse_id required'}), 400

        from models import LocationClassificationCorrection

        success_count = 0
        error_count = 0
        results = []

        for correction_data in corrections:
            try:
                location_code = correction_data.get('location_code')
                corrected_type = correction_data.get('corrected_type')

                if not location_code or not corrected_type:
                    results.append({
                        'location_code': location_code,
                        'success': False,
                        'error': 'Missing location_code or corrected_type'
                    })
                    error_count += 1
                    continue

                # Create or update correction
                existing = LocationClassificationCorrection.query.filter_by(
                    warehouse_id=warehouse_id,
                    location_code=location_code,
                    corrected_by=current_user.id
                ).first()

                if existing:
                    existing.corrected_type = corrected_type
                    existing.is_active = True
                    existing.location_pattern = existing.extract_pattern()
                    correction = existing
                else:
                    correction = LocationClassificationCorrection(
                        warehouse_id=warehouse_id,
                        location_code=location_code,
                        corrected_type=corrected_type,
                        corrected_by=current_user.id
                    )
                    correction.location_pattern = correction.extract_pattern()
                    db.session.add(correction)

                db.session.commit()

                results.append({
                    'location_code': location_code,
                    'success': True,
                    'correction_id': correction.id
                })
                success_count += 1

            except Exception as e:
                results.append({
                    'location_code': correction_data.get('location_code', 'unknown'),
                    'success': False,
                    'error': str(e)
                })
                error_count += 1
                db.session.rollback()

        return jsonify({
            'results': results,
            'summary': {
                'total_processed': len(corrections),
                'success_count': success_count,
                'error_count': error_count,
                'success_rate': success_count / len(corrections) * 100
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Bulk correction failed: {str(e)}'}), 500


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