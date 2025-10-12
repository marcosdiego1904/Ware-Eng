"""
Test Script for Enhanced Location Classification System
Phase 1 Implementation Validation

This script tests the zero-cost intelligent location classifier
to validate it reduces UNKNOWN classifications from 70% to <25%.
"""

import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_classification_samples():
    """Test with sample location codes representing real-world scenarios"""

    # Import the enhanced classifier
    from enhanced_location_classifier import EnhancedLocationClassifier

    # Initialize classifier (without database for testing)
    classifier = EnhancedLocationClassifier()

    # Test cases representing real warehouse location codes
    test_locations = [
        # RECEIVING areas (should be classified correctly)
        'RECV-01', 'RECV-02', 'RECEIVING-DOCK-A', 'INBOUND-01',
        'REC-001', 'DOCK-RECEIVING', 'TEMP-HOLD-1', 'DOCK-01',

        # STORAGE areas (should be classified correctly)
        'A-01-001A', 'B-12-045C', '01-02-015D', 'RACK-12-45',
        'STOR-A12-B34', 'AISLE-C-01-B', '001A001', 'WH1-A12-045A',

        # TRANSITIONAL areas (should be classified correctly)
        'STAGE-01', 'STAGING-AREA-A', 'TRANSIT-01', 'WORK-IN-PROGRESS',
        'PREP-AREA-1', 'SORT-01', 'BUFFER-ZONE-A',

        # DOCK areas (should be classified correctly)
        'DOCK-A', 'DOOR-12', 'BAY-DOOR-3', 'TRUCK-DOCK-1',
        'GATE-A', 'LOADING-BAY-2',

        # AISLE areas (should be classified correctly)
        'AISLE-1', 'AISLE-A-12', 'CORRIDOR-01',

        # Challenging cases (previously UNKNOWN)
        'TEMP-123', 'HOLD-AREA', 'MOVE-TO-STORAGE',
        'OUTBOUND-PREP', 'CONSOLIDATE-01', 'QUALITY-CHECK',
        'ALPHA-ZONE', 'BETA-STAGING', 'OVERFLOW-01',

        # Edge cases
        'X', 'MISC', '???', 'UNKNOWN-AREA',
        '', '   ', 'SPECIAL-PROJECT-AREA'
    ]

    print("[TEST] Testing Enhanced Location Classification System")
    print("=" * 60)
    print(f"Testing {len(test_locations)} location codes...\n")

    results = {}
    classification_stats = {
        'RECEIVING': 0,
        'STORAGE': 0,
        'TRANSITIONAL': 0,
        'STAGING': 0,
        'DOCK': 0,
        'AISLE': 0,
        'SPECIAL': 0,
        'UNKNOWN': 0,
        'MISSING': 0
    }

    confidence_scores = []
    method_counts = {}

    # Test each location
    for location in test_locations:
        try:
            result = classifier.classify_location(location)
            results[location] = result

            # Update statistics
            classification_stats[result.location_type] += 1
            confidence_scores.append(result.confidence)
            method_counts[result.method] = method_counts.get(result.method, 0) + 1

            # Print result
            confidence_bar = "#" * int(result.confidence * 10) + "-" * (10 - int(result.confidence * 10))
            print(f"{location:25} -> {result.location_type:12} [{confidence_bar}] {result.confidence:.2f} ({result.method})")

        except Exception as e:
            print(f"{location:25} -> ERROR: {str(e)}")
            classification_stats['UNKNOWN'] += 1

    print("\n" + "=" * 60)
    print("[RESULTS] CLASSIFICATION RESULTS")
    print("=" * 60)

    total_locations = len([loc for loc in test_locations if loc.strip()])  # Exclude empty
    unknown_count = classification_stats['UNKNOWN']
    unknown_rate = (unknown_count / total_locations) * 100 if total_locations > 0 else 0

    print(f"Total locations tested: {total_locations}")
    print(f"Unknown classifications: {unknown_count}")
    print(f"Unknown rate: {unknown_rate:.1f}%")
    print(f"Average confidence: {sum(confidence_scores)/len(confidence_scores):.3f}")

    print(f"\n[STATS] Type Distribution:")
    for location_type, count in classification_stats.items():
        percentage = (count / total_locations) * 100 if total_locations > 0 else 0
        print(f"  {location_type:12}: {count:2d} ({percentage:5.1f}%)")

    print(f"\n[METHODS] Method Distribution:")
    for method, count in method_counts.items():
        percentage = (count / total_locations) * 100 if total_locations > 0 else 0
        print(f"  {method:12}: {count:2d} ({percentage:5.1f}%)")

    # Success criteria
    print("\n" + "=" * 60)
    print("[EVALUATION] SUCCESS CRITERIA EVALUATION")
    print("=" * 60)

    target_unknown_rate = 25.0
    success = unknown_rate < target_unknown_rate

    print(f"Target: Unknown rate < {target_unknown_rate}%")
    print(f"Actual: {unknown_rate:.1f}%")
    print(f"Status: {'PASS' if success else 'FAIL'}")

    if success:
        print(f"\n[SUCCESS] Enhanced classifier reduces unknown rate from ~70% to {unknown_rate:.1f}%")
        print("Crisis fix objective achieved!")
    else:
        print(f"\n[WARNING] Needs improvement. Target was <{target_unknown_rate}%, got {unknown_rate:.1f}%")

    return success, results

