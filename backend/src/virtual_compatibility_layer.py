"""
Virtual Location Compatibility Layer
Ensures backwards compatibility while providing virtual location benefits

This module provides compatibility shims and migration utilities to ensure
existing code continues working while gradually transitioning to virtual locations.
"""

import os
from typing import Dict, Any, List, Optional
from flask import current_app
from models import WarehouseConfig, Location
from database import db
from virtual_template_integration import get_virtual_engine_for_warehouse


class VirtualLocationCompatibilityManager:
    """
    Manages compatibility between virtual and physical location systems
    """
    
    def __init__(self):
        # Feature flags for gradual rollout
        self.enable_virtual_locations = os.environ.get('ENABLE_VIRTUAL_LOCATIONS', 'true').lower() == 'true'
        self.fallback_to_physical = os.environ.get('FALLBACK_TO_PHYSICAL', 'true').lower() == 'true'
        self.debug_compatibility = os.environ.get('DEBUG_VIRTUAL_COMPATIBILITY', 'false').lower() == 'true'
        
        if self.debug_compatibility:
            print(f"[VIRTUAL_COMPAT] Initialized with virtual_locations={self.enable_virtual_locations}, fallback={self.fallback_to_physical}")
    
    def get_location_by_code(self, warehouse_id: str, location_code: str) -> Optional[Dict[str, Any]]:
        """
        Compatibility method that works with both virtual and physical locations
        
        This replaces direct Location.query calls throughout the codebase
        """
        if self.debug_compatibility:
            print(f"[VIRTUAL_COMPAT] Looking up location '{location_code}' in warehouse '{warehouse_id}'")
        
        # Try virtual location first if enabled
        if self.enable_virtual_locations:
            virtual_result = self._get_virtual_location(warehouse_id, location_code)
            if virtual_result:
                if self.debug_compatibility:
                    print(f"[VIRTUAL_COMPAT] Found virtual location: {virtual_result['code']}")
                return virtual_result
        
        # Fall back to physical location if virtual not found or disabled
        if self.fallback_to_physical:
            physical_result = self._get_physical_location(warehouse_id, location_code)
            if physical_result:
                if self.debug_compatibility:
                    print(f"[VIRTUAL_COMPAT] Found physical location: {physical_result['code']}")
                return physical_result
        
        if self.debug_compatibility:
            print(f"[VIRTUAL_COMPAT] Location '{location_code}' not found in warehouse '{warehouse_id}'")
        return None
    
    def _get_virtual_location(self, warehouse_id: str, location_code: str) -> Optional[Dict[str, Any]]:
        """Get location from virtual engine"""
        try:
            virtual_engine = get_virtual_engine_for_warehouse(warehouse_id)
            if not virtual_engine:
                return None
            
            properties = virtual_engine.get_location_properties(location_code)
            if not properties or not properties.is_valid:
                return None
            
            # Convert to dictionary format compatible with old Location model
            return {
                'code': properties.code,
                'location_type': properties.location_type,
                'capacity': properties.capacity,
                'pallet_capacity': properties.capacity,  # Alias for compatibility
                'zone': properties.zone,
                'warehouse_id': warehouse_id,
                'aisle_number': properties.aisle_number,
                'rack_number': None,  # Virtual engine uses rack_identifier
                'position_number': properties.position_number,
                'level': properties.level,
                'is_active': True,
                'source': 'virtual'
            }
            
        except Exception as e:
            if self.debug_compatibility:
                print(f"[VIRTUAL_COMPAT] Virtual location lookup failed: {e}")
            return None
    
    def _get_physical_location(self, warehouse_id: str, location_code: str) -> Optional[Dict[str, Any]]:
        """Get location from physical database"""
        try:
            location = Location.query.filter_by(
                warehouse_id=warehouse_id,
                code=location_code
            ).first()
            
            if not location:
                return None
            
            return {
                'code': location.code,
                'location_type': location.location_type,
                'capacity': location.capacity or location.pallet_capacity or 1,
                'pallet_capacity': location.pallet_capacity or location.capacity or 1,
                'zone': location.zone,
                'warehouse_id': location.warehouse_id,
                'aisle_number': location.aisle_number,
                'rack_number': location.rack_number,
                'position_number': location.position_number,
                'level': location.level,
                'is_active': location.is_active,
                'source': 'physical'
            }
            
        except Exception as e:
            if self.debug_compatibility:
                print(f"[VIRTUAL_COMPAT] Physical location lookup failed: {e}")
            return None
    
    def get_all_warehouse_locations(self, warehouse_id: str) -> List[Dict[str, Any]]:
        """
        Get all locations for a warehouse (virtual or physical)
        
        WARNING: For virtual warehouses with large location spaces, this could
        return millions of locations. Use with caution or implement pagination.
        """
        if self.debug_compatibility:
            print(f"[VIRTUAL_COMPAT] Getting all locations for warehouse '{warehouse_id}'")
        
        # Check if this is a virtual warehouse
        if self.enable_virtual_locations:
            virtual_engine = get_virtual_engine_for_warehouse(warehouse_id)
            if virtual_engine:
                return self._get_all_virtual_locations(virtual_engine, limit=1000)  # Safety limit
        
        # Fall back to physical locations
        return self._get_all_physical_locations(warehouse_id)
    
    def _get_all_virtual_locations(self, virtual_engine, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Generate a representative sample of virtual locations
        
        NOTE: For large virtual warehouses, we don't generate ALL possible locations
        as that could be millions. Instead, we return a sample or specific locations.
        PRIORITY: Special areas are ALWAYS included and generated first
        """
        locations = []
        
        # Add all special areas FIRST (these are finite and essential for UI)
        warehouse_summary = virtual_engine.get_warehouse_summary()
        
        # Add special areas (these are finite and manageable) - PRIORITY FOR UI
        for special_area in warehouse_summary.get('special_areas_list', []):
            properties = virtual_engine.get_location_properties(special_area)
            if properties and properties.is_valid:
                locations.append({
                    'id': hash(properties.code),  # Add ID for frontend compatibility
                    'code': properties.code,
                    'location_type': properties.location_type,
                    'capacity': properties.capacity,
                    'pallet_capacity': properties.capacity,
                    'zone': properties.zone,
                    'warehouse_id': virtual_engine.warehouse_id,
                    'aisle_number': properties.aisle_number,
                    'rack_number': None,  # Virtual engine uses rack_identifier
                    'position_number': properties.position_number,
                    'level': properties.level,
                    'is_storage_location': False,  # Special areas are not storage
                    'full_address': f"Special Area: {properties.code}",
                    'is_active': True,
                    'created_at': '2025-01-01T00:00:00Z',  # Default timestamp
                    'source': 'virtual_special'
                })
        
        # Add a sample of storage locations (not all - that could be millions!)
        storage_sample = self._generate_storage_location_sample(virtual_engine, limit - len(locations))
        locations.extend(storage_sample)
        
        if self.debug_compatibility:
            print(f"[VIRTUAL_COMPAT] Generated {len(locations)} virtual locations (sample)")
        
        return locations
    
    def _generate_storage_location_sample(self, virtual_engine, limit: int) -> List[Dict[str, Any]]:
        """Generate a representative sample of storage locations"""
        sample_locations = []
        warehouse_summary = virtual_engine.get_warehouse_summary()
        dims = warehouse_summary['warehouse_dimensions']
        
        # Generate sample locations across the warehouse space
        aisles = min(dims['aisles'], 3)  # Sample first 3 aisles
        racks = min(dims['racks_per_aisle'], 2)  # Sample first 2 racks per aisle
        positions = min(dims['positions_per_rack'], 10)  # Sample first 10 positions per rack
        levels = min(dims['levels_per_position'], 4)  # All levels
        
        count = 0
        for aisle in range(1, aisles + 1):
            for rack_idx in range(racks):
                rack = chr(ord('A') + rack_idx)  # A, B, C...
                for position in range(1, positions + 1):
                    for level_idx in range(levels):
                        level = chr(ord('A') + level_idx)  # A, B, C, D
                        
                        if count >= limit:
                            break
                        
                        # Generate location code in expected format
                        location_code = f"{aisle:02d}-{rack}{position:02d}-{level}"
                        properties = virtual_engine.get_location_properties(location_code)
                        
                        if properties and properties.is_valid:
                            sample_locations.append({
                                'id': hash(properties.code),  # Add ID for frontend compatibility
                                'code': properties.code,
                                'location_type': properties.location_type,
                                'capacity': properties.capacity,
                                'pallet_capacity': properties.capacity,
                                'zone': properties.zone,
                                'warehouse_id': virtual_engine.warehouse_id,
                                'aisle_number': properties.aisle_number,
                                'rack_number': None,  # Virtual uses rack_identifier
                                'position_number': properties.position_number,
                                'level': properties.level,
                                'is_storage_location': True,  # Storage locations
                                'full_address': f"A{properties.aisle_number:02d}-{properties.rack_identifier}{properties.position_number:02d}-{properties.level}",
                                'is_active': True,
                                'created_at': '2025-01-01T00:00:00Z',  # Default timestamp
                                'source': 'virtual_sample'
                            })
                            count += 1
        
        return sample_locations
    
    def _get_all_physical_locations(self, warehouse_id: str) -> List[Dict[str, Any]]:
        """Get all physical locations from database"""
        try:
            locations = Location.query.filter_by(warehouse_id=warehouse_id).all()
            
            return [{
                'code': loc.code,
                'location_type': loc.location_type,
                'capacity': loc.capacity or loc.pallet_capacity or 1,
                'pallet_capacity': loc.pallet_capacity or loc.capacity or 1,
                'zone': loc.zone,
                'warehouse_id': loc.warehouse_id,
                'aisle_number': loc.aisle_number,
                'rack_number': loc.rack_number,
                'position_number': loc.position_number,
                'level': loc.level,
                'is_active': loc.is_active,
                'source': 'physical'
            } for loc in locations]
            
        except Exception as e:
            if self.debug_compatibility:
                print(f"[VIRTUAL_COMPAT] Failed to get physical locations: {e}")
            return []
    
    def is_virtual_warehouse(self, warehouse_id: str) -> bool:
        """Check if warehouse is using virtual locations"""
        try:
            # Check if warehouse has WarehouseConfig - if so, treat as virtual by default
            config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            if not config:
                if self.debug_compatibility:
                    print(f"[VIRTUAL_COMPAT] No config found for {warehouse_id} - not virtual")
                return False
            
            # NEW LOGIC: If warehouse has config, prioritize virtual locations
            # This ensures consistent behavior for special locations
            if self.debug_compatibility:
                print(f"[VIRTUAL_COMPAT] Warehouse {warehouse_id} has config - treating as virtual")
            
            physical_count = Location.query.filter_by(warehouse_id=warehouse_id).count()
            expected_locations = (config.num_aisles * config.racks_per_aisle * 
                                config.positions_per_rack * config.levels_per_position)
            
            # NEW: Always prefer virtual for warehouses with configs unless explicitly legacy
            # You can set FORCE_PHYSICAL_MODE=true in environment to disable this
            force_physical = os.environ.get('FORCE_PHYSICAL_MODE', 'false').lower() == 'true'
            
            if force_physical:
                if self.debug_compatibility:
                    print(f"[VIRTUAL_COMPAT] FORCE_PHYSICAL_MODE enabled - using physical locations")
                return False
            
            # Default: treat warehouses with configs as virtual
            return True
            
        except Exception as e:
            if self.debug_compatibility:
                print(f"[VIRTUAL_COMPAT] Error checking virtual status: {e}")
            return False
    
    def get_warehouse_statistics(self, warehouse_id: str) -> Dict[str, Any]:
        """Get comprehensive warehouse statistics"""
        stats = {
            'warehouse_id': warehouse_id,
            'is_virtual': self.is_virtual_warehouse(warehouse_id),
            'physical_location_count': 0,
            'virtual_location_count': 0,
            'has_configuration': False
        }
        
        try:
            # Check for warehouse configuration
            config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            stats['has_configuration'] = config is not None
            
            # Count physical locations
            stats['physical_location_count'] = Location.query.filter_by(warehouse_id=warehouse_id).count()
            
            # Calculate virtual locations if applicable
            if stats['is_virtual'] and config:
                virtual_engine = get_virtual_engine_for_warehouse(warehouse_id)
                if virtual_engine:
                    warehouse_summary = virtual_engine.get_warehouse_summary()
                    stats['virtual_location_count'] = warehouse_summary['total_possible_locations']
                    stats['virtual_storage_locations'] = warehouse_summary['storage_locations']
                    stats['virtual_special_areas'] = warehouse_summary['special_areas']
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats


# Global instance for easy access
compatibility_manager = VirtualLocationCompatibilityManager()


def get_compatibility_manager():
    """Get the global compatibility manager instance"""
    return compatibility_manager


def get_location_by_code_compat(warehouse_id: str, location_code: str) -> Optional[Dict[str, Any]]:
    """Convenience function for location lookup with compatibility"""
    return compatibility_manager.get_location_by_code(warehouse_id, location_code)


def is_virtual_warehouse_compat(warehouse_id: str) -> bool:
    """Convenience function to check if warehouse is virtual"""
    return compatibility_manager.is_virtual_warehouse(warehouse_id)