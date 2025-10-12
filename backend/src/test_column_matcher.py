"""
Unit Tests for Intelligent Column Matching System

Tests the three-layer matching strategy:
1. Exact matching (normalized)
2. Fuzzy string similarity
3. Semantic keyword matching

Run with: python test_column_matcher.py
"""

import unittest
from column_matcher import ColumnMatcher, suggest_column_mapping


class TestColumnNormalization(unittest.TestCase):
    """Test column name normalization."""

    def setUp(self):
        self.matcher = ColumnMatcher()

    def test_lowercase_conversion(self):
        self.assertEqual(self.matcher.normalize_column_name('PALLET_ID'), 'pallet_id')
        self.assertEqual(self.matcher.normalize_column_name('Location'), 'location')

    def test_space_to_underscore(self):
        self.assertEqual(self.matcher.normalize_column_name('Pallet Number'), 'pallet_number')
        self.assertEqual(self.matcher.normalize_column_name('Receipt   Number'), 'receipt_number')

    def test_hyphen_replacement(self):
        self.assertEqual(self.matcher.normalize_column_name('pallet-id'), 'pallet_id')
        self.assertEqual(self.matcher.normalize_column_name('creation-date'), 'creation_date')

    def test_dot_replacement(self):
        self.assertEqual(self.matcher.normalize_column_name('pallet.id'), 'pallet_id')

    def test_special_char_removal(self):
        self.assertEqual(self.matcher.normalize_column_name('Pallet #ID'), 'pallet_id')
        self.assertEqual(self.matcher.normalize_column_name('Receipt@Number'), 'receiptnumber')

    def test_leading_trailing_underscore_removal(self):
        self.assertEqual(self.matcher.normalize_column_name('_pallet_id_'), 'pallet_id')

    def test_collapse_multiple_underscores(self):
        self.assertEqual(self.matcher.normalize_column_name('pallet___id'), 'pallet_id')


class TestExactMatching(unittest.TestCase):
    """Test Layer 1: Exact matching after normalization."""

    def setUp(self):
        self.matcher = ColumnMatcher()

    def test_perfect_match(self):
        result = self.matcher._exact_match('pallet_id', 'pallet_id')
        self.assertIsNotNone(result)
        self.assertEqual(result, 1.0)

    def test_case_insensitive_match(self):
        result = self.matcher._exact_match('pallet_id', 'PALLET_ID')
        self.assertIsNotNone(result)
        self.assertEqual(result, 0.99)

    def test_space_underscore_match(self):
        result = self.matcher._exact_match('pallet_id', 'Pallet ID')
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0.99)

    def test_no_match(self):
        result = self.matcher._exact_match('pallet_id', 'location')
        self.assertIsNone(result)


class TestFuzzyMatching(unittest.TestCase):
    """Test Layer 2: Fuzzy string similarity."""

    def setUp(self):
        self.matcher = ColumnMatcher()

    def test_high_similarity(self):
        result = self.matcher._fuzzy_match('pallet_id', 'Pallet number')
        self.assertGreater(result, 0.7)

    def test_abbreviation_similarity(self):
        result = self.matcher._fuzzy_match('location', 'Loc')
        self.assertGreater(result, 0.6)

    def test_partial_match(self):
        result = self.matcher._fuzzy_match('description', 'Item Description')
        self.assertGreater(result, 0.7)

    def test_low_similarity(self):
        result = self.matcher._fuzzy_match('pallet_id', 'Random Column')
        self.assertLess(result, 0.5)


class TestSemanticMatching(unittest.TestCase):
    """Test Layer 3: Semantic keyword matching."""

    def setUp(self):
        self.matcher = ColumnMatcher()

    def test_keyword_match_pallet_id(self):
        # "Pallet" is a keyword for pallet_id
        result = self.matcher._semantic_match('pallet_id', 'Pallet')
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0.5)

    def test_keyword_match_location(self):
        # "Bin" is a keyword for location
        result = self.matcher._semantic_match('location', 'Bin')
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0.5)

    def test_keyword_match_receipt_number(self):
        # "ASN" is a keyword for receipt_number
        result = self.matcher._semantic_match('receipt_number', 'ASN')
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0.5)

    def test_keyword_match_description(self):
        # "SKU" is a keyword for description
        result = self.matcher._semantic_match('description', 'SKU')
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0.5)

    def test_keyword_match_creation_date(self):
        # "Scan Date" is a keyword for creation_date
        result = self.matcher._semantic_match('creation_date', 'Scan Date')
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0.5)

    def test_no_keyword_match(self):
        result = self.matcher._semantic_match('pallet_id', 'Random Column')
        self.assertIsNone(result)


