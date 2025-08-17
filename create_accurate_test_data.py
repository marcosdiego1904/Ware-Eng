import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Create comprehensive test data matching actual warehouse size
# Warehouse: 2 aisles × 1 rack × 25 positions × 3 levels = 150 storage positions

now = datetime.now()

# Storage location generator for actual warehouse structure
def generate_storage_locations():
    locations = []
    for aisle in range(1, 3):  # 2 aisles (01, 02)
        for rack in range(1, 2):  # 1 rack (01)
            for position in range(1, 26):  # 25 positions (001-025)
                for level in ['A', 'B', 'C']:  # 3 levels
                    location = f"{aisle:02d}-{rack:02d}-{position:03d}{level}"
                    locations.append(location)
    return locations

storage_locations = generate_storage_locations()
print(f"Generated {len(storage_locations)} storage locations")

# Normal baseline pallets distributed across warehouse (30 pallets - ~20% capacity utilization)
normal_pallets = [
    ['PLT-NORMAL-001', '01-01-001A', now - timedelta(hours=2), 'RCT-NORMAL-001', 'Standard Product A'],
    ['PLT-NORMAL-002', '01-01-001B', now - timedelta(hours=2, minutes=5), 'RCT-NORMAL-002', 'Standard Product B'],
    ['PLT-NORMAL-003', '01-01-002A', now - timedelta(hours=2, minutes=10), 'RCT-NORMAL-003', 'Standard Product C'],
    ['PLT-NORMAL-004', '01-01-003A', now - timedelta(hours=2, minutes=15), 'RCT-NORMAL-004', 'Standard Product D'],
    ['PLT-NORMAL-005', '01-01-005A', now - timedelta(hours=2, minutes=20), 'RCT-NORMAL-005', 'Standard Product E'],
    ['PLT-NORMAL-006', '01-01-008A', now - timedelta(hours=2, minutes=25), 'RCT-NORMAL-006', 'Standard Product F'],
    ['PLT-NORMAL-007', '01-01-010B', now - timedelta(hours=2, minutes=30), 'RCT-NORMAL-007', 'Standard Product G'],
    ['PLT-NORMAL-008', '01-01-012A', now - timedelta(hours=2, minutes=35), 'RCT-NORMAL-008', 'Standard Product H'],
    ['PLT-NORMAL-009', '01-01-015C', now - timedelta(hours=2, minutes=40), 'RCT-NORMAL-009', 'Standard Product I'],
    ['PLT-NORMAL-010', '01-01-020A', now - timedelta(hours=2, minutes=45), 'RCT-NORMAL-010', 'Standard Product J'],
    ['PLT-NORMAL-011', '02-01-001A', now - timedelta(hours=2, minutes=50), 'RCT-NORMAL-011', 'Standard Product K'],
    ['PLT-NORMAL-012', '02-01-003B', now - timedelta(hours=2, minutes=55), 'RCT-NORMAL-012', 'Standard Product L'],
    ['PLT-NORMAL-013', '02-01-005A', now - timedelta(hours=3), 'RCT-NORMAL-013', 'Standard Product M'],
    ['PLT-NORMAL-014', '02-01-008C', now - timedelta(hours=3, minutes=5), 'RCT-NORMAL-014', 'Standard Product N'],
    ['PLT-NORMAL-015', '02-01-010A', now - timedelta(hours=3, minutes=10), 'RCT-NORMAL-015', 'Standard Product O'],
    ['PLT-NORMAL-016', '02-01-012B', now - timedelta(hours=3, minutes=15), 'RCT-NORMAL-016', 'Standard Product P'],
    ['PLT-NORMAL-017', '02-01-015A', now - timedelta(hours=3, minutes=20), 'RCT-NORMAL-017', 'Standard Product Q'],
    ['PLT-NORMAL-018', '02-01-018C', now - timedelta(hours=3, minutes=25), 'RCT-NORMAL-018', 'Standard Product R'],
    ['PLT-NORMAL-019', '02-01-020A', now - timedelta(hours=3, minutes=30), 'RCT-NORMAL-019', 'Standard Product S'],
    ['PLT-NORMAL-020', '02-01-025B', now - timedelta(hours=3, minutes=35), 'RCT-NORMAL-020', 'Standard Product T'],
    # Special area pallets
    ['PLT-NORMAL-021', 'STAGE-01', now - timedelta(minutes=30), 'RCT-NORMAL-021', 'Staging Product A'],
    ['PLT-NORMAL-022', 'STAGE-02', now - timedelta(minutes=35), 'RCT-NORMAL-022', 'Staging Product B'],
    ['PLT-NORMAL-023', 'DOCK-01', now - timedelta(minutes=40), 'RCT-NORMAL-023', 'Loading Product A'],
    ['PLT-NORMAL-024', 'DOCK-02', now - timedelta(minutes=45), 'RCT-NORMAL-024', 'Loading Product B'],
    ['PLT-NORMAL-025', 'RECV-01', now - timedelta(hours=1), 'RCT-NORMAL-025', 'Recent Arrival A'],
    ['PLT-NORMAL-026', 'RECV-02', now - timedelta(hours=1, minutes=15), 'RCT-NORMAL-026', 'Recent Arrival B'],
    ['PLT-NORMAL-027', '01-01-007A', now - timedelta(hours=4), 'RCT-NORMAL-027', 'Standard Product U'],
    ['PLT-NORMAL-028', '01-01-014B', now - timedelta(hours=4, minutes=10), 'RCT-NORMAL-028', 'Standard Product V'],
    ['PLT-NORMAL-029', '02-01-007A', now - timedelta(hours=4, minutes=20), 'RCT-NORMAL-029', 'Standard Product W'],
    ['PLT-NORMAL-030', '02-01-022C', now - timedelta(hours=4, minutes=30), 'RCT-NORMAL-030', 'Standard Product X'],
]

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
    ['PLT-LOT-001-01', '01-01-004A', now - timedelta(hours=8), 'LOT-001', 'Coordinated Lot Product 1'],
    ['PLT-LOT-001-02', '01-01-004B', now - timedelta(hours=8), 'LOT-001', 'Coordinated Lot Product 2'],
    ['PLT-LOT-001-03', '01-01-006A', now - timedelta(hours=8), 'LOT-001', 'Coordinated Lot Product 3'],
    ['PLT-LOT-001-04', '01-01-006B', now - timedelta(hours=8), 'LOT-001', 'Coordinated Lot Product 4'],
    ['PLT-LOT-001-05', '02-01-004A', now - timedelta(hours=8), 'LOT-001', 'Coordinated Lot Product 5'],
    ['PLT-LOT-001-06', '02-01-004B', now - timedelta(hours=8), 'LOT-001', 'Coordinated Lot Product 6'],
    ['PLT-LOT-001-07', '02-01-006A', now - timedelta(hours=8), 'LOT-001', 'Coordinated Lot Product 7'],
    ['PLT-LOT-001-08', '02-01-006B', now - timedelta(hours=8), 'LOT-001', 'Coordinated Lot Product 8'],
    ['PLT-LOT-001-09', '01-01-009A', now - timedelta(hours=8), 'LOT-001', 'Coordinated Lot Product 9'],
    ['PLT-LOT-001-STRAGGLER', 'RECV-01', now - timedelta(hours=8), 'LOT-001', 'Coordinated Lot Product STRAGGLER'],  # ANOMALY
]

