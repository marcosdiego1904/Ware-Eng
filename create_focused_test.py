#!/usr/bin/env python3
"""
Focused Test Generator for Lot Coordination and Overcapacity Detection
Creates small, targeted test cases for specific anomaly types
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_focused_test():
    """Create focused test data for lot coordination and overcapacity"""
    data = []
    
    print("Creating focused test for Lot Coordination and Overcapacity Detection")
    print("=" * 70)
    
    # =================================================================
    # SECTION 1: LOT COORDINATION TEST CASES
    # =================================================================
    print("\n1. Creating Lot Coordination Test Cases...")
    
    # Complete Lot (Control) - LOT-COMPLETE-001
    print("   - Complete Lot (LOT-COMPLETE-001): 20 pallets, all within 24h")
    base_time = datetime.now() - timedelta(hours=12)
    for i in range(20):
        data.append({
            'pallet_id': f'PLT-COMP-{i+1:03d}',
            'receipt_number': f'RCP-20250831-{1000+i}',
            'description': 'ELECTRONICS - Complete Lot',
            'lot_number': 'LOT-COMPLETE-001',
            'location': f'{(i%4)+1}-{((i//4)%2)+1:02d}-{(i%42)+1:02d}A',
            'creation_date': (base_time + timedelta(minutes=i*30)).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Incomplete Lot (75% complete) - LOT-INCOMPLETE-002  
    print("   - Incomplete Lot (LOT-INCOMPLETE-002): 15 pallets complete, 5 stragglers (3+ days late)")
    # 15 completed pallets (on time)
    complete_time = datetime.now() - timedelta(days=5)
    for i in range(15):
        data.append({
            'pallet_id': f'PLT-INCMP-{i+1:03d}',
            'receipt_number': f'RCP-20250826-{2000+i}',
            'description': 'AUTOMOTIVE - Incomplete Lot - Complete',
            'lot_number': 'LOT-INCOMPLETE-002',
            'location': f'{(i%4)+1}-{((i//4)%2)+1:02d}-{(i%42)+10:02d}B',
            'creation_date': (complete_time + timedelta(hours=i*2)).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 5 straggler pallets (late arrivals)
    straggler_time = datetime.now() - timedelta(days=1)  # 4 days after main lot
    for i in range(5):
        data.append({
            'pallet_id': f'PLT-STRAG-{i+1:03d}',
            'receipt_number': f'RCP-20250830-{2100+i}',
            'description': 'AUTOMOTIVE - Incomplete Lot - Straggler',
            'lot_number': 'LOT-INCOMPLETE-002',
            'location': f'{(i%4)+1}-{((i//4)%2)+1:02d}-{(i%42)+15:02d}C',
            'creation_date': (straggler_time + timedelta(hours=i*6)).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Mixed Timeline Lot - LOT-DELAYED-003
    print("   - Delayed Lot (LOT-DELAYED-003): 12 pallets spread over 2 weeks")
    start_time = datetime.now() - timedelta(days=14)
    for i in range(12):
        days_offset = random.randint(0, 14)  # Random arrival over 2 weeks
        data.append({
            'pallet_id': f'PLT-DELAY-{i+1:03d}',
            'receipt_number': f'RCP-2025081{7+days_offset//7}-{3000+i}',
            'description': 'TEXTILES - Delayed Lot',
            'lot_number': 'LOT-DELAYED-003',
            'location': f'{(i%4)+1}-{((i//4)%2)+1:02d}-{(i%42)+20:02d}D',
            'creation_date': (start_time + timedelta(days=days_offset, hours=i)).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    print(f"   Generated {20+15+5+12} pallets for lot coordination testing")
    
    # =================================================================
    # SECTION 2: STORAGE LOCATION OVERCAPACITY TEST CASES
    # =================================================================
    print("\n2. Creating Storage Location Overcapacity Test Cases...")
    
    # Target specific storage locations for overcapacity (capacity=1 each)
    overcap_storage_locations = ['1-01-01A', '2-01-01A', '3-01-01A']
    
    pallet_counter = 4000
    for location in overcap_storage_locations:
        # Put 3 pallets in each location (should trigger 2 overcapacity violations per location)
        print(f"   - Location {location}: 3 pallets (capacity=1, expect 2 violations)")
        for i in range(3):
            data.append({
                'pallet_id': f'PLT-OVER-{pallet_counter}',
                'receipt_number': f'RCP-20250831-{pallet_counter}',
                'description': f'OVERCAP STORAGE - {location}',
                'lot_number': f'LOT-OVERCAP-STORAGE-{location}',
                'location': location,
                'creation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            pallet_counter += 1
    
    print(f"   Generated {len(overcap_storage_locations)*3} pallets for storage overcapacity testing")
    
    # =================================================================
    # SECTION 3: SPECIAL LOCATION OVERCAPACITY TEST CASES  
    # =================================================================
    print("\n3. Creating Special Location Overcapacity Test Cases...")
    
    # Target special locations with controlled overcapacity
    special_overcap = [
        ('STAGE-01', 5, 8),    # Capacity 5, put 8 pallets (3 violations)
        ('DOCK-01', 2, 5),     # Capacity 2, put 5 pallets (3 violations) 
        ('RECV-01', 10, 12),   # Capacity 10, put 12 pallets (2 violations)
        ('AISLE-01', 10, 13)   # Capacity 10, put 13 pallets (3 violations)
    ]
    
    for location, capacity, pallets_to_add in special_overcap:
        violations = pallets_to_add - capacity
        print(f"   - {location}: {pallets_to_add} pallets (capacity={capacity}, expect {violations} violations)")
        for i in range(pallets_to_add):
            data.append({
                'pallet_id': f'PLT-SPEC-{pallet_counter}',
                'receipt_number': f'RCP-20250831-{pallet_counter}',
                'description': f'OVERCAP SPECIAL - {location}',
                'lot_number': f'LOT-OVERCAP-SPECIAL-{location}',
                'location': location,
                'creation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            pallet_counter += 1
    
    special_pallets = sum([pallets for _, _, pallets in special_overcap])
    print(f"   Generated {special_pallets} pallets for special location overcapacity testing")
    
    # =================================================================
    # SECTION 4: CONTROL PALLETS (VALID DATA)
    # =================================================================
    print("\n4. Adding Control Pallets (Valid Data)...")
    
    # Add some normal, valid pallets to ensure system doesn't flag everything
    for i in range(20):
        data.append({
            'pallet_id': f'PLT-CTRL-{i+1:03d}',
            'receipt_number': f'RCP-20250831-{5000+i}',
            'description': 'VALID CONTROL DATA',
            'lot_number': f'LOT-CONTROL-{(i//5)+1:03d}',
            'location': f'{(i%4)+1}-{((i//8)%2)+1:02d}-{(i%42)+25:02d}{chr(65+(i%4))}',
            'creation_date': (datetime.now() - timedelta(hours=random.randint(1, 48))).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    print(f"   Generated 20 control pallets for baseline validation")
    
    # =================================================================
    # GENERATE FINAL DATASET
    # =================================================================
    total_pallets = len(data)
    print(f"\nTotal pallets generated: {total_pallets}")
    print("\nExpected Anomalies:")
    print("- Lot Coordination: 5-17 anomalies (stragglers and delayed pallets)")
    print("- Storage Overcapacity: 6 anomalies (2 per location × 3 locations)")  
    print("- Special Overcapacity: 11 anomalies (3+3+2+3 violations)")
    print("- Total Expected: ~22-34 anomalies")
    
    # Create DataFrame and export
    df = pd.DataFrame(data)
    output_file = "inventoryreport.xlsx"
    df.to_excel(output_file, index=False)
    
    print(f"\n*** Successfully created {output_file} ***")
    print(f"Ready for testing lot coordination and overcapacity detection!")
    
    # Display sample data
    print(f"\nSample Data (first 10 rows):")
    print(df.head(10)[['pallet_id', 'lot_number', 'location', 'description']].to_string(index=False))
    
    return df

if __name__ == "__main__":
    create_focused_test()