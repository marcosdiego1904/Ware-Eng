#!/usr/bin/env python3
"""
Simple test to debug format configuration directly without HTTP requests
"""

import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_template_creation_direct():
    """Test template creation directly through the app context"""
    
    print("[TEST] Direct Template Creation Format Config Test")
    print("=" * 60)
    
    try:
        from app import app
        from database import db
        from models import WarehouseTemplate
        from core_models import User
        
        with app.app_context():
            # Find test user
            user = User.query.filter_by(username='mtest').first()
            if not user:
                print("❌ User 'mtest' not found. Please create this user first.")
                return False
                
            print(f"✅ Found user: {user.username} (ID: {user.id})")
            
            # Test 1: Create template without format config (current behavior)
            print("\n📝 Test 1: Creating template WITHOUT format config...")
            
            template_no_format = WarehouseTemplate(
                name=f"NoFormat_{datetime.now().strftime('%H%M%S')}",
                description="Template without format config",
                num_aisles=2,
                racks_per_aisle=1,
                positions_per_rack=10,
                levels_per_position=2,
                level_names="AB",
                default_pallet_capacity=1,
                bidimensional_racks=False,
                # NO FORMAT CONFIG
                location_format_config=None,
                format_confidence=0.0,
                format_examples=None,
                format_learned_date=None,
                # Basic fields
                is_public=False,
                created_by=user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True,
                usage_count=0
            )
            
            template_no_format.generate_template_code()
            db.session.add(template_no_format)
            db.session.commit()
            
            print(f"   ✅ Created: {template_no_format.name} (ID: {template_no_format.id})")
            print(f"   has_location_format(): {template_no_format.has_location_format()}")
            
            # Test 2: Create template WITH format config (what should happen)
            print("\n📝 Test 2: Creating template WITH format config...")
            
            # Create a proper format config
            format_config = {
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
            
            format_examples = ["010A", "325B", "245D", "100C", "005A"]
            
            template_with_format = WarehouseTemplate(
                name=f"WithFormat_{datetime.now().strftime('%H%M%S')}",
                description="Template with format config",
                num_aisles=2,
                racks_per_aisle=1,
                positions_per_rack=10,
                levels_per_position=2,
                level_names="AB",
                default_pallet_capacity=1,
                bidimensional_racks=False,
                # WITH FORMAT CONFIG
                location_format_config=json.dumps(format_config),
                format_confidence=0.95,
                format_examples=json.dumps(format_examples),
                format_learned_date=datetime.utcnow(),
                # Basic fields
                is_public=False,
                created_by=user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True,
                usage_count=0
            )
            
            template_with_format.generate_template_code()
            db.session.add(template_with_format)
            db.session.commit()
            
            print(f"   ✅ Created: {template_with_format.name} (ID: {template_with_format.id})")
            print(f"   has_location_format(): {template_with_format.has_location_format()}")
            print(f"   format_confidence: {template_with_format.format_confidence}")
            
            # Test 3: Check what the smart config system sees
            print("\n📋 Test 3: Checking smart config template selection...")
            
            templates_with_format = WarehouseTemplate.query.filter_by(
                created_by=user.id,
                is_active=True
            ).filter(WarehouseTemplate.location_format_config.isnot(None)).all()
            
            print(f"   Templates with format config found: {len(templates_with_format)}")
            for t in templates_with_format:
                print(f"   - {t.name} (ID: {t.id}): confidence {t.format_confidence}")
            
            # Test 4: Simulate the selection that was failing
            print("\n🎯 Test 4: Simulating the template selection logic...")
            
            # This is the exact query from our earlier fix
            selected_template = WarehouseTemplate.query.filter_by(
                created_by=user.id,
                is_active=True
            ).filter(WarehouseTemplate.location_format_config.isnot(None)).order_by(
                WarehouseTemplate.updated_at.desc()
            ).first()
            
            if selected_template:
                print(f"   ✅ Selected template: {selected_template.name}")
                print(f"   Format Config: True (has format configuration)")
            else:
                print(f"   ❌ No template with format config selected")
                print(f"   This means all templates have Format Config: False")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_existing_templates():
    """Analyze the existing templates to see what's missing"""
    
    print("\n🔍 Analyzing Existing Templates")
    print("=" * 60)
    
    try:
        from app import app
        from database import db
        from models import WarehouseTemplate
        from core_models import User
        
        with app.app_context():
            user = User.query.filter_by(username='mtest').first()
            if not user:
                print("❌ User 'mtest' not found")
                return False
            
            templates = WarehouseTemplate.query.filter_by(
                created_by=user.id,
                is_active=True
            ).order_by(WarehouseTemplate.created_at.desc()).all()
            
            print(f"📋 Found {len(templates)} templates for user 'mtest':")
            
            for i, template in enumerate(templates):
                print(f"\n{i+1}. '{template.name}' (ID: {template.id})")
                print(f"   Created: {template.created_at}")
                print(f"   Template Code: {template.template_code}")
                
                # Detailed format analysis
                print(f"   📄 Format Configuration Analysis:")
                config_raw = template.location_format_config
                print(f"      location_format_config: {repr(config_raw)}")
                print(f"      location_format_config length: {len(config_raw) if config_raw else 0}")
                print(f"      format_confidence: {template.format_confidence}")
                print(f"      format_examples: {repr(template.format_examples)}")
                print(f"      format_learned_date: {template.format_learned_date}")
                
                # Method checks
                has_format = template.has_location_format()
                bool_config = bool(template.location_format_config)
                bool_confidence = bool(template.format_confidence)
                
                print(f"      🔍 Method Results:")
                print(f"         has_location_format(): {has_format}")
                print(f"         bool(location_format_config): {bool_config}")
                print(f"         bool(format_confidence): {bool_confidence}")
                
                # This is what determines "Format Config: True/False" in logs
                final_result = bool_config and bool_confidence
                print(f"         📊 Final Result (shows in logs): {final_result}")
                
                if final_result:
                    print(f"         ✅ This template SHOULD show 'Format Config: True'")
                else:
                    print(f"         ❌ This template shows 'Format Config: False'")
                    if not bool_config:
                        print(f"            Reason: No location_format_config data")
                    if not bool_confidence:
                        print(f"            Reason: format_confidence is 0.0 or None")
            
            return True
            
    except Exception as e:
        print(f"❌ Error analyzing templates: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Simple Format Configuration Debug Test")
    print("Testing template creation and format config persistence")
    print()
    
    # Analyze existing templates first
    analysis_success = analyze_existing_templates()
    
    if analysis_success:
        # Test creating new templates with and without format config
        test_success = test_template_creation_direct()
        
        if test_success:
            print("\n🎉 SUCCESS: All tests completed!")
        else:
            print("\n❌ FAILED: Some tests failed")
    else:
        print("\n❌ FAILED: Could not analyze existing templates")
    
    print("\n" + "=" * 60)
    print("🎯 KEY FINDINGS:")
    print("- Check which templates show 'Final Result: True' vs 'False'")
    print("- Templates need BOTH location_format_config AND format_confidence > 0")
    print("- If all existing templates show 'False', the issue is in template creation")
    print("- If test templates show 'True', the creation logic works correctly")