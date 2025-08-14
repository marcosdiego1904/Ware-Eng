#!/usr/bin/env python3
"""
Test the location validation fix directly
"""

import sys
sys.path.append('backend/src')

from app import app
from models import Location
from database import db
from rule_engine import InvalidLocationEvaluator
import pandas as pd

def test_fixed_validation():
    """Test the fixed location validation logic"""
    
    with app.app_context():
        print("=== TESTING FIXED LOCATION VALIDATION ===")
        
        # Create test inventory data (same as our fixed inventory)
        test_data = [
            {'pallet_id': 'STAG000', 'location': 'RECEIVING'},
            {'pallet_id': 'OVER000', 'location': '001A'},
            {'pallet_id': 'LOT000', 'location': '002A'},
            {'pallet_id': 'TEMP000', 'location': '005A'},
            {'pallet_id': 'SPEC000', 'location': 'STAGING'},
            {'pallet_id': 'SPEC001', 'location': 'DOCK01'},
            {'pallet_id': 'MISS001', 'location': ''},  # Empty - should be skipped
            {'pallet_id': 'INV001', 'location': 'INVALID-XYZ'},  # Invalid
            {'pallet_id': 'INV002', 'location': '99-99-999-Z'}  # Invalid
        ]
        
        df = pd.DataFrame(test_data)
        
        # Create evaluator and mock rule
        evaluator = InvalidLocationEvaluator()
        
        class MockRule:
            def __init__(self):
                self.conditions = '{"check_undefined_locations": true}'
                self.parameters = '{}'
                self.priority = 'HIGH'
        
        rule = MockRule()
        
        print(f"Testing {len(df)} pallets...")
        
        # Run evaluation
        anomalies = evaluator.evaluate(rule, df)
        
        print(f"\nResults:")
        print(f"  Total pallets: {len(df)}")
        print(f"  Invalid locations: {len(anomalies)}")
        print(f"  Expected invalid: 2 (INVALID-XYZ, 99-99-999-Z)")
        
        print(f"\nInvalid pallets found:")
        for anomaly in anomalies:
            print(f"  - {anomaly['pallet_id']}: {anomaly['location']}")
        
        # Check if only the expected invalid locations were flagged
        invalid_pallets = [a['pallet_id'] for a in anomalies]
        expected_invalid = ['INV001', 'INV002']
        
        success = set(invalid_pallets) == set(expected_invalid)
        print(f"\nTest Result: {'PASS' if success else 'FAIL'}")
        
        if not success:
            print(f"  Expected: {expected_invalid}")
            print(f"  Got: {invalid_pallets}")
        
        return success

if __name__ == "__main__":
    test_fixed_validation()