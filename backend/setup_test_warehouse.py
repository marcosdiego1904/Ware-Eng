#!/usr/bin/env python3
"""
Set up a realistic test warehouse layout for WareWise testing

This creates a complete warehouse with:
- Receiving areas
- Storage aisles 
- Temperature zones
- Special purpose areas
- Proper capacity and location types
"""

import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location

def create_test_warehouse():
    """Create a comprehensive test warehouse layout"""
    with app.app_context():
        
        print(f"Setting up test warehouse locations...")
        
        # Use warehouse_id = 1 (assuming default warehouse exists)
        warehouse_id = 1
        
        # Clear existing test locations (be careful not to delete all)
        test_location_prefixes = ['RECV', 'SHIP', 'PICK', 'PACK', 'COLD', 'FROZEN', 'SECURE', 'BULK', 'HAZMAT', 'RETURN', 'DAMAGED', 'QUARANTINE', 'QC-', 'XDOCK', 'AISLE-', 'LOST-', 'OVERFLOW', 'STAGING', 'INBOUND', 'TEMP-', 'MAINT', 'BATTERY', 'WILL-CALL']
        
        for prefix in test_location_prefixes:
            test_locations = Location.query.filter(Location.code.like(f'{prefix}%')).all()
            for loc in test_locations:
                db.session.delete(loc)
        
        # Define warehouse layout
        locations_to_create = []
        
        # === RECEIVING AREAS === (10 locations)
        receiving_areas = [
            ('RECEIVING', 'RECEIVING', 'Main receiving dock', 50),
            ('RECV-01', 'RECEIVING', 'Receiving bay 1', 25),
            ('RECV-02', 'RECEIVING', 'Receiving bay 2', 25), 
            ('RECV-03', 'RECEIVING', 'Receiving bay 3', 25),
            ('STAGING-A', 'RECEIVING', 'Staging area A', 30),
            ('STAGING-B', 'RECEIVING', 'Staging area B', 30),
            ('INBOUND-1', 'RECEIVING', 'Inbound processing 1', 20),
            ('INBOUND-2', 'RECEIVING', 'Inbound processing 2', 20),
            ('TEMP-HOLD', 'RECEIVING', 'Temporary holding', 15),
            ('QC-INSPECT', 'RECEIVING', 'Quality control inspection', 10)
        ]
        
        # === STORAGE AISLES === (50 locations)
        # Aisles A-E, Rows 01-10
        for aisle in ['A', 'B', 'C', 'D', 'E']:
            for row in range(1, 11):
                location_code = f"{aisle}{row:02d}"
                locations_to_create.append((
                    location_code, 'STORAGE', f'Storage aisle {aisle} row {row:02d}', 
                    20 if aisle in ['A', 'B'] else 15  # Premium aisles have higher capacity
                ))
        
        # === SPECIALIZED STORAGE === (20 locations)
        specialized_areas = [
            # Cold storage
            ('COLD-01', 'COLD_STORAGE', 'Refrigerated zone 1', 30),
            ('COLD-02', 'COLD_STORAGE', 'Refrigerated zone 2', 30),
            ('COLD-03', 'COLD_STORAGE', 'Refrigerated zone 3', 30),
            ('FROZEN-01', 'FROZEN_STORAGE', 'Freezer zone 1', 25),
            ('FROZEN-02', 'FROZEN_STORAGE', 'Freezer zone 2', 25),
            
            # High value
            ('SECURE-01', 'SECURE_STORAGE', 'High value storage 1', 10),
            ('SECURE-02', 'SECURE_STORAGE', 'High value storage 2', 10),
            
            # Oversized
            ('BULK-01', 'BULK_STORAGE', 'Bulk storage 1', 5),
            ('BULK-02', 'BULK_STORAGE', 'Bulk storage 2', 5),
            ('BULK-03', 'BULK_STORAGE', 'Bulk storage 3', 5),
            
            # Hazmat
            ('HAZMAT-01', 'HAZMAT_STORAGE', 'Hazardous materials 1', 8),
            ('HAZMAT-02', 'HAZMAT_STORAGE', 'Hazardous materials 2', 8),
            
            # Returns
            ('RETURN-01', 'RETURN_AREA', 'Returns processing 1', 40),
            ('RETURN-02', 'RETURN_AREA', 'Returns processing 2', 40),
            
            # Damaged
            ('DAMAGED-01', 'DAMAGED_AREA', 'Damaged goods holding', 25),
            ('DAMAGED-02', 'DAMAGED_AREA', 'Salvage area', 25),
            
            # Quarantine  
            ('QUARANTINE', 'QUARANTINE', 'Quality hold area', 20),
            ('QC-HOLD', 'QUARANTINE', 'QC investigation hold', 15),
            
            # Cross-dock
            ('XDOCK-01', 'CROSS_DOCK', 'Cross dock bay 1', 35),
            ('XDOCK-02', 'CROSS_DOCK', 'Cross dock bay 2', 35)
        ]
        
        # === OPERATIONAL AREAS === (15 locations)
        operational_areas = [
            # Picking
            ('PICK-ZONE-A', 'PICK_ZONE', 'Picking zone A', 100),
            ('PICK-ZONE-B', 'PICK_ZONE', 'Picking zone B', 100),
            ('PICK-STAGE', 'PICK_ZONE', 'Pick staging area', 80),
            
            # Packing
            ('PACK-01', 'PACK_AREA', 'Packing station 1', 50),
            ('PACK-02', 'PACK_AREA', 'Packing station 2', 50),
            ('PACK-03', 'PACK_AREA', 'Packing station 3', 50),
            
            # Shipping
            ('SHIP-DOCK-1', 'SHIPPING', 'Shipping dock 1', 60),
            ('SHIP-DOCK-2', 'SHIPPING', 'Shipping dock 2', 60),
            ('SHIP-STAGE', 'SHIPPING', 'Shipping staging', 80),
            ('WILL-CALL', 'SHIPPING', 'Will call pickup', 30),
            
            # Equipment
            ('MAINT-AREA', 'MAINTENANCE', 'Equipment maintenance', 5),
            ('BATTERY-CHG', 'MAINTENANCE', 'Battery charging station', 0),
            
            # Problem areas (for testing)
            ('AISLE-TEMP', 'AISLE', 'Temporary aisle storage', 2),  # Low capacity for testing
            ('LOST-FOUND', 'UNKNOWN', 'Lost and found', 10),
            ('OVERFLOW', 'OVERFLOW', 'Overflow staging', 200)  # High capacity
        ]
        
        # Combine all location definitions
        all_locations = receiving_areas + specialized_areas + operational_areas
        
        # Add storage aisles
        for aisle in ['A', 'B', 'C', 'D', 'E']:
            for row in range(1, 11):
                location_code = f"{aisle}{row:02d}"
                all_locations.append((
                    location_code, 'STORAGE', f'Storage aisle {aisle} row {row:02d}', 
                    20 if aisle in ['A', 'B'] else 15
                ))
        
        # Create all locations
        print(f"Creating {len(all_locations)} warehouse locations...")
        
        for code, location_type, description, capacity in all_locations:
            # Set temperature zone based on location type
            if location_type in ['COLD_STORAGE']:
                zone = 'REFRIGERATED'
            elif location_type in ['FROZEN_STORAGE']:
                zone = 'FROZEN'
            elif location_type in ['HAZMAT_STORAGE']:
                zone = 'HAZMAT'
            else:
                zone = 'AMBIENT'
            
            location = Location(
                code=code,
                location_type=location_type,
                description=description,
                capacity=capacity,
                warehouse_id=warehouse_id,
                zone=zone,
                is_active=True
            )
            db.session.add(location)
        
        # Add a few inactive locations for testing
        inactive_locations = [
            ('OLD-AREA-1', 'STORAGE', 'Decommissioned area 1', 10, False),
            ('CONSTRUCTION', 'MAINTENANCE', 'Under construction', 0, False),
            ('TEMP-CLOSED', 'STORAGE', 'Temporarily closed', 20, False)
        ]
        
        for code, location_type, description, capacity, is_active in inactive_locations:
            location = Location(
                code=code,
                location_type=location_type, 
                description=description,
                capacity=capacity,
                warehouse_id=warehouse_id,
                zone='AMBIENT',
                is_active=is_active
            )
            db.session.add(location)
        
        db.session.commit()
        
        # Verify creation
        total_locations = Location.query.filter_by(warehouse_id=warehouse_id).count()
        active_locations = Location.query.filter_by(warehouse_id=warehouse_id, is_active=True).count()
        
        print(f"✅ Warehouse setup complete!")
        print(f"   Total locations: {total_locations}")
        print(f"   Active locations: {active_locations}")
        print(f"   Inactive locations: {total_locations - active_locations}")
        
        # Print location summary by type
        print(f"\nLocation breakdown by type:")
        location_types = db.session.query(Location.location_type, db.func.count(Location.id)).filter_by(
            warehouse_id=warehouse_id, is_active=True
        ).group_by(Location.location_type).all()
        
        for loc_type, count in location_types:
            print(f"   {loc_type}: {count} locations")
        
        return warehouse_id