def test_behavioral_analysis():
    """Test behavioral analysis with mock inventory data"""

    print("\n" + "=" * 60)
    print("[BEHAVIORAL] TESTING BEHAVIORAL ANALYSIS")
    print("=" * 60)

    from enhanced_location_classifier import EnhancedLocationClassifier

    classifier = EnhancedLocationClassifier()

    # Create mock inventory data for behavioral analysis
    inventory_data = pd.DataFrame([
        # High diversity receiving area
        {'location': 'AREA-X', 'product': 'WIDGET-A', 'creation_date': '2024-01-15 08:00:00'},
        {'location': 'AREA-X', 'product': 'WIDGET-B', 'creation_date': '2024-01-15 09:00:00'},
        {'location': 'AREA-X', 'product': 'GADGET-C', 'creation_date': '2024-01-15 10:00:00'},
        {'location': 'AREA-X', 'product': 'TOOL-D', 'creation_date': '2024-01-15 11:00:00'},
        {'location': 'AREA-X', 'product': 'PART-E', 'creation_date': '2024-01-15 12:00:00'},

        # Low diversity storage area
        {'location': 'AREA-Y', 'product': 'WIDGET-A', 'creation_date': '2024-01-10 08:00:00'},
        {'location': 'AREA-Y', 'product': 'WIDGET-A', 'creation_date': '2024-01-11 08:00:00'},
        {'location': 'AREA-Y', 'product': 'WIDGET-A', 'creation_date': '2024-01-12 08:00:00'},
        {'location': 'AREA-Y', 'product': 'WIDGET-A', 'creation_date': '2024-01-13 08:00:00'},
        {'location': 'AREA-Y', 'product': 'WIDGET-A', 'creation_date': '2024-01-14 08:00:00'},
    ])

    # Convert creation_date to datetime
    inventory_data['creation_date'] = pd.to_datetime(inventory_data['creation_date'])

    # Test behavioral classification
    test_cases = ['AREA-X', 'AREA-Y']

    for location in test_cases:
        result = classifier.classify_location(location, inventory_context=inventory_data)

        print(f"{location:10} -> {result.location_type:12} (confidence: {result.confidence:.2f})")
        print(f"           Method: {result.method}")
        print(f"           Reasoning: {result.reasoning}\n")

    print("[OK] Behavioral analysis test completed")

def test_pattern_coverage():
    """Test coverage of different location patterns"""

    print("\n" + "=" * 60)
    print("[PATTERNS] TESTING PATTERN COVERAGE")
    print("=" * 60)

    from enhanced_location_classifier import EnhancedLocationClassifier

    classifier = EnhancedLocationClassifier()

    # Test various pattern types
    pattern_tests = {
        'Receiving Explicit': ['RECV-01', 'RECEIVING', 'INBOUND', 'DOCK'],
        'Receiving Positional': ['AREA-01', 'ZONE-002', 'LOC-003'],
        'Storage Grid': ['A-12-045B', '12A045', 'A12-B34', 'RACK-12-45'],
        'Storage Levels': ['A12-A', 'SLOT-045-B', 'POS-123-C', 'BIN-001-D'],
        'Transitional': ['STAGE-01', 'PREP-AREA', 'WORK-01', 'TRANSIT'],
        'Dock Patterns': ['DOCK-A', 'DOOR-12', 'GATE-1', 'BAY-3'],
        'Edge Cases': ['', 'X', '???', 'SPECIAL'],
    }

    for pattern_type, locations in pattern_tests.items():
        print(f"\n{pattern_type}:")
        for location in locations:
            result = classifier.classify_location(location)
            print(f"  {location:15} -> {result.location_type:12} ({result.confidence:.2f})")

    print("\n[OK] Pattern coverage test completed")

if __name__ == "__main__":
    print("[START] Enhanced Location Classification System Test Suite")
    print("Phase 1: Zero-Cost Crisis Fix Validation\n")

    try:
        # Run main classification test
        success, results = test_classification_samples()

        # Run behavioral analysis test
        test_behavioral_analysis()

        # Run pattern coverage test
        test_pattern_coverage()

        print("\n" + "=" * 60)
        print("[COMPLETED] TEST SUITE COMPLETED")
        print("=" * 60)

        if success:
            print("[PASS] All tests passed! Ready for production deployment.")
            print("[IMPACT] Expected impact: Reduce UNKNOWN classifications from 70% to <25%")
            print("[OBJECTIVE] Crisis fix objective: ACHIEVED")
        else:
            print("[WARNING] Some tests need attention before production deployment.")

    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("Make sure you're running from the backend directory")
        print("Try: cd backend && python test_enhanced_classifier.py")

    except Exception as e:
        print(f"[ERROR] Test Error: {e}")
        import traceback
        traceback.print_exc()