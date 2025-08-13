#!/usr/bin/env python3
"""
Debug location validation issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from models import Rule, Location

with app.app_context():
    print('=== LOCATION VALIDATION DEBUG ===')
    
    # 1. Clean up Rule 47 if it exists
    rule47 = Rule.query.get(47)
    if rule47:
        print(f'Rule 47 found: {rule47.name} (Active: {rule47.is_active})')
        if rule47.is_active:
            rule47.is_active = False
            db.session.commit()
            print('✓ Deactivated Rule 47')
    
    # 2. Check location validation query
    test_locations = ['HOLA2_RECV-2', 'RECEIVING', '001A']
    
    print('\n=== TESTING LOCATION QUERIES ===')
    
    # Test the actual query used in InvalidLocationEvaluator
    from sqlalchemy import or_
    locations = Location.query.filter(
        or_(Location.is_active == True, Location.is_active.is_(None))
    ).all()
    
    valid_location_codes = {loc.code for loc in locations}
    print(f'Total valid locations found: {len(valid_location_codes)}')
    
    print('\nTesting our specific locations:')
    for test_loc in test_locations:
        # Check if in valid set
        in_valid_set = test_loc in valid_location_codes
        
        # Check database record
        loc_obj = Location.query.filter_by(code=test_loc).first()
        
        if in_valid_set:
            print(f'  ✓ {test_loc}: FOUND in valid locations')
        else:
            print(f'  ✗ {test_loc}: NOT FOUND in valid locations')
            
        if loc_obj:
            print(f'    DB: is_active={loc_obj.is_active}, type={loc_obj.location_type}')
        else:
            print(f'    DB: No record found')
            
    # 3. Check if InvalidLocationEvaluator is using the updated code
    print('\n=== CHECKING RULE_ENGINE.PY ===')
    
    try:
        with open('src/rule_engine.py', 'r') as f:
            content = f.read()
            if 'or_(Location.is_active == True, Location.is_active.is_(None))' in content:
                print('✓ rule_engine.py has the updated location query')
            else:
                print('✗ rule_engine.py does not have the updated query')
                
                # Check what query it does have
                if 'Location.query.filter_by(is_active=True)' in content:
                    print('  Found old query: filter_by(is_active=True)')
                else:
                    print('  Unknown query format in file')
    except Exception as e:
        print(f'Error reading rule_engine.py: {e}')
    
    # 4. Final active rules check
    print('\n=== ACTIVE RULES CHECK ===')
    active_rules = Rule.query.filter_by(is_active=True).all()
    print(f'Total active rules: {len(active_rules)}')
    for rule in active_rules:
        print(f'  {rule.id}: {rule.name}')