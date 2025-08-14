#!/usr/bin/env python3
"""
Test API with debug output to trace location validation issue
"""

import requests
import os

def test_inventory_upload():
    """Upload the fixed inventory and analyze results"""
    
    api_base = "http://localhost:5000/api/v1"
    
    # Check if fixed inventory file exists
    inventory_file = "FakeCorp_Fixed_Inventory.xlsx"
    if not os.path.exists(inventory_file):
        print(f"Error: {inventory_file} not found")
        return
    
    print("Testing fixed inventory with debug output...")
    print("=" * 50)
    
    # Upload and analyze
    with open(inventory_file, 'rb') as f:
        files = {'file': f}
        data = {
            'column_mapping': '{"pallet_id": "Pallet ID", "location": "Location", "description": "Description", "receipt_number": "Receipt Number", "creation_date": "Creation Date"}'
        }
        
        print("Uploading inventory file...")
        response = requests.post(f"{api_base}/analyze", files=files, data=data)
        
    if response.status_code == 200:
        result = response.json()
        print(f"Analysis completed!")
        print(f"Total anomalies: {result.get('total_anomalies', 0)}")
        
        # Print anomaly breakdown
        anomalies_by_rule = result.get('anomalies_by_rule', {})
        for rule_name, count in anomalies_by_rule.items():
            print(f"  {rule_name}: {count} anomalies")
        
        # Print some specific anomalies
        anomalies = result.get('anomalies', [])
        if anomalies:
            print(f"\nFirst 5 anomalies:")
            for i, anomaly in enumerate(anomalies[:5]):
                print(f"  {i+1}. {anomaly.get('pallet_id', 'N/A')} - {anomaly.get('anomaly_type', 'N/A')} - {anomaly.get('details', 'N/A')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_inventory_upload()