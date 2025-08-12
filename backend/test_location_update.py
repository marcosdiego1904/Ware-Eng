#!/usr/bin/env python3
"""
Test script to debug the location update endpoint
"""

import sys
sys.path.append('src')

from app import app
from models import Location
from database import db

def test_location_update():
    """Test the location update functionality"""
    with app.app_context():
        print("=== TESTING LOCATION UPDATE ENDPOINT ===\n")
        
        # Get a special location to test with
        special_location = Location.query.filter(
            Location.warehouse_id == 'DEFAULT',
            Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
        ).first()
        
        if not special_location:
            print("No special location found to test with!")
            return
        
        print(f"Testing with location:")
        print(f"  ID: {special_location.id}")
        print(f"  Code: {special_location.code}")
        print(f"  Type: {special_location.location_type}")
        print(f"  Capacity: {special_location.capacity}")
        print(f"  Zone: {special_location.zone}")
        print()
        
        # Test the database update directly
        print("=== DIRECT DATABASE UPDATE TEST ===")
        original_capacity = special_location.capacity
        new_capacity = original_capacity + 5
        
        try:
            special_location.capacity = new_capacity
            db.session.commit()
            print("SUCCESS: Direct database update successful")
            print("   Capacity changed from " + str(original_capacity) + " to " + str(new_capacity))
            
            # Revert the change
            special_location.capacity = original_capacity
            db.session.commit()
            print("SUCCESS: Reverted change back to " + str(original_capacity))
            
        except Exception as e:
            db.session.rollback()
            print("FAILED: Direct database update failed: " + str(e))
            return
        
        # Test the API endpoint logic
        print("\n=== API ENDPOINT LOGIC TEST ===")
        try:
            # Simulate what the API endpoint does
            location_id = special_location.id
            location = Location.query.get_or_404(location_id)
            print("SUCCESS: Location.query.get_or_404(" + str(location_id) + ") successful")
            print("   Found: " + location.code)
            
            # Test updating fields
            updatable_fields = [
                'code', 'pattern', 'location_type', 'capacity', 'zone', 
                'warehouse_id', 'aisle_number', 'rack_number', 'position_number', 
                'level', 'pallet_capacity', 'is_active'
            ]
            
            # Simulate updating capacity
            test_data = {'capacity': new_capacity}
            
            for field, value in test_data.items():
                if field in updatable_fields and hasattr(location, field):
                    setattr(location, field, value)
                    print("SUCCESS: Updated " + field + " to " + str(value))
            
            # Test commit
            db.session.commit()
            print("SUCCESS: Database commit successful")
            
            # Verify the change
            updated_location = Location.query.get(location_id)
            if updated_location.capacity == new_capacity:
                print("SUCCESS: Update verified: capacity is now " + str(updated_location.capacity))
            else:
                print("FAILED: Update failed: capacity is " + str(updated_location.capacity) + ", expected " + str(new_capacity))
            
            # Revert
            updated_location.capacity = original_capacity
            db.session.commit()
            print("SUCCESS: Reverted to original capacity: " + str(original_capacity))
            
        except Exception as e:
            db.session.rollback()
            print("FAILED: API endpoint logic test failed: " + str(e))
            return
        
        print("\n=== ENDPOINT URL TEST ===")
        print("The API endpoint should be accessible at:")
        print("  PUT /api/v1/locations/" + str(special_location.id))
        print("  Full URL: http://localhost:5000/api/v1/locations/" + str(special_location.id))
        
        print("\n=== SUMMARY ===")
        print("SUCCESS: Database operations work correctly")
        print("SUCCESS: Location query and update logic works")
        print("ANALYSIS: The 404 issue is likely:")
        print("   1. Authentication failure (no/invalid token)")
        print("   2. Incorrect URL being called by frontend")
        print("   3. Server not running when frontend makes the call")
        print("   4. Wrong HTTP method being used")

if __name__ == "__main__":
    test_location_update()