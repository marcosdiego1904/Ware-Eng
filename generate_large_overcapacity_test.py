#!/usr/bin/env python3
"""
Generate Large-Scale Overcapacity Test Inventory

This creates a comprehensive test with significantly more pallets and overcapacity
scenarios to demonstrate the enhancement at enterprise scale.

Target Scenario:
- ~2,000+ pallets across ~800+ locations
- Multiple warehouse zones with different capacity patterns
- High overcapacity volume to showcase dramatic alert reduction
- Mix of mild and severe overcapacity situations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_large_storage_inventory():
    """Generate large-scale storage location inventory"""
    
    pallets = []
    pallet_counter = 1
    
    # Expand storage grid: 6 aisles × 8 racks × 20 positions × 3 levels = 2,880 possible locations
    print("Generating large-scale storage locations...")
    
    # Normal capacity storage locations (1,200 locations with 1 pallet each)
    normal_storage_count = 1200
    storage_locations = []
    
    for aisle in range(1, 7):  # 6 aisles
        for rack in range(1, 9):  # 8 racks each
            for position in range(1, 21):  # 20 positions each
                for level in ['A', 'B', 'C']:  # 3 levels each
                    location = f"{aisle}-{rack:02d}-{position:03d}{level}"
                    storage_locations.append(location)
    
    # Select random subset for normal capacity
    normal_locations = random.sample(storage_locations, normal_storage_count)
    
    for location in normal_locations:
        pallets.append({
            'pallet_id': f'PLT-{pallet_counter:05d}',
            'location': location,
            'product_code': f'PROD-{random.randint(1000, 9999)}',
            'lot_number': f'LOT{random.randint(10000, 99999)}',
            'quantity': random.randint(10, 150),
            'received_date': (datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S'),
            'expiry_date': (datetime.now() + timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
            'temperature_zone': random.choice(['AMBIENT', 'COLD', 'FROZEN'])
        })
        pallet_counter += 1
    
    print(f"Created {len(normal_locations)} normal storage locations")
    
    # Overcapacity storage locations - create significant overcapacity scenarios
    overcapacity_storage = []
    
    # Mild overcapacity (2 pallets in 1-capacity locations) - 80 locations
    mild_overcapacity_locs = random.sample([loc for loc in storage_locations if loc not in normal_locations], 80)
    for location in mild_overcapacity_locs:
        overcapacity_storage.append({'location': location, 'pallets': 2})
    
    # Moderate overcapacity (3 pallets in 1-capacity locations) - 40 locations  
    moderate_overcapacity_locs = random.sample([loc for loc in storage_locations if loc not in normal_locations and loc not in mild_overcapacity_locs], 40)
    for location in moderate_overcapacity_locs:
        overcapacity_storage.append({'location': location, 'pallets': 3})
    
    # Severe overcapacity (4-5 pallets in 1-capacity locations) - 20 locations
    severe_overcapacity_locs = random.sample([loc for loc in storage_locations if loc not in normal_locations and loc not in mild_overcapacity_locs and loc not in moderate_overcapacity_locs], 20)
    for location in severe_overcapacity_locs:
        overcapacity_storage.append({'location': location, 'pallets': random.randint(4, 5)})
    
    # Generate pallets for overcapacity locations
    for oc_info in overcapacity_storage:
        for i in range(oc_info['pallets']):
            pallets.append({
                'pallet_id': f'PLT-{pallet_counter:05d}',
                'location': oc_info['location'],
                'product_code': f'PROD-{random.randint(1000, 9999)}',
                'lot_number': f'LOT{random.randint(10000, 99999)}',
                'quantity': random.randint(10, 150),
                'received_date': (datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S'),
                'expiry_date': (datetime.now() + timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
                'temperature_zone': random.choice(['AMBIENT', 'COLD', 'FROZEN'])
            })
            pallet_counter += 1
    
    print(f"Created {len(overcapacity_storage)} overcapacity storage locations:")
    print(f"  - Mild (2 pallets): {len(mild_overcapacity_locs)} locations")
    print(f"  - Moderate (3 pallets): {len(moderate_overcapacity_locs)} locations") 
    print(f"  - Severe (4-5 pallets): {len(severe_overcapacity_locs)} locations")
    
    return pallets, pallet_counter

def generate_large_special_areas(pallet_counter_start):
    """Generate large-scale special area inventory with significant overcapacity"""
    
    pallets = []
    pallet_counter = pallet_counter_start
    
    # Expanded special areas with varying capacities and overcapacity scenarios
    special_areas = {
        # Receiving areas - high volume processing
        'RECV-01': {'capacity': 15, 'pallets': 22},    # 147% capacity 
        'RECV-02': {'capacity': 15, 'pallets': 18},    # 120% capacity
        'RECV-03': {'capacity': 12, 'pallets': 17},    # 142% capacity
        'RECV-04': {'capacity': 12, 'pallets': 8},     # Normal
        'RECV-05': {'capacity': 10, 'pallets': 14},    # 140% capacity
        'RECV-06': {'capacity': 10, 'pallets': 6},     # Normal
        
        # Staging areas - temporary holding  
        'STAGE-01': {'capacity': 8, 'pallets': 12},    # 150% capacity
        'STAGE-02': {'capacity': 8, 'pallets': 11},    # 138% capacity
        'STAGE-03': {'capacity': 6, 'pallets': 9},     # 150% capacity
        'STAGE-04': {'capacity': 6, 'pallets': 4},     # Normal
        'STAGE-05': {'capacity': 5, 'pallets': 8},     # 160% capacity
        
        # Dock areas - shipping/receiving
        'DOCK-01': {'capacity': 3, 'pallets': 5},      # 167% capacity
        'DOCK-02': {'capacity': 3, 'pallets': 4},      # 133% capacity
        'DOCK-03': {'capacity': 2, 'pallets': 4},      # 200% capacity
        'DOCK-04': {'capacity': 2, 'pallets': 3},      # 150% capacity
        'DOCK-05': {'capacity': 4, 'pallets': 6},      # 150% capacity
        'DOCK-06': {'capacity': 4, 'pallets': 2},      # Normal
        
        # Aisle areas - transitional zones
        'AISLE-01': {'capacity': 12, 'pallets': 18},   # 150% capacity
        'AISLE-02': {'capacity': 12, 'pallets': 16},   # 133% capacity  
        'AISLE-03': {'capacity': 15, 'pallets': 22},   # 147% capacity
        'AISLE-04': {'capacity': 15, 'pallets': 25},   # 167% capacity
        'AISLE-05': {'capacity': 10, 'pallets': 16},   # 160% capacity
        'AISLE-06': {'capacity': 10, 'pallets': 15},   # 150% capacity
        'AISLE-07': {'capacity': 8, 'pallets': 13},    # 163% capacity
        'AISLE-08': {'capacity': 8, 'pallets': 12},    # 150% capacity
        'AISLE-09': {'capacity': 6, 'pallets': 10},    # 167% capacity
        'AISLE-10': {'capacity': 6, 'pallets': 4},     # Normal
        
        # Bulk storage areas - high capacity
        'BULK-01': {'capacity': 20, 'pallets': 28},    # 140% capacity
        'BULK-02': {'capacity': 20, 'pallets': 32},    # 160% capacity
        'BULK-03': {'capacity': 25, 'pallets': 35},    # 140% capacity
        'BULK-04': {'capacity': 25, 'pallets': 15},    # Normal
        
        # Floor storage areas
        'FLOOR-01': {'capacity': 30, 'pallets': 45},   # 150% capacity
        'FLOOR-02': {'capacity': 30, 'pallets': 42},   # 140% capacity
        'FLOOR-03': {'capacity': 35, 'pallets': 50},   # 143% capacity
        'FLOOR-04': {'capacity': 35, 'pallets': 20},   # Normal
    }
    
    overcapacity_count = 0
    total_pallets_in_special = 0
    
    for location, config in special_areas.items():
        area_type = location.split('-')[0]
        
        if config['pallets'] > config['capacity']:
            overcapacity_count += 1
        
        total_pallets_in_special += config['pallets']
        
        for i in range(config['pallets']):
            pallets.append({
                'pallet_id': f'{area_type}-{pallet_counter:05d}',
                'location': location,
                'product_code': f'PROD-{random.randint(1000, 9999)}',
                'lot_number': f'LOT{random.randint(10000, 99999)}',
                'quantity': random.randint(75, 300),  # Larger quantities for special areas
                'received_date': (datetime.now() - timedelta(hours=random.randint(1, 168))).strftime('%Y-%m-%d %H:%M:%S'),
                'expiry_date': (datetime.now() + timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
                'temperature_zone': random.choice(['AMBIENT', 'COLD', 'FROZEN'])
            })
            pallet_counter += 1
    
    print(f"Created {len(special_areas)} special areas with {total_pallets_in_special} pallets:")
    print(f"  - Overcapacity areas: {overcapacity_count}")
    print(f"  - Normal areas: {len(special_areas) - overcapacity_count}")
    
    # Print detailed breakdown
    for area_type in ['RECV', 'STAGE', 'DOCK', 'AISLE', 'BULK', 'FLOOR']:
        area_locations = [loc for loc in special_areas.keys() if loc.startswith(area_type)]
        area_overcapacity = sum(1 for loc in area_locations if special_areas[loc]['pallets'] > special_areas[loc]['capacity'])
        if area_locations:
            print(f"    • {area_type} areas: {len(area_locations)} total, {area_overcapacity} overcapacity")
    
    return pallets, pallet_counter, special_areas

def calculate_expected_results(storage_overcapacity_count, storage_overcapacity_pallets, 
                             special_overcapacity_count, special_overcapacity_pallets):
    """Calculate expected alert volumes for comparison"""
    
    # Legacy: Individual alerts for ALL pallets in overcapacity locations
    legacy_alerts = storage_overcapacity_pallets + special_overcapacity_pallets
    
    # Enhanced: Individual alerts for storage + location-level alerts for special areas
    enhanced_alerts = storage_overcapacity_pallets + special_overcapacity_count
    
    reduction_count = legacy_alerts - enhanced_alerts
    reduction_percentage = (reduction_count / legacy_alerts) * 100 if legacy_alerts > 0 else 0
    
    return {
        'legacy_alerts': legacy_alerts,
        'enhanced_alerts': enhanced_alerts,
        'reduction_count': reduction_count,
        'reduction_percentage': reduction_percentage
    }

def main():
    """Generate large-scale test inventory"""
    
    print("Generating Large-Scale Overcapacity Test Inventory")
    print("=" * 60)
    
    # Generate storage inventory
    storage_pallets, pallet_counter = generate_large_storage_inventory()
    
    # Generate special area inventory  
    special_pallets, final_counter, special_config = generate_large_special_areas(pallet_counter)
    
    # Combine all pallets
    all_pallets = storage_pallets + special_pallets
    inventory_df = pd.DataFrame(all_pallets)
    
    print(f"\\nLarge-Scale Inventory Summary:")
    print(f"Total pallets: {len(inventory_df):,}")
    print(f"Unique locations: {inventory_df['location'].nunique():,}")
    
    # Analyze overcapacity scenarios
    location_counts = inventory_df['location'].value_counts()
    
    # Storage analysis
    storage_pattern = r'^\d+-\d+-\d+[A-Z]$'
    storage_pallets_df = inventory_df[inventory_df['location'].str.match(storage_pattern)]
    storage_overcapacity_locs = []
    storage_overcapacity_pallets = 0
    
    for location in storage_pallets_df['location'].unique():
        count = location_counts[location]
        if count > 1:  # Storage capacity is 1
            storage_overcapacity_locs.append((location, count))
            storage_overcapacity_pallets += count
    
    # Special areas analysis
    special_pallets_df = inventory_df[~inventory_df['location'].str.match(storage_pattern)]
    special_overcapacity_locs = []
    special_overcapacity_pallets = 0
    
    for location, config in special_config.items():
        count = location_counts[location]
        if count > config['capacity']:
            special_overcapacity_locs.append((location, count, config['capacity']))
            special_overcapacity_pallets += count
    
    print(f"\\nOvercapacity Analysis:")
    print(f"Storage locations:")
    print(f"  - Total: {storage_pallets_df['location'].nunique():,} locations")
    print(f"  - Overcapacity: {len(storage_overcapacity_locs)} locations ({storage_overcapacity_pallets} pallets)")
    print(f"Special areas:")
    print(f"  - Total: {len(special_config)} locations") 
    print(f"  - Overcapacity: {len(special_overcapacity_locs)} locations ({special_overcapacity_pallets} pallets)")
    
    # Calculate expected results
    results = calculate_expected_results(
        len(storage_overcapacity_locs), storage_overcapacity_pallets,
        len(special_overcapacity_locs), special_overcapacity_pallets
    )
    
    print(f"\\nExpected Alert Analysis:")
    print(f"Legacy system alerts: {results['legacy_alerts']:,}")
    print(f"Enhanced system alerts: {results['enhanced_alerts']:,}")
    print(f"Expected reduction: {results['reduction_count']:,} alerts ({results['reduction_percentage']:.1f}%)")
    
    # Save to Excel
    output_file = 'large_scale_overcapacity_test.xlsx'
    inventory_df.to_excel(output_file, index=False, sheet_name='Inventory')
    
    print(f"\\nCreated large-scale test file: {output_file}")
    print(f"\\nTest Impact Demonstration:")
    print(f"+ Enterprise scale: {len(inventory_df):,} pallets across {inventory_df['location'].nunique():,} locations")
    print(f"+ High overcapacity volume: {results['legacy_alerts']:,} total alerts")
    print(f"+ Dramatic reduction potential: {results['reduction_percentage']:.1f}% alert reduction")
    print(f"+ Real-world complexity: Mixed capacity scenarios and area types")
    
    print(f"\\nReady for large-scale testing!")

if __name__ == "__main__":
    main()