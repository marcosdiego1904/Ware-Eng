#!/usr/bin/env python3
"""
Update rule descriptions for clearer distinction between dual STAGNANT_PALLETS rules
"""
import sys
import json
sys.path.append('backend/src')

from backend.src.app import app
from backend.src.database import db
from backend.src.models import Rule

def update_descriptions():
    """Update rule descriptions with clearer distinction"""
    
    with app.app_context():
        print("=== UPDATING RULE DESCRIPTIONS ===")
        print()
        
        # Find Rule #1 and Rule #10
        rule1 = Rule.query.filter_by(id=1).first()
        rule10 = Rule.query.filter_by(name="Stuck Pallets in Transit").first()
        
        if not rule1:
            print("ERROR: Rule #1 not found!")
            return False
        
        if not rule10:
            print("ERROR: Rule #10 (Stuck Pallets in Transit) not found!")
            return False
        
        print("Current descriptions:")
        print(f"Rule #{rule1.id}: {rule1.description}")
        print(f"Rule #{rule10.id}: {rule10.description}")
        print()
        
        # Update Rule #1 description
        rule1.description = "Identifies pallets forgotten in receiving areas for over 10 hours. Normal receiving workflow takes 6-8 hours, so this threshold captures true inefficiencies while reducing alert fatigue from routine operations."
        
        # Update Rule #10 description  
        rule10.description = "Detects pallets stuck in transitional areas (aisles, crossdocks) for over 4 hours. These locations should have high turnover, so extended stays indicate workflow bottlenecks, equipment failures, or process disruptions requiring immediate attention."
        
        print("NEW DESCRIPTIONS:")
        print(f"Rule #{rule1.id} - {rule1.name}:")
        print(f"  {rule1.description}")
        print()
        print(f"Rule #{rule10.id} - {rule10.name}:")
        print(f"  {rule10.description}")
        print()
        
        try:
            db.session.commit()
            print("SUCCESS: Rule descriptions updated!")
            print()
            
            print("BENEFITS OF NEW DESCRIPTIONS:")
            print("- Clearly explain the business reasoning behind thresholds")
            print("- Distinguish between 'forgotten' vs 'stuck' pallet scenarios")
            print("- Help users understand when each rule should trigger")
            print("- Provide context for different urgency levels (HIGH vs VERY_HIGH)")
            
            return True
            
        except Exception as e:
            print(f"ERROR saving changes: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = update_descriptions()
    if success:
        print("\nRule description updates completed successfully!")
    else:
        print("\nRule description updates failed!")