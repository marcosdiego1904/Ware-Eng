#!/usr/bin/env python3
"""
FakeCorp Distribution Center - Small Test Inventory Report
Creates minimal inventory data for quick testing
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_small_inventory():
    """Create small test inventory with key scenarios"""
    
    inventory_data = []
    
    # === SCENARIO 1: STAGNANT PALLETS (4 pallets) ===
    for i in range(4):
        inventory_data.append({
            'Pallet ID': f'STAG{i:03d}',
            'Location': 'RECV-DOCK',
            'Receipt Number': f'REC{i}',
            'Description': 'Bosch Brake Pads - BRAKE',
            'Creation Date': (datetime.now() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 25,
            'Weight': 800
        })
    
    # === SCENARIO 2: OVERCAPACITY (3 pallets in same location) ===
    for i in range(3):
        inventory_data.append({
            'Pallet ID': f'OVER{i:03d}',
            'Location': '01-01-001-A',  # Same location
            'Receipt Number': f'OVER{i}',
            'Description': 'OEM Oil Filter - ENGINE',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 30,
            'Weight': 600
        })
    
    # === SCENARIO 3: LOT STRAGGLERS (6 stored + 2 in receiving) ===
    lot_id = 'LOT001'
    
    # 6 stored pallets
    for i in range(6):
        inventory_data.append({
            'Pallet ID': f'LOT{i:03d}',
            'Location': f'01-01-{i+10:03d}-A',
            'Receipt Number': lot_id,
            'Description': 'Continental Timing Belt - ENGINE',
            'Creation Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 40,
            'Weight': 750
        })
    
    # 2 stragglers in receiving
    for i in range(2):
        inventory_data.append({
            'Pallet ID': f'STR{i:03d}',
            'Location': 'RECV-DOCK',
            'Receipt Number': lot_id,
            'Description': 'Continental Timing Belt - ENGINE',
            'Creation Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 40,
            'Weight': 750
        })
    
    # === SCENARIO 4: TEMPERATURE VIOLATIONS (3 pallets) ===
    for i in range(3):
        inventory_data.append({
            'Pallet ID': f'TEMP{i:03d}',
            'Location': f'02-01-{i+5:03d}-B',
            'Receipt Number': f'TEMP{i}',
            'Description': 'FROZEN Rubber Seals - BODY',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 20,
            'Weight': 400
        })
    
    # === SCENARIO 5: LOCATION ERRORS (3 pallets) ===
    location_errors = [
        {'id': 'MISS001', 'location': '', 'desc': 'Missing Location'},
        {'id': 'INV001', 'location': 'INVALID-XYZ', 'desc': 'Invalid Location'},
        {'id': 'INV002', 'location': '99-99-999-Z', 'desc': 'Non-existent Location'}
    ]
    
    for error in location_errors:
        inventory_data.append({
            'Pallet ID': error['id'],
            'Location': error['location'],
            'Receipt Number': error['id'],
            'Description': f'Denso Alternator - ELECTRICAL ({error["desc"]})',
            'Creation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 15,
            'Weight': 500
        })
    
    # === NORMAL INVENTORY (15 pallets) ===
    products = [
        'Bosch Spark Plugs - ENGINE',
        'Valeo Clutch Kit - TRANSMISSION', 
        'Continental Brake Discs - BRAKE',
        'OEM Shock Absorber - SUSPENSION',
        'Denso Battery - ELECTRICAL'
    ]
    
    for i in range(15):
        inventory_data.append({
            'Pallet ID': f'NORM{i:03d}',
            'Location': f'0{(i%2)+1}-0{(i%2)+1}-{i+20:03d}-{chr(65+(i%3))}',  # Spread across locations
            'Receipt Number': f'NORM{i//5}',
            'Description': products[i % len(products)],
            'Creation Date': (datetime.now() - timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': random.randint(20, 50),
            'Weight': random.randint(500, 1000)
        })
    
    # === SPECIAL AREAS (3 pallets) ===
    special_pallets = [
        {'location': 'QC-STAGE', 'desc': 'Quality Check'},
        {'location': 'SHIP-DOCK', 'desc': 'Ready to Ship'},
        {'location': 'RECV-DOCK', 'desc': 'Just Arrived'}
    ]
    
    for i, special in enumerate(special_pallets):
        inventory_data.append({
            'Pallet ID': f'SPEC{i:03d}',
            'Location': special['location'],
            'Receipt Number': f'SPEC{i}',
            'Description': f'Bosch ECU - ELECTRICAL ({special["desc"]})',
            'Creation Date': (datetime.now() - timedelta(hours=i+1)).strftime('%Y-%m-%d %H:%M:%S'),
            'Quantity': 25,
            'Weight': 600
        })
    
    return inventory_data

def main():
    """Generate and save the small inventory report"""
    print("FakeCorp Distribution Center - Small Test Inventory")
    print("=" * 50)
    
    print("Generating small test inventory...")
    inventory_data = create_small_inventory()
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Save to Excel file
    output_file = 'FakeCorp_Small_Inventory.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\nSmall inventory report generated!")
    print(f"File: {output_file}")
    print(f"Total pallets: {len(inventory_data)}")
    
    # Summary
    print(f"\nTest Scenarios (Small Scale):")
    print(f"   - Stagnant Pallets: 4 (10+ hours in receiving)")
    print(f"   - Overcapacity: 3 (same location)")  
    print(f"   - Lot Stragglers: 2 (8 total in lot)")
    print(f"   - Temperature Violations: 3 (frozen in general)")
    print(f"   - Location Errors: 3 (missing/invalid)")
    print(f"   - Normal Inventory: 15 (baseline)")
    print(f"   - Special Areas: 3 (staging/shipping)")
    
    print(f"\nPerfect for quick testing - upload {output_file} to your app!")

if __name__ == "__main__":
    main()