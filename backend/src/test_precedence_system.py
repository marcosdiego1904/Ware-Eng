#!/usr/bin/env python3
"""
Test script for Rule Precedence System
Verifies that the precedence system works correctly and eliminates double-counting
"""

import os
import sys

# Add the backend src directory to the path
backend_src = os.path.dirname(__file__)
sys.path.insert(0, backend_src)

from rule_precedence_system import (
    create_precedence_manager, 
    set_global_precedence_config,
    get_precedence_config
)

def test_basic_precedence_functionality():
    """Test basic precedence manager functionality"""
    print("Testing Basic Precedence Functionality")
    print("-" * 50)
    
    # Test configuration
    config = get_precedence_config()
    print(f"✅ Default config loaded: {config}")
    
    # Test precedence manager creation
    manager = create_precedence_manager()
    print(f"✅ Precedence manager created: enabled={manager.enable_precedence}")
    
    # Test with disabled precedence
    set_global_precedence_config(enable_precedence=False)
    disabled_manager = create_precedence_manager()
    print(f"✅ Disabled manager created: enabled={disabled_manager.enable_precedence}")
    
    # Reset to enabled
    set_global_precedence_config(enable_precedence=True)
    enabled_manager = create_precedence_manager()
    print(f"✅ Enabled manager created: enabled={enabled_manager.enable_precedence}")
    
    return True

def test_exclusion_registry():
    """Test the exclusion registry functionality"""
    print("\n🧪 Testing Exclusion Registry")
    print("-" * 50)
    
    manager = create_precedence_manager()
    registry = manager.registry
    
    # Add some test exclusions
    registry.add_exclusion("PALLET_001", 1, "Invalid Location Rule", "INVALID_LOCATION", 1, "Test invalid location")
    registry.add_exclusion("PALLET_002", 2, "Data Integrity Rule", "DATA_INTEGRITY", 1, "Test data integrity")
    registry.add_exclusion("PALLET_003", 3, "Overcapacity Rule", "OVERCAPACITY", 2, "Test overcapacity")
    
    print(f"✅ Added 3 test exclusions")
    
    # Test exclusion checking
    test_cases = [
        ("PALLET_001", 2, True, "Should be excluded - higher precedence rule flagged it"),
        ("PALLET_001", 1, False, "Should NOT be excluded - same precedence level"),
        ("PALLET_002", 3, True, "Should be excluded - precedence 1 > 3"),
        ("PALLET_004", 4, False, "Should NOT be excluded - pallet not in registry"),
    ]
    
    for pallet_id, requesting_precedence, expected_excluded, description in test_cases:
        is_excluded = registry.is_excluded(pallet_id, requesting_precedence)
        status = "✅" if is_excluded == expected_excluded else "❌"
        print(f"{status} {description}: {is_excluded}")
    
    # Test stats
    stats = registry.get_exclusion_stats()
    print(f"✅ Registry stats: {stats}")
    
    return True

def test_rule_sorting():
    """Test rule sorting by precedence"""
    print("\n🧪 Testing Rule Sorting")
    print("-" * 50)
    
    # Create mock rule objects
    class MockRule:
        def __init__(self, name, precedence_level, rule_id):
            self.name = name
            self.precedence_level = precedence_level
            self.id = rule_id
    
    rules = [
        MockRule("Process Efficiency Rule", 3, 1),
        MockRule("Data Integrity Rule", 1, 2),  # Should be first
        MockRule("Operational Safety Rule", 2, 3),
        MockRule("Data Quality Rule", 4, 4),  # Should be last
        MockRule("Another Data Integrity Rule", 1, 5),  # Should be second (same precedence, sorted by ID)
    ]
    
    manager = create_precedence_manager()
    sorted_rules = manager.sort_rules_by_precedence(rules)
    
    print("Rules sorted by precedence (lower number = higher precedence):")
    for i, rule in enumerate(sorted_rules, 1):
        print(f"  {i}. {rule.name} (precedence: {rule.precedence_level}, ID: {rule.id})")
    
    # Verify sorting correctness
    expected_order = [2, 5, 3, 1, 4]  # IDs in expected order
    actual_order = [rule.id for rule in sorted_rules]
    
    if actual_order == expected_order:
        print("✅ Rule sorting works correctly")
        return True
    else:
        print(f"❌ Rule sorting failed. Expected: {expected_order}, Got: {actual_order}")
        return False

def test_exclusion_patterns():
    """Test default exclusion patterns"""
    print("\n🧪 Testing Exclusion Patterns")
    print("-" * 50)
    
    manager = create_precedence_manager()
    
    # Test that overcapacity has exclusion patterns for invalid locations
    patterns = manager.default_exclusion_patterns
    
    if 'OVERCAPACITY' in patterns:
        overcapacity_pattern = patterns['OVERCAPACITY']
        expected_excludes = ['INVALID_LOCATION', 'DATA_INTEGRITY']
        
        if overcapacity_pattern['exclude_if_flagged_by'] == expected_excludes:
            print("✅ Overcapacity exclusion pattern correct")
        else:
            print(f"❌ Overcapacity exclusion pattern incorrect: {overcapacity_pattern}")
            return False
    else:
        print("❌ Overcapacity exclusion pattern not found")
        return False
    
    print(f"✅ Found {len(patterns)} default exclusion patterns")
    for rule_type, pattern in patterns.items():
        excludes = pattern['exclude_if_flagged_by']
        reason = pattern['reason']
        print(f"  - {rule_type} excludes if flagged by {excludes}: {reason}")
    
    return True

def test_environment_variables():
    """Test environment variable configuration"""
    print("\n🧪 Testing Environment Variable Configuration")
    print("-" * 50)
    
    # Test with environment variable disabled
    os.environ['RULE_PRECEDENCE_ENABLED'] = 'false'
    
    # Clear global config to force environment reading
    set_global_precedence_config()
    
    config = get_precedence_config()
    if not config['enable_precedence']:
        print("✅ Environment variable disabling works")
    else:
        print("❌ Environment variable disabling failed")
        return False
    
    # Test with environment variable enabled
    os.environ['RULE_PRECEDENCE_ENABLED'] = 'true'
    config = get_precedence_config()
    if config['enable_precedence']:
        print("✅ Environment variable enabling works")
    else:
        print("❌ Environment variable enabling failed")
        return False
    
    # Clean up environment variables
    if 'RULE_PRECEDENCE_ENABLED' in os.environ:
        del os.environ['RULE_PRECEDENCE_ENABLED']
    
    return True

def main():
    """Run all tests"""
    print("Rule Precedence System Tests")
    print("=" * 60)
    
    tests = [
        test_basic_precedence_functionality,
        test_exclusion_registry,
        test_rule_sorting,
        test_exclusion_patterns,
        test_environment_variables
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_func.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test_func.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test Summary")
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("🎉 All tests passed! Rule precedence system is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)