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
            
            # Step 4: ENHANCED - Create physical special location records with error tracking
            special_locations_result = self._create_physical_special_locations(
                template, warehouse_id, current_user
            )
            
            # Step 5: Handle potential failures and provide user feedback
            if special_locations_result['failure_count'] > 0:
                print(f"[VIRTUAL_TEMPLATE] ⚠️ WARNING: {special_locations_result['failure_count']} locations failed to create:")
                for error in special_locations_result['error_summary']:
                    print(f"[VIRTUAL_TEMPLATE]   - {error}")
            
            # Step 6: Increment template usage (only if no critical errors)
            if not special_locations_result.get('critical_error', False):
                template.increment_usage()
            
            return {
                'success': True,
                'warehouse_id': warehouse_id,
                'configuration': config_dict,
                'virtual_location_summary': virtual_summary,
                'template_code': template.template_code,
                'creation_method': 'hybrid_virtual_with_physical_special_areas',
                'locations_created': special_locations_result['success_count'],  # Successful locations only
                'locations_failed': special_locations_result['failure_count'],    # NEW: Failed count
                'failed_locations': special_locations_result['failed_locations'], # NEW: Detailed failures
                'virtual_locations_available': virtual_summary['total_possible_locations'],
                'special_areas': special_locations_result['success_count'],
                'location_creation_summary': {
                    'expected': special_locations_result['total_expected'],
                    'processed': special_locations_result['total_processed'],  
                    'successful': special_locations_result['success_count'],
                    'failed': special_locations_result['failure_count'],
                    'error_details': special_locations_result['error_summary']
                }
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
        
        # CRITICAL FIX: Copy smart configuration format fields from template
        # This ensures virtual engines have access to format configuration
        if template.location_format_config:
            print(f"[VIRTUAL_TEMPLATE] Copying format configuration from template to warehouse config")
            config.location_format_config = template.location_format_config
            config.format_confidence = template.format_confidence
            config.format_examples = template.format_examples
            config.format_learned_date = template.format_learned_date or datetime.utcnow()
            
            # Parse and log format details for debugging
            try:
                import json
                format_config = json.loads(template.location_format_config)
                pattern_type = format_config.get('pattern_type', 'unknown')
                confidence = template.format_confidence or 0
                print(f"[VIRTUAL_TEMPLATE] Format: {pattern_type} (confidence: {confidence:.1%})")
            except (json.JSONDecodeError, TypeError):
                print(f"[VIRTUAL_TEMPLATE] Format configuration copied (parsing failed)")
        else:
            print(f"[VIRTUAL_TEMPLATE] No format configuration to copy from template")
        
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
        
        Enhanced with comprehensive error detection and reporting.
        
        Returns:
            dict: {
                'created_locations': list,
                'failed_locations': list,
                'success_count': int,
                'failure_count': int,
                'error_summary': list
            }
        """
        created_special_locations = []
        failed_locations = []
        error_summary = []
        
        try:
            print(f"[VIRTUAL_TEMPLATE] Creating physical special area locations for warehouse {warehouse_id}")
            
            # Remove existing special locations for this warehouse to prevent duplicates
            existing_special = Location.query.filter(
                Location.warehouse_id == warehouse_id,
                Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL'])
            ).all()
            
            if existing_special:
                print(f"[VIRTUAL_TEMPLATE] Removing {len(existing_special)} existing special locations for clean setup")
                for loc in existing_special:
                    print(f"[VIRTUAL_TEMPLATE] Deleting existing location: {loc.code} ({loc.location_type})")
                    db.session.delete(loc)
                
                # Flush deletions before creating new locations
                db.session.flush()
                print(f"[VIRTUAL_TEMPLATE] Successfully removed {len(existing_special)} existing locations")
            else:
                print("[VIRTUAL_TEMPLATE] No existing special locations to remove")
            
            # Process each type of special area from template
            special_area_configs = [
                (template.receiving_areas_template, 'RECEIVING', 'DOCK', 10),
                (template.staging_areas_template, 'STAGING', 'STAGING', 5),
                (template.dock_areas_template, 'DOCK', 'DOCK', 2)
            ]
            
            # CRITICAL FIX: Add AISLE locations (TRANSITIONAL type) for warehouse aisles
            # This matches the logic from template_api.py lines 87-98
            if hasattr(template, 'num_aisles') and template.num_aisles > 0:
                aisle_locations_data = []
                for aisle_num in range(1, template.num_aisles + 1):
                    aisle_locations_data.append({
                        'code': f'AISLE-{aisle_num:02d}',
                        'capacity': 10,  # Temporary capacity for pallets in transit
                        'zone': 'GENERAL'
                    })
                
                # Add AISLE locations as TRANSITIONAL type
                special_area_configs.append((json.dumps(aisle_locations_data), 'TRANSITIONAL', 'GENERAL', 10))
                print(f"[VIRTUAL_TEMPLATE] Added {len(aisle_locations_data)} AISLE locations for {template.num_aisles} aisles")
            
            # ENHANCED ERROR DETECTION: Process each area type with comprehensive tracking
            total_expected_locations = 0
            total_processed_locations = 0
            
            for areas_template, location_type, default_zone, default_capacity in special_area_configs:
                if not areas_template:
                    print(f"[VIRTUAL_TEMPLATE] No {location_type} areas defined in template")
                    continue
                    
                try:
                    areas = json.loads(areas_template) if isinstance(areas_template, str) else areas_template
                    area_count = len(areas)
                    total_expected_locations += area_count
                    print(f"[VIRTUAL_TEMPLATE] Processing {area_count} {location_type} areas")
                    
                    locations_created_for_type = 0
                    locations_failed_for_type = 0
                    
                    for area_index, area_data in enumerate(areas):
                        location_code = area_data.get('code', f'{location_type}_{area_index + 1}')
                        total_processed_locations += 1
                        
                        # ENHANCED VALIDATION: Check for problematic location codes
                        validation_errors = []
                        
                        if not location_code or not location_code.strip():
                            validation_errors.append("Location code is empty")
                        elif len(location_code.strip()) > 50:  # Database column limit
                            validation_errors.append(f"Location code too long ({len(location_code)} chars, max 50)")
                        elif location_code.strip() != location_code:
                            validation_errors.append("Location code has leading/trailing whitespace")
                        
                        if validation_errors:
                            error_msg = f"Validation failed for {location_code}: {'; '.join(validation_errors)}"
                            print(f"[VIRTUAL_TEMPLATE] ❌ VALIDATION ERROR: {error_msg}")
                            failed_locations.append({
                                'code': location_code,
                                'type': location_type,
                                'error': error_msg,
                                'stage': 'validation'
                            })
                            error_summary.append(error_msg)
                            locations_failed_for_type += 1
                            continue
                        
                        # ENHANCED DUPLICATE CHECK with detailed logging
                        existing_check = Location.query.filter(
                            Location.code == location_code.strip(),
                            Location.warehouse_id == warehouse_id
                        ).first()
                        
                        if existing_check:
                            error_msg = f"Location {location_code} already exists (ID: {existing_check.id})"
                            print(f"[VIRTUAL_TEMPLATE] ❌ DUPLICATE ERROR: {error_msg}")
                            failed_locations.append({
                                'code': location_code,
                                'type': location_type,
                                'error': error_msg,
                                'stage': 'duplicate_check'
                            })
                            error_summary.append(error_msg)
                            locations_failed_for_type += 1
                            continue
                        
                        # ENHANCED LOCATION CREATION with detailed error capture
                        try:
                            location = Location(
                                code=location_code.strip(),
                                location_type=location_type,
                                capacity=area_data.get('capacity', default_capacity),
                                pallet_capacity=area_data.get('capacity', default_capacity),
                                zone=area_data.get('zone', default_zone),
                                warehouse_id=warehouse_id,
                                created_by=current_user.id,
                                is_active=True
                            )
                            
                            # TRANSACTION SAFETY: Add to session and flush for validation
                            db.session.add(location)
                            db.session.flush()  # Get database validation without committing
                            
                            created_special_locations.append(location)
                            locations_created_for_type += 1
                            print(f"[VIRTUAL_TEMPLATE] ✅ Created: {location.code} ({location_type}) capacity={location.capacity}")
                            
                        except Exception as creation_error:
                            # DETAILED ERROR ANALYSIS
                            error_type = type(creation_error).__name__
                            error_msg = f"Failed to create {location_code} ({location_type}): {error_type} - {str(creation_error)}"
                            
                            print(f"[VIRTUAL_TEMPLATE] ❌ CREATION ERROR: {error_msg}")
                            failed_locations.append({
                                'code': location_code,
                                'type': location_type,
                                'error': error_msg,
                                'stage': 'database_creation',
                                'exception_type': error_type
                            })
                            error_summary.append(error_msg)
                            locations_failed_for_type += 1
                            
                            # Rollback the failed transaction
                            db.session.rollback()
                    
                    print(f"[VIRTUAL_TEMPLATE] {location_type} SUMMARY: ✅ {locations_created_for_type} created, ❌ {locations_failed_for_type} failed")
                        
                except (json.JSONDecodeError, TypeError) as json_error:
                    error_msg = f"JSON processing error for {location_type} areas: {str(json_error)}"
                    print(f"[VIRTUAL_TEMPLATE] ❌ JSON ERROR: {error_msg}")
                    error_summary.append(error_msg)
                    
                    # Count all locations in this type as failed
                    try:
                        failed_count = len(json.loads(areas_template)) if isinstance(areas_template, str) else len(areas_template)
                        for i in range(failed_count):
                            failed_locations.append({
                                'code': f'{location_type}_AREA_{i+1}',
                                'type': location_type,
                                'error': error_msg,
                                'stage': 'json_parsing'
                            })
                    except:
                        failed_locations.append({
                            'code': f'{location_type}_AREAS',
                            'type': location_type,
                            'error': error_msg,
                            'stage': 'json_parsing'
                        })
            
            # FINAL SUMMARY AND REPORTING
            success_count = len(created_special_locations)
            failure_count = len(failed_locations)
            
            print(f"[VIRTUAL_TEMPLATE] ==================== SPECIAL LOCATION CREATION SUMMARY ====================")
            print(f"[VIRTUAL_TEMPLATE] Expected: {total_expected_locations}")
            print(f"[VIRTUAL_TEMPLATE] Processed: {total_processed_locations}")
            print(f"[VIRTUAL_TEMPLATE] ✅ Created: {success_count}")
            print(f"[VIRTUAL_TEMPLATE] ❌ Failed: {failure_count}")
            
            if failed_locations:
                print(f"[VIRTUAL_TEMPLATE] FAILED LOCATIONS DETAILS:")
                for failed in failed_locations:
                    print(f"[VIRTUAL_TEMPLATE]   ❌ {failed['code']} ({failed['type']}) - {failed['error']}")
            
            # Flush but don't commit yet (will be committed by caller)
            if success_count > 0:
                db.session.flush()
                print(f"[VIRTUAL_TEMPLATE] Successfully prepared {success_count} special locations for commit")
            
            # ENHANCED RETURN: Detailed results for caller analysis
            return {
                'created_locations': created_special_locations,
                'failed_locations': failed_locations,
                'success_count': success_count,
                'failure_count': failure_count,
                'error_summary': error_summary,
                'total_expected': total_expected_locations,
                'total_processed': total_processed_locations
            }
            
        except Exception as e:
            error_msg = f"Critical error creating physical special locations: {str(e)}"
            print(f"[VIRTUAL_TEMPLATE] ❌ CRITICAL ERROR: {error_msg}")
            error_summary.append(error_msg)
            
            # Return error result structure
            return {
                'created_locations': created_special_locations,
                'failed_locations': failed_locations + [{'code': 'SYSTEM_ERROR', 'type': 'ALL', 'error': error_msg, 'stage': 'system_exception'}],
                'success_count': len(created_special_locations),
                'failure_count': len(failed_locations) + 1,
                'error_summary': error_summary,
                'total_expected': 0,
                'total_processed': 0,
                'critical_error': True
            }
    
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