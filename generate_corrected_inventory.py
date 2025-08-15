import pandas as pd
from datetime import datetime, timedelta
import random

# Create test data with CORRECTED understanding of rules
data = []

# Current time for calculating stagnant pallets
now = datetime.now()

# 1. STAGNANT PALLETS - Pallets sitting too long in RECEIVING (6+ hours)
stagnant_base_time = now - timedelta(hours=8)  # 8 hours ago (exceeds 6-hour threshold)
for i in range(5):
    data.append({
        'pallet_id': f'STAG{i+1:03d}',
        'location': 'RECV-01',
        'creation_date': stagnant_base_time - timedelta(minutes=random.randint(0, 120)),
        'receipt_number': f'REC{i+1001}',
        'description': f'Standard Product {i+1}',
        'location_type': 'RECEIVING'
    })

# 2. CORRECTED UNCOORDINATED LOTS TEST - Lot with 80%+ completion and stragglers
lot_receipt = 'REC2001'

# Add 8 pallets in FINAL storage (80% completion)
for i in range(8):
    data.append({
        'pallet_id': f'FINAL{i+1:03d}',
        'location': 'USER_01-02-005A',  # Using actual warehouse structure
        'creation_date': now - timedelta(hours=2),
        'receipt_number': lot_receipt,
        'description': 'Product for Lot Test - FINAL',
        'location_type': 'FINAL'
    })

# Add 2 stragglers still in RECEIVING (should trigger rule: 8/10 = 80% complete)
for i in range(2):
    data.append({
        'pallet_id': f'STRAG{i+1:03d}',
        'location': 'RECV-01',
        'creation_date': now - timedelta(hours=2),
        'receipt_number': lot_receipt,
        'description': 'Product for Lot Test - STRAGGLER',
        'location_type': 'RECEIVING'
    })

# 3. NORMAL INCOMPLETE LOT - Should NOT trigger (only 30% complete)
lot_receipt_normal = 'REC2002'
# Add 3 pallets in FINAL storage (30% completion - should NOT trigger)
for i in range(3):
    data.append({
        'pallet_id': f'NORM_FINAL{i+1:03d}',
        'location': 'USER_02-01-010B',
        'creation_date': now - timedelta(hours=1),
        'receipt_number': lot_receipt_normal,
        'description': 'Normal Incomplete Lot - FINAL',
        'location_type': 'FINAL'
    })

# Add 7 pallets still in RECEIVING (should NOT trigger - only 30% complete)
for i in range(7):
    data.append({
        'pallet_id': f'NORM_RECV{i+1:03d}',
        'location': 'RECV-02',
        'creation_date': now - timedelta(hours=1),
        'receipt_number': lot_receipt_normal,
        'description': 'Normal Incomplete Lot - RECEIVING',
        'location_type': 'RECEIVING'
    })

# 4. SINGLE PALLET LOTS - Should NOT trigger (no stragglers possible)
for i in range(3):
    data.append({
        'pallet_id': f'SINGLE{i+1:03d}',
        'location': 'RECV-02',
        'creation_date': now - timedelta(minutes=30),
        'receipt_number': f'REC{i+3001}',
        'description': f'Single Pallet Lot {i+1}',
        'location_type': 'RECEIVING'
    })

# 5. CORRECTED AISLE STAGNANT TEST - Using REAL AISLE locations
# Pallets stuck in AISLE locations for 6+ hours (exceeds 4-hour threshold)
aisle_locations = ['AISLE-A', 'AISLE-B', 'AISLETEST']
for i, aisle in enumerate(aisle_locations):
    data.append({
        'pallet_id': f'AISLE_STUCK{i+1:03d}',
        'location': aisle,
        'creation_date': now - timedelta(hours=6),  # 6 hours (exceeds 4-hour threshold)
        'receipt_number': f'REC{i+5001}',
        'description': f'Pallet Stuck in AISLE {aisle}',
        'location_type': 'TRANSITIONAL'
    })

