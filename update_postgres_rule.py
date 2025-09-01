#!/usr/bin/env python3
"""
Update PostgreSQL Production Database to Enable Location Differentiation

This script updates the production PostgreSQL database to enable the enhanced
overcapacity rule with location differentiation.
"""

import json
import os
import sys

# You'll need to install: pip install psycopg2-binary
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

def update_postgres_rule():
    """Update the PostgreSQL rule to enable location differentiation"""
    
    print("Updating PostgreSQL Production Database")
    print("=" * 40)
    
    # Database connection parameters - UPDATE THESE FOR YOUR SYSTEM
    db_params = {
        'host': 'localhost',  # Update with your PostgreSQL host
        'port': 5432,         # Update with your PostgreSQL port  
        'database': 'warehouse_db',  # Update with your database name
        'user': 'your_username',     # Update with your username
        'password': 'your_password'  # Update with your password
    }
    
    print("⚠️  IMPORTANT: Update database connection parameters in this script!")
    print("   Current settings:")
    for key, value in db_params.items():
        if key == 'password':
            print(f"   {key}: {'*' * len(str(value))}")
        else:
            print(f"   {key}: {value}")
    
    print("\\nProceed? (y/N):", end=" ")
    if input().lower() != 'y':
        print("Aborted.")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check current overcapacity rules
        cursor.execute("""
            SELECT id, name, rule_type, is_active, parameters 
            FROM rule 
            WHERE rule_type = 'OVERCAPACITY'
            ORDER BY id
        """)
        
        rules = cursor.fetchall()
        print(f"\\nFound {len(rules)} overcapacity rules:")
        
        for rule in rules:
            status = "Active" if rule['is_active'] else "Inactive"
            print(f"  - {rule['name']} (ID: {rule['id']}): {status}")
            
            if rule['parameters']:
                try:
                    params = json.loads(rule['parameters'])
                    print(f"    Parameters: {params}")
                except:
                    print(f"    Parameters: {rule['parameters']}")
        
        # Find the overcapacity rule to update
        overcapacity_rule = None
        for rule in rules:
            if rule['name'] == 'Overcapacity Alert':
                overcapacity_rule = rule
                break
        
        if not overcapacity_rule:
            print("\\nERROR: Could not find 'Overcapacity Alert' rule")
            return False
        
        rule_id = overcapacity_rule['id']
        
        # Update the rule parameters to enable location differentiation
        current_params = json.loads(overcapacity_rule['parameters']) if overcapacity_rule['parameters'] else {}
        
        # Add location differentiation parameter
        current_params['use_location_differentiation'] = True
        current_params['use_statistical_analysis'] = False
        
        updated_params_json = json.dumps(current_params)
        
        print(f"\\nUpdating rule ID {rule_id} parameters:")
        print(f"  Current: {overcapacity_rule['parameters']}")
        print(f"  Updated: {updated_params_json}")
        
        cursor.execute("""
            UPDATE rule 
            SET parameters = %s, updated_at = NOW()
            WHERE id = %s
        """, (updated_params_json, rule_id))
        
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT parameters FROM rule WHERE id = %s", (rule_id,))
        updated_rule = cursor.fetchone()
        
        print(f"\\n✅ Rule updated successfully!")
        print(f"   New parameters: {updated_rule['parameters']}")
        
        # Verify location differentiation is enabled
        params = json.loads(updated_rule['parameters'])
        if params.get('use_location_differentiation') == True:
            print("   ✅ Location differentiation: ENABLED")
        else:
            print("   ❌ Location differentiation: NOT enabled")
        
        cursor.close()
        conn.close()
        
        print("\\n🎉 PostgreSQL database updated successfully!")
        print("\\nNext steps:")
        print("1. Upload 'large_scale_overcapacity_test.xlsx' to your WMS system")  
        print("2. Run the analysis again")
        print("3. Expected: ~397 alerts (vs 891 from legacy system)")
        print("4. Look for 'Storage Overcapacity' and 'Special Area Capacity' alert types")
        
        return True
        
    except psycopg2.Error as e:
        print(f"\\nPostgreSQL Error: {e}")
        return False
    except Exception as e:
        print(f"\\nError: {e}")
        return False

if __name__ == "__main__":
    print("WARNING: This script requires updating database connection parameters!")
    print("Please edit the script to set your PostgreSQL connection details.")
    print("\\nContinue anyway? (y/N):", end=" ")
    
    if input().lower() == 'y':
        success = update_postgres_rule()
        sys.exit(0 if success else 1)
    else:
        print("Please edit the database parameters and run again.")
        sys.exit(1)