#!/usr/bin/env python3
"""
Test the new user warehouse API
"""

import sys
sys.path.append('src')

from app import app
from database import db
from core_models import User
from flask_login import login_user
import json

def test_user_warehouse_api():
    """Test the user warehouse detection API"""
    print("TESTING USER WAREHOUSE API")
    print("=" * 40)
    
    with app.app_context():
        # Get a test user
        user = User.query.filter_by(username='marcosbarzola@devbymarcos.com').first()
        if not user:
            print("ERROR: Test user not found")
            return
        
        print(f"Testing with user: {user.username}")
        
        # Test the API endpoint directly
        with app.test_client() as client:
            # Create a request context and login the user
            with client.session_transaction() as sess:
                # Simulate user login session
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # Test the primary warehouse endpoint
            print("\nTesting /api/v1/user/warehouse endpoint:")
            response = client.get('/api/v1/user/warehouse')
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print("Response:")
                print(json.dumps(data, indent=2))
                
                if data['success']:
                    print(f"\nSUCCESS: Primary warehouse detected as {data['primary_warehouse']}")
                    print(f"Detection method: {data['detection_method']}")
                    print(f"Special areas: {data['special_areas_count']}")
                else:
                    print(f"FAILED: {data.get('error', 'Unknown error')}")
            else:
                print(f"ERROR: HTTP {response.status_code}")
                print(response.get_data(as_text=True))
            
            # Test the all warehouses endpoint
            print(f"\nTesting /api/v1/user/warehouses endpoint:")
            response = client.get('/api/v1/user/warehouses')
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print("All user warehouses:")
                for warehouse in data.get('warehouses', []):
                    print(f"  - {warehouse['warehouse_id']}: {warehouse['warehouse_name']} ({warehouse['special_areas_count']} special areas)")

if __name__ == "__main__":
    test_user_warehouse_api()