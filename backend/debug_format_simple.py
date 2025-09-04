#!/usr/bin/env python3
"""
Simple format configuration debug test without Unicode characters
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def analyze_existing_templates():
    """Analyze existing templates to see what's missing"""
    
    print("[ANALYSIS] Analyzing Existing Templates")
    print("=" * 60)
    
    try:
        from app import app
        from database import db
        from models import WarehouseTemplate
        from core_models import User
        
        with app.app_context():
            user = User.query.filter_by(username='mtest').first()
            if not user:
                print("[ERROR] User 'mtest' not found")
                return False
            
            templates = WarehouseTemplate.query.filter_by(
                created_by=user.id,
                is_active=True
            ).order_by(WarehouseTemplate.created_at.desc()).all()
            
            print(f"[INFO] Found {len(templates)} templates for user 'mtest':")
            
            for i, template in enumerate(templates):
                print(f"\n{i+1}. '{template.name}' (ID: {template.id})")
                print(f"   Created: {template.created_at}")
                print(f"   Template Code: {template.template_code}")
                
                # Check format configuration details
                config_raw = template.location_format_config
                print(f"   [FORMAT ANALYSIS]:")
                print(f"      location_format_config: {repr(config_raw)}")
                print(f"      Config length: {len(config_raw) if config_raw else 0}")
                print(f"      format_confidence: {template.format_confidence}")
                print(f"      format_examples: {repr(template.format_examples)}")
                print(f"      format_learned_date: {template.format_learned_date}")
                
                # Check the conditions that determine "Format Config: True/False"
                has_config = bool(template.location_format_config)
                has_confidence = bool(template.format_confidence)
                has_format_method = template.has_location_format()
                
                print(f"   [CHECKS]:")
                print(f"      bool(location_format_config): {has_config}")
                print(f"      bool(format_confidence): {has_confidence}")
                print(f"      has_location_format(): {has_format_method}")
                
                # This determines what shows in the smart config logs
                shows_format_true = has_config and has_confidence
                print(f"      [RESULT] Shows 'Format Config: {shows_format_true}'")
                
                if not shows_format_true:
                    if not has_config:
                        print(f"         Issue: No location_format_config data")
                    if not has_confidence:
                        print(f"         Issue: format_confidence is 0 or None")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Error analyzing templates: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("[DEBUG] Format Configuration Analysis")
    print("Checking why templates show 'Format Config: False'")
    print()
    
    success = analyze_existing_templates()
    
    print("\n" + "=" * 60)
    if success:
        print("[SUMMARY] Analysis completed successfully")
        print("Key points:")
        print("- Templates showing 'Format Config: False' are missing data")
        print("- Need BOTH location_format_config AND format_confidence > 0")
        print("- Check which specific field is missing for each template")
    else:
        print("[SUMMARY] Analysis failed - check error messages above")