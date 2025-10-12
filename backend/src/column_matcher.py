"""
Intelligent Column Matching Service for Warehouse Intelligence Engine

This module provides production-ready fuzzy matching for WMS export column mapping.
It uses a three-layer matching strategy to handle real-world column name variations:

Layer 1: Exact & Normalized Matching (99-100% confidence)
- Direct matches after normalization (case, spaces, underscores)
- Example: "Pallet_ID" → "pallet_id" ✓

Layer 2: Fuzzy String Similarity (70-99% confidence)
- Levenshtein distance using rapidfuzz library
- Example: "Pallet number" → "pallet_id" (85% confidence)

Layer 3: Semantic Keyword Expansion (50-70% confidence)
- WMS-specific keyword dictionary with abbreviations
- Example: "ASN" → "receipt_number" (65% confidence)

Author: WareWise Intelligence Team
Date: 2025-01-09
"""

from rapidfuzz import fuzz, process
from typing import Dict, List, Tuple, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ColumnMatcher:
    """
    Intelligent column matching service for WMS export data.

    Handles common variations in WMS exports:
    - Case differences: "PALLET_ID", "Pallet_ID", "pallet_id"
    - Spacing variations: "Pallet ID", "PalletID", "pallet_id"
    - Multi-word vs snake_case: "Pallet number" vs "pallet_id"
    - Abbreviations: "Loc" vs "location", "ASN" vs "receipt_number"
    - WMS-specific terms: "Bin" vs "location", "SKU" vs "description"
    """

    # System column definitions
    REQUIRED_COLUMNS = {
        'pallet_id': {
            'label': 'Pallet ID',
            'description': 'Unique identifier for each pallet',
            'required': True
        },
        'location': {
            'label': 'Location',
            'description': 'Current warehouse location',
            'required': True
        },
        'description': {
            'label': 'Description',
            'description': 'Product description or SKU',
            'required': True
        },
        'receipt_number': {
            'label': 'Receipt Number',
            'description': 'Lot or receipt identifier',
            'required': True
        },
        'creation_date': {
            'label': 'Creation Date',
            'description': 'Date when pallet was created',
            'required': True
        }
    }

    # Semantic keyword expansion for Layer 3 matching
    # Based on 15+ years of real-world WMS integration experience
    SEMANTIC_KEYWORDS = {
        'pallet_id': [
            'pallet', 'id', 'identifier', 'plt', 'palletid', 'pallet number',
            'pallet no', 'pallet#', 'pltid', 'lpn', 'license plate number',
            'pallet_number', 'palletnumber', 'pallet num'
        ],
        'location': [
            'location', 'loc', 'position', 'bin', 'zone', 'warehouse location',
            'storage location', 'storage loc', 'bin location', 'warehouse pos',
            'location code', 'locn', 'wh location', 'storage position'
        ],
        'description': [
            'description', 'desc', 'product', 'item', 'sku', 'material',
            'product description', 'item description', 'item desc', 'product desc',
            'material description', 'product name', 'item name', 'sku description',
            'part description', 'part desc'
        ],
        'receipt_number': [
            'receipt', 'lot', 'batch', 'po', 'order', 'asn', 'inbound',
            'receipt number', 'receipt no', 'receipt#', 'lot number', 'lot no',
            'batch number', 'po number', 'purchase order', 'order number',
            'asn number', 'inbound doc', 'receiving doc', 'receiving number',
            'receiving#', 'receipt_no', 'receiptnumber'
        ],
        'creation_date': [
            'date', 'created', 'timestamp', 'time', 'scan date', 'entry date',
            'creation date', 'create date', 'received date', 'receipt date',
            'scan time', 'entry time', 'timestamp', 'date created', 'datetime',
            'creation_date', 'creationdate', 'createdate', 'date received'
        ]
    }

    def __init__(self):
        """Initialize the column matcher with semantic keywords."""
        self.required_columns = list(self.REQUIRED_COLUMNS.keys())
        logger.info("[COLUMN_MATCHER] Initialized with %d required columns", len(self.required_columns))

    def normalize_column_name(self, column: str) -> str:
        """
        Normalize column name for comparison.

        Transformations:
        - Convert to lowercase
        - Replace spaces, hyphens, dots with underscores
        - Remove special characters
        - Collapse multiple underscores

        Args:
            column: Raw column name from Excel file

        Returns:
            Normalized column name
        """
        normalized = column.lower()
        normalized = re.sub(r'[\s\-\.]+', '_', normalized)  # spaces/hyphens/dots → underscores
        normalized = re.sub(r'[^\w_]', '', normalized)  # remove special chars
        normalized = re.sub(r'_+', '_', normalized)  # collapse multiple underscores
        normalized = normalized.strip('_')  # remove leading/trailing underscores
        return normalized

    def _exact_match(self, required_col: str, user_col: str) -> Optional[float]:
        """
        Layer 1: Check for exact match after normalization.

        Returns:
            Confidence score (0.99-1.0) if match, None otherwise
        """
        normalized_required = self.normalize_column_name(required_col)
        normalized_user = self.normalize_column_name(user_col)

        if normalized_required == normalized_user:
            # Perfect match after normalization
            return 1.0 if required_col == user_col else 0.99

        return None

    def _fuzzy_match(self, required_col: str, user_col: str) -> float:
        """
        Layer 2: Fuzzy string similarity using Levenshtein distance.

        Uses rapidfuzz's ratio scoring which combines:
        - Levenshtein distance (edit operations)
        - Token sort ratio (word order invariant)
        - Partial ratio (substring matching)

        Returns:
            Confidence score (0.0-1.0)
        """
        # Normalize both columns for comparison
        normalized_required = self.normalize_column_name(required_col)
        normalized_user = self.normalize_column_name(user_col)

        # Calculate multiple similarity metrics
        basic_ratio = fuzz.ratio(normalized_required, normalized_user) / 100.0
        partial_ratio = fuzz.partial_ratio(normalized_required, normalized_user) / 100.0
        token_sort_ratio = fuzz.token_sort_ratio(normalized_required, normalized_user) / 100.0

        # Use maximum of the three ratios for best matching
        # This handles word order differences and partial matches
        max_ratio = max(basic_ratio, partial_ratio, token_sort_ratio)

        logger.debug(
            "[FUZZY] %s vs %s: basic=%.2f, partial=%.2f, token_sort=%.2f, max=%.2f",
            required_col, user_col, basic_ratio, partial_ratio, token_sort_ratio, max_ratio
        )

        return max_ratio

    def _semantic_match(self, required_col: str, user_col: str) -> Optional[float]:
        """
        Layer 3: Semantic keyword matching using domain knowledge.

        Checks if user column contains any of the semantic keywords
        associated with the required column.

        Returns:
            Confidence score (0.5-0.7) if semantic match found, None otherwise
        """
        keywords = self.SEMANTIC_KEYWORDS.get(required_col, [])
        normalized_user = self.normalize_column_name(user_col)

        # Check for keyword presence in normalized user column
        for keyword in keywords:
            normalized_keyword = self.normalize_column_name(keyword)

            # Exact keyword match
            if normalized_keyword == normalized_user:
                return 0.70

            # Keyword substring match
            if normalized_keyword in normalized_user or normalized_user in normalized_keyword:
                # Higher confidence for longer matches
                match_ratio = min(len(normalized_keyword), len(normalized_user)) / max(len(normalized_keyword), len(normalized_user))
                confidence = 0.50 + (match_ratio * 0.15)  # 0.50-0.65 range
                return min(confidence, 0.69)  # Cap at 0.69 to stay below fuzzy layer

        return None

    def find_best_match(
        self,
        required_col: str,
        user_columns: List[str],
        min_confidence: float = 0.50
    ) -> Optional[Dict[str, any]]:
        """
        Find the best matching user column for a required column.

        Uses three-layer matching strategy:
        1. Exact match (normalized)
        2. Fuzzy string similarity
        3. Semantic keyword matching

        Args:
            required_col: Required system column name
            user_columns: List of available user column names
            min_confidence: Minimum confidence threshold (default: 0.50)

        Returns:
            Dictionary with match details or None if no match found:
            {
                'matched_column': 'Pallet number',
                'confidence': 0.87,
                'method': 'fuzzy',
                'normalized_user': 'pallet_number',
                'normalized_required': 'pallet_id'
            }
        """
        best_match = None
        best_confidence = min_confidence
        best_method = None

        for user_col in user_columns:
            # Layer 1: Exact match
            exact_conf = self._exact_match(required_col, user_col)
            if exact_conf is not None and exact_conf > best_confidence:
                best_match = user_col
                best_confidence = exact_conf
                best_method = 'exact'
                logger.debug("[LAYER1] Exact match: %s → %s (%.2f)", user_col, required_col, exact_conf)
                continue  # Perfect match, no need to check other layers

            # Layer 2: Fuzzy match
            fuzzy_conf = self._fuzzy_match(required_col, user_col)
            if fuzzy_conf > best_confidence and fuzzy_conf >= 0.70:  # Fuzzy layer threshold
                best_match = user_col
                best_confidence = fuzzy_conf
                best_method = 'fuzzy'
                logger.debug("[LAYER2] Fuzzy match: %s → %s (%.2f)", user_col, required_col, fuzzy_conf)

            # Layer 3: Semantic match (only if fuzzy didn't find a good match)
            if best_confidence < 0.70:
                semantic_conf = self._semantic_match(required_col, user_col)
                if semantic_conf is not None and semantic_conf > best_confidence:
                    best_match = user_col
                    best_confidence = semantic_conf
                    best_method = 'semantic'
                    logger.debug("[LAYER3] Semantic match: %s → %s (%.2f)", user_col, required_col, semantic_conf)

        if best_match:
            return {
                'matched_column': best_match,
                'confidence': round(best_confidence, 2),
                'method': best_method,
                'normalized_user': self.normalize_column_name(best_match),
                'normalized_required': self.normalize_column_name(required_col)
            }

        return None

    def find_all_matches(
        self,
        user_columns: List[str],
        include_alternatives: bool = True,
        alternative_threshold: float = 0.50,
        max_alternatives: int = 3
    ) -> Dict[str, Dict[str, any]]:
        """
        Find best matches for all required columns.

        Args:
            user_columns: List of column names from user's Excel file
            include_alternatives: Whether to include alternative matches
            alternative_threshold: Minimum confidence for alternatives
            max_alternatives: Maximum number of alternatives to return

        Returns:
            Dictionary mapping required columns to match details:
            {
                'pallet_id': {
                    'matched_column': 'Pallet number',
                    'confidence': 0.87,
                    'method': 'fuzzy',
                    'alternatives': [
                        {'column': 'Pallet ID', 'confidence': 0.95},
                        {'column': 'PLT_ID', 'confidence': 0.75}
                    ]
                },
                'location': {
                    'matched_column': 'Loc',
                    'confidence': 0.78,
                    'method': 'semantic',
                    'alternatives': []
                }
            }
        """
        results = {}

        logger.info("[COLUMN_MATCHER] Analyzing %d user columns for %d required columns",
                   len(user_columns), len(self.required_columns))

        for required_col in self.required_columns:
            # Find best match
            best_match = self.find_best_match(required_col, user_columns)

            if best_match:
                results[required_col] = {
                    'matched_column': best_match['matched_column'],
                    'confidence': best_match['confidence'],
                    'method': best_match['method'],
                    'alternatives': []
                }

                # Find alternative matches if requested
                if include_alternatives:
                    alternatives = []
                    for user_col in user_columns:
                        if user_col == best_match['matched_column']:
                            continue  # Skip the best match

                        # Calculate confidence for this alternative
                        exact_conf = self._exact_match(required_col, user_col)
                        if exact_conf:
                            conf = exact_conf
                        else:
                            fuzzy_conf = self._fuzzy_match(required_col, user_col)
                            semantic_conf = self._semantic_match(required_col, user_col) or 0.0
                            conf = max(fuzzy_conf, semantic_conf)

                        if conf >= alternative_threshold and conf < best_match['confidence']:
                            alternatives.append({
                                'column': user_col,
                                'confidence': round(conf, 2)
                            })

                    # Sort by confidence and take top N
                    alternatives.sort(key=lambda x: x['confidence'], reverse=True)
                    results[required_col]['alternatives'] = alternatives[:max_alternatives]

                logger.info("[MATCH] %s → %s (%.0f%% via %s, %d alternatives)",
                           required_col, best_match['matched_column'],
                           best_match['confidence'] * 100, best_match['method'],
                           len(results[required_col]['alternatives']))
            else:
                # No match found
                results[required_col] = {
                    'matched_column': None,
                    'confidence': 0.0,
                    'method': None,
                    'alternatives': []
                }
                logger.warning("[NO_MATCH] Could not find match for required column: %s", required_col)

        return results

    def get_unmapped_columns(
        self,
        user_columns: List[str],
        matches: Dict[str, Dict[str, any]]
    ) -> List[str]:
        """
        Get list of user columns that were not mapped to any required column.

        Args:
            user_columns: List of column names from user's Excel file
            matches: Result from find_all_matches()

        Returns:
            List of unmapped column names
        """
        mapped_columns = set()
        for match_info in matches.values():
            if match_info['matched_column']:
                mapped_columns.add(match_info['matched_column'])

        unmapped = [col for col in user_columns if col not in mapped_columns]

        if unmapped:
            logger.info("[UNMAPPED] %d user columns not mapped: %s", len(unmapped), unmapped)

        return unmapped

    def get_unmapped_required(self, matches: Dict[str, Dict[str, any]]) -> List[str]:
        """
        Get list of required columns that were not matched.

        Args:
            matches: Result from find_all_matches()

        Returns:
            List of unmapped required column names
        """
        unmapped = [
            req_col for req_col, match_info in matches.items()
            if not match_info['matched_column']
        ]

        if unmapped:
            logger.warning("[UNMAPPED_REQUIRED] %d required columns not matched: %s",
                          len(unmapped), unmapped)

        return unmapped


