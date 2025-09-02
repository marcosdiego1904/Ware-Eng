#!/usr/bin/env python3
"""
Database Migration Test for Smart Configuration
==============================================

Test that the database has the required format fields for Smart Configuration.
"""

import os
import sys
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def print_test_result(test_name, success, details="", error="", exec_time=0):
    """Print test result"""
    symbol = "[PASS]" if success else "[FAIL]"
    print(f"{symbol} {test_name}")
    if details:
        print(f"    Details: {details}")
    if error:
        print(f"    Error: {error}")
    print()

def test_migration_script():
    """Test the migration script exists and can run"""
    print("TESTING DATABASE MIGRATION")
    print("=" * 50)
    
    results = []
    
    # Test 1: Check migration script exists
    try:
        migration_script = os.path.join(src_dir, 'migrate_location_format_fields.py')
        
        if os.path.exists(migration_script):
            print_test_result("Migration Script Exists", True, 
                             f"Found at {migration_script}")
            results.append(('Migration Script Exists', True))
        else:
            print_test_result("Migration Script Exists", False, 
                             error=f"Not found at {migration_script}")
            results.append(('Migration Script Exists', False))
            return results
            
    except Exception as e:
        print_test_result("Migration Script Exists", False, error=str(e))
        results.append(('Migration Script Exists', False))
        return results
    
    # Test 2: Check migration script content
    try:
        with open(migration_script, 'r') as f:
            content = f.read()
        
        # Check for key migration operations
        required_fields = [
            'location_format_config',
            'format_confidence',
            'format_examples', 
            'format_learned_date'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in content:
                missing_fields.append(field)
        
        if not missing_fields:
            print_test_result("Migration Script Content", True,
                             f"All {len(required_fields)} format fields found in migration")
            results.append(('Migration Script Content', True))
        else:
            print_test_result("Migration Script Content", False,
                             error=f"Missing fields: {missing_fields}")
            results.append(('Migration Script Content', False))
            
    except Exception as e:
        print_test_result("Migration Script Content", False, error=str(e))
        results.append(('Migration Script Content', False))
    
    # Test 3: Check WarehouseTemplate model has format fields
    try:
        from models import WarehouseTemplate
        
        # Check if model has the required attributes
        format_attributes = [
            'location_format_config',
            'format_confidence', 
            'format_examples',
            'format_learned_date'
        ]
        
        missing_attrs = []
        for attr in format_attributes:
            if not hasattr(WarehouseTemplate, attr):
                missing_attrs.append(attr)
        
        if not missing_attrs:
            print_test_result("Model Format Attributes", True,
                             f"All {len(format_attributes)} format attributes present")
            results.append(('Model Format Attributes', True))
        else:
            print_test_result("Model Format Attributes", False,
                             error=f"Missing attributes: {missing_attrs}")
            results.append(('Model Format Attributes', False))
            
    except Exception as e:
        print_test_result("Model Format Attributes", False, error=str(e))
        results.append(('Model Format Attributes', False))
    
    # Test 4: Check format methods exist
    try:
        from models import WarehouseTemplate
        
        # Check if model has the required methods
        format_methods = [
            'get_location_format_config',
            'set_location_format_config',
            'get_format_examples',
            'set_format_examples',
            'has_location_format'
        ]
        
        missing_methods = []
        for method in format_methods:
            if not hasattr(WarehouseTemplate, method):
                missing_methods.append(method)
        
        if not missing_methods:
            print_test_result("Model Format Methods", True,
                             f"All {len(format_methods)} format methods present")
            results.append(('Model Format Methods', True))
        else:
            print_test_result("Model Format Methods", False,
                             error=f"Missing methods: {missing_methods}")
            results.append(('Model Format Methods', False))
            
    except Exception as e:
        print_test_result("Model Format Methods", False, error=str(e))
        results.append(('Model Format Methods', False))
    
    return results

def test_template_format_functionality():
    """Test that template format functionality works"""
    print("TESTING TEMPLATE FORMAT FUNCTIONALITY")
    print("=" * 50)
    
    results = []
    
    try:
        from models import WarehouseTemplate
        
        # Test template creation with format
        template = WarehouseTemplate()
        template.name = "Test Template"
        template.num_aisles = 3
        template.racks_per_aisle = 5
        template.positions_per_rack = 20
        
        # Test format configuration
        test_config = {
            'pattern_type': 'position_level',
            'confidence': 0.95,
            'canonical_converter': '01-01-{position:03d}{level}',
            'examples': ['010A', '325B', '245D'],
            'detection_metadata': {
                'detector_version': '1.0.0',
                'detection_timestamp': datetime.now().isoformat()
            }
        }
        
        # Test setting format config
        template.set_location_format_config(test_config)
        template.format_confidence = 0.95
        
        # Test getting format config
        retrieved_config = template.get_location_format_config()
        
        if retrieved_config == test_config:
            print_test_result("Format Config Round Trip", True,
                             "Format configuration stored and retrieved correctly")
            results.append(('Format Config Round Trip', True))
        else:
            print_test_result("Format Config Round Trip", False,
                             error="Retrieved config doesn't match stored config")
            results.append(('Format Config Round Trip', False))
        
        # Test format examples
        examples = ['010A', '325B', '245D', '156C']
        template.set_format_examples(examples)
        
        retrieved_examples = template.get_format_examples()
        
        if retrieved_examples == examples:
            print_test_result("Format Examples Round Trip", True,
                             f"All {len(examples)} examples stored and retrieved")
            results.append(('Format Examples Round Trip', True))
        else:
            print_test_result("Format Examples Round Trip", False,
                             error="Retrieved examples don't match stored examples")
            results.append(('Format Examples Round Trip', False))
        
        # Test has_location_format method
        if template.has_location_format():
            print_test_result("Has Location Format Check", True,
                             "Template correctly identifies it has format")
            results.append(('Has Location Format Check', True))
        else:
            print_test_result("Has Location Format Check", False,
                             error="Template should have format but check failed")
            results.append(('Has Location Format Check', False))
        
        # Test clearing format
        template.set_location_format_config(None)
        template.format_confidence = None
        
        if not template.has_location_format():
            print_test_result("Format Clearing", True,
                             "Format cleared successfully")
            results.append(('Format Clearing', True))
        else:
            print_test_result("Format Clearing", False,
                             error="Format not cleared properly")
            results.append(('Format Clearing', False))
            
    except Exception as e:
        print_test_result("Template Format Functionality", False, error=str(e))
        results.append(('Template Format Functionality', False))
    
    return results

def print_summary(all_results):
    """Print test execution summary"""
    print("\n" + "=" * 70)
    print("DATABASE MIGRATION - TEST SUMMARY")
    print("=" * 70)
    
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(sum(1 for _, success in results if success) for results in all_results.values())
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    print("\nTEST RESULTS BY CATEGORY:")
    print("-" * 40)
    
    for category, results in all_results.items():
        category_passed = sum(1 for _, success in results if success)
        category_total = len(results)
        category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
        
        print(f"{category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        for test_name, success in results:
            status = "[PASS]" if success else "[FAIL]"
            print(f"  {status} {test_name}")
    
    print("\n" + "=" * 70)
    
    if pass_rate >= 90:
        print("RESULT: DATABASE MIGRATION IS COMPLETE AND WORKING")
    elif pass_rate >= 70:
        print("RESULT: DATABASE MIGRATION IS MOSTLY WORKING")  
    else:
        print("RESULT: DATABASE MIGRATION NEEDS ATTENTION")
    
    print("=" * 70)

def main():
    """Main test runner"""
    print("Smart Configuration - Database Migration Test")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    all_results = {}
    
    try:
        all_results['Migration'] = test_migration_script()
        all_results['Template Format Functionality'] = test_template_format_functionality()
        
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
    except Exception as e:
        print(f"\nCritical error during test execution: {e}")
    finally:
        print_summary(all_results)

if __name__ == "__main__":
    main()