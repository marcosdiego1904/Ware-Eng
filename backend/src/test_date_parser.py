"""
Unit Tests for Smart Date Parser

Tests the DateFormatDetector, SmartDateParser, and DateQualityValidator classes
to ensure correct detection and parsing of various date formats.

Run with: python test_date_parser.py
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from date_parser import DateFormatDetector, SmartDateParser, DateQualityValidator, ParseResult


class TestDateFormatDetector(unittest.TestCase):
    """Test date format detection"""

    def test_detect_excel_serial(self):
        """Test Excel serial number detection"""
        dates = pd.Series([45666.6111, 45667.2500, 45668.0000])  # Jan 9-11, 2025
        detector = DateFormatDetector()
        result = detector.detect_format(dates)

        self.assertEqual(result['format_type'], detector.EXCEL_SERIAL)
        self.assertGreater(result['confidence'], 0.95)
        self.assertEqual(result['parsing_strategy'], 'excel')

    def test_detect_iso_format(self):
        """Test ISO format detection"""
        dates = pd.Series(['2025-01-09 14:40:03', '2025-01-10 15:30:00', '2025-01-11 16:20:00'])
        detector = DateFormatDetector()
        result = detector.detect_format(dates)

        self.assertEqual(result['format_type'], detector.ISO_FORMAT)
        self.assertEqual(result['confidence'], 1.0)
        self.assertEqual(result['parsing_strategy'], 'iso')

    def test_detect_unix_timestamp(self):
        """Test Unix timestamp detection"""
        dates = pd.Series(['20250109144003', '20250110153000', '20250111162000'])
        detector = DateFormatDetector()
        result = detector.detect_format(dates)

        self.assertEqual(result['format_type'], detector.UNIX_TIMESTAMP)
        self.assertGreater(result['confidence'], 0.95)
        self.assertEqual(result['parsing_strategy'], 'unix')

    def test_detect_us_slash_format(self):
        """Test US slash format detection"""
        # Use dates where second part > 12 to prove US format (month/day, so day > 12)
        dates = pd.Series(['1/13/2025', '2/15/2025', '3/20/2025'])  # 13, 15, 20 in day position prove US
        detector = DateFormatDetector()
        result = detector.detect_format(dates)

        self.assertEqual(result['format_type'], detector.US_SLASH)
        self.assertEqual(result.get('format_hint'), 'US')
        self.assertEqual(result['parsing_strategy'], 'slash')

    def test_detect_eu_slash_format(self):
        """Test EU slash format detection"""
        # Use dates where first part > 12 to prove EU format (day first)
        dates = pd.Series(['09/01/2025', '15/02/2025', '20/03/2025'])  # 15, 20 prove EU
        detector = DateFormatDetector()
        result = detector.detect_format(dates)

        self.assertEqual(result['format_type'], detector.EU_SLASH)
        self.assertEqual(result.get('format_hint'), 'EU')

    def test_detect_mixed_formats(self):
        """Test mixed format detection"""
        dates = pd.Series(['2025-01-09', '1/10/2025', 'Jan 11, 2025'])
        detector = DateFormatDetector()
        result = detector.detect_format(dates)

        self.assertEqual(result['format_type'], detector.MIXED)
        self.assertLess(result['confidence'], 0.8)

    def test_detect_empty_series(self):
        """Test detection with empty series"""
        dates = pd.Series([], dtype=object)
        detector = DateFormatDetector()
        result = detector.detect_format(dates)

        self.assertEqual(result['format_type'], detector.UNKNOWN)
        self.assertEqual(result['confidence'], 0.0)

    def test_detect_all_null_series(self):
        """Test detection with all null values"""
        dates = pd.Series([None, None, None])
        detector = DateFormatDetector()
        result = detector.detect_format(dates)

        self.assertEqual(result['format_type'], detector.UNKNOWN)
        self.assertEqual(result['confidence'], 0.0)


class TestSmartDateParser(unittest.TestCase):
    """Test date parsing strategies"""

    def test_parse_excel_serial(self):
        """Test Excel serial number parsing"""
        # Excel serial for January 9, 2025
        dates = pd.Series([45666.6111, 45667.0, 45668.5])  # Jan 9-11, 2025
        parser = SmartDateParser()
        result = parser._parse_excel_serial(dates)

        self.assertEqual(result.success_rate, 1.0)
        self.assertIsInstance(result, ParseResult)

        # Check first date
        parsed_date = result.parsed_series.iloc[0]
        self.assertEqual(parsed_date.year, 2025)
        self.assertEqual(parsed_date.month, 1)
        self.assertEqual(parsed_date.day, 9)

    def test_parse_unix_timestamp(self):
        """Test Unix timestamp parsing"""
        dates = pd.Series(['20250109144003', '20250110153000'])
        parser = SmartDateParser()
        result = parser._parse_unix_timestamp(dates)

        self.assertEqual(result.success_rate, 1.0)
        self.assertEqual(result.parsed_series.iloc[0], datetime(2025, 1, 9, 14, 40, 3))
        self.assertEqual(result.parsed_series.iloc[1], datetime(2025, 1, 10, 15, 30, 0))

    def test_parse_iso_format(self):
        """Test ISO format parsing"""
        dates = pd.Series(['2025-01-09 14:40:03', '2025-01-10 15:30:00'])
        parser = SmartDateParser()
        result = parser._parse_iso_format(dates)

        self.assertEqual(result.success_rate, 1.0)
        self.assertEqual(result.method, 'iso_format')

    def test_parse_slash_format_us(self):
        """Test US slash format parsing"""
        dates = pd.Series(['1/9/2025', '2/10/2025'])
        parser = SmartDateParser()
        result = parser._parse_slash_format(dates, format_hint='US')

        self.assertEqual(result.success_rate, 1.0)
        # Verify month comes first (US format)
        self.assertEqual(result.parsed_series.iloc[0].month, 1)
        self.assertEqual(result.parsed_series.iloc[0].day, 9)

    def test_parse_slash_format_eu(self):
        """Test EU slash format parsing"""
        dates = pd.Series(['09/01/2025', '10/02/2025'])
        parser = SmartDateParser()
        result = parser._parse_slash_format(dates, format_hint='EU')

        self.assertEqual(result.success_rate, 1.0)
        # Verify day comes first (EU format)
        self.assertEqual(result.parsed_series.iloc[0].day, 9)
        self.assertEqual(result.parsed_series.iloc[0].month, 1)

    def test_parse_with_dateutil_fallback(self):
        """Test dateutil flexible parsing"""
        dates = pd.Series(['Jan 9, 2025', '9-Jan-2025', 'January 9, 2025'])
        parser = SmartDateParser()
        result = parser._parse_with_dateutil(dates)

        self.assertGreater(result.success_rate, 0.9)
        self.assertEqual(result.method, 'dateutil_flexible')

    def test_parse_with_nulls(self):
        """Test parsing with null values"""
        dates = pd.Series([45666.0, None, 45668.0])  # Jan 9, 11, 2025
        parser = SmartDateParser()
        result = parser._parse_excel_serial(dates)

        # Should parse 2 out of 3
        non_null_original = dates.notna().sum()
        non_null_parsed = result.parsed_series.notna().sum()
        self.assertEqual(non_null_original, non_null_parsed)

    def test_parse_invalid_excel_serial(self):
        """Test parsing with invalid Excel serial numbers"""
        dates = pd.Series([0, -1, 999999])  # Out of reasonable range
        parser = SmartDateParser()
        result = parser._parse_excel_serial(dates)

        # These should fail to parse
        self.assertLess(result.success_rate, 1.0)

    def test_parse_invalid_unix_timestamp(self):
        """Test parsing with invalid Unix timestamps"""
        dates = pd.Series(['12345', '99999999999999', 'not_a_date'])
        parser = SmartDateParser()
        result = parser._parse_unix_timestamp(dates)

        # These should all fail
        self.assertEqual(result.success_rate, 0.0)

    def test_end_to_end_parsing(self):
        """Test complete parsing workflow"""
        dates = pd.Series([45666.6111, 45667.0, 45668.5])  # Jan 9-11, 2025
        parser = SmartDateParser()

        # Auto-detect and parse
        result = parser.parse_dates(dates)

        self.assertEqual(result.success_rate, 1.0)
        self.assertEqual(len(result.parsed_series), 3)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result.parsed_series))


class TestDateQualityValidator(unittest.TestCase):
    """Test date quality validation"""

    def test_validate_good_dates(self):
        """Test validation of clean dates"""
        original = pd.Series(['2025-01-09', '2025-01-10', '2025-01-11'])
        parsed = pd.to_datetime(original)

        validator = DateQualityValidator()
        result = validator.validate(original, parsed)

        self.assertEqual(result['parse_success_rate'], 1.0)
        self.assertGreater(result['quality_score'], 0.9)
        self.assertEqual(len(result['warnings']), 0)

    def test_detect_future_dates(self):
        """Test detection of future dates"""
        future_date = pd.Timestamp.now() + timedelta(days=365)
        dates = pd.Series([future_date, future_date])

        validator = DateQualityValidator()
        result = validator.validate(dates, dates)

        self.assertEqual(result['future_dates_count'], 2)
        self.assertGreater(len(result['warnings']), 0)
        self.assertTrue(any('future' in w.lower() for w in result['warnings']))

    def test_detect_ancient_dates(self):
        """Test detection of ancient dates"""
        ancient_date = pd.Timestamp(datetime(1800, 1, 1))
        dates = pd.Series([ancient_date, ancient_date])

        validator = DateQualityValidator()
        result = validator.validate(dates, dates)

        self.assertEqual(result['ancient_dates_count'], 2)
        self.assertGreater(len(result['warnings']), 0)
        self.assertTrue(any('1900' in w for w in result['warnings']))

    def test_detect_parsing_failures(self):
        """Test detection of parsing failures"""
        original = pd.Series(['2025-01-09', '2025-01-10', 'invalid'])
        parsed = pd.to_datetime(original, errors='coerce')

        validator = DateQualityValidator()
        result = validator.validate(original, parsed)

        # Should have < 100% parse success
        self.assertLess(result['parse_success_rate'], 1.0)
        self.assertAlmostEqual(result['parse_success_rate'], 2/3, places=2)

    def test_detect_outliers(self):
        """Test detection of statistical outliers"""
        # Create dates clustered around Jan 2025, with one outlier in 2020
        dates = pd.Series([
            pd.Timestamp('2025-01-09'),
            pd.Timestamp('2025-01-10'),
            pd.Timestamp('2025-01-11'),
            pd.Timestamp('2025-01-12'),
            pd.Timestamp('2025-01-13'),
            pd.Timestamp('2025-01-14'),
            pd.Timestamp('2025-01-15'),
            pd.Timestamp('2025-01-16'),
            pd.Timestamp('2025-01-17'),
            pd.Timestamp('2025-01-18'),
            pd.Timestamp('2025-01-19'),
            pd.Timestamp('2020-01-01'),  # Outlier: 5 years earlier
        ])

        validator = DateQualityValidator()
        result = validator.validate(dates, dates)

        # Should detect the 2020 date as an outlier
        self.assertGreater(len(result['outliers']), 0)
        self.assertTrue(any('outlier' in w.lower() for w in result['warnings']))

    def test_quality_score_calculation(self):
        """Test quality score calculation"""
        # Perfect dates
        perfect_dates = pd.Series([pd.Timestamp('2025-01-09')] * 10)
        validator = DateQualityValidator()
        result = validator.validate(perfect_dates, perfect_dates)
        self.assertGreater(result['quality_score'], 0.95)

        # Dates with issues (future dates)
        future_dates = pd.Series([pd.Timestamp.now() + timedelta(days=i*30) for i in range(10)])
        result_future = validator.validate(future_dates, future_dates)
        self.assertLess(result_future['quality_score'], result['quality_score'])

    def test_empty_dates(self):
        """Test validation with no valid dates"""
        dates = pd.Series([pd.NaT, pd.NaT, pd.NaT])
        validator = DateQualityValidator()
        result = validator.validate(dates, dates)

        self.assertEqual(result['parse_success_rate'], 0.0)
        self.assertEqual(result['date_range'], (None, None))
        self.assertIn('No valid dates', ' '.join(result['warnings']))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_single_date(self):
        """Test parsing with single date"""
        dates = pd.Series([45666.6111])  # Jan 9, 2025
        parser = SmartDateParser()
        result = parser.parse_dates(dates)

        self.assertEqual(result.success_rate, 1.0)
        self.assertEqual(len(result.parsed_series), 1)

    def test_large_dataset(self):
        """Test parsing with large dataset (performance)"""
        # Generate 1000 Excel serial dates
        base_serial = 45666  # Jan 9, 2025
        dates = pd.Series([base_serial + i * 0.1 for i in range(1000)])

        parser = SmartDateParser()
        result = parser.parse_dates(dates)

        self.assertEqual(result.success_rate, 1.0)
        self.assertEqual(len(result.parsed_series), 1000)

    def test_mixed_valid_invalid(self):
        """Test parsing with mix of valid and invalid dates"""
        dates = pd.Series([45666.0, 'invalid', 45668.0, None, 45669.0])  # Jan 9, 11, 12, 2025
        parser = SmartDateParser()
        result = parser.parse_dates(dates)

        # Should successfully parse the 3 valid Excel serials
        self.assertGreater(result.success_rate, 0.5)

    def test_date_range_boundaries(self):
        """Test dates at reasonable boundaries"""
        # Test year 1900 and 2100
        dates = pd.Series([2.0, 73051.0])  # Jan 1, 1900 and Jan 1, 2100
        parser = SmartDateParser()
        result = parser._parse_excel_serial(dates)

        # Both should parse
        self.assertEqual(result.success_rate, 1.0)


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDateFormatDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestSmartDateParser))
    suite.addTests(loader.loadTestsFromTestCase(TestDateQualityValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
