"""
CRITICAL FIX: Add missing special areas to USER_TESTF warehouse

This script addresses the issue where RECV-01, RECV-02, and other special areas
are missing from the USER_TESTF warehouse database, causing rule failures.

The analysis shows these locations are referenced in the inventory but don't exist
in the database, causing warehouse detection to fail and rules to malfunction.
"""

import sys
import os
sys.path.append('src')

# Import the Flask app directly
import app
from models import db, Location, WarehouseConfig

def add_missing_special_areas():
    """Add missing special areas to USER_TESTF warehouse"""
    # Use the existing Flask app instance
    with app.app.app_context():
        warehouse_id = 'USER_TESTF'
        
        # Define the special areas that need to be added
        # Note: Using correct field names from Location model
        special_areas = [
            {
                'code': 'RECV-01',
                'location_type': 'RECEIVING',
                'zone': 'RECEIVING',
                'pallet_capacity': 10,
            },
            {
                'code': 'RECV-02', 
                'location_type': 'RECEIVING',
                'zone': 'RECEIVING',
                'pallet_capacity': 10,
            },
            {
                'code': 'AISLE-01',
                'location_type': 'TRANSITIONAL',
                'zone': 'TRANSITIONAL',
                'pallet_capacity': 10,
            },
            {
                'code': 'AISLE-02',
                'location_type': 'TRANSITIONAL',
                'zone': 'TRANSITIONAL', 
                'pallet_capacity': 1,  # Note: Analysis shows this has capacity=1 in existing data
            }
        ]
        
        print(f"Adding missing special areas to warehouse: {warehouse_id}")
        
        # Check current state
        existing_locations = Location.query.filter_by(warehouse_id=warehouse_id).all()
        existing_codes = {loc.code for loc in existing_locations}
        
        print(f"Current location count: {len(existing_locations)}")
        print(f"Existing special areas: {[code for code in existing_codes if any(special in code for special in ['RECV', 'AISLE', 'DOCK', 'STAGE'])]}")
        
        # Add missing special areas
        added_count = 0
        for area in special_areas:
            if area['code'] not in existing_codes:
                print(f"Adding missing location: {area['code']}")
                
                new_location = Location(
                    warehouse_id=warehouse_id,
                    code=area['code'],
                    location_type=area['location_type'],
                    zone=area['zone'],
                    pallet_capacity=area['pallet_capacity'],
                    is_active=True,
                    created_by=1  # System user
                )
                
                db.session.add(new_location)
                added_count += 1
            else:
                print(f"Location already exists: {area['code']}")
        
        if added_count > 0:
            try:
                db.session.commit()
                print(f"SUCCESS: Added {added_count} special areas to {warehouse_id}")
            except Exception as e:
                db.session.rollback()
                print(f"ERROR: Failed to add special areas: {e}")
                return False
        else:
            print("INFO: All special areas already exist")
        
        # Verify the additions
        updated_locations = Location.query.filter_by(warehouse_id=warehouse_id).all()
        special_area_codes = [loc.code for loc in updated_locations if any(special in loc.code for special in ['RECV', 'AISLE', 'DOCK', 'STAGE'])]
        
        print(f"Final location count: {len(updated_locations)}")
        print(f"Special areas now available: {special_area_codes}")
        
        # Check if required locations from analysis are now present
        required_for_analysis = ['RECV-01', 'RECV-02', 'AISLE-01', 'AISLE-02']
        missing_critical = [code for code in required_for_analysis if code not in [loc.code for loc in updated_locations]]
        
        if missing_critical:
            print(f"WARNING: Still missing critical locations: {missing_critical}")
            return False
        else:
            print("SUCCESS: All critical special areas are now present!")
            return True

if __name__ == "__main__":
    print("=" * 60)
    print("CRITICAL FIX: Adding missing special areas to USER_TESTF")
    print("=" * 60)
    
    success = add_missing_special_areas()
    
    if success:
        print("\nDATABASE REPAIR COMPLETED SUCCESSFULLY!")
        print("The warehouse detection system should now work properly.")
    else:
        print("\nDATABASE REPAIR FAILED!")
        print("Manual intervention may be required.")