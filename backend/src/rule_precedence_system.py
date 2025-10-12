#!/usr/bin/env python3
"""
Rule Precedence System - Eliminates double-counting between rules

This module implements a precedence-based exclusion system that prevents
the same pallet from being flagged by multiple rules when one rule has
higher business logic precedence than another.

Key Classes:
- PalletExclusionRegistry: Tracks which pallets have been flagged by rules
- RulePrecedenceManager: Manages rule precedence and exclusion logic
"""

from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class ExclusionRecord:
    """Record of a pallet being excluded by a rule"""
    pallet_id: str
    rule_id: int
    rule_name: str
    rule_type: str
    precedence_level: int
    timestamp: datetime
    reason: str

class PalletExclusionRegistry:
    """
    Registry that tracks which pallets have been flagged by higher-precedence rules
    and should be excluded from evaluation by lower-precedence rules.
    """
    
    def __init__(self):
        self.exclusions: Dict[str, List[ExclusionRecord]] = {}  # pallet_id -> list of exclusion records
        self.stats = {
            'total_exclusions': 0,
            'rules_with_exclusions': set(),
            'exclusions_by_rule_type': {}
        }
    
    def add_exclusion(self, pallet_id: str, rule_id: int, rule_name: str, 
                     rule_type: str, precedence_level: int, reason: str = None):
        """Add a pallet to the exclusion registry"""
        if not pallet_id:
            return
        
        exclusion = ExclusionRecord(
            pallet_id=pallet_id,
            rule_id=rule_id,
            rule_name=rule_name,
            rule_type=rule_type,
            precedence_level=precedence_level,
            timestamp=datetime.now(),
            reason=reason or f"Flagged by {rule_name}"
        )
        
        if pallet_id not in self.exclusions:
            self.exclusions[pallet_id] = []
        
        self.exclusions[pallet_id].append(exclusion)
        
        # Update stats
        self.stats['total_exclusions'] += 1
        self.stats['rules_with_exclusions'].add(rule_type)
        if rule_type not in self.stats['exclusions_by_rule_type']:
            self.stats['exclusions_by_rule_type'][rule_type] = 0
        self.stats['exclusions_by_rule_type'][rule_type] += 1
        
        logger.debug(f"Added exclusion: {pallet_id} excluded by {rule_name} (precedence {precedence_level})")
    
    def is_excluded(self, pallet_id: str, requesting_rule_precedence: int, 
                   requesting_rule_type: str = None) -> bool:
        """Check if a pallet is excluded from evaluation by a requesting rule"""
        if not pallet_id or pallet_id not in self.exclusions:
            return False
        
        # Check if any exclusion has higher precedence (lower number = higher precedence)
        for exclusion in self.exclusions[pallet_id]:
            if exclusion.precedence_level < requesting_rule_precedence:
                logger.debug(f"Pallet {pallet_id} excluded from {requesting_rule_type} "
                           f"(precedence {requesting_rule_precedence}) by {exclusion.rule_name} "
                           f"(precedence {exclusion.precedence_level})")
                return True
        
        return False
    
    def get_exclusion_reason(self, pallet_id: str, requesting_rule_precedence: int) -> Optional[str]:
        """Get the reason why a pallet is excluded"""
        if not self.is_excluded(pallet_id, requesting_rule_precedence):
            return None
        
        # Find the highest precedence exclusion (lowest number)
        highest_precedence_exclusion = None
        for exclusion in self.exclusions[pallet_id]:
            if exclusion.precedence_level < requesting_rule_precedence:
                if (highest_precedence_exclusion is None or 
                    exclusion.precedence_level < highest_precedence_exclusion.precedence_level):
                    highest_precedence_exclusion = exclusion
        
        if highest_precedence_exclusion:
            return (f"Excluded by {highest_precedence_exclusion.rule_name} "
                   f"({highest_precedence_exclusion.reason})")
        
        return "Excluded by higher precedence rule"
    
    def get_exclusions_for_pallet(self, pallet_id: str) -> List[ExclusionRecord]:
        """Get all exclusion records for a specific pallet"""
        return self.exclusions.get(pallet_id, [])
    
    def get_exclusion_stats(self) -> Dict[str, Any]:
        """Get statistics about exclusions"""
        return {
            'total_exclusions': self.stats['total_exclusions'],
            'unique_pallets_excluded': len(self.exclusions),
            'rules_with_exclusions': len(self.stats['rules_with_exclusions']),
            'exclusions_by_rule_type': dict(self.stats['exclusions_by_rule_type'])
        }
    
    def clear(self):
        """Clear all exclusions (for new evaluation cycle)"""
        self.exclusions.clear()
        self.stats = {
            'total_exclusions': 0,
            'rules_with_exclusions': set(),
            'exclusions_by_rule_type': {}
        }

