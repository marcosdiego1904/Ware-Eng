import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

# Create comprehensive test data with HIGH warehouse utilization
# Target: ~200-250 pallets (60-70% capacity utilization)
now = datetime.now()

# Storage location generator for actual warehouse structure
def generate_storage_locations():
    locations = []
    for aisle in range(1, 3):  # 2 aisles (01, 02)
        for rack in range(1, 2):  # 1 rack (01)
            for position in range(1, 26):  # 25 positions (001-025)
                for level in ['A', 'B', 'C']:  # 3 levels
                    location = f"{aisle:02d}-{rack:01d}-{position:03d}{level}"
                    locations.append(location)
    return locations

storage_locations = generate_storage_locations()
print(f"Generated {len(storage_locations)} storage locations")

# Generate comprehensive normal operations pallets
def generate_normal_pallets():
    pallets = []
    receipt_counter = 1
    pallet_counter = 1
    
    # Product categories for variety
    product_types = [
        'Electronics Components', 'Automotive Parts', 'Household Items', 'Industrial Supplies',
        'Office Equipment', 'Construction Materials', 'Textiles', 'Paper Products',
        'Chemical Supplies', 'Food Products', 'Medical Supplies', 'Sports Equipment',
        'Garden Supplies', 'Cleaning Products', 'Hardware', 'Packaging Materials'
    ]
    
    # Fill storage locations with normal operations (130 pallets in storage)
    used_locations = set()
    for i in range(130):
        # Select random storage location
        location = random.choice([loc for loc in storage_locations if loc not in used_locations])
        used_locations.add(location)
        
        # Random time in past 1-10 days for realistic variety
        hours_ago = random.randint(1, 240)  # 1-10 days
        product = random.choice(product_types)
        
        pallets.append([
            f'PLT-NORM-{pallet_counter:03d}',
            location,
            now - timedelta(hours=hours_ago),
            f'RCT-NORM-{receipt_counter:03d}',
            f'{product} Item {pallet_counter}'
        ])
        
        pallet_counter += 1
        if pallet_counter % 5 == 0:  # New receipt every 5 pallets
            receipt_counter += 1
    
    # Add pallets in special areas (normal operations)
    special_areas = [
        ('RECV-01', 3, 'Recent arrivals'),  # 3 pallets in RECV-01
        ('RECV-02', 2, 'Recent arrivals'),  # 2 pallets in RECV-02
        ('STAGE-01', 4, 'Outbound staging'), # 4 pallets in STAGE-01
        ('DOCK-01', 1, 'Loading'),          # 1 pallet in DOCK-01
        ('AISLE-01', 2, 'In transit'),      # 2 pallets in AISLE-01
        ('AISLE-02', 3, 'In transit'),      # 3 pallets in AISLE-02
    ]
    
    for location, count, description in special_areas:
        for i in range(count):
            pallets.append([
                f'PLT-SPEC-{pallet_counter:03d}',
                location,
                now - timedelta(hours=random.randint(1, 8)),  # Recent activity
                f'RCT-SPEC-{receipt_counter:03d}',
                f'{description} Product {i+1}'
            ])
            pallet_counter += 1
            if i == 0:  # New receipt for each special area
                receipt_counter += 1
    
    return pallets

# Generate normal operations pallets
normal_pallets = generate_normal_pallets()

# RULE 1: STAGNANT_PALLETS (>10 hours in RECEIVING) - 5 anomalies
stagnant_pallets = [
    ['PLT-STAGNANT-001', 'RECV-01', now - timedelta(hours=12), 'RCT-STAGNANT-001', 'Stagnant Product 1'],
    ['PLT-STAGNANT-002', 'RECV-01', now - timedelta(hours=15), 'RCT-STAGNANT-002', 'Stagnant Product 2'],
    ['PLT-STAGNANT-003', 'RECV-02', now - timedelta(hours=18), 'RCT-STAGNANT-003', 'Stagnant Product 3'],
    ['PLT-STAGNANT-004', 'RECV-02', now - timedelta(hours=20), 'RCT-STAGNANT-004', 'Stagnant Product 4'],
    ['PLT-STAGNANT-005', 'RECV-01', now - timedelta(hours=14), 'RCT-STAGNANT-005', 'Stagnant Product 5'],
]

