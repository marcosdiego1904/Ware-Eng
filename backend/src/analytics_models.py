"""
Analytics Models for Pilot Program Monitoring
Tracks usage, business, and technical metrics for ROI analysis
"""

from datetime import datetime
from database import db
import json


class AnalyticsEvent(db.Model):
    """
    Track all user actions and interactions
    Used for feature usage analysis and user journey tracking
    """
    __tablename__ = 'analytics_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse_config.id'), nullable=True, index=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)

    # Event classification
    event_type = db.Column(db.String(50), nullable=False, index=True)  # login, file_upload, rule_execution, etc.
    event_category = db.Column(db.String(50), nullable=False)  # usage, business, technical
    event_action = db.Column(db.String(100), nullable=False)  # clicked, uploaded, generated, etc.

    # Event data stored as JSON for flexibility
    event_data = db.Column(db.JSON, nullable=True)  # {file_size: 5.2, rule_type: "expiry_check", etc.}

    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = db.relationship('User', backref='analytics_events')
    warehouse = db.relationship('WarehouseConfig', backref='analytics_events')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'warehouse_id': self.warehouse_id,
            'session_id': self.session_id,
            'event_type': self.event_type,
            'event_category': self.event_category,
            'event_action': self.event_action,
            'event_data': self.event_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AnalyticsSession(db.Model):
    """
    Track user login sessions and time spent in app
    Used for login frequency and engagement metrics
    """
    __tablename__ = 'analytics_sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse_config.id'), nullable=True)

    # Session timing
    login_time = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    logout_time = db.Column(db.DateTime(timezone=True), nullable=True)
    last_activity = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    duration_minutes = db.Column(db.Float, nullable=True)  # Calculated on logout

    # Session metadata
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 max length
    user_agent = db.Column(db.String(500), nullable=True)
    browser = db.Column(db.String(50), nullable=True)
    device_type = db.Column(db.String(50), nullable=True)  # desktop, mobile, tablet

    # Relationships
    user = db.relationship('User', backref='sessions')
    warehouse = db.relationship('WarehouseConfig', backref='sessions')

    def calculate_duration(self):
        """Calculate session duration in minutes"""
        if self.logout_time and self.login_time:
            delta = self.logout_time - self.login_time
            self.duration_minutes = delta.total_seconds() / 60
        return self.duration_minutes

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'warehouse_id': self.warehouse_id,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'logout_time': self.logout_time.isoformat() if self.logout_time else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'duration_minutes': self.duration_minutes,
            'browser': self.browser,
            'device_type': self.device_type
        }


