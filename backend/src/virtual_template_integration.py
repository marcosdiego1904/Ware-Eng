"""
Virtual Location Integration for Template System
Enhances the template API to work with virtual locations while maintaining backwards compatibility
"""

import json
from datetime import datetime
from flask import current_app
from database import db
from models import WarehouseConfig, WarehouseTemplate, Location
from virtual_location_engine import create_virtual_engine_from_warehouse_config


class VirtualTemplateManager:
    """
    Manages template application with virtual location integration
    
    KEY INTEGRATION: This class bridges template creation with virtual location engine
    """
    
    def __init__(self):
        self.use_virtual_locations = True  # Feature flag for gradual rollout
    
    def apply_template_with_virtual_locations(self, template, warehouse_id, warehouse_name, current_user, customizations=None):
        """
        Apply template creating WarehouseConfig but NO physical location records
        
        CRITICAL: This is the new template application process that creates virtual locations
        
        Returns:
            dict: Application results with virtual location summary
        """
        try:
            print(f"[VIRTUAL_TEMPLATE] Applying template '{template.name}' to warehouse '{warehouse_id}'")
            
            # Step 1: Create or update WarehouseConfig (same as before)
            config = self._create_or_update_warehouse_config(
                template, warehouse_id, warehouse_name, current_user, customizations
            )
            
            # Step 2: Create virtual location engine from config
            config_dict = config.to_dict()
            virtual_engine = create_virtual_engine_from_warehouse_config(config_dict)
            
            # Step 3: Store virtual engine metadata (for debugging and metrics)
            virtual_summary = virtual_engine.get_warehouse_summary()
            
            db.session.commit()
            
            print(f"[VIRTUAL_TEMPLATE] Virtual warehouse created successfully:")
            print(f"  - Total virtual locations: {virtual_summary['total_possible_locations']:,}")
            print(f"  - Storage locations: {virtual_summary['storage_locations']:,}")
            print(f"  - Special areas: {virtual_summary['special_areas']}")
            
            # Step 4: CRITICAL FIX - Create physical special location records
            # This allows Special Areas Management UI to display them
            special_locations_created = self._create_physical_special_locations(
                template, warehouse_id, current_user
            )
            
            # Step 5: Increment template usage
            template.increment_usage()
            
            return {
                'success': True,
                'warehouse_id': warehouse_id,
                'configuration': config_dict,
                'virtual_location_summary': virtual_summary,
                'template_code': template.template_code,
                'creation_method': 'hybrid_virtual_with_physical_special_areas',
                'locations_created': len(special_locations_created),  # Physical special locations
                'virtual_locations_available': virtual_summary['total_possible_locations'],
                'special_areas': len(special_locations_created)
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Virtual template application failed: {str(e)}")
            raise
    
    def apply_template_legacy_mode(self, template, warehouse_id, warehouse_name, current_user, customizations=None):
        """
        Legacy template application with physical location generation
        
        This method maintains the old behavior for backwards compatibility
        """
        print(f"[VIRTUAL_TEMPLATE] Applying template in LEGACY mode (creating physical locations)")
        
        # Import the original function from template_api
        from template_api import generate_locations_from_template
        
        # Create warehouse config
        config = self._create_or_update_warehouse_config(
            template, warehouse_id, warehouse_name, current_user, customizations
        )
        
        # Generate physical locations (old method)
        created_locations = generate_locations_from_template(template, warehouse_id, current_user)
        
        db.session.commit()
        
        template.increment_usage()
        
        return {
            'success': True,
            'warehouse_id': warehouse_id,
            'configuration': config.to_dict(),
            'template_code': template.template_code,
            'creation_method': 'physical_locations',
            'locations_created': len(created_locations),
            'storage_locations': len([loc for loc in created_locations if loc.location_type == 'STORAGE']),
            'special_areas': len([loc for loc in created_locations if loc.location_type != 'STORAGE'])
        }
    
    def _create_or_update_warehouse_config(self, template, warehouse_id, warehouse_name, current_user, customizations):
        """
        Create or update WarehouseConfig record
        
        This is shared logic between virtual and legacy modes
        """
        # Check if warehouse already exists
        existing_config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
        
        if existing_config:
            # Update existing configuration
            config = existing_config
            
            # CRITICAL: Clear existing physical locations if they exist
            # This prevents hybrid scenarios where some locations are physical and others virtual
            if self.use_virtual_locations:
                existing_locations_count = Location.query.filter_by(warehouse_id=warehouse_id).count()
                if existing_locations_count > 0:
                    print(f"[VIRTUAL_TEMPLATE] Removing {existing_locations_count} existing physical locations")
                    Location.query.filter_by(warehouse_id=warehouse_id).delete()
                    db.session.flush()
        else:
            # Create new warehouse configuration
            config = WarehouseConfig(warehouse_id=warehouse_id, created_by=current_user.id)
            db.session.add(config)
        
        # Copy template configuration to warehouse config
        config.warehouse_name = warehouse_name
        config.num_aisles = template.num_aisles
        config.racks_per_aisle = template.racks_per_aisle
        config.positions_per_rack = template.positions_per_rack
        config.levels_per_position = template.levels_per_position
        config.level_names = template.level_names
        config.default_pallet_capacity = template.default_pallet_capacity
        config.bidimensional_racks = template.bidimensional_racks
        config.receiving_areas = template.receiving_areas_template
        config.staging_areas = template.staging_areas_template
        config.dock_areas = template.dock_areas_template
        config.updated_at = datetime.utcnow()
        
        # Apply any customizations
        if customizations:
            for field, value in customizations.items():
                if hasattr(config, field):
                    setattr(config, field, value)
                    print(f"[VIRTUAL_TEMPLATE] Applied customization: {field} = {value}")
        
        return config
    
    def _create_physical_special_locations(self, template, warehouse_id, current_user):
        """
        Create physical location records for special areas only
        
        This is the HYBRID ARCHITECTURE FIX - special areas as physical records
        while keeping storage locations virtual for performance.
        
        Returns:
            list: Created location objects
        """
        created_special_locations = []
        
        try:
            print(f"[VIRTUAL_TEMPLATE] Creating physical special area locations for warehouse {warehouse_id}")
            
            # Remove any existing special locations for this warehouse to prevent duplicates
            existing_special = Location.query.filter(
                Location.warehouse_id == warehouse_id,
                Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL'])
            ).all()
            
            if existing_special:
                print(f"[VIRTUAL_TEMPLATE] Removing {len(existing_special)} existing special locations")
                for loc in existing_special:
                    db.session.delete(loc)
                db.session.flush()
            
            # Process each type of special area from template
            special_area_configs = [
                (template.receiving_areas_template, 'RECEIVING', 'DOCK', 10),
                (template.staging_areas_template, 'STAGING', 'STAGING', 5),
                (template.dock_areas_template, 'DOCK', 'DOCK', 2)
            ]
            
            for areas_template, location_type, default_zone, default_capacity in special_area_configs:
                if not areas_template:
                    continue
                    
                try:
                    areas = json.loads(areas_template) if isinstance(areas_template, str) else areas_template
                    print(f"[VIRTUAL_TEMPLATE] Processing {len(areas)} {location_type} areas")
                    
                    for area_data in areas:
                        # Create physical special location record
                        location = Location(
                            code=area_data.get('code', f'{location_type}_1'),
                            location_type=location_type,
                            capacity=area_data.get('capacity', default_capacity),
                            pallet_capacity=area_data.get('capacity', default_capacity),
                            zone=area_data.get('zone', default_zone),
                            warehouse_id=warehouse_id,
                            created_by=current_user.id,
                            is_active=True
                        )
                        
                        db.session.add(location)
                        created_special_locations.append(location)
                        print(f"[VIRTUAL_TEMPLATE] Created special location: {location.code} ({location_type})")
                        
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"[VIRTUAL_TEMPLATE] Error processing {location_type} areas: {e}")
                    continue
            
            # Flush but don't commit yet (will be committed by caller)
            db.session.flush()
            
            print(f"[VIRTUAL_TEMPLATE] Successfully prepared {len(created_special_locations)} special locations")
            return created_special_locations
            
        except Exception as e:
            current_app.logger.error(f"Error creating physical special locations: {e}")
            # Don't rollback here, let the caller handle it
            return []
    
    def get_virtual_location_engine_for_warehouse(self, warehouse_id):
        """
        Create virtual location engine for existing warehouse
        
        This method is used by rule evaluators to get virtual location validation
        """
        try:
            config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            if not config:
                print(f"[VIRTUAL_TEMPLATE] No configuration found for warehouse {warehouse_id}")
                return None
            
            config_dict = config.to_dict()
            virtual_engine = create_virtual_engine_from_warehouse_config(config_dict)
            
            print(f"[VIRTUAL_TEMPLATE] Created virtual engine for warehouse {warehouse_id}")
            return virtual_engine
            
        except Exception as e:
            print(f"[VIRTUAL_TEMPLATE] Failed to create virtual engine for {warehouse_id}: {e}")
            return None
    
    def validate_template_configuration(self, template_config):
        """
        Validate template configuration before creating virtual locations
        
        This ensures the template will generate a valid virtual location universe
        """
        errors = []
        warnings = []
        
        # Required fields validation
        required_fields = ['num_aisles', 'racks_per_aisle', 'positions_per_rack', 'levels_per_position']
        for field in required_fields:
            if field not in template_config or template_config[field] <= 0:
                errors.append(f"Invalid {field}: must be positive integer")
        
        # Reasonable bounds checking
        if template_config.get('num_aisles', 0) > 100:
            warnings.append("Large number of aisles may impact performance")
        
        if template_config.get('positions_per_rack', 0) > 1000:
            warnings.append("Very large rack capacity - ensure this is correct")
        
        # Calculate total locations for memory estimation
        total_locations = (template_config.get('num_aisles', 1) * 
                         template_config.get('racks_per_aisle', 1) * 
                         template_config.get('positions_per_rack', 1) * 
                         template_config.get('levels_per_position', 1))
        
        if total_locations > 1000000:  # 1 million locations
            warnings.append(f"Very large warehouse ({total_locations:,} locations) - consider splitting")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'estimated_locations': total_locations
        }


