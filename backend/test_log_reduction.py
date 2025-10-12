"""
Test the unit-agnostic log reduction functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_log_filtering():
    """Test that the log filtering works correctly"""

    print("Testing log filtering for UNIT_AGNOSTIC messages...")

    # Import the log filter
    from quick_logging_fix import LogFilter

    filter_obj = LogFilter()

    # Test messages that should be suppressed
    suppressed_messages = [
        "[UNIT_AGNOSTIC] Location 001A detected as unit type: pallets",
        "[UNIT_AGNOSTIC] Location 002B detected as unit type: pallets",
        "[UNIT_AGNOSTIC] Error accessing scope service for INVALID: error message"
    ]

    # Test messages that should be preserved
    preserved_messages = [
        "[UNIT_AGNOSTIC] Starting unit-agnostic overcapacity detection for warehouse TEST",
        "[UNIT_AGNOSTIC] Found 25 overcapacity locations",
        "[UNIT_AGNOSTIC] Analyzing 100 locations with inventory",
        "[UNIT_AGNOSTIC] OVERCAPACITY: 001A has 5/1 pallets (+4 excess)"
    ]

    print("Testing suppressed messages:")
    for msg in suppressed_messages:
        should_suppress = filter_obj.should_suppress(msg)
        status = "SUPPRESSED" if should_suppress else "SHOWN"
        print(f"  {status}: {msg[:50]}...")

    print("\nTesting preserved messages:")
    for msg in preserved_messages:
        should_suppress = filter_obj.should_suppress(msg)
        status = "SUPPRESSED" if should_suppress else "SHOWN"
        print(f"  {status}: {msg[:50]}...")

    # Test the actual filtering
    print("\nTesting with filter active:")

    # Apply filter temporarily
    import builtins
    original_print = builtins.print
    builtins.print = filter_obj.filter_print

    print("[UNIT_AGNOSTIC] Location 123A detected as unit type: pallets")  # Should be suppressed
    print("[UNIT_AGNOSTIC] Found 15 overcapacity locations")  # Should be shown
    print("[UNIT_AGNOSTIC] Starting unit-agnostic overcapacity detection")  # Should be shown

    # Restore original print
    builtins.print = original_print

    print("Log filtering test completed!")

if __name__ == "__main__":
    test_log_filtering()