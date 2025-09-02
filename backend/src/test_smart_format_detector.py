"""
Comprehensive Test Suite for SmartFormatDetector

This test suite validates the Smart Configuration system for location formats,
covering all supported patterns, edge cases, and integration scenarios.

Test Coverage:
1. Pattern Detection (Position+Level, Standard, Compact, Special)
2. Confidence Scoring
3. Edge Cases and Error Handling
4. Integration with CanonicalLocationService
5. Format Configuration Creation
6. API Integration Scenarios
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the backend src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_format_detector import (
    SmartFormatDetector, 
    PatternType, 
    FormatPattern,
    PositionLevelAnalyzer,
    StandardAnalyzer,
    CompactAnalyzer,
    SpecialAnalyzer,
    detect_location_format,
    create_format_configuration
)


class TestPatternAnalyzers(unittest.TestCase):
    """Test individual pattern analyzers"""
    
    def test_position_level_analyzer(self):
        """Test PositionLevelAnalyzer with various inputs"""
        analyzer = PositionLevelAnalyzer()
        
        # Valid position+level patterns
        valid_examples = ["010A", "325B", "245D", "156C", "087A"]
        result = analyzer.analyze(valid_examples)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.pattern_type, PatternType.POSITION_LEVEL)
        self.assertGreater(result.confidence, 0.8)
        self.assertEqual(len(result.examples), 5)
        
        # Invalid patterns should return None
        invalid_examples = ["01-01-001A", "RECV-01", "A1B2C3"]
        result = analyzer.analyze(invalid_examples)
        self.assertIsNone(result)
        
        # Mixed valid/invalid should still work if enough valid examples
        mixed_examples = ["010A", "325B", "invalid", "245D"]
        result = analyzer.analyze(mixed_examples)
        self.assertIsNotNone(result)
        self.assertGreater(result.confidence, 0.5)
    
    def test_standard_analyzer(self):
        """Test StandardAnalyzer with canonical format patterns"""
        analyzer = StandardAnalyzer()
        
        # Valid standard patterns
        valid_examples = ["01-01-001A", "02-03-045B", "10-05-123C"]
        result = analyzer.analyze(valid_examples)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.pattern_type, PatternType.STANDARD)
        self.assertGreater(result.confidence, 0.7)
        
        # Test variable padding
        variable_examples = ["1-1-1A", "01-01-01A", "1-1-001A"]
        result = analyzer.analyze(variable_examples)
        self.assertIsNotNone(result)
        
        # Invalid patterns
        invalid_examples = ["010A", "01A01A", "RECV-01"]
        result = analyzer.analyze(invalid_examples)
        self.assertIsNone(result)
    
    def test_compact_analyzer(self):
        """Test CompactAnalyzer with compact format patterns"""
        analyzer = CompactAnalyzer()
        
        # Valid compact patterns
        valid_examples = ["01A01A", "02B15C", "03C25D"]
        result = analyzer.analyze(valid_examples)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.pattern_type, PatternType.COMPACT)
        self.assertGreater(result.confidence, 0.6)
        
        # Invalid patterns
        invalid_examples = ["010A", "01-01-001A", "RECV-01"]
        result = analyzer.analyze(invalid_examples)
        self.assertIsNone(result)
    
    def test_special_analyzer(self):
        """Test SpecialAnalyzer with special location patterns"""
        analyzer = SpecialAnalyzer()
        
        # Valid special patterns
        valid_examples = ["RECV-01", "STAGE-02", "DOCK-01", "RECEIVING"]
        result = analyzer.analyze(valid_examples)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.pattern_type, PatternType.SPECIAL)
        self.assertGreater(result.confidence, 0.8)
        
        # Invalid patterns
        invalid_examples = ["010A", "01-01-001A", "01A01A"]
        result = analyzer.analyze(invalid_examples)
        self.assertIsNone(result)


class TestSmartFormatDetector(unittest.TestCase):
    """Test main SmartFormatDetector class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = SmartFormatDetector()
    
    def test_position_level_detection(self):
        """Test detection of position+level format"""
        examples = ["010A", "325B", "245D", "156C", "087A"]
        result = self.detector.detect_format(examples)
        
        self.assertTrue(result['detected_pattern'])
        self.assertEqual(result['detected_pattern']['pattern_type'], 'position_level')
        self.assertGreater(result['confidence'], 0.8)
        self.assertIn('canonical_examples', result)
        self.assertGreater(len(result['canonical_examples']), 0)
        
        # Check canonical conversion examples
        self.assertIn('010A → 01-01-010A', result['canonical_examples'])
    
    def test_standard_format_detection(self):
        """Test detection of standard canonical format"""
        examples = ["01-01-001A", "02-03-045B", "10-05-123C"]
        result = self.detector.detect_format(examples)
        
        self.assertTrue(result['detected_pattern'])
        self.assertEqual(result['detected_pattern']['pattern_type'], 'standard')
        self.assertGreater(result['confidence'], 0.7)
    
    def test_compact_format_detection(self):
        """Test detection of compact format"""
        examples = ["01A01A", "02B15C", "03C25D"]
        result = self.detector.detect_format(examples)
        
        self.assertTrue(result['detected_pattern'])
        self.assertEqual(result['detected_pattern']['pattern_type'], 'compact')
        self.assertGreater(result['confidence'], 0.6)
    
    def test_special_format_detection(self):
        """Test detection of special location format"""
        examples = ["RECV-01", "STAGE-02", "DOCK-01"]
        result = self.detector.detect_format(examples)
        
        self.assertTrue(result['detected_pattern'])
        self.assertEqual(result['detected_pattern']['pattern_type'], 'special')
        self.assertGreater(result['confidence'], 0.8)
    
    def test_mixed_format_handling(self):
        """Test handling of mixed format examples"""
        # Mix different formats - should pick the most confident one
        examples = ["010A", "325B", "01-01-001A", "245D"]
        result = self.detector.detect_format(examples)
        
        # Should detect position_level due to majority
        self.assertTrue(result['detected_pattern'])
        self.assertEqual(result['detected_pattern']['pattern_type'], 'position_level')
        self.assertGreater(len(result['all_patterns']), 1)  # Should find multiple patterns
    
    def test_empty_input_handling(self):
        """Test handling of empty or invalid inputs"""
        # Empty list
        result = self.detector.detect_format([])
        self.assertIsNone(result['detected_pattern'])
        self.assertEqual(result['confidence'], 0.0)
        
        # None input
        result = self.detector.detect_format(None)
        self.assertIsNone(result['detected_pattern'])
        
        # Invalid examples
        result = self.detector.detect_format(["", "   ", None, 123])
        self.assertIsNone(result['detected_pattern'])
    
    def test_confidence_scoring(self):
        """Test confidence scoring accuracy"""
        # High confidence case - many consistent examples
        high_conf_examples = ["010A", "325B", "245D", "156C", "087A", "234B", "445C"]
        result = self.detector.detect_format(high_conf_examples)
        high_confidence = result['confidence']
        
        # Low confidence case - few examples
        low_conf_examples = ["010A", "325B"]
        result = self.detector.detect_format(low_conf_examples)
        low_confidence = result['confidence']
        
        # High confidence should be greater than low confidence
        self.assertGreater(high_confidence, low_confidence)
        self.assertGreater(high_confidence, 0.8)
    
    def test_canonical_example_generation(self):
        """Test generation of canonical conversion examples"""
        examples = ["010A", "325B", "245D"]
        result = self.detector.detect_format(examples)
        
        canonical_examples = result['canonical_examples']
        self.assertGreater(len(canonical_examples), 0)
        
        # Check format of canonical examples
        for example in canonical_examples:
            self.assertIn('→', example)
            self.assertTrue(example.startswith(('010A', '325B', '245D')))
    
    def test_recommendations_generation(self):
        """Test generation of actionable recommendations"""
        examples = ["010A", "325B"]
        result = self.detector.detect_format(examples)
        
        recommendations = result['recommendations']
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Should suggest providing more examples for small sample size
        recommendation_text = ' '.join(recommendations)
        self.assertIn('more examples', recommendation_text.lower())


