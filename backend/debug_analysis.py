#!/usr/bin/env python3
"""
Debug Analysis Script
Diagnoses why the analysis isn't finding anomalies.

This script will:
1. Check if rules are being loaded
2. Verify inventory data format  
3. Test rule evaluation with sample data
4. Identify compatibility issues
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from models import Rule, RuleCategory, Location
from rule_engine import RuleEngine
from enhanced_main import run_enhanced_engine

def check_rules_status():
    """Check if rules are properly loaded and active"""
    print("="*50)
    print("1. CHECKING RULES STATUS")
    print("="*50)
    
    # Count active rules
    active_rules = Rule.query.filter_by(is_active=True).all()
    total_rules = Rule.query.count()
    
    print(f"Total rules in database: {total_rules}")
    print(f"Active rules: {len(active_rules)}")
    
    if not active_rules:
        print("❌ NO ACTIVE RULES FOUND! This is why no anomalies are detected.")
        return False
    
    print("\nActive Rules:")
    for rule in active_rules:
        print(f"  - [{rule.id}] {rule.name} ({rule.rule_type}) - {rule.priority}")
        try:
            conditions = json.loads(rule.conditions) if rule.conditions else {}
            print(f"    Conditions: {conditions}")
        except json.JSONDecodeError:
            print(f"    Conditions: INVALID JSON - {rule.conditions}")
    
    return True

def check_locations_status():
    """Check location mappings"""
    print("\n" + "="*50)
    print("2. CHECKING LOCATION MAPPINGS")
    print("="*50)
    
    locations = Location.query.filter_by(is_active=True).all()
    print(f"Active locations: {len(locations)}")
    
    if not locations:
        print("❌ NO LOCATIONS FOUND! Rules may not work properly.")
        return False
    
    print("\nLocation Mappings:")
    for loc in locations:
        print(f"  - {loc.code} ({loc.location_type}) - capacity: {loc.capacity}")
        if loc.pattern:
            print(f"    Pattern: {loc.pattern}")
    
    return True

def create_test_inventory_data():
    """Create test inventory data that should trigger anomalies"""
    print("\n" + "="*50)
    print("3. CREATING TEST DATA")
    print("="*50)
    
    # Create data that SHOULD trigger multiple anomalies
    now = datetime.now()
    
    test_data = pd.DataFrame({
        'pallet_id': ['P001', 'P002', 'P003', 'P004', 'P005', 'P006'],
        'location': ['RECEIVING', 'RECEIVING', 'AISLE-A', 'AISLE-A', 'INVALID_LOC', 'FINAL'],
        'creation_date': [
            now - timedelta(hours=10),  # Should trigger "Forgotten Pallets" (>6h in RECEIVING)
            now - timedelta(hours=8),   # Should trigger "Forgotten Pallets" (>6h in RECEIVING)  
            now - timedelta(hours=6),   # Should trigger "AISLE Stuck Pallets" (>4h in AISLE)
            now - timedelta(hours=5),   # Should trigger "AISLE Stuck Pallets" (>4h in AISLE)
            now - timedelta(hours=2),   # Should trigger "Invalid Location"
            now - timedelta(hours=1)    # Normal case
        ],
        'receipt_number': ['R001', 'R001', 'R002', 'R003', 'R004', 'R005'],
        'description': ['Test Product A', 'Test Product B', 'Test Product C', 'Test Product D', 'Test Product E', 'Test Product F']
    })
    
    print("Created test inventory data:")
    print(test_data.to_string())
    
    print(f"\nExpected anomalies:")
    print(f"  - P001: Forgotten Pallet (10h in RECEIVING)")  
    print(f"  - P002: Forgotten Pallet (8h in RECEIVING)")
    print(f"  - P003: AISLE Stuck Pallet (6h in AISLE-A)")
    print(f"  - P004: AISLE Stuck Pallet (5h in AISLE-A)")
    print(f"  - P005: Invalid Location (INVALID_LOC)")
    
    return test_data

def test_rule_engine_directly():
    """Test the rule engine directly with test data"""
    print("\n" + "="*50)
    print("4. TESTING RULE ENGINE DIRECTLY")
    print("="*50)
    
    test_data = create_test_inventory_data()
    
    try:
        # Initialize rule engine
        rule_engine = RuleEngine(db.session)
        
        # Load rules
        rules = rule_engine.load_active_rules()
        print(f"Loaded {len(rules)} active rules")
        
        if not rules:
            print("❌ No rules loaded by engine!")
            return False
        
        # Evaluate each rule individually
        all_anomalies = []
        for rule in rules:
            print(f"\nTesting rule: {rule.name}")
            result = rule_engine.evaluate_rule(rule, test_data)
            
            print(f"  Success: {result.success}")
            print(f"  Execution time: {result.execution_time_ms}ms")
            print(f"  Anomalies found: {len(result.anomalies)}")
            
            if result.error_message:
                print(f"  ❌ Error: {result.error_message}")
            
            if result.anomalies:
                print("  Anomalies:")
                for anomaly in result.anomalies:
                    print(f"    - {anomaly.get('pallet_id')}: {anomaly.get('anomaly_type')} - {anomaly.get('details')}")
                all_anomalies.extend(result.anomalies)
            else:
                print("  - No anomalies found")
        
        print(f"\nTotal anomalies across all rules: {len(all_anomalies)}")
        return len(all_anomalies) > 0
        
    except Exception as e:
        print(f"❌ Error testing rule engine: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_main():
    """Test the enhanced main engine"""
    print("\n" + "="*50)
    print("5. TESTING ENHANCED MAIN ENGINE")
    print("="*50)
    
    test_data = create_test_inventory_data()
    
    try:
        # Test the enhanced engine
        anomalies = run_enhanced_engine(
            test_data,
            use_database_rules=True,
            rule_ids=None  # Use all active rules
        )
        
        print(f"Enhanced engine returned {len(anomalies)} anomalies")
        
        if anomalies:
            print("\nAnomalies found:")
            for i, anomaly in enumerate(anomalies, 1):
                print(f"  {i}. {anomaly.get('pallet_id')}: {anomaly.get('anomaly_type')}")
                print(f"     Priority: {anomaly.get('priority')}")
                print(f"     Details: {anomaly.get('details')}")
                print()
        else:
            print("❌ No anomalies found by enhanced engine!")
        
        return len(anomalies) > 0
        
    except Exception as e:
        print(f"❌ Error testing enhanced engine: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_data_columns():
    """Check what columns are expected vs provided"""
    print("\n" + "="*50)
    print("6. CHECKING DATA COLUMN REQUIREMENTS")
    print("="*50)
    
    # Required columns for rules to work
    required_columns = [
        'pallet_id', 'location', 'creation_date', 
        'receipt_number', 'description'
    ]
    
    print("Required columns for rules to work:")
    for col in required_columns:
        print(f"  - {col}")
    
    # Check a sample data file if it exists
    sample_files = [
        'backend/data/inventory_report.xlsx',
        'backend/data/inventory_report2.xlsx',
        'backend/data/inventory_report3.xlsx'
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            print(f"\nChecking sample file: {file_path}")
            try:
                df = pd.read_excel(file_path, nrows=5)
                print("Available columns:")
                for col in df.columns:
                    print(f"  - {col}")
                
                print("Missing required columns:")
                missing = [col for col in required_columns if col not in df.columns]
                if missing:
                    for col in missing:
                        print(f"  ❌ {col}")
                else:
                    print("  ✅ All required columns present")
                
                break
            except Exception as e:
                print(f"  Error reading file: {e}")
    
    return True

def main():
    """Main debugging function"""
    print("WAREHOUSE ANALYSIS DEBUGGING")
    print("="*60)
    
    with app.app_context():
        try:
            # Run all diagnostic checks
            rules_ok = check_rules_status()
            locations_ok = check_locations_status()
            columns_ok = check_data_columns()
            
            if rules_ok and locations_ok:
                engine_ok = test_rule_engine_directly()
                main_ok = test_enhanced_main()
                
                print("\n" + "="*60)
                print("DEBUGGING SUMMARY")
                print("="*60)
                print(f"Rules loaded: {'✅' if rules_ok else '❌'}")
                print(f"Locations configured: {'✅' if locations_ok else '❌'}")
                print(f"Data columns: {'✅' if columns_ok else '❌'}")
                print(f"Rule engine works: {'✅' if engine_ok else '❌'}")
                print(f"Enhanced main works: {'✅' if main_ok else '❌'}")
                
                if not engine_ok or not main_ok:
                    print("\n🔍 ISSUE IDENTIFIED:")
                    if not engine_ok:
                        print("  - Rule engine is not detecting anomalies with test data")
                    if not main_ok:
                        print("  - Enhanced main engine is not working properly")
                    print("\nThis suggests a logic issue in the rule evaluators.")
                else:
                    print("\n✅ SYSTEM APPEARS TO BE WORKING")
                    print("The issue might be with your specific inventory data.")
                    print("Check that your data has the right column names and data types.")
            
        except Exception as e:
            print(f"❌ Error during debugging: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()