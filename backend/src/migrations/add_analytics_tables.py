"""
Database Migration: Add Analytics Tables for Pilot Program Monitoring

Run this migration to create the analytics tracking tables:
- analytics_events
- analytics_sessions
- analytics_file_uploads
- analytics_anomalies
- analytics_time_savings

Usage:
    From the backend directory:
    python -c "from src.migrations.add_analytics_tables import run_migration; run_migration()"

    Or from backend/src:
    python -c "from migrations.add_analytics_tables import run_migration; run_migration()"
"""

import os
import sys
import logging

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Create all analytics tables and add is_admin column"""
    try:
        # Import database and models
        from database import db
        from analytics_models import (
            AnalyticsEvent,
            AnalyticsSession,
            AnalyticsFileUpload,
            AnalyticsAnomaly,
            AnalyticsTimeSavings
        )
        from core_models import User, AnalysisReport, Anomaly
        # Import WarehouseConfig so SQLAlchemy knows about the table
        from models import WarehouseConfig

        logger.info("Starting analytics tables migration...")

        # Create Flask app to get db context
        from flask import Flask
        from dotenv import load_dotenv

        load_dotenv()

        app = Flask(__name__)

        # Database configuration
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # Fix postgres:// to postgresql:// for SQLAlchemy
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        else:
            # Fallback to SQLite for development
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'

        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize db with app
        db.init_app(app)

        with app.app_context():
            # Create all analytics tables
            db.create_all()

            logger.info("Successfully created analytics tables:")
            logger.info("  [OK] analytics_events")
            logger.info("  [OK] analytics_sessions")
            logger.info("  [OK] analytics_file_uploads")
            logger.info("  [OK] analytics_anomalies")
            logger.info("  [OK] analytics_time_savings")

            # Check if is_admin column exists, if not add it
            try:
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                columns = [col['name'] for col in inspector.get_columns('user')]

                if 'is_admin' not in columns:
                    logger.info("Adding is_admin column to user table...")
                    with db.engine.connect() as conn:
                        conn.execute(text('ALTER TABLE "user" ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL'))
                        conn.commit()
                    logger.info("  [OK] is_admin column added")
                else:
                    logger.info("  [INFO] is_admin column already exists")

            except Exception as e:
                logger.warning(f"Could not check/add is_admin column: {e}")
                logger.info("You may need to manually add: ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL")

            print("\n[SUCCESS] Analytics tables migration completed successfully!")
            print("You can now start tracking pilot program metrics.")
            return True

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n[ERROR] Migration failed. Check logs for details.")
        return False


if __name__ == "__main__":
    run_migration()
