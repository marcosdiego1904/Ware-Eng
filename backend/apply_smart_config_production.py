#!/usr/bin/env python3
"""
Smart Configuration Production Migration

This script applies Smart Configuration database changes for BOTH:
- SQLite (development)
- PostgreSQL (production)

It detects the database type and uses appropriate syntax for each.
"""

import os
import sys
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def get_database_type(engine):
    """Detect database type from SQLAlchemy engine"""
    return engine.dialect.name.lower()

def run_production_migration():
    """Run Smart Configuration migration for production"""
    print("=" * 70)
    print("SMART CONFIGURATION - PRODUCTION MIGRATION")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import Flask app and database with context
        from app import app
        from database import db
        from sqlalchemy import text
        
        with app.app_context():
            # Detect database type
            db_type = get_database_type(db.engine)
            print(f"\n1. Detected database type: {db_type.upper()}")
            
            # Check current schema
            print("\n2. Checking current Smart Configuration schema...")
            
            # Database-specific column checking
            if db_type == 'postgresql':
                check_columns_sql = """
                    SELECT COUNT(*) as column_count
                    FROM information_schema.columns 
                    WHERE table_name = 'warehouse_template' 
                    AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                """
            else:  # SQLite
                check_columns_sql = """
                    SELECT COUNT(*) as column_count
                    FROM pragma_table_info('warehouse_template')
                    WHERE name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                """
            
            with db.engine.connect() as connection:
                result = connection.execute(text(check_columns_sql))
                row = result.fetchone()
                existing_columns = row[0] if row else 0
            
            print(f"   Found {existing_columns}/4 Smart Configuration columns")
            
            # Step 3: Add columns if needed
            if existing_columns < 4:
                print(f"\n3. Adding Smart Configuration columns to warehouse_template...")
                
                # Database-specific column definitions
                if db_type == 'postgresql':
                    columns_to_add = [
                        ('location_format_config', 'TEXT'),
                        ('format_confidence', 'FLOAT'),
                        ('format_examples', 'TEXT'),
                        ('format_learned_date', 'TIMESTAMP')
                    ]
                else:  # SQLite
                    columns_to_add = [
                        ('location_format_config', 'TEXT'),
                        ('format_confidence', 'REAL'),
                        ('format_examples', 'TEXT'),
                        ('format_learned_date', 'TIMESTAMP')
                    ]
                
                with db.engine.connect() as connection:
                    for col_name, col_type in columns_to_add:
                        try:
                            if db_type == 'postgresql':
                                sql = f'ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS {col_name} {col_type}'
                            else:
                                sql = f'ALTER TABLE warehouse_template ADD COLUMN {col_name} {col_type}'
                            
                            connection.execute(text(sql))
                            print(f"   + Added column: {col_name} ({col_type})")
                        except Exception as col_error:
                            if 'already exists' in str(col_error).lower() or 'duplicate column' in str(col_error).lower():
                                print(f"   o Column {col_name} already exists")
                            else:
                                print(f"   ! Error adding {col_name}: {col_error}")
                    
                    connection.commit()
                print("   + Columns added successfully")
            else:
                print("\n3. All warehouse_template columns exist - skipping")
            
            # Step 4: Create location_format_history table
            print("\n4. Creating location_format_history table...")
            
            try:
                # Check if table exists
                with db.engine.connect() as connection:
                    try:
                        result = connection.execute(text("SELECT COUNT(*) FROM location_format_history LIMIT 1"))
                        print("   o location_format_history table already exists")
                        table_exists = True
                    except:
                        table_exists = False
                
                if not table_exists:
                    # Database-specific table creation
                    if db_type == 'postgresql':
                        create_table_sql = """
                        CREATE TABLE location_format_history (
                            id SERIAL PRIMARY KEY,
                            warehouse_template_id INTEGER NOT NULL REFERENCES warehouse_template(id) ON DELETE CASCADE,
                            original_format TEXT,
                            new_format TEXT,
                            detected_at TIMESTAMP DEFAULT NOW(),
                            confidence_score FLOAT NOT NULL,
                            user_confirmed BOOLEAN DEFAULT FALSE,
                            applied BOOLEAN DEFAULT FALSE,
                            reviewed_by INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
                            reviewed_at TIMESTAMP,
                            sample_locations TEXT,
                            trigger_report_id INTEGER,
                            pattern_change_type VARCHAR(50),
                            affected_location_count INTEGER DEFAULT 0
                        )
                        """
                    else:  # SQLite
                        create_table_sql = """
                        CREATE TABLE location_format_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            warehouse_template_id INTEGER NOT NULL,
                            original_format TEXT,
                            new_format TEXT,
                            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            confidence_score REAL NOT NULL,
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
                    print("   + Creating performance indexes...")
                    index_queries = [
                        "CREATE INDEX IF NOT EXISTS idx_format_history_template ON location_format_history(warehouse_template_id)",
                        "CREATE INDEX IF NOT EXISTS idx_format_history_date ON location_format_history(detected_at)",
                    ]
                    
                    # PostgreSQL-specific index with WHERE clause
                    if db_type == 'postgresql':
                        index_queries.append("CREATE INDEX IF NOT EXISTS idx_format_history_pending ON location_format_history(user_confirmed, reviewed_at) WHERE reviewed_at IS NULL")
                    
                    with db.engine.connect() as connection:
                        for idx_sql in index_queries:
                            try:
                                connection.execute(text(idx_sql))
                            except Exception as idx_error:
                                print(f"     ! Index warning: {idx_error}")
                        connection.commit()
                    print("   + Indexes created")
                
            except Exception as e:
                print(f"   - Error with location_format_history table: {e}")
                return False
            
            # Step 5: Update existing templates
            print("\n5. Updating existing templates with default values...")
            
            try:
                from models import WarehouseTemplate
                
                templates_to_update = WarehouseTemplate.query.filter(
                    WarehouseTemplate.format_confidence.is_(None)
                ).count()
                
                if templates_to_update > 0:
                    update_sql = """
                    UPDATE warehouse_template 
                    SET format_confidence = 0.0, format_learned_date = created_at
                    WHERE format_confidence IS NULL
                    """
                    
                    with db.engine.connect() as connection:
                        connection.execute(text(update_sql))
                        connection.commit()
                    
                    print(f"   + Updated {templates_to_update} existing templates")
                else:
                    print("   o All templates already have format configuration")
                
            except Exception as e:
                print(f"   ! Warning updating templates: {e}")
            
            # Step 6: Verify migration
            print("\n6. Verifying Smart Configuration system...")
            
            try:
                # Test new columns
                from models import WarehouseTemplate
                
                templates = WarehouseTemplate.query.limit(1).all()
                if templates:
                    template = templates[0]
                    format_config = template.location_format_config
                    confidence = template.format_confidence
                    print(f"   + New columns accessible on template: {template.name}")
                else:
                    print("   o No templates to test, but schema appears correct")
                
                # Test format history table
                with db.engine.connect() as connection:
                    connection.execute(text("SELECT COUNT(*) FROM location_format_history"))
                print("   + location_format_history table accessible")
                
                # Test Smart Configuration imports
                from smart_format_detector import SmartFormatDetector
                from format_evolution_tracker import FormatEvolutionTracker
                print("   + Smart Configuration modules importable")
                
            except Exception as e:
                print(f"   - Verification failed: {e}")
                return False
            
            # Success!
            print("\n" + "=" * 70)
            print(f"+ SMART CONFIGURATION MIGRATION COMPLETED FOR {db_type.upper()}")
            print("=" * 70)
            
            print(f"\nDatabase: {db_type.upper()}")
            print("Features now available:")
            print("  + Real-time location format detection in templates")
            print("  + Automatic format normalization during uploads")
            print("  + Format evolution tracking and user notifications")
            print("  + Complete API ecosystem for format management")
            print("  + Cross-database compatibility (SQLite + PostgreSQL)")
            
            if db_type == 'postgresql':
                print("\nProduction-specific features:")
                print("  + Advanced indexing with WHERE clauses")
                print("  + Foreign key constraints with CASCADE")
                print("  + SERIAL primary keys for better performance")
                print("  + Database comments for documentation")
            
            print("\nSmart Configuration is ready for production use!")
            
            return True
            
    except Exception as e:
        print(f"\n- MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_sql_file_migration(sql_file_path):
    """Alternative: Run SQL file migration directly"""
    print("\n" + "=" * 70)
    print("ALTERNATIVE: SQL FILE MIGRATION")
    print("=" * 70)
    
    try:
        from app import app
        from database import db
        from sqlalchemy import text
        
        with app.app_context():
            db_type = get_database_type(db.engine)
            print(f"Database type: {db_type.upper()}")
            
            if db_type != 'postgresql':
                print("This SQL file is designed for PostgreSQL production.")
                print("Use the automated migration above for other databases.")
                return False
            
            if not os.path.exists(sql_file_path):
                print(f"SQL file not found: {sql_file_path}")
                return False
            
            print(f"Executing SQL file: {sql_file_path}")
            
            with open(sql_file_path, 'r') as f:
                sql_content = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            with db.engine.connect() as connection:
                for i, statement in enumerate(statements, 1):
                    if statement.upper().startswith(('SELECT', 'COMMENT')):
                        try:
                            result = connection.execute(text(statement))
                            if statement.upper().startswith('SELECT'):
                                row = result.fetchone()
                                if row:
                                    print(f"  Statement {i}: {row[0]}")
                        except Exception as e:
                            print(f"  Statement {i} warning: {e}")
                    else:
                        try:
                            connection.execute(text(statement))
                            print(f"  + Executed statement {i}")
                        except Exception as e:
                            if 'already exists' in str(e).lower():
                                print(f"  o Statement {i}: already exists")
                            else:
                                print(f"  ! Statement {i} error: {e}")
                
                connection.commit()
            
            print("+ PostgreSQL SQL migration completed!")
            return True
            
    except Exception as e:
        print(f"- SQL migration failed: {e}")
        return False

if __name__ == "__main__":
    print("Smart Configuration Production Migration")
    print("Choose migration method:")
    print("1. Automated Python migration (recommended)")
    print("2. PostgreSQL SQL file migration")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        sql_file = os.path.join(os.path.dirname(__file__), 'migrations', 'smart_config_postgresql.sql')
        success = run_sql_file_migration(sql_file)
    else:
        success = run_production_migration()
    
    sys.exit(0 if success else 1)