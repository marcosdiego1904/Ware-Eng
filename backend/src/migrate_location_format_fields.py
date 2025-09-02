"""
Database Migration: Add Smart Location Format Fields to WarehouseTemplate

This migration adds the location format configuration fields to the 
WarehouseTemplate table to support the Smart Configuration system.

New fields:
- location_format_config: TEXT (JSON) - Format configuration from SmartFormatDetector
- format_confidence: FLOAT - Detection confidence score (0.0-1.0)  
- format_examples: TEXT (JSON) - Original user examples used for detection
- format_learned_date: DATETIME - When format was detected/learned

These fields enable warehouses to define location formats by simply providing
examples during template creation, with the system automatically learning
the pattern and generating conversion rules.
"""

import logging
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData, Table, Column, Float, Text, DateTime
from sqlalchemy.exc import SQLAlchemyError
import os
import sys

# Add the backend src directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from models import WarehouseTemplate

logger = logging.getLogger(__name__)


class LocationFormatMigration:
    """
    Migration class for adding location format fields to WarehouseTemplate
    """
    
    def __init__(self, db_connection_string=None):
        """
        Initialize migration with database connection
        
        Args:
            db_connection_string: Database connection string (optional, uses app config if not provided)
        """
        self.db_connection_string = db_connection_string
        self.migration_name = "add_location_format_fields_to_warehouse_template"
        self.migration_version = "1.0.0"
        
        # SQL statements for the migration
        self.add_columns_sql = """
        ALTER TABLE warehouse_template 
        ADD COLUMN location_format_config TEXT,
        ADD COLUMN format_confidence FLOAT,
        ADD COLUMN format_examples TEXT,
        ADD COLUMN format_learned_date DATETIME;
        """
        
        # SQL for rollback (remove columns)
        self.rollback_sql = """
        ALTER TABLE warehouse_template 
        DROP COLUMN location_format_config,
        DROP COLUMN format_confidence,
        DROP COLUMN format_examples,
        DROP COLUMN format_learned_date;
        """
        
        # SQL to check if migration is already applied
        self.check_columns_sql = """
        SELECT COUNT(*) as column_count
        FROM information_schema.columns 
        WHERE table_name = 'warehouse_template' 
        AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date');
        """
        
        logger.info(f"LocationFormatMigration initialized - {self.migration_name} v{self.migration_version}")
    
    def check_migration_status(self):
        """
        Check if the migration has already been applied
        
        Returns:
            tuple: (is_applied: bool, existing_columns: int)
        """
        try:
            with db.engine.connect() as connection:
                result = connection.execute(text(self.check_columns_sql))
                row = result.fetchone()
                existing_columns = row.column_count if row else 0
                
                # Migration is applied if all 4 columns exist
                is_applied = existing_columns == 4
                
                logger.info(f"Migration status check: {existing_columns}/4 columns exist, applied={is_applied}")
                return is_applied, existing_columns
                
        except Exception as e:
            logger.error(f"Failed to check migration status: {e}")
            return False, 0
    
    def apply_migration(self, dry_run=False):
        """
        Apply the migration to add location format fields
        
        Args:
            dry_run: If True, only show what would be done without executing
            
        Returns:
            bool: True if migration succeeded, False otherwise
        """
        logger.info(f"Starting migration: {self.migration_name} (dry_run={dry_run})")
        
        try:
            # Check current status
            is_applied, existing_columns = self.check_migration_status()
            
            if is_applied:
                logger.info("Migration already applied - all columns exist")
                return True
            
            if existing_columns > 0:
                logger.warning(f"Partial migration detected - {existing_columns}/4 columns exist")
                logger.info("Attempting to continue migration...")
            
            if dry_run:
                logger.info("DRY RUN - Would execute SQL:")
                logger.info(self.add_columns_sql)
                return True
            
            # Execute the migration
            with db.engine.connect() as connection:
                with connection.begin() as transaction:
                    try:
                        # Add the new columns
                        logger.info("Adding location format fields to warehouse_template table...")
                        connection.execute(text(self.add_columns_sql))
                        
                        # Verify the columns were added
                        is_applied_after, columns_after = self.check_migration_status()
                        if not is_applied_after:
                            raise Exception(f"Migration verification failed: only {columns_after}/4 columns exist after migration")
                        
                        # Commit the transaction
                        transaction.commit()
                        logger.info("Migration completed successfully")
                        
                        # Update any existing templates with default values if needed
                        self._update_existing_templates()
                        
                        return True
                        
                    except Exception as e:
                        transaction.rollback()
                        logger.error(f"Migration failed, rolled back: {e}")
                        return False
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def rollback_migration(self, dry_run=False):
        """
        Rollback the migration by removing location format fields
        
        Args:
            dry_run: If True, only show what would be done without executing
            
        Returns:
            bool: True if rollback succeeded, False otherwise
        """
        logger.info(f"Starting rollback: {self.migration_name} (dry_run={dry_run})")
        
        try:
            # Check current status
            is_applied, existing_columns = self.check_migration_status()
            
            if not is_applied and existing_columns == 0:
                logger.info("Migration not applied - nothing to rollback")
                return True
            
            if dry_run:
                logger.info("DRY RUN - Would execute SQL:")
                logger.info(self.rollback_sql)
                return True
            
            # Execute the rollback
            with db.engine.connect() as connection:
                with connection.begin() as transaction:
                    try:
                        logger.info("Removing location format fields from warehouse_template table...")
                        connection.execute(text(self.rollback_sql))
                        
                        # Verify the columns were removed
                        is_applied_after, columns_after = self.check_migration_status()
                        if columns_after > 0:
                            raise Exception(f"Rollback verification failed: {columns_after} columns still exist")
                        
                        transaction.commit()
                        logger.info("Rollback completed successfully")
                        return True
                        
                    except Exception as e:
                        transaction.rollback()
                        logger.error(f"Rollback failed, rolled back: {e}")
                        return False
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def _update_existing_templates(self):
        """
        Update existing warehouse templates with default values for new fields
        """
        try:
            # Count existing templates
            template_count = WarehouseTemplate.query.count()
            logger.info(f"Checking {template_count} existing templates for format configuration updates")
            
            # Note: We don't set default values since the fields are optional
            # Templates without format configuration will work normally
            # The Smart Format Detector will be used when users want to configure formats
            
            logger.info("Existing templates will maintain compatibility - no default values needed")
            
        except Exception as e:
            logger.warning(f"Failed to update existing templates: {e}")
            # This is not critical for migration success
    
    def generate_sample_format_config(self):
        """
        Generate a sample format configuration for testing purposes
        
        Returns:
            dict: Sample format configuration
        """
        from smart_format_detector import SmartFormatDetector, PatternType
        
        sample_config = {
            'pattern_type': PatternType.POSITION_LEVEL.value,
            'regex_pattern': r'^(\d{3})([A-Z])$',
            'canonical_converter': '01-01-{position:03d}{level}',
            'confidence': 0.95,
            'examples': ['010A', '325B', '245D'],
            'components': {
                'position_digits': 3,
                'level_format': 'single_letter',
                'default_aisle': 1,
                'default_rack': 1
            },
            'description': 'Position+Level format (PPP+L) detected with 95.0% confidence',
            'detection_metadata': {
                'detector_version': '1.0.0',
                'detection_timestamp': datetime.utcnow().isoformat(),
                'input_example_count': 3,
                'alternative_patterns_count': 0
            }
        }
        
        return sample_config
    
    def create_test_template_with_format(self, name="Test Smart Format Template"):
        """
        Create a test template with format configuration for validation
        
        Args:
            name: Template name
            
        Returns:
            WarehouseTemplate: Created template or None if failed
        """
        try:
            from models import db
            
            # Create basic template
            template = WarehouseTemplate(
                name=name,
                description="Test template with smart location format configuration",
                num_aisles=4,
                racks_per_aisle=2,
                positions_per_rack=50,
                levels_per_position=4,
                level_names='ABCD',
                default_pallet_capacity=1,
                created_by=1  # System user
            )
            
            # Add format configuration
            sample_config = self.generate_sample_format_config()
            template.set_location_format_config(sample_config)
            template.format_confidence = 0.95
            template.set_format_examples(['010A', '325B', '245D'])
            
            # Generate template code
            template.generate_template_code()
            
            # Save to database
            db.session.add(template)
            db.session.commit()
            
            logger.info(f"Created test template with ID {template.id}: {template.name}")
            logger.info(f"Format summary: {template.get_format_summary()}")
            
            return template
            
        except Exception as e:
            logger.error(f"Failed to create test template: {e}")
            if 'db' in locals():
                db.session.rollback()
            return None


