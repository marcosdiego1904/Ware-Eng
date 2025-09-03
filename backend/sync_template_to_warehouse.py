#!/usr/bin/env python3
"""
Sync Smart Configuration from Template to Warehouse

This script copies the Smart Configuration from a template (like s10)
to the warehouse configuration (like DEFAULT) that the rule engine uses.
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def sync_template_to_warehouse(template_name, warehouse_id):
    """Sync Smart Configuration from template to warehouse"""
    
    # Force PostgreSQL connection
    os.environ['DATABASE_URL'] = "postgresql://ware_eng_db_user:fqvKdOGZEt1CGIeLF4J1AG8RTtCv0Zdu@dpg-d23244fg127c73fga10g-a.ohio-postgres.render.com/ware_eng_db"
    
    print("=" * 70)
    print("SYNCING TEMPLATE SMART CONFIGURATION TO WAREHOUSE")
    print("=" * 70)
    print(f"Source template: {template_name}")
    print(f"Target warehouse: {warehouse_id}")
    print(f"Using DATABASE_URL: PostgreSQL")
    
    try:
        from app import app, db
        from models import WarehouseTemplate, WarehouseConfig
        
        # Force the app to use PostgreSQL by overriding the config
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
        
        with app.app_context():
            print(f"Database engine: {db.engine.dialect.name}")
            
            # Get the source template
            template = WarehouseTemplate.query.filter_by(name=template_name).first()
            
            if not template:
                print(f"ERROR: Template '{template_name}' not found!")
                return False
            
            print(f"Found template: {template.name} (ID: {template.id})")
            
            # Check if template has Smart Configuration
            if not template.location_format_config:
                print(f"ERROR: Template '{template_name}' has no Smart Configuration!")
                return False
            
            template_config = json.loads(template.location_format_config)
            print(f"Template format config: {template_config.get('pattern_type', 'unknown')} pattern")
            print(f"Template confidence: {template.format_confidence:.2%}")
            
            # Get the target warehouse
            warehouse = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            
            if not warehouse:
                print(f"ERROR: Warehouse '{warehouse_id}' not found!")
                return False
            
            print(f"Found warehouse: {warehouse.warehouse_name}")
            
            # Copy Smart Configuration from template to warehouse
            warehouse.location_format_config = template.location_format_config
            warehouse.format_confidence = template.format_confidence
            warehouse.format_examples = template.format_examples
            warehouse.format_learned_date = datetime.now()
            
            db.session.commit()
            
            print("\\nSUCCESS: Smart Configuration synced!")
            print("-" * 40)
            print(f"Copied from template '{template_name}' to warehouse '{warehouse_id}':")
            print(f"  - Pattern type: {template_config.get('pattern_type', 'unknown')}")
            print(f"  - Regex pattern: {template_config.get('regex_pattern', 'unknown')}")
            print(f"  - Confidence: {template.format_confidence:.2%}")
            print(f"  - Examples: {template.format_examples}")
            
            return True
            
    except Exception as e:
        print(f"ERROR: Sync failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python sync_template_to_warehouse.py TEMPLATE_NAME WAREHOUSE_ID")
        print("Example: python sync_template_to_warehouse.py s10 DEFAULT")
        sys.exit(1)
    
    template_name = sys.argv[1]
    warehouse_id = sys.argv[2]
    
    success = sync_template_to_warehouse(template_name, warehouse_id)
    
    if success:
        print(f"\\nNext: Test your rule engine - it should now use {template_name}'s format config!")
    else:
        print(f"\\nFailed to sync. Check the error above.")