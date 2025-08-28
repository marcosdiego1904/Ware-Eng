"""
Virtual Location Engine for WareWise
Provides algorithmic location validation without database storage

This engine replaces the traditional approach of storing thousands of location
records with mathematical validation based on warehouse template rules.
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VirtualLocationProperties:
    """Properties of a virtual location derived from code and warehouse config"""
    code: str
    location_type: str  # STORAGE, RECEIVING, STAGING, DOCK, TRANSITIONAL
    capacity: int
    zone: str
    aisle_number: Optional[int] = None
    rack_identifier: Optional[str] = None
    position_number: Optional[int] = None
    level: Optional[str] = None
    is_valid: bool = True


class VirtualLocationEngine:
    """
    Core virtual location engine that validates locations algorithmically
    
    CRITICAL INTEGRATION: Works directly with WarehouseConfig from template creation
    """
    
    def __init__(self, warehouse_config: Dict[str, Any]):
        """
        Initialize virtual location engine from warehouse template configuration
        
        Args:
            warehouse_config: Configuration from template creation process
                Expected format from WarehouseConfig.to_dict():
                {
                    'warehouse_id': 'USER_TESTF',
                    'num_aisles': 2,
                    'racks_per_aisle': 2, 
                    'positions_per_rack': 35,
                    'levels_per_position': 4,
                    'level_names': 'ABCD',
                    'default_pallet_capacity': 1,
                    'receiving_areas': [{'code': 'RECV-01', 'capacity': 10}, ...],
                    'staging_areas': [{'code': 'STAGE-01', 'capacity': 5}, ...],
                    'dock_areas': [{'code': 'DOCK-01', 'capacity': 2}, ...]
                }
        """
        self.config = warehouse_config
        self.warehouse_id = warehouse_config.get('warehouse_id', 'DEFAULT')
        
        # Define the mathematical location universe
        self.storage_space = {
            'aisles': list(range(1, warehouse_config.get('num_aisles', 2) + 1)),
            'racks': self._get_rack_identifiers(warehouse_config),
            'positions': list(range(1, warehouse_config.get('positions_per_rack', 35) + 1)),
            'levels': list(warehouse_config.get('level_names', 'ABCD'))
        }
        
        # Build special areas lookup
        self.special_areas = self._build_special_areas_lookup()
        
        print(f"[VIRTUAL_ENGINE] Initialized for warehouse {self.warehouse_id}")
        print(f"  Storage universe: {len(self.storage_space['aisles'])} aisles × {len(self.storage_space['racks'])} racks × {len(self.storage_space['positions'])} positions × {len(self.storage_space['levels'])} levels")
        print(f"  Total storage locations: {self.calculate_total_storage_locations():,}")
        print(f"  Special areas: {len(self.special_areas)}")
    
    def _get_rack_identifiers(self, config: Dict[str, Any]) -> List[str]:
        """Generate rack identifiers (A, B, C, etc.) based on warehouse config"""
        racks_per_aisle = config.get('racks_per_aisle', 2)
        # Generate rack letters: A, B, C, D, etc.
        return [chr(ord('A') + i) for i in range(racks_per_aisle)]
    
    def _build_special_areas_lookup(self) -> Dict[str, Dict[str, Any]]:
        """Build lookup table for special areas from warehouse config"""
        special_areas = {}
        
        # Add receiving areas - RESPECT zone from config
        for area in self.config.get('receiving_areas', []):
            if isinstance(area, dict) and 'code' in area:
                special_areas[area['code']] = {
                    'location_type': 'RECEIVING',
                    'capacity': area.get('capacity', 10),
                    'zone': area.get('zone', 'RECEIVING')  # Use config zone or default
                }
        
        # Add staging areas - RESPECT zone from config
        for area in self.config.get('staging_areas', []):
            if isinstance(area, dict) and 'code' in area:
                special_areas[area['code']] = {
                    'location_type': 'STAGING',
                    'capacity': area.get('capacity', 5),
                    'zone': area.get('zone', 'STAGING')  # Use config zone or default
                }
        
        # Add dock areas - RESPECT zone from config
        for area in self.config.get('dock_areas', []):
            if isinstance(area, dict) and 'code' in area:
                special_areas[area['code']] = {
                    'location_type': 'DOCK',
                    'capacity': area.get('capacity', 2),
                    'zone': area.get('zone', 'DOCK')  # Use config zone or default
                }
        
        # Add AISLE transitional areas (one per aisle) - enabled by default for consistency
        # Physical warehouses typically have aisle transitional areas
        if self.config.get('auto_create_aisle_areas', True):  # Changed default to True
            for aisle_num in self.storage_space['aisles']:
                aisle_code = f'AISLE-{aisle_num:02d}'
                special_areas[aisle_code] = {
                    'location_type': 'TRANSITIONAL',
                    'capacity': 10,  # Standard transitional capacity
                    'zone': 'GENERAL'
                }
        
        return special_areas
    
    def validate_location(self, location_code: str) -> Tuple[bool, str]:
        """
        CORE METHOD: Validate if a location exists in this warehouse's virtual universe
        
        Args:
            location_code: Location code from inventory file
            
        Returns:
            Tuple of (is_valid: bool, reason: str)
        """
        if not location_code or not str(location_code).strip():
            return False, "Empty or null location code"
        
        code = str(location_code).strip().upper()
        
        # Remove warehouse prefix if present for validation
        normalized_code = self._remove_warehouse_prefix(code)
        
        # Check special areas first - DIRECT lookup instead of pattern matching
        if normalized_code in self.special_areas:
            return True, "Valid special area"
        
        # Check storage location format and bounds
        return self._validate_storage_location(normalized_code)
    
    def _remove_warehouse_prefix(self, location_code: str) -> str:
        """Remove warehouse prefix from location code for validation"""
        # Handle prefixes like USER_TESTF_, ALICE_, etc.
        prefixes_to_remove = [
            f'{self.warehouse_id}_',
            'USER_', 'ALICE_', 'WH01_', 'WH02_', 'WH_', 'DEFAULT_'
        ]
        
        code = location_code.upper()
        for prefix in prefixes_to_remove:
            if code.startswith(prefix):
                return code[len(prefix):]
        
        return code
    
    def _is_special_area(self, location_code: str) -> bool:
        """Check if location code matches special area patterns"""
        special_patterns = [
            r'^RECV-\d+$',      # RECV-01, RECV-02
            r'^STAGE-\d+$',     # STAGE-01
            r'^DOCK-\d+$',      # DOCK-01
            r'^AISLE-\d+$'      # AISLE-01, AISLE-02
        ]
        
        for pattern in special_patterns:
            if re.match(pattern, location_code):
                return True
        
        return False
    
    def _validate_storage_location(self, location_code: str) -> Tuple[bool, str]:
        """
        Validate storage location against warehouse dimensions
        
        Expected formats:
        - 01-A01-A (aisle-rack+position-level)
        - 01-A-001-A (aisle-rack-position-level) 
        - 02-B15-C (aisle-rack+position-level)
        """
        # Try different storage location patterns
        storage_patterns = [
            # Pattern 1: XX-YZZ-W (aisle-rack+position-level)
            r'^(\d{1,2})-([A-Z])(\d{1,3})-([A-Z])$',
            # Pattern 2: XX-Y-ZZZ-W (aisle-rack-position-level)  
            r'^(\d{1,2})-([A-Z])-(\d{1,3})-([A-Z])$',
            # Pattern 3: XX-YY-ZZZ-W (aisle-rack-position-level with 2-digit rack)
            r'^(\d{1,2})-(\d{1,2})-(\d{1,3})([A-Z])$'
        ]
        
        for pattern in storage_patterns:
            match = re.match(pattern, location_code)
            if match:
                try:
                    if len(match.groups()) == 4:
                        aisle_str, rack_str, position_str, level = match.groups()
                        
                        # Convert to integers for validation
                        aisle = int(aisle_str)
                        level = level.upper()
                        
                        # Handle rack identification (letter or number)
                        if rack_str.isalpha():
                            rack = rack_str.upper()
                        else:
                            # Convert number to letter (01 -> A, 02 -> B)
                            rack_num = int(rack_str)
                            if rack_num <= len(self.storage_space['racks']):
                                rack = self.storage_space['racks'][rack_num - 1]
                            else:
                                return False, f"Rack number {rack_num} exceeds warehouse racks (max: {len(self.storage_space['racks'])})"
                        
                        position = int(position_str)
                        
                        # Validate against warehouse dimensions
                        return self._check_storage_bounds(aisle, rack, position, level, location_code)
                        
                except (ValueError, IndexError) as e:
                    continue
        
        return False, f"Storage location format not recognized: '{location_code}'"
    
    def _check_storage_bounds(self, aisle: int, rack: str, position: int, level: str, original_code: str) -> Tuple[bool, str]:
        """Check if storage location components are within warehouse bounds"""
        
        # Validate aisle
        if aisle not in self.storage_space['aisles']:
            max_aisle = max(self.storage_space['aisles'])
            return False, f"Aisle {aisle} exceeds warehouse capacity (max: {max_aisle})"
        
        # Validate rack
        if rack not in self.storage_space['racks']:
            available_racks = ', '.join(self.storage_space['racks'])
            return False, f"Rack '{rack}' not available (available: {available_racks})"
        
        # Validate position
        if position not in self.storage_space['positions']:
            max_position = max(self.storage_space['positions'])
            return False, f"Position {position} exceeds rack capacity (max: {max_position})"
        
        # Validate level
        if level not in self.storage_space['levels']:
            available_levels = ', '.join(self.storage_space['levels'])
            return False, f"Level '{level}' not available (available: {available_levels})"
        
        return True, "Valid storage location"
    
    def get_location_properties(self, location_code: str) -> Optional[VirtualLocationProperties]:
        """
        Get complete properties for a location (replaces database lookup)
        
        Args:
            location_code: Location code to analyze
            
        Returns:
            VirtualLocationProperties object with all derived properties
        """
        is_valid, reason = self.validate_location(location_code)
        
        if not is_valid:
            return VirtualLocationProperties(
                code=location_code,
                location_type='UNKNOWN',
                capacity=0,
                zone='UNKNOWN',
                is_valid=False
            )
        
        code = str(location_code).strip().upper()
        normalized_code = self._remove_warehouse_prefix(code)
        
        # Handle special areas
        if normalized_code in self.special_areas:
            area_info = self.special_areas[normalized_code]
            return VirtualLocationProperties(
                code=location_code,
                location_type=area_info['location_type'],
                capacity=area_info['capacity'],
                zone=area_info['zone'],
                is_valid=True
            )
        
        # Handle storage locations
        return self._derive_storage_properties(location_code, normalized_code)
    
    def _derive_storage_properties(self, original_code: str, normalized_code: str) -> VirtualLocationProperties:
        """Derive properties for storage locations"""
        # Parse storage location components
        storage_patterns = [
            r'^(\d{1,2})-([A-Z])(\d{1,3})-([A-Z])$',
            r'^(\d{1,2})-([A-Z])-(\d{1,3})-([A-Z])$',
            r'^(\d{1,2})-(\d{1,2})-(\d{1,3})([A-Z])$'
        ]
        
        aisle_number = None
        rack_identifier = None
        position_number = None
        level = None
        
        for pattern in storage_patterns:
            match = re.match(pattern, normalized_code)
            if match:
                groups = match.groups()
                aisle_number = int(groups[0])
                level = groups[-1].upper()
                
                if len(groups) == 4:
                    if groups[1].isalpha():
                        rack_identifier = groups[1].upper()
                        position_number = int(groups[2])
                    else:
                        rack_num = int(groups[1])
                        rack_identifier = self.storage_space['racks'][rack_num - 1] if rack_num <= len(self.storage_space['racks']) else 'A'
                        position_number = int(groups[2])
                break
        
        return VirtualLocationProperties(
            code=original_code,
            location_type='STORAGE',
            capacity=self.config.get('default_pallet_capacity', 1),
            zone='STORAGE',
            aisle_number=aisle_number,
            rack_identifier=rack_identifier,
            position_number=position_number,
            level=level,
            is_valid=True
        )
    
    def calculate_total_storage_locations(self) -> int:
        """Calculate total number of possible storage locations"""
        return (len(self.storage_space['aisles']) * 
                len(self.storage_space['racks']) * 
                len(self.storage_space['positions']) * 
                len(self.storage_space['levels']))
    
    def calculate_total_locations(self) -> int:
        """Calculate total number of all possible locations (storage + special)"""
        return self.calculate_total_storage_locations() + len(self.special_areas)
    
    def get_warehouse_summary(self) -> Dict[str, Any]:
        """Get summary of virtual warehouse configuration"""
        return {
            'warehouse_id': self.warehouse_id,
            'total_possible_locations': self.calculate_total_locations(),
            'storage_locations': self.calculate_total_storage_locations(),
            'special_areas': len(self.special_areas),
            'warehouse_dimensions': {
                'aisles': len(self.storage_space['aisles']),
                'racks_per_aisle': len(self.storage_space['racks']),
                'positions_per_rack': len(self.storage_space['positions']),
                'levels_per_position': len(self.storage_space['levels'])
            },
            'special_areas_list': list(self.special_areas.keys())
        }


class VirtualLocationValidator:
    """
    Utility class for batch location validation
    Replaces expensive database queries with algorithmic validation
    """
    
    def __init__(self, virtual_engine: VirtualLocationEngine):
        self.engine = virtual_engine
    
    def validate_inventory_locations(self, inventory_locations: List[str]) -> Dict[str, Any]:
        """
        Batch validate inventory locations against virtual warehouse
        
        Args:
            inventory_locations: List of location codes from inventory file
            
        Returns:
            Comprehensive validation results
        """
        results = {
            'total_locations': len(inventory_locations),
            'valid_locations': [],
            'invalid_locations': [],
            'validation_details': {},
            'coverage_analysis': {}
        }
        
        print(f"[VIRTUAL_VALIDATOR] Validating {len(inventory_locations)} locations")
        
        for location_code in inventory_locations:
            is_valid, reason = self.engine.validate_location(location_code)
            
            validation_detail = {
                'location_code': location_code,
                'is_valid': is_valid,
                'reason': reason
            }
            
            if is_valid:
                results['valid_locations'].append(location_code)
                properties = self.engine.get_location_properties(location_code)
                validation_detail['properties'] = properties
            else:
                results['invalid_locations'].append(location_code)
            
            results['validation_details'][location_code] = validation_detail
        
        # Calculate coverage metrics
        total_possible = self.engine.calculate_total_locations()
        unique_valid = len(set(results['valid_locations']))
        
        results['coverage_analysis'] = {
            'warehouse_coverage_percentage': (unique_valid / total_possible * 100) if total_possible > 0 else 0,
            'unique_valid_locations': unique_valid,
            'total_possible_locations': total_possible,
            'validation_success_rate': (len(results['valid_locations']) / len(inventory_locations) * 100) if inventory_locations else 0
        }
        
        print(f"[VIRTUAL_VALIDATOR] Results: {len(results['valid_locations'])} valid, {len(results['invalid_locations'])} invalid")
        
        return results


def create_virtual_engine_from_warehouse_config(warehouse_config: Dict[str, Any]) -> VirtualLocationEngine:
    """
    Factory function to create virtual location engine from warehouse configuration
    
    CRITICAL: This is the main integration point with the template system
    """
    print(f"[VIRTUAL_ENGINE_FACTORY] Creating virtual engine for warehouse: {warehouse_config.get('warehouse_id', 'UNKNOWN')}")
    
    return VirtualLocationEngine(warehouse_config)