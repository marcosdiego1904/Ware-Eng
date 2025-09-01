#!/usr/bin/env python3
"""
Check current rules in the database
"""

import sqlite3
import json
import os

def check_rules():
    """Check current rules in database"""
    
    print("Current Rules in Database")
    print("=" * 35)
    
    db_path = os.path.join(os.path.dirname(__file__), 'backend/instance/database.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all overcapacity rules
        cursor.execute("""
            SELECT id, name, rule_type, is_active, parameters, conditions
            FROM rule 
            WHERE rule_type = 'OVERCAPACITY'
            ORDER BY id
        """)
        
        rules = cursor.fetchall()
        
        print(f"Found {len(rules)} overcapacity rules:")
        
        for rule_id, name, rule_type, is_active, parameters, conditions in rules:
            status = "ACTIVE" if is_active else "INACTIVE"
            print(f"\\n  Rule ID {rule_id}: {name}")
            print(f"    Status: {status}")
            print(f"    Type: {rule_type}")
            
            if parameters:
                try:
                    params = json.loads(parameters)
                    print(f"    Parameters: {params}")
                except:
                    print(f"    Parameters: {parameters}")
            
            if conditions:
                try:
                    conds = json.loads(conditions)
                    print(f"    Conditions: {conds}")
                except:
                    print(f"    Conditions: {conditions}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_rules()