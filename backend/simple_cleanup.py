#!/usr/bin/env python3
"""
Simple rule cleanup - deactivate the remaining 2 custom rules
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from database import db
from models import Rule

with app.app_context():
    print("Deactivating remaining custom rules...")
    
    # Deactivate Rule 9 and Rule 13 (the remaining active custom rules)
    custom_rules = [9, 13]
    
    for rule_id in custom_rules:
        rule = Rule.query.get(rule_id)
        if rule and rule.is_active:
            rule.is_active = False
            print(f"Deactivated Rule {rule_id}: {rule.name}")
    
    db.session.commit()
    
    # Verify final state
    active_rules = Rule.query.filter_by(is_active=True).all()
    print(f"\nFinal result: {len(active_rules)} active rules")
    
    for rule in active_rules:
        print(f"  {rule.id}: {rule.name}")
    
    print("\nSuccess! You now have exactly the 8 default rules active.")