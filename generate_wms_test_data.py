#!/usr/bin/env python3
"""
QA Test Data Generator for Warehouse Anomaly Detection System
Creates controlled dataset with exactly 30 anomalies per business rule
Target: 2000 rows with capacity-aware distribution
"""

import pandas as pd
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import numpy as np

class WarehouseTestDataGenerator:
    def __init__(self):
        self.total_pallets = 2000
        self.anomalies_per_rule = 30
        self.rules_count = 8
        self.total_anomalies = self.anomalies_per_rule * self.rules_count
        self.valid_pallets = self.total_pallets - self.total_anomalies
        
        # Warehouse structure (corrected to match system expectations)
        self.aisles = ['1', '2', '3', '4']  # Numeric aisles, not letters
        self.racks = ['01', '02']  
        self.positions = [f"{i:02d}" for i in range(1, 43)]  # 01-42 (not 63)
        self.levels = ['A', 'B', 'C', 'D']
        
        # Special locations with capacities
        self.special_locations = {
            'RECV-01': 10, 'RECV-02': 10, 'STAGE-01': 5, 'DOCK-01': 2,
            'AISLE-01': 10, 'AISLE-02': 10, 'AISLE-03': 10, 
            'AISLE-04': 10, 'AISLE-05': 10
        }
        
        # Product types and restrictions
        self.product_types = {
            'ELECTRONICS': ['RECEIVING', 'GENERAL'],
            'CHEMICALS': ['DOCK'],  # Restricted
            'FOOD': ['RECEIVING', 'STAGING'],
            'TEXTILES': ['GENERAL', 'STAGING'],
            'AUTOMOTIVE': ['GENERAL', 'DOCK'],
            'PHARMACEUTICALS': ['RECEIVING']  # Restricted
        }
        
        self.lot_prefixes = ['LOT-A', 'LOT-B', 'LOT-C', 'LOT-D', 'LOT-E']
        
    def generate_storage_location(self) -> str:
        """Generate valid storage location: 1-01-01A format"""
        aisle = random.choice(self.aisles)
        rack = random.choice(self.racks)
        position = random.choice(self.positions)
        level = random.choice(self.levels)
        return f"{aisle}-{rack}-{position}{level}"
    
    def generate_invalid_location(self) -> str:
        """Generate invalid location for testing"""
        invalid_patterns = [
            f"5-01-01A",  # Invalid aisle (only 1-4 exist)
            f"1-03-01A",  # Invalid rack (only 01-02 exist)
            f"1-01-43A",  # Invalid position (>42)
            f"1-01-01E",  # Invalid level (only A-D exist)
            f"INVALID-LOC",  # Malformed
            f"1-1-1A",    # Wrong format (missing zero padding)
            f"A-01-01A",  # Old letter format
        ]
        return random.choice(invalid_patterns)
    
    def generate_receipt_number(self) -> str:
        """Generate receipt number in format RCP-YYYYMMDD-NNNN"""
        date_str = datetime.now().strftime("%Y%m%d")
        num = random.randint(1000, 9999)
        return f"RCP-{date_str}-{num}"
    
    def generate_lot_number(self) -> str:
        """Generate lot number"""
        prefix = random.choice(self.lot_prefixes)
        suffix = random.randint(100, 999)
        return f"{prefix}-{suffix}"
    
    def create_base_data(self) -> List[Dict]:
        """Create base valid pallet data"""
        data = []
        used_storage_locations = set()
        
        # Generate valid pallets with capacity awareness
        for i in range(self.valid_pallets):
            pallet_id = f"PLT-{i+1:06d}"
            receipt_number = self.generate_receipt_number()
            
            # Product selection
            product_type = random.choice(list(self.product_types.keys()))
            description = f"{product_type} - Batch {random.randint(100, 999)}"
            
            # Location assignment (prefer unique storage locations)
            if i < 1200 and len(used_storage_locations) < 1344:  # Use unique storage locations (4×2×42×4=1344)
                while True:
                    location = self.generate_storage_location()
                    if location not in used_storage_locations:
                        used_storage_locations.add(location)
                        break
            else:
                # Use special locations very sparingly or allow some storage duplication
                if random.random() < 0.1:  # Reduced from 0.3 to 0.1 to limit special area usage
                    location = random.choice(list(self.special_locations.keys()))
                else:
                    location = self.generate_storage_location()
            
            # Creation date (mostly recent, some older for variety)
            days_ago = random.choices(
                range(0, 90), 
                weights=[50] + [max(1, 50-i) for i in range(1, 90)]
            )[0]
            creation_date = datetime.now() - timedelta(days=days_ago, 
                                                      hours=random.randint(0, 23),
                                                      minutes=random.randint(0, 59))
            
            data.append({
                'pallet_id': pallet_id,
                'receipt_number': receipt_number,
                'lot_number': self.generate_lot_number(),
                'description': description,
                'product_type': product_type,
                'location': location,
                'creation_date': creation_date.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return data
    
    def add_stagnant_pallets_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Add 30 stagnant pallets (>72 hours in staging)"""
        anomalies = []
        for i in range(self.anomalies_per_rule):
            pallet_id = f"ANM-STAG-{i+1:03d}"
            receipt_number = self.generate_receipt_number()
            
            # Create stagnant pallet (>72 hours in staging)
            hours_stagnant = random.randint(73, 168)  # 3-7 days
            creation_date = datetime.now() - timedelta(hours=hours_stagnant)
            
            anomalies.append({
                'pallet_id': pallet_id,
                'receipt_number': receipt_number,
                'lot_number': self.generate_lot_number(),
                'description': f"STAGNANT - {random.choice(['ELECTRONICS', 'FOOD'])} - Batch {random.randint(100, 999)}",
                'product_type': random.choice(['ELECTRONICS', 'FOOD']),
                'location': 'STAGE-01',
                'creation_date': creation_date.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return anomalies
    
    def add_uncoordinated_lots_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Add 30 uncoordinated lot stragglers"""
        anomalies = []
        
        # Create base lot that's 85% complete
        base_lot = "LOT-INCOMPLETE-001"
        
        for i in range(self.anomalies_per_rule):
            pallet_id = f"ANM-UNCRD-{i+1:03d}"
            receipt_number = self.generate_receipt_number()
            
            # Straggler pallets from incomplete lot
            days_behind = random.randint(2, 10)
            creation_date = datetime.now() - timedelta(days=days_behind)
            
            anomalies.append({
                'pallet_id': pallet_id,
                'receipt_number': receipt_number,
                'lot_number': base_lot,
                'description': f"STRAGGLER - {random.choice(['TEXTILES', 'AUTOMOTIVE'])} - Batch {random.randint(100, 999)}",
                'product_type': random.choice(['TEXTILES', 'AUTOMOTIVE']),
                'location': self.generate_storage_location(),
                'creation_date': creation_date.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return anomalies
    
    def add_overcapacity_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Add exactly 30 overcapacity violations"""
        anomalies = []
        
        # Target specific locations for overcapacity
        overcapacity_locations = [
            '1-01-01A', '2-01-01A', '3-01-01A',  # Storage locations (capacity=1)
            'STAGE-01', 'DOCK-01'  # Special locations  
        ]
        
        for i in range(self.anomalies_per_rule):
            pallet_id = f"ANM-OVER-{i+1:03d}"
            receipt_number = self.generate_receipt_number()
            
            # Assign to overcapacity location
            location = random.choice(overcapacity_locations)
            
            anomalies.append({
                'pallet_id': pallet_id,
                'receipt_number': receipt_number,
                'lot_number': self.generate_lot_number(),
                'description': f"OVERCAP - {random.choice(['ELECTRONICS', 'FOOD'])} - Batch {random.randint(100, 999)}",
                'product_type': random.choice(['ELECTRONICS', 'FOOD']),
                'location': location,
                'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return anomalies
    
    def add_invalid_location_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Add 30 invalid location anomalies"""
        anomalies = []
        
        for i in range(self.anomalies_per_rule):
            pallet_id = f"ANM-INVLOC-{i+1:03d}"
            receipt_number = self.generate_receipt_number()
            
            anomalies.append({
                'pallet_id': pallet_id,
                'receipt_number': receipt_number,
                'lot_number': self.generate_lot_number(),
                'description': f"INVALID LOC - {random.choice(['ELECTRONICS', 'TEXTILES'])} - Batch {random.randint(100, 999)}",
                'product_type': random.choice(['ELECTRONICS', 'TEXTILES']),
                'location': self.generate_invalid_location(),
                'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return anomalies
    
    def add_location_specific_stagnant_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Add 30 location-specific stagnant pallets (>48 hours in AISLE locations)"""
        anomalies = []
        
        aisle_locations = ['AISLE-01', 'AISLE-02', 'AISLE-03', 'AISLE-04', 'AISLE-05']
        
        for i in range(self.anomalies_per_rule):
            pallet_id = f"ANM-LSTAG-{i+1:03d}"
            receipt_number = self.generate_receipt_number()
            
            # Create stagnant pallet in aisle (>48 hours)
            hours_stagnant = random.randint(49, 120)  # 2-5 days
            creation_date = datetime.now() - timedelta(hours=hours_stagnant)
            
            anomalies.append({
                'pallet_id': pallet_id,
                'receipt_number': receipt_number,
                'lot_number': self.generate_lot_number(),
                'description': f"AISLE STAGNANT - {random.choice(['AUTOMOTIVE', 'TEXTILES'])} - Batch {random.randint(100, 999)}",
                'product_type': random.choice(['AUTOMOTIVE', 'TEXTILES']),
                'location': random.choice(aisle_locations),
                'creation_date': creation_date.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return anomalies
    
    def add_data_integrity_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Add 30 data integrity anomalies (duplicates + malformed data)"""
        anomalies = []
        
        # Duplicate scans (15) + malformed locations (15)
        for i in range(15):
            # Duplicate pallet IDs
            existing_pallet = random.choice(data)
            pallet_id = existing_pallet['pallet_id']  # Duplicate!
            
            anomalies.append({
                'pallet_id': pallet_id,
                'receipt_number': self.generate_receipt_number(),
                'lot_number': self.generate_lot_number(),
                'description': f"DUPLICATE - {random.choice(['ELECTRONICS', 'FOOD'])} - Batch {random.randint(100, 999)}",
                'product_type': random.choice(['ELECTRONICS', 'FOOD']),
                'location': self.generate_storage_location(),
                'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        for i in range(15):
            # Malformed locations
            malformed_locations = [
                "1-01-01",  # Missing level
                "1--01A",   # Missing rack
                "1-01-A",   # Missing position
                "-01-01A",  # Missing aisle
                "1 01 01A", # Wrong separator
                "1-01-01-A", # Extra separator
                "1/01/01A", # Wrong separator type
                "1-1-1A"    # Wrong format (no zero padding)
            ]
            
            pallet_id = f"ANM-MALFORM-{i+1:03d}"
            
            anomalies.append({
                'pallet_id': pallet_id,
                'receipt_number': self.generate_receipt_number(),
                'lot_number': self.generate_lot_number(),
                'description': f"MALFORMED LOC - {random.choice(['TEXTILES', 'AUTOMOTIVE'])} - Batch {random.randint(100, 999)}",
                'product_type': random.choice(['TEXTILES', 'AUTOMOTIVE']),
                'location': random.choice(malformed_locations),
                'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return anomalies
    
    def add_missing_location_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Add 30 missing location anomalies"""
        anomalies = []
        
        for i in range(self.anomalies_per_rule):
            pallet_id = f"ANM-MISSING-{i+1:03d}"
            receipt_number = self.generate_receipt_number()
            
            # Random missing location patterns
            location_value = random.choice([None, "", "  ", "NULL", "N/A"])
            
            anomalies.append({
                'pallet_id': pallet_id,
                'receipt_number': receipt_number,
                'lot_number': self.generate_lot_number(),
                'description': f"MISSING LOC - {random.choice(['ELECTRONICS', 'FOOD'])} - Batch {random.randint(100, 999)}",
                'product_type': random.choice(['ELECTRONICS', 'FOOD']),
                'location': location_value,
                'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return anomalies
    
    def add_product_incompatibility_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Add 30 product incompatibility anomalies"""
        anomalies = []
        
        # Restricted product placements
        violations = [
            ('CHEMICALS', 'STAGE-01'),     # Should be in DOCK only
            ('CHEMICALS', 'RECV-01'),      # Should be in DOCK only
            ('PHARMACEUTICALS', 'DOCK-01'), # Should be in RECEIVING only
            ('PHARMACEUTICALS', 'STAGE-01') # Should be in RECEIVING only
        ]
        
        for i in range(self.anomalies_per_rule):
            pallet_id = f"ANM-INCOMP-{i+1:03d}"
            receipt_number = self.generate_receipt_number()
            
            product_type, wrong_location = random.choice(violations)
            
            anomalies.append({
                'pallet_id': pallet_id,
                'receipt_number': receipt_number,
                'lot_number': self.generate_lot_number(),
                'description': f"INCOMPATIBLE - {product_type} - Batch {random.randint(100, 999)}",
                'product_type': product_type,
                'location': wrong_location,
                'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return anomalies
    
    def generate_dataset(self) -> pd.DataFrame:
        """Generate complete test dataset"""
        print("*** Generating QA Test Dataset for Warehouse Anomaly Detection")
        print(f"Target: {self.total_pallets} pallets with {self.total_anomalies} controlled anomalies")
        print()
        
        # Create base valid data
        print("*** Creating base valid pallet data...")
        data = self.create_base_data()
        print(f"*** Generated {len(data)} valid pallets")
        
        # Add anomalies by rule type
        anomaly_generators = [
            ("STAGNANT_PALLETS", self.add_stagnant_pallets_anomalies),
            ("UNCOORDINATED_LOTS", self.add_uncoordinated_lots_anomalies),
            ("OVERCAPACITY", self.add_overcapacity_anomalies),
            ("INVALID_LOCATION", self.add_invalid_location_anomalies),
            ("LOCATION_SPECIFIC_STAGNANT", self.add_location_specific_stagnant_anomalies),
            ("DATA_INTEGRITY", self.add_data_integrity_anomalies),
            ("MISSING_LOCATION", self.add_missing_location_anomalies),
            ("PRODUCT_INCOMPATIBILITY", self.add_product_incompatibility_anomalies)
        ]
        
        print("\n*** Adding controlled anomalies...")
        for rule_name, generator in anomaly_generators:
            anomalies = generator(data)
            data.extend(anomalies)
            print(f"   {rule_name}: {len(anomalies)} anomalies")
        
        # Shuffle data to randomize order
        random.shuffle(data)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Remove product_type and lot_number columns (internal use only)
        df = df[['pallet_id', 'receipt_number', 'description', 'location', 'creation_date']]
        
        print(f"\n*** Dataset Summary:")
        print(f"   Total pallets: {len(df)}")
        print(f"   Valid pallets: {self.valid_pallets}")
        print(f"   Total anomalies: {len(df) - self.valid_pallets}")
        print(f"   Anomalies per rule: {self.anomalies_per_rule}")
        
        return df
    
    def validate_capacity_distribution(self, df: pd.DataFrame):
        """Validate that capacity constraints are respected"""
        print("\n*** Capacity Validation:")
        
        location_counts = df['location'].value_counts()
        
        # Check storage locations (should mostly be capacity=1)
        storage_violations = 0
        for location, count in location_counts.items():
            if location and isinstance(location, str) and len(location) == 8 and '-' in location:  # Storage location format 1-01-01A
                if count > 1:
                    storage_violations += 1
        
        print(f"   Storage locations with >1 pallet: {storage_violations}")
        print(f"   Target overcapacity violations: {self.anomalies_per_rule}")
        
        # Check special locations
        print("   Special location distribution:")
        for special_loc in self.special_locations.keys():
            count = location_counts.get(special_loc, 0)
            capacity = self.special_locations[special_loc]
            status = "*** OVER" if count > capacity else "*** OK"
            print(f"     {special_loc}: {count}/{capacity} {status}")

def main():
    """Main execution function"""
    print("*** QA Test Data Generator for Warehouse Anomaly Detection")
    print("=" * 60)
    
    generator = WarehouseTestDataGenerator()
    
    # Generate dataset
    df = generator.generate_dataset()
    
    # Validate capacity constraints
    generator.validate_capacity_distribution(df)
    
    # Export to Excel
    output_file = "test5_corrected.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n*** Exported dataset to: {output_file}")
    
    # Display sample data
    print("\n*** Sample Data (first 10 rows):")
    print(df.head(10).to_string(index=False))
    
    print("\n*** QA Test Dataset Generation Complete!")
    
    return df

if __name__ == "__main__":
    main()
