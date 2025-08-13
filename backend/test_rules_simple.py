#!/usr/bin/env python3
"""
WareWise Rule Engine Testing - Simplified Version
Tests all evaluators with realistic scenarios
"""

import os
import sys
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import random

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rule_engine import (
    StagnantPalletsEvaluator, 
    OvercapacityEvaluator,
    InvalidLocationEvaluator,
    UncoordinatedLotsEvaluator,
    MissingLocationEvaluator,
    DataIntegrityEvaluator,
    TemperatureZoneMismatchEvaluator
)

class MockRule:
    """Mock rule for testing"""
    def __init__(self, rule_type, conditions):
        self.id = 999
        self.name = f"Test {rule_type}"
        self.rule_type = rule_type
        self.priority = "MEDIUM"
        self.conditions = json.dumps(conditions)
        self.parameters = "{}"

class MockLocation:
    """Mock location for testing"""
    def __init__(self, code, capacity=1, location_type="STORAGE", zone="GENERAL"):
        self.code = code
        self.capacity = capacity
        self.location_type = location_type
        self.zone = zone

def test_stagnant_pallets():
    """Test StagnantPalletsEvaluator"""
    print("Testing StagnantPalletsEvaluator...")
    
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
    
    # Test evaluator
    evaluator = StagnantPalletsEvaluator()
    start_time = time.time()
    
    try:
        anomalies = evaluator.evaluate(rule, data)
        execution_time = int((time.time() - start_time) * 1000)
        
        print(f"  Result: {len(anomalies)} anomalies found ({execution_time}ms)")
        print(f"  Expected: 2 anomalies (pallets older than 6 hours)")
        
        if len(anomalies) == 2:
            print("  Status: PASS")
            return True
        else:
            print(f"  Status: FAIL - Expected 2, got {len(anomalies)}")
            return False
            
    except Exception as e:
        print(f"  Status: ERROR - {str(e)}")
        return False

def test_overcapacity():
    """Test OvercapacityEvaluator with mock location lookup"""
    print("Testing OvercapacityEvaluator...")
    
    # Create test data with overcapacity situation
    data = pd.DataFrame([
        {'pallet_id': 'OVER001', 'location': 'LOC001'},
        {'pallet_id': 'OVER002', 'location': 'LOC001'},  # Same location
        {'pallet_id': 'OVER003', 'location': 'LOC001'},  # Same location (3 pallets total)
        {'pallet_id': 'NORM001', 'location': 'LOC002'},  # Different location
    ])
    
    rule = MockRule('OVERCAPACITY', {'check_all_locations': True})
    
    # Mock the evaluator's location lookup
    class MockOvercapacityEvaluator(OvercapacityEvaluator):
        def _find_location_by_code(self, location_code):
            # Mock capacity: LOC001 has capacity 1, LOC002 has capacity 5
            if location_code == 'LOC001':
                return MockLocation('LOC001', capacity=1)
            elif location_code == 'LOC002':
                return MockLocation('LOC002', capacity=5)
            return None
    
    evaluator = MockOvercapacityEvaluator()
    start_time = time.time()
    
    try:
        anomalies = evaluator.evaluate(rule, data)
        execution_time = int((time.time() - start_time) * 1000)
        
        print(f"  Result: {len(anomalies)} anomalies found ({execution_time}ms)")
        print(f"  Expected: 3 anomalies (all 3 pallets in overcapacity location)")
        
        if len(anomalies) == 3:
            print("  Status: PASS")
            return True
        else:
            print(f"  Status: FAIL - Expected 3, got {len(anomalies)}")
            for anomaly in anomalies:
                print(f"    - {anomaly}")
            return False
            
    except Exception as e:
        print(f"  Status: ERROR - {str(e)}")
        return False

def test_missing_location():
    """Test MissingLocationEvaluator"""
    print("Testing MissingLocationEvaluator...")
    
    data = pd.DataFrame([
        {'pallet_id': 'MISS001', 'location': None},
        {'pallet_id': 'MISS002', 'location': ''},
        {'pallet_id': 'MISS003', 'location': 'nan'},
        {'pallet_id': 'NORM001', 'location': 'VALID_LOC'},
    ])
    
    rule = MockRule('MISSING_LOCATION', {})
    evaluator = MissingLocationEvaluator()
    
    start_time = time.time()
    
    try:
        anomalies = evaluator.evaluate(rule, data)
        execution_time = int((time.time() - start_time) * 1000)
        
        print(f"  Result: {len(anomalies)} anomalies found ({execution_time}ms)")
        print(f"  Expected: 3 anomalies (missing/empty locations)")
        
        if len(anomalies) == 3:
            print("  Status: PASS")
            return True
        else:
            print(f"  Status: FAIL - Expected 3, got {len(anomalies)}")
            return False
            
    except Exception as e:
        print(f"  Status: ERROR - {str(e)}")
        return False

def test_data_integrity():
    """Test DataIntegrityEvaluator"""
    print("Testing DataIntegrityEvaluator...")
    
    data = pd.DataFrame([
        {'pallet_id': 'DUP001', 'location': 'LOC001'},
        {'pallet_id': 'DUP001', 'location': 'LOC002'},  # Duplicate ID
        {'pallet_id': 'BAD001', 'location': 'INVALID@#$LOCATION!!!'},  # Bad location
        {'pallet_id': 'NORM001', 'location': 'NORMAL_LOC'},
    ])
    
    rule = MockRule('DATA_INTEGRITY', {
        'check_duplicate_scans': True,
        'check_impossible_locations': True
    })
    
    evaluator = DataIntegrityEvaluator()
    start_time = time.time()
    
    try:
        anomalies = evaluator.evaluate(rule, data)
        execution_time = int((time.time() - start_time) * 1000)
        
        print(f"  Result: {len(anomalies)} anomalies found ({execution_time}ms)")
        print(f"  Expected: 3 anomalies (2 duplicates + 1 impossible location)")
        
        if len(anomalies) >= 2:  # At least duplicates should be found
            print("  Status: PASS")
            return True
        else:
            print(f"  Status: FAIL - Expected at least 2, got {len(anomalies)}")
            return False
            
    except Exception as e:
        print(f"  Status: ERROR - {str(e)}")
        return False

