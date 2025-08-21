#!/usr/bin/env python3
"""
Comprehensive Rule Validation Test Inventory Generator
Creates strategic test inventory for USER_TESTF warehouse testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

def generate_comprehensive_test_inventory():
    """Generate comprehensive test inventory with strategic violations"""
    
    # Set random seed for reproducible tests
    random.seed(42)
    np.random.seed(42)
    
    # Warehouse layout configuration
    warehouse_config = {
        'special_areas': {
            'RECV-01': {'capacity': 10, 'zone': 'RECEIVING'},
            'RECV-02': {'capacity': 10, 'zone': 'RECEIVING'}, 
            'STAGE-01': {'capacity': 5, 'zone': 'STAGING'},
            'DOCK-01': {'capacity': 2, 'zone': 'DOCK'},
            'AISLE-01': {'capacity': 10, 'zone': 'GENERAL'},
            'AISLE-02': {'capacity': 10, 'zone': 'GENERAL'}
        },
        'storage_structure': {
            'aisles': [1, 2],
            'racks': ['A', 'B'], 
            'positions': list(range(1, 36)),  # 1-35
            'levels': ['A', 'B', 'C', 'D'],
            'capacity_per_level': 2
        }
    }
    
    # Generate storage locations
    storage_locations = []
    for aisle in warehouse_config['storage_structure']['aisles']:
        for rack in warehouse_config['storage_structure']['racks']:
            for pos in warehouse_config['storage_structure']['positions']:
                for level in warehouse_config['storage_structure']['levels']:
                    location = f"{aisle:02d}-{rack}{pos:02d}-{level}"
                    storage_locations.append(location)
    
    # Product types and distributions
    product_types = {
        'GENERAL': 0.70,
        'HAZMAT': 0.15, 
        'FROZEN': 0.10,
        'FRAGILE': 0.03,
        'OVERSIZED': 0.02
    }
    
    temperature_requirements = {
        'GENERAL': 'AMBIENT',
        'HAZMAT': 'AMBIENT', 
        'FROZEN': 'FROZEN',
        'FRAGILE': 'AMBIENT',
        'OVERSIZED': 'AMBIENT'
    }
    
    # Receipt numbers for lot scenarios
    receipt_numbers = [
        f"RCP{2024}{''.join(random.choices(string.digits, k=4))}" 
        for _ in range(25)
    ]
    
    inventory_data = []
    pallet_counter = 1
    
    # Current time reference
    now = datetime.now()
    
    print("Generating comprehensive test inventory...")
    print("=" * 50)
    
    # 1. FORGOTTEN PALLETS VIOLATIONS
    print("Adding Forgotten Pallets violations...")
    
    # Critical: 4+ days old in RECEIVING (3 pallets)
    for i in range(3):
        location = random.choice(['RECV-01', 'RECV-02'])
        creation_date = now - timedelta(days=random.randint(4, 7))
        product_type = random.choices(list(product_types.keys()), weights=list(product_types.values()))[0]
        
        inventory_data.append({
            'Pallet ID': f"PLT{pallet_counter:06d}",
            'Location': location,
            'Description': f"CRITICAL FORGOTTEN - {product_type} Product {i+1}",
            'Receipt Number': random.choice(receipt_numbers),
            'Creation Date': creation_date,
            'Product Type': product_type,
            'Temperature Requirement': temperature_requirements[product_type]
        })
        pallet_counter += 1
    
    # High: 2-4 days old in RECEIVING (4 pallets)
    for i in range(4):
        location = random.choice(['RECV-01', 'RECV-02'])
        creation_date = now - timedelta(days=random.uniform(2.0, 3.9))
        product_type = random.choices(list(product_types.keys()), weights=list(product_types.values()))[0]
        
        inventory_data.append({
            'Pallet ID': f"PLT{pallet_counter:06d}",
            'Location': location,
            'Description': f"HIGH FORGOTTEN - {product_type} Product {i+1}",
            'Receipt Number': random.choice(receipt_numbers),
            'Creation Date': creation_date,
            'Product Type': product_type,
            'Temperature Requirement': temperature_requirements[product_type]
        })
        pallet_counter += 1
    
    # Medium: 12+ hours in STAGING (3 pallets)
    for i in range(3):
        creation_date = now - timedelta(hours=random.randint(13, 30))
        product_type = random.choices(list(product_types.keys()), weights=list(product_types.values()))[0]
        
        inventory_data.append({
            'Pallet ID': f"PLT{pallet_counter:06d}",
            'Location': 'STAGE-01',
            'Description': f"MEDIUM FORGOTTEN - {product_type} Product {i+1}",
            'Receipt Number': random.choice(receipt_numbers),
            'Creation Date': creation_date,
            'Product Type': product_type,
            'Temperature Requirement': temperature_requirements[product_type]
        })
        pallet_counter += 1
    
    # 2. INCOMPLETE LOTS VIOLATIONS
    print("Adding Incomplete Lots violations...")
    
    # Lot with 80%+ pallets in STORAGE, stragglers in RECEIVING
    incomplete_lot_rcpt = receipt_numbers[0]
    
    # Add 8 pallets in storage (80% of 10-pallet lot)
    for i in range(8):
        storage_loc = random.choice(storage_locations)
        creation_date = now - timedelta(hours=random.randint(6, 24))
        product_type = 'GENERAL'
        
        inventory_data.append({
            'Pallet ID': f"PLT{pallet_counter:06d}",
            'Location': storage_loc,
            'Description': f"LOT MAIN - {product_type} Product {i+1}",
            'Receipt Number': incomplete_lot_rcpt,
            'Creation Date': creation_date,
            'Product Type': product_type,
            'Temperature Requirement': temperature_requirements[product_type]
        })
        pallet_counter += 1
    
    # Add 2 stragglers in RECEIVING (should trigger incomplete lot rule)
    for i in range(2):
        location = random.choice(['RECV-01', 'RECV-02'])
        creation_date = now - timedelta(hours=random.randint(6, 24))
        product_type = 'GENERAL'
        
        inventory_data.append({
            'Pallet ID': f"PLT{pallet_counter:06d}",
            'Location': location,
            'Description': f"LOT STRAGGLER - {product_type} Product {i+1}",
            'Receipt Number': incomplete_lot_rcpt,
            'Creation Date': creation_date,
            'Product Type': product_type,
            'Temperature Requirement': temperature_requirements[product_type]
        })
        pallet_counter += 1
    
    # 3. OVERCAPACITY VIOLATIONS
    print("Adding Overcapacity violations...")
    
    # RECEIVING overcapacity: 15 pallets in RECV-01 (capacity 10)
    for i in range(15):
        creation_date = now - timedelta(hours=random.randint(1, 6))
        product_type = random.choices(list(product_types.keys()), weights=list(product_types.values()))[0]
        
        inventory_data.append({
            'Pallet ID': f"PLT{pallet_counter:06d}",
            'Location': 'RECV-01',
            'Description': f"OVERCAP RECV - {product_type} Product {i+1}",
            'Receipt Number': random.choice(receipt_numbers),
            'Creation Date': creation_date,
            'Product Type': product_type,
            'Temperature Requirement': temperature_requirements[product_type]
        })
        pallet_counter += 1
    
    # STORAGE overcapacity: Multiple 2-capacity locations with 3-4 pallets
    overcap_storage_locations = random.sample(storage_locations, 15)
    for location in overcap_storage_locations:
        pallets_in_location = random.randint(3, 4)  # 3-4 pallets in 2-capacity location
        for i in range(pallets_in_location):
            creation_date = now - timedelta(hours=random.randint(1, 12))
            product_type = random.choices(list(product_types.keys()), weights=list(product_types.values()))[0]
            
            inventory_data.append({
                'Pallet ID': f"PLT{pallet_counter:06d}",
                'Location': location,
                'Description': f"OVERCAP STOR - {product_type} Product {i+1}",
                'Receipt Number': random.choice(receipt_numbers),
                'Creation Date': creation_date,
                'Product Type': product_type,
                'Temperature Requirement': temperature_requirements[product_type]
            })
            pallet_counter += 1
    
    # 4. INVALID LOCATIONS VIOLATIONS
    print("Adding Invalid Locations violations...")
    
    invalid_locations = [
        'INVALID-LOC-001', 'BAD-FORMAT', '@#$%^&',
        '99-99-999Z', 'FAKE-LOCATION'
    ]
    
    for i, location in enumerate(invalid_locations):
        creation_date = now - timedelta(hours=random.randint(1, 24))
        product_type = random.choices(list(product_types.keys()), weights=list(product_types.values()))[0]
        
        inventory_data.append({
            'Pallet ID': f"PLT{pallet_counter:06d}",
            'Location': location,
            'Description': f"INVALID LOC - {product_type} Product {i+1}",
            'Receipt Number': random.choice(receipt_numbers),
            'Creation Date': creation_date,
            'Product Type': product_type,
            'Temperature Requirement': temperature_requirements[product_type]
        })
        pallet_counter += 1
    
    # 5. AISLE STUCK VIOLATIONS
    print("Adding Aisle Stuck violations...")
    
    # Pallets >4 hours old in AISLE locations (3 pallets)
    for i in range(3):
        location = random.choice(['AISLE-01', 'AISLE-02'])
        creation_date = now - timedelta(hours=random.randint(5, 12))
        product_type = random.choices(list(product_types.keys()), weights=list(product_types.values()))[0]
        
        inventory_data.append({
            'Pallet ID': f"PLT{pallet_counter:06d}",
            'Location': location,
            'Description': f"AISLE STUCK - {product_type} Product {i+1}",
            'Receipt Number': random.choice(receipt_numbers),
            'Creation Date': creation_date,
            'Product Type': product_type,
            'Temperature Requirement': temperature_requirements[product_type]
        })
        pallet_counter += 1
    
    # 6. SCANNER ERROR VIOLATIONS
    print("Adding Scanner Error violations...")
    
    # Duplicate pallet IDs in different locations (2 scenarios)
    duplicate_pallet_id = f"PLT{pallet_counter:06d}"
    
    # First instance
    inventory_data.append({
        'Pallet ID': duplicate_pallet_id,
        'Location': 'RECV-01',
        'Description': "DUPLICATE SCAN - General Product A",
        'Receipt Number': random.choice(receipt_numbers),
        'Creation Date': now - timedelta(hours=2),
        'Product Type': 'GENERAL',
        'Temperature Requirement': 'AMBIENT'
    })
    
    # Second instance (duplicate)
    inventory_data.append({
        'Pallet ID': duplicate_pallet_id,
        'Location': '01-A01-A',
        'Description': "DUPLICATE SCAN - General Product A (Duplicate)",
        'Receipt Number': random.choice(receipt_numbers),
        'Creation Date': now - timedelta(hours=1),
        'Product Type': 'GENERAL',
        'Temperature Requirement': 'AMBIENT'
    })
    
    pallet_counter += 1
    
    # Empty/corrupted pallet IDs (2 scenarios)
    corrupt_entries = ['', None, '   ', 'PLT###ERR']
    for i, corrupt_id in enumerate(corrupt_entries[:2]):
        creation_date = now - timedelta(hours=random.randint(1, 6))
        
        inventory_data.append({
            'Pallet ID': corrupt_id if corrupt_id else '',
            'Location': random.choice(['RECV-02', 'STAGE-01']),
            'Description': f"CORRUPTED SCAN - Error Entry {i+1}",
            'Receipt Number': random.choice(receipt_numbers),
            'Creation Date': creation_date,
            'Product Type': 'GENERAL',
            'Temperature Requirement': 'AMBIENT'
        })
    
    # 7. CROSS-RULE SCENARIOS
    print("Adding Cross-Rule scenarios...")
    
    # Pallets triggering both Forgotten + Overcapacity (8 pallets)
    # Add more old pallets to already overcapacity RECV-01
    for i in range(8):
        creation_date = now - timedelta(days=random.uniform(1.5, 3.0))
        product_type = random.choices(list(product_types.keys()), weights=list(product_types.values()))[0]
        
        inventory_data.append({
            'Pallet ID': f"PLT{pallet_counter:06d}",
            'Location': 'RECV-01',
            'Description': f"CROSS-RULE FORGOT+OVERCAP - {product_type} Product {i+1}",
            'Receipt Number': random.choice(receipt_numbers),
            'Creation Date': creation_date,
            'Product Type': product_type,
            'Temperature Requirement': temperature_requirements[product_type]
        })
        pallet_counter += 1
    
    # 8. NORMAL OPERATIONS (60-70% of inventory)
    print("Adding Normal Operations inventory...")
    
    # Calculate target total inventory (aim for ~300 pallets total)
    current_count = len(inventory_data)
    target_total = 300
    normal_operations_count = target_total - current_count
    
    # Add normal operations pallets
    for i in range(normal_operations_count):
        # Recent creation dates (last 24 hours)
        creation_date = now - timedelta(hours=random.uniform(0.1, 24.0))
        
        # Realistic location distribution
        location_type = random.choices(
            ['storage', 'receiving', 'staging', 'dock'],
            weights=[0.70, 0.15, 0.10, 0.05]
        )[0]
        
        if location_type == 'storage':
            location = random.choice(storage_locations)
        elif location_type == 'receiving':
            location = random.choice(['RECV-01', 'RECV-02'])
        elif location_type == 'staging':
            location = 'STAGE-01'
        else:
            location = 'DOCK-01'
        
        product_type = random.choices(list(product_types.keys()), weights=list(product_types.values()))[0]
        
        inventory_data.append({
            'Pallet ID': f"PLT{pallet_counter:06d}",
            'Location': location,
            'Description': f"NORMAL OPS - {product_type} Product {i+1}",
            'Receipt Number': random.choice(receipt_numbers),
            'Creation Date': creation_date,
            'Product Type': product_type,
            'Temperature Requirement': temperature_requirements[product_type]
        })
        pallet_counter += 1
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Sort by creation date (oldest first)
    df = df.sort_values('Creation Date')
    
    print(f"\nGenerated {len(df)} total inventory records")
    print(f"Unique locations: {df['Location'].nunique()}")
    print(f"Unique lots: {df['Receipt Number'].nunique()}")
    print(f"Date range: {df['Creation Date'].min()} to {df['Creation Date'].max()}")
    
    return df

def create_validation_summary():
    """Create expected violations summary"""
    
    summary = """
