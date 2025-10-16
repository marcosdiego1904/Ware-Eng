#!/usr/bin/env python3
"""
Web-based PostgreSQL Smart Configuration Migration

This script creates a temporary web endpoint that can be called to apply
the Smart Configuration migration to PostgreSQL production.
"""

import sys
import os
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from flask import Flask, jsonify
from sqlalchemy import create_engine, text, inspect
import logging

def create_migration_app():
    """Create a Flask app specifically for running the migration"""
    app = Flask(__name__)
    
    # Use your PostgreSQL connection string
    database_url = "postgresql://ware_eng_db_user:fqvKdOGZEt1CGIeLF4J1AG8RTtCv0Zdu@dpg-d23244fg127c73fga10g-a.ohio-postgres.render.com/ware_eng_db"
    
    @app.route('/migrate-smart-config')
    def migrate_smart_config():
        """Apply Smart Configuration migration to PostgreSQL"""
        try:
            # Create engine with PostgreSQL connection
            engine = create_engine(database_url, echo=True)
            
            # Check connection
            with engine.connect() as connection:
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"Connected to: {version}")
                
                # Check current schema
                inspector = inspect(engine)
                columns = inspector.get_columns('warehouse_config')
                column_names = [col['name'] for col in columns]
                
                smart_config_columns = [
                    'location_format_config',
                    'format_confidence', 
                    'format_examples',
                    'format_learned_date'
                ]
                
                missing_columns = [col for col in smart_config_columns if col not in column_names]
                
                if not missing_columns:
                    return jsonify({
                        'success': True,
                        'message': 'All Smart Configuration columns already exist!',
                        'existing_columns': column_names
                    })
                
                # Apply the migration
                migration_sql = [
                    "ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS location_format_config TEXT",
                    "ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_confidence FLOAT DEFAULT 0.0",
                    "ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_examples TEXT",
                    "ALTER TABLE warehouse_config ADD COLUMN IF NOT EXISTS format_learned_date TIMESTAMP",
                    "UPDATE warehouse_config SET format_confidence = 0.0 WHERE format_confidence IS NULL"
                ]
                
                executed_statements = []
                for sql_statement in migration_sql:
                    try:
                        connection.execute(text(sql_statement))
                        executed_statements.append(sql_statement)
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            executed_statements.append(f"SKIPPED: {sql_statement} (already exists)")
                        else:
                            raise e
                
                connection.commit()
                
                # Verify the migration
                updated_columns = inspector.get_columns('warehouse_config')
                updated_column_names = [col['name'] for col in updated_columns]
                
                verification = {}
                for col in smart_config_columns:
                    verification[col] = "EXISTS" if col in updated_column_names else "MISSING"
                
                return jsonify({
                    'success': True,
                    'message': 'Smart Configuration migration completed successfully!',
                    'missing_columns_before': missing_columns,
                    'executed_statements': executed_statements,
                    'verification': verification
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Migration failed'
            }), 500
    
    return app

if __name__ == "__main__":
    app = create_migration_app()
    print("=" * 70)
    print("WEB-BASED POSTGRESQL SMART CONFIGURATION MIGRATION")
    print("=" * 70)
    print("Starting migration web server...")
    print("Navigate to: http://localhost:5001/migrate-smart-config")
    print("=" * 70)
    
    # Suppress Flask development server warnings
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    app.run(host='localhost', port=5001, debug=False)