class VirtualLocationCache:
    """
    Cache for virtual location engines to avoid recreating them repeatedly
    """
    
    def __init__(self):
        self._engine_cache = {}
        self._cache_timestamps = {}
        self.cache_ttl_seconds = 3600  # 1 hour cache TTL
    
    def get_engine(self, warehouse_id):
        """Get cached virtual engine or create new one"""
        now = datetime.utcnow().timestamp()
        
        # Check if we have a fresh cached engine
        if (warehouse_id in self._engine_cache and 
            warehouse_id in self._cache_timestamps and
            (now - self._cache_timestamps[warehouse_id]) < self.cache_ttl_seconds):
            
            return self._engine_cache[warehouse_id]
        
        # Create new engine and cache it
        template_manager = VirtualTemplateManager()
        engine = template_manager.get_virtual_location_engine_for_warehouse(warehouse_id)
        
        if engine:
            self._engine_cache[warehouse_id] = engine
            self._cache_timestamps[warehouse_id] = now
            
        return engine
    
    def clear_cache(self, warehouse_id=None):
        """Clear cache for specific warehouse or all warehouses"""
        if warehouse_id:
            self._engine_cache.pop(warehouse_id, None)
            self._cache_timestamps.pop(warehouse_id, None)
        else:
            self._engine_cache.clear()
            self._cache_timestamps.clear()


# Global instances for easy access
virtual_template_manager = VirtualTemplateManager()
virtual_location_cache = VirtualLocationCache()


def get_virtual_template_manager():
    """Get the global virtual template manager instance"""
    return virtual_template_manager


def get_virtual_engine_for_warehouse(warehouse_id):
    """Convenience function to get virtual location engine for a warehouse"""
    return virtual_location_cache.get_engine(warehouse_id)