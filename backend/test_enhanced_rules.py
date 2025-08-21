#!/usr/bin/env python3
"""
Test script for enhanced rule engine with temporal fixes
"""
import requests
import json

def test_enhanced_rules():
    """Test the enhanced rule engine with all temporal fixes"""
    
    print("Testing Enhanced Rule Engine with Temporal Fixes")
    print("=" * 60)
    
    # API endpoint
    url = "http://localhost:5000/api/v1/reports"
    
    # Prepare the file upload
    try:
        with open('data/comprehensive_inventory_test.xlsx', 'rb') as f:
            files = {'file': ('test_inventory_with_anomalies.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            headers = {
                'Authorization': 'Bearer test_token',
                'Origin': 'https://ware-eng.vercel.app'
            }
            
            print("Uploading test inventory file...")
            response = requests.post(url, files=files, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"SUCCESS: {response.status_code}")
                print(f"Total Anomalies: {result.get('total_anomalies', 'Unknown')}")
                print(f"Processing Time: {result.get('processing_time', 'Unknown')}")
                print()
                
                # Print anomaly breakdown
                if 'anomaly_breakdown' in result:
                    print("Anomaly Breakdown:")
                    for anomaly_type, count in result['anomaly_breakdown'].items():
                        print(f"  - {anomaly_type}: {count}")
                    print()
                
                # Print rule results
                if 'rule_results' in result:
                    print("Rule Results:")
                    for rule_result in result['rule_results']:
                        name = rule_result.get('rule_name', 'Unknown')
                        count = rule_result.get('anomaly_count', 0)
                        time = rule_result.get('execution_time', 0)
                        print(f"  - {name}: {count} anomalies ({time}ms)")
                    print()
                
                # Success criteria check
                expected_anomalies = 28
                actual_anomalies = result.get('total_anomalies', 0)
                
                print("Success Analysis:")
                print(f"  Expected: ~{expected_anomalies} anomalies")
                print(f"  Actual: {actual_anomalies} anomalies")
                print(f"  Achievement: {actual_anomalies/expected_anomalies*100:.1f}%")
                
                if actual_anomalies >= 25:  # 89%+ success rate
                    print("  EXCELLENT: Temporal fixes working!")
                elif actual_anomalies >= 20:  # 71%+ success rate
                    print("  GOOD: Significant improvement achieved")
                else:
                    print("  NEEDS WORK: More fixes required")
                
                return result
                
            else:
                print(f"ERROR: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except FileNotFoundError:
        print("ERROR: Test file not found")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    test_enhanced_rules()