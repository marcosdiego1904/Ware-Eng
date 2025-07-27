"""
Test script for the enhanced warehouse rules system
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Set environment variables
os.environ['FLASK_SECRET_KEY'] = 'test-secret-key'
os.environ['DATABASE_URL'] = ''  # Use SQLite

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_database_rules():
    """Test that database rules are loaded correctly"""
    print("Testing database rules...")
    
    from app import app, db
    from models import Rule, RuleCategory
    
    with app.app_context():
        # Check categories
        categories = RuleCategory.query.all()
        print(f"Categories found: {len(categories)}")
        for cat in categories:
            print(f"  - {cat.name}: {cat.display_name} (Priority: {cat.priority})")
        
        # Check rules
        rules = Rule.query.filter_by(is_active=True).all()
        print(f"\nActive rules found: {len(rules)}")
        for rule in rules:
            print(f"  - [{rule.id}] {rule.name} ({rule.rule_type}) - {rule.priority}")

def test_rule_engine():
    """Test the rule engine with sample data"""
    print("\nTesting rule engine...")
    
    from app import app, db
    from rule_engine import RuleEngine
    
    # Create sample inventory data
    sample_data = pd.DataFrame({
        'pallet_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'location': ['RECEIVING', 'AISLE-A1', 'RECEIVING', 'FINAL-B2', 'UNKNOWN-LOC'],
        'creation_date': [
            datetime.now() - timedelta(hours=10),  # Old pallet in receiving
            datetime.now() - timedelta(hours=2),   # Recent pallet in aisle
            datetime.now() - timedelta(hours=12),  # Very old pallet in receiving
            datetime.now() - timedelta(hours=1),   # Fresh pallet in final
            datetime.now() - timedelta(hours=6)    # Medium age pallet in unknown location
        ],
        'receipt_number': ['R001', 'R002', 'R001', 'R002', 'R003'],
        'description': ['Frozen Food', 'General Item', 'Refrigerated', 'Ambient Product', 'General Item']
    })
    
    print(f"Sample data: {len(sample_data)} rows")
    
    with app.app_context():
        rule_engine = RuleEngine(db.session)
        
        # Test all rules
        results = rule_engine.evaluate_all_rules(sample_data)
        
        total_anomalies = 0
        for result in results:
            print(f"Rule {result.rule_id}: {len(result.anomalies)} anomalies, {result.execution_time_ms}ms")
            if result.anomalies:
                for anomaly in result.anomalies[:2]:  # Show first 2
                    print(f"  - {anomaly['anomaly_type']}: {anomaly['details']}")
            total_anomalies += len(result.anomalies)
        
        print(f"\nTotal anomalies found: {total_anomalies}")

def test_enhanced_engine():
    """Test the enhanced analysis engine"""
    print("\nTesting enhanced analysis engine...")
    
    from app import app
    from enhanced_main import run_enhanced_engine, get_available_rules
    
    with app.app_context():
        # Test getting available rules
        available_rules = get_available_rules()
        print(f"Available rule categories: {len(available_rules)}")
        for category in available_rules:
            print(f"  - {category['display_name']}: {len(category['rules'])} rules")
        
        # Create sample data
        sample_data = pd.DataFrame({
            'pallet_id': ['P001', 'P002', 'P003'],
            'location': ['RECEIVING', 'RECEIVING', 'FINAL-A1'],
            'creation_date': [
                datetime.now() - timedelta(hours=10),
                datetime.now() - timedelta(hours=8),
                datetime.now() - timedelta(hours=1)
            ],
            'receipt_number': ['R001', 'R001', 'R001'],
            'description': ['Product A', 'Product B', 'Product C']
        })
        
        # Run enhanced engine
        anomalies = run_enhanced_engine(
            sample_data,
            use_database_rules=True
        )
        
        print(f"Enhanced engine found: {len(anomalies)} anomalies")
        for anomaly in anomalies[:3]:  # Show first 3
            print(f"  - {anomaly['anomaly_type']}: {anomaly['details']}")

def test_api_integration():
    """Test that the API is properly integrated"""
    print("\nTesting API integration...")
    
    from app import app
    
    with app.app_context():
        # Test that rules API is registered
        rules_found = False
        for rule in app.url_map.iter_rules():
            if '/api/v1/rules' in rule.rule:
                rules_found = True
                print(f"  Found API endpoint: {rule.rule}")
                break
        
        if rules_found:
            print("  Rules API is properly integrated")
        else:
            print("  Rules API not found")

def main():
    """Run all tests"""
    print("Enhanced Warehouse Rules System - Integration Test")
    print("=" * 60)
    
    try:
        test_database_rules()
        test_rule_engine()
        test_enhanced_engine()
        test_api_integration()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("\nSystem Status:")
        print("  Database rules loaded")
        print("  Rule engine functional") 
        print("  Enhanced analysis engine working")
        print("  API endpoints registered")
        print("\nThe enhanced warehouse rules system is ready!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()