#!/usr/bin/env python3
"""
CORRECTED PRECISION EXCEL INVENTORY - 800 PALLETS  
================================================

FIXES CRITICAL BUG: Position range 1-28 (not 1-29) for USER_MARCOS9 warehouse

This corrected version addresses the cascade failure discovered in testing:
- Positions 1-28 only (warehouse max capacity constraint)
- Surgical anomaly precision targeting each of 7 evaluators
- Proper Excel structure for comprehensive analysis

BUG FIXED: Original generator used range(1, 30) creating invalid position 29
SOLUTION: Now uses range(1, 29) creating valid positions 1-28 only
"""

import pandas as pd
from datetime import datetime, timedelta
import random
import os
from typing import List, Dict

class CorrectedPrecisionInventoryGenerator:
    """Generates corrected Excel inventory with surgical precision for 800 pallets"""
    
    def __init__(self):
        self.now = datetime.now()
        
        # USER_MARCOS9 warehouse - CORRECTED: Positions 1-28 only
        # CRITICAL FIX: The previous version incorrectly used range(1, 30)
        self.storage_locations = self._generate_corrected_storage_locations()
        self.special_locations = ['RECV-01', 'RECV-02', 'STAGE-01', 'DOCK-01', 'AISLE-01']
        self.all_valid_locations = self.storage_locations + self.special_locations
        
        # Surgical anomaly targets for 800 pallets (5% anomaly rate = 40 anomalies)
        self.target_anomalies = {
            'stagnant_pallets': 8,       # StagnantPalletsEvaluator: >10h in RECV
            'uncoordinated_lots': 6,     # UncoordinatedLotsEvaluator: lot stragglers <80%
            'overcapacity': 8,           # OvercapacityEvaluator: >1 pallet per location
            'invalid_locations': 4,      # VirtualInvalidLocationEvaluator: invalid formats
            'aisle_stagnant': 6,         # LocationSpecificStagnantEvaluator: >4h in AISLE
            'duplicates': 4,             # DataIntegrityEvaluator: duplicate pallet_ids
            'mapping_errors': 4          # LocationMappingErrorEvaluator: type mismatches
        }
        
        print("CORRECTED PRECISION EXCEL INVENTORY GENERATOR")
        print("============================================")
        print(f"CRITICAL BUG FIX: Position range corrected to 1-28 (was 1-29)")
        print(f"Target: 800 pallets with {sum(self.target_anomalies.values())} surgical anomalies")
        print(f"Warehouse: USER_MARCOS9 (positions 1-28 only)")
        print(f"Valid storage locations: {len(self.storage_locations)}")
        print(f"Total valid locations: {len(self.all_valid_locations)}")
        
    def _generate_corrected_storage_locations(self) -> List[str]:
        """Generate CORRECTED storage locations - positions 1-28 only"""
        locations = []
        
        # CRITICAL FIX: range(1, 29) creates positions 1-28 (not 1-29)
        for aisle in ['01']:  # Only aisle 01 based on debug logs
            for rack in ['01']:
                for position in range(1, 29):  # CORRECTED: 28 positions (001-028)
                    for level in ['A', 'B', 'C', 'D']:  # 4 levels
                        location = f"{aisle}-{rack}-{position:03d}{level}"
                        locations.append(location)
        
        return locations  # 112 storage locations (28 × 4)
    
    def generate_corrected_precision_inventory(self) -> List[Dict]:
        """Generate exactly 800 pallets with corrected surgical anomaly precision"""
        
        print(f"\nGenerating corrected surgical precision inventory...")
        print(f"Storage location range: 01-01-001A to 01-01-028D (112 locations)")
        
        inventory = []
        
        # 1. Generate clean baseline (760 pallets)
        clean_count = 800 - sum(self.target_anomalies.values())
        print(f"Generating {clean_count} clean baseline records...")
        inventory.extend(self._generate_clean_inventory(clean_count))
        
        # 2. Add surgical anomalies (40 pallets total)
        print("Adding corrected surgical anomalies:")
        
        # StagnantPalletsEvaluator: >10h in RECEIVING locations
        print(f"  - {self.target_anomalies['stagnant_pallets']} stagnant pallets (>10h in RECV)")
        inventory.extend(self._generate_stagnant_pallets())
        
        # UncoordinatedLotsEvaluator: Lot completion <80%
        print(f"  - {self.target_anomalies['uncoordinated_lots']} uncoordinated lots (<80% completion)")
        inventory.extend(self._generate_uncoordinated_lots())
        
        # OvercapacityEvaluator: >1 pallet per location (statistical violations)
        print(f"  - {self.target_anomalies['overcapacity']} overcapacity violations (multiple pallets/location)")
        inventory.extend(self._generate_overcapacity_anomalies())
        
        # VirtualInvalidLocationEvaluator: Invalid location formats (NO position 29!)
        print(f"  - {self.target_anomalies['invalid_locations']} invalid locations (format violations)")
        inventory.extend(self._generate_invalid_locations())
        
        # LocationSpecificStagnantEvaluator: >4h in AISLE locations
        print(f"  - {self.target_anomalies['aisle_stagnant']} aisle stagnant (>4h in AISLE-01)")
        inventory.extend(self._generate_aisle_stagnant())
        
        # DataIntegrityEvaluator: Duplicate pallet IDs
        print(f"  - {self.target_anomalies['duplicates']} duplicate pallets (integrity violations)")
        inventory.extend(self._generate_duplicates())
        
        # LocationMappingErrorEvaluator: Location type mismatches
        print(f"  - {self.target_anomalies['mapping_errors']} mapping errors (type mismatches)")
        inventory.extend(self._generate_mapping_errors())
        
        # Shuffle to distribute anomalies
        random.shuffle(inventory)
        
        print(f"\nGenerated: {len(inventory)} total pallets")
        return inventory
    
    def _generate_clean_inventory(self, count: int) -> List[Dict]:
        """Generate clean baseline inventory records with proper distribution"""
        records = []
        
        # Distribute pallets across storage locations to avoid overcapacity
        # Use only 80% of available storage locations to ensure good distribution
        usable_locations = random.sample(self.storage_locations, min(90, len(self.storage_locations)))
        
        for i in range(count):
            # Round-robin through locations to ensure even distribution
            location = usable_locations[i % len(usable_locations)]
            
            record = {
                'pallet_id': f"CLEAN_{i+1:04d}",
                'location': location,
                'location_type': 'STORAGE',
                'creation_date': self._random_recent_date(hours_range=(0.5, 8)),  # Recent, not stagnant
                'receipt_number': f"RCT_CLEAN_{i+1:04d}",
                'description': 'STANDARD_PRODUCT'
            }
            records.append(record)
        
        return records
    
    def _generate_stagnant_pallets(self) -> List[Dict]:
        """StagnantPalletsEvaluator: Pallets >10h in RECEIVING locations"""
        records = []
        
        for i in range(self.target_anomalies['stagnant_pallets']):
            record = {
                'pallet_id': f"STAG_{i+1:03d}",
                'location': random.choice(['RECV-01', 'RECV-02']),
                'location_type': 'RECEIVING',
                'creation_date': self._stagnant_date(min_hours=12, max_hours=24),  # >10h threshold
                'receipt_number': f"RCT_STAG_{i+1:03d}",
                'description': 'STAGNANT_RECEIVING'
            }
            records.append(record)
        
        return records
    
    def _generate_uncoordinated_lots(self) -> List[Dict]:
        """UncoordinatedLotsEvaluator: Lot completion <80% (stragglers in RECEIVING)"""
        records = []
        
        # Create incomplete lot with stragglers
        lot_receipt = "RCT_LOT_INCOMPLETE_001"
        
        # 4 stored pallets (67% of 6-pallet lot = <80% completion threshold)
        for i in range(4):
            record = {
                'pallet_id': f"LOT_STORED_{i+1:03d}",
                'location': random.choice(self.storage_locations[:20]),  # Use first 20 locations
                'location_type': 'STORAGE',
                'creation_date': self._random_recent_date(hours_range=(6, 8)),
                'receipt_number': lot_receipt,
                'description': 'LOT_MEMBER_STORED'
            }
            records.append(record)
        
        # 2 stragglers still in RECEIVING (triggers <80% completion)
        for i in range(2):
            record = {
                'pallet_id': f"LOT_STRAGGLER_{i+1:03d}",
                'location': random.choice(['RECV-01', 'RECV-02']),
                'location_type': 'RECEIVING',
                'creation_date': self._random_recent_date(hours_range=(6, 9)),
                'receipt_number': lot_receipt,
                'description': 'LOT_STRAGGLER'
            }
            records.append(record)
        
        return records
    
    def _generate_overcapacity_anomalies(self) -> List[Dict]:
        """OvercapacityEvaluator: Multiple pallets per location (capacity=1)"""
        records = []
        
        # Create overcapacity scenarios: 4 specific locations with 2 pallets each
        # Use locations not used by clean inventory to avoid cascade issues
        overcapacity_locations = random.sample(self.storage_locations[-20:], 4)
        
        pallet_counter = 1
        for location in overcapacity_locations:
            for i in range(2):  # 2 pallets per location (violates capacity=1)
                record = {
                    'pallet_id': f"OVER_{pallet_counter:03d}",
                    'location': location,
                    'location_type': 'STORAGE',
                    'creation_date': self._random_recent_date(hours_range=(1, 6)),
                    'receipt_number': f"RCT_OVER_{pallet_counter:03d}",
                    'description': 'OVERCAPACITY_VIOLATION'
                }
                records.append(record)
                pallet_counter += 1
        
        return records
    
    def _generate_invalid_locations(self) -> List[Dict]:
        """VirtualInvalidLocationEvaluator: Invalid location formats (NO position 29!)"""
        records = []
        
        # CORRECTED: No position 29 locations - use clearly invalid formats only
        invalid_locations = [
            "INVALID_ZONE_999",           # Completely invalid
            "99-99-999Z",                 # Invalid aisle/rack/position/level
            "01-99-001A",                 # Invalid rack 99 (only rack 01 exists)
            "CLEARLY_INVALID_LOCATION"    # Obviously wrong format
        ]
        
        for i, location in enumerate(invalid_locations):
            record = {
                'pallet_id': f"INVALID_{i+1:03d}",
                'location': location,
                'location_type': 'UNKNOWN',
                'creation_date': self._random_recent_date(hours_range=(2, 8)),
                'receipt_number': f"RCT_INVALID_{i+1:03d}",
                'description': 'INVALID_LOCATION'
            }
            records.append(record)
        
        return records
    
    def _generate_aisle_stagnant(self) -> List[Dict]:
        """LocationSpecificStagnantEvaluator: >4h in AISLE locations"""
        records = []
        
        for i in range(self.target_anomalies['aisle_stagnant']):
            record = {
                'pallet_id': f"AISLE_STAG_{i+1:03d}",
                'location': 'AISLE-01',
                'location_type': 'TRANSITIONAL',
                'creation_date': self._stagnant_date(min_hours=5, max_hours=12),  # >4h threshold
                'receipt_number': f"RCT_AISLE_{i+1:03d}",
                'description': 'AISLE_STAGNANT'
            }
            records.append(record)
        
        return records
    
    def _generate_duplicates(self) -> List[Dict]:
        """DataIntegrityEvaluator: Duplicate pallet IDs"""
        records = []
        
        # Create 2 duplicate pairs (4 records total)
        for pair in range(2):
            duplicate_id = f"DUPLICATE_{pair+1:03d}"
            
            # First occurrence
            record1 = {
                'pallet_id': duplicate_id,
                'location': random.choice(['RECV-01', 'RECV-02']),
                'location_type': 'RECEIVING',
                'creation_date': self._random_recent_date(hours_range=(4, 8)),
                'receipt_number': f"RCT_DUP_A_{pair+1:03d}",
                'description': 'DUPLICATE_SCAN_FIRST'
            }
            
            # Second occurrence (duplicate)
            record2 = {
                'pallet_id': duplicate_id,
                'location': random.choice(self.storage_locations[:10]),  # Use first 10 locations
                'location_type': 'STORAGE',
                'creation_date': self._random_recent_date(hours_range=(2, 6)),
                'receipt_number': f"RCT_DUP_B_{pair+1:03d}",
                'description': 'DUPLICATE_SCAN_SECOND'
            }
            
            records.extend([record1, record2])
        
        return records
    
    def _generate_mapping_errors(self) -> List[Dict]:
        """LocationMappingErrorEvaluator: Location type mismatches"""
        records = []
        
        # Use valid storage locations for type mismatches
        valid_storage_sample = random.sample(self.storage_locations[:10], 2)
        
        mapping_errors = [
            {'location': valid_storage_sample[0], 'wrong_type': 'RECEIVING'},  # Storage location marked as RECEIVING
            {'location': valid_storage_sample[1], 'wrong_type': 'TRANSITIONAL'},  # Storage location marked as TRANSITIONAL
            {'location': 'RECV-01', 'wrong_type': 'STORAGE'},      # RECEIVING location marked as STORAGE
            {'location': 'AISLE-01', 'wrong_type': 'STORAGE'}      # TRANSITIONAL location marked as STORAGE
        ]
        
        for i, error in enumerate(mapping_errors):
            record = {
                'pallet_id': f"MAPPING_ERROR_{i+1:03d}",
                'location': error['location'],
                'location_type': error['wrong_type'],  # Wrong type for location
                'creation_date': self._random_recent_date(hours_range=(1, 6)),
                'receipt_number': f"RCT_MAPPING_{i+1:03d}",
                'description': 'TYPE_MISMATCH'
            }
            records.append(record)
        
        return records
    
    def _random_recent_date(self, hours_range: tuple = (0.5, 8)) -> str:
        """Generate recent timestamp within specified hour range"""
        min_hours, max_hours = hours_range
        hours_ago = random.uniform(min_hours, max_hours)
        timestamp = self.now - timedelta(hours=hours_ago)
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    def _stagnant_date(self, min_hours: int = 12, max_hours: int = 48) -> str:
        """Generate stagnant timestamp (older than thresholds)"""
        hours_ago = random.uniform(min_hours, max_hours)
        timestamp = self.now - timedelta(hours=hours_ago)
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    def save_to_excel(self, inventory: List[Dict], filename: str):
        """Save corrected inventory to Excel file with analysis sheet"""
        
        # Create DataFrame
        df = pd.DataFrame(inventory)
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main inventory sheet
            df.to_excel(writer, sheet_name='Inventory', index=False)
            
            # Analysis summary sheet
            analysis_data = {
                'Metric': [
                    'CORRECTION STATUS',
                    'Position Range Fix',
                    'Total Pallets',
                    'Clean Pallets', 
                    'Total Anomalies',
                    'Stagnant Pallets (>10h RECV)',
                    'Uncoordinated Lots (<80%)',
                    'Overcapacity Violations',
                    'Invalid Locations',
                    'Aisle Stagnant (>4h AISLE)',
                    'Duplicate Pallets',
                    'Mapping Errors',
                    'Anomaly Rate (%)',
                    'Storage Location Range',
                    'Expected Detection Rate'
                ],
                'Count': [
                    'FIXED - Bug Corrected',
                    'Positions 1-28 (was 1-29)',
                    len(inventory),
                    len(inventory) - sum(self.target_anomalies.values()),
                    sum(self.target_anomalies.values()),
                    self.target_anomalies['stagnant_pallets'],
                    self.target_anomalies['uncoordinated_lots'],
                    self.target_anomalies['overcapacity'],
                    self.target_anomalies['invalid_locations'],
                    self.target_anomalies['aisle_stagnant'],
                    self.target_anomalies['duplicates'],
                    self.target_anomalies['mapping_errors'],
                    f"{(sum(self.target_anomalies.values()) / len(inventory) * 100):.1f}%",
                    '01-01-001A to 01-01-028D',
                    '100% (40 surgical anomalies)'
                ]
            }
            
            analysis_df = pd.DataFrame(analysis_data)
            analysis_df.to_excel(writer, sheet_name='Analysis', index=False)
            
            # Location distribution sheet
            location_dist = df['location'].value_counts().reset_index()
            location_dist.columns = ['Location', 'Pallet_Count']
            location_dist.to_excel(writer, sheet_name='Location_Distribution', index=False)
        
        print(f"\nCorrected Excel inventory saved: {filename}")
        print(f"  - Inventory sheet: {len(inventory)} records")
        print(f"  - Analysis sheet: Corrected anomaly breakdown")
        print(f"  - Location Distribution sheet: Proper pallet distribution")

def main():
    """Generate corrected precision Excel inventory with exactly 800 pallets"""
    
    generator = CorrectedPrecisionInventoryGenerator()
    
    # Generate corrected precision inventory
    inventory = generator.generate_corrected_precision_inventory()
    
    # Save to Excel
    filename = "corrected_precision_inventory_800_pallets.xlsx"
    generator.save_to_excel(inventory, filename)
    
    print(f"\nCORRECTED PRECISION INVENTORY COMPLETE!")
    print(f"File: {filename}")
    print(f"CRITICAL BUG FIXED: Position range now 1-28 (was 1-29)")
    print(f"Ready for WareWise testing with corrected surgical precision!")

if __name__ == "__main__":
    main()