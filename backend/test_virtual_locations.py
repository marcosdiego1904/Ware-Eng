#!/usr/bin/env python3
"""
Test Suite for Virtual Location System
Comprehensive testing of virtual location validation and performance
"""

import sys
import os
import time
import pandas as pd
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test imports
from virtual_location_engine import VirtualLocationEngine, VirtualLocationValidator
from virtual_template_integration import VirtualTemplateManager
from virtual_invalid_location_evaluator import VirtualLocationEvaluatorTester
from virtual_compatibility_layer import VirtualLocationCompatibilityManager


def create_test_warehouse_config():
    """Create a test warehouse configuration matching USER_TESTF requirements"""
    return {
        'warehouse_id': 'USER_TESTF',
        'warehouse_name': 'Test Warehouse F',
        'num_aisles': 2,
        'racks_per_aisle': 2, 
        'positions_per_rack': 35,
        'levels_per_position': 4,
        'level_names': 'ABCD',
        'default_pallet_capacity': 1,
        'receiving_areas': [
            {'code': 'RECV-01', 'capacity': 10},
            {'code': 'RECV-02', 'capacity': 10}
        ],
        'staging_areas': [
            {'code': 'STAGE-01', 'capacity': 5}
        ],
        'dock_areas': [
            {'code': 'DOCK-01', 'capacity': 2}
        ]
    }


def test_virtual_engine_creation():
    """Test 1: Virtual engine creation and basic functionality"""
    print("\n" + "="*60)
    print("TEST 1: Virtual Engine Creation")
    print("="*60)
    
    try:
        config = create_test_warehouse_config()
        engine = VirtualLocationEngine(config)
        
        summary = engine.get_warehouse_summary()
        print(f"✅ Virtual engine created successfully")
        print(f"   Warehouse ID: {summary['warehouse_id']}")
        print(f"   Total locations: {summary['total_possible_locations']:,}")
        print(f"   Storage locations: {summary['storage_locations']:,}")
        print(f"   Special areas: {summary['special_areas']}")
        print(f"   Dimensions: {summary['warehouse_dimensions']}")
        
        return True, engine
        
    except Exception as e:
        print(f"❌ Virtual engine creation failed: {e}")
        return False, None


def test_location_validation(engine):
    """Test 2: Location validation accuracy"""
    print("\n" + "="*60)
    print("TEST 2: Location Validation Accuracy")
    print("="*60)
    
    # Test locations from your critical issue report
    test_locations = {
        'expected_valid': [
            'RECV-01',
            'RECV-02', 
            'STAGE-01',
            'DOCK-01',
            'AISLE-01',
            'AISLE-02',
            '01-A01-A',  # Aisle 1, Rack A, Position 1, Level A
            '01-A35-A',  # Aisle 1, Rack A, Position 35, Level A
            '01-B01-D',  # Aisle 1, Rack B, Position 1, Level D
            '02-A15-C',  # Aisle 2, Rack A, Position 15, Level C
            '02-B35-D'   # Aisle 2, Rack B, Position 35, Level D
        ],
        'expected_invalid': [
            '',           # Empty location
            'INVALID',    # Contains "INVALID"
            'RECV-03',    # Only have RECV-01, RECV-02
            '03-A01-A',   # Aisle 3 doesn't exist (only 1-2)
            '01-C01-A',   # Rack C doesn't exist (only A-B)
            '01-A36-A',   # Position 36 exceeds capacity (max 35)
            '01-A01-E',   # Level E doesn't exist (only A-D)
            '@#$%^&*',    # Invalid characters
            'A' * 50     # Too long
        ]
    }
    
    total_tests = 0
    passed_tests = 0
    
    print("Testing valid locations:")
    for location in test_locations['expected_valid']:
        is_valid, reason = engine.validate_location(location)
        total_tests += 1
        
        if is_valid:
            print(f"  ✅ '{location}' -> VALID ({reason})")
            passed_tests += 1
        else:
            print(f"  ❌ '{location}' -> INVALID (expected valid) - {reason}")
    
    print("\nTesting invalid locations:")
    for location in test_locations['expected_invalid']:
        is_valid, reason = engine.validate_location(location)
        total_tests += 1
        
        if not is_valid:
            print(f"  ✅ '{location}' -> INVALID ({reason})")
            passed_tests += 1
        else:
            print(f"  ❌ '{location}' -> VALID (expected invalid) - {reason}")
    
    accuracy = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n📊 Validation Accuracy: {passed_tests}/{total_tests} = {accuracy:.1f}%")
    
    return accuracy >= 90.0  # 90% accuracy threshold