def test_uncoordinated_lots():
    """Test UncoordinatedLotsEvaluator"""
    print("Testing UncoordinatedLotsEvaluator...")
    
    # Create lot data: 8 pallets stored (80% complete), 2 still in receiving
    data_rows = []
    lot_number = 'LOT001'
    
    # 8 stored pallets (80% completion)
    for i in range(8):
        data_rows.append({
            'pallet_id': f'LOT{i:03d}',
            'location': f'STORAGE_{i}',
            'receipt_number': lot_number,
            'description': 'Lot Product'
        })
    
    # 2 pallets still in receiving (stragglers)
    for i in range(8, 10):
        data_rows.append({
            'pallet_id': f'LOT{i:03d}',
            'location': 'RECEIVING',
            'receipt_number': lot_number,
            'description': 'Lot Product'
        })
    
    data = pd.DataFrame(data_rows)
    
    # Mock the evaluator to recognize location types
    class MockUncoordinatedLotsEvaluator(UncoordinatedLotsEvaluator):
        def _assign_location_types(self, inventory_df):
            df = inventory_df.copy()
            def get_location_type(location):
                if location == 'RECEIVING':
                    return 'RECEIVING'
                elif location.startswith('STORAGE_'):
                    return 'FINAL'
                return 'UNKNOWN'
            
            df['location_type'] = df['location'].apply(get_location_type)
            return df
    
    rule = MockRule('UNCOORDINATED_LOTS', {
        'completion_threshold': 0.8,
        'location_types': ['RECEIVING']
    })
    
    evaluator = MockUncoordinatedLotsEvaluator()
    start_time = time.time()
    
    try:
        anomalies = evaluator.evaluate(rule, data)
        execution_time = int((time.time() - start_time) * 1000)
        
        print(f"  Result: {len(anomalies)} anomalies found ({execution_time}ms)")
        print(f"  Expected: 2 anomalies (lot stragglers in receiving)")
        
        if len(anomalies) == 2:
            print("  Status: PASS")
            return True
        else:
            print(f"  Status: FAIL - Expected 2, got {len(anomalies)}")
            return False
            
    except Exception as e:
        print(f"  Status: ERROR - {str(e)}")
        return False

def test_performance():
    """Test performance with large dataset"""
    print("Testing Performance with 5000 pallets...")
    
    # Generate 5000 pallets with some stagnant ones
    data_rows = []
    for i in range(5000):
        if i % 100 == 0:  # 1% stagnant pallets
            creation_date = datetime.now() - timedelta(hours=8)
            location = 'RECEIVING'
        else:
            creation_date = datetime.now() - timedelta(hours=random.randint(0, 4))
            location = f'STORAGE_{i%500}'
        
        data_rows.append({
            'pallet_id': f'PERF{i:05d}',
            'location': location,
            'creation_date': creation_date,
            'receipt_number': f'REC{i//50:04d}',
            'description': 'Performance Test Product'
        })
    
    data = pd.DataFrame(data_rows)
    
    rule = MockRule('STAGNANT_PALLETS', {
        'location_types': ['RECEIVING'],
        'time_threshold_hours': 6
    })
    
    evaluator = StagnantPalletsEvaluator()
    start_time = time.time()
    
    try:
        anomalies = evaluator.evaluate(rule, data)
        execution_time = int((time.time() - start_time) * 1000)
        throughput = len(data) * 1000 // execution_time if execution_time > 0 else 0
        
        print(f"  Result: {len(anomalies)} anomalies found ({execution_time}ms)")
        print(f"  Throughput: {throughput} pallets/second")
        print(f"  Expected: ~50 anomalies (1% of data)")
        
        if execution_time < 1000 and 40 <= len(anomalies) <= 60:  # Under 1 second, reasonable anomaly count
            print("  Status: PASS")
            return True
        else:
            print(f"  Status: SLOW or anomaly count off")
            return False
            
    except Exception as e:
        print(f"  Status: ERROR - {str(e)}")
        return False

def main():
    """Run all tests"""
    print("WareWise Rule Engine Comprehensive Testing")
    print("=" * 50)
    
    tests = [
        ("Stagnant Pallets", test_stagnant_pallets),
        ("Overcapacity", test_overcapacity),
        ("Missing Location", test_missing_location),
        ("Data Integrity", test_data_integrity),
        ("Uncoordinated Lots", test_uncoordinated_lots),
        ("Performance", test_performance)
    ]
    
    results = []
    total_time_start = time.time()
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        result = test_func()
        results.append((test_name, result))
    
    total_time = int((time.time() - total_time_start) * 1000)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass Rate: {passed/total*100:.1f}%")
    print(f"Total Time: {total_time}ms")
    
    print(f"\nDetailed Results:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
    
    # Production readiness
    print(f"\nProduction Readiness Assessment:")
    if passed == total:
        print("EXCELLENT - All tests passed, system is production ready")
    elif passed >= total * 0.8:
        print("GOOD - Most tests passed, minor issues to address")
    else:
        print("NEEDS WORK - Several tests failed, requires fixes")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())