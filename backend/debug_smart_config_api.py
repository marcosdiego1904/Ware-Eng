#!/usr/bin/env python3
"""
Debug Smart Configuration API Issues

This script tests the Smart Configuration format detection to identify
why the API is returning "No pattern detected" for clear patterns.
"""

import os
import sys
import json

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_format_detection():
    """Test the format detection with the exact examples from the UI"""
    print("=" * 60)
    print("SMART CONFIGURATION DEBUG - FORMAT DETECTION")
    print("=" * 60)
    
    try:
        from app import app
        from smart_format_detector import SmartFormatDetector
        
        with app.app_context():
            detector = SmartFormatDetector()
            
            # Test cases from your UI screenshots
            test_cases = [
                {
                    'name': 'Position+Level Format (From Screenshot 1)',
                    'examples': ['020A', '124C', '324D']
                },
                {
                    'name': 'Position+Level Format (From Screenshot 2)', 
                    'examples': ['010A', '325B', '245D', '100C', '005A']
                },
                {
                    'name': 'Standard Format (From Screenshot 3)',
                    'examples': ['A01-R02-P15', 'B05-R01-P03', 'C12-R03-P25']
                },
                {
                    'name': 'Expected Working Examples',
                    'examples': ['010A', '325B', '245D', '156C', '087A']
                }
            ]
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n{i}. Testing: {test_case['name']}")
                print(f"   Examples: {test_case['examples']}")
                
                try:
                    # Test with the exact method used by the API
                    result = detector.detect_format(test_case['examples'])
                    
                    print(f"   Result: {json.dumps(result, indent=2)[:200]}...")
                    
                    if result.get('detected_pattern'):
                        pattern = result['detected_pattern']
                        print(f"   SUCCESS: Detected {pattern.get('pattern_type')} with {pattern.get('confidence', 0):.1%} confidence")
                    else:
                        print(f"   FAILED: No pattern detected")
                        print(f"   Confidence: {result.get('confidence', 0)}")
                        
                except Exception as e:
                    print(f"   ERROR: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"\n" + "=" * 60)
            print("TESTING API ENDPOINT DIRECTLY")
            print("=" * 60)
            
            # Test the actual API endpoint
            from template_api import detect_location_format
            from flask import Flask
            from unittest.mock import Mock
            
            # Create a mock request for testing
            test_app = Flask(__name__)
            
            with test_app.test_request_context(
                '/api/templates/detect-format',
                method='POST',
                json={'examples': ['010A', '325B', '245D', '100C', '005A']}
            ):
                try:
                    # Mock current_user
                    mock_user = Mock()
                    mock_user.id = 1
                    
                    # This should be the actual API call
                    from flask import request
                    print(f"Request JSON: {request.get_json()}")
                    
                    # Call the API endpoint function directly
                    response = detect_location_format(mock_user)
                    print(f"API Response: {response}")
                    
                except Exception as api_error:
                    print(f"API Error: {api_error}")
                    import traceback
                    traceback.print_exc()
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

def check_api_endpoint():
    """Check if the API endpoint is accessible"""
    print(f"\n" + "=" * 60)
    print("API ENDPOINT ACCESSIBILITY CHECK")
    print("=" * 60)
    
    try:
        from template_api import template_bp
        
        print("Template blueprint available: YES")
        
        # Check if detect_location_format endpoint exists
        endpoints = []
        for rule in template_bp.url_map.iter_rules():
            if 'detect-format' in rule.rule:
                endpoints.append(f"{rule.rule} [{', '.join(rule.methods)}]")
        
        if endpoints:
            print(f"Format detection endpoints found:")
            for endpoint in endpoints:
                print(f"  - {endpoint}")
        else:
            print("No format detection endpoints found!")
            
        # List all template endpoints
        print(f"\nAll template endpoints:")
        for rule in template_bp.url_map.iter_rules():
            if rule.endpoint.startswith('template'):
                print(f"  - {rule.rule} [{', '.join(rule.methods)}] -> {rule.endpoint}")
        
    except Exception as e:
        print(f"Endpoint check failed: {e}")

if __name__ == "__main__":
    test_format_detection()
    check_api_endpoint()