#!/usr/bin/env python3
"""
Test the Fixed Flask Context Issue
Tests that the rule engine now works properly with Flask app context
"""

import os
import sys
import json
import time
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from database import db
from models import Rule, RuleCategory, Location, WarehouseConfig
from core_models import User
from rule_engine import RuleEngine, StagnantPalletsEvaluator

class MockRule:
    """Mock rule for testing"""
    def __init__(self, rule_type, conditions):
        self.id = 999
        self.name = f"Test {rule_type}"
        self.rule_type = rule_type
        self.priority = "MEDIUM"
        self.conditions = json.dumps(conditions)
        self.parameters = "{}"

def create_test_app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-key'
    
    db.init_app(app)
    
    return app

def test_stagnant_pallets_with_context():
    """Test StagnantPalletsEvaluator with proper Flask context"""
    print("Testing StagnantPalletsEvaluator with Flask Context...")
    
    app = create_test_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create test locations
        receiving_loc = Location(
            code='RECEIVING',
            location_type='RECEIVING',
            capacity=20,
            zone='SPECIAL'
        )
        db.session.add(receiving_loc)
        db.session.commit()
        
        # Create test data with stagnant pallets
        data = pd.DataFrame([
            {
                'pallet_id': 'STAG001',
                'location': 'RECEIVING',
                'creation_date': datetime.now() - timedelta(hours=8),  # 8 hours old
                'receipt_number': 'REC001',
                'description': 'Test Product'
            },
            {
                'pallet_id': 'STAG002', 
                'location': 'RECEIVING',
                'creation_date': datetime.now() - timedelta(hours=10),  # 10 hours old
                'receipt_number': 'REC002',
                'description': 'Test Product'
            },
            {
                'pallet_id': 'NORM001',
                'location': 'RECEIVING', 
                'creation_date': datetime.now() - timedelta(hours=2),  # 2 hours old (normal)
                'receipt_number': 'REC003',
                'description': 'Test Product'
            }
        ])
        
        # Create rule
        rule = MockRule('STAGNANT_PALLETS', {
            'location_types': ['RECEIVING'],
            'time_threshold_hours': 6
        })
        
        # Test evaluator with Flask app context
        evaluator = StagnantPalletsEvaluator(app=app)
        
        start_time = time.time()
        
        try:
            anomalies = evaluator.evaluate(rule, data)
            execution_time = int((time.time() - start_time) * 1000)
            
            print(f"  Result: {len(anomalies)} anomalies found ({execution_time}ms)")
            print(f"  Expected: 2 anomalies (pallets older than 6 hours)")
            
            if len(anomalies) == 2:
                print("  Status: PASS - Flask context issue FIXED!")
                return True
            else:
                print(f"  Status: FAIL - Expected 2, got {len(anomalies)}")
                for anomaly in anomalies:
                    print(f"    - {anomaly}")
                return False
                
        except Exception as e:
            print(f"  Status: ERROR - {str(e)}")
            return False

def test_rule_engine_with_context():
    """Test full RuleEngine with Flask context"""
    print("Testing RuleEngine with Flask Context...")
    
    app = create_test_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create test user (check User model fields)
        user = User(username='testuser')
        if hasattr(user, 'email'):
            user.email = 'test@test.com'
        user.set_password('test123')
        db.session.add(user)
        
        # Create rule categories
        flow_category = RuleCategory(
            name='FLOW_TIME',
            display_name='Flow & Time Rules',
            priority=1,
            description='Test category'
        )
        db.session.add(flow_category)
        
        # Create test locations
        locations = [
            Location(code='RECEIVING', location_type='RECEIVING', capacity=20, zone='SPECIAL'),
            Location(code='01-01-001A', location_type='STORAGE', capacity=1, zone='GENERAL'),
            Location(code='01-01-002A', location_type='STORAGE', capacity=1, zone='GENERAL'),
        ]
        for loc in locations:
            db.session.add(loc)
        
        db.session.commit()
        
        # Create test rule
        rule = Rule(
            name='Test Stagnant Pallets',
            description='Test rule for stagnant pallets',
            category_id=flow_category.id,
            rule_type='STAGNANT_PALLETS',
            conditions=json.dumps({
                'location_types': ['RECEIVING'],
                'time_threshold_hours': 6
            }),
            priority='HIGH',
            created_by=user.id
        )
        db.session.add(rule)
        db.session.commit()
        
        # Create test data
        test_data = pd.DataFrame([
            {
                'pallet_id': 'STAG001',
                'location': 'RECEIVING',
                'creation_date': datetime.now() - timedelta(hours=8),
                'receipt_number': 'REC001',
                'description': 'Stagnant Product'
            },
            {
                'pallet_id': 'OVER001',
                'location': '01-01-001A',  # This location has capacity 1
                'creation_date': datetime.now(),
                'receipt_number': 'REC002',
                'description': 'Overcapacity Product 1'
            },
            {
                'pallet_id': 'OVER002', 
                'location': '01-01-001A',  # Same location (overcapacity)
                'creation_date': datetime.now(),
                'receipt_number': 'REC003',
                'description': 'Overcapacity Product 2'
            }
        ])
        
        # Test RuleEngine with app context
        rule_engine = RuleEngine(db.session, app=app)
        
        start_time = time.time()
        
        try:
            results = rule_engine.evaluate_all_rules(test_data)
            execution_time = int((time.time() - start_time) * 1000)
            
            total_anomalies = sum(len(result.anomalies) for result in results)
            
            print(f"  Result: {total_anomalies} total anomalies found ({execution_time}ms)")
            print(f"  Rules executed: {len(results)}")
            
            for result in results:
                print(f"    - Rule {result.rule_id}: {len(result.anomalies)} anomalies, {result.execution_time_ms}ms")
                if result.error_message:
                    print(f"      Error: {result.error_message}")
            
            if total_anomalies > 0 and all(result.success for result in results):
                print("  Status: PASS - RuleEngine working with Flask context!")
                return True
            else:
                print("  Status: PARTIAL - Some rules had issues")
                return False
                
        except Exception as e:
            print(f"  Status: ERROR - {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Run context fix tests"""
    print("Testing Flask Context Fixes")
    print("=" * 40)
    
    tests = [
        ("StagnantPalletsEvaluator Context Fix", test_stagnant_pallets_with_context),
        ("RuleEngine Context Fix", test_rule_engine_with_context)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 40)
    print("CONTEXT FIX TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass Rate: {passed/total*100:.1f}%")
    
    print(f"\nDetailed Results:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
    
    if passed == total:
        print(f"\n✅ SUCCESS: Flask context issue has been FIXED!")
        print("The rule engine now works properly with database operations.")
        print("Ready for production deployment!")
    else:
        print(f"\n⚠️  PARTIAL: Some tests still failing, needs more work.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())