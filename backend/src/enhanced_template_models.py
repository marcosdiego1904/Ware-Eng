"""
Enhanced Template Models with Privacy and Organization Support
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from database import db
import json

class Organization(db.Model):
    """
    Company/Organization model for template privacy control
    """
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_name = db.Column(db.String(150), nullable=False)
    organization_code = db.Column(db.String(50), unique=True, nullable=False)
    industry = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    users = db.relationship('User', backref='organization', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_name': self.organization_name,
            'organization_code': self.organization_code,
            'industry': self.industry,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class TemplateCategory(db.Model):
    """
    Template categories for better organization
    """
    __tablename__ = 'template_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False, unique=True)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon_name = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category_name': self.category_name,
            'display_name': self.display_name,
            'description': self.description,
            'icon_name': self.icon_name,
            'sort_order': self.sort_order,
            'is_active': self.is_active
        }

class EnhancedWarehouseTemplate(db.Model):
    """
    Enhanced warehouse template with privacy controls and organization support
    """
    __tablename__ = 'warehouse_template'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    template_code = db.Column(db.String(20), unique=True)
    
    # Template configuration
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
    
    # Enhanced privacy and organization fields
    visibility = db.Column(db.String(20), default='PRIVATE')  # PRIVATE, COMPANY, PUBLIC
    company_id = db.Column(db.String(100))  # For company-wide templates
    industry_category = db.Column(db.String(50))
    template_category = db.Column(db.String(50), default='CUSTOM')
    featured = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Numeric(2, 1), default=0.0)
    downloads_count = db.Column(db.Integer, default=0)
    tags = db.Column(db.Text)  # JSON array of tags
    
    # Legacy compatibility
    is_public = db.Column(db.Boolean, default=False)  # Keep for backward compatibility
    usage_count = db.Column(db.Integer, default=0)
    based_on_config_id = db.Column(db.Integer, db.ForeignKey('warehouse_config.id'))
    
    # System fields
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    permissions = db.relationship('TemplatePermission', backref='template', lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship('TemplateReview', backref='template', lazy=True, cascade="all, delete-orphan")
    
    def get_tags(self):
        """Parse tags JSON string into list"""
        try:
            return json.loads(self.tags) if self.tags else []
        except json.JSONDecodeError:
            return []
    
    def set_tags(self, tags_list):
        """Set tags from list to JSON string"""
        self.tags = json.dumps(tags_list)
    
    def get_visibility_display(self):
        """Get human-readable visibility status"""
        visibility_map = {
            'PRIVATE': 'Private (Only You)',
            'COMPANY': 'Company Only',
            'PUBLIC': 'Public (Everyone)'
        }
        return visibility_map.get(self.visibility, 'Private')
    
    def can_user_access(self, user):
        """Check if a user can access this template"""
        # Creator always has access
        if self.created_by == user.id:
            return True
        
        # Public templates are accessible to everyone
        if self.visibility == 'PUBLIC' or self.is_public:
            return True
        
        # Company templates are accessible to same organization users
        if self.visibility == 'COMPANY':
            creator_org = self.creator.organization_id if self.creator else None
            user_org = user.organization_id if hasattr(user, 'organization_id') else None
            return creator_org and user_org and creator_org == user_org
        
        # Check explicit permissions
        permission = TemplatePermission.query.filter_by(
            template_id=self.id,
            user_id=user.id
        ).first()
        
        return permission is not None
    
    def increment_usage(self):
        """Increment usage counter when template is applied"""
        self.usage_count = (self.usage_count or 0) + 1
        self.downloads_count = (self.downloads_count or 0) + 1
        db.session.commit()
    
    def calculate_rating(self):
        """Calculate average rating from reviews"""
        if self.reviews:
            total_rating = sum(review.rating for review in self.reviews)
            self.rating = round(total_rating / len(self.reviews), 1)
            return self.rating
        return 0.0
    
    def to_dict(self, include_sensitive=False):
        base_dict = {
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
            'visibility': self.visibility,
            'visibility_display': self.get_visibility_display(),
            'template_category': self.template_category,
            'featured': self.featured,
            'rating': float(self.rating) if self.rating else 0.0,
            'usage_count': self.usage_count,
            'downloads_count': self.downloads_count,
            'tags': self.get_tags(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'creator_username': self.creator.username if self.creator else None,
            'creator_organization': self.creator.organization.organization_name if self.creator and hasattr(self.creator, 'organization') and self.creator.organization else None,
            'review_count': len(self.reviews),
            # Legacy compatibility
            'is_public': self.visibility == 'PUBLIC'
        }
        
        if include_sensitive:
            base_dict.update({
                'receiving_areas_template': self.get_receiving_areas_template(),
                'staging_areas_template': self.get_staging_areas_template(),
                'dock_areas_template': self.get_dock_areas_template(),
                'company_id': self.company_id,
                'industry_category': self.industry_category,
                'created_by': self.created_by
            })
        
        return base_dict

class TemplatePermission(db.Model):
    """
    Explicit template sharing permissions
    """
    __tablename__ = 'template_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('warehouse_template.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    permission_type = db.Column(db.String(20), default='VIEW')  # VIEW, USE, EDIT
    granted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    granted_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    organization = db.relationship('Organization', foreign_keys=[organization_id])
    granter = db.relationship('User', foreign_keys=[granted_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'permission_type': self.permission_type,
            'granted_by': self.granted_by,
            'granted_at': self.granted_at.isoformat(),
            'user_username': self.user.username if self.user else None,
            'organization_name': self.organization.organization_name if self.organization else None,
            'granter_username': self.granter.username if self.granter else None
        }

class TemplateReview(db.Model):
    """
    Template reviews and ratings
    """
    __tablename__ = 'template_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('warehouse_template.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'),
        db.UniqueConstraint('template_id', 'user_id', name='one_review_per_user'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'created_at': self.created_at.isoformat(),
            'username': self.user.username if self.user else None
        }