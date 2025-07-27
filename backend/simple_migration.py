"""
Simple Database Migration Script for Warehouse Rules System
"""

import os
import sys
import json

# Set environment variables
os.environ['FLASK_SECRET_KEY'] = 'migration-secret-key-temp'
os.environ['DATABASE_URL'] = ''  # Use SQLite for development

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import Flask app and database
from app import app, db, User

def run_migration():
    print("Starting Warehouse Rules System Migration")
    print("=" * 50)
    
    # Import models before creating tables
    from models import (
        RuleCategory, Rule, RuleHistory, RuleTemplate, 
        RulePerformance, Location, create_default_categories, 
        get_default_rules_data
    )
    
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        print("Creating default categories...")
        categories = create_default_categories()
        print(f"Created {len(categories)} categories")
        
        print("Creating default rules...")
        
        # Get or create admin user
        admin_user = User.query.first()
        if not admin_user:
            admin_user = User(username='system_admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.flush()
        
        rules_data = get_default_rules_data()
        created_rules = []
        
        for rule_data in rules_data:
            # Get category
            category = RuleCategory.query.filter_by(name=rule_data['category']).first()
            if not category:
                print(f"Warning: Category {rule_data['category']} not found")
                continue
            
            # Check if rule already exists
            existing_rule = Rule.query.filter_by(
                name=rule_data['name'],
                rule_type=rule_data['rule_type']
            ).first()
            
            if existing_rule:
                print(f"Skipping existing rule: {rule_data['name']}")
                continue
            
            # Create new rule
            rule = Rule(
                name=rule_data['name'],
                description=rule_data['description'],
                category_id=category.id,
                rule_type=rule_data['rule_type'],
                priority=rule_data['priority'],
                is_default=True,
                is_active=True,
                created_by=admin_user.id
            )
            
            rule.set_conditions(rule_data['conditions'])
            rule.set_parameters(rule_data['parameters'])
            
            db.session.add(rule)
            created_rules.append(rule)
            
            print(f"Created rule: {rule_data['name']}")
        
        db.session.commit()
        print(f"Created {len(created_rules)} default rules")
        
        # Verify migration
        print("\nVerifying migration...")
        categories_count = RuleCategory.query.count()
        rules_count = Rule.query.count()
        print(f"Rule categories: {categories_count}")
        print(f"Total rules: {rules_count}")
        
        if categories_count >= 3 and rules_count >= 8:
            print("Migration completed successfully!")
            return True
        else:
            print("Migration verification failed!")
            return False

if __name__ == '__main__':
    success = run_migration()
    if success:
        print("\nReady to start using the new rules system!")
    else:
        print("\nPlease check the errors above and try again.")