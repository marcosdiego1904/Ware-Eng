"""
Database Migration Script for Warehouse Rules System
Implementation Plan Phase 1: Database Foundation

This script handles:
1. Creating new database tables for the rules system
2. Migrating existing Excel rules to database
3. Seeding default rules and categories
4. Backing up existing data
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from flask import Flask

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app and database
from app import app, User, AnalysisReport, Anomaly, AnomalyHistory
from database import db
from models import (
    RuleCategory, Rule, RuleHistory, RuleTemplate, 
    RulePerformance, Location, create_default_categories, 
    get_default_rules_data
)

class DatabaseMigrator:
    """
    Handles the migration from Excel-based rules to database-driven system
    """
    
    def __init__(self):
        self.app = app
        self.db = db
        self.backup_data = {}
        
    def backup_existing_data(self):
        """
        Create backup of existing analysis reports and anomalies
        """
        print("Creating backup of existing data...")
        
        with self.app.app_context():
            # Backup users
            users = User.query.all()
            self.backup_data['users'] = [
                {
                    'id': u.id,
                    'username': u.username,
                    'password_hash': u.password_hash
                } for u in users
            ]
            
            # Backup reports
            reports = AnalysisReport.query.all()
            self.backup_data['reports'] = [
                {
                    'id': r.id,
                    'report_name': r.report_name,
                    'timestamp': r.timestamp.isoformat(),
                    'user_id': r.user_id,
                    'location_summary': r.location_summary
                } for r in reports
            ]
            
            # Backup anomalies
            anomalies = Anomaly.query.all()
            self.backup_data['anomalies'] = [
                {
                    'id': a.id,
                    'description': a.description,
                    'details': a.details,
                    'report_id': a.report_id,
                    'status': a.status
                } for a in anomalies
            ]
            
            # Backup anomaly history
            history = AnomalyHistory.query.all()
            self.backup_data['anomaly_history'] = [
                {
                    'id': h.id,
                    'anomaly_id': h.anomaly_id,
                    'old_status': h.old_status,
                    'new_status': h.new_status,
                    'comment': h.comment,
                    'user_id': h.user_id,
                    'timestamp': h.timestamp.isoformat()
                } for h in history
            ]
        
        # Save backup to file
        backup_filename = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(os.path.dirname(__file__), '..', 'backups', backup_filename)
        
        # Create backups directory if it doesn't exist
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        with open(backup_path, 'w') as f:
            json.dump(self.backup_data, f, indent=2)
        
        print(f"Backup created: {backup_path}")
        return backup_path
    
    def create_new_tables(self):
        """
        Create all new tables for the rules system
        """
        print("Creating new database tables...")
        
        with self.app.app_context():
            # Create all new tables
            db.create_all()
            
            # Add new columns to existing tables if needed
            try:
                # Add rule_id to anomaly table if it doesn't exist
                with db.engine.connect() as conn:
                    # Check if rule_id column exists in anomaly table
                    if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
                        result = conn.execute(text("""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name='anomaly' AND column_name='rule_id'
                        """))
                        if not result.fetchone():
                            conn.execute(text("ALTER TABLE anomaly ADD COLUMN rule_id INTEGER"))
                            conn.execute(text("ALTER TABLE anomaly ADD CONSTRAINT fk_anomaly_rule FOREIGN KEY (rule_id) REFERENCES rule(id)"))
                    else:
                        # SQLite approach
                        try:
                            conn.execute(text("ALTER TABLE anomaly ADD COLUMN rule_id INTEGER"))
                        except Exception:
                            # Column might already exist
                            pass
                    
                    # Add rules_used to analysis_report table
                    if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
                        result = conn.execute(text("""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name='analysis_report' AND column_name='rules_used'
                        """))
                        if not result.fetchone():
                            conn.execute(text("ALTER TABLE analysis_report ADD COLUMN rules_used TEXT"))
                    else:
                        # SQLite approach
                        try:
                            conn.execute(text("ALTER TABLE analysis_report ADD COLUMN rules_used TEXT"))
                        except Exception:
                            # Column might already exist
                            pass
                    
                    conn.commit()
                    
            except Exception as e:
                print(f"⚠️  Warning: Could not add new columns: {e}")
        
        print("✅ New database tables created successfully")
    
    def create_default_categories(self):
        """
        Create the Three Pillars Framework categories
        """
        print("📂 Creating default rule categories...")
        
        with self.app.app_context():
            categories = create_default_categories()
            print(f"✅ Created {len(categories)} rule categories")
            return categories
    
    def create_default_rules(self):
        """
        Create the default rules package
        """
        print("⚙️  Creating default rules...")
        
        with self.app.app_context():
            # Get default admin user (first user or create one)
            admin_user = User.query.first()
            if not admin_user:
                admin_user = User(username='system_admin')
                admin_user.set_password('admin123')  # Temporary password
                db.session.add(admin_user)
                db.session.flush()
            
            rules_data = get_default_rules_data()
            created_rules = []
            
            for rule_data in rules_data:
                # Get category
                category = RuleCategory.query.filter_by(name=rule_data['category']).first()
                if not category:
                    print(f"⚠️  Warning: Category {rule_data['category']} not found")
                    continue
                
                # Check if rule already exists
                existing_rule = Rule.query.filter_by(
                    name=rule_data['name'],
                    rule_type=rule_data['rule_type']
                ).first()
                
                if existing_rule:
                    print(f"⏭️  Skipping existing rule: {rule_data['name']}")
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
                
                print(f"✅ Created rule: {rule_data['name']}")
            
            db.session.commit()
            print(f"✅ Created {len(created_rules)} default rules")
            return created_rules
    
    def migrate_excel_rules(self):
        """
        Migrate existing warehouse_rules.xlsx to database locations
        """
        print("📊 Migrating Excel rules to database...")
        
        excel_rules_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'warehouse_rules.xlsx'
        )
        
        if not os.path.exists(excel_rules_path):
            print(f"⚠️  Warning: Excel rules file not found: {excel_rules_path}")
            return []
        
        try:
            rules_df = pd.read_excel(excel_rules_path)
            print(f"📖 Found {len(rules_df)} rules in Excel file")
            
            with self.app.app_context():
                created_locations = []
                
                for index, rule in rules_df.iterrows():
                    # Check if location already exists
                    existing_location = Location.query.filter_by(
                        code=rule['location_pattern']
                    ).first()
                    
                    if existing_location:
                        continue
                    
                    # Create new location
                    location = Location(
                        code=rule['location_pattern'],
                        pattern=rule['location_pattern'],
                        location_type=rule['location_type'],
                        capacity=int(rule['capacity']) if pd.notna(rule['capacity']) else 1,
                        zone=rule.get('zone', 'GENERAL')
                    )
                    
                    # Set allowed products if available
                    if pd.notna(rule.get('allowed_description')):
                        location.set_allowed_products([rule['allowed_description']])
                    
                    db.session.add(location)
                    created_locations.append(location)
                    
                    print(f"✅ Migrated location: {rule['location_pattern']}")
                
                db.session.commit()
                print(f"✅ Migrated {len(created_locations)} locations from Excel")
                return created_locations
                
        except Exception as e:
            print(f"❌ Error migrating Excel rules: {e}")
            return []
    
    def create_sample_templates(self):
        """
        Create sample rule templates for user convenience
        """
        print("📋 Creating sample rule templates...")
        
        with self.app.app_context():
            admin_user = User.query.first()
            if not admin_user:
                return []
            
            templates_data = [
                {
                    'name': 'Simple Time-based Rule',
                    'description': 'Template for creating time-based anomaly detection rules',
                    'category': 'FLOW_TIME',
                    'template_conditions': {
                        'location_types': ['{{location_type}}'],
                        'time_threshold_hours': '{{time_threshold}}'
                    },
                    'parameters_schema': {
                        'location_type': {'type': 'select', 'options': ['RECEIVING', 'TRANSITIONAL', 'FINAL']},
                        'time_threshold': {'type': 'integer', 'min': 1, 'max': 48, 'default': 8}
                    }
                },
                {
                    'name': 'Capacity-based Rule',
                    'description': 'Template for creating capacity-related rules',
                    'category': 'SPACE',
                    'template_conditions': {
                        'check_all_locations': True,
                        'capacity_threshold': '{{capacity_threshold}}'
                    },
                    'parameters_schema': {
                        'capacity_threshold': {'type': 'float', 'min': 0.5, 'max': 1.0, 'default': 1.0}
                    }
                }
            ]
            
            created_templates = []
            
            for template_data in templates_data:
                category = RuleCategory.query.filter_by(name=template_data['category']).first()
                if not category:
                    continue
                
                template = RuleTemplate(
                    name=template_data['name'],
                    description=template_data['description'],
                    category_id=category.id,
                    is_public=True,
                    created_by=admin_user.id
                )
                
                template.template_conditions = json.dumps(template_data['template_conditions'])
                template.parameters_schema = json.dumps(template_data['parameters_schema'])
                
                db.session.add(template)
                created_templates.append(template)
                
                print(f"✅ Created template: {template_data['name']}")
            
            db.session.commit()
            print(f"✅ Created {len(created_templates)} rule templates")
            return created_templates
    
    def verify_migration(self):
        """
        Verify that the migration was successful
        """
        print("🔍 Verifying migration...")
        
        with self.app.app_context():
            # Check categories
            categories_count = RuleCategory.query.count()
            print(f"📂 Rule categories: {categories_count}")
            
            # Check rules
            rules_count = Rule.query.count()
            default_rules_count = Rule.query.filter_by(is_default=True).count()
            print(f"⚙️  Total rules: {rules_count} ({default_rules_count} default)")
            
            # Check locations
            locations_count = Location.query.count()
            print(f"📍 Locations: {locations_count}")
            
            # Check templates
            templates_count = RuleTemplate.query.count()
            print(f"📋 Rule templates: {templates_count}")
            
            # Check existing data integrity
            reports_count = AnalysisReport.query.count()
            anomalies_count = Anomaly.query.count()
            print(f"📊 Existing reports: {reports_count}")
            print(f"⚠️  Existing anomalies: {anomalies_count}")
            
            if categories_count >= 3 and rules_count >= 8:
                print("✅ Migration verification successful!")
                return True
            else:
                print("❌ Migration verification failed!")
                return False
    
    def run_full_migration(self):
        """
        Execute the complete migration process
        """
        print("🚀 Starting Warehouse Rules System Migration")
        print("=" * 50)
        
        try:
            # Step 1: Backup existing data
            backup_path = self.backup_existing_data()
            
            # Step 2: Create new tables
            self.create_new_tables()
            
            # Step 3: Create default categories
            self.create_default_categories()
            
            # Step 4: Create default rules
            self.create_default_rules()
            
            # Step 5: Migrate Excel rules to locations
            self.migrate_excel_rules()
            
            # Step 6: Create sample templates
            self.create_sample_templates()
            
            # Step 7: Verify migration
            success = self.verify_migration()
            
            if success:
                print("\n✅ MIGRATION COMPLETED SUCCESSFULLY!")
                print(f"📁 Backup saved to: {backup_path}")
                print("\n🎯 Next Steps:")
                print("1. Test the new rules system in the frontend")
                print("2. Verify existing analysis reports still work")
                print("3. Create your first custom rule using the new system")
            else:
                print("\n❌ MIGRATION COMPLETED WITH WARNINGS!")
                print("Please check the verification results above.")
            
            return success
            
        except Exception as e:
            print(f"\n❌ MIGRATION FAILED: {e}")
            print("Your original data should be safe.")
            print(f"Backup location: {backup_path if 'backup_path' in locals() else 'Not created'}")
            return False

def main():
    """
    Main function to run the migration
    """
    print("Warehouse Rules System Database Migration")
    print("This will add new tables and migrate existing data.")
    print("Your existing data will be backed up before any changes.")
    
    # Confirmation
    confirm = input("\nDo you want to proceed? (yes/no): ").lower().strip()
    if confirm not in ['yes', 'y']:
        print("Migration cancelled.")
        return
    
    # Create migrator and run
    migrator = DatabaseMigrator()
    success = migrator.run_full_migration()
    
    if success:
        print("\n🎉 Ready to start using the new rules system!")
    else:
        print("\n⚠️  Please check the errors above and try again.")

if __name__ == '__main__':
    main()