import pandas as pd
from datetime import datetime, timedelta

def create_comprehensive_test_file():
    """
    Generates a comprehensive Excel file for testing all 10 AI-generated rule scenarios.
    The file contains two sheets: 'inventory_data' and 'location_master'.
    """
    now = datetime.now()

    # --- Location Master Data ---
    # Defines all valid locations, their types, zones, capacities, and product restrictions.
    location_master_data = {
        'code': [
            'DOCK-A1', 'DOCK-A2', 'STAGE-B2', 'AISLE-G5', 'AISLE-C4', 
            'STOR-A1', 'STOR-A2', 'STOR-A3', 'STOR-A4', 'STOR-A5', 
            'STOR-B1', 'STOR-B2', 'STOR-B3', 'STOR-B4', 'FREEZER-A1',
            'HAZMAT-A1', 'CHEM-STORE-A1', 'AISLE-A1', 'RECEIVING-01', 'STAGING-01'
        ],
        'type': [
            'RECEIVING', 'RECEIVING', 'STAGING', 'AISLE', 'AISLE',
            'FINAL', 'FINAL', 'FINAL', 'FINAL', 'FINAL',
            'FINAL', 'FINAL', 'FINAL', 'FINAL', 'FINAL',
            'HAZMAT', 'CHEMICAL', 'AISLE', 'RECEIVING', 'STAGING'
        ],
        'zone': [
            'DOCK', 'DOCK', 'STAGING', 'AMBIENT', 'AMBIENT',
            'STORAGE', 'STORAGE', 'STORAGE', 'STORAGE', 'STORAGE',
            'STORAGE', 'STORAGE', 'STORAGE', 'STORAGE', 'FREEZER',
            'HAZMAT', 'CHEMICAL', 'AMBIENT', 'DOCK', 'STAGING'
        ],
        'capacity': [10, 10, 5, 20, 20, 1, 1, 1, 1, 1, 1, 1, 1, 1, 50, 2, 10, 20, 10, 5],
        'allowed_products': [
            '*', '* ', '*', '*', '*', '* ', '*', '*', '*', '*',
            '*', '*', '*', '*', '*FROZEN*', '*HAZMAT*', '*FLAMMABLE*',
            '*', '* ', '*'
        ]
    }
    location_master_df = pd.DataFrame(location_master_data)

    # --- Inventory Data ---
    # Contains pallet information designed to trigger specific rules.
    inventory_data = {
        'pallet_id': [
            # Rule 1: Stagnant in Receiving (>8 hours)
            'R001', 'R002_NORMAL',
            # Rule 2: High-Value Stagnant (>2 hours)
            'HV001', 'HV002_NORMAL',
            # Rule 3: Temp Mismatch
            'FROZ01', 'FROZ02_NORMAL',
            # Rule 4: Aisle Blocker (>1 hour)
            'AISLE-BLOCKER', 'AISLE-NORMAL',
            # Rule 5: Uncoordinated Lots
            'STRAGGLER-01', 'LOT2-A', 'LOT2-B', 'LOT2-C', 'LOT2-D', 'LOT2-E',
            'LOT2-F', 'LOT2-G', 'LOT2-H', 'LOT2-I',
            # Rule 6: Invalid Location
            'BAD-LOC-01',
            # Rule 7: Overcapacity
            'HAZ01', 'HAZ02', 'HAZ03',
            # Rule 8: Data Integrity
            'DUP-SCAN-01', 'DUP-SCAN-01', 'IMPOSSIBLE-LOC',
            # Rule 9: Missing Location
            'LOST-01',
            # Rule 10: Product Incompatibility
            'CHEM-OXIDIZER', 'CHEM-FLAMMABLE_NORMAL',
            # Normal Data
            'NORMAL-PALLET-01', 'NORMAL-PALLET-02'
        ],
        'description': [
            # Rule 1
            'General Goods', 'General Goods',
            # Rule 2
            'Electronics - Laptops', 'Electronics - Keyboards',
            # Rule 3
            'FROZEN Peas', 'FROZEN Corn',
            # Rule 4
            'Canned Goods', 'Canned Goods',
            # Rule 5
            'Acme Corp Widgets', 'Acme Corp Widgets', 'Acme Corp Widgets', 'Acme Corp Widgets', 'Acme Corp Widgets',
            'Acme Corp Widgets', 'Acme Corp Widgets', 'Acme Corp Widgets', 'Acme Corp Widgets', 'Acme Corp Widgets',
            # Rule 6
            'Sporting Goods',
            # Rule 7
            'HAZMAT-A', 'HAZMAT-B', 'HAZMAT-C',
            # Rule 8
            'Duplicate Scan Pallet', 'Duplicate Scan Pallet', 'Impossible Location Pallet',
            # Rule 9
            'Lost Pallet',
            # Rule 10
            'Oxidizing Agent', 'Flammable Liquid',
            # Normal
            'Dry Goods', 'Beverages'
        ],
        'location': [
            # Rule 1
            'RECEIVING-01', 'RECEIVING-01',
            # Rule 2
            'STAGING-01', 'STAGING-01',
            # Rule 3
            'AISLE-G5', 'FREEZER-A1',
            # Rule 4
            'AISLE-C4', 'AISLE-A1',
            # Rule 5
            'RECEIVING-01', 'STOR-A1', 'STOR-A2', 'STOR-A3', 'STOR-A4', 'STOR-A5',
            'STOR-B1', 'STOR-B2', 'STOR-B3', 'STOR-B4',
            # Rule 6
            'AISLE-Z99',
            # Rule 7
            'HAZMAT-A1', 'HAZMAT-A1', 'HAZMAT-A1',
            # Rule 8
            'DOCK-A2', 'DOCK-A2', 'THIS-IS-WAY-TOO-LONG-FOR-A-LOCATION-CODE',
            # Rule 9
            None,
            # Rule 10
            'CHEM-STORE-A1', 'CHEM-STORE-A1',
            # Normal
            'STOR-A1', 'AISLE-A1'
        ],
        'creation_date': [
            # Rule 1
            now - timedelta(hours=9), now - timedelta(hours=1),
            # Rule 2
            now - timedelta(hours=3), now - timedelta(hours=1),
            # Rule 3
            now - timedelta(minutes=30), now - timedelta(minutes=30),
            # Rule 4
            now - timedelta(hours=2), now - timedelta(minutes=30),
            # Rule 5
            now - timedelta(days=1), now - timedelta(days=1), now - timedelta(days=1), now - timedelta(days=1), now - timedelta(days=1),
            now - timedelta(days=1), now - timedelta(days=1), now - timedelta(days=1), now - timedelta(days=1), now - timedelta(days=1),
            # Rule 6
            now - timedelta(hours=5),
            # Rule 7
            now - timedelta(hours=1), now - timedelta(hours=1), now - timedelta(hours=1),
            # Rule 8
            now - timedelta(minutes=10), now - timedelta(minutes=10), now - timedelta(minutes=5),
            # Rule 9
            now - timedelta(hours=6),
            # Rule 10
            now - timedelta(hours=2), now - timedelta(hours=2),
            # Normal
            now - timedelta(days=2), now - timedelta(hours=4)
        ],
        'receipt_number': [
            'LOT-A', 'LOT-A', 'LOT-B', 'LOT-B', 'LOT-C', 'LOT-C', 'LOT-D', 'LOT-D',
            'LOT-ACME-123', 'LOT-ACME-123', 'LOT-ACME-123', 'LOT-ACME-123', 'LOT-ACME-123', 'LOT-ACME-123',
            'LOT-ACME-123', 'LOT-ACME-123', 'LOT-ACME-123', 'LOT-ACME-123',
            'LOT-E',
            'LOT-F', 'LOT-F', 'LOT-F',
            'LOT-G',
            'LOT-H',
            'LOT-I', 'LOT-J',
            'LOT-K', 'LOT-L', 'LOT-M', 'LOT-N'
        ],
        'customer_id': [
            'CUST-001', 'CUST-001',
            'CUST-002', 'CUST-002',
            'CUST-003', 'CUST-003',
            'CUST-004', 'CUST-004',
            'ACME-CORP', 'ACME-CORP', 'ACME-CORP', 'ACME-CORP', 'ACME-CORP', 'ACME-CORP',
            'ACME-CORP', 'ACME-CORP', 'ACME-CORP', 'ACME-CORP',
            'CUST-005',
            'CUST-006', 'CUST-006', 'CUST-006',
            'CUST-007',
            'CUST-008',
            'CUST-009', 'CUST-010',
            'CUST-011', 'CUST-012', 'CUST-013', 'CUST-014'
        ]
    }
    inventory_df = pd.DataFrame(inventory_data)

    # --- Write to Excel ---
    file_path = 'C:/Users/juanb/Documents/Diego/Projects/ware2/backend/data/comprehensive_inventory_test.xlsx'
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        inventory_df.to_excel(writer, sheet_name='inventory_data', index=False)
        location_master_df.to_excel(writer, sheet_name='location_master', index=False)

    print(f"Successfully created test file at {file_path}")

if __name__ == '__main__':
    create_comprehensive_test_file()