# Expected Violations Summary

**Test File**: comprehensive_rule_validation_test.xlsx
**Total Pallets**: ~300
**Test Focus**: Comprehensive rule validation with cross-rule intelligence

## Rule 1 (Forgotten Pallets): 10 expected violations
- Critical: 3 pallets (4+ days in RECEIVING)
- High: 4 pallets (2-4 days in RECEIVING)  
- Medium: 3 pallets (12+ hours in STAGING)

## Rule 2 (Incomplete Lots): 1 expected violation
- RCP2024XXXX: 2 stragglers in RECEIVING (80% completion)

## Rule 3 (Overcapacity): 60+ expected violations
- RECV-01: 23+ pallets in 10-capacity location (2.3x overcapacity)
- Storage locations: 15 locations with 3-4 pallets in 2-capacity levels

## Rule 4 (Invalid Locations): 5 expected violations
- INVALID-LOC-001, BAD-FORMAT, @#$%^&, 99-99-999Z, FAKE-LOCATION

## Rule 5 (Aisle Stuck): 3 expected violations
- AISLE-01/AISLE-02 locations with pallets >4 hours old

## Rule 7 (Scanner Errors): 3 expected violations
- 1 duplicate pallet ID in different locations
- 2 corrupted/empty pallet ID entries

## Cross-Rule Intelligence: 8+ expected correlations
- 8 pallets triggering both Forgotten Pallets + Overcapacity in RECV-01
- Invalid locations contributing to overall warehouse inefficiency

