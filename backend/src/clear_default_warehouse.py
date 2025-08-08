#!/usr/bin/env python3
"""
Clear DEFAULT warehouse locations to fix mixed naming convention issues
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import app
from database import db
from models import Location, WarehouseConfig

def clear_default_warehouse():
    """Clear all locations from DEFAULT warehouse"""
    
    print("Clearing DEFAULT warehouse locations...")
    
    with app.app_context():
        try:
            # Get current DEFAULT locations
            default_locations = Location.query.filter_by(warehouse_id='DEFAULT').all()
            print(f"Found {len(default_locations)} locations in DEFAULT warehouse")
            
            if default_locations:
                print("Location codes to be deleted:")
                for loc in default_locations:
                    print(f"  {loc.code} ({loc.location_type})")
                
                # Delete all DEFAULT warehouse locations
                deleted_count = Location.query.filter_by(warehouse_id='DEFAULT').delete()
                db.session.commit()
                
                print(f"Successfully deleted {deleted_count} locations from DEFAULT warehouse")
            else:
                print("No locations found in DEFAULT warehouse")
            
            # Also clear DEFAULT warehouse config to start fresh
            default_config = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').first()
            if default_config:
                db.session.delete(default_config)
                db.session.commit()
                print("Deleted DEFAULT warehouse configuration")
            
            return True
            
        except Exception as e:
            print(f"Error clearing DEFAULT warehouse: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("DEFAULT Warehouse Cleanup Tool")
    print("=" * 40)
    
    response = input("This will delete ALL locations in the DEFAULT warehouse. Continue? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = clear_default_warehouse()
        if success:
            print("DEFAULT warehouse cleared successfully!")
            print("You can now run the warehouse setup wizard to create new structured locations.")
        else:
            print("Failed to clear DEFAULT warehouse.")
    else:
        print("Operation cancelled.")