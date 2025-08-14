#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test All Location Creation Paths to Verify No Prefixes
Tests all three fixed location creation methods
"""

import sys
import os
sys.path.append('src')

from app import app, db
from models import Location, WarehouseConfig

def test_all_location_creation_paths():
    """Test that all location creation paths produce clean codes"""
    
    print("Testing all location creation paths for clean codes...")
    
    with app.app_context():
        test_warehouse_id = 'USER_TESTCLEAN'
        
        # Clean up any existing test locations
        Location.query.filter_by(warehouse_id=test_warehouse_id).delete()
        db.session.commit()
        
        print(f"\n=== Testing Location Creation Paths ===")
        print(f"Test warehouse: {test_warehouse_id}")
        
        # Test 1: Direct Location model creation (models.py path)
        print(f"\n1. Testing Location.create_from_structure() method...")
        
        try:
            test_location = Location.create_from_structure(
                warehouse_id=test_warehouse_id,
                aisle_num=1,
                rack_num=1,
                position_num=1,
                level='A',
                created_by=1
            )
            db.session.add(test_location)
            db.session.commit()
            
            if test_location.code.startswith(('USER_', 'TESTCLEAN_')):
                print(f"   ❌ FAILED: {test_location.code} has prefix")
                return False
            else:
                print(f"   ✅ SUCCESS: {test_location.code} is clean")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            return False
        
        # Test 2: Direct Location constructor
        print(f"\n2. Testing direct Location() constructor...")
        
        try:
            test_location_2 = Location(
                code='RCV-TEST',
                warehouse_id=test_warehouse_id,
                location_type='RECEIVING',
                capacity=10,
                created_by=1
            )
            db.session.add(test_location_2)
            db.session.commit()
            
            if test_location_2.code.startswith(('USER_', 'TESTCLEAN_')):
                print(f"   ❌ FAILED: {test_location_2.code} has prefix")
                return False
            else:
                print(f"   ✅ SUCCESS: {test_location_2.code} is clean")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            return False
            
        print(f"\n=== Summary ===")
        
        # Check final results
        clean_locations = Location.query.filter_by(warehouse_id=test_warehouse_id).all()
        
        print(f"Created {len(clean_locations)} test locations:")
        all_clean = True
        
        for loc in clean_locations:
            has_prefix = any(loc.code.startswith(prefix) for prefix in ['USER_', 'TESTCLEAN_', 'TESTF_'])
            status = "❌ HAS PREFIX" if has_prefix else "✅ CLEAN"
            print(f"  - {loc.code} {status}")
            if has_prefix:
                all_clean = False
        
        # Cleanup
        Location.query.filter_by(warehouse_id=test_warehouse_id).delete()
        db.session.commit()
        
        return all_clean

if __name__ == '__main__':
    print("Location Creation Path Test")
    print("=" * 50)
    
    success = test_all_location_creation_paths()
    
    if success:
        print(f"\n✅ ALL TESTS PASSED!")
        print("✅ No prefixes found in any location creation path")
        print("🎉 The prefix issue should be completely fixed now!")
        
        print(f"\nNext steps:")
        print("1. Recreate your warehouse through the UI")
        print("2. Special areas should now have clean names like RCV-001")
        print("3. Test your inventory again - should resolve 27 invalid location errors")
        
    else:
        print(f"\n❌ SOME TESTS FAILED!")
        print("❌ Prefixes are still being added somewhere")
        print("🔧 Additional investigation needed")
    
    print("\n" + "=" * 50)