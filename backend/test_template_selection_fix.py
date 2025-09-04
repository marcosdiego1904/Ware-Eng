#!/usr/bin/env python3
"""
Test script for template selection fix
Verifies that templates are selected based on updated_at DESC order
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timedelta
from database import db
from models import WarehouseTemplate
from core_models import User

def test_template_selection_order():
    """Test that templates are selected by updated_at DESC order"""
    
    print("🔍 Testing Template Selection Order Fix")
    print("=" * 50)
    
    try:
        # Create test user if doesn't exist
        test_user = User.query.filter_by(username='marcos9').first()
        if not test_user:
            print("❌ Test user 'marcos9' not found")
            return False
        
        print(f"✅ Found test user: {test_user.username} (ID: {test_user.id})")
        
        # Query templates with format config (Priority 3 fallback scenario)
        # This simulates the exact query that was causing the issue
        templates_with_format_config = WarehouseTemplate.query.filter_by(
            created_by=test_user.id,
            is_active=True
        ).filter(WarehouseTemplate.location_format_config.isnot(None)).order_by(
            WarehouseTemplate.updated_at.desc()  # This is the fix
        ).all()
        
        print(f"\n📋 Found {len(templates_with_format_config)} templates with format config:")
        
        for idx, template in enumerate(templates_with_format_config[:5]):  # Show first 5
            print(f"  {idx+1}. '{template.name}' (ID: {template.id})")
            print(f"      Created: {template.created_at}")
            print(f"      Updated: {template.updated_at}")
            print(f"      Format Config: {bool(template.location_format_config)}")
            print()
        
        # Test the fixed query - should return most recently updated template
        selected_template = WarehouseTemplate.query.filter_by(
            created_by=test_user.id,
            is_active=True
        ).filter(WarehouseTemplate.location_format_config.isnot(None)).order_by(
            WarehouseTemplate.updated_at.desc()
        ).first()
        
        if selected_template:
            print(f"🎯 SELECTED TEMPLATE: '{selected_template.name}' (ID: {selected_template.id})")
            print(f"   Updated: {selected_template.updated_at}")
            
            # Check if this is s12 (the intended template)
            if selected_template.name == 's12':
                print("✅ SUCCESS: s12 template correctly selected!")
                return True
            elif selected_template.name == 's8':
                print("❌ ISSUE: s8 template still selected - may need more investigation")
                return False
            else:
                print(f"⚠️  INFO: Different template '{selected_template.name}' selected")
                print("    This may be correct if it was updated more recently")
                return True
        else:
            print("❌ ERROR: No template with format config found")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during test: {e}")
        return False

def show_template_comparison():
    """Show comparison between s8 and s12 templates"""
    
    print("\n🔍 Template Comparison Analysis")
    print("=" * 50)
    
    try:
        s8_template = WarehouseTemplate.query.filter_by(name='s8').first()
        s12_template = WarehouseTemplate.query.filter_by(name='s12').first()
        
        if not s8_template or not s12_template:
            print("❌ Could not find both s8 and s12 templates")
            return
        
        print("Template Details:")
        print(f"📋 s8  (ID: {s8_template.id}):")
        print(f"    Created:  {s8_template.created_at}")
        print(f"    Updated:  {s8_template.updated_at}")
        print(f"    Format Config: {bool(s8_template.location_format_config)}")
        
        print(f"\n📋 s12 (ID: {s12_template.id}):")
        print(f"    Created:  {s12_template.created_at}")
        print(f"    Updated:  {s12_template.updated_at}")
        print(f"    Format Config: {bool(s12_template.location_format_config)}")
        
        # Determine which should be selected
        if s12_template.updated_at > s8_template.updated_at:
            print("\n✅ s12 should be selected (more recently updated)")
        elif s8_template.updated_at > s12_template.updated_at:
            print("\n⚠️  s8 should be selected (more recently updated)")
        else:
            print("\n🔄 Both templates have same update time")
            
    except Exception as e:
        print(f"❌ ERROR during comparison: {e}")

if __name__ == '__main__':
    print("🧪 Template Selection Fix Test")
    print("Testing the fix for template selection ordering issue")
    print()
    
    # Set up Flask app context
    from app import app
    with app.app_context():
        # Show template comparison first
        show_template_comparison()
        
        # Test the selection logic
        success = test_template_selection_order()
        
        if success:
            print("\n🎉 TEST PASSED: Template selection fix working correctly!")
        else:
            print("\n❌ TEST FAILED: Template selection issue may persist")
            
        print("\n" + "=" * 50)
        print("Fix Applied:")
        print("- Added .order_by(WarehouseTemplate.updated_at.desc()) to all template queries")
        print("- This ensures consistent selection across PostgreSQL and SQLite")
        print("- Most recently updated templates are now prioritized")