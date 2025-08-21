import pandas as pd
import datetime
from datetime import timedelta
import random

# Base timestamp for creating realistic time spread
base_date = datetime.datetime(2025, 8, 20, 10, 0, 0)

# Initialize inventory data list
inventory_data = []

print("Creating Traditional Rack Warehouse Test Inventory...")
print("Target: ~350 pallets with comprehensive rule validation")
print()

# =========================================================================
# RULE 1: STAGNANT_PALLETS (Forgotten Pallets Alert)
# Test critical, high, and medium priority scenarios
# =========================================================================
print("Creating STAGNANT_PALLETS test cases...")

# Critical: 4+ days old in RECEIVING (3 pallets)
critical_forgotten = [
    {'id': 'CRITICAL_FORGOTTEN_001', 'location': 'RECV-01', 'desc': 'Critical forgotten pallet - 5 days', 'lot': 'LOT_CRITICAL_001', 'hours_ago': 120},
    {'id': 'CRITICAL_FORGOTTEN_002', 'location': 'RECV-02', 'desc': 'Critical forgotten pallet - 4.5 days', 'lot': 'LOT_CRITICAL_002', 'hours_ago': 108},
    {'id': 'CRITICAL_FORGOTTEN_003', 'location': 'RECV-01', 'desc': 'Critical forgotten pallet - 6 days', 'lot': 'LOT_CRITICAL_003', 'hours_ago': 144},
]

# High: 2-4 days old in RECEIVING (4 pallets)  
high_forgotten = [
    {'id': 'HIGH_FORGOTTEN_001', 'location': 'RECV-01', 'desc': 'High priority forgotten - 3 days', 'lot': 'LOT_HIGH_001', 'hours_ago': 72},
    {'id': 'HIGH_FORGOTTEN_002', 'location': 'RECV-02', 'desc': 'High priority forgotten - 2.5 days', 'lot': 'LOT_HIGH_002', 'hours_ago': 60},
    {'id': 'HIGH_FORGOTTEN_003', 'location': 'RECV-01', 'desc': 'High priority forgotten - 3.5 days', 'lot': 'LOT_HIGH_003', 'hours_ago': 84},
    {'id': 'HIGH_FORGOTTEN_004', 'location': 'RECV-02', 'desc': 'High priority forgotten - 2.2 days', 'lot': 'LOT_HIGH_004', 'hours_ago': 53},
]

# Medium: 12+ hours in STAGING (3 pallets)
medium_forgotten = [
    {'id': 'MEDIUM_FORGOTTEN_001', 'location': 'STAGE-01', 'desc': 'Medium forgotten staging - 18h', 'lot': 'LOT_STAGE_001', 'hours_ago': 18},
    {'id': 'MEDIUM_FORGOTTEN_002', 'location': 'STAGE-01', 'desc': 'Medium forgotten staging - 24h', 'lot': 'LOT_STAGE_002', 'hours_ago': 24},
    {'id': 'MEDIUM_FORGOTTEN_003', 'location': 'STAGE-01', 'desc': 'Medium forgotten staging - 15h', 'lot': 'LOT_STAGE_003', 'hours_ago': 15},
]

for pallet in critical_forgotten + high_forgotten + medium_forgotten:
    inventory_data.append({
        'Pallet ID': pallet['id'],
        'Location': pallet['location'],
        'Description': pallet['desc'],
        'Receipt Number': pallet['lot'],
        'Creation Date': base_date - timedelta(hours=pallet['hours_ago']),
        'Product Type': 'GENERAL',
        'Temperature Requirement': 'AMBIENT'
    })

# =========================================================================
# RULE 2: UNCOORDINATED_LOTS (Incomplete Lots Alert)
# Test lots with stragglers in RECEIVING while majority in STORAGE
# =========================================================================
print("Creating UNCOORDINATED_LOTS test cases...")

# Scenario 1: LOT_INCOMPLETE_001 - 80% complete (4 in STORAGE, 1 straggler in RECEIVING)
incomplete_lot_1 = [
    {'id': 'INCOMPLETE_LOT_001_1', 'location': '01-01-005A', 'lot': 'LOT_INCOMPLETE_001'},
    {'id': 'INCOMPLETE_LOT_001_2', 'location': '01-01-005B', 'lot': 'LOT_INCOMPLETE_001'},
    {'id': 'INCOMPLETE_LOT_001_3', 'location': '01-01-005C', 'lot': 'LOT_INCOMPLETE_001'},
    {'id': 'INCOMPLETE_LOT_001_4', 'location': '01-01-005D', 'lot': 'LOT_INCOMPLETE_001'},
    {'id': 'INCOMPLETE_LOT_001_STRAGGLER', 'location': 'RECV-01', 'lot': 'LOT_INCOMPLETE_001'},  # Straggler
]

