#!/usr/bin/env python3
"""
Add AISLE locations to the Flask app's database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend/src'))

def add_aisle_locations():
    """Add AISLE locations to the Flask app's database"""
    try:
        # Import Flask app and models
        from app import create_app_context
        from models import Location, db
        
        # Use Flask app context to ensure we're using the same database
        with create_app_context() as app:
            with app.app_context():
                print("Adding AISLE locations to Flask app database...")
                
                # Check current location count
                total_locations = Location.query.count()
                print(f"Current total locations in Flask database: {total_locations}")
                
                # Check if AISLE locations already exist
                existing_aisle = Location.query.filter(Location.code.like('%AISLE%')).all()
                print(f"Existing AISLE locations: {len(existing_aisle)}")
                
                if existing_aisle:
                    print("AISLE locations already exist:")
                    for loc in existing_aisle:
                        print(f"  - {loc.code} (warehouse: {loc.warehouse_id})")
                    return
                
                # Create AISLE locations
                aisle_locations = [
                    {
                        'code': 'AISLE-A',
                        'warehouse_id': 'DEFAULT',
                        'location_type': 'TRANSITIONAL',
                        'zone': 'GENERAL',
                        'capacity': 2,
                        'is_active': True,
                        'aisle_number': None,
                        'rack_number': None,
                        'position_number': None,
                        'level': None
                    },
                    {
                        'code': 'AISLE-B', 
                        'warehouse_id': 'DEFAULT',
                        'location_type': 'TRANSITIONAL',
                        'zone': 'GENERAL',
                        'capacity': 2,
                        'is_active': True,
                        'aisle_number': None,
                        'rack_number': None,
                        'position_number': None,
                        'level': None
                    },
                    {
                        'code': 'AISLETEST',
                        'warehouse_id': 'DEFAULT', 
                        'location_type': 'STORAGE',
                        'zone': 'GENERAL',
                        'capacity': 1,
                        'is_active': True,
                        'aisle_number': None,
                        'rack_number': None,
                        'position_number': None,
                        'level': None
                    }
                ]
                
                # Add locations to database
                added_count = 0
                for loc_data in aisle_locations:
                    # Check if location already exists
                    existing = Location.query.filter_by(
                        code=loc_data['code'], 
                        warehouse_id=loc_data['warehouse_id']
                    ).first()
                    
                    if not existing:
                        new_location = Location(**loc_data)
                        db.session.add(new_location)
                        added_count += 1
                        print(f"  Added: {loc_data['code']}")
                    else:
                        print(f"  Already exists: {loc_data['code']}")
                
                if added_count > 0:
                    db.session.commit()
                    print(f"\\nSuccessfully added {added_count} AISLE locations!")
                else:
                    print("\\nNo new AISLE locations added.")
                
                # Verify addition
                final_aisle = Location.query.filter(Location.code.like('%AISLE%')).all()
                print(f"Final AISLE location count: {len(final_aisle)}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def create_app_context():
    """Create Flask app context"""
    try:
        from app import app
        return app
    except:
        # Try alternative import
        import sys
        sys.path.append('backend/src')
        from app import app
        return app

if __name__ == "__main__":
    add_aisle_locations()