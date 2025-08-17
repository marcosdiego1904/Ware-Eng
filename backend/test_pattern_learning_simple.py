#!/usr/bin/env python3
"""
Simple test for pattern learning system
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_pattern_learning():
    """Test pattern learning with manual examples"""
    
    print("=== TESTING PATTERN LEARNING SYSTEM ===")
    
    from pattern_learning_system import LocationPatternLearner
    
    # Initialize learner
    learner = LocationPatternLearner()
    
    # Manually train some patterns
    print("\\nStep 1: Training with manual examples...")
    
    training_examples = [
        # (user_input, database_match, warehouse_id, confidence)
        ('2-1-11B', '02-01-011B', 'USER_TESTF', 0.95),
        ('01-1-007B', '01-01-007B', 'USER_TESTF', 0.90),
        ('RECV-1', 'RECV-001', 'USER_TESTF', 0.85),
        ('STAGE-02', 'STAGE-002', 'USER_TESTF', 0.88),
        ('1-1-1A', '01-01-001A', 'USER_TESTF', 0.92),
    ]
    
    for user_input, db_match, warehouse, confidence in training_examples:
        learner.learn_from_successful_match(user_input, db_match, warehouse, confidence)
        print(f"  Learned: '{user_input}' -> '{db_match}'")
    
    # Test pattern suggestions
    print("\\nStep 2: Testing pattern suggestions...")
    
    test_inputs = ['3-2-15C', 'RECV-5', '02-1-001B']
    
    for test_input in test_inputs:
        print(f"\\nTesting: '{test_input}'")
        suggestions = learner.suggest_location_matches(test_input, 'USER_TESTF')
        
        if suggestions:
            for suggestion, confidence in suggestions[:3]:
                print(f"  -> '{suggestion}' (confidence: {confidence:.2f})")
        else:
            print("  -> No suggestions")
    
    # Show statistics
    print("\\nStep 3: Learning statistics...")
    stats = learner.get_learning_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test transformation extraction
    print("\\nStep 4: Testing transformation extraction...")
    test_transformations = [
        ('2-1-11B', '02-01-011B'),
        ('RECV-1', 'RECV-001'),
        ('EXACT-MATCH', 'EXACT-MATCH')
    ]
    
    for input_loc, output_loc in test_transformations:
        transformation = learner._extract_transformation_pattern(input_loc, output_loc)
        print(f"  '{input_loc}' -> '{output_loc}': {transformation}")
    
    return True

def test_regex_patterns():
    """Test regex patterns are working correctly"""
    
    print("\\n=== TESTING REGEX PATTERNS ===")
    
    test_cases = [
        (r'^\\d{1,2}-\\d{1,2}-\\d{1,3}[A-Z]$', ['2-1-11B', '02-01-011B', '1-1-1A']),
        (r'^[A-Z]+-\\d+$', ['RECV-1', 'STAGE-02', 'DOCK-5']),
        (r'^\\d{2}-\\d{2}-\\d{3}[A-Z]$', ['02-01-011B', '01-01-001A'])
    ]
    
    for pattern, test_strings in test_cases:
        print(f"\\nPattern: {pattern}")
        for test_string in test_strings:
            match = re.match(pattern, test_string)
            print(f"  '{test_string}': {'MATCH' if match else 'NO MATCH'}")

def main():
    """Run pattern learning tests"""
    
    print("PATTERN LEARNING VALIDATION")
    print("=" * 40)
    
    # Test regex patterns first
    test_regex_patterns()
    
    # Test pattern learning
    learning_success = test_pattern_learning()
    
    print("\\n" + "=" * 40)
    print(f"Pattern Learning Status: {'SUCCESS' if learning_success else 'FAILED'}")
    
    return learning_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)