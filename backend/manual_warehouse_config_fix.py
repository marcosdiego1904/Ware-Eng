#!/usr/bin/env python3
"""
Manual fix to update existing WarehouseConfig with template format configuration
This simulates what the analysis process fix will do automatically
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def fix_warehouse_config_format():
    """Manually update WarehouseConfig with template format configuration"""
    
    print("=" * 80)
    print("MANUAL FIX: Update WarehouseConfig with Template Format Configuration")
    print("=" * 80)
    
    try:
        from app import app
        from database import db
        from models import WarehouseTemplate, WarehouseConfig
        from core_models import User
        from datetime import datetime
        
        with app.app_context():
            # Get the template with format configuration
            user = User.query.filter_by(username='mtest').first()
            if not user:
                print("[ERROR] User 'mtest' not found")
                return False
            
            template = WarehouseTemplate.query.filter_by(
                created_by=user.id,
                is_active=True
            ).order_by(WarehouseTemplate.updated_at.desc()).first()
            
            if not template:
                print("[ERROR] No active template found")
                return False
            
            print(f"[TEMPLATE] Found template: {template.name} (ID: {template.id})")
            print(f"   Has format config: {bool(template.location_format_config)}")
            print(f"   Format confidence: {template.format_confidence}")
            
            if not template.location_format_config:
                print("[ERROR] Template has no format configuration to copy")
                return False
            
            # Get or create WarehouseConfig for DEFAULT warehouse
            warehouse_id = "DEFAULT"
            warehouse_config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            
            if warehouse_config:
                print(f"[WAREHOUSE_CONFIG] Found existing config for {warehouse_id}")
                print(f"   Current format config: {bool(warehouse_config.location_format_config)}")
            else:
                print(f"[WAREHOUSE_CONFIG] Creating new config for {warehouse_id}")
                warehouse_config = WarehouseConfig(
                    warehouse_id=warehouse_id,
                    warehouse_name=f"Auto-created from template {template.name}",
                    created_by=user.id
                )
                db.session.add(warehouse_config)
            
            # Copy all template configuration to warehouse config
            print("[COPYING] Transferring template configuration to warehouse config...")
            
            warehouse_config.num_aisles = template.num_aisles
            warehouse_config.racks_per_aisle = template.racks_per_aisle  
            warehouse_config.positions_per_rack = template.positions_per_rack
            warehouse_config.levels_per_position = template.levels_per_position
            warehouse_config.level_names = template.level_names
            warehouse_config.default_pallet_capacity = template.default_pallet_capacity
            warehouse_config.bidimensional_racks = template.bidimensional_racks
            warehouse_config.receiving_areas = template.receiving_areas_template
            warehouse_config.staging_areas = template.staging_areas_template
            warehouse_config.dock_areas = template.dock_areas_template
            
            # CRITICAL: Copy format configuration fields
            warehouse_config.location_format_config = template.location_format_config
            warehouse_config.format_confidence = template.format_confidence
            warehouse_config.format_examples = template.format_examples
            warehouse_config.format_learned_date = template.format_learned_date
            warehouse_config.updated_at = datetime.utcnow()
            
            # Commit changes
            db.session.commit()
            
            print(f"[SUCCESS] WarehouseConfig updated successfully!")
            print(f"   Template: {template.name}")
            print(f"   Warehouse ID: {warehouse_id}")
            print(f"   Format config copied: {bool(warehouse_config.location_format_config)}")
            print(f"   Format confidence: {warehouse_config.format_confidence}")
            
            # CRITICAL: Clear virtual engine cache after updating WarehouseConfig
            print(f"[CACHE_CLEAR] Clearing virtual engine cache for {warehouse_id}")
            try:
                from virtual_template_integration import virtual_location_cache
                virtual_location_cache.clear_cache(warehouse_id)
                print(f"[CACHE_CLEAR] Virtual engine cache cleared successfully")
            except Exception as cache_error:
                print(f"[CACHE_CLEAR] Error: Could not clear cache: {cache_error}")
            
            # Verify the fix
            print("\n[VERIFICATION] Testing virtual engine creation...")
            from virtual_template_integration import get_virtual_engine_for_warehouse
            
            virtual_engine = get_virtual_engine_for_warehouse(warehouse_id)
            if virtual_engine:
                print(f"   Virtual engine created: OK")
                engine_has_format = bool(getattr(virtual_engine, 'location_format_config', None))
                print(f"   Engine has format config: {engine_has_format}")
                
                if engine_has_format:
                    # Test location validation
                    test_locations = ['006B', '010A', '325B', '245D']
                    print(f"\n[LOCATION_TEST] Testing position_level format validation:")
                    
                    for location in test_locations:
                        is_valid, reason = virtual_engine.validate_location(location)
                        status = "OK" if is_valid else "ERROR"
                        print(f"   {location}: [{status}] {reason}")
                
            else:
                print(f"   Virtual engine creation failed!")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_warehouse_config_format()
    
    if success:
        print(f"\n" + "=" * 80)
        print("MANUAL FIX COMPLETED SUCCESSFULLY")
        print("The WarehouseConfig now has format configuration from the template")
        print("Virtual engine should now validate locations correctly")
        print("=" * 80)
    else:
        print(f"\n" + "=" * 80)
        print("MANUAL FIX FAILED - Check error messages above")
        print("=" * 80)