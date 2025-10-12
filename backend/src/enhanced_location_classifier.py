"""
Enhanced Location Classification System
Zero-Cost Solution for Location Type Dependency Crisis

This module provides intelligent location classification without external AI dependencies,
designed to reduce "UNKNOWN" classifications from 70% to <25% immediately.
"""

import re
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

@dataclass
class ClassificationResult:
    """Result of location classification with confidence scoring"""
    location_type: str
    confidence: float
    method: str  # 'pattern', 'behavioral', 'user_correction', 'virtual'
    reasoning: str

class LocationCategory(Enum):
    """Standard warehouse location categories"""
    RECEIVING = "RECEIVING"
    STORAGE = "STORAGE"
    TRANSITIONAL = "TRANSITIONAL"
    STAGING = "STAGING"
    DOCK = "DOCK"
    AISLE = "AISLE"
    SPECIAL = "SPECIAL"
    UNKNOWN = "UNKNOWN"

class EnhancedLocationClassifier:
    """
    Intelligent location classification system combining multiple approaches:
    1. Enhanced pattern recognition
    2. Behavioral analysis using inventory statistics
    3. User feedback learning
    4. Confidence scoring
    """

    def __init__(self, db_session=None, virtual_engine=None):
        self.db = db_session
        self.virtual_engine = virtual_engine
        self.user_corrections = {}  # Cache for user corrections
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize comprehensive pattern library for location classification"""
        self.pattern_library = {
            'RECEIVING': {
                'explicit_keywords': [
                    'recv', 'receiving', 'inbound', 'dock', 'rec', 'receive',
                    'incoming', 'arrival', 'delivery', 'unload', 'intake'
                ],
                'positional_patterns': [
                    r'.*-0[1-5]$',      # Common receiving numbering: -01, -02, -03, -04, -05
                    r'.*-00[1-9]$',     # Zero-padded receiving: -001, -002, etc.
                    r'.*dock.*\d+$',    # Dock with numbers: DOCK-1, DOCK-2
                    r'rec[_-]?\d+',     # REC-1, REC_2, REC01, etc.
                ],
                'semantic_patterns': [
                    r'.*temp.*',        # Temporary holding
                    r'.*hold.*',        # Holding areas
                    r'.*buffer.*',      # Buffer zones
                    r'.*queue.*',       # Queue areas
                ],
                'confidence_weight': 0.9
            },

            'STORAGE': {
                'explicit_keywords': [
                    'stor', 'storage', 'rack', 'shelf', 'aisle', 'bin',
                    'slot', 'position', 'bay', 'tier'
                ],
                'grid_patterns': [
                    r'^[a-z]-\d+.*',           # A-12-045B format
                    r'^\d{2,}[a-z]\d+.*',      # 12A045 format
                    r'^[a-z]\d{2,}-[a-z]\d{2,}.*',  # A12-B34 format
                    r'.*rack.*\d+.*',          # RACK-12-45
                    r'.*aisle.*[a-z].*\d+.*',  # AISLE-A-12
                ],
                'level_patterns': [
                    r'.*-[a-d]$',             # Ends with level: -A, -B, -C, -D
                    r'.*[a-d]\d+$',           # Level + position: A12, B034
                    r'.*l[0-9]+.*',           # Level indicators: L1, L2, L3
                ],
                'confidence_weight': 0.85
            },

            'TRANSITIONAL': {
                'explicit_keywords': [
                    'stage', 'staging', 'transit', 'transfer', 'move', 'temp',
                    'work', 'process', 'prep', 'preparation', 'sort', 'consolidate'
                ],
                'workflow_patterns': [
                    r'.*wip.*',               # Work in progress
                    r'.*staging.*',           # Staging areas
                    r'.*prep.*',              # Preparation areas
                    r'.*sort.*',              # Sorting areas
                ],
                'confidence_weight': 0.8
            },

            'STAGING': {
                'explicit_keywords': [
                    'stage', 'staging', 'outbound', 'ship', 'shipping', 'load',
                    'loading', 'departure', 'dispatch', 'ship-to'
                ],
                'shipping_patterns': [
                    r'.*ship.*\d+.*',         # SHIP-1, SHIP-DOCK-A
                    r'.*load.*\d+.*',         # LOAD-1, LOADING-BAY-2
                    r'.*out.*\d+.*',          # OUT-1, OUTBOUND-2
                ],
                'confidence_weight': 0.8
            },

            'DOCK': {
                'explicit_keywords': [
                    'dock', 'door', 'gate', 'bay', 'truck', 'trailer'
                ],
                'dock_patterns': [
                    r'.*dock.*\d+.*',         # DOCK-1, TRUCK-DOCK-A
                    r'.*door.*\d+.*',         # DOOR-12, BAY-DOOR-3
                    r'.*gate.*[a-z0-9]+.*',   # GATE-A, GATE-12
                ],
                'confidence_weight': 0.9
            },

            'AISLE': {
                'explicit_keywords': ['aisle', 'corridor', 'walkway'],
                'aisle_patterns': [
                    r'.*aisle.*\d+.*',        # AISLE-1, AISLE-A
                    r'^aisle.*',              # Starts with AISLE
                ],
                'confidence_weight': 0.85
            }
        }

    def classify_location(self, location: str, inventory_context: pd.DataFrame = None,
                         warehouse_context: dict = None) -> ClassificationResult:
        """
        Main classification method with multi-layered approach

        Args:
            location: Location code to classify
            inventory_context: Historical inventory data for behavioral analysis
            warehouse_context: Warehouse configuration context

        Returns:
            ClassificationResult with type, confidence, method, and reasoning
        """
        if pd.isna(location) or not str(location).strip():
            return ClassificationResult('MISSING', 1.0, 'validation', 'Empty location code')

        location_str = str(location).strip()

        # Priority 1: User corrections (perfect accuracy)
        user_result = self._check_user_corrections(location_str, warehouse_context)
        if user_result:
            return user_result

        # Priority 2: Virtual engine validation (if available)
        virtual_result = self._check_virtual_engine(location_str)
        if virtual_result and virtual_result.confidence > 0.8:
            return virtual_result

        # Priority 3: Enhanced pattern matching
        pattern_result = self._classify_by_patterns(location_str)

        # Priority 4: Behavioral analysis (if inventory data available)
        if inventory_context is not None and len(inventory_context) > 0:
            behavioral_result = self._classify_by_behavior(location_str, inventory_context)
            if behavioral_result and behavioral_result.confidence > 0.7:
                # Combine pattern and behavioral analysis
                return self._combine_classifications(pattern_result, behavioral_result)

        return pattern_result

    def _classify_by_patterns(self, location: str) -> ClassificationResult:
        """Enhanced pattern-based classification with confidence scoring"""
        location_clean = location.upper().strip()

        classification_scores = {}

        for location_type, patterns in self.pattern_library.items():
            total_score = 0
            matches = []

            # Check explicit keywords
            for keyword in patterns.get('explicit_keywords', []):
                if keyword.upper() in location_clean:
                    total_score += 1.0
                    matches.append(f"keyword:{keyword}")

            # Check pattern groups
            for pattern_group in ['positional_patterns', 'semantic_patterns',
                                'grid_patterns', 'level_patterns', 'workflow_patterns',
                                'shipping_patterns', 'dock_patterns', 'aisle_patterns']:
                for pattern in patterns.get(pattern_group, []):
                    if re.match(pattern, location_clean):
                        total_score += 0.8
                        matches.append(f"pattern:{pattern}")

            if total_score > 0:
                # Apply confidence weight and normalize
                confidence = min(total_score * patterns.get('confidence_weight', 0.7), 0.95)
                classification_scores[location_type] = {
                    'confidence': confidence,
                    'matches': matches
                }

        if not classification_scores:
            return self._fallback_classification(location_clean)

        # Select best classification
        best_type = max(classification_scores, key=lambda k: classification_scores[k]['confidence'])
        best_score = classification_scores[best_type]

        reasoning = f"Matched {len(best_score['matches'])} patterns: {', '.join(best_score['matches'][:3])}"

        return ClassificationResult(
            location_type=best_type,
            confidence=best_score['confidence'],
            method='pattern',
            reasoning=reasoning
        )

    def _classify_by_behavior(self, location: str, inventory_data: pd.DataFrame) -> Optional[ClassificationResult]:
        """Behavioral classification using inventory statistics"""
        location_data = inventory_data[inventory_data['location'] == location]

        if len(location_data) < 2:  # Need minimum data for behavioral analysis
            return None

        # Calculate behavioral indicators
        unique_products = location_data['product'].nunique() if 'product' in location_data.columns else 0
        total_pallets = len(location_data)
        diversity_ratio = unique_products / total_pallets if total_pallets > 0 else 0

        # Analyze timing patterns if creation_date available
        has_timing_data = 'creation_date' in location_data.columns
        avg_dwell_time = None

        if has_timing_data:
            try:
                location_data['creation_date'] = pd.to_datetime(location_data['creation_date'])
                current_time = pd.Timestamp.now()
                dwell_times = (current_time - location_data['creation_date']).dt.total_seconds() / 3600  # hours
                avg_dwell_time = dwell_times.mean()
            except:
                pass

        # Behavioral classification rules
        if diversity_ratio > 0.8:  # High product diversity suggests receiving/transitional
            confidence = min(0.7 + (diversity_ratio - 0.8) * 0.5, 0.9)
            return ClassificationResult(
                location_type='RECEIVING',
                confidence=confidence,
                method='behavioral',
                reasoning=f"High product diversity ({diversity_ratio:.2f}) indicates receiving area"
            )

        if diversity_ratio < 0.2 and total_pallets > 3:  # Low diversity, consistent products
            confidence = min(0.7 + (0.2 - diversity_ratio) * 1.0, 0.9)
            return ClassificationResult(
                location_type='STORAGE',
                confidence=confidence,
                method='behavioral',
                reasoning=f"Low product diversity ({diversity_ratio:.2f}) indicates storage area"
            )

        # Dwell time analysis
        if avg_dwell_time is not None:
            if avg_dwell_time < 24:  # Less than 24 hours
                return ClassificationResult(
                    location_type='RECEIVING',
                    confidence=0.75,
                    method='behavioral',
                    reasoning=f"Short average dwell time ({avg_dwell_time:.1f}h) indicates receiving"
                )
            elif avg_dwell_time > 168:  # More than 1 week
                return ClassificationResult(
                    location_type='STORAGE',
                    confidence=0.8,
                    method='behavioral',
                    reasoning=f"Long average dwell time ({avg_dwell_time:.1f}h) indicates storage"
                )

        return None

    def _fallback_classification(self, location: str) -> ClassificationResult:
        """Final fallback for unmatched locations using heuristics"""
        location_clean = location.upper()

        # Simple heuristics for common patterns
        if any(char.isdigit() for char in location_clean) and any(char.isalpha() for char in location_clean):
            if len([c for c in location_clean if c.isdigit()]) > len([c for c in location_clean if c.isalpha()]):
                # More numbers than letters suggests structured storage
                return ClassificationResult('STORAGE', 0.6, 'heuristic', 'Alphanumeric with digit majority')

        # Very short codes often special areas
        if len(location_clean.replace('-', '').replace('_', '')) <= 3:
            return ClassificationResult('SPECIAL', 0.5, 'heuristic', 'Short code suggests special area')

        # Default to UNKNOWN with low confidence
        return ClassificationResult('UNKNOWN', 0.1, 'fallback', 'No matching patterns found')

    def _check_user_corrections(self, location: str, warehouse_context: dict = None) -> Optional[ClassificationResult]:
        """Check for user corrections from database"""
        if not warehouse_context or not warehouse_context.get('warehouse_id') or not self.db:
            return None

        try:
            from models import LocationClassificationCorrection

            # Find correction for this location
            correction = LocationClassificationCorrection.find_correction_for_location(
                warehouse_id=warehouse_context['warehouse_id'],
                location_code=location
            )

            if correction:
                # Update usage statistics
                correction.increment_applied_count()
                self.db.commit()

                return ClassificationResult(
                    location_type=correction.corrected_type,
                    confidence=correction.pattern_confidence,
                    method='user_correction',
                    reasoning=f"User correction applied (used {correction.applied_count} times)"
                )

        except Exception as e:
            print(f"[ENHANCED_CLASSIFIER] Error checking user corrections: {e}")

        return None

    def _check_virtual_engine(self, location: str) -> Optional[ClassificationResult]:
        """Use virtual engine if available for validation"""
        if not self.virtual_engine:
            return None

        try:
            if hasattr(self.virtual_engine, 'special_areas'):
                special_areas_upper = [area.upper() for area in self.virtual_engine.special_areas]
                if location.upper() in special_areas_upper:
                    # Classify special areas by pattern
                    location_upper = location.upper()
                    if any(pattern in location_upper for pattern in ['RECV', 'RECEIVING', 'DOCK', 'INBOUND']):
                        return ClassificationResult('RECEIVING', 0.9, 'virtual', 'Virtual engine special area classification')
                    elif any(pattern in location_upper for pattern in ['STAGE', 'STAGING', 'TRANSIT']):
                        return ClassificationResult('TRANSITIONAL', 0.9, 'virtual', 'Virtual engine special area classification')

            if hasattr(self.virtual_engine, 'validate_location'):
                validation_result = self.virtual_engine.validate_location(location)
                # Handle tuple result (is_valid: bool, reason: str)
                if isinstance(validation_result, tuple) and len(validation_result) >= 2:
                    is_valid, reason = validation_result
                    if is_valid:
                        return ClassificationResult('STORAGE', 0.85, 'virtual', 'Virtual engine validation passed')
                # Handle dict result (fallback for other implementations)
                elif isinstance(validation_result, dict) and validation_result.get('is_valid'):
                    return ClassificationResult('STORAGE', 0.85, 'virtual', 'Virtual engine validation passed')
        except Exception as e:
            print(f"[ENHANCED_CLASSIFIER] Virtual engine error: {e}")

        return None

    def _combine_classifications(self, pattern_result: ClassificationResult,
                               behavioral_result: ClassificationResult) -> ClassificationResult:
        """Combine pattern and behavioral analysis results"""
        # If both agree, increase confidence
        if pattern_result.location_type == behavioral_result.location_type:
            combined_confidence = min(pattern_result.confidence + 0.1, 0.95)
            return ClassificationResult(
                location_type=pattern_result.location_type,
                confidence=combined_confidence,
                method='combined',
                reasoning=f"Pattern + Behavioral: {pattern_result.reasoning}"
            )

        # If they disagree, use the higher confidence one
        if behavioral_result.confidence > pattern_result.confidence:
            return behavioral_result
        else:
            return pattern_result

    def classify_batch(self, locations: List[str], inventory_df: pd.DataFrame = None,
                      warehouse_context: dict = None) -> Dict[str, ClassificationResult]:
        """Batch classification for efficiency"""
        results = {}

        for location in locations:
            # Filter inventory data for this location if available
            location_inventory = None
            if inventory_df is not None:
                location_inventory = inventory_df[inventory_df['location'] == location]

            results[location] = self.classify_location(location, location_inventory, warehouse_context)

        return results

    def get_classification_summary(self, results: Dict[str, ClassificationResult]) -> Dict[str, Any]:
        """Generate summary statistics for classification results"""
        if not results:
            return {}

        type_counts = {}
        confidence_stats = []
        method_counts = {}

        for location, result in results.items():
            # Count types
            type_counts[result.location_type] = type_counts.get(result.location_type, 0) + 1

            # Collect confidence scores
            confidence_stats.append(result.confidence)

            # Count methods
            method_counts[result.method] = method_counts.get(result.method, 0) + 1

        unknown_rate = type_counts.get('UNKNOWN', 0) / len(results) * 100
        avg_confidence = sum(confidence_stats) / len(confidence_stats)

        return {
            'total_locations': len(results),
            'type_distribution': type_counts,
            'unknown_rate_percent': round(unknown_rate, 1),
            'average_confidence': round(avg_confidence, 3),
            'method_distribution': method_counts,
            'high_confidence_count': len([c for c in confidence_stats if c > 0.8])
        }