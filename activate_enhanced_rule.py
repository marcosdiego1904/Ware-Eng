#!/usr/bin/env python3
"""
Activate Enhanced Overcapacity Rule with Location Differentiation

This script will:
1. Disable the legacy "Overcapacity Alert" rule
2. Enable the "Enhanced Overcapacity with Location Differentiation" rule
3. Verify the changes were applied correctly
"""

import sys
import os
import sqlite3
import json

# Add the backend source directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def get_database_path():
    """Find the database file"""
    # Use the correct database file
    db_path = 'backend/instance/database.db'
    full_path = os.path.join(os.path.dirname(__file__), db_path)
    if os.path.exists(full_path):
        return full_path
    
    return None

def activate_enhanced_rule():
    """Activate the enhanced overcapacity rule and disable the legacy one"""
    
    print("Activating Enhanced Overcapacity Rule with Location Differentiation")
    print("=" * 65)
    
    # Find database
    db_path = get_database_path()
    if not db_path:
        print("ERROR: Could not find database file")
        print("   Please ensure you're running this from the project root directory")
        return False
    
    print(f"Found database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current rule status
        print("\\nCurrent rule status:")
        cursor.execute("""
            SELECT id, name, rule_type, is_active, parameters 
            FROM rule 
            WHERE rule_type = 'OVERCAPACITY' 
            ORDER BY id
        """)
        
        rules = cursor.fetchall()
        if not rules:
            print("ERROR: No overcapacity rules found in database")
            return False
        
        legacy_rule_id = None
        enhanced_rule_id = None
        
        for rule_id, name, rule_type, is_active, parameters in rules:
            print(f"  - {name} (ID: {rule_id}): {'Active' if is_active else 'Inactive'}")
            
            if "Enhanced" in name and "Location Differentiation" in name:
                enhanced_rule_id = rule_id
            elif name == "Overcapacity Alert":
                legacy_rule_id = rule_id
        
        if not enhanced_rule_id:
            print("ERROR: Enhanced Overcapacity rule not found")
            print("   Please run the migration script first")
            return False
        
        if not legacy_rule_id:
            print("ERROR: Legacy Overcapacity Alert rule not found") 
            return False
        
        print(f"\\nMaking changes:")
        
        # Disable legacy rule
        cursor.execute("UPDATE rule SET is_active = 0 WHERE id = ?", (legacy_rule_id,))
        print(f"  + Disabled legacy 'Overcapacity Alert' (ID: {legacy_rule_id})")
        
        # Enable enhanced rule  
        cursor.execute("UPDATE rule SET is_active = 1 WHERE id = ?", (enhanced_rule_id,))
        print(f"  + Enabled 'Enhanced Overcapacity with Location Differentiation' (ID: {enhanced_rule_id})")
        
        # Verify the enhanced rule has correct parameters
        cursor.execute("SELECT parameters FROM rule WHERE id = ?", (enhanced_rule_id,))
        result = cursor.fetchone()
        if result:
            try:
                params = json.loads(result[0]) if result[0] else {}
                if params.get('use_location_differentiation') != True:
                    # Update parameters to ensure location differentiation is enabled
                    updated_params = {
                        "use_location_differentiation": True,
                        "use_statistical_analysis": False
                    }
                    cursor.execute("UPDATE rule SET parameters = ? WHERE id = ?", 
                                 (json.dumps(updated_params), enhanced_rule_id))
                    print(f"  + Updated parameters to enable location differentiation")
                else:
                    print(f"  + Parameters already correctly configured")
            except json.JSONDecodeError:
                print("  WARNING: Could not parse rule parameters")
        
        # Commit changes
        conn.commit()
        
        # Verify final status
        print("\\nFinal rule status:")
        cursor.execute("""
            SELECT id, name, rule_type, is_active, parameters 
            FROM rule 
            WHERE rule_type = 'OVERCAPACITY' 
            ORDER BY id
        """)
        
        for rule_id, name, rule_type, is_active, parameters in cursor.fetchall():
            status = "Active" if is_active else "Inactive"
            print(f"  - {name} (ID: {rule_id}): {status}")
            
            if is_active and "Enhanced" in name:
                try:
                    params = json.loads(parameters) if parameters else {}
                    differentiation = params.get('use_location_differentiation', False)
                    print(f"    Location differentiation: {'Enabled' if differentiation else 'Disabled'}")
                except:
                    pass
        
        conn.close()
        
        print("\\nConfiguration updated successfully!")
        print("\\nNext steps:")
        print("1. Upload 'large_scale_overcapacity_test.xlsx' to your WMS system")
        print("2. Run the analysis again")
        print("3. Expect ~397 alerts (vs 891 from legacy system)")
        print("4. Look for differentiated alert types and priorities")
        
        return True
        
    except sqlite3.Error as e:
        print(f"ERROR: Database error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = activate_enhanced_rule()
    sys.exit(0 if success else 1)