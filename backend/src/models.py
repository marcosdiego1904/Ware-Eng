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
    Dynamic warehouse location definitions with hierarchical structure support
    """
    __tablename__ = 'location'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    pattern = db.Column(db.String(100))  # Regex pattern for matching location codes
    location_type = db.Column(db.String(30), nullable=False)  # RECEIVING, STORAGE, STAGING, DOCK
    capacity = db.Column(db.Integer, default=1)
    allowed_products = db.Column(db.Text)  # JSON array of allowed product patterns
    zone = db.Column(db.String(50))  # Warehouse zone identifier
    
    # Warehouse structure fields for hierarchical organization
    warehouse_id = db.Column(db.String(50), default='DEFAULT')  # Multi-warehouse support
    aisle_number = db.Column(db.Integer)  # Aisle number (1, 2, 3, 4, etc.)
    rack_number = db.Column(db.Integer)   # Rack number within aisle (1, 2, etc.)
    position_number = db.Column(db.Integer)  # Position number (001-100, etc.)
    level = db.Column(db.String(1))       # Level within position (A, B, C, D)
    pallet_capacity = db.Column(db.Integer, default=1)  # Pallets per level (1 or 2)
    
    # Additional metadata
    location_hierarchy = db.Column(db.Text)  # JSON for flexible hierarchy data
    special_requirements = db.Column(db.Text)  # JSON for temperature, hazmat, etc.
    
    # System fields
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    
    # Database indexes for performance optimization
    __table_args__ = (
        db.Index('idx_location_warehouse_type', 'warehouse_id', 'location_type'),
        db.Index('idx_location_warehouse_zone', 'warehouse_id', 'zone'),
        db.Index('idx_location_warehouse_active', 'warehouse_id', 'is_active'),
        db.Index('idx_location_structure', 'warehouse_id', 'aisle_number', 'rack_number'),
        db.Index('idx_location_code_active', 'code', 'is_active'),
        db.Index('idx_location_created_by', 'created_by'),
    )
    
    def get_allowed_products(self):
        """Parse allowed products JSON string into list"""
        try:
            return json.loads(self.allowed_products) if self.allowed_products else []
        except json.JSONDecodeError:
            return []
    
    def set_allowed_products(self, products_list):
        """Set allowed products from list to JSON string"""
        self.allowed_products = json.dumps(products_list)
    
    def get_location_hierarchy(self):
        """Parse location hierarchy JSON string into dict"""
        try:
            return json.loads(self.location_hierarchy) if self.location_hierarchy else {}
        except json.JSONDecodeError:
            return {}
    
    def set_location_hierarchy(self, hierarchy_dict):
        """Set location hierarchy from dict to JSON string"""
        self.location_hierarchy = json.dumps(hierarchy_dict)
    
    def get_special_requirements(self):
        """Parse special requirements JSON string into dict"""
        try:
            return json.loads(self.special_requirements) if self.special_requirements else {}
        except json.JSONDecodeError:
            return {}
    
    def set_special_requirements(self, requirements_dict):
        """Set special requirements from dict to JSON string"""
        self.special_requirements = json.dumps(requirements_dict)
    
    def is_storage_location(self):
        """Check if this is a storage location with hierarchical structure"""
        return (self.aisle_number is not None and 
                self.rack_number is not None and 
                self.position_number is not None and 
                self.level is not None)
    
    def get_full_address(self):
        """Get human-readable full address"""
        if self.is_storage_location():
            return f"Aisle {self.aisle_number}, Rack {self.rack_number}, Position {self.position_number:03d}{self.level}"
        else:
            return self.code
    
    def generate_code_from_structure(self):
        """Generate location code from hierarchical structure"""
        if self.is_storage_location():
            # Format: 01-02-001A (clean format, no DEFAULT_ prefix)
            base_code = f"{self.aisle_number:02d}-{self.rack_number:02d}-{self.position_number:03d}{self.level}"
            
            # Apply clean naming logic
            if self.warehouse_id == 'DEFAULT' or self.warehouse_id is None:
                return base_code
            else:
                warehouse_prefix = self.warehouse_id.replace('DEFAULT', 'WH')[:4]
                return f"{warehouse_prefix}_{base_code}"
        else:
            return self.code
    
    @classmethod
    def create_from_structure(cls, warehouse_id, aisle_num, rack_num, position_num, level, 
                            pallet_capacity=1, zone='GENERAL', location_type='STORAGE', **kwargs):
        """Create location from warehouse structure parameters"""
        # Generate clean location code (Phase 1: Remove DEFAULT_ prefix)
        base_code = f"{aisle_num:02d}-{rack_num:02d}-{position_num:03d}{level}"
        
        # Use clean format for all warehouses (no prefixes needed)
        code = base_code
        
        # Check for conflicts and add suffix if needed
        attempt = 0
        original_code = code
        while cls.query.filter_by(code=code).first():
            attempt += 1
            code = f"{original_code}_{attempt}"
        
        location = cls(
            code=code,
            warehouse_id=warehouse_id,
            aisle_number=aisle_num,
            rack_number=rack_num,
            position_number=position_num,
            level=level,
            pallet_capacity=pallet_capacity,
            capacity=pallet_capacity,  # Keep backward compatibility
            zone=zone,
            location_type=location_type,
            **kwargs
        )
        
        # Set hierarchy data for queries and analytics
        location.set_location_hierarchy({
            'aisle': aisle_num,
            'rack': rack_num,
            'position': position_num,
            'level': level,
            'full_address': location.get_full_address()
        })
        
        return location
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'pattern': self.pattern,
            'location_type': self.location_type,
            'capacity': self.capacity,
            'allowed_products': self.get_allowed_products(),
            'zone': self.zone,
            'warehouse_id': self.warehouse_id,
            'aisle_number': self.aisle_number,
            'rack_number': self.rack_number,
            'position_number': self.position_number,
            'level': self.level,
            'pallet_capacity': self.pallet_capacity,
            'location_hierarchy': self.get_location_hierarchy(),
            'special_requirements': self.get_special_requirements(),
            'is_storage_location': self.is_storage_location(),
            'full_address': self.get_full_address(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None
        }

class WarehouseConfig(db.Model):
    """
    Warehouse configuration settings for setup wizard and templates
    """
    __tablename__ = 'warehouse_config'
    
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.String(50), nullable=False, unique=True)
    warehouse_name = db.Column(db.String(120), nullable=False)
    
    # Structure configuration from wizard
    num_aisles = db.Column(db.Integer, nullable=False)
    racks_per_aisle = db.Column(db.Integer, nullable=False)
    positions_per_rack = db.Column(db.Integer, nullable=False)
    levels_per_position = db.Column(db.Integer, default=4)
    level_names = db.Column(db.String(20), default='ABCD')  # A,B,C,D or custom
    default_pallet_capacity = db.Column(db.Integer, default=1)
    bidimensional_racks = db.Column(db.Boolean, default=False)  # 1 or 2 pallets per level
    
    # Special areas configuration
    receiving_areas = db.Column(db.Text)  # JSON array of receiving area configs
    staging_areas = db.Column(db.Text)   # JSON array of staging area configs
    dock_areas = db.Column(db.Text)      # JSON array of dock area configs
    
    # Default settings
    default_zone = db.Column(db.String(50), default='GENERAL')
    position_numbering_start = db.Column(db.Integer, default=1)
    position_numbering_split = db.Column(db.Boolean, default=True)  # Split per rack (0-49, 50-99)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    templates = db.relationship('WarehouseTemplate', backref='source_config', lazy=True)
    
    def get_receiving_areas(self):
        """Parse receiving areas JSON string into list"""
        try:
            return json.loads(self.receiving_areas) if self.receiving_areas else []
        except json.JSONDecodeError:
            return []
    
    def set_receiving_areas(self, areas_list):
        """Set receiving areas from list to JSON string"""
        self.receiving_areas = json.dumps(areas_list)
    
    def get_staging_areas(self):
        """Parse staging areas JSON string into list"""
        try:
            return json.loads(self.staging_areas) if self.staging_areas else []
        except json.JSONDecodeError:
            return []
    
    def set_staging_areas(self, areas_list):
        """Set staging areas from list to JSON string"""
        self.staging_areas = json.dumps(areas_list)
    
    def get_dock_areas(self):
        """Parse dock areas JSON string into list"""
        try:
            return json.loads(self.dock_areas) if self.dock_areas else []
        except json.JSONDecodeError:
            return []
    
    def set_dock_areas(self, areas_list):
        """Set dock areas from list to JSON string"""
        self.dock_areas = json.dumps(areas_list)
    
    def calculate_total_storage_locations(self):
        """Calculate total number of storage locations"""
        return (self.num_aisles * self.racks_per_aisle * 
                self.positions_per_rack * self.levels_per_position)
    
    def calculate_total_capacity(self):
        """Calculate total pallet capacity"""
        storage_capacity = self.calculate_total_storage_locations() * self.default_pallet_capacity
        
        # Add special areas capacity
        receiving_capacity = sum(area.get('capacity', 0) for area in self.get_receiving_areas())
        staging_capacity = sum(area.get('capacity', 0) for area in self.get_staging_areas())
        dock_capacity = sum(area.get('capacity', 0) for area in self.get_dock_areas())
        
        return storage_capacity + receiving_capacity + staging_capacity + dock_capacity
    
    def to_dict(self):
        return {
            'id': self.id,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse_name,
            'num_aisles': self.num_aisles,
            'racks_per_aisle': self.racks_per_aisle,
            'positions_per_rack': self.positions_per_rack,
            'levels_per_position': self.levels_per_position,
            'level_names': self.level_names,
            'default_pallet_capacity': self.default_pallet_capacity,
            'bidimensional_racks': self.bidimensional_racks,
            'receiving_areas': self.get_receiving_areas(),
            'staging_areas': self.get_staging_areas(),
            'dock_areas': self.get_dock_areas(),
            'default_zone': self.default_zone,
            'position_numbering_start': self.position_numbering_start,
            'position_numbering_split': self.position_numbering_split,
            'total_storage_locations': self.calculate_total_storage_locations(),
            'total_capacity': self.calculate_total_capacity(),
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }

class WarehouseTemplate(db.Model):
    """
    Shareable warehouse templates for quick setup across multiple facilities
    """
    __tablename__ = 'warehouse_template'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    template_code = db.Column(db.String(20), unique=True)  # Shareable code like #WAR-4A2R
    
    # Template configuration (same as WarehouseConfig)
    num_aisles = db.Column(db.Integer, nullable=False)
    racks_per_aisle = db.Column(db.Integer, nullable=False)
    positions_per_rack = db.Column(db.Integer, nullable=False)
    levels_per_position = db.Column(db.Integer, default=4)
    level_names = db.Column(db.String(20), default='ABCD')
    default_pallet_capacity = db.Column(db.Integer, default=1)
    bidimensional_racks = db.Column(db.Boolean, default=False)
    
    # Special areas template
    receiving_areas_template = db.Column(db.Text)
    staging_areas_template = db.Column(db.Text)
    dock_areas_template = db.Column(db.Text)
    
    # Smart Location Format Configuration
    location_format_config = db.Column(db.Text)  # JSON configuration from SmartFormatDetector
    format_confidence = db.Column(db.Float)      # Detection confidence score (0.0-1.0)
    format_examples = db.Column(db.Text)         # JSON array of original user examples
    format_learned_date = db.Column(db.DateTime) # When format was detected/learned
    
    # Template metadata
    based_on_config_id = db.Column(db.Integer, db.ForeignKey('warehouse_config.id'))
    is_public = db.Column(db.Boolean, default=False)  # Public templates available to all
    usage_count = db.Column(db.Integer, default=0)
    
    # System fields
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    
    # Database indexes for performance optimization
    __table_args__ = (
        db.Index('idx_template_public_active', 'is_public', 'is_active'),
        db.Index('idx_template_usage_created', 'usage_count', 'created_at'),
        db.Index('idx_template_creator_active', 'created_by', 'is_active'),
        db.Index('idx_template_code_active', 'template_code', 'is_active'),
        db.Index('idx_template_structure', 'num_aisles', 'racks_per_aisle', 'positions_per_rack'),
    )
    
    def get_receiving_areas_template(self):
        """Parse receiving areas template JSON string into list"""
        try:
            return json.loads(self.receiving_areas_template) if self.receiving_areas_template else []
        except json.JSONDecodeError:
            return []
    
    def set_receiving_areas_template(self, areas_list):
        """Set receiving areas template from list to JSON string"""
        self.receiving_areas_template = json.dumps(areas_list)
    
    def get_staging_areas_template(self):
        """Parse staging areas template JSON string into list"""
        try:
            return json.loads(self.staging_areas_template) if self.staging_areas_template else []
        except json.JSONDecodeError:
            return []
    
    def set_staging_areas_template(self, areas_list):
        """Set staging areas template from list to JSON string"""
        self.staging_areas_template = json.dumps(areas_list)
    
    def get_dock_areas_template(self):
        """Parse dock areas template JSON string into list"""
        try:
            return json.loads(self.dock_areas_template) if self.dock_areas_template else []
        except json.JSONDecodeError:
            return []
    
    def set_dock_areas_template(self, areas_list):
        """Set dock areas template from list to JSON string"""
        self.dock_areas_template = json.dumps(areas_list)
    
    def get_location_format_config(self):
        """Parse location format configuration JSON string into dict"""
        try:
            return json.loads(self.location_format_config) if self.location_format_config else {}
        except json.JSONDecodeError:
            return {}
    
    def set_location_format_config(self, format_config_dict):
        """Set location format configuration from dict to JSON string"""
        if format_config_dict:
            self.location_format_config = json.dumps(format_config_dict)
            self.format_learned_date = datetime.utcnow()
        else:
            self.location_format_config = None
            self.format_learned_date = None
    
    def get_format_examples(self):
        """Parse format examples JSON string into list"""
        try:
            return json.loads(self.format_examples) if self.format_examples else []
        except json.JSONDecodeError:
            return []
    
    def set_format_examples(self, examples_list):
        """Set format examples from list to JSON string"""
        self.format_examples = json.dumps(examples_list) if examples_list else None
    
    def has_location_format(self):
        """Check if template has a learned location format configuration"""
        return bool(self.location_format_config and self.format_confidence)
    
    def get_format_summary(self):
        """Get human-readable format summary for display"""
        if not self.has_location_format():
            return "No location format configured"
        
        config = self.get_location_format_config()
        pattern_type = config.get('pattern_type', 'unknown')
        confidence = self.format_confidence or 0
        example_count = len(self.get_format_examples())
        
        return f"{pattern_type.title()} format ({confidence:.1%} confidence, {example_count} examples)"
    
    def generate_template_code(self):
        """Generate unique shareable template code"""
        import random
        import string
        
        # Format: #WAR-{aisles}A{racks}R-{random}
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        code = f"WAR-{self.num_aisles}A{self.racks_per_aisle}R-{random_suffix}"
        
        # Ensure uniqueness
        while WarehouseTemplate.query.filter_by(template_code=code).first():
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            code = f"WAR-{self.num_aisles}A{self.racks_per_aisle}R-{random_suffix}"
        
        self.template_code = code
        return code
    
    def increment_usage(self):
        """Increment usage counter when template is applied"""
        self.usage_count = (self.usage_count or 0) + 1
        db.session.commit()
    
    @classmethod
    def create_from_config(cls, config, name, description=None, is_public=False):
        """Create template from existing warehouse config"""
        template = cls(
            name=name,
            description=description or f"Template based on {config.warehouse_name}",
            num_aisles=config.num_aisles,
            racks_per_aisle=config.racks_per_aisle,
            positions_per_rack=config.positions_per_rack,
            levels_per_position=config.levels_per_position,
            level_names=config.level_names,
            default_pallet_capacity=config.default_pallet_capacity,
            bidimensional_racks=config.bidimensional_racks,
            receiving_areas_template=config.receiving_areas,
            staging_areas_template=config.staging_areas,
            dock_areas_template=config.dock_areas,
            based_on_config_id=config.id,
            is_public=is_public,
            created_by=config.created_by
        )
        
        template.generate_template_code()
        return template
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template_code': self.template_code,
            'num_aisles': self.num_aisles,
            'racks_per_aisle': self.racks_per_aisle,
            'positions_per_rack': self.positions_per_rack,
            'levels_per_position': self.levels_per_position,
            'level_names': self.level_names,
            'default_pallet_capacity': self.default_pallet_capacity,
            'bidimensional_racks': self.bidimensional_racks,
            'receiving_areas_template': self.get_receiving_areas_template(),
            'staging_areas_template': self.get_staging_areas_template(),
            'dock_areas_template': self.get_dock_areas_template(),
            'location_format_config': self.get_location_format_config(),
            'format_confidence': self.format_confidence,
            'format_examples': self.get_format_examples(),
            'format_learned_date': self.format_learned_date.isoformat() if self.format_learned_date else None,
            'has_location_format': self.has_location_format(),
            'format_summary': self.get_format_summary(),
            'based_on_config_id': self.based_on_config_id,
            'is_public': self.is_public,
            'usage_count': self.usage_count,
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
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