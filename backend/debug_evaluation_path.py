#!/usr/bin/env python3
"""
Debug script to see exactly which evaluation path is being taken
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

def debug_evaluation_path():
    """Debug which evaluation path is actually being taken"""
    
    print("="*80)
    print("DEBUGGING OVERCAPACITY EVALUATION PATH")
    print("="*80)
    
    with app.app_context():
        # Get the overcapacity rule
        rule = Rule.query.filter_by(rule_type='OVERCAPACITY').first()
        print(f"Rule: {rule.name} (ID: {rule.id})")
        print(f"Parameters: '{rule.parameters}'")
        print(f"Conditions: '{rule.conditions}'")
        
        # Parse parameters exactly like the evaluator does
        try:
            conditions = json.loads(rule.conditions) if rule.conditions else {}
        except:
            conditions = {}
            
        try:
            parameters = json.loads(rule.parameters) if rule.parameters else {}
        except:
            parameters = {}
        
        print(f"Parsed parameters: {parameters}")
        print(f"Parsed conditions: {conditions}")
        
        # Check the use_statistical_analysis setting
        use_statistical_analysis = parameters.get('use_statistical_analysis', False)
        significance_threshold = parameters.get('significance_threshold', 1.0)
        min_severity_ratio = parameters.get('min_severity_ratio', 1.2)
        
        print(f"\nEVALUATION PATH DECISION:")
        print(f"- use_statistical_analysis: {use_statistical_analysis} (type: {type(use_statistical_analysis)})")
        print(f"- significance_threshold: {significance_threshold}")
        print(f"- min_severity_ratio: {min_severity_ratio}")
        print(f"- Will use statistical analysis: {'YES' if use_statistical_analysis else 'NO'}")
        print(f"- Expected path: {'_evaluate_with_statistical_analysis' if use_statistical_analysis else '_evaluate_legacy'}")
        
        # Create simple test data
        test_data = [
            {'pallet_id': 'TEST001', 'location': '01-01-001A'},
            {'pallet_id': 'TEST002', 'location': '01-01-001A'},  # Violation
            {'pallet_id': 'TEST003', 'location': '02-01-001B'},  # Normal
        ]
        test_df = pd.DataFrame(test_data)
        
        # Create evaluator and monkey-patch the methods to add debug info
        evaluator = OvercapacityEvaluator()
        
        # Store original methods
        original_legacy = evaluator._evaluate_legacy
        original_statistical = evaluator._evaluate_with_statistical_analysis
        
        def debug_legacy(rule, inventory_df):
            print(f"\n🔍 CALLED: _evaluate_legacy()")
            print(f"   Rule: {rule.name}")
            print(f"   Inventory records: {len(inventory_df)}")
            result = original_legacy(rule, inventory_df)
            print(f"   Returned anomalies: {len(result)}")
            if len(result) > 0:
                print(f"   Sample anomaly keys: {list(result[0].keys())}")
                print(f"   Sample anomaly type: {result[0].get('anomaly_type', 'N/A')}")
            return result
            
        def debug_statistical(rule, inventory_df, sig_threshold, min_severity):
            print(f"\n🔍 CALLED: _evaluate_with_statistical_analysis()")
            print(f"   Rule: {rule.name}")
            print(f"   Inventory records: {len(inventory_df)}")
            print(f"   Significance threshold: {sig_threshold}")
            print(f"   Min severity ratio: {min_severity}")
            result = original_statistical(rule, inventory_df, sig_threshold, min_severity)
            print(f"   Returned anomalies: {len(result)}")
            if len(result) > 0:
                print(f"   Sample anomaly keys: {list(result[0].keys())}")
                print(f"   Sample anomaly type: {result[0].get('anomaly_type', 'N/A')}")
                # Check for statistical fields
                statistical_fields = [k for k in result[0].keys() if 'statistical' in k.lower() or 'severity_ratio' in k or 'utilization' in k]
                print(f"   Statistical fields found: {statistical_fields}")
            return result
        
        # Monkey patch
        evaluator._evaluate_legacy = debug_legacy
        evaluator._evaluate_with_statistical_analysis = debug_statistical
        
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
        
        print(f"\nCalling evaluator.evaluate()...")
        anomalies = evaluator.evaluate(rule, test_df, warehouse_context)
        
        print(f"\nFINAL RESULTS:")
        print(f"- Total anomalies: {len(anomalies)}")
        
        if len(anomalies) > 0:
            print(f"- First anomaly:")
            for key, value in anomalies[0].items():
                print(f"    {key}: {value}")
            
            # Check if this contains statistical fields
            statistical_fields = [k for k in anomalies[0].keys() if any(keyword in k.lower() for keyword in ['statistical', 'severity', 'utilization', 'expected', 'bypass'])]
            if statistical_fields:
                print(f"\n⚠️  STATISTICAL FIELDS FOUND:")
                for field in statistical_fields:
                    print(f"    {field}: {anomalies[0][field]}")
                print(f"This indicates statistical analysis was used!")
            else:
                print(f"\n✅ NO STATISTICAL FIELDS - Legacy evaluation confirmed")

if __name__ == "__main__":
    debug_evaluation_path()