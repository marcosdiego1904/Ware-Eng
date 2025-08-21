#!/usr/bin/env python3
"""
Test script for enhanced rule engine with proper authentication
"""
import requests
import json
import jwt
import datetime
from werkzeug.security import generate_password_hash

def create_test_token():
    """Create a valid JWT token for testing"""
    
    # Test user payload
    payload = {
        'user_id': 999,  # Test user ID
        'username': 'testf',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    
    # Use a default secret key for testing (in production this would be configured)
    secret_key = 'your-secret-key-here'  # This should match your Flask app's SECRET_KEY
    
    # Generate JWT token
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def test_enhanced_rules():
    """Test the enhanced rule engine with proper authentication"""
    
    print("Testing Enhanced Rule Engine with Authentication")
    print("=" * 60)
    
    # Create test token
    try:
        token = create_test_token()
        print("JWT token created successfully")
    except Exception as e:
        print(f"Error creating token: {e}")
        return None
    
    # API endpoint
    url = "http://localhost:5000/api/v1/reports"
    
    # Prepare the file upload
    try:
        with open('data/comprehensive_inventory_test.xlsx', 'rb') as f:
            files = {'file': ('comprehensive_inventory_test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            headers = {
                'Authorization': f'Bearer {token}',
                'Origin': 'https://ware-eng.vercel.app'
            }
            
            print("Uploading test inventory file...")
            response = requests.post(url, files=files, headers=headers, timeout=60)
            
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
                
                # Specific rule focus for our temporal fixes
                stagnant_found = False
                uncoordinated_found = False
                
                if 'rule_results' in result:
                    for rule_result in result['rule_results']:
                        name = rule_result.get('rule_name', '').lower()
                        count = rule_result.get('anomaly_count', 0)
                        
                        if 'stagnant' in name or 'forgotten' in name:
                            stagnant_found = count > 0
                            print(f"STAGNANT PALLETS: {count} anomalies found")
                        elif 'uncoordinated' in name or 'lots' in name:
                            uncoordinated_found = count > 0
                            print(f"UNCOORDINATED LOTS: {count} anomalies found")
                
                # Success criteria check
                expected_anomalies = 28
                actual_anomalies = result.get('total_anomalies', 0)
                
                print("\nSuccess Analysis:")
                print(f"  Expected: ~{expected_anomalies} anomalies")
                print(f"  Actual: {actual_anomalies} anomalies")
                print(f"  Achievement: {actual_anomalies/expected_anomalies*100:.1f}%")
                
                print("\nTemporal Fix Status:")
                print(f"  Stagnant Pallets Working: {'YES' if stagnant_found else 'NO'}")
                print(f"  Uncoordinated Lots Working: {'YES' if uncoordinated_found else 'NO'}")
                
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