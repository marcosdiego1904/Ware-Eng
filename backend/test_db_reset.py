"""
Test script to simulate database deletion and verify auto-recreation of bootstrap code
This demonstrates the solution to your problem
"""
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set required environment variable
os.environ['FLASK_SECRET_KEY'] = 'test-key-for-verification'

def test_database_reset():
    """Simulate deleting the database and checking if bootstrap code is recreated"""

    print("\n" + "="*60)
    print("DATABASE RESET SIMULATION TEST")
    print("="*60 + "\n")

    # Step 1: Check if bootstrap code exists
    print("Step 1: Checking if bootstrap code currently exists...")
    from app import app, db
    from core_models import InvitationCode

    with app.app_context():
        bootstrap = InvitationCode.query.filter_by(code='BOOTSTRAP2025').first()
        if bootstrap:
            print("[OK] Bootstrap code found in current database")
            print(f"    Code: {bootstrap.code}")
            print(f"    Created at: {bootstrap.created_at}")
        else:
            print("[INFO] Bootstrap code not found (will be created)")

    # Step 2: Simulate database deletion
    print("\nStep 2: Simulating database deletion...")
    print("[INFO] In real scenario, you would run: del instance\\database.db")
    print("[INFO] For this test, we'll drop and recreate tables")

    with app.app_context():
        # Drop all tables (simulates database deletion)
        db.drop_all()
        print("[OK] All tables dropped (database deleted)")

        # Recreate tables
        db.create_all()
        print("[OK] Tables recreated (empty database)")

        # Check if bootstrap code exists (it shouldn't yet)
        bootstrap = InvitationCode.query.filter_by(code='BOOTSTRAP2025').first()
        if bootstrap:
            print("[UNEXPECTED] Bootstrap code still exists after deletion!")
        else:
            print("[OK] Bootstrap code not found (as expected after deletion)")

    # Step 3: Run initialization (this happens automatically when you start the server)
    print("\nStep 3: Running database initialization (happens automatically on server start)...")
    from db_init import init_database

    with app.app_context():
        init_database()

    # Step 4: Verify bootstrap code was created
    print("\nStep 4: Verifying bootstrap code was recreated...")

    with app.app_context():
        bootstrap = InvitationCode.query.filter_by(code='BOOTSTRAP2025').first()

        if bootstrap:
            print("\n" + "="*60)
            print("[SUCCESS] BOOTSTRAP CODE RECREATED AUTOMATICALLY!")
            print("="*60)
            print(f"\nCode details:")
            print(f"  Code: {bootstrap.code}")
            print(f"  Max uses: {bootstrap.max_uses}")
            print(f"  Current uses: {bootstrap.current_uses}")
            print(f"  Is active: {bootstrap.is_active}")
            print(f"  Created at: {bootstrap.created_at}")
            is_valid, message = bootstrap.is_valid()
            print(f"  Is valid: {is_valid} - {message}")
            print("\n" + "="*60)
            print("SOLUTION VERIFIED: You can now delete the database")
            print("and the BOOTSTRAP2025 code will be recreated automatically")
            print("when you start the backend server!")
            print("="*60 + "\n")
        else:
            print("\n[FAILED] Bootstrap code was not recreated!")
            print("This shouldn't happen - please check the db_init.py file\n")

if __name__ == '__main__':
    test_database_reset()
