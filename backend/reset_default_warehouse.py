
import os
import sys
from flask import Flask
from sqlalchemy.orm.exc import NoResultFound

# Add the src directory to the Python path to allow direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import db
from models import Location, WarehouseConfig

def create_minimal_app():
    """Create a minimal Flask app instance for context."""
    app = Flask(__name__)
    # Configure the database URI. Default to a local SQLite DB if not set.
    # This should match the configuration in your main app for consistency.
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def reset_warehouse_data(warehouse_id: str):
    """
    Deletes all locations and the configuration for a specific warehouse_id.
    """
    app = create_minimal_app()
    with app.app_context():
        print(f"--- Starting reset for warehouse_id: {warehouse_id} ---")

        # 1. Delete all locations associated with the warehouse
        try:
            locations_deleted = Location.query.filter_by(warehouse_id=warehouse_id).delete()
            print(f"Found and deleted {locations_deleted} locations.")
        except Exception as e:
            print(f"Error deleting locations: {e}")
            db.session.rollback()
            return

        # 2. Delete the warehouse configuration itself
        try:
            config_to_delete = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).one()
            db.session.delete(config_to_delete)
            print(f"Found and deleted warehouse configuration for '{config_to_delete.warehouse_name}'.")
        except NoResultFound:
            print("No warehouse configuration found to delete.")
            # If config doesn't exist, we can still commit the location deletion
        except Exception as e:
            print(f"Error deleting warehouse configuration: {e}")
            db.session.rollback()
            return

        # 3. Commit the transaction
        try:
            db.session.commit()
            print("--- Reset complete. All changes have been committed. ---")
        except Exception as e:
            print(f"Error committing changes to the database: {e}")
            db.session.rollback()

if __name__ == "__main__":
    # The ID of the warehouse to reset.
    WAREHOUSE_ID_TO_RESET = "DEFAULT"
    reset_warehouse_data(WAREHOUSE_ID_TO_RESET)
