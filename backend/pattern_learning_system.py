#!/usr/bin/env python3
"""
Phase 3: Pattern Learning System
Implements adaptive location pattern recognition and learning capabilities
"""

import sys
import os
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, Counter
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location

class LocationPatternLearner:
    """Learns and adapts to location format patterns automatically"""
    
    def __init__(self, pattern_cache_file: str = 'location_patterns.pkl'):
        self.pattern_cache_file = pattern_cache_file
        self.learned_patterns = self._load_patterns()
        self.success_history = []
        self.failure_history = []
        self.learning_stats = {
            'patterns_learned': 0,
            'successful_matches': 0,
            'failed_matches': 0,
            'last_learning_session': None
        }
    
    def _load_patterns(self) -> Dict:
        """Load previously learned patterns from cache"""
        try:
            if os.path.exists(self.pattern_cache_file):
                with open(self.pattern_cache_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"Could not load pattern cache: {e}")
        
        return {
            'successful_transformations': defaultdict(list),
            'format_patterns': defaultdict(int),
            'warehouse_specific_patterns': defaultdict(dict),
            'transformation_confidence': defaultdict(float)
        }
    
    def _save_patterns(self):
        """Save learned patterns to cache"""
        try:
            with open(self.pattern_cache_file, 'wb') as f:
                pickle.dump(self.learned_patterns, f)
        except Exception as e:
            print(f"Could not save pattern cache: {e}")
    
    def learn_from_successful_match(self, inventory_location: str, matched_db_location: str, 
                                  warehouse_id: str, confidence_score: float = 1.0):
        """
        Learn from successful location matches to improve future recognition
        
        Args:
            inventory_location: Original location from inventory data
            matched_db_location: Location that successfully matched in database
            warehouse_id: Warehouse context for the match
            confidence_score: Confidence score of the match (0.0-1.0)
        """
        print(f"[PATTERN_LEARNING] Learning: '{inventory_location}' -> '{matched_db_location}' (warehouse: {warehouse_id})")
        
        # Extract transformation pattern
        transformation = self._extract_transformation_pattern(inventory_location, matched_db_location)
        
        if transformation:
            # Store successful transformation
            key = f"{transformation['pattern_type']}:{transformation['from_format']}:{transformation['to_format']}"
            self.learned_patterns['successful_transformations'][key].append({
                'inventory_location': inventory_location,
                'matched_location': matched_db_location,
                'warehouse_id': warehouse_id,
                'confidence': confidence_score,
                'timestamp': datetime.now().isoformat(),
                'transformation': transformation
            })
            
            # Update warehouse-specific patterns
            if warehouse_id not in self.learned_patterns['warehouse_specific_patterns']:
                self.learned_patterns['warehouse_specific_patterns'][warehouse_id] = defaultdict(list)
            
            self.learned_patterns['warehouse_specific_patterns'][warehouse_id][transformation['pattern_type']].append(transformation)
            
            # Update confidence scoring
            self.learned_patterns['transformation_confidence'][key] = min(
                self.learned_patterns['transformation_confidence'][key] + (confidence_score * 0.1),
                1.0
            )
            
            # Track learning statistics
            self.learning_stats['successful_matches'] += 1
            self.learning_stats['patterns_learned'] += 1
            
            print(f"[PATTERN_LEARNING] Learned transformation pattern: {transformation}")
    
    def _extract_transformation_pattern(self, input_loc: str, output_loc: str) -> Optional[Dict]:
        """
        Extract the transformation pattern between two location strings
        
        Args:
            input_loc: Input location string
            output_loc: Output location string
            
        Returns:
            Dictionary describing the transformation pattern
        """
        input_clean = input_loc.strip().upper()
        output_clean = output_loc.strip().upper()
        
        if input_clean == output_clean:
            return {
                'pattern_type': 'EXACT_MATCH',
                'from_format': input_clean,
                'to_format': output_clean,
                'transformation': 'none'
            }
        
        # Check for padding transformations
        if re.match(r'^\d{1,2}-\d{1,2}-\d{1,3}[A-Z]$', input_clean) and re.match(r'^\d{2}-\d{2}-\d{3}[A-Z]$', output_clean):
            return {
                'pattern_type': 'AISLE_PADDING',
                'from_format': self._extract_format_pattern(input_clean),
                'to_format': self._extract_format_pattern(output_clean),
                'transformation': 'zero_pad_standardization'
            }
        
        # Check for special location transformations
        if re.match(r'^[A-Z]+-\d+$', input_clean) and re.match(r'^[A-Z]+-\d{2,3}$', output_clean):
            return {
                'pattern_type': 'SPECIAL_LOCATION_PADDING',
                'from_format': self._extract_format_pattern(input_clean),
                'to_format': self._extract_format_pattern(output_clean),
                'transformation': 'special_location_standardization'
            }
        
        # Check for prefix additions/removals
        if input_clean in output_clean or output_clean in input_clean:
            return {
                'pattern_type': 'PREFIX_MODIFICATION',
                'from_format': input_clean,
                'to_format': output_clean,
                'transformation': 'prefix_adjustment'
            }
        
        return None
    
    def _extract_format_pattern(self, location: str) -> str:
        """Extract a general format pattern from a location string"""
        # Replace digits with D and letters with L to create pattern
        pattern = re.sub(r'\d', 'D', location)
        pattern = re.sub(r'[A-Z]', 'L', pattern)
        return pattern
    
    def suggest_location_matches(self, inventory_location: str, warehouse_id: str = None) -> List[Tuple[str, float]]:
        """
        Suggest potential location matches based on learned patterns
        
        Args:
            inventory_location: Location to find matches for
            warehouse_id: Optional warehouse context
            
        Returns:
            List of (suggested_location, confidence_score) tuples
        """
        suggestions = []
        input_clean = inventory_location.strip().upper()
        
        print(f"[PATTERN_SUGGESTION] Finding suggestions for '{inventory_location}' (warehouse: {warehouse_id})")
        
        # Check learned transformations
        for transformation_key, examples in self.learned_patterns['successful_transformations'].items():
            pattern_type, from_format, to_format = transformation_key.split(':', 2)
            
            # Filter by warehouse if specified
            relevant_examples = examples
            if warehouse_id:
                relevant_examples = [ex for ex in examples if ex['warehouse_id'] == warehouse_id]
            
            if not relevant_examples:
                continue
            
            # Try to apply learned transformations
            for example in relevant_examples[-5:]:  # Use recent examples
                suggested = self._apply_transformation_pattern(
                    input_clean, 
                    example['transformation']
                )
                
                if suggested and suggested != input_clean:
                    confidence = (
                        example['confidence'] * 
                        self.learned_patterns['transformation_confidence'][transformation_key] *
                        0.8  # Discount for pattern-based suggestion
                    )
                    suggestions.append((suggested, confidence))
        
        # Remove duplicates and sort by confidence
        unique_suggestions = {}
        for suggestion, confidence in suggestions:
            if suggestion not in unique_suggestions or confidence > unique_suggestions[suggestion]:
                unique_suggestions[suggestion] = confidence
        
        sorted_suggestions = sorted(unique_suggestions.items(), key=lambda x: x[1], reverse=True)
        
        print(f"[PATTERN_SUGGESTION] Generated {len(sorted_suggestions)} suggestions")
        for suggestion, confidence in sorted_suggestions[:3]:  # Show top 3
            print(f"  '{suggestion}' (confidence: {confidence:.2f})")
        
        return sorted_suggestions
    
    def _apply_transformation_pattern(self, input_location: str, transformation: Dict) -> Optional[str]:
        """
        Apply a learned transformation pattern to an input location
        
        Args:
            input_location: Location to transform
            transformation: Transformation pattern to apply
            
        Returns:
            Transformed location or None if not applicable
        """
        if transformation['pattern_type'] == 'AISLE_PADDING':
            # Apply aisle padding transformation
            match = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{1,3})([A-Z])$', input_location)
            if match:
                aisle, rack, position, level = match.groups()
                return f"{aisle.zfill(2)}-{rack.zfill(2)}-{position.zfill(3)}{level}"
        
        elif transformation['pattern_type'] == 'SPECIAL_LOCATION_PADDING':
            # Apply special location padding
            match = re.match(r'^([A-Z]+)-(\d+)$', input_location)
            if match:
                prefix, number = match.groups()
                return f"{prefix}-{number.zfill(3)}"
        
        elif transformation['pattern_type'] == 'PREFIX_MODIFICATION':
            # Apply prefix modifications based on learned patterns
            if transformation['transformation'] == 'prefix_adjustment':
                # This would need more sophisticated logic based on specific patterns
                pass
        
        return None
    
    def analyze_warehouse_patterns(self, warehouse_id: str) -> Dict:
        """
        Analyze learned patterns for a specific warehouse
        
        Args:
            warehouse_id: Warehouse to analyze
            
        Returns:
            Analysis of warehouse-specific patterns
        """
        print(f"[PATTERN_ANALYSIS] Analyzing patterns for warehouse: {warehouse_id}")
        
        if warehouse_id not in self.learned_patterns['warehouse_specific_patterns']:
            return {'error': 'No patterns learned for this warehouse'}
        
        warehouse_patterns = self.learned_patterns['warehouse_specific_patterns'][warehouse_id]
        
        analysis = {
            'warehouse_id': warehouse_id,
            'total_patterns': sum(len(patterns) for patterns in warehouse_patterns.values()),
            'pattern_types': {},
            'most_common_transformations': [],
            'success_rate_by_type': {}
        }
        
        # Analyze pattern types
        for pattern_type, patterns in warehouse_patterns.items():
            analysis['pattern_types'][pattern_type] = len(patterns)
            
            # Find most common transformations
            transformations = [p['transformation'] for p in patterns]
            common_transformations = Counter(transformations).most_common(3)
            analysis['most_common_transformations'].extend(common_transformations)
        
        print(f"[PATTERN_ANALYSIS] Found {analysis['total_patterns']} patterns across {len(analysis['pattern_types'])} types")
        
        return analysis
    
    def get_learning_statistics(self) -> Dict:
        """Get comprehensive learning statistics"""
        stats = self.learning_stats.copy()
        stats.update({
            'total_transformation_patterns': len(self.learned_patterns['successful_transformations']),
            'warehouses_with_patterns': len(self.learned_patterns['warehouse_specific_patterns']),
            'average_confidence': sum(self.learned_patterns['transformation_confidence'].values()) / 
                                max(len(self.learned_patterns['transformation_confidence']), 1)
        })
        return stats
    
    def train_from_database(self, max_samples: int = 100) -> int:
        """
        Train the pattern learner from existing database locations
        
        Args:
            max_samples: Maximum number of samples to use for training
            
        Returns:
            Number of patterns learned
        """
        print(f"[PATTERN_TRAINING] Training from database (max {max_samples} samples)")
        
        with app.app_context():
            # Get diverse location samples
            locations = db.session.query(Location.code, Location.warehouse_id).limit(max_samples).all()
            
            patterns_learned = 0
            
            # Simulate learning by creating variations and learning from "matches"
            for location_code, warehouse_id in locations:
                # Create some variations that would represent "user input"
                variations = self._generate_input_variations(location_code)
                
                for variation in variations:
                    if variation != location_code:
                        # Simulate successful match learning
                        self.learn_from_successful_match(
                            variation, location_code, warehouse_id, confidence_score=0.9
                        )
                        patterns_learned += 1
            
            self.learning_stats['last_learning_session'] = datetime.now().isoformat()
            self._save_patterns()
            
            print(f"[PATTERN_TRAINING] Learned {patterns_learned} patterns from {len(locations)} database locations")
            
        return patterns_learned
    
    def _generate_input_variations(self, standard_location: str) -> List[str]:
        """
        Generate variations of a standard location that users might input
        
        Args:
            standard_location: Standard format location
            
        Returns:
            List of possible user input variations
        """
        variations = [standard_location]  # Include original
        
        # For aisle format locations (XX-XX-XXXA)
        match = re.match(r'^(\\d{2})-(\\d{2})-(\\d{3})([A-Z])$', standard_location)
        if match:
            aisle, rack, position, level = match.groups()
            
            # Generate padding variations
            variations.extend([
                f"{int(aisle)}-{int(rack)}-{int(position)}{level}",  # Remove padding
                f"{aisle.zfill(2)}-{int(rack)}-{position}{level}",   # Mixed padding
                f"{int(aisle)}-{rack.zfill(2)}-{int(position)}{level}",  # Mixed padding
            ])
        
        # For special locations (PREFIX-XXX)
        match = re.match(r'^([A-Z]+)-(\\d{3})$', standard_location)
        if match:
            prefix, number = match.groups()
            variations.extend([
                f"{prefix}-{int(number)}",  # Remove padding
                f"{prefix}-{number.zfill(2)}",  # Different padding
            ])
        
        return list(set(variations))  # Remove duplicates

