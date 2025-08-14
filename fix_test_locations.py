#!/usr/bin/env python3
"""
Create missing locations for Central DC test inventory
"""
import sys
import os
sys.path.append('backend/src')

from models import db, Location
from app import app
import pandas as pd

def create_missing_locations():
    """Create locations that match our test inventory"""
    
    with app.app_context():
        # Read our test inventory to get all unique locations
        df = pd.read_excel('CentralDC_Compact_Inventory.xlsx', sheet_name='Inventory')
        unique_locations = df['location'].unique()
        
        print(f"Found {len(unique_locations)} unique locations in test inventory")
        
        # Check which ones are missing
        missing_locations = []
        existing_count = 0
        
        for location in unique_locations:
            existing = Location.query.filter_by(code=location).first()
            if not existing:
                missing_locations.append(location)
            else:
                existing_count += 1
        
        print(f"Existing locations: {existing_count}")
        print(f"Missing locations: {len(missing_locations)}")
        
        if not missing_locations:
            print("All locations already exist!")
            return
        
        # Create missing locations with appropriate types
        created_count = 0
        
        for location in missing_locations:
            # Skip NaN values
            if pd.isna(location) or not isinstance(location, str):
                continue
                
            # Determine location type based on pattern
            if location.startswith('RCV-'):
                location_type = 'RECEIVING'
                capacity = 10
            elif location.startswith('STG-'):
                location_type = 'STAGING'  
                capacity = 5
            elif location.startswith('DOCK-'):
                location_type = 'DOCK'
                capacity = 3
            elif location.startswith('FINAL-'):
                location_type = 'FINAL'
                capacity = 1
            elif location in ['INVALID-LOC', 'ERROR-404', 'NULL_LOCATION', 'UNKNOWN-001', '99-99-99X', 'MISPLACED']:
                location_type = 'UNKNOWN'
                capacity = 0
            else:
                # Storage location pattern (AA-RR-PPL)
                location_type = 'STORAGE'
                capacity = 1
            
            # Create the location
            new_location = Location(
                code=location,
                location_type=location_type,
                capacity=capacity,
                pattern=f"^{location.replace('-', '\\-')}$",  # Escape hyphens for regex
                zone=location_type,
                is_active=True
            )
            
            try:
                db.session.add(new_location)
                created_count += 1
                print(f"Created: {location} ({location_type})")
                
                # Commit every 50 locations to avoid memory issues
                if created_count % 50 == 0:
                    db.session.commit()
                    print(f"Committed {created_count} locations...")
                    
            except Exception as e:
                print(f"Error creating {location}: {e}")
                db.session.rollback()
        
        # Final commit
        try:
            db.session.commit()
            print(f"\n✅ Successfully created {created_count} locations!")
            
            # Verify the locations were created
            print("\n=== VERIFICATION ===")
            test_locations = ['02-06-03A', '04-04-06B', 'RCV-001', 'STG-001', 'FINAL-006', 'INVALID-LOC']
            for test_loc in test_locations:
                found = Location.query.filter_by(code=test_loc).first()
                status = "✅ FOUND" if found else "❌ NOT FOUND"
                print(f"{test_loc}: {status}")
                
        except Exception as e:
            print(f"Error committing locations: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_missing_locations()