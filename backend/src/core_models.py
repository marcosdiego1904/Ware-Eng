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
    analysis_limit = db.Column(db.Integer, default=10)  # Number of analyses allowed
    reports = db.relationship('AnalysisReport', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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