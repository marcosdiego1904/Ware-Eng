"""
Comprehensive Test Suite for RulePatternResolver
Tests dynamic pattern resolution across different warehouse location formats.

This test suite validates:
1. Template-based pattern generation for zone-based, position-level, and canonical formats
2. Pattern resolver integration with rule evaluators
3. Backward compatibility with existing location formats
4. Cache performance and TTL behavior
5. Fallback mechanisms for error conditions
"""

import unittest
import pandas as pd
import tempfile
import sqlite3
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Test imports
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rule_pattern_resolver import RulePatternResolver, PatternSet
from rule_engine import RuleEngine, LocationSpecificStagnantEvaluator, LocationMappingErrorEvaluator


class TestRulePatternResolver(unittest.TestCase):
    """Test RulePatternResolver core functionality"""

    def setUp(self):
        """Set up test environment with mock database and app context"""
        self.mock_db = Mock()
        self.mock_app = Mock()

        # Create test resolver
        self.resolver = RulePatternResolver(self.mock_db, self.mock_app)

        # Test warehouse contexts
        self.zone_warehouse = {
            'warehouse_id': 'USER_TESTWAREHOUSE',
            'detection_method': 'zone_based'
        }

        self.position_warehouse = {
            'warehouse_id': 'USER_POSITIONTEST',
            'detection_method': 'position_level'
        }

    def test_extract_warehouse_id(self):
        """Test warehouse ID extraction from different context formats"""
        # Direct warehouse_id
        context1 = {'warehouse_id': 'TEST_WAREHOUSE'}
        self.assertEqual(self.resolver._extract_warehouse_id(context1), 'TEST_WAREHOUSE')

        # Warehouse fallback
        context2 = {'warehouse': 'FALLBACK_WAREHOUSE'}
        self.assertEqual(self.resolver._extract_warehouse_id(context2), 'FALLBACK_WAREHOUSE')

        # Detection method fallback
        context3 = {'detection_method': 'USER_METHOD_WAREHOUSE'}
        self.assertEqual(self.resolver._extract_warehouse_id(context3), 'USER_METHOD_WAREHOUSE')

        # Empty context
        self.assertIsNone(self.resolver._extract_warehouse_id({}))
        self.assertIsNone(self.resolver._extract_warehouse_id(None))

    def test_default_patterns(self):
        """Test default pattern generation maintains backward compatibility"""
        patterns = self.resolver._get_default_patterns('LOCATION_SPECIFIC_STAGNANT')

        self.assertIsInstance(patterns, PatternSet)
        self.assertEqual(patterns.source, 'default_fallback')
        self.assertEqual(patterns.confidence, 1.0)

        # Verify backward compatibility patterns (raw strings match exactly)
        self.assertIn(r'^\\d{3,6}[A-Z]$', patterns.storage_patterns)
        self.assertIn(r'^AISLE.*', patterns.transitional_patterns)

    def test_zone_based_pattern_generation(self):
        """Test zone-based pattern generation for ZONE-L-NNN format"""
        template_config = {
            'pattern_type': 'zone_based',
            'confidence': 0.95,
            'business_zones': ['PICK', 'BULK', 'OVER'],
            'transitional_zones': ['TRAN', 'FLOW']
        }

        patterns = self.resolver._convert_template_to_patterns(template_config, 'LOCATION_SPECIFIC_STAGNANT')

        self.assertEqual(patterns.source, 'zone_based_template')
        self.assertEqual(patterns.confidence, 0.95)

        # Check zone-based patterns
        storage_pattern = patterns.storage_patterns[0]
        self.assertIn('PICK|BULK|OVER', storage_pattern)
        self.assertIn('[A-Z]', storage_pattern)
        self.assertIn('\\d{3}', storage_pattern)

    def test_position_level_pattern_generation(self):
        """Test position+level pattern generation for NNN+L format"""
        template_config = {
            'pattern_type': 'position_level',
            'confidence': 0.90,
            'position_digits': 'variable_3_to_6'
        }

        patterns = self.resolver._convert_template_to_patterns(template_config, 'LOCATION_SPECIFIC_STAGNANT')

        self.assertEqual(patterns.source, 'position_level_template')
        self.assertEqual(patterns.confidence, 0.90)

        # Check position+level patterns
        storage_pattern = patterns.storage_patterns[0]
        self.assertIn('\\d{3,6}[A-Z]', storage_pattern)

    def test_canonical_pattern_generation(self):
        """Test canonical pattern generation for AA-RR-PPP+L format"""
        template_config = {
            'pattern_type': 'canonical',
            'confidence': 0.85
        }

        patterns = self.resolver._convert_template_to_patterns(template_config, 'LOCATION_SPECIFIC_STAGNANT')

        self.assertEqual(patterns.source, 'canonical_template')
        self.assertEqual(patterns.confidence, 0.85)

        # Check canonical patterns
        storage_pattern = patterns.storage_patterns[0]
        self.assertIn('\\d{2}-\\d{2}-\\d{3}[A-Z]', storage_pattern)

    def test_cache_functionality(self):
        """Test caching behavior and TTL expiration"""
        # Mock template config
        with patch.object(self.resolver, '_get_template_config') as mock_template:
            mock_template.return_value = {
                'pattern_type': 'zone_based',
                'confidence': 0.95,
                'business_zones': ['PICK', 'BULK']
            }

            # First call should cache the result
            patterns1 = self.resolver.get_patterns_for_rule('TEST_RULE', self.zone_warehouse)
            self.assertEqual(len(self.resolver._pattern_cache), 1)

            # Second call should use cache
            patterns2 = self.resolver.get_patterns_for_rule('TEST_RULE', self.zone_warehouse)
            self.assertEqual(patterns1.source, patterns2.source)

            # Mock template should only be called once due to caching
            self.assertEqual(mock_template.call_count, 1)

    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration behavior"""
        # Set short TTL for testing
        original_ttl = self.resolver._cache_ttl
        self.resolver._cache_ttl = 0.1  # 100ms

        try:
            with patch.object(self.resolver, '_get_template_config') as mock_template:
                mock_template.return_value = {
                    'pattern_type': 'zone_based',
                    'confidence': 0.95
                }

                # First call
                self.resolver.get_patterns_for_rule('TEST_RULE', self.zone_warehouse)
                self.assertEqual(mock_template.call_count, 1)

                # Wait for TTL expiration
                time.sleep(0.15)

                # Second call should re-query due to TTL expiration
                self.resolver.get_patterns_for_rule('TEST_RULE', self.zone_warehouse)
                self.assertEqual(mock_template.call_count, 2)

        finally:
            self.resolver._cache_ttl = original_ttl

    def test_cache_cleanup(self):
        """Test LRU cache cleanup when max size exceeded"""
        original_max_size = self.resolver._max_cache_size
        self.resolver._max_cache_size = 3  # Small size for testing

        try:
            # Clear existing cache
            self.resolver._pattern_cache.clear()

            # Fill cache beyond max size
            for i in range(5):
                cache_key = f"warehouse_{i}:rule_{i}"
                self.resolver._pattern_cache[cache_key] = {
                    'patterns': Mock(),
                    'timestamp': time.time() - i  # Different timestamps for LRU
                }

            # Trigger cleanup
            self.resolver._cleanup_cache()

            # Should have removed oldest entries (20% cleanup)
            expected_remaining = max(3, len(self.resolver._pattern_cache) - 1)  # At least max_size or current - 20%
            self.assertLessEqual(len(self.resolver._pattern_cache), expected_remaining)

        finally:
            self.resolver._max_cache_size = original_max_size

    def test_error_handling_fallback(self):
        """Test graceful fallback on template resolution errors"""
        with patch.object(self.resolver, '_get_template_config') as mock_template:
            # Simulate template resolution error
            mock_template.side_effect = Exception("Template query failed")

            # Should fall back to default patterns
            patterns = self.resolver.get_patterns_for_rule('TEST_RULE', self.zone_warehouse)

            self.assertEqual(patterns.source, 'default_fallback')
            self.assertGreater(len(patterns.storage_patterns), 0)

    def test_get_cache_stats(self):
        """Test cache statistics reporting"""
        # Add some cache entries
        self.resolver._pattern_cache['test1:rule1'] = {'timestamp': time.time()}
        self.resolver._template_cache['test1'] = {'timestamp': time.time()}

        stats = self.resolver.get_cache_stats()

        self.assertEqual(stats['pattern_cache_size'], 1)
        self.assertEqual(stats['template_cache_size'], 1)
        self.assertIn('test1:rule1', stats['pattern_cache_keys'])
        self.assertIn('test1', stats['template_cache_keys'])


class TestRuleEvaluatorIntegration(unittest.TestCase):
    """Test pattern resolver integration with rule evaluators"""

    def setUp(self):
        """Set up test environment with mock components"""
        self.mock_app = Mock()
        self.mock_resolver = Mock()

        # Create test evaluators with pattern resolver
        self.stagnant_evaluator = LocationSpecificStagnantEvaluator(
            app=self.mock_app,
            pattern_resolver=self.mock_resolver
        )

        self.mapping_evaluator = LocationMappingErrorEvaluator(
            app=self.mock_app,
            pattern_resolver=self.mock_resolver
        )

    def test_stagnant_evaluator_pattern_integration(self):
        """Test LocationSpecificStagnantEvaluator uses pattern resolver"""
        # Mock pattern resolver response
        mock_patterns = PatternSet(
            storage_patterns=[],
            transitional_patterns=[r'^TRAN-[A-Z]-\\d{3}$', r'^FLOW-[A-Z]-\\d{3}$'],
            receiving_patterns=[],
            staging_patterns=[],
            dock_patterns=[],
            special_patterns=[],
            confidence=0.95,
            source='zone_based_template'
        )
        self.mock_resolver.get_patterns_for_rule.return_value = mock_patterns

        # Test data with zone-based locations
        test_data = pd.DataFrame({
            'pallet_id': ['P001', 'P002', 'P003'],
            'location': ['TRAN-A-150', 'FLOW-B-075', 'PICK-C-001'],
            'creation_date': [
                datetime.now() - timedelta(days=30),
                datetime.now() - timedelta(days=25),
                datetime.now() - timedelta(days=20)
            ]
        })

        warehouse_context = {'warehouse_id': 'USER_TESTWAREHOUSE'}
        conditions = {'location_pattern': 'AISLE*'}

        # Test actual method that exists
        patterns = self.stagnant_evaluator._get_location_patterns(conditions, warehouse_context)

        # Verify pattern resolver was called
        self.mock_resolver.get_patterns_for_rule.assert_called_once_with(
            'LOCATION_SPECIFIC_STAGNANT', warehouse_context
        )

        # Verify patterns were processed correctly (anchors removed)
        self.assertIn('TRAN-[A-Z]-\\d{3}', patterns)
        self.assertIn('FLOW-[A-Z]-\\d{3}', patterns)

    def test_mapping_evaluator_pattern_integration(self):
        """Test LocationMappingErrorEvaluator uses pattern resolver"""
        # Mock pattern resolver response
        mock_patterns = PatternSet(
            storage_patterns=[r'^PICK-[A-Z]-\\d{3}$', r'^BULK-[A-Z]-\\d{3}$'],
            transitional_patterns=[r'^TRAN-[A-Z]-\\d{3}$'],
            receiving_patterns=[r'^RECV-\\d+$'],
            staging_patterns=[r'^STAGE-\\d+$'],
            dock_patterns=[r'^DOCK-\\d+$'],
            special_patterns=[],
            confidence=0.95,
            source='zone_based_template'
        )
        self.mock_resolver.get_patterns_for_rule.return_value = mock_patterns

        warehouse_context = {'warehouse_id': 'USER_TESTWAREHOUSE'}

        # Test pattern retrieval
        patterns = self.mapping_evaluator._get_location_type_patterns_enhanced(warehouse_context)

        # Verify pattern resolver was called
        self.mock_resolver.get_patterns_for_rule.assert_called_once_with(
            'LOCATION_MAPPING_ERROR', warehouse_context
        )

        # Verify pattern structure
        self.assertIn('STORAGE', patterns)
        self.assertIn('TRANSITIONAL', patterns)
        self.assertIn('RECEIVING', patterns)

        # Verify specific patterns (should have anchors removed for pandas compatibility)
        self.assertIn('PICK-[A-Z]-\\\\d{3}', patterns['STORAGE'])
        self.assertIn('BULK-[A-Z]-\\\\d{3}', patterns['STORAGE'])
        self.assertIn('TRAN-[A-Z]-\\\\d{3}', patterns['TRANSITIONAL'])

    def test_backward_compatibility_without_resolver(self):
        """Test evaluators work without pattern resolver (backward compatibility)"""
        # Create evaluators without pattern resolver
        stagnant_evaluator = LocationSpecificStagnantEvaluator(app=self.mock_app)
        mapping_evaluator = LocationMappingErrorEvaluator(app=self.mock_app)

        # Verify they initialize without error
        self.assertIsNone(stagnant_evaluator.pattern_resolver)
        self.assertIsNone(mapping_evaluator.pattern_resolver)

        # Verify fallback behavior works
        warehouse_context = {'warehouse_id': 'USER_TESTWAREHOUSE'}
        conditions = {'location_pattern': 'AISLE*'}

        # These should fall back to original patterns
        stagnant_patterns = stagnant_evaluator._get_location_patterns(conditions, warehouse_context)
        mapping_patterns = mapping_evaluator._get_location_type_patterns_enhanced(warehouse_context)

        # Should return original hardcoded patterns
        self.assertIn('AISLE.*', stagnant_patterns)
        self.assertIsInstance(mapping_patterns, dict)


class TestEndToEndPatternResolution(unittest.TestCase):
    """End-to-end testing of pattern resolution with actual rule engine"""

    def setUp(self):
        """Set up test environment with temporary database"""
        # Create temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.test_db = sqlite3.connect(self.db_path)

        # Create mock Flask app
        self.mock_app = Mock()
        self.mock_app.app_context.return_value.__enter__ = Mock()
        self.mock_app.app_context.return_value.__exit__ = Mock()

    def tearDown(self):
        """Clean up test environment"""
        try:
            self.test_db.close()
            os.close(self.db_fd)
            os.unlink(self.db_path)
        except (PermissionError, FileNotFoundError):
            # Handle Windows file locking issues gracefully
            pass

    def test_rule_engine_with_pattern_resolver(self):
        """Test complete rule engine initialization with pattern resolver"""
        with patch('rule_engine.Rule') as mock_rule:
            # Mock active rules
            mock_rule.query.filter.return_value.all.return_value = []

            # Create rule engine
            rule_engine = RuleEngine(db_session=Mock(), app=self.mock_app)

            # Verify pattern resolver was initialized
            self.assertIn('LOCATION_SPECIFIC_STAGNANT', rule_engine.evaluators)
            self.assertIn('LOCATION_MAPPING_ERROR', rule_engine.evaluators)

            # Verify enhanced evaluators have pattern resolver
            stagnant_evaluator = rule_engine.evaluators['LOCATION_SPECIFIC_STAGNANT']
            mapping_evaluator = rule_engine.evaluators['LOCATION_MAPPING_ERROR']

            self.assertIsNotNone(stagnant_evaluator.pattern_resolver)
            self.assertIsNotNone(mapping_evaluator.pattern_resolver)


def create_test_inventory_data():
    """Create test inventory data with zone-based locations"""
    return pd.DataFrame({
        'pallet_id': [
            'P001', 'P002', 'P003', 'P004', 'P005',
            'P006', 'P007', 'P008', 'P009', 'P010'
        ],
        'location': [
            # Zone-based locations that should trigger rules
            'TRAN-A-150',  # Transitional - should trigger stagnant rule
            'FLOW-B-075',  # Transitional - should trigger stagnant rule
            'PICK-C-001',  # Storage location
            'BULK-D-200',  # Storage location
            'OVER-E-350',  # Storage location
            # Invalid/unmapped locations - should trigger mapping rule
            'INVALID-LOC-1',
            'UNMAPPED-2',
            'BAD-FORMAT',
            # Standard locations for comparison
            '100A',  # Original format
            'AISLE-5'  # Original transitional format
        ],
        'creation_date': [
            # Old dates to trigger stagnant rule
            datetime.now() - timedelta(days=30),
            datetime.now() - timedelta(days=25),
            datetime.now() - timedelta(days=20),
            datetime.now() - timedelta(days=15),
            datetime.now() - timedelta(days=10),
            datetime.now() - timedelta(days=5),
            datetime.now() - timedelta(days=4),
            datetime.now() - timedelta(days=3),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=1)
        ]
    })


if __name__ == '__main__':
    print("=== RulePatternResolver Test Suite ===")
    print("Testing dynamic pattern resolution for warehouse location formats")
    print()

    # Create test suite using modern unittest approach
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # Add test classes
    test_suite.addTests(loader.loadTestsFromTestCase(TestRulePatternResolver))
    test_suite.addTests(loader.loadTestsFromTestCase(TestRuleEvaluatorIntegration))
    test_suite.addTests(loader.loadTestsFromTestCase(TestEndToEndPatternResolution))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)

    print("\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    if result.testsRun > 0:
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print("\n=== Failures ===")
        for test, traceback in result.failures:
            print(f"FAIL: {test}")
            print(traceback)

    if result.errors:
        print("\n=== Errors ===")
        for test, traceback in result.errors:
            print(f"ERROR: {test}")
            print(traceback)

    print("\n=== Pattern Resolution Test Complete ===")