#!/usr/bin/env python3
"""
Smart Configuration System for Location Formats - Demonstration

This script demonstrates the complete Smart Configuration system workflow,
showing how warehouses can define location formats by simply providing examples.

Usage:
    python demo_smart_format_system.py
    python demo_smart_format_system.py --interactive
    python demo_smart_format_system.py --test-patterns
"""

import sys
import os
import json
from datetime import datetime

# Add the backend src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_format_detector import SmartFormatDetector, detect_location_format, create_format_configuration


def demo_position_level_format():
    """Demonstrate position+level format detection"""
    print("\n" + "="*60)
    print("DEMO 1: POSITION+LEVEL FORMAT DETECTION")
    print("="*60)
    
    examples = ["010A", "325B", "245D", "156C", "087A"]
    print(f"Input examples: {examples}")
    print("Expected pattern: Position+Level (PPP+L)")
    
    result = detect_location_format(examples)
    
    print(f"\nDetected pattern: {result['detected_pattern']['pattern_type'] if result['detected_pattern'] else 'None'}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Analysis: {result['analysis_summary']}")
    
    print("\nCanonical conversion examples:")
    for example in result['canonical_examples'][:3]:
        print(f"  {example}")
    
    print("\nRecommendations:")
    for rec in result['recommendations'][:2]:
        print(f"  • {rec}")
    
    return result


def demo_standard_format():
    """Demonstrate standard format detection"""
    print("\n" + "="*60)
    print("DEMO 2: STANDARD CANONICAL FORMAT")
    print("="*60)
    
    examples = ["01-01-001A", "02-03-045B", "10-05-123C", "01-02-067D"]
    print(f"Input examples: {examples}")
    print("Expected pattern: Standard canonical (AA-RR-PPP+L)")
    
    result = detect_location_format(examples)
    
    print(f"\nDetected pattern: {result['detected_pattern']['pattern_type'] if result['detected_pattern'] else 'None'}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Analysis: {result['analysis_summary']}")
    
    print("\nCanonical conversion examples:")
    for example in result['canonical_examples'][:3]:
        print(f"  {example}")
    
    return result


def demo_compact_format():
    """Demonstrate compact format detection"""
    print("\n" + "="*60)
    print("DEMO 3: COMPACT FORMAT DETECTION")
    print("="*60)
    
    examples = ["01A01A", "02B15C", "03C25D", "04A45B"]
    print(f"Input examples: {examples}")
    print("Expected pattern: Compact (AA+L+PP+L)")
    
    result = detect_location_format(examples)
    
    print(f"\nDetected pattern: {result['detected_pattern']['pattern_type'] if result['detected_pattern'] else 'None'}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Analysis: {result['analysis_summary']}")
    
    print("\nCanonical conversion examples:")
    for example in result['canonical_examples'][:3]:
        print(f"  {example}")
    
    return result


def demo_special_format():
    """Demonstrate special location format detection"""
    print("\n" + "="*60)
    print("DEMO 4: SPECIAL LOCATION FORMAT")
    print("="*60)
    
    examples = ["RECV-01", "STAGE-02", "DOCK-01", "AISLE-03"]
    print(f"Input examples: {examples}")
    print("Expected pattern: Special locations")
    
    result = detect_location_format(examples)
    
    print(f"\nDetected pattern: {result['detected_pattern']['pattern_type'] if result['detected_pattern'] else 'None'}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Analysis: {result['analysis_summary']}")
    
    print("\nCanonical conversion examples:")
    for example in result['canonical_examples'][:3]:
        print(f"  {example}")
    
    return result