# 6. NORMAL AISLE USAGE - Pallets in AISLE for short time (should NOT trigger)
for i in range(2):
    data.append({
        'pallet_id': f'AISLE_OK{i+1:03d}',
        'location': 'AISLE-A',
        'creation_date': now - timedelta(hours=2),  # Only 2 hours (under 4-hour threshold)
        'receipt_number': f'REC{i+6001}',
        'description': f'Normal AISLE Usage {i+1}',
        'location_type': 'TRANSITIONAL'
    })

# 7. OVERCAPACITY - More pallets than location capacity allows
# RECV-01 has capacity 10, let's add more pallets
for i in range(8):  # 8 more + 5 stagnant + 2 stragglers = 15 total (exceeds capacity of 10)
    data.append({
        'pallet_id': f'OVER{i+1:03d}',
        'location': 'RECV-01',
        'creation_date': now - timedelta(hours=1),
        'receipt_number': f'REC{i+7001}',
        'description': f'Overcapacity Test Product {i+1}',
        'location_type': 'RECEIVING'
    })

# 8. INVALID LOCATION - Pallets in locations not defined in the system
invalid_locations = ['BADLOC-01', 'UNKNOWN-X', 'MISSING-Z']
for i, bad_loc in enumerate(invalid_locations):
    data.append({
        'pallet_id': f'INV{i+1:03d}',
        'location': bad_loc,
        'creation_date': now - timedelta(hours=1),
        'receipt_number': f'REC{i+8001}',
        'description': f'Invalid Location Test {i+1}',
        'location_type': 'UNKNOWN'
    })

# 9. DATA INTEGRITY ISSUES
# Duplicate scans (same pallet_id appears twice)
data.append({
    'pallet_id': 'DUP001',
    'location': 'RECV-01',
    'creation_date': now - timedelta(hours=1),
    'receipt_number': 'REC9001',
    'description': 'Duplicate Scan Test',
    'location_type': 'RECEIVING'
})
data.append({
    'pallet_id': 'DUP001',  # Same pallet ID - triggers duplicate scan detection
    'location': 'STAGE-01',
    'creation_date': now - timedelta(hours=1),
    'receipt_number': 'REC9001',
    'description': 'Duplicate Scan Test',
    'location_type': 'STAGING'
})

# 10. NORMAL OPERATIONS - Some normal pallets
normal_locations = ['STAGE-01', 'STAGE-02', 'DOCK-01', 'DOCK-02']
for i in range(8):
    location = random.choice(normal_locations)
    location_type = 'STAGING' if 'STAGE' in location else 'DOCK'
    
    data.append({
        'pallet_id': f'NORMAL{i+1:03d}',
        'location': location,
        'creation_date': now - timedelta(minutes=random.randint(10, 90)),  # Recent activity
        'receipt_number': f'REC{i+10001}',
        'description': f'Normal Operation Product {i+1}',
        'location_type': location_type
    })

# Create DataFrame and save to Excel
df = pd.DataFrame(data)

# Format the creation_date column properly
df['creation_date'] = df['creation_date'].dt.strftime('%Y-%m-%d %H:%M:%S')

print(f'Created CORRECTED inventory report with {len(df)} pallets')
print(f'Expected rule violations:')
print(f'- Rule #2 (Lot Stragglers): 2 violations (REC2001: 80% complete, 2 stragglers)')
print(f'- Rule #2 (Should NOT trigger): Single pallets, 30% complete lot')
print(f'- Rule #5 (AISLE Stuck): 3 violations (6+ hours in AISLE-A, AISLE-B, AISLETEST)')
print(f'- Rule #5 (Should NOT trigger): 2 pallets in AISLE-A for only 2 hours')
print(f'- Rule #1 (Stagnant): 5 violations (RECV-01 for 8+ hours)')
print(f'- Rule #3 (Overcapacity): RECV-01 with 15+ pallets (capacity: 10)')
print(f'- Rule #4 (Invalid Locations): 3 violations (BADLOC-01, UNKNOWN-X, MISSING-Z)')
print(f'- Rule #7 (Data Integrity): 1 duplicate scan')

# Save to Excel file
df.to_excel('inventoryreport_corrected.xlsx', index=False)
print('Excel file saved as inventoryreport_corrected.xlsx')