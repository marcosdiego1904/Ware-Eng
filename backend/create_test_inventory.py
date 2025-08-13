#!/usr/bin/env python3
"""
Create Metro Distribution Center Test Inventory
Realistic warehouse data for live user testing
"""

import pandas as pd
from datetime import datetime, timedelta
import random
import os

def create_metro_warehouse_inventory():
    """Create realistic inventory data for Metro Distribution Center"""
    
    inventory_data = []
    
    print("Creating Metro Distribution Center Inventory Report...")
    print("=" * 50)
    
    # ===== SCENARIO 1: STAGNANT PALLETS (6 pallets) =====
    print("Adding stagnant pallets scenario...")
    stagnant_pallets = [
        {
            'Pallet ID': 'MDC001',
            'Location': 'RECEIVING',
            'Receipt Number': 'REC240801',
            'Description': 'Electronics - Laptops',
            'Quantity': 25,
            'Weight (lbs)': 1250,
            'Created Date': (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'ELEC-LAP-001'
        },
        {
            'Pallet ID': 'MDC002',
            'Location': 'RECEIVING',
            'Receipt Number': 'REC240801',
            'Description': 'Electronics - Tablets', 
            'Quantity': 40,
            'Weight (lbs)': 800,
            'Created Date': (datetime.now() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'ELEC-TAB-002'
        },
        {
            'Pallet ID': 'MDC003',
            'Location': 'RECEIVING',
            'Receipt Number': 'REC240802',
            'Description': 'Home & Garden - Tools',
            'Quantity': 50,
            'Weight (lbs)': 2000,
            'Created Date': (datetime.now() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'HOME-TOOL-003'
        },
        {
            'Pallet ID': 'MDC004',
            'Location': 'RECEIVING',
            'Receipt Number': 'REC240802',
            'Description': 'Automotive - Parts',
            'Quantity': 30,
            'Weight (lbs)': 1500,
            'Created Date': (datetime.now() - timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'AUTO-PART-004'
        },
        {
            'Pallet ID': 'MDC005',
            'Location': 'RECEIVING',
            'Receipt Number': 'REC240803',
            'Description': 'Sports Equipment',
            'Quantity': 35,
            'Weight (lbs)': 1750,
            'Created Date': (datetime.now() - timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'SPORT-EQ-005'
        },
        {
            'Pallet ID': 'MDC006',
            'Location': 'RECEIVING',
            'Receipt Number': 'REC240803',
            'Description': 'Office Supplies',
            'Quantity': 60,
            'Weight (lbs)': 900,
            'Created Date': (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'OFF-SUP-006'
        }
    ]
    inventory_data.extend(stagnant_pallets)
    
    # ===== SCENARIO 2: OVERCAPACITY (4 locations, 2 pallets each) =====
    print("Adding overcapacity scenario...")
    overcapacity_pallets = [
        # Location A1-001 (2 pallets in 1-capacity location)
        {
            'Pallet ID': 'MDC010',
            'Location': 'A1-001',
            'Receipt Number': 'REC240804',
            'Description': 'Books & Media',
            'Quantity': 45,
            'Weight (lbs)': 900,
            'Created Date': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'BOOK-MED-010'
        },
        {
            'Pallet ID': 'MDC011',
            'Location': 'A1-001',  # Same location = overcapacity
            'Receipt Number': 'REC240804',
            'Description': 'Books & Media',
            'Quantity': 55,
            'Weight (lbs)': 1100,
            'Created Date': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'BOOK-MED-011'
        },
        
        # Location A2-005 (2 pallets in 1-capacity location)
        {
            'Pallet ID': 'MDC012',
            'Location': 'A2-005',
            'Receipt Number': 'REC240805',
            'Description': 'Clothing & Apparel',
            'Quantity': 80,
            'Weight (lbs)': 600,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'CLOTH-APP-012'
        },
        {
            'Pallet ID': 'MDC013',
            'Location': 'A2-005',  # Same location = overcapacity
            'Receipt Number': 'REC240805',
            'Description': 'Clothing & Apparel',
            'Quantity': 75,
            'Weight (lbs)': 650,
            'Created Date': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'CLOTH-APP-013'
        },
        
        # Location B1-010 (2 pallets in 1-capacity location)
        {
            'Pallet ID': 'MDC014',
            'Location': 'B1-010',
            'Receipt Number': 'REC240806',
            'Description': 'Health & Beauty',
            'Quantity': 90,
            'Weight (lbs)': 450,
            'Created Date': (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'HEALTH-BEA-014'
        },
        {
            'Pallet ID': 'MDC015',
            'Location': 'B1-010',  # Same location = overcapacity
            'Receipt Number': 'REC240806',
            'Description': 'Health & Beauty',
            'Quantity': 85,
            'Weight (lbs)': 500,
            'Created Date': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'HEALTH-BEA-015'
        },
        
        # Location B2-020 (2 pallets in 1-capacity location)
        {
            'Pallet ID': 'MDC016',
            'Location': 'B2-020',
            'Receipt Number': 'REC240807',
            'Description': 'Kitchen & Dining',
            'Quantity': 40,
            'Weight (lbs)': 1600,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'KITCH-DIN-016'
        },
        {
            'Pallet ID': 'MDC017',
            'Location': 'B2-020',  # Same location = overcapacity
            'Receipt Number': 'REC240807',
            'Description': 'Kitchen & Dining',
            'Quantity': 35,
            'Weight (lbs)': 1400,
            'Created Date': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'KITCH-DIN-017'
        }
    ]
    inventory_data.extend(overcapacity_pallets)
    
    # ===== SCENARIO 3: INCOMPLETE LOT (10 pallets, 8 stored, 2 in receiving) =====
    print("Adding incomplete lot scenario...")
    lot_number = 'LOT240810'
    
    # 8 pallets already stored (80% complete - above 70% threshold)
    stored_lot_pallets = [
        {
            'Pallet ID': 'MDC020',
            'Location': 'A3-012',
            'Receipt Number': lot_number,
            'Description': 'Toys & Games - Action Figures',
            'Quantity': 50,
            'Weight (lbs)': 750,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'TOY-GAME-020'
        },
        {
            'Pallet ID': 'MDC021',
            'Location': 'A3-013',
            'Receipt Number': lot_number,
            'Description': 'Toys & Games - Board Games',
            'Quantity': 60,
            'Weight (lbs)': 800,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'TOY-GAME-021'
        },
        {
            'Pallet ID': 'MDC022',
            'Location': 'A3-014',
            'Receipt Number': lot_number,
            'Description': 'Toys & Games - Puzzles',
            'Quantity': 45,
            'Weight (lbs)': 675,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'TOY-GAME-022'
        },
        {
            'Pallet ID': 'MDC023',
            'Location': 'B3-015',
            'Receipt Number': lot_number,
            'Description': 'Toys & Games - Educational',
            'Quantity': 55,
            'Weight (lbs)': 825,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'TOY-GAME-023'
        },
        {
            'Pallet ID': 'MDC024',
            'Location': 'B3-016',
            'Receipt Number': lot_number,
            'Description': 'Toys & Games - Outdoor',
            'Quantity': 40,
            'Weight (lbs)': 1200,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'TOY-GAME-024'
        },
        {
            'Pallet ID': 'MDC025',
            'Location': 'B3-017',
            'Receipt Number': lot_number,
            'Description': 'Toys & Games - Electronic',
            'Quantity': 30,
            'Weight (lbs)': 900,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'TOY-GAME-025'
        },
        {
            'Pallet ID': 'MDC026',
            'Location': 'A4-018',
            'Receipt Number': lot_number,
            'Description': 'Toys & Games - Arts & Crafts',
            'Quantity': 65,
            'Weight (lbs)': 650,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'TOY-GAME-026'
        },
        {
            'Pallet ID': 'MDC027',
            'Location': 'A4-019',
            'Receipt Number': lot_number,
            'Description': 'Toys & Games - Building Sets',
            'Quantity': 35,
            'Weight (lbs)': 1050,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'TOY-GAME-027'
        }
    ]
    inventory_data.extend(stored_lot_pallets)
    
    # 2 stragglers still in receiving (lot completion issue)
    straggler_pallets = [
        {
            'Pallet ID': 'MDC028',
            'Location': 'RECEIVING',  # Should be stored like the others
            'Receipt Number': lot_number,
            'Description': 'Toys & Games - Remote Control',
            'Quantity': 25,
            'Weight (lbs)': 750,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'TOY-GAME-028'
        },
        {
            'Pallet ID': 'MDC029',
            'Location': 'RECEIVING',  # Should be stored like the others
            'Receipt Number': lot_number,
            'Description': 'Toys & Games - Sports Toys',
            'Quantity': 40,
            'Weight (lbs)': 1000,
            'Created Date': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'TOY-GAME-029'
        }
    ]
    inventory_data.extend(straggler_pallets)
    
    # ===== SCENARIO 4: INVALID LOCATIONS (3 pallets) =====
    print("Adding invalid locations scenario...")
    invalid_location_pallets = [
        {
            'Pallet ID': 'MDC030',
            'Location': 'Z9-999',  # Invalid location code
            'Receipt Number': 'REC240808',
            'Description': 'Pet Supplies',
            'Quantity': 70,
            'Weight (lbs)': 840,
            'Created Date': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'PET-SUP-030'
        },
        {
            'Pallet ID': 'MDC031',
            'Location': 'INVALID_LOC',  # Invalid location code
            'Receipt Number': 'REC240809',
            'Description': 'Garden Supplies',
            'Quantity': 45,
            'Weight (lbs)': 1350,
            'Created Date': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'GARD-SUP-031'
        },
        {
            'Pallet ID': 'MDC032',
            'Location': 'X1-ABC',  # Invalid location code
            'Receipt Number': 'REC240810',
            'Description': 'Hardware Tools',
            'Quantity': 25,
            'Weight (lbs)': 1250,
            'Created Date': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'HARD-TOOL-032'
        }
    ]
    inventory_data.extend(invalid_location_pallets)
    
    # ===== SCENARIO 5: MISSING LOCATIONS (2 pallets) =====
    print("Adding missing locations scenario...")
    missing_location_pallets = [
        {
            'Pallet ID': 'MDC035',
            'Location': '',  # Empty location
            'Receipt Number': 'REC240811',
            'Description': 'Bathroom Fixtures',
            'Quantity': 15,
            'Weight (lbs)': 900,
            'Created Date': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'BATH-FIX-035'
        },
        {
            'Pallet ID': 'MDC036',
            'Location': None,  # Missing location (will be empty in Excel)
            'Receipt Number': 'REC240812',
            'Description': 'Lighting Equipment',
            'Quantity': 20,
            'Weight (lbs)': 600,
            'Created Date': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': 'LIGHT-EQ-036'
        }
    ]
    inventory_data.extend(missing_location_pallets)
    
    # ===== NORMAL OPERATIONS (20 pallets for baseline) =====
    print("Adding normal operations pallets...")
    normal_locations = ['STAGING_A', 'STAGING_B', 'A1-002', 'A1-003', 'A2-001', 
                       'A2-002', 'B1-001', 'B1-002', 'B2-001', 'B2-002',
                       'A3-001', 'A3-002', 'B3-001', 'B3-002', 'A4-001',
                       'A4-002', 'B4-001', 'B4-002', 'DOCK_01', 'DOCK_02']
    
    normal_products = [
        ('Furniture - Chairs', 'FURN-CHAIR'),
        ('Furniture - Tables', 'FURN-TABLE'), 
        ('Electronics - Cables', 'ELEC-CABLE'),
        ('Home Decor - Vases', 'HOME-VASE'),
        ('Bedding & Bath', 'BED-BATH'),
        ('Small Appliances', 'SMALL-APP'),
        ('Camping Gear', 'CAMP-GEAR'),
        ('Art Supplies', 'ART-SUP'),
        ('Musical Instruments', 'MUSIC-INST'),
        ('Exercise Equipment', 'EXER-EQ')
    ]
    
    for i in range(20):
        location = normal_locations[i]
        product_desc, sku_prefix = random.choice(normal_products)
        
        normal_pallet = {
            'Pallet ID': f'MDC{40 + i:03d}',
            'Location': location,
            'Receipt Number': f'REC24081{3 + i//5}',
            'Description': product_desc,
            'Quantity': random.randint(20, 80),
            'Weight (lbs)': random.randint(400, 1800),
            'Created Date': (datetime.now() - timedelta(hours=random.randint(0, 3))).strftime('%Y-%m-%d %H:%M:%S'),
            'SKU': f'{sku_prefix}-{40 + i:03d}'
        }
        inventory_data.append(normal_pallet)
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Save to Excel
    output_file = 'metro_warehouse_inventory.xlsx'
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"\n✓ Created {output_file}")
    print(f"✓ Total pallets: {len(inventory_data)}")
    print(f"✓ File size: {os.path.getsize(output_file) / 1024:.1f} KB")
    
    # Summary of test scenarios
    print(f"\nTest Scenarios Included:")
    print(f"✓ 6 stagnant pallets in RECEIVING (>4 hours)")
    print(f"✓ 8 overcapacity pallets (4 locations with 2 pallets each)")
    print(f"✓ 2 lot stragglers (80% of lot stored, 2 still in receiving)")
    print(f"✓ 3 invalid location codes")
    print(f"✓ 2 missing locations")
    print(f"✓ 20 normal operations pallets")
    print(f"\nExpected Anomalies: ~21 total")
    print(f"- Very High Priority: 8 (stagnant + lot issues)")
    print(f"- High Priority: 8 (overcapacity)")
    print(f"- Medium Priority: 5 (invalid + missing locations)")
    
    return output_file

if __name__ == "__main__":
    create_metro_warehouse_inventory()