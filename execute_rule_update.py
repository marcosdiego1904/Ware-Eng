#!/usr/bin/env python3
"""
Execute rule updates directly on the SQLite database
"""
import sqlite3
import json
import os

def execute_rule_updates():
    """Execute the rule threshold updates"""
    
    # Find the correct database file
    db_paths = [
        'backend/instance/warehouse.db',
        'backend/warehouse.db', 
        'instance/warehouse_rules.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("Error: Could not find warehouse database file")
        return False
    
    print(f"Using database: {db_path}")
    print()
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== EXECUTING RULE THRESHOLD UPDATES ===")
        print()
        
        # Check current Rule #1
        print("1. Current Rule #1 status:")
        cursor.execute("SELECT id, name, rule_type, conditions, priority FROM rule WHERE id = 1")
        current_rule = cursor.fetchone()
        if current_rule:
            print(f"   ID: {current_rule[0]}")
            print(f"   Name: {current_rule[1]}")
            print(f"   Type: {current_rule[2]}")
            print(f"   Conditions: {current_rule[3]}")
            print(f"   Priority: {current_rule[4]}")
        else:
            print("   Rule #1 not found!")
            return False
        print()
        
        # Update Rule #1
        print("2. Updating Rule #1...")
        update_sql = """
        UPDATE rule SET
          name = 'Forgotten Pallets in Receiving',
          description = 'Detects pallets that have been in receiving areas for more than 10 hours, indicating they may have been forgotten during normal processing workflow.',
          conditions = '{"time_threshold_hours": 10, "location_types": ["RECEIVING"]}',
          priority = 'HIGH'
        WHERE id = 1
        """
        cursor.execute(update_sql)
        print("   Rule #1 updated successfully!")
        print()
        
        # Check if Rule #1B already exists
        print("3. Checking for existing transit rule...")
        cursor.execute("SELECT id FROM rule WHERE name = 'Stuck Pallets in Transit'")
        existing_rule1b = cursor.fetchone()
        
        if existing_rule1b:
            print(f"   Found existing rule with ID {existing_rule1b[0]}, updating it...")
            update_rule1b_sql = """
            UPDATE rule SET
              description = 'Detects pallets stuck in transitional areas (aisles, crossdocks) for more than 4 hours, indicating workflow bottlenecks or equipment issues.',
              rule_type = 'STAGNANT_PALLETS',
              conditions = '{"time_threshold_hours": 4, "location_types": ["TRANSITIONAL"]}',
              parameters = '{}',
              priority = 'VERY_HIGH',
              is_active = 1
            WHERE name = 'Stuck Pallets in Transit'
            """
            cursor.execute(update_rule1b_sql)
        else:
            print("   Creating new Rule #1B...")
            # Get category_id from Rule #1
            cursor.execute("SELECT category_id FROM rule WHERE id = 1")
            category_result = cursor.fetchone()
            category_id = category_result[0] if category_result else 1
            
            insert_rule1b_sql = """
            INSERT INTO rule (
              name, description, rule_type, conditions, parameters, priority, is_active, category_id
            ) VALUES (
              'Stuck Pallets in Transit',
              'Detects pallets stuck in transitional areas (aisles, crossdocks) for more than 4 hours, indicating workflow bottlenecks or equipment issues.',
              'STAGNANT_PALLETS',
              '{"time_threshold_hours": 4, "location_types": ["TRANSITIONAL"]}',
              '{}',
              'VERY_HIGH',
              1,
              ?
            )
            """
            cursor.execute(insert_rule1b_sql, (category_id,))
        
        print("   Transit rule configured successfully!")
        print()
        
        # Verify the changes
        print("4. Verifying updates:")
        cursor.execute("""
            SELECT id, name, rule_type, conditions, priority, is_active
            FROM rule
            WHERE rule_type = 'STAGNANT_PALLETS'
            ORDER BY id
        """)
        
        stagnant_rules = cursor.fetchall()
        for rule in stagnant_rules:
            print(f"   Rule {rule[0]}: {rule[1]}")
            print(f"     Type: {rule[2]}")
            print(f"     Conditions: {rule[3]}")
            print(f"     Priority: {rule[4]}")
            print(f"     Active: {rule[5]}")
            print()
        
        # Commit changes
        conn.commit()
        print("SUCCESS: All changes committed to database!")
        print()
        
        print("EXPECTED IMPACT:")
        print("  Rule #1 (Forgotten Pallets in Receiving):")
        print("    - Threshold: 10 hours (was 6 hours)")
        print("    - Locations: RECEIVING only (was RECEIVING + TRANSITIONAL)")
        print("    - Priority: HIGH (was VERY_HIGH)")
        print("    - Expected: ~62% reduction in false positives")
        print()
        print("  Rule #1B (Stuck Pallets in Transit):")
        print("    - Threshold: 4 hours (new)")
        print("    - Locations: TRANSITIONAL only")
        print("    - Priority: VERY_HIGH")
        print("    - Expected: Better detection of stuck pallets")
        
        return True
        
    except Exception as e:
        print(f"Error updating rules: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = execute_rule_updates()
    if success:
        print("\nRule updates completed successfully!")
    else:
        print("\nRule updates failed!")