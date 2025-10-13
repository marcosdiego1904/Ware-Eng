"""
Create test user in PostgreSQL database
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from core_models import User, InvitationCode

def create_test_user():
    """Create a test user for testing"""
    with app.app_context():
        print("=" * 70)
        print("Creating Test User")
        print("=" * 70)
        print()

        # Check if user exists
        test_user = User.query.filter_by(username='testuser').first()

        if test_user:
            print("[INFO] Test user 'testuser' already exists")
            print(f"   ID: {test_user.id}")
            print(f"   Username: {test_user.username}")
        else:
            # Create test user
            test_user = User(username='testuser')
            test_user.set_password('testpassword123')
            db.session.add(test_user)
            db.session.commit()

            print("[OK] Created test user:")
            print(f"   Username: testuser")
            print(f"   Password: testpassword123")
            print(f"   ID: {test_user.id}")

        print()
        print("=" * 70)
        print("Test Credentials:")
        print("=" * 70)
        print("Username: testuser")
        print("Password: testpassword123")
        print()
        print("Invitation Code (for registration): BOOTSTRAP2025")
        print()
        print("=" * 70)
        print()
        print("You can now:")
        print("1. Start the Flask server: python run_server.py")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Login at http://localhost:3000")
        print()

if __name__ == "__main__":
    create_test_user()
