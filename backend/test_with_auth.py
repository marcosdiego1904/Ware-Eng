#!/usr/bin/env python3
"""
Test locations API with authentication
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

def create_test_token():
    """Create a test JWT token"""
    with app.app_context():
        # Get the first user
        user = User.query.first()
        if not user:
            print("No users found!")
            return None
            
        print(f"Creating token for user: {user.username} (ID: {user.id})")
        
        # Create JWT token
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        return token, user

def test_api_with_auth():
    """Test the API with authentication"""
    token, user = create_test_token()
    if not token:
        return
        
    print(f"Generated token: {token[:50]}...")
    
    # Test API call
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            'http://localhost:5000/api/v1/locations?warehouse_id=DEFAULT&per_page=10',
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            locations = data.get('locations', [])
            print(f"Found {len(locations)} locations")
            
            if locations:
                print("First few locations:")
                for loc in locations[:5]:
                    print(f"  - {loc['code']} ({loc['location_type']}) - Zone: {loc.get('zone', 'N/A')}")
                
                # Count special locations
                special = [loc for loc in locations if loc['location_type'] in ['RECEIVING', 'STAGING', 'DOCK']]
                print(f"\nSpecial locations: {len(special)}")
                for loc in special:
                    print(f"  - {loc['code']} ({loc['location_type']}) - Zone: {loc.get('zone', 'N/A')}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Make sure Flask is running on localhost:5000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_api_with_auth()