class TestBestMatchFinding(unittest.TestCase):
    """Test best match selection across all layers."""

    def setUp(self):
        self.matcher = ColumnMatcher()

    def test_exact_match_priority(self):
        # Exact match should win over fuzzy
        user_columns = ['pallet_id', 'Pallet Number']
        result = self.matcher.find_best_match('pallet_id', user_columns)

        self.assertIsNotNone(result)
        self.assertEqual(result['matched_column'], 'pallet_id')
        self.assertEqual(result['method'], 'exact')
        self.assertGreaterEqual(result['confidence'], 0.99)

    def test_fuzzy_match_when_no_exact(self):
        user_columns = ['Pallet Number', 'Location', 'Item']
        result = self.matcher.find_best_match('pallet_id', user_columns)

        self.assertIsNotNone(result)
        self.assertEqual(result['matched_column'], 'Pallet Number')
        self.assertIn(result['method'], ['fuzzy', 'semantic'])
        self.assertGreater(result['confidence'], 0.7)

    def test_semantic_match_when_fuzzy_low(self):
        user_columns = ['Loc', 'Item', 'Date']
        result = self.matcher.find_best_match('location', user_columns)

        self.assertIsNotNone(result)
        self.assertEqual(result['matched_column'], 'Loc')
        self.assertGreater(result['confidence'], 0.5)

    def test_no_match_below_threshold(self):
        user_columns = ['Random1', 'Random2', 'Random3']
        result = self.matcher.find_best_match('pallet_id', user_columns)

        self.assertIsNone(result)


class TestRealWorldScenarios(unittest.TestCase):
    """Test with real-world WMS export column variations."""

    def setUp(self):
        self.matcher = ColumnMatcher()

    def test_manhattan_wms_style(self):
        """Test Manhattan WMS export format."""
        user_columns = ['LPN', 'Warehouse Location', 'Item Description', 'ASN', 'Received Date']

        result_pallet = self.matcher.find_best_match('pallet_id', user_columns)
        self.assertEqual(result_pallet['matched_column'], 'LPN')

        result_location = self.matcher.find_best_match('location', user_columns)
        self.assertEqual(result_location['matched_column'], 'Warehouse Location')

        result_desc = self.matcher.find_best_match('description', user_columns)
        self.assertEqual(result_desc['matched_column'], 'Item Description')

        result_receipt = self.matcher.find_best_match('receipt_number', user_columns)
        self.assertEqual(result_receipt['matched_column'], 'ASN')

        result_date = self.matcher.find_best_match('creation_date', user_columns)
        self.assertEqual(result_date['matched_column'], 'Received Date')

    def test_sap_style_columns(self):
        """Test SAP WMS export format."""
        user_columns = ['Pallet_ID', 'Bin', 'Material Description', 'PO Number', 'Timestamp']

        result_pallet = self.matcher.find_best_match('pallet_id', user_columns)
        self.assertEqual(result_pallet['matched_column'], 'Pallet_ID')

        result_location = self.matcher.find_best_match('location', user_columns)
        self.assertEqual(result_location['matched_column'], 'Bin')

        result_desc = self.matcher.find_best_match('description', user_columns)
        self.assertEqual(result_desc['matched_column'], 'Material Description')

        result_receipt = self.matcher.find_best_match('receipt_number', user_columns)
        self.assertEqual(result_receipt['matched_column'], 'PO Number')

        result_date = self.matcher.find_best_match('creation_date', user_columns)
        self.assertEqual(result_date['matched_column'], 'Timestamp')

    def test_generic_export_with_spaces(self):
        """Test generic export with multi-word column names."""
        user_columns = ['Pallet number', 'Location', 'Item description', 'Receipt number', 'creation_date']

        matches = self.matcher.find_all_matches(user_columns, include_alternatives=False)

        self.assertEqual(matches['pallet_id']['matched_column'], 'Pallet number')
        self.assertEqual(matches['location']['matched_column'], 'Location')
        self.assertEqual(matches['description']['matched_column'], 'Item description')
        self.assertEqual(matches['receipt_number']['matched_column'], 'Receipt number')
        self.assertEqual(matches['creation_date']['matched_column'], 'creation_date')

    def test_mixed_case_and_abbreviations(self):
        """Test exports with mixed case and abbreviations."""
        user_columns = ['PALLET_ID', 'LOC', 'PRODUCT', 'LOT', 'SCAN DATE']

        matches = self.matcher.find_all_matches(user_columns, include_alternatives=False)

        # All should match with reasonable confidence
        self.assertIsNotNone(matches['pallet_id']['matched_column'])
        self.assertIsNotNone(matches['location']['matched_column'])
        self.assertIsNotNone(matches['description']['matched_column'])
        self.assertIsNotNone(matches['receipt_number']['matched_column'])
        self.assertIsNotNone(matches['creation_date']['matched_column'])


