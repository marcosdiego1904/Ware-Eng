#!/usr/bin/env python3
"""
Add more special areas to DEFAULT warehouse to test multiple locations
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig

def add_special_areas_to_default():
    """Add staging and dock areas to DEFAULT warehouse"""
    print("ADDING SPECIAL AREAS TO DEFAULT WAREHOUSE")
    print("=" * 50)
    
    with app.app_context():
        config = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').first()
        if not config:
            print("ERROR: DEFAULT warehouse config not found")
            return
        
        print(f"Current warehouse: {config.warehouse_name}")
        
        # Check current special areas
        receiving = config.get_receiving_areas()
        staging = config.get_staging_areas()  
        dock = config.get_dock_areas()
        
        print(f"Current special areas:")
        print(f"  Receiving: {len(receiving)} - {[r.get('code') for r in receiving]}")
        print(f"  Staging: {len(staging)} - {[s.get('code') for s in staging]}")
        print(f"  Dock: {len(dock)} - {[d.get('code') for d in dock]}")
        
        # Add staging areas if none exist
        if len(staging) == 0:
            new_staging = [
                {'code': 'STAGE-01', 'type': 'STAGING', 'capacity': 8, 'zone': 'STAGING'},
                {'code': 'STAGE-02', 'type': 'STAGING', 'capacity': 6, 'zone': 'STAGING'}
            ]
            config.set_staging_areas(new_staging)
            print("Added 2 staging areas")
        
        # Add dock areas if none exist  
        if len(dock) == 0:
            new_dock = [
                {'code': 'DOCK-01', 'type': 'DOCK', 'capacity': 4, 'zone': 'DOCK'},
                {'code': 'DOCK-02', 'type': 'DOCK', 'capacity': 4, 'zone': 'DOCK'}
            ]
            config.set_dock_areas(new_dock)
            print("Added 2 dock areas")
        
        # Commit changes
        db.session.commit()
        print("Changes committed to database")
        
        # Verify the changes
        print("\nVerification:")
        config = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').first()
        receiving = config.get_receiving_areas()
        staging = config.get_staging_areas()
        dock = config.get_dock_areas()
        total = len(receiving) + len(staging) + len(dock)
        
        print(f"  Total special areas now: {total}")
        print(f"  Receiving: {[r.get('code') for r in receiving]}")
        print(f"  Staging: {[s.get('code') for s in staging]}")  
        print(f"  Dock: {[d.get('code') for d in dock]}")
        
        # Test virtual locations
        from virtual_compatibility_layer import get_compatibility_manager
        compat_manager = get_compatibility_manager()
        
        locations = compat_manager.get_all_warehouse_locations('DEFAULT')
        special_locs = [
            loc for loc in locations 
            if loc.get('location_type') in ['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL']
        ]
        
        print(f"\nVirtual locations after update:")
        print(f"  Total special locations: {len(special_locs)}")
        for loc in special_locs:
            print(f"    {loc['code']} ({loc['location_type']}) - Zone: {loc['zone']}")

if __name__ == "__main__":
    add_special_areas_to_default()
    print("\n" + "=" * 50)
    print("✅ DEFAULT warehouse now has multiple special areas!")
    print("🔄 Refresh your frontend to see all locations")