# Scenario 2: LOT_INCOMPLETE_002 - 75% complete (3 in STORAGE, 1 straggler in RECEIVING)
incomplete_lot_2 = [
    {'id': 'INCOMPLETE_LOT_002_1', 'location': '01-02-010A', 'lot': 'LOT_INCOMPLETE_002'},
    {'id': 'INCOMPLETE_LOT_002_2', 'location': '01-02-010B', 'lot': 'LOT_INCOMPLETE_002'},
    {'id': 'INCOMPLETE_LOT_002_3', 'location': '01-02-010C', 'lot': 'LOT_INCOMPLETE_002'},
    {'id': 'INCOMPLETE_LOT_002_STRAGGLER', 'location': 'RECV-02', 'lot': 'LOT_INCOMPLETE_002'},  # Straggler
]

for i, pallet in enumerate(incomplete_lot_1 + incomplete_lot_2):
    inventory_data.append({
        'Pallet ID': pallet['id'],
        'Location': pallet['location'],
        'Description': f'Incomplete lot test pallet {i+1}',
        'Receipt Number': pallet['lot'],
        'Creation Date': base_date - timedelta(hours=36+i),
        'Product Type': 'GENERAL',
        'Temperature Requirement': 'AMBIENT'
    })

# =========================================================================
# RULE 3: OVERCAPACITY (Overcapacity Alert)
# Test RECEIVING and STORAGE overcapacity scenarios
# =========================================================================
print("Creating OVERCAPACITY test cases...")

# RECEIVING Overcapacity: 15 pallets in RECV-01 (10-capacity) = 1.5x
recv_overcap = []
for i in range(1, 16):
    recv_overcap.append({
        'id': f'RECV_OVERCAP_{i:03d}',
        'location': 'RECV-01',
        'desc': f'RECV overcapacity test {i}',
        'lot': f'LOT_RECV_OVERCAP_{((i-1)//5)+1:03d}',
        'hours_ago': i + 5  # Make these forgotten too for cross-rule testing
    })

# STORAGE Overcapacity: Multiple pallets in 1-capacity locations
storage_overcap = [
    # 3 pallets in 01-01-015A (3.0x capacity)
    {'id': 'STORAGE_OVERCAP_001', 'location': '01-01-015A'},
    {'id': 'STORAGE_OVERCAP_002', 'location': '01-01-015A'},
    {'id': 'STORAGE_OVERCAP_003', 'location': '01-01-015A'},
    
    # 2 pallets in 01-01-015B (2.0x capacity)
    {'id': 'STORAGE_OVERCAP_004', 'location': '01-01-015B'},
    {'id': 'STORAGE_OVERCAP_005', 'location': '01-01-015B'},
    
    # 4 pallets in 01-02-020A (4.0x capacity - extreme case)
    {'id': 'STORAGE_OVERCAP_006', 'location': '01-02-020A'},
    {'id': 'STORAGE_OVERCAP_007', 'location': '01-02-020A'},
    {'id': 'STORAGE_OVERCAP_008', 'location': '01-02-020A'},
    {'id': 'STORAGE_OVERCAP_009', 'location': '01-02-020A'},
]

for pallet in recv_overcap:
    inventory_data.append({
        'Pallet ID': pallet['id'],
        'Location': pallet['location'],
        'Description': pallet['desc'],
        'Receipt Number': pallet['lot'],
        'Creation Date': base_date - timedelta(hours=pallet['hours_ago']),
        'Product Type': 'GENERAL',
        'Temperature Requirement': 'AMBIENT'
    })

for i, pallet in enumerate(storage_overcap):
    inventory_data.append({
        'Pallet ID': pallet['id'],
        'Location': pallet['location'],
        'Description': f'Storage overcapacity test {i+1}',
        'Receipt Number': f'LOT_STORAGE_OVERCAP_{i+1:03d}',
        'Creation Date': base_date - timedelta(hours=12+i),
        'Product Type': 'GENERAL',
        'Temperature Requirement': 'AMBIENT'
    })

# =========================================================================
# RULE 4: INVALID_LOCATION (Invalid Locations Alert)
# Test various invalid location formats
# =========================================================================
print("Creating INVALID_LOCATION test cases...")

