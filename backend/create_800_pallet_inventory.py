#!/usr/bin/env python3
"""
Comprehensive 800-Pallet Test Inventory Generator
Creates exactly 800 pallets with strategic anomalies to test all system rules
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_pallet_id():
    """Generate realistic pallet IDs"""
    return f"PL{random.randint(100000, 999999)}"

def generate_location_code(aisle, rack, position, level):
    """Generate location code in format: 01-02-001A"""
    return f"{aisle:02d}-{rack:02d}-{position:03d}{level}"

def generate_lot_number():
    """Generate realistic lot numbers"""
    prefix = random.choice(['LOT', 'LT', 'BATCH'])
    return f"{prefix}{random.randint(10000, 99999)}"

def generate_product_description():
    """Generate realistic product descriptions"""
    products = [
        "Industrial Steel Components", "Automotive Parts", "Electronic Components",
        "Pharmaceutical Supplies", "Consumer Electronics", "Textile Products",
        "Building Materials", "Chemical Supplies", "Food Products",
        "Machinery Parts", "Office Supplies", "Medical Equipment",
        "Cleaning Supplies", "Paper Products", "Plastic Components",
        "Metal Hardware", "Glass Materials", "Rubber Products",
        "Packaging Materials", "Industrial Tools"
    ]
    return random.choice(products)

def main():
    """Generate comprehensive 800-pallet test inventory"""
    print("Creating comprehensive 800-pallet inventory...")
    
    # Create valid storage locations (4 aisles × 2 racks × 29 positions × 4 levels = 928 locations)
    valid_storage_locations = []
    level_names = ['A', 'B', 'C', 'D']
    for aisle in range(1, 5):
        for rack in range(1, 3):
            for position in range(1, 30):
                for level in level_names:
                    valid_storage_locations.append(generate_location_code(aisle, rack, position, level))

    special_locations = ['RECV-01', 'RECV-02', 'STAGE-01', 'DOCK-01', 'AISLE-01', 'AISLE-02', 'AISLE-03', 'AISLE-04']
    current_time = datetime.now()
    inventory_data = []

    # Generate base valid inventory (720 pallets = 90%)
    print("Generating 720 valid base pallets...")
    for i in range(720):
        pallet_id = generate_pallet_id()
        
        # 85% in storage locations, 15% in special areas (not stagnant)
        if i < 612:  # 85% in storage
            location = random.choice(valid_storage_locations)
            zone = 'GENERAL'
        else:  # 15% in special areas
            location = random.choice(['STAGE-01', 'DOCK-01'])
            zone = 'STAGING' if 'STAGE' in location else 'DOCK'
        
        # Recent timestamps to avoid stagnation
        received_time = current_time - timedelta(hours=random.uniform(0.5, 8))
        
        inventory_data.append({
            'pallet_id': pallet_id,
            'location': location,
            'lot_number': generate_lot_number(),
            'description': generate_product_description(),
            'quantity': random.randint(1, 4),
            'received_date': received_time.strftime('%Y-%m-%d'),
            'received_time': received_time.strftime('%H:%M:%S'),
            'last_updated': received_time.strftime('%Y-%m-%d %H:%M:%S'),
            'zone': zone,
            'status': 'ACTIVE',
            'warehouse_id': 'DEFAULT',
            'created_by': 'SYSTEM_TEST',
            'weight_kg': round(random.uniform(50, 500), 2),
            'dimensions': f"{random.randint(100,200)}x{random.randint(100,200)}x{random.randint(100,300)}"
        })

    print("Injecting strategic anomalies...")
    anomaly_counts = {}

    # 1. STAGNANT_PALLETS (8 violations - >10 hours in RECEIVING)
    for i in range(8):
        stagnant_time = current_time - timedelta(hours=random.uniform(12, 48))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': random.choice(['RECV-01', 'RECV-02']),
            'lot_number': f"STAGNANT-{generate_lot_number()}",
            'description': generate_product_description(),
            'quantity': random.randint(1, 4),
            'received_date': stagnant_time.strftime('%Y-%m-%d'),
            'received_time': stagnant_time.strftime('%H:%M:%S'),
            'last_updated': stagnant_time.strftime('%Y-%m-%d %H:%M:%S'),
            'zone': 'RECEIVING',
            'status': 'ACTIVE',
            'warehouse_id': 'DEFAULT',
            'created_by': 'SYSTEM_TEST',
            'weight_kg': round(random.uniform(50, 500), 2),
            'dimensions': f"{random.randint(100,200)}x{random.randint(100,200)}x{random.randint(100,300)}"
        })
    anomaly_counts['STAGNANT_PALLETS'] = 8

    # 2. UNCOORDINATED_LOTS (6 violations - incomplete lots)
    shared_lot = f"INCOMPLETE-{generate_lot_number()}"
    for i in range(6):
        old_time = current_time - timedelta(hours=random.uniform(5, 15))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': random.choice(['RECV-01', 'RECV-02']),
            'lot_number': shared_lot,  # Same lot number for testing
            'description': generate_product_description(),
            'quantity': random.randint(1, 4),
            'received_date': old_time.strftime('%Y-%m-%d'),
            'received_time': old_time.strftime('%H:%M:%S'),
            'last_updated': old_time.strftime('%Y-%m-%d %H:%M:%S'),
            'zone': 'RECEIVING',
            'status': 'ACTIVE',
            'warehouse_id': 'DEFAULT',
            'created_by': 'SYSTEM_TEST',
            'weight_kg': round(random.uniform(50, 500), 2),
            'dimensions': f"{random.randint(100,200)}x{random.randint(100,200)}x{random.randint(100,300)}"
        })

    # Add some completed pallets from same lot in storage
    for i in range(15):  # Make lot 21 pallets total (6 incomplete + 15 completed = >80% completion)
        completed_time = current_time - timedelta(hours=random.uniform(16, 30))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': random.choice(valid_storage_locations[:50]),  # Use some storage locations
            'lot_number': shared_lot,
            'description': generate_product_description(),
            'quantity': random.randint(1, 4),
            'received_date': completed_time.strftime('%Y-%m-%d'),
            'received_time': completed_time.strftime('%H:%M:%S'),
            'last_updated': (completed_time + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),  # Later move time
            'zone': 'GENERAL',
            'status': 'ACTIVE',
            'warehouse_id': 'DEFAULT',
            'created_by': 'SYSTEM_TEST',
            'weight_kg': round(random.uniform(50, 500), 2),
            'dimensions': f"{random.randint(100,200)}x{random.randint(100,200)}x{random.randint(100,300)}"
        })
    anomaly_counts['UNCOORDINATED_LOTS'] = 6

    # 3. OVERCAPACITY (Create multiple pallets in same locations to exceed capacity)
    overcapacity_data = [
        ('RECV-01', 12),  # Exceed capacity of 10
        ('RECV-02', 11),  # Exceed capacity of 10  
        ('STAGE-01', 7),  # Exceed capacity of 5
        ('DOCK-01', 4),   # Exceed capacity of 2
        ('01-01-001A', 2), # Storage location (capacity 1)
        ('01-01-002B', 2), # Storage location (capacity 1)
        ('02-02-005C', 3), # Storage location (capacity 1)
    ]

    total_overcap = 0
    for location, pallet_count in overcapacity_data:
        for i in range(pallet_count):
            recent_time = current_time - timedelta(hours=random.uniform(1, 6))
            inventory_data.append({
                'pallet_id': generate_pallet_id(),
                'location': location,
                'lot_number': f"OVERCAP-{generate_lot_number()}",
                'description': generate_product_description(),
                'quantity': 1,
                'received_date': recent_time.strftime('%Y-%m-%d'),
                'received_time': recent_time.strftime('%H:%M:%S'),
                'last_updated': recent_time.strftime('%Y-%m-%d %H:%M:%S'),
                'zone': 'RECEIVING' if 'RECV' in location else 
                       'STAGING' if 'STAGE' in location else 
                       'DOCK' if 'DOCK' in location else 'GENERAL',
                'status': 'ACTIVE',
                'warehouse_id': 'DEFAULT',
                'created_by': 'SYSTEM_TEST',
                'weight_kg': round(random.uniform(50, 500), 2),
                'dimensions': f"{random.randint(100,200)}x{random.randint(100,200)}x{random.randint(100,300)}"
            })
            total_overcap += 1
    anomaly_counts['OVERCAPACITY'] = total_overcap

    # 4. INVALID_LOCATION (8 violations - undefined locations)
    invalid_locations = [
        'INVALID-LOC-001', 'RECV-99', 'AISLE-99', '99-99-999Z',
        'DOCK-99', 'STAGE-99', 'UNKNOWN-AREA-X1', '05-01-001A'  # Aisle 5 doesn't exist
    ]

    for location in invalid_locations:
        recent_time = current_time - timedelta(hours=random.uniform(1, 5))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': location,
            'lot_number': f"INVALID-{generate_lot_number()}",
            'description': generate_product_description(),
            'quantity': random.randint(1, 4),
            'received_date': recent_time.strftime('%Y-%m-%d'),
            'received_time': recent_time.strftime('%H:%M:%S'),
            'last_updated': recent_time.strftime('%Y-%m-%d %H:%M:%S'),
            'zone': 'UNKNOWN',
            'status': 'ACTIVE',
            'warehouse_id': 'DEFAULT',
            'created_by': 'SYSTEM_TEST',
            'weight_kg': round(random.uniform(50, 500), 2),
            'dimensions': f"{random.randint(100,200)}x{random.randint(100,200)}x{random.randint(100,300)}"
        })
    anomaly_counts['INVALID_LOCATION'] = len(invalid_locations)

    # 5. LOCATION_SPECIFIC_STAGNANT (7 violations - >4 hours in AISLE locations)
    aisle_locations = ['AISLE-01', 'AISLE-02', 'AISLE-03', 'AISLE-04']
    for i in range(7):
        stuck_time = current_time - timedelta(hours=random.uniform(5, 24))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': random.choice(aisle_locations),
            'lot_number': f"STUCK-{generate_lot_number()}",
            'description': generate_product_description(),
            'quantity': random.randint(1, 4),
            'received_date': stuck_time.strftime('%Y-%m-%d'),
            'received_time': stuck_time.strftime('%H:%M:%S'),
            'last_updated': stuck_time.strftime('%Y-%m-%d %H:%M:%S'),
            'zone': 'GENERAL',
            'status': 'ACTIVE',
            'warehouse_id': 'DEFAULT',
            'created_by': 'SYSTEM_TEST',
            'weight_kg': round(random.uniform(50, 500), 2),
            'dimensions': f"{random.randint(100,200)}x{random.randint(100,200)}x{random.randint(100,300)}"
        })
    anomaly_counts['LOCATION_SPECIFIC_STAGNANT'] = 7

    # 6. DATA_INTEGRITY (6 violations - scanning errors)
    data_issues = [
        {'location': 'A1-B2-C3D', 'issue': 'malformed_location'},
        {'location': '00-00-000X', 'issue': 'zero_coordinates'},
        {'location': 'ABC-DEF-GHI', 'issue': 'non_numeric_coordinates'},
        {'location': '1-2-3', 'issue': 'incomplete_format'},
        {'location': '01-01-001A', 'issue': 'duplicate_scan_1', 'pallet_id': 'DUP123456'},
        {'location': '02-02-002B', 'issue': 'duplicate_scan_2', 'pallet_id': 'DUP123456'},
    ]

    for issue_data in data_issues:
        pallet_id = issue_data.get('pallet_id', generate_pallet_id())
        recent_time = current_time - timedelta(minutes=random.uniform(30, 180))
        inventory_data.append({
            'pallet_id': pallet_id,
            'location': issue_data['location'],
            'lot_number': f"DATA-ERR-{generate_lot_number()}",
            'description': generate_product_description(),
            'quantity': random.randint(1, 4),
            'received_date': recent_time.strftime('%Y-%m-%d'),
            'received_time': recent_time.strftime('%H:%M:%S'),
            'last_updated': recent_time.strftime('%Y-%m-%d %H:%M:%S'),
            'zone': 'GENERAL',
            'status': 'ACTIVE',
            'warehouse_id': 'DEFAULT',
            'created_by': 'SYSTEM_TEST',
            'weight_kg': round(random.uniform(50, 500), 2),
            'dimensions': f"{random.randint(100,200)}x{random.randint(100,200)}x{random.randint(100,300)}"
        })
    anomaly_counts['DATA_INTEGRITY'] = len(data_issues)

    # 7. LOCATION_MAPPING_ERROR (6 violations - type inconsistencies)
    mapping_errors = [
        {'location': 'RECV-01', 'wrong_zone': 'STORAGE'},
        {'location': 'STAGE-01', 'wrong_zone': 'DOCK'},
        {'location': 'DOCK-01', 'wrong_zone': 'RECEIVING'},
        {'location': '01-01-001A', 'wrong_zone': 'RECEIVING'},
        {'location': '02-02-002B', 'wrong_zone': 'STAGING'},
        {'location': 'AISLE-01', 'wrong_zone': 'STORAGE'},
    ]

    for error_data in mapping_errors:
        recent_time = current_time - timedelta(hours=random.uniform(2, 8))
        inventory_data.append({
            'pallet_id': generate_pallet_id(),
            'location': error_data['location'],
            'lot_number': f"MAP-ERR-{generate_lot_number()}",
            'description': generate_product_description(),
            'quantity': random.randint(1, 4),
            'received_date': recent_time.strftime('%Y-%m-%d'),
            'received_time': recent_time.strftime('%H:%M:%S'),
            'last_updated': recent_time.strftime('%Y-%m-%d %H:%M:%S'),
            'zone': error_data['wrong_zone'],  # Wrong zone for this location type
            'status': 'ACTIVE',
            'warehouse_id': 'DEFAULT',
            'created_by': 'SYSTEM_TEST',
            'weight_kg': round(random.uniform(50, 500), 2),
            'dimensions': f"{random.randint(100,200)}x{random.randint(100,200)}x{random.randint(100,300)}"
        })
    anomaly_counts['LOCATION_MAPPING_ERROR'] = len(mapping_errors)
    anomaly_counts['TEMPERATURE_ZONE_MISMATCH'] = 0  # Excluded per requirements

    # Ensure exactly 800 records
    current_count = len(inventory_data)
    if current_count > 800:
        inventory_data = inventory_data[:800]
    elif current_count < 800:
        # Add more valid pallets to reach 800
        additional_needed = 800 - current_count
        for i in range(additional_needed):
            recent_time = current_time - timedelta(hours=random.uniform(0.5, 8))
            inventory_data.append({
                'pallet_id': generate_pallet_id(),
                'location': random.choice(valid_storage_locations),
                'lot_number': generate_lot_number(),
                'description': generate_product_description(),
                'quantity': random.randint(1, 4),
                'received_date': recent_time.strftime('%Y-%m-%d'),
                'received_time': recent_time.strftime('%H:%M:%S'),
                'last_updated': recent_time.strftime('%Y-%m-%d %H:%M:%S'),
                'zone': 'GENERAL',
                'status': 'ACTIVE',
                'warehouse_id': 'DEFAULT',
                'created_by': 'SYSTEM_TEST',
                'weight_kg': round(random.uniform(50, 500), 2),
                'dimensions': f"{random.randint(100,200)}x{random.randint(100,200)}x{random.randint(100,300)}"
            })

    # Shuffle and create DataFrame
    random.shuffle(inventory_data)
    df = pd.DataFrame(inventory_data)

    # Reorder columns for better presentation
    column_order = ['pallet_id', 'location', 'lot_number', 'description', 'quantity', 
                   'received_date', 'received_time', 'last_updated', 'zone', 'status',
                   'warehouse_id', 'weight_kg', 'dimensions', 'created_by']
    df = df[column_order]

    # Export to Excel
    output_file = 'inventoryreport.xlsx'
    df.to_excel(output_file, index=False, engine='openpyxl')

    total_anomalies = sum(anomaly_counts.values())
    
    print(f"\n{'='*60}")
    print(f"COMPREHENSIVE TEST INVENTORY GENERATED")
    print(f"{'='*60}")
    print(f"Total pallets: {len(df)}")
    print(f"Valid pallets: ~{720} (~90%)")
    print(f"Anomalous pallets: ~{total_anomalies} (~{total_anomalies/8:.1f}%)")
    print(f"Output file: {output_file}")
    
    print(f"\n{'='*40}")
    print("ANOMALY BREAKDOWN BY RULE TYPE:")
    print(f"{'='*40}")
    for i, (rule_type, count) in enumerate(anomaly_counts.items(), 1):
        print(f"{i}. {rule_type}: {count} violations")
    
    print(f"\nTotal anomalies injected: {total_anomalies}")
    print(f"{'='*60}")
    
    return df, total_anomalies, anomaly_counts

if __name__ == "__main__":
    df, total_anomalies, anomaly_breakdown = main()