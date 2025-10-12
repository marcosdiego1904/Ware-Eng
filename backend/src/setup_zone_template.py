"""
Script to create or update WarehouseTemplate for USER_MTEST with proper zone-based location format
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_zone_based_template():
    """Create/update template for USER_MTEST with zone-based configuration"""
    print("=== Setting up Zone-Based Template for USER_MTEST ===")

    try:
        from flask import Flask
        from models import db, WarehouseTemplate

        # Create Flask app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(app)

        with app.app_context():
            print("1. Checking existing template...")

            # Check if template already exists
            existing_template = WarehouseTemplate.query.filter_by(warehouse_id='USER_MTEST').first()

            if existing_template:
                print(f"   Found existing template: {existing_template.name}")
                print(f"   Current format config: {existing_template.location_format_config}")
                template = existing_template
            else:
                print("   No existing template found, creating new one...")

                # Create new template
                template = WarehouseTemplate(
                    name='USER_MTEST Zone-Based Template',
                    description='Zone-based warehouse template with PICK/BULK/OVER/CASE/EACH zones',
                    warehouse_id='USER_MTEST',
                    template_code='ZONE-MTEST-001',
                    num_aisles=5,
                    racks_per_aisle=20,
                    positions_per_rack=50,
                    levels_per_position=4,
                    level_names='ABCDE',
                    default_pallet_capacity=1,
                    is_active=True,
                    is_public=False,
                    created_by=1,  # Assuming user ID 1 exists
                    created_at=datetime.utcnow()
                )

                db.session.add(template)

            print("2. Setting up zone-based location format configuration...")

            # Define zone-based location format configuration
            zone_format_config = {
                "pattern_type": "zone_based",
                "confidence": 0.95,
                "format_name": "Zone-Level-Position (ZONE-L-NNN)",
                "description": "Zone-based format with business zones, level letter, and 3-digit position",
                "example_locations": [
                    "PICK-A-001", "BULK-B-150", "OVER-C-075",
                    "CASE-D-200", "EACH-E-300", "TRAN-A-150"
                ],
                "business_zones": [
                    "PICK",   # Picking zones
                    "BULK",   # Bulk storage
                    "OVER",   # Oversize items
                    "CASE",   # Case picking
                    "EACH"    # Each picking
                ],
                "transitional_zones": [
                    "TRAN",     # Transitional areas
                    "FLOW",     # Flow areas
                    "TRANSIT"   # Transit areas
                ],
                "receiving_zones": [
                    "RECV",       # Receiving areas
                    "RECEIVING"   # Full receiving name
                ],
                "staging_zones": [
                    "STAGE",    # Staging areas
                    "STAGING"   # Full staging name
                ],
                "dock_zones": [
                    "DOCK",     # Dock areas
                    "DOCKING"   # Full dock name
                ],
                "special_zones": [
                    "NOWHERE",  # Problem locations
                    "QUARANTINE",
                    "HOLD"
                ],
                "level_pattern": "[A-Z]",          # Single letter level
                "position_pattern": "\\d{3}",      # 3-digit position
                "separator": "-",                  # Separator character
                "full_pattern": "^[A-Z]+-[A-Z]-\\d{3}$",  # Complete regex pattern
                "validation_rules": {
                    "min_position": 1,
                    "max_position": 999,
                    "allowed_levels": ["A", "B", "C", "D", "E"],
                    "case_sensitive": True
                }
            }

            # Set the location format configuration
            template.set_location_format_config(zone_format_config)
            template.format_confidence = 0.95

            # Set format examples
            format_examples = [
                "PICK-A-001", "PICK-A-150", "BULK-B-075",
                "OVER-C-200", "CASE-D-100", "EACH-E-250",
                "TRAN-A-150", "RECV-01", "STAGE-05"
            ]
            template.set_format_examples(format_examples)

            # Update metadata
            template.format_learned_date = datetime.utcnow()

            print("3. Saving template to database...")

            try:
                db.session.commit()
                print("   ✅ Template saved successfully!")

                # Verify the configuration
                print("4. Verifying template configuration...")
                saved_config = template.get_location_format_config()
                print(f"   Pattern type: {saved_config.get('pattern_type')}")
                print(f"   Confidence: {template.format_confidence}")
                print(f"   Business zones: {saved_config.get('business_zones')}")
                print(f"   Full pattern: {saved_config.get('full_pattern')}")

                print("\n5. Testing pattern matching...")

                # Test pattern matching
                import re
                full_pattern = saved_config.get('full_pattern')
                test_locations = [
                    'PICK-A-001', 'BULK-B-150', 'OVER-C-075',
                    'CASE-D-200', 'EACH-E-300', 'TRAN-A-150',
                    '400A', 'NOWHERE-01', 'invalid-location'
                ]

                print(f"   Testing pattern: {full_pattern}")
                for location in test_locations:
                    match = re.match(full_pattern, location)
                    status = "✅ MATCH" if match else "❌ NO MATCH"
                    print(f"   {location}: {status}")

            except Exception as e:
                print(f"   ❌ Error saving template: {e}")
                db.session.rollback()
                raise

    except Exception as e:
        print(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()

def test_pattern_resolver_after_setup():
    """Test pattern resolver after template setup"""
    print(f"\n=== Testing Pattern Resolver After Setup ===")

    try:
        from rule_pattern_resolver import RulePatternResolver
        from unittest.mock import Mock

        # Create resolver with mock Flask app
        mock_db = Mock()

        # Create actual Flask app for template queries
        from flask import Flask
        from models import db

        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        resolver = RulePatternResolver(mock_db, app)

        warehouse_context = {
            'warehouse_id': 'USER_MTEST',
            'detection_method': 'explicit_template'
        }

        print("1. Testing pattern resolution...")
        patterns = resolver.get_patterns_for_rule('LOCATION_SPECIFIC_STAGNANT', warehouse_context)

        print(f"   Pattern source: {patterns.source}")
        print(f"   Confidence: {patterns.confidence}")
        print(f"   Storage patterns: {patterns.storage_patterns}")
        print(f"   Transitional patterns: {patterns.transitional_patterns}")

        if patterns.source == 'zone_based_template':
            print("   ✅ SUCCESS: Using zone-based template patterns!")
        else:
            print("   ❌ Still using fallback patterns")

    except Exception as e:
        print(f"Pattern resolver test failed: {e}")

if __name__ == '__main__':
    setup_zone_based_template()
    test_pattern_resolver_after_setup()

    print(f"\n=== Summary ===")
    print("Template setup complete. The pattern resolver should now:")
    print("1. Find the USER_MTEST template in the database")
    print("2. Load zone-based location format configuration")
    print("3. Generate proper patterns that match PICK-A-001, BULK-B-150, etc.")
    print("4. Rules #5 and #8 should now detect anomalies correctly!")
    print(f"\nNext step: Re-run your test to see Rules #5 and #8 working correctly.")