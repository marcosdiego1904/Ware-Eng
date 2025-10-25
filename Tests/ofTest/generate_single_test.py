#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single Test File Generator for WareWise Progressive Testing

Usage:
    python generate_single_test.py <pallets> <anomalies_per_rule>

Examples:
    python generate_single_test.py 100 5      # Baseline test
    python generate_single_test.py 500 5      # Medium scale
    python generate_single_test.py 1000 10    # High density

Generates ONE test file with detailed validation report.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add TestDone to path to import flexible generator
sys.path.insert(0, str(Path(__file__).parent.parent / "TestDone"))

# Import the flexible generator
try:
    from flexible_test_generator import FlexibleTestInventoryGenerator, GeneratorConfig
except ImportError as e:
    print("ERROR: Could not import flexible_test_generator.py")
    print(f"Make sure flexible_test_generator.py exists in Tests/TestDone/")
    print(f"Import error: {e}")
    sys.exit(1)


def print_usage():
    """Print usage information"""
    print(__doc__)


def generate_single_test(pallets: int, anomalies_per_rule: int):
    """
    Generate a single test file with detailed reporting

    Args:
        pallets: Total number of pallets to generate
        anomalies_per_rule: Number of anomalies per rule type
    """

    # Create descriptive filename
    filename = f"test_{pallets}p_{anomalies_per_rule}a.xlsx"
    output_path = Path(__file__).parent / filename

    print("\n" + "="*70)
    print("WAREWISE PROGRESSIVE TEST GENERATOR")
    print("="*70)
    print(f"\nGenerating: {filename}")
    print(f"Pallets: {pallets:,}")
    print(f"Anomalies per rule: {anomalies_per_rule}")
    print(f"Expected total anomalies: {anomalies_per_rule * 6} (6 active rules)")
    print("\n" + "-"*70)

    # Create configuration
    config = GeneratorConfig(
        total_pallets=pallets,
        anomalies_per_rule=anomalies_per_rule,
        output_filename=filename,
        output_directory=str(Path(__file__).parent),
        verbose=False  # We'll create our own detailed report
    )

    # Generate inventory
    print("\n[*] Generating inventory data...")
    start_time = datetime.now()

    generator = FlexibleTestInventoryGenerator(config)
    df = generator.generate_inventory()

    # Save to Excel
    print("[*] Saving to Excel...")
    filepath = generator.save_to_excel(df)

    generation_time = (datetime.now() - start_time).total_seconds()

    print(f"[OK] File saved: {filepath}")
    print(f"[*] Generation time: {generation_time:.2f} seconds")

    # Print detailed anomaly report
    print("\n" + "="*70)
    print("DETAILED ANOMALY REPORT (Expected Detection)")
    print("="*70)

    total_expected = 0

    # Rule 1: Stagnant Pallets
    print(f"\n[OK] Rule 1: Stagnant Pallets (RECEIVING >10h)")
    print(f"  Expected: {len(generator.anomaly_tracking['stagnant_pallets'])} anomalies")
    if generator.anomaly_tracking['stagnant_pallets']:
        print(f"  Pallet IDs: {', '.join(generator.anomaly_tracking['stagnant_pallets'][:5])}")
        if len(generator.anomaly_tracking['stagnant_pallets']) > 5:
            print(f"              ... and {len(generator.anomaly_tracking['stagnant_pallets']) - 5} more")
    print(f"  Locations: RECV-01, RECV-02")
    print(f"  Age: 12-20 hours (threshold: >10h)")
    total_expected += len(generator.anomaly_tracking['stagnant_pallets'])

    # Rule 2: Incomplete Lots
    print(f"\n[OK] Rule 2: Incomplete Lots (stragglers when 80%+ stored)")
    print(f"  Expected: {len(generator.anomaly_tracking['incomplete_lots'])} anomalies")
    if generator.anomaly_tracking['incomplete_lots']:
        print(f"  Pallet IDs: {', '.join(generator.anomaly_tracking['incomplete_lots'][:5])}")
        if len(generator.anomaly_tracking['incomplete_lots']) > 5:
            print(f"              ... and {len(generator.anomaly_tracking['incomplete_lots']) - 5} more")
    print(f"  Pattern: 90% of lot in STORAGE, stragglers in RECEIVING")
    total_expected += len(generator.anomaly_tracking['incomplete_lots'])

    # Rule 3: Overcapacity
    print(f"\n[OK] Rule 3: Overcapacity (locations exceeding capacity)")
    print(f"  Expected: {len(generator.anomaly_tracking['overcapacity'])} injected anomalies")
    if generator.anomaly_tracking['overcapacity']:
        print(f"  Pallet IDs: {', '.join(generator.anomaly_tracking['overcapacity'][:5])}")
        if len(generator.anomaly_tracking['overcapacity']) > 5:
            print(f"              ... and {len(generator.anomaly_tracking['overcapacity']) - 5} more")
    print(f"  Strategy: Special areas (W-01, W-02, RECV, AISLE)")
    print(f"  Note: May see additional emergent overcapacity in storage locations")
    if pallets >= 2000:
        print(f"        (Expected for {pallets:,} pallets due to statistical distribution)")
    total_expected += len(generator.anomaly_tracking['overcapacity'])

    # Rule 4: Invalid Locations
    print(f"\n[OK] Rule 4: Invalid Locations (undefined location codes)")
    print(f"  Expected: {len(generator.anomaly_tracking['invalid_locations'])} anomalies")
    if generator.anomaly_tracking['invalid_locations']:
        print(f"  Pallet IDs: {', '.join(generator.anomaly_tracking['invalid_locations'][:5])}")
        if len(generator.anomaly_tracking['invalid_locations']) > 5:
            print(f"              ... and {len(generator.anomaly_tracking['invalid_locations']) - 5} more")
    print(f"  Locations: UNKNOWN, MISSING, 999Z, TEMP-HOLD, XXX-999, etc.")
    total_expected += len(generator.anomaly_tracking['invalid_locations'])

    # Rule 5: AISLE Stuck
    print(f"\n[OK] Rule 5: AISLE Stuck Pallets (AISLE locations >4h)")
    print(f"  Expected: {len(generator.anomaly_tracking['aisle_stuck'])} anomalies")
    if generator.anomaly_tracking['aisle_stuck']:
        print(f"  Pallet IDs: {', '.join(generator.anomaly_tracking['aisle_stuck'][:5])}")
        if len(generator.anomaly_tracking['aisle_stuck']) > 5:
            print(f"              ... and {len(generator.anomaly_tracking['aisle_stuck']) - 5} more")
    print(f"  Locations: AISLE-01 through AISLE-10")
    print(f"  Age: 5-10 hours (threshold: >4h)")
    total_expected += len(generator.anomaly_tracking['aisle_stuck'])

    # Rule 7: Scanner Errors
    print(f"\n[OK] Rule 7: Scanner Errors (data integrity issues)")
    print(f"  Expected: {len(generator.anomaly_tracking['scanner_errors'])} anomalies")
    if generator.anomaly_tracking['scanner_errors']:
        print(f"  Pallet IDs: {', '.join(generator.anomaly_tracking['scanner_errors'][:5])}")
        if len(generator.anomaly_tracking['scanner_errors']) > 5:
            print(f"              ... and {len(generator.anomaly_tracking['scanner_errors']) - 5} more")
    print(f"  Types: Duplicate IDs, empty locations, future dates")
    total_expected += len(generator.anomaly_tracking['scanner_errors'])

    # Summary
    print("\n" + "="*70)
    print(f"SUMMARY")
    print("="*70)
    print(f"Total Pallets: {len(df):,}")
    print(f"Total Injected Anomalies: {total_expected}")
    print(f"Clean Pallets: {len(df) - total_expected:,}")
    print(f"Anomaly Rate: {(total_expected / len(df) * 100):.1f}%")
    print(f"\nFile: {filepath}")
    print(f"Size: {Path(filepath).stat().st_size / 1024:.2f} KB")

    # Validation checklist
    print("\n" + "="*70)
    print("VALIDATION CHECKLIST")
    print("="*70)
    print("\nNext Steps:")
    print("1. [ ] Upload file to WareWise > New Analysis")
    print("2. [ ] Run analysis")
    print(f"3. [ ] Verify total anomaly count: {total_expected} expected")
    print("\nPer-Rule Validation:")
    print(f"   [ ] Rule 1 (Stagnant): {len(generator.anomaly_tracking['stagnant_pallets'])} expected")
    print(f"   [ ] Rule 2 (Incomplete Lots): {len(generator.anomaly_tracking['incomplete_lots'])} expected")
    print(f"   [ ] Rule 3 (Overcapacity): {len(generator.anomaly_tracking['overcapacity'])} expected (+ emergent)")
    print(f"   [ ] Rule 4 (Invalid Locations): {len(generator.anomaly_tracking['invalid_locations'])} expected")
    print(f"   [ ] Rule 5 (AISLE Stuck): {len(generator.anomaly_tracking['aisle_stuck'])} expected")
    print(f"   [ ] Rule 7 (Scanner Errors): {len(generator.anomaly_tracking['scanner_errors'])} expected")

    print("\nIf Results Don't Match:")
    print("  > Check warehouse template includes all location formats")
    print("  > Verify rule thresholds (10h, 4h, 80%)")
    print("  > Review location type detection")
    print("  > Compare detected pallet IDs with report above")

    if pallets >= 2000:
        print("\n[!] IMPORTANT NOTE for large files:")
        print("    Overcapacity will show MORE than injected count due to emergent")
        print("    violations from statistical distribution (this is CORRECT behavior).")
        print(f"    At {pallets:,} pallets, expect ~{int(pallets * 0.18)} total overcapacity detections")

    print("\n" + "="*70)
    print("Generation Complete!")
    print("="*70)
    print(f"\nFile ready: {filename}")
    print("Upload to WareWise and validate results before generating next test.\n")


def main():
    """Main entry point"""

    # Check arguments
    if len(sys.argv) != 3:
        print("ERROR: Wrong number of arguments\n")
        print_usage()
        sys.exit(1)

    try:
        pallets = int(sys.argv[1])
        anomalies_per_rule = int(sys.argv[2])
    except ValueError:
        print("ERROR: Arguments must be integers\n")
        print_usage()
        sys.exit(1)

    # Validate inputs
    if pallets < 50:
        print("ERROR: Pallets must be at least 50")
        sys.exit(1)

    if anomalies_per_rule < 1:
        print("ERROR: Anomalies per rule must be at least 1")
        sys.exit(1)

    if anomalies_per_rule > pallets // 10:
        print(f"[!] WARNING: {anomalies_per_rule} anomalies per rule in {pallets} pallets")
        print(f"    This is a high density ({(anomalies_per_rule * 6 / pallets * 100):.1f}% anomaly rate)")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)

    # Generate test
    try:
        generate_single_test(pallets, anomalies_per_rule)
    except Exception as e:
        print(f"\nERROR: Generation failed")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
