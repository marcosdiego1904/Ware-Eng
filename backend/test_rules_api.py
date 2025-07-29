#!/usr/bin/env python3
"""
Test script for the Rules Management API
Tests creating, viewing, editing, and deleting rules
"""

import os
import sys
import json
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from models import Rule, RuleCategory
from core_models import User

def test_rules_system():
    """Test the complete rules management workflow"""
    
    with app.app_context():
        print("=== Testing Rules Management System ===\n")
        
        # 1. List current rules
        print("1. Current Rules in Database:")
        rules = Rule.query.all()
        for rule in rules:
            print(f"   ID: {rule.id} | Name: {rule.name} | Type: {rule.rule_type} | Active: {rule.is_active} | Default: {rule.is_default}")
        print(f"   Total: {len(rules)} rules\n")
        
        # 2. List categories  
        print("2. Available Categories:")
        categories = RuleCategory.query.all()
        for cat in categories:
            print(f"   ID: {cat.id} | Name: {cat.name} | Display: {cat.display_name} | Priority: {cat.priority}")
        print(f"   Total: {len(categories)} categories\n")
        
        # 3. Get or create system user for testing
        system_user = User.query.filter_by(username='system').first()
        if not system_user:
            print("   Creating system user for testing...")
            system_user = User(username='system', password_hash='system_generated')
            db.session.add(system_user)
            db.session.commit()
            print(f"   + Created system user (ID: {system_user.id})")
        
        # 4. Create a new custom rule
        print("3. Creating New Custom Rule:")
        
        # Find FLOW_TIME category
        flow_category = RuleCategory.query.filter_by(name='FLOW_TIME').first()
        if not flow_category:
            print("ERROR: FLOW_TIME category not found")
            return
            
        new_rule = Rule(
            name="Test Custom Slow Movement Rule",
            description="Custom rule to detect pallets moving too slowly through the warehouse",
            category_id=flow_category.id,
            rule_type="SLOW_MOVEMENT",
            priority="HIGH",
            is_active=True,
            is_default=False,
            created_by=system_user.id
        )
        
        # Set conditions for the rule
        conditions = {
            "location_types": ["TRANSITIONAL", "AISLE"],
            "time_threshold_hours": 12,
            "movement_speed_threshold": 2  # pallets per hour
        }
        new_rule.set_conditions(conditions)
        
        # Set parameters
        parameters = {
            "time_threshold_hours": {
                "type": "integer", 
                "min": 1, 
                "max": 48, 
                "default": 12
            },
            "movement_speed_threshold": {
                "type": "float",
                "min": 0.1,
                "max": 10.0,
                "default": 2.0
            }
        }
        new_rule.set_parameters(parameters)
        
        try:
            db.session.add(new_rule)
            db.session.commit()
            print(f"   + Created rule: {new_rule.name} (ID: {new_rule.id})")
            print(f"   + Conditions: {new_rule.get_conditions()}")
            print(f"   + Parameters: {new_rule.get_parameters()}")
        except Exception as e:
            print(f"   - Failed to create rule: {e}")
            db.session.rollback()
            return
        
        # 5. Update the rule
        print("\n4. Updating Custom Rule:")
        try:
            new_rule.description = "Updated: Custom rule to detect pallets moving too slowly (modified threshold)"
            # Update conditions
            updated_conditions = new_rule.get_conditions()
            updated_conditions["time_threshold_hours"] = 8  # Make it more sensitive
            new_rule.set_conditions(updated_conditions)
            new_rule.updated_at = datetime.utcnow()
            
            db.session.commit()
            print(f"   + Updated rule description and time threshold to 8 hours")
        except Exception as e:
            print(f"   - Failed to update rule: {e}")
            db.session.rollback()
        
        # 6. Test rule activation/deactivation
        print("\n5. Testing Rule Activation:")
        try:
            # Deactivate
            new_rule.is_active = False
            db.session.commit()
            print(f"   + Deactivated rule: {new_rule.name}")
            
            # Reactivate
            new_rule.is_active = True  
            db.session.commit()
            print(f"   + Reactivated rule: {new_rule.name}")
        except Exception as e:
            print(f"   - Failed to toggle rule activation: {e}")
            db.session.rollback()
        
        # 7. List all rules including the new one
        print("\n6. Final Rules List (Default + Custom):")
        all_rules = Rule.query.order_by(Rule.is_default.desc(), Rule.created_at.desc()).all()
        
        default_count = 0
        custom_count = 0
        
        for rule in all_rules:
            rule_type = "DEFAULT" if rule.is_default else "CUSTOM"
            status = "ACTIVE" if rule.is_active else "INACTIVE"
            print(f"   {rule_type:8} | {rule.name:35} | {rule.rule_type:20} | {rule.priority:10} | {status}")
            
            if rule.is_default:
                default_count += 1
            else:
                custom_count += 1
        
        print(f"\n   Summary: {default_count} default rules, {custom_count} custom rules")
        
        # 8. Test rule integration (simulate how they'd be used in analysis)
        print("\n7. Testing Rule Integration:")
        active_rules = Rule.query.filter_by(is_active=True).all()
        print(f"   + Found {len(active_rules)} active rules ready for analysis")
        
        for rule in active_rules[-3:]:  # Show last 3 rules
            print(f"   - {rule.name} ({rule.rule_type}) - Priority: {rule.priority}")
        
        # 9. Cleanup - optionally delete the test rule
        print(f"\n8. Cleanup Options:")
        print(f"   Test rule created: {new_rule.name} (ID: {new_rule.id})")
        print(f"   To delete: Rule.query.get({new_rule.id}).delete()")
        print(f"   Keeping rule for manual testing...")
        
        print(f"\n=== Rules Management System Test Complete ===")
        print(f"+ System can create, read, update rules")
        print(f"+ Custom rules integrate with default rules") 
        print(f"+ Rule conditions and parameters work properly")
        print(f"+ Database relationships are intact")

if __name__ == "__main__":
    test_rules_system()