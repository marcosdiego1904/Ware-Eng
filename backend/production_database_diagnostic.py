#!/usr/bin/env python3
"""
Production Database Diagnostic - Quick Check
Run this in production to diagnose the PostgreSQL database issue
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def quick_production_diagnostic():
    """Quick diagnostic for production database"""
    
    from app import app, db
    from models import Location, WarehouseConfig
    
    with app.app_context():
        print("=== PRODUCTION DATABASE DIAGNOSTIC ===")
        print(f"Database type: {db.engine.dialect.name}")
        print(f"Database URL: {str(db.engine.url)[:50]}...")
        
        # Check 1: What warehouses exist?
        print(f"\n1. WAREHOUSE INVENTORY:")
        warehouses = db.session.query(Location.warehouse_id).distinct().all()
        
        for (warehouse_id,) in warehouses:
            count = db.session.query(Location).filter_by(warehouse_id=warehouse_id).count()
            print(f"   {warehouse_id}: {count} locations")
            
            # Show sample locations
            sample_locations = db.session.query(Location.code).filter_by(warehouse_id=warehouse_id).limit(5).all()
            sample_codes = [loc.code for loc in sample_locations]
            print(f"     Sample: {sample_codes}")
        
        # Check 2: Is DEFAULT warehouse present?
        default_count = db.session.query(Location).filter_by(warehouse_id='DEFAULT').count()
        if default_count > 0:
            print(f"\n❌ ISSUE FOUND: DEFAULT warehouse has {default_count} locations")
            print(f"   This is likely causing the warehouse detection issue!")
        else:
            print(f"\n✅ DEFAULT warehouse: Not found (good)")
        
        # Check 3: Test specific locations from your inventory
        print(f"\n2. LOCATION EXISTENCE TEST:")
        test_locations = ["02-1-011B", "01-1-007B", "RECV-01", "STAGE-01", "DOCK-01"]
        
        for loc in test_locations:
            matches = db.session.query(Location.warehouse_id).filter_by(code=loc).all()
            warehouses_with_loc = [m.warehouse_id for m in matches]
            
            if warehouses_with_loc:
                print(f"   {loc}: Found in {warehouses_with_loc}")
            else:
                print(f"   {loc}: NOT FOUND")
        
        # Check 4: Quick warehouse detection test
        print(f"\n3. WAREHOUSE DETECTION TEST:")
        try:
            from rule_engine import RuleEngine
            import pandas as pd
            
            rule_engine = RuleEngine(db.session)
            test_df = pd.DataFrame({'location': test_locations})
            
            result = rule_engine._detect_warehouse_context(test_df)
            detected = result.get('warehouse_id')
            confidence = result.get('confidence_level')
            score = result.get('match_score', 0)
            
            print(f"   Detected warehouse: {detected}")
            print(f"   Confidence: {confidence}")
            print(f"   Score: {score:.1%}")
            
            if detected == 'USER_TESTF':
                print(f"   ✅ Correctly detected USER_TESTF")
            else:
                print(f"   ❌ Wrong detection - should be USER_TESTF")
                
        except Exception as e:
            print(f"   Error during detection test: {e}")
        
        # Summary
        print(f"\n=== DIAGNOSTIC SUMMARY ===")
        
        if default_count > 0:
            print(f"🔴 PRODUCTION ISSUE CONFIRMED:")
            print(f"   • DEFAULT warehouse exists with {default_count} locations")
            print(f"   • This interferes with USER_TESTF detection")
            print(f"   • Fix: Remove DEFAULT warehouse locations")
        else:
            print(f"🟢 NO DATABASE ISSUES FOUND:")
            print(f"   • Only USER_TESTF warehouse exists")
            print(f"   • Detection should work correctly")

if __name__ == '__main__':
    quick_production_diagnostic()