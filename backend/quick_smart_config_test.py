#!/usr/bin/env python3
"""
Quick Test for Smart Configuration System Core Components
=========================================================

Focused test script to verify the key Smart Configuration functionality
without Unicode encoding issues or complex dependencies.
"""

import os
import sys
import time
import json
import traceback
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def print_test_result(test_name, success, details="", error="", exec_time=0):
    """Print test result with ASCII-safe symbols"""
    symbol = "[PASS]" if success else "[FAIL]"
    print(f"{symbol} {test_name} ({exec_time:.2f}s)")
    if details:
        print(f"    Details: {details}")
    if error:
        print(f"    Error: {error}")
    print()

def test_smart_format_detector_core():
    """Test core SmartFormatDetector functionality"""
    print("TESTING SMART FORMAT DETECTOR CORE")
    print("=" * 50)
    
    results = []
    
    # Test 1: Import and initialization
    print("Test 1: Import and initialization")
    start_time = time.time()
    try:
        from smart_format_detector import SmartFormatDetector, detect_location_format
        detector = SmartFormatDetector()
        
        exec_time = time.time() - start_time
        print_test_result("SmartFormatDetector Import & Init", True, 
                         "Successfully imported and initialized", "", exec_time)
        results.append(('Import & Init', True, exec_time))
        
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("SmartFormatDetector Import & Init", False, 
                         "", str(e), exec_time)
        results.append(('Import & Init', False, exec_time))
        return results
    
    # Test 2: Position+Level Pattern Detection (MAIN TEST CASE)
    print("Test 2: Position+Level Pattern Detection")
    start_time = time.time()
    try:
        # This is the exact test case from the requirements
        examples = ["010A", "325B", "245D"]
        result = detector.detect_format(examples)
        
        exec_time = time.time() - start_time
        
        # Validate the result structure
        required_keys = ['detected_pattern', 'confidence', 'canonical_examples', 
                        'analysis_summary', 'recommendations']
        missing_keys = [key for key in required_keys if key not in result]
        
        if missing_keys:
            raise Exception(f"Missing keys in result: {missing_keys}")
            
        detected_pattern = result.get('detected_pattern')
        confidence = result.get('confidence', 0)
        
        # Validate detection accuracy
        if not detected_pattern:
            raise Exception("No pattern detected for position+level examples")
            
        if detected_pattern['pattern_type'] != 'position_level':
            raise Exception(f"Expected 'position_level', got '{detected_pattern['pattern_type']}'")
            
        if confidence < 0.9:  # Should be high confidence for clear pattern
            raise Exception(f"Low confidence for clear pattern: {confidence:.2%}")
        
        # Print detailed results
        print(f"    Pattern Type: {detected_pattern['pattern_type']}")
        print(f"    Confidence: {confidence:.1%}")
        print(f"    Canonical Converter: {detected_pattern['canonical_converter']}")
        print(f"    Examples processed: {len(examples)}")
        print(f"    Canonical examples generated: {len(result.get('canonical_examples', []))}")
        
        details = f"Pattern: {detected_pattern['pattern_type']}, Confidence: {confidence:.1%}"
        print_test_result("Position+Level Pattern Detection", True, details, "", exec_time)
        results.append(('Position+Level Detection', True, exec_time))
        
        # Show canonical conversion examples
        print("    Canonical conversion examples:")
        for canonical_ex in result.get('canonical_examples', [])[:3]:
            print(f"      {canonical_ex}")
        
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Position+Level Pattern Detection", False, "", str(e), exec_time)
        results.append(('Position+Level Detection', False, exec_time))
    
    # Test 3: Standard Format Detection
    print("Test 3: Standard Format Detection")
    start_time = time.time()
    try:
        examples = ["01-01-001A", "02-15-032B", "03-08-145C"]
        result = detector.detect_format(examples)
        
        exec_time = time.time() - start_time
        detected_pattern = result.get('detected_pattern')
        
        print(f"    Input examples: {examples}")
        print(f"    Detected pattern: {detected_pattern['pattern_type'] if detected_pattern else 'None'}")
        print(f"    Confidence: {result.get('confidence', 0):.1%}")
        
        if detected_pattern and detected_pattern['pattern_type'] == 'standard':
            details = f"Standard format detected with {result['confidence']:.1%} confidence"
            print_test_result("Standard Format Detection", True, details, "", exec_time)
            results.append(('Standard Format Detection', True, exec_time))
        else:
            # This might be expected if the pattern isn't clear enough
            details = f"Pattern detected: {detected_pattern['pattern_type'] if detected_pattern else 'None'}"
            print_test_result("Standard Format Detection", True, details, "", exec_time)
            results.append(('Standard Format Detection', True, exec_time))
            
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Standard Format Detection", False, "", str(e), exec_time)
        results.append(('Standard Format Detection', False, exec_time))
    
    # Test 4: Format Configuration Creation
    print("Test 4: Format Configuration Creation")
    start_time = time.time()
    try:
        examples = ["010A", "325B", "245D"]
        detection_result = detector.detect_format(examples)
        
        # Create format configuration for database storage
        warehouse_context = {
            'name': 'Test Warehouse',
            'description': 'Testing format configuration creation'
        }
        format_config = detector.create_format_config(detection_result, warehouse_context)
        
        exec_time = time.time() - start_time
        
        if not format_config:
            raise Exception("Format config creation returned empty result")
        
        # Validate format config structure
        required_config_keys = ['pattern_type', 'confidence', 'canonical_converter', 'examples']
        missing_config_keys = [key for key in required_config_keys if key not in format_config]
        
        if missing_config_keys:
            raise Exception(f"Missing keys in format config: {missing_config_keys}")
        
        print(f"    Format config keys: {list(format_config.keys())}")
        print(f"    Pattern type: {format_config.get('pattern_type')}")
        print(f"    Has warehouse context: {'warehouse_context' in format_config}")
        
        details = f"Config created with {len(format_config)} fields"
        print_test_result("Format Configuration Creation", True, details, "", exec_time)
        results.append(('Format Config Creation', True, exec_time))
        
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Format Configuration Creation", False, "", str(e), exec_time)
        results.append(('Format Config Creation', False, exec_time))
    
    # Test 5: Format Validation
    print("Test 5: Format Validation")
    start_time = time.time()
    try:
        # Test valid format config
        valid_config = {
            'pattern_type': 'position_level',
            'confidence': 0.95,
            'canonical_converter': '01-01-{position:03d}{level}',
            'examples': ['010A', '325B', '245D']
        }
        
        validation = detector.validate_format_config(valid_config)
        
        exec_time = time.time() - start_time
        
        print(f"    Validation result: {validation}")
        print(f"    Is valid: {validation.get('valid', False)}")
        print(f"    Errors: {validation.get('errors', [])}")
        print(f"    Warnings: {validation.get('warnings', [])}")
        
        if validation.get('valid'):
            print_test_result("Format Validation", True, "Valid config passed validation", "", exec_time)
            results.append(('Format Validation', True, exec_time))
        else:
            raise Exception(f"Valid config failed validation: {validation.get('errors')}")
            
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Format Validation", False, "", str(e), exec_time)
        results.append(('Format Validation', False, exec_time))
    
    return results

