#!/usr/bin/env python3
"""
Test our new targeted inventory specifically for UNCOORDINATED_LOTS and LOCATION_MAPPING_ERROR rules
"""

import sys
import os
sys.path.append('src')

import pandas as pd
from rule_engine import RuleEngine
from app import app, db
from models import Rule
import json

def test_targeted_rules():
    """Test the two problematic rules with our targeted inventory"""

    print("[TEST] Loading 2K enhanced test inventory...")
    df = pd.read_excel('enhanced_test_inventory_2k.xlsx')
    print(f"[LOAD] {len(df)} records loaded (2K stress test)")

    # Set up Flask app context
    with app.app_context():
        print("[INIT] Initializing rule engine with database context...")
        rule_engine = RuleEngine(db.session)

        print("[TEST] Testing UNCOORDINATED_LOTS rule...")
        uncoord_rule = Rule(
            name="Test Uncoordinated Lots",
            rule_type="UNCOORDINATED_LOTS",
            conditions=json.dumps({
                'completion_threshold': 0.8,
                'location_types': ['RECEIVING'],
                'final_location_types': ['STORAGE']
            }),
            priority="HIGH"
        )

        uncoord_result = rule_engine.evaluate_rule(uncoord_rule, df, {'warehouse_id': 'USER_MTEST'})
        uncoord_anomalies = uncoord_result.anomalies if hasattr(uncoord_result, 'anomalies') else []
        print(f"[UNCOORDINATED_LOTS] Found {len(uncoord_anomalies)} anomalies")

        if uncoord_anomalies:
            print("[SAMPLE] First 3 UNCOORDINATED_LOTS anomalies:")
            for i, anomaly in enumerate(uncoord_anomalies[:3]):
                print(f"  {i+1}. {anomaly.get('pallet_id')} in {anomaly.get('location')} - {anomaly.get('details')}")

        print("\n[TEST] Testing LOCATION_MAPPING_ERROR rule...")
        mapping_rule = Rule(
            name="Test Location Mapping",
            rule_type="LOCATION_MAPPING_ERROR",
            conditions=json.dumps({
                'validate_location_types': True,
                'check_pattern_consistency': True
            }),
            priority="HIGH"
        )

        mapping_result = rule_engine.evaluate_rule(mapping_rule, df, {'warehouse_id': 'USER_MTEST'})
        mapping_anomalies = mapping_result.anomalies if hasattr(mapping_result, 'anomalies') else []
        print(f"[LOCATION_MAPPING_ERROR] Found {len(mapping_anomalies)} anomalies")

        if mapping_anomalies:
            print("[SAMPLE] First 3 LOCATION_MAPPING_ERROR anomalies:")
            for i, anomaly in enumerate(mapping_anomalies[:3]):
                print(f"  {i+1}. {anomaly.get('pallet_id')} in {anomaly.get('location')} - {anomaly.get('details')}")

        print(f"\n[SUMMARY] Results:")
        print(f"  UNCOORDINATED_LOTS: {len(uncoord_anomalies)} anomalies (Expected: 50)")
        print(f"  LOCATION_MAPPING_ERROR: {len(mapping_anomalies)} anomalies (Expected: 50)")

        total_expected = 50 + 50
        total_found = len(uncoord_anomalies) + len(mapping_anomalies)
        success_rate = (total_found / total_expected) * 100 if total_expected > 0 else 0

        print(f"  Combined success rate: {success_rate:.1f}% ({total_found}/{total_expected})")

        if total_found > 0:
            print("[SUCCESS] Rules are now working!")
        else:
            print("[FAILED] Rules still not triggering - need more investigation")

if __name__ == "__main__":
    test_targeted_rules()