# RULE 3: OVERCAPACITY - 2 anomalies 
overcap_pallets = [
    # RECV-01 overcapacity (capacity 10, adding 12 pallets = 2 extra)
    ['PLT-OVERCAP-01', 'RECV-01', now - timedelta(hours=1), 'RCT-OVERCAP-01', 'Overcapacity Test 1'],
    ['PLT-OVERCAP-02', 'RECV-01', now - timedelta(hours=1, minutes=5), 'RCT-OVERCAP-02', 'Overcapacity Test 2'],
    ['PLT-OVERCAP-03', 'RECV-01', now - timedelta(hours=1, minutes=10), 'RCT-OVERCAP-03', 'Overcapacity Test 3'],
    ['PLT-OVERCAP-04', 'RECV-01', now - timedelta(hours=1, minutes=15), 'RCT-OVERCAP-04', 'Overcapacity Test 4'],
    ['PLT-OVERCAP-05', 'RECV-01', now - timedelta(hours=1, minutes=20), 'RCT-OVERCAP-05', 'Overcapacity Test 5'],
    ['PLT-OVERCAP-06', 'RECV-01', now - timedelta(hours=1, minutes=25), 'RCT-OVERCAP-06', 'Overcapacity Test 6'],
    ['PLT-OVERCAP-07', 'RECV-01', now - timedelta(hours=1, minutes=30), 'RCT-OVERCAP-07', 'Overcapacity Test 7'],
    ['PLT-OVERCAP-08', 'RECV-01', now - timedelta(hours=1, minutes=35), 'RCT-OVERCAP-08', 'Overcapacity Test 8'],
    ['PLT-OVERCAP-09', 'RECV-01', now - timedelta(hours=1, minutes=40), 'RCT-OVERCAP-09', 'Overcapacity Test 9'],
    ['PLT-OVERCAP-10', 'RECV-01', now - timedelta(hours=1, minutes=45), 'RCT-OVERCAP-10', 'Overcapacity Test 10'],
    ['PLT-OVERCAP-11', 'RECV-01', now - timedelta(hours=1, minutes=50), 'RCT-OVERCAP-11', 'Overcapacity Test 11'],
    ['PLT-OVERCAP-12', 'RECV-01', now - timedelta(hours=1, minutes=55), 'RCT-OVERCAP-12', 'Overcapacity Test 12'],
    # Storage position overcapacity (capacity 2, adding 4 pallets = 2 extra)
    ['PLT-OVERCAP-STORAGE-01', '01-01-011A', now - timedelta(hours=1), 'RCT-OVERCAP-STORAGE-01', 'Storage Overcap 1'],
    ['PLT-OVERCAP-STORAGE-02', '01-01-011A', now - timedelta(hours=1, minutes=5), 'RCT-OVERCAP-STORAGE-02', 'Storage Overcap 2'],
    ['PLT-OVERCAP-STORAGE-03', '01-01-011A', now - timedelta(hours=1, minutes=10), 'RCT-OVERCAP-STORAGE-03', 'Storage Overcap 3'],
    ['PLT-OVERCAP-STORAGE-04', '01-01-011A', now - timedelta(hours=1, minutes=15), 'RCT-OVERCAP-STORAGE-04', 'Storage Overcap 4'],
]