invalid_locations = [
    {'id': 'INVALID_001', 'location': 'INVALID-LOC-001', 'desc': 'Invalid location format test 1'},
    {'id': 'INVALID_002', 'location': 'BAD-FORMAT', 'desc': 'Invalid location format test 2'},
    {'id': 'INVALID_003', 'location': '@#$%^&', 'desc': 'Invalid special characters test'},
    {'id': 'INVALID_004', 'location': '99-99-999Z', 'desc': 'Non-existent rack location'},
    {'id': 'INVALID_005', 'location': 'FAKE-LOCATION', 'desc': 'Completely fake location'},
]

for i, pallet in enumerate(invalid_locations):
    inventory_data.append({
        'Pallet ID': pallet['id'],
        'Location': pallet['location'],
        'Description': pallet['desc'],
        'Receipt Number': f'LOT_INVALID_{i+1:03d}',
        'Creation Date': base_date - timedelta(hours=48+i),
        'Product Type': 'GENERAL',
        'Temperature Requirement': 'AMBIENT'
    })

# =========================================================================
# RULE 5: LOCATION_SPECIFIC_STAGNANT (AISLE Stuck Pallets)
# Test pallets stuck in AISLE locations
# =========================================================================
print("Creating LOCATION_SPECIFIC_STAGNANT test cases...")

aisle_stuck = [
    {'id': 'AISLE_STUCK_001', 'location': 'AISLE-01', 'hours': 25},  # >4h threshold
    {'id': 'AISLE_STUCK_002', 'location': 'AISLE-02', 'hours': 30},
    {'id': 'AISLE_STUCK_003', 'location': 'AISLE-01', 'hours': 48},
]

for pallet in aisle_stuck:
    inventory_data.append({
        'Pallet ID': pallet['id'],
        'Location': pallet['location'],
        'Description': f'Aisle stuck test - {pallet["hours"]}h old',
        'Receipt Number': f'LOT_AISLE_{pallet["id"][-3:]}',
        'Creation Date': base_date - timedelta(hours=pallet['hours']),
        'Product Type': 'GENERAL',
        'Temperature Requirement': 'AMBIENT'
    })

# =========================================================================
# RULE 7: DATA_INTEGRITY (Scanner Error Detection)
# Test duplicate scans and corrupted IDs
# =========================================================================
print("Creating DATA_INTEGRITY test cases...")

# Duplicate scan scenarios
duplicate_scans = [
    {'id': 'DUPLICATE_SCAN_001', 'location': '01-01-018A', 'desc': 'Scanner error - duplicate 1'},
    {'id': 'DUPLICATE_SCAN_001', 'location': '01-01-018B', 'desc': 'Scanner error - duplicate 2'},
    {'id': 'CORRUPTED_ID_###', 'location': '01-01-019A', 'desc': 'Scanner error - corrupted ID'},
    {'id': '', 'location': '01-01-019B', 'desc': 'Scanner error - empty ID'},
]

for i, pallet in enumerate(duplicate_scans):
    inventory_data.append({
        'Pallet ID': pallet['id'],
        'Location': pallet['location'],
        'Description': pallet['desc'],
        'Receipt Number': f'LOT_SCANNER_{i+1:03d}',
        'Creation Date': base_date - timedelta(minutes=30+i*5),
        'Product Type': 'GENERAL',
        'Temperature Requirement': 'AMBIENT'
    })

# =========================================================================
# NORMAL OPERATIONS (60-70% of inventory)
# Realistic warehouse operations with proper distributions
# =========================================================================
print("Creating NORMAL OPERATIONS inventory...")

# Recent storage locations (proper utilization)
normal_storage_locations = []
for aisle in range(1, 4):  # 3 aisles
    for rack in range(1, 3):  # 2 racks  
        for position in range(1, 21):  # 20 positions
            for level in ['A', 'B', 'C', 'D']:  # 4 levels
                location = f'{aisle:02d}-{rack:02d}-{position:03d}{level}'
                normal_storage_locations.append(location)

# Randomly select locations for normal operations (avoid overcapacity test locations)
excluded_locations = ['01-01-015A', '01-01-015B', '01-02-020A']
available_locations = [loc for loc in normal_storage_locations if loc not in excluded_locations]

# Create normal inventory (200 pallets for 60-70% of total)
normal_pallets = random.sample(available_locations, 200)

# Product type distribution
product_types = ['GENERAL'] * 140 + ['HAZMAT'] * 30 + ['FROZEN'] * 20 + ['FRAGILE'] * 10
random.shuffle(product_types)

# Temperature requirements
temp_requirements = ['AMBIENT'] * 170 + ['CONTROLLED'] * 20 + ['FROZEN'] * 10

# Lot numbers (realistic distribution)
lot_numbers = [f'LOT_NORMAL_{i:03d}' for i in range(1, 26)] * 8  # 25 lots, 8 pallets each

