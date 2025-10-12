#!/usr/bin/env python3
"""
Enhanced Comprehensive Test Inventory Generator
Tests the Location Type Dependency Crisis Resolution + Enhanced Classification

MAJOR CHANGES from original:
1. [INVALID] REMOVED location_type column - our enhanced classifier should handle this!
2. [VALID] INCREASED anomaly count for thorough testing
3. [VALID] ADDED new anomaly types for complete rule coverage
4. [VALID] ENHANCED pattern diversity for classification testing

This will generate 1000+ pallets with 350+ intentional anomalies across all 8 rules.
"""

import pandas as pd
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

class EnhancedInventoryGenerator:
    """Generate comprehensive test inventory WITHOUT location_type column"""

    def __init__(self):
        self.base_time = datetime.now()
        self.pallet_counter = 1
        self.inventory_data = []
        self.anomaly_count = 0  # Track injected anomalies

        # Track anomalies by type
        self.anomaly_tracker = {
            'STAGNANT_PALLETS': 0,
            'UNCOORDINATED_LOTS': 0,
            'OVERCAPACITY': 0,
            'INVALID_LOCATION': 0,
            'LOCATION_SPECIFIC_STAGNANT': 0,
            'TEMPERATURE_ZONE_MISMATCH': 0,
            'DATA_INTEGRITY': 0,
            'LOCATION_MAPPING_ERROR': 0
        }

        self._initialize_locations()

    def _initialize_locations(self):
        """Initialize comprehensive location pools for enhanced testing"""
        print("[ENHANCED] Initializing enhanced location pools...")

        # VALID STORAGE LOCATIONS (our enhanced classifier should detect these as STORAGE)
        self.valid_storage_locations = []

        # Standard format: 001A-100D (400 locations)
        for aisle_num in range(1, 101):
            for position_letter in ['A', 'B', 'C', 'D']:
                self.valid_storage_locations.append(f'{aisle_num:03d}{position_letter}')

        # Extended format: 101A-120D (80 more locations)
        for aisle_num in range(101, 121):
            for position_letter in ['A', 'B', 'C', 'D']:
                self.valid_storage_locations.append(f'{aisle_num:03d}{position_letter}')

        # VALID SPECIAL AREAS (enhanced classifier should detect these correctly)
        self.valid_special_locations = {
            'RECEIVING': ['RECV-01', 'RECV-02', 'RECEIVING-DOCK-A', 'INBOUND-01', 'REC-001', 'DOCK-RECEIVING'],
            'STAGING': ['STAGE-01', 'STAGE-02', 'STAGING-AREA-A', 'OUTBOUND-PREP', 'PREP-AREA-1'],
            'TRANSITIONAL': ['TRANSIT-01', 'WORK-IN-PROGRESS', 'SORT-01', 'TEMP-HOLD-1', 'BUFFER-ZONE-A'],
            'DOCK': ['DOCK-01', 'DOCK-02', 'DOOR-12', 'BAY-DOOR-3', 'TRUCK-DOCK-1', 'GATE-A'],
            'AISLE': ['AISLE-01', 'AISLE-02', 'AISLE-03', 'AISLE-A-12', 'CORRIDOR-01'],
            'SPECIAL': ['W-20', 'ALPHA-ZONE', 'BETA-STAGING']  # W-20 for overcapacity testing
        }

        # INVALID LOCATIONS (should be detected as UNKNOWN/MISSING by enhanced classifier)
        self.invalid_locations = [
            # Pattern-breaking locations
            *[f'BOX-{i:03d}' for i in range(1, 41)],  # More BOX locations
            *[f'ITEM-{chr(65 + i % 26)}-{i+1:03d}' for i in range(40)],  # More ITEM locations
            *[f'TEMP-{i:02d}' for i in range(1, 31)],  # More TEMP locations

            # Completely invalid formats
            'NOWHERE-01', 'INVALID-SPOT', 'UNKNOWN-LOC', 'MISSING-AREA',
            'UNDEFINED-01', 'NOT-FOUND', 'BAD-LOCATION', 'ERROR-LOC',
            'VOID-01', 'NULL-SPACE', 'LIMBO-01', 'LOST-PALLET',
            'MYSTERY-BOX', 'PHANTOM-01', 'GHOST-LOC', 'DEAD-ZONE',

            # Malformed "valid-looking" codes
            '025A', '030B', '099Z', '000A', '001X', '999Y', 'AAAA', 'BBBB',
            '12345', 'TOOLONG-LOCATION-NAME', '', '   ', '???'
        ]

        # RACK-STYLE LOCATIONS (should be detected as STORAGE)
        self.rack_locations = [
            *[f'RACK-{i}-{j}' for i in range(1, 21) for j in range(1, 6)],
            *[f'A-{i:02d}-{j:03d}{level}' for i in range(1, 11) for j in range(1, 16) for level in ['A', 'B']]
        ]

        print(f"  [VALID] Storage: {len(self.valid_storage_locations)} locations")
        print(f"  [VALID] Special: {sum(len(locs) for locs in self.valid_special_locations.values())} locations")
        print(f"  [VALID] Rack-style: {len(self.rack_locations)} locations")
        print(f"  [INVALID] Invalid: {len(self.invalid_locations)} locations")

    def generate_enhanced_inventory(self) -> pd.DataFrame:
        """Generate enhanced inventory with increased anomaly coverage"""
        print("\n[ENHANCED] COMPREHENSIVE INVENTORY GENERATOR")
        print("="*60)
        print("Testing: Location Type Dependency Crisis Resolution")
        print("Features: NO location_type column, Enhanced Classification")
        print()

        # Generate enhanced anomaly sets
        print("[ENHANCED_2K] Generating enhanced rule-specific anomalies for 2,000 pallets...")
        print("[ENHANCED_2K] Fresh anomaly patterns - larger scale stress test")

        # Rule 1: STAGNANT_PALLETS (60 anomalies - scaled up)
        self._generate_stagnant_pallets(60)

        # Rule 2: UNCOORDINATED_LOTS (50 anomalies - scaled up)
        self._generate_uncoordinated_lots(50)

        # Rule 3: OVERCAPACITY (80 anomalies - scaled up)
        self._generate_overcapacity_anomalies(80)

        # Rule 4: INVALID_LOCATION (200 anomalies - massive stress test)
        self._generate_invalid_location_anomalies(200)

        # Rule 5: LOCATION_SPECIFIC_STAGNANT (40 anomalies - scaled up)
        self._generate_aisle_stuck_pallets(40)

        # Rule 6: TEMPERATURE_ZONE_MISMATCH (50 anomalies - scaled up)
        self._generate_cold_chain_violations(50)

        # Rule 7: DATA_INTEGRITY (70 anomalies - scaled up)
        self._generate_data_integrity_issues(70)

        # Rule 8: LOCATION_MAPPING_ERROR (50 anomalies - scaled up)
        self._generate_location_mapping_errors(50)

        # Fill remaining slots with normal pallets
        remaining_slots = 2000 - len(self.inventory_data)
        self._generate_normal_pallets(remaining_slots)

        # Convert to DataFrame WITHOUT location_type column
        df = pd.DataFrame(self.inventory_data)
        # CRITICAL: Remove location_type column to test our enhanced classifier
        df = df[['pallet_id', 'location', 'creation_date', 'receipt_number', 'product']]

        return df

    def _add_pallet(self, pallet_data: Dict[str, Any], is_anomaly: bool = False, anomaly_type: str = None):
        """Add a pallet to inventory with anomaly tracking"""
        # Ensure creation_date is string format
        if isinstance(pallet_data['creation_date'], datetime):
            pallet_data['creation_date'] = pallet_data['creation_date'].strftime('%Y-%m-%d %H:%M:%S')

        # Use 'product' instead of 'description' for compatibility
        if 'description' in pallet_data:
            pallet_data['product'] = pallet_data.pop('description')

        # Track anomalies
        if is_anomaly and anomaly_type:
            self.anomaly_count += 1
            self.anomaly_tracker[anomaly_type] += 1

        self.inventory_data.append(pallet_data)
        self.pallet_counter += 1

    def _generate_stagnant_pallets(self, count: int):
        """Rule 1: STAGNANT_PALLETS - Enhanced with various receiving areas"""
        print(f"1. [STAGNANT] Stagnant Pallets: {count} anomalies")

        for i in range(count):
            # Vary the stagnant time (12-48 hours old)
            stagnant_hours = 12 + (i % 37)  # 12-48 hours
            stagnant_time = self.base_time - timedelta(hours=stagnant_hours)

            # Use different receiving areas
            receiving_locations = self.valid_special_locations['RECEIVING']
            location = receiving_locations[i % len(receiving_locations)]

            self._add_pallet({
                'pallet_id': f'STAGNANT_{self.pallet_counter:04d}',
                'location': location,
                'creation_date': stagnant_time,
                'receipt_number': f'STAGNANT_LOT_{i//5 + 1}',
                'product': f'Stagnant Product {i+1}'
            }, is_anomaly=True, anomaly_type='STAGNANT_PALLETS')

    def _generate_uncoordinated_lots(self, count: int):
        """Rule 2: UNCOORDINATED_LOTS - GUARANTEED TRIGGERS with 85%+ completion"""
        print(f"2. [UNCOORD] Uncoordinated Lots: {count} anomalies")
        print(f"   [TARGET] Creating lots with >80% completion to guarantee rule triggers")

        # Create 5 lots with GUARANTEED high completion ratios (85-95%)
        lots_to_create = min(5, (count // 5) + 1)
        stragglers_per_lot = max(1, count // lots_to_create)

        for lot_num in range(lots_to_create):
            lot_name = f'HIGH_COMPLETION_LOT_{lot_num+1:03d}'

            # Calculate completion ratio to guarantee >80% threshold
            # If we want 85% completion with X stragglers: stored_count = X * (0.85/0.15) = X * 5.67
            target_completion = 0.85 + (lot_num * 0.02)  # 85%, 87%, 89%, 91%, 93%
            stored_count = int(stragglers_per_lot * (target_completion / (1 - target_completion)))

            print(f"   [LOT] {lot_name}: {stored_count} stored + {stragglers_per_lot} stragglers = {target_completion:.1%} completion")

            # Create stored pallets (will be classified as STORAGE)
            for i in range(stored_count):
                location = self.valid_storage_locations[(lot_num * 50 + i) % len(self.valid_storage_locations)]
                self._add_pallet({
                    'pallet_id': f'STORED_{self.pallet_counter:04d}',
                    'location': location,
                    'creation_date': self.base_time - timedelta(hours=4 + lot_num),
                    'receipt_number': lot_name,
                    'product': f'Lot {lot_num+1} Stored Product {i+1}'
                })

            # Create stragglers (the anomalies) - explicitly in RECEIVING areas
            receiving_locations = self.valid_special_locations['RECEIVING']
            for i in range(stragglers_per_lot):
                if self.anomaly_tracker['UNCOORDINATED_LOTS'] >= count:
                    break

                location = receiving_locations[i % len(receiving_locations)]
                self._add_pallet({
                    'pallet_id': f'STRAGGLER_{self.pallet_counter:04d}',
                    'location': location,
                    'creation_date': self.base_time - timedelta(hours=1),
                    'receipt_number': lot_name,
                    'product': f'Lot {lot_num+1} Straggler Product {i+1}'
                }, is_anomaly=True, anomaly_type='UNCOORDINATED_LOTS')

        print(f"   [RESULT] Generated {self.anomaly_tracker['UNCOORDINATED_LOTS']} guaranteed stragglers")

    def _generate_overcapacity_anomalies(self, count: int):
        """Rule 3: OVERCAPACITY - Enhanced with multiple overcapacity scenarios"""
        print(f"3. [OVERCAP] Overcapacity: {count} anomalies")

        anomaly_locations = 0

        # W-20 mega overcapacity (capacity 1, put 15 pallets)
        for i in range(15):
            self._add_pallet({
                'pallet_id': f'W20_OVER_{self.pallet_counter:04d}',
                'location': 'W-20',
                'creation_date': self.base_time - timedelta(minutes=30 + i*2),
                'receipt_number': 'W20_OVERCAP_LOT',
                'product': f'W-20 Overcapacity Product {i+1}'
            }, is_anomaly=(i == 0), anomaly_type='OVERCAPACITY')  # Count as 1 location anomaly
        anomaly_locations += 1

        # Storage overcapacity (capacity 1, put 6 pallets each)
        storage_overcap_locations = (count - 1) // 6 + 1  # Calculate needed locations
        for loc_idx in range(min(storage_overcap_locations, (count - 1))):
            base_location = self.valid_storage_locations[100 + loc_idx]  # Use end of valid locations
            pallets_in_location = min(6, count - 1 - (loc_idx * 6))

            for pallet_idx in range(pallets_in_location):
                self._add_pallet({
                    'pallet_id': f'OVERCAP_{self.pallet_counter:04d}',
                    'location': base_location,
                    'creation_date': self.base_time - timedelta(hours=2, minutes=pallet_idx*5),
                    'receipt_number': f'OVERCAP_LOT_{loc_idx+1}',
                    'product': f'Overcapacity Product {loc_idx+1}-{pallet_idx+1}'
                }, is_anomaly=(pallet_idx == 0), anomaly_type='OVERCAPACITY')  # Count each location once
            anomaly_locations += 1

        print(f"   Created {anomaly_locations} overcapacity locations")

    def _generate_invalid_location_anomalies(self, count: int):
        """Rule 4: INVALID_LOCATION - FRESH PATTERNS for 2K test"""
        print(f"4. [INVALID] Invalid Locations: {count} anomalies")
        print(f"   [FRESH] Using completely new invalid patterns for 2K test")

        # FRESH invalid location patterns for 2K test
        fresh_invalid_patterns = [
            # Database corruption patterns
            'CORRUPTED-DB-001', 'LOST-DATA-002', 'SQL-ERROR-003',
            # Network/System failures
            'NET-TIMEOUT-001', 'SYS-CRASH-002', 'CONN-LOST-003',
            # Hardware failures
            'SCANNER-FAIL-001', 'PRINTER-JAM-002', 'DEVICE-ERROR-003',
            # Human error patterns
            'TYPO-LOCATION-001', 'WRONG-BUILDING-002', 'MISREAD-LABEL-003',
            # Impossible coordinates
            'FLOOR-99', 'AISLE-999', 'ZONE-XXX', 'BAY-000',
            # Special characters that break systems
            'LOC@TION-001', 'PLACE#002', 'AREA$003', 'SPOT%004',
            # Extremely long location names
            'EXTREMELY-LONG-LOCATION-NAME-THAT-BREAKS-SYSTEMS-001',
            'SUPER-ULTRA-MEGA-LONG-WAREHOUSE-LOCATION-NAME-002',
            # Empty/null-like patterns
            'NULL', 'UNDEFINED', 'EMPTY', 'BLANK',
            # Geographic impossibilities
            'NORTH-POLE-STORAGE', 'MARS-WAREHOUSE-001', 'MOON-BAY-002',
            # Time-based impossible locations
            'YESTERDAY-LOCATION', 'FUTURE-STORAGE-2030', 'TIME-PARADOX-001'
        ]

        # Extend with more patterns if needed
        base_patterns = len(fresh_invalid_patterns)
        while len(fresh_invalid_patterns) < count:
            fresh_invalid_patterns.extend([
                f'AUTO-INVALID-{i:03d}' for i in range(len(fresh_invalid_patterns) - base_patterns + 1,
                                                      min(len(fresh_invalid_patterns) - base_patterns + 51, count - base_patterns + 1))
            ])

        for i in range(count):
            location = fresh_invalid_patterns[i % len(fresh_invalid_patterns)]
            self._add_pallet({
                'pallet_id': f'INVALID_{self.pallet_counter:04d}',
                'location': location,
                'creation_date': self.base_time - timedelta(hours=1, minutes=i*2),
                'receipt_number': f'INVALID_LOT_{i+1}',
                'product': f'Fresh Invalid Pattern Product {i+1}'
            }, is_anomaly=True, anomaly_type='INVALID_LOCATION')

    def _generate_aisle_stuck_pallets(self, count: int):
        """Rule 5: LOCATION_SPECIFIC_STAGNANT - Enhanced aisle stuck scenarios"""
        print(f"5. [STUCK] AISLE Stuck: {count} anomalies")

        for i in range(count):
            # Vary stuck time (4-24 hours)
            stuck_hours = 4 + (i % 21)  # 4-24 hours
            stuck_time = self.base_time - timedelta(hours=stuck_hours)

            aisle_locations = self.valid_special_locations['AISLE']
            location = aisle_locations[i % len(aisle_locations)]

            self._add_pallet({
                'pallet_id': f'STUCK_{self.pallet_counter:04d}',
                'location': location,
                'creation_date': stuck_time,
                'receipt_number': f'STUCK_LOT_{i+1}',
                'product': f'Aisle Stuck Product {i+1}'
            }, is_anomaly=True, anomaly_type='LOCATION_SPECIFIC_STAGNANT')

    def _generate_cold_chain_violations(self, count: int):
        """Rule 6: TEMPERATURE_ZONE_MISMATCH - Enhanced cold chain testing"""
        print(f"6. [COLD] Cold Chain: {count} anomalies")

        # Enhanced frozen product patterns
        frozen_patterns = [
            'FROZEN_PRODUCT_', 'REFRIGERATED_ITEM_', 'ICE_CREAM_',
            'FROZEN_VEGETABLES_', 'REFRIGERATED_DAIRY_', 'COLD_STORAGE_ITEM_'
        ]

        for i in range(count):
            # Put frozen products in general storage (violation)
            location = self.valid_storage_locations[(200 + i) % len(self.valid_storage_locations)]
            violation_time = self.base_time - timedelta(minutes=30 + i*3)

            pattern = frozen_patterns[i % len(frozen_patterns)]

            self._add_pallet({
                'pallet_id': f'COLD_{self.pallet_counter:04d}',
                'location': location,
                'creation_date': violation_time,
                'receipt_number': f'FROZEN_LOT_{i+1}',
                'product': f'{pattern}{i+1}'
            }, is_anomaly=True, anomaly_type='TEMPERATURE_ZONE_MISMATCH')

    def _generate_data_integrity_issues(self, count: int):
        """Rule 7: DATA_INTEGRITY - Enhanced with more error types"""
        print(f"7. [INTEGRITY] Scanner Errors: {count} anomalies")

        # Split between duplicates, future dates, and malformed data
        duplicates = count // 3
        future_dates = count // 3
        malformed = count - duplicates - future_dates

        # Generate duplicates
        for i in range(duplicates):
            # Original
            self._add_pallet({
                'pallet_id': f'DUP_{i+1:03d}',
                'location': self.valid_storage_locations[(300 + i) % len(self.valid_storage_locations)],
                'creation_date': self.base_time - timedelta(hours=2),
                'receipt_number': f'ORIG_LOT_{i+1}',
                'product': f'Original Product {i+1}'
            })
            # Duplicate (anomaly)
            self._add_pallet({
                'pallet_id': f'DUP_{i+1:03d}',  # Same ID = anomaly
                'location': self.rack_locations[i % len(self.rack_locations)],
                'creation_date': self.base_time - timedelta(hours=1),
                'receipt_number': f'DUP_LOT_{i+1}',
                'product': f'Duplicate Product {i+1}'
            }, is_anomaly=True, anomaly_type='DATA_INTEGRITY')

        # Generate future dates
        for i in range(future_dates):
            future_days = 1 + (i % 90)  # 1-90 days in future
            self._add_pallet({
                'pallet_id': f'FUTURE_{self.pallet_counter:04d}',
                'location': self.valid_storage_locations[(320 + i) % len(self.valid_storage_locations)],
                'creation_date': self.base_time + timedelta(days=future_days),
                'receipt_number': f'FUTURE_LOT_{i+1}',
                'product': f'Future Product {i+1}'
            }, is_anomaly=True, anomaly_type='DATA_INTEGRITY')

        # Generate malformed data
        for i in range(malformed):
            self._add_pallet({
                'pallet_id': f'MALFORMED_{self.pallet_counter:04d}',
                'location': self.valid_storage_locations[(340 + i) % len(self.valid_storage_locations)],
                'creation_date': '2023-13-45 25:99:99',  # Invalid date format
                'receipt_number': '',  # Empty receipt
                'product': ''  # Empty product
            }, is_anomaly=True, anomaly_type='DATA_INTEGRITY')

    def _generate_location_mapping_errors(self, count: int):
        """Rule 8: LOCATION_MAPPING_ERROR - GUARANTEED TRIGGERS with impossible patterns"""
        print(f"8. [MAPPING] Location Mapping: {count} anomalies")
        print(f"   [TARGET] Creating locations that will definitely confuse pattern matching")

        # Create truly problematic location patterns that should trigger the rule
        # Mix expected patterns with wrong location types to create mapping errors
        problematic_patterns = [
            # Storage locations with products that should be in receiving
            ('001A', 'RECEIVING'),  # Storage location but should be receiving
            ('002B', 'RECEIVING'),  # Storage location but should be receiving
            ('003C', 'RECEIVING'),  # Storage location but should be receiving
            # Receiving locations with products that should be stored
            ('RECEIVING-01', 'STORAGE'),  # Receiving location but should be storage
            ('RECEIVING-02', 'STORAGE'),  # Receiving location but should be storage
            ('DOCK-RECEIVING-01', 'STORAGE'),  # Receiving location but should be storage
            # Impossible combinations
            ('STORAGE-RECEIVING-HYBRID', 'STORAGE'),  # Impossible hybrid
            ('DOCK-STORAGE-RACK-01', 'RECEIVING'),    # Impossible multi-type
            ('RECV-FINAL-DOCK-02', 'STORAGE'),       # Impossible chain
            # Completely invalid patterns
            ('UNKNOWN-TYPE-LOCATION', 'STORAGE'),     # Unknown pattern
            ('INVALID-PATTERN-123', 'RECEIVING'),     # Invalid pattern
            ('BROKEN-LOCATION-NAME', 'STORAGE'),      # Broken pattern
        ]

        pattern_index = 0
        for i in range(count):
            location, intended_type = problematic_patterns[pattern_index % len(problematic_patterns)]
            pattern_index += 1

            # Create products that suggest they should be in the intended_type location
            if intended_type == 'RECEIVING':
                product_name = f'Incoming Product {i+1} - Should be in RECEIVING'
                receipt_prefix = 'INCOMING'
            else:
                product_name = f'Stored Product {i+1} - Should be in STORAGE'
                receipt_prefix = 'STORED'

            self._add_pallet({
                'pallet_id': f'MAPPING_{self.pallet_counter:04d}',
                'location': location,
                'creation_date': self.base_time - timedelta(hours=1, minutes=i*3),
                'receipt_number': f'{receipt_prefix}_LOT_{i+1}',
                'product': product_name
            }, is_anomaly=True, anomaly_type='LOCATION_MAPPING_ERROR')

            if i < 10:  # Show first 10 for debugging
                print(f"   [MISMATCH] '{location}' (classified as ?) vs intended '{intended_type}'")

        print(f"   [RESULT] Generated {count} location mapping conflicts")

    def _generate_normal_pallets(self, count: int):
        """Fill remaining slots with normal, compliant pallets"""
        print(f"\n[VALID] Filling {count} normal pallets...")

        all_valid_locations = (
            self.valid_storage_locations +
            self.rack_locations +
            [loc for locs in self.valid_special_locations.values() for loc in locs]
        )

        for i in range(count):
            location = all_valid_locations[i % len(all_valid_locations)]

            # Vary creation times for realistic distribution
            hours_ago = 1 + (i % 72)  # 1-72 hours ago

            self._add_pallet({
                'pallet_id': f'NORMAL_{self.pallet_counter:04d}',
                'location': location,
                'creation_date': self.base_time - timedelta(hours=hours_ago),
                'receipt_number': f'NORMAL_LOT_{i//10 + 1}',
                'product': f'Normal Product {i+1}'
            })

def main():
    """Generate enhanced comprehensive test inventory"""
    generator = EnhancedInventoryGenerator()
    df = generator.generate_enhanced_inventory()

    # Save to Excel
    filename = "enhanced_test_inventory_2k.xlsx"
    df.to_excel(filename, index=False)

    # Comprehensive analysis
    total_pallets = len(df)
    total_anomalies = generator.anomaly_count

    # Location analysis
    storage_like = len([loc for loc in df['location'] if loc.endswith(('A', 'B', 'C', 'D')) and len(loc) == 4])
    rack_like = len([loc for loc in df['location'] if 'RACK-' in loc or 'A-' in loc])
    special_like = len([loc for loc in df['location'] if any(word in loc for word in ['RECV', 'DOCK', 'STAGE', 'AISLE', 'TRANSIT'])])
    invalid_like = len([loc for loc in df['location'] if loc.startswith(('BOX-', 'ITEM-', 'TEMP-')) or loc in ['NOWHERE-01', 'INVALID-SPOT', '', '   ']])

    print("\n" + "="*60)
    print("[SUCCESS] ENHANCED INVENTORY GENERATION COMPLETE")
    print("="*60)
    print(f"[FILE] File: {filename}")
    print(f"[STATS] Total pallets: {total_pallets}")
    print(f"[ANOMALIES] Total anomalies injected: {total_anomalies}")
    print()
    print("[BREAKDOWN] EXACT ANOMALY BREAKDOWN:")
    for rule_type, count in generator.anomaly_tracker.items():
        if count > 0:
            print(f"   {rule_type}: {count} anomalies")
    print()
    print("[LOCATION] LOCATION PATTERN DISTRIBUTION:")
    print(f"   [STORAGE] Storage-like (###A format): {storage_like} pallets")
    print(f"   [RACK] Rack-like (RACK-# format): {rack_like} pallets")
    print(f"   [SPECIAL] Special areas (RECV/DOCK/etc): {special_like} pallets")
    print(f"   [INVALID] Invalid patterns: {invalid_like} pallets")
    print()
    print("[TEST] TESTING OBJECTIVES:")
    print("   [VALID] Location Type Dependency Crisis Resolution")
    print("   [VALID] Enhanced Classification System Validation")
    print("   [VALID] NO location_type column provided")
    print("   [VALID] Maximum anomaly coverage for all 8 rules")
    print("   [VALID] Pattern diversity for classifier testing")
    print()
    print(f"[SUCCESS] Ready for comprehensive testing with {total_anomalies} known anomalies!")

    # Expected vs actual comparison table
    print("\n" + "="*60)
    print("[EXPECTED] EXPECTED ANOMALY RESULTS FOR COMPARISON:")
    print("="*60)
    expected_total = sum(generator.anomaly_tracker.values())
    print(f"[TARGET] Expected Total Anomalies: {expected_total}")
    print("[COMPARE] Compare this with actual results from rule engine!")

if __name__ == "__main__":
    main()