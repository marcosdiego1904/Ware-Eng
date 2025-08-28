#!/usr/bin/env python3
"""
Test the user warehouse detection using Flask session-based authentication
"""

import sys
sys.path.append('src')

from app import app
from database import db
from core_models import User
from models import WarehouseConfig
import json

def test_session_integration():
    """Test the user warehouse API using Flask test client with session authentication"""
    print("TESTING USER WAREHOUSE API WITH SESSION AUTHENTICATION")
    print("=" * 65)
    
    with app.app_context():
        # Get the test user
        user = User.query.filter_by(username='marcosbarzola@devbymarcos.com').first()
        if not user:
            print("ERROR: Test user not found")
            return
            
        print(f"Found user: {user.username} (ID: {user.id})")
        
        # Test with Flask test client
        with app.test_client() as client:
            # Simulate user session
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            print("\nStep 1: Testing user warehouse detection API")
            print("-" * 45)
            
            response = client.get('/api/v1/user/warehouse')
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print("OK User Warehouse API Response:")
                print(json.dumps(data, indent=2))
                
                warehouse_id = data.get('primary_warehouse')
                warehouse_name = data.get('primary_warehouse_name')
                special_areas = data.get('special_areas_count', 0)
                method = data.get('detection_method')
                
                print(f"\nDETECTED PRIMARY WAREHOUSE:")
                print(f"   Warehouse ID: {warehouse_id}")
                print(f"   Warehouse Name: {warehouse_name}")  
                print(f"   Special Areas: {special_areas}")
                print(f"   Detection Method: {method}")
                
                print(f"\nStep 2: Testing locations API with detected warehouse")
                print("-" * 50)
                
                # Test locations API with the detected warehouse
                locations_response = client.get(f'/api/v1/locations?warehouse_id={warehouse_id}&location_type=special')
                print(f"Locations API Status: {locations_response.status_code}")
                
                if locations_response.status_code == 200:
                    locations_data = locations_response.get_json()
                    special_locations = locations_data.get('locations', [])
                    
                    print(f"OK Found {len(special_locations)} special locations:")
                    
                    if special_locations:
                        for i, location in enumerate(special_locations[:10], 1):  # Show first 10
                            print(f"   {i}. {location.get('location_code')}: {location.get('location_name')} ({location.get('location_type')})")
                            
                        if len(special_locations) > 10:
                            print(f"   ... and {len(special_locations) - 10} more locations")
                    else:
                        print("   No special locations found for this warehouse")
                        
                else:
                    print(f"ERROR Locations API Error: {locations_response.get_data(as_text=True)}")
                    
                print(f"\nStep 3: Testing warehouse configuration")
                print("-" * 40)
                
                # Check the warehouse configuration directly
                warehouse_config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
                if warehouse_config:
                    receiving_areas = warehouse_config.get_receiving_areas()
                    staging_areas = warehouse_config.get_staging_areas()
                    dock_areas = warehouse_config.get_dock_areas()
                    
                    print(f"OK Warehouse configuration found:")
                    print(f"   Receiving areas: {len(receiving_areas)}")
                    print(f"   Staging areas: {len(staging_areas)}")
                    print(f"   Dock areas: {len(dock_areas)}")
                    print(f"   Total special areas in config: {len(receiving_areas) + len(staging_areas) + len(dock_areas)}")
                    
                    if receiving_areas:
                        print(f"   Receiving: {', '.join(receiving_areas)}")
                    if staging_areas:
                        print(f"   Staging: {', '.join(staging_areas)}")
                    if dock_areas:
                        print(f"   Dock: {', '.join(dock_areas)}")
                else:
                    print(f"ERROR No warehouse configuration found for {warehouse_id}")
                    
            else:
                print(f"ERROR User Warehouse API Error: {response.get_data(as_text=True)}")
                
            print(f"\nStep 4: Testing all user warehouses endpoint")
            print("-" * 45)
            
            all_warehouses_response = client.get('/api/v1/user/warehouses')
            print(f"All Warehouses API Status: {all_warehouses_response.status_code}")
            
            if all_warehouses_response.status_code == 200:
                all_data = all_warehouses_response.get_json()
                warehouses = all_data.get('warehouses', [])
                
                print(f"OK User has access to {len(warehouses)} warehouses:")
                for warehouse in warehouses:
                    is_primary = "*" if warehouse['warehouse_id'] == warehouse_id else " "
                    print(f"   {is_primary} {warehouse['warehouse_id']}: {warehouse['warehouse_name']} ({warehouse['special_areas_count']} special areas)")
            else:
                print(f"ERROR All Warehouses API Error: {all_warehouses_response.get_data(as_text=True)}")

if __name__ == "__main__":
    test_session_integration()