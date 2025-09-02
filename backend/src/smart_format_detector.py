"""
Smart Format Detector for Warehouse Location Formats

This module provides intelligent detection of location format patterns based on 
user-provided examples. It analyzes location patterns and generates format 
configurations that integrate seamlessly with the existing CanonicalLocationService.

Key Features:
- Pattern analysis from minimal examples (e.g., "010A", "325B", "245D")
- Automatic format detection with confidence scoring
- Integration with existing canonical location system
- Support for common warehouse location patterns
- Robust error handling and edge case management

Architecture:
1. SmartFormatDetector: Core pattern detection logic
2. FormatPattern: Data structure for detected patterns
3. PatternAnalyzer: Individual pattern analysis components
4. ConfidenceCalculator: Pattern confidence scoring
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, Counter
import json

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Supported location pattern types"""
    STANDARD = "standard"           # "01-01-001A" - already canonical
    POSITION_LEVEL = "position_level"  # "010A" - position + level
    COMPACT = "compact"            # "01A01A" - aisle + level + position + level
    SPECIAL = "special"            # "RECV-01", "STAGE-01" - special areas
    ZONE = "zone"                  # "ZONE-A-001", "AREA-B-125" - zone-based locations
    UNKNOWN = "unknown"            # Unparseable patterns


@dataclass
class FormatPattern:
    """
    Detected format pattern with metadata
    """
    pattern_type: PatternType
    regex_pattern: str
    canonical_converter: str
    confidence: float
    examples: List[str]
    components: Dict[str, any]
    description: str
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'pattern_type': self.pattern_type.value,
            'regex_pattern': self.regex_pattern,
            'canonical_converter': self.canonical_converter,
            'confidence': self.confidence,
            'examples': self.examples,
            'components': self.components,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'FormatPattern':
        """Create from dictionary"""
        return cls(
            pattern_type=PatternType(data['pattern_type']),
            regex_pattern=data['regex_pattern'],
            canonical_converter=data['canonical_converter'],
            confidence=data['confidence'],
            examples=data['examples'],
            components=data['components'],
            description=data['description']
        )


class PatternAnalyzer:
    """
    Base class for individual pattern analyzers
    """
    
    def __init__(self, pattern_type: PatternType):
        self.pattern_type = pattern_type
    
    def analyze(self, examples: List[str]) -> Optional[FormatPattern]:
        """
        Analyze examples for this specific pattern type
        
        Args:
            examples: List of location code examples
            
        Returns:
            FormatPattern if pattern matches, None otherwise
        """
        raise NotImplementedError
    
    def _calculate_confidence(self, examples: List[str], matched_examples: List[str]) -> float:
        """Calculate confidence based on match ratio and pattern consistency"""
        if not examples:
            return 0.0
        
        match_ratio = len(matched_examples) / len(examples)
        
        # Bonus for consistent patterns
        consistency_bonus = self._calculate_consistency_bonus(matched_examples)
        
        # Penalty for very few examples
        sample_size_factor = min(1.0, len(matched_examples) / 3.0)
        
        confidence = match_ratio * sample_size_factor * (1.0 + consistency_bonus)
        return min(1.0, confidence)
    
    def _calculate_consistency_bonus(self, examples: List[str]) -> float:
        """Calculate bonus for consistent patterns within examples"""
        if len(examples) < 2:
            return 0.0
        
        # Check for consistent length
        lengths = [len(ex) for ex in examples]
        length_consistency = len(set(lengths)) == 1
        
        # Check for consistent character patterns
        pattern_consistency = self._check_pattern_consistency(examples)
        
        bonus = 0.0
        if length_consistency:
            bonus += 0.1
        if pattern_consistency:
            bonus += 0.15
            
        return bonus
    
    def _check_pattern_consistency(self, examples: List[str]) -> bool:
        """Check if examples follow consistent character patterns"""
        if len(examples) < 2:
            return True
        
        # Create pattern signature for each example
        def get_pattern_signature(s: str) -> str:
            return ''.join('D' if c.isdigit() else 'A' if c.isalpha() else 'S' for c in s)
        
        signatures = [get_pattern_signature(ex) for ex in examples]
        return len(set(signatures)) == 1