def main():
    """
    Main function to run the migration
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Location Format Fields Migration')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    parser.add_argument('--status', action='store_true', help='Check migration status only')
    parser.add_argument('--create-test', action='store_true', help='Create test template after migration')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create migration instance
    migration = LocationFormatMigration()
    
    try:
        if args.status:
            # Check status only
            is_applied, existing_columns = migration.check_migration_status()
            print(f"Migration Status: {'Applied' if is_applied else 'Not Applied'}")
            print(f"Existing Columns: {existing_columns}/4")
            return 0
        
        elif args.rollback:
            # Rollback migration
            success = migration.rollback_migration(dry_run=args.dry_run)
            if success:
                print("Migration rollback completed successfully")
                return 0
            else:
                print("Migration rollback failed")
                return 1
        
        else:
            # Apply migration
            success = migration.apply_migration(dry_run=args.dry_run)
            if success:
                print("Migration applied successfully")
                
                if args.create_test and not args.dry_run:
                    # Create test template
                    test_template = migration.create_test_template_with_format()
                    if test_template:
                        print(f"Created test template: {test_template.name}")
                        print(f"Format: {test_template.get_format_summary()}")
                    else:
                        print("Failed to create test template")
                
                return 0
            else:
                print("Migration failed")
                return 1
    
    except KeyboardInterrupt:
        print("\nMigration interrupted by user")
        return 1
    except Exception as e:
        print(f"Migration error: {e}")
        logger.exception("Unexpected error during migration")
        return 1


if __name__ == "__main__":
    exit(main())