# Convenience function for easy integration
def suggest_column_mapping(
    user_columns: List[str],
    include_alternatives: bool = True
) -> Dict[str, any]:
    """
    Convenience function to get column mapping suggestions.

    Args:
        user_columns: List of column names from user's Excel file
        include_alternatives: Whether to include alternative matches

    Returns:
        Complete mapping suggestions with metadata:
        {
            'suggestions': {...},  # Mapping suggestions
            'user_columns': [...],  # Original user columns
            'unmapped_required': [...],  # Required columns with no match
            'unmapped_user': [...],  # User columns not mapped
            'auto_mappable': {...},  # Columns safe to auto-map (high confidence)
            'requires_review': {...}  # Columns needing user review (low confidence)
        }
    """
    matcher = ColumnMatcher()

    # Find all matches
    matches = matcher.find_all_matches(user_columns, include_alternatives)

    # Get unmapped columns
    unmapped_required = matcher.get_unmapped_required(matches)
    unmapped_user = matcher.get_unmapped_columns(user_columns, matches)

    # Categorize by confidence for UX guidance
    auto_mappable = {}
    requires_review = {}

    for req_col, match_info in matches.items():
        if match_info['matched_column']:
            if match_info['confidence'] >= 0.85:
                # High confidence - safe to auto-apply
                auto_mappable[req_col] = match_info
            else:
                # Lower confidence - needs user review
                requires_review[req_col] = match_info

    return {
        'suggestions': matches,
        'user_columns': user_columns,
        'unmapped_required': unmapped_required,
        'unmapped_user': unmapped_user,
        'auto_mappable': auto_mappable,
        'requires_review': requires_review,
        'statistics': {
            'total_required': len(matcher.required_columns),
            'total_user_columns': len(user_columns),
            'matched': len([m for m in matches.values() if m['matched_column']]),
            'unmapped_required': len(unmapped_required),
            'unmapped_user': len(unmapped_user),
            'auto_mappable_count': len(auto_mappable),
            'requires_review_count': len(requires_review)
        }
    }
