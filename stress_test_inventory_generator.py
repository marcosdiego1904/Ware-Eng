#!/usr/bin/env python3
"""
WAREWISE SYSTEM STRESS TEST INVENTORY GENERATOR
==============================================

Creates large-scale test inventories to stress test the WareWise rule engine:
- 1K, 5K, 10K, 25K, and 50K record datasets
- Uses correct USER_MARCOS9 warehouse location formats  
- Maintains surgical anomaly precision at scale
- Includes performance benchmarking capabilities

Based on USER_MARCOS9 warehouse structure:
- Storage: XX-XX-XXXA/B format (01-01-001A to 02-01-029B)
- Special: RECV-01, RECV-02, STAGE-01, DOCK-01, AISLE-01
- Total capacity: 469 locations
"""

import pandas as pd
from datetime import datetime, timedelta
import random
import math
import csv
import os
from typing import List, Dict, Tuple

class WarehouseStressTestGenerator:
    """Generates large-scale stress test inventories with precise anomaly targeting"""
    
    def __init__(self):
        self.now = datetime.now()
        
        # USER_MARCOS9 warehouse location formats
        self.storage_locations = self._generate_storage_locations()
        self.special_locations = ['RECV-01', 'RECV-02', 'STAGE-01', 'DOCK-01', 'AISLE-01']
        self.all_valid_locations = self.storage_locations + self.special_locations
        
        # Anomaly targeting configuration
        self.anomaly_config = {
            'stagnant_pallets_rate': 0.02,      # 2% of pallets are stagnant (>10h in RECV)
            'uncoordinated_lots_rate': 0.005,   # 0.5% are lot stragglers  
            'overcapacity_locations': 0.01,     # 1% of locations are overcapacity
            'invalid_locations_rate': 0.003,    # 0.3% have invalid locations
            'aisle_stagnant_rate': 0.008,       # 0.8% stuck in AISLE (>4h)
            'duplicate_rate': 0.002,            # 0.2% are duplicates
            'impossible_location_rate': 0.001   # 0.1% impossible locations
        }
        
        print("WAREWISE STRESS TEST GENERATOR")
        print("==============================")
        print(f"Warehouse: USER_MARCOS9")
        print(f"Valid locations: {len(self.all_valid_locations)}")
        print(f"Storage positions: {len(self.storage_locations)}")
        print(f"Special areas: {len(self.special_locations)}")
        
    def _generate_storage_locations(self) -> List[str]:
        """Generate all valid USER_MARCOS9 storage location codes"""
        locations = []
        
        # Based on debug logs: 2 aisles × 1 rack × 29 positions × 4 levels  
        for aisle in ['01', '02']:
            for rack in ['01']:  # Only 1 rack per aisle
                for position in range(1, 30):  # 29 positions (001-029)
                    for level in ['A', 'B', 'C', 'D']:  # 4 levels
                        location = f"{aisle}-{rack}-{position:03d}{level}"
                        locations.append(location)
        
        return locations
    
    def generate_stress_inventory(self, target_size: int) -> List[Dict]:
        """Generate large-scale stress test inventory with precise anomaly targeting"""
        
        print(f"\nGenerating {target_size:,} record stress test inventory...")
        
        # Calculate target anomalies based on rates
        target_anomalies = self._calculate_target_anomalies(target_size)
        print(f"Target anomalies: {sum(target_anomalies.values())} total")
        
        # Generate base inventory (clean records)
        clean_records = target_size - sum(target_anomalies.values())
        print(f"Clean records: {clean_records:,}")
        
        inventory = []
        
        # Generate clean baseline inventory
        inventory.extend(self._generate_clean_inventory(clean_records))
        
        # Add surgical anomalies
        inventory.extend(self._generate_stagnant_pallets(target_anomalies['stagnant_pallets']))
        inventory.extend(self._generate_uncoordinated_lots(target_anomalies['uncoordinated_lots']))
        inventory.extend(self._generate_overcapacity_anomalies(target_anomalies['overcapacity']))
        inventory.extend(self._generate_invalid_locations(target_anomalies['invalid_locations']))
        inventory.extend(self._generate_aisle_stagnant(target_anomalies['aisle_stagnant']))
        inventory.extend(self._generate_duplicates(target_anomalies['duplicates']))
        inventory.extend(self._generate_impossible_locations(target_anomalies['impossible_locations']))
        
        # Shuffle to distribute anomalies randomly
        random.shuffle(inventory)
        
        print(f"Generated inventory: {len(inventory):,} records")
        return inventory
    
    def _calculate_target_anomalies(self, total_size: int) -> Dict[str, int]:
        """Calculate target anomaly counts based on rates"""
        return {
            'stagnant_pallets': max(5, int(total_size * self.anomaly_config['stagnant_pallets_rate'])),
            'uncoordinated_lots': max(3, int(total_size * self.anomaly_config['uncoordinated_lots_rate'])),
            'overcapacity': max(2, int(total_size * self.anomaly_config['overcapacity_locations'])),
            'invalid_locations': max(2, int(total_size * self.anomaly_config['invalid_locations_rate'])),
            'aisle_stagnant': max(3, int(total_size * self.anomaly_config['aisle_stagnant_rate'])),
            'duplicates': max(4, int(total_size * self.anomaly_config['duplicate_rate'])),
            'impossible_locations': max(2, int(total_size * self.anomaly_config['impossible_location_rate']))
        }
    
    def _generate_clean_inventory(self, count: int) -> List[Dict]:
        """Generate clean operational records"""
        records = []
        
        for i in range(count):
            # Random valid location  
            location = random.choice(self.all_valid_locations)
            
            # Safe time range (1-8 hours ago for storage, 1-9h for RECV)
            if location.startswith('RECV'):
                hours_ago = random.uniform(1, 9)  # Under 10h threshold
            elif location.startswith('AISLE'):
                hours_ago = random.uniform(0.1, 3.8)  # Under 4h threshold
            else:
                hours_ago = random.uniform(1, 8)
                
            created = self.now - timedelta(hours=hours_ago)
            
            records.append({
                'pallet_id': f'CLN-{i+1:06d}',
                'location': location,
                'creation_date': created.strftime('%Y-%m-%d %H:%M:%S'),
                'receipt_number': f'RCT-CLEAN-{i+1:06d}',
                'description': f'Clean Product {random.choice(["A", "B", "C", "D", "E"])}'
            })
        
        return records
    
    def _generate_stagnant_pallets(self, count: int) -> List[Dict]:
        """Generate stagnant pallets (>10h in RECV locations)"""
        records = []
        
        for i in range(count):
            # Use RECV locations only
            location = random.choice(['RECV-01', 'RECV-02'])
            
            # 11-48 hours ago (well over 10h threshold)
            hours_ago = random.uniform(11, 48)
            created = self.now - timedelta(hours=hours_ago)
            
            records.append({
                'pallet_id': f'STAG-{i+1:05d}',
                'location': location,
                'creation_date': created.strftime('%Y-%m-%d %H:%M:%S'),
                'receipt_number': f'RCT-STAG-{i+1:05d}',
                'description': f'Stagnant Product {i+1}'
            })
        
        return records
    
    def _generate_uncoordinated_lots(self, count: int) -> List[Dict]:
        """Generate uncoordinated lot scenarios (80%+ completion with stragglers)"""
        records = []
        
        for i in range(count):
            lot_id = f'LOT-UNCOORD-{i+1:03d}'
            lot_size = random.randint(8, 15)  # 8-15 pallet lots
            
            # 80-90% in storage (triggers threshold)
            stored_count = max(int(lot_size * random.uniform(0.8, 0.9)), lot_size - 2)
            straggler_count = lot_size - stored_count
            
            created_time = self.now - timedelta(hours=random.uniform(6, 24))
            
            # Generate stored pallets
            for j in range(stored_count):
                storage_loc = random.choice(self.storage_locations)
                records.append({
                    'pallet_id': f'{lot_id}-STORED-{j+1:02d}',
                    'location': storage_loc,
                    'creation_date': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'receipt_number': lot_id,
                    'description': f'Lot Product {j+1}'
                })
            
            # Generate stragglers in RECV (triggers anomaly)
            for j in range(straggler_count):
                records.append({
                    'pallet_id': f'{lot_id}-STRAGGLER-{j+1:02d}', 
                    'location': random.choice(['RECV-01', 'RECV-02']),
                    'creation_date': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'receipt_number': lot_id,
                    'description': f'Lot Straggler {j+1}'
                })
        
        return records
    
    def _generate_overcapacity_anomalies(self, count: int) -> List[Dict]:
        """Generate overcapacity situations"""
        records = []
        
        # Create scenarios where locations have 2x+ their normal capacity
        locations_to_overfill = random.sample(self.storage_locations[:50], min(count, 50))
        
        for i, location in enumerate(locations_to_overfill):
            # Assume normal capacity is 2-4 pallets, create 6-12 pallets
            pallets_in_location = random.randint(6, 12)
            
            created_base = self.now - timedelta(hours=random.uniform(1, 6))
            
            for j in range(pallets_in_location):
                records.append({
                    'pallet_id': f'OVER-{i+1:03d}-{j+1:02d}',
                    'location': location,
                    'creation_date': (created_base - timedelta(minutes=j*5)).strftime('%Y-%m-%d %H:%M:%S'),
                    'receipt_number': f'RCT-OVER-{i+1:03d}',
                    'description': f'Overcapacity Product {j+1}'
                })
        
        return records
    
    def _generate_invalid_locations(self, count: int) -> List[Dict]:
        """Generate clearly invalid location formats"""
        records = []
        
        invalid_patterns = [
            'INVALID_LOC_{}',
            'BAD-FORMAT-{}', 
            'WRONG_PATTERN_{}',
            'MISSING-LOCATION-{}',
            'ERROR_CODE_{}'
        ]
        
        for i in range(count):
            pattern = random.choice(invalid_patterns)
            invalid_location = pattern.format(f'{i+1:03d}')
            
            records.append({
                'pallet_id': f'INVALID-{i+1:04d}',
                'location': invalid_location,
                'creation_date': (self.now - timedelta(hours=random.uniform(1, 12))).strftime('%Y-%m-%d %H:%M:%S'),
                'receipt_number': f'RCT-INVALID-{i+1:04d}',
                'description': f'Invalid Location Product {i+1}'
            })
        
        return records
    
    def _generate_aisle_stagnant(self, count: int) -> List[Dict]:
        """Generate AISLE location stagnant pallets (>4h threshold)"""
        records = []
        
        for i in range(count):
            # Use AISLE-01 location
            location = 'AISLE-01'
            
            # 5-12 hours ago (over 4h threshold) 
            hours_ago = random.uniform(5, 12)
            created = self.now - timedelta(hours=hours_ago)
            
            records.append({
                'pallet_id': f'AISLE-STAG-{i+1:04d}',
                'location': location,
                'creation_date': created.strftime('%Y-%m-%d %H:%M:%S'),
                'receipt_number': f'RCT-AISLE-{i+1:04d}',
                'description': f'Aisle Stagnant Product {i+1}'
            })
        
        return records
    
    def _generate_duplicates(self, count: int) -> List[Dict]:
        """Generate duplicate pallet IDs for integrity testing"""
        records = []
        
        # Generate pairs of duplicates
        for i in range(0, count, 2):
            duplicate_id = f'DUPLICATE-{i//2+1:04d}'
            
            created_time = self.now - timedelta(hours=random.uniform(1, 8))
            
            # First instance
            records.append({
                'pallet_id': duplicate_id,
                'location': random.choice(['RECV-01', 'RECV-02']),
                'creation_date': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                'receipt_number': f'RCT-DUP-{i//2+1:04d}-A',
                'description': f'Duplicate Product A'
            })
            
            # Second instance (creates duplicate)
            if i + 1 < count:
                records.append({
                    'pallet_id': duplicate_id,
                    'location': random.choice(self.storage_locations),
                    'creation_date': (created_time + timedelta(minutes=random.randint(30, 180))).strftime('%Y-%m-%d %H:%M:%S'),
                    'receipt_number': f'RCT-DUP-{i//2+1:04d}-B',
                    'description': f'Duplicate Product B'
                })
        
        return records
    
    def _generate_impossible_locations(self, count: int) -> List[Dict]:
        """Generate impossibly long/corrupted location codes"""
        records = []
        
        impossible_patterns = [
            'IMPOSSIBLY_LONG_LOCATION_CODE_INDICATING_SEVERE_SYSTEM_ERROR_OR_DATA_CORRUPTION_{}',
            'CORRUPTED_DATABASE_ENTRY_WITH_EXCESSIVE_LENGTH_AND_INVALID_CHARACTERS_{}',
            'SYSTEM_ERROR_LOCATION_CODE_OVERFLOW_BUFFER_EXCEPTION_DETECTED_{}'
        ]
        
        for i in range(count):
            pattern = random.choice(impossible_patterns)
            impossible_location = pattern.format(f'{i+1:03d}')
            
            records.append({
                'pallet_id': f'IMPOSSIBLE-{i+1:04d}',
                'location': impossible_location,
                'creation_date': (self.now - timedelta(hours=random.uniform(1, 6))).strftime('%Y-%m-%d %H:%M:%S'),
                'receipt_number': f'RCT-IMPOSSIBLE-{i+1:04d}',
                'description': f'Impossible Location Product {i+1}'
            })
        
        return records
    
    def save_inventory(self, inventory: List[Dict], size_label: str):
        """Save inventory to CSV and Excel files"""
        
        df = pd.DataFrame(inventory)
        
        csv_file = f'stress_test_inventory_{size_label}.csv'
        excel_file = f'stress_test_inventory_{size_label}.xlsx'
        
        # Save CSV
        df.to_csv(csv_file, index=False)
        
        # Save Excel 
        df.to_excel(excel_file, index=False, engine='openpyxl')
        
        # File size info
        csv_size = os.path.getsize(csv_file) / (1024 * 1024)  # MB
        excel_size = os.path.getsize(excel_file) / (1024 * 1024)  # MB
        
        print(f"Files saved:")
        print(f"  CSV: {csv_file} ({csv_size:.1f} MB)")
        print(f"  Excel: {excel_file} ({excel_size:.1f} MB)")
        
        return csv_file, excel_file

