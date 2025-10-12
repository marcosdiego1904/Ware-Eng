"""
Migration script to add warehouse_id and template_id to analysis_report table
"""
import sqlite3
import os

# Find the database file
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')

if not os.path.exists(db_path):
    print(f"[ERROR] Database not found at: {db_path}")
    exit(1)

print(f"[INFO] Database found at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute("PRAGMA table_info(analysis_report)")
    columns = [row[1] for row in cursor.fetchall()]

    # Add warehouse_id if missing
    if 'warehouse_id' not in columns:
        print("[INFO] Adding 'warehouse_id' column...")
        cursor.execute("ALTER TABLE analysis_report ADD COLUMN warehouse_id VARCHAR(50)")
        print("[SUCCESS] warehouse_id column added")
    else:
        print("[SUCCESS] warehouse_id column already exists")

    # Add template_id if missing
    if 'template_id' not in columns:
        print("[INFO] Adding 'template_id' column...")
        cursor.execute("ALTER TABLE analysis_report ADD COLUMN template_id INTEGER")
        print("[SUCCESS] template_id column added")
    else:
        print("[SUCCESS] template_id column already exists")

    conn.commit()
    conn.close()

    print("\n[INFO] Current analysis_report schema:")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(analysis_report)")
    for row in cursor.fetchall():
        print(f"   {row[1]} ({row[2]})")
    conn.close()

    print("\n[SUCCESS] Migration completed successfully!")

except Exception as e:
    print(f"[ERROR] Migration failed: {e}")
    exit(1)
