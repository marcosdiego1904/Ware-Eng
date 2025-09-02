"""
Admin Migration Endpoint - Smart Configuration

This creates a special admin endpoint that runs the Smart Configuration
database migration directly through your application.

SECURITY: This should only be used once and then disabled.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import text
from database import db
import os
from datetime import datetime

# Create admin blueprint
admin_migration_bp = Blueprint('admin_migration', __name__, url_prefix='/api/admin')


@admin_migration_bp.route('/migrate-smart-config', methods=['POST'])
def migrate_smart_config():
    """
    Admin endpoint to run Smart Configuration database migration
    
    POST /api/admin/migrate-smart-config
    
    SECURITY: Add authentication/authorization as needed
    """
    
    # Simple security check - you can modify this
    auth_key = request.headers.get('X-Admin-Key')
    expected_key = os.environ.get('ADMIN_MIGRATION_KEY', 'smart-config-migration-2024')
    
    if auth_key != expected_key:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Valid admin key required'
        }), 401
    
    try:
        migration_steps = []
        
        # Step 1: Check database type
        db_type = db.engine.dialect.name.lower()
        migration_steps.append(f"Database type detected: {db_type.upper()}")
        
        # Step 2: Check current schema
        if db_type == 'postgresql':
            check_columns_sql = """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'warehouse_template' 
                AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                ORDER BY column_name
            """
        else:
            return jsonify({
                'error': 'Unsupported database type',
                'message': f'This migration is for PostgreSQL, found {db_type}'
            }), 400
        
        with db.engine.connect() as connection:
            result = connection.execute(text(check_columns_sql))
            existing_columns = result.fetchall()
        
        migration_steps.append(f"Found {len(existing_columns)}/4 Smart Configuration columns")
        
        if len(existing_columns) >= 4:
            return jsonify({
                'success': True,
                'message': 'Migration already applied',
                'steps': migration_steps + ['All Smart Configuration columns already exist']
            })
        
        # Step 3: Apply migration
        migration_statements = [
            "ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS location_format_config TEXT",
            "ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS format_confidence FLOAT", 
            "ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS format_examples TEXT",
            "ALTER TABLE warehouse_template ADD COLUMN IF NOT EXISTS format_learned_date TIMESTAMP"
        ]
        
        with db.engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            try:
                for i, statement in enumerate(migration_statements, 1):
                    connection.execute(text(statement))
                    migration_steps.append(f"Step {i}: Added column {statement.split()[-2]}")
                
                # Update existing templates with default values
                update_sql = """
                UPDATE warehouse_template 
                SET format_confidence = 0.0, format_learned_date = created_at
                WHERE format_confidence IS NULL
                """
                result = connection.execute(text(update_sql))
                affected_rows = result.rowcount
                migration_steps.append(f"Updated {affected_rows} existing templates with default values")
                
                # Create location_format_history table
                create_history_table_sql = """
                CREATE TABLE IF NOT EXISTS location_format_history (
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
                connection.execute(text(create_history_table_sql))
                migration_steps.append("Created location_format_history table")
                
                # Create indexes
                index_statements = [
                    "CREATE INDEX IF NOT EXISTS idx_format_history_template ON location_format_history(warehouse_template_id)",
                    "CREATE INDEX IF NOT EXISTS idx_format_history_date ON location_format_history(detected_at)",
                    "CREATE INDEX IF NOT EXISTS idx_format_history_pending ON location_format_history(user_confirmed, reviewed_at) WHERE reviewed_at IS NULL"
                ]
                
                for idx_sql in index_statements:
                    try:
                        connection.execute(text(idx_sql))
                        migration_steps.append(f"Created index: {idx_sql.split()[-3]}")
                    except Exception as idx_error:
                        migration_steps.append(f"Index warning: {idx_error}")
                
                # Commit transaction
                trans.commit()
                migration_steps.append("Migration transaction committed successfully")
                
            except Exception as e:
                trans.rollback()
                migration_steps.append(f"Migration failed, transaction rolled back: {e}")
                raise
        
        # Step 4: Verify migration
        with db.engine.connect() as connection:
            result = connection.execute(text(check_columns_sql))
            final_columns = result.fetchall()
        
        migration_steps.append(f"Verification: {len(final_columns)}/4 columns now exist")
        
        if len(final_columns) >= 4:
            migration_steps.append("✓ Smart Configuration migration completed successfully!")
            
            return jsonify({
                'success': True,
                'message': 'Smart Configuration migration completed successfully',
                'database_type': db_type,
                'columns_added': len(final_columns),
                'steps': migration_steps,
                'timestamp': datetime.now().isoformat(),
                'next_steps': [
                    'Remove the hotfix from models.py (make columns non-nullable)',
                    'Test the Templates tab - should load without errors',
                    'Test Smart Configuration features in template creation',
                    'Disable this migration endpoint for security'
                ]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Migration verification failed',
                'steps': migration_steps
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Migration failed',
            'steps': migration_steps if 'migration_steps' in locals() else []
        }), 500


@admin_migration_bp.route('/migration-status', methods=['GET'])
def migration_status():
    """
    Check Smart Configuration migration status
    
    GET /api/admin/migration-status
    """
    try:
        db_type = db.engine.dialect.name.lower()
        
        if db_type == 'postgresql':
            check_sql = """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'warehouse_template' 
                AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                ORDER BY column_name
            """
        else:
            check_sql = """
                SELECT name, type 
                FROM pragma_table_info('warehouse_template')
                WHERE name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                ORDER BY name
            """
        
        with db.engine.connect() as connection:
            result = connection.execute(text(check_sql))
            columns = result.fetchall()
        
        # Check location_format_history table
        history_exists = False
        try:
            with db.engine.connect() as connection:
                connection.execute(text("SELECT COUNT(*) FROM location_format_history LIMIT 1"))
            history_exists = True
        except:
            pass
        
        return jsonify({
            'database_type': db_type,
            'smart_config_columns': len(columns),
            'columns_detail': [{'name': col[0], 'type': col[1]} for col in columns],
            'location_format_history_exists': history_exists,
            'migration_needed': len(columns) < 4 or not history_exists,
            'migration_status': 'completed' if len(columns) >= 4 and history_exists else 'needed'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to check migration status'
        }), 500


# Register the blueprint (you'll add this to your main app)
def register_admin_migration_blueprint(app):
    """Register the admin migration blueprint with the Flask app"""
    app.register_blueprint(admin_migration_bp)