# RULE 4: INVALID_LOCATION - 3 anomalies
invalid_pallets = [
    ['PLT-INVALID-001', 'BADLOC-01', now - timedelta(hours=3), 'RCT-INVALID-001', 'Invalid Location Test 1'],
    ['PLT-INVALID-002', 'UNKNOWN-99', now - timedelta(hours=3, minutes=5), 'RCT-INVALID-002', 'Invalid Location Test 2'],
    ['PLT-INVALID-003', 'FAKE-AREA', now - timedelta(hours=3, minutes=10), 'RCT-INVALID-003', 'Invalid Location Test 3'],
]

# RULE 5: LOCATION_SPECIFIC_STAGNANT (AISLE >4 hours) - 4 anomalies
aisle_stuck_pallets = [
    ['PLT-AISLE-STUCK-01', 'AISLE-NORTH', now - timedelta(hours=6), 'RCT-AISLE-01', 'Aisle Stuck Product 1'],
    ['PLT-AISLE-STUCK-02', 'AISLE-NORTH', now - timedelta(hours=8), 'RCT-AISLE-02', 'Aisle Stuck Product 2'],
    ['PLT-AISLE-STUCK-03', 'AISLE-SOUTH', now - timedelta(hours=7), 'RCT-AISLE-03', 'Aisle Stuck Product 3'],
    ['PLT-AISLE-STUCK-04', 'AISLE-SOUTH', now - timedelta(hours=9), 'RCT-AISLE-04', 'Aisle Stuck Product 4'],
]

