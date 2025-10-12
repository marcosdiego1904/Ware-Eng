#!/usr/bin/env python3
"""
PostgreSQL Schema Validation Tool
==================================

This script compares the expected SQLAlchemy model schema with the actual
PostgreSQL database schema to identify any missing columns or mismatches.

Usage:
    python check_schema_mismatch.py

This tool helps prevent errors like:
    psycopg2.errors.UndefinedColumn: column does not exist
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))


def check_schema():
    """Compare SQLAlchemy models with actual database schema"""

    print("=" * 80)
    print("PostgreSQL Schema Validation")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Import database connection
    try:
        from database import db
        from flask import Flask
        from dotenv import load_dotenv

        # Load environment variables
        load_dotenv()

        print("[1/4] Environment and imports loaded successfully")

    except ImportError as e:
        print(f"ERROR: Failed to import required modules: {e}")
        return False

    # Create Flask app for database context
    try:
        app = Flask(__name__)

        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')

        if not database_url:
            print("ERROR: DATABASE_URL environment variable not set")
            return False

        # Handle Heroku postgres:// -> postgresql:// conversion
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize database with app
        db.init_app(app)

        print(f"[2/4] Database connection configured")

    except Exception as e:
        print(f"ERROR: Failed to configure database: {e}")
        return False

    # Import all models
    try:
        from core_models import (User, AnalysisReport, Anomaly, AnomalyHistory,
                                 UserWarehouseAccess, InvitationCode)
        from models import (RuleCategory, Rule, RuleHistory, RuleTemplate,
                          RulePerformance, Location, WarehouseConfig,
                          WarehouseTemplate, LocationFormatHistory,
                          WarehouseScopeConfig, LocationClassificationCorrection)

        models = [
            ('user', User),
            ('analysis_report', AnalysisReport),
            ('anomaly', Anomaly),
            ('anomaly_history', AnomalyHistory),
            ('user_warehouse_access', UserWarehouseAccess),
            ('invitation_code', InvitationCode),
            ('rule_category', RuleCategory),
            ('rule', Rule),
            ('rule_history', RuleHistory),
            ('rule_template', RuleTemplate),
            ('rule_performance', RulePerformance),
            ('location', Location),
            ('warehouse_config', WarehouseConfig),
            ('warehouse_template', WarehouseTemplate),
            ('location_format_history', LocationFormatHistory),
            ('warehouse_scope_config', WarehouseScopeConfig),
            ('location_classification_correction', LocationClassificationCorrection)
        ]

        print(f"[3/4] Loaded {len(models)} models for validation")

    except ImportError as e:
        print(f"ERROR: Failed to import models: {e}")
        return False

    # Validate each model
    mismatches_found = False

    with app.app_context():
        print(f"[4/4] Validating schema...")
        print()

        for table_name, model_class in models:
            try:
                # Get expected columns from SQLAlchemy model
                expected_columns = {}
                for column in model_class.__table__.columns:
                    expected_columns[column.name] = {
                        'type': str(column.type),
                        'nullable': column.nullable,
                        'has_default': column.default is not None or column.server_default is not None
                    }

                # Check if table exists in database
                result = db.session.execute(db.text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = '{table_name}'
                    );
                """))

                table_exists = result.scalar()

                if not table_exists:
                    print(f"⚠️  Table '{table_name}' does not exist in database")
                    print(f"    Expected {len(expected_columns)} columns")
                    print()
                    mismatches_found = True
                    continue

                # Get actual columns from database
                result = db.session.execute(db.text(f"""
                    SELECT
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """))

                actual_columns = {}
                for row in result:
                    actual_columns[row[0]] = {
                        'type': row[1],
                        'nullable': row[2] == 'YES',
                        'has_default': row[3] is not None
                    }

                # Compare columns
                missing_columns = set(expected_columns.keys()) - set(actual_columns.keys())
                extra_columns = set(actual_columns.keys()) - set(expected_columns.keys())

                if missing_columns or extra_columns:
                    print(f"⚠️  Schema mismatch in table '{table_name}':")

                    if missing_columns:
                        print(f"    Missing columns ({len(missing_columns)}):")
                        for col in sorted(missing_columns):
                            col_info = expected_columns[col]
                            print(f"      - {col}: {col_info['type']}")
                        mismatches_found = True

                    if extra_columns:
                        print(f"    Extra columns ({len(extra_columns)}):")
                        for col in sorted(extra_columns):
                            print(f"      - {col}")

                    print()
                else:
                    print(f"✅ Table '{table_name}': All {len(expected_columns)} columns match")

            except Exception as e:
                print(f"❌ Error checking table '{table_name}': {e}")
                print()
                mismatches_found = True

    print()
    print("=" * 80)

    if mismatches_found:
        print("⚠️  SCHEMA MISMATCHES DETECTED")
        print()
        print("Some tables or columns are missing from the database.")
        print("Review the output above and apply necessary migrations.")
    else:
        print("✅ SCHEMA VALIDATION PASSED")
        print()
        print("All tables and columns match the expected schema.")

    print("=" * 80)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return not mismatches_found


if __name__ == '__main__':
    try:
        success = check_schema()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print()
        print("Validation cancelled by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print()
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
