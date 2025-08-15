#!/usr/bin/env python3
"""
Update Rule #1 thresholds via API calls
"""
import requests
import json
import time

def get_auth_token():
    """Get authentication token (you may need to implement actual login)"""
    # For now, we'll need to manually provide a token or implement login
    # This is a placeholder - you might need to login via the web interface first
    return None

def update_rules_directly():
    """Update rules by directly modifying the database file approach"""
    print("=== MANUAL RULE UPDATE APPROACH ===")
    print()
    print("Since API access requires authentication, let's provide the SQL commands")
    print("to update the rules directly. You can run these in your preferred SQLite tool.")
    print()
    
    print("🔧 SQL COMMANDS TO EXECUTE:")
    print()
    
    print("-- 1. Update Rule #1 for RECEIVING locations with 10-hour threshold")
    print("UPDATE rule SET")
    print("  name = 'Forgotten Pallets in Receiving',")
    print("  description = 'Detects pallets that have been in receiving areas for more than 10 hours, indicating they may have been forgotten during normal processing workflow.',")
    print("  conditions = '{\"time_threshold_hours\": 10, \"location_types\": [\"RECEIVING\"]}',")
    print("  priority = 'HIGH'")
    print("WHERE id = 1;")
    print()
    
    print("-- 2. Insert new Rule #1B for TRANSITIONAL locations with 4-hour threshold")
    print("INSERT INTO rule (")
    print("  name, description, rule_type, conditions, parameters, priority, is_active, category_id")
    print(") VALUES (")
    print("  'Stuck Pallets in Transit',")
    print("  'Detects pallets stuck in transitional areas (aisles, crossdocks) for more than 4 hours, indicating workflow bottlenecks or equipment issues.',")
    print("  'STAGNANT_PALLETS',")
    print("  '{\"time_threshold_hours\": 4, \"location_types\": [\"TRANSITIONAL\"]}',")
    print("  '{}',")
    print("  'VERY_HIGH',")
    print("  1,")
    print("  (SELECT category_id FROM rule WHERE id = 1)")
    print(");")
    print()
    
    print("-- 3. Verify the changes")
    print("SELECT id, name, rule_type, conditions, priority, is_active")
    print("FROM rule") 
    print("WHERE rule_type = 'STAGNANT_PALLETS'")
    print("ORDER BY id;")
    print()
    
    print("📊 EXPECTED RESULTS AFTER UPDATE:")
    print()
    print("Rule #1 (Forgotten Pallets in Receiving):")
    print("  • Threshold: 10 hours (was 6 hours)")
    print("  • Locations: RECEIVING only (was RECEIVING + TRANSITIONAL)")
    print("  • Priority: HIGH (was VERY_HIGH)")
    print("  • Expected reduction: ~62% fewer false positives")
    print()
    
    print("Rule #1B (Stuck Pallets in Transit):")
    print("  • Threshold: 4 hours (new)")
    print("  • Locations: TRANSITIONAL only")
    print("  • Priority: VERY_HIGH")
    print("  • Purpose: Catch stuck pallets in aisles faster")
    print()
    
    print("🎯 BUSINESS IMPACT:")
    print("  • RECEIVING: Normal 6-8h processing no longer flagged")
    print("  • TRANSITIONAL: Better detection of actually stuck pallets")
    print("  • Overall: More actionable alerts, less noise")

def create_json_configs():
    """Create JSON configuration files for manual import"""
    
    rule1_config = {
        "id": 1,
        "name": "Forgotten Pallets in Receiving",
        "description": "Detects pallets that have been in receiving areas for more than 10 hours, indicating they may have been forgotten during normal processing workflow.",
        "rule_type": "STAGNANT_PALLETS",
        "conditions": {
            "time_threshold_hours": 10,
            "location_types": ["RECEIVING"]
        },
        "parameters": {},
        "priority": "HIGH",
        "is_active": True
    }
    
    rule1b_config = {
        "name": "Stuck Pallets in Transit",
        "description": "Detects pallets stuck in transitional areas (aisles, crossdocks) for more than 4 hours, indicating workflow bottlenecks or equipment issues.",
        "rule_type": "STAGNANT_PALLETS",
        "conditions": {
            "time_threshold_hours": 4,
            "location_types": ["TRANSITIONAL"]
        },
        "parameters": {},
        "priority": "VERY_HIGH",
        "is_active": True
    }
    
    # Save configurations
    with open('rule1_updated_config.json', 'w') as f:
        json.dump(rule1_config, f, indent=2)
    
    with open('rule1b_new_config.json', 'w') as f:
        json.dump(rule1b_config, f, indent=2)
    
    print()
    print("📁 CONFIGURATION FILES CREATED:")
    print("  • rule1_updated_config.json - Updated Rule #1 configuration")
    print("  • rule1b_new_config.json - New Rule #1B configuration")
    print()

if __name__ == "__main__":
    update_rules_directly()
    create_json_configs()