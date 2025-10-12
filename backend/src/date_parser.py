"""
Smart Date Parser for Warehouse Intelligence Engine

Purpose: Intelligent date format detection and parsing with multiple strategies
to handle real-world date variations (Excel serial, Unix timestamps, EU/US formats, etc.)

Architecture:
- Layer 1: Detection (analyze column and identify format pattern)
- Layer 2: Parsing (apply appropriate parsing strategy)
- Layer 3: Validation (quality checks and outlier detection)
- Layer 4: User Feedback (confidence scoring and warnings)

Similar to column_matcher.py but for date formats instead of column names.
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ParseResult:
    """Result of date parsing operation"""
    parsed_series: pd.Series
    success_rate: float
    failed_indices: List[int]
    confidence: float
    method: str = 'unknown'


class DateFormatDetector:
    """
    Detects date format from a pandas Series of date-like values

    Supported Formats:
    - EXCEL_SERIAL: 44935.6111 (days since 1900-01-01)
    - ISO_FORMAT: 2025-01-09 14:40:03
    - US_SLASH: 1/9/2025 2:40 PM (MM/DD/YYYY)
    - EU_SLASH: 09/01/2025 14:40 (DD/MM/YYYY)
    - UNIX_TIMESTAMP: 20250109144003 (YYYYMMDDHHMMSS)
    - HUMAN_READABLE: Jan 9, 2025
    - MIXED: Multiple formats in same column
    """

    # Format type constants
    EXCEL_SERIAL = 'EXCEL_SERIAL'
    ISO_FORMAT = 'ISO_FORMAT'
    US_SLASH = 'US_SLASH'
    EU_SLASH = 'EU_SLASH'
    UNIX_TIMESTAMP = 'UNIX_TIMESTAMP'
    HUMAN_READABLE = 'HUMAN_READABLE'
    MIXED = 'MIXED'
    UNKNOWN = 'UNKNOWN'

    def detect_format(self, date_series: pd.Series, sample_size: int = 100) -> Dict[str, Any]:
        """
        Analyze date column and detect format

        Args:
            date_series: pandas Series of date-like values
            sample_size: Number of non-null values to sample for detection

        Returns:
            Dictionary with format information:
            {
                'format_type': str,
                'confidence': float (0.0-1.0),
                'sample_values': List[str],
                'parsing_strategy': str,
                'unparseable_count': int,
                'total_count': int,
                'format_hint': Optional[str]  # 'US' or 'EU' for slash formats
            }
        """
        # Filter out null values
        non_null_series = date_series.dropna()
        total_count = len(date_series)
        non_null_count = len(non_null_series)

        if non_null_count == 0:
            return {
                'format_type': self.UNKNOWN,
                'confidence': 0.0,
                'sample_values': [],
                'parsing_strategy': 'none',
                'unparseable_count': total_count,
                'total_count': total_count,
                'format_hint': None
            }

        # Sample for performance (max 100 values)
        sample = non_null_series.sample(min(sample_size, non_null_count), random_state=42)

        # Count format matches
        format_counts = {
            self.EXCEL_SERIAL: 0,
            self.ISO_FORMAT: 0,
            self.US_SLASH: 0,
            self.EU_SLASH: 0,
            self.UNIX_TIMESTAMP: 0,
            self.HUMAN_READABLE: 0
        }

        for value in sample:
            if self._is_excel_serial(value):
                format_counts[self.EXCEL_SERIAL] += 1
            elif self._is_iso_format(value):
                format_counts[self.ISO_FORMAT] += 1
            elif self._is_unix_timestamp(value):
                format_counts[self.UNIX_TIMESTAMP] += 1
            elif self._is_slash_format(value):
                # Will disambiguate US vs EU later
                format_counts[self.US_SLASH] += 1
            else:
                # Might be human-readable format
                format_counts[self.HUMAN_READABLE] += 1

        # Determine dominant format
        total_matches = sum(format_counts.values())
        if total_matches == 0:
            dominant_format = self.UNKNOWN
            confidence = 0.0
        else:
            dominant_format = max(format_counts, key=format_counts.get)
            confidence = format_counts[dominant_format] / len(sample)

        # Store the dominant format before potential MIXED reclassification
        original_dominant_format = dominant_format

        # Check if mixed formats (no single format > 80%)
        if confidence < 0.8 and total_matches > 0:
            dominant_format = self.MIXED
            confidence = confidence * 0.7  # Penalty for mixed formats

        # Disambiguate US vs EU slash formats
        format_hint = None
        if dominant_format == self.US_SLASH or original_dominant_format == self.US_SLASH:
            format_hint = self._disambiguate_slash_format(sample)
            if format_hint == 'EU':
                dominant_format = self.EU_SLASH if dominant_format != self.MIXED else self.MIXED

        # Determine parsing strategy
        parsing_strategy = self._get_parsing_strategy(dominant_format)

        # Get sample values for display
        sample_values = [str(v) for v in sample.head(5).tolist()]

        return {
            'format_type': dominant_format,
            'confidence': confidence,
            'sample_values': sample_values,
            'parsing_strategy': parsing_strategy,
            'unparseable_count': total_count - non_null_count,  # Initial estimate
            'total_count': total_count,
            'format_hint': format_hint,
            'dominant_format': original_dominant_format  # NEW: Preserve original dominant format
        }

    def _is_excel_serial(self, value) -> bool:
        """Check if value is Excel serial number (40000-60000 range for 2010-2064)"""
        if pd.isna(value):
            return False
        try:
            num_val = float(value)
            # Excel serial numbers for reasonable date range (2009-2164)
            # 40000 = 2009-07-06, 60000 = 2064-04-15
            return 40000 <= num_val <= 60000
        except (ValueError, TypeError):
            return False

    def _is_unix_timestamp(self, value) -> bool:
        """Check if value matches YYYYMMDDHHMMSS pattern (14 digits)"""
        if pd.isna(value):
            return False
        str_val = str(value).strip()
        # Check for 14-digit pattern
        if not re.match(r'^\d{14}$', str_val):
            return False
        # Validate year range (1900-2100)
        try:
            year = int(str_val[0:4])
            return 1900 <= year <= 2100
        except ValueError:
            return False

    def _is_iso_format(self, value) -> bool:
        """Check if value matches ISO date format (YYYY-MM-DD)"""
        if pd.isna(value):
            return False
        str_val = str(value).strip()
        # YYYY-MM-DD or YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM:SS
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}', str_val))

    def _is_slash_format(self, value) -> bool:
        """Check if value contains slash dates (MM/DD/YYYY or DD/MM/YYYY)"""
        if pd.isna(value):
            return False
        str_val = str(value).strip()
        # Match \d{1,2}/\d{1,2}/\d{4} or \d{1,2}/\d{1,2}/\d{2}
        return bool(re.match(r'^\d{1,2}/\d{1,2}/\d{2,4}', str_val))

    def _disambiguate_slash_format(self, date_series: pd.Series) -> str:
        """
        Determine if slash format is US (MM/DD/YYYY) or EU (DD/MM/YYYY)

        Strategy:
        - If any first part > 12, it must be EU (day can be > 12, month cannot)
        - If all first parts <= 12, assume US (most common globally)
        - Check multiple samples for confidence
        """
        eu_indicators = 0
        us_indicators = 0

        for value in date_series:
            if not self._is_slash_format(value):
                continue

            str_val = str(value).strip()
            parts = str_val.split('/')
            if len(parts) < 2:
                continue

            try:
                first_part = int(parts[0])
                second_part = int(parts[1])

                # If first part > 12, must be day (EU format)
                if first_part > 12:
                    eu_indicators += 1
                # If second part > 12, must be day, so first part is month (US format)
                elif second_part > 12:
                    us_indicators += 1
                # Both <= 12, ambiguous
                else:
                    # Check if it looks more like US format (month first)
                    # This is a heuristic - if we have MM/DD where MM is small and DD is larger
                    if first_part <= 12 and second_part <= 31:
                        us_indicators += 0.5  # Slight preference for US
            except ValueError:
                continue

        # Determine format based on indicators
        if eu_indicators > 0:
            return 'EU'
        elif us_indicators > eu_indicators:
            return 'US'
        else:
            return 'US'  # Default to US format if ambiguous

    def _get_parsing_strategy(self, format_type: str) -> str:
        """Map format type to parsing strategy"""
        strategy_map = {
            self.EXCEL_SERIAL: 'excel',
            self.ISO_FORMAT: 'iso',
            self.US_SLASH: 'slash',
            self.EU_SLASH: 'slash',
            self.UNIX_TIMESTAMP: 'unix',
            self.HUMAN_READABLE: 'dateutil',
            self.MIXED: 'dateutil',
            self.UNKNOWN: 'dateutil'
        }
        return strategy_map.get(format_type, 'dateutil')


class SmartDateParser:
    """
    Intelligent date parser with multiple fallback strategies

    Strategies:
    1. Excel Serial: Convert serial numbers to datetime
    2. Unix Timestamp: Parse YYYYMMDDHHMMSS format
    3. ISO Format: Use explicit format string for performance
    4. Slash Format: Handle US/EU disambiguation
    5. Dateutil Fallback: Flexible parsing for human-readable formats
    """

    def __init__(self):
        self.detector = DateFormatDetector()

    def parse_dates(self, date_series: pd.Series, format_info: Optional[Dict] = None) -> ParseResult:
        """
        Main parsing function - intelligently parse dates based on detected format

        Args:
            date_series: pandas Series of date-like values
            format_info: Optional pre-detected format info (from DateFormatDetector)

        Returns:
            ParseResult object with parsed dates and metadata
        """
        # Auto-detect format if not provided
        if format_info is None:
            format_info = self.detector.detect_format(date_series)

        # Choose parsing strategy based on detected format
        strategy = format_info['parsing_strategy']
        format_type = format_info['format_type']

        # For MIXED formats, try dominant format first
        if format_type == 'MIXED' and 'dominant_format' in format_info:
            dominant_format = format_info['dominant_format']

            # Try parsing with dominant format first
            if dominant_format == 'EXCEL_SERIAL':
                result = self._parse_excel_serial(date_series)
                # If success rate is good enough (>50%), use it
                if result.success_rate > 0.5:
                    return result
            elif dominant_format == 'ISO_FORMAT':
                result = self._parse_iso_format(date_series)
                if result.success_rate > 0.5:
                    return result
            elif dominant_format == 'UNIX_TIMESTAMP':
                result = self._parse_unix_timestamp(date_series)
                if result.success_rate > 0.5:
                    return result
            elif dominant_format in ['US_SLASH', 'EU_SLASH']:
                format_hint = format_info.get('format_hint', 'US')
                result = self._parse_slash_format(date_series, format_hint)
                if result.success_rate > 0.5:
                    return result

            # If dominant format didn't work well, fall through to dateutil

        if strategy == 'excel':
            return self._parse_excel_serial(date_series)
        elif strategy == 'iso':
            return self._parse_iso_format(date_series)
        elif strategy == 'unix':
            return self._parse_unix_timestamp(date_series)
        elif strategy == 'slash':
            format_hint = format_info.get('format_hint', 'US')
            return self._parse_slash_format(date_series, format_hint)
        else:
            # Fallback to dateutil for flexible parsing
            return self._parse_with_dateutil(date_series)

    def _parse_excel_serial(self, date_series: pd.Series) -> ParseResult:
        """
        Convert Excel serial numbers to datetime

        Excel stores dates as serial numbers:
        - Windows Excel: Days since 1900-01-01 (with a leap year bug)
        - Mac Excel: Days since 1904-01-01

        Formula: datetime(1899, 12, 30) + timedelta(days=serial_number)
        Note: 1899-12-30 accounts for Excel's 1900 leap year bug
        """
        def convert_serial(value):
            if pd.isna(value):
                return pd.NaT
            try:
                serial = float(value)

                # Windows Excel epoch (most common)
                days = int(serial)
                fraction = serial - days

                # Excel epoch: 1899-12-30 (adjusts for 1900 leap year bug)
                base_date = datetime(1899, 12, 30)
                result = base_date + timedelta(days=days, seconds=fraction * 86400)

                # Sanity check: result should be between 1900 and 2200
                if result.year < 1900 or result.year > 2200:
                    return pd.NaT

                return result
            except (ValueError, TypeError, OverflowError):
                return pd.NaT

        parsed_series = date_series.apply(convert_serial)
        non_null_parsed = parsed_series.notna().sum()
        non_null_original = date_series.notna().sum()

        success_rate = non_null_parsed / non_null_original if non_null_original > 0 else 0.0
        failed_indices = parsed_series[parsed_series.isna() & date_series.notna()].index.tolist()

        return ParseResult(
            parsed_series=parsed_series,
            success_rate=success_rate,
            failed_indices=failed_indices,
            confidence=success_rate,
            method='excel_serial'
        )

    def _parse_unix_timestamp(self, date_series: pd.Series) -> ParseResult:
        """
        Parse YYYYMMDDHHMMSS format

        Example: 20250109144003 → 2025-01-09 14:40:03
        Common in ERP systems and database exports
        """
        def convert_unix(value):
            if pd.isna(value):
                return pd.NaT
            try:
                str_val = str(value).strip()
                if len(str_val) != 14:
                    return pd.NaT

                year = int(str_val[0:4])
                month = int(str_val[4:6])
                day = int(str_val[6:8])
                hour = int(str_val[8:10])
                minute = int(str_val[10:12])
                second = int(str_val[12:14])

                # Validate ranges
                if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
                    return pd.NaT
                if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                    return pd.NaT

                return datetime(year, month, day, hour, minute, second)
            except (ValueError, TypeError):
                return pd.NaT

        parsed_series = date_series.apply(convert_unix)
        non_null_parsed = parsed_series.notna().sum()
        non_null_original = date_series.notna().sum()

        success_rate = non_null_parsed / non_null_original if non_null_original > 0 else 0.0
        failed_indices = parsed_series[parsed_series.isna() & date_series.notna()].index.tolist()

        return ParseResult(
            parsed_series=parsed_series,
            success_rate=success_rate,
            failed_indices=failed_indices,
            confidence=success_rate,
            method='unix_timestamp'
        )

    def _parse_iso_format(self, date_series: pd.Series) -> ParseResult:
        """
        Parse ISO format dates (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)

        Uses pandas to_datetime with error handling
        """
        try:
            # Try with explicit format first (faster)
            parsed_series = pd.to_datetime(date_series, format='%Y-%m-%d', errors='coerce')

            # If that fails for some, try without format (handles time component)
            if parsed_series.isna().sum() > date_series.isna().sum():
                parsed_series = pd.to_datetime(date_series, errors='coerce')
        except Exception:
            parsed_series = pd.to_datetime(date_series, errors='coerce')

        non_null_parsed = parsed_series.notna().sum()
        non_null_original = date_series.notna().sum()

        success_rate = non_null_parsed / non_null_original if non_null_original > 0 else 0.0
        failed_indices = parsed_series[parsed_series.isna() & date_series.notna()].index.tolist()

        return ParseResult(
            parsed_series=parsed_series,
            success_rate=success_rate,
            failed_indices=failed_indices,
            confidence=success_rate,
            method='iso_format'
        )

    def _parse_slash_format(self, date_series: pd.Series, format_hint: str = 'US') -> ParseResult:
        """
        Parse slash dates with US/EU disambiguation

        US Format: MM/DD/YYYY (e.g., 1/9/2025 = January 9, 2025)
        EU Format: DD/MM/YYYY (e.g., 9/1/2025 = January 9, 2025)
        """
        if format_hint == 'EU':
            # Try EU format first (day/month/year)
            date_formats = ['%d/%m/%Y', '%d/%m/%y', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M']
        else:
            # Try US format first (month/day/year)
            date_formats = ['%m/%d/%Y', '%m/%d/%y', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M']

        parsed_series = None
        best_success_rate = 0.0

        # Try each format and use the one with best success rate
        for date_format in date_formats:
            try:
                temp_parsed = pd.to_datetime(date_series, format=date_format, errors='coerce')
                temp_success_rate = temp_parsed.notna().sum() / date_series.notna().sum() if date_series.notna().sum() > 0 else 0

                if temp_success_rate > best_success_rate:
                    best_success_rate = temp_success_rate
                    parsed_series = temp_parsed
            except Exception:
                continue

        # If no format worked, fallback to infer_datetime_format
        if parsed_series is None or best_success_rate < 0.5:
            try:
                parsed_series = pd.to_datetime(date_series, infer_datetime_format=True, errors='coerce')
                best_success_rate = parsed_series.notna().sum() / date_series.notna().sum() if date_series.notna().sum() > 0 else 0
            except Exception:
                parsed_series = pd.Series([pd.NaT] * len(date_series), index=date_series.index)
                best_success_rate = 0.0

        failed_indices = parsed_series[parsed_series.isna() & date_series.notna()].index.tolist()

        # Slight confidence penalty for ambiguous slash formats
        confidence = best_success_rate * 0.9

        return ParseResult(
            parsed_series=parsed_series,
            success_rate=best_success_rate,
            failed_indices=failed_indices,
            confidence=confidence,
            method=f'slash_{format_hint.lower()}'
        )

    def _parse_with_dateutil(self, date_series: pd.Series) -> ParseResult:
        """
        Fallback: Use dateutil.parser for flexible parsing

        Handles human-readable formats:
        - "Jan 9, 2025"
        - "9-Jan-2025"
        - "January 9, 2025"
        - Mixed formats
        """
        try:
            from dateutil import parser as dateutil_parser

            def parse_flexible(value):
                if pd.isna(value):
                    return pd.NaT
                try:
                    # dateutil.parser.parse is very flexible
                    return dateutil_parser.parse(str(value))
                except (ValueError, TypeError, dateutil_parser.ParserError):
                    return pd.NaT

            parsed_series = date_series.apply(parse_flexible)
        except ImportError:
            # Fallback if dateutil not available - use pandas basic parsing
            print("[DATE_PARSER] Warning: python-dateutil not available, using pandas fallback")
            parsed_series = pd.to_datetime(date_series, errors='coerce')

        non_null_parsed = parsed_series.notna().sum()
        non_null_original = date_series.notna().sum()

        success_rate = non_null_parsed / non_null_original if non_null_original > 0 else 0.0
        failed_indices = parsed_series[parsed_series.isna() & date_series.notna()].index.tolist()

        # Lower confidence for flexible parsing (less predictable)
        confidence = success_rate * 0.85

        return ParseResult(
            parsed_series=parsed_series,
            success_rate=success_rate,
            failed_indices=failed_indices,
            confidence=confidence,
            method='dateutil_flexible'
        )


class DateQualityValidator:
    """
    Validates parsed dates and identifies quality issues

    Checks:
    - Parse success rate
    - Date range (min/max)
    - Future dates (dates after today)
    - Ancient dates (dates before 1900)
    - Statistical outliers (dates > 2 std deviations from mean)
    """

    def validate(self, original_series: pd.Series, parsed_series: pd.Series) -> Dict[str, Any]:
        """
        Validate parsed dates for quality issues

        Args:
            original_series: Original unparsed date values
            parsed_series: Parsed datetime values

        Returns:
            Dictionary with validation results:
            {
                'parse_success_rate': float,
                'date_range': tuple (min_date, max_date),
                'outliers': List[int],  # Indices of outlier dates
                'future_dates_count': int,
                'ancient_dates_count': int,
                'quality_score': float (0.0-1.0),
                'warnings': List[str]
            }
        """
        warnings = []

        # Calculate parse success rate
        non_null_original = original_series.notna().sum()
        non_null_parsed = parsed_series.notna().sum()
        parse_success_rate = non_null_parsed / non_null_original if non_null_original > 0 else 0.0

        # Get date range
        valid_dates = parsed_series.dropna()
        if len(valid_dates) > 0:
            min_date = valid_dates.min()
            max_date = valid_dates.max()
            date_range = (min_date, max_date)
        else:
            date_range = (None, None)
            warnings.append("No valid dates found after parsing")

        # Check for future dates
        now = pd.Timestamp.now()
        future_dates = parsed_series[parsed_series > now]
        future_dates_count = len(future_dates)
        if future_dates_count > 0:
            warnings.append(f"{future_dates_count} dates are in the future")

        # Check for ancient dates (before 1900)
        ancient_threshold = pd.Timestamp(datetime(1900, 1, 1))
        ancient_dates = parsed_series[parsed_series < ancient_threshold]
        ancient_dates_count = len(ancient_dates)
        if ancient_dates_count > 0:
            warnings.append(f"{ancient_dates_count} dates are before 1900")

        # Detect statistical outliers
        outliers = []
        if len(valid_dates) > 10:  # Need enough data for meaningful statistics
            try:
                # Convert to Unix timestamps for statistical analysis
                timestamps = valid_dates.astype('int64') / 10**9  # Convert to seconds
                mean_ts = timestamps.mean()
                std_ts = timestamps.std()

                if std_ts > 0:  # Avoid division by zero
                    outlier_mask = np.abs(timestamps - mean_ts) > (2 * std_ts)
                    outliers = timestamps[outlier_mask].index.tolist()

                    if len(outliers) > 0:
                        warnings.append(f"{len(outliers)} dates are statistical outliers (>2 std dev from mean)")
            except Exception:
                # Silently skip outlier detection if it fails
                pass

        # Calculate overall quality score
        quality_score = 0.0

        # 70% weight on parse success
        quality_score += parse_success_rate * 0.7

        # 15% weight on reasonable future dates (< 5% future dates is OK)
        if non_null_parsed > 0:
            future_ratio = future_dates_count / non_null_parsed
            if future_ratio < 0.05:
                quality_score += 0.15
            elif future_ratio < 0.10:
                quality_score += 0.10
        else:
            quality_score += 0.15  # No dates to check

        # 15% weight on reasonable ancient dates (< 5% ancient dates is OK)
        if non_null_parsed > 0:
            ancient_ratio = ancient_dates_count / non_null_parsed
            if ancient_ratio < 0.05:
                quality_score += 0.15
            elif ancient_ratio < 0.10:
                quality_score += 0.10
        else:
            quality_score += 0.15  # No dates to check

        # Cap at 1.0
        quality_score = min(quality_score, 1.0)

        return {
            'parse_success_rate': parse_success_rate,
            'date_range': date_range,
            'outliers': outliers,
            'future_dates_count': future_dates_count,
            'ancient_dates_count': ancient_dates_count,
            'quality_score': quality_score,
            'warnings': warnings
        }


# Convenience function for quick parsing
def smart_parse_dates(date_series: pd.Series, return_metadata: bool = False):
    """
    Convenience function for quick date parsing

    Args:
        date_series: pandas Series of date-like values
        return_metadata: If True, return (parsed_series, format_info, parse_result, quality_info)
                        If False, return only parsed_series

    Returns:
        Parsed datetime Series, optionally with metadata
    """
    detector = DateFormatDetector()
    format_info = detector.detect_format(date_series)

    parser = SmartDateParser()
    parse_result = parser.parse_dates(date_series, format_info)

    if return_metadata:
        validator = DateQualityValidator()
        quality_info = validator.validate(date_series, parse_result.parsed_series)
        return parse_result.parsed_series, format_info, parse_result, quality_info
    else:
        return parse_result.parsed_series