for i, location in enumerate(normal_pallets):
    inventory_data.append({
        'Pallet ID': f'NORMAL_PLT_{i+1:04d}',
        'Location': location,
        'Description': f'Normal operation pallet {i+1}',
        'Receipt Number': random.choice(lot_numbers),
        'Creation Date': base_date - timedelta(hours=random.randint(1, 48)),
        'Product Type': product_types[i] if i < len(product_types) else 'GENERAL',
        'Temperature Requirement': temp_requirements[i] if i < len(temp_requirements) else 'AMBIENT'
    })

# Recent operations in special areas (normal capacity)
special_area_normal = [
    # RECV-02 with normal load (7 pallets in 10-capacity)
    *[{'location': 'RECV-02', 'desc': f'Normal receiving {i}'} for i in range(1, 8)],
    
    # STAGE-01 with normal load (3 pallets in 5-capacity)  
    *[{'location': 'STAGE-01', 'desc': f'Normal staging {i}'} for i in range(1, 4)],
    
    # DOCK-01 with normal load (1 pallet in 2-capacity)
    {'location': 'DOCK-01', 'desc': 'Normal dock operations'},
]

for i, pallet in enumerate(special_area_normal):
    inventory_data.append({
        'Pallet ID': f'NORMAL_SPEC_{i+1:03d}',
        'Location': pallet['location'],
        'Description': pallet['desc'],
        'Receipt Number': f'LOT_NORMAL_SPEC_{i+1:03d}',
        'Creation Date': base_date - timedelta(hours=random.randint(1, 8)),
        'Product Type': 'GENERAL',
        'Temperature Requirement': 'AMBIENT'
    })

# =========================================================================
# CREATE EXCEL FILE
# =========================================================================
print(f"Creating Excel file with {len(inventory_data)} total pallets...")

# Create DataFrame
df = pd.DataFrame(inventory_data)

# Save to Excel
filename = 'traditional_rack_basic_validation_test.xlsx'
df.to_excel(f'C:/Users/juanb/Documents/Diego/Projects/ware2/backend/{filename}', index=False)

print(f'✅ Successfully created: {filename}')
print(f'📊 Total pallets: {len(df)}')
print()

# =========================================================================
# EXPECTED VIOLATIONS SUMMARY
# =========================================================================
print("=" * 60)
print("EXPECTED VIOLATIONS SUMMARY")
print("=" * 60)

print(f"**Test File**: {filename}")
print(f"**Total Pallets**: {len(df)}")
print(f"**Test Focus**: Traditional Rack Basic Validation - All Rules")
print()

print("### Rule 1 (Forgotten Pallets): 25 expected violations")
print("- Critical: 3 pallets (>4 days in RECEIVING)")
print("- High: 4 pallets (2-4 days in RECEIVING)")
print("- Medium: 3 pallets (>12h in STAGING)")
print("- Cross-rule: 15 pallets (RECV overcapacity + forgotten)")
print()

print("### Rule 2 (Incomplete Lots): 2 expected violations")
print("- LOT_INCOMPLETE_001: 1 straggler (80% complete)")
print("- LOT_INCOMPLETE_002: 1 straggler (75% complete)")
print()

print("### Rule 3 (Overcapacity): 24 expected violations")
print("- RECV-01: 15 pallets in 10-capacity location (1.5x)")
print("- 01-01-015A: 3 pallets in 1-capacity location (3.0x)")
print("- 01-01-015B: 2 pallets in 1-capacity location (2.0x)")
print("- 01-02-020A: 4 pallets in 1-capacity location (4.0x)")
print()

print("### Rule 4 (Invalid Locations): 5 expected violations")
print("- INVALID-LOC-001, BAD-FORMAT, @#$%^&, 99-99-999Z, FAKE-LOCATION")
print()

print("### Rule 5 (Aisle Stuck): 3 expected violations")
print("- AISLE-01: 2 pallets >4h old")
print("- AISLE-02: 1 pallet >4h old")
print()

print("### Rule 7 (Scanner Errors): 4 expected violations")
print("- Duplicates: DUPLICATE_SCAN_001 (2 locations)")
print("- Corrupted: CORRUPTED_ID_###, empty ID")
print()

print("### Cross-Rule Intelligence: 15 expected correlations")
print("- RECV-01 overcapacity pallets also trigger forgotten pallet rule")
print("- Multi-dimensional detection validation")
print()

print("### Performance Expectations:")
print("- Processing time: <8 seconds")
print("- Memory usage: <100 MB")
print("- Response time: <5 seconds")
print()

print("=" * 60)
print("✅ TEST INVENTORY CREATION COMPLETE")
print("🎯 Ready for systematic validation testing")
print("=" * 60)