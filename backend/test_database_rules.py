#!/usr/bin/env python3
"""
Test script to verify database rules connectivity and configuration.
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import app, db
    from models import Rule
    
    print("Testing Database Rules Configuration...")
    print("=" * 50)
    
    # Test app context
    with app.app_context():
        # Test database connectivity
        try:
            rule_count = Rule.query.count()
            print(f"[SUCCESS] Database connectivity: OK")
            print(f"[INFO] Rules in database: {rule_count}")
            
            if rule_count > 0:
                # Show first few rules
                rules = Rule.query.limit(3).all()
                print("\nSample rules:")
                for rule in rules:
                    print(f"  - {rule.name} ({rule.rule_type}) - Active: {rule.is_active}")
                    print(f"    Conditions: {rule.conditions}")
            else:
                print("[WARNING] No rules found in database. Database migration may be needed.")
                
        except Exception as e:
            print(f"[ERROR] Database connectivity: FAILED")
            print(f"Error: {e}")
            
    # Test fallback configuration
    print(f"\nConfiguration:")
    print(f"ALLOW_EXCEL_FALLBACK: {os.getenv('ALLOW_EXCEL_FALLBACK', 'false')}")
    
    # Check if Excel backup exists
    excel_backup = os.path.join(os.path.dirname(__file__), 'data', 'warehouse_rules.xlsx.backup')
    excel_original = os.path.join(os.path.dirname(__file__), 'data', 'warehouse_rules.xlsx')
    
    print(f"Excel fallback file (backup): {'EXISTS' if os.path.exists(excel_backup) else 'NOT FOUND'}")
    print(f"Excel original file: {'EXISTS (FALLBACK TRIGGER!)' if os.path.exists(excel_original) else 'NOT FOUND (GOOD)'}")
    
    print("\n[SUCCESS] Configuration Test Complete!")
    
except ImportError as e:
    print(f"[ERROR] Import Error: {e}")
    print("Make sure you're in the backend directory and dependencies are installed.")
except Exception as e:
    print(f"[ERROR] Unexpected Error: {e}")