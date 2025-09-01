import pandas as pd

df = pd.read_excel('test5.xlsx')

print("## Sample Dataset (test5.xlsx) - First 15 Rows")
print()
print("| pallet_id | receipt_number | description | location | creation_date |")
print("|-----------|---------------|-------------|----------|---------------|")

for idx, row in df.head(15).iterrows():
    print(f"| {row['pallet_id']} | {row['receipt_number']} | {row['description']} | {row['location']} | {row['creation_date']} |")