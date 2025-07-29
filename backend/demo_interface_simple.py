#!/usr/bin/env python3
"""
Simple demo script to show the visual rule management interface
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def show_interface_overview():
    """Display the complete rule management interface overview"""
    
    print("\n" + "="*80)
    print("WAREHOUSE RULE MANAGEMENT - VISUAL INTERFACE OVERVIEW")
    print("="*80)
    
    print("\nWHAT YOU GET:")
    print("   + Complete web-based rule management interface")
    print("   + View all rules (8 default + your custom rules)")
    print("   + Create, edit, delete rules with forms")
    print("   + Real-time filtering and search")
    print("   + Visual rule status indicators")
    print("   + Rule testing and validation")
    
    print("\nACCESS POINTS:")
    print("   * Main Interface: http://localhost:5000/rules")
    print("   * API Endpoints: http://localhost:5000/api/v1/rules")
    print("   * Categories API: http://localhost:5000/api/v1/categories")
    
    print("\nINTERFACE FEATURES:")
    
    print("\n   DASHBOARD CARDS:")
    print("      - Total Rules Counter")
    print("      - Active Rules Counter") 
    print("      - Default Rules Counter")
    print("      - Custom Rules Counter")
    
    print("\n   ADVANCED FILTERS:")
    print("      - Filter by Category (FLOW_TIME, SPACE, PRODUCT)")
    print("      - Filter by Status (Active/Inactive)")
    print("      - Filter by Type (Default/Custom)")
    print("      - Real-time Search")
    
    print("\n   RULE CARDS DISPLAY:")
    print("      - Rule Name & Description")
    print("      - Visual Priority Badges (VERY_HIGH, HIGH, MEDIUM, LOW)")
    print("      - Status Indicators (Active/Inactive)")
    print("      - Type Badges (Default/Custom)")
    print("      - Expandable Rule Details")
    print("      - JSON Conditions & Parameters View")
    
    print("\n   RULE MANAGEMENT:")
    print("      - Create New Rule Button")
    print("      - Edit Rule Forms")
    print("      - Delete Rules (with safety checks)")
    print("      - Activate/Deactivate Toggle")
    print("      - Rule Details Expansion")
    
    print("\n   MODAL FORMS:")
    print("      - Rule Creation Form")
    print("      - Rule Editing Form")
    print("      - JSON Validation")
    print("      - Category Selection")
    print("      - Priority Selection")
    print("      - Rule Type Selection")
    
    print("\nCURRENT RULES IN YOUR SYSTEM:")
    
    try:
        from app import app
        from database import db
        from models import Rule, RuleCategory
        
        with app.app_context():
            rules = Rule.query.all()
            categories = RuleCategory.query.all()
            
            print(f"\n   STATISTICS:")
            print(f"      Total Rules: {len(rules)}")
            print(f"      Active Rules: {sum(1 for r in rules if r.is_active)}")
            print(f"      Default Rules: {sum(1 for r in rules if r.is_default)}")
            print(f"      Custom Rules: {sum(1 for r in rules if not r.is_default)}")
            print(f"      Categories: {len(categories)}")
            
            print(f"\n   RULES BREAKDOWN:")
            for category in categories:
                cat_rules = [r for r in rules if r.category_id == category.id]
                active_count = sum(1 for r in cat_rules if r.is_active)
                print(f"      {category.display_name:25} | {len(cat_rules):2} rules | {active_count:2} active")
            
            print(f"\n   RULES BY TYPE:")
            for rule in rules[:10]:  # Show first 10 rules
                status = "ACTIVE" if rule.is_active else "INACTIVE"
                rule_type = "DEFAULT" if rule.is_default else "CUSTOM "
                priority_symbol = {
                    'VERY_HIGH': '!!!',
                    'HIGH': '!! ', 
                    'MEDIUM': '!  ',
                    'LOW': '   '
                }.get(rule.priority, '?  ')
                
                print(f"      {rule_type} | {priority_symbol} {rule.priority:10} | {status:8} | {rule.name}")
            
            if len(rules) > 10:
                print(f"      ... and {len(rules) - 10} more rules")
    
    except Exception as e:
        print(f"   WARNING: Could not load rules from database: {e}")
    
    print("\nHOW TO ACCESS:")
    print("   1. Run: python run_server.py")
    print("   2. Open: http://localhost:5000/rules")
    print("   3. Navigate using the 'Rules' button in the top navigation")
    
    print("\nINTERFACE CAPABILITIES:")
    print("   + View all rules in beautiful cards")
    print("   + Create new custom rules with forms")
    print("   + Edit existing rules (custom rules only)")
    print("   + Delete rules with safety validation")
    print("   + Toggle rule activation/deactivation")
    print("   + Filter and search rules instantly")
    print("   + View rule JSON conditions and parameters")
    print("   + Visual priority and status indicators")
    print("   + Responsive design for mobile/desktop")
    
    print("\nRESPONSIVE DESIGN:")
    print("   * Desktop: Full grid layout with all features")
    print("   * Tablet: Responsive grid with adapted controls")
    print("   * Mobile: Stacked layout with touch-friendly buttons")
    
    print("\nVISUAL DESIGN:")
    print("   * Modern card-based layout")
    print("   * Color-coded priority badges")
    print("   * Smooth animations and transitions")
    print("   * Clean typography and spacing")
    print("   * Professional warehouse theme")
    
    print("\n" + "="*80)
    print("YOUR RULE MANAGEMENT SYSTEM IS READY!")
    print("   Navigate to http://localhost:5000/rules to see your visual interface")
    print("="*80 + "\n")

def show_api_endpoints():
    """Show available API endpoints"""
    
    print("\nAVAILABLE API ENDPOINTS:")
    print("-" * 50)
    
    endpoints = [
        ("GET", "/api/v1/rules", "List all rules with filtering"),
        ("GET", "/api/v1/rules/{id}", "Get specific rule details"),
        ("POST", "/api/v1/rules", "Create new rule"),
        ("PUT", "/api/v1/rules/{id}", "Update existing rule"),
        ("DELETE", "/api/v1/rules/{id}", "Delete rule"),
        ("POST", "/api/v1/rules/{id}/activate", "Toggle rule status"),
        ("GET", "/api/v1/categories", "List rule categories"),
        ("POST", "/api/v1/rules/test", "Test rules against data"),
        ("POST", "/api/v1/rules/preview", "Preview rule results"),
        ("POST", "/api/v1/rules/validate", "Validate rule conditions"),
        ("GET", "/api/v1/rules/{id}/performance", "Get rule performance"),
        ("GET", "/api/v1/rules/analytics", "Get rules analytics"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"   {method:6} {endpoint:35} - {description}")

if __name__ == "__main__":
    show_interface_overview()
    show_api_endpoints()
    
    print("\nWould you like to start the server now? ")
    print("   Run: python run_server.py")
    print("   Then visit: http://localhost:5000/rules\n")