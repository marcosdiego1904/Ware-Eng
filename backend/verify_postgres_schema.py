"""
Verify PostgreSQL Schema and Data
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connection details
DB_NAME = "ware_eng_dev"
PG_USER = "postgres"
PG_PASSWORD = "Lavacalola44!"
PG_HOST = "localhost"
PG_PORT = "5432"

def verify_schema():
    """Verify database schema and data"""
    print("=" * 70)
    print("PostgreSQL Schema Verification")
    print("=" * 70)
    print()

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT
        )
        cursor = conn.cursor()

        # Check tables
        print("1. Checking tables...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"   Found {len(tables)} tables:")
        for table in tables:
            print(f"      - {table[0]}")
        print()

        # Check key tables exist
        expected_tables = [
            'user', 'analysis_report', 'anomaly', 'anomaly_history',
            'rule_category', 'rule', 'rule_history', 'rule_performance',
            'location', 'warehouse_config', 'warehouse_template'
        ]

        existing = [t[0] for t in tables]
        missing = [t for t in expected_tables if t not in existing]

        if missing:
            print(f"   [WARNING] Missing tables: {', '.join(missing)}")
        else:
            print("   [OK] All core tables exist")
        print()

        # Check users
        print("2. Checking users...")
        cursor.execute("SELECT COUNT(*) FROM \"user\"")
        user_count = cursor.fetchone()[0]
        print(f"   Users: {user_count}")

        if user_count > 0:
            cursor.execute("SELECT username FROM \"user\" LIMIT 5")
            users = cursor.fetchall()
            for user in users:
                print(f"      - {user[0]}")
        print()

        # Check rules
        print("3. Checking rules...")
        cursor.execute("SELECT COUNT(*) FROM rule")
        rule_count = cursor.fetchone()[0]
        print(f"   Rules: {rule_count}")

        if rule_count > 0:
            cursor.execute("SELECT name, rule_type, is_active FROM rule LIMIT 10")
            rules = cursor.fetchall()
            for rule in rules:
                status = "[ACTIVE]" if rule[2] else "[INACTIVE]"
                print(f"      {status} {rule[0]} ({rule[1]})")
        print()

        # Check rule categories
        print("4. Checking rule categories...")
        cursor.execute("SELECT name, display_name FROM rule_category")
        categories = cursor.fetchall()
        print(f"   Categories: {len(categories)}")
        for cat in categories:
            print(f"      - {cat[0]}: {cat[1]}")
        print()

        # Check locations
        print("5. Checking locations...")
        cursor.execute("SELECT COUNT(*) FROM location")
        location_count = cursor.fetchone()[0]
        print(f"   Locations: {location_count}")
        print()

        # Check warehouse configs
        print("6. Checking warehouse configurations...")
        cursor.execute("SELECT warehouse_id, warehouse_name, num_aisles, racks_per_aisle FROM warehouse_config")
        warehouses = cursor.fetchall()
        print(f"   Warehouses: {len(warehouses)}")
        for wh in warehouses:
            print(f"      - {wh[0]} ({wh[1]}): {wh[2]} aisles, {wh[3]} racks/aisle")
        print()

        # Check invitation codes
        print("7. Checking invitation codes...")
        cursor.execute("SELECT code, is_active, max_uses, current_uses FROM invitation_code")
        invites = cursor.fetchall()
        print(f"   Invitation codes: {len(invites)}")
        for inv in invites:
            print(f"      - {inv[0]} [{inv[2]-inv[3]}/{inv[2]} remaining]")
        print()

        cursor.close()
        conn.close()

        print("=" * 70)
        print("[SUCCESS] Database schema verification complete!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Create a test user")
        print("2. Test API endpoints")
        print("3. Upload test file and run analysis")
        return True

    except psycopg2.Error as e:
        print(f"[ERROR] PostgreSQL Error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    verify_schema()
