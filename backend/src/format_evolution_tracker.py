"""
Format Evolution Tracker for Smart Configuration System

This module monitors location format patterns during inventory uploads and
detects when formats change or evolve over time, allowing the system to
adapt to warehouse operational changes.

Key Features:
- Real-time format drift detection
- New pattern identification  
- Confidence scoring for evolution candidates
- User notification and approval workflow
- Automatic template format updates
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from collections import Counter, defaultdict
from datetime import datetime

# Local imports
from database import db
from models import WarehouseTemplate, LocationFormatHistory
from smart_format_detector import SmartFormatDetector

logger = logging.getLogger(__name__)


@dataclass
class FormatEvolutionCandidate:
    """
    Represents a potential format evolution detected during analysis
    """
    new_pattern_type: str
    confidence_score: float
    sample_locations: List[str]
    affected_count: int
    original_format: Dict
    new_format: Dict
    change_type: str  # 'new_pattern', 'format_drift', 'special_locations'
    change_description: str


class FormatEvolutionTracker:
    """
    Monitors and detects location format evolution for Smart Configuration
    
    This class analyzes incoming location data during inventory uploads to detect:
    1. Format drift - gradual changes to existing patterns
    2. New patterns - completely new location formats appearing
    3. Special locations - new special area patterns
    4. Format refinements - improvements to pattern recognition
    """
    
    def __init__(self, warehouse_template: WarehouseTemplate, evolution_threshold: float = 0.7):
        """
        Initialize evolution tracker for a specific warehouse template
        
        Args:
            warehouse_template: The template to monitor for format evolution
            evolution_threshold: Minimum confidence to trigger evolution detection
        """
        self.template = warehouse_template
        self.evolution_threshold = evolution_threshold
        self.detector = SmartFormatDetector()
        
        # Get current format configuration
        self.current_format = warehouse_template.get_location_format_config() if warehouse_template else {}
        self.current_pattern = self.current_format.get('pattern_type', 'unknown')
        
        logger.info(f"FormatEvolutionTracker initialized for template '{warehouse_template.name if warehouse_template else 'Unknown'}' "
                   f"with pattern '{self.current_pattern}'")
    
    def check_for_evolution(self, location_codes: List[str], report_id: Optional[int] = None) -> List[FormatEvolutionCandidate]:
        """
        Check if location codes contain evolution patterns
        
        Args:
            location_codes: List of location codes from inventory upload
            report_id: Optional report ID that triggered this check
            
        Returns:
            List of evolution candidates found
        """
        if not location_codes or not self.template:
            return []
        
        # Clean and deduplicate location codes
        clean_locations = self._clean_location_codes(location_codes)
        
        if len(clean_locations) < 3:
            logger.debug("Insufficient location codes for evolution detection")
            return []
        
        logger.info(f"Checking {len(clean_locations)} locations for format evolution")
        
        evolution_candidates = []
        
        # 1. Check for new patterns that don't match current format
        new_pattern_candidates = self._detect_new_patterns(clean_locations)
        evolution_candidates.extend(new_pattern_candidates)
        
        # 2. Check for format drift in existing patterns
        if self.current_format:
            drift_candidates = self._detect_format_drift(clean_locations)
            evolution_candidates.extend(drift_candidates)
        
        # 3. Check for new special location patterns
        special_candidates = self._detect_special_locations(clean_locations)
        evolution_candidates.extend(special_candidates)
        
        # Log evolution candidates
        if evolution_candidates:
            logger.info(f"Found {len(evolution_candidates)} format evolution candidates")
            for candidate in evolution_candidates:
                logger.info(f"  - {candidate.change_type}: {candidate.change_description} "
                           f"(confidence: {candidate.confidence_score:.1%}, affects {candidate.affected_count} locations)")
        
        # Store significant evolution candidates in database
        self._store_evolution_candidates(evolution_candidates, report_id)
        
        return evolution_candidates
    
    def _clean_location_codes(self, location_codes: List[str]) -> List[str]:
        """Clean and prepare location codes for analysis"""
        clean_codes = []
        seen = set()
        
        for code in location_codes:
            if not isinstance(code, str):
                continue
            
            clean_code = str(code).strip().upper()
            if clean_code and clean_code not in seen and len(clean_code) <= 50:  # Reasonable length limit
                clean_codes.append(clean_code)
                seen.add(clean_code)
        
        return clean_codes[:500]  # Limit sample size for performance
    
    def _detect_new_patterns(self, location_codes: List[str]) -> List[FormatEvolutionCandidate]:
        """Detect completely new location patterns"""
        candidates = []
        
        try:
            # Use SmartFormatDetector to analyze all locations
            detection_result = self.detector.detect_format(location_codes)
            
            if not detection_result.get('detected_pattern'):
                return candidates
            
            detected_pattern = detection_result['detected_pattern']
            detected_type = detected_pattern.get('pattern_type')
            confidence = detected_pattern.get('confidence', 0)
            
            # Check if this is a new pattern different from current
            if (detected_type != self.current_pattern and 
                confidence >= self.evolution_threshold):
                
                # Count how many locations match the new pattern
                affected_count = self._count_matching_locations(location_codes, detected_pattern)
                
                if affected_count >= 3:  # Minimum threshold for pattern significance
                    candidate = FormatEvolutionCandidate(
                        new_pattern_type=detected_type,
                        confidence_score=confidence,
                        sample_locations=location_codes[:10],  # Sample for user review
                        affected_count=affected_count,
                        original_format=self.current_format,
                        new_format=self.detector.create_format_config(detection_result),
                        change_type='new_pattern',
                        change_description=f"New {detected_type} pattern detected (was {self.current_pattern})"
                    )
                    candidates.append(candidate)
                    logger.info(f"New pattern detected: {detected_type} with {confidence:.1%} confidence")
            
        except Exception as e:
            logger.error(f"Error detecting new patterns: {e}")
        
        return candidates
    
    def _detect_format_drift(self, location_codes: List[str]) -> List[FormatEvolutionCandidate]:
        """Detect drift in existing format patterns"""
        candidates = []
        
        if not self.current_format:
            return candidates
        
        try:
            # Sample locations that don't match current pattern
            current_regex = self.current_format.get('regex_pattern', '')
            if not current_regex:
                return candidates
            
            non_matching = []
            for code in location_codes:
                if not re.match(current_regex, code):
                    non_matching.append(code)
            
            # If we have enough non-matching locations, analyze them
            if len(non_matching) >= 5 and len(non_matching) / len(location_codes) > 0.1:  # >10% drift
                drift_result = self.detector.detect_format(non_matching)
                
                if drift_result.get('detected_pattern'):
                    detected = drift_result['detected_pattern']
                    confidence = detected.get('confidence', 0)
                    
                    if confidence >= self.evolution_threshold:
                        candidate = FormatEvolutionCandidate(
                            new_pattern_type=detected.get('pattern_type'),
                            confidence_score=confidence,
                            sample_locations=non_matching[:10],
                            affected_count=len(non_matching),
                            original_format=self.current_format,
                            new_format=self.detector.create_format_config(drift_result),
                            change_type='format_drift',
                            change_description=f"Format drift detected in {self.current_pattern} pattern"
                        )
                        candidates.append(candidate)
                        logger.info(f"Format drift detected: {len(non_matching)} locations don't match current pattern")
        
        except Exception as e:
            logger.error(f"Error detecting format drift: {e}")
        
        return candidates
    
    def _detect_special_locations(self, location_codes: List[str]) -> List[FormatEvolutionCandidate]:
        """Detect new special location patterns"""
        candidates = []
        
        try:
            # Look for potential special location patterns
            special_patterns = [
                r'^(RECV|RECEIVING|DOCK|STAGE|STAGING|SHIP|SHIPPING|QC|QUALITY|DAMAGE|HOLD)-?\d*$',
                r'^(TEMP|TEMPORARY|TRANSIT|TRANSFER|MOVE|OVERFLOW|BULK)-?\d*$',
                r'^(A|B|C|D|E|F)\d{1,3}$',  # Simple aisle codes
                r'^(ZONE|AREA|SECTION)-?[A-Z\d]+$'
            ]
            
            special_locations = []
            for code in location_codes:
                for pattern in special_patterns:
                    if re.match(pattern, code, re.IGNORECASE):
                        special_locations.append(code.upper())
                        break
            
            # Check if we have enough special locations to warrant a pattern
            if len(special_locations) >= 3:
                # Check if these are new (not in current format special locations)
                current_special = self.current_format.get('special_locations', {})
                existing_patterns = current_special.get('patterns', [])
                
                # Simple check - if we have special locations but no existing patterns, it's new
                if not existing_patterns or len(special_locations) > len(existing_patterns) * 2:
                    candidate = FormatEvolutionCandidate(
                        new_pattern_type='special',
                        confidence_score=0.8,  # High confidence for special patterns
                        sample_locations=special_locations[:10],
                        affected_count=len(special_locations),
                        original_format=self.current_format,
                        new_format={**self.current_format, 'special_locations': {'patterns': special_patterns[:2]}},
                        change_type='special_locations',
                        change_description=f"New special location patterns detected ({len(special_locations)} locations)"
                    )
                    candidates.append(candidate)
                    logger.info(f"Special location patterns detected: {len(special_locations)} locations")
        
        except Exception as e:
            logger.error(f"Error detecting special locations: {e}")
        
        return candidates
    
    def _count_matching_locations(self, location_codes: List[str], pattern_config: Dict) -> int:
        """Count how many locations match a given pattern configuration"""
        try:
            regex_pattern = pattern_config.get('regex_pattern', '')
            if not regex_pattern:
                return 0
            
            count = 0
            for code in location_codes:
                if re.match(regex_pattern, code):
                    count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error counting matching locations: {e}")
            return 0
    
    def _store_evolution_candidates(self, candidates: List[FormatEvolutionCandidate], report_id: Optional[int]):
        """Store evolution candidates in database for user review"""
        if not candidates or not self.template:
            return
        
        try:
            for candidate in candidates:
                # Only store significant candidates
                if candidate.confidence_score >= self.evolution_threshold and candidate.affected_count >= 3:
                    
                    # Check if similar evolution already exists and is pending
                    existing = LocationFormatHistory.query.filter_by(
                        warehouse_template_id=self.template.id,
                        user_confirmed=False,
                        pattern_change_type=candidate.change_type
                    ).filter(
                        LocationFormatHistory.reviewed_at.is_(None)
                    ).first()
                    
                    if existing:
                        logger.debug(f"Similar evolution candidate already pending for template {self.template.id}")
                        continue
                    
                    # Create new evolution record
                    evolution = LocationFormatHistory(
                        warehouse_template_id=self.template.id,
                        confidence_score=candidate.confidence_score,
                        pattern_change_type=candidate.change_type,
                        affected_location_count=candidate.affected_count,
                        trigger_report_id=report_id
                    )
                    
                    evolution.set_original_format(candidate.original_format)
                    evolution.set_new_format(candidate.new_format)
                    evolution.set_sample_locations(candidate.sample_locations)
                    
                    db.session.add(evolution)
                    logger.info(f"Stored evolution candidate: {candidate.change_type} for template {self.template.id}")
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error storing evolution candidates: {e}")
            db.session.rollback()
    
    def get_pending_evolutions(self) -> List[LocationFormatHistory]:
        """Get pending format evolutions for this template"""
        if not self.template:
            return []
        
        return LocationFormatHistory.query.filter_by(
            warehouse_template_id=self.template.id,
            user_confirmed=False
        ).filter(
            LocationFormatHistory.reviewed_at.is_(None)
        ).order_by(LocationFormatHistory.detected_at.desc()).all()
    
    def apply_evolution(self, evolution_id: int, user_id: int, confirmed: bool) -> bool:
        """Apply or reject a format evolution"""
        try:
            evolution = LocationFormatHistory.query.get(evolution_id)
            if not evolution or evolution.warehouse_template_id != self.template.id:
                return False
            
            if confirmed:
                evolution.confirm_change(user_id)
                logger.info(f"Applied format evolution {evolution_id} for template {self.template.id}")
            else:
                evolution.reject_change(user_id)
                logger.info(f"Rejected format evolution {evolution_id} for template {self.template.id}")
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error applying evolution {evolution_id}: {e}")
            db.session.rollback()
            return False


# Convenience functions for easy integration

def check_format_evolution(warehouse_template: WarehouseTemplate, location_codes: List[str], 
                          report_id: Optional[int] = None) -> List[FormatEvolutionCandidate]:
    """
    Convenience function to check for format evolution
    
    Args:
        warehouse_template: Template to check for evolution
        location_codes: Location codes from inventory upload
        report_id: Optional report ID that triggered this check
        
    Returns:
        List of evolution candidates found
    """
    tracker = FormatEvolutionTracker(warehouse_template)
    return tracker.check_for_evolution(location_codes, report_id)


def get_pending_format_evolutions(user_id: int) -> List[Dict]:
    """
    Get all pending format evolutions for a user's templates
    
    Args:
        user_id: User ID to get evolutions for
        
    Returns:
        List of pending evolution data
    """
    try:
        # Get user's templates
        from models import WarehouseTemplate
        user_templates = WarehouseTemplate.query.filter_by(created_by=user_id, is_active=True).all()
        
        pending_evolutions = []
        for template in user_templates:
            evolutions = LocationFormatHistory.query.filter_by(
                warehouse_template_id=template.id,
                user_confirmed=False
            ).filter(
                LocationFormatHistory.reviewed_at.is_(None)
            ).order_by(LocationFormatHistory.detected_at.desc()).all()
            
            for evolution in evolutions:
                pending_evolutions.append(evolution.to_dict())
        
        return pending_evolutions
        
    except Exception as e:
        logger.error(f"Error getting pending evolutions for user {user_id}: {e}")
        return []


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    print("Format Evolution Tracker - Smart Configuration System")
    print("This module monitors location format changes during inventory uploads")