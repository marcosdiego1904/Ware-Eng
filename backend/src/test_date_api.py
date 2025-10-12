"""
Quick API Test for Date Parser

Tests the date detection logic directly without needing to upload files.
Validates that all date formats are correctly detected and parsed.

Run: python test_date_api.py
"""

import pandas as pd
from datetime import datetime, timedelta
from date_parser import DateFormatDetector, SmartDateParser, DateQualityValidator

def test_format(name, date_series, expected_format, expected_strategy):
    """Test a specific date format"""
    print(f"\n{'='*70}")
    print(f"Test: {name}")
    print('='*70)

    # Detect format
    detector = DateFormatDetector()
    format_info = detector.detect_format(date_series)

    # Parse dates
    parser = SmartDateParser()
    parse_result = parser.parse_dates(date_series, format_info)

    # Validate quality
    validator = DateQualityValidator()
    quality = validator.validate(date_series, parse_result.parsed_series)

    # Results
    print(f"Format Detected:     {format_info['format_type']}")
    print(f"Expected:            {expected_format}")
    print(f"Confidence:          {format_info['confidence']:.1%}")
    print(f"Parsing Strategy:    {format_info['parsing_strategy']}")
    print(f"Expected Strategy:   {expected_strategy}")
    print(f"Parse Success Rate:  {parse_result.success_rate:.1%}")
    print(f"Quality Score:       {quality['quality_score']:.1%}")
    print(f"Sample Values:       {format_info['sample_values'][:3]}")

    # Warnings
    if quality['warnings']:
        print(f"\nWarnings:")
        for warning in quality['warnings']:
            print(f"  WARNING: {warning}")

    # Validation
    success = True
    if format_info['format_type'] != expected_format:
        print(f"\nX FAILED: Format mismatch!")
        success = False
    elif format_info['parsing_strategy'] != expected_strategy:
        print(f"\nX FAILED: Strategy mismatch!")
        success = False
    elif parse_result.success_rate < 0.95:
        print(f"\nX FAILED: Low parse success rate!")
        success = False
    else:
        print(f"\n>> PASSED")

    return success

def main():
    print("="*70)
    print("DATE PARSER API TESTS")
    print("="*70)
    print("\nTesting all 6 date format types...\n")

    base_date = datetime(2025, 1, 9, 14, 40, 3)
    results = []

    # ========================================================================
    # Test 1: Excel Serial Numbers
    # ========================================================================
    excel_serials = []
    for i in range(20):
        date = base_date + timedelta(days=i, hours=i*2)
        delta = date - datetime(1899, 12, 30)
        serial = delta.days + (delta.seconds / 86400)
        excel_serials.append(serial)

    results.append(test_format(
        "Excel Serial Numbers",
        pd.Series(excel_serials),
        "EXCEL_SERIAL",
        "excel"
    ))

    # ========================================================================
    # Test 2: ISO Format
    # ========================================================================
    iso_dates = []
    for i in range(20):
        date = base_date + timedelta(days=i, hours=i*2)
        iso_dates.append(date.strftime('%Y-%m-%d %H:%M:%S'))

    results.append(test_format(
        "ISO Format (YYYY-MM-DD HH:MM:SS)",
        pd.Series(iso_dates),
        "ISO_FORMAT",
        "iso"
    ))

    # ========================================================================
    # Test 3: US Slash Format
    # ========================================================================
    us_dates = []
    for i in range(20):
        date = base_date + timedelta(days=i)
        us_dates.append(date.strftime('%m/%d/%Y'))

    results.append(test_format(
        "US Slash Format (MM/DD/YYYY)",
        pd.Series(us_dates),
        "US_SLASH",
        "slash"
    ))

    # ========================================================================
    # Test 4: EU Slash Format
    # ========================================================================
    eu_dates = []
    for i in range(20):
        date = base_date + timedelta(days=i)
        eu_dates.append(date.strftime('%d/%m/%Y'))

    results.append(test_format(
        "EU Slash Format (DD/MM/YYYY)",
        pd.Series(eu_dates),
        "EU_SLASH",
        "slash"
    ))

    # ========================================================================
    # Test 5: Unix Timestamp
    # ========================================================================
    unix_dates = []
    for i in range(20):
        date = base_date + timedelta(days=i, hours=i*2)
        unix_dates.append(date.strftime('%Y%m%d%H%M%S'))

    results.append(test_format(
        "Unix Timestamp (YYYYMMDDHHMMSS)",
        pd.Series(unix_dates),
        "UNIX_TIMESTAMP",
        "unix"
    ))

    # ========================================================================
    # Test 6: Mixed Formats
    # ========================================================================
    mixed_dates = []
    for i in range(20):
        date = base_date + timedelta(days=i)
        if i % 2 == 0:
            # Excel serial (dominant)
            delta = date - datetime(1899, 12, 30)
            mixed_dates.append(delta.days + (delta.seconds / 86400))
        else:
            # ISO format
            mixed_dates.append(date.strftime('%Y-%m-%d'))

    # For mixed formats, we expect MIXED detection but Excel parsing (dominant)
    print(f"\n{'='*70}")
    print(f"Test: Mixed Formats (50% Excel, 50% ISO)")
    print('='*70)

    detector = DateFormatDetector()
    format_info = detector.detect_format(pd.Series(mixed_dates))
    parser = SmartDateParser()
    parse_result = parser.parse_dates(pd.Series(mixed_dates), format_info)

    print(f"Format Detected:     {format_info['format_type']}")
    print(f"Dominant Format:     {format_info.get('dominant_format', 'N/A')}")
    print(f"Confidence:          {format_info['confidence']:.1%}")
    print(f"Parse Success Rate:  {parse_result.success_rate:.1%}")
    print(f"Parsing Method:      {parse_result.method}")
    print(f"Sample Values:       {format_info['sample_values'][:3]}")

    # Mixed should detect MIXED format and try dominant format first
    if format_info['format_type'] == 'MIXED' and parse_result.success_rate >= 0.5:
        print(f"\n>> PASSED (correctly handled mixed formats)")
        results.append(True)
    else:
        print(f"\nX FAILED (mixed format handling issue)")
        results.append(False)

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")

    if all(results):
        print("\n*** ALL TESTS PASSED! Date parser is working correctly. ***")
        print("\nNext step: Upload test Excel files to the frontend to see the UI")
        print("Run: python generate_date_test_files.py")
    else:
        print("\n*** Some tests failed. Review the output above for details. ***")

    print("="*70)

    return all(results)

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
