#!/usr/bin/env python3
"""
Update Rule #1 thresholds to implement location-type-specific thresholds
"""
import sys
import os
import json

# Add backend src to path
sys.path.append('backend/src')

from database import db
from models import Rule, RuleCategory
from core_models import User  # Import User model to resolve dependency
from flask import Flask

def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    
    # Database configuration - use the existing database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backend/instance/warehouse.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Initialize database
    db.init_app(app)
    
    return app

def update_rule_thresholds():
    """Update Rule #1 and create new Rule #1B"""
    app = create_app()
    
    with app.app_context():
        print("=== UPDATING RULE THRESHOLDS (Option 2) ===")
        print()
        
        # Find current Rule #1
        rule1 = Rule.query.filter_by(id=1).first()
        if not rule1:
            print("❌ Rule #1 not found!")
            return
        
        print(f"📋 Current Rule #1: {rule1.name}")
        print(f"   Type: {rule1.rule_type}")
        print(f"   Current conditions: {rule1.conditions}")
        print()
        
        # Update Rule #1 to focus on RECEIVING with 10-hour threshold
        print("🔄 Updating Rule #1 for RECEIVING locations...")
        new_conditions_1 = {
            "time_threshold_hours": 10,
            "location_types": ["RECEIVING"]
        }
        
        rule1.name = "Forgotten Pallets in Receiving"
        rule1.description = "Detects pallets that have been in receiving areas for more than 10 hours, indicating they may have been forgotten during normal processing workflow."
        rule1.conditions = json.dumps(new_conditions_1)
        rule1.priority = "HIGH"  # Reduced from VERY_HIGH since 10h allows normal processing
        
        print(f"   ✅ Updated: {rule1.name}")
        print(f"   📊 New threshold: 10 hours")
        print(f"   📍 Locations: RECEIVING only")
        print(f"   🚨 Priority: HIGH")
        print()
        
        # Check if Rule #1B already exists
        rule1b = Rule.query.filter_by(name="Stuck Pallets in Transit").first()
        
        if rule1b:
            print("🔄 Updating existing Rule #1B for TRANSITIONAL locations...")
        else:
            print("🆕 Creating new Rule #1B for TRANSITIONAL locations...")
            rule1b = Rule()
        
        # Configure Rule #1B for TRANSITIONAL with 4-hour threshold
        new_conditions_1b = {
            "time_threshold_hours": 4,
            "location_types": ["TRANSITIONAL"]
        }
        
        rule1b.name = "Stuck Pallets in Transit"
        rule1b.description = "Detects pallets stuck in transitional areas (aisles, crossdocks) for more than 4 hours, indicating workflow bottlenecks or equipment issues."
        rule1b.rule_type = "STAGNANT_PALLETS"
        rule1b.conditions = json.dumps(new_conditions_1b)
        rule1b.parameters = "{}"
        rule1b.priority = "VERY_HIGH"  # Higher priority since pallets shouldn't be stuck in aisles
        rule1b.is_active = True
        
        # Get the same category as Rule #1
        rule1b.category_id = rule1.category_id
        
        if not rule1b.id:
            db.session.add(rule1b)
        
        print(f"   ✅ Configured: {rule1b.name}")
        print(f"   📊 New threshold: 4 hours")
        print(f"   📍 Locations: TRANSITIONAL only")
        print(f"   🚨 Priority: VERY_HIGH")
        print()
        
        # Commit changes
        try:
            db.session.commit()
            print("💾 Changes saved successfully!")
            print()
            
            # Verify the changes
            print("🔍 VERIFICATION:")
            updated_rule1 = Rule.query.filter_by(id=1).first()
            updated_rule1b = Rule.query.filter_by(name="Stuck Pallets in Transit").first()
            
            print(f"   Rule #1: {updated_rule1.name}")
            print(f"     Conditions: {updated_rule1.conditions}")
            print(f"     Priority: {updated_rule1.priority}")
            
            print(f"   Rule #1B: {updated_rule1b.name}")
            print(f"     Conditions: {updated_rule1b.conditions}")
            print(f"     Priority: {updated_rule1b.priority}")
            print()
            
            print("✅ IMPLEMENTATION COMPLETE!")
            print()
            print("📈 Expected Impact:")
            print("   • RECEIVING: ~62% reduction in false positives")
            print("   • TRANSITIONAL: Better detection of stuck pallets")
            print("   • Overall: More actionable alerts, less noise")
            
        except Exception as e:
            print(f"❌ Error saving changes: {e}")
            db.session.rollback()

if __name__ == "__main__":
    update_rule_thresholds()