def test_performance_comparison(engine):
    """Test 3: Performance comparison vs. traditional database approach"""
    print("\n" + "="*60)
    print("TEST 3: Performance Comparison")
    print("="*60)
    
    # Generate test location set similar to real inventory
    test_locations = []
    
    # Add some valid storage locations
    for aisle in [1, 2]:
        for rack in ['A', 'B']:
            for pos in range(1, 21):  # Test first 20 positions
                for level in ['A', 'B', 'C']:
                    test_locations.append(f"{aisle:02d}-{rack}{pos:02d}-{level}")
    
    # Add special areas
    test_locations.extend(['RECV-01', 'RECV-02', 'STAGE-01', 'DOCK-01'])
    
    # Add some invalid locations
    test_locations.extend(['INVALID-01', '99-Z99-Z', 'ERROR', ''])
    
    print(f"Testing performance with {len(test_locations)} locations")
    
    # Test virtual validation performance
    start_time = time.time()
    
    valid_count = 0
    invalid_count = 0
    
    for location in test_locations:
        is_valid, reason = engine.validate_location(location)
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
    
    virtual_time = time.time() - start_time
    
    # Simulate old database approach (based on measurements from old system)
    # Old approach: ~150ms per location with variant generation and database queries
    estimated_old_time = len(test_locations) * 0.15
    
    performance_improvement = estimated_old_time / virtual_time if virtual_time > 0 else float('inf')
    
    print(f"📊 Performance Results:")
    print(f"   Virtual validation time: {virtual_time:.3f} seconds")
    print(f"   Estimated old approach: {estimated_old_time:.3f} seconds")
    print(f"   Performance improvement: {performance_improvement:.1f}x faster")
    print(f"   Throughput: {len(test_locations)/virtual_time:.0f} locations/second")
    print(f"   Valid locations: {valid_count}")
    print(f"   Invalid locations: {invalid_count}")
    
    return performance_improvement >= 10.0  # At least 10x improvement


def test_template_integration():
    """Test 4: Template integration with virtual locations"""
    print("\n" + "="*60)
    print("TEST 4: Template Integration")
    print("="*60)
    
    try:
        # Create template manager
        template_manager = VirtualTemplateManager()
        
        # Test template validation
        config = create_test_warehouse_config()
        validation_result = template_manager.validate_template_configuration(config)
        
        print(f"📋 Template Validation:")
        print(f"   Valid: {validation_result['is_valid']}")
        print(f"   Errors: {len(validation_result['errors'])}")
        print(f"   Warnings: {len(validation_result['warnings'])}")
        print(f"   Estimated locations: {validation_result['estimated_locations']:,}")
        
        if validation_result['errors']:
            for error in validation_result['errors']:
                print(f"   ❌ Error: {error}")
        
        if validation_result['warnings']:
            for warning in validation_result['warnings']:
                print(f"   ⚠️  Warning: {warning}")
        
        return validation_result['is_valid']
        
    except Exception as e:
        print(f"❌ Template integration test failed: {e}")
        return False


def test_compatibility_layer():
    """Test 5: Backwards compatibility layer"""
    print("\n" + "="*60)
    print("TEST 5: Backwards Compatibility")
    print("="*60)
    
    try:
        # Create compatibility manager
        compat_manager = VirtualLocationCompatibilityManager()
        
        # Test virtual warehouse detection
        warehouse_id = 'USER_TESTF'
        is_virtual = compat_manager.is_virtual_warehouse(warehouse_id)
        
        print(f"🔗 Compatibility Layer:")
        print(f"   Virtual locations enabled: {compat_manager.enable_virtual_locations}")
        print(f"   Fallback to physical: {compat_manager.fallback_to_physical}")
        print(f"   Warehouse {warehouse_id} is virtual: {is_virtual}")
        
        # Test location lookup compatibility
        test_location = 'RECV-01'
        location_data = compat_manager.get_location_by_code(warehouse_id, test_location)
        
        if location_data:
            print(f"   Location lookup for '{test_location}': ✅")
            print(f"     Source: {location_data.get('source', 'unknown')}")
            print(f"     Type: {location_data.get('location_type', 'unknown')}")
            print(f"     Capacity: {location_data.get('capacity', 'unknown')}")
        else:
            print(f"   Location lookup for '{test_location}': ❌")
        
        return location_data is not None
        
    except Exception as e:
        print(f"❌ Compatibility layer test failed: {e}")
        return False