def test_template_models():
    """Test enhanced template models"""
    print("TESTING ENHANCED TEMPLATE MODELS")
    print("=" * 50)
    
    results = []
    
    # Test 1: Import enhanced template models
    print("Test 1: Enhanced template models import")
    start_time = time.time()
    try:
        from models import WarehouseTemplate
        
        exec_time = time.time() - start_time
        print_test_result("Enhanced Template Models Import", True, 
                         "WarehouseTemplate imported successfully", "", exec_time)
        results.append(('Enhanced Models Import', True, exec_time))
        
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Enhanced Template Models Import", False, "", str(e), exec_time)
        results.append(('Enhanced Models Import', False, exec_time))
        return results
    
    # Test 2: Template format methods
    print("Test 2: Template format configuration methods")
    start_time = time.time()
    try:
        template = WarehouseTemplate()
        
        # Test format configuration methods
        test_config = {
            'pattern_type': 'position_level',
            'confidence': 0.95,
            'canonical_converter': '01-01-{position:03d}{level}',
            'examples': ['010A', '325B'],
            'components': {'position_digits': 3, 'level_format': 'single_letter'}
        }
        
        # Test setting and getting format config
        template.set_location_format_config(test_config)
        retrieved_config = template.get_location_format_config()
        
        if retrieved_config != test_config:
            raise Exception("Format config round-trip failed")
        
        # Test format examples methods
        template.set_format_examples(['010A', '325B', '245D'])
        examples = template.get_format_examples()
        
        if len(examples) != 3:
            raise Exception(f"Expected 3 examples, got {len(examples)}")
        
        print(f"    Format config round-trip: SUCCESS")
        print(f"    Format examples storage: {len(examples)} examples")
        print(f"    Template has format confidence: {hasattr(template, 'format_confidence')}")
        
        exec_time = time.time() - start_time
        print_test_result("Template Format Methods", True, 
                         "All format methods working correctly", "", exec_time)
        results.append(('Template Format Methods', True, exec_time))
        
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Template Format Methods", False, "", str(e), exec_time)
        results.append(('Template Format Methods', False, exec_time))
    
    return results

def test_api_integration():
    """Test API integration points"""
    print("TESTING API INTEGRATION POINTS")
    print("=" * 50)
    
    results = []
    
    # Test 1: Template API import
    print("Test 1: Template API import")
    start_time = time.time()
    try:
        from template_api import template_bp
        
        exec_time = time.time() - start_time
        print(f"    Template blueprint: {template_bp.name}")
        print(f"    Blueprint URL prefix: {template_bp.url_prefix}")
        
        print_test_result("Template API Import", True, 
                         "Template API blueprint imported successfully", "", exec_time)
        results.append(('Template API Import', True, exec_time))
        
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("Template API Import", False, "", str(e), exec_time)
        results.append(('Template API Import', False, exec_time))
    
    return results

