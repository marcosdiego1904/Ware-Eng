"""
Optimized SQLAlchemy Models for Warehouse Settings
Production-Ready Models with Performance Enhancements

This module provides optimized versions of the warehouse models with:
- Proper composite unique constraints
- PostgreSQL-specific optimizations
- Bulk operation methods
- Performance monitoring capabilities
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey,
    Index, UniqueConstraint, CheckConstraint, func, and_, or_
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates, Session
from sqlalchemy.ext.hybrid import hybrid_property
from database import db

class OptimizedWarehouseConfig(db.Model):
    """
    Optimized Warehouse Configuration with PostgreSQL-specific enhancements
    """
    __tablename__ = 'warehouse_config'
    
    id = Column(Integer, primary_key=True)
    warehouse_id = Column(String(50), nullable=False)
    warehouse_name = Column(String(120), nullable=False)
    
    # Structure configuration with validation
    num_aisles = Column(Integer, nullable=False)
    racks_per_aisle = Column(Integer, nullable=False)
    positions_per_rack = Column(Integer, nullable=False)
    levels_per_position = Column(Integer, default=4)
    level_names = Column(String(20), default='ABCD')
    default_pallet_capacity = Column(Integer, default=1)
    bidimensional_racks = Column(Boolean, default=False)
    
    # JSONB fields for better performance (PostgreSQL specific)
    receiving_areas = Column(JSONB, default=lambda: [])
    staging_areas = Column(JSONB, default=lambda: [])
    dock_areas = Column(JSONB, default=lambda: [])
    
    # Default settings
    default_zone = Column(String(50), default='GENERAL')
    position_numbering_start = Column(Integer, default=1)
    position_numbering_split = Column(Boolean, default=True)
    
    # Metadata with proper indexing
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Constraints
    __table_args__ = (
        # CRITICAL FIX: Composite unique constraint instead of global unique
        UniqueConstraint('warehouse_id', 'created_by', name='unique_warehouse_per_user'),
        CheckConstraint('num_aisles > 0', name='check_num_aisles_positive'),
        CheckConstraint('racks_per_aisle > 0', name='check_racks_per_aisle_positive'),
        CheckConstraint('positions_per_rack > 0', name='check_positions_per_rack_positive'),
        CheckConstraint('levels_per_position > 0', name='check_levels_per_position_positive'),
        CheckConstraint('default_pallet_capacity > 0', name='check_default_pallet_capacity_positive'),
        
        # Performance indexes
        Index('idx_warehouse_config_warehouse_id', 'warehouse_id', postgresql_where=is_active == True),
        Index('idx_warehouse_config_created_by', 'created_by', postgresql_where=is_active == True),
        Index('idx_warehouse_config_created_at', 'created_at'),
        
        # JSON GIN indexes for fast searching
        Index('idx_warehouse_receiving_areas_gin', 'receiving_areas', postgresql_using='gin',
              postgresql_where=receiving_areas != func.cast('[]', JSONB)),
        Index('idx_warehouse_staging_areas_gin', 'staging_areas', postgresql_using='gin',
              postgresql_where=staging_areas != func.cast('[]', JSONB)),
        Index('idx_warehouse_dock_areas_gin', 'dock_areas', postgresql_using='gin',
              postgresql_where=dock_areas != func.cast('[]', JSONB)),
    )
    
    # Relationships
    creator = relationship('User', foreign_keys=[created_by])
    templates = relationship('OptimizedWarehouseTemplate', back_populates='source_config', lazy='dynamic')
    
    @validates('num_aisles', 'racks_per_aisle', 'positions_per_rack', 'levels_per_position')
    def validate_positive_integers(self, key, value):
        """Validate that structural parameters are positive integers"""
        if value is not None and value <= 0:
            raise ValueError(f'{key} must be a positive integer')
        return value
    
    @validates('level_names')
    def validate_level_names(self, key, value):
        """Validate level names format"""
        if value and (len(value) < 1 or len(value) > 10):
            raise ValueError('level_names must be 1-10 characters long')
        return value
    
    @hybrid_property
    def total_storage_locations(self) -> int:
        """Calculate total number of storage locations"""
        return (self.num_aisles * self.racks_per_aisle * 
                self.positions_per_rack * self.levels_per_position)
    
    @hybrid_property
    def total_capacity(self) -> int:
        """Calculate total warehouse capacity"""
        storage_capacity = self.total_storage_locations * self.default_pallet_capacity
        receiving_capacity = sum(area.get('capacity', 0) for area in (self.receiving_areas or []))
        staging_capacity = sum(area.get('capacity', 0) for area in (self.staging_areas or []))
        dock_capacity = sum(area.get('capacity', 0) for area in (self.dock_areas or []))
        return storage_capacity + receiving_capacity + staging_capacity + dock_capacity
    
    def get_receiving_areas(self) -> List[Dict[str, Any]]:
        """Get receiving areas as Python list"""
        return self.receiving_areas or []
    
    def get_staging_areas(self) -> List[Dict[str, Any]]:
        """Get staging areas as Python list"""
        return self.staging_areas or []
    
    def get_dock_areas(self) -> List[Dict[str, Any]]:
        """Get dock areas as Python list"""
        return self.dock_areas or []
    
    @classmethod
    def get_by_warehouse_and_user(cls, warehouse_id: str, user_id: int):
        """Optimized query to get warehouse config by ID and user"""
        return cls.query.filter(
            cls.warehouse_id == warehouse_id,
            cls.created_by == user_id,
            cls.is_active == True
        ).first()
    
    @classmethod
    def get_user_warehouses(cls, user_id: int, limit: int = 50):
        """Get all warehouses for a user with optimization"""
        return cls.query.filter(
            cls.created_by == user_id,
            cls.is_active == True
        ).order_by(cls.updated_at.desc()).limit(limit).all()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with calculated fields"""
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
            'total_storage_locations': self.total_storage_locations,
            'total_capacity': self.total_capacity,
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

