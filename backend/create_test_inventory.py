#!/usr/bin/env python3
"""
Create comprehensive Excel inventory report to test special locations
"""

import pandas as pd
from datetime import datetime, timedelta

def create_test_inventory():
    # Current datetime for timestamp calculations
    now = datetime.now()
    
    # Test inventory data targeting specific rules
    test_inventory = []
    
    # Rule 1: "Forgotten Pallets Alert" - RECEIVING locations > 10 hours
    print("Creating forgotten pallets in RECEIVING locations...")
    forgotten_pallets = [
        {
            'Pallet ID': 'PALLET-FORGOTTEN-001',
            'Product Name': 'Test Product Alpha',
            'Location': 'RECV-01',
            'Quantity': 5,
            'Timestamp': (now - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-ALPHA-001',
            'Lot': 'LOT-2024-001',
            'Status': 'RECEIVING'
        },
        {
            'Pallet ID': 'PALLET-FORGOTTEN-002', 
            'Product Name': 'Test Product Beta',
            'Location': 'RECV-02',
            'Quantity': 8,
            'Timestamp': (now - timedelta(hours=15)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-BETA-002',
            'Lot': 'LOT-2024-002',
            'Status': 'RECEIVING'
        },
        {
            'Pallet ID': 'PALLET-FORGOTTEN-003',
            'Product Name': 'Test Product Gamma',
            'Location': 'RECV-03', 
            'Quantity': 1,
            'Timestamp': (now - timedelta(hours=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-GAMMA-003',
            'Lot': 'LOT-2024-003',
            'Status': 'RECEIVING'
        }
    ]
    test_inventory.extend(forgotten_pallets)
    
    # Rule 2: "Incomplete Lots Alert" - Most of lot stored, some still in RECEIVING
    print("Creating incomplete lots in RECEIVING...")
    incomplete_lot_data = [
        # Most of LOT-2024-100 already stored
        {
            'Pallet ID': 'PALLET-STORED-100A',
            'Product Name': 'Product Delta Complete', 
            'Location': '01-A01-A',  # Storage location
            'Quantity': 10,
            'Timestamp': (now - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-DELTA-100',
            'Lot': 'LOT-2024-100',
            'Status': 'STORED'
        },
        {
            'Pallet ID': 'PALLET-STORED-100B',
            'Product Name': 'Product Delta Complete',
            'Location': '01-A02-A',  # Storage location  
            'Quantity': 10,
            'Timestamp': (now - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-DELTA-100',
            'Lot': 'LOT-2024-100',
            'Status': 'STORED'
        },
        {
            'Pallet ID': 'PALLET-STORED-100C',
            'Product Name': 'Product Delta Complete',
            'Location': '01-A03-A',  # Storage location
            'Quantity': 10, 
            'Timestamp': (now - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-DELTA-100',
            'Lot': 'LOT-2024-100',
            'Status': 'STORED'
        },
        # But one pallet still stuck in RECEIVING (should trigger alert)
        {
            'Pallet ID': 'PALLET-INCOMPLETE-100D',
            'Product Name': 'Product Delta Complete',
            'Location': 'RECV-01',  # Still in receiving!
            'Quantity': 10,
            'Timestamp': (now - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-DELTA-100',
            'Lot': 'LOT-2024-100',
            'Status': 'RECEIVING'
        }
    ]
    test_inventory.extend(incomplete_lot_data)
    
    # Rule 3: "Overcapacity Alert" - Exceed location capacity
    print("Creating overcapacity situations...")
    overcapacity_data = [
        # RECV-03 has capacity 1, but we'll put 2 pallets there
        {
            'Pallet ID': 'PALLET-OVERCAP-001',
            'Product Name': 'Overcapacity Test Alpha',
            'Location': 'RECV-03',
            'Quantity': 1,
            'Timestamp': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-OVERCAP-001', 
            'Lot': 'LOT-2024-OVER-001',
            'Status': 'RECEIVING'
        },
        {
            'Pallet ID': 'PALLET-OVERCAP-002',
            'Product Name': 'Overcapacity Test Beta',
            'Location': 'RECV-03',  # Same location - should exceed capacity
            'Quantity': 1,
            'Timestamp': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-OVERCAP-002',
            'Lot': 'LOT-2024-OVER-002', 
            'Status': 'RECEIVING'
        },
        # DOCK-01 has capacity 2, put 3 pallets
        {
            'Pallet ID': 'PALLET-DOCK-OVER-001',
            'Product Name': 'Dock Overcap Alpha',
            'Location': 'DOCK-01',
            'Quantity': 1,
            'Timestamp': (now - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-DOCK-001',
            'Lot': 'LOT-2024-DOCK-001',
            'Status': 'SHIPPING'
        },
        {
            'Pallet ID': 'PALLET-DOCK-OVER-002', 
            'Product Name': 'Dock Overcap Beta',
            'Location': 'DOCK-01',
            'Quantity': 1,
            'Timestamp': (now - timedelta(minutes=25)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-DOCK-002',
            'Lot': 'LOT-2024-DOCK-002',
            'Status': 'SHIPPING'
        },
        {
            'Pallet ID': 'PALLET-DOCK-OVER-003',
            'Product Name': 'Dock Overcap Gamma', 
            'Location': 'DOCK-01',  # Third pallet - exceeds capacity of 2
            'Quantity': 1,
            'Timestamp': (now - timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-DOCK-003',
            'Lot': 'LOT-2024-DOCK-003',
            'Status': 'SHIPPING'
        }
    ]
    test_inventory.extend(overcapacity_data)
    
    # Rule 4: "Invalid Locations Alert" - Test with some invalid locations mixed in
    print("Creating invalid location entries...")
    invalid_location_data = [
        {
            'Pallet ID': 'PALLET-INVALID-001',
            'Product Name': 'Invalid Location Test',
            'Location': 'INVALID-LOCATION-X99',  # Invalid location
            'Quantity': 5,
            'Timestamp': (now - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-INVALID-001',
            'Lot': 'LOT-2024-INVALID-001',
            'Status': 'UNKNOWN'
        },
        {
            'Pallet ID': 'PALLET-INVALID-002',
            'Product Name': 'Another Invalid Test',
            'Location': 'NONEXISTENT-LOC',  # Another invalid location
            'Quantity': 3,
            'Timestamp': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-INVALID-002', 
            'Lot': 'LOT-2024-INVALID-002',
            'Status': 'UNKNOWN'
        }
    ]
    test_inventory.extend(invalid_location_data)
    
    # Rule 5: "AISLE Stuck Pallets" - Pallets stuck in AISLE locations > 4 hours
    print("Creating AISLE stuck pallets...")
    aisle_stuck_data = [
        {
            'Pallet ID': 'PALLET-AISLE-STUCK-001',
            'Product Name': 'Aisle Stuck Alpha',
            'Location': 'AISLE-01',
            'Quantity': 2,
            'Timestamp': (now - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-AISLE-001',
            'Lot': 'LOT-2024-AISLE-001',
            'Status': 'TRANSITIONAL'
        },
        {
            'Pallet ID': 'PALLET-AISLE-STUCK-002',
            'Product Name': 'Aisle Stuck Beta', 
            'Location': 'AISLE-02',
            'Quantity': 3,
            'Timestamp': (now - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-AISLE-002',
            'Lot': 'LOT-2024-AISLE-002', 
            'Status': 'TRANSITIONAL'
        },
        {
            'Pallet ID': 'PALLET-AISLE-STUCK-003',
            'Product Name': 'Aisle Stuck Gamma',
            'Location': 'AISLE-03',
            'Quantity': 1,
            'Timestamp': (now - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-AISLE-003',
            'Lot': 'LOT-2024-AISLE-003',
            'Status': 'TRANSITIONAL'
        }
    ]
    test_inventory.extend(aisle_stuck_data)
    
    # Rule 6: "Cold Chain Violations" - Frozen products in wrong zones
    print("Creating cold chain violations...")
    cold_chain_violations = [
        {
            'Pallet ID': 'PALLET-COLD-VIOLATION-001',
            'Product Name': 'FROZEN Ice Cream Premium',  # Contains "FROZEN" keyword
            'Location': 'STAGE-01',  # STAGING zone = STAGING, should trigger if not cold zone
            'Quantity': 4,
            'Timestamp': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-FROZEN-001',
            'Lot': 'LOT-2024-FROZEN-001',
            'Status': 'STAGING'
        },
        {
            'Pallet ID': 'PALLET-COLD-VIOLATION-002', 
            'Product Name': 'REFRIGERATED Dairy Products',  # Contains "REFRIGERATED" keyword
            'Location': 'AISLE-04',  # GENERAL zone, should trigger violation
            'Quantity': 6,
            'Timestamp': (now - timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-REFRIGERATED-001',
            'Lot': 'LOT-2024-REFRIG-001',
            'Status': 'TRANSITIONAL'
        }
    ]
    test_inventory.extend(cold_chain_violations)
    
    # Add some normal/compliant inventory for contrast
    print("Adding compliant inventory for baseline...")
    compliant_data = [
        {
            'Pallet ID': 'PALLET-NORMAL-001',
            'Product Name': 'Normal Product Alpha',
            'Location': 'RECV-01',
            'Quantity': 3,
            'Timestamp': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),  # Within 10-hour limit
            'SKU': 'SKU-NORMAL-001',
            'Lot': 'LOT-2024-NORMAL-001',
            'Status': 'RECEIVING'
        },
        {
            'Pallet ID': 'PALLET-NORMAL-002',
            'Product Name': 'Normal Product Beta',
            'Location': 'STAGE-02',
            'Quantity': 2,
            'Timestamp': (now - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-NORMAL-002',
            'Lot': 'LOT-2024-NORMAL-002', 
            'Status': 'STAGING'
        },
        {
            'Pallet ID': 'PALLET-NORMAL-003',
            'Product Name': 'Normal Product Gamma',
            'Location': 'DOCK-02',
            'Quantity': 1,
            'Timestamp': (now - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-NORMAL-003',
            'Lot': 'LOT-2024-NORMAL-003',
            'Status': 'SHIPPING'
        },
        # Some properly stored items
        {
            'Pallet ID': 'PALLET-STORED-001',
            'Product Name': 'Stored Product Alpha',
            'Location': '01-A01-B',
            'Quantity': 8,
            'Timestamp': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-STORED-001',
            'Lot': 'LOT-2024-STORED-001',
            'Status': 'STORED'
        },
        {
            'Pallet ID': 'PALLET-STORED-002',
            'Product Name': 'Stored Product Beta',
            'Location': '01-B02-A', 
            'Quantity': 6,
            'Timestamp': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SKU-STORED-002',
            'Lot': 'LOT-2024-STORED-002',
            'Status': 'STORED'
        }
    ]
    test_inventory.extend(compliant_data)
    
    return test_inventory

if __name__ == "__main__":
    # Create inventory data
    test_inventory = create_test_inventory()
    
    # Create DataFrame and save as Excel
    print("Creating Excel file...")
    df = pd.DataFrame(test_inventory)
    
    # Ensure proper column order
    column_order = ['Pallet ID', 'Product Name', 'Location', 'Quantity', 'Timestamp', 'SKU', 'Lot', 'Status']
    df = df.reindex(columns=column_order)
    
    # Save to Excel
    excel_path = 'inventoryreport.xlsx'
    df.to_excel(excel_path, index=False, sheet_name='Inventory Test Data')
    
    print(f"Excel file created: {excel_path}")
    print(f"Total records: {len(df)}")
    print("\nTest coverage summary:")
    print("- Forgotten Pallets (RECEIVING > 10hrs): 3 records")
    print("- Incomplete Lots (partial lot stored): 1 problematic record") 
    print("- Overcapacity Violations: 5 records (RECV-03 + DOCK-01)")
    print("- Invalid Locations: 2 records")
    print("- AISLE Stuck Pallets (>4hrs): 3 records") 
    print("- Cold Chain Violations: 2 records")
    print("- Normal/Compliant Records: 7 records")
    
    # Count pallets by special location
    special_locations = [
        {'code': 'RECV-01', 'type': 'RECEIVING'},
        {'code': 'RECV-02', 'type': 'RECEIVING'}, 
        {'code': 'RECV-03', 'type': 'RECEIVING'},
        {'code': 'STAGE-01', 'type': 'STAGING'},
        {'code': 'STAGE-02', 'type': 'STAGING'},
        {'code': 'STAGE-03', 'type': 'STAGING'},
        {'code': 'DOCK-01', 'type': 'DOCK'},
        {'code': 'DOCK-02', 'type': 'DOCK'},
        {'code': 'DOCK-03', 'type': 'DOCK'},
        {'code': 'AISLE-01', 'type': 'TRANSITIONAL'},
        {'code': 'AISLE-02', 'type': 'TRANSITIONAL'},
        {'code': 'AISLE-03', 'type': 'TRANSITIONAL'},
        {'code': 'AISLE-04', 'type': 'TRANSITIONAL'}
    ]
    
    print("\nSpecial locations targeted:")
    for loc in special_locations:
        count = len(df[df['Location'] == loc['code']])
        if count > 0:
            print(f"- {loc['code']} ({loc['type']}): {count} pallets")