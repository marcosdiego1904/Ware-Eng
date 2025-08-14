#!/usr/bin/env python3
"""
Debug incomplete lots detection
"""
import sys
import os
sys.path.append('backend/src')

from models import db, Rule
from app import app
import pandas as pd

def debug_incomplete_lots():
    """Debug incomplete lots detection"""
    
    with app.app_context():
        # Load test inventory
        df = pd.read_excel('CentralDC_Compact_Inventory.xlsx', sheet_name='Inventory')
        
        print("=== INCOMPLETE LOTS ANALYSIS ===")
        
        # Group by receipt number
        receipt_groups = df.groupby('receipt_number')
        
        print(f"Total receipt numbers: {len(receipt_groups)}")
        
        # Check for incomplete lots
        incomplete_lots = []
        for receipt, group in receipt_groups:
            location_types = group['location_type'].unique()
            if len(location_types) > 1:
                incomplete_lots.append({
                    'receipt': receipt,
                    'total_pallets': len(group),
                    'location_types': list(location_types),
                    'locations': list(group['location'].unique())
                })
        
        print(f"Found {len(incomplete_lots)} incomplete lots:")
        for lot in incomplete_lots:
            print(f"  Receipt {lot['receipt']}: {lot['total_pallets']} pallets across {lot['location_types']}")
            print(f"    Locations: {lot['locations'][:3]}{'...' if len(lot['locations']) > 3 else ''}")
        
        # Check the rule conditions
        incomplete_rule = Rule.query.filter_by(name='Incomplete Lots Alert').first()
        if incomplete_rule:
            print(f"\nIncomplete Lots Rule: {incomplete_rule.name}")
            print(f"Type: {incomplete_rule.rule_type}")
            print(f"Conditions: {incomplete_rule.conditions}")
            print(f"Active: {incomplete_rule.is_active}")
            
            # Parse conditions
            import json
            conditions = json.loads(incomplete_rule.conditions)
            completion_threshold = conditions.get('completion_threshold', 0.8)
            location_types = conditions.get('location_types', ['RECEIVING'])
            
            print(f"\nRule looks for:")
            print(f"- Completion threshold: {completion_threshold}")
            print(f"- Location types: {location_types}")
            
            # Check if our incomplete lots match the rule criteria
            print("\n=== RULE MATCH ANALYSIS ===")
            matching_lots = 0
            for lot in incomplete_lots:
                # Check if any location types match the rule criteria
                has_target_type = any(loc_type in location_types for loc_type in lot['location_types'])
                print(f"Receipt {lot['receipt']}: Target types {location_types} in {lot['location_types']} = {has_target_type}")
                if has_target_type:
                    matching_lots += 1
            
            print(f"Lots matching rule criteria: {matching_lots}")
        else:
            print("Incomplete Lots Alert rule not found!")

if __name__ == "__main__":
    debug_incomplete_lots()