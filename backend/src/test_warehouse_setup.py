#!/usr/bin/env python3
"""
Test the fixed warehouse setup API
"""

import requests
import json

API_BASE_URL = 'http://localhost:5000/api/v1'

def get_auth_token():
    """Get authentication token"""
    response = requests.post(f"{API_BASE_URL}/auth/login", json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    
    if response.status_code == 200:
        return response.json().get('token')
    else:
        print(f"Authentication failed: {response.status_code}")
        return None

def test_warehouse_setup():
    """Test warehouse setup with duplicate prevention"""
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test setup data
    setup_data = {
        'warehouse_id': 'TEST_WAREHOUSE_001',
        'configuration': {
            'warehouse_name': 'Test Warehouse',
            'num_aisles': 2,
            'racks_per_aisle': 2,
            'positions_per_rack': 5,
            'levels_per_position': 2,
            'level_names': 'AB',
            'default_pallet_capacity': 1,
            'bidimensional_racks': False,
            'default_zone': 'GENERAL'
        },
        'receiving_areas': [
            {'code': 'RECV_TEST', 'type': 'RECEIVING', 'capacity': 5, 'zone': 'DOCK'}
        ],
        'generate_locations': True,
        'create_template': False
    }
    
    print("Testing warehouse setup...")
    print(f"Setup data: {json.dumps(setup_data, indent=2)}")
    
    response = requests.post(f"{API_BASE_URL}/warehouse/setup", json=setup_data, headers=headers)
    
    print(f"Response status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code in [200, 201]

if __name__ == "__main__":
    success = test_warehouse_setup()
    if success:
        print("Warehouse setup test passed!")
    else:
        print("Warehouse setup test failed!")