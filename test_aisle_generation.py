#!/usr/bin/env python3
"""
Test AISLE location generation in template system
"""

import json

def test_aisle_generation():
    """Test the AISLE location generation logic"""
    
    print("=== Testing AISLE Location Generation ===")
    
    # Simulate template parameters
    num_aisles = 4  # Example: 4 aisles warehouse
    
    # Generate AISLE locations (same logic as added to template_api.py)
    aisle_locations_data = []
    for aisle_num in range(1, num_aisles + 1):
        aisle_locations_data.append({
            'code': f'AISLE-{aisle_num:02d}',
            'capacity': 10,
            'zone': 'GENERAL'
        })
    
    print(f"For a {num_aisles}-aisle warehouse, generated AISLE locations:")
    for aisle_data in aisle_locations_data:
        print(f"  - {aisle_data['code']} (capacity: {aisle_data['capacity']}, zone: {aisle_data['zone']})")
    
    print(f"\nJSON template data:")
    print(json.dumps(aisle_locations_data, indent=2))
    
    print(f"\nThese locations would be created with:")
    print(f"  - location_type: 'TRANSITIONAL'")
    print(f"  - zone: 'GENERAL'") 
    print(f"  - capacity: 10")
    print(f"  - Active for Rule #5 detection")

if __name__ == "__main__":
    test_aisle_generation()