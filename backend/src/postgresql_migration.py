"""
PostgreSQL Production Migration
Creates UserWarehouseAccess table specifically for PostgreSQL on Render
"""

import os
import sys
import psycopg2
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

def run_postgresql_migration():
    """
    Create UserWarehouseAccess table in PostgreSQL production database
    """
    print("Running PostgreSQL Production Migration...")
    print("=" * 60)
    
    try:
        # Set up Flask app context for database URL
        from app import app
        from database import db
        from core_models import User, UserWarehouseAccess
        
        with app.app_context():
            print("1. Connecting to PostgreSQL database...")
            
            # Get database URL from Flask config
            database_url = app.config.get('DATABASE_URL') or app.config.get('SQLALCHEMY_DATABASE_URI')
            print(f"   Database URL: {database_url[:50]}..." if database_url else "   No database URL found")
            
            print("\n2. Creating UserWarehouseAccess table if not exists...")
            
            # Use raw SQL to create table with PostgreSQL-specific syntax
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS user_warehouse_access (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES "user"(id),
                warehouse_id VARCHAR(50) NOT NULL,
                access_level VARCHAR(20) DEFAULT 'READ',
                is_default BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, warehouse_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_user_warehouse ON user_warehouse_access(user_id, warehouse_id);
            CREATE INDEX IF NOT EXISTS idx_user_default ON user_warehouse_access(user_id, is_default);
            """
            
            # Execute raw SQL
            db.session.execute(db.text(create_table_sql))
            db.session.commit()
            print("   Table created successfully")
            
            print("\n3. Checking for existing data...")
            
            # Check if table has data
            try:
                existing_count = db.session.execute(
                    db.text("SELECT COUNT(*) FROM user_warehouse_access")
                ).scalar()
                print(f"   Found {existing_count} existing warehouse access records")
                
                if existing_count > 0:
                    print("   Migration already completed")
                    return True
            except Exception as e:
                print(f"   Error checking existing data: {e}")
            
            print("\n4. Migrating users to warehouse access...")
            
            # Get all users
            users = User.query.all()
            print(f"   Found {users} users to migrate")
            
            created_count = 0
            for user in users:
                try:
                    # Determine warehouse ID
                    username = user.username.lower()
                    if username == 'testf':
                        warehouse_id = 'USER_TESTF'
                    elif username == 'marcos9':
                        warehouse_id = 'USER_MARCOS9'
                    elif username == 'alice':
                        warehouse_id = 'USER_ALICE'
                    else:
                        warehouse_id = f'USER_{user.username.upper()}'
                    
                    # Insert warehouse access record using raw SQL
                    insert_sql = """
                    INSERT INTO user_warehouse_access (user_id, warehouse_id, access_level, is_default)
                    VALUES (:user_id, :warehouse_id, 'ADMIN', true)
                    ON CONFLICT (user_id, warehouse_id) DO NOTHING
                    """
                    
                    result = db.session.execute(db.text(insert_sql), {
                        'user_id': user.id,
                        'warehouse_id': warehouse_id
                    })
                    
                    if result.rowcount > 0:
                        created_count += 1
                        print(f"   Created access: {user.username} -> {warehouse_id}")
                    else:
                        print(f"   Already exists: {user.username} -> {warehouse_id}")
                        
                except Exception as e:
                    print(f"   ERROR creating access for {user.username}: {e}")
            
            db.session.commit()
            print(f"\n   Successfully created {created_count} new warehouse access records")
            
            print("\n5. Validating migration...")
            
            # Verify the migration
            total_users = User.query.count()
            total_access = db.session.execute(
                db.text("SELECT COUNT(*) FROM user_warehouse_access")
            ).scalar()
            
            print(f"   Total users: {total_users}")
            print(f"   Total warehouse access records: {total_access}")
            print(f"   Coverage: {total_access/total_users*100:.1f}%" if total_users > 0 else "   Coverage: N/A")
            
            # Test specific user
            testf_access = db.session.execute(
                db.text("""
                    SELECT warehouse_id, access_level, is_default 
                    FROM user_warehouse_access ua
                    JOIN "user" u ON ua.user_id = u.id
                    WHERE u.username = 'testf'
                """)
            ).fetchone()
            
            if testf_access:
                print(f"   testf access: {testf_access[0]} ({testf_access[1]}, default: {testf_access[2]})")
            else:
                print("   WARNING: testf user access not found")
            
            print("\n" + "=" * 60)
            print("PostgreSQL migration completed successfully!")
            print("\nThe long-term warehouse context resolution is now live in production!")
            
            return True
            
    except Exception as e:
        print(f"\nPostgreSQL migration failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to rollback
        try:
            db.session.rollback()
        except:
            pass
            
        return False

if __name__ == "__main__":
    success = run_postgresql_migration()
    sys.exit(0 if success else 1)