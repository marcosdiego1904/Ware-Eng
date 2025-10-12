#!/usr/bin/env python3
"""
Debug the virtual engine cache issue with special locations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from models import WarehouseConfig
from database import db
from virtual_template_integration import get_virtual_engine_for_warehouse

def debug_cache_issue():
    """Debug the special location capacity issue"""
    
    with app.app_context():
        print("=== VIRTUAL ENGINE CACHE DEBUG INVESTIGATION ===")
        print()
        
        # Step 1: Check database config
        print("1. CHECKING DATABASE CONFIG...")
        try:
            config = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').first()
            if config:
                config_dict = config.to_dict()
                print(f"   ✅ Found config for DEFAULT warehouse")
                print(f"   📊 Receiving areas: {len(config_dict.get('receiving_areas', []))}")
                print(f"   📊 Staging areas: {len(config_dict.get('staging_areas', []))}")
                print(f"   📊 Dock areas: {len(config_dict.get('dock_areas', []))}")
                
                # Check the problematic locations specifically
                problem_locations = [
                    'BULK_STAGING_COMPLEX_01', 
                    'MEGA_RECEIVING_DOCK_02', 
                    'BULK_STAGING_COMPLEX_02',
                    'MASTER_STAGING_HUB_01'
                ]
                
                print()
                print("2. CHECKING PROBLEM LOCATIONS IN DATABASE...")
                for loc in problem_locations:
                    found_in_receiving = any(
                        area.get('code') == loc 
                        for area in config_dict.get('receiving_areas', [])
                    )
                    found_in_staging = any(
                        area.get('code') == loc 
                        for area in config_dict.get('staging_areas', [])
                    )
                    found_in_dock = any(
                        area.get('code') == loc 
                        for area in config_dict.get('dock_areas', [])
                    )
                    
                    status = "❌ NOT FOUND"
                    if found_in_receiving or found_in_staging or found_in_dock:
                        status = "✅ FOUND"
                        area_type = "RECEIVING" if found_in_receiving else ("STAGING" if found_in_staging else "DOCK")
                        
                        # Get the capacity
                        areas = config_dict.get(f'{area_type.lower()}_areas', [])
                        capacity = None
                        for area in areas:
                            if area.get('code') == loc:
                                capacity = area.get('capacity')
                                break
                        
                        status += f" in {area_type} with capacity {capacity}"
                    
                    print(f"   {loc}: {status}")
                
            else:
                print("   ❌ ERROR: No config found for DEFAULT warehouse!")
                return
                
        except Exception as e:
            print(f"   ❌ ERROR getting config: {e}")
            return

        print()
        print("3. TESTING VIRTUAL ENGINE LOOKUP...")
        try:
            # Force clear cache first
            from virtual_template_integration import virtual_location_cache
            virtual_location_cache.clear_cache('DEFAULT')
            print("   🔄 Cleared virtual engine cache")
            
            # Get fresh engine instance
            engine = get_virtual_engine_for_warehouse('DEFAULT')
            if engine:
                print("   ✅ Virtual engine loaded successfully")
                
                # Test each problem location
                print()
                print("4. TESTING PROBLEM LOCATIONS IN VIRTUAL ENGINE...")
                for loc in problem_locations:
                    try:
                        props = engine.get_location_properties(loc)
                        status_emoji = "✅" if props.capacity > 0 else "❌"
                        print(f"   {status_emoji} {loc}:")
                        print(f"      Capacity: {props.capacity}")
                        print(f"      Type: {props.location_type}")
                        print(f"      Valid: {props.is_valid}")
                        print(f"      Zone: {props.zone}")
                        
                        # If capacity is 0, this is our problem
                        if props.capacity == 0:
                            print(f"      🔍 PROBLEM: This location has capacity 0!")
                            
                            # Check if it's in the special_areas lookup
                            normalized_code = engine._remove_warehouse_prefix(loc.strip().upper())
                            in_special_areas = normalized_code in engine.special_areas
                            print(f"      🔍 In special_areas lookup: {in_special_areas}")
                            
                            if not in_special_areas:
                                print(f"      🔍 Available special areas: {list(engine.special_areas.keys())[:5]}...")
                        
                    except Exception as e:
                        print(f"   ❌ ERROR testing {loc}: {e}")
                        
            else:
                print("   ❌ ERROR: Could not load virtual engine")
                
        except Exception as e:
            print(f"   ❌ ERROR with virtual engine: {e}")
            import traceback
            traceback.print_exc()

        print()
        print("5. CHECKING SPECIAL AREAS LOOKUP TABLE...")
        try:
            engine = get_virtual_engine_for_warehouse('DEFAULT')
            if engine and hasattr(engine, 'special_areas'):
                print(f"   📊 Total special areas in lookup: {len(engine.special_areas)}")
                print("   🔍 First 10 special areas:")
                for i, (code, info) in enumerate(list(engine.special_areas.items())[:10]):
                    print(f"      {code}: capacity={info.get('capacity', 0)}, type={info.get('location_type', 'UNKNOWN')}")
                
                # Check if any of our problem locations are in there
                print()
                print("   🔍 Problem locations in lookup table:")
                for loc in problem_locations:
                    normalized = engine._remove_warehouse_prefix(loc.strip().upper())
                    if normalized in engine.special_areas:
                        info = engine.special_areas[normalized]
                        print(f"      ✅ {loc} -> {normalized}: {info}")
                    else:
                        print(f"      ❌ {loc} -> {normalized}: NOT FOUND")
                        
        except Exception as e:
            print(f"   ❌ ERROR checking special areas: {e}")

if __name__ == "__main__":
    debug_cache_issue()