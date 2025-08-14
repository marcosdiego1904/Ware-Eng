#!/usr/bin/env python3
"""
Debug Location Matching - Find out why valid locations are not being found
"""

import sys
sys.path.append('backend/src')

from app import app
from models import Location
from database import db
from rule_engine import InvalidLocationEvaluator
import pandas as pd

def test_location_matching():
    """Test the location matching logic directly"""
    
    with app.app_context():
        # Get test locations from our inventory
        test_locations = [
            'RECEIVING',
            '001A', 
            '002A',
            '003A',
            'STAGING',
            'DOCK01',
            'INVALID-XYZ'  # This should fail
        ]
        
        print("=== LOCATION MATCHING DEBUG ===")
        print(f"Total locations in database: {Location.query.count()}")
        
        # Create evaluator to test
        evaluator = InvalidLocationEvaluator()
        
        for test_loc in test_locations:
            print(f"\n--- Testing location: '{test_loc}' ---")
            
            # Test 1: Direct database query
            direct_match = Location.query.filter_by(code=test_loc).first()
            print(f"1. Direct match: {direct_match.code if direct_match else 'NOT FOUND'}")
            
            # Test 2: Smart matching through evaluator
            smart_match = evaluator._find_location_by_code(test_loc)
            print(f"2. Smart match: {smart_match.code if smart_match else 'NOT FOUND'}")
            
            # Test 3: Normalization
            normalized = evaluator._normalize_location_code(test_loc)
            print(f"3. Normalized: '{test_loc}' -> '{normalized}'")
            
            # Test 4: Check if normalized version exists
            if normalized != test_loc:
                normalized_match = Location.query.filter_by(code=normalized).first()
                print(f"4. Normalized match: {normalized_match.code if normalized_match else 'NOT FOUND'}")
            
            # Test 5: Pattern matching
            patterns = Location.query.filter(Location.pattern.isnot(None)).all()
            pattern_matches = []
            for loc in patterns:
                if evaluator._matches_pattern(test_loc, loc.pattern):
                    pattern_matches.append(loc.pattern)
            print(f"5. Pattern matches: {pattern_matches if pattern_matches else 'NONE'}")
        
        # Show some sample locations from database for reference
        print(f"\n=== SAMPLE DATABASE LOCATIONS ===")
        sample_locations = Location.query.filter_by(location_type='STORAGE').limit(10).all()
        for loc in sample_locations:
            print(f"Storage: {loc.code}")
            
        special_locations = Location.query.filter(Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])).limit(10).all()
        for loc in special_locations:
            print(f"Special: {loc.code} ({loc.location_type})")

def test_inventory_processing():
    """Test with actual inventory data to see validation results"""
    
    # Create small test dataset
    test_data = [
        {'pallet_id': 'TEST001', 'location': 'RECEIVING'},
        {'pallet_id': 'TEST002', 'location': '001A'},
        {'pallet_id': 'TEST003', 'location': 'STAGING'},
        {'pallet_id': 'TEST004', 'location': 'INVALID-XYZ'}
    ]
    
    df = pd.DataFrame(test_data)
    
    with app.app_context():
        print(f"\n=== INVENTORY VALIDATION TEST ===")
        
        evaluator = InvalidLocationEvaluator()
        
        # Mock rule for testing
        class MockRule:
            def __init__(self):
                self.conditions = '{"check_undefined_locations": true}'
                self.parameters = '{}'
        
        rule = MockRule()
        
        # Run evaluation
        anomalies = evaluator.evaluate(rule, df)
        
        print(f"Total pallets: {len(df)}")
        print(f"Invalid locations found: {len(anomalies)}")
        
        for anomaly in anomalies:
            print(f"  - {anomaly['pallet_id']}: {anomaly.get('description', 'N/A')}")
        
        # Expected: Only TEST004 should be invalid

if __name__ == "__main__":
    test_location_matching()
    test_inventory_processing()