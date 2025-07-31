
import pandas as pd
from datetime import datetime, timedelta

def generate_test_data():
    """
    Generates a pandas DataFrame with inventory data designed to trigger specific warehouse rules.
    """
    now = datetime.now()

    data = []

    # --- Rule 1: Forgotten Pallets (Stagnant in Receiving) ---
    # 3 pallets in DOCK-01 for over 2 hours
    for i in range(1, 4):
        data.append({
            'pallet_id': f'STAGNANT-{i:03d}',
            'location': 'DOCK-01',
            'creation_date': now - timedelta(hours=3),
            'receipt_number': 'LOT-A',
            'description': 'Electronics - Awaiting Storage'
        })

    # --- Rule 2: Incomplete Lots (Stragglers) ---
    # LOT-B has 10 pallets total. 8 are stored, 2 are stragglers. (80% completion > 75% threshold)
    # 8 stored pallets (should NOT be flagged)
    for i in range(1, 9):
        data.append({
            'pallet_id': f'LOT-B-STORED-{i:03d}',
            'location': f'STORE-A{i}',
            'creation_date': now - timedelta(days=1),
            'receipt_number': 'LOT-B',
            'description': 'Apparel - Stored'
        })
    # 2 straggler pallets (SHOULD be flagged)
    for i in range(1, 3):
        data.append({
            'pallet_id': f'LOT-B-STRAGGLER-{i:03d}',
            'location': 'DOCK-02',
            'creation_date': now - timedelta(days=2),
            'receipt_number': 'LOT-B',
            'description': 'Apparel - Straggler'
        })

    # --- Rule 3: Overcapacity ---
    # DOCK-03 has a capacity of 5. We will place 6 pallets here.
    # All 6 pallets SHOULD be flagged.
    for i in range(1, 7):
        data.append({
            'pallet_id': f'OVERCAP-{i:03d}',
            'location': 'DOCK-03',
            'creation_date': now - timedelta(minutes=30),
            'receipt_number': 'LOT-C',
            'description': 'General Goods - Overcapacity'
        })

    # --- Rule 4: Clear Blocked Aisles ---
    # 2 pallets in AISLETEST for over 2 hours.
    # Both SHOULD be flagged.
    for i in range(1, 3):
        data.append({
            'pallet_id': f'AISLE-BLOCKER-{i:03d}',
            'location': 'AISLETEST',
            'creation_date': now - timedelta(hours=4),
            'receipt_number': 'LOT-D',
            'description': 'Empty Pallets - Blocking Aisle'
        })

    # --- "Normal" Data (Should NOT trigger any rules) ---
    # 50 pallets that are fresh and in valid, non-congested locations.
    for i in range(1, 51):
        data.append({
            'pallet_id': f'NORMAL-{i:03d}',
            'location': f'STORE-B{i}',
            'creation_date': now - timedelta(minutes=i),
            'receipt_number': 'LOT-E',
            'description': 'Standard Inventory'
        })
    
    # --- Another normal lot, not yet complete ---
    # 5 pallets in receiving, 2 stored. (28% completion < 75% threshold)
    for i in range(1, 6):
        data.append({
            'pallet_id': f'LOT-F-RECEIVING-{i:03d}',
            'location': 'DOCK-04',
            'creation_date': now - timedelta(minutes=10),
            'receipt_number': 'LOT-F',
            'description': 'New Arrival - Processing'
        })
    for i in range(1, 3):
        data.append({
            'pallet_id': f'LOT-F-STORED-{i:03d}',
            'location': f'STORE-C{i}',
            'creation_date': now - timedelta(minutes=5),
            'receipt_number': 'LOT-F',
            'description': 'New Arrival - Stored'
        })


    df = pd.DataFrame(data)
    
    # Ensure correct datetime format for Excel
    df['creation_date'] = df['creation_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return df

if __name__ == "__main__":
    inventory_df = generate_test_data()
    
    # Save to CSV first, then convert
    csv_path = 'C:/Users/juanb/Documents/Diego/Projects/ware2/backend/data/inventory_report_for_testing.csv'
    excel_path = 'C:/Users/juanb/Documents/Diego/Projects/ware2/backend/data/inventory_report_for_testing.xlsx'
    
    inventory_df.to_csv(csv_path, index=False)
    
    # Convert CSV to Excel
    inventory_df.to_excel(excel_path, index=False, engine='openpyxl')
    
    print(f"Successfully generated test data at {excel_path}")
    print(f"Total records: {len(inventory_df)}")