class RulePrecedenceManager:
    """
    Manages rule precedence logic and exclusion patterns.
    Determines which pallets should be excluded from rule evaluation.
    """
    
    def __init__(self, enable_precedence: bool = True):
        self.enable_precedence = enable_precedence
        self.registry = PalletExclusionRegistry()
        
        # Default exclusion patterns - can be overridden by rule-specific exclusion_rules
        self.default_exclusion_patterns = {
            'OVERCAPACITY': {
                'exclude_if_flagged_by': ['INVALID_LOCATION', 'DATA_INTEGRITY'],
                'reason': 'Invalid locations cannot have capacity constraints'
            },
            'LOCATION_MAPPING_ERROR': {
                'exclude_if_flagged_by': ['INVALID_LOCATION'],
                'reason': 'Invalid locations already flagged for location issues'
            },
            'TEMPERATURE_ZONE_MISMATCH': {
                'exclude_if_flagged_by': ['INVALID_LOCATION'],
                'reason': 'Invalid locations cannot have zone constraints'
            }
        }
    
    def sort_rules_by_precedence(self, rules: List[Any]) -> List[Any]:
        """Sort rules by precedence level (lower number = higher precedence)"""
        if not self.enable_precedence:
            return rules
        
        return sorted(rules, key=lambda rule: (
            getattr(rule, 'precedence_level', 4),  # Primary: precedence level
            rule.id  # Secondary: rule ID for consistent ordering
        ))
    
    def should_exclude_pallet(self, pallet_id: str, rule: Any, anomaly_data: Dict[str, Any] = None) -> bool:
        """
        Determine if a pallet should be excluded from evaluation by the given rule.
        
        Args:
            pallet_id: The pallet to check
            rule: The rule requesting evaluation
            anomaly_data: Optional anomaly data for context-aware exclusion
            
        Returns:
            True if pallet should be excluded, False otherwise
        """
        if not self.enable_precedence:
            return False
        
        if not pallet_id or not rule:
            return False
        
        rule_precedence = getattr(rule, 'precedence_level', 4)
        rule_type = getattr(rule, 'rule_type', '')
        
        # Check registry for higher-precedence exclusions
        if self.registry.is_excluded(pallet_id, rule_precedence, rule_type):
            return True
        
        # Check rule-specific exclusion patterns
        exclusion_rules = getattr(rule, 'get_exclusion_rules', lambda: {})()
        if exclusion_rules and 'exclude_if_flagged_by' in exclusion_rules:
            target_rule_types = exclusion_rules['exclude_if_flagged_by']
            
            # Check if pallet was flagged by any of the target rule types
            for exclusion in self.registry.get_exclusions_for_pallet(pallet_id):
                if exclusion.rule_type in target_rule_types:
                    logger.debug(f"Pallet {pallet_id} excluded from {rule_type} by rule-specific pattern")
                    return True
        
        # Check default exclusion patterns
        elif rule_type in self.default_exclusion_patterns:
            pattern = self.default_exclusion_patterns[rule_type]
            target_rule_types = pattern['exclude_if_flagged_by']
            
            for exclusion in self.registry.get_exclusions_for_pallet(pallet_id):
                if exclusion.rule_type in target_rule_types:
                    logger.debug(f"Pallet {pallet_id} excluded from {rule_type} by default pattern")
                    return True
        
        return False
    
    def register_anomalies(self, rule: Any, anomalies: List[Dict[str, Any]]):
        """Register anomalies in the exclusion registry for subsequent rules to check"""
        if not self.enable_precedence or not anomalies:
            return
        
        rule_id = getattr(rule, 'id', 0)
        rule_name = getattr(rule, 'name', 'Unknown Rule')
        rule_type = getattr(rule, 'rule_type', 'UNKNOWN')
        precedence_level = getattr(rule, 'precedence_level', 4)
        
        for anomaly in anomalies:
            pallet_id = anomaly.get('pallet_id')
            # Handle pandas Series or scalar values
            if pallet_id is not None and str(pallet_id).strip():
                reason = f"Flagged as {anomaly.get('anomaly_type', 'anomaly')}"
                # Convert to string to handle pandas Series or other types
                pallet_id_str = str(pallet_id)
                self.registry.add_exclusion(
                    pallet_id=pallet_id_str,
                    rule_id=rule_id,
                    rule_name=rule_name,
                    rule_type=rule_type,
                    precedence_level=precedence_level,
                    reason=reason
                )
    
    def get_exclusion_summary(self) -> Dict[str, Any]:
        """Get summary of exclusions for logging and debugging"""
        stats = self.registry.get_exclusion_stats()
        
        return {
            'precedence_enabled': self.enable_precedence,
            'exclusion_stats': stats,
            'default_patterns_count': len(self.default_exclusion_patterns)
        }
    
    def reset_for_new_evaluation(self):
        """Reset the registry for a new rule evaluation cycle"""
        self.registry.clear()

# Configuration management
def get_precedence_config() -> Dict[str, Any]:
    """Get precedence system configuration from environment variables and defaults"""
    import os
    
    config = {
        'enable_precedence': True,  # Default enabled
        'debug_logging': False,
        'exclusion_patterns_enabled': True
    }
    
    # Check environment variables for overrides
    env_enabled = os.getenv('RULE_PRECEDENCE_ENABLED', '').lower()
    if env_enabled in ['false', 'f', '0', 'no', 'off', 'disabled']:
        config['enable_precedence'] = False
    elif env_enabled in ['true', 't', '1', 'yes', 'on', 'enabled']:
        config['enable_precedence'] = True
    
    env_debug = os.getenv('RULE_PRECEDENCE_DEBUG', '').lower()
    if env_debug in ['true', 't', '1', 'yes', 'on']:
        config['debug_logging'] = True
    
    return config

def set_global_precedence_config(**kwargs):
    """Set global precedence configuration (for testing and admin control)"""
    global _global_precedence_config
    _global_precedence_config = kwargs

# Global config storage
_global_precedence_config = {}

# Utility functions for integration
def create_precedence_manager(enable_precedence: bool = None) -> RulePrecedenceManager:
    """Factory function to create a precedence manager with system settings"""
    
    # Priority order: explicit parameter > global config > environment > default
    if enable_precedence is None:
        if 'enable_precedence' in _global_precedence_config:
            enable_precedence = _global_precedence_config['enable_precedence']
        else:
            config = get_precedence_config()
            enable_precedence = config['enable_precedence']
    
    logger.info(f"Creating precedence manager with precedence_enabled={enable_precedence}")
    return RulePrecedenceManager(enable_precedence=enable_precedence)