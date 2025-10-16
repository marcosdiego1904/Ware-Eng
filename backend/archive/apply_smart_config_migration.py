#!/usr/bin/env python3
"""
Smart Configuration Database Migration Runner

This script applies the database schema changes needed for the Smart Configuration system:
1. Adds location format columns to warehouse_template table
2. Creates location_format_history table for evolution tracking
3. Sets up indexes and constraints
"""

import os
import sys
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def run_migration():
    """Run the Smart Configuration database migration"""
    print("=" * 60)
    print("SMART CONFIGURATION DATABASE MIGRATION")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import Flask app and database with context
        from app import app
        from database import db
        from sqlalchemy import text
        
        with app.app_context():
            print("\n1. Checking current database schema...")
            
            # Check if columns already exist
            try:
                with db.engine.connect() as connection:
                    result = connection.execute(text("""
                        SELECT COUNT(*) as column_count
                        FROM information_schema.columns 
                        WHERE table_name = 'warehouse_template' 
                        AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                    """))
                    row = result.fetchone()
                    existing_columns = row[0] if row else 0
                
                print(f"   Found {existing_columns}/4 Smart Configuration columns in warehouse_template")
                
            except Exception as e:
                # Try SQLite syntax (for development)
                try:
                    with db.engine.connect() as connection:
                        result = connection.execute(text("""
                            SELECT COUNT(*) as column_count
                            FROM pragma_table_info('warehouse_template')
                            WHERE name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                        """))
                        row = result.fetchone()
                        existing_columns = row[0] if row else 0
                    
                    print(f"   Found {existing_columns}/4 Smart Configuration columns in warehouse_template (SQLite)")
                    
                except Exception as e2:
                    print(f"   Could not check existing columns: {e2}")
                    existing_columns = 0
            
            # Step 2: Add columns to warehouse_template if needed
            if existing_columns < 4:
                print(f"\n2. Adding Smart Configuration columns to warehouse_template...")
                
                try:
                    # Add columns one by one for better compatibility
                    columns_to_add = [
                        ('location_format_config', 'TEXT'),
                        ('format_confidence', 'FLOAT'),
                        ('format_examples', 'TEXT'),
                        ('format_learned_date', 'TIMESTAMP')
                    ]
                    
                    for col_name, col_type in columns_to_add:
                        try:
                            with db.engine.connect() as connection:
                                connection.execute(text(f'ALTER TABLE warehouse_template ADD COLUMN {col_name} {col_type}'))
                                connection.commit()
                            print(f"   + Added column: {col_name}")
                        except Exception as col_error:
                            if 'already exists' in str(col_error).lower() or 'duplicate column' in str(col_error).lower():
                                print(f"   o Column {col_name} already exists")
                            else:
                                print(f"   ! Error adding {col_name}: {col_error}")
                    
                    db.session.commit()
                    print("   + warehouse_template columns added successfully")
                    
                except Exception as e:
                    print(f"   - Error adding columns: {e}")
                    db.session.rollback()
                    return False
            else:
                print("\n2. warehouse_template columns already exist - skipping")
            
            # Step 3: Create location_format_history table
            print("\n3. Creating location_format_history table...")
            
            try:
                # Check if table exists first
                try:
                    with db.engine.connect() as connection:
                        result = connection.execute(text("SELECT COUNT(*) FROM location_format_history LIMIT 1"))
                    print("   o location_format_history table already exists")
                except:
                    # Table doesn't exist, create it
                    create_table_sql = """
                    CREATE TABLE location_format_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        warehouse_template_id INTEGER NOT NULL,
                        original_format TEXT,
                        new_format TEXT,
                        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        confidence_score FLOAT NOT NULL,
                        user_confirmed BOOLEAN DEFAULT FALSE,
                        applied BOOLEAN DEFAULT FALSE,
                        reviewed_by INTEGER,
                        reviewed_at TIMESTAMP,
                        sample_locations TEXT,
                        trigger_report_id INTEGER,
                        pattern_change_type VARCHAR(50),
                        affected_location_count INTEGER DEFAULT 0,
                        FOREIGN KEY (warehouse_template_id) REFERENCES warehouse_template (id)
                    )
                    """
                    
                    with db.engine.connect() as connection:
                        connection.execute(text(create_table_sql))
                        connection.commit()
                    print("   + Created location_format_history table")
                    
                    # Create indexes
                    try:
                        with db.engine.connect() as connection:
                            connection.execute(text("CREATE INDEX idx_format_history_template ON location_format_history(warehouse_template_id)"))
                            connection.execute(text("CREATE INDEX idx_format_history_date ON location_format_history(detected_at)"))
                            connection.commit()
                        print("   + Created indexes")
                    except Exception as idx_error:
                        print(f"   ! Index creation warning: {idx_error}")
                    
                    db.session.commit()
                    print("   + location_format_history table created successfully")
                
            except Exception as e:
                print(f"   - Error creating location_format_history table: {e}")
                db.session.rollback()
                return False
            
            # Step 4: Update existing templates with default values
            print("\n4. Updating existing templates...")
            
            try:
                from models import WarehouseTemplate
                
                # Count templates without format config
                templates_to_update = WarehouseTemplate.query.filter(
                    WarehouseTemplate.format_confidence.is_(None)
                ).count()
                
                if templates_to_update > 0:
                    # Update templates to have default confidence of 0.0
                    update_sql = """
                    UPDATE warehouse_template 
                    SET format_confidence = 0.0, format_learned_date = created_at
                    WHERE format_confidence IS NULL
                    """
                    
                    with db.engine.connect() as connection:
                        connection.execute(text(update_sql))
                        connection.commit()
                    db.session.commit()
                    print(f"   + Updated {templates_to_update} existing templates with default values")
                else:
                    print("   o No templates need updating")
                
            except Exception as e:
                print(f"   ! Warning updating templates: {e}")
                # This is not critical for migration success
            
            # Step 5: Verification
            print("\n5. Verifying migration...")
            
            try:
                # Test that we can query the new columns
                from models import WarehouseTemplate
                
                templates = WarehouseTemplate.query.limit(1).all()
                if templates:
                    template = templates[0]
                    # Try to access new columns
                    format_config = template.location_format_config
                    confidence = template.format_confidence
                    print(f"   + New columns accessible on template: {template.name}")
                else:
                    print("   o No templates to test, but schema appears correct")
                
                # Test location_format_history table
                try:
                    with db.engine.connect() as connection:
                        connection.execute(text("SELECT COUNT(*) FROM location_format_history"))
                    print("   + location_format_history table accessible")
                except Exception as e:
                    print(f"   - Error accessing location_format_history: {e}")
                    return False
                
            except Exception as e:
                print(f"   - Verification failed: {e}")
                return False
            
            print("\n" + "=" * 60)
            print("+ SMART CONFIGURATION MIGRATION COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print("\nThe Smart Configuration system is now ready!")
            print("You can now:")
            print("• Create templates with automatic location format detection")
            print("• Upload inventories with format normalization")
            print("• Track format evolution over time")
            print("• Use all Smart Configuration features")
            
            return True
            
    except Exception as e:
        print(f"\n- MIGRATION FAILED: {e}")
        print("\nPlease check the error above and try again.")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)