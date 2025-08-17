#!/usr/bin/env python3
"""
Check all warehouses in database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location

def check_all_warehouses():
    """Check all warehouses in database"""
    
    with app.app_context():
        total_locations = db.session.query(Location).count()
        print(f'Total locations in database: {total_locations}')
        
        warehouses = db.session.query(Location.warehouse_id, db.func.count(Location.id)).group_by(Location.warehouse_id).all()
        print('Warehouse distribution:')
        for warehouse_id, count in warehouses:
            print(f'  {warehouse_id}: {count}')
            
        # Show some samples from each warehouse
        for warehouse_id, count in warehouses:
            print(f'\nSample locations from {warehouse_id}:')
            samples = db.session.query(Location.code).filter(
                Location.warehouse_id == warehouse_id
            ).limit(5).all()
            for location in samples:
                print(f'  {location.code}')

if __name__ == '__main__':
    check_all_warehouses()