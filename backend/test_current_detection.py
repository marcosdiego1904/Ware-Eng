#!/usr/bin/env python3
"""
Test current warehouse detection directly
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_current_detection():
    """Test the current warehouse detection system"""
    
    print("=== TESTING CURRENT WAREHOUSE DETECTION ===")
    
    from app import app, db
    from models import Location
    from rule_engine import RuleEngine
    
    with app.app_context():
        # Check database state
        warehouses = db.session.query(
            Location.warehouse_id,
            db.func.count(Location.id).label('count')
        ).group_by(Location.warehouse_id).all()
        
        print("Current warehouses:")
        for warehouse_id, count in warehouses:
            print(f"  {warehouse_id}: {count} locations")
        
        # Test locations from the error report
        test_locations = [
            '02-1-011B', '01-1-007B', '01-1-019A', '02-1-003B', 
            '01-1-004C', '02-1-021A', '01-1-014C', '01-1-001C',
            'RECV-01', 'RECV-02', 'STAGE-01', 'AISLE-01', 'AISLE-02'
        ]
        
        print(f"\\nTesting with real inventory locations: {test_locations}")
        
        # Create DataFrame
        test_df = pd.DataFrame({'location': test_locations})
        
        # Initialize rule engine
        rule_engine = RuleEngine(db.session)
        
        # Test the detection
        print("\\nRunning warehouse detection...")
        detection_result = rule_engine._detect_warehouse_context(test_df)
        
        print(f"\\nDetection Results:")
        print(f"  Warehouse ID: {detection_result.get('warehouse_id', 'None')}")
        print(f"  Match Score: {detection_result.get('match_score', 0):.1%}")
        print(f"  Confidence: {detection_result.get('confidence_level', 'NONE')}")
        print(f"  Matching Locations: {detection_result.get('matching_locations', 0)}")
        print(f"  Total Inventory: {detection_result.get('total_inventory_locations', 0)}")
        
        # Check if detected warehouse makes sense
        if detection_result.get('warehouse_id'):
            detected_warehouse = detection_result['warehouse_id']
            match_score = detection_result.get('match_score', 0)
            confidence = detection_result.get('confidence_level', 'NONE')
            
            print(f"\\nSuccessfully detected: {detected_warehouse}")
            print(f"  Score: {match_score:.1%}, Confidence: {confidence}")
            
            if match_score > 0.1:  # At least 10% match
                print("Detection appears to be working!")
                return True
            else:
                print("Low match score - may need improvement")
                return False
        else:
            print("No warehouse detected")
            return False

def test_run_sync_utility():
    """Test running the sync utility"""
    
    print("\\n=== TESTING SYNC UTILITY ===")
    
    try:
        from environment_sync_utility import EnvironmentSyncUtility
        
        sync_util = EnvironmentSyncUtility()
        analysis = sync_util.analyze_environment_differences()
        
        print(f"Environment: {analysis.get('environment_type', 'Unknown')}")
        print(f"Database: {analysis.get('database_type', 'Unknown')}")
        print(f"Total Locations: {analysis.get('total_locations', 0)}")
        
        # Test validation
        test_locations = ['02-1-011B', '01-1-007B', 'RECV-01', 'STAGE-01']
        validation = sync_util.validate_warehouse_detection(test_locations)
        
        detection = validation.get('detection_result', {})
        print(f"Validation Result: {detection.get('warehouse_id', 'None')} ({detection.get('confidence_level', 'NONE')})")
        
        return True
        
    except Exception as e:
        print(f"Sync utility error: {str(e)}")
        return False

if __name__ == '__main__':
    print("CURRENT SYSTEM VALIDATION")
    print("=" * 40)
    
    detection_works = test_current_detection()
    sync_works = test_run_sync_utility()
    
    print(f"\\n" + "=" * 40)
    print(f"Detection System: {'WORKING' if detection_works else 'NEEDS WORK'}")
    print(f"Sync Utility: {'WORKING' if sync_works else 'NEEDS WORK'}")
    
    if detection_works and sync_works:
        print("\\nPHASE 1 CORE FUNCTIONALITY WORKING")
    else:
        print("\\nPHASE 1 NEEDS DEBUGGING")