#!/usr/bin/env python3
"""
Template-Based Invalid Location Evaluator
Dynamic, template-driven replacement for hardcoded location validation

ARCHITECTURAL SOLUTION:
- Replaces hardcoded validation rules with dynamic template-based validation
- Uses warehouse_context to resolve actual warehouse configuration
- Validates against real template dimensions instead of static limits
- Supports multiple warehouse layouts without code changes

This evaluator solves the core issue: 
Backend validates against 29 positions while template defines 46 positions
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from rule_engine import BaseRuleEvaluator, Rule

logger = logging.getLogger(__name__)

class TemplateBasedInvalidLocationEvaluator(BaseRuleEvaluator):
    """
    REFACTORED: Template-aware invalid location evaluator
    
    KEY IMPROVEMENT:
    Instead of hardcoded validation rules, this evaluator:
    1. Resolves warehouse_context → actual template configuration
    2. Creates VirtualLocationEngine with correct template dimensions  
    3. Validates locations against template-specific constraints
    4. Adapts automatically to different warehouse layouts
    
    SOLVES:
    - Frontend shows 46 positions, backend validates against 29 positions
    - System cannot handle multiple warehouse types
    - Validation rules hardcoded instead of template-driven
    """
    
    def __init__(self, app=None, db_session=None):
        """
        Initialize template-based invalid location evaluator
        
        Args:
            app: Flask application instance (for compatibility)
            db_session: Database session for template resolution
        """
        super().__init__()
        self.app = app
        self.db_session = db_session
        
        # Initialize template resolution system
        try:
            from warehouse_template_resolver import get_validator_factory
            self.validator_factory = get_validator_factory(db_session)
            self.template_resolution_available = True
            logger.info("[TEMPLATE_INVALID_LOCATION] Template resolution system initialized")
        except ImportError as e:
            logger.error(f"[TEMPLATE_INVALID_LOCATION] Template resolution unavailable: {e}")
            self.template_resolution_available = False
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        """
        CORE METHOD: Template-based invalid location evaluation
        
        DYNAMIC RESOLUTION FLOW:
        1. Extract warehouse_id from warehouse_context
        2. Resolve warehouse_id → template configuration
        3. Create VirtualLocationEngine with template dimensions
        4. Validate inventory locations against template constraints
        5. Generate anomalies for locations that violate template rules
        
        Args:
            rule: Rule definition with conditions
            inventory_df: Inventory DataFrame with location column
            warehouse_context: Context containing warehouse_id
            
        Returns:
            List of invalid location anomalies
        """
        if not self.template_resolution_available:
            logger.error("[TEMPLATE_INVALID_LOCATION] Template resolution system not available")
            return self._fallback_evaluation(rule, inventory_df, warehouse_context)
        
        warehouse_id = warehouse_context.get('warehouse_id') if warehouse_context else None
        
        logger.info(f"[TEMPLATE_INVALID_LOCATION] Starting template-based evaluation for warehouse: {warehouse_id}")
        
        if not warehouse_id:
            logger.warning("[TEMPLATE_INVALID_LOCATION] No warehouse_id provided, cannot resolve template")
            return self._fallback_evaluation(rule, inventory_df, warehouse_context)
        
        try:
            return self._evaluate_with_template_resolution(rule, inventory_df, warehouse_context)
        except Exception as e:
            logger.error(f"[TEMPLATE_INVALID_LOCATION] Template evaluation failed: {e}")
            logger.info("[TEMPLATE_INVALID_LOCATION] Falling back to basic evaluation")
            return self._fallback_evaluation(rule, inventory_df, warehouse_context)
    
    def _evaluate_with_template_resolution(self, rule: Rule, inventory_df: pd.DataFrame, 
                                         warehouse_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        ENHANCED: Perform template-based location validation
        
        TEMPLATE RESOLUTION PROCESS:
        1. warehouse_context['warehouse_id'] → WarehouseTemplateResolver
        2. Resolver queries database OR uses pattern matching
        3. Returns warehouse configuration (dimensions, capacities, etc.)
        4. VirtualLocationEngine validates against template rules
        5. Invalid locations flagged based on actual template constraints
        """
        warehouse_id = warehouse_context.get('warehouse_id')
        
        # Step 1: Create template-aware virtual engine
        logger.info(f"[TEMPLATE_INVALID_LOCATION] Resolving template for warehouse: {warehouse_id}")
        
        virtual_engine = self.validator_factory.create_virtual_engine(warehouse_context)
        
        # Log resolved template information for debugging
        if hasattr(virtual_engine, '_template_resolution'):
            resolution = virtual_engine._template_resolution
            logger.info(f"[TEMPLATE_INVALID_LOCATION] Template resolved via: {resolution.resolution_method}")
            logger.info(f"[TEMPLATE_INVALID_LOCATION] Confidence: {resolution.confidence}")
            logger.info(f"[TEMPLATE_INVALID_LOCATION] Source: {resolution.template_source}")
        
        # Log template dimensions for verification
        warehouse_summary = virtual_engine.get_warehouse_summary()
        dimensions = warehouse_summary['warehouse_dimensions']
        logger.info(f"[TEMPLATE_INVALID_LOCATION] Template dimensions: {dimensions['aisles']}×{dimensions['racks_per_aisle']}×{dimensions['positions_per_rack']}×{dimensions['levels_per_position']}")
        logger.info(f"[TEMPLATE_INVALID_LOCATION] Total storage locations: {warehouse_summary['storage_locations']:,}")
        
        # Step 2: Get unique locations from inventory
        if 'location' not in inventory_df.columns:
            logger.warning("[TEMPLATE_INVALID_LOCATION] No location column in inventory")
            return []
        
        unique_locations = list(set(inventory_df['location'].dropna().astype(str)))
        logger.info(f"[TEMPLATE_INVALID_LOCATION] Validating {len(unique_locations)} unique locations")
        
        # Step 3: Batch validate locations against template
        invalid_locations = []
        validation_stats = {'valid': 0, 'invalid': 0, 'empty': 0}
        
        for location in unique_locations:
            location_str = str(location).strip()
            
            if not location_str or location_str.lower() in ['nan', 'none', '']:
                validation_stats['empty'] += 1
                continue
            
            # CORE VALIDATION: Use template-specific rules
            is_valid, reason = virtual_engine.validate_location(location_str)
            
            if is_valid:
                validation_stats['valid'] += 1
                logger.debug(f"[TEMPLATE_INVALID_LOCATION] Valid: {location_str}")
            else:
                validation_stats['invalid'] += 1
                invalid_locations.append({
                    'location_code': location_str,
                    'reason': reason,
                    'template_validation': True
                })
                logger.debug(f"[TEMPLATE_INVALID_LOCATION] Invalid: {location_str} → {reason}")
        
        # Log validation statistics
        logger.info(f"[TEMPLATE_INVALID_LOCATION] Validation complete:")
        logger.info(f"  Valid locations: {validation_stats['valid']}")
        logger.info(f"  Invalid locations: {validation_stats['invalid']}")
        logger.info(f"  Empty/null locations: {validation_stats['empty']}")
        
        # Step 4: Generate anomalies for invalid locations
        anomalies = []
        invalid_location_codes = {invalid['location_code'] for invalid in invalid_locations}
        
        for _, pallet in inventory_df.iterrows():
            location = str(pallet['location']).strip()
            
            # Skip empty/null locations (handled by MISSING_LOCATION rule)
            if pd.isna(pallet['location']) or not location or location.lower() in ['nan', 'none', '']:
                continue
            
            if location in invalid_location_codes:
                # Get detailed validation info
                validation_detail = next(
                    (invalid for invalid in invalid_locations if invalid['location_code'] == location),
                    {'reason': 'unknown_validation_error', 'template_validation': False}
                )
                
                # Create anomaly with template-specific details
                anomaly = {
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Invalid Location',
                    'priority': rule.priority,
                    'details': self._create_template_specific_message(
                        location, validation_detail, warehouse_summary
                    )
                }
                
                anomalies.append(anomaly)
        
        logger.info(f"[TEMPLATE_INVALID_LOCATION] Generated {len(anomalies)} template-based anomalies")
        
        # DIAGNOSTIC: Log comparison with old system would detect
        if logger.isEnabledFor(logging.DEBUG):
            self._log_validation_diagnostics(warehouse_id, validation_stats, warehouse_summary)
        
        return anomalies
    
    def _create_template_specific_message(self, location: str, validation_detail: Dict[str, Any], 
                                        warehouse_summary: Dict[str, Any]) -> str:
        """
        Create detailed, template-specific error message
        
        IMPROVEMENT: Instead of generic "not found in database", provide specific
        template constraint violations (e.g., "Position 47 exceeds template limit 46")
        """
        reason = validation_detail.get('reason', 'unknown')
        dimensions = warehouse_summary['warehouse_dimensions']
        
        base_message = f"Location '{location}' is invalid"
        
        # Parse specific template constraint violations
        if 'exceeds' in reason.lower():
            template_info = f" (Template: {dimensions['aisles']}×{dimensions['racks_per_aisle']}×{dimensions['positions_per_rack']}×{dimensions['levels_per_position']})"
            return f"{base_message}: {reason}{template_info}"
        elif 'format' in reason.lower():
            return f"{base_message}: {reason}"
        else:
            return f"{base_message}: {reason} (Template: {warehouse_summary['warehouse_id']})"
    
    def _log_validation_diagnostics(self, warehouse_id: str, validation_stats: Dict[str, int], 
                                  warehouse_summary: Dict[str, Any]) -> None:
        """Log diagnostic information for system monitoring"""
        logger.debug(f"[TEMPLATE_INVALID_LOCATION] DIAGNOSTICS for {warehouse_id}:")
        logger.debug(f"  Template source: {getattr(self.validator_factory, '_template_resolution', {}).get('resolution_method', 'unknown')}")
        logger.debug(f"  Template dimensions: {warehouse_summary['warehouse_dimensions']}")
        logger.debug(f"  Validation coverage: {validation_stats['valid']}/{validation_stats['valid'] + validation_stats['invalid']} locations valid")
        logger.debug(f"  Template capacity: {warehouse_summary['storage_locations']:,} storage + {warehouse_summary['special_areas']} special")
    
    def _fallback_evaluation(self, rule: Rule, inventory_df: pd.DataFrame, 
                           warehouse_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        FALLBACK: Basic location validation when template resolution fails
        
        This provides minimal validation without template-specific constraints.
        Uses pattern matching to identify obviously invalid locations.
        """
        logger.warning("[TEMPLATE_INVALID_LOCATION] Using fallback validation - reduced accuracy expected")
        
        anomalies = []
        
        if 'location' not in inventory_df.columns:
            return anomalies
        
        # Basic pattern-based validation (no template constraints)
        for _, pallet in inventory_df.iterrows():
            location = str(pallet['location']).strip()
            
            # Skip empty/null
            if pd.isna(pallet['location']) or not location or location.lower() in ['nan', 'none', '']:
                continue
            
            # Basic invalid patterns (obvious cases only)
            if self._is_obviously_invalid_location(location):
                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Invalid Location',
                    'priority': rule.priority,
                    'details': f"Location '{location}' has invalid format (fallback validation - template constraints not checked)"
                })
        
        logger.warning(f"[TEMPLATE_INVALID_LOCATION] Fallback validation found {len(anomalies)} obvious anomalies")
        logger.warning("[TEMPLATE_INVALID_LOCATION] Template-specific constraints not enforced - consider fixing template resolution")
        
        return anomalies
    
    def _is_obviously_invalid_location(self, location: str) -> bool:
        """
        Basic pattern matching for obviously invalid locations
        
        This catches only the most obvious cases without template knowledge:
        - Special characters that are never valid
        - Impossibly long location codes  
        - Common error patterns
        """
        import re
        
        # Obviously invalid patterns
        invalid_patterns = [
            r'^[!@#$%^&*()]+',  # Starts with special characters
            r'.{50,}',          # Impossibly long (50+ characters)
            r'^ERROR',          # Error prefixes
            r'^INVALID',        # Invalid prefixes  
            r'^UNDEFINED',      # Undefined prefixes
            r'^TEMP',           # Temporary prefixes (often test data)
            r'GHOST',           # Ghost locations
        ]
        
        location_upper = location.upper()
        
        for pattern in invalid_patterns:
            if re.search(pattern, location_upper):
                return True
        
        return False


# INTEGRATION FUNCTIONS for existing rule engine

def create_template_based_invalid_location_evaluator(app=None, db_session=None):
    """
    Factory function to create template-based invalid location evaluator
    
    This can be used to replace the existing InvalidLocationEvaluator in the rule engine
    """
    return TemplateBasedInvalidLocationEvaluator(app, db_session)

def get_evaluator_replacement_info() -> Dict[str, Any]:
    """
    Get information about replacing the existing evaluator
    
    Returns guidance for integrating this evaluator into the rule engine
    """
    return {
        'old_evaluator': 'InvalidLocationEvaluator',
        'new_evaluator': 'TemplateBasedInvalidLocationEvaluator',
        'replacement_method': 'create_template_based_invalid_location_evaluator',
        'benefits': [
            'Dynamic template-based validation',
            'Supports multiple warehouse layouts',
            'Resolves hardcoded dimension constraints',
            'Automatic adaptation to template changes'
        ],
        'integration_steps': [
            '1. Import template_based_invalid_location_evaluator',
            '2. Replace InvalidLocationEvaluator initialization with create_template_based_invalid_location_evaluator()',
            '3. Ensure warehouse_context includes warehouse_id in rule evaluation',
            '4. Test with different warehouse templates'
        ],
        'compatibility': 'Full backward compatibility with existing Rule and BaseRuleEvaluator interfaces'
    }

# DIAGNOSTIC FUNCTIONS

def test_template_resolution_for_warehouse(warehouse_id: str, db_session=None) -> Dict[str, Any]:
    """
    Test template resolution for a specific warehouse
    
    Useful for debugging template resolution issues
    """
    try:
        from warehouse_template_resolver import diagnose_warehouse_template_resolution
        return diagnose_warehouse_template_resolution(warehouse_id, db_session)
    except ImportError:
        return {
            'error': 'warehouse_template_resolver module not available',
            'recommendation': 'Ensure warehouse_template_resolver.py is in the same directory'
        }

def compare_validation_approaches(inventory_df: pd.DataFrame, warehouse_context: Dict[str, Any], 
                                db_session=None) -> Dict[str, Any]:
    """
    Compare template-based validation vs fallback validation
    
    Useful for measuring the impact of template-based validation
    """
    results = {
        'comparison_timestamp': pd.Timestamp.now().isoformat(),
        'warehouse_context': warehouse_context,
        'inventory_stats': {
            'total_pallets': len(inventory_df),
            'unique_locations': len(set(inventory_df['location'].dropna().astype(str)))
        }
    }
    
    # Test template-based validation
    try:
        template_evaluator = TemplateBasedInvalidLocationEvaluator(db_session=db_session)
        from rule_engine import Rule
        test_rule = Rule(name='test', rule_type='INVALID_LOCATION', priority=1, conditions='{}')
        
        template_anomalies = template_evaluator._evaluate_with_template_resolution(
            test_rule, inventory_df, warehouse_context
        )
        
        results['template_validation'] = {
            'status': 'SUCCESS',
            'anomalies_found': len(template_anomalies),
            'sample_anomalies': template_anomalies[:3]  # First 3 for inspection
        }
    except Exception as e:
        results['template_validation'] = {
            'status': 'FAILED',
            'error': str(e)
        }
    
    # Test fallback validation
    try:
        fallback_anomalies = template_evaluator._fallback_evaluation(
            test_rule, inventory_df, warehouse_context
        )
        
        results['fallback_validation'] = {
            'status': 'SUCCESS',
            'anomalies_found': len(fallback_anomalies),
            'sample_anomalies': fallback_anomalies[:3]
        }
    except Exception as e:
        results['fallback_validation'] = {
            'status': 'FAILED',
            'error': str(e)
        }
    
    # Calculate impact
    if results['template_validation']['status'] == 'SUCCESS' and results['fallback_validation']['status'] == 'SUCCESS':
        template_count = results['template_validation']['anomalies_found']
        fallback_count = results['fallback_validation']['anomalies_found']
        
        results['impact_analysis'] = {
            'template_based_anomalies': template_count,
            'fallback_anomalies': fallback_count,
            'difference': template_count - fallback_count,
            'accuracy_improvement': f"{abs(template_count - fallback_count)} anomalies difference",
            'recommendation': 'Template-based validation provides more accurate results' if template_count != fallback_count else 'Both methods produce similar results'
        }
    
    return results