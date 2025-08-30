#!/usr/bin/env python3
"""
Warehouse Template Resolver
Dynamic template resolution system for template-driven validation architecture

This module provides the missing link between warehouse_context (warehouse_id) and
the actual warehouse configuration that should be used for validation.

ARCHITECTURAL SOLUTION:
- Resolves warehouse_id → WarehouseConfig → VirtualLocationEngine configuration
- Enables dynamic, template-based validation instead of hardcoded rules
- Supports multiple warehouse types with different dimensions and constraints
"""

import json
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from flask import current_app

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class TemplateResolutionResult:
    """Result of template resolution with all necessary context"""
    warehouse_id: str
    warehouse_config: Dict[str, Any]
    resolution_method: str  # 'database', 'default_mapping', 'fallback'
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW'
    template_source: str  # Description of where config came from


class WarehouseTemplateResolver:
    """
    Core template resolver that bridges warehouse_context to actual configurations
    
    DESIGN PHILOSOPHY:
    - Always try to resolve to a real template first
    - Provide intelligent fallbacks for missing configurations  
    - Log resolution process for debugging and monitoring
    - Enable both database and static template resolution
    """
    
    def __init__(self, db_session=None):
        """
        Initialize template resolver
        
        Args:
            db_session: SQLAlchemy session for database access (optional)
        """
        self.db_session = db_session
        
        # Static template definitions as fallback
        self.static_templates = self._get_static_template_definitions()
        
        logger.info("[TEMPLATE_RESOLVER] Initialized warehouse template resolver")
    
    def resolve_warehouse_template(self, warehouse_context: Dict[str, Any]) -> TemplateResolutionResult:
        """
        CORE METHOD: Resolve warehouse_context to actual template configuration
        
        Resolution Priority:
        1. Database lookup by warehouse_id
        2. Static template mapping
        3. Intelligent defaults based on warehouse_id patterns
        4. System fallback template
        
        Args:
            warehouse_context: Context from rule engine containing warehouse_id
            
        Returns:
            TemplateResolutionResult with resolved configuration
        """
        warehouse_id = warehouse_context.get('warehouse_id')
        
        if not warehouse_id:
            logger.warning("[TEMPLATE_RESOLVER] No warehouse_id in context, using default")
            return self._create_fallback_result('NO_WAREHOUSE_ID', 'default')
        
        logger.info(f"[TEMPLATE_RESOLVER] Resolving template for warehouse: {warehouse_id}")
        
        # Step 1: Try database resolution
        if self.db_session:
            db_result = self._resolve_from_database(warehouse_id)
            if db_result:
                return db_result
        
        # Step 2: Try static template mapping
        static_result = self._resolve_from_static_templates(warehouse_id)
        if static_result:
            return static_result
        
        # Step 3: Try intelligent pattern matching
        pattern_result = self._resolve_from_patterns(warehouse_id)
        if pattern_result:
            return pattern_result
        
        # Step 4: System fallback
        logger.warning(f"[TEMPLATE_RESOLVER] Could not resolve {warehouse_id}, using fallback")
        return self._create_fallback_result(warehouse_id, 'no_match_found')
    
    def _resolve_from_database(self, warehouse_id: str) -> Optional[TemplateResolutionResult]:
        """Resolve template from database WarehouseConfig table"""
        try:
            from models import WarehouseConfig
            
            config = WarehouseConfig.query.filter_by(
                warehouse_id=warehouse_id, 
                is_active=True
            ).first()
            
            if config:
                warehouse_config = config.to_dict()
                logger.info(f"[TEMPLATE_RESOLVER] Found database config for {warehouse_id}")
                logger.debug(f"[TEMPLATE_RESOLVER] Config: {warehouse_config}")
                
                return TemplateResolutionResult(
                    warehouse_id=warehouse_id,
                    warehouse_config=warehouse_config,
                    resolution_method='database',
                    confidence='HIGH',
                    template_source=f'Database WarehouseConfig.id={config.id}'
                )
            else:
                logger.info(f"[TEMPLATE_RESOLVER] No database config found for {warehouse_id}")
                return None
                
        except ImportError:
            logger.warning("[TEMPLATE_RESOLVER] WarehouseConfig model not available")
            return None
        except Exception as e:
            logger.error(f"[TEMPLATE_RESOLVER] Database resolution failed: {e}")
            return None
    
    def _resolve_from_static_templates(self, warehouse_id: str) -> Optional[TemplateResolutionResult]:
        """Resolve from static template definitions"""
        if warehouse_id in self.static_templates:
            template = self.static_templates[warehouse_id]
            logger.info(f"[TEMPLATE_RESOLVER] Found static template for {warehouse_id}")
            
            return TemplateResolutionResult(
                warehouse_id=warehouse_id,
                warehouse_config=template,
                resolution_method='static_mapping',
                confidence='MEDIUM',
                template_source=f'Static template definition'
            )
        
        return None
    
    def _resolve_from_patterns(self, warehouse_id: str) -> Optional[TemplateResolutionResult]:
        """Resolve using intelligent pattern matching"""
        
        # Pattern 1: USER_* → DEFAULT template (most common case)
        if warehouse_id.startswith('USER_'):
            logger.info(f"[TEMPLATE_RESOLVER] Applying USER_ pattern to {warehouse_id}")
            return TemplateResolutionResult(
                warehouse_id=warehouse_id,
                warehouse_config=self.static_templates['DEFAULT'],
                resolution_method='pattern_matching',
                confidence='MEDIUM',
                template_source='USER_ pattern → DEFAULT template'
            )
        
        # Pattern 2: SMALL_* → SMALL template
        if warehouse_id.startswith('SMALL_') or 'SMALL' in warehouse_id:
            logger.info(f"[TEMPLATE_RESOLVER] Applying SMALL pattern to {warehouse_id}")
            return TemplateResolutionResult(
                warehouse_id=warehouse_id,
                warehouse_config=self.static_templates['SMALL'],
                resolution_method='pattern_matching',
                confidence='MEDIUM',
                template_source='SMALL pattern → SMALL template'
            )
        
        # Pattern 3: LARGE_* → LARGE template
        if warehouse_id.startswith('LARGE_') or 'LARGE' in warehouse_id:
            logger.info(f"[TEMPLATE_RESOLVER] Applying LARGE pattern to {warehouse_id}")
            return TemplateResolutionResult(
                warehouse_id=warehouse_id,
                warehouse_config=self.static_templates['LARGE'],
                resolution_method='pattern_matching',
                confidence='MEDIUM',
                template_source='LARGE pattern → LARGE template'
            )
        
        return None
    
    def _create_fallback_result(self, warehouse_id: str, reason: str) -> TemplateResolutionResult:
        """Create fallback template result"""
        logger.warning(f"[TEMPLATE_RESOLVER] Using fallback template for {warehouse_id}: {reason}")
        
        return TemplateResolutionResult(
            warehouse_id=warehouse_id,
            warehouse_config=self.static_templates['DEFAULT'],
            resolution_method='fallback',
            confidence='LOW',
            template_source=f'System fallback due to: {reason}'
        )
    
    def _get_static_template_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Define static template configurations for different warehouse types
        
        These serve as:
        1. Fallback templates when database is unavailable
        2. Reference implementations for different warehouse scales
        3. Pattern matching targets
        
        CRITICAL: These must match the WarehouseConfig.to_dict() format
        """
        return {
            'DEFAULT': {
                'warehouse_id': 'DEFAULT',
                'warehouse_name': 'Default Warehouse Layout',
                'num_aisles': 4,
                'racks_per_aisle': 2,
                'positions_per_rack': 46,  # FIXED: Updated from hardcoded 29 to correct 46
                'levels_per_position': 4,
                'level_names': 'ABCD',
                'default_pallet_capacity': 1,
                'bidimensional_racks': False,
                'receiving_areas': [
                    {'code': 'RECV-01', 'capacity': 10, 'zone': 'RECEIVING'},
                    {'code': 'RECV-02', 'capacity': 10, 'zone': 'RECEIVING'}
                ],
                'staging_areas': [
                    {'code': 'STAGE-01', 'capacity': 5, 'zone': 'STAGING'}
                ],
                'dock_areas': [
                    {'code': 'DOCK-01', 'capacity': 2, 'zone': 'DOCK'}
                ],
                'auto_create_aisle_areas': True
            },
            
            'SMALL': {
                'warehouse_id': 'SMALL',
                'warehouse_name': 'Small Warehouse Layout',
                'num_aisles': 2,
                'racks_per_aisle': 1,
                'positions_per_rack': 20,
                'levels_per_position': 3,
                'level_names': 'ABC',
                'default_pallet_capacity': 1,
                'bidimensional_racks': False,
                'receiving_areas': [
                    {'code': 'RECV-01', 'capacity': 5, 'zone': 'RECEIVING'}
                ],
                'staging_areas': [
                    {'code': 'STAGE-01', 'capacity': 3, 'zone': 'STAGING'}
                ],
                'dock_areas': [
                    {'code': 'DOCK-01', 'capacity': 1, 'zone': 'DOCK'}
                ],
                'auto_create_aisle_areas': True
            },
            
            'LARGE': {
                'warehouse_id': 'LARGE',
                'warehouse_name': 'Large Warehouse Layout',
                'num_aisles': 6,
                'racks_per_aisle': 3,
                'positions_per_rack': 60,
                'levels_per_position': 5,
                'level_names': 'ABCDE',
                'default_pallet_capacity': 1,
                'bidimensional_racks': False,
                'receiving_areas': [
                    {'code': 'RECV-01', 'capacity': 15, 'zone': 'RECEIVING'},
                    {'code': 'RECV-02', 'capacity': 15, 'zone': 'RECEIVING'},
                    {'code': 'RECV-03', 'capacity': 15, 'zone': 'RECEIVING'}
                ],
                'staging_areas': [
                    {'code': 'STAGE-01', 'capacity': 10, 'zone': 'STAGING'},
                    {'code': 'STAGE-02', 'capacity': 10, 'zone': 'STAGING'}
                ],
                'dock_areas': [
                    {'code': 'DOCK-01', 'capacity': 3, 'zone': 'DOCK'},
                    {'code': 'DOCK-02', 'capacity': 3, 'zone': 'DOCK'},
                    {'code': 'DOCK-03', 'capacity': 3, 'zone': 'DOCK'}
                ],
                'auto_create_aisle_areas': True
            }
        }
    
    def get_validation_summary(self, warehouse_id: str) -> Dict[str, Any]:
        """
        Get comprehensive validation summary for a warehouse
        
        Useful for debugging and system diagnostics
        """
        warehouse_context = {'warehouse_id': warehouse_id}
        result = self.resolve_warehouse_template(warehouse_context)
        
        config = result.warehouse_config
        storage_locations = (config['num_aisles'] * config['racks_per_aisle'] * 
                           config['positions_per_rack'] * config['levels_per_position'])
        
        return {
            'warehouse_id': warehouse_id,
            'resolution_result': {
                'method': result.resolution_method,
                'confidence': result.confidence,
                'source': result.template_source
            },
            'template_config': {
                'warehouse_name': config.get('warehouse_name', 'Unknown'),
                'dimensions': f"{config['num_aisles']}×{config['racks_per_aisle']}×{config['positions_per_rack']}×{config['levels_per_position']}",
                'total_storage_locations': storage_locations,
                'special_areas': len(config.get('receiving_areas', [])) + len(config.get('staging_areas', [])) + len(config.get('dock_areas', []))
            },
            'validation_constraints': {
                'max_aisle': config['num_aisles'],
                'max_position': config['positions_per_rack'],
                'valid_levels': list(config['level_names']),
                'pallet_capacity': config['default_pallet_capacity']
            }
        }


class TemplateBasedLocationValidatorFactory:
    """
    Factory for creating template-aware location validators
    
    DESIGN: This replaces the need to modify every evaluator individually.
    Instead, we create validators that automatically adapt to the resolved template.
    """
    
    def __init__(self, db_session=None):
        """Initialize validator factory with template resolver"""
        self.template_resolver = WarehouseTemplateResolver(db_session)
        logger.info("[VALIDATOR_FACTORY] Initialized template-based location validator factory")
    
    def create_virtual_engine(self, warehouse_context: Dict[str, Any]):
        """
        Create VirtualLocationEngine configured for the specific warehouse template
        
        This is the KEY INTEGRATION POINT that solves the hardcoded validation issue
        
        Args:
            warehouse_context: Context containing warehouse_id from rule evaluation
            
        Returns:
            VirtualLocationEngine configured with the correct template
        """
        # Resolve the warehouse template dynamically
        resolution_result = self.template_resolver.resolve_warehouse_template(warehouse_context)
        
        logger.info(f"[VALIDATOR_FACTORY] Creating virtual engine for {resolution_result.warehouse_id}")
        logger.info(f"[VALIDATOR_FACTORY] Resolution: {resolution_result.resolution_method} ({resolution_result.confidence})")
        
        # Import and create VirtualLocationEngine with resolved config
        from virtual_location_engine import VirtualLocationEngine
        
        virtual_engine = VirtualLocationEngine(resolution_result.warehouse_config)
        
        # Add resolution metadata for debugging
        virtual_engine._template_resolution = resolution_result
        
        return virtual_engine
    
    def create_location_validator(self, warehouse_context: Dict[str, Any]):
        """
        Create complete location validator (Virtual Engine + Validator wrapper)
        
        Args:
            warehouse_context: Context containing warehouse_id
            
        Returns:
            VirtualLocationValidator ready for batch validation
        """
        virtual_engine = self.create_virtual_engine(warehouse_context)
        
        from virtual_location_engine import VirtualLocationValidator
        return VirtualLocationValidator(virtual_engine)


# Singleton instances for system-wide use
_template_resolver_instance = None
_validator_factory_instance = None

def get_template_resolver(db_session=None) -> WarehouseTemplateResolver:
    """Get singleton template resolver instance"""
    global _template_resolver_instance
    
    if _template_resolver_instance is None:
        _template_resolver_instance = WarehouseTemplateResolver(db_session)
    
    return _template_resolver_instance

def get_validator_factory(db_session=None) -> TemplateBasedLocationValidatorFactory:
    """Get singleton validator factory instance"""
    global _validator_factory_instance
    
    if _validator_factory_instance is None:
        _validator_factory_instance = TemplateBasedLocationValidatorFactory(db_session)
    
    return _validator_factory_instance

def resolve_warehouse_config(warehouse_context: Dict[str, Any], db_session=None) -> Dict[str, Any]:
    """
    CONVENIENCE FUNCTION: Quick warehouse configuration resolution
    
    This is the main entry point for rule evaluators that need template configuration
    
    Args:
        warehouse_context: Context from rule engine
        db_session: Database session (optional)
        
    Returns:
        Resolved warehouse configuration dictionary ready for VirtualLocationEngine
    """
    resolver = get_template_resolver(db_session)
    result = resolver.resolve_warehouse_template(warehouse_context)
    return result.warehouse_config

# DIAGNOSTIC FUNCTIONS for system monitoring and debugging

def diagnose_warehouse_template_resolution(warehouse_id: str, db_session=None) -> Dict[str, Any]:
    """
    Comprehensive diagnostic function for template resolution debugging
    
    Args:
        warehouse_id: Warehouse to diagnose
        db_session: Database session
        
    Returns:
        Detailed diagnostic report
    """
    resolver = get_template_resolver(db_session)
    warehouse_context = {'warehouse_id': warehouse_id}
    
    # Get resolution result
    result = resolver.resolve_warehouse_template(warehouse_context)
    
    # Get validation summary
    validation_summary = resolver.get_validation_summary(warehouse_id)
    
    # Test virtual engine creation
    try:
        factory = get_validator_factory(db_session)
        virtual_engine = factory.create_virtual_engine(warehouse_context)
        engine_summary = virtual_engine.get_warehouse_summary()
        virtual_engine_status = 'SUCCESS'
    except Exception as e:
        engine_summary = {'error': str(e)}
        virtual_engine_status = 'FAILED'
    
    return {
        'warehouse_id': warehouse_id,
        'timestamp': logger.handlers[0].format(logging.LogRecord(
            'template_resolver', logging.INFO, '', 0, '', (), None
        )) if logger.handlers else 'N/A',
        'template_resolution': {
            'status': 'SUCCESS' if result else 'FAILED',
            'method': result.resolution_method,
            'confidence': result.confidence,
            'source': result.template_source
        },
        'validation_summary': validation_summary,
        'virtual_engine_creation': {
            'status': virtual_engine_status,
            'engine_summary': engine_summary
        },
        'recommendations': _generate_resolution_recommendations(result, validation_summary)
    }

def _generate_resolution_recommendations(result: TemplateResolutionResult, 
                                       validation_summary: Dict[str, Any]):
    """Generate recommendations for improving template resolution"""
    recommendations = []
    
    if result.confidence == 'LOW':
        recommendations.append(f"Consider creating database WarehouseConfig entry for {result.warehouse_id}")
    
    if result.resolution_method == 'fallback':
        recommendations.append("Warehouse configuration not found - using system defaults")
        recommendations.append("Verify warehouse_id matches expected format")
    
    if result.resolution_method == 'pattern_matching':
        recommendations.append("Using pattern-based template - consider explicit database configuration for better accuracy")
    
    storage_locations = validation_summary['template_config']['total_storage_locations']
    if storage_locations > 10000:
        recommendations.append("Large warehouse configuration detected - monitor validation performance")
    
    return recommendations