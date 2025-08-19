"""
Production Template Engine

Implements the complete production workflow:
1. User creates template with structure definition
2. Template generates ALL required locations (storage + special areas)
3. System validates template completeness before allowing analysis
4. Analysis only works against properly templated warehouses
5. Location format intelligence adapts user inputs to template structure

This ensures proper production workflow where templates are mandatory
and analysis is always performed against complete, validated warehouse structures.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from sqlalchemy import and_, or_

from models import Location, WarehouseConfig, WarehouseTemplate, db
from location_service import get_canonical_service

logger = logging.getLogger(__name__)

@dataclass
class TemplateStructure:
    """Production template structure definition"""
    num_aisles: int
    racks_per_aisle: int  
    positions_per_rack: int
    levels_per_position: int
    level_names: str  # e.g., "ABCD"
    default_pallet_capacity: int
    
    # Special areas
    receiving_areas: List[Dict]  # [{"code": "RECV-01", "capacity": 10}, ...]
    staging_areas: List[Dict]    # [{"code": "STAGE-01", "capacity": 5}, ...]
    dock_areas: List[Dict]       # [{"code": "DOCK-01", "capacity": 2}, ...]
    transitional_areas: List[Dict]  # [{"code": "AISLE-01", "capacity": 10}, ...]

class ProductionTemplateEngine:
    """
    Production-grade template engine that enforces proper workflow:
    Template Creation → Location Generation → Validation → Analysis
    """
    
    def __init__(self):
        self.canonical_service = get_canonical_service()
        logger.info("Production Template Engine initialized")
    
    def create_production_template(self, 
                                 template_name: str,
                                 warehouse_id: str,
                                 structure: TemplateStructure,
                                 created_by: int = 1) -> Dict:
        """
        Create a production template with complete location generation.
        
        This is the ONLY way to create warehouses in production - templates are mandatory.
        
        Args:
            template_name: Name for the template
            warehouse_id: Unique warehouse identifier
            structure: Complete template structure definition
            created_by: User ID creating the template
            
        Returns:
            Dictionary with creation results and validation
        """
        try:
            logger.info(f"Creating production template '{template_name}' for warehouse '{warehouse_id}'")
            
            # Step 1: Validate template structure
            validation = self._validate_template_structure(structure)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': f"Template validation failed: {validation['errors']}",
                    'template': None,
                    'locations_created': 0
                }
            
            # Step 2: Create warehouse configuration
            config = WarehouseConfig(
                warehouse_id=warehouse_id,
                warehouse_name=template_name,
                num_aisles=structure.num_aisles,
                racks_per_aisle=structure.racks_per_aisle,
                positions_per_rack=structure.positions_per_rack,
                levels_per_position=structure.levels_per_position,
                level_names=structure.level_names,
                default_pallet_capacity=structure.default_pallet_capacity,
                bidimensional_racks=False,  # Standard configuration
                created_by=created_by
            )
            
            # Store special areas as JSON
            config.receiving_areas = json.dumps(structure.receiving_areas)
            config.staging_areas = json.dumps(structure.staging_areas) 
            config.dock_areas = json.dumps(structure.dock_areas)
            
            db.session.add(config)
            db.session.flush()  # Get the config ID
            
            # Step 3: Generate ALL locations based on template
            locations_created = self._generate_all_locations(warehouse_id, structure, created_by)
            
            # Step 4: Create template record for reusability
            template = WarehouseTemplate(
                name=template_name,
                description=f"Production template for {warehouse_id}",
                num_aisles=structure.num_aisles,
                racks_per_aisle=structure.racks_per_aisle,
                positions_per_rack=structure.positions_per_rack,
                levels_per_position=structure.levels_per_position,
                level_names=structure.level_names,
                default_pallet_capacity=structure.default_pallet_capacity,
                receiving_areas_template=json.dumps(structure.receiving_areas),
                staging_areas_template=json.dumps(structure.staging_areas),
                dock_areas_template=json.dumps(structure.dock_areas),
                is_public=False,
                created_by=created_by
            )
            
            template.generate_template_code()
            db.session.add(template)
            
            # Step 5: Commit everything
            db.session.commit()
            
            # Step 6: Validate final result
            final_validation = self._validate_warehouse_completeness(warehouse_id)
            
            result = {
                'success': True,
                'message': f'Production template created successfully',
                'warehouse_id': warehouse_id,
                'template_code': template.template_code,
                'locations_created': locations_created,
                'template_validation': validation,
                'warehouse_validation': final_validation,
                'structure': {
                    'storage_locations': structure.num_aisles * structure.racks_per_aisle * structure.positions_per_rack * structure.levels_per_position,
                    'special_areas': len(structure.receiving_areas) + len(structure.staging_areas) + len(structure.dock_areas) + len(structure.transitional_areas),
                    'total_capacity': self._calculate_total_capacity(structure)
                }
            }
            
            logger.info(f"Production template '{template_name}' created: {locations_created['total']} locations")
            return result
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create production template: {e}")
            return {
                'success': False,
                'error': f"Template creation failed: {str(e)}",
                'template': None,
                'locations_created': 0
            }
    
    def _validate_template_structure(self, structure: TemplateStructure) -> Dict:
        """Validate template structure for production requirements"""
        errors = []
        warnings = []
        
        # Basic structure validation
        if structure.num_aisles <= 0 or structure.num_aisles > 50:
            errors.append(f"Invalid aisles: {structure.num_aisles} (must be 1-50)")
            
        if structure.racks_per_aisle <= 0 or structure.racks_per_aisle > 50:
            errors.append(f"Invalid racks per aisle: {structure.racks_per_aisle} (must be 1-50)")
            
        if structure.positions_per_rack <= 0 or structure.positions_per_rack > 999:
            errors.append(f"Invalid positions per rack: {structure.positions_per_rack} (must be 1-999)")
            
        if structure.levels_per_position <= 0 or structure.levels_per_position > 26:
            errors.append(f"Invalid levels per position: {structure.levels_per_position} (must be 1-26)")
            
        # Level names validation
        if len(structure.level_names) != structure.levels_per_position:
            errors.append(f"Level names '{structure.level_names}' doesn't match levels per position {structure.levels_per_position}")
        
        # Capacity validation
        if structure.default_pallet_capacity <= 0:
            errors.append(f"Invalid default capacity: {structure.default_pallet_capacity}")
        
        # Special areas validation
        if not structure.receiving_areas:
            warnings.append("No receiving areas defined - analysis may fail")
            
        # Calculate expected locations
        expected_storage = structure.num_aisles * structure.racks_per_aisle * structure.positions_per_rack * structure.levels_per_position
        expected_special = len(structure.receiving_areas) + len(structure.staging_areas) + len(structure.dock_areas) + len(structure.transitional_areas)
        
        if expected_storage > 100000:
            warnings.append(f"Large warehouse: {expected_storage} storage locations will be created")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'expected_locations': {
                'storage': expected_storage,
                'special': expected_special,
                'total': expected_storage + expected_special
            }
        }
    
    def _generate_all_locations(self, warehouse_id: str, structure: TemplateStructure, created_by: int) -> Dict:
        """Generate ALL locations for the warehouse based on template structure"""
        locations_created = {
            'storage': 0,
            'receiving': 0,
            'staging': 0,
            'dock': 0,
            'transitional': 0,
            'total': 0
        }
        
        try:
            # Generate storage locations in batches
            storage_locations = self._generate_storage_locations(warehouse_id, structure, created_by)
            db.session.bulk_save_objects(storage_locations)
            locations_created['storage'] = len(storage_locations)
            
            # Generate special areas
            special_locations = self._generate_special_areas(warehouse_id, structure, created_by)
            db.session.bulk_save_objects(special_locations)
            
            # Count special area types
            for location in special_locations:
                if location.location_type == 'RECEIVING':
                    locations_created['receiving'] += 1
                elif location.location_type == 'STAGING':
                    locations_created['staging'] += 1
                elif location.location_type == 'DOCK':
                    locations_created['dock'] += 1
                elif location.location_type == 'TRANSITIONAL':
                    locations_created['transitional'] += 1
            
            locations_created['total'] = sum(locations_created.values()) - locations_created['total']  # Avoid double counting
            
            logger.info(f"Generated {locations_created['total']} locations for warehouse {warehouse_id}")
            return locations_created
            
        except Exception as e:
            logger.error(f"Error generating locations: {e}")
            raise
    
    def _generate_storage_locations(self, warehouse_id: str, structure: TemplateStructure, created_by: int) -> List[Location]:
        """Generate all storage locations based on template structure"""
        locations = []
        
        for aisle in range(1, structure.num_aisles + 1):
            for rack in range(1, structure.racks_per_aisle + 1):
                for position in range(1, structure.positions_per_rack + 1):
                    for level_idx in range(structure.levels_per_position):
                        level = structure.level_names[level_idx]
                        
                        # Generate canonical location code
                        code = f"{aisle:02d}-{rack:02d}-{position:03d}{level}"
                        
                        location = Location(
                            warehouse_id=warehouse_id,
                            code=code,
                            location_type='STORAGE',
                            zone='STORAGE',
                            pallet_capacity=structure.default_pallet_capacity,
                            is_active=True,
                            created_by=created_by
                        )
                        
                        locations.append(location)
        
        return locations
    
    def _generate_special_areas(self, warehouse_id: str, structure: TemplateStructure, created_by: int) -> List[Location]:
        """Generate all special area locations"""
        locations = []
        
        # Receiving areas
        for area in structure.receiving_areas:
            location = Location(
                warehouse_id=warehouse_id,
                code=area['code'],
                location_type='RECEIVING',
                zone='RECEIVING',
                pallet_capacity=area.get('capacity', 10),
                is_active=True,
                created_by=created_by
            )
            locations.append(location)
        
        # Staging areas  
        for area in structure.staging_areas:
            location = Location(
                warehouse_id=warehouse_id,
                code=area['code'],
                location_type='STAGING',
                zone='STAGING',
                pallet_capacity=area.get('capacity', 5),
                is_active=True,
                created_by=created_by
            )
            locations.append(location)
        
        # Dock areas
        for area in structure.dock_areas:
            location = Location(
                warehouse_id=warehouse_id,
                code=area['code'],
                location_type='DOCK',
                zone='DOCK',
                pallet_capacity=area.get('capacity', 2),
                is_active=True,
                created_by=created_by
            )
            locations.append(location)
        
        # Transitional areas (AISLE locations)
        for area in structure.transitional_areas:
            location = Location(
                warehouse_id=warehouse_id,
                code=area['code'],
                location_type='TRANSITIONAL',
                zone='GENERAL',
                pallet_capacity=area.get('capacity', 10),
                is_active=True,
                created_by=created_by
            )
            locations.append(location)
        
        return locations
    
    def _calculate_total_capacity(self, structure: TemplateStructure) -> int:
        """Calculate total pallet capacity of the warehouse"""
        storage_capacity = (structure.num_aisles * structure.racks_per_aisle * 
                          structure.positions_per_rack * structure.levels_per_position * 
                          structure.default_pallet_capacity)
        
        special_capacity = sum([
            sum(area.get('capacity', 0) for area in structure.receiving_areas),
            sum(area.get('capacity', 0) for area in structure.staging_areas),
            sum(area.get('capacity', 0) for area in structure.dock_areas),
            sum(area.get('capacity', 0) for area in structure.transitional_areas)
        ])
        
        return storage_capacity + special_capacity
    
    def _validate_warehouse_completeness(self, warehouse_id: str) -> Dict:
        """Validate that warehouse template was applied completely"""
        try:
            # Count locations by type
            location_counts = db.session.query(
                Location.location_type,
                db.func.count(Location.id)
            ).filter(
                Location.warehouse_id == warehouse_id,
                Location.is_active == True
            ).group_by(Location.location_type).all()
            
            counts_dict = {loc_type: count for loc_type, count in location_counts}
            total_locations = sum(counts_dict.values())
            
            # Check for required location types
            required_types = ['STORAGE']
            missing_types = [t for t in required_types if t not in counts_dict]
            
            return {
                'complete': len(missing_types) == 0 and total_locations > 0,
                'total_locations': total_locations,
                'location_types': counts_dict,
                'missing_types': missing_types,
                'warehouse_id': warehouse_id
            }
            
        except Exception as e:
            logger.error(f"Error validating warehouse completeness: {e}")
            return {
                'complete': False,
                'error': str(e),
                'warehouse_id': warehouse_id
            }
    
    def is_warehouse_ready_for_analysis(self, warehouse_id: str) -> Tuple[bool, str]:
        """
        Check if warehouse is ready for rule analysis.
        
        Production requirement: Analysis can only run on properly templated warehouses.
        
        Returns:
            (ready: bool, message: str)
        """
        try:
            # Check warehouse configuration exists
            config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            if not config:
                return False, f"No warehouse configuration found for '{warehouse_id}'"
            
            # Check locations exist
            location_count = Location.query.filter(
                Location.warehouse_id == warehouse_id,
                Location.is_active == True
            ).count()
            
            if location_count == 0:
                return False, f"No locations found for warehouse '{warehouse_id}'. Create template first."
            
            # Check for required location types
            storage_count = Location.query.filter(
                Location.warehouse_id == warehouse_id,
                Location.location_type == 'STORAGE',
                Location.is_active == True
            ).count()
            
            if storage_count == 0:
                return False, f"No storage locations found for warehouse '{warehouse_id}'"
            
            # All checks passed
            return True, f"Warehouse '{warehouse_id}' ready for analysis ({location_count} locations)"
            
        except Exception as e:
            logger.error(f"Error checking warehouse readiness: {e}")
            return False, f"Error validating warehouse: {str(e)}"

# Factory function for easy integration
def get_production_template_engine() -> ProductionTemplateEngine:
    """Get singleton instance of production template engine"""
    return ProductionTemplateEngine()