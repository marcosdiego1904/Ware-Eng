"""
Simple PostgreSQL Database Setup Script
Creates the ware_eng_dev database with provided credentials
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

# Credentials
PG_USER = "postgres"
PG_PASSWORD = "Lavacalola44!"
PG_HOST = "localhost"
PG_PORT = "5432"
DB_NAME = "ware_eng_dev"

def setup_database():
    """Create the development database"""
    print("=" * 70)
    print("PostgreSQL Development Database Setup")
    print("=" * 70)
    print(f"Creating database: {DB_NAME}")
    print(f"Host: {PG_HOST}:{PG_PORT}")
    print(f"User: {PG_USER}")
    print()

    try:
        # Connect to PostgreSQL server (default 'postgres' database)
        print("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            dbname='postgres',
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print("[OK] Connected successfully")
        print()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'")
        exists = cursor.fetchone()

        if exists:
            print(f"[WARNING] Database '{DB_NAME}' already exists")
            print("Dropping and recreating...")

            # Terminate existing connections
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{DB_NAME}'
                AND pid <> pg_backend_pid()
            """)

            # Drop database
            cursor.execute(f"DROP DATABASE {DB_NAME}")
            print(f"[OK] Dropped existing database")

        # Create database
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"[OK] Created database '{DB_NAME}'")
        print()

        cursor.close()
        conn.close()

        # Test connection to new database
        print(f"Testing connection to '{DB_NAME}'...")
        test_conn = psycopg2.connect(
            dbname=DB_NAME,
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT
        )
        test_cursor = test_conn.cursor()
        test_cursor.execute("SELECT version()")
        version = test_cursor.fetchone()[0]
        print("[OK] Connection successful!")
        print(f"   {version.split(',')[0]}")
        test_cursor.close()
        test_conn.close()

        # Generate connection string
        print()
        print("=" * 70)
        print("[SUCCESS] DATABASE SETUP COMPLETE!")
        print("=" * 70)
        print()

        connection_string = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{DB_NAME}"
        print("Connection string (add to .env):")
        print()
        print(f"DATABASE_URL={connection_string}")
        print()
        print("=" * 70)

        return connection_string

    except psycopg2.Error as e:
        print(f"[ERROR] PostgreSQL Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Verify PostgreSQL service is running")
        print("2. Check if password is correct")
        print("3. Ensure postgres user has CREATE DATABASE permission")
        return None

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return None

if __name__ == "__main__":
    connection_string = setup_database()

    if connection_string:
        # Update .env file
        env_path = "C:\\Users\\juanb\\Documents\\Diego\\Projects\\ware2\\backend\\.env"
        print(f"\nUpdating {env_path}...")

        try:
            # Read existing .env
            try:
                with open(env_path, 'r') as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []

            # Update or add DATABASE_URL
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('DATABASE_URL='):
                    lines[i] = f"DATABASE_URL={connection_string}\n"
                    updated = True
                    break

            if not updated:
                if lines and not lines[-1].endswith('\n'):
                    lines.append('\n')
                lines.append(f"\n# PostgreSQL Development Database\n")
                lines.append(f"DATABASE_URL={connection_string}\n")

            # Write back
            with open(env_path, 'w') as f:
                f.writelines(lines)

            print("[OK] Updated .env file successfully")
            print()
            print("Next steps:")
            print("1. Restart your Flask server (it will now use PostgreSQL)")
            print("2. Run migrations to create tables")
            print("3. Test your application")

            sys.exit(0)

        except Exception as e:
            print(f"[WARNING] Could not update .env file: {e}")
            print("Please manually add the DATABASE_URL to your .env file")
            sys.exit(1)
    else:
        print("\n[ERROR] Database setup failed")
        sys.exit(1)
