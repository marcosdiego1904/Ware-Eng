#!/usr/bin/env python3
"""
Comprehensive debugging of the special locations issue
Tests the entire flow from database to API response
"""

import sys
sys.path.append('src')
import jwt
import requests
import json
from datetime import datetime, timedelta

from app import app
from core_models import User
from database import db
from models import Location, WarehouseConfig

def test_complete_flow():
    """Test the complete flow from database to API"""
    
    print("=" * 80)
    print("COMPREHENSIVE SPECIAL LOCATIONS DEBUG")
    print("=" * 80)
    
    with app.app_context():
        # Step 1: Database verification
        print("\n1. DATABASE VERIFICATION:")
        print("-" * 40)
        
        # Check warehouse configs
        configs = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').all()
        print(f"Found {len(configs)} warehouse configs for DEFAULT:")
        for config in configs:
            print(f"  - Config ID: {config.id}, Name: {config.warehouse_name}")
            print(f"    Receiving areas: {config.receiving_areas}")
            print(f"    Staging areas: {config.staging_areas}")
            print(f"    Dock areas: {config.dock_areas}")
        
        # Check locations in database
        all_locations = Location.query.filter_by(warehouse_id='DEFAULT').count()
        special_locations = Location.query.filter(
            Location.warehouse_id == 'DEFAULT',
            Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
        ).all()
        
        print(f"\nTotal DEFAULT locations in DB: {all_locations}")
        print(f"Special locations in DB: {len(special_locations)}")
        for loc in special_locations:
            print(f"  - {loc.code} ({loc.location_type}) Zone:{loc.zone} Active:{loc.is_active}")
        
        # Step 2: Authentication test
        print("\n2. AUTHENTICATION TEST:")
        print("-" * 40)
        
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            print("ERROR: testuser not found!")
            return
        
        print(f"Test user found: {test_user.username} (ID: {test_user.id})")
        
        # Create token
        payload = {
            'user_id': test_user.id,
            'username': test_user.username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        print(f"Token created: {token[:30]}...")
        
        # Step 3: API endpoint test
        print("\n3. API ENDPOINT TEST:")
        print("-" * 40)
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test different API calls that frontend might make
        test_urls = [
            'http://localhost:5000/api/v1/locations?warehouse_id=DEFAULT&per_page=100',
            'http://localhost:5000/api/v1/locations?warehouse_id=DEFAULT&page=1&per_page=50',
            'http://localhost:5000/api/v1/locations?warehouse_id=DEFAULT'
        ]
        
        for url in test_urls:
            print(f"\nTesting: {url}")
            try:
                response = requests.get(url, headers=headers)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    locations = data.get('locations', [])
                    special = [loc for loc in locations if loc['location_type'] in ['RECEIVING', 'STAGING', 'DOCK']]
                    
                    print(f"Total locations returned: {len(locations)}")
                    print(f"Special locations returned: {len(special)}")
                    
                    if special:
                        print("Special locations in API response:")
                        for loc in special[:5]:  # Show first 5
                            print(f"  - {loc['code']} ({loc['location_type']}) Zone:{loc.get('zone', 'N/A')}")
                    else:
                        print("WARNING: No special locations in API response!")
                        if locations:
                            print("First 5 locations returned:")
                            for loc in locations[:5]:
                                print(f"  - {loc['code']} ({loc['location_type']}) Zone:{loc.get('zone', 'N/A')}")
                else:
                    print(f"ERROR: {response.text}")
                    
            except Exception as e:
                print(f"ERROR: {e}")
        
        # Step 4: Frontend simulation
        print("\n4. FRONTEND SIMULATION:")
        print("-" * 40)
        
        # Simulate the exact API call the frontend should make
        frontend_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # This is the exact call the frontend location store should make
        frontend_url = 'http://localhost:5000/api/v1/locations'
        frontend_params = {
            'warehouse_id': 'DEFAULT',
            'page': '1',
            'per_page': '100'
        }
        
        print(f"Frontend URL: {frontend_url}")
        print(f"Frontend params: {frontend_params}")
        
        try:
            response = requests.get(frontend_url, params=frontend_params, headers=frontend_headers)
            print(f"Frontend simulation status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response structure: {list(data.keys())}")
                
                locations = data.get('locations', [])
                pagination = data.get('pagination', {})
                summary = data.get('summary', {})
                
                print(f"Locations array length: {len(locations)}")
                print(f"Pagination: {pagination}")
                print(f"Summary: {summary}")
                
                # Filter like frontend does
                special_frontend = [loc for loc in locations if loc['location_type'] in ['RECEIVING', 'STAGING', 'DOCK']]
                print(f"Special locations after frontend filtering: {len(special_frontend)}")
                
                if special_frontend:
                    print("SUCCESS: Special locations would appear in frontend!")
                    for loc in special_frontend:
                        print(f"  ✓ {loc['code']} ({loc['location_type']})")
                else:
                    print("PROBLEM: No special locations after frontend filtering")
                    print("Investigating why...")
                    
                    # Show location types in response
                    location_types = {}
                    for loc in locations:
                        loc_type = loc.get('location_type', 'UNKNOWN')
                        location_types[loc_type] = location_types.get(loc_type, 0) + 1
                    print(f"Location types in response: {location_types}")
            else:
                print(f"Frontend simulation failed: {response.text}")
                
        except Exception as e:
            print(f"Frontend simulation error: {e}")

        # Step 5: Configuration check
        print("\n5. CONFIGURATION CHECK:")
        print("-" * 40)
        
        # Check if there are any configuration issues
        config = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').first()
        if config:
            print(f"Active config: {config.warehouse_name} (ID: {config.id})")
            print(f"Created: {config.created_at}")
            print(f"Updated: {config.updated_at}")
            
            # Parse special areas from config
            def parse_areas(area_data):
                if not area_data:
                    return []
                if isinstance(area_data, str):
                    try:
                        return json.loads(area_data)
                    except:
                        return []
                return area_data if isinstance(area_data, list) else []
            
            receiving = parse_areas(config.receiving_areas)
            staging = parse_areas(config.staging_areas)
            dock = parse_areas(config.dock_areas)
            
            print(f"Config receiving areas: {len(receiving)}")
            print(f"Config staging areas: {len(staging)}")  
            print(f"Config dock areas: {len(dock)}")
            
            # Verify locations match config
            expected_codes = set()
            for area in receiving + staging + dock:
                expected_codes.add(f"DEFAULT_{area['code']}")
            
            actual_codes = set(loc.code for loc in special_locations)
            
            print(f"Expected location codes: {sorted(expected_codes)}")
            print(f"Actual location codes: {sorted(actual_codes)}")
            
            if expected_codes == actual_codes:
                print("✓ Location codes match configuration")
            else:
                missing = expected_codes - actual_codes
                extra = actual_codes - expected_codes
                if missing:
                    print(f"✗ Missing locations: {missing}")
                if extra:
                    print(f"✗ Extra locations: {extra}")
        else:
            print("ERROR: No warehouse config found for DEFAULT!")

if __name__ == '__main__':
    test_complete_flow()