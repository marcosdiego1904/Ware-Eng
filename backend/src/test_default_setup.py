#!/usr/bin/env python3
"""
Test DEFAULT warehouse setup after cleanup
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

def test_default_warehouse_setup():
    """Test DEFAULT warehouse setup"""
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test setup data for DEFAULT warehouse (simulating frontend)
    setup_data = {
        'warehouse_id': 'DEFAULT',
        'configuration': {
            'warehouse_name': 'Default Warehouse',
            'num_aisles': 4,
            'racks_per_aisle': 2,
            'positions_per_rack': 50,
            'levels_per_position': 4,
            'level_names': 'ABCD',
            'default_pallet_capacity': 1,
            'bidimensional_racks': False,
            'default_zone': 'GENERAL'
        },
        'receiving_areas': [
            {'code': 'RECEIVING', 'type': 'RECEIVING', 'capacity': 10, 'zone': 'DOCK'}
        ],
        'generate_locations': True,
        'create_template': False
    }
    
    print("Testing DEFAULT warehouse setup...")
    print(f"Setup data: warehouse_id = {setup_data['warehouse_id']}")
    print(f"Aisles: {setup_data['configuration']['num_aisles']}")
    print(f"Racks per aisle: {setup_data['configuration']['racks_per_aisle']}")
    print(f"Positions per rack: {setup_data['configuration']['positions_per_rack']}")
    print(f"Levels per position: {setup_data['configuration']['levels_per_position']}")
    
    response = requests.post(f"{API_BASE_URL}/warehouse/setup", json=setup_data, headers=headers)
    
    print(f"\\nResponse status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"SUCCESS!")
        print(f"  Warehouse: {result.get('warehouse_id')}")
        print(f"  Locations created: {result.get('locations_created')}")
        print(f"  Total capacity: {result.get('total_capacity')} pallets")
        return True
    else:
        print(f"FAILED!")
        try:
            error = response.json()
            print(f"  Error: {error.get('error', 'Unknown error')}")
        except:
            print(f"  Response: {response.text}")
        return False

if __name__ == "__main__":
    success = test_default_warehouse_setup()
    print(f"\\nResult: {'SUCCESS' if success else 'FAILED'}")