# RULE 2: UNCOORDINATED_LOTS (90% in storage, 10% straggler) - 1 anomaly
lot_pallets = [
    ['PLT-LOT-001-01', '01-01-024A', now - timedelta(hours=8), 'LOT-SPECIAL-001', 'Coordinated Lot Product 1'],
    ['PLT-LOT-001-02', '01-01-024B', now - timedelta(hours=8), 'LOT-SPECIAL-001', 'Coordinated Lot Product 2'],
    ['PLT-LOT-001-03', '01-01-024C', now - timedelta(hours=8), 'LOT-SPECIAL-001', 'Coordinated Lot Product 3'],
    ['PLT-LOT-001-04', '02-01-024A', now - timedelta(hours=8), 'LOT-SPECIAL-001', 'Coordinated Lot Product 4'],
    ['PLT-LOT-001-05', '02-01-024B', now - timedelta(hours=8), 'LOT-SPECIAL-001', 'Coordinated Lot Product 5'],
    ['PLT-LOT-001-06', '02-01-024C', now - timedelta(hours=8), 'LOT-SPECIAL-001', 'Coordinated Lot Product 6'],
    ['PLT-LOT-001-07', '01-01-023A', now - timedelta(hours=8), 'LOT-SPECIAL-001', 'Coordinated Lot Product 7'],
    ['PLT-LOT-001-08', '01-01-023B', now - timedelta(hours=8), 'LOT-SPECIAL-001', 'Coordinated Lot Product 8'],
    ['PLT-LOT-001-09', '01-01-023C', now - timedelta(hours=8), 'LOT-SPECIAL-001', 'Coordinated Lot Product 9'],
    ['PLT-LOT-001-STRAGGLER', 'RECV-01', now - timedelta(hours=8), 'LOT-SPECIAL-001', 'Coordinated Lot Product STRAGGLER'],  # ANOMALY
]

# RULE 3: OVERCAPACITY - 2 anomalies
overcap_pallets = [
    # RECV-01 overcapacity (capacity 10, we'll have 12+ total with normal operations)
    ['PLT-OVERCAP-01', 'RECV-01', now - timedelta(hours=1), 'RCT-OVERCAP-001', 'Overcapacity Test 1'],
    ['PLT-OVERCAP-02', 'RECV-01', now - timedelta(hours=1, minutes=5), 'RCT-OVERCAP-002', 'Overcapacity Test 2'],
    ['PLT-OVERCAP-03', 'RECV-01', now - timedelta(hours=1, minutes=10), 'RCT-OVERCAP-003', 'Overcapacity Test 3'],
    ['PLT-OVERCAP-04', 'RECV-01', now - timedelta(hours=1, minutes=15), 'RCT-OVERCAP-004', 'Overcapacity Test 4'],
    ['PLT-OVERCAP-05', 'RECV-01', now - timedelta(hours=1, minutes=20), 'RCT-OVERCAP-005', 'Overcapacity Test 5'],
    ['PLT-OVERCAP-06', 'RECV-01', now - timedelta(hours=1, minutes=25), 'RCT-OVERCAP-006', 'Overcapacity Test 6'],
    ['PLT-OVERCAP-07', 'RECV-01', now - timedelta(hours=1, minutes=30), 'RCT-OVERCAP-007', 'Overcapacity Test 7'],
    ['PLT-OVERCAP-08', 'RECV-01', now - timedelta(hours=1, minutes=35), 'RCT-OVERCAP-008', 'Overcapacity Test 8'],
    
    # Storage position overcapacity (capacity 2, adding 4 pallets to same position)
    ['PLT-OVERCAP-STORAGE-01', '02-01-023A', now - timedelta(hours=1), 'RCT-OVERCAP-STORAGE-01', 'Storage Overcap 1'],
    ['PLT-OVERCAP-STORAGE-02', '02-01-023A', now - timedelta(hours=1, minutes=5), 'RCT-OVERCAP-STORAGE-02', 'Storage Overcap 2'],
    ['PLT-OVERCAP-STORAGE-03', '02-01-023A', now - timedelta(hours=1, minutes=10), 'RCT-OVERCAP-STORAGE-03', 'Storage Overcap 3'],
    ['PLT-OVERCAP-STORAGE-04', '02-01-023A', now - timedelta(hours=1, minutes=15), 'RCT-OVERCAP-STORAGE-04', 'Storage Overcap 4'],
]

# RULE 4: INVALID_LOCATION - 3 anomalies
invalid_pallets = [
    ['PLT-INVALID-001', 'BADLOC-01', now - timedelta(hours=3), 'RCT-INVALID-001', 'Invalid Location Test 1'],
    ['PLT-INVALID-002', 'UNKNOWN-99', now - timedelta(hours=3, minutes=5), 'RCT-INVALID-002', 'Invalid Location Test 2'],
    ['PLT-INVALID-003', 'FAKE-AREA', now - timedelta(hours=3, minutes=10), 'RCT-INVALID-003', 'Invalid Location Test 3'],
]