# RULE 6: TEMPERATURE_ZONE_MISMATCH - 3 anomalies (FROZEN/REFRIGERATED in wrong zones)
temp_violation_pallets = [
    ['PLT-TEMP-VIOLATION-01', '01-01-016A', now - timedelta(hours=4), 'RCT-TEMP-01', 'FROZEN VEGETABLES'],
    ['PLT-TEMP-VIOLATION-02', '02-01-016B', now - timedelta(hours=4, minutes=5), 'RCT-TEMP-02', 'FROZEN MEAT PRODUCTS'],
    ['PLT-TEMP-VIOLATION-03', '01-01-017C', now - timedelta(hours=4, minutes=10), 'RCT-TEMP-03', 'REFRIGERATED DAIRY'],
]

# RULE 7: DATA_INTEGRITY (Duplicate pallet IDs) - 4 anomalies (2 sets of duplicates)
duplicate_pallets = [
    ['DUP-001', '01-01-018A', now - timedelta(hours=5), 'RCT-DUP-001', 'Duplicate Pallet Test 1'],
    ['DUP-001', '02-01-018B', now - timedelta(hours=5, minutes=5), 'RCT-DUP-001-COPY', 'Duplicate Pallet Test 1 Copy'],
    ['DUP-002', '01-01-019A', now - timedelta(hours=5, minutes=10), 'RCT-DUP-002', 'Duplicate Pallet Test 2'],
    ['DUP-002', '02-01-019B', now - timedelta(hours=5, minutes=15), 'RCT-DUP-002-COPY', 'Duplicate Pallet Test 2 Copy'],
]

# RULE 8: LOCATION_MAPPING_ERROR - 2 anomalies (inconsistent location mappings)
mapping_error_pallets = [
    ['PLT-MAPPING-ERROR-01', 'RECV-01', now - timedelta(hours=6), 'RCT-MAPPING-01', 'Location Mapping Error 1'],
    ['PLT-MAPPING-ERROR-02', 'DOCK-01', now - timedelta(hours=6, minutes=5), 'RCT-MAPPING-02', 'Location Mapping Error 2'],
]

# Combine all data
all_data = (normal_pallets + stagnant_pallets + lot_pallets + overcap_pallets + 
           invalid_pallets + aisle_stuck_pallets + temp_violation_pallets + 
           duplicate_pallets + mapping_error_pallets)

# Create DataFrame
df = pd.DataFrame(all_data, columns=['Pallet ID', 'Current Location', 'Created Date', 'Receipt Number', 'Description'])

# Convert Created Date to proper datetime format
df['Created Date'] = pd.to_datetime(df['Created Date'])

# Save to Excel
df.to_excel('test_inventory_report.xlsx', index=False, engine='openpyxl')

print('SUCCESS: Test inventory report created successfully!')
print(f'Total records: {len(df)}')
print(f'Normal operations: 30 pallets')
print(f'Date range: {df["Created Date"].min()} to {df["Created Date"].max()}')
print(f'Warehouse capacity utilization: {len(df)}/334 = {len(df)/334*100:.1f}%')
print('\nAnomaly Summary:')
print('- Rule 1 (Stagnant Pallets): 5 anomalies')
print('- Rule 2 (Uncoordinated Lots): 1 anomaly')
print('- Rule 3 (Overcapacity): 2 anomalies')
print('- Rule 4 (Invalid Location): 3 anomalies')
print('- Rule 5 (Aisle Stuck): 4 anomalies')
print('- Rule 6 (Temperature Violations): 3 anomalies')
print('- Rule 7 (Data Integrity): 4 anomalies')
print('- Rule 8 (Location Mapping): 2 anomalies')
print('TOTAL EXPECTED ANOMALIES: 24')
print('\nStorage location examples:')
print('- First position: 01-01-001A (Aisle 1, Rack 1, Position 1, Level A)')
print('- Last position: 02-01-025C (Aisle 2, Rack 1, Position 25, Level C)')
print(f'- Total storage positions available: {len(storage_locations)}')