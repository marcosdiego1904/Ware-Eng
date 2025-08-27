import pandas as pd

# Load and preview the corrected data
df = pd.read_excel('inventoryreport_corrected.xlsx')

print("CORRECTED DATA VERIFICATION:")
print("="*70)
print(f"Total Records: {len(df)}")
print(f"Columns: {list(df.columns)}")

print("\nSample location codes (should be in format 0X-Y-ZZZ-W):")
sample_locations = df['Location_Code'].unique()[:20]
for loc in sample_locations:
    print(f"  {loc}")

print(f"\nTotal unique locations: {len(df['Location_Code'].unique())}")

# Check for specific anomalies
print("\nANOMALY VERIFICATION:")
print("-" * 30)

# Check for invalid location anomalies
invalid_locs = df[df['Location_Code'].str.contains('INVALID|UNKN|4A|01A|--', regex=True, na=False)]
print(f"Invalid location anomalies found: {len(invalid_locs)}")

# Check for duplicate pallet IDs
duplicate_pallets = df[df.duplicated(['Pallet_ID'], keep=False)]
print(f"Duplicate pallet ID anomalies found: {len(duplicate_pallets)}")

# Check for temperature sensitive products
temp_products = df[df['Product_Code'].str.contains('FROZEN|REFRIGERATED', regex=True, na=False)]
print(f"Temperature sensitive products found: {len(temp_products)}")

# Check for special area locations
special_areas = df[df['Location_Code'].str.contains('RECV-|STAGE-|DOCK-|AISLE-', regex=True, na=False)]
print(f"Special area locations found: {len(special_areas)}")

print(f"\nFile saved as: inventoryreport_corrected.xlsx")
print("Ready for WMS rule engine testing!")