class PositionLevelAnalyzer(PatternAnalyzer):
    """
    Analyzes position+level patterns like "010A", "325B", "245D"
    """
    
    def __init__(self):
        super().__init__(PatternType.POSITION_LEVEL)
    
    def analyze(self, examples: List[str]) -> Optional[FormatPattern]:
        """
        Detect position+level pattern: PPPX where PPP=position, X=level
        
        Examples: "010A", "325B", "245D" → "01-01-010A", "01-01-325B", "01-01-245D"
        """
        pattern = r'^(\d{3})([A-Z])$'
        matched_examples = []
        
        for example in examples:
            if re.match(pattern, example.strip().upper()):
                matched_examples.append(example.strip().upper())
        
        if not matched_examples:
            return None
        
        confidence = self._calculate_confidence(examples, matched_examples)
        
        # Ensure minimum confidence threshold
        if confidence < 0.5:
            return None
        
        return FormatPattern(
            pattern_type=self.pattern_type,
            regex_pattern=pattern,
            canonical_converter="01-01-{position:03d}{level}",
            confidence=confidence,
            examples=matched_examples[:5],  # Keep up to 5 examples
            components={
                'position_digits': 3,
                'level_format': 'single_letter',
                'default_aisle': 1,
                'default_rack': 1
            },
            description=f"Position+Level format (PPP+L) detected with {confidence:.1%} confidence"
        )


class StandardAnalyzer(PatternAnalyzer):
    """
    Analyzes standard canonical patterns like "01-01-001A"
    """
    
    def __init__(self):
        super().__init__(PatternType.STANDARD)
    
    def analyze(self, examples: List[str]) -> Optional[FormatPattern]:
        """
        Detect standard canonical pattern: AA-RR-PPPL
        """
        pattern = r'^(\d{1,2})-(\d{1,2})-(\d{1,3})([A-Z])$'
        matched_examples = []
        
        for example in examples:
            if re.match(pattern, example.strip().upper()):
                matched_examples.append(example.strip().upper())
        
        if not matched_examples:
            return None
        
        confidence = self._calculate_confidence(examples, matched_examples)
        
        if confidence < 0.7:  # Higher threshold for standard format
            return None
        
        return FormatPattern(
            pattern_type=self.pattern_type,
            regex_pattern=pattern,
            canonical_converter="{aisle:02d}-{rack:02d}-{position:03d}{level}",
            confidence=confidence,
            examples=matched_examples[:5],
            components={
                'aisle_digits': 2,
                'rack_digits': 2,
                'position_digits': 3,
                'level_format': 'single_letter',
                'separators': ['-', '-']
            },
            description=f"Standard canonical format (AA-RR-PPP+L) detected with {confidence:.1%} confidence"
        )


class LetterPrefixedAnalyzer(PatternAnalyzer):
    """
    Analyzes letter-prefixed patterns like "A01-R02-P15"
    """
    
    def __init__(self):
        super().__init__(PatternType.STANDARD)  # Use STANDARD type for letter-prefixed
    
    def analyze(self, examples: List[str]) -> Optional[FormatPattern]:
        """
        Detect letter-prefixed patterns: A01-R02-P15, B05-R01-P03, etc.
        """
        # Pattern for letter-prefixed segments with optional level
        patterns = [
            r'^([A-Z]\d{1,2})-([A-Z]\d{1,2})-([A-Z]\d{1,3})([A-Z])?$',  # With level: A01-R02-P15A
            r'^([A-Z]\d{1,2})-([A-Z]\d{1,2})-([A-Z]\d{1,3})$'            # Without level: A01-R02-P15
        ]
        
        best_matches = []
        best_pattern = None
        
        for pattern in patterns:
            matched_examples = []
            for example in examples:
                if re.match(pattern, example.strip().upper()):
                    matched_examples.append(example.strip().upper())
            
            if len(matched_examples) > len(best_matches):
                best_matches = matched_examples
                best_pattern = pattern
        
        if not best_matches:
            return None
        
        confidence = self._calculate_confidence(examples, best_matches)
        
        if confidence < 0.6:  # Slightly lower threshold for letter-prefixed
            return None
        
        # Determine if pattern has level suffix
        has_level = r'([A-Z])\)?\$$' in best_pattern
        
        return FormatPattern(
            pattern_type=self.pattern_type,
            regex_pattern=best_pattern,
            canonical_converter="{aisle_prefix}{aisle:02d}-{rack_prefix}{rack:02d}-{position_prefix}{position:02d}" + ("{level}" if has_level else ""),
            confidence=confidence,
            examples=best_matches[:5],
            components={
                'aisle_prefix': True,
                'rack_prefix': True,
                'position_prefix': True,
                'aisle_digits': 2,
                'rack_digits': 2,
                'position_digits': 2,
                'level_format': 'single_letter' if has_level else 'none',
                'separators': ['-', '-']
            },
            description=f"Letter-prefixed format (A##-R##-P##) detected with {confidence:.1%} confidence"
        )


