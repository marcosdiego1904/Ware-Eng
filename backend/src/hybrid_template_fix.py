"""
CRITICAL FIX: Special Locations Not Appearing Issue

This script fixes the hybrid virtual/physical location architecture
by ensuring special areas are always created as physical records
while keeping storage locations virtual.

Root Cause: Template application was creating only virtual engines
but Special Areas Management UI expects physical location records.

Solution: Hybrid approach - Virtual storage + Physical special areas
"""

import json
import sys
sys.path.append('.')

from src.app import app
from src.database import db
from src.models import WarehouseTemplate, WarehouseConfig, Location
from src.core_models import User


def create_special_locations_from_template(template, warehouse_id, current_user):
    """
    Create ONLY special area locations as physical records
    
    This allows the Special Areas Management UI to display them
    while keeping storage locations virtual.
    """
    created_special_locations = []
    
    try:
        print(f"[HYBRID_FIX] Creating special area locations for warehouse {warehouse_id}")
        
        # Process each type of special area
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
                print(f"[HYBRID_FIX] Processing {len(areas)} {location_type} areas")
                
                for area_data in areas:
                    # Check if location already exists
                    code = area_data.get('code', f'{location_type}_1')
                    existing = Location.query.filter_by(
                        warehouse_id=warehouse_id,
                        code=code
                    ).first()
                    
                    if existing:
                        print(f"[HYBRID_FIX] Special location {code} already exists, skipping")
                        continue
                    
                    # Create physical special location record
                    location = Location(
                        code=code,
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
                    print(f"[HYBRID_FIX] Created special location: {code} ({location_type})")
                    
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[HYBRID_FIX] Error processing {location_type} areas: {e}")
                continue
        
        # Commit the special location records
        if created_special_locations:
            db.session.commit()
            print(f"[HYBRID_FIX] Successfully created {len(created_special_locations)} special locations")
        else:
            print(f"[HYBRID_FIX] No special locations created (may already exist)")
            
        return created_special_locations
        
    except Exception as e:
        db.session.rollback()
        print(f"[HYBRID_FIX] Error creating special locations: {e}")
        return []


def fix_existing_template_applications():
    """
    Retroactively fix existing template applications that are missing special locations
    """
    with app.app_context():
        print("=== HYBRID ARCHITECTURE FIX ===")
        print("Creating physical special location records for existing virtual template applications\n")
        
        # Find all warehouse configs that should have special areas but don't
        configs = WarehouseConfig.query.all()
        
        for config in configs:
            print(f"\nChecking warehouse: {config.warehouse_name} (ID: {config.warehouse_id})")
            
            # Count existing special locations
            existing_special = Location.query.filter(
                Location.warehouse_id == config.warehouse_id,
                Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
            ).count()
            
            print(f"  Current special locations: {existing_special}")
            
            # Count expected special locations from config
            expected_special = 0
            if config.receiving_areas:
                try:
                    receiving = json.loads(config.receiving_areas) if isinstance(config.receiving_areas, str) else config.receiving_areas
                    expected_special += len(receiving) if receiving else 0
                except:
                    pass
            
            if config.staging_areas:
                try:
                    staging = json.loads(config.staging_areas) if isinstance(config.staging_areas, str) else config.staging_areas
                    expected_special += len(staging) if staging else 0
                except:
                    pass
                    
            if config.dock_areas:
                try:
                    dock = json.loads(config.dock_areas) if isinstance(config.dock_areas, str) else config.dock_areas
                    expected_special += len(dock) if dock else 0
                except:
                    pass
            
            print(f"  Expected special locations: {expected_special}")
            
            if expected_special > existing_special:
                print(f"  >>> NEEDS FIX: Missing {expected_special - existing_special} special locations")
                
                # Create a mock template from the config to use existing logic
                mock_template = type('MockTemplate', (), {
                    'receiving_areas_template': config.receiving_areas,
                    'staging_areas_template': config.staging_areas,  
                    'dock_areas_template': config.dock_areas
                })()
                
                # Get the config creator as current user
                creator = User.query.get(config.created_by)
                if creator:
                    created = create_special_locations_from_template(
                        mock_template, config.warehouse_id, creator
                    )
                    print(f"  >>> FIXED: Created {len(created)} special locations")
                else:
                    print(f"  >>> ERROR: Config creator not found (ID: {config.created_by})")
            else:
                print(f"  >>> OK: Special locations already exist")


if __name__ == "__main__":
    fix_existing_template_applications()