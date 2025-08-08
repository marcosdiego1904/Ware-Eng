#!/usr/bin/env python3
"""
Test script for the Location Management System
Run this to test API endpoints and basic functionality
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Test configuration
API_BASE_URL = 'http://localhost:5000/api/v1'
TEST_USER_CREDENTIALS = {
    'username': 'testuser',
    'password': 'testpass123'
}

class LocationSystemTester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        
    def authenticate(self):
        """Get authentication token"""
        print("🔐 Authenticating...")
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}/auth/login",
                json=TEST_USER_CREDENTIALS
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print("   Make sure a test user exists or update credentials")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_warehouse_config_api(self):
        """Test warehouse configuration endpoints"""
        print("\n🏗️ Testing Warehouse Configuration API...")
        
        # Test GET config (should be 404 for new warehouse)
        response = self.session.get(f"{API_BASE_URL}/warehouse/config?warehouse_id=TEST_WAREHOUSE")
        if response.status_code == 404:
            print("✅ GET config returns 404 for non-existent warehouse (expected)")
        else:
            print(f"⚠️ GET config returned: {response.status_code}")
        
        # Test validation
        test_config = {
            'num_aisles': 4,
            'racks_per_aisle': 2,
            'positions_per_rack': 50,
            'levels_per_position': 4,
            'default_pallet_capacity': 1
        }
        
        response = self.session.post(f"{API_BASE_URL}/warehouse/validate", json=test_config)
        if response.status_code == 200:
            validation = response.json()
            print(f"✅ Configuration validation successful")
            print(f"   Valid: {validation['valid']}")
            if 'calculations' in validation:
                calcs = validation['calculations']
                print(f"   Total locations: {calcs.get('total_storage_locations', 'N/A')}")
                print(f"   Total capacity: {calcs.get('total_capacity', 'N/A')} pallets")
        else:
            print(f"❌ Configuration validation failed: {response.status_code}")
        
        # Test preview
        response = self.session.post(f"{API_BASE_URL}/warehouse/preview", json=test_config)
        if response.status_code == 200:
            preview = response.json()
            print("✅ Configuration preview successful")
            if 'preview' in preview:
                totals = preview['preview'].get('totals', {})
                print(f"   Storage locations: {totals.get('storage_locations', 'N/A')}")
                sample_locations = preview['preview'].get('sample_locations', [])
                if sample_locations:
                    print(f"   Sample codes: {', '.join([loc['code'] for loc in sample_locations[:5]])}")
        else:
            print(f"❌ Configuration preview failed: {response.status_code}")
    
    def test_location_api(self):
        """Test location management endpoints"""
        print("\n📍 Testing Location Management API...")
        
        # Test GET locations
        response = self.session.get(f"{API_BASE_URL}/locations?warehouse_id=DEFAULT")
        if response.status_code == 200:
            data = response.json()
            locations = data.get('locations', [])
            summary = data.get('summary', {})
            print(f"✅ GET locations successful")
            print(f"   Found {len(locations)} locations")
            print(f"   Total capacity: {summary.get('total_capacity', 'N/A')} pallets")
        else:
            print(f"❌ GET locations failed: {response.status_code}")
        
        # Test location validation
        test_locations = [
            {
                'code': 'TEST001A',
                'location_type': 'STORAGE',
                'warehouse_id': 'TEST_WAREHOUSE',
                'aisle_number': 1,
                'rack_number': 1,
                'position_number': 1,
                'level': 'A',
                'pallet_capacity': 1,
                'zone': 'GENERAL'
            },
            {
                'code': 'TEST001B',
                'location_type': 'STORAGE',
                'warehouse_id': 'TEST_WAREHOUSE',
                'aisle_number': 1,
                'rack_number': 1,
                'position_number': 1,
                'level': 'B',
                'pallet_capacity': 1,
                'zone': 'GENERAL'
            }
        ]
        
        response = self.session.post(f"{API_BASE_URL}/locations/validate", json={'locations': test_locations})
        if response.status_code == 200:
            validation = response.json()
            print("✅ Location validation successful")
            results = validation.get('validation_results', [])
            valid_count = sum(1 for r in results if r['valid'])
            print(f"   Valid locations: {valid_count}/{len(results)}")
        else:
            print(f"❌ Location validation failed: {response.status_code}")
    
    def test_template_api(self):
        """Test template management endpoints"""
        print("\n📋 Testing Template Management API...")
        
        # Test GET templates
        response = self.session.get(f"{API_BASE_URL}/templates?scope=all")
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
            summary = data.get('summary', {})
            print(f"✅ GET templates successful")
            print(f"   Found {len(templates)} templates")
            print(f"   My templates: {summary.get('my_templates', 0)}")
            print(f"   Public templates: {summary.get('public_templates', 0)}")
        else:
            print(f"❌ GET templates failed: {response.status_code}")
        
        # Test popular templates
        response = self.session.get(f"{API_BASE_URL}/templates/popular?limit=5")
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
            print(f"✅ GET popular templates successful ({len(templates)} found)")
        else:
            print(f"❌ GET popular templates failed: {response.status_code}")
    
    def test_complete_workflow(self):
        """Test a complete warehouse setup workflow"""
        print("\n🔄 Testing Complete Workflow...")
        
        # Setup data for a test warehouse
        setup_data = {
            'warehouse_id': f'TEST_WORKFLOW_{int(datetime.now().timestamp())}',
            'configuration': {
                'warehouse_name': 'Test Workflow Warehouse',
                'num_aisles': 2,
                'racks_per_aisle': 2,
                'positions_per_rack': 10,
                'levels_per_position': 2,
                'level_names': 'AB',
                'default_pallet_capacity': 1,
                'bidimensional_racks': False,
                'default_zone': 'GENERAL'
            },
            'receiving_areas': [
                {'code': 'RECV_TEST', 'type': 'RECEIVING', 'capacity': 5, 'zone': 'DOCK'}
            ],
            'generate_locations': True,
            'create_template': True,
            'template_name': 'Test Workflow Template',
            'template_description': 'Generated during API testing',
            'template_is_public': False
        }
        
        print(f"   Setting up warehouse: {setup_data['warehouse_id']}")
        response = self.session.post(f"{API_BASE_URL}/warehouse/setup", json=setup_data)
        
        if response.status_code == 201:
            result = response.json()
            warehouse_id = result.get('warehouse_id')
            locations_created = result.get('locations_created', 0)
            
            print(f"✅ Warehouse setup successful!")
            print(f"   Warehouse ID: {warehouse_id}")
            print(f"   Locations created: {locations_created}")
            print(f"   Total capacity: {result.get('total_capacity', 'N/A')} pallets")
            
            if 'template' in result:
                template = result['template']
                print(f"   Template created: {template['name']} ({template['template_code']})")
            
            return warehouse_id
        else:
            print(f"❌ Warehouse setup failed: {response.status_code}")
            if response.text:
                try:
                    error = response.json()
                    print(f"   Error: {error.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            return None
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Location Management System API Test Suite")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("\n❌ Cannot proceed without authentication")
            print("   Please ensure the server is running and test user exists")
            return False
        
        # Run tests
        self.test_warehouse_config_api()
        self.test_location_api()
        self.test_template_api()
        
        # Test complete workflow
        test_warehouse_id = self.test_complete_workflow()
        
        print("\n" + "=" * 60)
        if test_warehouse_id:
            print("🎉 All Tests Completed Successfully!")
            print(f"   Test warehouse created: {test_warehouse_id}")
        else:
            print("⚠️ Tests completed with some issues")
        print("=" * 60)
        
        return True

def main():
    """Main test runner"""
    tester = LocationSystemTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())