class TestFormatConfiguration(unittest.TestCase):
    """Test format configuration creation and validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = SmartFormatDetector()
    
    def test_format_config_creation(self):
        """Test creation of complete format configuration"""
        examples = ["010A", "325B", "245D"]
        detection_result = self.detector.detect_format(examples)
        
        warehouse_context = {
            'name': 'Test Warehouse',
            'description': 'Test facility'
        }
        
        format_config = self.detector.create_format_config(detection_result, warehouse_context)
        
        # Validate required fields
        required_fields = [
            'pattern_type', 'confidence', 'canonical_converter',
            'examples', 'description', 'detection_metadata'
        ]
        for field in required_fields:
            self.assertIn(field, format_config)
        
        # Validate warehouse context is included
        self.assertIn('warehouse_context', format_config)
        self.assertEqual(format_config['warehouse_context']['name'], 'Test Warehouse')
    
    def test_format_config_validation(self):
        """Test validation of format configurations"""
        # Valid configuration
        valid_config = {
            'pattern_type': 'position_level',
            'confidence': 0.95,
            'canonical_converter': '01-01-{position:03d}{level}',
            'examples': ['010A', '325B']
        }
        
        validation = self.detector.validate_format_config(valid_config)
        self.assertTrue(validation['valid'])
        self.assertEqual(len(validation['errors']), 0)
        
        # Invalid configuration - missing required fields
        invalid_config = {
            'pattern_type': 'position_level'
            # Missing other required fields
        }
        
        validation = self.detector.validate_format_config(invalid_config)
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['errors']), 0)
        
        # Invalid pattern type
        invalid_pattern_config = {
            'pattern_type': 'invalid_type',
            'confidence': 0.95,
            'canonical_converter': 'test'
        }
        
        validation = self.detector.validate_format_config(invalid_pattern_config)
        self.assertFalse(validation['valid'])


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = SmartFormatDetector()
    
    def test_very_long_examples_list(self):
        """Test handling of very long examples list"""
        # Create 100 examples
        examples = [f"{i:03d}A" for i in range(100)]
        result = self.detector.detect_format(examples)
        
        # Should limit examples and still work
        self.assertTrue(result['detected_pattern'])
        self.assertLessEqual(len(result['input_examples']), 20)  # Limited in _clean_examples
    
    def test_inconsistent_examples(self):
        """Test handling of inconsistent example formats"""
        inconsistent_examples = [
            "010A",      # position_level
            "01-01-001A", # standard  
            "01A01A",     # compact
            "RECV-01",    # special
            "invalid123"  # invalid
        ]
        
        result = self.detector.detect_format(inconsistent_examples)
        
        # Should still detect something, likely with lower confidence
        # The exact result depends on which pattern has more matches
        self.assertGreater(len(result['all_patterns']), 1)
    
    def test_special_characters_handling(self):
        """Test handling of examples with special characters"""
        special_examples = ["010A", "325B!", "245D@", "156C#"]
        result = self.detector.detect_format(special_examples)
        
        # Should handle cleaning and still detect valid patterns
        # Depending on implementation, might detect based on valid examples only
        if result['detected_pattern']:
            self.assertGreater(result['confidence'], 0)
    
    def test_case_sensitivity_handling(self):
        """Test handling of different case examples"""
        mixed_case_examples = ["010a", "325B", "245d", "156C"]
        result = self.detector.detect_format(mixed_case_examples)
        
        # Should normalize to uppercase and detect pattern
        self.assertTrue(result['detected_pattern'])
        self.assertEqual(result['detected_pattern']['pattern_type'], 'position_level')
        
        # Check that examples are normalized
        for example in result['input_examples']:
            self.assertEqual(example, example.upper())
    
    def test_whitespace_handling(self):
        """Test handling of examples with whitespace"""
        whitespace_examples = ["  010A  ", " 325B", "245D ", "\t156C\n"]
        result = self.detector.detect_format(whitespace_examples)
        
        # Should strip whitespace and detect pattern
        self.assertTrue(result['detected_pattern'])
        
        # Check that whitespace is stripped
        for example in result['input_examples']:
            self.assertEqual(example, example.strip())


class TestIntegrationWithCanonicalService(unittest.TestCase):
    """Test integration with existing CanonicalLocationService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = SmartFormatDetector()
    
    @patch('smart_format_detector.logger')
    def test_integration_workflow(self, mock_logger):
        """Test complete integration workflow"""
        # 1. Detect format
        examples = ["010A", "325B", "245D"]
        detection_result = self.detector.detect_format(examples)
        
        # 2. Create format configuration
        format_config = self.detector.create_format_config(detection_result)
        
        # 3. Validate configuration
        validation = self.detector.validate_format_config(format_config)
        
        self.assertTrue(validation['valid'])
        self.assertTrue(detection_result['detected_pattern'])
        self.assertIn('canonical_examples', detection_result)
    
    def test_canonical_conversion_compatibility(self):
        """Test compatibility with canonical location conversion"""
        examples = ["010A", "325B", "245D"]
        result = self.detector.detect_format(examples)
        
        canonical_examples = result['canonical_examples']
        
        # Verify canonical format structure
        for canonical_example in canonical_examples:
            if '→' in canonical_example:
                original, canonical = canonical_example.split(' → ')
                # Canonical format should match expected pattern
                self.assertRegex(canonical, r'^\d{2}-\d{2}-\d{3}[A-Z]$')


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def test_detect_location_format_function(self):
        """Test detect_location_format convenience function"""
        examples = ["010A", "325B", "245D"]
        result = detect_location_format(examples)
        
        self.assertIn('detected_pattern', result)
        self.assertIn('confidence', result)
        self.assertIn('canonical_examples', result)
    
    def test_create_format_configuration_function(self):
        """Test create_format_configuration convenience function"""
        examples = ["010A", "325B", "245D"]
        warehouse_context = {'name': 'Test Warehouse'}
        
        config = create_format_configuration(examples, warehouse_context)
        
        if config:  # Only test if detection succeeded
            self.assertIn('pattern_type', config)
            self.assertIn('warehouse_context', config)


class TestPerformanceAndScalability(unittest.TestCase):
    """Test performance and scalability aspects"""
    
    def test_large_example_set_performance(self):
        """Test performance with large example sets"""
        import time
        
        # Create large example set
        large_examples = [f"{i:03d}A" for i in range(50)]
        
        start_time = time.time()
        result = detect_location_format(large_examples)
        end_time = time.time()
        
        # Should complete within reasonable time (adjust as needed)
        execution_time = end_time - start_time
        self.assertLess(execution_time, 2.0)  # Should complete within 2 seconds
        
        if result['detected_pattern']:
            self.assertGreater(result['confidence'], 0)


def run_comprehensive_test_suite():
    """Run all tests and generate a comprehensive report"""
    
    print("="*80)
    print("SMART FORMAT DETECTOR - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestPatternAnalyzers,
        TestSmartFormatDetector,
        TestFormatConfiguration,
        TestEdgeCasesAndErrorHandling,
        TestIntegrationWithCanonicalService,
        TestConvenienceFunctions,
        TestPerformanceAndScalability
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run comprehensive test suite
    success = run_comprehensive_test_suite()
    
    if success:
        print("\n🎉 All tests passed! Smart Format Detector is ready for production.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review and fix issues before deployment.")
        sys.exit(1)