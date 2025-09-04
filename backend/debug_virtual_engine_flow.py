#!/usr/bin/env python3
"""
Deep Investigation: Virtual Engine Smart Configuration Data Flow
Comprehensive trace from template creation to rule evaluation
"""

import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def trace_template_to_virtual_engine():
    """Trace the complete data flow from template to virtual engine"""
    
    print("=" * 80)
    print("DEEP INVESTIGATION: Virtual Engine Smart Configuration Data Flow")
    print("=" * 80)
    
    try:
        from app import app
        from database import db
        from models import WarehouseTemplate, WarehouseConfig
        from core_models import User
        from virtual_template_integration import get_virtual_engine_for_warehouse
        from virtual_location_engine import VirtualLocationEngine
        
        with app.app_context():
            # Step 1: Get the template with format configuration
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
            
            print(f"\n[STEP 1] TEMPLATE ANALYSIS")
            print(f"Template: {template.name} (ID: {template.id})")
            print(f"Template Code: {template.template_code}")
            
            # Parse the format configuration
            format_config = None
            if template.location_format_config:
                try:
                    format_config = json.loads(template.location_format_config)
                    print(f"[OK] Format Config Found:")
                    print(f"   Pattern Type: {format_config.get('pattern_type')}")
                    print(f"   Regex Pattern: {format_config.get('regex_pattern')}")
                    print(f"   Examples: {format_config.get('examples')}")
                    print(f"   Confidence: {format_config.get('confidence', template.format_confidence)}")
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Format Config JSON Parse Error: {e}")
                    format_config = None
            else:
                print("[ERROR] No format configuration found in template")
            
            # Step 2: Check how template gets applied to warehouse config
            print(f"\n[STEP 2] WAREHOUSE CONFIG ANALYSIS")
            warehouse_id = "DEFAULT"  # This is what's used in the logs
            
            warehouse_config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            
            if warehouse_config:
                print(f"[OK] WarehouseConfig found for warehouse_id: {warehouse_id}")
                config_dict = warehouse_config.to_dict()
                print(f"   Config keys: {list(config_dict.keys())}")
                
                # CRITICAL CHECK: Does warehouse config have format configuration?
                if 'location_format_config' in config_dict:
                    wh_format_config = config_dict['location_format_config']
                    print(f"   [OK] Warehouse has location_format_config: {type(wh_format_config)}")
                    if wh_format_config:
                        try:
                            if isinstance(wh_format_config, str):
                                parsed_wh_config = json.loads(wh_format_config)
                            else:
                                parsed_wh_config = wh_format_config
                            print(f"      Pattern: {parsed_wh_config.get('pattern_type')}")
                            print(f"      Regex: {parsed_wh_config.get('regex_pattern')}")
                        except Exception as e:
                            print(f"      [ERROR] Error parsing warehouse format config: {e}")
                    else:
                        print(f"      [ERROR] Warehouse format config is empty/null")
                else:
                    print(f"   [ERROR] Warehouse config missing location_format_config field")
                    
                    # Check if template format should be copied to warehouse config
                    print(f"\n[CRITICAL ISSUE CHECK] Template vs Warehouse Config Sync")
                    if format_config and not config_dict.get('location_format_config'):
                        print(f"   [ISSUE FOUND] Template has format config but warehouse config doesn't!")
                        print(f"   Template format: {format_config.get('pattern_type')}")
                        print(f"   Warehouse format: None")
                        print(f"   This explains why virtual engine can't access smart configuration")
            else:
                print(f"[ERROR] No WarehouseConfig found for warehouse_id: {warehouse_id}")
                print(f"   This is a major issue - templates should create warehouse configs")
            
            # Step 3: Test virtual engine creation
            print(f"\n[STEP 3] VIRTUAL ENGINE CREATION TEST")
            
            try:
                virtual_engine = get_virtual_engine_for_warehouse(warehouse_id)
                if virtual_engine:
                    print(f"[OK] Virtual engine created successfully")
                    print(f"   Engine type: {type(virtual_engine)}")
                    print(f"   Warehouse ID: {virtual_engine.warehouse_id}")
                    
                    # Check if virtual engine has format configuration
                    if hasattr(virtual_engine, 'location_format_config'):
                        engine_format = virtual_engine.location_format_config
                        print(f"   Format config in engine: {bool(engine_format)}")
                        if engine_format:
                            print(f"      Pattern: {engine_format.get('pattern_type')}")
                            print(f"      Regex: {engine_format.get('regex_pattern')}")
                        else:
                            print(f"      [ERROR] Virtual engine has no format configuration!")
                    else:
                        print(f"   [ERROR] Virtual engine missing location_format_config attribute!")
                    
                    # Test location validation with the engine
                    print(f"\n[STEP 4] LOCATION VALIDATION TEST")
                    test_locations = ['006B', '010A', '325B', '245D']
                    
                    for location in test_locations:
                        is_valid, reason = virtual_engine.validate_location(location)
                        status = "[OK]" if is_valid else "[ERROR]"
                        print(f"   {status} '{location}': {reason}")
                        
                        if not is_valid:
                            print(f"      Location '{location}' should be valid for position_level format!")
                
                else:
                    print(f"[ERROR] Failed to create virtual engine for warehouse {warehouse_id}")
                    
            except Exception as e:
                print(f"[ERROR] Error creating virtual engine: {e}")
                import traceback
                traceback.print_exc()
            
            # Step 4: Identify the exact data flow break point
            print(f"\n[STEP 5] DATA FLOW BREAK POINT ANALYSIS")
            
            flow_checks = [
                ("Template has format config", bool(template.location_format_config)),
                ("Template format confidence > 0", bool(template.format_confidence)),
                ("WarehouseConfig exists", bool(warehouse_config)),
                ("WarehouseConfig has format", bool(warehouse_config and warehouse_config.to_dict().get('location_format_config')) if warehouse_config else False),
                ("Virtual engine created", bool(virtual_engine) if 'virtual_engine' in locals() else False),
                ("Virtual engine has format", bool(virtual_engine and getattr(virtual_engine, 'location_format_config', None)) if 'virtual_engine' in locals() else False)
            ]
            
            print("Data Flow Integrity Check:")
            for check_name, result in flow_checks:
                status = "[OK]" if result else "[ERROR]"
                print(f"   {status} {check_name}")
            
            # Find the first failure point
            failure_points = [check for check, result in flow_checks if not result]
            if failure_points:
                print(f"\n[CRITICAL ISSUE IDENTIFIED]:")
                print(f"   First failure: {failure_points[0]}")
                print(f"   This is where the data flow breaks!")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = trace_template_to_virtual_engine()
    
    if success:
        print(f"\n" + "=" * 80)
        print("INVESTIGATION COMPLETED")
        print("Check the analysis above for data flow break points")
        print("=" * 80)
    else:
        print(f"\n" + "=" * 80)
        print("INVESTIGATION FAILED - Check error messages above")
        print("=" * 80)