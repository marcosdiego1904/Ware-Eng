#!/usr/bin/env python3
"""
Create Enhanced Overcapacity Rule with Location Differentiation

This script will:
1. Create the "Enhanced Overcapacity with Location Differentiation" rule
2. Disable the legacy "Overcapacity Alert" rule  
3. Configure the enhanced rule with correct parameters
"""

import sqlite3
import json
import os
from datetime import datetime

def create_enhanced_rule():
    """Create the enhanced overcapacity rule"""
    
    print("Creating Enhanced Overcapacity Rule with Location Differentiation")
    print("=" * 70)
    
    db_path = os.path.join(os.path.dirname(__file__), 'backend/instance/database.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current status
        cursor.execute("SELECT id, name, is_active FROM rule WHERE rule_type = 'OVERCAPACITY'")
        existing_rules = cursor.fetchall()
        
        print("Current overcapacity rules:")
        for rule_id, name, is_active in existing_rules:
            status = "Active" if is_active else "Inactive"
            print(f"  - {name} (ID: {rule_id}): {status}")
        
        # Check if enhanced rule already exists
        cursor.execute("SELECT id FROM rule WHERE name LIKE '%Enhanced%Location%Differentiation%'")
        enhanced_exists = cursor.fetchone()
        
        if enhanced_exists:
            enhanced_rule_id = enhanced_exists[0]
            print(f"\\nEnhanced rule already exists (ID: {enhanced_rule_id})")
        else:
            # Create the enhanced rule
            enhanced_rule_data = {
                'name': 'Enhanced Overcapacity with Location Differentiation',
                'description': 'Business-context-aware overcapacity detection with differentiated alerting for Storage (critical) vs Special areas (operational)',
                'category_id': 2,  # SPACE category
                'rule_type': 'OVERCAPACITY',
                'conditions': json.dumps({
                    "check_all_locations": True
                }),
                'parameters': json.dumps({
                    "use_location_differentiation": True,
                    "use_statistical_analysis": False
                }),
                'priority': 'HIGH',
                'is_active': False,  # Start inactive
                'is_default': False,
                'created_by': 1,  # Default user
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'modified_from_default': False
            }
            
            cursor.execute("""
                INSERT INTO rule (name, description, category_id, rule_type, conditions, 
                                parameters, priority, is_active, is_default, created_by, 
                                created_at, updated_at, modified_from_default)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                enhanced_rule_data['name'],
                enhanced_rule_data['description'],
                enhanced_rule_data['category_id'],
                enhanced_rule_data['rule_type'],
                enhanced_rule_data['conditions'],
                enhanced_rule_data['parameters'],
                enhanced_rule_data['priority'],
                enhanced_rule_data['is_active'],
                enhanced_rule_data['is_default'],
                enhanced_rule_data['created_by'],
                enhanced_rule_data['created_at'],
                enhanced_rule_data['updated_at'],
                enhanced_rule_data['modified_from_default']
            ))
            
            enhanced_rule_id = cursor.lastrowid
            print(f"\\nCreated enhanced rule (ID: {enhanced_rule_id})")
        
        # Now activate enhanced and deactivate legacy
        print("\\nMaking configuration changes:")
        
        # Disable legacy rule
        cursor.execute("UPDATE rule SET is_active = 0 WHERE name = 'Overcapacity Alert'")
        print("  + Disabled legacy 'Overcapacity Alert' rule")
        
        # Enable enhanced rule
        cursor.execute("UPDATE rule SET is_active = 1 WHERE id = ?", (enhanced_rule_id,))
        print("  + Enabled 'Enhanced Overcapacity with Location Differentiation' rule")
        
        # Commit changes
        conn.commit()
        
        # Verify final status
        print("\\nFinal rule status:")
        cursor.execute("SELECT id, name, is_active, parameters FROM rule WHERE rule_type = 'OVERCAPACITY' ORDER BY id")
        
        for rule_id, name, is_active, parameters in cursor.fetchall():
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
        
        print("\\nConfiguration completed successfully!")
        print("\\nNext steps:")
        print("1. Upload 'large_scale_overcapacity_test.xlsx' to your WMS system")
        print("2. Run the analysis again")
        print("3. Expected results:")
        print("   - Legacy system: 891 alerts")
        print("   - Enhanced system: ~397 alerts (55% reduction)")
        print("   - Look for 'Storage Overcapacity' and 'Special Area Capacity' alert types")
        print("   - Notice different priorities: 'Very High' vs 'High'")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = create_enhanced_rule()
    exit(0 if success else 1)