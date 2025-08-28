#!/usr/bin/env python3
"""
Test script to verify that smart violations are now properly disabled
"""

import pandas as pd
import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, 'src')

from app import app
from rule_engine import OvercapacityEvaluator
from models import Rule

def test_smart_disabled():
    """Test that smart violations are disabled and only obvious violations are detected"""
    
    print("="*60)
    print("TESTING: Smart Violations Disabled Fix")
    print("="*60)
    
    with app.app_context():
        # Get the overcapacity rule from database
        rule = Rule.query.filter_by(rule_type='OVERCAPACITY').first()
        if not rule:
            print("ERROR: No OVERCAPACITY rule found!")
            return False
            
        print(f"Rule: {rule.name}")
        print(f"Parameters: {rule.parameters}")
        
        # Parse parameters
        params = json.loads(rule.parameters) if rule.parameters else {}
        use_smart = params.get('use_statistical_analysis', False)
        print(f"Smart Analytics Setting: {use_smart}")
        
        # Create test data - same as the original test
        test_data = []
        
        # Add obvious violations (16 pallets in same location)
        duplicate_location = "01-01-001A"
        for i in range(16):
            test_data.append({
                'pallet_id': f'CAP{i+1:03d}',
                'location': duplicate_location
            })
        
        # Add some valid locations  
        valid_locations = ['01-01-002B', '01-01-003C', '01-01-004D', '01-01-005A']
        for i, loc in enumerate(valid_locations):
            test_data.append({
                'pallet_id': f'VALID{i+1:03d}',
                'location': loc
            })
        
        # Create DataFrame
        test_df = pd.DataFrame(test_data)
        
        print(f"\nTest Data:")
        print(f"- Total pallets: {len(test_df)}")
        print(f"- Locations with multiple pallets: {duplicate_location} (16 pallets)")
        
        # Run the rule evaluation
        evaluator = OvercapacityEvaluator()
        anomalies = evaluator.evaluate(rule, test_df)
        
        print(f"\nResults:")
        print(f"- Anomalies detected: {len(anomalies)}")
        
        if len(anomalies) > 0:
            # Check anomaly types
            anomaly_types = [a.get('anomaly_type', 'Unknown') for a in anomalies]
            print(f"- Anomaly types: {set(anomaly_types)}")
            
            # Check if any are marked as "Smart Overcapacity"
            smart_violations = [a for a in anomalies if 'Smart' in str(a.get('anomaly_type', ''))]
            obvious_violations = [a for a in anomalies if a.get('anomaly_type') == 'Overcapacity']
            
            print(f"- Obvious violations: {len(obvious_violations)}")
            print(f"- Smart violations: {len(smart_violations)}")
            
            if len(smart_violations) == 0:
                print("✅ SUCCESS: No smart violations detected!")
                return True
            else:
                print("❌ FAILURE: Smart violations still being detected!")
                print("Smart violations found:")
                for sv in smart_violations[:3]:  # Show first 3
                    print(f"  - {sv}")
                return False
        else:
            print("❌ FAILURE: No anomalies detected at all!")
            return False

if __name__ == "__main__":
    success = test_smart_disabled()
    if success:
        print("\n✅ Fix confirmed: Smart violations are now disabled!")
    else:
        print("\n❌ Fix failed: Smart violations are still active!")