"""
Database configuration module to avoid circular imports
"""
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance
db = SQLAlchemy()