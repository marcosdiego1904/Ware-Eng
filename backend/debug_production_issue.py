#!/usr/bin/env python3
"""
Debug script to reproduce the exact 51 anomalies issue from production log
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

def reproduce_production_issue():
    """Reproduce the 51 anomalies issue from production"""
    
    print("="*80)
    print("REPRODUCING PRODUCTION OVERCAPACITY ISSUE (51 vs ~16-21)")
    print("="*80)
    
    with app.app_context():
        # Get the overcapacity rule
        rule = Rule.query.filter_by(rule_type='OVERCAPACITY').first()
        print(f"Rule: {rule.name} (ID: {rule.id})")
        print(f"Parameters: {rule.parameters}")
        
        # Create production-like test data
        # From the log: 800 records total, with locations like:
        # ['03-02-004A', '02-01-030D', '02-02-001B', '02-02-032B', '03-02-027B', ...]
        
        test_data = []
        
        # Simulate the actual production data that caused 51 anomalies
        # If there are 51 anomalies and locations have capacity 1, that means:
        # - Some locations have multiple pallets
        
        # Let's create a scenario that could cause 51 anomalies:
        # 1. The main violation: 01-01-001A with 16 pallets (16 anomalies)
        # 2. Additional smaller violations that sum to 35 more anomalies
        
        violation_scenarios = [
            ('01-01-001A', 16),  # Main violation from log
            ('02-01-030D', 5),   # Additional violations
            ('02-02-001B', 4),
            ('02-02-032B', 3),
            ('03-02-027B', 3),
            ('02-02-011C', 3),
            ('03-01-023D', 3),
            ('03-02-006D', 3),
            ('03-02-004A', 2),
            ('02-01-031A', 2),
            ('03-02-025A', 2),
            ('03-01-025B', 2),
            ('02-02-035C', 2),
            ('03-01-021A', 2),
            ('02-01-025D', 1),  # Normal locations
            ('03-02-018B', 1),
            ('02-02-015A', 1),
        ]
        
        pallet_counter = 1
        expected_violations = 0
        
        for location, count in violation_scenarios:
            for i in range(count):
                test_data.append({
                    'pallet_id': f'PLT{pallet_counter:05d}',
                    'location': location
                })
                pallet_counter += 1
            
            if count > 1:  # Capacity = 1, so > 1 is a violation
                expected_violations += count
                print(f"  {location}: {count} pallets = {count} violations")
        
        print(f"Expected total violations: {expected_violations}")
        
        # Create DataFrame
        test_df = pd.DataFrame(test_data)
        
        print(f"\nTest Data:")
        print(f"- Total pallets: {len(test_df)}")
        print(f"- Unique locations: {test_df['location'].nunique()}")
        
        # Show location counts
        location_counts = test_df['location'].value_counts()
        print(f"Location breakdown:")
        violations_over_1 = 0
        for location, count in location_counts.items():
            if count > 1:
                violations_over_1 += count
                print(f"  {location}: {count} pallets ({'VIOLATION' if count > 1 else 'OK'})")
        
        print(f"Expected violations (capacity=1): {violations_over_1}")
        
        # Run the evaluator with same context as production
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
        
        evaluator = OvercapacityEvaluator()
        anomalies = evaluator.evaluate(rule, test_df, warehouse_context)
        
        print(f"\nACTUAL RESULTS:")
        print(f"Anomalies found: {len(anomalies)}")
        print(f"Expected: {expected_violations}")
        print(f"Difference: {len(anomalies) - expected_violations}")
        
        if len(anomalies) != expected_violations:
            print(f"\nDISCREPANCY ANALYSIS:")
            
            # Check anomaly types
            anomaly_types = {}
            capacity_info = {}
            
            for anomaly in anomalies[:10]:  # Check first 10
                anomaly_type = anomaly.get('anomaly_type', 'Unknown')
                location = anomaly.get('location', 'Unknown')
                details = anomaly.get('details', '')
                
                anomaly_types[anomaly_type] = anomaly_types.get(anomaly_type, 0) + 1
                
                if location not in capacity_info:
                    capacity_info[location] = details
            
            print(f"Anomaly types: {anomaly_types}")
            print(f"Sample capacity details:")
            for location, details in list(capacity_info.items())[:5]:
                print(f"  {location}: {details}")
        
        return len(anomalies) == 51  # Return True if we reproduced the issue

if __name__ == "__main__":
    reproduced = reproduce_production_issue()
    if reproduced:
        print("\n🎯 ISSUE REPRODUCED: We found the root cause!")
    else:
        print("\n❓ ISSUE NOT REPRODUCED: Need more investigation")