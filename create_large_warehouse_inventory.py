#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Large Warehouse Inventory Report
Doubled size: 8 aisles × 8 racks × 10 positions × 2 levels = 1,280 storage locations
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_large_warehouse_inventory():
    """Create inventory for doubled warehouse size"""
    
    # DOUBLED warehouse structure
    WAREHOUSE_STRUCTURE = {
        'aisles': 8,           # 8 aisles (01-08)
        'racks': 8,            # 8 racks per aisle (01-08)  
        'positions': 10,       # 10 positions per rack (001-010)
        'levels': ['A', 'B'],  # 2 levels per position (A, B)
        'capacity_per_level': 1  # 1 pallet per level
    }
    
    # Generate all possible storage locations
    def generate_storage_locations():
        locations = []
        for aisle in range(1, WAREHOUSE_STRUCTURE['aisles'] + 1):
            for rack in range(1, WAREHOUSE_STRUCTURE['racks'] + 1):
                for position in range(1, WAREHOUSE_STRUCTURE['positions'] + 1):
                    for level in WAREHOUSE_STRUCTURE['levels']:
                        location_code = f'{aisle:02d}-{rack:02d}-{position:03d}{level}'
                        locations.append(location_code)
        return locations
    
    all_storage_locations = generate_storage_locations()
    print(f'Generated {len(all_storage_locations)} storage locations (8x8x10x2)')
    print(f'Sample locations: {all_storage_locations[:15]}')
    
    # More special areas for larger warehouse
    special_areas = ['RCV-001', 'RCV-002', 'RCV-003', 'RCV-004', 'RCV-005', 
                    'STG-001', 'STG-002', 'STG-003', 'STG-004',
                    'DOCK-01', 'DOCK-02', 'DOCK-03', 'DOCK-04']
    
    inventory_records = []
    base_time = datetime.now()
    pallet_id = 5000  # Start with 5000 for large warehouse
    
    # More product types for variety
    product_types = ['ELECTRONICS', 'CLOTHING', 'FURNITURE', 'BOOKS', 'TOOLS', 
                    'FOOD', 'AUTOMOTIVE', 'TOYS', 'APPLIANCES', 'CHEMICALS']
    receipt_numbers = [f'RCP{8000 + i}' for i in range(100)]  # 100 receipt numbers
    
    print('Creating large warehouse inventory scenarios...')
    
    # Scenario 1: Stagnant pallets in receiving (scaled up)
    print('1. Adding stagnant pallets in receiving...')
    for i in range(25):  # 25 stagnant pallets (scaled from 12)
        old_time = base_time - timedelta(hours=random.randint(7, 48))  # 7-48 hours old
        inventory_records.append({
            'pallet_id': f'PLT{pallet_id}',
            'location': random.choice(['RCV-001', 'RCV-002', 'RCV-003', 'RCV-004', 'RCV-005']),
            'creation_date': old_time.strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': random.choice(receipt_numbers),
            'description': random.choice(product_types),
            'lot_number': f'LOT{2000 + i}',
            'quantity': random.randint(25, 150)
        })
        pallet_id += 1
    
    # Scenario 2: Multiple incomplete lots (scaled up)
    print('2. Adding incomplete lot scenarios...')
    # Create 3 different incomplete lots
    incomplete_lots = [
        {'lot': 'LOT3000', 'receipt': 'RCP9000', 'total': 10, 'stored': 7},  # 70% completion
        {'lot': 'LOT3001', 'receipt': 'RCP9001', 'total': 12, 'stored': 9},  # 75% completion  
        {'lot': 'LOT3002', 'receipt': 'RCP9002', 'total': 15, 'stored': 11}, # 73% completion
    ]
    
    for lot_info in incomplete_lots:
        for i in range(lot_info['total']):
            if i < lot_info['stored']:  # Stored pallets
                location = random.choice(all_storage_locations[:200])  # Use first 200 locations
                creation_time = base_time - timedelta(hours=random.randint(2, 12))
            else:  # Remaining pallets in receiving
                location = random.choice(['RCV-002', 'RCV-003', 'RCV-004'])
                creation_time = base_time - timedelta(hours=random.randint(8, 20))
            
            inventory_records.append({
                'pallet_id': f'PLT{pallet_id}',
                'location': location,
                'creation_date': creation_time.strftime('%Y-%m-%d %H:%M:%S'),
                'receipt_number': lot_info['receipt'],
                'description': random.choice(['ELECTRONICS', 'AUTOMOTIVE', 'APPLIANCES']),
                'lot_number': lot_info['lot'],
                'quantity': random.randint(40, 100)
            })
            pallet_id += 1
    
    # Scenario 3: Overcapacity locations (scaled up)
    print('3. Adding overcapacity scenarios...')
    # Pick 15 specific locations and put 2-3 pallets each
    overcap_scenarios = [
        # 2 pallets each (10 locations)
        {'locations': [f'0{a}-0{r}-00{p}A' for a in range(1,4) for r in range(1,4) for p in range(1,3)][:10], 'pallets': 2},
        # 3 pallets each (5 locations) 
        {'locations': [f'0{a}-0{r}-00{p}B' for a in range(4,7) for r in range(1,3) for p in range(3,6)][:5], 'pallets': 3}
    ]
    
    for scenario in overcap_scenarios:
        for location in scenario['locations']:
            for i in range(scenario['pallets']):
                inventory_records.append({
                    'pallet_id': f'PLT{pallet_id}',
                    'location': location,
                    'creation_date': (base_time - timedelta(hours=random.randint(1, 10))).strftime('%Y-%m-%d %H:%M:%S'),
                    'receipt_number': f'RCP{10000 + len(inventory_records)}',
                    'description': random.choice(product_types),
                    'lot_number': f'LOT{4000 + len(inventory_records)}',
                    'quantity': random.randint(30, 90)
                })
                pallet_id += 1
    
    # Scenario 4: Invalid locations (scaled up)
    print('4. Adding invalid location tests...')
    invalid_locations = ['INVALID-ZONE-1', 'MISSING-LOC-2', 'TYPO-LOCATION-3', 
                        'WRONG-FORMAT', 'BAD-AISLE-99', 'UNKNOWN-AREA']
    for invalid_loc in invalid_locations:
        inventory_records.append({
            'pallet_id': f'PLT{pallet_id}',
            'location': invalid_loc,
            'creation_date': (base_time - timedelta(hours=random.randint(1, 6))).strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': f'RCP{11000 + len(inventory_records)}',
            'description': random.choice(product_types),
            'lot_number': f'LOT{5000 + len(inventory_records)}',
            'quantity': random.randint(20, 80)
        })
        pallet_id += 1
    
    # Scenario 5: Normal stored pallets (scaled up significantly)
    print('5. Adding normally stored pallets...')
    # Use a much larger subset of storage locations (30% utilization)
    num_used_locations = int(len(all_storage_locations) * 0.3)  # 30% of 1280 = 384 locations
    used_storage_locations = random.sample(all_storage_locations, num_used_locations)
    
    for i, location in enumerate(used_storage_locations):
        inventory_records.append({
            'pallet_id': f'PLT{pallet_id}',
            'location': location,
            'creation_date': (base_time - timedelta(hours=random.randint(24, 336))).strftime('%Y-%m-%d %H:%M:%S'),  # 1-14 days old
            'receipt_number': random.choice(receipt_numbers),
            'description': random.choice(product_types),
            'lot_number': f'LOT{6000 + i}',
            'quantity': random.randint(20, 150)
        })
        pallet_id += 1
    
    # Scenario 6: Staging and dock workflow (scaled up)
    print('6. Adding staging and dock workflow...')
    # More pallets in staging workflow
    for i in range(20):  # 20 pallets in staging
        inventory_records.append({
            'pallet_id': f'PLT{pallet_id}',
            'location': random.choice(['STG-001', 'STG-002', 'STG-003', 'STG-004']),
            'creation_date': (base_time - timedelta(hours=random.randint(1, 12))).strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': f'RCP{12000 + i}',
            'description': random.choice(product_types),
            'lot_number': f'LOT{7000 + i}',
            'quantity': random.randint(15, 75)
        })
        pallet_id += 1
    
    # Some pallets at docks (outbound)
    for i in range(15):  # 15 pallets at docks
        inventory_records.append({
            'pallet_id': f'PLT{pallet_id}',
            'location': random.choice(['DOCK-01', 'DOCK-02', 'DOCK-03', 'DOCK-04']),
            'creation_date': (base_time - timedelta(hours=random.randint(1, 6))).strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': f'RCP{13000 + i}',
            'description': random.choice(product_types),
            'lot_number': f'LOT{8000 + i}',
            'quantity': random.randint(10, 60)
        })
        pallet_id += 1
    
    return inventory_records

