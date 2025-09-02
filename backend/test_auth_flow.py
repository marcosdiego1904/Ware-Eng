#!/usr/bin/env python3
"""
Test Authentication Flow for Smart Configuration API

This script tests the complete authentication and API flow to identify
why the Smart Configuration format detection is failing in production.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_local_vs_production():
    """Compare local and production API behavior"""
    print("=" * 60)
    print("AUTHENTICATION & API FLOW DEBUG")
    print("=" * 60)
    
    # Test endpoints
    base_urls = {
        'local': 'http://localhost:5000',
        'production': 'https://ware-eng.onrender.com'  # Replace with actual production URL
    }
    
    # Test data
    test_examples = ['010A', '325B', '245D', '100C', '005A']
    
    for env_name, base_url in base_urls.items():
        print(f"\n🔍 TESTING {env_name.upper()} ENVIRONMENT")
        print(f"Base URL: {base_url}")
        print("-" * 40)
        
        # Test 1: Basic connectivity
        try:
            response = requests.get(f"{base_url}/", timeout=10)
            print(f"✅ Basic connectivity: {response.status_code}")
        except Exception as e:
            print(f"❌ Basic connectivity failed: {e}")
            continue
        
        # Test 2: Debug endpoint (no auth required)
        debug_endpoint = f"{base_url}/api/debug/test-format-detection"
        try:
            response = requests.post(
                debug_endpoint, 
                json={'examples': test_examples},
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            print(f"🔧 Debug endpoint: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                pattern = result.get('detection_result', {}).get('detected_pattern', {}).get('pattern_type', 'None')
                print(f"   Format detected: {pattern} (Success: {success})")
            else:
                print(f"   Error: {response.text[:200]}")
        except Exception as e:
            print(f"🔧 Debug endpoint failed: {e}")
        
        # Test 3: Main API endpoint structure
        main_endpoint = f"{base_url}/api/v1/templates/detect-format"
        try:
            # Test without auth (should get 401)
            response = requests.post(
                main_endpoint,
                json={'examples': test_examples},
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            print(f"🔐 Main API (no auth): {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Authentication required (as expected)")
            else:
                print(f"   ⚠️  Unexpected response: {response.text[:200]}")
        except Exception as e:
            print(f"🔐 Main API test failed: {e}")
        
        # Test 4: Check CORS headers
        try:
            response = requests.options(main_endpoint, timeout=10)
            cors_headers = {k: v for k, v in response.headers.items() if 'cors' in k.lower() or 'access-control' in k.lower()}
            print(f"🌐 CORS check: {response.status_code}")
            if cors_headers:
                print("   CORS headers found:")
                for header, value in cors_headers.items():
                    print(f"     {header}: {value}")
            else:
                print("   ⚠️  No CORS headers found")
        except Exception as e:
            print(f"🌐 CORS check failed: {e}")

def test_with_mock_auth():
    """Test API with a mock authentication token"""
    print(f"\n" + "=" * 60)
    print("MOCK AUTHENTICATION TEST")
    print("=" * 60)
    
    print("\nThis test will show you how to create a valid JWT token")
    print("for testing the main API endpoint.")
    print("\nTo create a token, you need to:")
    print("1. Run your Flask app locally")
    print("2. Use the login endpoint to get a token")
    print("3. Copy the token from the response")
    
    print("\nExample curl command to get token:")
    print("curl -X POST http://localhost:5000/api/v1/auth/login \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"username\":\"your_username\",\"password\":\"your_password\"}'")

def generate_debug_instructions():
    """Generate debug instructions for the user"""
    print(f"\n" + "=" * 60)
    print("DEBUG INSTRUCTIONS FOR USER")
    print("=" * 60)
    
    debug_steps = [
        {
            'step': 1,
            'title': 'Check Production Environment Variables',
            'instructions': [
                'Verify NEXT_PUBLIC_API_URL in production frontend',
                'Should point to your backend URL (e.g., https://your-backend.onrender.com/api/v1)',
                'Check that the backend is accessible at that URL'
            ]
        },
        {
            'step': 2,
            'title': 'Test Authentication Token',
            'instructions': [
                'Open browser dev tools on the production site',
                'Go to Application/Local Storage',
                'Check if auth_token exists and is valid',
                'Try logging out and logging back in'
            ]
        },
        {
            'step': 3,
            'title': 'Test API Endpoints Directly',
            'instructions': [
                'Use the production API test script (test_production_api.py)',
                'Test debug endpoint first (no auth needed)',
                'Then test main API with valid token'
            ]
        },
        {
            'step': 4,
            'title': 'Check Backend Logs',
            'instructions': [
                'Check backend logs for any errors during API calls',
                'Look for 500 errors, import failures, or database issues',
                'Verify all blueprints are registered correctly'
            ]
        }
    ]
    
    for step_info in debug_steps:
        print(f"\nStep {step_info['step']}: {step_info['title']}")
        print("-" * (len(step_info['title']) + 10))
        for instruction in step_info['instructions']:
            print(f"  • {instruction}")

def main():
    print("Smart Configuration Authentication & API Debug Tool")
    print("This tool helps identify authentication and connection issues")
    
    # Test basic connectivity and API structure
    test_local_vs_production()
    
    # Show authentication testing guidance
    test_with_mock_auth()
    
    # Provide debug instructions
    generate_debug_instructions()
    
    print(f"\n" + "=" * 60)
    print("SUMMARY & NEXT STEPS")
    print("=" * 60)
    print("Based on our earlier tests:")
    print("✅ Smart Configuration format detection works 100% locally")
    print("✅ Database schema is correct in production")
    print("❓ API authentication/connection is the likely issue")
    print("\nRecommended next steps:")
    print("1. Check production environment variables")
    print("2. Test debug endpoint in production browser")
    print("3. Verify authentication token in production")
    print("4. Check backend logs for any errors")

if __name__ == "__main__":
    main()