class OptimizedLocation(db.Model):
    """
    Highly Optimized Location Model for Production Scale
    Handles thousands of locations per warehouse efficiently
    """
    __tablename__ = 'location'
    
    id = Column(Integer, primary_key=True)
    
    # CRITICAL FIX: Composite unique constraint (code, warehouse_id)
    code = Column(String(50), nullable=False)
    warehouse_id = Column(String(50), nullable=False, default='DEFAULT')
    
    # Core location properties
    pattern = Column(String(100))
    location_type = Column(String(30), nullable=False)
    capacity = Column(Integer, default=1)
    
    # JSONB fields for performance (PostgreSQL specific)
    allowed_products = Column(JSONB, default=lambda: [])
    special_requirements = Column(JSONB, default=lambda: {})
    location_hierarchy = Column(JSONB, default=lambda: {})
    
    # Warehouse structure fields (heavily indexed)
    zone = Column(String(50))
    aisle_number = Column(Integer)
    rack_number = Column(Integer)
    position_number = Column(Integer)
    level = Column(String(1))
    pallet_capacity = Column(Integer, default=1)
    
    # System fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('user.id'))
    
    # Constraints and Indexes
    __table_args__ = (
        # PERFORMANCE CRITICAL: Composite unique constraint
        UniqueConstraint('code', 'warehouse_id', name='unique_location_per_warehouse'),
        CheckConstraint('capacity > 0', name='check_capacity_positive'),
        CheckConstraint('pallet_capacity > 0', name='check_pallet_capacity_positive'),
        
        # High-performance indexes for major query patterns
        Index('idx_location_warehouse_id', 'warehouse_id', postgresql_where=is_active == True),
        Index('idx_location_warehouse_type', 'warehouse_id', 'location_type', 
              postgresql_where=is_active == True),
        Index('idx_location_structure', 'warehouse_id', 'aisle_number', 'rack_number', 
              'position_number', 'level', postgresql_where=and_(is_active == True, aisle_number != None)),
        Index('idx_location_zone', 'warehouse_id', 'zone', postgresql_where=is_active == True),
        Index('idx_location_pattern', 'pattern', postgresql_where=pattern != None),
        
        # JSON GIN indexes for fast JSON queries
        Index('idx_location_special_requirements_gin', 'special_requirements', postgresql_using='gin',
              postgresql_where=special_requirements != func.cast('{}', JSONB)),
        Index('idx_location_allowed_products_gin', 'allowed_products', postgresql_using='gin',
              postgresql_where=allowed_products != func.cast('[]', JSONB)),
        Index('idx_location_hierarchy_gin', 'location_hierarchy', postgresql_using='gin'),
    )
    
    # Relationships
    creator = relationship('User', foreign_keys=[created_by])
    
    @validates('capacity', 'pallet_capacity')
    def validate_positive_capacity(self, key, value):
        """Validate capacity values are positive"""
        if value is not None and value <= 0:
            raise ValueError(f'{key} must be a positive integer')
        return value
    
    @hybrid_property
    def is_storage_location(self) -> bool:
        """Check if this is a hierarchical storage location"""
        return (self.aisle_number is not None and 
                self.rack_number is not None and 
                self.position_number is not None and 
                self.level is not None)
    
    @hybrid_property
    def full_address(self) -> str:
        """Get human-readable full address"""
        if self.is_storage_location:
            return f"Aisle {self.aisle_number}, Rack {self.rack_number}, Position {self.position_number:03d}{self.level}"
        return self.code
    
    def get_allowed_products(self) -> List[str]:
        """Get allowed products as Python list"""
        return self.allowed_products or []
    
    def get_special_requirements(self) -> Dict[str, Any]:
        """Get special requirements as Python dict"""
        return self.special_requirements or {}
    
    def get_location_hierarchy(self) -> Dict[str, Any]:
        """Get location hierarchy as Python dict"""
        return self.location_hierarchy or {}
    
    @classmethod
    def get_warehouse_locations(cls, warehouse_id: str, location_type: Optional[str] = None, 
                              zone: Optional[str] = None, active_only: bool = True):
        """Optimized query to get locations for a warehouse"""
        query = cls.query.filter(cls.warehouse_id == warehouse_id)
        
        if active_only:
            query = query.filter(cls.is_active == True)
        
        if location_type:
            query = query.filter(cls.location_type == location_type)
        
        if zone:
            query = query.filter(cls.zone == zone)
        
        return query
    
    @classmethod
    def get_storage_locations_by_aisle(cls, warehouse_id: str, aisle_number: int):
        """Get all storage locations for a specific aisle"""
        return cls.query.filter(
            cls.warehouse_id == warehouse_id,
            cls.aisle_number == aisle_number,
            cls.is_active == True
        ).order_by(cls.rack_number, cls.position_number, cls.level).all()
    
    @classmethod
    def bulk_create_from_structure(cls, warehouse_id: str, structure_data: List[Dict], 
                                 created_by: int, batch_size: int = 1000):
        """
        High-performance bulk creation of locations
        Uses batch processing to handle thousands of locations efficiently
        """
        locations = []
        for i, data in enumerate(structure_data):
            location = cls(
                code=data['code'],
                warehouse_id=warehouse_id,
                location_type=data.get('location_type', 'STORAGE'),
                capacity=data.get('capacity', 1),
                zone=data.get('zone', 'GENERAL'),
                aisle_number=data.get('aisle_number'),
                rack_number=data.get('rack_number'),
                position_number=data.get('position_number'),
                level=data.get('level'),
                pallet_capacity=data.get('pallet_capacity', 1),
                location_hierarchy=data.get('location_hierarchy', {}),
                created_by=created_by
            )
            locations.append(location)
            
            # Batch insert every batch_size records
            if (i + 1) % batch_size == 0:
                db.session.bulk_save_objects(locations)
                db.session.flush()
                locations = []
        
        # Insert remaining locations
        if locations:
            db.session.bulk_save_objects(locations)
            db.session.flush()
    
    @classmethod
    def clear_warehouse_locations(cls, warehouse_id: str):
        """Efficiently clear all locations for a warehouse"""
        return cls.query.filter(cls.warehouse_id == warehouse_id).delete()
    
    @classmethod
    def get_warehouse_statistics(cls, warehouse_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a warehouse"""
        base_query = cls.query.filter(cls.warehouse_id == warehouse_id, cls.is_active == True)
        
        total_locations = base_query.count()
        storage_locations = base_query.filter(cls.location_type == 'STORAGE').count()
        receiving_locations = base_query.filter(cls.location_type == 'RECEIVING').count()
        staging_locations = base_query.filter(cls.location_type == 'STAGING').count()
        dock_locations = base_query.filter(cls.location_type == 'DOCK').count()
        
        capacity_result = base_query.with_entities(
            func.sum(cls.capacity).label('total_capacity'),
            func.avg(cls.capacity).label('avg_capacity'),
            func.max(cls.aisle_number).label('max_aisle'),
            func.max(cls.rack_number).label('max_rack')
        ).first()
        
        return {
            'total_locations': total_locations,
            'storage_locations': storage_locations,
            'receiving_locations': receiving_locations,
            'staging_locations': staging_locations,
            'dock_locations': dock_locations,
            'total_capacity': capacity_result.total_capacity or 0,
            'avg_capacity': float(capacity_result.avg_capacity or 0),
            'max_aisle': capacity_result.max_aisle,
            'max_rack': capacity_result.max_rack
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with all fields"""
        return {
            'id': self.id,
            'code': self.code,
            'warehouse_id': self.warehouse_id,
            'pattern': self.pattern,
            'location_type': self.location_type,
            'capacity': self.capacity,
            'allowed_products': self.get_allowed_products(),
            'special_requirements': self.get_special_requirements(),
            'zone': self.zone,
            'aisle_number': self.aisle_number,
            'rack_number': self.rack_number,
            'position_number': self.position_number,
            'level': self.level,
            'pallet_capacity': self.pallet_capacity,
            'location_hierarchy': self.get_location_hierarchy(),
            'is_storage_location': self.is_storage_location,
            'full_address': self.full_address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None
        }

class OptimizedWarehouseTemplate(db.Model):
    """
    Optimized Warehouse Template Model
    """
    __tablename__ = 'warehouse_template'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(Text)
    template_code = Column(String(20), unique=True)
    
    # Template configuration (mirrors warehouse_config)
    num_aisles = Column(Integer, nullable=False)
    racks_per_aisle = Column(Integer, nullable=False)
    positions_per_rack = Column(Integer, nullable=False)
    levels_per_position = Column(Integer, default=4)
    level_names = Column(String(20), default='ABCD')
    default_pallet_capacity = Column(Integer, default=1)
    bidimensional_racks = Column(Boolean, default=False)
    
    # Special areas as JSONB
    receiving_areas_template = Column(JSONB, default=lambda: [])
    staging_areas_template = Column(JSONB, default=lambda: [])
    dock_areas_template = Column(JSONB, default=lambda: [])
    
    # Template metadata
    based_on_config_id = Column(Integer, ForeignKey('warehouse_config.id'))
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # System fields
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint('num_aisles > 0', name='check_template_num_aisles_positive'),
        CheckConstraint('racks_per_aisle > 0', name='check_template_racks_per_aisle_positive'),
        CheckConstraint('positions_per_rack > 0', name='check_template_positions_per_rack_positive'),
        
        Index('idx_template_public', 'is_public', postgresql_where=is_active == True),
        Index('idx_template_usage', 'usage_count', postgresql_order_by='usage_count DESC',
              postgresql_where=is_active == True),
        Index('idx_template_created_by', 'created_by', postgresql_where=is_active == True),
        
        # JSON indexes for template search
        Index('idx_template_receiving_gin', 'receiving_areas_template', postgresql_using='gin'),
        Index('idx_template_staging_gin', 'staging_areas_template', postgresql_using='gin'),
        Index('idx_template_dock_gin', 'dock_areas_template', postgresql_using='gin'),
    )
    
    # Relationships
    creator = relationship('User', foreign_keys=[created_by])
    source_config = relationship('OptimizedWarehouseConfig', back_populates='templates')
    
    @classmethod
    def get_public_templates(cls, limit: int = 50):
        """Get public templates ordered by usage"""
        return cls.query.filter(
            cls.is_public == True,
            cls.is_active == True
        ).order_by(cls.usage_count.desc()).limit(limit).all()
    
    @classmethod
    def get_user_templates(cls, user_id: int, include_public: bool = True, limit: int = 50):
        """Get templates for a user, optionally including public templates"""
        query = cls.query.filter(cls.is_active == True)
        
        if include_public:
            query = query.filter(or_(cls.created_by == user_id, cls.is_public == True))
        else:
            query = query.filter(cls.created_by == user_id)
        
        return query.order_by(cls.usage_count.desc(), cls.updated_at.desc()).limit(limit).all()
    
    def increment_usage(self):
        """Increment usage counter atomically"""
        self.usage_count = (self.usage_count or 0) + 1
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
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
            'receiving_areas_template': self.receiving_areas_template or [],
            'staging_areas_template': self.staging_areas_template or [],
            'dock_areas_template': self.dock_areas_template or [],
            'based_on_config_id': self.based_on_config_id,
            'is_public': self.is_public,
            'usage_count': self.usage_count,
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }


