#!/usr/bin/env python3
"""
Quick test of warehouse configuration API
"""

import os
import sys
import requests
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

API_BASE_URL = 'http://localhost:5000/api/v1'

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"Authentication successful")
            return token
        else:
            print(f"Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def test_warehouse_config_api():
    """Test warehouse configuration endpoints"""
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Cannot proceed without authentication")
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # Test GET config
        print("\\nTesting GET /warehouse/config...")
        response = requests.get(f"{API_BASE_URL}/warehouse/config?warehouse_id=DEFAULT", headers=headers)
        
        if response.status_code == 200:
            config = response.json()
            print(f"Warehouse config retrieved successfully")
            print(f"  Warehouse: {config.get('warehouse_name', 'Unknown')}")
            print(f"  Aisles: {config.get('num_aisles', 'Unknown')}")
            print(f"  Total locations: {config.get('total_storage_locations', 'Unknown')}")
            return True
        else:
            print(f"GET config failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"API test error: {e}")
        return False

def test_locations_api():
    """Test locations API"""
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        print("\\nTesting GET /locations...")
        response = requests.get(f"{API_BASE_URL}/locations?warehouse_id=DEFAULT", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            locations = data.get('locations', [])
            summary = data.get('summary', {})
            print(f"Locations retrieved successfully")
            print(f"  Found {len(locations)} locations")
            print(f"  Total capacity: {summary.get('total_capacity', 'Unknown')} pallets")
            return True
        else:
            print(f"GET locations failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Locations API test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Warehouse APIs...")
    print("=" * 50)
    
    config_ok = test_warehouse_config_api()
    locations_ok = test_locations_api()
    
    print("\\n" + "=" * 50)
    if config_ok and locations_ok:
        print("All API tests passed!")
    else:
        print("Some API tests failed")
    print("=" * 50)