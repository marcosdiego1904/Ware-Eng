#!/usr/bin/env python3
"""
Test Production API Endpoints for Smart Configuration

This script tests both the main format detection API and debug endpoint
to identify why the UI is showing 400 Bad Request errors.
"""

import os
import sys
import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def setup_requests_session():
    """Setup requests session with retries and proper headers"""
    session = requests.Session()
    
    # Setup retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "POST", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set default headers
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'SmartConfig-Test-Script/1.0'
    })
    
    return session

def get_production_url():
    """Get the production URL from environment or user input"""
    # Try to get from environment first
    prod_url = os.getenv('PRODUCTION_URL')
    
    if not prod_url:
        print("Production URL not found in environment.")
        print("Please enter your production URL (e.g., https://yourapp.onrender.com):")
        prod_url = input().strip()
        
        if not prod_url.startswith(('http://', 'https://')):
            prod_url = 'https://' + prod_url
    
    return prod_url.rstrip('/')

def get_auth_token():
    """Get authentication token for API calls"""
    print("\nAuthentication required for main API endpoint.")
    print("Please provide your JWT token (from browser dev tools or login):")
    token = input().strip()
    return token

def test_debug_endpoint(session, base_url):
    """Test the debug format detection endpoint (no auth required)"""
    print("\n" + "="*60)
    print("TESTING DEBUG ENDPOINT")
    print("="*60)
    
    endpoint = f"{base_url}/api/debug/test-format-detection"
    
    test_cases = [
        {
            'name': 'Position+Level Format',
            'examples': ['010A', '325B', '245D', '100C', '005A']
        },
        {
            'name': 'Standard Format',
            'examples': ['A01-R02-P15', 'B05-R01-P03', 'C12-R03-P25']
        }
    ]
    
    for test_case in test_cases:
        print(f"\n Testing: {test_case['name']}")
        print(f"   Examples: {test_case['examples']}")
        
        try:
            response = session.post(endpoint, json={'examples': test_case['examples']}, timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    pattern = result.get('detection_result', {}).get('detected_pattern')
                    if pattern:
                        print(f"   SUCCESS: Detected {pattern.get('pattern_type')} with {pattern.get('confidence', 0):.1%} confidence")
                    else:
                        print(f"   PARTIAL: No pattern detected")
                else:
                    print(f"   FAILED: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ERROR: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   CONNECTION ERROR: {e}")

def test_main_api_endpoint(session, base_url, token):
    """Test the main API endpoint (requires auth)"""
    print("\n" + "="*60)
    print("TESTING MAIN API ENDPOINT")
    print("="*60)
    
    endpoint = f"{base_url}/api/v1/templates/detect-format"
    
    # Add authorization header
    session.headers.update({
        'Authorization': f'Bearer {token}'
    })
    
    test_cases = [
        {
            'name': 'Position+Level Format',
            'examples': ['010A', '325B', '245D', '100C', '005A']
        },
        {
            'name': 'Standard Format',
            'examples': ['A01-R02-P15', 'B05-R01-P03', 'C12-R03-P25']
        }
    ]
    
    for test_case in test_cases:
        print(f"\n Testing: {test_case['name']}")
        print(f"   Examples: {test_case['examples']}")
        
        payload = {
            'examples': test_case['examples'],
            'warehouse_context': {
                'name': 'Test Warehouse',
                'description': 'Testing Smart Configuration'
            }
        }
        
        try:
            response = session.post(endpoint, json=payload, timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    detection = result.get('detection_result', {})
                    pattern = detection.get('detected_pattern')
                    if pattern:
                        print(f"   SUCCESS: Detected {pattern.get('pattern_type')} with {detection.get('confidence', 0):.1%} confidence")
                        print(f"   Format Config: {bool(result.get('format_config'))}")
                    else:
                        print(f"   PARTIAL: No pattern detected")
                else:
                    print(f"   FAILED: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ERROR: {response.text[:500]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   CONNECTION ERROR: {e}")

def main():
    print("Smart Configuration Production API Test")
    print("=" * 60)
    
    # Setup
    session = setup_requests_session()
    base_url = get_production_url()
    
    print(f"Testing against: {base_url}")
    
    # Test debug endpoint first (no auth needed)
    test_debug_endpoint(session, base_url)
    
    # Test main API endpoint (requires auth)
    print("\n" + "="*60)
    print("MAIN API ENDPOINT TEST")
    print("="*60)
    
    try_main_api = input("\nTest main API endpoint? (requires auth token) [y/N]: ").lower()
    
    if try_main_api == 'y':
        token = get_auth_token()
        if token:
            test_main_api_endpoint(session, base_url, token)
        else:
            print("No token provided, skipping main API test")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()