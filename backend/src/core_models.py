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

class AnalysisReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(120), nullable=False, default=f"Analysis Report")
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anomalies = db.relationship('Anomaly', backref='report', lazy=True, cascade="all, delete-orphan")
    location_summary = db.Column(db.Text, nullable=True) # Stores a JSON string of the location summary

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