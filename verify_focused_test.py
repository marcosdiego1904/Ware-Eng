import pandas as pd

df = pd.read_excel('inventoryreport.xlsx')

print('File verification:')
print(f'Total rows: {len(df)}')
print(f'Columns: {df.columns.tolist()}')
print()

print('Lot distribution:')
print(df['lot_number'].value_counts())
print()

print('Location distribution (overcapacity targets):')
overcap_locs = ['1-01-01A', '2-01-01A', '3-01-01A', 'STAGE-01', 'DOCK-01', 'RECV-01', 'AISLE-01']
for loc in overcap_locs:
    count = (df['location'] == loc).sum()
    print(f'{loc}: {count} pallets')