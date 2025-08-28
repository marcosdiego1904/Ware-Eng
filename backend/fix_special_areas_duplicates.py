#!/usr/bin/env python3
"""
Fix duplicate special area codes in warehouse configurations
This script identifies and removes duplicate special areas while preserving data integrity
"""

import sys
import json
from typing import List, Dict, Any

sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig

def remove_duplicates_from_areas(areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate special areas based on code, keeping the first occurrence"""
    if not areas:
        return areas
    
    seen_codes = set()
    unique_areas = []
    
    for area in areas:
        if isinstance(area, dict):
            code = area.get('code', '')
            if code and code not in seen_codes:
                seen_codes.add(code)
                unique_areas.append(area)
            elif code in seen_codes:
                print(f"    Removing duplicate area: {code}")
    
    return unique_areas

def standardize_zone_assignments(areas: List[Dict[str, Any]], area_type: str) -> List[Dict[str, Any]]:
    """Standardize zone assignments for special areas"""
    zone_mapping = {
        'RECEIVING': 'RECEIVING',
        'STAGING': 'STAGING', 
        'DOCK': 'DOCK'
    }
    
    standard_zone = zone_mapping.get(area_type, 'GENERAL')
    
    for area in areas:
        if isinstance(area, dict):
            # Ensure consistent zone assignment
            if area.get('zone') != standard_zone:
                old_zone = area.get('zone', 'undefined')
                area['zone'] = standard_zone
                print(f"    Standardized zone for {area.get('code', 'unknown')}: {old_zone} -> {standard_zone}")
            
            # Ensure type consistency
            if area.get('type') != area_type:
                old_type = area.get('type', 'undefined')
                area['type'] = area_type
                print(f"    Standardized type for {area.get('code', 'unknown')}: {old_type} -> {area_type}")
    
    return areas

def validate_capacity_values(areas: List[Dict[str, Any]], area_type: str) -> List[Dict[str, Any]]:
    """Validate and fix capacity values for special areas"""
    default_capacities = {
        'RECEIVING': 10,
        'STAGING': 5,
        'DOCK': 2
    }
    
    default_capacity = default_capacities.get(area_type, 5)
    
    for area in areas:
        if isinstance(area, dict):
            capacity = area.get('capacity', 0)
            if not isinstance(capacity, int) or capacity <= 0 or capacity > 100:
                old_capacity = capacity
                area['capacity'] = default_capacity
                print(f"    Fixed invalid capacity for {area.get('code', 'unknown')}: {old_capacity} -> {default_capacity}")
    
    return areas

def fix_warehouse_special_areas():
    """Fix special area configurations in all warehouses"""
    print("=== FIXING SPECIAL AREAS DUPLICATES ===\n")
    
    with app.app_context():
        # Get all warehouse configurations
        configs = WarehouseConfig.query.all()
        print(f"Found {len(configs)} warehouse configurations to check\n")
        
        changes_made = 0
        
        for config in configs:
            print(f"Checking warehouse: {config.warehouse_name} (ID: {config.warehouse_id})")
            config_changed = False
            
            # Process receiving areas
            if config.receiving_areas:
                try:
                    receiving_areas = json.loads(config.receiving_areas) if isinstance(config.receiving_areas, str) else config.receiving_areas
                    if receiving_areas:
                        original_count = len(receiving_areas)
                        
                        # Remove duplicates
                        unique_receiving = remove_duplicates_from_areas(receiving_areas)
                        
                        # Standardize zones and types
                        unique_receiving = standardize_zone_assignments(unique_receiving, 'RECEIVING')
                        
                        # Validate capacities
                        unique_receiving = validate_capacity_values(unique_receiving, 'RECEIVING')
                        
                        if len(unique_receiving) != original_count or unique_receiving != receiving_areas:
                            config.receiving_areas = json.dumps(unique_receiving) if unique_receiving else None
                            config_changed = True
                            print(f"  [OK] Fixed receiving areas: {original_count} -> {len(unique_receiving)}")
                        
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"  [WARN] Error processing receiving areas: {e}")
            
            # Process staging areas
            if config.staging_areas:
                try:
                    staging_areas = json.loads(config.staging_areas) if isinstance(config.staging_areas, str) else config.staging_areas
                    if staging_areas:
                        original_count = len(staging_areas)
                        
                        # Remove duplicates
                        unique_staging = remove_duplicates_from_areas(staging_areas)
                        
                        # Standardize zones and types
                        unique_staging = standardize_zone_assignments(unique_staging, 'STAGING')
                        
                        # Validate capacities
                        unique_staging = validate_capacity_values(unique_staging, 'STAGING')
                        
                        if len(unique_staging) != original_count or unique_staging != staging_areas:
                            config.staging_areas = json.dumps(unique_staging) if unique_staging else None
                            config_changed = True
                            print(f"  [OK] Fixed staging areas: {original_count} -> {len(unique_staging)}")
                        
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"  [WARN] Error processing staging areas: {e}")
            
            # Process dock areas
            if config.dock_areas:
                try:
                    dock_areas = json.loads(config.dock_areas) if isinstance(config.dock_areas, str) else config.dock_areas
                    if dock_areas:
                        original_count = len(dock_areas)
                        
                        # Remove duplicates
                        unique_dock = remove_duplicates_from_areas(dock_areas)
                        
                        # Standardize zones and types
                        unique_dock = standardize_zone_assignments(unique_dock, 'DOCK')
                        
                        # Validate capacities
                        unique_dock = validate_capacity_values(unique_dock, 'DOCK')
                        
                        if len(unique_dock) != original_count or unique_dock != dock_areas:
                            config.dock_areas = json.dumps(unique_dock) if unique_dock else None
                            config_changed = True
                            print(f"  [OK] Fixed dock areas: {original_count} -> {len(unique_dock)}")
                        
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"  [WARN] Error processing dock areas: {e}")
            
            if config_changed:
                changes_made += 1
                print(f"  [SAVE] Saving changes for {config.warehouse_name}")
            else:
                print(f"  [OK] No changes needed for {config.warehouse_name}")
            
            print()
        
        # Commit all changes
        if changes_made > 0:
            db.session.commit()
            print(f"[SUCCESS] Successfully fixed {changes_made} warehouse configurations!")
        else:
            print("[INFO] No fixes were needed - all configurations are clean!")

def verify_fixes():
    """Verify that fixes were applied correctly"""
    print("\n=== VERIFYING FIXES ===\n")
    
    with app.app_context():
        configs = WarehouseConfig.query.all()
        
        for config in configs:
            print(f"Warehouse: {config.warehouse_name} (ID: {config.warehouse_id})")
            
            # Check receiving areas
            if config.receiving_areas:
                try:
                    receiving_areas = json.loads(config.receiving_areas) if isinstance(config.receiving_areas, str) else config.receiving_areas
                    codes = [area.get('code') for area in receiving_areas if isinstance(area, dict)]
                    unique_codes = set(codes)
                    
                    if len(codes) != len(unique_codes):
                        print(f"  [ERROR] Still has duplicate receiving areas: {codes}")
                    else:
                        print(f"  [OK] Receiving areas clean: {codes}")
                except:
                    print(f"  [WARN] Error checking receiving areas")
            
            # Check staging areas
            if config.staging_areas:
                try:
                    staging_areas = json.loads(config.staging_areas) if isinstance(config.staging_areas, str) else config.staging_areas
                    codes = [area.get('code') for area in staging_areas if isinstance(area, dict)]
                    unique_codes = set(codes)
                    
                    if len(codes) != len(unique_codes):
                        print(f"  [ERROR] Still has duplicate staging areas: {codes}")
                    else:
                        print(f"  [OK] Staging areas clean: {codes}")
                except:
                    print(f"  [WARN] Error checking staging areas")
            
            # Check dock areas
            if config.dock_areas:
                try:
                    dock_areas = json.loads(config.dock_areas) if isinstance(config.dock_areas, str) else config.dock_areas
                    codes = [area.get('code') for area in dock_areas if isinstance(area, dict)]
                    unique_codes = set(codes)
                    
                    if len(codes) != len(unique_codes):
                        print(f"  [ERROR] Still has duplicate dock areas: {codes}")
                    else:
                        print(f"  [OK] Dock areas clean: {codes}")
                except:
                    print(f"  [WARN] Error checking dock areas")
            
            print()

if __name__ == "__main__":
    # Fix the duplicates
    fix_warehouse_special_areas()
    
    # Verify fixes
    verify_fixes()