# RULE 5: LOCATION_SPECIFIC_STAGNANT (AISLE >4 hours) - 4 anomalies
aisle_stuck_pallets = [
    ['PLT-AISLE-STUCK-01', 'AISLE-01', now - timedelta(hours=6), 'RCT-AISLE-STUCK-01', 'Aisle Stuck Product 1'],
    ['PLT-AISLE-STUCK-02', 'AISLE-01', now - timedelta(hours=8), 'RCT-AISLE-STUCK-02', 'Aisle Stuck Product 2'],
    ['PLT-AISLE-STUCK-03', 'AISLE-02', now - timedelta(hours=7), 'RCT-AISLE-STUCK-03', 'Aisle Stuck Product 3'],
    ['PLT-AISLE-STUCK-04', 'AISLE-02', now - timedelta(hours=9), 'RCT-AISLE-STUCK-04', 'Aisle Stuck Product 4'],
]

# RULE 6: TEMPERATURE_ZONE_MISMATCH - 3 anomalies
temp_violation_pallets = [
    ['PLT-TEMP-VIOLATION-01', '01-01-022A', now - timedelta(hours=4), 'RCT-TEMP-VIOLATION-01', 'FROZEN VEGETABLES'],
    ['PLT-TEMP-VIOLATION-02', '02-01-022A', now - timedelta(hours=4, minutes=5), 'RCT-TEMP-VIOLATION-02', 'FROZEN MEAT PRODUCTS'],
    ['PLT-TEMP-VIOLATION-03', '01-01-021A', now - timedelta(hours=4, minutes=10), 'RCT-TEMP-VIOLATION-03', 'REFRIGERATED DAIRY'],
]

# RULE 7: DATA_INTEGRITY (Duplicate pallet IDs) - 4 anomalies
duplicate_pallets = [
    ['DUP-001', '01-01-020A', now - timedelta(hours=5), 'RCT-DUP-001', 'Duplicate Pallet Test 1'],
    ['DUP-001', '02-01-020A', now - timedelta(hours=5, minutes=5), 'RCT-DUP-001-COPY', 'Duplicate Pallet Test 1 Copy'],
    ['DUP-002', '01-01-019A', now - timedelta(hours=5, minutes=10), 'RCT-DUP-002', 'Duplicate Pallet Test 2'],
    ['DUP-002', '02-01-019A', now - timedelta(hours=5, minutes=15), 'RCT-DUP-002-COPY', 'Duplicate Pallet Test 2 Copy'],
]

# RULE 8: LOCATION_MAPPING_ERROR - 2 anomalies
mapping_error_pallets = [
    ['PLT-MAPPING-ERROR-01', 'RECV-02', now - timedelta(hours=6), 'RCT-MAPPING-ERROR-01', 'Location Mapping Error 1'],
    ['PLT-MAPPING-ERROR-02', 'STAGE-01', now - timedelta(hours=6, minutes=5), 'RCT-MAPPING-ERROR-02', 'Location Mapping Error 2'],
]

# Combine all data
all_data = (normal_pallets + stagnant_pallets + lot_pallets + overcap_pallets + 
           invalid_pallets + aisle_stuck_pallets + temp_violation_pallets + 
           duplicate_pallets + mapping_error_pallets)

# Create DataFrame
df = pd.DataFrame(all_data, columns=['Pallet ID', 'Current Location', 'Created Date', 'Receipt Number', 'Description'])

# Convert Created Date to proper datetime format
df['Created Date'] = pd.to_datetime(df['Created Date'])

# Sort by created date for realistic report flow
df = df.sort_values('Created Date').reset_index(drop=True)

# Save to Excel
df.to_excel('test_inventory_report.xlsx', index=False, engine='openpyxl')

# Calculate statistics
total_pallets = len(df)
normal_ops = len(normal_pallets)
anomalies = total_pallets - normal_ops
utilization = (total_pallets / 347) * 100

print('SUCCESS: Comprehensive test inventory report created!')
print(f'Total records: {total_pallets} pallets')
print(f'Normal operations: {normal_ops} pallets')
print(f'Anomaly records: {anomalies} pallets')
print(f'Warehouse capacity utilization: {utilization:.1f}% ({total_pallets}/347)')
print(f'Date range: {df["Created Date"].min()} to {df["Created Date"].max()}')

print('\nWarehouse Distribution:')
print(f'- Storage positions used: ~130/150 ({130/150*100:.1f}%)')
print(f'- Special areas utilized: All 6 areas active')

print('\nAnomaly Summary:')
print('- Rule 1 (Stagnant Pallets): 5 anomalies')
print('- Rule 2 (Uncoordinated Lots): 1 anomaly')
print('- Rule 3 (Overcapacity): 2 locations')
print('- Rule 4 (Invalid Location): 3 anomalies')
print('- Rule 5 (Aisle Stuck): 4 anomalies')
print('- Rule 6 (Temperature Violations): 3 anomalies')
print('- Rule 7 (Data Integrity): 4 anomalies')
print('- Rule 8 (Location Mapping): 2 anomalies')
print('TOTAL EXPECTED ANOMALIES: 24')

print('\nThis comprehensive test simulates a busy warehouse with realistic operational volume!')