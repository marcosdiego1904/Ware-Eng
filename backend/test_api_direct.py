#!/usr/bin/env python3
"""
Direct API test to bypass authentication and see what data is returned
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import Location
import json

def test_location_api_direct():
    """Test the location API endpoint directly"""
    with app.app_context():
        print("=== TESTING LOCATION API DIRECTLY ===\n")
        
        # Import the location API functions
        from location_api import get_locations
        from flask import Flask, request
        
        # Create a test request context
        with app.test_request_context('/api/v1/locations?warehouse_id=DEFAULT&per_page=20'):
            try:
                # Call the API function directly
                response_data = get_locations()
                print("API Response structure:")
                print(f"- Status: {response_data[1] if isinstance(response_data, tuple) else 'Success'}")
                
                if isinstance(response_data, tuple):
                    data = response_data[0]
                else:
                    data = response_data
                
                if hasattr(data, 'get_json'):
                    json_data = data.get_json()
                    print(f"- Locations count: {len(json_data.get('locations', []))}")
                    print(f"- Pagination: {json_data.get('pagination', {})}")
                    
                    locations = json_data.get('locations', [])
                    if locations:
                        print(f"\nFirst 5 locations:")
                        for i, loc in enumerate(locations[:5]):
                            print(f"  {i+1}. {loc.get('code')} ({loc.get('location_type')}) - {loc.get('zone')}")
                        
                        # Count by type
                        type_counts = {}
                        for loc in locations:
                            loc_type = loc.get('location_type')
                            type_counts[loc_type] = type_counts.get(loc_type, 0) + 1
                        print(f"\nLocation type counts: {type_counts}")
                        
                        # Find special locations
                        special = [loc for loc in locations if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK']]
                        print(f"\nSpecial locations found: {len(special)}")
                        for loc in special:
                            print(f"  - {loc.get('code')} ({loc.get('location_type')}) - {loc.get('zone')}")
                else:
                    print(f"Unexpected response format: {type(data)}")
                    
            except Exception as e:
                print(f"Error calling API: {e}")
                import traceback
                traceback.print_exc()

if __name__ == '__main__':
    test_location_api_direct()