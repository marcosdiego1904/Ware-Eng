"""
Create admin user directly in production PostgreSQL database
Run this to create the admin user you set up earlier
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def create_admin_user(username, password):
    """Create admin user in production database"""
    from werkzeug.security import generate_password_hash
    import psycopg2

    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("[ERROR] DATABASE_URL not found in environment")
        print("Make sure you have a .env file with DATABASE_URL set")
        return False

    # Fix postgres:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        # Check if user already exists
        cur.execute('SELECT id, username, is_admin FROM "user" WHERE username = %s', (username,))
        existing = cur.fetchone()

        if existing:
            print(f"[INFO] User '{username}' already exists (id: {existing[0]})")
            print(f"[INFO] Updating to admin...")
            cur.execute('UPDATE "user" SET is_admin = TRUE WHERE username = %s', (username,))
            conn.commit()
            print(f"[SUCCESS] User '{username}' is now an admin")
        else:
            # Generate password hash
            password_hash = generate_password_hash(password)

            # Create user
            cur.execute('''
                INSERT INTO "user" (username, password_hash, is_admin, max_reports, max_templates,
                                   clear_previous_anomalies, show_clear_warning)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (username, password_hash, True, 999, 999, True, True))

            user_id = cur.fetchone()[0]
            conn.commit()

            print(f"[SUCCESS] Admin user '{username}' created successfully (id: {user_id})")

        # Verify
        cur.execute('SELECT id, username, is_admin FROM "user" WHERE username = %s', (username,))
        result = cur.fetchone()
        print(f"\nVerification:")
        print(f"  ID: {result[0]}")
        print(f"  Username: {result[1]}")
        print(f"  is_admin: {result[2]}")

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"[ERROR] Failed to create user: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Create Admin User in Production Database")
    print("=" * 60)
    print()

    username = input("Enter admin username: ").strip()
    password = input("Enter admin password: ").strip()

    print()
    print("Creating admin user in production database...")
    print()

    success = create_admin_user(username, password)

    if success:
        print()
        print("=" * 60)
        print("Admin user ready! You can now:")
        print("1. Restart your backend server")
        print("2. Login with these credentials")
        print("3. Access /admin/pilot-analytics")
        print("=" * 60)
