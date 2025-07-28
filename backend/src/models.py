"""
Enhanced Database Models for Warehouse Rules System
Implementation Plan Phase 1: Database Foundation

This module extends the existing models with the new rule management system
as outlined in the Warehouse Rules Implementation Plan.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Import the shared database instance
from database import db

# ==== EXISTING MODELS (Reference from app.py) ====
# These models already exist in app.py - keeping here for reference
# class User(db.Model, UserMixin):
# class AnalysisReport(db.Model):
# class Anomaly(db.Model):
# class AnomalyHistory(db.Model):

# ==== NEW MODELS FOR RULES SYSTEM ====

class RuleCategory(db.Model):
    """
    Three Pillars Framework Categories: FLOW_TIME, SPACE, PRODUCT
    """
    __tablename__ = 'rule_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # FLOW_TIME, SPACE, PRODUCT
    display_name = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.Integer, nullable=False)  # 1=highest
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    rules = db.relationship('Rule', backref='category', lazy=True, cascade="all, delete-orphan")
    templates = db.relationship('RuleTemplate', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'priority': self.priority,
            'description': self.description,
            'is_active': self.is_active,
            'rule_count': len(self.rules)
        }

class Rule(db.Model):
    """
    Dynamic warehouse rules that replace the static Excel-based system
    """
    __tablename__ = 'rule'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('rule_category.id'), nullable=False)
    rule_type = db.Column(db.String(50), nullable=False)  # STAGNANT_PALLETS, OVERCAPACITY, etc.
    conditions = db.Column(db.Text, nullable=False)  # JSON string for rule conditions
    parameters = db.Column(db.Text)  # JSON string for configurable parameters
    priority = db.Column(db.String(20), default='MEDIUM')  # VERY_HIGH, HIGH, MEDIUM, LOW
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)  # System default rules
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    history = db.relationship('RuleHistory', backref='rule', lazy=True, cascade="all, delete-orphan")
    performance_records = db.relationship('RulePerformance', backref='rule', lazy=True, cascade="all, delete-orphan")
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def get_conditions(self):
        """Parse conditions JSON string into dict"""
        try:
            return json.loads(self.conditions) if self.conditions else {}
        except json.JSONDecodeError:
            return {}
    
    def set_conditions(self, conditions_dict):
        """Set conditions from dict to JSON string"""
        self.conditions = json.dumps(conditions_dict)
    
    def get_parameters(self):
        """Parse parameters JSON string into dict"""
        try:
            return json.loads(self.parameters) if self.parameters else {}
        except json.JSONDecodeError:
            return {}
    
    def set_parameters(self, parameters_dict):
        """Set parameters from dict to JSON string"""
        self.parameters = json.dumps(parameters_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'rule_type': self.rule_type,
            'conditions': self.get_conditions(),
            'parameters': self.get_parameters(),
            'priority': self.priority,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RuleHistory(db.Model):
    """
    Version control and change tracking for rules
    """
    __tablename__ = 'rule_history'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    changes = db.Column(db.Text, nullable=False)  # JSON string describing changes
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[changed_by])
    
    def get_changes(self):
        """Parse changes JSON string into dict"""
        try:
            return json.loads(self.changes) if self.changes else {}
        except json.JSONDecodeError:
            return {}
    
    def set_changes(self, changes_dict):
        """Set changes from dict to JSON string"""
        self.changes = json.dumps(changes_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'version': self.version,
            'changes': self.get_changes(),
            'changed_by': self.changed_by,
            'user_username': self.user.username if self.user else None,
            'timestamp': self.timestamp.isoformat()
        }

class RuleTemplate(db.Model):
    """
    Predefined rule templates for easy rule creation
    """
    __tablename__ = 'rule_template'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('rule_category.id'))
    template_conditions = db.Column(db.Text, nullable=False)  # JSON template with placeholders
    parameters_schema = db.Column(db.Text)  # JSON schema for parameters validation
    is_public = db.Column(db.Boolean, default=False)  # Public templates available to all users
    usage_count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def get_template_conditions(self):
        """Parse template conditions JSON string into dict"""
        try:
            return json.loads(self.template_conditions) if self.template_conditions else {}
        except json.JSONDecodeError:
            return {}
    
    def get_parameters_schema(self):
        """Parse parameters schema JSON string into dict"""
        try:
            return json.loads(self.parameters_schema) if self.parameters_schema else {}
        except json.JSONDecodeError:
            return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'template_conditions': self.get_template_conditions(),
            'parameters_schema': self.get_parameters_schema(),
            'is_public': self.is_public,
            'usage_count': self.usage_count,
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat()
        }

class RulePerformance(db.Model):
    """
    Track rule performance and effectiveness metrics
    """
    __tablename__ = 'rule_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('analysis_report.id'), nullable=False)
    anomalies_detected = db.Column(db.Integer, default=0)
    false_positives = db.Column(db.Integer, default=0)
    execution_time_ms = db.Column(db.Integer)  # Execution time in milliseconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    report = db.relationship('AnalysisReport', foreign_keys=[report_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'rule_name': self.rule.name if self.rule else None,
            'report_id': self.report_id,
            'anomalies_detected': self.anomalies_detected,
            'false_positives': self.false_positives,
            'execution_time_ms': self.execution_time_ms,
            'timestamp': self.timestamp.isoformat()
        }

class Location(db.Model):
    """
    Dynamic warehouse location definitions replacing Excel-based rules
    """
    __tablename__ = 'location'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    pattern = db.Column(db.String(100))  # Regex pattern for matching location codes
    location_type = db.Column(db.String(30), nullable=False)  # RECEIVING, FINAL, TRANSITIONAL
    capacity = db.Column(db.Integer, default=1)
    allowed_products = db.Column(db.Text)  # JSON array of allowed product patterns
    zone = db.Column(db.String(50))  # Warehouse zone identifier
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_allowed_products(self):
        """Parse allowed products JSON string into list"""
        try:
            return json.loads(self.allowed_products) if self.allowed_products else []
        except json.JSONDecodeError:
            return []
    
    def set_allowed_products(self, products_list):
        """Set allowed products from list to JSON string"""
        self.allowed_products = json.dumps(products_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'pattern': self.pattern,
            'location_type': self.location_type,
            'capacity': self.capacity,
            'allowed_products': self.get_allowed_products(),
            'zone': self.zone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

# ==== ENHANCED EXISTING MODELS ====

# Extend Anomaly model to include rule relationship
def enhance_anomaly_model():
    """
    Adds rule_id foreign key to existing Anomaly model
    This will be handled in migration script
    """
    pass

# Extend AnalysisReport model to include rules used
def enhance_analysis_report_model():
    """
    Adds rules_used JSON field to track which rules were applied
    This will be handled in migration script
    """
    pass

# ==== UTILITY FUNCTIONS ====

def create_default_categories():
    """
    Create the Three Pillars Framework categories
    """
    categories = [
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
    
    created_categories = []
    for cat_data in categories:
        existing = RuleCategory.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = RuleCategory(**cat_data)
            db.session.add(category)
            created_categories.append(category)
    
    db.session.commit()
    return created_categories

def get_default_rules_data():
    """
    Returns the default rules package as defined in the implementation plan
    """
    return [
        # Core 4 Rules (Original)
        {
            "name": "Forgotten Pallets Alert",
            "rule_type": "STAGNANT_PALLETS",
            "category": "FLOW_TIME",
            "description": "Detects pallets that have been sitting in receiving or transitional areas for too long",
            "conditions": {
                "location_types": ["RECEIVING", "TRANSITIONAL"],
                "time_threshold_hours": 6
            },
            "parameters": {
                "time_threshold_hours": {"type": "integer", "min": 1, "max": 24, "default": 6}
            },
            "priority": "VERY_HIGH"
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