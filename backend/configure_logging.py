#!/usr/bin/env python3
"""
Quick script to configure optimized logging for the warehouse system
This sets the logging to ESSENTIAL level by default to reduce verbose output
"""

import os
from src.optimized_logging import configure_logging

def setup_default_logging():
    """Configure logging for production-like environment"""
    # Set environment variables for optimized logging
    os.environ['WARE_LOG_LEVEL'] = 'ESSENTIAL'
    os.environ['WARE_LOG_CATEGORIES'] = 'RULE_ENGINE,LOCATION_VALIDATION,ERRORS,PERFORMANCE'
    
    # Initialize the optimized logger
    configure_logging('ESSENTIAL', 'RULE_ENGINE,LOCATION_VALIDATION,ERRORS,PERFORMANCE')
    
    print("[SUCCESS] Logging configured:")
    print("   - Level: ESSENTIAL (reduced verbosity)")
    print("   - Categories: RULE_ENGINE, LOCATION_VALIDATION, ERRORS, PERFORMANCE")
    print("   - This eliminates per-location validation spam")
    print()
    print("To change logging levels:")
    print("   - SILENT: Only critical errors")
    print("   - ESSENTIAL: Key results (current)")
    print("   - DIAGNOSTIC: Error details + performance")
    print("   - VERBOSE: Full debug info")
    print("   - FLOOD: Everything (original verbose output)")

if __name__ == "__main__":
    setup_default_logging()