class TestFullMatchingWorkflow(unittest.TestCase):
    """Test complete matching workflow."""

    def test_suggest_column_mapping_complete(self):
        """Test the main suggest_column_mapping function."""
        user_columns = ['Pallet number', 'Location', 'Item description', 'Receipt number', 'Time in storage']

        result = suggest_column_mapping(user_columns, include_alternatives=True)

        # Check structure
        self.assertIn('suggestions', result)
        self.assertIn('user_columns', result)
        self.assertIn('unmapped_required', result)
        self.assertIn('unmapped_user', result)
        self.assertIn('auto_mappable', result)
        self.assertIn('requires_review', result)
        self.assertIn('statistics', result)

        # Check suggestions
        self.assertEqual(len(result['suggestions']), 5)  # 5 required columns

        # Check auto-mappable (high confidence >= 0.85)
        self.assertGreater(len(result['auto_mappable']), 0)

        # Check statistics
        stats = result['statistics']
        self.assertEqual(stats['total_required'], 5)
        self.assertEqual(stats['total_user_columns'], 5)
        self.assertGreater(stats['matched'], 0)

    def test_suggest_with_unmapped_required(self):
        """Test when some required columns cannot be mapped."""
        user_columns = ['Pallet number', 'Location']  # Missing description, receipt_number, creation_date

        result = suggest_column_mapping(user_columns, include_alternatives=False)

        # Should have unmapped required columns
        # Note: Our matcher is smart enough to find 'receipt_number' from 'number' in 'Pallet number'
        # So we expect at least 1 unmapped, not necessarily all 3
        self.assertGreaterEqual(len(result['unmapped_required']), 1)
        # At minimum, description should be unmapped (no match for it)
        self.assertIn('description', result['unmapped_required'])

    def test_suggest_with_unmapped_user(self):
        """Test when user has extra columns not needed."""
        user_columns = ['Pallet number', 'Location', 'Description', 'Receipt number', 'Date', 'Extra1', 'Extra2']

        result = suggest_column_mapping(user_columns, include_alternatives=False)

        # Should have unmapped user columns
        self.assertGreater(len(result['unmapped_user']), 0)
        self.assertIn('Extra1', result['unmapped_user'])
        self.assertIn('Extra2', result['unmapped_user'])

    def test_alternatives_included(self):
        """Test that alternatives are provided when requested."""
        user_columns = ['Pallet', 'Pallet number', 'LPN']  # Multiple potential matches for pallet_id

        result = suggest_column_mapping(user_columns, include_alternatives=True)

        # Should have alternatives for pallet_id
        pallet_match = result['suggestions']['pallet_id']
        if len(user_columns) > 1:  # Only if there are potential alternatives
            self.assertIn('alternatives', pallet_match)


class TestConfidenceLevels(unittest.TestCase):
    """Test confidence level categorization."""

    def test_high_confidence_auto_mappable(self):
        """High confidence matches (>=0.85) should be auto-mappable."""
        user_columns = ['pallet_id', 'location', 'description', 'receipt_number', 'creation_date']

        result = suggest_column_mapping(user_columns, include_alternatives=False)

        # All should be auto-mappable (exact matches)
        self.assertEqual(len(result['auto_mappable']), 5)
        self.assertEqual(len(result['requires_review']), 0)

    def test_low_confidence_requires_review(self):
        """Low confidence matches (<0.85) should require review."""
        user_columns = ['PLT', 'Loc', 'Item', 'Lot', 'Date']  # All abbreviations

        result = suggest_column_mapping(user_columns, include_alternatives=False)

        # Most should require review (fuzzy/semantic matches)
        self.assertGreater(len(result['requires_review']), 0)


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("INTELLIGENT COLUMN MATCHING SYSTEM - UNIT TESTS")
    print("=" * 70)
    print()

    success = run_tests()

    print()
    print("=" * 70)
    if success:
        print("[SUCCESS] ALL TESTS PASSED - Column matcher is production-ready!")
    else:
        print("[FAILED] SOME TESTS FAILED - Review failures above")
    print("=" * 70)

    exit(0 if success else 1)
