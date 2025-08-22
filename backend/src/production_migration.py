"""
Production Database Migration: Create UserWarehouseAccess table
This migration will work with the live production database
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

def run_production_migration():
    """
    Create UserWarehouseAccess table in production database
    """
    print("Running Production Database Migration...")
    print("=" * 60)
    
    try:
        # Set up Flask app context
        from app import app
        from database import db
        from core_models import User, UserWarehouseAccess
        
        with app.app_context():
            print("1. Checking current database state...")
            
            # Check if table already exists
            try:
                existing_count = UserWarehouseAccess.query.count()
                print(f"   UserWarehouseAccess table exists with {existing_count} records")
                return True
            except Exception as e:
                print(f"   UserWarehouseAccess table does not exist: {e}")
            
            print("\n2. Creating UserWarehouseAccess table...")
            
            # Create the table
            db.create_all()
            print("   Table created successfully")
            
            print("\n3. Creating warehouse access for existing users...")
            
            # Get all users
            users = User.query.all()
            print(f"   Found {len(users)} users to migrate")
            
            created_count = 0
            for user in users:
                try:
                    # Check if user already has warehouse access
                    existing_access = UserWarehouseAccess.query.filter_by(user_id=user.id).first()
                    if existing_access:
                        print(f"   User {user.username} already has warehouse access")
                        continue
                    
                    # Determine warehouse ID for user
                    if user.username.lower() == 'testf':
                        warehouse_id = 'USER_TESTF'
                    elif user.username.lower() == 'marcos9':
                        warehouse_id = 'USER_MARCOS9'
                    elif user.username.lower() == 'alice':
                        warehouse_id = 'USER_ALICE'
                    else:
                        warehouse_id = f'USER_{user.username.upper()}'
                    
                    # Create warehouse access record
                    warehouse_access = UserWarehouseAccess(
                        user_id=user.id,
                        warehouse_id=warehouse_id,
                        access_level='ADMIN',
                        is_default=True
                    )
                    
                    db.session.add(warehouse_access)
                    created_count += 1
                    
                    print(f"   Created access: {user.username} -> {warehouse_id}")
                    
                except Exception as e:
                    print(f"   ERROR creating access for {user.username}: {e}")
            
            # Commit all changes
            db.session.commit()
            print(f"\n   Successfully created {created_count} warehouse access records")
            
            print("\n4. Validating migration...")
            
            # Verify the migration
            total_users = User.query.count()
            users_with_access = db.session.query(User.id).join(UserWarehouseAccess).distinct().count()
            
            print(f"   Total users: {total_users}")
            print(f"   Users with warehouse access: {users_with_access}")
            print(f"   Coverage: {users_with_access/total_users*100:.1f}%" if total_users > 0 else "   Coverage: N/A")
            
            # Test user resolution
            from warehouse_context_resolver import resolve_warehouse_context_for_user
            test_user = User.query.filter_by(username='testf').first()
            if test_user:
                try:
                    test_context = resolve_warehouse_context_for_user(test_user)
                    print(f"   Test resolution: {test_user.username} -> {test_context.get('warehouse_id')}")
                except Exception as e:
                    print(f"   Test resolution failed: {e}")
            
            print("\n" + "=" * 60)
            print("Production migration completed successfully!")
            
            return True
            
    except Exception as e:
        print(f"\nProduction migration failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to rollback
        try:
            db.session.rollback()
        except:
            pass
            
        return False

if __name__ == "__main__":
    success = run_production_migration()
    sys.exit(0 if success else 1)