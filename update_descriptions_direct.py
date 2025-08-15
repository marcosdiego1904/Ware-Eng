#!/usr/bin/env python3
"""
Update rule descriptions directly using SQLite
"""
import sqlite3
import os

def update_descriptions():
    """Update rule descriptions directly in the database"""
    
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
        
        print("=== UPDATING RULE DESCRIPTIONS ===")
        print()
        
        # Check current descriptions
        print("Current descriptions:")
        cursor.execute("SELECT id, name, description FROM rule WHERE id = 1 OR name = 'Stuck Pallets in Transit'")
        current_rules = cursor.fetchall()
        
        for rule in current_rules:
            print(f"Rule #{rule[0]} - {rule[1]}:")
            print(f"  {rule[2]}")
            print()
        
        # Update Rule #1 description
        rule1_description = "Identifies pallets forgotten in receiving areas for over 10 hours. Normal receiving workflow takes 6-8 hours, so this threshold captures true inefficiencies while reducing alert fatigue from routine operations."
        
        cursor.execute("""
            UPDATE rule SET
                description = ?
            WHERE id = 1
        """, (rule1_description,))
        
        print("Updated Rule #1 description")
        
        # Update Rule #10 description
        rule10_description = "Detects pallets stuck in transitional areas (aisles, crossdocks) for over 4 hours. These locations should have high turnover, so extended stays indicate workflow bottlenecks, equipment failures, or process disruptions requiring immediate attention."
        
        cursor.execute("""
            UPDATE rule SET
                description = ?
            WHERE name = 'Stuck Pallets in Transit'
        """, (rule10_description,))
        
        print("Updated Rule #10 description")
        print()
        
        # Verify the changes
        print("NEW DESCRIPTIONS:")
        cursor.execute("SELECT id, name, description FROM rule WHERE id = 1 OR name = 'Stuck Pallets in Transit'")
        updated_rules = cursor.fetchall()
        
        for rule in updated_rules:
            print(f"Rule #{rule[0]} - {rule[1]}:")
            print(f"  {rule[2]}")
            print()
        
        # Commit changes
        conn.commit()
        print("SUCCESS: Rule descriptions updated!")
        print()
        
        print("BENEFITS OF NEW DESCRIPTIONS:")
        print("- Clearly explain the business reasoning behind thresholds")
        print("- Distinguish between 'forgotten' vs 'stuck' pallet scenarios") 
        print("- Help users understand when each rule should trigger")
        print("- Provide context for different urgency levels (HIGH vs VERY_HIGH)")
        
        return True
        
    except Exception as e:
        print(f"Error updating descriptions: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = update_descriptions()
    if success:
        print("\nRule description updates completed successfully!")
    else:
        print("\nRule description updates failed!")