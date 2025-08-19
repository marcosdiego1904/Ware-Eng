#!/usr/bin/env python3
"""
Test Dynamic Location Auto-Creation
Demonstrates the proper architectural solution for template flexibility
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from app import app, db
from location_service import get_location_matcher, get_canonical_service
from models import Location, WarehouseConfig
import pandas as pd

def test_dynamic_creation():
    """Test dynamic location creation with various scenarios"""
    
    with app.app_context():
        print("=== TESTING DYNAMIC LOCATION AUTO-CREATION ===")
        
        # Create a test warehouse with minimal template (unique name)
        import time
        test_warehouse = f"TEST_DYNAMIC_{int(time.time())}"
        
        # Clean up any existing test data
        Location.query.filter_by(warehouse_id=test_warehouse).delete()
        WarehouseConfig.query.filter_by(warehouse_id=test_warehouse).delete()
        db.session.commit()
        
        # Create minimal warehouse config (1 aisle, 1 rack, 5 positions, 2 levels)
        config = WarehouseConfig(
            warehouse_id=test_warehouse,
            warehouse_name="Test Dynamic Warehouse",
            num_aisles=1,
            racks_per_aisle=1, 
            positions_per_rack=5,
            levels_per_position=2,
            default_pallet_capacity=2,
            created_by=1
        )
        db.session.add(config)
        
        # Create only minimal locations (1 aisle, 1 rack, 5 positions, 2 levels = 10 locations)
        base_locations = []
        for pos in range(1, 6):  # 001-005
            for level in ['A', 'B']:
                code = f"01-01-{pos:03d}{level}"
                location = Location(
                    warehouse_id=test_warehouse,
                    code=code,
                    location_type='STORAGE',
                    zone='STORAGE',
                    pallet_capacity=2,
                    is_active=True,
                    created_by=1
                )
                base_locations.append(location)
        
        db.session.add_all(base_locations)
        db.session.commit()
        
        initial_count = Location.query.filter_by(warehouse_id=test_warehouse).count()
        print(f"Created minimal warehouse: {initial_count} locations")
        
        # Test inventory with locations OUTSIDE the template boundaries
        test_inventory_data = [
            ['PALLET001', '001A01', 'Test Product', 'REC001'],  # EXISTS (01-01-001A)
            ['PALLET002', '007C03', 'Test Product', 'REC001'],  # MISSING (01-03-007C) - outside template
            ['PALLET003', '015D05', 'Test Product', 'REC001'],  # MISSING (01-05-015D) - way outside
            ['PALLET004', 'B2-010', 'Test Product', 'REC001'],  # MISSING (01-02-010B) - different format
            ['PALLET005', 'RECV-01', 'Test Product', 'REC001'], # SPECIAL - should NOT auto-create
        ]
        
        df = pd.DataFrame(test_inventory_data, columns=['Pallet ID', 'Location', 'Description', 'Receipt'])
        df = df.rename(columns={'Location': 'location'})
        
        print(f"\nTesting inventory with {len(df)} locations...")
        
        canonical_service = get_canonical_service()
        matcher = get_location_matcher()
        
        results = []
        for _, row in df.iterrows():
            original = row['location']
            canonical = canonical_service.to_canonical(original)
            
            print(f"\nTesting: {original} -> {canonical}")
            
            # Try to find/create the location
            location = matcher.find_location(original, test_warehouse)
            
            if location:
                print(f"  ✅ SUCCESS: Found/created {location.code}")
                results.append(('SUCCESS', original, canonical, location.code))
            else:
                print(f"  ❌ FAILED: Could not find or create")
                results.append(('FAILED', original, canonical, None))
        
        # Check final location count
        final_count = Location.query.filter_by(warehouse_id=test_warehouse).count()
        auto_created = final_count - initial_count
        
        print(f"\n=== RESULTS ===")
        print(f"Initial locations: {initial_count}")
        print(f"Final locations: {final_count}")
        print(f"Auto-created: {auto_created}")
        
        print(f"\nDetailed results:")
        for status, original, canonical, result in results:
            print(f"  {status}: {original} -> {canonical} -> {result or 'NOT_CREATED'}")
        
        # Show which locations were auto-created
        if auto_created > 0:
            print(f"\nAuto-created locations:")
            auto_created_locs = Location.query.filter(
                Location.warehouse_id == test_warehouse,
                ~Location.code.in_([loc.code for loc in base_locations])
            ).all()
            
            for loc in auto_created_locs:
                print(f"  {loc.code} - {loc.location_type} - Capacity: {loc.pallet_capacity}")
        
        # Clean up
        Location.query.filter_by(warehouse_id=test_warehouse).delete()
        WarehouseConfig.query.filter_by(warehouse_id=test_warehouse).delete()
        db.session.commit()
        
        print(f"\n=== ARCHITECTURAL SOLUTION TEST COMPLETE ===")
        return auto_created > 0

if __name__ == "__main__":
    success = test_dynamic_creation()
    if success:
        print("✅ Dynamic location creation is working - proper architectural solution implemented!")
    else:
        print("❌ Dynamic location creation failed - needs debugging")
    sys.exit(0 if success else 1)