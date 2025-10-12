"""
Core database models that need to be shared between app.py and other modules
"""
from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))  # Increased to accommodate scrypt hashes
    reports = db.relationship('AnalysisReport', backref='author', lazy=True)
    warehouse_access = db.relationship('UserWarehouseAccess', backref='user', lazy=True, cascade="all, delete-orphan")

    # Analysis preferences - Clear Previous Anomalies feature
    clear_previous_anomalies = db.Column(db.Boolean, default=True, nullable=False)  # Default: clear on new analysis
    show_clear_warning = db.Column(db.Boolean, default=True, nullable=False)  # Default: show warning modal

    # Database efficiency limits - Control resource usage per user
    max_reports = db.Column(db.Integer, default=5, nullable=False)  # Maximum number of reports allowed
    max_templates = db.Column(db.Integer, default=5, nullable=False)  # Maximum number of templates allowed

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_default_warehouse(self):
        """Get user's default warehouse for automatic context resolution"""
        default_access = UserWarehouseAccess.query.filter_by(
            user_id=self.id, 
            is_default=True
        ).first()
        return default_access.warehouse_id if default_access else None
    
    def get_accessible_warehouses(self):
        """Get list of warehouse IDs the user has access to"""
        return [access.warehouse_id for access in self.warehouse_access]
    
    def has_warehouse_access(self, warehouse_id, required_level='READ'):
        """Check if user has specific level access to warehouse"""
        access_levels = {'READ': 1, 'WRITE': 2, 'ADMIN': 3}
        required_level_num = access_levels.get(required_level, 1)
        
        user_access = UserWarehouseAccess.query.filter_by(
            user_id=self.id,
            warehouse_id=warehouse_id
        ).first()
        
        if not user_access:
            return False
            
        user_level_num = access_levels.get(user_access.access_level, 1)
        return user_level_num >= required_level_num

    def should_clear_previous_anomalies(self):
        """Check if user preference is to clear previous anomalies on new analysis"""
        return self.clear_previous_anomalies

    def should_show_clear_warning(self):
        """Check if user wants to see the clear warning modal"""
        return self.show_clear_warning

    def get_unresolved_anomaly_count(self):
        """Get count of unresolved anomalies for this user"""
        from sqlalchemy import and_
        count = db.session.query(Anomaly).join(AnalysisReport).filter(
            and_(
                AnalysisReport.user_id == self.id,
                Anomaly.status != 'Resolved',
                Anomaly.status != 'Cleared'  # Also exclude cleared anomalies
            )
        ).count()
        return count

    def update_analysis_preferences(self, clear_previous=None, show_warning=None):
        """Update user's analysis preferences"""
        if clear_previous is not None:
            self.clear_previous_anomalies = clear_previous
        if show_warning is not None:
            self.show_clear_warning = show_warning
        db.session.commit()

class AnalysisReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(120), nullable=False, default=f"Analysis Report")
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anomalies = db.relationship('Anomaly', backref='report', lazy=True, cascade="all, delete-orphan")
    location_summary = db.Column(db.Text, nullable=True) # Stores a JSON string of the location summary
    inventory_count = db.Column(db.Integer, nullable=True) # Total number of pallets/items in the uploaded inventory file
    warehouse_id = db.Column(db.String(50), nullable=True) # Warehouse used for this analysis (for capacity calculations)
    template_id = db.Column(db.Integer, nullable=True) # Template ID used for this analysis (audit trail)

class Anomaly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True) # Could store JSON or other details
    report_id = db.Column(db.Integer, db.ForeignKey('analysis_report.id'), nullable=False)
    status = db.Column(db.String(20), default='New', nullable=False)
    history = db.relationship('AnomalyHistory', backref='anomaly', lazy='dynamic', cascade="all, delete-orphan")

class AnomalyHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anomaly_id = db.Column(db.Integer, db.ForeignKey('anomaly.id'), nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class UserWarehouseAccess(db.Model):
    """
    LONG-TERM SOLUTION: Explicit user-warehouse associations
    Replaces username-based warehouse detection with proper permissions
    """
    __tablename__ = 'user_warehouse_access'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    warehouse_id = db.Column(db.String(50), nullable=False)
    access_level = db.Column(db.String(20), default='READ')  # READ, WRITE, ADMIN
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for performance
    __table_args__ = (
        db.Index('idx_user_warehouse', 'user_id', 'warehouse_id'),
        db.Index('idx_user_default', 'user_id', 'is_default'),
        db.UniqueConstraint('user_id', 'warehouse_id', name='uq_user_warehouse'),
    )

    def __repr__(self):
        return f'<UserWarehouseAccess {self.user_id}:{self.warehouse_id}({self.access_level})>'


class InvitationCode(db.Model):
    """
    Invitation-only registration system
    Controls user registration through invitation codes
    """
    __tablename__ = 'invitation_code'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    used_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    used_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    max_uses = db.Column(db.Integer, default=1, nullable=False)
    current_uses = db.Column(db.Integer, default=0, nullable=False)
    expires_at = db.Column(db.DateTime)  # Optional expiration
    notes = db.Column(db.String(255))  # Optional notes about the invitation

    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_invitations')
    user = db.relationship('User', foreign_keys=[used_by], backref='used_invitation')

    # Indexes for performance
    __table_args__ = (
        db.Index('idx_invitation_code_active', 'code', 'is_active'),
        db.Index('idx_invitation_created_by', 'created_by'),
    )

    def is_valid(self):
        """Check if invitation code is still valid"""
        if not self.is_active:
            return False, "Invitation code is inactive"

        if self.current_uses >= self.max_uses:
            return False, "Invitation code has reached maximum uses"

        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False, "Invitation code has expired"

        return True, "Valid"

    def use_code(self, user_id):
        """Mark invitation as used by a user"""
        self.current_uses += 1
        self.used_by = user_id
        self.used_at = datetime.utcnow()

        # Auto-deactivate if max uses reached
        if self.current_uses >= self.max_uses:
            self.is_active = False

    def to_dict(self):
        """Convert to dictionary for API responses"""
        is_valid, message = self.is_valid()
        return {
            'id': self.id,
            'code': self.code,
            'is_active': self.is_active,
            'is_valid': is_valid,
            'validation_message': message,
            'max_uses': self.max_uses,
            'current_uses': self.current_uses,
            'created_at': self.created_at.isoformat(),
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'creator_username': self.creator.username if self.creator else None,
            'notes': self.notes
        }

    def __repr__(self):
        return f'<InvitationCode {self.code} ({self.current_uses}/{self.max_uses})>'