def demo_mixed_format():
    """Demonstrate handling of mixed format examples"""
    print("\n" + "="*60)
    print("DEMO 5: MIXED FORMAT HANDLING")
    print("="*60)
    
    examples = ["010A", "325B", "01-01-001A", "245D", "RECV-01"]
    print(f"Input examples: {examples}")
    print("Expected: Should detect the most confident pattern")
    
    result = detect_location_format(examples)
    
    print(f"\nDetected pattern: {result['detected_pattern']['pattern_type'] if result['detected_pattern'] else 'None'}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Alternative patterns found: {len(result['all_patterns'])}")
    print(f"Analysis: {result['analysis_summary']}")
    
    print("\nAll detected patterns:")
    for i, pattern in enumerate(result['all_patterns'], 1):
        print(f"  {i}. {pattern['pattern_type']} (confidence: {pattern['confidence']:.1%})")
    
    return result


def demo_format_configuration_creation():
    """Demonstrate complete format configuration creation"""
    print("\n" + "="*60)
    print("DEMO 6: FORMAT CONFIGURATION CREATION")
    print("="*60)
    
    examples = ["010A", "325B", "245D"]
    warehouse_context = {
        'name': 'Main Distribution Center',
        'description': 'Primary warehouse facility',
        'location': 'Chicago, IL'
    }
    
    print(f"Input examples: {examples}")
    print(f"Warehouse context: {warehouse_context['name']}")
    
    # Create complete format configuration
    format_config = create_format_configuration(examples, warehouse_context)
    
    if format_config:
        print(f"\nGenerated configuration:")
        print(f"  Pattern Type: {format_config['pattern_type']}")
        print(f"  Confidence: {format_config['confidence']:.1%}")
        print(f"  Components: {format_config['components']}")
        print(f"  Description: {format_config['description']}")
        
        print(f"\nDatabase storage ready:")
        print(f"  Configuration size: {len(json.dumps(format_config))} bytes")
        print(f"  Warehouse context included: {'warehouse_context' in format_config}")
        print(f"  Detection metadata: {format_config['detection_metadata']['detector_version']}")
    else:
        print("\n❌ Failed to create format configuration")
    
    return format_config


def demo_integration_with_existing_system():
    """Demonstrate integration with existing canonical location service"""
    print("\n" + "="*60)
    print("DEMO 7: INTEGRATION WITH CANONICAL LOCATION SERVICE")
    print("="*60)
    
    try:
        from location_service import get_canonical_service
        canonical_service = get_canonical_service()
        
        examples = ["010A", "325B", "245D"]
        print(f"Input examples: {examples}")
        
        # Test with existing canonical service
        print(f"\nTesting with existing CanonicalLocationService:")
        for example in examples:
            canonical = canonical_service.to_canonical(example)
            print(f"  {example} → {canonical}")
        
        # Now test with Smart Format Detector
        result = detect_location_format(examples)
        
        print(f"\nSmart Format Detector results:")
        print(f"  Detected pattern: {result['detected_pattern']['pattern_type'] if result['detected_pattern'] else 'None'}")
        print(f"  Canonical examples: {len(result['canonical_examples'])} generated")
        
        # Verify compatibility
        compatible = True
        for canonical_example in result['canonical_examples'][:3]:
            if '→' in canonical_example:
                original, detected_canonical = canonical_example.split(' → ')
                service_canonical = canonical_service.to_canonical(original.strip())
                if detected_canonical.strip() != service_canonical:
                    compatible = False
                    print(f"  ⚠️  Mismatch: {original} → Detected: {detected_canonical}, Service: {service_canonical}")
        
        if compatible:
            print("  ✅ Full compatibility with existing CanonicalLocationService")
        
    except ImportError:
        print("CanonicalLocationService not available - skipping integration test")
    except Exception as e:
        print(f"Integration test failed: {e}")


