#!/usr/bin/env python3
"""
Smart Configuration Hotfix - Make Columns Optional

This script temporarily modifies the WarehouseTemplate model to make 
Smart Configuration columns optional, preventing errors when they 
don't exist in the database yet.

USE THIS ONLY AS A TEMPORARY MEASURE UNTIL PRODUCTION MIGRATION IS APPLIED.
"""

import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def apply_hotfix():
    """Apply hotfix to make Smart Configuration columns optional"""
    
    models_file = os.path.join(src_dir, 'models.py')
    
    if not os.path.exists(models_file):
        print("ERROR: models.py not found")
        return False
    
    print("=" * 60)
    print("SMART CONFIGURATION HOTFIX")
    print("=" * 60)
    print("Making Smart Configuration columns optional...")
    
    # Read current models.py
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if hotfix already applied
    if 'SMART_CONFIG_HOTFIX_APPLIED' in content:
        print("Hotfix already applied!")
        return True
    
    # Find the WarehouseTemplate class and modify Smart Configuration columns
    replacements = [
        # Make columns nullable and add default values
        ('location_format_config = db.Column(db.Text)', 'location_format_config = db.Column(db.Text, nullable=True)'),
        ('format_confidence = db.Column(db.Float)', 'format_confidence = db.Column(db.Float, nullable=True, default=0.0)'),
        ('format_examples = db.Column(db.Text)', 'format_examples = db.Column(db.Text, nullable=True)'),
        ('format_learned_date = db.Column(db.DateTime)', 'format_learned_date = db.Column(db.DateTime, nullable=True)'),
    ]
    
    modified = False
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"+ Modified: {old.split('=')[0].strip()}")
    
    if modified:
        # Add hotfix marker
        content += '\n\n# SMART_CONFIG_HOTFIX_APPLIED - Remove this after production migration\n'
        
        # Write back to file
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✓ Hotfix applied successfully!")
        print("\nThis allows the application to run without Smart Configuration columns.")
        print("IMPORTANT: Apply the production migration as soon as possible!")
        print("Then remove this hotfix by running: python remove_smart_config_hotfix.py")
        
        return True
    else:
        print("No modifications needed - columns already optional or not found")
        return False

def remove_hotfix():
    """Remove the hotfix and restore original model definitions"""
    
    models_file = os.path.join(src_dir, 'models.py')
    
    if not os.path.exists(models_file):
        print("ERROR: models.py not found")
        return False
    
    print("Removing Smart Configuration hotfix...")
    
    # Read current models.py
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if hotfix was applied
    if 'SMART_CONFIG_HOTFIX_APPLIED' not in content:
        print("No hotfix to remove")
        return True
    
    # Reverse the changes
    replacements = [
        ('location_format_config = db.Column(db.Text, nullable=True)', 'location_format_config = db.Column(db.Text)'),
        ('format_confidence = db.Column(db.Float, nullable=True, default=0.0)', 'format_confidence = db.Column(db.Float)'),
        ('format_examples = db.Column(db.Text, nullable=True)', 'format_examples = db.Column(db.Text)'),
        ('format_learned_date = db.Column(db.DateTime, nullable=True)', 'format_learned_date = db.Column(db.DateTime)'),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"✓ Restored: {new.split('=')[0].strip()}")
    
    # Remove hotfix marker
    content = content.replace('\n\n# SMART_CONFIG_HOTFIX_APPLIED - Remove this after production migration\n', '')
    
    # Write back to file
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Hotfix removed successfully!")
    print("Models restored to original state.")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Configuration Hotfix')
    parser.add_argument('--remove', action='store_true', help='Remove the hotfix')
    
    args = parser.parse_args()
    
    if args.remove:
        success = remove_hotfix()
    else:
        success = apply_hotfix()
    
    sys.exit(0 if success else 1)