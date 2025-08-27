import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

def generate_location_code(aisle, rack, position, level):
    """Generate valid location code in format: [Aisle][Rack]-[Position]-[Level]"""
    return f"{aisle}{rack}-{position:02d}-{level}"

def generate_special_area_code(area_type, number):
    """Generate special area location codes"""
    return f"{area_type}-{number:02d}"

def generate_valid_pallet():
    """Generate a valid pallet record"""
    pallet_id = f"PLT{random.randint(100000, 999999)}"
    
    # Generate valid location
    aisle = random.choice(['1', '2', '3'])
    rack = random.choice(['A', 'B'])
    position = random.randint(1, 42)
    level = random.choice(['A', 'B', 'C', 'D'])
    location = generate_location_code(aisle, rack, position, level)
    
    # Valid dimensions (within limits)
    length = round(random.uniform(1.0, 2.4), 2)  # Max 2.5m
    width = round(random.uniform(0.8, 1.4), 2)   # Max 1.5m
    height = round(random.uniform(0.5, 1.9), 2)  # Max 2.0m
    
    # Valid weight (reasonable for stacking)
    weight = round(random.uniform(100, 800), 1)  # Reasonable weight
    
    # Other valid fields
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
    """Generate pallets with specific rule violations"""
    anomalies = []
    
    # Rule 1: Stacking Weight Limit Violations (12 violations)
    base_location = "1A-15"
    heavy_pallets = [
        {'Pallet_ID': 'PLT999901', 'Location_Code': f'{base_location}-A', 'Weight_KG': 1500.0},
        {'Pallet_ID': 'PLT999902', 'Location_Code': f'{base_location}-B', 'Weight_KG': 1500.0},
        {'Pallet_ID': 'PLT999903', 'Location_Code': f'{base_location}-C', 'Weight_KG': 1500.0},
        {'Pallet_ID': 'PLT999904', 'Location_Code': f'{base_location}-D', 'Weight_KG': 1500.0}  # Total: 6000kg
    ]
    
    base_location2 = "2B-25"
    heavy_pallets2 = [
        {'Pallet_ID': 'PLT999905', 'Location_Code': f'{base_location2}-A', 'Weight_KG': 1200.0},
        {'Pallet_ID': 'PLT999906', 'Location_Code': f'{base_location2}-B', 'Weight_KG': 1200.0},
        {'Pallet_ID': 'PLT999907', 'Location_Code': f'{base_location2}-C', 'Weight_KG': 1200.0},
        {'Pallet_ID': 'PLT999908', 'Location_Code': f'{base_location2}-D', 'Weight_KG': 1200.0}  # Total: 4800kg
    ]
    
    base_location3 = "3A-10"
    heavy_pallets3 = [
        {'Pallet_ID': 'PLT999909', 'Location_Code': f'{base_location3}-A', 'Weight_KG': 1300.0},
        {'Pallet_ID': 'PLT999910', 'Location_Code': f'{base_location3}-B', 'Weight_KG': 1300.0},
        {'Pallet_ID': 'PLT999911', 'Location_Code': f'{base_location3}-C', 'Weight_KG': 1300.0},
        {'Pallet_ID': 'PLT999912', 'Location_Code': f'{base_location3}-D', 'Weight_KG': 1300.0}  # Total: 5200kg
    ]
    
    for pallet in heavy_pallets + heavy_pallets2 + heavy_pallets3:
        full_pallet = generate_valid_pallet()
        full_pallet.update(pallet)
        anomalies.append(full_pallet)
    
    # Rule 2: Duplicate Location Violations (10 violations - 5 pairs)
    duplicate_locations = ["3A-30-A", "1B-05-B", "2A-40-C", "3B-12-D", "1A-25-A"]
    for i, loc in enumerate(duplicate_locations):
        # First pallet at location
        pallet1 = generate_valid_pallet()
        pallet1.update({
            'Pallet_ID': f'PLT888{i*2+1:02d}',
            'Location_Code': loc
        })
        anomalies.append(pallet1)
        
        # Duplicate pallet at same location
        pallet2 = generate_valid_pallet()
        pallet2.update({
            'Pallet_ID': f'PLT888{i*2+2:02d}',
            'Location_Code': loc
        })
        anomalies.append(pallet2)
    
    # Rule 3: Oversized Pallet Violations (8 violations)
    oversized_violations = [
        {'Pallet_ID': 'PLT777701', 'Length_M': 3.0, 'Width_M': 1.2, 'Height_M': 1.5},  # Length too big
        {'Pallet_ID': 'PLT777702', 'Length_M': 2.0, 'Width_M': 2.0, 'Height_M': 1.5},  # Width too big
        {'Pallet_ID': 'PLT777703', 'Length_M': 2.0, 'Width_M': 1.2, 'Height_M': 2.5},  # Height too big
        {'Pallet_ID': 'PLT777704', 'Length_M': 2.8, 'Width_M': 1.8, 'Height_M': 1.5},  # Length and Width too big
        {'Pallet_ID': 'PLT777705', 'Length_M': 2.6, 'Width_M': 1.2, 'Height_M': 2.3},  # Length and Height too big
        {'Pallet_ID': 'PLT777706', 'Length_M': 2.0, 'Width_M': 1.7, 'Height_M': 2.2},  # Width and Height too big
        {'Pallet_ID': 'PLT777707', 'Length_M': 3.2, 'Width_M': 1.8, 'Height_M': 2.4},  # All dimensions too big
        {'Pallet_ID': 'PLT777708', 'Length_M': 2.7, 'Width_M': 1.6, 'Height_M': 1.5}   # Length and Width too big
    ]
    
    for violation in oversized_violations:
        pallet = generate_valid_pallet()
        pallet.update(violation)
        anomalies.append(pallet)
    
    # Rule 4: Invalid Location Code Violations (10 violations)
    invalid_locations = [
        'PLT666601', '4A-01-A',    # Invalid aisle (should be 1-3)
        'PLT666602', '1C-01-A',    # Invalid rack (should be A or B)
        'PLT666603', '1A-43-A',    # Invalid position (should be 1-42)
        'PLT666604', '1A-01-E',    # Invalid level (should be A-D)
        'PLT666605', '1A-1-A',     # Invalid format (position not zero-padded)
        'PLT666606', '1A01A',      # Invalid format (missing separators)
        'PLT666607', 'A1-01-A',    # Invalid format (aisle/rack swapped)
        'PLT666608', '1A-00-A',    # Invalid position (position 0)
        'PLT666609', 'INVALID-LOC', # Completely invalid format
        'PLT666610', '1A-01-'      # Incomplete location code
    ]
    
    for i in range(0, len(invalid_locations), 2):
        pallet = generate_valid_pallet()
        pallet.update({
            'Pallet_ID': invalid_locations[i],
            'Location_Code': invalid_locations[i+1]
        })
        anomalies.append(pallet)
    
    # Rule 5: Capacity Violations - Exceeding special area capacity (10 violations)
    capacity_violations = [
        # RECEIVING area has capacity 10, adding 11th pallet
        {'Pallet_ID': 'PLT333301', 'Location_Code': 'RECEIVING-11'},
        {'Pallet_ID': 'PLT333302', 'Location_Code': 'RECEIVING-12'},
        {'Pallet_ID': 'PLT333303', 'Location_Code': 'RECEIVING-13'},
        # STAGING area has capacity 5, adding 6th+ pallets  
        {'Pallet_ID': 'PLT333304', 'Location_Code': 'STAGING-06'},
        {'Pallet_ID': 'PLT333305', 'Location_Code': 'STAGING-07'},
        {'Pallet_ID': 'PLT333306', 'Location_Code': 'STAGING-08'},
        # DOCK area has capacity 2, adding 3rd+ pallets
        {'Pallet_ID': 'PLT333307', 'Location_Code': 'DOCK-03'},
        {'Pallet_ID': 'PLT333308', 'Location_Code': 'DOCK-04'},
        {'Pallet_ID': 'PLT333309', 'Location_Code': 'DOCK-05'},
        {'Pallet_ID': 'PLT333310', 'Location_Code': 'DOCK-06'}
    ]
    
    for violation in capacity_violations:
        pallet = generate_valid_pallet()
        pallet.update(violation)
        anomalies.append(pallet)
    
    # Rule 6: Negative/Zero Values Violations (18 violations)
    negative_violations = [
        {'Pallet_ID': 'PLT555501', 'Weight_KG': -50.0},
        {'Pallet_ID': 'PLT555502', 'Weight_KG': 0.0},
        {'Pallet_ID': 'PLT555503', 'Length_M': -1.5},
        {'Pallet_ID': 'PLT555504', 'Width_M': 0.0},
        {'Pallet_ID': 'PLT555505', 'Height_M': -0.8},
        {'Pallet_ID': 'PLT555506', 'Quantity': -10},
        {'Pallet_ID': 'PLT555507', 'Quantity': 0},
        {'Pallet_ID': 'PLT555508', 'Weight_KG': -100.0, 'Length_M': -2.0},
        {'Pallet_ID': 'PLT555509', 'Width_M': 0.0, 'Height_M': 0.0},
        {'Pallet_ID': 'PLT555510', 'Weight_KG': -25.0, 'Quantity': -5},
        {'Pallet_ID': 'PLT555511', 'Length_M': -1.2, 'Width_M': -0.9, 'Height_M': -1.1},
        {'Pallet_ID': 'PLT555512', 'Weight_KG': 0.0, 'Quantity': 0},
        {'Pallet_ID': 'PLT555513', 'Weight_KG': -75.5},
        {'Pallet_ID': 'PLT555514', 'Length_M': -2.1},
        {'Pallet_ID': 'PLT555515', 'Width_M': -1.3},
        {'Pallet_ID': 'PLT555516', 'Height_M': -1.7},
        {'Pallet_ID': 'PLT555517', 'Quantity': -25},
        {'Pallet_ID': 'PLT555518', 'Weight_KG': -200.0, 'Width_M': -1.1, 'Quantity': -3}
    ]
    
    for violation in negative_violations:
        pallet = generate_valid_pallet()
        pallet.update(violation)
        anomalies.append(pallet)
    
    # Rule 7: Special Area Misuse Violations (12 violations)
    special_area_violations = [
        {'Pallet_ID': 'PLT444401', 'Location_Code': 'RECEIVING-01', 'Status': 'ACTIVE'},  # Should be PENDING in RECEIVING
        {'Pallet_ID': 'PLT444402', 'Location_Code': 'RECEIVING-02', 'Status': 'RESERVED'}, # Should be PENDING in RECEIVING
        {'Pallet_ID': 'PLT444403', 'Location_Code': 'STAGING-01', 'Status': 'PENDING'},   # Should be ACTIVE in STAGING
        {'Pallet_ID': 'PLT444404', 'Location_Code': 'STAGING-02', 'Status': 'RESERVED'},  # Should be ACTIVE in STAGING
        {'Pallet_ID': 'PLT444405', 'Location_Code': 'DOCK-01', 'Status': 'PENDING'},      # Should be RESERVED in DOCK
        {'Pallet_ID': 'PLT444406', 'Location_Code': 'DOCK-02', 'Status': 'ACTIVE'},      # Should be RESERVED in DOCK
        {'Pallet_ID': 'PLT444407', 'Location_Code': 'RECEIVING-03', 'Status': 'ACTIVE'},
        {'Pallet_ID': 'PLT444408', 'Location_Code': 'RECEIVING-04', 'Status': 'RESERVED'},
        {'Pallet_ID': 'PLT444409', 'Location_Code': 'STAGING-03', 'Status': 'PENDING'},
        {'Pallet_ID': 'PLT444410', 'Location_Code': 'STAGING-04', 'Status': 'RESERVED'},
        {'Pallet_ID': 'PLT444411', 'Location_Code': 'RECEIVING-05', 'Status': 'RESERVED'},
        {'Pallet_ID': 'PLT444412', 'Location_Code': 'STAGING-05', 'Status': 'PENDING'}
    ]
    
    for violation in special_area_violations:
        pallet = generate_valid_pallet()
        pallet.update(violation)
        anomalies.append(pallet)
    
    return anomalies

