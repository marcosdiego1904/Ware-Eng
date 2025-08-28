#!/usr/bin/env python3
"""
Debug how user-warehouse mapping currently works
"""

import sys
sys.path.append('src')

from app import app
from database import db
from models import WarehouseConfig
from core_models import User

def debug_user_warehouse_mapping():
    """Investigate current user-warehouse relationship"""
    print("DEBUGGING USER-WAREHOUSE MAPPING")
    print("=" * 50)
    
    with app.app_context():
        # Get all users
        users = User.query.all()
        print(f"Total users: {len(users)}")
        
        # Get all warehouse configs
        configs = WarehouseConfig.query.all()
        print(f"Total warehouse configs: {len(configs)}")
        
        print(f"\nUser-Warehouse Analysis:")
        print("-" * 30)
        
        user_warehouses = {}
        
        for user in users[:10]:  # First 10 users
            print(f"\nUser: {user.username} (ID: {user.id})")
            
            # Find warehouses associated with this user
            user_configs = []
            
            # Method 1: Check warehouse_id patterns (USER_username format)
            user_pattern = f'USER_{user.username.upper()}'
            pattern_matches = [c for c in configs if c.warehouse_id.startswith(user_pattern)]
            if pattern_matches:
                user_configs.extend(pattern_matches)
                print(f"  Pattern matches: {[c.warehouse_id for c in pattern_matches]}")
            
            # Method 2: Check created_by field
            created_matches = [c for c in configs if c.created_by == user.id]
            if created_matches:
                user_configs.extend(created_matches)
                print(f"  Created by user: {[c.warehouse_id for c in created_matches]}")
            
            # Method 3: Check if user has a default warehouse
            if user.username.upper() in ['MARCOS9', 'HOLA3', 'HOLA4', 'HOLA5']:
                expected_warehouse = f'USER_{user.username.upper()}'
                expected_config = WarehouseConfig.query.filter_by(warehouse_id=expected_warehouse).first()
                if expected_config:
                    print(f"  Expected warehouse exists: {expected_warehouse}")
                    if expected_config not in user_configs:
                        user_configs.append(expected_config)
            
            # Remove duplicates
            user_configs = list(set(user_configs))
            user_warehouses[user.username] = user_configs
            
            if user_configs:
                print(f"  Total warehouses: {len(user_configs)}")
                for config in user_configs:
                    special_count = len(config.get_receiving_areas()) + len(config.get_staging_areas()) + len(config.get_dock_areas())
                    print(f"    - {config.warehouse_id}: {config.warehouse_name} ({special_count} special areas)")
            else:
                print(f"  No warehouses found for {user.username}")
        
        return user_warehouses

def find_current_user_warehouse_logic():
    """Check how the frontend determines current user's warehouse"""
    print(f"\n{'='*50}")
    print("CURRENT WAREHOUSE DETECTION LOGIC")
    print("=" * 50)
    
    with app.app_context():
        # Check if there's a pattern for determining user's warehouse
        print("Checking common warehouse ID patterns:")
        
        # Get sample users
        users = User.query.limit(5).all()
        
        for user in users:
            possible_warehouses = [
                f'USER_{user.username.upper()}',
                f'USER_{user.username}',
                f'{user.username.upper()}',
                f'{user.id}',
                f'WAREHOUSE_{user.id}',
                'DEFAULT'
            ]
            
            print(f"\nUser: {user.username}")
            existing_warehouses = []
            
            for warehouse_id in possible_warehouses:
                config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
                if config:
                    existing_warehouses.append({
                        'warehouse_id': warehouse_id,
                        'name': config.warehouse_name,
                        'special_areas': len(config.get_receiving_areas()) + len(config.get_staging_areas()) + len(config.get_dock_areas())
                    })
            
            if existing_warehouses:
                print(f"  Existing warehouses:")
                for wh in existing_warehouses:
                    print(f"    - {wh['warehouse_id']}: {wh['name']} ({wh['special_areas']} special areas)")
                
                # Suggest primary warehouse
                user_specific = [wh for wh in existing_warehouses if user.username.upper() in wh['warehouse_id']]
                if user_specific:
                    print(f"  -> Suggested primary: {user_specific[0]['warehouse_id']}")
                else:
                    print(f"  -> Fallback to: {existing_warehouses[0]['warehouse_id']}")
            else:
                print(f"  No warehouses found - would default to DEFAULT")

def analyze_frontend_routing():
    """Analyze how frontend should route users to their warehouses"""
    print(f"\n{'='*50}")
    print("FRONTEND ROUTING ANALYSIS")
    print("=" * 50)
    
    print("Current Issues:")
    print("1. Frontend might be hardcoded to 'DEFAULT' warehouse")
    print("2. Missing user-specific warehouse detection")
    print("3. No dynamic routing based on current user")
    
    print(f"\nRecommended Solution:")
    print("1. Frontend should detect current user from auth context")
    print("2. Look up user's primary warehouse (USER_{username} pattern)")
    print("3. Fallback to DEFAULT only if user has no specific warehouse")
    print("4. Update location-manager to use dynamic warehouseId")

if __name__ == "__main__":
    user_warehouses = debug_user_warehouse_mapping()
    find_current_user_warehouse_logic() 
    analyze_frontend_routing()
    
    print(f"\n{'='*50}")
    print("SUMMARY:")
    print("- Users have specific warehouses (USER_username pattern)")
    print("- Frontend needs dynamic warehouse detection")
    print("- Special locations should reflect user's specific template")
    print("- Current DEFAULT fallback is temporary solution")