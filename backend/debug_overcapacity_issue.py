#!/usr/bin/env python3
"""
Debug script to trace exactly what's happening in the overcapacity evaluation
that's causing 51 anomalies instead of the expected obvious violations only
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

def debug_overcapacity_evaluation():
    """Debug the exact overcapacity evaluation process"""
    
    print("="*80)
    print("DEBUGGING OVERCAPACITY EVALUATION ISSUE")
    print("="*80)
    
    with app.app_context():
        # Get the overcapacity rule
        rule = Rule.query.filter_by(rule_type='OVERCAPACITY').first()
        print(f"Rule: {rule.name} (ID: {rule.id})")
        print(f"Parameters: {rule.parameters}")
        print(f"Conditions: {rule.conditions}")
        
        # Parse parameters to check what the evaluator sees
        params = json.loads(rule.parameters) if rule.parameters else {}
        conditions = json.loads(rule.conditions) if rule.conditions else {}
        
        print(f"Parsed parameters: {params}")
        print(f"use_statistical_analysis setting: {params.get('use_statistical_analysis', 'DEFAULT (False)')}")
        
        # Create the same test data structure that was in the logs
        # Based on the log showing "01-01-001A" with 16 pallets
        test_data = []
        
        # Create exactly what might be in the real data
        # Add the 16 pallets in 01-01-001A (obvious violation)
        for i in range(16):
            test_data.append({
                'pallet_id': f'CAP{i+1:03d}',
                'location': '01-01-001A'
            })
        
        # Add some additional pallets to other locations to simulate real data
        other_locations = [
            ('02-01-001B', 2),  # Another violation 
            ('03-01-001C', 3),  # Another violation
            ('04-01-001D', 1),  # Normal
            ('05-01-001E', 1),  # Normal
        ]
        
        pallet_counter = 17
        for location, count in other_locations:
            for i in range(count):
                test_data.append({
                    'pallet_id': f'PLT{pallet_counter:03d}',
                    'location': location
                })
                pallet_counter += 1
                
        # Create DataFrame
        test_df = pd.DataFrame(test_data)
        
        print(f"\nTest Data Analysis:")
        print(f"Total pallets: {len(test_df)}")
        
        location_counts = test_df['location'].value_counts()
        print(f"Location counts:")
        for location, count in location_counts.items():
            print(f"  {location}: {count} pallets")
        
        print(f"\nExpected violations:")
        expected_violations = 0
        for location, count in location_counts.items():
            capacity = 1  # Standard capacity
            if count > capacity:
                expected_violations += count
                print(f"  {location}: {count} pallets (capacity: {capacity}) = {count} violations")
        print(f"Total expected anomalies: {expected_violations}")
        
        # Now run the actual evaluator
        print(f"\nRunning OvercapacityEvaluator...")
        evaluator = OvercapacityEvaluator()
        
        # Enable debug for more visibility
        evaluator.debug = True
        
        warehouse_context = {
            'warehouse_id': 'USER_MARCOS9',
            'confidence': 'DEFAULT_MAPPING', 
            'coverage': 1.0,
            'access_level': 'ADMIN',
            'resolution_method': 'user_default',
            'user_id': 1,
            'username': 'marcos9',
            'timestamp': 'RESOLVER_V2'
        }
        
        anomalies = evaluator.evaluate(rule, test_df, warehouse_context)
        
        print(f"\nACTUAL RESULTS:")
        print(f"Anomalies found: {len(anomalies)}")
        
        if len(anomalies) > 0:
            # Group by location to see the pattern
            location_anomalies = {}
            for anomaly in anomalies:
                loc = anomaly.get('location', 'Unknown')
                if loc not in location_anomalies:
                    location_anomalies[loc] = []
                location_anomalies[loc].append(anomaly)
            
            print(f"Anomalies by location:")
            for loc, anoms in location_anomalies.items():
                print(f"  {loc}: {len(anoms)} anomalies")
                if len(anoms) > 0:
                    sample = anoms[0]
                    print(f"    Sample anomaly_type: {sample.get('anomaly_type', 'N/A')}")
                    print(f"    Sample details: {sample.get('details', 'N/A')}")
                    
                    # Check if any are smart violations
                    smart_count = sum(1 for a in anoms if 'Smart' in str(a.get('anomaly_type', '')))
                    obvious_count = sum(1 for a in anoms if a.get('anomaly_type') == 'Overcapacity')
                    print(f"    Smart violations: {smart_count}")
                    print(f"    Obvious violations: {obvious_count}")
        
        print(f"\nDISCREPANCY ANALYSIS:")
        print(f"Expected: {expected_violations} anomalies")
        print(f"Actual: {len(anomalies)} anomalies")
        print(f"Difference: {len(anomalies) - expected_violations}")
        
        if len(anomalies) != expected_violations:
            print(f"❌ ISSUE CONFIRMED: Anomaly count mismatch!")
            if len(anomalies) > 0:
                print(f"First few anomalies:")
                for i, anomaly in enumerate(anomalies[:5]):
                    print(f"  {i+1}. {anomaly}")
        else:
            print(f"✅ Anomaly count matches expected")

if __name__ == "__main__":
    debug_overcapacity_evaluation()