"""
Create Demo User for Customer Presentations
Generates a professional demo account with enhanced limits and monitoring
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from core_models import User, InvitationCode
from sqlalchemy import text

def create_demo_user(customer_name: str, email: str = None, password: str = "Demo2025!"):
    """
    Create a demo user account for customer presentations

    Args:
        customer_name: Name of the customer/company (e.g., "Acme Corp")
        email: Optional email for reference
        password: Default password (should be changed by customer)
    """
    with app.app_context():
        print("=" * 60)
        print("DEMO USER CREATION TOOL")
        print("=" * 60)

        # Generate username from customer name
        username_base = customer_name.lower().replace(' ', '_').replace('-', '_')
        username = f"demo_{username_base}"

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"\n⚠️  User '{username}' already exists!")
            print(f"   User ID: {existing_user.id}")
            print(f"   Max Reports: {existing_user.max_reports}")
            print(f"   Max Templates: {existing_user.max_templates}")

            response = input("\nDo you want to update this user? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return None

            user = existing_user
            print(f"\n✓ Updating existing user...")
        else:
            # Create new user
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            print(f"\n✓ Creating new user: {username}")

        # Set enhanced limits for demo accounts
        user.max_reports = 10  # Higher limit for demos
        user.max_templates = 10  # Higher limit for demos

        # Add metadata if available (using JSON in a note field)
        # Note: You might want to add a notes field to User model in the future

        db.session.commit()
        db.session.refresh(user)

        print("\n" + "=" * 60)
        print("✓ DEMO USER CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nCustomer: {customer_name}")
        if email:
            print(f"Email: {email}")
        print(f"\nCredentials:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"  User ID: {user.id}")
        print(f"\nLimits:")
        print(f"  Max Reports: {user.max_reports}")
        print(f"  Max Templates: {user.max_templates}")
        print(f"\nCreated: {datetime.utcnow().isoformat()}")
        print("\n" + "=" * 60)
        print("IMPORTANT: Share these credentials securely!")
        print("Recommend customer changes password after first login.")
        print("=" * 60)

        return user


def create_demo_invitation(customer_name: str, max_uses: int = 1):
    """
    Create a custom invitation code for a specific customer
    """
    with app.app_context():
        # Generate customer-specific code
        code_base = customer_name.upper().replace(' ', '').replace('-', '')[:8]
        code = f"{code_base}DEMO"

        # Check if code exists
        existing = InvitationCode.query.filter_by(code=code).first()
        if existing:
            print(f"\n⚠️  Invitation code '{code}' already exists")
            print(f"   Current uses: {existing.current_uses}/{existing.max_uses}")
            return existing

        # Create invitation
        invitation = InvitationCode(
            code=code,
            created_by=None,  # System-generated
            max_uses=max_uses,
            notes=f"Demo invitation for {customer_name}"
        )

        db.session.add(invitation)
        db.session.commit()

        print(f"\n✓ Invitation code created: {code}")
        print(f"  Max uses: {max_uses}")

        return invitation


def list_demo_users():
    """List all demo users"""
    with app.app_context():
        demo_users = User.query.filter(User.username.like('demo_%')).all()

        if not demo_users:
            print("\nNo demo users found.")
            return

        print("\n" + "=" * 60)
        print("DEMO USERS")
        print("=" * 60)

        for user in demo_users:
            print(f"\nUsername: {user.username}")
            print(f"  User ID: {user.id}")
            print(f"  Max Reports: {user.max_reports}")
            print(f"  Max Templates: {user.max_templates}")

            # Get usage stats
            from core_models import AnalysisReport
            from models import WarehouseTemplate

            report_count = AnalysisReport.query.filter_by(user_id=user.id).count()
            template_count = WarehouseTemplate.query.filter_by(
                created_by=user.id,
                is_active=True
            ).count()

            print(f"  Current Reports: {report_count}/{user.max_reports}")
            print(f"  Current Templates: {template_count}/{user.max_templates}")


def interactive_mode():
    """Interactive demo user creation"""
    print("\n" + "=" * 60)
    print("DEMO USER CREATION - INTERACTIVE MODE")
    print("=" * 60)

    customer_name = input("\nEnter customer/company name: ").strip()
    if not customer_name:
        print("Error: Customer name is required")
        return

    email = input("Enter email (optional, press Enter to skip): ").strip()

    password = input("Enter password (press Enter for default 'Demo2025!'): ").strip()
    if not password:
        password = "Demo2025!"

    print("\n" + "-" * 60)
    print("REVIEW:")
    print(f"  Customer: {customer_name}")
    if email:
        print(f"  Email: {email}")
    print(f"  Username: demo_{customer_name.lower().replace(' ', '_')}")
    print(f"  Password: {password}")
    print(f"  Limits: 10 reports, 10 templates")
    print("-" * 60)

    confirm = input("\nCreate this user? (y/n): ")
    if confirm.lower() == 'y':
        user = create_demo_user(customer_name, email, password)
        if user:
            print("\n✓ Demo user created successfully!")
    else:
        print("Cancelled.")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'list':
            list_demo_users()
        elif command == 'create':
            if len(sys.argv) < 3:
                print("Usage: python create_demo_user.py create <customer_name> [email] [password]")
                sys.exit(1)

            customer_name = sys.argv[2]
            email = sys.argv[3] if len(sys.argv) > 3 else None
            password = sys.argv[4] if len(sys.argv) > 4 else "Demo2025!"

            create_demo_user(customer_name, email, password)
        elif command == 'invite':
            if len(sys.argv) < 3:
                print("Usage: python create_demo_user.py invite <customer_name> [max_uses]")
                sys.exit(1)

            customer_name = sys.argv[2]
            max_uses = int(sys.argv[3]) if len(sys.argv) > 3 else 1

            create_demo_invitation(customer_name, max_uses)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: create, list, invite")
            sys.exit(1)
    else:
        # Interactive mode
        interactive_mode()