def main():
    print('Creating Large Warehouse Inventory Report')
    print('Structure: 8 aisles x 8 racks x 10 positions x 2 levels = 1,280 storage locations')
    print('=' * 80)
    
    # Create inventory data
    inventory_data = create_large_warehouse_inventory()
    
    # Create DataFrame
    inventory_df = pd.DataFrame(inventory_data)
    
    # Save to Excel
    filename = 'LargeWarehouse_Inventory.xlsx'
    inventory_df.to_excel(filename, index=False)
    
    print(f'Created {filename} with {len(inventory_df)} pallets')
    
    # Summary by location type
    location_summary = {}
    for _, row in inventory_df.iterrows():
        location = row['location']
        if location.startswith('RCV-'):
            loc_type = 'RECEIVING'
        elif location.startswith('STG-'):
            loc_type = 'STAGING'  
        elif location.startswith('DOCK-'):
            loc_type = 'DOCK'
        elif any(location.startswith(invalid) for invalid in ['INVALID', 'MISSING', 'TYPO', 'WRONG', 'BAD', 'UNKNOWN']):
            loc_type = 'INVALID'
        elif '-' in location and len(location.split('-')) >= 3:
            loc_type = 'STORAGE'
        else:
            loc_type = 'OTHER'
        
        location_summary[loc_type] = location_summary.get(loc_type, 0) + 1
    
    print(f'\\nInventory Distribution:')
    for loc_type, count in sorted(location_summary.items()):
        print(f'   {loc_type}: {count} pallets')
    
    print(f'\\nExpected Test Results:')
    print(f'   - Stagnant Pallets: ~25 anomalies (7-48h old in receiving)')
    print(f'   - Incomplete Lots: 3 anomalies (3 lots with <80% completion)')
    print(f'   - Overcapacity: ~25 anomalies (10 locations x 2 + 5 locations x 3)')
    print(f'   - Invalid Locations: 6 anomalies')  
    print(f'   - Normal Operations: ~400+ pallets should be fine')
    print(f'   - TOTAL EXPECTED: ~59 anomalies')
    
    print(f'\\nWarehouse Utilization:')
    storage_pallets = location_summary.get('STORAGE', 0)
    total_capacity = 1280  # 8x8x10x2
    utilization = (storage_pallets / total_capacity) * 100
    print(f'   Storage locations used: {storage_pallets} / 1,280 ({utilization:.1f}% utilization)')

if __name__ == '__main__':
    main()