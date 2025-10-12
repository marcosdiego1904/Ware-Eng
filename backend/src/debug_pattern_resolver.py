"""
Debug script to investigate why pattern resolution is failing for USER_MTEST
"""

import sys
import os
from unittest.mock import Mock

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_pattern_resolver():
    """Debug pattern resolution for USER_MTEST warehouse"""
    print("=== Pattern Resolver Debug Session ===")

    try:
        from rule_pattern_resolver import RulePatternResolver, PatternSet

        # Create mock dependencies
        mock_db = Mock()
        mock_app = Mock()

        # Create resolver
        resolver = RulePatternResolver(mock_db, mock_app)

        print(f"1. Testing warehouse ID extraction...")

        warehouse_contexts = [
            {'warehouse_id': 'USER_MTEST', 'detection_method': 'explicit_template'},
            {'warehouse_id': 'USER_MTEST'},
            {'warehouse': 'USER_MTEST'},
            {'detection_method': 'USER_MTEST'},
        ]

        for i, context in enumerate(warehouse_contexts):
            warehouse_id = resolver._extract_warehouse_id(context)
            print(f"   Context {i+1}: {context} -> warehouse_id: {warehouse_id}")

        print(f"\n2. Testing template config retrieval...")

        # Test template config retrieval
        try:
            config = resolver._get_template_config('USER_MTEST')
            print(f"   Template config for USER_MTEST: {config}")

            if config is None:
                print(f"   >>> Template config is None - this explains fallback to default patterns!")
                print(f"   >>> Check if WarehouseTemplate exists for warehouse_id='USER_MTEST'")

        except Exception as e:
            print(f"   Template config error: {e}")

        print(f"\n3. Testing pattern resolution...")

        test_context = {'warehouse_id': 'USER_MTEST', 'detection_method': 'explicit_template'}

        try:
            patterns = resolver.get_patterns_for_rule('LOCATION_SPECIFIC_STAGNANT', test_context)
            print(f"   Pattern source: {patterns.source}")
            print(f"   Confidence: {patterns.confidence}")
            print(f"   Storage patterns: {patterns.storage_patterns}")
            print(f"   Transitional patterns: {patterns.transitional_patterns}")

            if patterns.source == 'default_fallback':
                print(f"   >>> PROBLEM: Using fallback patterns instead of template-based patterns!")

        except Exception as e:
            print(f"   Pattern resolution error: {e}")

        print(f"\n4. Testing zone-based pattern generation manually...")

        # Test zone-based pattern generation manually
        test_template_config = {
            'pattern_type': 'zone_based',
            'confidence': 0.95,
            'business_zones': ['PICK', 'BULK', 'OVER', 'CASE', 'EACH'],
            'transitional_zones': ['TRAN', 'FLOW', 'TRANSIT']
        }

        try:
            manual_patterns = resolver._convert_template_to_patterns(test_template_config, 'LOCATION_SPECIFIC_STAGNANT')
            print(f"   Manual zone-based patterns:")
            print(f"     Source: {manual_patterns.source}")
            print(f"     Storage: {manual_patterns.storage_patterns}")
            print(f"     Transitional: {manual_patterns.transitional_patterns}")

            # Test if these patterns would match our test locations
            test_locations = ['PICK-A-001', 'BULK-B-002', 'OVER-C-003', 'TRAN-A-150']

            import re
            print(f"   Testing pattern matching:")
            for pattern in manual_patterns.storage_patterns:
                print(f"     Pattern: {pattern}")
                for location in test_locations:
                    match = re.match(pattern, location)
                    print(f"       {location}: {'MATCH' if match else 'NO MATCH'}")

        except Exception as e:
            print(f"   Manual pattern generation error: {e}")

    except Exception as e:
        print(f"Error during debug: {e}")
        import traceback
        traceback.print_exc()

def check_database_templates():
    """Check if database has templates for USER_MTEST"""
    print(f"\n=== Database Template Check ===")

    try:
        # Try to create a basic Flask app context to query the database
        from flask import Flask
        from models import db, WarehouseTemplate

        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(app)

        with app.app_context():
            # Check if WarehouseTemplate table exists
            try:
                templates = WarehouseTemplate.query.filter_by(warehouse_id='USER_MTEST').all()
                print(f"Found {len(templates)} templates for USER_MTEST")

                for template in templates:
                    print(f"  Template ID: {template.id}")
                    print(f"  Name: {template.name}")
                    print(f"  Active: {template.is_active}")
                    print(f"  Location format config: {template.location_format_config}")

                if not templates:
                    print(">>> NO TEMPLATES FOUND - This explains the fallback behavior!")
                    print(">>> The pattern resolver can't find template configuration for USER_MTEST")

            except Exception as e:
                print(f"Error querying templates: {e}")

    except Exception as e:
        print(f"Database check failed: {e}")

if __name__ == '__main__':
    debug_pattern_resolver()
    check_database_templates()

    print(f"\n=== Conclusion ===")
    print("If template config is None and no database templates exist,")
    print("then the pattern resolver correctly falls back to default patterns.")
    print("The solution is to ensure USER_MTEST has a proper zone-based template configuration.")