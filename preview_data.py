import pandas as pd

# Load and preview the generated data
df = pd.read_excel('inventoryreport.xlsx')

print("DATA PREVIEW:")
print("="*70)
print(f"Total Records: {len(df)}")
print(f"Columns: {list(df.columns)}")
print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nSample of location codes:")
print(df['Location_Code'].unique()[:15])