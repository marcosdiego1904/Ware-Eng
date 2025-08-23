#!/usr/bin/env python3
"""
Debug and fix testf user account
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from core_models import User, UserWarehouseAccess

def debug_testf_user():
    """Debug testf user account and permissions"""
    
    with app.app_context():
        print("=== DEBUGGING TESTF USER ===")
        
        # Find testf user
        testf_user = User.query.filter_by(username='testf').first()
        
        if not testf_user:
            print("ERROR: testf user not found! Creating...")
            testf_user = User(username='testf')
            testf_user.set_password('testf123')  # Set a known password
            db.session.add(testf_user)
            db.session.commit()
            print("SUCCESS: testf user created with password 'testf123'")
        else:
            print(f"SUCCESS: testf user found:")
            print(f"  - ID: {testf_user.id}")
            print(f"  - Username: {testf_user.username}")
            print(f"  - Created: {testf_user.created_at if hasattr(testf_user, 'created_at') else 'N/A'}")
            
            # Reset password to known value
            print("FIXING: Resetting password to 'testf123'...")
            testf_user.set_password('testf123')
            db.session.commit()
            print("SUCCESS: Password reset complete")
        
        # Check warehouse access
        print("\n=== CHECKING WAREHOUSE ACCESS ===")
        warehouse_access = UserWarehouseAccess.query.filter_by(user_id=testf_user.id).all()
        
        if warehouse_access:
            print(f"SUCCESS: Found {len(warehouse_access)} warehouse access records:")
            for access in warehouse_access:
                print(f"  - Warehouse: {access.warehouse_id}")
                print(f"  - Access Level: {access.access_level}")
                print(f"  - Default: {access.is_default}")
        else:
            print("ERROR: No warehouse access found! Creating...")
            
            # Create warehouse access for testf
            access = UserWarehouseAccess(
                user_id=testf_user.id,
                warehouse_id='USER_TESTF',
                access_level='ADMIN',
                is_default=True
            )
            db.session.add(access)
            db.session.commit()
            print("SUCCESS: Created warehouse access for USER_TESTF")
        
        # Check user permissions/roles
        print("\n=== CHECKING USER ATTRIBUTES ===")
        user_dict = {}
        for attr in dir(testf_user):
            if not attr.startswith('_') and not callable(getattr(testf_user, attr)):
                try:
                    value = getattr(testf_user, attr)
                    user_dict[attr] = value
                except:
                    user_dict[attr] = "Error accessing"
        
        for key, value in user_dict.items():
            print(f"  - {key}: {value}")
        
        print(f"\n=== TESTING PASSWORD ===")
        test_password = 'testf123'
        if testf_user.check_password(test_password):
            print(f"SUCCESS: Password '{test_password}' works!")
        else:
            print(f"ERROR: Password '{test_password}' failed!")
            
        return testf_user

if __name__ == '__main__':
    debug_testf_user()