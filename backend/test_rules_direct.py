#!/usr/bin/env python3
"""
Direct test of the enhanced rule engine bypassing HTTP
"""
import sys
import os
import pandas as pd
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_enhanced_rules_direct():
    """Test the enhanced rule engine directly without HTTP"""
    
    print("Testing Enhanced Rule Engine - Direct Access")
    print("=" * 60)
    
    try:
        # Import the rule engine
        from rule_engine import RuleEngine
        from models import Rule
        
        # Set up environment
        os.environ['FLASK_SECRET_KEY'] = 'test-secret-key-for-testing'
        
        # Import Flask app
        from app import app
        
        with app.app_context():
            print("Loading rule engine...")
            
            # Create rule engine instance
            engine = RuleEngine(app)
            
            # Load test data
            print("Loading test inventory data...")
            test_file = 'data/comprehensive_inventory_test.xlsx'
            
            if not os.path.exists(test_file):
                print(f"ERROR: Test file {test_file} not found")
                return None
            
            inventory_df = pd.read_excel(test_file)
            print(f"Loaded {len(inventory_df)} inventory records")
            print(f"Columns: {list(inventory_df.columns)}")
            print()
            
            # Get active rules
            rules = Rule.query.filter_by(is_active=True).all()
            print(f"Found {len(rules)} active rules:")
            for rule in rules:
                print(f"  - {rule.name} ({rule.rule_type})")
            print()
            
            # Run analysis
            print("Running enhanced rule engine analysis...")
            start_time = datetime.now()
            
            # Extract rule IDs for the engine
            rule_ids = [rule.id for rule in rules]
            result = engine.evaluate_all_rules(inventory_df, rule_ids)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            # Analyze results (result is a list of RuleEvaluationResult)
            all_anomalies = []
            for rule_result in result:
                all_anomalies.extend(rule_result.anomalies)
            
            total_anomalies = len(all_anomalies)
            
            print(f"Analysis complete!")
            print(f"Total anomalies found: {total_anomalies}")
            print(f"Processing time: {processing_time:.0f}ms")
            print()
            
            # Anomaly breakdown
            anomaly_breakdown = {}
            for anomaly in all_anomalies:
                anomaly_type = anomaly.get('anomaly_type', 'Unknown')
                anomaly_breakdown[anomaly_type] = anomaly_breakdown.get(anomaly_type, 0) + 1
            
            if anomaly_breakdown:
                print("Anomaly Breakdown:")
                for anomaly_type, count in anomaly_breakdown.items():
                    print(f"  - {anomaly_type}: {count}")
                print()
            
            # Rule results
            print("Rule Results:")
            for rule_result in result:
                print(f"  - {rule_result.rule_name}: {len(rule_result.anomalies)} anomalies ({rule_result.execution_time}ms)")
            print()
            
            # Focus on our temporal fixes
            stagnant_found = False
            uncoordinated_found = False
            
            for rule_result in result:
                name = rule_result.rule_name.lower()
                count = len(rule_result.anomalies)
                
                if 'stagnant' in name or 'forgotten' in name:
                    stagnant_found = count > 0
                    print(f"STAGNANT PALLETS: {count} anomalies found")
                elif 'uncoordinated' in name or 'lots' in name:
                    uncoordinated_found = count > 0
                    print(f"UNCOORDINATED LOTS: {count} anomalies found")
            
            # Success analysis
            expected_anomalies = 28
            print("\nSuccess Analysis:")
            print(f"  Expected: ~{expected_anomalies} anomalies")
            print(f"  Actual: {total_anomalies} anomalies")
            print(f"  Achievement: {total_anomalies/expected_anomalies*100:.1f}%")
            
            print("\nTemporal Fix Status:")
            print(f"  Stagnant Pallets Working: {'YES' if stagnant_found else 'NO'}")
            print(f"  Uncoordinated Lots Working: {'YES' if uncoordinated_found else 'NO'}")
            
            if total_anomalies >= 25:  # 89%+ success rate
                print("  EXCELLENT: Temporal fixes working!")
            elif total_anomalies >= 20:  # 71%+ success rate
                print("  GOOD: Significant improvement achieved")
            else:
                print("  NEEDS WORK: More fixes required")
            
            return result
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_enhanced_rules_direct()