def interactive_demo():
    """Interactive demo allowing user to input their own examples"""
    print("\n" + "="*60)
    print("INTERACTIVE SMART FORMAT DETECTOR")
    print("="*60)
    
    print("Enter your location examples (one per line, empty line to finish):")
    
    examples = []
    while True:
        example = input(f"Example {len(examples) + 1}: ").strip()
        if not example:
            break
        examples.append(example)
    
    if not examples:
        print("No examples provided. Exiting.")
        return
    
    print(f"\nAnalyzing {len(examples)} examples: {examples}")
    
    result = detect_location_format(examples)
    
    print(f"\n{'='*60}")
    print("DETECTION RESULTS")
    print(f"{'='*60}")
    
    if result['detected_pattern']:
        pattern = result['detected_pattern']
        print(f"✅ Pattern detected: {pattern['pattern_type'].upper()}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Description: {pattern['description']}")
        
        print(f"\nComponents:")
        for key, value in pattern['components'].items():
            print(f"   {key}: {value}")
        
        print(f"\nCanonical conversion examples:")
        for example in result['canonical_examples']:
            print(f"   {example}")
        
        print(f"\nRecommendations:")
        for rec in result['recommendations']:
            print(f"   • {rec}")
    else:
        print("❌ No reliable pattern detected")
        print(f"Analysis: {result['analysis_summary']}")
        print(f"Recommendations:")
        for rec in result['recommendations']:
            print(f"   • {rec}")


def test_all_patterns():
    """Test all supported patterns systematically"""
    print("\n" + "="*60)
    print("SYSTEMATIC PATTERN TESTING")
    print("="*60)
    
    test_cases = [
        {
            'name': 'Position+Level',
            'examples': ['010A', '325B', '245D', '156C'],
            'expected_type': 'position_level'
        },
        {
            'name': 'Standard Canonical',
            'examples': ['01-01-001A', '02-03-045B', '10-05-123C'],
            'expected_type': 'standard'
        },
        {
            'name': 'Compact Format',
            'examples': ['01A01A', '02B15C', '03C25D'],
            'expected_type': 'compact'
        },
        {
            'name': 'Special Locations',
            'examples': ['RECV-01', 'STAGE-02', 'DOCK-01'],
            'expected_type': 'special'
        },
        {
            'name': 'Variable Padding',
            'examples': ['1-1-1A', '01-01-01A', '1-1-001A'],
            'expected_type': 'standard'
        },
        {
            'name': 'Mixed Invalid',
            'examples': ['invalid', '123xyz', 'ABC!@#'],
            'expected_type': None
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Examples: {test_case['examples']}")
        
        result = detect_location_format(test_case['examples'])
        
        detected_type = result['detected_pattern']['pattern_type'] if result['detected_pattern'] else None
        expected_type = test_case['expected_type']
        
        success = detected_type == expected_type
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"Expected: {expected_type or 'None'}")
        print(f"Detected: {detected_type or 'None'}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Status: {status}")
        
        results.append({
            'name': test_case['name'],
            'success': success,
            'expected': expected_type,
            'detected': detected_type,
            'confidence': result['confidence']
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['name']}")


def main():
    """Main demo function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Configuration System Demo')
    parser.add_argument('--interactive', action='store_true', help='Run interactive demo')
    parser.add_argument('--test-patterns', action='store_true', help='Test all patterns systematically')
    parser.add_argument('--integration', action='store_true', help='Test integration with existing system')
    
    args = parser.parse_args()
    
    print("🚀 SMART CONFIGURATION SYSTEM FOR LOCATION FORMATS")
    print("   Automatic pattern detection from user examples")
    print("   Zero-friction warehouse location format configuration")
    
    if args.interactive:
        interactive_demo()
    elif args.test_patterns:
        test_all_patterns()
    elif args.integration:
        demo_integration_with_existing_system()
    else:
        # Run all demos
        demo_position_level_format()
        demo_standard_format()
        demo_compact_format()
        demo_special_format()
        demo_mixed_format()
        demo_format_configuration_creation()
        demo_integration_with_existing_system()
    
    print("\n" + "="*60)
    print("🎉 SMART CONFIGURATION SYSTEM DEMO COMPLETE")
    print("="*60)
    print("The system is now ready for integration with warehouse templates!")
    print("Users can simply paste location examples during template creation,")
    print("and the system will automatically detect and configure the format.")


if __name__ == "__main__":
    main()