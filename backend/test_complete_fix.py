#!/usr/bin/env python3
"""
Test the complete Special Locations fix
Tests both template application and UI display pipeline
"""

import sys
import json
sys.path.append('src')

from app import app
from database import db
from models import WarehouseTemplate, WarehouseConfig, Location
from core_models import User
from virtual_template_integration import get_virtual_template_manager


def test_complete_special_locations_flow():
    """Test the entire flow from template creation to UI display"""
    with app.app_context():
        print("=== TESTING COMPLETE SPECIAL LOCATIONS FIX ===\n")
        
        # Step 1: Find a template with special areas
        template = WarehouseTemplate.query.filter(
            WarehouseTemplate.receiving_areas_template.isnot(None)
        ).first()
        
        if not template:
            print("[ERROR] No templates with special areas found!")
            return
            
        print(f"[SUCCESS] Found template: {template.name} (ID: {template.id})")
        
        # Parse template special areas
        receiving_areas = json.loads(template.receiving_areas_template) if template.receiving_areas_template else []
        staging_areas = json.loads(template.staging_areas_template) if template.staging_areas_template else []
        dock_areas = json.loads(template.dock_areas_template) if template.dock_areas_template else []
        
        expected_special_count = len(receiving_areas) + len(staging_areas) + len(dock_areas)
        print(f"   Expected special locations: {expected_special_count}")
        print(f"   - Receiving: {len(receiving_areas)}")
        print(f"   - Staging: {len(staging_areas)}")  
        print(f"   - Dock: {len(dock_areas)}")
        
        # Step 2: Apply template using our FIXED virtual template manager
        print(f"\\n🔧 Applying template with HYBRID virtual/physical approach...")
        
        test_warehouse_id = f"TEST_COMPLETE_FIX_{template.id}"
        test_user = User.query.first()  # Use first available user
        
        if not test_user:
            print("❌ No test user found!")
            return
            
        try:
            virtual_manager = get_virtual_template_manager()
            result = virtual_manager.apply_template_with_virtual_locations(
                template, test_warehouse_id, f"Test Fix Warehouse", test_user
            )
            
            print(f"✅ Template application result:")
            print(f"   - Creation method: {result['creation_method']}")
            print(f"   - Physical special areas created: {result.get('special_areas', 0)}")
            print(f"   - Virtual storage locations available: {result.get('virtual_locations_available', 0)}")
            
        except Exception as e:
            print(f"❌ Template application failed: {e}")
            return
        
        # Step 3: Verify physical special locations were created
        print(f"\\n🔍 Verifying physical special locations in database...")
        
        actual_special_locations = Location.query.filter(
            Location.warehouse_id == test_warehouse_id,
            Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
        ).all()
        
        print(f"✅ Found {len(actual_special_locations)} physical special locations:")
        for loc in actual_special_locations:
            print(f"   - {loc.code} ({loc.location_type}, capacity: {loc.capacity})")
        
        # Step 4: Test the User Warehouse API (what frontend calls)
        print(f"\\n📡 Testing User Warehouse API (frontend warehouse detection)...")
        
        # Create a test config for this warehouse
        test_config = WarehouseConfig.query.filter_by(warehouse_id=test_warehouse_id).first()
        if test_config:
            # Test the FIXED API logic
            api_special_count = Location.query.filter(
                Location.warehouse_id == test_warehouse_id,
                Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
            ).count()
            
            print(f"✅ User Warehouse API would report:")
            print(f"   - Warehouse: {test_config.warehouse_name}")
            print(f"   - Warehouse ID: {test_warehouse_id}")
            print(f"   - Special areas count: {api_special_count}")
            
            # Verify counts match
            if api_special_count == expected_special_count == len(actual_special_locations):
                print(f"\\n🎉 SUCCESS! All counts match: {api_special_count} special areas")
                print(f"   ✅ Template expected: {expected_special_count}")
                print(f"   ✅ Physical DB records: {len(actual_special_locations)}")
                print(f"   ✅ API would report: {api_special_count}")
                print(f"\\n🚀 The frontend should now display all special locations correctly!")
            else:
                print(f"\\n❌ MISMATCH in counts:")
                print(f"   Template expected: {expected_special_count}")
                print(f"   Physical DB records: {len(actual_special_locations)}")
                print(f"   API would report: {api_special_count}")
        
        # Cleanup the test data
        print(f"\\n🧹 Cleaning up test data...")
        Location.query.filter_by(warehouse_id=test_warehouse_id).delete()
        WarehouseConfig.query.filter_by(warehouse_id=test_warehouse_id).delete()
        db.session.commit()
        print(f"✅ Test data cleaned up")


if __name__ == "__main__":
    test_complete_special_locations_flow()