def main():
    """Generate multiple stress test datasets"""
    
    generator = WarehouseStressTestGenerator()
    
    # Graduated stress test sizes
    test_sizes = [
        (1_000, "1K"),
        (5_000, "5K"), 
        (10_000, "10K"),
        (25_000, "25K"),
        (50_000, "50K")
    ]
    
    print(f"\nGenerating {len(test_sizes)} stress test datasets...")
    
    results = []
    
    for size, label in test_sizes:
        print(f"\n{'='*60}")
        print(f"GENERATING {label} STRESS TEST ({size:,} records)")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        
        # Generate inventory
        inventory = generator.generate_stress_inventory(size)
        
        # Save files
        csv_file, excel_file = generator.save_inventory(inventory, label)
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        # Calculate expected anomalies
        target_anomalies = generator._calculate_target_anomalies(size)
        total_expected = sum(target_anomalies.values())
        
        results.append({
            'size': size,
            'label': label,
            'csv_file': csv_file,
            'excel_file': excel_file,
            'generation_time': generation_time,
            'expected_anomalies': total_expected,
            'anomaly_breakdown': target_anomalies
        })
        
        print(f"Generation time: {generation_time:.2f} seconds")
        print(f"Expected anomalies: {total_expected}")
        print(f"Records per second: {size / generation_time:.0f}")
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"STRESS TEST GENERATION COMPLETE")
    print(f"{'='*80}")
    
    for result in results:
        print(f"\n{result['label']} Dataset ({result['size']:,} records):")
        print(f"  Files: {result['csv_file']}, {result['excel_file']}")
        print(f"  Expected anomalies: {result['expected_anomalies']}")
        print(f"  Generation time: {result['generation_time']:.2f}s")
    
    print(f"\nSTRESS TESTING RECOMMENDATIONS:")
    print(f"1. Start with 1K dataset to verify anomaly detection accuracy")
    print(f"2. Progress through 5K → 10K → 25K → 50K to test scalability")  
    print(f"3. Monitor memory usage and execution time at each scale")
    print(f"4. Expected behavior: Linear scaling with consistent anomaly rates")
    print(f"\nAll datasets use correct USER_MARCOS9 warehouse location formats!")

if __name__ == "__main__":
    # Set random seed for reproducible results
    random.seed(42)
    main()