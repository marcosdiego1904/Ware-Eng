#!/usr/bin/env python3
"""
Flexible Test Inventory Generator for WareWise Rule Validation
=============================================================

Creates scalable test inventory files with precise anomaly injection for
validating warehouse rule engine accuracy.

Features:
- Progressive scaling: 100 → 10,000+ pallets
- Fixed anomaly counts regardless of file size
- Format-aware location generation (###L pattern)
- Warehouse-specific special areas (RECV, AISLE, W-##)
- Detailed generation reports

Author: WareWise Testing Team
Date: 2025-01-09
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import argparse
import sys
from pathlib import Path

# ==================== CONFIGURATION ====================

@dataclass
class GeneratorConfig:
    """Configuration for test inventory generation"""

    # Size configuration
    total_pallets: int = 100
    anomalies_per_rule: int = 5

    # Output configuration
    output_filename: Optional[str] = None
    output_directory: str = "."

    # Location format configuration
    storage_format: str = "###L"  # Format: 001A, 213B, 031C
    storage_capacity: int = 2      # 2 pallets per storage location

    # Position range for storage locations
    min_position: int = 1
    max_position: int = 999

    # Available levels
    levels: List[str] = field(default_factory=lambda: ['A', 'B', 'C', 'D'])

    # Special areas configuration
    receiving_areas: List[str] = field(default_factory=lambda: ['RECV-01', 'RECV-02'])
    aisle_areas: List[str] = field(default_factory=lambda: [f'AISLE-{i:02d}' for i in range(1, 11)])  # AISLE-01 to AISLE-10
    wall_areas: List[str] = field(default_factory=lambda: [f'W-{i:02d}' for i in range(1, 6)])  # W-01 to W-05

    # Special area capacities
    receiving_capacity: int = 10
    aisle_capacity: int = 5
    wall_capacity: int = 1

    # Product configuration
    products: List[str] = field(default_factory=lambda: [
        'Widget Assembly Kit',
        'Component Box A',
        'Component Box B',
        'Finished Product SKU-001',
        'Finished Product SKU-002',
        'Raw Material Bundle',
        'Packaging Supplies',
        'Hardware Kit'
    ])

    # Receipt number configuration
    receipt_prefix: str = 'RCV'

    # Verbose logging
    verbose: bool = False


# ==================== MAIN GENERATOR ====================

class FlexibleTestInventoryGenerator:
    """
    Scalable test inventory generator with precise anomaly control
    """

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.inventory_data: List[Dict[str, Any]] = []
        self.anomaly_tracking: Dict[str, List[str]] = {}

        # Initialize anomaly tracking for all rule types
        self.rule_types = [
            'stagnant_pallets',
            'incomplete_lots',
            'overcapacity',
            'invalid_locations',
            'aisle_stuck',
            'scanner_errors',
            'location_mapping_errors'
        ]

        for rule_type in self.rule_types:
            self.anomaly_tracking[rule_type] = []

    # ==================== LOCATION GENERATION ====================

    def generate_storage_location(self) -> str:
        """Generate storage location in ###L format (e.g., 001A, 213B, 031C)"""
        position = random.randint(self.config.min_position, self.config.max_position)
        level = random.choice(self.config.levels)
        return f"{position:03d}{level}"

    def generate_receiving_location(self) -> str:
        """Generate receiving area location (RECV-01, RECV-02)"""
        return random.choice(self.config.receiving_areas)

    def generate_aisle_location(self) -> str:
        """Generate aisle location (AISLE-01 to AISLE-10)"""
        return random.choice(self.config.aisle_areas)

    def generate_wall_location(self) -> str:
        """Generate wall special location (W-01 to W-05)"""
        return random.choice(self.config.wall_areas)

    def generate_invalid_location(self) -> str:
        """Generate an invalid location code for testing"""
        invalid_formats = [
            'INVALID-LOC-01',
            'UNKNOWN',
            'TEMP-HOLD',
            'XXX-999',
            'NO-LOCATION',
            '999Z',  # Invalid level
            'MISSING'
        ]
        return random.choice(invalid_formats)

    # ==================== DATA GENERATION ====================

    def generate_pallet_id(self, index: int) -> str:
        """Generate unique pallet ID"""
        return f"PLT-{index:06d}"

    def generate_receipt_number(self, lot_num: Optional[int] = None) -> str:
        """Generate receipt/lot number"""
        if lot_num is not None:
            return f"{self.config.receipt_prefix}-LOT-{lot_num:04d}"
        else:
            return f"{self.config.receipt_prefix}-{random.randint(10000, 99999)}"

    def generate_product(self) -> str:
        """Generate product description"""
        return random.choice(self.config.products)

    def generate_creation_date(self, hours_ago: int = None) -> str:
        """Generate creation date timestamp"""
        if hours_ago is None:
            # Random age between 1 and 8 hours for normal pallets
            hours_ago = random.randint(1, 8)

        timestamp = datetime.now() - timedelta(hours=hours_ago)
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # ==================== BASE PALLET GENERATION ====================

    def generate_base_pallet(self, index: int) -> Dict[str, Any]:
        """Generate a clean base pallet (no anomalies)"""
        location = self.generate_storage_location()

        return {
            'pallet_id': self.generate_pallet_id(index),
            'location': location,
            'creation_date': self.generate_creation_date(),
            'receipt_number': self.generate_receipt_number(),
            'product': self.generate_product()
        }

    # ==================== ANOMALY INJECTION METHODS ====================

    def _inject_stagnant_pallets(self, anomaly_count: int):
        """
        Rule 1: Stagnant Pallets - Pallets in RECEIVING >10 hours

        Creates pallets in receiving areas that are 12-20 hours old
        """
        if self.config.verbose:
            print(f"  Injecting {anomaly_count} stagnant pallets...")

        for i in range(anomaly_count):
            location = self.generate_receiving_location()
            hours_old = random.randint(12, 20)  # Must be >10 hours

            pallet = {
                'pallet_id': f"STAGNANT-{i+1:03d}",
                'location': location,
                'creation_date': self.generate_creation_date(hours_ago=hours_old),
                'receipt_number': self.generate_receipt_number(),
                'product': self.generate_product()
            }

            self.inventory_data.append(pallet)
            self.anomaly_tracking['stagnant_pallets'].append(pallet['pallet_id'])

    def _inject_incomplete_lots(self, anomaly_count: int):
        """
        Rule 2: Incomplete Lots - Straggler pallets when 80%+ of lot is stored

        Creates lots where most pallets are in STORAGE but some remain in RECEIVING
        FIXED: Dynamically scales lot size based on anomaly count to maintain >80% threshold
        """
        if self.config.verbose:
            print(f"  Injecting {anomaly_count} incomplete lot stragglers...")

        # Create 2-3 lots with stragglers, ensuring each lot meets threshold
        num_lots = min(3, max(2, (anomaly_count + 1) // 2))
        stragglers_per_lot = anomaly_count // num_lots
        extra_stragglers = anomaly_count % num_lots

        for lot_num in range(num_lots):
            lot_id = 5000 + lot_num

            # Determine stragglers for this lot
            lot_stragglers = stragglers_per_lot
            if lot_num < extra_stragglers:
                lot_stragglers += 1

            # DYNAMIC LOT SIZING: Scale lot size to maintain >80% threshold
            # Formula: If we have S stragglers, we need T total where S/T < 0.2 (stragglers < 20%)
            # Therefore: T > S / 0.2 = S * 5
            # We use 90% stored (10% stragglers) for safety: T = S * 10

            min_lot_size_for_threshold = lot_stragglers * 5  # 80% threshold
            safe_lot_size = max(10, lot_stragglers * 10)  # 90% for reliability

            # Total pallets in lot
            total_in_lot = safe_lot_size
            straggler_count = lot_stragglers
            stored_count = total_in_lot - straggler_count

            # Verify math: stored_count / total_in_lot should be >80%
            stored_percentage = (stored_count / total_in_lot * 100) if total_in_lot > 0 else 0

            if self.config.verbose and anomaly_count > 10:
                print(f"    LOT{lot_id}: {total_in_lot} pallets total, {stored_count} stored ({stored_percentage:.0f}%), {straggler_count} stragglers")

            # Create stored pallets in STORAGE
            for i in range(stored_count):
                pallet = {
                    'pallet_id': f"LOT{lot_id}-{i+1:02d}",
                    'location': self.generate_storage_location(),
                    'creation_date': self.generate_creation_date(hours_ago=random.randint(24, 48)),
                    'receipt_number': self.generate_receipt_number(lot_num=lot_id),
                    'product': self.generate_product()
                }
                self.inventory_data.append(pallet)

            # Create stragglers in RECEIVING
            for i in range(straggler_count):
                pallet = {
                    'pallet_id': f"LOT{lot_id}-STRAGGLER-{i+1:02d}",
                    'location': self.generate_receiving_location(),
                    'creation_date': self.generate_creation_date(hours_ago=random.randint(2, 6)),
                    'receipt_number': self.generate_receipt_number(lot_num=lot_id),
                    'product': self.generate_product()
                }
                self.inventory_data.append(pallet)
                self.anomaly_tracking['incomplete_lots'].append(pallet['pallet_id'])

    def _inject_overcapacity(self, anomaly_count: int):
        """
        Rule 3: Overcapacity - Locations exceeding capacity

        CRITICAL: For storage locations, ALL pallets in overcapacity location are flagged
        For special areas, only 1 representative anomaly per location

        Strategy: Use special areas (RECV, AISLE, W) for predictable 1:1 mapping
        """
        if self.config.verbose:
            print(f"  Injecting {anomaly_count} overcapacity violations...")

        # Use special areas for predictable anomaly count
        # Each special area overcapacity = 1 anomaly

        for i in range(anomaly_count):
            if i < 2:
                # First 2: Overcapacity in wall areas (capacity=1, put 2 pallets)
                location = self.config.wall_areas[i]
                capacity = 1
                pallets_to_add = 2

            elif i < 4:
                # Next 2: Overcapacity in receiving (capacity=10, put 11-12 pallets)
                location = self.generate_receiving_location()
                capacity = self.config.receiving_capacity
                pallets_to_add = capacity + random.randint(1, 2)

            else:
                # Rest: Overcapacity in aisle (capacity=5, put 6-7 pallets)
                location = self.generate_aisle_location()
                capacity = self.config.aisle_capacity
                pallets_to_add = capacity + random.randint(1, 2)

            # Add pallets to this location (only 1 will be tracked as anomaly for special areas)
            for j in range(pallets_to_add):
                pallet = {
                    'pallet_id': f"OVERCAP-{i+1:02d}-{j+1:02d}",
                    'location': location,
                    'creation_date': self.generate_creation_date(hours_ago=random.randint(2, 5)),  # Fixed age: 2-5h (well below 10h threshold)
                    'receipt_number': self.generate_receipt_number(),
                    'product': self.generate_product()
                }
                self.inventory_data.append(pallet)

            # Track one representative anomaly per location
            self.anomaly_tracking['overcapacity'].append(f"OVERCAP-{i+1:02d}-01")

    def _inject_invalid_locations(self, anomaly_count: int):
        """
        Rule 4: Invalid Locations - Pallets in undefined locations

        Creates pallets with location codes not in warehouse template
        """
        if self.config.verbose:
            print(f"  Injecting {anomaly_count} invalid location pallets...")

        for i in range(anomaly_count):
            location = self.generate_invalid_location()

            pallet = {
                'pallet_id': f"INVALID-{i+1:03d}",
                'location': location,
                'creation_date': self.generate_creation_date(),
                'receipt_number': self.generate_receipt_number(),
                'product': self.generate_product()
            }

            self.inventory_data.append(pallet)
            self.anomaly_tracking['invalid_locations'].append(pallet['pallet_id'])

    def _inject_aisle_stuck(self, anomaly_count: int):
        """
        Rule 5: AISLE Stuck Pallets - Pallets in AISLE locations >4 hours

        Creates pallets in aisle locations that are 5-10 hours old
        """
        if self.config.verbose:
            print(f"  Injecting {anomaly_count} AISLE stuck pallets...")

        for i in range(anomaly_count):
            location = self.generate_aisle_location()
            hours_old = random.randint(5, 10)  # Must be >4 hours

            pallet = {
                'pallet_id': f"AISLE-STUCK-{i+1:03d}",
                'location': location,
                'creation_date': self.generate_creation_date(hours_ago=hours_old),
                'receipt_number': self.generate_receipt_number(),
                'product': self.generate_product()
            }

            self.inventory_data.append(pallet)
            self.anomaly_tracking['aisle_stuck'].append(pallet['pallet_id'])

    def _inject_scanner_errors(self, anomaly_count: int):
        """
        Rule 7: Scanner Errors - Data integrity issues

        Creates data quality problems:
        - Duplicate pallet IDs
        - Empty/missing required fields
        - Future dates
        """
        if self.config.verbose:
            print(f"  Injecting {anomaly_count} scanner errors...")

        # Split anomalies between different error types
        duplicate_count = anomaly_count // 2
        data_issue_count = anomaly_count - duplicate_count

        # Create duplicates
        for i in range(duplicate_count):
            duplicate_id = f"DUPLICATE-{i+1:03d}"

            # First occurrence
            pallet1 = {
                'pallet_id': duplicate_id,
                'location': self.generate_storage_location(),
                'creation_date': self.generate_creation_date(),
                'receipt_number': self.generate_receipt_number(),
                'product': self.generate_product()
            }

            # Second occurrence (duplicate)
            pallet2 = {
                'pallet_id': duplicate_id,  # SAME ID - scanner error!
                'location': self.generate_storage_location(),
                'creation_date': self.generate_creation_date(),
                'receipt_number': self.generate_receipt_number(),
                'product': self.generate_product()
            }

            self.inventory_data.append(pallet1)
            self.inventory_data.append(pallet2)
            self.anomaly_tracking['scanner_errors'].append(duplicate_id)

        # Create data integrity issues (empty fields, future dates)
        for i in range(data_issue_count):
            if i % 2 == 0:
                # Empty location (scanner didn't capture location)
                pallet = {
                    'pallet_id': f"DATA-ERROR-{i+1:03d}",
                    'location': '',  # EMPTY - data integrity issue!
                    'creation_date': self.generate_creation_date(),
                    'receipt_number': self.generate_receipt_number(),
                    'product': self.generate_product()
                }
            else:
                # Future date (timestamp error)
                future_date = datetime.now() + timedelta(days=random.randint(1, 7))
                pallet = {
                    'pallet_id': f"DATA-ERROR-{i+1:03d}",
                    'location': self.generate_storage_location(),
                    'creation_date': future_date.strftime("%Y-%m-%d %H:%M:%S"),  # FUTURE - impossible!
                    'receipt_number': self.generate_receipt_number(),
                    'product': self.generate_product()
                }

            self.inventory_data.append(pallet)
            self.anomaly_tracking['scanner_errors'].append(pallet['pallet_id'])

    def _inject_location_mapping_errors(self, anomaly_count: int):
        """
        Rule 8: Location Mapping Errors - DEPRECATED

        This rule is no longer applicable since we removed the location_type column.
        The system now auto-detects location types from location codes, making manual
        location_type mismatches impossible in real-world reports.

        This method is kept for backwards compatibility but does nothing.
        """
        if self.config.verbose:
            print(f"  Skipping location mapping errors (rule deprecated - no location_type column)")

        # Do not inject any anomalies for this rule
        pass

    # ==================== GENERATION ORCHESTRATION ====================

    def generate_inventory(self) -> pd.DataFrame:
        """
        Generate complete test inventory with anomalies

        Returns:
            DataFrame with all inventory data
        """
        if self.config.verbose:
            print(f"\n=== GENERATING TEST INVENTORY ===")
            print(f"Total pallets: {self.config.total_pallets}")
            print(f"Anomalies per rule: {self.config.anomalies_per_rule}")

        # Reset data
        self.inventory_data = []
        for rule_type in self.rule_types:
            self.anomaly_tracking[rule_type] = []

        # Inject anomalies first
        print(f"\nInjecting anomalies...")
        self._inject_stagnant_pallets(self.config.anomalies_per_rule)
        self._inject_incomplete_lots(self.config.anomalies_per_rule)
        self._inject_overcapacity(self.config.anomalies_per_rule)
        self._inject_invalid_locations(self.config.anomalies_per_rule)
        self._inject_aisle_stuck(self.config.anomalies_per_rule)
        self._inject_scanner_errors(self.config.anomalies_per_rule)
        self._inject_location_mapping_errors(self.config.anomalies_per_rule)

        # Calculate how many clean pallets we need
        current_pallet_count = len(self.inventory_data)
        clean_pallets_needed = self.config.total_pallets - current_pallet_count

        if self.config.verbose:
            print(f"\nGenerating {clean_pallets_needed} clean pallets...")

        # Generate clean pallets to reach target count
        for i in range(clean_pallets_needed):
            pallet = self.generate_base_pallet(1000 + i)
            self.inventory_data.append(pallet)

        # Convert to DataFrame
        df = pd.DataFrame(self.inventory_data)

        # Shuffle to mix anomalies with clean data
        df = df.sample(frac=1).reset_index(drop=True)

        return df

    def save_to_excel(self, df: pd.DataFrame) -> str:
        """
        Save inventory DataFrame to Excel file

        Returns:
            Path to saved file
        """
        # Generate filename if not provided
        if self.config.output_filename:
            filename = self.config.output_filename
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_inventory_{self.config.total_pallets}p_{self.config.anomalies_per_rule}a_{timestamp}.xlsx"

        # Ensure .xlsx extension
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'

        # Build full path
        output_path = Path(self.config.output_directory) / filename

        # Save to Excel
        df.to_excel(output_path, index=False)

        return str(output_path)

    def print_generation_report(self, df: pd.DataFrame, filepath: str):
        """Print detailed generation report"""
        print(f"\n{'='*60}")
        print(f"TEST INVENTORY GENERATION REPORT")
        print(f"{'='*60}")
        print(f"\nGeneral Statistics:")
        print(f"  Total Pallets: {len(df)}")

        total_anomalies = sum(len(pallets) for pallets in self.anomaly_tracking.values())
        print(f"  Total Anomalies Injected: {total_anomalies}")
        print(f"  Clean Pallets: {len(df) - total_anomalies}")

        print(f"\nAnomaly Breakdown:")
        anomaly_names = {
            'stagnant_pallets': 'Stagnant Pallets (RECEIVING >10h)',
            'incomplete_lots': 'Incomplete Lots (stragglers)',
            'overcapacity': 'Overcapacity (special areas)',
            'invalid_locations': 'Invalid Locations',
            'aisle_stuck': 'AISLE Stuck (>4h)',
            'scanner_errors': 'Scanner Errors (duplicates, data issues)',
            'location_mapping_errors': 'Location Mapping Errors'
        }

        for rule_type, pallets in self.anomaly_tracking.items():
            name = anomaly_names.get(rule_type, rule_type)
            count = len(pallets)
            print(f"  [OK] {name}: {count}")

        print(f"\nLocation Distribution:")
        # Note: location_type column removed - system auto-detects from location codes
        print(f"  - Total unique locations: {df['location'].nunique()}")

        print(f"\nOutput:")
        print(f"  File saved: {filepath}")
        print(f"  File size: {Path(filepath).stat().st_size / 1024:.2f} KB")

        print(f"\n{'='*60}")
        print(f"[SUCCESS] Generation complete! Upload this file to WareWise for testing.")
        print(f"{'='*60}\n")


# ==================== CLI INTERFACE ====================

def create_quick_config() -> GeneratorConfig:
    """Create quick test configuration (default: 100 pallets, 5 anomalies per rule)"""
    return GeneratorConfig(
        total_pallets=100,
        anomalies_per_rule=5,
        verbose=True
    )

def create_stress_test_config(pallets: int = 2000) -> GeneratorConfig:
    """Create stress test configuration"""
    return GeneratorConfig(
        total_pallets=pallets,
        anomalies_per_rule=5,
        verbose=True
    )

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Flexible Test Inventory Generator for WareWise',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test (100 pallets, 5 anomalies per rule)
  python flexible_test_generator.py --quick

  # Custom size
  python flexible_test_generator.py --pallets 500

  # Custom anomalies
  python flexible_test_generator.py --pallets 300 --anomalies 10

  # Stress test
  python flexible_test_generator.py --stress-test 2000

  # Custom output
  python flexible_test_generator.py --output ../my_test.xlsx
        """
    )

    # Main arguments
    parser.add_argument('--quick', action='store_true',
                       help='Quick test mode (100 pallets, 5 anomalies per rule)')
    parser.add_argument('--stress-test', type=int, metavar='PALLETS',
                       help='Stress test mode with specified pallet count')
    parser.add_argument('--pallets', type=int, default=100,
                       help='Total number of pallets to generate (default: 100)')
    parser.add_argument('--anomalies', type=int, default=5,
                       help='Anomalies per rule type (default: 5)')
    parser.add_argument('--output', type=str,
                       help='Output filename (auto-generated if not specified)')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose logging')

    args = parser.parse_args()

    # Create configuration based on arguments
    if args.quick:
        config = create_quick_config()
    elif args.stress_test:
        config = create_stress_test_config(args.stress_test)
    else:
        config = GeneratorConfig(
            total_pallets=args.pallets,
            anomalies_per_rule=args.anomalies,
            output_filename=args.output,
            verbose=args.verbose or True  # Always verbose by default
        )

    # Generate inventory
    generator = FlexibleTestInventoryGenerator(config)
    df = generator.generate_inventory()
    filepath = generator.save_to_excel(df)
    generator.print_generation_report(df, filepath)


if __name__ == "__main__":
    main()
