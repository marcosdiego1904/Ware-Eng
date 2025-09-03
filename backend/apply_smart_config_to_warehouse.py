#!/usr/bin/env python3
"""
Apply Smart Configuration to Production Warehouse

This script applies the position_level Smart Configuration format
to resolve the "006B invalid location" issues.
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def apply_smart_config_to_warehouse(warehouse_id, examples=None):
    """Apply Smart Configuration to a specific warehouse"""
    
    if examples is None:
        # Use the examples that match your inventory format
        examples = ['006B', '010A', '325B', '245D', '156C', '087A', '123A', '999B']
    
    print("=" * 70)
    print("APPLYING SMART CONFIGURATION TO PRODUCTION WAREHOUSE")
    print("=" * 70)
    print(f"Target warehouse: {warehouse_id}")
    print(f"Format examples: {examples}")
    
    try:
        from app import app, db
        from models import WarehouseConfig
        from smart_format_detector import SmartFormatDetector
        
        with app.app_context():
            # Get the target warehouse
            warehouse = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            
            if not warehouse:
                print(f"ERROR: Warehouse '{warehouse_id}' not found!")
                return False
            
            print(f"Found warehouse: {warehouse.warehouse_name}")
            
            # Create Smart Configuration using SmartFormatDetector
            detector = SmartFormatDetector()
            print("Detecting location format...")
            
            detection_result = detector.detect_format(examples)
            format_config = detection_result['detected_pattern']
            
            print(f"Detected format: {format_config['pattern_type']}")
            print(f"Pattern: {format_config['regex_pattern']}")
            print(f"Confidence: {format_config['confidence']:.2%}")
            
            # Apply Smart Configuration to the warehouse
            warehouse.location_format_config = json.dumps(format_config)
            warehouse.format_confidence = format_config['confidence']
            warehouse.format_examples = json.dumps(examples)
            warehouse.format_learned_date = datetime.now()
            
            db.session.commit()
            
            print("\nSUCCESS: Smart Configuration applied!")
            print("-" * 40)
            print("Expected results:")
            print("  - Location '006B' should now be VALID")
            print("  - Dramatically fewer 'Invalid Location' anomalies")
            print("  - Only genuinely invalid locations flagged")
            
            return True
            
    except Exception as e:
        print(f"ERROR: Failed to apply Smart Configuration: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python apply_smart_config_to_warehouse.py WAREHOUSE_ID")
        print("Example: python apply_smart_config_to_warehouse.py DEFAULT")
        sys.exit(1)
    
    warehouse_id = sys.argv[1]
    success = apply_smart_config_to_warehouse(warehouse_id)
    
    if success:
        print(f"\nNext: Test your rule engine - location '006B' should now be VALID!")
    else:
        print(f"\nFailed to apply Smart Configuration. Check the error above.")