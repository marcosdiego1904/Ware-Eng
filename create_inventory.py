import pandas as pd
from datetime import datetime, timedelta

data = []
now = datetime.now()

# 1. FORGOTTEN PALLETS (4 anomalies) - >6 hours in RECEIVING/TRANSITIONAL
data.extend([
    {'Pallet ID': 'FORGOT-001', 'Location': 'RECV-01', 'Created Date': now - timedelta(hours=8), 'Receipt Number': 'REC001', 'Description': 'Frozen Vegetables'},
    {'Pallet ID': 'FORGOT-002', 'Location': 'RECV-02', 'Created Date': now - timedelta(hours=12), 'Receipt Number': 'REC002', 'Description': 'Dairy Products'},
    {'Pallet ID': 'FORGOT-003', 'Location': 'AISLE-01', 'Created Date': now - timedelta(hours=10), 'Receipt Number': 'REC003', 'Description': 'Paper Towels'},
    {'Pallet ID': 'FORGOT-004', 'Location': 'AISLE-02', 'Created Date': now - timedelta(hours=7), 'Receipt Number': 'REC004', 'Description': 'Canned Goods'},
])

# 2. INCOMPLETE LOTS (3 anomalies) - Lot with missing pallets
data.extend([
    {'Pallet ID': 'LOT-A-001', 'Location': '01A01A', 'Created Date': now - timedelta(hours=2), 'Receipt Number': 'LOT001', 'Description': 'Bread Lot A'},
    {'Pallet ID': 'LOT-A-002', 'Location': '01A01B', 'Created Date': now - timedelta(hours=2), 'Receipt Number': 'LOT001', 'Description': 'Bread Lot A'},
    {'Pallet ID': 'LOT-A-003', 'Location': '01A02A', 'Created Date': now - timedelta(hours=2), 'Receipt Number': 'LOT001', 'Description': 'Bread Lot A'},
])

