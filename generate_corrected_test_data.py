import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

def generate_correct_location_code(aisle, rack, position, level):
    """Generate correct location code in format: 0X-Y-ZZZ-W (Pattern 2)"""
    return f"{aisle:02d}-{rack}-{position:03d}-{level}"

def generate_special_area_code(area_type, number):
    """Generate special area location codes"""
    return f"{area_type}-{number:02d}"

def generate_valid_pallet():
    """Generate a valid pallet record with correct location format"""
    pallet_id = f"PLT{random.randint(100000, 999999)}"
    
    # Generate valid location using correct format
    aisle = random.randint(1, 3)  # Aisles 01-03
    rack = random.choice(['A', 'B'])  # Racks A, B
    position = random.randint(1, 50)  # Positions 001-050
    level = random.choice(['A', 'B', 'C', 'D'])  # Levels A-D
    location = generate_correct_location_code(aisle, rack, position, level)
    
    # Valid dimensions (within warehouse limits)
    length = round(random.uniform(1.0, 2.4), 2)
    width = round(random.uniform(0.8, 1.4), 2)
    height = round(random.uniform(0.5, 1.9), 2)
    
    # Valid weight
    weight = round(random.uniform(100, 800), 1)
    
    # Other fields
    product_code = f"PROD{random.randint(1000, 9999)}"
    quantity = random.randint(1, 100)
    batch_number = f"BATCH{random.randint(2024001, 2024365)}"
    
    # Random date within last 30 days
    days_ago = random.randint(0, 30)
    received_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        'Pallet_ID': pallet_id,
        'Location_Code': location,
        'Product_Code': product_code,
        'Quantity': quantity,
        'Weight_KG': weight,
        'Length_M': length,
        'Width_M': width,
        'Height_M': height,
        'Batch_Number': batch_number,
        'Received_Date': received_date,
        'Status': random.choice(['ACTIVE', 'RESERVED', 'PENDING']),
        'Priority': random.choice(['HIGH', 'MEDIUM', 'LOW'])
    }

def generate_anomalous_pallets():
    """Generate pallets with specific rule violations based on actual system rules"""
    anomalies = []
    
    # Rule 1: STAGNANT_PALLETS - Pallets in RECEIVING areas too long (10 violations)
    for i in range(10):
        pallet = generate_valid_pallet()
        # Create old timestamp (> 10 hours ago to trigger forgotten pallets alert)
        old_date = (datetime.now() - timedelta(hours=random.randint(12, 48))).strftime('%Y-%m-%d %H:%M:%S')
        pallet.update({
            'Pallet_ID': f'PLT990{i+1:02d}',
            'Location_Code': 'RECV-02',  # Valid special area
            'Received_Date': old_date,
            'Status': 'PENDING'
        })
        anomalies.append(pallet)
    
    # Rule 2: UNCOORDINATED_LOTS - Pallets left behind in receiving (8 violations)
    # Create a batch where most pallets moved to final storage but some stayed
    shared_batch = 'BATCH2024100'
    for i in range(8):
        pallet = generate_valid_pallet()
        pallet.update({
            'Pallet_ID': f'PLT980{i+1:02d}',
            'Location_Code': 'RECV-02',  # Still in receiving
            'Batch_Number': shared_batch,  # Same batch
            'Status': 'PENDING'
        })
        anomalies.append(pallet)
    
    # Rule 3: INVALID_LOCATION - Invalid location codes (15 violations)
    invalid_locations = [
        'PLT970001', '4A-001-A',      # Invalid aisle (should be 1-3)
        'PLT970002', '01-C-001-A',    # Invalid rack (should be A or B)
        'PLT970003', '01-A-051-A',    # Invalid position (should be 1-50)
        'PLT970004', '01-A-001-E',    # Invalid level (should be A-D)
        'PLT970005', '1-A-1-A',       # Wrong format (not zero-padded)
        'PLT970006', '01A001A',       # Missing separators
        'PLT970007', 'A01-001-A',     # Wrong format (letters/numbers swapped)
        'PLT970008', '01-A-000-A',    # Invalid position (position 0)
        'PLT970009', 'INVALID-LOC',   # Completely invalid
        'PLT970010', '01-A-001-',     # Incomplete location
        'PLT970011', '00-A-001-A',    # Invalid aisle (aisle 0)
        'PLT970012', '01--001-A',     # Missing rack
        'PLT970013', '01-A--A',       # Missing position
        'PLT970014', 'UNKN-99',       # Invalid special area
        'PLT970015', 'RECV-99'        # Invalid special area number
    ]
    
    for i in range(0, len(invalid_locations), 2):
        pallet = generate_valid_pallet()
        pallet.update({
            'Pallet_ID': invalid_locations[i],
            'Location_Code': invalid_locations[i+1]
        })
        anomalies.append(pallet)
    
    # Rule 4: OVERCAPACITY - Multiple pallets in same location (20 violations = 10 pairs)
    overcapacity_locations = [
        '01-A-001-A', '01-A-002-B', '01-A-003-C', '01-A-004-D', '01-A-005-A',
        '02-B-010-A', '02-B-011-B', '03-A-020-C', '03-A-021-D', '02-A-030-A'
    ]
    
    for i, loc in enumerate(overcapacity_locations):
        # First pallet at location
        pallet1 = generate_valid_pallet()
        pallet1.update({
            'Pallet_ID': f'PLT960{i*2+1:02d}',
            'Location_Code': loc
        })
        anomalies.append(pallet1)
        
        # Second pallet at same location (causes overcapacity)
        pallet2 = generate_valid_pallet()
        pallet2.update({
            'Pallet_ID': f'PLT960{i*2+2:02d}',
            'Location_Code': loc
        })
        anomalies.append(pallet2)
    
    # Rule 5: DATA_INTEGRITY - Duplicate pallet IDs (5 violations)
    duplicate_ids = ['PLT950001', 'PLT950002', 'PLT950003', 'PLT950004', 'PLT950005']
    
    for dup_id in duplicate_ids:
        # First instance
        pallet1 = generate_valid_pallet()
        pallet1.update({
            'Pallet_ID': dup_id,
            'Location_Code': generate_correct_location_code(1, 'A', random.randint(1, 50), 'A')
        })
        anomalies.append(pallet1)
        
        # Duplicate instance
        pallet2 = generate_valid_pallet()
        pallet2.update({
            'Pallet_ID': dup_id,
            'Location_Code': generate_correct_location_code(2, 'B', random.randint(1, 50), 'B')
        })
        anomalies.append(pallet2)
    
    # Rule 6: TEMPERATURE_ZONE_MISMATCH - Temperature sensitive products in wrong zones (7 violations)
    temp_violations = [
        {'Pallet_ID': 'PLT940001', 'Product_Code': 'FROZEN_FISH_001', 'Location_Code': '01-A-001-A'},
        {'Pallet_ID': 'PLT940002', 'Product_Code': 'REFRIGERATED_DAIRY', 'Location_Code': '01-A-002-A'},
        {'Pallet_ID': 'PLT940003', 'Product_Code': 'ICE_CREAM_FROZEN', 'Location_Code': '01-A-003-A'},
        {'Pallet_ID': 'PLT940004', 'Product_Code': 'FROZEN_VEGETABLES', 'Location_Code': '02-B-001-A'},
        {'Pallet_ID': 'PLT940005', 'Product_Code': 'REFRIGERATED_MEAT', 'Location_Code': '02-B-002-A'},
        {'Pallet_ID': 'PLT940006', 'Product_Code': 'FROZEN_PIZZA_BOX', 'Location_Code': '03-A-001-A'},
        {'Pallet_ID': 'PLT940007', 'Product_Code': 'REFRIGERATED_JUICE', 'Location_Code': '03-A-002-A'}
    ]
    
    for violation in temp_violations:
        pallet = generate_valid_pallet()
        pallet.update(violation)
        anomalies.append(pallet)
    
    # Rule 7: LOCATION_SPECIFIC_STAGNANT - Pallets stuck in AISLE locations (10 violations)
    for i in range(10):
        pallet = generate_valid_pallet()
        # Create old timestamp (> 4 hours ago to trigger AISLE stuck pallets alert)
        old_date = (datetime.now() - timedelta(hours=random.randint(6, 24))).strftime('%Y-%m-%d %H:%M:%S')
        pallet.update({
            'Pallet_ID': f'PLT930{i+1:02d}',
            'Location_Code': f'AISLE-{random.choice(["01", "02", "03"])}',  # Valid AISLE areas
            'Received_Date': old_date,
            'Status': 'ACTIVE'
        })
        anomalies.append(pallet)
    
    return anomalies