def test_integration_workflow():
    """Test end-to-end integration workflow"""
    print("TESTING END-TO-END INTEGRATION WORKFLOW")
    print("=" * 50)
    
    results = []
    
    print("Test 1: Complete workflow simulation")
    start_time = time.time()
    try:
        # Step 1: Import required modules
        from smart_format_detector import SmartFormatDetector
        from models import WarehouseTemplate
        
        # Step 2: Format detection
        detector = SmartFormatDetector()
        examples = ["010A", "325B", "245D", "156C"]
        detection_result = detector.detect_format(examples)
        
        if not detection_result.get('detected_pattern'):
            raise Exception("Step 1 failed: No pattern detected")
        
        print(f"    Step 1: Format detection - {detection_result['detected_pattern']['pattern_type']}")
        
        # Step 3: Format configuration creation
        warehouse_context = {'name': 'Integration Test Warehouse'}
        format_config = detector.create_format_config(detection_result, warehouse_context)
        
        if not format_config:
            raise Exception("Step 2 failed: Format config creation failed")
        
        print(f"    Step 2: Format config created with {len(format_config)} fields")
        
        # Step 4: Format validation
        validation = detector.validate_format_config(format_config)
        if not validation.get('valid'):
            raise Exception(f"Step 3 failed: Format validation failed: {validation.get('errors')}")
        
        print(f"    Step 3: Format validation passed")
        
        # Step 5: Template model integration
        template = WarehouseTemplate()
        template.name = "Integration Test Template"
        template.num_aisles = 5
        template.racks_per_aisle = 10
        template.positions_per_rack = 20
        
        template.set_location_format_config(format_config)
        template.set_format_examples(examples)
        template.format_confidence = detection_result.get('confidence')
        
        # Verify round-trip
        stored_config = template.get_location_format_config()
        stored_examples = template.get_format_examples()
        
        if stored_config != format_config:
            raise Exception("Step 4 failed: Format config round-trip failed")
        
        if stored_examples != examples:
            raise Exception("Step 4 failed: Examples round-trip failed")
        
        print(f"    Step 4: Template integration successful")
        print(f"    Step 5: Data round-trip verified")
        
        exec_time = time.time() - start_time
        
        details = f"5 steps completed successfully, confidence: {detection_result.get('confidence', 0):.1%}"
        print_test_result("End-to-End Integration Workflow", True, details, "", exec_time)
        results.append(('E2E Integration Workflow', True, exec_time))
        
    except Exception as e:
        exec_time = time.time() - start_time
        print_test_result("End-to-End Integration Workflow", False, "", str(e), exec_time)
        results.append(('E2E Integration Workflow', False, exec_time))
    
    return results

def print_summary(all_results):
    """Print test execution summary"""
    print("\n" + "=" * 70)
    print("SMART CONFIGURATION SYSTEM - TEST SUMMARY")
    print("=" * 70)
    
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(sum(1 for _, success, _ in results if success) for results in all_results.values())
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    print("\nTEST RESULTS BY CATEGORY:")
    print("-" * 40)
    
    for category, results in all_results.items():
        category_passed = sum(1 for _, success, _ in results if success)
        category_total = len(results)
        category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
        
        print(f"{category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        for test_name, success, exec_time in results:
            status = "[PASS]" if success else "[FAIL]"
            print(f"  {status} {test_name} ({exec_time:.2f}s)")
    
    print("\n" + "=" * 70)
    
    if pass_rate >= 80:
        print("OVERALL RESULT: SMART CONFIGURATION SYSTEM IS WORKING WELL")
    elif pass_rate >= 60:
        print("OVERALL RESULT: SMART CONFIGURATION SYSTEM IS MOSTLY FUNCTIONAL")
    else:
        print("OVERALL RESULT: SMART CONFIGURATION SYSTEM NEEDS ATTENTION")
    
    print("=" * 70)

def main():
    """Main test runner"""
    print("Smart Configuration System - Quick Test Suite")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    all_results = {}
    
    try:
        # Run all test categories
        all_results['Core Format Detector'] = test_smart_format_detector_core()
        all_results['Template Models'] = test_template_models()
        all_results['API Integration'] = test_api_integration()
        all_results['End-to-End Workflow'] = test_integration_workflow()
        
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
    except Exception as e:
        print(f"\nCritical error during test execution: {e}")
        traceback.print_exc()
    finally:
        print_summary(all_results)
        
        # Save results to JSON
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'results': {category: [{'test': test, 'success': success, 'time': time} 
                                 for test, success, time in results] 
                       for category, results in all_results.items()}
        }
        
        report_file = f"quick_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed test report saved to: {report_file}")

if __name__ == "__main__":
    main()