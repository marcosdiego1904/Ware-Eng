#!/usr/bin/env python3
"""
Script to update user analysis limits
"""
import sys
import os
sys.path.append('src')

from database import db
from core_models import User
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Add the new column if it doesn't exist
    try:
        db.engine.execute('ALTER TABLE user ADD COLUMN analysis_limit INTEGER DEFAULT 10')
        print("Added analysis_limit column to user table")
    except Exception as e:
        print(f"Column may already exist: {e}")
    
    # Update testf user
    user = User.query.filter_by(username='testf').first()
    if user:
        user.analysis_limit = 999999  # Infinite permits
        db.session.commit()
        print(f'Updated user {user.username} - Analysis limit: {user.analysis_limit}')
    else:
        print('User testf not found')
        # List all users
        users = User.query.all()
        print('Available users:')
        for u in users:
            print(f'  - {u.username}')