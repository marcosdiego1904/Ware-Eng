"""
Professional Database Migration System
Industry-standard approach with version control and rollback capability
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
from database import db
from models import RuleCategory, Rule, Location
from core_models import User


class Migration:
    """Base migration class"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.timestamp = datetime.utcnow()
    
    def up(self):
        """Apply the migration"""
        raise NotImplementedError("Subclasses must implement up()")
    
    def down(self):
        """Rollback the migration (optional)"""
        pass


class SchemaVersion(db.Model):
    """Track applied migrations"""
    __tablename__ = 'schema_version'
    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)


class MigrationRunner:
    """Handles migration execution and tracking"""
    
    def __init__(self):
        self.migrations = []
        self._register_migrations()
    
    def _register_migrations(self):
        """Register all available migrations"""
        self.migrations = [
            CreateRulesTablesMigration("001", "Create rules system tables"),
            SeedDefaultRulesMigration("002", "Seed default warehouse rules"),
            CreateLocationsMigration("003", "Create basic location mappings"),
        ]
        
        # Sort by version
        self.migrations.sort(key=lambda m: m.version)
    
    def get_current_version(self) -> str:
        """Get the current schema version"""
        try:
            # Ensure schema_version table exists
            db.create_all()
            
            latest = SchemaVersion.query.order_by(SchemaVersion.version.desc()).first()
            return latest.version if latest else "000"
        except:
            return "000"
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get migrations that haven't been applied"""
        current_version = self.get_current_version()
        applied_versions = set()
        
        try:
            applied = SchemaVersion.query.all()
            applied_versions = {v.version for v in applied}
        except:
            pass
        
        pending = []
        for migration in self.migrations:
            if migration.version not in applied_versions:
                pending.append(migration)
        
        return pending
    
    def run_migrations(self, target_version: str = None) -> bool:
        """Run pending migrations up to target version"""
        try:
            pending = self.get_pending_migrations()
            
            if not pending:
                print("No pending migrations.")
                return True
            
            print(f"Found {len(pending)} pending migrations.")
            
            for migration in pending:
                if target_version and migration.version > target_version:
                    break
                
                print(f"Applying migration {migration.version}: {migration.description}")
                
                try:
                    # Run the migration
                    migration.up()
                    
                    # Record as applied
                    version_record = SchemaVersion(
                        version=migration.version,
                        description=migration.description
                    )
                    db.session.add(version_record)
                    db.session.commit()
                    
                    print(f"✓ Migration {migration.version} applied successfully")
                    
                except Exception as e:
                    print(f"✗ Migration {migration.version} failed: {e}")
                    db.session.rollback()
                    return False
            
            return True
            
        except Exception as e:
            print(f"Migration runner error: {e}")
            return False
    
    def check_migrations_needed(self) -> bool:
        """Check if migrations are needed (lightweight check)"""
        try:
            # Quick check - do we have active rules?
            rule_count = Rule.query.filter_by(is_active=True).count()
            return rule_count == 0
        except:
            # If query fails, probably need migrations
            return True


# Specific Migration Classes

class CreateRulesTablesMigration(Migration):
    """Create all rules system tables"""
    
    def up(self):
        # Import here to avoid circular imports
        from models import RuleCategory, Rule, RuleHistory, RuleTemplate, RulePerformance, Location
        
        # Create all tables
        db.create_all()


