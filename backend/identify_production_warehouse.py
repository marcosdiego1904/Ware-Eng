#!/usr/bin/env python3
"""
Identify Production Warehouse for Smart Configuration Setup

This script helps identify which warehouse in your production database
needs Smart Configuration applied to resolve the invalid location issues.
"""

import sys
import os
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def identify_production_warehouse():
    """Identify which warehouse needs Smart Configuration"""
    print("=" * 60)
    print("IDENTIFYING PRODUCTION WAREHOUSE FOR SMART CONFIGURATION")
    print("=" * 60)
    
    try:
        from app import app, db
        from models import WarehouseConfig
        
        with app.app_context():
            print(f"Database engine: {db.engine.dialect.name}")
            
            # Get all warehouse configurations
            warehouses = WarehouseConfig.query.filter_by(is_active=True).all()
            
            print(f"\nFound {len(warehouses)} active warehouses:")
            print("-" * 50)
            
            for i, warehouse in enumerate(warehouses, 1):
                print(f"{i}. Warehouse ID: {warehouse.warehouse_id}")
                print(f"   Name: {warehouse.warehouse_name}")
                print(f"   Created: {warehouse.created_at}")
                print(f"   Has Smart Config: {'Yes' if warehouse.location_format_config else 'No'}")
                
                if warehouse.location_format_config:
                    import json
                    try:
                        config = json.loads(warehouse.location_format_config)
                        print(f"   Format Type: {config.get('pattern_type', 'unknown')}")
                    except:
                        print(f"   Format Type: invalid JSON")
                print()
            
            # Recommend which warehouse to configure
            unconfigured = [w for w in warehouses if not w.location_format_config]
            
            if unconfigured:
                print("RECOMMENDATION:")
                print("The following warehouses need Smart Configuration:")
                for warehouse in unconfigured:
                    print(f"  - {warehouse.warehouse_id} ({warehouse.warehouse_name})")
                
                if len(unconfigured) == 1:
                    target = unconfigured[0]
                    print(f"\nRECOMMENDED ACTION:")
                    print(f"Apply Smart Configuration to: {target.warehouse_id}")
                    return target.warehouse_id
            else:
                print("All warehouses already have Smart Configuration!")
                return None
                
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    warehouse_id = identify_production_warehouse()
    if warehouse_id:
        print(f"\nNext: Apply Smart Configuration to warehouse '{warehouse_id}'")
    else:
        print(f"\nNo action needed - all warehouses configured")