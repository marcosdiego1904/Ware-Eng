import pandas as pd

# Create test inventory data with CORRECT database location formats
data = [
    # STAGNANT_PALLETS - Items >6 hours old in RECEIVING
    ['OLD001', 'RECV-01', 'Frozen Pizza Boxes', 'REC2024001', '2025-08-18 02:00:00', 'FOOD', 'FROZEN'],
    ['OLD002', 'RECV-01', 'Dairy Products - Milk', 'REC2024001', '2025-08-18 02:00:00', 'FOOD', 'REFRIGERATED'],
    ['OLD003', 'RECV-02', 'Canned Goods - Tomatoes', 'REC2024001', '2025-08-18 02:00:00', 'FOOD', 'AMBIENT'],
    ['STALE001', 'RECV-01', 'Office Supplies', 'REC2024002', '2025-08-18 08:00:00', 'GENERAL', 'AMBIENT'],
    ['STALE002', 'RECV-02', 'Cleaning Chemicals', 'REC2024002', '2025-08-18 08:00:00', 'CHEMICAL', 'AMBIENT'],
    
    # UNCOORDINATED_LOTS - 1 pallet left in RECEIVING while others moved to STORAGE
    ['LOT001', 'RECV-01', 'Electronics - Tablets', 'REC2024003', '2025-08-19 06:00:00', 'ELECTRONICS', 'AMBIENT'],
    ['LOT002', '01-01-005A', 'Electronics - Tablets', 'REC2024003', '2025-08-19 06:00:00', 'ELECTRONICS', 'AMBIENT'],
    ['LOT003', '01-01-005B', 'Electronics - Tablets', 'REC2024003', '2025-08-19 06:00:00', 'ELECTRONICS', 'AMBIENT'],
    ['LOT004', '01-01-005C', 'Electronics - Tablets', 'REC2024003', '2025-08-19 06:00:00', 'ELECTRONICS', 'AMBIENT'],
    ['LOT005', '01-01-006A', 'Electronics - Tablets', 'REC2024003', '2025-08-19 06:00:00', 'ELECTRONICS', 'AMBIENT'],
    
    # OVERCAPACITY - RECEIVING locations (test with 12 pallets, capacity should be 10)
    ['OVER1', 'RECV-01', 'Paper Products 1', 'REC2024004', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['OVER2', 'RECV-01', 'Paper Products 2', 'REC2024004', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['OVER3', 'RECV-01', 'Paper Products 3', 'REC2024004', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['OVER4', 'RECV-01', 'Paper Products 4', 'REC2024004', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['OVER5', 'RECV-01', 'Paper Products 5', 'REC2024004', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['OVER6', 'RECV-01', 'Paper Products 6', 'REC2024004', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['OVER7', 'RECV-01', 'Paper Products 7', 'REC2024004', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    
    # OVERCAPACITY - STORAGE locations (capacity=1 each) 
    ['RACK1', '01-01-001A', 'Rack Overload Product A', 'REC2024011', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['RACK2', '01-01-001A', 'Rack Overload Product B', 'REC2024011', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['RACK3', '01-01-001A', 'Rack Overload Product C', 'REC2024011', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    
    ['RACK4', '01-01-002B', 'Second Rack Overload A', 'REC2024012', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['RACK5', '01-01-002B', 'Second Rack Overload B', 'REC2024012', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    
    ['RACK6', '01-01-003C', 'Third Rack Overload A', 'REC2024013', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['RACK7', '01-01-003C', 'Third Rack Overload B', 'REC2024013', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['RACK8', '01-01-003C', 'Third Rack Overload C', 'REC2024013', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    ['RACK9', '01-01-003C', 'Third Rack Overload D', 'REC2024013', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
    
    # INVALID_LOCATION - Non-existent locations
    ['INVALID1', 'BADLOC001', 'Invalid Location Product', 'REC2024005', '2025-08-19 11:00:00', 'GENERAL', 'AMBIENT'],
    ['INVALID2', 'ZONE-999', 'Non-existent Zone', 'REC2024005', '2025-08-19 11:00:00', 'GENERAL', 'AMBIENT'],
    ['INVALID3', '', 'Missing Location Product', 'REC2024005', '2025-08-19 11:00:00', 'GENERAL', 'AMBIENT'],
    
    # LOCATION_SPECIFIC_STAGNANT - Items >4 hours in AISLE locations  
    ['AISLE1', 'AISLE-01', 'Stuck in Aisle Product', 'REC2024006', '2025-08-18 09:00:00', 'GENERAL', 'AMBIENT'],
    ['AISLE2', 'AISLE-02', 'Another Stuck Product', 'REC2024006', '2025-08-18 09:00:00', 'GENERAL', 'AMBIENT'],
    
    # TEMPERATURE_ZONE_MISMATCH - Frozen/Refrigerated items in wrong zones
    ['TEMP1', '01-01-010A', 'Frozen Ice Cream', 'REC2024007', '2025-08-19 12:00:00', 'FOOD', 'FROZEN'],
    ['TEMP2', '01-01-010B', 'Refrigerated Meat', 'REC2024007', '2025-08-19 12:00:00', 'FOOD', 'REFRIGERATED'], 
    ['TEMP3', 'AISLE-01', 'Frozen Vegetables', 'REC2024007', '2025-08-19 12:00:00', 'FOOD', 'FROZEN'],
    
    # DATA_INTEGRITY - Scanner errors
    ['DUP001', '01-01-020A', 'Duplicate Scan Test', 'REC2024008', '2025-08-19 13:00:00', 'GENERAL', 'AMBIENT'],
    ['DUP001', '01-01-020B', 'Duplicate Scan Test', 'REC2024008', '2025-08-19 13:00:00', 'GENERAL', 'AMBIENT'],
    ['BADCHAR', 'LOC@#$%', 'Invalid Character Location', 'REC2024009', '2025-08-19 14:00:00', 'GENERAL', 'AMBIENT'],
    ['TOOLONG', 'VERYLONGLOCATIONCODETHATEXCEEDSLIMITS123456', 'Location Too Long', 'REC2024009', '2025-08-19 14:00:00', 'GENERAL', 'AMBIENT'],
    
    # Normal items
    ['NORMAL1', '01-01-030A', 'Normal Product 1', 'REC2024010', '2025-08-19 15:00:00', 'GENERAL', 'AMBIENT'],
    ['NORMAL2', '01-01-030B', 'Normal Product 2', 'REC2024010', '2025-08-19 15:00:00', 'GENERAL', 'AMBIENT'],
    ['NORMAL3', '01-01-030C', 'Normal Product 3', 'REC2024010', '2025-08-19 15:00:00', 'GENERAL', 'AMBIENT'],
]

columns = ['Pallet ID', 'Location', 'Description', 'Receipt Number', 'Creation Date', 'Product Type', 'Temperature Requirement']
df = pd.DataFrame(data, columns=columns)
df.to_excel('inventoryreport_corrected.xlsx', index=False)

print('CORRECTED test file created!')
print(f'Total records: {len(df)}')
print()
print('KEY CHANGES:')
print('- RECV-01: 12 pallets (should trigger overcapacity if capacity=10)')
print('- Storage locations: 01-01-001A (3 pallets), 01-01-002B (2 pallets), 01-01-003C (4 pallets)')
print('- All locations now match database format (01-01-XXXL)')
print('- Electronics lot: 1 in RECEIVING, 4 in STORAGE (should trigger uncoordinated lots)')
print()
print('File: inventoryreport_corrected.xlsx')