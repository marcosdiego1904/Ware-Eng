#!/usr/bin/env python3
"""
Test the enhanced special location creation error detection.
This will help identify the "missing one location" bug pattern.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from models import WarehouseTemplate
from core_models import User
from virtual_template_integration import VirtualTemplateManager
from database import db
import json

def test_problematic_location_scenarios():
    """Test various problematic location scenarios that could cause silent failures"""
    
    with app.app_context():
        print("🔍 TESTING SPECIAL LOCATION BUG DETECTION")
        print("=" * 60)
        
        # Create a test user
        test_user = User.query.filter_by(username='test_user').first()
        if not test_user:
            test_user = User(
                username='test_user',
                email='test@example.com',
                password_hash='dummy'
            )
            db.session.add(test_user)
            db.session.commit()
        
        # Test scenarios that could cause silent failures
        problematic_scenarios = [
            {
                'name': 'Trailing Spaces Bug',
                'staging_areas': [
                    {'code': 'STAGING_01', 'capacity': 5},
                    {'code': 'STAGING_02 ', 'capacity': 5},  # Trailing space
                    {'code': 'STAGING_03', 'capacity': 5},
                ]
            },
            {
                'name': 'Empty Location Code',
                'staging_areas': [
                    {'code': 'STAGING_01', 'capacity': 5},
                    {'code': '', 'capacity': 5},  # Empty code
                    {'code': 'STAGING_03', 'capacity': 5},
                ]
            },
            {
                'name': 'Duplicate Location Codes',
                'staging_areas': [
                    {'code': 'STAGING_01', 'capacity': 5},
                    {'code': 'STAGING_01', 'capacity': 10},  # Duplicate
                    {'code': 'STAGING_03', 'capacity': 5},
                ]
            },
            {
                'name': 'Very Long Location Code',
                'staging_areas': [
                    {'code': 'STAGING_01', 'capacity': 5},
                    {'code': 'A' * 60, 'capacity': 5},  # Too long (>50 chars)
                    {'code': 'STAGING_03', 'capacity': 5},
                ]
            },
            {
                'name': 'Mixed Valid and Invalid',
                'staging_areas': [
                    {'code': 'STAGING_AREA_01', 'capacity': 5},
                    {'code': 'STAGING_AREA_02', 'capacity': 5},
                    {'code': 'STAGING_AREA_03', 'capacity': 5},
                    {'code': 'STAGING_AREA_04', 'capacity': 5},
                    {'code': 'STAGING_AREA_05 ', 'capacity': 5},  # Trailing space
                    {'code': 'STAGING_AREA_06', 'capacity': 5},
                    {'code': 'STAGING_AREA_07', 'capacity': 5},
                    {'code': 'STAGING_AREA_08', 'capacity': 5},
                    {'code': 'STAGING_AREA_09', 'capacity': 5},
                    {'code': 'STAGING_AREA_10', 'capacity': 5},
                    {'code': 'STAGING_AREA_11', 'capacity': 5},
                    {'code': 'STAGING_AREA_12', 'capacity': 5},
                    {'code': 'STAGING_AREA_13', 'capacity': 5},
                    {'code': 'STAGING_AREA_14', 'capacity': 5},
                    {'code': '', 'capacity': 5},  # Empty code (this should be the "missing one")
                ]
            }
        ]
        
        virtual_manager = VirtualTemplateManager()
        
        for scenario in problematic_scenarios:
            print(f"\n🧪 Testing Scenario: {scenario['name']}")
            print("-" * 40)
            
            # Create test template
            template = WarehouseTemplate(
                name=f"Test Template - {scenario['name']}",
                template_code=f"TEST_{scenario['name'].replace(' ', '_').upper()}",
                num_aisles=2,
                racks_per_aisle=2,
                positions_per_rack=10,
                levels_per_position=4,
                level_names='ABCD',
                staging_areas_template=json.dumps(scenario['staging_areas']),
                created_by=test_user.id,
                is_active=True
            )
            
            db.session.add(template)
            db.session.commit()
            
            # Test the enhanced location creation
            try:
                warehouse_id = f"TEST_WAREHOUSE_{template.id}"
                result = virtual_manager._create_physical_special_locations(
                    template, warehouse_id, test_user
                )
                
                expected_count = len(scenario['staging_areas'])
                actual_count = result['success_count']
                failed_count = result['failure_count']
                
                print(f"   Expected locations: {expected_count}")
                print(f"   ✅ Created locations: {actual_count}")
                print(f"   ❌ Failed locations: {failed_count}")
                
                if failed_count > 0:
                    print(f"   📋 FAILURE DETAILS:")
                    for failure in result['failed_locations']:
                        print(f"      - {failure['code']} ({failure['type']}): {failure['error']}")
                
                # This should detect the exact pattern you experienced
                if expected_count == 15 and actual_count == 14 and failed_count == 1:
                    print(f"   🎯 REPRODUCED THE BUG! Expected 15, got 14, failed 1")
                    print(f"   🔍 Root cause: {result['failed_locations'][0]['error']}")
                
                print(f"   📊 Success Rate: {(actual_count/expected_count)*100:.1f}%")
                
                # Clean up
                db.session.rollback()  # Don't actually save test locations
                
            except Exception as e:
                print(f"   ❌ Test failed with exception: {e}")
                db.session.rollback()
            
            # Clean up template
            try:
                db.session.delete(template)
                db.session.commit()
            except:
                db.session.rollback()

if __name__ == "__main__":
    test_problematic_location_scenarios()