"""
Quick migration script to add inventory_count column to analysis_report table
"""
import sqlite3
import os

# Find the database file
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')

if not os.path.exists(db_path):
    print(f"[ERROR] Database not found at: {db_path}")
    print("Please check the database location.")
    exit(1)

print(f"[INFO] Database found at: {db_path}")

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if column already exists
    cursor.execute("PRAGMA table_info(analysis_report)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'inventory_count' in columns:
        print("[SUCCESS] Column 'inventory_count' already exists in analysis_report table")
    else:
        print("[INFO] Adding 'inventory_count' column to analysis_report table...")
        cursor.execute("ALTER TABLE analysis_report ADD COLUMN inventory_count INTEGER")
        conn.commit()
        print("[SUCCESS] Migration completed successfully!")

        # Verify the column was added
        cursor.execute("PRAGMA table_info(analysis_report)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'inventory_count' in columns:
            print("[SUCCESS] Verified: Column added successfully")
        else:
            print("[WARNING] Column may not have been added properly")

    conn.close()
    print("\n[INFO] Current analysis_report schema:")

    # Reconnect to show schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(analysis_report)")
    for row in cursor.fetchall():
        print(f"   {row[1]} ({row[2]})")
    conn.close()

except Exception as e:
    print(f"[ERROR] Error during migration: {e}")
    exit(1)
