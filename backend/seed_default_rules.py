#!/usr/bin/env python3
"""
Seed Default Rules Script
Seeds the default warehouse rules into the database for immediate use.

This script creates:
1. The Three Pillars categories (FLOW_TIME, SPACE, PRODUCT)
2. The 8 default rules as defined in the system design
3. Basic location mappings for rule evaluation

Run this script to enable analysis functionality with default rules.
"""

import os
import sys
import json
from datetime import datetime

# Add the src directory to the Python path to resolve imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from models import RuleCategory, Rule, Location

def create_default_categories():
    """Create the Three Pillars Framework categories"""
    print("Creating default rule categories...")
    
    categories_data = [
        {
            'name': 'FLOW_TIME',
            'display_name': 'Flow & Time Rules',
            'priority': 1,  # Maximum priority
            'description': 'Rules that detect stagnant pallets, uncoordinated lots, and time-based issues'
        },
        {
            'name': 'SPACE',
            'display_name': 'Space Management Rules',
            'priority': 2,  # High priority
            'description': 'Rules that manage warehouse space, capacity, and location compliance'
        },
        {
            'name': 'PRODUCT',
            'display_name': 'Product Compatibility Rules',
            'priority': 3,  # Medium priority
            'description': 'Rules that ensure products are stored in appropriate locations'
        }
    ]
    
    created_categories = {}
    for cat_data in categories_data:
        existing = RuleCategory.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = RuleCategory(**cat_data)
            db.session.add(category)
            db.session.flush()  # Get the ID
            created_categories[cat_data['name']] = category
            print(f"  + Created category: {cat_data['display_name']}")
        else:
            created_categories[cat_data['name']] = existing
            print(f"  - Category already exists: {cat_data['display_name']}")
    
    db.session.commit()
    return created_categories