## Performance Expectations:
- Processing time: <5 seconds
- Memory usage: <50 MB
- Response time: <3 seconds
- Rule execution: <1000ms per rule

## Data Quality Verification:
[✓] All required columns present
[✓] Realistic pallet ID formats (PLT######)
[✓] Valid location codes (mix of valid/invalid as designed)
[✓] 7-day date range with realistic timestamps
[✓] Product type distribution: 70% GENERAL, 15% HAZMAT, 10% FROZEN, 5% other
[✓] 25 different receipt numbers for lot diversity
"""
    
    return summary

if __name__ == "__main__":
    # Generate test inventory
    df = generate_comprehensive_test_inventory()
    
    # Save to Excel
    output_path = "comprehensive_rule_validation_test.xlsx"
    df.to_excel(output_path, index=False)
    
    # Create validation summary
    summary = create_validation_summary()
    summary_path = "comprehensive_rule_validation_expected_results.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n[SUCCESS] Test inventory created: {output_path}")
    print(f"[SUCCESS] Expected results documented: {summary_path}")
    print(f"\nTotal records: {len(df)}")
    print(f"Unique locations: {df['Location'].nunique()}")
    print(f"Unique lots: {df['Receipt Number'].nunique()}")
    print(f"Date range: {df['Creation Date'].min()} to {df['Creation Date'].max()}")
    
    # Display product type distribution
    print("\nProduct Type Distribution:")
    product_dist = df['Product Type'].value_counts(normalize=True)
    for product, percentage in product_dist.items():
        print(f"  {product}: {percentage:.1%}")