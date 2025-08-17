#!/usr/bin/env python3
"""
Test and validate Phase 1 warehouse detection improvements
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location
from rule_engine import RuleEngine

def test_enhanced_normalization():
    """Test the enhanced location normalization system"""
    
    print("=== TESTING ENHANCED LOCATION NORMALIZATION ===")
    
    with app.app_context():
        rule_engine = RuleEngine(db.session)
        
        # Test cases covering various format variations
        test_cases = [
            # Standard format variations
            ("02-1-011B", ["02-1-011B", "02-01-011B", "02-1-11B", "02-01-11B", "2-1-11B"]),
            ("01-01-001A", ["01-01-001A", "01-1-001A", "01-01-01A", "01-1-01A", "1-1-1A"]),
            
            # Special location formats
            ("RECV-01", ["RECV-01", "RECV-001", "RECV-1"]),
            ("STAGE-1", ["STAGE-1", "STAGE-01", "STAGE-001"]),
            ("AISLE-02", ["AISLE-02", "AISLE-002", "AISLE-2"]),
            
            # Edge cases
            ("DOCK1", ["DOCK1", "DOCK-1", "DOCK-01", "DOCK-001"]),
            ("FINAL2", ["FINAL2", "FINAL-2", "FINAL-02", "FINAL-002"]),
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for input_location, expected_variants in test_cases:
            print(f"\\nTesting: {input_location}")
            
            actual_variants = rule_engine._normalize_position_format(input_location)
            print(f"  Generated variants: {actual_variants}")
            print(f"  Expected to include: {expected_variants}")
            
            # Check if original is included
            if input_location not in actual_variants:
                print(f"  ❌ FAIL: Original location not in variants")
                continue
            
            # Check if we have good coverage of expected variants
            overlap = set(actual_variants) & set(expected_variants)
            coverage = len(overlap) / len(expected_variants)
            
            if coverage >= 0.6:  # At least 60% coverage
                print(f"  PASS: {coverage:.1%} coverage of expected variants")
                passed_tests += 1
            else:
                print(f"  FAIL: Only {coverage:.1%} coverage of expected variants")
        
        print(f"\\n📊 NORMALIZATION TEST RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests:.1%})")
        return passed_tests / total_tests >= 0.8  # 80% pass rate required

def test_warehouse_detection_accuracy():
    """Test warehouse detection accuracy with various scenarios"""
    
    print("\\n=== TESTING WAREHOUSE DETECTION ACCURACY ===")
    
    with app.app_context():
        rule_engine = RuleEngine(db.session)
        
        # Get current warehouse distribution
        warehouses = db.session.query(
            Location.warehouse_id,
            db.func.count(Location.id).label('count')
        ).group_by(Location.warehouse_id).all()
        
        print("Available warehouses:")
        warehouse_dict = {}
        for warehouse_id, count in warehouses:
            warehouse_dict[warehouse_id] = count
            print(f"  {warehouse_id}: {count} locations")
        
        if not warehouses:
            print("❌ No warehouses found in database")
            return False
        
        # Test scenarios with known location sets
        test_scenarios = []
        
        # Scenario 1: Perfect match scenario
        if 'DEFAULT' in warehouse_dict:
            default_sample = db.session.query(Location.code).filter_by(
                warehouse_id='DEFAULT'
            ).limit(10).all()
            
            if default_sample:
                test_scenarios.append({
                    'name': 'DEFAULT warehouse perfect match',
                    'locations': [loc.code for loc in default_sample],
                    'expected_warehouse': 'DEFAULT',
                    'expected_confidence': 'HIGH'
                })
        
        # Scenario 2: Mixed format scenario
        mixed_locations = [
            '02-1-011B', '01-01-007B', '01-1-019A', '02-1-003B',  # Mixed padding
            'RECV-01', 'RECV-02', 'STAGE-01'  # Special locations
        ]
        test_scenarios.append({
            'name': 'Mixed format detection',
            'locations': mixed_locations,
            'expected_warehouse': None,  # Will depend on data
            'expected_confidence': 'MEDIUM'  # At least medium confidence
        })
        
        # Scenario 3: Minimal match scenario
        minimal_locations = ['UNKNOWN-LOC-999', 'FAKE-LOCATION']
        test_scenarios.append({
            'name': 'No match scenario',
            'locations': minimal_locations,
            'expected_warehouse': None,
            'expected_confidence': 'NONE'
        })
        
        passed_scenarios = 0
        total_scenarios = len(test_scenarios)
        
        for scenario in test_scenarios:
            print(f"\\n🧪 Testing scenario: {scenario['name']}")
            print(f"   Locations: {scenario['locations'][:3]}{'...' if len(scenario['locations']) > 3 else ''}")
            
            # Create test DataFrame
            test_df = pd.DataFrame({'location': scenario['locations']})
            
            # Run detection
            detection_result = rule_engine._detect_warehouse_context(test_df)
            
            detected_warehouse = detection_result.get('warehouse_id')
            confidence_level = detection_result.get('confidence_level', 'NONE')
            match_score = detection_result.get('match_score', 0)
            
            print(f"   Result: {detected_warehouse or 'None'} (confidence: {confidence_level}, score: {match_score:.1%})")
            
            # Evaluate results
            scenario_passed = True
            
            if scenario['expected_warehouse']:
                if detected_warehouse != scenario['expected_warehouse']:
                    print(f"   ❌ Expected {scenario['expected_warehouse']}, got {detected_warehouse}")
                    scenario_passed = False
            
            # Check confidence level progression
            confidence_levels = ['NONE', 'VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']
            expected_idx = confidence_levels.index(scenario['expected_confidence'])
            actual_idx = confidence_levels.index(confidence_level) if confidence_level in confidence_levels else 0
            
            if scenario['expected_confidence'] == 'NONE':
                if confidence_level != 'NONE':
                    print(f"   ❌ Expected no detection, but got {confidence_level}")
                    scenario_passed = False
            elif actual_idx < expected_idx:
                print(f"   ❌ Expected at least {scenario['expected_confidence']} confidence, got {confidence_level}")
                scenario_passed = False
            
            if scenario_passed:
                print(f"   ✅ PASS")
                passed_scenarios += 1
            else:
                print(f"   ❌ FAIL")
        
        print(f"\\n📊 DETECTION TEST RESULTS: {passed_scenarios}/{total_scenarios} scenarios passed ({passed_scenarios/total_scenarios:.1%})")
        return passed_scenarios / total_scenarios >= 0.67  # 67% pass rate required

def test_environment_sync_utility():
    """Test the environment synchronization utility"""
    
    print("\\n=== TESTING ENVIRONMENT SYNC UTILITY ===")
    
    try:
        from environment_sync_utility import EnvironmentSyncUtility
        
        sync_util = EnvironmentSyncUtility()
        
        # Test environment analysis
        print("Testing environment analysis...")
        analysis = sync_util.analyze_environment_differences()
        
        required_fields = ['database_type', 'environment_type', 'total_locations', 'warehouse_distribution']
        analysis_valid = all(field in analysis for field in required_fields)
        
        if analysis_valid:
            print(f"✅ Environment analysis working: {analysis['environment_type']} with {analysis['total_locations']} locations")
        else:
            print(f"❌ Environment analysis missing required fields")
            return False
        
        # Test validation with sample data
        print("Testing warehouse detection validation...")
        test_locations = [
            '02-1-011B', '01-1-007B', '01-1-019A', 'RECV-01', 'STAGE-01'
        ]
        
        validation_result = sync_util.validate_warehouse_detection(test_locations)
        
        if 'detection_result' in validation_result:
            detection = validation_result['detection_result']
            print(f"✅ Validation working: detected {detection.get('warehouse_id', 'None')} with {detection.get('confidence_level', 'NONE')} confidence")
        else:
            print(f"❌ Validation failed")
            return False
        
        print("✅ Environment sync utility tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Environment sync utility test failed: {str(e)}")
        return False

def performance_benchmark():
    """Benchmark the performance of enhanced detection"""
    
    print("\\n=== PERFORMANCE BENCHMARK ===")
    
    with app.app_context():
        rule_engine = RuleEngine(db.session)
        
        # Create test dataset of various sizes
        test_sizes = [10, 50, 100]
        
        # Get sample locations from database
        all_locations = db.session.query(Location.code).limit(100).all()
        
        if not all_locations:
            print("❌ No locations available for performance testing")
            return False
        
        location_codes = [loc.code for loc in all_locations]
        
        for size in test_sizes:
            test_locations = location_codes[:size]
            test_df = pd.DataFrame({'location': test_locations})
            
            # Time the detection
            start_time = datetime.now()
            detection_result = rule_engine._detect_warehouse_context(test_df)
            end_time = datetime.now()
            
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            print(f"  {size} locations: {duration_ms:.0f}ms (target: <500ms)")
            
            if duration_ms > 500:  # Performance target
                print(f"    ⚠️  Performance warning: exceeds 500ms target")
            else:
                print(f"    ✅ Performance acceptable")
        
        return True

def main():
    """Run all Phase 1 tests"""
    
    print("PHASE 1 VALIDATION - ENHANCED WAREHOUSE DETECTION")
    print("=" * 60)
    
    test_results = {
        'normalization': test_enhanced_normalization(),
        'detection_accuracy': test_warehouse_detection_accuracy(),
        'sync_utility': test_environment_sync_utility(),
        'performance': performance_benchmark()
    }
    
    # Summary
    print("\\n" + "=" * 60)
    print("PHASE 1 TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(test_results.values())
    total_count = len(test_results)
    
    for test_name, passed in test_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    overall_success = passed_count / total_count
    print(f"\\nOverall Success Rate: {overall_success:.1%} ({passed_count}/{total_count})")
    
    if overall_success >= 0.75:  # 75% pass rate required
        print("\\nPHASE 1 VALIDATION SUCCESSFUL - Ready for Phase 2")
        return True
    else:
        print("\\nPHASE 1 VALIDATION FAILED - Fix issues before proceeding")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)