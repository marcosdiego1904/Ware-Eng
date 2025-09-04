#!/usr/bin/env python3
"""
Test script to reproduce the template creation format config issue
Simulates the exact frontend->backend flow
"""

import os
import sys
import json
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_template_creation_with_format_config():
    """Test creating a template with format configuration through the API"""
    
    print("🧪 Testing Template Creation with Format Configuration")
    print("=" * 60)
    
    # First, we need to authenticate
    print("1. Authenticating...")
    
    login_data = {
        "username": "mtest",
        "password": "pass123"  # Replace with actual password
    }
    
    try:
        # Try to login
        login_response = requests.post(
            'http://localhost:5000/api/v1/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        token = login_response.json().get('token')
        if not token:
            print("❌ No token received from login")
            return False
            
        print(f"✅ Authentication successful, token: {token[:20]}...")
        
    except requests.ConnectionError:
        print("❌ Cannot connect to backend server at localhost:5000")
        print("Make sure the Flask server is running")
        return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # 2. Simulate format detection (like the frontend does)
    print("\n2. Testing format detection...")
    
    format_detection_data = {
        "examples": ["010A", "325B", "245D", "100C", "005A"]
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        detect_response = requests.post(
            'http://localhost:5000/api/v1/templates/detect-format',
            json=format_detection_data,
            headers=headers
        )
        
        if detect_response.status_code != 200:
            print(f"❌ Format detection failed: {detect_response.status_code}")
            print(f"Response: {detect_response.text}")
            return False
        
        detection_result = detect_response.json()
        print(f"✅ Format detection successful:")
        print(f"   Success: {detection_result.get('success', False)}")
        print(f"   Format Config: {detection_result.get('format_config', 'None')}")
        
        # Extract format configuration
        format_config = detection_result.get('format_config')
        if not format_config:
            print("⚠️  No format config returned from detection")
            
    except Exception as e:
        print(f"❌ Format detection error: {e}")
        return False
    
    # 3. Create template with format configuration
    print("\n3. Creating template with format configuration...")
    
    # This simulates exactly what the frontend sends
    template_data = {
        # Basic Information
        "name": "Test_Format_Template",
        "description": "Test template with format configuration",
        "category": "CUSTOM",
        "industry": "TEST",
        "tags": ["test", "format"],
        "visibility": "PRIVATE",
        
        # Structure Configuration
        "num_aisles": 4,
        "racks_per_aisle": 2,
        "positions_per_rack": 50,
        "levels_per_position": 4,
        "level_names": "ABCD",
        "default_pallet_capacity": 1,
        "bidimensional_racks": False,
        
        # Special Areas
        "receiving_areas": [{"code": "RECEIVING", "type": "RECEIVING", "capacity": 10, "zone": "DOCK"}],
        "staging_areas": [],
        "dock_areas": [],
        
        # Location Format Configuration (this is the critical part)
        "format_config": format_config,  # From detection API
        "format_pattern_name": "position_level",
        "format_examples": ["010A", "325B", "245D", "100C", "005A"]
    }
    
    print(f"📝 Template data being sent:")
    print(f"   format_config: {template_data['format_config']}")
    print(f"   format_pattern_name: {template_data['format_pattern_name']}")
    print(f"   format_examples: {template_data['format_examples']}")
    
    try:
        create_response = requests.post(
            'http://localhost:5000/api/v1/standalone-templates/create',
            json=template_data,
            headers=headers
        )
        
        if create_response.status_code != 200:
            print(f"❌ Template creation failed: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
        
        created_template = create_response.json()
        template_info = created_template.get('template', {})
        
        print(f"✅ Template created successfully:")
        print(f"   Template ID: {template_info.get('id')}")
        print(f"   Template Name: {template_info.get('name')}")
        print(f"   Template Code: {template_info.get('template_code')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template creation error: {e}")
        return False

def test_format_detection_only():
    """Test just the format detection API"""
    
    print("\n🔍 Testing Format Detection API Only")
    print("=" * 60)
    
    # Test without authentication first
    format_detection_data = {
        "examples": ["010A", "325B", "245D", "100C", "005A"]
    }
    
    try:
        # This should fail due to missing auth
        detect_response = requests.post(
            'http://localhost:5000/api/v1/templates/detect-format',
            json=format_detection_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Format detection without auth: {detect_response.status_code}")
        if detect_response.status_code == 401:
            print("✅ Correctly requires authentication")
        else:
            print(f"Response: {detect_response.text}")
            
    except requests.ConnectionError:
        print("❌ Cannot connect to backend server")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("🧪 Template Creation Format Config Test Suite")
    print("Testing the complete frontend->backend flow for template creation")
    print()
    
    # Test format detection
    format_detection_success = test_format_detection_only()
    
    # Test full template creation flow
    if format_detection_success:
        template_creation_success = test_template_creation_with_format_config()
        
        if template_creation_success:
            print("\n🎉 SUCCESS: Template creation flow completed successfully!")
            print("Check the backend logs for [STANDALONE_TEMPLATE_DEBUG] messages")
            print("This will show exactly what format configuration data is being received and saved")
        else:
            print("\n❌ FAILED: Template creation flow failed")
            print("Check the backend logs for error details")
    else:
        print("\n❌ FAILED: Cannot test template creation without format detection working")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Check backend server logs for debugging output")
    print("2. Verify the format configuration is being saved correctly")
    print("3. Check the database to confirm templates have format_config data")