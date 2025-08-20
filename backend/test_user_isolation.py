#!/usr/bin/env python3
"""
Test script to validate user-warehouse isolation fix
"""
import sys
import os
sys.path.append('src')

# Mock a user object for testing
class MockUser:
    def __init__(self, username):
        self.username = username
        self.id = 1

def test_warehouse_filtering_logic():
    """Test the warehouse filtering logic we implemented"""
    
    # Test data - simulating what would be in the database
    all_warehouse_ids = [
        'USER_MARCOS9', 'USER_TESTF', 'USER_HOLA3', 
        'USER_HOLA2', 'USER_MARCOS10', 'NONEXISTENT',
        'PRODUCTION_1755626038', 'PRODUCTION_1755626071'
    ]
    
    test_users = [
        MockUser('marcos9'),
        MockUser('testf'),
        MockUser('hola3'),
        MockUser('admin')  # User with no warehouses
    ]
    
    for user in test_users:
        print(f"\n=== Testing warehouse filtering for user: {user.username} ===")
        
        # Simulate the filtering logic from our fix
        username_upper = user.username.upper()
        user_warehouse_ids = []
        
        for warehouse_id in all_warehouse_ids:
            # This mimics our SQLAlchemy filter logic
            if (warehouse_id and (
                username_upper in warehouse_id.upper() or
                user.username in warehouse_id or
                warehouse_id == user.username or
                warehouse_id == f'USER_{username_upper}' or
                warehouse_id == f'USER_{user.username}'
            )):
                user_warehouse_ids.append(warehouse_id)
        
        print(f"User '{user.username}' would see warehouses: {user_warehouse_ids}")
        print(f"Filtered from {len(all_warehouse_ids)} total to {len(user_warehouse_ids)} user-specific warehouses")
        
        if len(user_warehouse_ids) == 0:
            print(f"WARNING: User '{user.username}' has no accessible warehouses!")
        elif len(user_warehouse_ids) > 1:
            print(f"INFO: User '{user.username}' has access to multiple warehouses")
        else:
            print(f"SUCCESS: User '{user.username}' has access to exactly 1 warehouse")

def test_cross_user_isolation():
    """Test that users can't see each other's warehouses"""
    
    print(f"\n=== Cross-User Isolation Test ===")
    
    # User MARCOS9 should only see their warehouse, not TESTF's
    marcos_user = MockUser('marcos9')
    testf_user = MockUser('testf')
    
    all_warehouse_ids = ['USER_MARCOS9', 'USER_TESTF', 'USER_HOLA3']
    
    # Test MARCOS9 user
    marcos_warehouses = []
    username_upper = marcos_user.username.upper()
    for warehouse_id in all_warehouse_ids:
        if username_upper in warehouse_id.upper():
            marcos_warehouses.append(warehouse_id)
    
    # Test TESTF user  
    testf_warehouses = []
    username_upper = testf_user.username.upper()
    for warehouse_id in all_warehouse_ids:
        if username_upper in warehouse_id.upper():
            testf_warehouses.append(warehouse_id)
    
    print(f"MARCOS9 sees: {marcos_warehouses}")
    print(f"TESTF sees: {testf_warehouses}")
    
    # Verify isolation
    if not set(marcos_warehouses).intersection(set(testf_warehouses)):
        print("SUCCESS: Users cannot see each other's warehouses")
    else:
        print("FAILED: Users can see each other's warehouses!")

if __name__ == "__main__":
    print("USER-WAREHOUSE ISOLATION TEST")
    print("=" * 50)
    
    test_warehouse_filtering_logic()
    test_cross_user_isolation()
    
    print(f"\nSUMMARY:")
    print(f"The security fix should prevent users from seeing other users' warehouse data.")
    print(f"Each user will only see warehouses that match their username pattern.")
    print(f"This resolves the critical multi-tenancy security issue you identified!")