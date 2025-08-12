#!/usr/bin/env python3
"""
Debug script to simulate the exact frontend API call for locations
"""

import sys
sys.path.append('src')

import requests
import json
from app import app

def simulate_frontend_api_call():
    """Simulate the exact API call that the frontend makes"""
    with app.app_context():
        # This simulates what the frontend does
        base_url = 'http://localhost:5000/api/v1'
        
        # Create a test user token (this would normally come from login)
        print("=== SIMULATING FRONTEND API CALL FOR LOCATIONS ===\n")
        
        # The parameters that the frontend sends
        params = {
            'warehouse_id': 'DEFAULT',
            'page': '1',
            'per_page': '100'
        }
        
        headers = {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json'
        }
        
        try:
            # This is the exact URL the frontend calls
            url = f"{base_url}/locations"
            print(f"Making API call to: {url}")
            print(f"Parameters: {params}")
            print(f"Headers: {headers}")
            
            # Make the call (this would fail since server isn't running, but shows the format)
            # response = requests.get(url, params=params, headers=headers)
            
            print("\n=== WHAT THE API SHOULD RETURN ===")
            
            # Instead, let's call the backend function directly
            from location_api import location_bp
            from flask import request
            from models import Location
            from database import db
            
            # Simulate the backend query that happens in get_locations
            warehouse_id = 'DEFAULT'
            
            print(f"Querying database for warehouse_id='{warehouse_id}'...")
            
            # This is the exact query from the API
            query = Location.query.filter_by(warehouse_id=warehouse_id)
            
            # Apply the same ordering
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
            
            # Get the first 20 locations (simulating per_page=100 but showing first 20)
            locations = query.limit(20).all()
            
            print(f"\nFound {len(locations)} locations:")
            print("First 20 locations that would be returned to frontend:")
            
            location_types = {}
            special_areas = []
            
            for i, loc in enumerate(locations, 1):
                location_types[loc.location_type] = location_types.get(loc.location_type, 0) + 1
                if loc.location_type in ['RECEIVING', 'STAGING', 'DOCK']:
                    special_areas.append(loc.code)
                    
                print(f"  {i:2d}. {loc.code} ({loc.location_type}) - Zone: {loc.zone}, Capacity: {loc.capacity}")
            
            print(f"\nLocation type summary:")
            for loc_type, count in location_types.items():
                print(f"  {loc_type}: {count}")
                
            print(f"\nSpecial areas found: {special_areas}")
            
            if not special_areas:
                print("\n❌ NO SPECIAL AREAS FOUND! This confirms the frontend issue.")
                print("The API is not returning special locations to the frontend.")
            else:
                print(f"\n✅ {len(special_areas)} special areas found. Frontend should be able to display them.")
            
            # Check what the frontend filtering logic would do
            print(f"\n=== FRONTEND FILTERING SIMULATION ===")
            special_locations = [loc for loc in locations if loc.location_type in ['RECEIVING', 'STAGING', 'DOCK']]
            print(f"After frontend client-side filtering: {len(special_locations)} special locations")
            
            for loc in special_locations:
                print(f"  - {loc.code} ({loc.location_type})")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    simulate_frontend_api_call()