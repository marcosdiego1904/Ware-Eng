#!/usr/bin/env python3
"""
Update Rule #1 thresholds using Flask application context
"""
import sys
import json
sys.path.append('src')

from app import app
from database import db
from models import Rule, RuleCategory
from core_models import User

def update_rule_thresholds():
    """Update Rule #1 and create Rule #1B using Flask context"""
    
    with app.app_context():
        print("=== UPDATING RULE THRESHOLDS (Option 2) ===")
        print()
        
        # Find Rule #1
        rule1 = Rule.query.filter_by(id=1).first()
        if not rule1:
            print("ERROR: Rule #1 not found!")
            return False
        
        print("Current Rule #1:")
        print(f"   Name: {rule1.name}")
        print(f"   Type: {rule1.rule_type}")
        print(f"   Conditions: {rule1.conditions}")
        print(f"   Priority: {rule1.priority}")
        print()
        
        # Update Rule #1 for RECEIVING with 10-hour threshold
        print("Updating Rule #1 for RECEIVING locations...")
        rule1.name = "Forgotten Pallets in Receiving"
        rule1.description = "Detects pallets that have been in receiving areas for more than 10 hours, indicating they may have been forgotten during normal processing workflow."
        rule1.conditions = json.dumps({
            "time_threshold_hours": 10,
            "location_types": ["RECEIVING"]
        })
        rule1.priority = "HIGH"  # Reduced from VERY_HIGH
        
        print(f"   UPDATED: {rule1.name}")
        print(f"   New threshold: 10 hours")
        print(f"   Locations: RECEIVING only")
        print(f"   Priority: HIGH")
        print()
        
        # Check if Rule #1B already exists
        rule1b = Rule.query.filter_by(name="Stuck Pallets in Transit").first()
        
        if rule1b:
            print("Updating existing Rule #1B...")
        else:
            print("Creating new Rule #1B for TRANSITIONAL locations...")
            rule1b = Rule()
            db.session.add(rule1b)
        
        # Configure Rule #1B
        rule1b.name = "Stuck Pallets in Transit"
        rule1b.description = "Detects pallets stuck in transitional areas (aisles, crossdocks) for more than 4 hours, indicating workflow bottlenecks or equipment issues."
        rule1b.rule_type = "STAGNANT_PALLETS"
        rule1b.conditions = json.dumps({
            "time_threshold_hours": 4,
            "location_types": ["TRANSITIONAL"]
        })
        rule1b.parameters = "{}"
        rule1b.priority = "VERY_HIGH"
        rule1b.is_active = True
        rule1b.category_id = rule1.category_id  # Same category as Rule #1
        rule1b.created_by = rule1.created_by  # Use same creator as Rule #1
        rule1b.is_default = True  # Mark as default rule
        
        print(f"   CONFIGURED: {rule1b.name}")
        print(f"   New threshold: 4 hours")
        print(f"   Locations: TRANSITIONAL only")
        print(f"   Priority: VERY_HIGH")
        print()
        
        try:
            # Commit changes
            db.session.commit()
            print("Changes saved successfully!")
            print()
            
            # Verify the changes
            print("VERIFICATION:")
            all_stagnant_rules = Rule.query.filter_by(rule_type='STAGNANT_PALLETS').all()
            for rule in all_stagnant_rules:
                print(f"   Rule {rule.id}: {rule.name}")
                print(f"     Conditions: {rule.conditions}")
                print(f"     Priority: {rule.priority}")
                print(f"     Active: {rule.is_active}")
                print()
            
            print("IMPLEMENTATION COMPLETE!")
            print()
            print("Expected Impact:")
            print("   - RECEIVING: ~62% reduction in false positives")
            print("   - TRANSITIONAL: Better detection of stuck pallets")
            print("   - Overall: More actionable alerts, less noise")
            print()
            print("Business Benefits:")
            print("   - Normal 6-8h receiving process no longer flagged")
            print("   - Stuck aisle pallets caught within 4 hours")
            print("   - Reduced alert fatigue for warehouse staff")
            
            return True
            
        except Exception as e:
            print(f"ERROR saving changes: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = update_rule_thresholds()
    if success:
        print("\nRule threshold updates completed successfully!")
    else:
        print("\nRule updates failed!")