def create_some_invalid_locations():
    """Add some deliberately invalid/problematic locations for testing"""
    with app.app_context():
        # Create locations that should trigger validation issues
        problematic_locations = [
            # Location with null is_active (should be included in valid locations)
            ('NULL-ACTIVE', 'STORAGE', 'Location with NULL is_active', 15, None),
            
            # Invalid location that should not exist in database (will be referenced in inventory)
            # Note: We DON'T create this one - it will only exist in inventory file
            # ('INVALID-LOC-123', 'UNKNOWN', 'This should not exist', 1, True),
        ]
        
        for code, location_type, description, capacity, is_active in problematic_locations:
            location = Location(
                code=code,
                location_type=location_type,
                description=description, 
                capacity=capacity,
                warehouse_id=1,  # Assume first warehouse
                zone='AMBIENT',
                is_active=is_active
            )
            db.session.add(location)
        
        db.session.commit()
        print("Added problematic locations for testing edge cases")

if __name__ == '__main__':
    print("WareWise Test Warehouse Setup")
    print("=" * 50)
    
    warehouse_id = create_test_warehouse()
    create_some_invalid_locations()
    
    print(f"\n🎯 Test warehouse ready!")
    print(f"   Warehouse ID: {warehouse_id}")
    print(f"   Ready for inventory testing...")