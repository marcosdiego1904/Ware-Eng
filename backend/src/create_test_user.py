#!/usr/bin/env python3
"""
Create a test user for development and testing
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import app
from database import db
from core_models import User

def create_test_user():
    """Create a test user for authentication"""
    
    print("Creating test user...")
    
    with app.app_context():
        try:
            # Check if test user already exists
            existing_user = User.query.filter_by(username='testuser').first()
            
            if existing_user:
                print("Test user 'testuser' already exists")
                return True
            
            # Create new test user
            test_user = User(username='testuser')
            test_user.set_password('testpass123')
            
            db.session.add(test_user)
            db.session.commit()
            
            print("Test user created successfully!")
            print("Username: testuser")
            print("Password: testpass123")
            
            return True
            
        except Exception as e:
            print(f"Error creating test user: {str(e)}")
            return False

if __name__ == "__main__":
    success = create_test_user()
    if success:
        print("User creation completed successfully!")
        sys.exit(0)
    else:
        print("User creation failed!")
        sys.exit(1)