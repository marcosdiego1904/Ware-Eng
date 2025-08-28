#!/usr/bin/env python3
"""
Test the user warehouse detection with proper authentication
"""

import sys
sys.path.append('src')

import requests
import json

def test_with_auth():
    """Test the user warehouse API with proper authentication"""
    print("TESTING USER WAREHOUSE API WITH AUTHENTICATION")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # First, register/login a user
    test_user = {
        "username": "marcosbarzola@devbymarcos.com",
        "password": "test123"
    }
    
    print(f"Step 1: Attempting login for {test_user['username']}")
    print("-" * 40)
    
    try:
        # Try to log in
        login_response = session.post(
            f"{base_url}/api/v1/auth/login", 
            json=test_user,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f"Login Success: {login_data.get('success', False)}")
            
            if login_data.get('success') and 'token' in login_data:
                # Use the JWT token for subsequent requests
                token = login_data['token']
                session.headers.update({'Authorization': f'Bearer {token}'})
                
                print(f"\nStep 2: Testing user warehouse API with token")
                print("-" * 40)
                
                # Now test the warehouse API
                warehouse_response = session.get(f"{base_url}/api/v1/user/warehouse")
                
                print(f"Warehouse API Status: {warehouse_response.status_code}")
                
                if warehouse_response.status_code == 200:
                    warehouse_data = warehouse_response.json()
                    print("SUCCESS! User warehouse data:")
                    print(json.dumps(warehouse_data, indent=2))
                    
                    # Test location API with the detected warehouse
                    if warehouse_data.get('success') and warehouse_data.get('primary_warehouse'):
                        warehouse_id = warehouse_data.get('primary_warehouse')
                        
                        print(f"\nStep 3: Testing locations API for warehouse: {warehouse_id}")
                        print("-" * 40)
                        
                        locations_response = session.get(
                            f"{base_url}/api/v1/locations",
                            params={'warehouse_id': warehouse_id, 'location_type': 'special'}
                        )
                        
                        print(f"Locations API Status: {locations_response.status_code}")
                        
                        if locations_response.status_code == 200:
                            locations_data = locations_response.json()
                            special_locations = locations_data.get('locations', [])
                            print(f"Special locations found: {len(special_locations)}")
                            
                            if special_locations:
                                print("Special locations:")
                                for location in special_locations[:5]:
                                    print(f"  - {location.get('location_code')}: {location.get('location_name')}")
                            else:
                                print("No special locations found")
                        else:
                            print(f"Locations API Error: {locations_response.text}")
                    
                else:
                    print(f"Warehouse API Error: {warehouse_response.text}")
            else:
                print(f"Login failed: {login_data}")
        else:
            print(f"Login Error: {login_response.text}")
            
            # If login fails, maybe user doesn't exist, try registering
            print(f"\nTrying to register user...")
            register_response = session.post(
                f"{base_url}/api/v1/auth/register",
                json=test_user,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Register Status: {register_response.status_code}")
            if register_response.status_code == 200:
                print("Registration successful, now trying login again...")
                # Try login again after registration
                login_response = session.post(
                    f"{base_url}/api/v1/auth/login", 
                    json=test_user,
                    headers={'Content-Type': 'application/json'}
                )
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    if login_data.get('success') and 'token' in login_data:
                        token = login_data['token']
                        session.headers.update({'Authorization': f'Bearer {token}'})
                        
                        # Test the warehouse API after successful registration/login
                        warehouse_response = session.get(f"{base_url}/api/v1/user/warehouse")
                        print(f"Warehouse API Status: {warehouse_response.status_code}")
                        
                        if warehouse_response.status_code == 200:
                            warehouse_data = warehouse_response.json()
                            print("User warehouse data after registration:")
                            print(json.dumps(warehouse_data, indent=2))
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to backend server at http://localhost:5000")
        print("Make sure the backend server is running")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_with_auth()