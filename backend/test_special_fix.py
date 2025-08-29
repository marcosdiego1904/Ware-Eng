#!/usr/bin/env python3
"""
Test the special locations fix
"""
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from virtual_compatibility_layer import get_compatibility_manager
    from models import Location
    from database import db
    from app import app

    print("Testing special locations fix...")
    
    with app.app_context():
        # Test the fixed compatibility layer
        compat_manager = get_compatibility_manager()
        locations = compat_manager.get_all_warehouse_locations('DEFAULT')
        
        # Count by type for debugging  
        type_counts = {}
        special_areas = []
        for loc in locations:
            loc_type = loc['location_type']
            type_counts[loc_type] = type_counts.get(loc_type, 0) + 1
            if loc_type in ['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL']:
                special_areas.append(loc['code'])
        
        print('After Fix - Location counts by type:', type_counts)
        print('After Fix - Special areas:', sorted(special_areas))
        print('Total special areas:', len(special_areas))
        
        # Check if we still have the old wrong locations
        wrong_locations = ['RECV-01', 'RECV-02', 'RECV-03', 'STAGE-03', 'DOCK-03']
        found_wrong = [code for code in special_areas if code in wrong_locations]
        
        if found_wrong:
            print(f"X STILL BROKEN: Found old locations that should be gone: {found_wrong}")
        else:
            print("SUCCESS: No old wrong locations found")
            
        # Check if we have the correct new locations
        expected_locations = ['STAGE-01', 'STAGE-02', 'DOCK-01', 'DOCK-02', 'AISLE-01', 'AISLE-02', 'AISLE-03', 'AISLE-04']
        found_expected = [code for code in special_areas if code in expected_locations]
        
        print(f"Expected template locations found: {len(found_expected)}/{len(expected_locations)}")
        print(f"Expected: {expected_locations}")
        print(f"Found: {found_expected}")

except Exception as e:
    print(f"Error testing fix: {e}")
    import traceback
    traceback.print_exc()