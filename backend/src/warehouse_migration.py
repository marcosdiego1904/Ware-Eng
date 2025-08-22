"""
Migration Script: Warehouse Context Long-Term Solution
Creates UserWarehouseAccess records for existing users
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

def run_warehouse_migration():
    """
    Create database tables and migrate existing users to new warehouse system
    """
    print("Running Warehouse Context Migration...")
    print("=" * 60)
    
    try:
        # Set up Flask app context
        from app import app
        from database import db
        from core_models import User, UserWarehouseAccess
        from warehouse_context_resolver import warehouse_resolver
        
        with app.app_context():
            print("1. Creating database tables...")
            
            # Create new tables
            db.create_all()
            print("   Database tables created/updated")
            
            print("\n2. Migrating existing users...")
            
            # Run bulk migration using the resolver
            migration_results = warehouse_resolver.bulk_migrate_existing_users()
            
            print(f"   Users migrated: {migration_results['users_migrated']}")
            print(f"   Users skipped: {migration_results['users_skipped']}")
            
            if migration_results['created_access_records']:
                print("\n   Created warehouse access records:")
                for record in migration_results['created_access_records']:
                    print(f"     {record['username']} -> {record['warehouse_id']}")
            
            if migration_results['errors']:
                print("\n   Migration errors:")
                for error in migration_results['errors']:
                    print(f"     {error}")
            
            print("\n3. Validating migration...")
            
            # Verify migration results
            total_users = User.query.count()
            users_with_access = db.session.query(User.id).join(UserWarehouseAccess).distinct().count()
            
            print(f"   Total users: {total_users}")
            print(f"   Users with warehouse access: {users_with_access}")
            print(f"   Coverage: {users_with_access/total_users*100:.1f}%" if total_users > 0 else "   Coverage: N/A")
            
            print("\n4. Testing warehouse resolution...")
            
            # Test the new system with an existing user
            test_user = User.query.filter_by(username='testf').first()
            if test_user:
                test_context = warehouse_resolver.resolve_user_warehouse_context(test_user)
                print(f"   Test user 'testf' context: {test_context}")
                
                if test_context.get('warehouse_id'):
                    print("   Warehouse resolution working!")
                else:
                    print("   Warehouse resolution failed!")
            else:
                print("   Test user 'testf' not found")
            
            print("\n" + "=" * 60)
            print("Migration completed successfully!")
            print("\nNEXT STEPS:")
            print("1. Test the rule engine with the new system")
            print("2. Verify 30-anomaly detection is maintained")
            print("3. Monitor for any resolution issues")
            
            return True
            
    except Exception as e:
        print(f"\nMigration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_warehouse_migration()
    sys.exit(0 if success else 1)