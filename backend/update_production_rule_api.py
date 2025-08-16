#!/usr/bin/env python3
"""
Update production Rule ID 1 via API call.
This can be run from anywhere with internet access.
"""
import requests
import json

def update_production_rule_via_api():
    """Update Rule ID 1 via API call to production"""
    
    print("Updating Production Rule via API...")
    print("=" * 50)
    
    # You'll need to get these values from your production environment
    api_base_url = "https://your-backend-api-url/api/v1"  # Replace with actual backend URL
    
    # Step 1: You'll need to get an admin token first
    # This would typically be done through login
    
    print("To use this script, you need:")
    print("1. Your production backend API URL")
    print("2. An admin authentication token")
    print("3. Run this from a machine with internet access")
    print()
    
    # Example API call structure:
    example_curl = """
Example curl command to update the rule:

curl -X PUT "{api_url}/rules/1" \\
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "conditions": {{
      "time_threshold_hours": 10,
      "location_types": ["RECEIVING"]
    }}
  }}'
""".format(api_url=api_base_url)
    
    print(example_curl)
    
    # Manual API update instructions
    print("\nAlternative: Update via Frontend Dashboard")
    print("1. Go to https://ware-eng.vercel.app")
    print("2. Login as admin")
    print("3. Navigate to Rules management")
    print("4. Edit 'Forgotten Pallets Alert' (Rule ID 1)")
    print("5. Change time_threshold_hours from 6 to 10")
    print("6. Save the changes")

if __name__ == "__main__":
    update_production_rule_via_api()