def main():
    print("Generating WMS Test Data...")
    
    # Generate 720 valid pallets
    print("Creating 720 valid pallet records...")
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
    print("Creating 80 anomalous pallet records...")
    anomalous_pallets = generate_anomalous_pallets()
    
    # Combine all pallets
    all_pallets = valid_pallets + anomalous_pallets
    random.shuffle(all_pallets)  # Randomize order
    
    # Create DataFrame
    df = pd.DataFrame(all_pallets)
    
    # Generate Excel file
    print("Generating inventoryreport.xlsx...")
    df.to_excel('inventoryreport.xlsx', index=False, engine='openpyxl')
    
    print(f"Generated {len(all_pallets)} total pallet records")
    print(f"Valid records: {len(valid_pallets)}")
    print(f"Anomalous records: {len(anomalous_pallets)}")
    
    # Generate summary
    print("\n" + "="*50)
    print("ANOMALY SUMMARY REPORT")
    print("="*50)
    print(f"Total Anomalies Injected: {len(anomalous_pallets)}")
    print("Rule 1 (Stacking Weight Limit) Violations: 12")
    print("Rule 2 (Duplicate Location) Violations: 10") 
    print("Rule 3 (Oversized Pallet) Violations: 8")
    print("Rule 4 (Invalid Location Code) Violations: 10")
    print("Rule 5 (Capacity Violation) Violations: 10")
    print("Rule 6 (Negative/Zero Values) Violations: 18")
    print("Rule 7 (Special Area Misuse) Violations: 12")
    print("="*50)
    print(f"Total: {12+10+8+10+10+18+12} violations")

if __name__ == "__main__":
    main()