def create_default_rules(categories):
    """Create the default rules package"""
    print("\nCreating default rules...")
    
    # Default user ID (assuming user ID 1 exists, or create a system user)
    from core_models import User
    system_user = User.query.first()
    if not system_user:
        system_user = User(username='system', password_hash='system')
        db.session.add(system_user)
        db.session.flush()
    
    default_rules_data = [
        # Core 4 Rules (Original)
        {
            "name": "Forgotten Pallets Alert",
            "rule_type": "STAGNANT_PALLETS",
            "category": "FLOW_TIME",
            "description": "Detects pallets that have been in RECEIVING areas for more than 10 hours, indicating workflow inefficiencies or forgotten items.",
            "conditions": {
                "location_types": ["RECEIVING"],
                "time_threshold_hours": 10
            },
            "parameters": {
                "time_threshold_hours": {"type": "integer", "min": 1, "max": 24, "default": 10}
            },
            "priority": "HIGH"
        },
        {
            "name": "Incomplete Lots Alert", 
            "rule_type": "UNCOORDINATED_LOTS",
            "category": "FLOW_TIME",
            "description": "Identifies pallets still in receiving when most of their lot has been stored",
            "conditions": {
                "completion_threshold": 0.8,
                "location_types": ["RECEIVING"]
            },
            "parameters": {
                "completion_threshold": {"type": "float", "min": 0.5, "max": 1.0, "default": 0.8}
            },
            "priority": "VERY_HIGH"
        },
        {
            "name": "Overcapacity Alert",
            "rule_type": "OVERCAPACITY",
            "category": "SPACE", 
            "description": "Detects locations that exceed their designated storage capacity",
            "conditions": {
                "check_all_locations": True
            },
            "parameters": {},
            "priority": "HIGH"
        },
        {
            "name": "Invalid Locations Alert",
            "rule_type": "INVALID_LOCATION",
            "category": "SPACE",
            "description": "Finds pallets in locations not defined in warehouse rules",
            "conditions": {
                "check_undefined_locations": True
            },
            "parameters": {},
            "priority": "HIGH"
        },
        # Enhanced Rules (From Simulations)
        {
            "name": "AISLE Stuck Pallets",
            "rule_type": "LOCATION_SPECIFIC_STAGNANT",
            "category": "FLOW_TIME",
            "description": "Detects pallets stuck in AISLE locations for extended periods",
            "conditions": {
                "location_pattern": "AISLE*",
                "time_threshold_hours": 4
            },
            "parameters": {
                "location_pattern": {"type": "string", "default": "AISLE*"},
                "time_threshold_hours": {"type": "integer", "min": 1, "max": 12, "default": 4}
            },
            "priority": "HIGH"
        },
        {
            "name": "Cold Chain Violations",
            "rule_type": "TEMPERATURE_ZONE_MISMATCH",
            "category": "PRODUCT",
            "description": "Identifies temperature-sensitive products in inappropriate zones",
            "conditions": {
                "product_patterns": ["*FROZEN*", "*REFRIGERATED*"],
                "prohibited_zones": ["AMBIENT", "GENERAL"],
                "time_threshold_minutes": 30
            },
            "parameters": {
                "time_threshold_minutes": {"type": "integer", "min": 5, "max": 120, "default": 30}
            },
            "priority": "VERY_HIGH"
        },
        {
            "name": "Scanner Error Detection",
            "rule_type": "DATA_INTEGRITY",
            "category": "SPACE",
            "description": "Detects data integrity issues from scanning errors",
            "conditions": {
                "check_impossible_locations": True,
                "check_duplicate_scans": True
            },
            "parameters": {},
            "priority": "MEDIUM"
        },
        {
            "name": "Location Type Mismatches",
            "rule_type": "LOCATION_MAPPING_ERROR",
            "category": "SPACE",
            "description": "Identifies inconsistencies in location type mapping",
            "conditions": {
                "validate_location_types": True,
                "check_pattern_consistency": True
            },
            "parameters": {},
            "priority": "HIGH"
        }
    ]
    
    created_rules = []
    for rule_data in default_rules_data:
        existing = Rule.query.filter_by(name=rule_data['name']).first()
        if not existing:
            rule = Rule(
                name=rule_data['name'],
                description=rule_data['description'],
                category_id=categories[rule_data['category']].id,
                rule_type=rule_data['rule_type'],
                conditions=json.dumps(rule_data['conditions']),
                parameters=json.dumps(rule_data['parameters']),
                priority=rule_data['priority'],
                is_active=True,
                is_default=True,
                created_by=system_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(rule)
            created_rules.append(rule)
            print(f"  + Created rule: {rule_data['name']} ({rule_data['priority']})")
        else:
            print(f"  - Rule already exists: {rule_data['name']}")
    
    db.session.commit()
    return created_rules

def create_basic_locations():
    """Create basic location mappings for rule evaluation"""
    print("\nCreating basic location mappings...")
    
    basic_locations = [
        {
            'code': 'RECEIVING',
            'pattern': 'RECEIVING*',
            'location_type': 'RECEIVING',
            'capacity': 50,
            'zone': 'INBOUND'
        },
        {
            'code': 'AISLE-A',
            'pattern': 'AISLE-A*',
            'location_type': 'TRANSITIONAL',
            'capacity': 2,
            'zone': 'GENERAL'
        },
        {
            'code': 'AISLE-B',
            'pattern': 'AISLE-B*',
            'location_type': 'TRANSITIONAL',
            'capacity': 2,
            'zone': 'GENERAL'
        },
        {
            'code': 'FINAL',
            'pattern': 'FINAL*',
            'location_type': 'FINAL',
            'capacity': 1,
            'zone': 'STORAGE'
        }
    ]
    
    created_locations = []
    for loc_data in basic_locations:
        existing = Location.query.filter_by(code=loc_data['code']).first()
        if not existing:
            location = Location(
                code=loc_data['code'],
                pattern=loc_data['pattern'],
                location_type=loc_data['location_type'],
                capacity=loc_data['capacity'],
                zone=loc_data['zone'],
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(location)
            created_locations.append(location)
            print(f"  + Created location: {loc_data['code']} (capacity: {loc_data['capacity']})")
        else:
            print(f"  - Location already exists: {loc_data['code']}")
    
    db.session.commit()
    return created_locations

def verify_setup():
    """Verify that the setup was successful"""
    print("\nVerifying setup...")
    
    # Count categories
    category_count = RuleCategory.query.count()
    print(f"  Categories: {category_count}")
    
    # Count rules
    rule_count = Rule.query.filter_by(is_active=True).count()
    print(f"  Active rules: {rule_count}")
    
    # Count locations
    location_count = Location.query.filter_by(is_active=True).count()
    print(f"  Active locations: {location_count}")
    
    # Show rules by category
    categories = RuleCategory.query.order_by(RuleCategory.priority).all()
    for category in categories:
        rules = Rule.query.filter_by(category_id=category.id, is_active=True).all()
        print(f"\n  {category.display_name}:")
        for rule in rules:
            status = "DEFAULT" if rule.is_default else "CUSTOM"
            print(f"    - {rule.name} ({rule.priority}) [{status}]")
    
    return category_count > 0 and rule_count > 0

def main():
    """Main seeding function"""
    print("="*60)
    print("WAREHOUSE RULES SYSTEM - DEFAULT RULES SEEDING")
    print("="*60)
    
    with app.app_context():
        try:
            # Check if tables exist
            print("Checking database tables...")
            db.create_all()
            print("  + Database tables ready")
            
            # Create categories
            categories = create_default_categories()
            
            # Create rules
            rules = create_default_rules(categories)
            
            # Create basic locations
            locations = create_basic_locations()
            
            # Verify setup
            if verify_setup():
                print("\n" + "="*60)
                print("SUCCESS: Default rules have been seeded successfully!")
                print("Your analysis system is now ready to use.")
                print("You can now submit reports and get automatic analysis.")
                print("="*60)
            else:
                print("\nERROR: Setup verification failed!")
                
        except Exception as e:
            print(f"\nERROR during seeding: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    main()