#!/usr/bin/env python3
"""
Debug script to test rule engine with your test data
"""
import sys
import pandas as pd
sys.path.append('backend/src')

# Import the rule engine and models
from rule_engine import RuleEngine
from models import Rule, RuleCategory
from database import db
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backend/warehouse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def debug_rules():
    with app.app_context():
        # Load test data
        try:
            df = pd.read_excel('test_inventory_corrected.xlsx')
            print(f"[OK] Loaded test data: {len(df)} records")
        except Exception as e:
            print(f"[ERROR] Failed to load test data: {e}")
            return
        
        print(f"[DATA] Data columns: {list(df.columns)}")
        print(f"[DATA] Sample locations: {df['location'].value_counts().head()}")
        print()
        
        # Load all rules from database
        rules = Rule.query.filter_by(is_active=True).all()
        print(f"[RULES] Found {len(rules)} active rules:")
        
        for rule in rules:
            print(f"  - {rule.name} ({rule.rule_type}) - {rule.priority}")
            try:
                conditions = rule.get_conditions()
                print(f"     Conditions: {conditions}")
            except Exception as e:
                print(f"     [ERROR] Error parsing conditions: {e}")
        print()
        
        # Initialize rule engine
        try:
            engine = RuleEngine(db.session)
            print("[OK] Rule engine initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize rule engine: {e}")
            return
        
        # Test each rule individually
        print("[TEST] Testing each rule individually:")
        for rule in rules:
            print(f"\n--- Testing {rule.name} ---")
            try:
                result = engine.evaluate_rule(rule, df)
                print(f"[OK] Execution time: {result.execution_time_ms}ms")
                print(f"[OK] Success: {result.success}")
                print(f"[OK] Anomalies found: {len(result.anomalies)}")
                
                if result.anomalies:
                    for i, anomaly in enumerate(result.anomalies[:3]):  # Show first 3
                        print(f"   * Anomaly {i+1}: {anomaly.get('description', 'No description')}")
                
                if result.error_message:
                    print(f"[WARN]  Error: {result.error_message}")
                    
            except Exception as e:
                print(f"[ERROR] Rule evaluation failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Test specific data patterns
        print(f"\n[ANALYSIS] Data analysis:")
        print(f"RECEIVING locations: {len(df[df['location'] == 'RECEIVING'])}")
        print(f"STAGING-A locations: {len(df[df['location'] == 'STAGING-A'])}")
        print(f"STAGING-B locations: {len(df[df['location'] == 'STAGING-B'])}")
        print(f"DOCK-01 locations: {len(df[df['location'] == 'DOCK-01'])}")
        print(f"DOCK-02 locations: {len(df[df['location'] == 'DOCK-02'])}")
        print(f"AISLETEST locations: {len(df[df['location'] == 'AISLETEST'])}")
        print(f"Invalid locations: {len(df[df['location'].isin(['INVALIDLOC', 'PLT041', 'PLT042'])])}")

if __name__ == "__main__":
    debug_rules()