def main():
    print("Generating Corrected WMS Test Data...")
    
    # Generate 720 valid pallets (90% of 800)
    print("Creating 720 valid pallet records with correct location format...")
    valid_pallets = []
    used_locations = set()
    used_pallet_ids = set()
    
    for _ in range(720):
        while True:
            pallet = generate_valid_pallet()
            # Ensure no duplicates in valid data
            if pallet['Location_Code'] not in used_locations and pallet['Pallet_ID'] not in used_pallet_ids:
                used_locations.add(pallet['Location_Code'])
                used_pallet_ids.add(pallet['Pallet_ID'])
                valid_pallets.append(pallet)
                break
    
    # Generate 80 anomalous pallets
    print("Creating 80 anomalous pallet records based on actual system rules...")
    anomalous_pallets = generate_anomalous_pallets()
    
    print(f"Generated {len(anomalous_pallets)} anomalous pallets")
    
    # Combine all pallets
    all_pallets = valid_pallets + anomalous_pallets
    random.shuffle(all_pallets)  # Randomize order
    
    # Create DataFrame
    df = pd.DataFrame(all_pallets)
    
    # Generate Excel file
    print("Generating corrected inventoryreport.xlsx...")
    df.to_excel('inventoryreport_corrected.xlsx', index=False, engine='openpyxl')
    
    print(f"Generated {len(all_pallets)} total pallet records")
    print(f"Valid records: {len(valid_pallets)}")
    print(f"Anomalous records: {len(anomalous_pallets)}")
    
    # Generate summary
    print("\n" + "="*50)
    print("CORRECTED ANOMALY SUMMARY REPORT")
    print("="*50)
    print(f"Total Anomalies Injected: {len(anomalous_pallets)}")
    print("Rule 1 (Stagnant Pallets - RECEIVING) Violations: 10")
    print("Rule 2 (Uncoordinated Lots) Violations: 8")
    print("Rule 3 (Invalid Location) Violations: 15")
    print("Rule 4 (Overcapacity) Violations: 20")
    print("Rule 5 (Data Integrity - Duplicates) Violations: 10")
    print("Rule 6 (Temperature Zone Mismatch) Violations: 7")
    print("Rule 7 (Location Specific Stagnant - AISLE) Violations: 10")
    print("="*50)
    print(f"Total: {10+8+15+20+10+7+10} violations")
    print("\nLocation format corrected to match warehouse expectations:")
    print("- Storage locations: 0X-Y-ZZZ-W (e.g., '01-A-001-A')")
    print("- Special areas: AREA-NN (e.g., 'RECV-02', 'AISLE-01')")

if __name__ == "__main__":
    main()