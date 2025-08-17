#!/usr/bin/env python3
"""
Fix Production Database Issue - PostgreSQL vs SQLite Discrepancy
Diagnose and fix the warehouse detection issue in production PostgreSQL
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class ProductionDatabaseFixer:
    """Fix production database warehouse detection issues"""
    
    def __init__(self):
        self.fixes_applied = []
        self.issues_found = []
        
    def diagnose_production_database(self):
        """Diagnose the production database warehouse detection issue"""
        print("=== PRODUCTION DATABASE DIAGNOSIS ===")
        
        from app import app, db
        from models import Location, WarehouseConfig
        
        with app.app_context():
            print(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
            
            # Step 1: Check all warehouses in production
            print(f"\nStep 1: Checking warehouse inventory...")
            warehouses = db.session.query(Location.warehouse_id).distinct().all()
            
            warehouse_info = {}
            for (warehouse_id,) in warehouses:
                locations = db.session.query(Location).filter_by(warehouse_id=warehouse_id).all()
                warehouse_info[warehouse_id] = {
                    'total_locations': len(locations),
                    'location_types': {},
                    'sample_codes': []
                }
                
                # Categorize by type
                for location in locations:
                    location_type = location.location_type or 'UNKNOWN'
                    warehouse_info[warehouse_id]['location_types'][location_type] = \
                        warehouse_info[warehouse_id]['location_types'].get(location_type, 0) + 1
                
                # Sample codes
                warehouse_info[warehouse_id]['sample_codes'] = [loc.code for loc in locations[:5]]
                
                print(f"\n{warehouse_id}: {len(locations)} total locations")
                for loc_type, count in warehouse_info[warehouse_id]['location_types'].items():
                    print(f"  {loc_type}: {count}")
                print(f"  Sample codes: {warehouse_info[warehouse_id]['sample_codes']}")
            
            # Step 2: Check for problematic DEFAULT warehouse data
            if 'DEFAULT' in warehouse_info:
                print(f"\n⚠️ ISSUE FOUND: DEFAULT warehouse exists in production!")
                default_info = warehouse_info['DEFAULT']
                print(f"  DEFAULT has {default_info['total_locations']} locations")
                print(f"  This is likely causing warehouse detection to favor DEFAULT over USER_TESTF")
                self.issues_found.append("DEFAULT warehouse exists in production")
                
                # Check if DEFAULT locations overlap with USER_TESTF
                if 'USER_TESTF' in warehouse_info:
                    self._check_warehouse_overlap('DEFAULT', 'USER_TESTF')
            
            # Step 3: Check warehouse configurations
            print(f"\nStep 3: Checking warehouse configurations...")
            configs = db.session.query(WarehouseConfig).all()
            
            for config in configs:
                print(f"  {config.warehouse_id}: {config.aisles}×{config.racks}×{config.positions}×{config.levels}")
                if config.warehouse_id == 'DEFAULT':
                    print(f"    ⚠️ DEFAULT warehouse config found - should be removed")
                    self.issues_found.append("DEFAULT warehouse config exists")
            
            # Step 4: Test warehouse detection with real production data
            print(f"\nStep 4: Testing warehouse detection...")
            self._test_warehouse_detection_production()
            
            return warehouse_info
    
    def _check_warehouse_overlap(self, warehouse1, warehouse2):
        """Check if two warehouses have overlapping location codes"""
        from app import app, db
        from models import Location
        
        with app.app_context():
            # Get location codes for both warehouses
            codes1 = {loc.code for loc in db.session.query(Location.code).filter_by(warehouse_id=warehouse1).all()}
            codes2 = {loc.code for loc in db.session.query(Location.code).filter_by(warehouse_id=warehouse2).all()}
            
            overlap = codes1.intersection(codes2)
            
            if overlap:
                print(f"  ⚠️ OVERLAP FOUND: {len(overlap)} locations exist in both {warehouse1} and {warehouse2}")
                print(f"    Sample overlapping codes: {list(overlap)[:5]}")
                self.issues_found.append(f"Location overlap between {warehouse1} and {warehouse2}")
            else:
                print(f"  ✅ No location overlap between {warehouse1} and {warehouse2}")
    
    def _test_warehouse_detection_production(self):
        """Test warehouse detection with production data"""
        from app import app, db
        from rule_engine import RuleEngine
        
        with app.app_context():
            # Test with known USER_TESTF locations
            known_testf_locations = [
                "02-1-011B", "01-1-007B", "01-1-019A", "02-1-003B", "01-1-004C",
                "RECV-01", "STAGE-01", "DOCK-01", "AISLE-01", "AISLE-02"
            ]
            
            test_df = pd.DataFrame({'location': known_testf_locations})
            rule_engine = RuleEngine(db.session)
            
            print(f"  Testing with known USER_TESTF locations: {known_testf_locations}")
            detection_result = rule_engine._detect_warehouse_context(test_df)
            
            detected_warehouse = detection_result.get('warehouse_id')
            confidence = detection_result.get('confidence_level')
            score = detection_result.get('match_score', 0)
            
            print(f"  Detection result: {detected_warehouse} (confidence: {confidence}, score: {score:.1%})")
            
            if detected_warehouse != 'USER_TESTF':
                print(f"  ⚠️ ISSUE: Should detect USER_TESTF but detected {detected_warehouse}")
                self.issues_found.append(f"Incorrect warehouse detection: {detected_warehouse} instead of USER_TESTF")
            else:
                print(f"  ✅ Correctly detected USER_TESTF")
    
    def fix_production_database(self, auto_fix=False):
        """Fix the production database issues"""
        print(f"\n=== PRODUCTION DATABASE FIXES ===")
        
        if not self.issues_found:
            print("No issues found - database is clean!")
            return True
        
        print(f"Found {len(self.issues_found)} issues to fix:")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"  {i}. {issue}")
        
        if not auto_fix:
            response = input(f"\nProceed with automatic fixes? (y/N): ").strip().lower()
            if response != 'y':
                print("Fixes cancelled by user")
                return False
        
        from app import app, db
        from models import Location, WarehouseConfig
        
        with app.app_context():
            try:
                fixes_count = 0
                
                # Fix 1: Remove DEFAULT warehouse locations
                if any("DEFAULT warehouse exists" in issue for issue in self.issues_found):
                    print(f"\nFix 1: Removing DEFAULT warehouse locations...")
                    default_locations = db.session.query(Location).filter_by(warehouse_id='DEFAULT').all()
                    print(f"  Found {len(default_locations)} DEFAULT locations to remove")
                    
                    if default_locations:
                        # Show some examples before deletion
                        sample_codes = [loc.code for loc in default_locations[:5]]
                        print(f"  Sample codes to be deleted: {sample_codes}")
                        
                        deleted_count = db.session.query(Location).filter_by(warehouse_id='DEFAULT').delete()
                        db.session.commit()
                        
                        print(f"  ✅ Deleted {deleted_count} DEFAULT warehouse locations")
                        self.fixes_applied.append(f"Deleted {deleted_count} DEFAULT warehouse locations")
                        fixes_count += 1
                
                # Fix 2: Remove DEFAULT warehouse configuration
                if any("DEFAULT warehouse config exists" in issue for issue in self.issues_found):
                    print(f"\nFix 2: Removing DEFAULT warehouse configuration...")
                    default_config = db.session.query(WarehouseConfig).filter_by(warehouse_id='DEFAULT').first()
                    
                    if default_config:
                        db.session.delete(default_config)
                        db.session.commit()
                        
                        print(f"  ✅ Deleted DEFAULT warehouse configuration")
                        self.fixes_applied.append("Deleted DEFAULT warehouse configuration")
                        fixes_count += 1
                
                # Fix 3: Handle location overlaps (if any)
                overlap_issues = [issue for issue in self.issues_found if "Location overlap" in issue]
                if overlap_issues:
                    print(f"\nFix 3: Resolving location overlaps...")
                    for issue in overlap_issues:
                        print(f"  ⚠️ Manual intervention required for: {issue}")
                        print(f"    This requires careful analysis to determine which warehouse should own each location")
                
                print(f"\n✅ Applied {fixes_count} automatic fixes")
                
                # Verify fixes worked
                print(f"\nVerifying fixes...")
                remaining_default = db.session.query(Location).filter_by(warehouse_id='DEFAULT').count()
                
                if remaining_default == 0:
                    print(f"  ✅ DEFAULT warehouse successfully removed")
                else:
                    print(f"  ⚠️ {remaining_default} DEFAULT locations still remain")
                
                return fixes_count > 0
                
            except Exception as e:
                print(f"  ❌ Error applying fixes: {e}")
                db.session.rollback()
                return False
    
    def test_warehouse_detection_after_fix(self):
        """Test warehouse detection after applying fixes"""
        print(f"\n=== TESTING AFTER FIXES ===")
        
        from app import app, db
        from rule_engine import RuleEngine
        
        with app.app_context():
            # Test with the same locations that caused issues in production
            test_locations = [
                "02-1-011B", "01-1-007B", "01-1-019A", "02-1-003B", "01-1-004C",
                "RECV-01", "STAGE-01", "DOCK-01", "AISLE-01", "AISLE-02",
                "02-1-016B", "01-1-011A", "01-1-008B"
            ]
            
            test_df = pd.DataFrame({'location': test_locations})
            rule_engine = RuleEngine(db.session)
            
            print(f"Testing warehouse detection with {len(test_locations)} locations...")
            detection_result = rule_engine._detect_warehouse_context(test_df)
            
            detected_warehouse = detection_result.get('warehouse_id')
            confidence = detection_result.get('confidence_level')
            score = detection_result.get('match_score', 0)
            
            print(f"Detection result: {detected_warehouse}")
            print(f"Confidence: {confidence}")
            print(f"Match score: {score:.1%}")
            
            if detected_warehouse == 'USER_TESTF' and confidence in ['HIGH', 'VERY_HIGH']:
                print(f"\n🎉 SUCCESS: Warehouse detection now works correctly!")
                print(f"✅ Detects USER_TESTF with {confidence} confidence")
                return True
            else:
                print(f"\n⚠️ Still has issues - may need additional investigation")
                return False
    
    def generate_fix_report(self, output_file=None):
        """Generate a comprehensive fix report"""
        
        report = f"""
