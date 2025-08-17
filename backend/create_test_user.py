#!/usr/bin/env python3
"""
Create a test user for API testing
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from core_models import User

def create_test_user():
    """Create test user for API authentication"""
    
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(username='test_user').first()
        
        if existing_user:
            print("Test user already exists")
            return True
            
        # Create test user
        test_user = User(
            username='test_user'
        )
        test_user.set_password('test_pass')
        
        db.session.add(test_user)
        db.session.commit()
        
        print("Test user created successfully")
        print("Username: test_user")
        print("Password: test_pass")
        return True

if __name__ == '__main__':
    create_test_user()