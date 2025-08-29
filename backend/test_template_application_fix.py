#!/usr/bin/env python3
"""
Test the template application fix for duplicate key constraint violations
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from virtual_template_integration import VirtualTemplateManager
    from models import Location, WarehouseTemplate, WarehouseConfig
    from database import db
    from app import app

    print("Testing template application fix...")
    
    # Create app context
    with app.app_context():
        # Create test manager
        manager = VirtualTemplateManager()
        
        # Check current special locations for DEFAULT warehouse
        print("\n=== Current Special Locations for DEFAULT ===")
        existing_locations = Location.query.filter(
            Location.warehouse_id == 'DEFAULT',
            Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL'])
        ).all()
        
        if existing_locations:
            print(f"Found {len(existing_locations)} existing special locations:")
            for loc in existing_locations:
                print(f"- {loc.code} ({loc.location_type}) - Zone: {loc.zone}, Capacity: {loc.capacity}")
        else:
            print("No existing special locations found")
        
        # Test the _create_physical_special_locations method directly
        print("\n=== Testing Special Location Creation Logic ===")
        
        # Create a mock template (you might need to adjust this based on your actual template structure)
        class MockTemplate:
            def __init__(self):
                self.name = "Test Template"
                self.num_aisles = 2
                self.receiving_areas_template = '[{"code": "RECV-01", "capacity": 10, "zone": "RECEIVING"}, {"code": "RECV-02", "capacity": 10, "zone": "RECEIVING"}]'
                self.staging_areas_template = '[{"code": "STAGE-01", "capacity": 5, "zone": "STAGING"}]'
                self.dock_areas_template = '[{"code": "DOCK-01", "capacity": 2, "zone": "DOCK"}]'
        
        # Create a mock user
        class MockUser:
            def __init__(self):
                self.id = 1
        
        mock_template = MockTemplate()
        mock_user = MockUser()
        
        print("Testing the fixed _create_physical_special_locations method...")
        
        try:
            # This should handle existing locations gracefully
            created_locations = manager._create_physical_special_locations(
                mock_template, 'DEFAULT', mock_user
            )
            
            print(f"SUCCESS: Method completed and created {len(created_locations)} locations")
            
            # Check what exists now
            final_locations = Location.query.filter(
                Location.warehouse_id == 'DEFAULT',
                Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL'])
            ).all()
            
            print(f"\nFinal state: {len(final_locations)} special locations exist:")
            for loc in final_locations:
                print(f"- {loc.code} ({loc.location_type}) - Zone: {loc.zone}, Capacity: {loc.capacity}")
                
            # Test applying again (should not fail)
            print("\n=== Testing Second Application (Should Not Fail) ===")
            created_locations_2 = manager._create_physical_special_locations(
                mock_template, 'DEFAULT', mock_user
            )
            print(f"SUCCESS: Second application completed and created {len(created_locations_2)} locations")
            
        except Exception as e:
            print(f"ERROR in template application: {e}")
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f"Error testing fix: {e}")
    import traceback
    traceback.print_exc()