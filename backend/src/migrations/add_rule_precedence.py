#!/usr/bin/env python3
"""
Migration script to add rule precedence system
Adds precedence_level and exclusion_rules columns to rules table
Sets default precedence levels based on rule types
"""

import os
import sys
from sqlalchemy import text

# Add the backend src directory to the path
backend_src = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_src)

from app import app
from database import db
from models import Rule

def add_precedence_columns():
    """Add precedence_level and exclusion_rules columns to rules table"""
    
    # Note: In a production environment, this would be handled by Alembic migrations
    # For this implementation, we'll use raw SQL to add the columns
    
    try:
        with db.engine.connect() as conn:
            # Add precedence_level column (default 4 = lowest priority)
            try:
                conn.execute(text("""
                    ALTER TABLE rule 
                    ADD COLUMN precedence_level INTEGER DEFAULT 4
                """))
                print("Added precedence_level column")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print("WARNING: precedence_level column already exists")
                else:
                    raise e
            
            # Add exclusion_rules column
            try:
                conn.execute(text("""
                    ALTER TABLE rule 
                    ADD COLUMN exclusion_rules TEXT
                """))
                print("Added exclusion_rules column")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print("WARNING: exclusion_rules column already exists")
                else:
                    raise e
            
            conn.commit()
            
    except Exception as e:
        print(f"ERROR: Error adding columns: {e}")
        return False
    
    return True

def set_default_precedence_levels():
    """Set default precedence levels for existing rules based on rule types"""
    
    # Precedence hierarchy (lower number = higher precedence)
    rule_type_precedence = {
        # P1 - Data Integrity (Highest Precedence)
        'INVALID_LOCATION': 1,
        'DATA_INTEGRITY': 1,
        
        # P2 - Operational Safety  
        'OVERCAPACITY': 2,
        'TEMPERATURE_ZONE_MISMATCH': 2,
        
        # P3 - Process Efficiency
        'STAGNANT_PALLETS': 3,
        'UNCOORDINATED_LOTS': 3,
        'LOCATION_SPECIFIC_STAGNANT': 3,
        
        # P4 - Data Quality (Lowest Precedence)
        'LOCATION_MAPPING_ERROR': 4
    }
    
    # Default exclusion patterns for specific rule combinations
    default_exclusions = {
        'OVERCAPACITY': {
            'exclude_if_flagged_by': ['INVALID_LOCATION', 'DATA_INTEGRITY'],
            'reason': 'Invalid locations cannot have capacity constraints'
        },
        'LOCATION_MAPPING_ERROR': {
            'exclude_if_flagged_by': ['INVALID_LOCATION'],
            'reason': 'Invalid locations already flagged for location issues'
        }
    }
    
    try:
        rules = Rule.query.all()
        updated_count = 0
        
        for rule in rules:
            # Set precedence level based on rule type
            precedence = rule_type_precedence.get(rule.rule_type, 4)  # Default to lowest
            rule.precedence_level = precedence
            
            # Set default exclusion rules if applicable
            if rule.rule_type in default_exclusions:
                rule.set_exclusion_rules(default_exclusions[rule.rule_type])
            
            updated_count += 1
            print(f"Updated rule '{rule.name}' (type: {rule.rule_type}) -> precedence: {precedence}")
        
        db.session.commit()
        print(f"\nSuccessfully updated {updated_count} rules with precedence levels")
        
        # Show summary by precedence level
        print("\nPrecedence level summary:")
        for level in range(1, 5):
            count = Rule.query.filter_by(precedence_level=level).count()
            level_name = {
                1: "Data Integrity",
                2: "Operational Safety", 
                3: "Process Efficiency",
                4: "Data Quality"
            }.get(level, f"Level {level}")
            print(f"  Level {level} ({level_name}): {count} rules")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error setting precedence levels: {e}")
        db.session.rollback()
        return False

def main():
    """Run the migration"""
    print("Starting Rule Precedence Migration")
    print("=" * 50)
    
    # Use app context
    with app.app_context():
        
        # Step 1: Add columns
        print("Step 1: Adding precedence columns to rules table...")
        if not add_precedence_columns():
            print("ERROR: Failed to add columns. Aborting migration.")
            return
        
        # Step 2: Set default precedence levels
        print("\nStep 2: Setting default precedence levels...")
        if not set_default_precedence_levels():
            print("ERROR: Failed to set precedence levels. Columns were added but values not set.")
            return
        
        print("\n" + "=" * 50)
        print("Rule Precedence Migration Complete!")
        print("\nNext steps:")
        print("1. Test rule precedence system with existing inventory")
        print("2. Verify double-counting is eliminated")  
        print("3. Update rule management interface to show precedence")

if __name__ == "__main__":
    main()