class CompactAnalyzer(PatternAnalyzer):
    """
    Analyzes compact patterns like "01A01A"
    """
    
    def __init__(self):
        super().__init__(PatternType.COMPACT)
    
    def analyze(self, examples: List[str]) -> Optional[FormatPattern]:
        """
        Detect compact pattern: AALPPX where AA=aisle, L=level, PP=position, X=level
        """
        pattern = r'^(\d{1,2})([A-Z])(\d{1,2})([A-Z])$'
        matched_examples = []
        
        for example in examples:
            if re.match(pattern, example.strip().upper()):
                matched_examples.append(example.strip().upper())
        
        if not matched_examples:
            return None
        
        confidence = self._calculate_confidence(examples, matched_examples)
        
        if confidence < 0.6:
            return None
        
        return FormatPattern(
            pattern_type=self.pattern_type,
            regex_pattern=pattern,
            canonical_converter="{aisle:02d}-01-{position:03d}{level}",
            confidence=confidence,
            examples=matched_examples[:5],
            components={
                'aisle_digits': 2,
                'position_digits': 2,
                'level_format': 'single_letter',
                'default_rack': 1,
                'pattern_structure': 'aisle+level+position+level'
            },
            description=f"Compact format (AA+L+PP+L) detected with {confidence:.1%} confidence"
        )


class SpecialAnalyzer(PatternAnalyzer):
    """
    Analyzes special location patterns like "RECV-01", "STAGE-01"
    """
    
    def __init__(self):
        super().__init__(PatternType.SPECIAL)
    
    def analyze(self, examples: List[str]) -> Optional[FormatPattern]:
        """
        Detect special location patterns
        """
        pattern = r'^(RECV|STAGE|DOCK|AISLE|RECEIVING|STAGING|SHIPPING)-?(\d{1,3})?$'
        matched_examples = []
        
        for example in examples:
            clean_example = example.strip().upper()
            if re.match(pattern, clean_example) or clean_example in {'RECEIVING', 'STAGING', 'SHIPPING', 'DOCK'}:
                matched_examples.append(clean_example)
        
        if not matched_examples:
            return None
        
        confidence = self._calculate_confidence(examples, matched_examples)
        
        if confidence < 0.8:  # High threshold for special locations
            return None
        
        return FormatPattern(
            pattern_type=self.pattern_type,
            regex_pattern=pattern,
            canonical_converter="passthrough",  # Special locations pass through unchanged
            confidence=confidence,
            examples=matched_examples[:5],
            components={
                'special_types': list(set(ex.split('-')[0] for ex in matched_examples)),
                'numbered': any('-' in ex for ex in matched_examples)
            },
            description=f"Special location format detected with {confidence:.1%} confidence"
        )


class ZoneAnalyzer(PatternAnalyzer):
    """
    Analyzes zone-based location patterns like "ZONE-A-001", "SECTOR-B-125"
    """
    
    def __init__(self):
        super().__init__(PatternType.ZONE)
    
    def analyze(self, examples: List[str]) -> Optional[FormatPattern]:
        """
        Detect zone-based location patterns
        """
        # Zone patterns: ZONE-A-001, SECTOR-B-125, AREA-C-075, etc.
        patterns = [
            r'^(ZONE|AREA|SECTOR|REGION|BLOCK)-([A-Z])-(\d{3})$',
            r'^(ZONE|AREA|SECTOR|REGION|BLOCK)-([A-Z])(\d{2,3})$',
            r'^([A-Z]{3,6})-([A-Z])-(\d{2,3})$'
        ]
        
        matched_examples = []
        best_pattern = None
        best_pattern_matches = 0
        
        for pattern in patterns:
            current_matches = []
            for example in examples:
                clean_example = example.strip().upper()
                if re.match(pattern, clean_example):
                    current_matches.append(clean_example)
            
            if len(current_matches) > best_pattern_matches:
                best_pattern_matches = len(current_matches)
                matched_examples = current_matches
                best_pattern = pattern
        
        if not matched_examples:
            return None
        
        confidence = self._calculate_confidence(examples, matched_examples)
        
        if confidence < 0.7:  # Moderate threshold for zone patterns
            return None
        
        # Extract components for canonical conversion
        sample_match = re.match(best_pattern, matched_examples[0])
        if sample_match:
            groups = sample_match.groups()
            zone_prefix = groups[0]
            zone_letter = groups[1]
            zone_number = groups[2]
        else:
            zone_prefix = "ZONE"
            zone_letter = "A"
            zone_number = "001"
        
        return FormatPattern(
            pattern_type=self.pattern_type,
            regex_pattern=best_pattern,
            canonical_converter=f"{zone_prefix}-{{zone_letter}}-{{zone_number:03d}}",
            confidence=confidence,
            examples=matched_examples,
            components={
                'zone_prefix': zone_prefix,
                'zone_letter_format': 'single_letter',
                'zone_number_format': f'{len(zone_number)}_digit'
            },
            description=f"Zone-based location format detected with {confidence:.1%} confidence"
        )


