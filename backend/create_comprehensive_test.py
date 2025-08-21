import pandas as pd
import datetime

inventory_data = []
base_date = datetime.datetime(2025, 8, 20, 10, 0, 0)

# Complete test case list
all_test_cases = [
    # RULE 1: Forgotten Pallets
    {'id': 'FORGOTTEN_CRITICAL_001', 'loc': 'RECV-01', 'desc': 'Critical forgotten - 5 days', 'lot': 'LOT_OLD_001', 'time_offset': -120, 'type': 'GENERAL', 'temp': 'AMBIENT'},
    {'id': 'FORGOTTEN_CRITICAL_002', 'loc': 'RECV-02', 'desc': 'Critical forgotten - 4.5 days', 'lot': 'LOT_OLD_002', 'time_offset': -108, 'type': 'GENERAL', 'temp': 'AMBIENT'},
    {'id': 'FORGOTTEN_HIGH_001', 'loc': 'RECV-01', 'desc': 'High priority forgotten - 3 days', 'lot': 'LOT_OLD_003', 'time_offset': -72, 'type': 'GENERAL', 'temp': 'AMBIENT'},
    {'id': 'FORGOTTEN_HIGH_002', 'loc': 'RECV-02', 'desc': 'High priority forgotten - 2.5 days', 'lot': 'LOT_OLD_004', 'time_offset': -60, 'type': 'GENERAL', 'temp': 'AMBIENT'},
    {'id': 'FORGOTTEN_MEDIUM_001', 'loc': 'STAGE-01', 'desc': 'Medium forgotten staging - 18h', 'lot': 'LOT_STAGE_001', 'time_offset': -18, 'type': 'GENERAL', 'temp': 'AMBIENT'},
    {'id': 'FORGOTTEN_MEDIUM_002', 'loc': 'STAGE-01', 'desc': 'Medium forgotten staging - 15h', 'lot': 'LOT_STAGE_002', 'time_offset': -15, 'type': 'GENERAL', 'temp': 'AMBIENT'},
    
    # RULE 2: Incomplete Lots
    {'id': 'INCOMPLETE_LOT_001_1', 'loc': '01-01-005A', 'desc': 'Incomplete lot test 1', 'lot': 'LOT_INCOMPLETE_001', 'time_offset': -24, 'type': 'GENERAL', 'temp': 'AMBIENT'},
    {'id': 'INCOMPLETE_LOT_001_2', 'loc': '01-01-005B', 'desc': 'Incomplete lot test 2', 'lot': 'LOT_INCOMPLETE_001', 'time_offset': -25, 'type': 'GENERAL', 'temp': 'AMBIENT'},
    {'id': 'INCOMPLETE_LOT_001_3', 'loc': '01-01-005C', 'desc': 'Incomplete lot test 3', 'lot': 'LOT_INCOMPLETE_001', 'time_offset': -26, 'type': 'GENERAL', 'temp': 'AMBIENT'},
    {'id': 'INCOMPLETE_LOT_002_1', 'loc': '01-01-006A', 'desc': 'Incomplete lot test 4', 'lot': 'LOT_INCOMPLETE_002', 'time_offset': -27, 'type': 'GENERAL', 'temp': 'AMBIENT'},
    {'id': 'INCOMPLETE_LOT_002_2', 'loc': '01-01-006B', 'desc': 'Incomplete lot test 5', 'lot': 'LOT_INCOMPLETE_002', 'time_offset': -28, 'type': 'GENERAL', 'temp': 'AMBIENT'},
]

# RULE 3: Overcapacity - RECV (15 pallets in 10-capacity)
for i in range(1, 16):
    all_test_cases.append({
        'id': f'RECV_OVER_{i:03d}',
        'loc': 'RECV-01',
        'desc': f'RECV overcapacity {i}',
        'lot': f'LOT_OVERCAP_{((i-1)//5)+1:03d}',
        'time_offset': -i,
        'type': 'GENERAL',
        'temp': 'AMBIENT'
    })

# RULE 3: Storage overcapacity
storage_overcap = [
    {'id': 'STORAGE_OVER_001', 'loc': '01-01-010A'},
    {'id': 'STORAGE_OVER_002', 'loc': '01-01-010A'},
    {'id': 'STORAGE_OVER_003', 'loc': '01-01-011A'},
    {'id': 'STORAGE_OVER_004', 'loc': '01-01-011A'},
    {'id': 'STORAGE_OVER_005', 'loc': '01-01-011A'},
]

for i, pallet in enumerate(storage_overcap):
    all_test_cases.append({
        'id': pallet['id'],
        'loc': pallet['loc'],
        'desc': f'Storage overcapacity {i+1}',
        'lot': f'LOT_STORE_OVER_{i+1:03d}',
        'time_offset': -30-i,
        'type': 'GENERAL',
        'temp': 'AMBIENT'
    })

# RULE 4: Invalid Locations
invalid_cases = [
    {'id': 'INVALID_001', 'loc': 'INVALID-LOCATION-001'},
    {'id': 'INVALID_002', 'loc': '99-99-999Z'},
    {'id': 'INVALID_003', 'loc': '01-01-999E'},
    {'id': 'INVALID_004', 'loc': 'BAD-FORMAT'},
    {'id': 'INVALID_005', 'loc': 'TYPO-RECV-01'},
]

for i, pallet in enumerate(invalid_cases):
    all_test_cases.append({
        'id': pallet['id'],
        'loc': pallet['loc'],
        'desc': f'Invalid location test {i+1}',
        'lot': f'LOT_INVALID_{i+1:03d}',
        'time_offset': -48-i,
        'type': 'GENERAL',
        'temp': 'AMBIENT'
    })

