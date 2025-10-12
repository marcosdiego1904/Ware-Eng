"""
Test script to verify bootstrap invitation code is created automatically
Run this after deleting the database to see the initialization in action
"""
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set required environment variable
os.environ['FLASK_SECRET_KEY'] = 'test-key-for-verification'

from app import app, db
from core_models import InvitationCode

def test_bootstrap_code():
    """Test if bootstrap code exists"""
    with app.app_context():
        # Check if bootstrap code exists
        bootstrap = InvitationCode.query.filter_by(code='BOOTSTRAP2025').first()

        if bootstrap:
            print("[SUCCESS] Bootstrap invitation code exists!")
            print(f"   Code: {bootstrap.code}")
            print(f"   Max uses: {bootstrap.max_uses}")
            print(f"   Current uses: {bootstrap.current_uses}")
            print(f"   Is active: {bootstrap.is_active}")
            print(f"   Created at: {bootstrap.created_at}")
            is_valid, message = bootstrap.is_valid()
            print(f"   Is valid: {is_valid} - {message}")
        else:
            print("[FAILED] Bootstrap invitation code not found!")
            print("   This means the initialization didn't run or failed.")

if __name__ == '__main__':
    test_bootstrap_code()