def main():
    """Demonstrate pattern learning system"""
    
    print("PHASE 3: PATTERN LEARNING SYSTEM")
    print("=" * 40)
    
    # Initialize pattern learner
    learner = LocationPatternLearner()
    
    # Train from database
    print("\\nStep 1: Training from database...")
    patterns_learned = learner.train_from_database(max_samples=50)
    
    # Test pattern suggestions
    print("\\nStep 2: Testing pattern suggestions...")
    test_inputs = ['2-1-11B', 'RECV-1', '01-1-001A', 'DOCK1']
    
    for test_input in test_inputs:
        suggestions = learner.suggest_location_matches(test_input, 'USER_TESTF')
        print(f"\\nInput: '{test_input}'")
        if suggestions:
            for suggestion, confidence in suggestions[:3]:
                print(f"  -> '{suggestion}' (confidence: {confidence:.2f})")
        else:
            print("  -> No suggestions found")
    
    # Show learning statistics
    print("\\nStep 3: Learning statistics...")
    stats = learner.get_learning_statistics()
    print(f"  Patterns learned: {stats['patterns_learned']}")
    print(f"  Successful matches: {stats['successful_matches']}")
    print(f"  Transformation patterns: {stats['total_transformation_patterns']}")
    print(f"  Average confidence: {stats['average_confidence']:.2f}")
    
    # Analyze warehouse patterns
    print("\\nStep 4: Warehouse pattern analysis...")
    analysis = learner.analyze_warehouse_patterns('USER_TESTF')
    if 'error' not in analysis:
        print(f"  Total patterns: {analysis['total_patterns']}")
        print(f"  Pattern types: {list(analysis['pattern_types'].keys())}")
    else:
        print(f"  {analysis['error']}")
    
    print("\\n" + "=" * 40)
    print("PATTERN LEARNING SYSTEM DEMONSTRATED")
    
    return patterns_learned > 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)