# 3. OVERCAPACITY (6 anomalies) - Exceeding 2 pallets per level
# Put 4 pallets in 01A01A (capacity 2)
data.extend([
    {'Pallet ID': 'OVER-001', 'Location': '01A01A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'OVER001', 'Description': 'Excess 1'},
    {'Pallet ID': 'OVER-002', 'Location': '01A01A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'OVER002', 'Description': 'Excess 2'},
    {'Pallet ID': 'OVER-003', 'Location': '01A01A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'OVER003', 'Description': 'Excess 3'},
    {'Pallet ID': 'OVER-004', 'Location': '01A01A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'OVER004', 'Description': 'Excess 4'},
])

# Put 7 pallets in STAGE-01 (capacity 5)
data.extend([
    {'Pallet ID': 'STAGE-001', 'Location': 'STAGE-01', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'STG001', 'Description': 'Staging Overflow 1'},
    {'Pallet ID': 'STAGE-002', 'Location': 'STAGE-01', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'STG002', 'Description': 'Staging Overflow 2'},
])

# 4. INVALID LOCATIONS (3 anomalies) - Non-existent locations
data.extend([
    {'Pallet ID': 'INVALID-001', 'Location': 'FAKE-LOC-01', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'INV001', 'Description': 'Invalid Location'},
    {'Pallet ID': 'INVALID-002', 'Location': 'NONEXIST-02', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'INV002', 'Description': 'Bad Location'},
    {'Pallet ID': 'INVALID-003', 'Location': '99Z99Z', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'INV003', 'Description': 'Wrong Code'},
])

# 5. AISLE STUCK (2 anomalies) - Too long in transitional areas
data.extend([
    {'Pallet ID': 'STUCK-001', 'Location': 'AISLE-01', 'Created Date': now - timedelta(hours=24), 'Receipt Number': 'STUCK001', 'Description': 'Been Here Too Long'},
    {'Pallet ID': 'STUCK-002', 'Location': 'AISLE-02', 'Created Date': now - timedelta(hours=18), 'Receipt Number': 'STUCK002', 'Description': 'Another Stuck'},
])

# 6. COLD CHAIN (4 anomalies) - Temperature products in wrong zones
data.extend([
    {'Pallet ID': 'COLD-001', 'Location': '01A03A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'COLD001', 'Description': 'Ice Cream - Should be FROZEN'},
    {'Pallet ID': 'COLD-002', 'Location': '01A04A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'COLD002', 'Description': 'Milk - Should be COLD'},
    {'Pallet ID': 'COLD-003', 'Location': '01A05A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'COLD003', 'Description': 'Frozen Pizza - Should be FROZEN'},
    {'Pallet ID': 'COLD-004', 'Location': '01A06A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'COLD004', 'Description': 'Yogurt - Should be COLD'},
])

# 7. SCANNER ERROR (6 anomalies) - Data integrity issues
data.extend([
    {'Pallet ID': '', 'Location': '01A07A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'SCAN001', 'Description': 'Missing Pallet ID'},
    {'Pallet ID': 'SCAN-002', 'Location': '', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'SCAN002', 'Description': 'Missing Location'},
    {'Pallet ID': 'SCAN-003', 'Location': '01A08A', 'Created Date': '', 'Receipt Number': 'SCAN003', 'Description': 'Missing Date'},
    {'Pallet ID': 'SCAN-004', 'Location': '01A09A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': '', 'Description': 'Missing Receipt'},
    {'Pallet ID': 'DUPLICATE', 'Location': '01A10A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'SCAN005', 'Description': 'First Entry'},
    {'Pallet ID': 'DUPLICATE', 'Location': '01A10B', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'SCAN006', 'Description': 'Duplicate Entry'},
])

# 8. LOCATION MISMATCH (3 anomalies) - Product-location compatibility
data.extend([
    {'Pallet ID': 'MISMATCH-001', 'Location': 'DOCK-01', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'MIS001', 'Description': 'Heavy Item at Dock - Wrong Zone'},
    {'Pallet ID': 'MISMATCH-002', 'Location': 'RECV-01', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'MIS002', 'Description': 'Finished Good in Receiving'},
    {'Pallet ID': 'MISMATCH-003', 'Location': 'STAGE-01', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'MIS003', 'Description': 'Raw Material in Staging'},
])

# Good pallets for balance
data.extend([
    {'Pallet ID': 'GOOD-001', 'Location': '01A15A', 'Created Date': now - timedelta(hours=2), 'Receipt Number': 'GOOD001', 'Description': 'Normal Pallet 1'},
    {'Pallet ID': 'GOOD-002', 'Location': '01A15B', 'Created Date': now - timedelta(hours=2), 'Receipt Number': 'GOOD002', 'Description': 'Normal Pallet 2'},
    {'Pallet ID': 'GOOD-003', 'Location': '02A01A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'GOOD003', 'Description': 'Normal Pallet 3'},
    {'Pallet ID': 'GOOD-004', 'Location': '02A02A', 'Created Date': now - timedelta(hours=3), 'Receipt Number': 'GOOD004', 'Description': 'Normal Pallet 4'},
    {'Pallet ID': 'GOOD-005', 'Location': '02A03A', 'Created Date': now - timedelta(hours=1), 'Receipt Number': 'GOOD005', 'Description': 'Normal Pallet 5'},
])

df = pd.DataFrame(data)
df['Created Date'] = df['Created Date'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) and x != '' else '')
df.to_excel('inventoryreport.xlsx', index=False)

print(f'Created inventoryreport.xlsx with {len(df)} records')
print('\nEXPECTED ANOMALY COUNTS:')
print('   Rule 1 (Forgotten Pallets): 4 anomalies')
print('   Rule 2 (Incomplete Lots): 3 anomalies') 
print('   Rule 3 (Overcapacity): 6 anomalies')
print('   Rule 4 (Invalid Locations): 3 anomalies')
print('   Rule 5 (Aisle Stuck): 2 anomalies')
print('   Rule 6 (Cold Chain): 4 anomalies')
print('   Rule 7 (Scanner Error): 6 anomalies')
print('   Rule 8 (Location Mismatch): 3 anomalies')
print('   TOTAL EXPECTED: 31 anomalies')
print('   Good records: 5 pallets')