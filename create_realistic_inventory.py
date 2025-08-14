#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Realistic Inventory Report for Central Distribution Center
Based on actual warehouse structure: 4 aisles × 4 racks × 5 positions × 2 levels
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_realistic_inventory():
    """Create inventory data adapted to the actual warehouse structure"""
    
    # Warehouse structure
    WAREHOUSE_STRUCTURE = {
        'aisles': 4,           # 4 aisles (01, 02, 03, 04)
        'racks': 4,            # 4 racks per aisle (01, 02, 03, 04)  
        'positions': 5,        # 5 positions per rack (001, 002, 003, 004, 005)
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
                        location_code = f"{aisle:02d}-{rack:02d}-{position:03d}{level}"
                        locations.append(location_code)
        return locations
    
    all_storage_locations = generate_storage_locations()
    print(f"Generated {len(all_storage_locations)} possible storage locations")
    print(f"Sample locations: {all_storage_locations[:10]}")
    
    # Special areas (these should exist in your warehouse)
    special_areas = ['RCV-001', 'RCV-002', 'RCV-003', 'STG-001', 'STG-002', 'DOCK-01', 'DOCK-02']
    
    inventory_records = []
    base_time = datetime.now()
    pallet_id = 2000  # Start with 2000 to differentiate from previous test
    
    # Product types
    product_types = ['ELECTRONICS', 'CLOTHING', 'FURNITURE', 'BOOKS', 'TOOLS', 'FOOD']
    receipt_numbers = [f'RCP{3000 + i}' for i in range(30)]
    
    print(f"\nCreating inventory scenarios...")
    
    # Scenario 1: Stagnant pallets in receiving (should trigger Forgotten Pallets Alert)
    print("1. Adding stagnant pallets in receiving...")
    for i in range(12):  # 12 stagnant pallets (more realistic)
        old_time = base_time - timedelta(hours=random.randint(7, 36))  # 7-36 hours old
        inventory_records.append({
            'pallet_id': f'PLT{pallet_id}',
            'location': random.choice(['RCV-001', 'RCV-002', 'RCV-003']),
            'creation_date': old_time.strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': random.choice(receipt_numbers),
            'description': random.choice(product_types),
            'lot_number': f'LOT{1000 + i}',
            'quantity': random.randint(25, 100)
        })
        pallet_id += 1
    
    # Scenario 2: Incomplete lot (should trigger Incomplete Lots Alert)
    print("2. Adding incomplete lot scenario...")
    incomplete_lot = 'LOT2000'
    shared_receipt = 'RCP4000'
    # Create 8 pallets in lot, store 6, leave 2 in receiving (75% completion, should trigger 80% threshold)
    for i in range(8):
        if i < 6:  # First 6 pallets stored
            location = random.choice(all_storage_locations[:100])  # Use first 100 storage locations
            creation_time = base_time - timedelta(hours=random.randint(2, 8))
        else:  # Last 2 pallets still in receiving 
            location = random.choice(['RCV-002', 'RCV-003'])
            creation_time = base_time - timedelta(hours=random.randint(8, 15))
        
        inventory_records.append({
            'pallet_id': f'PLT{pallet_id}',
            'location': location,
            'creation_date': creation_time.strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': shared_receipt,
            'description': 'ELECTRONICS',
            'lot_number': incomplete_lot,
            'quantity': random.randint(40, 80)
        })
        pallet_id += 1
    
    # Scenario 3: Overcapacity locations (multiple pallets in 1-capacity locations)
    print("3. Adding overcapacity scenarios...")
    # Pick 5 specific locations and put 2 pallets each (should trigger overcapacity)
    overcap_locations = ['01-01-001A', '01-02-003B', '02-01-002A', '03-03-004B', '04-02-001A']
    for location in overcap_locations:
        for i in range(2):  # 2 pallets in each 1-capacity location
            inventory_records.append({
                'pallet_id': f'PLT{pallet_id}',
                'location': location,
                'creation_date': (base_time - timedelta(hours=random.randint(1, 6))).strftime('%Y-%m-%d %H:%M:%S'),
                'receipt_number': f'RCP{5000 + len(inventory_records)}',
                'description': random.choice(product_types),
                'lot_number': f'LOT{3000 + len(inventory_records)}',
                'quantity': random.randint(30, 70)
            })
            pallet_id += 1
    
    # Scenario 4: Invalid locations (should trigger Invalid Locations Alert)
    print("4. Adding invalid location tests...")
    invalid_locations = ['INVALID-ZONE', 'MISSING-LOC', 'TYPO-LOCATION']
    for invalid_loc in invalid_locations:
        inventory_records.append({
            'pallet_id': f'PLT{pallet_id}',
            'location': invalid_loc,
            'creation_date': (base_time - timedelta(hours=random.randint(1, 4))).strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': f'RCP{6000 + len(inventory_records)}',
            'description': random.choice(product_types),
            'lot_number': f'LOT{4000 + len(inventory_records)}',
            'quantity': random.randint(20, 60)
        })
        pallet_id += 1
    
    # Scenario 5: Normal stored pallets (distributed across warehouse)
    print("5. Adding normally stored pallets...")
    # Use a realistic subset of storage locations
    used_storage_locations = random.sample(all_storage_locations, min(100, len(all_storage_locations)))
    
    for i in range(80):  # 80 normal pallets distributed across warehouse
        inventory_records.append({
            'pallet_id': f'PLT{pallet_id}',
            'location': random.choice(used_storage_locations),
            'creation_date': (base_time - timedelta(hours=random.randint(24, 168))).strftime('%Y-%m-%d %H:%M:%S'),  # 1-7 days old
            'receipt_number': random.choice(receipt_numbers),
            'description': random.choice(product_types),
            'lot_number': f'LOT{5000 + i}',
            'quantity': random.randint(20, 120)
        })
        pallet_id += 1
    
    # Scenario 6: Some pallets in staging (normal workflow)
    print("6. Adding pallets in staging workflow...")
    for i in range(5):  # 5 pallets in staging (normal)
        inventory_records.append({
            'pallet_id': f'PLT{pallet_id}',
            'location': random.choice(['STG-001', 'STG-002']),
            'creation_date': (base_time - timedelta(hours=random.randint(1, 8))).strftime('%Y-%m-%d %H:%M:%S'),
            'receipt_number': f'RCP{7000 + i}',
            'description': random.choice(product_types),
            'lot_number': f'LOT{6000 + i}',
            'quantity': random.randint(15, 50)
        })
        pallet_id += 1
    
    return inventory_records

def main():
    """Generate the realistic inventory report"""
    print("Creating Realistic Inventory Report for Central Distribution Center")
    print("=" * 70)
    
    # Create inventory data
    inventory_data = create_realistic_inventory()
    
    # Create DataFrame
    inventory_df = pd.DataFrame(inventory_data)
    
    # Save to Excel
    filename = 'CentralDC_Realistic_Inventory.xlsx'
    inventory_df.to_excel(filename, index=False)
    
    print(f"\n✅ Created: {filename}")
    print(f"📊 Total pallets: {len(inventory_df)}")
    
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
        elif any(location.startswith(invalid) for invalid in ['INVALID', 'MISSING', 'TYPO']):
            loc_type = 'INVALID'
        elif '-' in location and len(location.split('-')) >= 3:
            loc_type = 'STORAGE'
        else:
            loc_type = 'OTHER'
        
        location_summary[loc_type] = location_summary.get(loc_type, 0) + 1
    
    print(f"\n📋 Inventory Distribution:")
    for loc_type, count in sorted(location_summary.items()):
        print(f"   {loc_type}: {count} pallets")
    
    print(f"\n🎯 Expected Test Results:")
    print(f"   ✓ Stagnant Pallets: ~12 anomalies (7-36h old in receiving)")
    print(f"   ✓ Incomplete Lots: 1 anomaly (6/8 stored = 75% < 80% threshold)")
    print(f"   ✓ Overcapacity: 10 anomalies (2 pallets each in 5 locations)")
    print(f"   ✓ Invalid Locations: 3 anomalies")
    print(f"   ✓ Normal Operations: ~85 pallets should be fine")
    
    print(f"\n🏗️  Warehouse Structure Used:")
    print(f"   - 4 aisles × 4 racks × 5 positions × 2 levels = 160 storage locations")
    print(f"   - Format: 01-01-001A through 04-04-005B")  
    print(f"   - Special areas: RCV-001/002/003, STG-001/002, DOCK-01/02")
    print(f"   - 1 pallet capacity per location")

if __name__ == '__main__':
    main()