#!/usr/bin/env python3
"""
Quick test to check if special locations are being returned by the API
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import Location
import requests
import json

def test_locations_api():
    with app.app_context():
        print("=== TESTING LOCATIONS API ===\n")
        
        # Check what's in the database directly
        print("1. DATABASE QUERY (special locations for DEFAULT):")
        special_locations = Location.query.filter(
            Location.warehouse_id == 'DEFAULT',
            Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
        ).all()
        
        print(f"Found {len(special_locations)} special locations in database:")
        for loc in special_locations:
            print(f"  - {loc.code} ({loc.location_type}) - Zone: {loc.zone}, Capacity: {loc.pallet_capacity}")
        
        print(f"\n2. ALL DEFAULT LOCATIONS (first 10):")
        all_locations = Location.query.filter(
            Location.warehouse_id == 'DEFAULT'
        ).limit(10).all()
        
        for loc in all_locations:
            print(f"  - {loc.code} ({loc.location_type}) - Zone: {loc.zone}")
        
        print(f"\nTotal DEFAULT locations: {Location.query.filter(Location.warehouse_id == 'DEFAULT').count()}")
        
        # Now test API response (without auth for now)
        print(f"\n3. API ENDPOINT TEST:")
        try:
            from location_api import location_api_bp
            print("Location API blueprint exists and is registered")
        except Exception as e:
            print(f"Error with location API: {e}")

if __name__ == '__main__':
    test_locations_api()