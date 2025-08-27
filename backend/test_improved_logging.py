#!/usr/bin/env python3
"""
Test script to demonstrate the improved logging vs the old verbose logging
"""

import os
import pandas as pd
from configure_logging import setup_default_logging

# Set up optimized logging
setup_default_logging()

# Import after logging is configured
from src.optimized_logging import get_logger

def create_sample_data():
    """Create a small sample dataset for testing"""
    sample_data = {
        'pallet_id': [f'PLT{i:03d}' for i in range(1, 11)],
        'location': [
            '01-01-001A',  # Valid
            '01-01-002B',  # Valid  
            'INVALID',     # Invalid - format
            '99-99-999Z',  # Invalid - out of bounds
            '01-01-003C',  # Valid
            '01-01-004D',  # Valid
            'X-Y-Z',       # Invalid - format
            '01-01-005A',  # Valid
            '00-01-001A',  # Invalid - aisle 0
            '01-01-006B'   # Valid
        ]
    }
    return pd.DataFrame(sample_data)

def demonstrate_logging_levels():
    """Show different logging levels in action"""
    logger = get_logger()
    
    print("\n" + "="*60)
    print("LOGGING IMPROVEMENTS DEMONSTRATION")
    print("="*60)
    
    print(f"\nCurrent logging level: {logger.level.value}")
    print(f"Enabled categories: {[cat.value for cat in logger.enabled_categories]}")
    
    print("\nBEFORE: Would show 757 location validations")
    print("- [VirtualInvalidLocationEvaluator_DEBUG] Validating location: '03-02-004A'")
    print("- [VirtualInvalidLocationEvaluator_DEBUG] Result: [VALID] - Valid storage location")
    print("- [VirtualInvalidLocationEvaluator_DEBUG] Validating location: '02-01-030D'")
    print("- [VirtualInvalidLocationEvaluator_DEBUG] Result: [VALID] - Valid storage location")
    print("- ... (753 more lines) ...")
    
    print("\nAFTER: Shows only essential information")
    sample_df = create_sample_data()
    total_locations = sample_df['location'].nunique() 
    invalid_count = 4  # From our sample data
    
    # Demonstrate the new concise logging
    print(f"\n[LOCATION_VALIDATION] Starting Invalid Locations Alert (ID: 4) - {len(sample_df):,} records, {total_locations} unique locations")
    
    # This would only show invalid locations at DIAGNOSTIC level
    print("[LOCATION_VALIDATION] [INVALID]: 'INVALID' -> Storage location format not recognized")
    print("[LOCATION_VALIDATION] [INVALID]: '99-99-999Z' -> Rack number 99 exceeds warehouse racks (max: 2)")
    print("[LOCATION_VALIDATION] [INVALID]: 'X-Y-Z' -> Storage location format not recognized")
    print("[LOCATION_VALIDATION] [INVALID]: '00-01-001A' -> Aisle 0 exceeds warehouse capacity (max: 3)")
    
    # Summary instead of per-location stats
    logger.location_validation_summary(total_locations, invalid_count, 'virtual_engine')
    
    print("\nLOGGING REDUCTION:")
    print(f"- Before: ~1,500+ lines of debug output")
    print(f"- After: ~10 lines of essential information")
    print(f"- Reduction: ~99% less verbose output")
    
    print("\nTo see more detail when needed:")
    print("- Set WARE_LOG_LEVEL=DIAGNOSTIC for error details")
    print("- Set WARE_LOG_LEVEL=VERBOSE for full debugging")
    print("- Set WARE_LOG_LEVEL=FLOOD to restore original verbosity")

if __name__ == "__main__":
    demonstrate_logging_levels()