def test_real_inventory_simulation(engine):
    """Test 6: Real inventory file simulation"""
    print("\n" + "="*60)
    print("TEST 6: Real Inventory Simulation")
    print("="*60)
    
    try:
        # Simulate inventory data similar to what caused USER_TESTF issue
        inventory_data = []
        
        # Add some pallets in valid locations
        valid_locations = ['RECV-01', 'STAGE-01', '01-A01-A', '01-A05-B', '02-B10-C', 'DOCK-01']
        for i, location in enumerate(valid_locations):
            inventory_data.append({
                'pallet_id': f'PALLET-{i+1:03d}',
                'location': location,
                'creation_date': datetime.now(),
                'description': f'Test Product {i+1}'
            })
        
        # Add some pallets in invalid locations (causing the original issue)
        invalid_locations = ['03-A01-A', 'RECV-03', '01-C15-A', '01-A99-A']
        for i, location in enumerate(invalid_locations):
            inventory_data.append({
                'pallet_id': f'INVALID-{i+1:03d}',
                'location': location,
                'creation_date': datetime.now(),
                'description': f'Invalid Location Test {i+1}'
            })
        
        # Create DataFrame
        inventory_df = pd.DataFrame(inventory_data)
        
        print(f"📦 Simulated Inventory:")
        print(f"   Total pallets: {len(inventory_df)}")
        print(f"   Valid location pallets: {len([loc for loc in valid_locations])}")
        print(f"   Invalid location pallets: {len([loc for loc in invalid_locations])}")
        
        # Test validation performance
        validator = VirtualLocationValidator(engine)
        
        all_locations = inventory_df['location'].unique().tolist()
        start_time = time.time()
        
        validation_results = validator.validate_inventory_locations(all_locations)
        
        validation_time = time.time() - start_time
        
        print(f"\n📊 Validation Results:")
        print(f"   Validation time: {validation_time:.3f} seconds")
        print(f"   Total locations: {validation_results['total_locations']}")
        print(f"   Valid locations: {len(validation_results['valid_locations'])}")
        print(f"   Invalid locations: {len(validation_results['invalid_locations'])}")
        print(f"   Success rate: {validation_results['coverage_analysis']['validation_success_rate']:.1f}%")
        
        # Show invalid locations with reasons
        print(f"\n❌ Invalid Locations Found:")
        for invalid in validation_results['invalid_locations']:
            detail = validation_results['validation_details'][invalid]
            print(f"   '{invalid}' -> {detail['reason']}")
        
        expected_invalid = len(invalid_locations)
        found_invalid = len(validation_results['invalid_locations'])
        
        return found_invalid == expected_invalid
        
    except Exception as e:
        print(f"❌ Inventory simulation test failed: {e}")
        return False


def run_full_test_suite():
    """Run the complete virtual location test suite"""
    print("🧪 VIRTUAL LOCATION SYSTEM TEST SUITE")
    print("=" * 80)
    print(f"Starting test suite at {datetime.now()}")
    
    tests = [
        ("Virtual Engine Creation", test_virtual_engine_creation),
        ("Location Validation", None),  # Requires engine from test 1
        ("Performance Comparison", None),  # Requires engine from test 1
        ("Template Integration", test_template_integration),
        ("Backwards Compatibility", test_compatibility_layer),
        ("Real Inventory Simulation", None)  # Requires engine from test 1
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    engine = None
    
    # Run test 1 first to get engine
    test_name, test_func = tests[0]
    print(f"\nRunning {test_name}...")
    success, engine = test_func()
    if success:
        passed_tests += 1
    
    if engine:
        # Run tests that require engine
        engine_dependent_tests = [
            ("Location Validation", lambda: test_location_validation(engine)),
            ("Performance Comparison", lambda: test_performance_comparison(engine)),
            ("Real Inventory Simulation", lambda: test_real_inventory_simulation(engine))
        ]
        
        for test_name, test_func in engine_dependent_tests:
            print(f"\nRunning {test_name}...")
            try:
                success = test_func()
                if success:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
    
    # Run standalone tests
    for test_name, test_func in tests[3:5]:  # Template Integration and Compatibility
        if test_func:
            print(f"\nRunning {test_name}...")
            try:
                success = test_func()
                if success:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
    
    # Final results
    print("\n" + "="*80)
    print("🎯 TEST SUITE RESULTS")
    print("="*80)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Virtual location system is ready for production.")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️  Most tests passed. Minor issues need attention before production.")
    else:
        print("❌ Multiple test failures. System needs debugging before deployment.")
    
    print(f"Test suite completed at {datetime.now()}")
    
    return passed_tests, total_tests


if __name__ == '__main__':
    """Run tests when script is executed directly"""
    try:
        passed, total = run_full_test_suite()
        exit_code = 0 if passed == total else 1
        sys.exit(exit_code)
    except Exception as e:
        print(f"💥 Test suite crashed: {e}")
        sys.exit(1)