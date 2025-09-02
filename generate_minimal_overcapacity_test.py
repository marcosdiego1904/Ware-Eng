#!/usr/bin/env python3
"""
Generate Well-Managed Warehouse Test with Minimal Overcapacity

This creates a test with the same scale (~2,140 pallets) but represents a 
well-managed warehouse with minimal overcapacity issues - showing how the 
enhancement works in optimal conditions.

Target Scenario:
- ~2,140 pallets across ~1,200 locations (same scale)
- Only 5-10% overcapacity rate (vs 20%+ in previous test)
- Demonstrates enhancement efficiency with fewer but still meaningful alerts
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_optimized_storage_inventory():
    """Generate well-managed storage location inventory"""
    
    pallets = []
    pallet_counter = 1
    
    print("Generating well-managed storage locations...")
    
    # Expand storage grid: same capacity as before
    storage_locations = []
    for aisle in range(1, 7):  # 6 aisles
        for rack in range(1, 9):  # 8 racks each
            for position in range(1, 21):  # 20 positions each
                for level in ['A', 'B', 'C']:  # 3 levels each
                    location = f"{aisle}-{rack:02d}-{position:03d}{level}"
                    storage_locations.append(location)
    
    # Normal capacity storage locations (1,400 locations with 1 pallet each)
    normal_storage_count = 1400
    normal_locations = random.sample(storage_locations, normal_storage_count)
    
    for location in normal_locations:
        pallets.append({
            'pallet_id': f'PLT-{pallet_counter:05d}',
            'location': location,
            'product_code': f'PROD-{random.randint(1000, 9999)}',
            'lot_number': f'LOT{random.randint(10000, 99999)}',
            'quantity': random.randint(10, 150),
            'received_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S'),
            'expiry_date': (datetime.now() + timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
            'temperature_zone': random.choice(['AMBIENT', 'COLD', 'FROZEN'])
        })
        pallet_counter += 1
    
    print(f"Created {len(normal_locations)} normal storage locations")
    
    # Minimal overcapacity storage locations - well-managed warehouse
    overcapacity_storage = []
    
    # Only mild overcapacity (2 pallets in 1-capacity locations) - 15 locations
    mild_overcapacity_locs = random.sample([loc for loc in storage_locations if loc not in normal_locations], 15)
    for location in mild_overcapacity_locs:
        overcapacity_storage.append({'location': location, 'pallets': 2})
    
    # Very few moderate overcapacity (3 pallets) - 5 locations
    moderate_overcapacity_locs = random.sample([loc for loc in storage_locations if loc not in normal_locations and loc not in mild_overcapacity_locs], 5)
    for location in moderate_overcapacity_locs:
        overcapacity_storage.append({'location': location, 'pallets': 3})
    
    # Generate pallets for overcapacity locations
    for oc_info in overcapacity_storage:
        for i in range(oc_info['pallets']):
            pallets.append({
                'pallet_id': f'PLT-{pallet_counter:05d}',
                'location': oc_info['location'],
                'product_code': f'PROD-{random.randint(1000, 9999)}',
                'lot_number': f'LOT{random.randint(10000, 99999)}',
                'quantity': random.randint(10, 150),
                'received_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S'),
                'expiry_date': (datetime.now() + timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
                'temperature_zone': random.choice(['AMBIENT', 'COLD', 'FROZEN'])
            })
            pallet_counter += 1
    
    print(f"Created {len(overcapacity_storage)} minimal overcapacity storage locations:")
    print(f"  - Mild (2 pallets): {len(mild_overcapacity_locs)} locations")
    print(f"  - Moderate (3 pallets): {len(moderate_overcapacity_locs)} locations")
    
    return pallets, pallet_counter

def generate_optimized_special_areas(pallet_counter_start):
    """Generate well-managed special area inventory with minimal overcapacity"""
    
    pallets = []
    pallet_counter = pallet_counter_start
    
    # Well-managed special areas - most within capacity, few overcapacity
    special_areas = {
        # Receiving areas - mostly well-managed
        'RECV-01': {'capacity': 15, 'pallets': 14},    # Just under capacity
        'RECV-02': {'capacity': 15, 'pallets': 12},    # Well under capacity  
        'RECV-03': {'capacity': 12, 'pallets': 16},    # 133% capacity - mild overcapacity
        'RECV-04': {'capacity': 12, 'pallets': 8},     # Normal
        'RECV-05': {'capacity': 10, 'pallets': 9},     # Normal
        'RECV-06': {'capacity': 10, 'pallets': 7},     # Normal
        
        # Staging areas - efficient management
        'STAGE-01': {'capacity': 8, 'pallets': 7},     # Normal
        'STAGE-02': {'capacity': 8, 'pallets': 10},    # 125% capacity - mild overcapacity
        'STAGE-03': {'capacity': 6, 'pallets': 5},     # Normal
        'STAGE-04': {'capacity': 6, 'pallets': 4},     # Normal
        'STAGE-05': {'capacity': 5, 'pallets': 4},     # Normal
        
        # Dock areas - mostly optimal
        'DOCK-01': {'capacity': 3, 'pallets': 3},      # At capacity
        'DOCK-02': {'capacity': 3, 'pallets': 2},      # Under capacity
        'DOCK-03': {'capacity': 2, 'pallets': 3},      # 150% capacity - mild overcapacity
        'DOCK-04': {'capacity': 2, 'pallets': 2},      # At capacity
        'DOCK-05': {'capacity': 4, 'pallets': 3},      # Under capacity
        'DOCK-06': {'capacity': 4, 'pallets': 2},      # Under capacity
        
        # Aisle areas - efficient flow
        'AISLE-01': {'capacity': 12, 'pallets': 11},   # Just under capacity
        'AISLE-02': {'capacity': 12, 'pallets': 10},   # Under capacity
        'AISLE-03': {'capacity': 15, 'pallets': 14},   # Just under capacity  
        'AISLE-04': {'capacity': 15, 'pallets': 18},   # 120% capacity - mild overcapacity
        'AISLE-05': {'capacity': 10, 'pallets': 9},    # Under capacity
        'AISLE-06': {'capacity': 10, 'pallets': 8},    # Under capacity
        'AISLE-07': {'capacity': 8, 'pallets': 7},     # Under capacity
        'AISLE-08': {'capacity': 8, 'pallets': 6},     # Under capacity
        'AISLE-09': {'capacity': 6, 'pallets': 5},     # Under capacity
        'AISLE-10': {'capacity': 6, 'pallets': 4},     # Under capacity
        
        # Bulk storage areas - well-managed
        'BULK-01': {'capacity': 20, 'pallets': 18},    # Under capacity
        'BULK-02': {'capacity': 20, 'pallets': 22},    # 110% capacity - mild overcapacity
        'BULK-03': {'capacity': 25, 'pallets': 23},    # Under capacity
        'BULK-04': {'capacity': 25, 'pallets': 15},    # Well under capacity
        
        # Floor storage areas - optimal
        'FLOOR-01': {'capacity': 30, 'pallets': 28},   # Under capacity
        'FLOOR-02': {'capacity': 30, 'pallets': 32},   # 107% capacity - mild overcapacity
        'FLOOR-03': {'capacity': 35, 'pallets': 30},   # Under capacity
        'FLOOR-04': {'capacity': 35, 'pallets': 20},   # Well under capacity
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
                'received_date': (datetime.now() - timedelta(hours=random.randint(1, 48))).strftime('%Y-%m-%d %H:%M:%S'),  # More recent
                'expiry_date': (datetime.now() + timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
                'temperature_zone': random.choice(['AMBIENT', 'COLD', 'FROZEN'])
            })
            pallet_counter += 1
    
    print(f"Created {len(special_areas)} special areas with {total_pallets_in_special} pallets:")
    print(f"  - Overcapacity areas: {overcapacity_count} (well-managed)")
    print(f"  - Normal areas: {len(special_areas) - overcapacity_count}")
    
    # Print detailed breakdown
    for area_type in ['RECV', 'STAGE', 'DOCK', 'AISLE', 'BULK', 'FLOOR']:
        area_locations = [loc for loc in special_areas.keys() if loc.startswith(area_type)]
        area_overcapacity = sum(1 for loc in area_locations if special_areas[loc]['pallets'] > special_areas[loc]['capacity'])
        if area_locations:
            print(f"    • {area_type} areas: {len(area_locations)} total, {area_overcapacity} overcapacity")
    
    return pallets, pallet_counter, special_areas

def calculate_minimal_expected_results(storage_overcapacity_count, storage_overcapacity_pallets, 
                                     special_overcapacity_count, special_overcapacity_pallets):
    """Calculate expected alert volumes for well-managed scenario"""
    
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
    """Generate well-managed warehouse test inventory"""
    
    print("Generating Well-Managed Warehouse Test with Minimal Overcapacity")
    print("=" * 70)
    
    # Generate storage inventory
    storage_pallets, pallet_counter = generate_optimized_storage_inventory()
    
    # Generate special area inventory  
    special_pallets, final_counter, special_config = generate_optimized_special_areas(pallet_counter)
    
    # Combine all pallets
    all_pallets = storage_pallets + special_pallets
    inventory_df = pd.DataFrame(all_pallets)
    
    print(f"\\nWell-Managed Warehouse Inventory Summary:")
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
    
    print(f"\\nMinimal Overcapacity Analysis:")
    print(f"Storage locations:")
    print(f"  - Total: {storage_pallets_df['location'].nunique():,} locations")
    print(f"  - Overcapacity: {len(storage_overcapacity_locs)} locations ({storage_overcapacity_pallets} pallets)")
    print(f"Special areas:")
    print(f"  - Total: {len(special_config)} locations") 
    print(f"  - Overcapacity: {len(special_overcapacity_locs)} locations ({special_overcapacity_pallets} pallets)")
    
    # Calculate expected results
    results = calculate_minimal_expected_results(
        len(storage_overcapacity_locs), storage_overcapacity_pallets,
        len(special_overcapacity_locs), special_overcapacity_pallets
    )
    
    print(f"\\nExpected Alert Analysis:")
    print(f"Legacy system alerts: {results['legacy_alerts']:,}")
    print(f"Enhanced system alerts: {results['enhanced_alerts']:,}")
    print(f"Expected reduction: {results['reduction_count']:,} alerts ({results['reduction_percentage']:.1f}%)")
    
    # Save to Excel
    output_file = 'well_managed_warehouse_test.xlsx'
    inventory_df.to_excel(output_file, index=False, sheet_name='Inventory')
    
    print(f"\\nCreated well-managed warehouse test file: {output_file}")
    print(f"\\nWell-Managed Scenario Demonstration:")
    print(f"+ Same scale: {len(inventory_df):,} pallets across {inventory_df['location'].nunique():,} locations")
    print(f"+ Minimal overcapacity: {results['legacy_alerts']:,} total alerts (vs 891 in previous test)")
    print(f"+ Efficiency demonstration: {results['reduction_percentage']:.1f}% alert reduction even in optimal conditions")
    print(f"+ Real-world scenario: Shows enhancement value in well-managed warehouses")
    
    print(f"\\nReady for well-managed warehouse testing!")

if __name__ == "__main__":
    main()