# RULE 5: AISLE Stuck Pallets
aisle_cases = [
    {'id': 'AISLE_STUCK_001', 'loc': 'AISLE-01', 'hours': 25},
    {'id': 'AISLE_STUCK_002', 'loc': 'AISLE-02', 'hours': 30},
    {'id': 'AISLE_STUCK_003', 'loc': 'AISLE-01', 'hours': 48},
]

for pallet in aisle_cases:
    all_test_cases.append({
        'id': pallet['id'],
        'loc': pallet['loc'],
        'desc': f'Aisle stuck test - {pallet["hours"]}h old',
        'lot': f'LOT_AISLE_{pallet["id"][-3:]}',
        'time_offset': -pallet['hours'],
        'type': 'GENERAL',
        'temp': 'AMBIENT'
    })

# RULE 7: Scanner Errors
scanner_cases = [
    {'id': 'DUPLICATE_SCAN_001', 'loc': '01-01-015A', 'desc': 'Scanner error - duplicate 1'},
    {'id': 'DUPLICATE_SCAN_001', 'loc': '01-01-015B', 'desc': 'Scanner error - duplicate 2'},
    {'id': 'CORRUPT_ID_###', 'loc': '01-01-016A', 'desc': 'Scanner error - corrupt ID'},
    {'id': '', 'loc': '01-01-016B', 'desc': 'Scanner error - empty ID'},
]

for i, pallet in enumerate(scanner_cases):
    all_test_cases.append({
        'id': pallet['id'],
        'loc': pallet['loc'],
        'desc': pallet['desc'],
        'lot': f'LOT_SCANNER_{i+1:03d}',
        'time_offset': 0,
        'type': 'GENERAL',
        'temp': 'AMBIENT'
    })

# RULE 8: Type Mismatches
mismatch_cases = [
    {'id': 'HAZMAT_MISMATCH_001', 'loc': '01-01-020A', 'desc': 'HAZMAT in wrong zone 1', 'type': 'HAZMAT', 'temp': 'CONTROLLED'},
    {'id': 'HAZMAT_MISMATCH_002', 'loc': '01-01-020B', 'desc': 'HAZMAT in wrong zone 2', 'type': 'HAZMAT', 'temp': 'CONTROLLED'},
    {'id': 'FROZEN_MISMATCH_001', 'loc': '01-01-021A', 'desc': 'FROZEN in wrong zone 1', 'type': 'FROZEN', 'temp': 'FROZEN'},
    {'id': 'FROZEN_MISMATCH_002', 'loc': '01-01-021B', 'desc': 'FROZEN in wrong zone 2', 'type': 'FROZEN', 'temp': 'FROZEN'},
]

for i, pallet in enumerate(mismatch_cases):
    all_test_cases.append({
        'id': pallet['id'],
        'loc': pallet['loc'],
        'desc': pallet['desc'],
        'lot': f'LOT_MISMATCH_{i+1:03d}',
        'time_offset': -12-i,
        'type': pallet['type'],
        'temp': pallet['temp']
    })

# Normal operations - should NOT trigger any rules
normal_cases = [
    {'id': 'NORMAL_STORAGE_001', 'loc': '01-01-030A', 'desc': 'Normal operation 1'},
    {'id': 'NORMAL_STORAGE_002', 'loc': '01-01-031A', 'desc': 'Normal operation 2'},
    {'id': 'NORMAL_STORAGE_003', 'loc': '01-01-032A', 'desc': 'Normal operation 3'},
    {'id': 'NORMAL_RECV_001', 'loc': 'RECV-02', 'desc': 'Normal RECV 1'},
    {'id': 'NORMAL_RECV_002', 'loc': 'RECV-02', 'desc': 'Normal RECV 2'},
    {'id': 'NORMAL_STAGE_001', 'loc': 'STAGE-01', 'desc': 'Normal STAGE 1'},
    {'id': 'NORMAL_STAGE_002', 'loc': 'STAGE-01', 'desc': 'Normal STAGE 2'},
]

for i, pallet in enumerate(normal_cases):
    all_test_cases.append({
        'id': pallet['id'],
        'loc': pallet['loc'],
        'desc': pallet['desc'],
        'lot': f'LOT_NORMAL_{i+1:03d}',
        'time_offset': -1-i//2,
        'type': 'GENERAL',
        'temp': 'AMBIENT'
    })

# Convert to DataFrame format
for case in all_test_cases:
    inventory_data.append({
        'Pallet ID': case['id'],
        'Location': case['loc'],
        'Description': case['desc'],
        'Receipt Number': case['lot'],
        'Creation Date': base_date + datetime.timedelta(hours=case['time_offset']),
        'Product Type': case['type'],
        'Temperature Requirement': case['temp']
    })

df = pd.DataFrame(inventory_data)
df.to_excel('comprehensive_rules_test_inventory.xlsx', index=False)

print(f'Created comprehensive test inventory with {len(df)} pallets')
print(f'\nTest scenarios included:')
print(f'- Rule 1 (Forgotten Pallets): 6 test cases')
print(f'- Rule 2 (Incomplete Lots): 5 test cases') 
print(f'- Rule 3 (Overcapacity): 20 test cases')
print(f'- Rule 4 (Invalid Locations): 5 test cases')
print(f'- Rule 5 (Aisle Stuck): 3 test cases')
print(f'- Rule 7 (Scanner Errors): 4 test cases')
print(f'- Rule 8 (Type Mismatches): 4 test cases')
print(f'- Normal Operations: 7 control cases')

print(f'\nLocation breakdown:')
location_counts = df['Location'].value_counts()
print(location_counts.head(15).to_string())
print(f'\nFile saved: comprehensive_rules_test_inventory.xlsx')