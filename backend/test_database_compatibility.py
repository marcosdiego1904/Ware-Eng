#!/usr/bin/env python3
"""
Test Smart Configuration Database Compatibility

Tests the Smart Configuration system with both SQLite and PostgreSQL
"""

import os
import sys
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_database_compatibility():
    """Test Smart Configuration compatibility with current database"""
    print("=" * 60)
    print("SMART CONFIGURATION DATABASE COMPATIBILITY TEST")
    print("=" * 60)
    
    try:
        from app import app
        from database import db
        from sqlalchemy import text
        
        with app.app_context():
            # Get database type
            db_type = db.engine.dialect.name.lower()
            print(f"Database Type: {db_type.upper()}")
            print(f"Database URL: {str(db.engine.url).split('@')[0]}@[HIDDEN]" if '@' in str(db.engine.url) else str(db.engine.url))
            
            # Test 1: Check if Smart Configuration columns exist
            print(f"\n1. Testing Smart Configuration schema...")
            
            if db_type == 'postgresql':
                check_sql = """
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'warehouse_template' 
                    AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                    ORDER BY column_name
                """
            else:  # SQLite
                check_sql = """
                    SELECT name, type 
                    FROM pragma_table_info('warehouse_template')
                    WHERE name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                    ORDER BY name
                """
            
            with db.engine.connect() as connection:
                result = connection.execute(text(check_sql))
                columns = result.fetchall()
            
            print(f"   Smart Configuration columns found: {len(columns)}/4")
            for col in columns:
                print(f"   + {col[0]} ({col[1]})")
            
            # Test 2: Check location_format_history table
            print(f"\n2. Testing location_format_history table...")
            
            try:
                with db.engine.connect() as connection:
                    result = connection.execute(text("SELECT COUNT(*) FROM location_format_history"))
                    count = result.fetchone()[0]
                print(f"   + Table exists with {count} records")
            except Exception as e:
                print(f"   - Table missing or error: {e}")
            
            # Test 3: Test model functionality
            print(f"\n3. Testing Smart Configuration models...")
            
            try:
                from models import WarehouseTemplate, LocationFormatHistory
                
                # Test WarehouseTemplate format methods
                templates = WarehouseTemplate.query.limit(1).all()
                if templates:
                    template = templates[0]
                    print(f"   + WarehouseTemplate accessible: {template.name}")
                    
                    # Test format methods
                    format_config = template.get_location_format_config()
                    format_summary = template.get_format_summary()
                    has_format = template.has_location_format()
                    
                    print(f"   + Format methods working: has_format={has_format}")
                    print(f"   + Format summary: {format_summary}")
                else:
                    print("   o No templates to test")
                
                # Test LocationFormatHistory
                history_count = LocationFormatHistory.query.count()
                print(f"   + LocationFormatHistory accessible: {history_count} records")
                
            except Exception as e:
                print(f"   - Model test error: {e}")
            
            # Test 4: Test Smart Configuration imports
            print(f"\n4. Testing Smart Configuration components...")
            
            try:
                from smart_format_detector import SmartFormatDetector
                detector = SmartFormatDetector()
                print("   + SmartFormatDetector imported successfully")
                
                from format_evolution_tracker import FormatEvolutionTracker
                print("   + FormatEvolutionTracker imported successfully")
                
                # Test basic detection
                test_examples = ["010A", "325B", "245D"]
                result = detector.detect_format(test_examples)
                confidence = result.get('confidence', 0)
                print(f"   + Format detection working: {confidence:.1%} confidence")
                
            except Exception as e:
                print(f"   - Smart Configuration import error: {e}")
            
            # Test 5: Database-specific features
            print(f"\n5. Testing database-specific features...")
            
            if db_type == 'postgresql':
                print("   PostgreSQL-specific tests:")
                try:
                    # Test JSONB functionality (if using JSONB)
                    with db.engine.connect() as connection:
                        result = connection.execute(text("SELECT version()"))
                        version = result.fetchone()[0]
                    print(f"   + PostgreSQL version: {version.split(',')[0]}")
                    
                    # Test index usage
                    with db.engine.connect() as connection:
                        result = connection.execute(text("""
                            SELECT indexname FROM pg_indexes 
                            WHERE tablename = 'location_format_history'
                        """))
                        indexes = result.fetchall()
                    print(f"   + Indexes on location_format_history: {len(indexes)}")
                    
                except Exception as e:
                    print(f"   - PostgreSQL test error: {e}")
                    
            else:  # SQLite
                print("   SQLite-specific tests:")
                try:
                    # Test SQLite version
                    with db.engine.connect() as connection:
                        result = connection.execute(text("SELECT sqlite_version()"))
                        version = result.fetchone()[0]
                    print(f"   + SQLite version: {version}")
                    
                    # Test foreign key support
                    with db.engine.connect() as connection:
                        result = connection.execute(text("PRAGMA foreign_keys"))
                        fk_enabled = result.fetchone()[0]
                    print(f"   + Foreign keys enabled: {bool(fk_enabled)}")
                    
                except Exception as e:
                    print(f"   - SQLite test error: {e}")
            
            print(f"\n" + "=" * 60)
            print(f"COMPATIBILITY TEST COMPLETED FOR {db_type.upper()}")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_migration_instructions():
    """Show instructions for applying Smart Configuration to production"""
    print("\n" + "=" * 60)
    print("PRODUCTION MIGRATION INSTRUCTIONS")
    print("=" * 60)
    
    print("""
FOR POSTGRESQL PRODUCTION:

1. Connect to your production PostgreSQL database
2. Run the SQL migration script:
   
   psql -U your_user -d your_database -f migrations/smart_config_postgresql.sql
   
   OR use the Python migration:
   
   python apply_smart_config_production.py

3. Verify the migration by checking:
   - warehouse_template has 4 new columns
   - location_format_history table exists
   - All indexes are created

FOR SQLITE DEVELOPMENT:

The migration has already been applied to your SQLite database.
No additional steps needed.

VERIFICATION:

After migration, test by:
1. Going to Templates tab (should load without errors)
2. Creating a new template with format detection
3. Uploading inventory to test format normalization
""")

if __name__ == "__main__":
    success = test_database_compatibility()
    
    if success:
        show_migration_instructions()
    
    sys.exit(0 if success else 1)