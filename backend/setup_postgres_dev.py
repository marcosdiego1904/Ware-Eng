"""
Setup PostgreSQL Database for Development
Creates a dedicated database for the Warehouse Intelligence Engine
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import getpass
import sys

def create_database():
    """Create the development database"""

    print("=" * 60)
    print("PostgreSQL Development Database Setup")
    print("=" * 60)
    print()

    # Get PostgreSQL credentials
    print("Enter your PostgreSQL credentials:")
    print("(These were set when you installed PostgreSQL)")
    print()

    pg_user = input("PostgreSQL username [postgres]: ").strip() or "postgres"
    pg_password = getpass.getpass("PostgreSQL password: ")
    pg_host = input("PostgreSQL host [localhost]: ").strip() or "localhost"
    pg_port = input("PostgreSQL port [5432]: ").strip() or "5432"

    print()
    print("Creating database 'ware_eng_dev'...")

    try:
        # Connect to PostgreSQL server (default 'postgres' database)
        conn = psycopg2.connect(
            dbname='postgres',
            user=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='ware_eng_dev'")
        exists = cursor.fetchone()

        if exists:
            print("⚠️  Database 'ware_eng_dev' already exists.")
            recreate = input("Do you want to DROP and recreate it? (yes/no): ").strip().lower()

            if recreate == 'yes':
                # Terminate existing connections
                cursor.execute("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = 'ware_eng_dev'
                    AND pid <> pg_backend_pid()
                """)

                # Drop database
                cursor.execute("DROP DATABASE ware_eng_dev")
                print("✅ Dropped existing database")

                # Create new database
                cursor.execute("CREATE DATABASE ware_eng_dev")
                print("✅ Created new database 'ware_eng_dev'")
            else:
                print("✅ Using existing database 'ware_eng_dev'")
        else:
            # Create database
            cursor.execute("CREATE DATABASE ware_eng_dev")
            print("✅ Created database 'ware_eng_dev'")

        cursor.close()
        conn.close()

        # Test connection to new database
        print()
        print("Testing connection to 'ware_eng_dev'...")
        test_conn = psycopg2.connect(
            dbname='ware_eng_dev',
            user=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port
        )
        test_cursor = test_conn.cursor()
        test_cursor.execute("SELECT version()")
        version = test_cursor.fetchone()[0]
        print(f"✅ Connection successful!")
        print(f"   PostgreSQL version: {version.split(',')[0]}")
        test_cursor.close()
        test_conn.close()

        # Generate connection string
        print()
        print("=" * 60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 60)
        print()
        print("Your database connection string:")
        print()
        connection_string = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/ware_eng_dev"
        # Show masked password for security
        masked_string = f"postgresql://{pg_user}:****@{pg_host}:{pg_port}/ware_eng_dev"
        print(f"   {masked_string}")
        print()
        print("IMPORTANT: Save this to your .env file:")
        print()
        print(f"DATABASE_URL={connection_string}")
        print()
        print("=" * 60)

        # Write to .env file
        env_path = "C:\\Users\\juanb\\Documents\\Diego\\Projects\\ware2\\backend\\.env"
        update_env = input("\nDo you want me to update your .env file automatically? (yes/no): ").strip().lower()

        if update_env == 'yes':
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
                    lines.append(f"\n# PostgreSQL Development Database\n")
                    lines.append(f"DATABASE_URL={connection_string}\n")

                # Write back
                with open(env_path, 'w') as f:
                    f.writelines(lines)

                print(f"✅ Updated {env_path}")
                print()
                print("Next steps:")
                print("1. Restart your Flask server")
                print("2. Run migrations to create tables")
                print("3. Test your application")

            except Exception as e:
                print(f"❌ Failed to update .env file: {e}")
                print(f"Please manually add the DATABASE_URL to your .env file")
        else:
            print("Please manually add the DATABASE_URL to your .env file")

        return True

    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error: {e}")
        print()
        print("Common issues:")
        print("1. Wrong password - Double-check your PostgreSQL password")
        print("2. PostgreSQL not running - Check if the service is running")
        print("3. Wrong host/port - Default is localhost:5432")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)
