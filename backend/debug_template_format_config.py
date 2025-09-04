#!/usr/bin/env python3
"""
Debug script to investigate template format configuration persistence issue
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import json
from datetime import datetime
from database import db
from models import WarehouseTemplate
from core_models import User

def debug_user_templates(username='mtest'):
    """Debug templates for a specific user"""
    
    print(f"🔍 Debugging Templates for User: {username}")
    print("=" * 60)
    
    try:
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found")
            return
        
        print(f"✅ Found user: {user.username} (ID: {user.id})")
        
        # Get all templates for this user
        templates = WarehouseTemplate.query.filter_by(
            created_by=user.id,
            is_active=True
        ).order_by(WarehouseTemplate.created_at.desc()).all()
        
        print(f"\n📋 Found {len(templates)} active templates:")
        
        for idx, template in enumerate(templates):
            print(f"\n{idx+1}. Template: '{template.name}' (ID: {template.id})")
            print(f"   Created: {template.created_at}")
            print(f"   Updated: {template.updated_at}")
            
            # Debug format configuration
            print(f"   📄 Format Config Details:")
            print(f"      Raw location_format_config: {repr(template.location_format_config)}")
            print(f"      location_format_config length: {len(template.location_format_config or '')}")
            print(f"      format_confidence: {template.format_confidence}")
            print(f"      format_examples: {repr(template.format_examples)}")
            print(f"      format_learned_date: {template.format_learned_date}")
            
            # Try to parse JSON
            if template.location_format_config:
                try:
                    parsed_config = json.loads(template.location_format_config)
                    print(f"      ✅ Parsed format config: {parsed_config}")
                    print(f"      Config keys: {list(parsed_config.keys()) if isinstance(parsed_config, dict) else 'Not a dict'}")
                except json.JSONDecodeError as e:
                    print(f"      ❌ JSON parse error: {e}")
            else:
                print(f"      ⚠️  No format config stored")
            
            # Check the has_location_format() method
            has_format = template.has_location_format()
            print(f"      has_location_format(): {has_format}")
            
            # Debug what bool(location_format_config) returns
            bool_check = bool(template.location_format_config)
            print(f"      bool(location_format_config): {bool_check}")
            
            print(f"   📊 Template Usage:")
            print(f"      Usage count: {template.usage_count}")
            print(f"      Is public: {template.is_public}")
            
        return templates
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        return []

def create_test_template_with_format():
    """Create a test template with format configuration to verify the flow"""
    
    print(f"\n🧪 Creating Test Template with Format Config")
    print("=" * 60)
    
    try:
        # Find test user
        user = User.query.filter_by(username='mtest').first()
        if not user:
            print("❌ Test user 'mtest' not found")
            return None
        
        # Create test format config
        test_format_config = {
            "pattern_type": "position_level",
            "format_name": "Position + Level",
            "regex_pattern": r"^(\d{3})([A-Z])$",
            "components": {
                "position": {"pattern": r"\d{3}", "example": "010"},
                "level": {"pattern": r"[A-Z]", "example": "A"}
            },
            "canonical_format": "{position:03d}{level}",
            "validation_examples": ["010A", "325B", "245D"]
        }
        
        test_examples = ["010A", "325B", "245D", "100C", "005A"]
        
        print("📝 Creating template with:")
        print(f"   Format Config: {test_format_config}")
        print(f"   Examples: {test_examples}")
        
        # Create the template
        template = WarehouseTemplate(
            name=f"Test_Format_{datetime.now().strftime('%H%M%S')}",
            description="Test template with format configuration",
            num_aisles=4,
            racks_per_aisle=2,
            positions_per_rack=50,
            levels_per_position=4,
            level_names="ABCD",
            default_pallet_capacity=1,
            bidimensional_racks=False,
            # Format configuration
            location_format_config=json.dumps(test_format_config),
            format_confidence=0.95,
            format_examples=json.dumps(test_examples),
            format_learned_date=datetime.utcnow(),
            # Basic fields
            is_public=False,
            created_by=user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            usage_count=0
        )
        
        # Generate template code
        template.generate_template_code()
        
        db.session.add(template)
        db.session.commit()
        
        print(f"✅ Test template created: '{template.name}' (ID: {template.id})")
        print(f"   Template code: {template.template_code}")
        
        # Verify it was saved correctly
        db.session.refresh(template)
        
        print(f"📄 Verification:")
        print(f"   location_format_config saved: {bool(template.location_format_config)}")
        print(f"   format_confidence: {template.format_confidence}")
        print(f"   has_location_format(): {template.has_location_format()}")
        
        return template
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating test template: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_template_creation_methods():
    """Compare how different APIs create templates"""
    
    print(f"\n🔄 Comparing Template Creation Methods")
    print("=" * 60)
    
    # Test the same flow as standalone_template_api.py
    user = User.query.filter_by(username='mtest').first()
    if not user:
        print("❌ Test user not found")
        return
    
    print("Testing direct WarehouseTemplate creation (like standalone_template_api.py):")
    
    # Simulate the exact creation process from standalone_template_api.py
    format_config = {
        "pattern_type": "position_level",
        "example": "test format"
    }
    format_examples = ["001A", "002B"]
    
    try:
        template = WarehouseTemplate(
            name="Debug_Direct_Creation",
            description="Testing direct creation",
            num_aisles=2,
            racks_per_aisle=1,
            positions_per_rack=10,
            levels_per_position=2,
            level_names="AB",
            default_pallet_capacity=1,
            bidimensional_racks=False,
            # Smart Location Format Configuration (exactly as in standalone_template_api.py)
            location_format_config=json.dumps(format_config) if format_config else None,
            format_confidence=1.0 if format_config else 0.0,
            format_examples=json.dumps(format_examples) if format_examples else None,
            format_learned_date=datetime.utcnow() if format_config else None,
            # Basic fields
            is_public=False,
            created_by=user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            usage_count=0
        )
        
        template.generate_template_code()
        db.session.add(template)
        db.session.commit()
        
        print(f"✅ Direct creation successful: {template.name} (ID: {template.id})")
        print(f"   Format config saved: {bool(template.location_format_config)}")
        print(f"   Raw config: {template.location_format_config}")
        
        return template
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Direct creation failed: {e}")
        return None

if __name__ == '__main__':
    print("🔍 Template Format Configuration Debug Script")
    print()
    
    # Set up Flask app context
    from app import app
    with app.app_context():
        # Debug existing templates
        existing_templates = debug_user_templates('mtest')
        
        # Create test template
        test_template = create_test_template_with_format()
        
        # Compare creation methods
        direct_template = compare_template_creation_methods()
        
        print("\n" + "=" * 60)
        print("🎯 SUMMARY")
        print("=" * 60)
        
        if existing_templates:
            configs_found = sum(1 for t in existing_templates if bool(t.location_format_config))
            print(f"Existing templates: {len(existing_templates)}")
            print(f"Templates with format config: {configs_found}")
            
            if configs_found == 0:
                print("❌ ISSUE: No existing templates have format configuration")
                print("   This confirms the bug - format configs are not being saved during normal template creation")
            else:
                print("✅ Some templates have format configuration")
        
        if test_template and test_template.has_location_format():
            print("✅ Test template creation with format config: SUCCESS")
        else:
            print("❌ Test template creation with format config: FAILED")
            
        if direct_template and direct_template.has_location_format():
            print("✅ Direct template creation (API simulation): SUCCESS")
        else:
            print("❌ Direct template creation (API simulation): FAILED")
        
        print("\nNext steps:")
        print("1. If test creation succeeds but user templates fail: Check frontend->backend data flow")
        print("2. If all creation fails: Check database schema or model methods")
        print("3. If direct creation succeeds: Issue is in the standalone_template_api.py logic")