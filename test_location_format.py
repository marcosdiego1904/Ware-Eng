#!/usr/bin/env python3
"""
Test script for enhanced location format intelligence.
Tests the new _parse_user_common method for handling various user formats.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from location_service import CanonicalLocationService

def test_location_formats():
    """Test various location formats to ensure proper conversion"""
    
    service = CanonicalLocationService()
    
    test_cases = [
        # Format: (input, expected_output, description)
        ("001A01", "01-01-001A", "User common format: position+level+rack"),
        ("001B02", "01-02-001B", "User common format: different rack"),  
        ("015C03", "01-03-015C", "User common format: 3-digit position"),
        ("A1-001", "01-01-001A", "User format: level+rack-position"),
        ("B2-015", "01-02-015B", "User format: different level and rack"),
        ("5A10", "01-10-005A", "Compact format: position+level+rack"),
        ("RECV-01", "RECV-01", "Special area: should remain unchanged"),
        ("01-01-001A", "01-01-001A", "Already canonical: should remain unchanged"),
        ("AISLE-02", "AISLE-02", "Special area: AISLE format"),
    ]
    
    print("Testing Enhanced Location Format Intelligence")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for input_format, expected, description in test_cases:
        try:
            result = service.to_canonical(input_format)
            status = "PASS" if result == expected else "FAIL"
            
            if result == expected:
                passed += 1
            else:
                failed += 1
                
            print(f"{status} | '{input_format}' -> '{result}' | Expected: '{expected}'")
            if result != expected:
                print(f"      Description: {description}")
                
        except Exception as e:
            failed += 1
            print(f"ERROR | '{input_format}' -> Exception: {e}")
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! Location format intelligence is working correctly.")
        return True
    else:
        print("Some tests failed. Check the implementation.")
        return False

if __name__ == "__main__":
    success = test_location_formats()
    sys.exit(0 if success else 1)