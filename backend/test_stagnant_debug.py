#!/usr/bin/env python3
"""
Test script to analyze debug_stagnant.xlsx with detailed rule execution tracing
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from rule_engine import RuleEngine
import pandas as pd
from datetime import datetime, timedelta

def test_debug_stagnant():
    """Test debug_stagnant.xlsx with enhanced logging"""
    print("=== TESTING DEBUG_STAGNANT.XLSX WITH ENHANCED LOGGING ===")
    
    # Use app context
    with app.app_context():
        # Load the debug file
        file_path = "debug_stagnant.xlsx"
        
        try:
            df = pd.read_excel(file_path)
            print(f"[TEST] Loaded file: {os.path.basename(file_path)}")
            print(f"[TEST] DataFrame shape: {df.shape}")
            print(f"[TEST] Columns: {list(df.columns)}")
            
            # Show the data
            print("\n[TEST] Data content:")
            for idx, row in df.iterrows():
                pallet_id = row.get('Pallet', 'N/A')
                location = row.get('Current Location', 'N/A')
                timestamp_str = row.get('Last Activity', 'N/A')
                print(f"   {idx+1}. Pallet: {pallet_id}, Location: {location}, Last Activity: {timestamp_str}")
            
            # Initialize rule engine
            rule_engine = RuleEngine(db, app)
            
            # Evaluate all rules
            print("\n" + "="*80)
            results = rule_engine.evaluate_all_rules(df)
            
            # Analyze results
            print("\n" + "="*80)
            print("[TEST] RULE EXECUTION SUMMARY:")
            
            successful_rules = [r for r in results if r.success]
            failed_rules = [r for r in results if not r.success]
            
            print(f"   Successful rules: {len(successful_rules)}")
            print(f"   Failed rules: {len(failed_rules)}")
            
            # Collect all anomalies
            all_anomalies = []
            for result in successful_rules:
                all_anomalies.extend(result.anomalies)
            
            print(f"   Total unique anomalies: {len(all_anomalies)}")
            
            # Group anomalies by type
            anomaly_types = {}
            for anomaly in all_anomalies:
                rule_type = anomaly.get('rule_type', 'Unknown')
                if rule_type not in anomaly_types:
                    anomaly_types[rule_type] = []
                anomaly_types[rule_type].append(anomaly)
            
            print(f"\n[TEST] ANOMALY BREAKDOWN BY TYPE:")
            for anomaly_type, type_anomalies in anomaly_types.items():
                print(f"   {anomaly_type}: {len(type_anomalies)} anomalies")
                for i, anomaly in enumerate(type_anomalies):
                    pallet_id = anomaly.get('pallet_id', 'N/A')
                    rule_name = anomaly.get('rule_name', 'N/A')
                    issue_desc = anomaly.get('issue_description', 'N/A')
                    print(f"      {i+1}. [{rule_name}] {pallet_id}: {issue_desc}")
            
            # Show failed rules
            if failed_rules:
                print(f"\n[TEST] FAILED RULES:")
                for result in failed_rules:
                    print(f"   Rule ID {result.rule_id}: {result.error_message}")
            
            return all_anomalies, results
            
        except FileNotFoundError:
            print(f"[TEST] File not found: {file_path}")
            return [], []
        except Exception as e:
            print(f"[TEST] Error: {e}")
            import traceback
            traceback.print_exc()
            return [], []

if __name__ == "__main__":
    test_debug_stagnant()