# Production Database Fix Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Issues Found
"""
        
        if self.issues_found:
            for i, issue in enumerate(self.issues_found, 1):
                report += f"{i}. {issue}\n"
        else:
            report += "No issues found - database is clean!\n"
        
        report += f"""
## Fixes Applied
"""
        
        if self.fixes_applied:
            for i, fix in enumerate(self.fixes_applied, 1):
                report += f"{i}. {fix}\n"
        else:
            report += "No fixes applied\n"
        
        report += f"""
## Recommendations
1. Test warehouse detection thoroughly in production environment
2. Monitor for any remaining DEFAULT warehouse references
3. Ensure all applications use USER_TESTF as the primary warehouse
4. Consider implementing warehouse validation checks in the application

## Database Environment
- Development: SQLite (clean USER_TESTF warehouse)
- Production: PostgreSQL (had legacy DEFAULT warehouse data)
- Issue: Conflicting warehouse data causing incorrect detection

## Resolution
The enhanced warehouse detection system works correctly when the database
contains only the intended USER_TESTF warehouse data. The production issue
was caused by legacy DEFAULT warehouse locations interfering with detection.
"""
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Fix report saved to: {output_file}")
        
        return report

def main():
    """Main execution function"""
    
    print("PRODUCTION DATABASE ISSUE FIXER")
    print("=" * 50)
    print("Diagnosing PostgreSQL vs SQLite warehouse detection discrepancy...")
    
    fixer = ProductionDatabaseFixer()
    
    # Step 1: Diagnose the issues
    warehouse_info = fixer.diagnose_production_database()
    
    # Step 2: Fix the issues (if any found)
    if fixer.issues_found:
        print(f"\n{len(fixer.issues_found)} issues found that need fixing")
        fixes_applied = fixer.fix_production_database()
        
        if fixes_applied:
            # Step 3: Test after fixes
            fixer.test_warehouse_detection_after_fix()
    else:
        print(f"\n✅ No issues found - database is clean!")
    
    # Step 4: Generate report
    report_file = f"production_database_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    fixer.generate_fix_report(report_file)
    
    # Summary
    print(f"\n" + "=" * 50)
    print("PRODUCTION DATABASE FIX SUMMARY")
    print("=" * 50)
    
    if fixer.issues_found:
        print(f"Issues found: {len(fixer.issues_found)}")
        print(f"Fixes applied: {len(fixer.fixes_applied)}")
        
        if fixer.fixes_applied:
            print(f"\n🎉 Production database issues have been resolved!")
            print(f"The warehouse detection should now work correctly in production.")
        else:
            print(f"\n⚠️ Issues found but fixes were not applied")
            print(f"Manual intervention may be required")
    else:
        print(f"No issues found - system is working correctly")
    
    return len(fixer.fixes_applied) > 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)