#!/usr/bin/env python3
"""
Warehouse Inventory Template Generator

Generates realistic inventory reports matching the format from real warehouse data:
- Location format: RACK.LEVEL+POSITION (e.g., 13.68C, 17.67A)
- Receipt numbers for tracking
- Realistic item codes, descriptions, and storage times
- Configurable rack layouts and inventory sizes

Based on analysis of actual warehouse Excel reports.
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import string

class WarehouseInventoryGenerator:
    def __init__(self):
        self.item_prefixes = [
            '0596VUS', '108546941002', 'A05828-0922', '0648VUS', 'MB535600',
            'A04974-0921', '3612622140629', '0291VUS', '0149VUS', '0119VUS',
            '0116VUS', '0131VUS', '0064VUS', '0123VUS'
        ]

        self.item_descriptions = [
            'SKN 2023 SKINC SYSTEMS SETBOX',
            'AW 292 PIPET 1ML THERMO FISHER LDPE NON-STERILE TRANSLUCENT TRANSFER 500/PK 8PK/CA',
            'NEW Carton, CeraVe Costco 16oz Cream +16oz Cream NON WINDOW',
            'DRM AMZ LOOSE PDR KIT INSRT 2022',
            '1US OTC TOL DAILY MOIST SPF30 100ml',
            'Dubl Kote Tape , CRV RITE AID SKINNY TWR SPR 22 SPF',
            'LBL WRAP ML LRP HYALU B5 VER HYALU 2',
            'VCY HM DEO VAPO100 ML LBL',
            'VCY INSTR LBL NORD ANTI V0204802',
            'VCY BACK LBL V0435400',
            'VCY FRONT LBL V0435400',
            'LRP ANTH A RWK CIRCLE FRNT LBL',
            'Vcy HM Gel Rasage 150M Back Label',
            'VCY DERMAFINISH STICK LABEL'
        ]

        self.receipt_prefixes = ['RC', 'RV', 'IN', 'PO']

        # Anomaly configuration defaults
        self.anomaly_config = {
            'stagnant_pallets': {'enabled': False, 'percentage': 15, 'min_weeks': 120},
            'overcapacity': {'enabled': False, 'percentage': 10, 'max_pallets_per_location': 5},
            'lot_stragglers': {'enabled': False, 'percentage': 8, 'create_orphaned_lots': True},
            'invalid_locations': {'enabled': False, 'percentage': 5, 'use_invalid_formats': True},
            'missing_data': {'enabled': False, 'percentage': 3, 'missing_fields': ['Receipt number']},
            'duplicate_pallets': {'enabled': False, 'percentage': 2, 'create_duplicates': True},
            'temperature_violations': {'enabled': False, 'percentage': 7, 'wrong_zones': True}
        }

    def generate_location(self, rack_num, max_level=68, positions_per_level=6):
        """Generate location in format: RACK.LEVEL+POSITION"""
        level = random.randint(1, max_level)
        position = random.choice(string.ascii_uppercase[:positions_per_level])
        return f"{rack_num}.{level:02d}{position}"

    def generate_pallet_number(self):
        """Generate realistic pallet numbers based on patterns from real data"""
        # Mix of different pallet number formats observed
        if random.random() < 0.3:
            # Short format (like 95000040649)
            return random.randint(95000000000, 99999999999)
        else:
            # Long format (like 777100000000462983)
            return random.randint(777100000000000000, 999100000000999999)

    def generate_receipt_number(self):
        """Generate receipt number for tracking"""
        prefix = random.choice(self.receipt_prefixes)
        number = random.randint(100000, 999999)
        return f"{prefix}{number}"

    def generate_time_in_storage(self):
        """Generate realistic time in storage format: XwYdZhAm"""
        weeks = random.randint(1, 200)
        days = random.randint(0, 6)
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        return f"{weeks}w {days}d {hours}h {minutes}m"

    def generate_base_quantity(self):
        """Generate realistic base quantities"""
        quantities = [144.0, 120.0, 1920.0, 85.0, 753.0, 240.0, 480.0, 96.0]
        return random.choice(quantities)

    def generate_item_code(self):
        """Generate realistic item codes"""
        if random.random() < 0.7:
            # Use existing patterns
            return random.choice(self.item_prefixes)
        else:
            # Generate new pattern
            if random.random() < 0.5:
                # Format: XXXXXXVUS
                return f"{random.randint(1000, 9999)}VUS"
            else:
                # Format: AXXXXX-XXXX
                letter = random.choice('ABCDEFGHIJKLMNOP')
                return f"{letter}{random.randint(10000, 99999)}-{random.randint(1000, 9999)}"

    def generate_item_description(self):
        """Generate realistic item descriptions"""
        if random.random() < 0.6:
            return random.choice(self.item_descriptions)
        else:
            # Generate variations
            brands = ['CeraVe', 'L\'Oreal', 'Vichy', 'La Roche-Posay', 'Neutrogena']
            products = ['Cream', 'Lotion', 'Serum', 'Cleanser', 'Sunscreen', 'Label', 'Kit']
            sizes = ['100ml', '150ml', '200ml', '16oz', '8oz']

            brand = random.choice(brands)
            product = random.choice(products)
            size = random.choice(sizes)

            return f"{brand} {product} {size}"

    def configure_anomalies(self, **anomaly_settings):
        """
        Configure anomaly injection settings

        Args:
            anomaly_settings: Dictionary of anomaly types and their configurations

        Example:
            generator.configure_anomalies(
                stagnant_pallets={'enabled': True, 'percentage': 20, 'min_weeks': 150},
                overcapacity={'enabled': True, 'percentage': 15, 'max_pallets_per_location': 8}
            )
        """
        for anomaly_type, settings in anomaly_settings.items():
            if anomaly_type in self.anomaly_config:
                self.anomaly_config[anomaly_type].update(settings)

    def _inject_stagnant_pallets(self, data, target_count):
        """Inject stagnant pallets (very old inventory)"""
        if target_count == 0:
            return

        config = self.anomaly_config['stagnant_pallets']
        min_weeks = config['min_weeks']

        # Select random items to make stagnant
        indices = random.sample(range(len(data)), min(target_count, len(data)))

        for idx in indices:
            # Create very old storage times
            weeks = random.randint(min_weeks, min_weeks + 100)
            days = random.randint(0, 6)
            hours = random.randint(0, 23)
            minutes = random.randint(0, 59)
            data[idx]['Time in storage'] = f"{weeks}w {days}d {hours}h {minutes}m"

    def _inject_overcapacity(self, data, target_count):
        """Inject overcapacity situations (multiple pallets per location)"""
        if target_count == 0:
            return

        config = self.anomaly_config['overcapacity']
        max_pallets = config['max_pallets_per_location']

        # Group items by location for overcapacity injection
        location_groups = {}
        for i, item in enumerate(data):
            loc = item['Location']
            if loc not in location_groups:
                location_groups[loc] = []
            location_groups[loc].append(i)

        # Select locations to overcrowd
        available_locations = list(location_groups.keys())
        locations_to_crowd = random.sample(available_locations, min(target_count // 2, len(available_locations)))

        for location in locations_to_crowd:
            # Add extra pallets to this location
            base_idx = location_groups[location][0]
            pallets_to_add = random.randint(2, max_pallets)

            for _ in range(pallets_to_add - 1):
                # Create duplicate location entry with different pallet
                new_item = data[base_idx].copy()
                new_item['Pallet number'] = self.generate_pallet_number()
                new_item['Receipt number'] = self.generate_receipt_number()
                new_item['Item code'] = self.generate_item_code()
                new_item['Item description'] = self.generate_item_description()
                data.append(new_item)

    def _inject_invalid_locations(self, data, target_count):
        """Inject invalid location formats"""
        if target_count == 0:
            return

        indices = random.sample(range(len(data)), min(target_count, len(data)))

        invalid_formats = [
            'INVALID-LOC',
            '99.99Z',  # Invalid position letter
            '0.00A',   # Invalid rack/level
            'XX.YYC',  # Non-numeric rack/level
            '13.69A',  # Level beyond typical range
            'TEMP-HOLD',
            'UNKNOWN'
        ]

        for idx in indices:
            data[idx]['Location'] = random.choice(invalid_formats)

    def _inject_missing_data(self, data, target_count):
        """Inject missing data anomalies"""
        if target_count == 0:
            return

        config = self.anomaly_config['missing_data']
        missing_fields = config['missing_fields']

        indices = random.sample(range(len(data)), min(target_count, len(data)))

        for idx in indices:
            # Randomly remove specified fields
            for field in missing_fields:
                if random.random() < 0.7:  # 70% chance to remove each field
                    if field in data[idx]:
                        data[idx][field] = None

    def _inject_duplicate_pallets(self, data, target_count):
        """Inject duplicate pallet numbers (data integrity issue)"""
        if target_count == 0:
            return

        # Select items to duplicate
        indices = random.sample(range(len(data)), min(target_count // 2, len(data)))

        for idx in indices:
            # Find another item to give the same pallet number
            target_idx = random.choice([i for i in range(len(data)) if i != idx])
            data[target_idx]['Pallet number'] = data[idx]['Pallet number']

    def _inject_lot_stragglers(self, data, target_count):
        """Inject lot stragglers (items that should be together but aren't)"""
        if target_count == 0:
            return

        # Create artificial lot patterns by giving items similar codes but different locations
        indices = random.sample(range(len(data)), min(target_count, len(data)))

        lot_base = f"LOT{random.randint(1000, 9999)}"

        for i, idx in enumerate(indices):
            # Create lot-based item codes
            data[idx]['Item code'] = f"{lot_base}-{i+1:03d}"
            # Spread them across different locations to create stragglers
            rack = random.choice([13, 17, 18, 19, 20])
            data[idx]['Location'] = self.generate_location(rack)

    def generate_inventory_report(self, rack_nums=[13, 17], num_items=500, filename=None, anomalies=None):
        """
        Generate a complete inventory report with controllable anomalies

        Args:
            rack_nums: List of rack numbers to include
            num_items: Total number of inventory items to generate
            filename: Output filename (auto-generated if None)
            anomalies: Dictionary of anomaly configurations to override defaults

        Example:
            anomalies = {
                'stagnant_pallets': {'enabled': True, 'percentage': 25},
                'overcapacity': {'enabled': True, 'percentage': 15},
                'invalid_locations': {'enabled': True, 'percentage': 5}
            }
        """
        # Configure anomalies if provided
        if anomalies:
            self.configure_anomalies(**anomalies)
        data = []

        for i in range(num_items):
            rack = random.choice(rack_nums)

            row = {
                'Location': self.generate_location(rack),
                'Pallet number': self.generate_pallet_number(),
                'Receipt number': self.generate_receipt_number(),
                'Base quantity': self.generate_base_quantity(),
                'Item code': self.generate_item_code(),
                'Item description': self.generate_item_description(),
                'Time in storage': self.generate_time_in_storage()
            }

            # Add some optional fields with random presence
            if random.random() < 0.2:
                row['NIL'] = random.randint(1, 20)

            if random.random() < 0.15:
                row['Founds'] = random.randint(1, 10)

            data.append(row)

        # Apply anomaly injections based on configuration
        total_anomalies_injected = 0
        anomaly_summary = {}

        for anomaly_type, config in self.anomaly_config.items():
            if config['enabled']:
                target_count = int((config['percentage'] / 100) * len(data))

                if anomaly_type == 'stagnant_pallets':
                    self._inject_stagnant_pallets(data, target_count)
                elif anomaly_type == 'overcapacity':
                    self._inject_overcapacity(data, target_count)
                elif anomaly_type == 'invalid_locations':
                    self._inject_invalid_locations(data, target_count)
                elif anomaly_type == 'missing_data':
                    self._inject_missing_data(data, target_count)
                elif anomaly_type == 'duplicate_pallets':
                    self._inject_duplicate_pallets(data, target_count)
                elif anomaly_type == 'lot_stragglers':
                    self._inject_lot_stragglers(data, target_count)

                anomaly_summary[anomaly_type] = target_count
                total_anomalies_injected += target_count

        df = pd.DataFrame(data)

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"warehouse_inventory_template_{timestamp}.xlsx"

        # Ensure .xlsx extension
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'

        # Save to file
        filepath = f"C:/Users/juanb/Documents/Diego/Projects/ware2/{filename}"
        df.to_excel(filepath, index=False)

        print(f"Generated inventory report: {filename}")
        print(f"Items: {len(df)}")

        # Handle rack extraction safely (some locations may be invalid)
        try:
            valid_locations = df['Location'].str.match(r'\d+\.\d+[A-Z]')
            valid_racks = df[valid_locations]['Location'].str.split('.').str[0].astype(int).unique()
            print(f"Racks: {sorted(valid_racks)}")
        except:
            print(f"Racks: Mixed (some invalid locations present)")

        print(f"Location range: {df['Location'].min()} to {df['Location'].max()}")
        print(f"Sample locations: {df['Location'].head(5).tolist()}")

        # Report anomalies injected
        if total_anomalies_injected > 0:
            print(f"\n=== ANOMALIES INJECTED ===")
            print(f"Total anomalies: {total_anomalies_injected}")
            for anomaly_type, count in anomaly_summary.items():
                percentage = (count / len(df)) * 100
                print(f"  {anomaly_type}: {count} items ({percentage:.1f}%)")
        else:
            print(f"\nNo anomalies injected (clean data)")

        return df, filepath

if __name__ == "__main__":
    generator = WarehouseInventoryGenerator()

    # Generate a test inventory with realistic parameters
    df, filepath = generator.generate_inventory_report(
        rack_nums=[13, 17, 18, 19, 20],  # Multiple racks
        num_items=300,  # Moderate size for testing
        filename="warehouse_test_inventory_template"
    )

    print(f"\nFile saved at: {filepath}")
    print(f"\nSample data:")
    print(df.head(10).to_string())