"""
Production Rule Engine

Enforces the production workflow:
1. Analysis requires valid template
2. Inventory locations must match template structure  
3. Template validation before rule execution
4. Complete rule results with template context

This ensures rules only run against properly configured warehouses.
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd

from rule_engine import RuleEngine
from production_template_engine import get_production_template_engine
from location_service import get_inventory_validator, get_canonical_service
from models import db

logger = logging.getLogger(__name__)

class ProductionRuleEngine:
    """
    Production rule engine with template validation requirements.
    
    Enforces that rule analysis only runs on properly templated warehouses
    and validates inventory against template structure.
    """
    
    def __init__(self):
        self.template_engine = get_production_template_engine()
        self.rule_engine = RuleEngine(db.session)
        self.inventory_validator = get_inventory_validator()
        self.canonical_service = get_canonical_service()
        logger.info("Production Rule Engine initialized")
    
    def analyze_inventory_production(self, 
                                   inventory_df: pd.DataFrame, 
                                   warehouse_id: str,
                                   validate_template: bool = True) -> Dict:
        """
        Production inventory analysis with template validation.
        
        This is the main entry point for rule analysis in production.
        Enforces the complete workflow validation.
        
        Args:
            inventory_df: Inventory data with 'location' column
            warehouse_id: Target warehouse ID
            validate_template: Whether to enforce template validation (default: True)
            
        Returns:
            Complete analysis results with template context
        """
        try:
            logger.info(f"Starting production inventory analysis for warehouse '{warehouse_id}'")
            
            # Step 1: Template validation (MANDATORY in production)
            if validate_template:
                template_ready, template_message = self.template_engine.is_warehouse_ready_for_analysis(warehouse_id)
                if not template_ready:
                    return {
                        'success': False,
                        'error': f"Template validation failed: {template_message}",
                        'error_type': 'TEMPLATE_NOT_READY',
                        'warehouse_id': warehouse_id,
                        'template_required': True,
                        'message': 'Create and apply a warehouse template before running analysis'
                    }
            
            # Step 2: Inventory validation against template
            location_validation = self._validate_inventory_locations(inventory_df, warehouse_id)
            
            if location_validation['warehouse_coverage'] < 50.0:  # Production threshold
                logger.warning(f"Low location coverage for warehouse '{warehouse_id}': {location_validation['warehouse_coverage']:.1f}%")
            
            # Step 3: Execute rules using validated template
            rule_results = self.rule_engine.evaluate_all_rules(inventory_df, warehouse_id)
            
            # Step 4: Enhance results with template context
            enhanced_results = self._enhance_results_with_template_context(
                rule_results, 
                warehouse_id, 
                location_validation
            )
            
            logger.info(f"Production analysis completed for warehouse '{warehouse_id}': {enhanced_results.get('total_anomalies', 0)} anomalies found")
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Production analysis failed for warehouse '{warehouse_id}': {e}")
            return {
                'success': False,
                'error': f"Analysis failed: {str(e)}",
                'error_type': 'ANALYSIS_ERROR',
                'warehouse_id': warehouse_id
            }
    
    def _validate_inventory_locations(self, inventory_df: pd.DataFrame, warehouse_id: str) -> Dict:
        """Validate inventory locations against warehouse template"""
        try:
            # Note: Column normalization is handled by rule engine's comprehensive _normalize_dataframe_columns()
            # No manual column renaming needed here - the rule engine handles all column variations

            # Run inventory validation
            validation_results = self.inventory_validator.validate_inventory_locations(
                inventory_df, 
                warehouse_id
            )
            
            # Enhance with template-specific insights
            template_context = self._analyze_template_coverage(validation_results, warehouse_id)
            validation_results.update(template_context)
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Inventory validation failed: {e}")
            return {
                'warehouse_coverage': 0.0,
                'valid_locations': {},
                'invalid_locations': [],
                'error': str(e)
            }
    
    def _analyze_template_coverage(self, validation_results: Dict, warehouse_id: str) -> Dict:
        """Analyze how well inventory covers the template structure"""
        try:
            # Get template structure info
            from models import WarehouseConfig
            config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            
            if not config:
                return {'template_analysis': {'error': 'No template configuration found'}}
            
            # Calculate template utilization
            total_valid = len(validation_results['valid_locations'])
            total_invalid = len(validation_results['invalid_locations'])
            
            # Analyze location type distribution
            location_types = {}
            for location_code, location_data in validation_results['valid_locations'].items():
                loc_type = location_data.get('location_object', {}).location_type or 'UNKNOWN'
                location_types[loc_type] = location_types.get(loc_type, 0) + 1
            
            template_analysis = {
                'template_configuration': {
                    'aisles': config.num_aisles,
                    'racks_per_aisle': config.racks_per_aisle,
                    'positions_per_rack': config.positions_per_rack,
                    'levels_per_position': config.levels_per_position,
                    'expected_storage_locations': (config.num_aisles * config.racks_per_aisle * 
                                                 config.positions_per_rack * config.levels_per_position)
                },
                'inventory_utilization': {
                    'valid_locations': total_valid,
                    'invalid_locations': total_invalid,
                    'coverage_percentage': validation_results.get('warehouse_coverage', 0.0),
                    'location_type_distribution': location_types
                },
                'template_readiness': total_valid > 0 and validation_results.get('warehouse_coverage', 0) > 10.0
            }
            
            return {'template_analysis': template_analysis}
            
        except Exception as e:
            logger.error(f"Template coverage analysis failed: {e}")
            return {'template_analysis': {'error': str(e)}}
    
    def _enhance_results_with_template_context(self, 
                                             rule_results: Dict, 
                                             warehouse_id: str, 
                                             location_validation: Dict) -> Dict:
        """Enhance rule results with template and validation context"""
        
        enhanced = {
            'success': True,
            'warehouse_id': warehouse_id,
            'analysis_type': 'PRODUCTION_WITH_TEMPLATE',
            'timestamp': pd.Timestamp.now().isoformat(),
            
            # Original rule results
            'rule_results': rule_results.get('results', {}),
            'total_anomalies': rule_results.get('total_anomalies', 0),
            'rules_executed': len(rule_results.get('results', {})),
            
            # Template validation context
            'template_validation': {
                'coverage_percentage': location_validation.get('warehouse_coverage', 0.0),
                'valid_locations_count': len(location_validation.get('valid_locations', {})),
                'invalid_locations_count': len(location_validation.get('invalid_locations', [])),
                'template_analysis': location_validation.get('template_analysis', {})
            },
            
            # Location intelligence summary
            'location_intelligence': {
                'format_types_detected': location_validation.get('format_analysis', {}),
                'normalization_success_rate': location_validation.get('normalization_stats', {}).get('normalization_success_rate', 0.0),
                'canonical_service_active': True
            }
        }
        
        # Add invalid locations summary if any
        if location_validation.get('invalid_locations'):
            enhanced['location_issues'] = {
                'invalid_locations': [
                    {
                        'location': inv['location_code'],
                        'canonical_form': inv['canonical_form'],
                        'reason': inv['reason']
                    }
                    for inv in location_validation['invalid_locations']
                ],
                'recommendations': self._generate_location_recommendations(location_validation)
            }
        
        return enhanced
    
    def _generate_location_recommendations(self, location_validation: Dict) -> List[str]:
        """Generate recommendations for fixing location issues"""
        recommendations = []
        
        invalid_count = len(location_validation.get('invalid_locations', []))
        if invalid_count > 0:
            recommendations.append(f"Found {invalid_count} invalid locations - verify inventory data or expand template")
        
        coverage = location_validation.get('warehouse_coverage', 0.0)
        if coverage < 80.0:
            recommendations.append(f"Low coverage ({coverage:.1f}%) - consider reviewing template structure or inventory data quality")
        
        format_issues = location_validation.get('normalization_stats', {}).get('unparseable_locations', 0)
        if format_issues > 0:
            recommendations.append(f"Found {format_issues} unparseable location formats - check location naming conventions")
        
        if not recommendations:
            recommendations.append("Location validation passed - all locations valid")
        
        return recommendations
    
    def get_warehouse_analysis_status(self, warehouse_id: str) -> Dict:
        """Get comprehensive warehouse analysis readiness status"""
        try:
            # Template readiness
            template_ready, template_message = self.template_engine.is_warehouse_ready_for_analysis(warehouse_id)
            
            # Location count and types
            from models import Location
            location_stats = db.session.query(
                Location.location_type,
                db.func.count(Location.id)
            ).filter(
                Location.warehouse_id == warehouse_id,
                Location.is_active == True
            ).group_by(Location.location_type).all()
            
            location_counts = {loc_type: count for loc_type, count in location_stats}
            total_locations = sum(location_counts.values())
            
            return {
                'warehouse_id': warehouse_id,
                'ready_for_analysis': template_ready,
                'readiness_message': template_message,
                'location_summary': {
                    'total_locations': total_locations,
                    'by_type': location_counts
                },
                'production_requirements': {
                    'template_applied': template_ready,
                    'minimum_locations': total_locations >= 10,
                    'storage_locations_exist': location_counts.get('STORAGE', 0) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting warehouse status: {e}")
            return {
                'warehouse_id': warehouse_id,
                'ready_for_analysis': False,
                'error': str(e)
            }

# Factory function
def get_production_rule_engine() -> ProductionRuleEngine:
    """Get singleton instance of production rule engine"""
    return ProductionRuleEngine()