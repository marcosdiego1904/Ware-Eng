#!/usr/bin/env python3
"""
Simple fix for missing special locations issue
Creates physical location records for existing template configurations
"""

import sys
import json
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig, Location
from core_models import User


def create_missing_special_locations():
    """Create missing special locations for existing warehouse configs"""
    with app.app_context():
        print("=== CREATING MISSING SPECIAL LOCATIONS ===\n")
        
        configs = WarehouseConfig.query.all()
        total_created = 0
        
        for config in configs:
            print(f"Processing warehouse: {config.warehouse_name} (ID: {config.warehouse_id})")
            
            # Check current special locations
            existing_special = Location.query.filter(
                Location.warehouse_id == config.warehouse_id,
                Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
            ).count()
            
            print(f"  Current special locations: {existing_special}")
            
            created_for_config = 0
            
            # Process receiving areas
            if config.receiving_areas:
                try:
                    receiving_areas = json.loads(config.receiving_areas) if isinstance(config.receiving_areas, str) else config.receiving_areas
                    if receiving_areas:
                        print(f"  Processing {len(receiving_areas)} receiving areas...")
                        for area in receiving_areas:
                            code = area.get('code', 'RECEIVING')
                            existing = Location.query.filter_by(
                                warehouse_id=config.warehouse_id,
                                code=code
                            ).first()
                            
                            if not existing:
                                location = Location(
                                    code=code,
                                    location_type='RECEIVING',
                                    capacity=area.get('capacity', 10),
                                    pallet_capacity=area.get('capacity', 10),
                                    zone=area.get('zone', 'DOCK'),
                                    warehouse_id=config.warehouse_id,
                                    created_by=config.created_by,
                                    is_active=True
                                )
                                db.session.add(location)
                                created_for_config += 1
                                print(f"    Created: {code} (RECEIVING)")
                            else:
                                print(f"    Exists: {code} (RECEIVING)")
                except Exception as e:
                    print(f"    Error processing receiving areas: {e}")
            
            # Process staging areas  
            if config.staging_areas:
                try:
                    staging_areas = json.loads(config.staging_areas) if isinstance(config.staging_areas, str) else config.staging_areas
                    if staging_areas:
                        print(f"  Processing {len(staging_areas)} staging areas...")
                        for area in staging_areas:
                            code = area.get('code', 'STAGING')
                            existing = Location.query.filter_by(
                                warehouse_id=config.warehouse_id,
                                code=code
                            ).first()
                            
                            if not existing:
                                location = Location(
                                    code=code,
                                    location_type='STAGING',
                                    capacity=area.get('capacity', 5),
                                    pallet_capacity=area.get('capacity', 5),
                                    zone=area.get('zone', 'STAGING'),
                                    warehouse_id=config.warehouse_id,
                                    created_by=config.created_by,
                                    is_active=True
                                )
                                db.session.add(location)
                                created_for_config += 1
                                print(f"    Created: {code} (STAGING)")
                            else:
                                print(f"    Exists: {code} (STAGING)")
                except Exception as e:
                    print(f"    Error processing staging areas: {e}")
            
            # Process dock areas
            if config.dock_areas:
                try:
                    dock_areas = json.loads(config.dock_areas) if isinstance(config.dock_areas, str) else config.dock_areas  
                    if dock_areas:
                        print(f"  Processing {len(dock_areas)} dock areas...")
                        for area in dock_areas:
                            code = area.get('code', 'DOCK')
                            existing = Location.query.filter_by(
                                warehouse_id=config.warehouse_id,
                                code=code
                            ).first()
                            
                            if not existing:
                                location = Location(
                                    code=code,
                                    location_type='DOCK',
                                    capacity=area.get('capacity', 2),
                                    pallet_capacity=area.get('capacity', 2), 
                                    zone=area.get('zone', 'DOCK'),
                                    warehouse_id=config.warehouse_id,
                                    created_by=config.created_by,
                                    is_active=True
                                )
                                db.session.add(location)
                                created_for_config += 1
                                print(f"    Created: {code} (DOCK)")
                            else:
                                print(f"    Exists: {code} (DOCK)")
                except Exception as e:
                    print(f"    Error processing dock areas: {e}")
            
            if created_for_config > 0:
                try:
                    db.session.commit()
                    print(f"  [SUCCESS] CREATED {created_for_config} special locations for {config.warehouse_name}")
                    total_created += created_for_config
                except Exception as e:
                    db.session.rollback()
                    print(f"  [ERROR] Failed to commit locations for {config.warehouse_name}: {e}")
            else:
                print(f"  [SKIP] No new locations needed for {config.warehouse_name}")
            
            print()
        
        print(f"=== SUMMARY ===")
        print(f"Total special locations created: {total_created}")
        print(f"Processed {len(configs)} warehouse configurations")
        
        if total_created > 0:
            print("\n[SUCCESS] Fix completed! Special locations should now appear in the UI.")
        else:
            print("\n[WARNING] No locations were created. They may already exist or configs may be missing special area data.")


if __name__ == "__main__":
    create_missing_special_locations()