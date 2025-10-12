"""
Generate Test Excel Files for Date Parser Testing

Creates 6 different test files with various date formats to validate
the smart date parser implementation.

Run: python generate_date_test_files.py
"""

import pandas as pd
from datetime import datetime, timedelta
import os

# Create output directory
output_dir = os.path.join(os.path.dirname(__file__), '..', 'test_files')
os.makedirs(output_dir, exist_ok=True)

print("="*70)
print("GENERATING DATE PARSER TEST FILES")
print("="*70)

# ============================================================================
# Test 1: Excel Serial Numbers (Most Common Format)
# ============================================================================
print("\n1. Creating Excel Serial Number test file...")
base_date = datetime(2025, 1, 9, 14, 40, 3)
excel_serials = []
for i in range(20):
    date = base_date + timedelta(days=i, hours=i*2)
    # Convert to Excel serial: days since 1899-12-30
    delta = date - datetime(1899, 12, 30)
    serial = delta.days + (delta.seconds / 86400)
    excel_serials.append(serial)

df_excel = pd.DataFrame({
    'Pallet_ID': [f'PLT{1000+i}' for i in range(20)],
    'Location': [f'A-01-{i+1:02d}-A' for i in range(20)],
    'Description': ['Product A'] * 10 + ['Product B'] * 10,
    'Created': excel_serials,
    'Quantity': [10 + i for i in range(20)],
    'Receipt_Number': [f'RCV{2000+i}' for i in range(20)]
})
excel_path = os.path.join(output_dir, 'test_excel_serial.xlsx')
df_excel.to_excel(excel_path, index=False)
print(f"   ✓ Created: {excel_path}")
print(f"   Sample dates: {excel_serials[:3]}")

# ============================================================================
# Test 2: ISO Format (YYYY-MM-DD HH:MM:SS)
# ============================================================================
print("\n2. Creating ISO Format test file...")
iso_dates = []
for i in range(20):
    date = base_date + timedelta(days=i, hours=i*2)
    iso_dates.append(date.strftime('%Y-%m-%d %H:%M:%S'))

df_iso = pd.DataFrame({
    'Pallet_ID': [f'PLT{2000+i}' for i in range(20)],
    'Location': [f'B-01-{i+1:02d}-A' for i in range(20)],
    'Description': ['Product C'] * 10 + ['Product D'] * 10,
    'Created': iso_dates,
    'Quantity': [15 + i for i in range(20)],
    'Receipt_Number': [f'RCV{3000+i}' for i in range(20)]
})
iso_path = os.path.join(output_dir, 'test_iso_format.xlsx')
df_iso.to_excel(iso_path, index=False)
print(f"   ✓ Created: {iso_path}")
print(f"   Sample dates: {iso_dates[:3]}")

# ============================================================================
# Test 3: US Slash Format (MM/DD/YYYY)
# ============================================================================
print("\n3. Creating US Slash Format test file...")
us_dates = []
for i in range(20):
    date = base_date + timedelta(days=i)
    # Use MM/DD/YYYY format - include dates with day >12 to prove US format
    us_dates.append(date.strftime('%m/%d/%Y'))

df_us = pd.DataFrame({
    'Pallet_ID': [f'PLT{3000+i}' for i in range(20)],
    'Location': [f'C-01-{i+1:02d}-A' for i in range(20)],
    'Description': ['Product E'] * 10 + ['Product F'] * 10,
    'Created': us_dates,
    'Quantity': [20 + i for i in range(20)],
    'Receipt_Number': [f'RCV{4000+i}' for i in range(20)]
})
us_path = os.path.join(output_dir, 'test_us_slash.xlsx')
df_us.to_excel(us_path, index=False)
print(f"   ✓ Created: {us_path}")
print(f"   Sample dates: {us_dates[:3]}")

# ============================================================================
# Test 4: EU Slash Format (DD/MM/YYYY)
# ============================================================================
print("\n4. Creating EU Slash Format test file...")
eu_dates = []
for i in range(20):
    date = base_date + timedelta(days=i)
    # Use DD/MM/YYYY format - include dates with day >12 to prove EU format
    eu_dates.append(date.strftime('%d/%m/%Y'))

