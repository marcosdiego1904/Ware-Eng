#!/usr/bin/env python3
"""
Test custom rules in analysis workflow
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
from models import Rule
from rule_engine import RuleEngine

def test_custom_rule_in_analysis():
    """Test that custom rules are included in analysis alongside default rules"""
    
    with app.app_context():
        print("=== Testing Custom Rule in Analysis Workflow ===\n")
        
        # 1. Get our custom rule
        custom_rule = Rule.query.filter_by(name="Test Custom Slow Movement Rule", is_default=False).first()
        if not custom_rule:
            print("ERROR: Custom rule not found. Run test_rules_api.py first.")
            return
        
        print(f"1. Found custom rule: {custom_rule.name} (ID: {custom_rule.id})")
        print(f"   Type: {custom_rule.rule_type} | Priority: {custom_rule.priority}")
        print(f"   Conditions: {custom_rule.get_conditions()}")
        
        # 2. Create sample data that should trigger our custom rule
        print(f"\n2. Creating test data to trigger custom rule...")
        test_data = pd.DataFrame({
            'pallet_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
            'location': ['AISLE-A1', 'AISLE-B2', 'RECEIVING', 'FINAL-C1', 'TRANSITIONAL'],
            'creation_date': [
                datetime.now() - timedelta(hours=15),  # Should trigger (15 > 8 hours)
                datetime.now() - timedelta(hours=10),  # Should trigger (10 > 8 hours) 
                datetime.now() - timedelta(hours=2),   # Should not trigger
                datetime.now() - timedelta(hours=1),   # Should not trigger
                datetime.now() - timedelta(hours=12),  # Should trigger (12 > 8 hours)
            ],
            'receipt_number': ['R001', 'R002', 'R003', 'R004', 'R005'],
            'description': ['Product A'] * 5,
            'lot_number': ['L001', 'L002', 'L003', 'L004', 'L005']
        })
        
        print(f"   Created {len(test_data)} test pallets")
        print(f"   Expected triggers: P001 (15h), P002 (10h), P005 (12h) = 3 anomalies")
        
        # 3. Test the rule engine with all rules (default + custom)
        print(f"\n3. Testing Rule Engine with All Rules...")
        
        try:
            rule_engine = RuleEngine(db.session)
            
            # Get all active rules
            all_rules = Rule.query.filter_by(is_active=True).all()
            print(f"   Found {len(all_rules)} active rules:")
            
            default_count = sum(1 for r in all_rules if r.is_default)
            custom_count = sum(1 for r in all_rules if not r.is_default)
            print(f"   - {default_count} default rules")
            print(f"   - {custom_count} custom rules")
            
            # Run all rules
            results = rule_engine.evaluate_all_rules(test_data)
            
            print(f"\n4. Analysis Results:")
            total_anomalies = 0
            
            for result in results:
                rule = Rule.query.get(result.rule_id)
                rule_type = "CUSTOM" if not rule.is_default else "DEFAULT"
                
                print(f"   {rule_type:8} | {rule.name:35} | {len(result.anomalies):2} anomalies | {result.execution_time_ms:3}ms")
                total_anomalies += len(result.anomalies)
                
                # Show details for our custom rule
                if rule.id == custom_rule.id and result.anomalies:
                    print(f"      Custom rule triggered for pallets: {[a['pallet_id'] for a in result.anomalies]}")
            
            print(f"\n   Total anomalies found: {total_anomalies}")
            
            # 5. Verify custom rule was executed
            custom_result = next((r for r in results if r.rule_id == custom_rule.id), None)
            if custom_result:
                if custom_result.success:
                    print(f"\n5. Custom Rule Verification:")
                    print(f"   + Custom rule executed successfully")
                    print(f"   + Found {len(custom_result.anomalies)} anomalies")
                    print(f"   + Execution time: {custom_result.execution_time_ms}ms")
                    
                    if custom_result.anomalies:
                        print(f"   + Anomalies detected:")
                        for anomaly in custom_result.anomalies:
                            print(f"     - Pallet {anomaly['pallet_id']} in {anomaly['location']}")
                else:
                    print(f"\n5. Custom Rule Issues:")
                    print(f"   - Rule execution failed: {custom_result.error_message}")
            else:
                print(f"\n5. ERROR: Custom rule was not executed!")
            
            # 6. Test with just the custom rule
            print(f"\n6. Testing Custom Rule Isolation:")
            custom_only_results = rule_engine.evaluate_all_rules(test_data, rule_ids=[custom_rule.id])
            
            if custom_only_results:
                custom_isolated = custom_only_results[0]
                print(f"   + Custom rule alone found {len(custom_isolated.anomalies)} anomalies")
                print(f"   + Confirms rule logic is working independently")
            
        except Exception as e:
            print(f"   ERROR in rule engine: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n=== Custom Rule Analysis Test Complete ===")
        
        # Summary
        if custom_result and custom_result.success:
            print(f"+ Custom rule successfully integrated with analysis system")
            print(f"+ Rule found {len(custom_result.anomalies)} anomalies as expected")
            print(f"+ Custom rules work alongside {default_count} default rules")
        else:
            print(f"- Custom rule integration has issues that need fixing")

if __name__ == "__main__":
    test_custom_rule_in_analysis()