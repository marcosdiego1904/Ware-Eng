"""
Database Initialization and Seeding
Automatically creates essential data on application startup
"""
from datetime import datetime, timedelta
from database import db
from core_models import InvitationCode

def init_bootstrap_invitation_code():
    """
    Create the bootstrap invitation code if it doesn't exist
    This allows the first user to register during development
    """
    BOOTSTRAP_CODE = 'BOOTSTRAP2025'

    # Check if the bootstrap code already exists
    existing_code = InvitationCode.query.filter_by(code=BOOTSTRAP_CODE).first()

    if existing_code:
        print(f"[OK] Bootstrap invitation code '{BOOTSTRAP_CODE}' already exists")
        return existing_code

    # Create the bootstrap invitation code
    bootstrap_invitation = InvitationCode(
        code=BOOTSTRAP_CODE,
        created_by=None,  # System-created, no user
        max_uses=999,     # Allow multiple uses for development
        expires_at=None,  # Never expires
        notes='Bootstrap invitation code for initial user registration',
        is_active=True
    )

    db.session.add(bootstrap_invitation)
    db.session.commit()

    print(f"[OK] Created bootstrap invitation code: {BOOTSTRAP_CODE}")
    print(f"     Max uses: {bootstrap_invitation.max_uses}")
    print(f"     Never expires")

    return bootstrap_invitation


def init_database():
    """
    Initialize database with essential data
    This runs automatically on application startup
    """
    print("\n=== Database Initialization ===")

    try:
        # Create bootstrap invitation code
        init_bootstrap_invitation_code()

        print("=== Database Initialization Complete ===\n")
        return True

    except Exception as e:
        print(f"[ERROR] Database initialization failed: {str(e)}")
        return False


def seed_development_data():
    """
    Optional: Seed additional development data
    Only call this explicitly when needed
    """
    pass