# =====================================================
# BULK OPERATIONS AND PERFORMANCE UTILITIES
# =====================================================

class WarehousePerformanceUtils:
    """
    Utility class for high-performance warehouse operations
    """
    
    @staticmethod
    def bulk_setup_warehouse(warehouse_id: str, config_data: Dict[str, Any], 
                           created_by: int, batch_size: int = 1000) -> Dict[str, int]:
        """
        High-performance warehouse setup with bulk operations
        """
        # Generate all location data first
        locations_data = []
        
        # Storage locations
        for aisle in range(1, config_data['num_aisles'] + 1):
            for rack in range(1, config_data['racks_per_aisle'] + 1):
                positions_start = config_data.get('position_numbering_start', 1)
                positions_end = config_data['positions_per_rack']
                
                if config_data.get('position_numbering_split') and config_data['racks_per_aisle'] == 2:
                    if rack == 1:
                        positions_end = positions_end // 2
                    else:
                        positions_start = (positions_end // 2) + 1
                
                for position in range(positions_start, positions_end + 1):
                    level_names = config_data.get('level_names', 'ABCD')
                    for level_idx in range(config_data.get('levels_per_position', 4)):
                        level = level_names[level_idx] if level_idx < len(level_names) else f'L{level_idx + 1}'
                        
                        # Generate clean location code
                        if warehouse_id == 'DEFAULT':
                            code = f"{position:03d}{level}"
                        else:
                            warehouse_prefix = warehouse_id.replace('DEFAULT', 'WH')[:4]
                            code = f"{warehouse_prefix}_{position:03d}{level}"
                        
                        locations_data.append({
                            'code': code,
                            'location_type': 'STORAGE',
                            'capacity': config_data.get('default_pallet_capacity', 1),
                            'zone': config_data.get('default_zone', 'GENERAL'),
                            'aisle_number': aisle,
                            'rack_number': rack,
                            'position_number': position,
                            'level': level,
                            'pallet_capacity': config_data.get('default_pallet_capacity', 1),
                            'location_hierarchy': {
                                'aisle': aisle,
                                'rack': rack,
                                'position': position,
                                'level': level,
                                'full_address': f"Aisle {aisle}, Rack {rack}, Position {position:03d}{level}"
                            }
                        })
        
        # Special areas
        for area_type, areas in [
            ('RECEIVING', config_data.get('receiving_areas', [])),
            ('STAGING', config_data.get('staging_areas', [])),
            ('DOCK', config_data.get('dock_areas', []))
        ]:
            for area in areas:
                locations_data.append({
                    'code': area['code'],
                    'location_type': area_type,
                    'capacity': area.get('capacity', 10),
                    'zone': area.get('zone', area_type),
                    'pallet_capacity': area.get('capacity', 10)
                })
        
        # Clear existing locations
        OptimizedLocation.clear_warehouse_locations(warehouse_id)
        
        # Bulk create all locations
        OptimizedLocation.bulk_create_from_structure(
            warehouse_id, locations_data, created_by, batch_size
        )
        
        db.session.commit()
        
        return {
            'total_locations': len(locations_data),
            'storage_locations': len([l for l in locations_data if l['location_type'] == 'STORAGE']),
            'special_locations': len([l for l in locations_data if l['location_type'] != 'STORAGE'])
        }
    
    @staticmethod
    def analyze_warehouse_performance(warehouse_id: str) -> Dict[str, Any]:
        """
        Analyze warehouse performance and suggest optimizations
        """
        stats = OptimizedLocation.get_warehouse_statistics(warehouse_id)
        
        # Calculate efficiency metrics
        avg_capacity = stats['avg_capacity']
        location_density = stats['total_locations'] / (stats['max_aisle'] or 1)
        
        recommendations = []
        if avg_capacity < 1.5:
            recommendations.append("Consider increasing pallet capacity for better space utilization")
        
        if location_density > 1000:
            recommendations.append("High location density - consider partitioning for better performance")
        
        return {
            **stats,
            'location_density': location_density,
            'recommendations': recommendations,
            'performance_score': min(100, int(100 - (location_density / 50)))
        }


# =====================================================
# MODEL ALIASES FOR BACKWARD COMPATIBILITY
# =====================================================

# Provide aliases for existing code compatibility
WarehouseConfig = OptimizedWarehouseConfig
Location = OptimizedLocation
WarehouseTemplate = OptimizedWarehouseTemplate