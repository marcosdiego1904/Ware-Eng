#!/usr/bin/env python3
"""
Test the frontend-backend integration for user warehouse detection
"""

import sys
sys.path.append('src')

import requests
import json

def test_frontend_integration():
    """Test the full flow that the frontend would use"""
    print("TESTING FRONTEND-BACKEND INTEGRATION")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test the user warehouse API endpoint
    print("\nTesting /api/v1/user/warehouse endpoint:")
    print("-" * 30)
    
    try:
        # This simulates what the frontend API call would do
        response = requests.get(f"{base_url}/api/v1/user/warehouse")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nAPI Response:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                print(f"\nFRONTEND WOULD RECEIVE:")
                print(f"- Primary Warehouse: {data.get('primary_warehouse')}")
                print(f"- Warehouse Name: {data.get('primary_warehouse_name')}")
                print(f"- Special Areas: {data.get('special_areas_count')}")
                print(f"- Detection Method: {data.get('detection_method')}")
                print(f"- Available Warehouses: {len(data.get('all_user_warehouses', []))}")
            else:
                print(f"ERROR: {data.get('error')}")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
        # Test the all warehouses endpoint
        print(f"\n\nTesting /api/v1/user/warehouses endpoint:")
        print("-" * 30)
        
        response2 = requests.get(f"{base_url}/api/v1/user/warehouses")
        print(f"Status Code: {response2.status_code}")
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"\nAll User Warehouses ({data2.get('total_count', 0)}):")
            for warehouse in data2.get('warehouses', []):
                print(f"  - {warehouse['warehouse_id']}: {warehouse['warehouse_name']} " +
                      f"({warehouse['special_areas_count']} special areas)")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to backend server at http://localhost:5000")
        print("Make sure the backend server is running")
    except Exception as e:
        print(f"ERROR: {e}")

def test_location_api_with_detected_warehouse():
    """Test location API using the detected warehouse"""
    print(f"\n\nTESTING LOCATION API WITH DETECTED WAREHOUSE")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # First get the user's warehouse
        warehouse_response = requests.get(f"{base_url}/api/v1/user/warehouse")
        if warehouse_response.status_code == 200:
            warehouse_data = warehouse_response.json()
            if warehouse_data.get('success'):
                warehouse_id = warehouse_data.get('primary_warehouse')
                print(f"Using warehouse: {warehouse_id}")
                
                # Now test the locations API with this warehouse
                locations_response = requests.get(
                    f"{base_url}/api/v1/locations",
                    params={'warehouse_id': warehouse_id, 'location_type': 'special'}
                )
                
                print(f"Locations API Status: {locations_response.status_code}")
                if locations_response.status_code == 200:
                    locations_data = locations_response.json()
                    special_locations = locations_data.get('locations', [])
                    print(f"Special locations found: {len(special_locations)}")
                    
                    for location in special_locations[:5]:  # Show first 5
                        print(f"  - {location.get('location_code')}: {location.get('location_name')} " +
                              f"({location.get('location_type')})")
                else:
                    print(f"Locations API Error: {locations_response.text}")
            else:
                print("Failed to get warehouse data")
        else:
            print("Failed to connect to warehouse API")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_frontend_integration()
    test_location_api_with_detected_warehouse()