#!/usr/bin/env python3
"""
FakeCorp Distribution Center - Test Inventory Report Generator
Creates realistic inventory data for 928-location warehouse testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_warehouse_locations():
    """Generate all possible warehouse locations based on template"""
    locations = []
    
    # Storage locations: 3 aisles × 2 racks × 50 positions × 3 levels = 900
    for aisle in range(1, 4):  # Aisles 1-3
        for rack in range(1, 3):  # Racks 1-2
            for position in range(1, 51):  # Positions 1-50
                for level in ['A', 'B', 'C']:  # Levels A, B, C
                    location_code = f"{aisle:02d}-{rack:02d}-{position:03d}-{level}"
                    locations.append({
                        'code': location_code,
                        'type': 'STORAGE',
                        'zone': 'GENERAL',
                        'capacity': 1
                    })
    
    # Special areas
    special_areas = [
        {'code': 'RECV-DOCK', 'type': 'RECEIVING', 'zone': 'INBOUND', 'capacity': 15},
        {'code': 'QC-STAGE', 'type': 'STAGING', 'zone': 'QUALITY', 'capacity': 8},
        {'code': 'SHIP-DOCK', 'type': 'DOCK', 'zone': 'SHIPPING', 'capacity': 5}
    ]
    
    locations.extend(special_areas)
    return locations

def generate_automotive_products():
    """Generate realistic automotive product descriptions"""
    categories = ['ENGINE', 'TRANSMISSION', 'BRAKE', 'SUSPENSION', 'ELECTRICAL', 'BODY', 'INTERIOR', 'EXHAUST']
    parts = {
        'ENGINE': ['Oil Filter', 'Air Filter', 'Spark Plugs', 'Gasket Set', 'Timing Belt', 'Water Pump'],
        'TRANSMISSION': ['Clutch Kit', 'CV Joint', 'Gear Oil', 'Flywheel', 'Torque Converter'],
        'BRAKE': ['Brake Pads', 'Brake Discs', 'Brake Fluid', 'Brake Lines', 'Caliper'],
        'SUSPENSION': ['Shock Absorber', 'Spring Coil', 'Strut Mount', 'Ball Joint', 'Control Arm'],
        'ELECTRICAL': ['Battery', 'Alternator', 'Starter Motor', 'Wiring Harness', 'ECU'],
        'BODY': ['Bumper', 'Headlight', 'Mirror', 'Door Handle', 'Fender'],
        'INTERIOR': ['Seat Cover', 'Dashboard', 'Floor Mat', 'Steering Wheel', 'Console'],
        'EXHAUST': ['Muffler', 'Catalytic Converter', 'Exhaust Pipe', 'Silencer', 'Manifold']
    }
    
    products = []
    for category in categories:
        for part in parts[category]:
            for brand in ['OEM', 'Bosch', 'Denso', 'Continental', 'Valeo']:
                products.append(f"{brand} {part} - {category}")
    
    return products

def create_comprehensive_inventory():
    """Create comprehensive test inventory with various scenarios"""
    
    locations = generate_warehouse_locations()
    products = generate_automotive_products()
    
    inventory_data = []
    pallet_counter = 1
    
    # === SCENARIO 1: STAGNANT PALLETS (Test for old pallets in receiving) ===
    print("Creating stagnant pallets scenario...")
    for i in range(12):  # 12 stagnant pallets
        hours_old = random.randint(8, 72)  # 8-72 hours old
        inventory_data.append({
            'Pallet ID': f'STAG{pallet_counter:04d}',
            'Location': 'RECV-DOCK',
            'Receipt Number': f'REC{i//3:03d}',  # Group in lots of 3
            'Description': random.choice(products),
            'Creation Date': (datetime.now() - timedelta(hours=hours_old)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': random.randint(20, 50),
            'Weight': random.randint(500, 1500)
        })
        pallet_counter += 1
    
    # === SCENARIO 2: OVERCAPACITY VIOLATIONS (Multiple pallets in same location) ===
    print("Creating overcapacity violations...")
    overcapacity_locations = ['01-01-001-A', '01-01-015-B', '02-01-030-C', '03-02-025-A']
    for location in overcapacity_locations:
        pallets_in_location = random.randint(2, 4)  # 2-4 pallets (capacity is 1)
        for i in range(pallets_in_location):
            inventory_data.append({
                'Pallet ID': f'OVER{pallet_counter:04d}',
                'Location': location,
                'Receipt Number': f'OVER{len(inventory_data)//10:03d}',
                'Description': random.choice(products),
                'Creation Date': (datetime.now() - timedelta(hours=random.randint(1, 6))).strftime('%Y-%m-%d %H:%M:%S'),
                'Quantity': random.randint(15, 35),
                'Weight': random.randint(400, 1200)
            })
            pallet_counter += 1
    
    # === SCENARIO 3: LOT STRAGGLERS (Most pallets stored, some still in receiving) ===
    print("Creating lot straggler scenarios...")
    for lot_num in range(3):  # 3 different lots
        lot_id = f'LOT{lot_num:03d}'
        lot_size = random.randint(8, 15)
        stragglers = random.randint(2, 4)
        
        # Stored pallets (majority)
        stored_count = lot_size - stragglers
        for i in range(stored_count):
            # Find available storage location
            storage_locations = [loc['code'] for loc in locations if loc['type'] == 'STORAGE']
            location = random.choice(storage_locations)
            
            inventory_data.append({
                'Pallet ID': f'LOT{lot_num}{i:02d}',
                'Location': location,
                'Receipt Number': lot_id,
                'Description': random.choice(products),
                'Creation Date': (datetime.now() - timedelta(hours=random.randint(4, 12))).strftime('%Y-%m-%d %H:%M:%S'),
                'Quantity': random.randint(25, 45),
                'Weight': random.randint(600, 1400)
            })
            pallet_counter += 1
        
        # Straggler pallets (still in receiving)
        for i in range(stragglers):
            inventory_data.append({
                'Pallet ID': f'STR{lot_num}{i:02d}',
                'Location': 'RECV-DOCK',
                'Receipt Number': lot_id,
                'Description': random.choice(products),
                'Creation Date': (datetime.now() - timedelta(hours=random.randint(4, 12))).strftime('%Y-%m-%d %H:%M:%S'),
                'Quantity': random.randint(25, 45),
                'Weight': random.randint(600, 1400)
            })
            pallet_counter += 1
    
    # === SCENARIO 4: TEMPERATURE VIOLATIONS (Frozen/Cold products in wrong zones) ===
    print("Creating temperature violation scenarios...")
    temp_sensitive_products = [
        'FROZEN Rubber Seals - BODY',
        'COLD Electronic Components - ELECTRICAL', 
        'REFRIGERATED Battery Cells - ELECTRICAL',
        'FROZEN Adhesive Compounds - BODY'
    ]
    
    for i in range(8):  # 8 temperature violations
        storage_locations = [loc['code'] for loc in locations if loc['type'] == 'STORAGE']
        location = random.choice(storage_locations)  # Should be in cold zone, but in general
        
        inventory_data.append({
            'Pallet ID': f'TEMP{pallet_counter:04d}',
            'Location': location,
            'Receipt Number': f'TEMP{i//2:03d}',
            'Description': random.choice(temp_sensitive_products),
            'Creation Date': (datetime.now() - timedelta(hours=random.randint(1, 8))).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': random.randint(10, 30),
            'Weight': random.randint(300, 800)
        })
        pallet_counter += 1
    
    # === SCENARIO 5: INVALID/MISSING LOCATIONS ===
    print("Creating location error scenarios...")
    
    # Missing locations
    for i in range(5):
        inventory_data.append({
            'Pallet ID': f'MISS{pallet_counter:04d}',
            'Location': '',  # Empty location
            'Receipt Number': f'MISS{i:03d}',
            'Description': random.choice(products),
            'Creation Date': (datetime.now() - timedelta(hours=random.randint(1, 4))).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': random.randint(20, 40),
            'Weight': random.randint(500, 1000)
        })
        pallet_counter += 1
    
    # Invalid locations
    invalid_locations = ['99-99-999-Z', 'INVALID-LOC', 'OLD-SYSTEM-A1', 'DELETED-RACK-B']
    for i, invalid_loc in enumerate(invalid_locations):
        inventory_data.append({
            'Pallet ID': f'INVL{pallet_counter:04d}',
            'Location': invalid_loc,
            'Receipt Number': f'INVL{i:03d}',
            'Description': random.choice(products),
            'Creation Date': (datetime.now() - timedelta(hours=random.randint(1, 6))).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': random.randint(15, 35),
            'Weight': random.randint(400, 900)
        })
        pallet_counter += 1
    
    # === NORMAL INVENTORY (Baseline data) ===
    print("Creating normal baseline inventory...")
    
    # Fill storage locations with normal inventory (about 60% capacity)
    storage_locations = [loc['code'] for loc in locations if loc['type'] == 'STORAGE']
    num_normal_pallets = int(len(storage_locations) * 0.6)  # 60% of storage filled
    
    used_locations = set()
    for i in range(num_normal_pallets):
        # Pick unused location
        available_locations = [loc for loc in storage_locations if loc not in used_locations]
        if not available_locations:
            break
            
        location = random.choice(available_locations)
        used_locations.add(location)
        
        inventory_data.append({
            'Pallet ID': f'NORM{pallet_counter:04d}',
            'Location': location,
            'Receipt Number': f'NORM{i//8:03d}',  # Group in lots of 8
            'Description': random.choice(products),
            'Creation Date': (datetime.now() - timedelta(hours=random.randint(1, 48))).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': random.randint(20, 50),
            'Weight': random.randint(500, 1500)
        })
        pallet_counter += 1
    
    # Some pallets in staging and shipping
    for area_code in ['QC-STAGE', 'SHIP-DOCK']:
        for i in range(random.randint(2, 4)):
            inventory_data.append({
                'Pallet ID': f'SPEC{pallet_counter:04d}',
                'Location': area_code,
                'Receipt Number': f'SPEC{i:03d}',
                'Description': random.choice(products),
                'Creation Date': (datetime.now() - timedelta(hours=random.randint(1, 12))).strftime('%Y-%m-%d %H:%M:%S'),
                'Quantity': random.randint(25, 45),
                'Weight': random.randint(600, 1300)
            })
            pallet_counter += 1
    
    return inventory_data

def main():
    """Generate and save the inventory report"""
    print("FakeCorp Distribution Center - Inventory Report Generator")
    print("=" * 60)
    
    print("Generating comprehensive test inventory...")
    inventory_data = create_comprehensive_inventory()
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Save to Excel file
    output_file = 'FakeCorp_Warehouse_Inventory_Report.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\nInventory report generated successfully!")
    print(f"File: {output_file}")
    print(f"Total pallets: {len(inventory_data)}")
    
    # Summary of test scenarios
    print(f"\nTest Scenarios Included:")
    print(f"   - Stagnant Pallets: ~12 (old pallets in receiving)")
    print(f"   - Overcapacity: ~12 (multiple pallets per location)")  
    print(f"   - Lot Stragglers: ~9 (incomplete lot putaway)")
    print(f"   - Temperature Violations: 8 (frozen/cold in wrong zones)")
    print(f"   - Missing Locations: 5 (empty location field)")
    print(f"   - Invalid Locations: 4 (non-existent location codes)")
    print(f"   - Normal Inventory: ~{len(inventory_data) - 50} (baseline)")
    
    print(f"\nExpected Columns:")
    print(f"   * Pallet ID")
    print(f"   * Location") 
    print(f"   * Receipt Number")
    print(f"   * Description")
    print(f"   * Creation Date")
    print(f"   * Quantity")
    print(f"   * Weight")
    
    print(f"\nReady for testing with default rules!")
    print(f"   Upload {output_file} to your WareWise dashboard")

if __name__ == "__main__":
    main()