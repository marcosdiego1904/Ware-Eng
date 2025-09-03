#!/usr/bin/env python3
"""
Test Smart Configuration Integration with Virtual Location Engine
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from virtual_location_engine import VirtualLocationEngine
from smart_format_detector import SmartFormatDetector

def test_smart_configuration_integration():
    """Test that VirtualLocationEngine can validate using Smart Configuration patterns"""
    
    print("=" * 60)
    print("TESTING SMART CONFIGURATION INTEGRATION")
    print("=" * 60)
    
    # Step 1: Create Smart Configuration format for position+level pattern
    print("\n1. Creating Smart Configuration format...")
    detector = SmartFormatDetector()
    examples = ['010A', '325B', '245D', '156C', '087A', '006B']
    detection_result = detector.detect_format(examples)
    
    format_config = detection_result['detected_pattern']
    print(f"   Format detected: {format_config['pattern_type']}")
    print(f"   Pattern: {format_config['regex_pattern']}")
    print(f"   Confidence: {format_config['confidence']:.2%}")
    
    # Step 2: Create warehouse config with Smart Configuration format
    print("\n2. Creating warehouse config with Smart Configuration...")
    warehouse_config = {
        'warehouse_id': 'TEST_SMART',
        'num_aisles': 2,
        'racks_per_aisle': 2, 
        'positions_per_rack': 999,  # Allow up to position 999
        'levels_per_position': 4,
        'level_names': 'ABCD',
        'default_pallet_capacity': 1,
        'receiving_areas': [{'code': 'RECV-01', 'capacity': 10}],
        'staging_areas': [{'code': 'STAGE-01', 'capacity': 5}],
        'dock_areas': [{'code': 'DOCK-01', 'capacity': 2}],
        'location_format_config': format_config  # NEW: Smart Configuration
    }
    
    # Step 3: Create VirtualLocationEngine with Smart Configuration
    print("\n3. Initializing VirtualLocationEngine with Smart Configuration...")
    engine = VirtualLocationEngine(warehouse_config)
    
    # Step 4: Test validation of position+level format locations
    print("\n4. Testing location validation...")
    test_locations = [
        ('006B', True, 'Valid position+level location'),
        ('010A', True, 'Valid position+level location'), 
        ('325B', True, 'Valid position+level location'),
        ('245D', True, 'Valid position+level location'),
        ('999A', True, 'Max position location'),
        ('000A', False, 'Position 0 is invalid'),
        ('123E', False, 'Level E not available (only A-D)'),
        ('RECV-01', True, 'Special area should be valid'),
        ('INVALID', False, 'Random string should be invalid')
    ]
    
    results = []
    for location, expected_valid, description in test_locations:
        is_valid, reason = engine.validate_location(location)
        status = "✅ PASS" if (is_valid == expected_valid) else "❌ FAIL"
        results.append((location, is_valid, expected_valid, status, reason))
        print(f"   {location:10} | {status} | Expected: {expected_valid:5} | Got: {is_valid:5} | {reason}")
    
    # Step 5: Summary
    print("\n5. Test Summary:")
    passed = sum(1 for r in results if "PASS" in r[3])
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"   Tests passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if passed == total:
        print("\n🎉 SUCCESS: Smart Configuration integration is working!")
        print("   VirtualLocationEngine now validates custom format patterns correctly.")
    else:
        print("\n⚠️ ISSUES FOUND: Some tests failed")
        failed_tests = [r for r in results if "FAIL" in r[3]]
        for location, is_valid, expected_valid, status, reason in failed_tests:
            print(f"   FAILED: {location} - expected {expected_valid}, got {is_valid}")
    
    return passed == total

if __name__ == "__main__":
    success = test_smart_configuration_integration()
    sys.exit(0 if success else 1)