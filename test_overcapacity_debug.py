#!/usr/bin/env python3
"""
Debug overcapacity detection
"""
import sys
import os
sys.path.append('backend/src')

from models import db, Rule
from app import app
import pandas as pd
from rule_engine import RuleEngine

def test_overcapacity_detection():
    """Test overcapacity detection manually"""
    
    with app.app_context():
        # Load our test inventory
        df = pd.read_excel('CentralDC_Compact_Inventory.xlsx', sheet_name='Inventory')
        print(f"Loaded inventory with {len(df)} records")
        
        # Check for locations with multiple pallets
        location_counts = df['location'].value_counts()
        overcapacity_locations = location_counts[location_counts > 1]
        print(f"\nFound {len(overcapacity_locations)} locations with multiple pallets:")
        print(overcapacity_locations.head(10))
        
        # Get the overcapacity rule
        overcapacity_rule = Rule.query.filter_by(name='Overcapacity Alert').first()
        if not overcapacity_rule:
            print("\nERROR: Overcapacity Alert rule not found!")
            return
            
        print(f"\nOvercapacity Rule: {overcapacity_rule.name}")
        print(f"Type: {overcapacity_rule.rule_type}")
        print(f"Conditions: {overcapacity_rule.conditions}")
        print(f"Active: {overcapacity_rule.is_active}")
        
        # Test the rule engine
        engine = RuleEngine(db.session)
        
        # Initialize the rule engine properly
        print("\n=== TESTING RULE ENGINE ===")
        
        # Test just the overcapacity rule
        result = engine.evaluate_all_rules(df, rule_ids=[overcapacity_rule.id])
        
        print(f"Rule engine returned {len(result)} anomalies")
        
        if result:
            print("\nSample anomalies:")
            for i, anomaly in enumerate(result[:5]):
                print(f"{i+1}. {anomaly}")
        else:
            print("No anomalies found - investigating...")
            
            # Check capacity data in our locations
            from models import Location
            sample_locations = ['RCV-001', 'RCV-002', 'RCV-005', 'FINAL-004', '02-02-04A']
            print("\n=== LOCATION CAPACITY CHECK ===")
            for loc_code in sample_locations:
                location = Location.query.filter_by(code=loc_code).first()
                if location:
                    pallet_count = len(df[df['location'] == loc_code])
                    print(f"{loc_code}: Capacity={location.capacity}, Pallets={pallet_count}, Overcapacity={pallet_count > location.capacity}")
                else:
                    print(f"{loc_code}: NOT FOUND in database")
                    
            # Check what the overcapacity evaluator is actually doing
            print("\n=== DIRECT OVERCAPACITY EVALUATION ===")
            from rule_engine import OvercapacityEvaluator
            evaluator = OvercapacityEvaluator()
            
            # Test the evaluator directly with debug
            test_result = evaluator.evaluate(overcapacity_rule, df)
            print(f"Direct evaluator returned: {len(test_result)} anomalies")
            
            if test_result:
                for i, anomaly in enumerate(test_result[:3]):
                    print(f"Anomaly {i+1}: {anomaly}")
            else:
                print("Direct evaluator also found 0 anomalies - checking why...")
                
                # Let's see what locations are being checked
                all_locations = df['location'].unique()
                print(f"Total unique locations in data: {len(all_locations)}")
                
                # Check if locations exist in database
                missing_locations = []
                for loc in all_locations[:10]:  # Check first 10
                    location = Location.query.filter_by(code=loc).first()
                    if not location:
                        missing_locations.append(loc)
                        
                print(f"Missing locations in first 10: {missing_locations}")
                
                # Test specific overcapacity logic manually
                print("\n=== MANUAL OVERCAPACITY CHECK ===")
                location_counts = df['location'].value_counts()
                for location_code, count in location_counts.head(5).items():
                    location_obj = Location.query.filter_by(code=location_code).first()
                    if location_obj:
                        capacity = location_obj.capacity
                        is_overcapacity = count > capacity
                        print(f"{location_code}: {count} pallets, capacity {capacity} -> {'OVERCAPACITY' if is_overcapacity else 'OK'}")
                    else:
                        print(f"{location_code}: {count} pallets, NO LOCATION RECORD")

if __name__ == "__main__":
    test_overcapacity_detection()