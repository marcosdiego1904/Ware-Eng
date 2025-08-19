import pandas as pd

# Create test inventory data with USER-FRIENDLY location formats
data = [
    # Using the original format that users naturally expect
    ['PALLET001', '001A01', 'Test Product A', 'REC2024001', '2025-08-19 15:00:00', 'GENERAL', 'AMBIENT'],
    ['PALLET002', '001B02', 'Test Product B', 'REC2024001', '2025-08-19 15:00:00', 'GENERAL', 'AMBIENT'], 
    ['PALLET003', '015C03', 'Test Product C', 'REC2024001', '2025-08-19 15:00:00', 'GENERAL', 'AMBIENT'],
    
    # Mixed formats that users might use
    ['PALLET004', 'A1-005', 'Test Product D', 'REC2024002', '2025-08-19 15:00:00', 'GENERAL', 'AMBIENT'],
    ['PALLET005', '5A10', 'Test Product E', 'REC2024002', '2025-08-19 15:00:00', 'GENERAL', 'AMBIENT'],
    
    # Special areas - should work as-is  
    ['PALLET006', 'RECV-01', 'Receiving Product', 'REC2024003', '2025-08-19 15:00:00', 'GENERAL', 'AMBIENT'],
    ['PALLET007', 'AISLE-01', 'Transit Product', 'REC2024003', '2025-08-19 15:00:00', 'GENERAL', 'AMBIENT'],
]

columns = ['Pallet ID', 'Location', 'Description', 'Receipt Number', 'Creation Date', 'Product Type', 'Temperature Requirement']
df = pd.DataFrame(data, columns=columns)
df.to_excel('inventoryreport_user_friendly.xlsx', index=False)

print('USER-FRIENDLY test file created!')
print(f'Total records: {len(df)}')
print('')
print('Location Formats Used (what users naturally expect):')
print('- 001A01 -> should convert to 01-01-001A')
print('- 001B02 -> should convert to 01-02-001B') 
print('- 015C03 -> should convert to 01-03-015C')
print('- A1-005 -> should convert to 01-01-005A')
print('- 5A10   -> should convert to 01-10-005A')
print('- RECV-01 -> should stay as RECV-01')
print('- AISLE-01 -> should stay as AISLE-01')
print('')
print('File: inventoryreport_user_friendly.xlsx')