class SeedDefaultRulesMigration(Migration):
    """Seed default warehouse rules"""
    
    def up(self):
        # Create categories first
        categories = self._create_categories()
        
        # Get/create system user
        system_user = self._get_system_user()
        
        # Create default rules
        self._create_default_rules(categories, system_user)
    
    def _create_categories(self) -> Dict[str, RuleCategory]:
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
        
        categories = {}
        for cat_data in categories_data:
            existing = RuleCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = RuleCategory(**cat_data)
                db.session.add(category)
                db.session.flush()
                categories[cat_data['name']] = category
            else:
                categories[cat_data['name']] = existing
        
        return categories
    
    def _get_system_user(self) -> User:
        system_user = User.query.filter_by(username='system').first()
        if not system_user:
            system_user = User(username='system', password_hash='system_generated')
            db.session.add(system_user)
            db.session.flush()
        return system_user
    
    def _create_default_rules(self, categories: Dict[str, RuleCategory], system_user: User):
        # Default rules data (same as before)
        default_rules = [
            {
                "name": "Forgotten Pallets Alert",
                "rule_type": "STAGNANT_PALLETS",
                "category": "FLOW_TIME",
                "description": "Detects pallets that have been sitting in receiving or transitional areas for too long",
                "conditions": {"location_types": ["RECEIVING", "TRANSITIONAL"], "time_threshold_hours": 6},
                "parameters": {"time_threshold_hours": {"type": "integer", "min": 1, "max": 24, "default": 6}},
                "priority": "VERY_HIGH"
            },
            {
                "name": "Incomplete Lots Alert", 
                "rule_type": "UNCOORDINATED_LOTS",
                "category": "FLOW_TIME",
                "description": "Identifies pallets still in receiving when most of their lot has been stored",
                "conditions": {"completion_threshold": 0.8, "location_types": ["RECEIVING"]},
                "parameters": {"completion_threshold": {"type": "float", "min": 0.5, "max": 1.0, "default": 0.8}},
                "priority": "VERY_HIGH"
            },
            {
                "name": "Overcapacity Alert",
                "rule_type": "OVERCAPACITY",
                "category": "SPACE", 
                "description": "Detects locations that exceed their designated storage capacity",
                "conditions": {"check_all_locations": True},
                "parameters": {},
                "priority": "HIGH"
            },
            {
                "name": "Invalid Locations Alert",
                "rule_type": "INVALID_LOCATION",
                "category": "SPACE",
                "description": "Finds pallets in locations not defined in warehouse rules",
                "conditions": {"check_undefined_locations": True},
                "parameters": {},
                "priority": "HIGH"
            },
            {
                "name": "AISLE Stuck Pallets",
                "rule_type": "LOCATION_SPECIFIC_STAGNANT",
                "category": "FLOW_TIME",
                "description": "Detects pallets stuck in AISLE locations for extended periods",
                "conditions": {"location_pattern": "AISLE*", "time_threshold_hours": 4},
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
                "parameters": {"time_threshold_minutes": {"type": "integer", "min": 5, "max": 120, "default": 30}},
                "priority": "VERY_HIGH"
            },
            {
                "name": "Scanner Error Detection",
                "rule_type": "DATA_INTEGRITY",
                "category": "SPACE",
                "description": "Detects data integrity issues from scanning errors",
                "conditions": {"check_impossible_locations": True, "check_duplicate_scans": True},
                "parameters": {},
                "priority": "MEDIUM"
            },
            {
                "name": "Location Type Mismatches",
                "rule_type": "LOCATION_MAPPING_ERROR",
                "category": "SPACE",
                "description": "Identifies inconsistencies in location type mapping",
                "conditions": {"validate_location_types": True, "check_pattern_consistency": True},
                "parameters": {},
                "priority": "HIGH"
            }
        ]
        
        created_count = 0
        for rule_data in default_rules:
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
        
        print(f"Created {created_count} default rules")


class CreateLocationsMigration(Migration):
    """Create basic location mappings"""
    
    def up(self):
        basic_locations = [
            {'code': 'RECEIVING', 'pattern': 'RECEIVING*', 'location_type': 'RECEIVING', 'capacity': 50, 'zone': 'INBOUND'},
            {'code': 'AISLE-A', 'pattern': 'AISLE-A*', 'location_type': 'TRANSITIONAL', 'capacity': 2, 'zone': 'GENERAL'},
            {'code': 'AISLE-B', 'pattern': 'AISLE-B*', 'location_type': 'TRANSITIONAL', 'capacity': 2, 'zone': 'GENERAL'},
            {'code': 'FINAL', 'pattern': 'FINAL*', 'location_type': 'FINAL', 'capacity': 1, 'zone': 'STORAGE'}
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
        
        print(f"Created {created_count} basic locations")


# Global migration runner instance
migration_runner = MigrationRunner()


def run_migrations_if_needed():
    """Run migrations only if needed (smart check)"""
    if migration_runner.check_migrations_needed():
        print("Running database migrations...")
        return migration_runner.run_migrations()
    else:
        print("Database is up to date.")
        return True


def force_run_migrations():
    """Force run all pending migrations"""
    return migration_runner.run_migrations()