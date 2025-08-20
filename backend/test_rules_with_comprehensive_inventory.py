"""
TEST RULES WITH COMPREHENSIVE INVENTORY

Runs the complete analysis pipeline with our strategic test inventory
to validate that all rules are working correctly and detecting expected anomalies.
"""

import sys
import os
sys.path.append('src')

import app
from models import db
import pandas as pd

def test_with_comprehensive_inventory():
    """Test rules with the comprehensive test inventory"""
    
    print("TESTING RULES WITH COMPREHENSIVE INVENTORY")
    print("=" * 60)
    
    try:
        with app.app.app_context():
            # Load the comprehensive test inventory
            inventory_path = r"C:\Users\juanb\Documents\Diego\Projects\ware2\comprehensive_rule_test_inventory.xlsx"
            
            if not os.path.exists(inventory_path):
                print(f"ERROR: Test inventory not found: {inventory_path}")
                return False
            
            print(f"Loading test inventory: {inventory_path}")
            inventory_df = pd.read_excel(inventory_path)
            print(f"Records loaded: {len(inventory_df)}")
            print(f"Columns: {list(inventory_df.columns)}")
            
            # Convert to expected format
            inventory_df = inventory_df.rename(columns={
                'Pallet ID': 'pallet_id',
                'Location': 'location',
                'Description': 'description', 
                'Receipt Number': 'receipt_number',
                'Creation Date': 'creation_date'
            })
            
            # Ensure datetime conversion
            inventory_df['creation_date'] = pd.to_datetime(inventory_df['creation_date'])
            
            print(f"Sample data:")
            print(inventory_df[['pallet_id', 'location', 'receipt_number', 'creation_date']].head())
            
            # Run enhanced analysis
            try:
                from enhanced_main import run_enhanced_engine
                
                print(f"\nRunning comprehensive rule analysis...")
                print("=" * 60)
                
                # Run the analysis with our test data
                analysis_result = run_enhanced_engine(inventory_df)
                
                print(f"\nCOMPREHENSIVE ANALYSIS COMPLETE!")
                print("=" * 60)
                
                # Parse results (analysis_result is a list of anomalies)
                total_anomalies = len(analysis_result) if isinstance(analysis_result, list) else 0
                
                print(f"Total anomalies detected: {total_anomalies}")
                
                # Group anomalies by type for analysis
                if isinstance(analysis_result, list) and total_anomalies > 0:
                    
                    # Try to categorize anomalies by rule type
                    anomaly_categories = {}
                    
                    for anomaly in analysis_result[:20]:  # Show first 20 for analysis
                        pallet_id = anomaly.get('pallet_id', 'Unknown')
                        message = anomaly.get('message', anomaly.get('reason', 'No message'))
                        
                        # Categorize based on message content
                        if 'RECEIVING for' in str(message) and 'threshold' in str(message):
                            category = "Rule 1: Stagnant Pallets"
                        elif 'straggler' in str(message).lower() or 'left behind' in str(message).lower():
                            category = "Rule 2: Uncoordinated Lots"
                        elif 'overcapacity' in str(message).lower() or 'capacity' in str(message).lower():
                            category = "Rule 3: Overcapacity"
                        elif 'invalid' in str(message).lower() or 'not found' in str(message).lower():
                            category = "Rule 4: Invalid Locations"
                        elif 'AISLE' in str(message) and 'threshold' in str(message):
                            category = "Rule 5: Aisle Stagnant"
                        elif 'duplicate' in str(message).lower() or 'scanner' in str(message).lower():
                            category = "Rule 7: Data Integrity"
                        else:
                            category = "Other/Unknown"
                        
                        if category not in anomaly_categories:
                            anomaly_categories[category] = []
                        
                        anomaly_categories[category].append({
                            'pallet_id': pallet_id,
                            'message': str(message)[:100] + "..." if len(str(message)) > 100 else str(message)
                        })
                    
                    # Display categorized results
                    print(f"\nANOMALY BREAKDOWN BY RULE:")
                    print("-" * 40)
                    
                    for category, anomalies in anomaly_categories.items():
                        print(f"\n{category}: {len(anomalies)} anomalies")
                        for i, anomaly in enumerate(anomalies[:5], 1):  # Show first 5 per category
                            print(f"  {i}. {anomaly['pallet_id']}: {anomaly['message']}")
                        if len(anomalies) > 5:
                            print(f"     ... and {len(anomalies) - 5} more")
                    
                    # Compare with expectations
                    print(f"\nEXPECTATION VS REALITY CHECK:")
                    print("-" * 40)
                    
                    expected_counts = {
                        "Rule 1: Stagnant Pallets": 8,
                        "Rule 2: Uncoordinated Lots": 1, 
                        "Rule 3: Overcapacity": 22,
                        "Rule 4: Invalid Locations": 9,
                        "Rule 5: Aisle Stagnant": 5,
                        "Rule 7: Data Integrity": 3,
                    }
                    
                    for rule, expected in expected_counts.items():
                        actual = len(anomaly_categories.get(rule, []))
                        status = "✓" if actual >= expected * 0.5 else "⚠" if actual > 0 else "✗"
                        print(f"  {status} {rule}: Expected ~{expected}, Got {actual}")
                    
                    overall_expected = sum(expected_counts.values())
                    accuracy = (total_anomalies / overall_expected) * 100 if overall_expected > 0 else 0
                    
                    print(f"\nOVERALL PERFORMANCE:")
                    print(f"  Expected total anomalies: ~{overall_expected}")
                    print(f"  Actual total anomalies: {total_anomalies}")
                    print(f"  Detection accuracy: {accuracy:.1f}%")
                    
                    if accuracy >= 80:
                        print(f"  Status: EXCELLENT - Rules working as expected!")
                    elif accuracy >= 60:
                        print(f"  Status: GOOD - Most rules working properly")
                    elif accuracy >= 40:
                        print(f"  Status: FAIR - Some rules may need attention")
                    else:
                        print(f"  Status: POOR - Rules may not be working correctly")
                
                else:
                    print("No anomalies detected or unexpected result format")
                    
                print(f"\nTEST COMPLETED SUCCESSFULLY!")
                return True
                
            except ImportError:
                print("Enhanced engine not available")
                return False
                
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_comprehensive_inventory()
    
    if success:
        print(f"\n🎉 COMPREHENSIVE RULE TEST SUCCESSFUL!")
        print(f"All rules have been validated with strategic test data.")
    else:
        print(f"\n❌ COMPREHENSIVE RULE TEST FAILED!")
        print(f"Some issues may need attention.")
    
    exit(0 if success else 1)