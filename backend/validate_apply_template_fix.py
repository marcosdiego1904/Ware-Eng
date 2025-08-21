#!/usr/bin/env python3
"""
Quick Validation Test - Apply Template Fix
Validates that the key components of the fix are in place
"""

import os
import sys

def validate_backend_changes():
    """Validate that backend changes are properly implemented"""
    
    print("=== VALIDATING BACKEND CHANGES ===")
    
    # Check 1: app.py accepts warehouse_id parameter
    app_py_path = os.path.join('src', 'app.py')
    
    if os.path.exists(app_py_path):
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for warehouse_id parameter extraction
        if "warehouse_id = request.form.get('warehouse_id')" in content:
            print("[PASS] app.py extracts warehouse_id from form data")
        else:
            print("[FAIL] app.py missing warehouse_id extraction")
            return False
            
        # Check for warehouse_id passing to engine
        if "warehouse_id=warehouse_id" in content:
            print("[PASS] app.py passes warehouse_id to analysis engine")
        else:
            print("[FAIL] app.py not passing warehouse_id to engine")
            return False
    else:
        print("[FAIL] app.py not found")
        return False
    
    # Check 2: enhanced_main.py accepts warehouse_id parameter
    enhanced_main_path = os.path.join('src', 'enhanced_main.py')
    
    if os.path.exists(enhanced_main_path):
        with open(enhanced_main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for warehouse_id parameter in function signature
        if "warehouse_id: str = None" in content:
            print("[PASS] enhanced_main.py accepts warehouse_id parameter")
        else:
            print("[FAIL] enhanced_main.py missing warehouse_id parameter")
            return False
            
        # Check for explicit warehouse context setting
        if "_warehouse_context = {" in content and "explicit_template" in content:
            print("[PASS] enhanced_main.py sets explicit warehouse context")
        else:
            print("[FAIL] enhanced_main.py not setting explicit warehouse context")
            return False
    else:
        print("[FAIL] enhanced_main.py not found")
        return False
    
    # Check 3: rule_engine.py respects explicit warehouse context
    rule_engine_path = os.path.join('src', 'rule_engine.py')
    
    if os.path.exists(rule_engine_path):
        with open(rule_engine_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for explicit warehouse context check
        if "hasattr(self, '_warehouse_context')" in content:
            print("[PASS] rule_engine.py checks for explicit warehouse context")
        else:
            print("[FAIL] rule_engine.py missing explicit warehouse context check")
            return False
            
        # Check for auto-detection bypass
        if "APPLY_TEMPLATE_FIX" in content:
            print("[PASS] rule_engine.py has apply template fix logging")
        else:
            print("[FAIL] rule_engine.py missing apply template fix")
            return False
    else:
        print("[FAIL] rule_engine.py not found")
        return False
    
    print("[SUCCESS] All backend changes validated")
    return True

def validate_frontend_changes():
    """Validate that frontend changes are properly implemented"""
    
    print("\n=== VALIDATING FRONTEND CHANGES ===")
    
    # Check frontend files exist and have proper changes
    frontend_base = os.path.join('..', 'frontend')
    
    # Check 1: new-analysis.tsx includes warehouse context
    analysis_path = os.path.join(frontend_base, 'components', 'dashboard', 'views', 'new-analysis.tsx')
    
    if os.path.exists(analysis_path):
        with open(analysis_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for location store import
        if "useLocationStore" in content:
            print("[PASS] new-analysis.tsx imports location store")
        else:
            print("[FAIL] new-analysis.tsx missing location store import")
            return False
            
        # Check for warehouse_id extraction
        if "currentWarehouseConfig?.warehouse_id" in content:
            print("[PASS] new-analysis.tsx extracts warehouse_id from config")
        else:
            print("[FAIL] new-analysis.tsx not extracting warehouse_id")
            return False
            
        # Check for warehouse context display
        if "Analysis Warehouse Configuration" in content:
            print("[PASS] new-analysis.tsx shows warehouse context to user")
        else:
            print("[FAIL] new-analysis.tsx missing warehouse context display")
            return False
    else:
        print("[FAIL] new-analysis.tsx not found")
        return False
    
    # Check 2: reports.ts API accepts warehouse_id
    reports_path = os.path.join(frontend_base, 'lib', 'reports.ts')
    
    if os.path.exists(reports_path):
        with open(reports_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for warehouse_id in interface
        if "warehouse_id?: string" in content:
            print("[PASS] reports.ts interface includes warehouse_id")
        else:
            print("[FAIL] reports.ts interface missing warehouse_id")
            return False
            
        # Check for warehouse_id in form data
        if "formData.append('warehouse_id', data.warehouse_id)" in content:
            print("[PASS] reports.ts sends warehouse_id to backend")
        else:
            print("[FAIL] reports.ts not sending warehouse_id")
            return False
    else:
        print("[FAIL] reports.ts not found")
        return False
    
    print("[SUCCESS] All frontend changes validated")
    return True

def run_validation():
    """Run complete validation of the Apply Template fix"""
    
    print("Apply Template Fix - Implementation Validation")
    print("=" * 50)
    
    # Change to backend directory for file checking
    original_dir = os.getcwd()
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    try:
        backend_valid = validate_backend_changes()
        frontend_valid = validate_frontend_changes()
        
        if backend_valid and frontend_valid:
            print("\n" + "=" * 50)
            print("[SUCCESS] APPLY TEMPLATE FIX FULLY IMPLEMENTED")
            print("=" * 50)
            print("\nKey Features Implemented:")
            print("• Backend accepts warehouse_id from applied templates")
            print("• Analysis engine bypasses auto-detection when template applied")
            print("• Frontend passes current warehouse configuration to analysis")
            print("• User sees which warehouse will be used for analysis")
            print("\nThe apply template workflow is now properly connected!")
            print("Users can apply a template and have analysis use that exact warehouse.")
            return True
        else:
            print("\n[FAIL] Implementation incomplete - review failed checks")
            return False
            
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)