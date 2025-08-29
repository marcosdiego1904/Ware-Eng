#!/usr/bin/env python3
"""
Test the VirtualInvalidLocationEvaluator fix for manually-created special locations
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from virtual_invalid_location_evaluator import VirtualInvalidLocationEvaluator
    from models import Location
    from database import db
    from app import app
    import pandas as pd

    print("Testing location validation fix...")
    
    # Create app context
    with app.app_context():
        # Create test evaluator
        evaluator = VirtualInvalidLocationEvaluator()
        
        # Test the physical special location check directly
        print("\n=== Testing _is_physical_special_location method ===")
        
        test_locations = [
            'RECV-01',  # Should be found (template-created)
            'RECV-02',  # Should be found (template-created) 
            'RECV-03',  # Should be found (manually-created)
            'STAGE-01', # Should be found (template-created)
            'AISLE-01', # Should be found (template-created)
            'INVALID-LOCATION-X99', # Should NOT be found
            '01-A01-A'  # Storage location - should NOT be found
        ]
        
        for location in test_locations:
            is_physical = evaluator._is_physical_special_location(location)
            print(f"Location '{location}': {'[YES] Physical special location' if is_physical else '[NO] Not physical special location'}")
        
        # Test the full validation method
        print("\n=== Testing _validate_location_with_physical_fallback method ===")
        
        # We need a virtual engine for this test
        from virtual_template_integration import get_virtual_engine_for_warehouse
        virtual_engine = get_virtual_engine_for_warehouse('DEFAULT')
        
        if virtual_engine:
            for location in test_locations:
                is_valid, reason = evaluator._validate_location_with_physical_fallback(location, virtual_engine)
                status = "[VALID]" if is_valid else "[INVALID]"
                print(f"Location '{location}': {status} ({reason})")
        else:
            print("[ERROR] No virtual engine available for testing")
        
        # Test with actual inventory data to simulate the real scenario
        print("\n=== Testing with sample inventory data ===")
        
        sample_inventory = pd.DataFrame([
            {'pallet_id': 'TEST-001', 'location': 'RECV-01', 'description': 'Test Product'},
            {'pallet_id': 'TEST-002', 'location': 'RECV-03', 'description': 'Test Product'}, # The problematic manually-created one
            {'pallet_id': 'TEST-003', 'location': 'AISLE-01', 'description': 'Test Product'},
            {'pallet_id': 'TEST-004', 'location': 'INVALID-LOCATION-X99', 'description': 'Test Product'},
        ])
        
        # Create a mock rule object
        class MockRule:
            def __init__(self):
                self.id = 999
                self.name = "Test Invalid Locations"
                self.priority = "HIGH"
                self.conditions = '{"check_undefined_locations": true}'
        
        mock_rule = MockRule()
        warehouse_context = {'warehouse_id': 'DEFAULT'}
        
        # Test the full evaluator
        anomalies = evaluator.evaluate(mock_rule, sample_inventory, warehouse_context)
        
        print(f"Total anomalies found: {len(anomalies)}")
        for anomaly in anomalies:
            print(f"- Anomaly: {anomaly['pallet_id']} at {anomaly['location']} - {anomaly.get('issue_description', 'No description')}")
        
        # Expected: Should only find INVALID-LOCATION-X99, not RECV-03
        recv_03_anomalies = [a for a in anomalies if a.get('location') == 'RECV-03']
        if recv_03_anomalies:
            print("[FAIL] RECV-03 still flagged as invalid - fix needs refinement")
        else:
            print("[SUCCESS] RECV-03 correctly recognized as valid!")
            
        invalid_location_anomalies = [a for a in anomalies if a.get('location') == 'INVALID-LOCATION-X99']
        if invalid_location_anomalies:
            print("[SUCCESS] INVALID-LOCATION-X99 correctly flagged as invalid")
        else:
            print("[FAIL] INVALID-LOCATION-X99 should have been flagged as invalid")

except Exception as e:
    print(f"Error testing fix: {e}")
    import traceback
    traceback.print_exc()