#!/usr/bin/env python3
"""
Generate Test Inventory Report for Overcapacity Enhancement Demo

This script creates a realistic inventory report (Excel file) that demonstrates
the location type differentiation enhancement with a mix of:
- Storage locations (1 pallet capacity each) - some overcapacity
- Special areas (varying capacities) - some overcapacity  

The data will show the dramatic alert reduction when using location differentiation.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_test_inventory():
    """Generate test inventory data with strategic overcapacity scenarios"""
    
    pallets = []
    
    # Storage rack locations (X-XX-XXX pattern) - 1 pallet capacity each
    # Create a mix of normal and overcapacity situations
    storage_locations = []
    
    # Generate storage locations: 3 aisles, 5 racks each, 10 positions each, 2 levels (A, B)
    for aisle in range(1, 4):  # Aisles 1-3
        for rack in range(1, 6):  # Racks 1-5  
            for position in range(1, 11):  # Positions 1-10
                for level in ['A', 'B']:  # Levels A, B
                    location = f"{aisle}-{rack:02d}-{position:03d}{level}"
                    storage_locations.append(location)
    
    print(f"Generated {len(storage_locations)} storage locations")
    
    # Normal storage locations (within capacity - 1 pallet each)
    normal_storage = random.sample(storage_locations, 250)  # 250 normal locations
    for i, location in enumerate(normal_storage):
        pallets.append({
            'pallet_id': f'PLT-{i+1:04d}',
            'location': location,
            'product_code': f'PROD-{random.randint(100, 999)}',
            'lot_number': f'LOT{random.randint(1000, 9999)}',
            'quantity': random.randint(10, 100),
            'received_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S'),
            'expiry_date': (datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
            'temperature_zone': random.choice(['AMBIENT', 'COLD', 'FROZEN'])
        })
    
    # Overcapacity storage locations (2 pallets in 1-capacity locations)
    overcapacity_storage = [
        '1-01-001A',  # 2 pallets
        '1-02-005B',  # 2 pallets  
        '2-03-007A',  # 2 pallets
        '3-01-002B',  # 2 pallets
        '3-04-009A'   # 2 pallets
    ]
    
    pallet_counter = 251
    for location in overcapacity_storage:
        # Add 2 pallets to each overcapacity storage location
        for j in range(2):
            pallets.append({
                'pallet_id': f'PLT-{pallet_counter:04d}',
                'location': location,
                'product_code': f'PROD-{random.randint(100, 999)}',
                'lot_number': f'LOT{random.randint(1000, 9999)}',
                'quantity': random.randint(10, 100),
                'received_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S'),
                'expiry_date': (datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                'temperature_zone': random.choice(['AMBIENT', 'COLD', 'FROZEN'])
            })
            pallet_counter += 1
    
    print(f"Created {len(overcapacity_storage)} overcapacity storage locations with 2 pallets each")
    
    # Special areas - mix of normal and overcapacity
    special_areas = {
        # Normal capacity special areas
        'RECV-02': {'capacity': 10, 'pallets': 8},     # Within capacity
        'STAGE-01': {'capacity': 5, 'pallets': 3},     # Within capacity
        'AISLE-02': {'capacity': 10, 'pallets': 7},    # Within capacity
        'AISLE-03': {'capacity': 10, 'pallets': 9},    # Within capacity
        'AISLE-05': {'capacity': 10, 'pallets': 6},    # Within capacity
        
        # Overcapacity special areas
        'RECV-01': {'capacity': 10, 'pallets': 12},    # 120% capacity
        'DOCK-01': {'capacity': 2, 'pallets': 3},      # 150% capacity  
        'AISLE-01': {'capacity': 10, 'pallets': 13},   # 130% capacity
        'AISLE-04': {'capacity': 10, 'pallets': 15},   # 150% capacity
    }
    
    for location, config in special_areas.items():
        area_type = location.split('-')[0]
        for j in range(config['pallets']):
            pallets.append({
                'pallet_id': f'{area_type}-{pallet_counter:04d}',
                'location': location,
                'product_code': f'PROD-{random.randint(100, 999)}',
                'lot_number': f'LOT{random.randint(1000, 9999)}',
                'quantity': random.randint(50, 200),  # Larger quantities for special areas
                'received_date': (datetime.now() - timedelta(hours=random.randint(1, 72))).strftime('%Y-%m-%d %H:%M:%S'),
                'expiry_date': (datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                'temperature_zone': random.choice(['AMBIENT', 'COLD', 'FROZEN'])
            })
            pallet_counter += 1
    
    print(f"Created special area inventory:")
    for location, config in special_areas.items():
        status = "OVERCAPACITY" if config['pallets'] > config['capacity'] else "NORMAL"
        print(f"  - {location}: {config['pallets']}/{config['capacity']} pallets ({status})")
    
    return pd.DataFrame(pallets)

def create_expected_results_summary():
    """Create a summary of expected results for validation"""
    
    summary = {
        'total_pallets': 0,
        'storage_locations': {
            'total': 255,  # 250 normal + 5 overcapacity
            'overcapacity': 5,
            'overcapacity_pallets': 10  # 2 pallets each in 5 locations
        },
        'special_areas': {
            'total': 9,
            'overcapacity': 4,  # RECV-01, DOCK-01, AISLE-01, AISLE-04
            'overcapacity_pallets': 43  # 12+3+13+15
        },
        'legacy_alerts': 0,  # Will be calculated
        'enhanced_alerts': 0,  # Will be calculated
        'expected_reduction': 0  # Will be calculated
    }
    
    # Calculate expected alerts
    summary['legacy_alerts'] = summary['storage_locations']['overcapacity_pallets'] + summary['special_areas']['overcapacity_pallets']
    summary['enhanced_alerts'] = summary['storage_locations']['overcapacity_pallets'] + summary['special_areas']['overcapacity']  # Individual + location-level
    summary['expected_reduction'] = ((summary['legacy_alerts'] - summary['enhanced_alerts']) / summary['legacy_alerts']) * 100
    
    return summary

def main():
    """Generate test inventory Excel file"""
    
    print("Generating Test Inventory for Overcapacity Enhancement Demo")
    print("=" * 60)
    
    # Generate inventory data
    inventory_df = generate_test_inventory()
    
    # Add summary statistics
    print(f"\\nInventory Summary:")
    print(f"Total pallets: {len(inventory_df)}")
    print(f"Unique locations: {inventory_df['location'].nunique()}")
    
    # Analyze by location type
    storage_pattern = r'^\d+-\d+-\d+[A-Z]$'
    storage_pallets = inventory_df[inventory_df['location'].str.match(storage_pattern)]
    special_pallets = inventory_df[~inventory_df['location'].str.match(storage_pattern)]
    
    print(f"Storage locations: {storage_pallets['location'].nunique()} locations, {len(storage_pallets)} pallets")
    print(f"Special areas: {special_pallets['location'].nunique()} locations, {len(special_pallets)} pallets")
    
    # Save to Excel
    output_file = 'inventoryreport.xlsx'
    inventory_df.to_excel(output_file, index=False, sheet_name='Inventory')
    
    print(f"\\nCreated test inventory file: {output_file}")
    
    # Generate expected results
    expected = create_expected_results_summary()
    
    print(f"\\nExpected Test Results:")
    print(f"Legacy system alerts: {expected['legacy_alerts']}")
    print(f"Enhanced system alerts: {expected['enhanced_alerts']}")
    print(f"Expected reduction: {expected['expected_reduction']:.1f}%")
    
    print(f"\\nTest Scenarios Created:")
    print(f"+ Storage overcapacity: 5 locations with 2 pallets each (10 individual alerts)")
    print(f"+ Special area overcapacity: 4 areas with varying excess (4 location-level alerts)")
    print(f"+ Normal capacity locations: Mixed storage and special areas within limits")
    
    print(f"\\nNext Steps:")
    print(f"1. Upload {output_file} to your WMS system")
    print(f"2. Run analysis with standard overcapacity rule")
    print(f"3. Run analysis with enhanced location differentiation rule")
    print(f"4. Compare alert volumes to validate ~{expected['expected_reduction']:.0f}% reduction")

if __name__ == "__main__":
    main()