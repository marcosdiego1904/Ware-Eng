"""
Automatic Database Migration System
Ensures database is properly initialized on every startup

This module automatically:
1. Creates all tables if they don't exist
2. Seeds default rules if the rules table is empty
3. Updates schema if needed
4. Handles both development and production environments
"""

import os
import json
from datetime import datetime
from flask import current_app
from database import db
from models import RuleCategory, Rule, Location
from core_models import User


class AutoMigrator:
    """Handles automatic database migrations and seeding"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the auto migrator with the Flask app"""
        self.app = app
        
        # Run migrations after app context is ready
        with app.app_context():
            try:
                self.ensure_database_ready()
            except Exception as e:
                print(f"Auto-migration failed: {e}")
                # Don't crash the app, just log the error
    
    def ensure_database_ready(self):
        """Main function that ensures database is ready for use"""
        print("Checking database initialization...")
        
        # Step 1: Create all tables
        self.create_tables()
        
        # Step 2: Check if rules exist, if not seed them
        self.ensure_rules_exist()
        
        # Step 3: Ensure basic locations exist
        self.ensure_locations_exist()
        
        print("Database initialization complete.")
    
    def create_tables(self):
        """Create all database tables"""
        try:
            db.create_all()
            print("+ Database tables verified/created")
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise
    
    def ensure_rules_exist(self):
        """Ensure default rules exist in the database"""
        try:
            # Check if rules table has any active rules
            rule_count = Rule.query.filter_by(is_active=True).count()
            
            if rule_count == 0:
                print("No active rules found. Seeding default rules...")
                self._seed_default_rules()
            else:
                print(f"+ Found {rule_count} active rules in database")
        except Exception as e:
            print(f"Error checking rules: {e}")
            # If there's an error (like table doesn't exist), try to create and seed
            try:
                self.create_tables()
                self._seed_default_rules()
            except Exception as seed_error:
                print(f"Failed to seed rules: {seed_error}")
                raise
    
    def ensure_locations_exist(self):
        """Ensure basic locations exist"""
        try:
            location_count = Location.query.filter_by(is_active=True).count()
            
            if location_count == 0:
                print("No locations found. Creating basic locations...")
                self._create_basic_locations()
            else:
                print(f"+ Found {location_count} locations in database")
        except Exception as e:
            print(f"Error with locations: {e}")
            try:
                self._create_basic_locations()
            except Exception as loc_error:
                print(f"Failed to create locations: {loc_error}")
    
    def _seed_default_rules(self):
        """Seed the default rules into the database"""
        # Create categories first
        categories = self._create_default_categories()
        
        # Get system user (create if doesn't exist)
        system_user = self._get_or_create_system_user()
        
        # Default rules data
        default_rules_data = [
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
                "parameters": {
                    "use_location_differentiation": False,
                    "use_statistical_analysis": False
                },
                "priority": "HIGH"
            },
            {
                "name": "Enhanced Overcapacity with Location Differentiation",
                "rule_type": "OVERCAPACITY", 
                "category": "SPACE",
                "description": "Business-context-aware overcapacity detection with differentiated alerting for Storage (critical) vs Special areas (operational)",
                "conditions": {
                    "check_all_locations": True
                },
                "parameters": {
                    "use_location_differentiation": True,
                    "use_statistical_analysis": False
                },
                "priority": "HIGH",
                "is_active": False
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
        
        # Create rules
        created_count = 0
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
                created_count += 1
        
        db.session.commit()
        print(f"+ Created {created_count} default rules")
    
    def _create_default_categories(self):
        """Create the Three Pillars Framework categories"""
        categories_data = [
            {
                'name': 'FLOW_TIME',
                'display_name': 'Flow & Time Rules',
                'priority': 1,
                'description': 'Rules that detect stagnant pallets, uncoordinated lots, and time-based issues'
            },
            {
                'name': 'SPACE',
                'display_name': 'Space Management Rules',
                'priority': 2,
                'description': 'Rules that manage warehouse space, capacity, and location compliance'
            },
            {
                'name': 'PRODUCT',
                'display_name': 'Product Compatibility Rules',
                'priority': 3,
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
            else:
                created_categories[cat_data['name']] = existing
        
        db.session.commit()
        return created_categories
    
    def _get_or_create_system_user(self):
        """Get or create a system user for default rules"""
        system_user = User.query.filter_by(username='system').first()
        if not system_user:
            system_user = User(username='system', password_hash='system_generated')
            db.session.add(system_user)
            db.session.flush()
        return system_user
    
    def _create_basic_locations(self):
        """Create basic location mappings"""
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
        
        created_count = 0
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
                created_count += 1
        
        db.session.commit()
        print(f"+ Created {created_count} basic locations")


# Create global instance
auto_migrator = AutoMigrator()


def init_auto_migration(app):
    """Initialize auto migration with the Flask app"""
    auto_migrator.init_app(app)
    return auto_migrator