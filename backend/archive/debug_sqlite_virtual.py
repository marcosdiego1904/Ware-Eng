#!/usr/bin/env python3
"""
Debug SQLite vs PostgreSQL differences in virtual location detection
"""

import sys
import os
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig
from virtual_compatibility_layer import get_compatibility_manager

def debug_sqlite_warehouses():
    """Debug warehouses in SQLite to see why virtual detection fails"""
    print("DEBUGGING SQLITE VIRTUAL LOCATION DETECTION")
    print("=" * 50)
    
    with app.app_context():
        # Check database type
        db_url = app.config.get('DATABASE_URL', 'sqlite')
        print(f"Database type: {'PostgreSQL' if 'postgresql' in db_url else 'SQLite'}")
        print(f"Database URL: {db_url[:50]}...")
        
        # Get all warehouse configs
        configs = WarehouseConfig.query.all()
        print(f"Total warehouse configs: {len(configs)}")
        print()
        
        compat_manager = get_compatibility_manager()
        
        for config in configs[:5]:  # Check first 5
            print(f"Warehouse: {config.warehouse_id} ({config.warehouse_name})")
            print(f"  Config ID: {config.id}")
            
            # Check raw database values
            print(f"  Raw receiving_areas: {type(config.receiving_areas)} - {config.receiving_areas}")
            print(f"  Raw staging_areas: {type(config.staging_areas)} - {config.staging_areas}")
            print(f"  Raw dock_areas: {type(config.dock_areas)} - {config.dock_areas}")
            
            # Check parsed values
            receiving = config.get_receiving_areas()
            staging = config.get_staging_areas()
            dock = config.get_dock_areas()
            
            print(f"  Parsed receiving: {type(receiving)} - {receiving}")
            print(f"  Parsed staging: {type(staging)} - {staging}")
            print(f"  Parsed dock: {type(dock)} - {dock}")
            
            # Check virtual detection
            is_virtual = compat_manager.is_virtual_warehouse(config.warehouse_id)
            print(f"  Virtual detected: {is_virtual}")
            
            # Check to_dict output
            config_dict = config.to_dict()
            print(f"  Config dict receiving_areas: {type(config_dict.get('receiving_areas'))} - {config_dict.get('receiving_areas')}")
            
            if is_virtual:
                try:
                    # Try to get virtual locations
                    locations = compat_manager.get_all_warehouse_locations(config.warehouse_id)
                    special_locs = [loc for loc in locations if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK']]
                    print(f"  Virtual special locations: {len(special_locs)}")
                    
                    for loc in special_locs:
                        print(f"    - {loc['code']} ({loc['location_type']})")
                        
                except Exception as e:
                    print(f"  ERROR getting virtual locations: {e}")
            
            print("-" * 30)

def test_virtual_engine_directly():
    """Test the virtual engine creation directly"""
    print("\nTESTING VIRTUAL ENGINE CREATION")
    print("=" * 40)
    
    with app.app_context():
        # Get a test config
        config = WarehouseConfig.query.first()
        if not config:
            print("No config found")
            return
            
        print(f"Testing with config: {config.warehouse_id}")
        
        # Get config dict
        config_dict = config.to_dict()
        print(f"Config dict keys: {list(config_dict.keys())}")
        
        # Check special areas in dict
        print(f"Receiving areas in dict: {config_dict.get('receiving_areas')}")
        print(f"Staging areas in dict: {config_dict.get('staging_areas')}")  
        print(f"Dock areas in dict: {config_dict.get('dock_areas')}")
        
        # Try to create virtual engine directly
        try:
            from virtual_location_engine import VirtualLocationEngine
            engine = VirtualLocationEngine(config_dict)
            
            print(f"Virtual engine created successfully")
            print(f"Special areas in engine: {len(engine.special_areas)}")
            
            for code, info in engine.special_areas.items():
                print(f"  - {code}: {info}")
                
        except Exception as e:
            print(f"ERROR creating virtual engine: {e}")
            import traceback
            traceback.print_exc()

def check_environment_variables():
    """Check environment variables that might affect virtual detection"""
    print("\nCHECKING ENVIRONMENT VARIABLES")
    print("=" * 40)
    
    env_vars = [
        'ENABLE_VIRTUAL_LOCATIONS',
        'FALLBACK_TO_PHYSICAL', 
        'DEBUG_VIRTUAL_COMPATIBILITY',
        'FORCE_PHYSICAL_MODE'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        print(f"{var}: {value}")

def main():
    """Run all debug tests"""
    debug_sqlite_warehouses()
    test_virtual_engine_directly()
    check_environment_variables()
    
    print("\nDEBUG SUMMARY:")
    print("- Check if special areas are properly parsed from JSON")
    print("- Verify virtual detection logic works in SQLite")
    print("- Ensure environment variables aren't blocking virtual mode")

if __name__ == "__main__":
    main()