class AnalyticsFileUpload(db.Model):
    """
    Track file upload performance and success rates
    Used for technical metrics and reliability analysis
    """
    __tablename__ = 'analytics_file_uploads'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse_config.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=False)

    # File details
    file_type = db.Column(db.String(20), nullable=False)  # inventory, rules
    file_name = db.Column(db.String(255), nullable=True)
    file_size_mb = db.Column(db.Float, nullable=True)

    # Processing metrics
    processing_time_seconds = db.Column(db.Float, nullable=True)
    success = db.Column(db.Boolean, default=False, nullable=False)
    error_message = db.Column(db.Text, nullable=True)

    # Analysis results
    columns_detected = db.Column(db.Integer, nullable=True)
    rows_processed = db.Column(db.Integer, nullable=True)
    anomalies_found = db.Column(db.Integer, nullable=True)

    # Timestamps
    uploaded_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = db.relationship('User', backref='file_uploads')
    warehouse = db.relationship('WarehouseConfig', backref='file_uploads')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'warehouse_id': self.warehouse_id,
            'file_type': self.file_type,
            'file_name': self.file_name,
            'file_size_mb': self.file_size_mb,
            'processing_time_seconds': self.processing_time_seconds,
            'success': self.success,
            'error_message': self.error_message,
            'columns_detected': self.columns_detected,
            'rows_processed': self.rows_processed,
            'anomalies_found': self.anomalies_found,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class AnalyticsAnomaly(db.Model):
    """
    Track anomaly detection and resolution for business impact metrics
    Links to existing Anomaly model for details
    """
    __tablename__ = 'analytics_anomalies'

    id = db.Column(db.Integer, primary_key=True)
    anomaly_id = db.Column(db.Integer, db.ForeignKey('anomaly.id'), nullable=False, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse_config.id'), nullable=True)

    # Detection details
    detected_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=True)  # critical, high, medium, low
    rule_type = db.Column(db.String(100), nullable=False, index=True)  # expiry_check, space_usage, etc.

    # Resolution tracking
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    time_to_resolve_hours = db.Column(db.Float, nullable=True)
    user_action = db.Column(db.String(50), nullable=True)  # dismissed, fixed, escalated, ignored

    # Business impact
    potential_cost_impact = db.Column(db.Float, nullable=True)  # Estimated $ saved by catching this
    impact_category = db.Column(db.String(50), nullable=True)  # inventory_loss, space_waste, compliance, etc.

    # Relationships
    anomaly = db.relationship('Anomaly', backref='analytics')
    user = db.relationship('User', backref='anomaly_analytics')
    warehouse = db.relationship('WarehouseConfig', backref='anomaly_analytics')

    def calculate_resolution_time(self):
        """Calculate time to resolve in hours"""
        if self.resolved_at and self.detected_at:
            delta = self.resolved_at - self.detected_at
            self.time_to_resolve_hours = delta.total_seconds() / 3600
        return self.time_to_resolve_hours

    def to_dict(self):
        return {
            'id': self.id,
            'anomaly_id': self.anomaly_id,
            'user_id': self.user_id,
            'warehouse_id': self.warehouse_id,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'severity': self.severity,
            'rule_type': self.rule_type,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'time_to_resolve_hours': self.time_to_resolve_hours,
            'user_action': self.user_action,
            'potential_cost_impact': self.potential_cost_impact,
            'impact_category': self.impact_category
        }


class AnalyticsTimeSavings(db.Model):
    """
    Aggregate time savings calculations for ROI reporting
    Compares automated processing time vs. estimated manual time
    """
    __tablename__ = 'analytics_time_savings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse_config.id'), nullable=True)

    # Date aggregation
    date = db.Column(db.Date, nullable=False, index=True)

    # Activity counts
    files_processed = db.Column(db.Integer, default=0, nullable=False)
    reports_generated = db.Column(db.Integer, default=0, nullable=False)
    anomalies_detected = db.Column(db.Integer, default=0, nullable=False)

    # Time tracking (in seconds for precision)
    automated_time_seconds = db.Column(db.Float, default=0, nullable=False)
    estimated_manual_time_seconds = db.Column(db.Float, default=0, nullable=False)
    time_saved_minutes = db.Column(db.Float, nullable=True)  # Calculated field

    # Cost metrics
    estimated_cost_savings = db.Column(db.Float, nullable=True)  # Based on hourly rate

    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref='time_savings')
    warehouse = db.relationship('WarehouseConfig', backref='time_savings')

    # Unique constraint: one record per user per warehouse per date
    __table_args__ = (
        db.UniqueConstraint('user_id', 'warehouse_id', 'date', name='unique_user_warehouse_date'),
    )

    def calculate_savings(self, hourly_rate=50.0):
        """
        Calculate time and cost savings

        Args:
            hourly_rate: Dollar amount per hour of labor (default $50/hr)
        """
        time_saved_seconds = self.estimated_manual_time_seconds - self.automated_time_seconds
        self.time_saved_minutes = time_saved_seconds / 60

        # Calculate cost savings
        time_saved_hours = time_saved_seconds / 3600
        self.estimated_cost_savings = time_saved_hours * hourly_rate

        return {
            'time_saved_minutes': self.time_saved_minutes,
            'cost_savings': self.estimated_cost_savings
        }

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'warehouse_id': self.warehouse_id,
            'date': self.date.isoformat() if self.date else None,
            'files_processed': self.files_processed,
            'reports_generated': self.reports_generated,
            'anomalies_detected': self.anomalies_detected,
            'automated_time_seconds': self.automated_time_seconds,
            'estimated_manual_time_seconds': self.estimated_manual_time_seconds,
            'time_saved_minutes': self.time_saved_minutes,
            'estimated_cost_savings': self.estimated_cost_savings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
