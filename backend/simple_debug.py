#!/usr/bin/env python3
"""
Simple Debug Script - No Unicode characters
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from models import Rule, Location
from enhanced_main import run_enhanced_engine

def main():
    print("DEBUGGING ANALYSIS - SIMPLE VERSION")
    print("="*50)
    
    with app.app_context():
        # Check rules
        active_rules = Rule.query.filter_by(is_active=True).count()
        print(f"Active rules in database: {active_rules}")
        
        # Check locations
        active_locations = Location.query.filter_by(is_active=True).count()
        print(f"Active locations in database: {active_locations}")
        
        if active_rules == 0:
            print("ERROR: No active rules found!")
            return
        
        # Create test data that should trigger anomalies
        now = datetime.now()
        test_data = pd.DataFrame({
            'pallet_id': ['P001', 'P002', 'P003'],
            'location': ['RECEIVING', 'RECEIVING', 'INVALID_LOC'],
            'creation_date': [
                now - timedelta(hours=10),  # Old pallet in RECEIVING
                now - timedelta(hours=8),   # Old pallet in RECEIVING  
                now - timedelta(hours=2)    # Invalid location
            ],
            'receipt_number': ['R001', 'R001', 'R002'],
            'description': ['Test A', 'Test B', 'Test C']
        })
        
        print("\nTesting with sample data:")
        print(test_data.to_string())
        
        # Test the enhanced engine
        try:
            anomalies = run_enhanced_engine(
                test_data,
                use_database_rules=True,
                rule_ids=None
            )
            
            print(f"\nResult: {len(anomalies)} anomalies found")
            
            if anomalies:
                print("\nAnomalies detected:")
                for i, anomaly in enumerate(anomalies, 1):
                    print(f"{i}. {anomaly.get('pallet_id')}: {anomaly.get('anomaly_type')}")
                    print(f"   Details: {anomaly.get('details')}")
                
                print("\nSYSTEM IS WORKING! The issue is with your specific data.")
                print("\nPossible issues with your data:")
                print("1. Column names don't match exactly (case sensitive)")
                print("2. creation_date is not in datetime format")
                print("3. Data doesn't meet the rule conditions")
                print("4. All pallets are too recent (no old pallets)")
                
            else:
                print("NO ANOMALIES FOUND - There might be a logic issue")
                
        except Exception as e:
            print(f"ERROR testing engine: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()