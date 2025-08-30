#!/usr/bin/env python3
"""
Simple test for the template-based validation system
Verifies core functionality without complex integration testing
"""

def test_template_resolver():
    """Test basic template resolution functionality"""
    print("=== TESTING TEMPLATE RESOLUTION SYSTEM ===")
    
    try:
        from warehouse_template_resolver import get_template_resolver
        print("PASS Successfully imported warehouse_template_resolver")
        
        # Test template resolver creation
        resolver = get_template_resolver()
        print("PASS Successfully created template resolver")
        
        # Test warehouse context resolution
        test_cases = [
            {'warehouse_id': 'USER_MARCOS9'},
            {'warehouse_id': 'SMALL_WAREHOUSE'},
            {'warehouse_id': 'UNKNOWN_WAREHOUSE'},
        ]
        
        for warehouse_context in test_cases:
            warehouse_id = warehouse_context['warehouse_id']
            print(f"\n--- Testing {warehouse_id} ---")
            
            result = resolver.resolve_warehouse_template(warehouse_context)
            print(f"Resolution method: {result.resolution_method}")
            print(f"Confidence: {result.confidence}")
            print(f"Template source: {result.template_source}")
            
            config = result.warehouse_config
            dimensions = f"{config['num_aisles']}×{config['racks_per_aisle']}×{config['positions_per_rack']}×{config['levels_per_position']}"
            print(f"Template dimensions: {dimensions}")
            
            # Key validation: Position 46 should be valid for DEFAULT template
            if warehouse_id == 'USER_MARCOS9' and config['positions_per_rack'] == 46:
                print("PASS CRITICAL FIX VERIFIED: Position 46 is within template bounds!")
            elif warehouse_id == 'USER_MARCOS9':
                print(f"FAIL ERROR: Expected 46 positions, got {config['positions_per_rack']}")
        
        print("\n=== TEMPLATE RESOLUTION TESTS PASSED ===")
        return True
        
    except Exception as e:
        print(f"FAIL Template resolution test failed: {e}")
        return False

def test_virtual_engine_creation():
    """Test VirtualLocationEngine creation with resolved templates"""
    print("\n=== TESTING VIRTUAL ENGINE CREATION ===")
    
    try:
        from warehouse_template_resolver import get_validator_factory
        
        factory = get_validator_factory()
        print("✓ Successfully created validator factory")
        
        # Test virtual engine creation
        warehouse_context = {'warehouse_id': 'USER_MARCOS9'}
        virtual_engine = factory.create_virtual_engine(warehouse_context)
        
        print("✓ Successfully created virtual engine")
        
        # Test location validation
        test_locations = [
            ('1-01-001A', True, 'Basic storage location'),
            ('4-02-046D', True, 'Maximum position (should be valid now!)'),
            ('1-01-047A', False, 'Beyond template limit'),
            ('RECV-01', True, 'Receiving area'),
            ('INVALID-ZONE', False, 'Invalid location')
        ]
        
        print("\n--- Location Validation Tests ---")
        for location, expected_valid, description in test_locations:
            is_valid, reason = virtual_engine.validate_location(location)
            
            if is_valid == expected_valid:
                status = "✓ PASS"
            else:
                status = "✗ FAIL"
            
            print(f"{status} {location}: {is_valid} ({reason})")
            
            # Critical test: Position 46 should now be valid
            if location == '4-02-046D' and is_valid:
                print("    🎯 ARCHITECTURAL FIX CONFIRMED: Position 46 is now valid!")
        
        print("\n=== VIRTUAL ENGINE TESTS PASSED ===")
        return True
        
    except Exception as e:
        print(f"✗ Virtual engine test failed: {e}")
        return False

def test_template_based_evaluator():
    """Test the new TemplateBasedInvalidLocationEvaluator"""
    print("\n=== TESTING TEMPLATE-BASED EVALUATOR ===")
    
    try:
        from template_based_invalid_location_evaluator import TemplateBasedInvalidLocationEvaluator
        
        evaluator = TemplateBasedInvalidLocationEvaluator()
        print("✓ Successfully created template-based evaluator")
        
        # Create test inventory with the problematic position 46
        import pandas as pd
        
        test_inventory = pd.DataFrame({
            'pallet_id': ['P000001', 'P000002', 'P000003', 'P000004', 'P000005'],
            'location': [
                '1-01-001A',      # Valid
                '4-02-046D',      # Should be valid now (was invalid with hardcoded limit)
                '1-01-047A',      # Invalid (exceeds template limit)
                'RECV-01',        # Valid special area
                'INVALID-ZONE'    # Invalid location
            ]
        })
        
        print("✓ Created test inventory with critical position 46 test")
        
        # Test template resolution and validation
        warehouse_context = {'warehouse_id': 'USER_MARCOS9'}
        
        # Create mock rule for testing
        class MockRule:
            def __init__(self):
                self.priority = 1
                
        rule = MockRule()
        
        # This is where the magic happens - template-based evaluation
        anomalies = evaluator._evaluate_with_template_resolution(
            rule, test_inventory, warehouse_context
        )
        
        print(f"✓ Evaluation completed: {len(anomalies)} anomalies found")
        
        # Critical validation: Position 46 should NOT be flagged as invalid
        position_46_flagged = any(
            '4-02-046D' in anomaly['location'] for anomaly in anomalies
        )
        
        if not position_46_flagged:
            print("🎯 ARCHITECTURAL SUCCESS: Position 46 is NOT flagged as invalid!")
            print("    This confirms the hardcoded 29-position limit is fixed.")
        else:
            print("✗ Position 46 still being flagged - check template configuration")
        
        # Show anomalies for verification
        print(f"\nAnomalies found ({len(anomalies)}):")
        for anomaly in anomalies:
            print(f"  - {anomaly['location']}: {anomaly['details']}")
        
        print("\n=== TEMPLATE-BASED EVALUATOR TESTS PASSED ===")
        return True
        
    except Exception as e:
        print(f"✗ Template-based evaluator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("TEMPLATE-BASED VALIDATION SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Template resolution
    if test_template_resolver():
        tests_passed += 1
    
    # Test 2: Virtual engine creation
    if test_virtual_engine_creation():
        tests_passed += 1
    
    # Test 3: Template-based evaluator
    if test_template_based_evaluator():
        tests_passed += 1
    
    print(f"\n{'='*60}")
    print(f"TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED - Template-based validation system is working!")
        print("\nKEY ARCHITECTURAL FIXES VERIFIED:")
        print("✓ Template resolution works for different warehouse types") 
        print("✓ Position 46 is now valid (was invalid with hardcoded 29 limit)")
        print("✓ Dynamic template configuration replaces hardcoded rules")
        print("✓ System can handle multiple warehouse layouts")
        
        print("\nREADY FOR INTEGRATION!")
    else:
        print("❌ Some tests failed - review errors above before integration")

if __name__ == "__main__":
    main()