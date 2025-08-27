#!/usr/bin/env python3
"""
DATABASE SETUP FOR PRECISION TEST INVENTORY
Creates required location records for surgical anomaly testing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from flask import Flask
from models import db, Location, RuleCategory, Rule
import json

def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    
    # Database configuration
    database_path = os.path.join(os.path.dirname(__file__), 'backend', 'warehouse_rules.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def setup_precision_test_locations():
    """Create locations required for precision testing"""
    
    app = create_app()
    
    with app.app_context():
        print("SETTING UP PRECISION TEST LOCATIONS")
        print("===================================")
        
        # Check if locations already exist
        existing_locations = {loc.code: loc for loc in Location.query.all()}
        
        # Required locations for precision tests
        test_locations = [
            {
                'code': 'TINY_LOCATION_01',
                'name': 'Tiny Test Location 01',
                'location_type': 'STORAGE',
                'capacity': 1,  # CRITICAL: Exactly 1 for overcapacity testing
                'warehouse_id': 'USER_TESTF',
                'zone': 'TEST',
                'is_active': True,
                'allowed_products': ['*']  # Allow any product
            },
            {
                'code': 'PERFECT_LOCATION_01', 
                'name': 'Perfect Test Location 01',
                'location_type': 'STORAGE',
                'capacity': 1,  # Exactly 1 for control testing
                'warehouse_id': 'USER_TESTF',
                'zone': 'TEST',
                'is_active': True,
                'allowed_products': ['*']
            },
            {
                'code': 'AISLE_A_01',
                'name': 'Test Aisle A Location 01',
                'location_type': 'TRANSITIONAL', 
                'capacity': 10,
                'warehouse_id': 'USER_TESTF',
                'zone': 'AISLE',
                'is_active': True,
                'allowed_products': ['*']
            },
            {
                'code': 'RECEIVING_01',
                'name': 'Test Receiving Location 01',
                'location_type': 'RECEIVING',
                'capacity': 50,
                'warehouse_id': 'USER_TESTF', 
                'zone': 'RECEIVING',
                'is_active': True,
                'allowed_products': ['*']
            },
            {
                'code': 'RECEIVING_02',
                'name': 'Test Receiving Location 02',
                'location_type': 'RECEIVING',
                'capacity': 50,
                'warehouse_id': 'USER_TESTF',
                'zone': 'RECEIVING', 
                'is_active': True,
                'allowed_products': ['*']
            },
            {
                'code': 'RECEIVING_03',
                'name': 'Test Receiving Location 03',
                'location_type': 'RECEIVING',
                'capacity': 50,
                'warehouse_id': 'USER_TESTF',
                'zone': 'RECEIVING',
                'is_active': True,
                'allowed_products': ['*']
            },
            {
                'code': 'RECEIVING_04',
                'name': 'Test Receiving Location 04',
                'location_type': 'RECEIVING',
                'capacity': 50,
                'warehouse_id': 'USER_TESTF',
                'zone': 'RECEIVING',
                'is_active': True,
                'allowed_products': ['*']
            }
        ]
        
        # Add storage locations for lot testing
        for i in range(1, 6):
            test_locations.append({
                'code': f'STORAGE_{i:02d}',
                'name': f'Test Storage Location {i:02d}',
                'location_type': 'STORAGE',
                'capacity': 10,
                'warehouse_id': 'USER_TESTF',
                'zone': 'STORAGE',
                'is_active': True,
                'allowed_products': ['*']
            })
            
        # Add clean storage locations for control records
        for i in range(1, 6):
            test_locations.append({
                'code': f'STORAGE_CLEAN_{i:02d}',
                'name': f'Clean Storage Location {i:02d}',
                'location_type': 'STORAGE', 
                'capacity': 20,
                'warehouse_id': 'USER_TESTF',
                'zone': 'STORAGE',
                'is_active': True,
                'allowed_products': ['*']
            })
        
        # Create or update locations
        created_count = 0
        updated_count = 0
        
        for loc_data in test_locations:
            code = loc_data['code']
            
            if code in existing_locations:
                # Update existing location
                location = existing_locations[code]
                location.capacity = loc_data['capacity']
                location.location_type = loc_data['location_type']
                location.is_active = loc_data['is_active']
                updated_count += 1
                print(f"Updated: {code} (capacity: {loc_data['capacity']})")
            else:
                # Create new location
                location = Location(
                    code=loc_data['code'],
                    name=loc_data['name'],
                    location_type=loc_data['location_type'],
                    capacity=loc_data['capacity'],
                    warehouse_id=loc_data['warehouse_id'],
                    zone=loc_data['zone'],
                    is_active=loc_data['is_active'],
                    allowed_products=json.dumps(loc_data['allowed_products'])
                )
                db.session.add(location)
                created_count += 1
                print(f"Created: {code} (capacity: {loc_data['capacity']})")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\\nSUMMARY:")
        print(f"Created: {created_count} locations")
        print(f"Updated: {updated_count} locations") 
        print(f"Total: {created_count + updated_count} locations ready")
        
        # Verify critical locations
        print(f"\\nCRITICAL VERIFICATION:")
        tiny_loc = Location.query.filter_by(code='TINY_LOCATION_01').first()
        if tiny_loc and tiny_loc.capacity == 1:
            print(f"✓ TINY_LOCATION_01 has capacity=1 (required for overcapacity test)")
        else:
            print(f"✗ TINY_LOCATION_01 missing or wrong capacity!")
            
        aisle_loc = Location.query.filter_by(code='AISLE_A_01').first()
        if aisle_loc:
            print(f"✓ AISLE_A_01 exists (required for location-specific stagnant test)")
        else:
            print(f"✗ AISLE_A_01 missing!")
        
        print(f"\\nDATABASE SETUP COMPLETE - Ready for precision testing!")

if __name__ == "__main__":
    setup_precision_test_locations()