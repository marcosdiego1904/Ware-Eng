import pandas as pd
from datetime import datetime, timedelta
import random

# Create comprehensive test data to trigger various rule violations
data = []

# Current time for calculating stagnant pallets
now = datetime.now()

# 1. STAGNANT PALLETS - Pallets sitting too long in RECEIVING (triggers default rule: 6+ hours)
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

# 2. UNCOORDINATED LOTS - Most pallets moved to final storage, but some left in receiving
lot_receipt = 'REC2001'
# Add 8 pallets in FINAL storage (80% completion)
for i in range(8):
    data.append({
        'pallet_id': f'LOT{i+1:03d}',
        'location': f'001A',  # Rack location
        'creation_date': now - timedelta(hours=2),
        'receipt_number': lot_receipt,
        'description': 'Product for Lot Test',
        'location_type': 'FINAL'
    })

# Add 2 stragglers still in RECEIVING (triggers rule when >80% in final)
for i in range(2):
    data.append({
        'pallet_id': f'STG{i+1:03d}',
        'location': 'RECV-01',
        'creation_date': now - timedelta(hours=2),
        'receipt_number': lot_receipt,
        'description': 'Product for Lot Test',
        'location_type': 'RECEIVING'
    })

# 3. OVERCAPACITY - More pallets than location capacity allows
# RECV-01 has capacity 10, let's add 12 pallets
for i in range(7):  # 7 more + 5 stagnant + 2 stragglers = 14 total (exceeds capacity of 10)
    data.append({
        'pallet_id': f'OVER{i+1:03d}',
        'location': 'RECV-01',
        'creation_date': now - timedelta(hours=1),
        'receipt_number': f'REC{i+3001}',
        'description': f'Overcapacity Test Product {i+1}',
        'location_type': 'RECEIVING'
    })

# 4. INVALID LOCATION - Pallets in locations not defined in the system
invalid_locations = ['BADLOC-01', 'UNKNOWN-X', 'MISSING-Z']
for i, bad_loc in enumerate(invalid_locations):
    data.append({
        'pallet_id': f'INV{i+1:03d}',
        'location': bad_loc,
        'creation_date': now - timedelta(hours=1),
        'receipt_number': f'REC{i+4001}',
        'description': f'Invalid Location Test {i+1}',
        'location_type': 'UNKNOWN'
    })

# 5. LOCATION SPECIFIC STAGNANT - Pallets stuck in AISLE locations (4+ hours threshold)
aisle_locations = ['001A', '002B', '003C']
for i, aisle in enumerate(aisle_locations):
    data.append({
        'pallet_id': f'AISLE{i+1:03d}',
        'location': aisle,
        'creation_date': now - timedelta(hours=6),  # 6 hours (exceeds 4-hour threshold)
        'receipt_number': f'REC{i+5001}',
        'description': f'Aisle Stagnant Product {i+1}',
        'location_type': 'FINAL'
    })

# 6. TEMPERATURE ZONE MISMATCH - Frozen products in wrong zones
temp_sensitive_products = ['FROZEN CHICKEN BREAST', 'REFRIGERATED DAIRY MILK', 'FROZEN VEGETABLES']
wrong_zones = ['DOCK-01', 'STAGE-01', 'RECV-02']  # These should be AMBIENT/GENERAL zones
for i, (product, location) in enumerate(zip(temp_sensitive_products, wrong_zones)):
    data.append({
        'pallet_id': f'TEMP{i+1:03d}',
        'location': location,
        'creation_date': now - timedelta(minutes=45),  # 45 minutes (exceeds 30-minute threshold)
        'receipt_number': f'REC{i+6001}',
        'description': product,
        'location_type': 'STAGING' if 'STAGE' in location else 'DOCK' if 'DOCK' in location else 'RECEIVING'
    })

# 7. DATA INTEGRITY ISSUES
# Duplicate scans (same pallet_id appears twice)
data.append({
    'pallet_id': 'DUP001',
    'location': 'RECV-01',
    'creation_date': now - timedelta(hours=1),
    'receipt_number': 'REC7001',
    'description': 'Duplicate Scan Test',
    'location_type': 'RECEIVING'
})
data.append({
    'pallet_id': 'DUP001',  # Same pallet ID - triggers duplicate scan detection
    'location': 'STAGE-01',
    'creation_date': now - timedelta(hours=1),
    'receipt_number': 'REC7001',
    'description': 'Duplicate Scan Test',
    'location_type': 'STAGING'
})

# Impossible locations (too long, special characters)
impossible_locations = ['VERYLONGLOCATIONCODEISIMPOSSIBLE123456789', 'LOC@#$%', '']
for i, imp_loc in enumerate(impossible_locations):
    data.append({
        'pallet_id': f'IMP{i+1:03d}',
        'location': imp_loc,
        'creation_date': now - timedelta(hours=1),
        'receipt_number': f'REC{i+8001}',
        'description': f'Impossible Location Test {i+1}',
        'location_type': 'UNKNOWN'
    })

# 8. MISSING LOCATION - Pallets with no location assigned
missing_location_values = [None, '', 'NAN']
for i, missing_val in enumerate(missing_location_values):
    data.append({
        'pallet_id': f'MISS{i+1:03d}',
        'location': missing_val,
        'creation_date': now - timedelta(hours=1),
        'receipt_number': f'REC{i+9001}',
        'description': f'Missing Location Test {i+1}',
        'location_type': 'UNKNOWN'
    })

# 9. NORMAL OPERATIONS - Some normal pallets to show the system working correctly
normal_locations = ['STAGE-01', 'STAGE-02', 'DOCK-01', 'DOCK-02']
for i in range(10):
    location = random.choice(normal_locations)
    location_type = 'STAGING' if 'STAGE' in location else 'DOCK'
    
    data.append({
        'pallet_id': f'NORM{i+1:03d}',
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

print(f'Created inventory report with {len(df)} pallets')
print(f'Expected rule violations:')
print(f'- Stagnant Pallets: 5 pallets in RECV-01 for 8+ hours')
print(f'- Uncoordinated Lots: 2 stragglers from lot REC2001 (80% completion)')
print(f'- Overcapacity: RECV-01 with 14 pallets (capacity: 10)')
print(f'- Invalid Locations: 3 pallets in undefined locations')
print(f'- Location Specific Stagnant: 3 pallets in AISLE locations for 6+ hours')
print(f'- Temperature Zone Mismatch: 3 frozen/refrigerated products in wrong zones')
print(f'- Data Integrity: 1 duplicate scan, 3 impossible locations')
print(f'- Missing Location: 3 pallets with no location')

# Save to Excel file
df.to_excel('inventoryreport.xlsx', index=False)
print('Excel file saved as inventoryreport.xlsx')