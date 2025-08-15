#!/usr/bin/env python3
"""
Update Rule #1 to implement the new dual-rule architecture
- 10-hour threshold
- RECEIVING locations only
- HIGH priority
"""

import sys
import os
import json

# Add current directory to path for imports
sys.path.insert(0, '.')

from app import app
from models import Rule
from database import db

def update_rule_1():
    """Update Rule #1 with the new dual-rule specifications"""
    
    with app.app_context():
        # Get Rule #1
        rule1 = Rule.query.get(1)
        
        if not rule1:
            print("ERROR: Rule #1 not found!")
            return False
            
        print(f"Current Rule #1:")
        print(f"   Name: {rule1.name}")
        print(f"   Conditions: {rule1.conditions}")
        print(f"   Priority: {rule1.priority}")
        
        # Update conditions to new dual-rule specifications
        new_conditions = {
            "time_threshold_hours": 10,
            "location_types": ["RECEIVING"]
        }
        
        # Update the rule
        rule1.conditions = json.dumps(new_conditions)
        rule1.priority = "HIGH"
        rule1.name = "Forgotten Pallets in Receiving"
        rule1.description = "Detects pallets that have been in RECEIVING areas for more than 10 hours, indicating workflow inefficiencies or forgotten items."
        
        # Save changes
        try:
            db.session.commit()
            print(f"SUCCESS: Rule #1 updated!")
            print(f"   New conditions: {rule1.conditions}")
            print(f"   New priority: {rule1.priority}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to update rule: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("Updating Rule #1 for dual STAGNANT_PALLETS implementation...")
    success = update_rule_1()
    
    if success:
        print("\nRule #1 update completed!")
        print("   - 10-hour threshold for RECEIVING areas")
        print("   - Reduces false positives from normal processing") 
        print("   - Ready for testing with next analysis")
    else:
        print("\nRule update failed!")