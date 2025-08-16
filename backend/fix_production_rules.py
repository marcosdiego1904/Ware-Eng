#!/usr/bin/env python3
"""
Fix production database rules to match development configuration.
This script should be run in the production environment.
"""
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def fix_production_rules():
    """Update production database rules to correct values"""
    try:
        from app import app, db
        from models import Rule
        
        print("Fixing Production Database Rules...")
        print("=" * 50)
        
        with app.app_context():
            # Check current environment
            is_production = os.environ.get('RENDER') == 'true' or os.environ.get('VERCEL') == '1'
            database_url = os.environ.get('DATABASE_URL')
            
            print(f"Environment: {'PRODUCTION' if is_production else 'DEVELOPMENT'}")
            print(f"Database URL set: {'YES' if database_url else 'NO'}")
            
            # Allow running in development for testing, but warn
            if not is_production:
                print("[WARNING] Running in development environment!")
                print("This will update your local database.")
                response = input("Continue? (y/N): ")
                if response.lower() != 'y':
                    return False
            
            # Fix Rule ID 1: Forgotten Pallets Alert
            rule1 = Rule.query.filter_by(id=1).first()
            if rule1:
                current_conditions = json.loads(rule1.conditions) if isinstance(rule1.conditions, str) else rule1.conditions
                print(f"\nRule 1 BEFORE: {rule1.name}")
                print(f"  Current conditions: {json.dumps(current_conditions, indent=2)}")
                
                # Update to correct configuration
                new_conditions = {
                    "time_threshold_hours": 10,
                    "location_types": ["RECEIVING"]
                }
                
                rule1.conditions = json.dumps(new_conditions)
                db.session.commit()
                
                print(f"  NEW conditions: {json.dumps(new_conditions, indent=2)}")
                print(f"  [SUCCESS] Rule 1 updated successfully!")
            else:
                print("[ERROR] Rule ID 1 not found!")
                return False
            
            # Verify all STAGNANT_PALLETS rules
            print(f"\nVerifying all STAGNANT_PALLETS rules:")
            stagnant_rules = Rule.query.filter_by(rule_type='STAGNANT_PALLETS', is_active=True).all()
            for rule in stagnant_rules:
                conditions = json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions
                threshold = conditions.get('time_threshold_hours', 'NOT SET')
                location_types = conditions.get('location_types', [])
                print(f"  Rule {rule.id}: {threshold}h for {location_types}")
            
            print(f"\n[SUCCESS] Production rules updated successfully!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed to update production rules: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_production_rules()
    if success:
        print("\n[SUCCESS] Production database rules have been fixed!")
        print("The next analysis should use the correct 10-hour threshold.")
    else:
        print("\n[ERROR] Failed to update production database rules.")
        sys.exit(1)