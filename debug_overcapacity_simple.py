#!/usr/bin/env python3
"""
Simple debug of overcapacity detection
"""
import sys
import os
sys.path.append('backend/src')

from models import db, Rule, Location
from app import app
import pandas as pd

def debug_overcapacity():
    """Debug overcapacity step by step"""
    
    with app.app_context():
        # Load test inventory
        df = pd.read_excel('CentralDC_Compact_Inventory.xlsx', sheet_name='Inventory')
        
        # Check capacity data in our locations
        sample_locations = ['RCV-001', 'RCV-002', 'RCV-005', 'FINAL-004', '02-02-04A']
        print("=== LOCATION CAPACITY CHECK ===")
        for loc_code in sample_locations:
            location = Location.query.filter_by(code=loc_code).first()
            if location:
                pallet_count = len(df[df['location'] == loc_code])
                print(f"{loc_code}: Capacity={location.capacity}, Pallets={pallet_count}, Overcapacity={pallet_count > location.capacity}")
            else:
                print(f"{loc_code}: NOT FOUND in database")
                
        # Test specific overcapacity logic manually
        print("\n=== MANUAL OVERCAPACITY CHECK ===")
        location_counts = df['location'].value_counts()
        overcapacity_found = 0
        
        for location_code, count in location_counts.head(10).items():
            location_obj = Location.query.filter_by(code=location_code).first()
            if location_obj:
                capacity = location_obj.capacity
                is_overcapacity = count > capacity
                status = 'OVERCAPACITY' if is_overcapacity else 'OK'
                print(f"{location_code}: {count} pallets, capacity {capacity} -> {status}")
                if is_overcapacity:
                    overcapacity_found += 1
            else:
                print(f"{location_code}: {count} pallets, NO LOCATION RECORD")
        
        print(f"\nFound {overcapacity_found} overcapacity locations manually")
        
        # Check what locations we created with what capacity
        print("\n=== CREATED LOCATION CAPACITY SETTINGS ===")
        receiving_locs = Location.query.filter_by(location_type='RECEIVING').all()
        for loc in receiving_locs[:5]:
            pallet_count = len(df[df['location'] == loc.code])
            print(f"{loc.code}: Capacity={loc.capacity}, Pallets={pallet_count}")

if __name__ == "__main__":
    debug_overcapacity()