class SmartFormatDetector:
    """
    Main format detection engine that analyzes location examples and 
    determines the most likely format pattern with confidence scoring.
    """
    
    def __init__(self):
        self.analyzers = [
            SpecialAnalyzer(),      # Check special locations first
            ZoneAnalyzer(),         # Then zone-based patterns (ZONE-A-001)
            StandardAnalyzer(),     # Then standard canonical format
            LetterPrefixedAnalyzer(), # Then letter-prefixed format (A01-R02-P15)
            PositionLevelAnalyzer(), # Then position+level
            CompactAnalyzer()       # Finally compact format
        ]
        logger.info("SmartFormatDetector initialized with %d analyzers", len(self.analyzers))
    
    def detect_format(self, examples: List[str]) -> Dict[str, any]:
        """
        Analyze location examples and detect the most likely format pattern.
        
        Args:
            examples: List of location code examples (e.g., ["010A", "325B", "245D"])
            
        Returns:
            Dictionary with detection results:
            {
                'detected_pattern': FormatPattern or None,
                'all_patterns': List[FormatPattern],
                'confidence': float,
                'canonical_examples': List[str],
                'analysis_summary': str,
                'recommendations': List[str]
            }
        """
        if not examples:
            return self._empty_result("No examples provided")
        
        # Clean and normalize examples
        cleaned_examples = self._clean_examples(examples)
        if not cleaned_examples:
            return self._empty_result("No valid examples after cleaning")
        
        logger.info("Analyzing %d location examples: %s", len(cleaned_examples), cleaned_examples[:5])
        
        # Run all analyzers
        detected_patterns = []
        for analyzer in self.analyzers:
            try:
                pattern = analyzer.analyze(cleaned_examples)
                if pattern:
                    detected_patterns.append(pattern)
                    logger.debug("Pattern detected by %s: %s (confidence: %.2f)",
                               analyzer.__class__.__name__, pattern.pattern_type.value, pattern.confidence)
            except Exception as e:
                logger.error("Analyzer %s failed: %s", analyzer.__class__.__name__, e)
        
        # Sort by confidence and select best
        detected_patterns.sort(key=lambda p: p.confidence, reverse=True)
        best_pattern = detected_patterns[0] if detected_patterns else None
        
        # Generate canonical examples
        canonical_examples = self._generate_canonical_examples(cleaned_examples, best_pattern)
        
        # Create analysis summary
        analysis_summary = self._create_analysis_summary(cleaned_examples, detected_patterns, best_pattern)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(best_pattern, cleaned_examples)
        
        result = {
            'detected_pattern': best_pattern.to_dict() if best_pattern else None,
            'all_patterns': [p.to_dict() for p in detected_patterns],
            'confidence': best_pattern.confidence if best_pattern else 0.0,
            'canonical_examples': canonical_examples,
            'analysis_summary': analysis_summary,
            'recommendations': recommendations,
            'input_examples': cleaned_examples
        }
        
        logger.info("Format detection completed. Best pattern: %s (confidence: %.2f)",
                   best_pattern.pattern_type.value if best_pattern else "None",
                   best_pattern.confidence if best_pattern else 0.0)
        
        return result
    
    def _clean_examples(self, examples: List[str]) -> List[str]:
        """Clean and normalize input examples"""
        cleaned = []
        for example in examples:
            if isinstance(example, str) and example.strip():
                clean_ex = example.strip().upper()
                if clean_ex not in cleaned:  # Remove duplicates
                    cleaned.append(clean_ex)
        
        # Limit to reasonable number of examples for analysis
        return cleaned[:20]
    
    def _generate_canonical_examples(self, examples: List[str], pattern: Optional[FormatPattern]) -> List[str]:
        """Generate canonical format examples based on detected pattern"""
        if not pattern or not examples:
            return []
        
        canonical_examples = []
        
        try:
            if pattern.pattern_type == PatternType.POSITION_LEVEL:
                # Convert position+level to canonical
                for example in examples[:5]:
                    match = re.match(r'^(\d{3})([A-Z])$', example)
                    if match:
                        position, level = match.groups()
                        canonical = f"01-01-{position}{level}"
                        canonical_examples.append(f"{example} -> {canonical}")
            
            elif pattern.pattern_type == PatternType.STANDARD:
                # Already canonical, just normalize padding
                for example in examples[:5]:
                    match = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{1,3})([A-Z])$', example)
                    if match:
                        aisle, rack, position, level = match.groups()
                        canonical = f"{int(aisle):02d}-{int(rack):02d}-{int(position):03d}{level}"
                        canonical_examples.append(f"{example} -> {canonical}")
            
            elif pattern.pattern_type == PatternType.COMPACT:
                # Convert compact to canonical
                for example in examples[:5]:
                    match = re.match(r'^(\d{1,2})([A-Z])(\d{1,2})([A-Z])$', example)
                    if match:
                        aisle, _, position, level = match.groups()
                        canonical = f"{int(aisle):02d}-01-{int(position):03d}{level}"
                        canonical_examples.append(f"{example} -> {canonical}")
            
            elif pattern.pattern_type == PatternType.SPECIAL:
                # Special locations pass through
                for example in examples[:5]:
                    canonical_examples.append(f"{example} -> {example}")
        
        except Exception as e:
            logger.error("Failed to generate canonical examples: %s", e)
        
        return canonical_examples
    
    def _create_analysis_summary(self, examples: List[str], patterns: List[FormatPattern], best_pattern: Optional[FormatPattern]) -> str:
        """Create human-readable analysis summary"""
        if not best_pattern:
            return f"Could not detect a reliable format pattern from {len(examples)} examples. " \
                   "Examples may be inconsistent or follow an unsupported format."
        
        summary_parts = [
            f"Analyzed {len(examples)} location examples.",
            f"Detected {best_pattern.pattern_type.value} format with {best_pattern.confidence:.1%} confidence.",
            best_pattern.description
        ]
        
        if len(patterns) > 1:
            summary_parts.append(f"Found {len(patterns)} possible patterns, selected the most confident match.")
        
        return " ".join(summary_parts)
    
    def _generate_recommendations(self, pattern: Optional[FormatPattern], examples: List[str]) -> List[str]:
        """Generate actionable recommendations based on detection results"""
        recommendations = []
        
        if not pattern:
            recommendations.extend([
                "Provide more consistent examples to improve pattern detection",
                "Ensure examples follow a standard warehouse location format",
                "Consider using a supported format: position+level (010A), standard (01-01-001A), or compact (01A01A)"
            ])
            return recommendations
        
        if pattern.confidence < 0.7:
            recommendations.append("Consider providing more examples to improve detection confidence")
        
        if pattern.pattern_type == PatternType.POSITION_LEVEL:
            recommendations.extend([
                "This format will be converted to canonical format (01-01-PPPL) with default aisle=01, rack=01",
                "Consider defining specific aisle and rack assignments for better organization",
                "Test the format with your existing location data to ensure compatibility"
            ])
        
        elif pattern.pattern_type == PatternType.STANDARD:
            recommendations.extend([
                "This format is already compatible with the canonical location system",
                "No conversion needed - locations will be used as provided",
                "Ensure all location components (aisle, rack, position, level) are correctly defined"
            ])
        
        elif pattern.pattern_type == PatternType.COMPACT:
            recommendations.extend([
                "This format will be converted with rack=01 as default",
                "Consider if bidirectional racks are needed for your warehouse layout",
                "Verify that the aisle and position mappings match your physical layout"
            ])
        
        elif pattern.pattern_type == PatternType.SPECIAL:
            recommendations.extend([
                "Special locations will pass through unchanged",
                "Ensure these special area definitions match your warehouse layout",
                "Consider defining capacity and operational rules for these areas"
            ])
        
        # General recommendations
        if len(examples) >= 10:
            recommendations.append("Good sample size provided - detection results should be reliable")
        elif len(examples) >= 5:
            recommendations.append("Moderate sample size - consider adding more examples for better accuracy")
        else:
            recommendations.append("Small sample size - provide more examples for more reliable detection")
        
        return recommendations
    
    def _empty_result(self, reason: str) -> Dict[str, any]:
        """Return empty result with error message"""
        return {
            'detected_pattern': None,
            'all_patterns': [],
            'confidence': 0.0,
            'canonical_examples': [],
            'analysis_summary': reason,
            'recommendations': ["Provide valid location examples to enable format detection"],
            'input_examples': []
        }
    
    def validate_format_config(self, format_config: Dict[str, any]) -> Dict[str, any]:
        """
        Validate a format configuration and ensure it's compatible with the canonical system.
        
        Args:
            format_config: Format configuration dictionary
            
        Returns:
            Validation result with status and messages
        """
        if not format_config:
            return {
                'valid': False,
                'errors': ['Format configuration is empty'],
                'warnings': []
            }
        
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['pattern_type', 'confidence', 'canonical_converter']
        for field in required_fields:
            if field not in format_config:
                errors.append(f"Missing required field: {field}")
        
        # Validate pattern type
        if 'pattern_type' in format_config:
            try:
                PatternType(format_config['pattern_type'])
            except ValueError:
                errors.append(f"Invalid pattern_type: {format_config['pattern_type']}")
        
        # Validate confidence
        if 'confidence' in format_config:
            confidence = format_config['confidence']
            if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
                errors.append("Confidence must be a number between 0 and 1")
            elif confidence < 0.5:
                warnings.append("Low confidence score may indicate unreliable format detection")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def create_format_config(self, detection_result: Dict[str, any], warehouse_metadata: Dict[str, any] = None) -> Dict[str, any]:
        """
        Create a complete format configuration for storage in the database.
        
        Args:
            detection_result: Result from detect_format method
            warehouse_metadata: Optional warehouse context information
            
        Returns:
            Complete format configuration ready for database storage
        """
        if not detection_result.get('detected_pattern'):
            return {}
        
        pattern = detection_result['detected_pattern']
        
        config = {
            'pattern_type': pattern['pattern_type'],
            'confidence': pattern['confidence'],
            'canonical_converter': pattern['canonical_converter'],
            'regex_pattern': pattern['regex_pattern'],
            'components': pattern['components'],
            'examples': pattern['examples'],
            'description': pattern['description'],
            'canonical_examples': detection_result['canonical_examples'],
            'analysis_summary': detection_result['analysis_summary'],
            'recommendations': detection_result['recommendations'],
            'detection_metadata': {
                'detector_version': '1.0.0',
                'detection_timestamp': None,  # Will be set by caller
                'input_example_count': len(detection_result['input_examples']),
                'alternative_patterns_count': len(detection_result['all_patterns']) - 1
            }
        }
        
        # Add warehouse metadata if provided
        if warehouse_metadata:
            config['warehouse_context'] = warehouse_metadata
        
        return config


# Convenience functions for easy integration
def detect_location_format(examples: List[str]) -> Dict[str, any]:
    """
    Convenience function to detect location format from examples.
    
    Args:
        examples: List of location code examples
        
    Returns:
        Format detection results
    """
    detector = SmartFormatDetector()
    return detector.detect_format(examples)


def create_format_configuration(examples: List[str], warehouse_context: Dict[str, any] = None) -> Dict[str, any]:
    """
    Convenience function to create a complete format configuration.
    
    Args:
        examples: List of location code examples
        warehouse_context: Optional warehouse metadata
        
    Returns:
        Complete format configuration for database storage
    """
    detector = SmartFormatDetector()
    detection_result = detector.detect_format(examples)
    return detector.create_format_config(detection_result, warehouse_context)


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    
    # Test with position+level format
    examples = ["010A", "325B", "245D", "156C", "087A"]
    print("Testing with position+level examples:", examples)
    
    result = detect_location_format(examples)
    print(f"Detected pattern: {result['detected_pattern']['pattern_type'] if result['detected_pattern'] else 'None'}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Analysis: {result['analysis_summary']}")
    print("Canonical examples:")
    for example in result['canonical_examples']:
        print(f"  {example}")