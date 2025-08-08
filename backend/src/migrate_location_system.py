#!/usr/bin/env python3
"""
Migration script to create the new location management tables
Run this script to set up the enhanced location system
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import app
from database import db
from models import (
    RuleCategory, Rule, RuleHistory, RuleTemplate, RulePerformance,
    Location, WarehouseConfig, WarehouseTemplate,
    create_default_categories
)

def migrate_location_system():
    """Create all new tables and set up default data"""
    
    print("Starting Location Management System Migration")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("All tables created successfully")
            
            # Create default rule categories
            print("\nSetting up default rule categories...")
            created_categories = create_default_categories()
            if created_categories:
                print(f"Created {len(created_categories)} rule categories")
            else:
                print("Rule categories already exist")
            
            # Create default locations for testing (if none exist)
            print("\nChecking for existing locations...")
            existing_locations = Location.query.count()
            
            if existing_locations == 0:
                print("Creating sample warehouse locations...")
                
                # Create basic receiving area
                receiving = Location(
                    code='RECEIVING',
                    location_type='RECEIVING',
                    capacity=10,
                    pallet_capacity=10,
                    zone='DOCK',
                    warehouse_id='DEFAULT',
                    created_by=1  # Assuming user ID 1 exists
                )
                db.session.add(receiving)
                
                # Create a few sample storage locations
                sample_locations = []
                for position in [1, 2, 3, 4, 5]:
                    for level in ['A', 'B']:
                        location = Location.create_from_structure(
                            warehouse_id='DEFAULT',
                            aisle_num=1,
                            rack_num=1,
                            position_num=position,
                            level=level,
                            pallet_capacity=1,
                            zone='GENERAL',
                            location_type='STORAGE',
                            created_by=1
                        )
                        sample_locations.append(location)
                        db.session.add(location)
                
                db.session.commit()
                print(f"Created {len(sample_locations) + 1} sample locations")
            else:
                print(f"Found {existing_locations} existing locations")
            
            # Create sample warehouse config (if none exists)
            print("\nChecking for warehouse configuration...")
            existing_config = WarehouseConfig.query.filter_by(warehouse_id='DEFAULT').first()
            
            if not existing_config:
                print("Creating default warehouse configuration...")
                config = WarehouseConfig(
                    warehouse_id='DEFAULT',
                    warehouse_name='Default Warehouse',
                    num_aisles=4,
                    racks_per_aisle=2,
                    positions_per_rack=50,
                    levels_per_position=4,
                    level_names='ABCD',
                    default_pallet_capacity=1,
                    bidimensional_racks=False,
                    default_zone='GENERAL',
                    position_numbering_start=1,
                    position_numbering_split=True,
                    created_by=1
                )
                
                # Set default receiving areas
                config.set_receiving_areas([
                    {'code': 'RECEIVING', 'type': 'RECEIVING', 'capacity': 10, 'zone': 'DOCK'}
                ])
                
                db.session.add(config)
                db.session.commit()
                print("Created default warehouse configuration")
            else:
                print("Warehouse configuration already exists")
            
            print("\n" + "=" * 60)
            print("Location Management System Migration Complete!")
            print("=" * 60)
            print("\nSummary:")
            print(f"   • Rule Categories: {RuleCategory.query.count()}")
            print(f"   • Rules: {Rule.query.count()}")  
            print(f"   • Locations: {Location.query.count()}")
            print(f"   • Warehouse Configs: {WarehouseConfig.query.count()}")
            print(f"   • Templates: {WarehouseTemplate.query.count()}")
            
            print("\nNext Steps:")
            print("   1. Start the backend server: python run_server.py")
            print("   2. Start the frontend server: npm run dev")
            print("   3. Navigate to Warehouse Settings in the dashboard")
            print("   4. Run the setup wizard to configure your warehouse")
            
            return True
            
        except Exception as e:
            print(f"\nMigration failed: {str(e)}")
            print("Please check your database connection and try again")
            return False

def check_migration_status():
    """Check if migration has already been run"""
    
    print("Checking migration status...")
    
    with app.app_context():
        try:
            # Check if new tables exist
            warehouse_configs = WarehouseConfig.query.count()
            templates = WarehouseTemplate.query.count()
            
            print(f"   • Warehouse Configs: {warehouse_configs}")
            print(f"   • Templates: {templates}")
            
            if warehouse_configs > 0 or templates > 0:
                print("Location system appears to be set up")
                return True
            else:
                print("Location system needs migration")
                return False
                
        except Exception as e:
            print(f"Cannot check migration status: {str(e)}")
            return False

if __name__ == "__main__":
    print("Location Management System Migration")
    print("=====================================\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_migration_status()
    else:
        # Ask for confirmation
        response = input("This will create new database tables. Continue? (y/N): ")
        
        if response.lower() in ['y', 'yes']:
            success = migrate_location_system()
            if success:
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print("Migration cancelled")
            sys.exit(0)