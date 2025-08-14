#!/usr/bin/env python3
"""
Central Distribution Center Inventory Report Generator
Creates a comprehensive test inventory Excel file for debugging the warehouse intelligence system.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

def generate_pallet_id():
    """Generate a random pallet ID in format PLT-XXXXXX"""
    return f"PLT-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

def generate_receipt_number():
    """Generate a random receipt number in format RCP-XXXXXX"""
    return f"RCP-{''.join(random.choices(string.digits, k=6))}"

def generate_creation_date(days_back_range=(1, 180)):
    """Generate a random creation date within the specified range"""
    days_back = random.randint(*days_back_range)
    return datetime.now() - timedelta(days=days_back)

def create_central_dc_inventory():
    """Create comprehensive inventory data for Central Distribution Center"""
    
    # Product categories for realistic data
    products = [
        "Electronics - TV Sets", "Electronics - Laptops", "Electronics - Smartphones",
        "Furniture - Chairs", "Furniture - Tables", "Furniture - Sofas",
        "Clothing - Jackets", "Clothing - Jeans", "Clothing - Shoes",
        "Appliances - Refrigerators", "Appliances - Washers", "Appliances - Dryers",
        "Books - Fiction", "Books - Technical", "Books - Educational",
        "Toys - Action Figures", "Toys - Board Games", "Toys - Educational",
        "Food - Canned Goods", "Food - Snacks", "Food - Beverages",
        "Sports - Equipment", "Sports - Apparel", "Sports - Accessories"
    ]
    
    inventory_data = []
    
    # 1. STORAGE LOCATIONS - Main warehouse (4 aisles × 6 racks × 8 positions × 2 levels)
    print("Generating storage locations...")
    
    for aisle in range(1, 5):  # 4 aisles (reduced from 8)
        for rack in range(1, 7):  # 6 racks (reduced from 8)
            for position in range(1, 9):  # 8 positions (reduced from 10)
                for level in ['A', 'B']:  # 2 levels
                    
                    location = f"{aisle:02d}-{rack:02d}-{position:02d}{level}"
                    
                    # 70% occupancy rate for more manageable dataset
                    if random.random() < 0.70:
                        # Create multiple pallets per location for overcapacity testing
                        num_pallets = 1
                        
                        # Create overcapacity scenarios (15% chance of 2 pallets only)
                        if random.random() < 0.15:
                            num_pallets = 2
                        
                        for pallet_num in range(num_pallets):
                            # Generate stagnant pallets (8% chance of very old dates)
                            if random.random() < 0.08:
                                creation_date = generate_creation_date((120, 300))  # Very old
                            else:
                                creation_date = generate_creation_date((1, 90))    # Normal range
                            
                            inventory_data.append({
                                'pallet_id': generate_pallet_id(),
                                'location': location,
                                'creation_date': creation_date.strftime('%Y-%m-%d'),
                                'receipt_number': generate_receipt_number(),
                                'description': random.choice(products),
                                'location_type': 'STORAGE'
                            })
    
    # 2. RECEIVING AREAS - Test receiving capacity and temporary storage
    print("Generating receiving area inventory...")
    
    receiving_areas = [
        ('RCV-001', 10), ('RCV-002', 10), ('RCV-003', 10), 
        ('RCV-004', 8), ('RCV-005', 8)
    ]
    
    for location, capacity in receiving_areas:
        # Fill to 60% capacity normally, fewer overcapacity scenarios
        fill_rate = 0.6 if random.random() < 0.9 else 1.1  # 10% chance of mild overcapacity
        num_pallets = max(1, int(capacity * fill_rate))
        
        for _ in range(num_pallets):
            # Receiving items should be recent (last 7 days)
            creation_date = generate_creation_date((0, 7))
            
            inventory_data.append({
                'pallet_id': generate_pallet_id(),
                'location': location,
                'creation_date': creation_date.strftime('%Y-%m-%d'),
                'receipt_number': generate_receipt_number(),
                'description': random.choice(products),
                'location_type': 'RECEIVING'
            })
    
    # 3. STAGING AREAS - Order preparation
    print("Generating staging area inventory...")
    
    staging_areas = [
        ('STG-001', 5), ('STG-002', 5), ('STG-003', 5), ('STG-004', 5)
    ]
    
    for location, capacity in staging_areas:
        # Staging areas should have lower utilization (40%)
        num_pallets = max(1, int(capacity * 0.4))
        
        for _ in range(num_pallets):
            # Staging items should be very recent (last 3 days)
            creation_date = generate_creation_date((0, 3))
            
            inventory_data.append({
                'pallet_id': generate_pallet_id(),
                'location': location,
                'creation_date': creation_date.strftime('%Y-%m-%d'),
                'receipt_number': generate_receipt_number(),
                'description': random.choice(products),
                'location_type': 'STAGING'
            })
    
    # 4. DOCK AREAS - Loading/shipping
    print("Generating dock area inventory...")
    
    dock_areas = [
        ('DOCK-01', 3), ('DOCK-02', 3), ('DOCK-03', 3), ('DOCK-04', 3)
    ]
    
    for location, capacity in dock_areas:
        # Dock areas have variable utilization (30-80%)
        fill_rate = random.uniform(0.3, 0.8)
        num_pallets = max(1, int(capacity * fill_rate))
        
        for _ in range(num_pallets):
            # Dock items should be very recent (today or yesterday)
            creation_date = generate_creation_date((0, 2))
            
            inventory_data.append({
                'pallet_id': generate_pallet_id(),
                'location': location,
                'creation_date': creation_date.strftime('%Y-%m-%d'),
                'receipt_number': generate_receipt_number(),
                'description': random.choice(products),
                'location_type': 'DOCK'
            })
    
    # 5. FINAL LOCATIONS - Add some items that should be in FINAL but are elsewhere
    print("Generating final location scenarios...")
    
    # Create incomplete lots - pallets that should be in FINAL locations
    final_receipt_numbers = [generate_receipt_number() for _ in range(5)]  # Reduced from 10
    
    for receipt_num in final_receipt_numbers:
        # Create 3-4 pallets per receipt (reduced from 3-5)
        num_pallets = random.randint(3, 4)
        
        for i in range(num_pallets):
            # 70% should be in proper FINAL locations, 30% scattered in STORAGE
            if i < num_pallets * 0.7:
                # These are in proper FINAL locations (simulated)
                location = f"FINAL-{random.randint(1, 20):03d}"
                location_type = 'FINAL'
            else:
                # These create incomplete lots - same receipt but in STORAGE
                aisle = random.randint(1, 8)
                rack = random.randint(1, 8) 
                position = random.randint(1, 10)
                level = random.choice(['A', 'B'])
                location = f"{aisle:02d}-{rack:02d}-{position:02d}{level}"
                location_type = 'STORAGE'
            
            creation_date = generate_creation_date((1, 30))
            
            inventory_data.append({
                'pallet_id': generate_pallet_id(),
                'location': location,
                'creation_date': creation_date.strftime('%Y-%m-%d'),
                'receipt_number': receipt_num,
                'description': random.choice(products),
                'location_type': location_type
            })
    
    # 6. INVALID/UNKNOWN LOCATIONS - Create some data quality issues
    print("Generating data quality test scenarios...")
    
    invalid_locations = [
        'UNKNOWN-001', 'INVALID-LOC', 'NULL', '99-99-99X', 'ERROR-404'  # Reduced from 8 to 5
    ]
    
    for location in invalid_locations:
        if random.random() < 0.6:  # 60% chance to include each invalid location (reduced from 70%)
            creation_date = generate_creation_date((1, 60))
            
            inventory_data.append({
                'pallet_id': generate_pallet_id(),
                'location': location if location else 'NULL_LOCATION',
                'creation_date': creation_date.strftime('%Y-%m-%d'),
                'receipt_number': generate_receipt_number(),
                'description': random.choice(products),
                'location_type': 'UNKNOWN'
            })
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Add some additional columns for testing
    df['warehouse_id'] = 'USER_TESTF'
    df['warehouse_name'] = 'Central Distribution Center'
    df['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Shuffle the data to make it more realistic
    df = df.sample(frac=1).reset_index(drop=True)
    
    print(f"\nGenerated {len(df)} pallet records")
    print(f"Storage locations: {len([x for x in df['location_type'] if x == 'STORAGE'])}")
    print(f"Receiving areas: {len([x for x in df['location_type'] if x == 'RECEIVING'])}")
    print(f"Staging areas: {len([x for x in df['location_type'] if x == 'STAGING'])}")
    print(f"Dock areas: {len([x for x in df['location_type'] if x == 'DOCK'])}")
    print(f"Final locations: {len([x for x in df['location_type'] if x == 'FINAL'])}")
    print(f"Unknown/Invalid: {len([x for x in df['location_type'] if x == 'UNKNOWN'])}")
    
    return df

def main():
    """Generate and save the inventory report"""
    print("Creating Central Distribution Center Inventory Report...")
    print("=" * 60)
    
    # Generate inventory data
    inventory_df = create_central_dc_inventory()
    
    # Save to Excel file
    output_file = 'CentralDC_Compact_Inventory.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main inventory sheet
        inventory_df.to_excel(writer, sheet_name='Inventory', index=False)
        
        # Summary sheet
        summary_data = {
            'Metric': [
                'Total Pallets',
                'Storage Locations Used',
                'Receiving Area Pallets', 
                'Staging Area Pallets',
                'Dock Area Pallets',
                'Final Location Pallets',
                'Invalid/Unknown Locations',
                'Potential Overcapacity Locations',
                'Stagnant Pallets (>120 days)',
                'Recent Pallets (<7 days)'
            ],
            'Value': [
                len(inventory_df),
                len(inventory_df[inventory_df['location_type'] == 'STORAGE']),
                len(inventory_df[inventory_df['location_type'] == 'RECEIVING']),
                len(inventory_df[inventory_df['location_type'] == 'STAGING']),
                len(inventory_df[inventory_df['location_type'] == 'DOCK']),
                len(inventory_df[inventory_df['location_type'] == 'FINAL']),
                len(inventory_df[inventory_df['location_type'] == 'UNKNOWN']),
                len(inventory_df.groupby('location').size()[inventory_df.groupby('location').size() > 1]),
                len(inventory_df[pd.to_datetime(inventory_df['creation_date']) < (datetime.now() - timedelta(days=120))]),
                len(inventory_df[pd.to_datetime(inventory_df['creation_date']) > (datetime.now() - timedelta(days=7))])
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Location capacity analysis
        location_analysis = inventory_df.groupby(['location', 'location_type']).size().reset_index(name='pallet_count')
        location_analysis['potential_overcapacity'] = location_analysis['pallet_count'] > 1
        location_analysis.to_excel(writer, sheet_name='Location_Analysis', index=False)
    
    print(f"\n[SUCCESS] Inventory report saved as: {output_file}")
    print(f"[INFO] Total records: {len(inventory_df)}")
    print("\n[TEST SCENARIOS] Included:")
    print("  - Overcapacity locations (multiple pallets per location)")
    print("  - Stagnant pallets (>120 days old)")
    print("  - Incomplete lots (same receipt across different location types)")
    print("  - Invalid/unknown locations")
    print("  - Various location types (STORAGE, RECEIVING, STAGING, DOCK, FINAL)")
    print("  - Realistic utilization patterns")
    
    print(f"\n[READY] This file is ready for testing the warehouse intelligence system!")
    print(f"        Upload it through the frontend to see rule engine results.")

if __name__ == "__main__":
    main()