df_eu = pd.DataFrame({
    'Pallet_ID': [f'PLT{4000+i}' for i in range(20)],
    'Location': [f'D-01-{i+1:02d}-A' for i in range(20)],
    'Description': ['Product G'] * 10 + ['Product H'] * 10,
    'Created': eu_dates,
    'Quantity': [25 + i for i in range(20)],
    'Receipt_Number': [f'RCV{5000+i}' for i in range(20)]
})
eu_path = os.path.join(output_dir, 'test_eu_slash.xlsx')
df_eu.to_excel(eu_path, index=False)
print(f"   ✓ Created: {eu_path}")
print(f"   Sample dates: {eu_dates[:3]}")

# ============================================================================
# Test 5: Unix Timestamp Format (YYYYMMDDHHMMSS)
# ============================================================================
print("\n5. Creating Unix Timestamp test file...")
unix_dates = []
for i in range(20):
    date = base_date + timedelta(days=i, hours=i*2)
    unix_dates.append(date.strftime('%Y%m%d%H%M%S'))

df_unix = pd.DataFrame({
    'Pallet_ID': [f'PLT{5000+i}' for i in range(20)],
    'Location': [f'E-01-{i+1:02d}-A' for i in range(20)],
    'Description': ['Product I'] * 10 + ['Product J'] * 10,
    'Created': unix_dates,
    'Quantity': [30 + i for i in range(20)],
    'Receipt_Number': [f'RCV{6000+i}' for i in range(20)]
})
unix_path = os.path.join(output_dir, 'test_unix_timestamp.xlsx')
df_unix.to_excel(unix_path, index=False)
print(f"   ✓ Created: {unix_path}")
print(f"   Sample dates: {unix_dates[:3]}")

# ============================================================================
# Test 6: Mixed Formats (Stress Test)
# ============================================================================
print("\n6. Creating Mixed Formats test file...")
mixed_dates = []
for i in range(20):
    date = base_date + timedelta(days=i)
    # Mix different formats
    if i % 5 == 0:
        # Excel serial
        delta = date - datetime(1899, 12, 30)
        mixed_dates.append(delta.days + (delta.seconds / 86400))
    elif i % 5 == 1:
        # ISO format
        mixed_dates.append(date.strftime('%Y-%m-%d %H:%M:%S'))
    elif i % 5 == 2:
        # US slash
        mixed_dates.append(date.strftime('%m/%d/%Y'))
    elif i % 5 == 3:
        # EU slash
        mixed_dates.append(date.strftime('%d/%m/%Y'))
    else:
        # Unix timestamp
        mixed_dates.append(date.strftime('%Y%m%d%H%M%S'))

df_mixed = pd.DataFrame({
    'Pallet_ID': [f'PLT{6000+i}' for i in range(20)],
    'Location': [f'F-01-{i+1:02d}-A' for i in range(20)],
    'Description': ['Product K'] * 10 + ['Product L'] * 10,
    'Created': mixed_dates,
    'Quantity': [35 + i for i in range(20)],
    'Receipt_Number': [f'RCV{7000+i}' for i in range(20)]
})
mixed_path = os.path.join(output_dir, 'test_mixed_formats.xlsx')
df_mixed.to_excel(mixed_path, index=False)
print(f"   ✓ Created: {mixed_path}")
print(f"   Sample dates (mixed): {mixed_dates[:5]}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*70)
print("TEST FILES GENERATED SUCCESSFULLY")
print("="*70)
print(f"\nLocation: {output_dir}")
print("\nFiles created:")
print(f"  1. test_excel_serial.xlsx      - Excel serial numbers (45666.6111)")
print(f"  2. test_iso_format.xlsx        - ISO dates (2025-01-09 14:40:03)")
print(f"  3. test_us_slash.xlsx          - US format (1/9/2025)")
print(f"  4. test_eu_slash.xlsx          - EU format (09/01/2025)")
print(f"  5. test_unix_timestamp.xlsx    - Unix timestamps (20250109144003)")
print(f"  6. test_mixed_formats.xlsx     - Mixed formats (stress test)")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)
print("\n1. Start the backend server:")
print("   cd backend && python run_server.py")
print("\n2. Start the frontend:")
print("   cd frontend && npm run dev")
print("\n3. Upload test files at:")
print("   http://localhost:3000/dashboard")
print("\n4. Check for Date Format Detection card on column mapping page")
print("\n5. Verify each format is correctly detected with high confidence")
print("\nSee DATE_PARSER_TESTING_GUIDE.md for detailed testing instructions.")
print("="*70)
