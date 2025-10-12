# Flexible Test Inventory Generator - Complete Guide

## 📖 Overview

The **Flexible Test Inventory Generator** is a precision tool for creating test inventory files with controlled anomaly injection to validate the WareWise rule engine. It supports progressive testing from small validation files (100 pallets) to large-scale stress tests (10,000+ pallets).

**Created**: 2025-01-09
**Version**: 2.0
**Status**: Production-Ready
**Last Updated**: 2025-01-09 (Removed location_type column)

---

## 🎯 Key Features

✅ **Progressive Scaling**: Scale from 100 to 10,000+ pallets with a single parameter
✅ **Fixed Anomaly Control**: Anomaly count independent of dataset size
✅ **Format-Aware**: Generates locations matching your warehouse template exactly
✅ **6 Active Rule Types**: Coverage of all applicable WareWise rules (Rule 8 deprecated)
✅ **Detailed Reports**: Complete breakdown of what was generated
✅ **Fast Generation**: 1000 pallets in <2 seconds
✅ **Real-World Format**: No location_type column - system auto-detects from location codes

---

## 🚀 Quick Start

### Basic Usage

```bash
# Navigate to Tests folder
cd Tests

# Quick test (100 pallets, 5 anomalies per rule)
python flexible_test_generator.py --quick

# Custom pallet count
python flexible_test_generator.py --pallets 500

# Custom anomalies per rule
python flexible_test_generator.py --pallets 300 --anomalies 10

# Stress test
python flexible_test_generator.py --stress-test 2000
```

### What You Get

Each run creates an Excel file with:
- **Total Pallets**: As specified (default: 100)
- **Anomalies**: 5 per rule × 6 active rules = 30 anomalies
- **Clean Pallets**: Remaining pallets (70 for default config)
- **Location Format**: ###L (001A, 213B, etc.) + special areas

---

## 📊 Rule Coverage

The generator injects anomalies for 6 active rule types (Rule 8 deprecated in v2.0):

### Rule 1: Stagnant Pallets
- **Type**: `STAGNANT_PALLETS`
- **Description**: Pallets in RECEIVING areas for >10 hours
- **Injection**: Creates pallets 12-20 hours old in RECV-01, RECV-02
- **Anomaly Count**: 1 per qualifying pallet
- **Example**: `STAGNANT-001` in RECV-01, 15 hours old

### Rule 2: Incomplete Lots
- **Type**: `UNCOORDINATED_LOTS`
- **Description**: Straggler pallets when 80%+ of lot is stored
- **Injection**: Creates 2-3 lots with 80% in STORAGE, rest in RECEIVING
- **Anomaly Count**: 1 per straggler pallet
- **Example**: LOT5000 has 8 pallets stored, 2 stragglers in receiving

### Rule 3: Overcapacity
- **Type**: `OVERCAPACITY`
- **Description**: Locations exceeding designated capacity
- **Injection**: Uses special areas (W-01, RECV, AISLE) for predictable counts
- **Anomaly Count**: **1 per overcapacity location** (special areas)
- **CRITICAL**: For storage locations, ALL pallets flagged (use special areas!)
- **Example**: W-01 (capacity=1) with 2 pallets

### Rule 4: Invalid Locations
- **Type**: `INVALID_LOCATION`
- **Description**: Pallets in locations not defined in warehouse
- **Injection**: Uses predefined invalid codes (INVALID-LOC-01, UNKNOWN, etc.)
- **Anomaly Count**: 1 per pallet
- **Example**: `INVALID-001` in location "UNKNOWN"

### Rule 5: AISLE Stuck Pallets
- **Type**: `LOCATION_SPECIFIC_STAGNANT`
- **Description**: Pallets in AISLE locations for >4 hours
- **Injection**: Creates pallets 5-10 hours old in AISLE-01 through AISLE-10
- **Anomaly Count**: 1 per qualifying pallet
- **Example**: `AISLE-STUCK-001` in AISLE-03, 7 hours old

### Rule 7: Scanner Errors
- **Type**: `DATA_INTEGRITY`
- **Description**: Data quality issues (duplicates, empty fields, future dates)
- **Injection**: Mix of duplicate pallet IDs and data issues
- **Anomaly Count**: 1 per data integrity issue
- **Example**:
  - `DUPLICATE-001` appears twice
  - `DATA-ERROR-001` has empty location
  - `DATA-ERROR-002` has future creation date

### ~~Rule 8: Location Mapping Errors~~ (DEPRECATED v2.0)
- **Type**: `LOCATION_MAPPING_ERROR`
- **Status**: ⚠️ **DEPRECATED** - No longer generates anomalies
- **Reason**: Real-world inventory reports don't include `location_type` column
- **System**: WareWise auto-detects location types from location codes
- **Note**: This rule caused 15 false positives in testing and is unnecessary

**Other Skipped Rules**:
- **Rule 6** (Cold Chain Violations): Not included - requires temperature-sensitive products not in basic specification

---

## 🏗️ Location Format Specification

### Storage Locations (###L Format)
- **Pattern**: `###L` where ### = 001-999, L = A-D
- **Examples**: `001A`, `213B`, `031C`, `456D`
- **Capacity**: 2 pallets per location
- **Location Type**: `STORAGE`

### Special Areas

#### Receiving Areas
- **Pattern**: `RECV-01`, `RECV-02`
- **Capacity**: 10 pallets per area
- **Location Type**: `RECEIVING`

#### Aisles
- **Pattern**: `AISLE-01` through `AISLE-10`
- **Capacity**: 5 pallets per aisle
- **Location Type**: `AISLE`

#### Wall Special Locations
- **Pattern**: `W-01` through `W-05`
- **Capacity**: 1 pallet per location
- **Location Type**: `SPECIAL`

#### Invalid Locations (for testing)
- **Patterns**: `INVALID-LOC-01`, `UNKNOWN`, `TEMP-HOLD`, `XXX-999`, `NO-LOCATION`, `999Z`, `MISSING`
- **Location Type**: `UNKNOWN`

---

## 📈 Progressive Testing Workflow

### Phase 1: Initial Validation (100 pallets)

**Goal**: Validate all rules trigger correctly

```bash
python flexible_test_generator.py --quick
```

**Expected Output**:
- 100 total pallets
- 30 anomalies (5 × 6 active rules)
- 70 clean pallets

**Upload to WareWise and verify**:
- [ ] Rule 1: 5 stagnant pallet anomalies detected
- [ ] Rule 2: 5 incomplete lot anomalies detected
- [ ] Rule 3: 5 overcapacity anomalies detected
- [ ] Rule 4: 5 invalid location anomalies detected
- [ ] Rule 5: 5 AISLE stuck anomalies detected
- [ ] Rule 7: 5 scanner error anomalies detected
- [ ] ~~Rule 8~~: 0 location mapping anomalies (deprecated)
- [ ] **Total: 30 anomalies**

### Phase 2: Medium Scale Testing (500 pallets)

**Goal**: Verify rules work with larger datasets

```bash
python flexible_test_generator.py --pallets 500
```

**Expected Output**:
- 500 total pallets
- Still 30 anomalies (same as Phase 1!)
- 470 clean pallets

**Key Validation**: Anomaly count should remain constant regardless of dataset size.

### Phase 3: Large Scale Testing (2000+ pallets)

**Goal**: Stress test performance and edge cases

```bash
python flexible_test_generator.py --stress-test 2000
```

**Expected Output**:
- 2000 total pallets
- Still 30 anomalies
- 1970 clean pallets

**Performance Target**: <5 seconds generation time

### Phase 4: Anomaly Scaling (Optional)

**Goal**: Test with more anomalies per rule

```bash
python flexible_test_generator.py --pallets 1000 --anomalies 20
```

**Expected Output**:
- 1000 total pallets
- 120 anomalies (20 × 6 active rules)
- 880 clean pallets

---

## 🎛️ Command Reference

### Quick Mode
```bash
python flexible_test_generator.py --quick
```
Default configuration: 100 pallets, 5 anomalies per rule

### Custom Pallet Count
```bash
python flexible_test_generator.py --pallets <count>
```
Generate specific number of pallets (minimum: 100, maximum: unlimited)

### Custom Anomalies Per Rule
```bash
python flexible_test_generator.py --pallets <count> --anomalies <num>
```
Control how many anomalies each rule type generates

### Stress Test Mode
```bash
python flexible_test_generator.py --stress-test <pallets>
```
Pre-configured for large-scale testing

### Custom Output Location
```bash
python flexible_test_generator.py --output <filename>
```
Specify custom output filename (default: auto-generated with timestamp)

### Verbose Mode
```bash
python flexible_test_generator.py --verbose
```
Detailed logging during generation (enabled by default)

### Help
```bash
python flexible_test_generator.py --help
```
Show all available options

---

## 📋 Output File Structure

### File Naming Convention
```
test_inventory_{pallets}p_{anomalies}a_{timestamp}.xlsx
```

**Example**: `test_inventory_100p_5a_20250109_143052.xlsx`

### Excel Columns

| Column | Type | Description |
|--------|------|-------------|
| `pallet_id` | String | Unique pallet identifier |
| `location` | String | Location code (###L or special area) |
| `creation_date` | Timestamp | When pallet entered location |
| `receipt_number` | String | Lot/receipt identifier |
| `product` | String | Product description |

**Note**: The `location_type` column was removed in v2.0. WareWise auto-detects location types from location codes.

### Sample Data

```
pallet_id,location,creation_date,receipt_number,product
PLT-001000,123A,2025-01-09 08:30:15,RCV-12345,Widget Assembly Kit
STAGNANT-001,RECV-01,2025-01-08 18:30:15,RCV-67890,Component Box A
LOT5000-01,456B,2025-01-08 10:30:15,RCV-LOT-5000,Finished Product SKU-001
OVERCAP-01-01,W-01,2025-01-09 09:15:22,RCV-23456,Packaging Supplies
INVALID-001,UNKNOWN,2025-01-09 07:45:30,RCV-34567,Hardware Kit
```

**Note**: No `location_type` column - system auto-detects from location code patterns.

---

## 🧪 Testing Scenarios

### Scenario 1: Rule Engine Validation
**Use Case**: Verify all rules detect anomalies correctly

```bash
# Generate small precise file
python flexible_test_generator.py --quick

# Upload to WareWise
# Verify EXACTLY 30 anomalies detected
# Check each rule type shows 5 anomalies (except Rule 8: 0)
```

### Scenario 2: Performance Benchmarking
**Use Case**: Test system performance with large datasets

```bash
# Generate progressively larger files
python flexible_test_generator.py --pallets 500
python flexible_test_generator.py --pallets 1000
python flexible_test_generator.py --stress-test 2000

# Measure upload and processing time
# Target: <10 seconds for 2000 pallets
```

### Scenario 3: Edge Case Testing
**Use Case**: Test system behavior with unusual data

```bash
# High anomaly density
python flexible_test_generator.py --pallets 200 --anomalies 20

# Very large file
python flexible_test_generator.py --stress-test 5000

# Minimal file
python flexible_test_generator.py --pallets 100 --anomalies 2
```

### Scenario 4: Regression Testing
**Use Case**: Ensure updates don't break existing functionality

```bash
# Generate baseline file
python flexible_test_generator.py --quick --output regression_baseline.xlsx

# After code changes, generate identical file
python flexible_test_generator.py --quick --output regression_test.xlsx

# Results should be identical (30 anomalies detected)
```

---

## 🔧 Advanced Configuration

### Modifying Location Ranges

Edit `flexible_test_generator.py`, `GeneratorConfig` class:

```python
@dataclass
class GeneratorConfig:
    # Position range for storage locations
    min_position: int = 1      # Change start position
    max_position: int = 999    # Change max position

    # Available levels
    levels: List[str] = field(default_factory=lambda: ['A', 'B', 'C', 'D', 'E'])  # Add more levels
```

### Adding More Special Areas

```python
@dataclass
class GeneratorConfig:
    # Add more receiving areas
    receiving_areas: List[str] = field(default_factory=lambda: ['RECV-01', 'RECV-02', 'RECV-03'])

    # Add more aisles
    aisle_areas: List[str] = field(default_factory=lambda: [f'AISLE-{i:02d}' for i in range(1, 21)])  # 20 aisles
```

### Changing Product List

```python
@dataclass
class GeneratorConfig:
    products: List[str] = field(default_factory=lambda: [
        'Your Product 1',
        'Your Product 2',
        'Your Product 3',
        # Add more products...
    ])
```

---

## ⚠️ Important Notes

### Overcapacity Rule Behavior

**CRITICAL UNDERSTANDING**: The overcapacity rule behaves differently for storage vs. special locations:

- **Storage Locations**: ALL pallets in overcapacity location are flagged as anomalies
  - Example: Location 123A (capacity=2) with 5 pallets → **5 anomalies**

- **Special Locations**: Only 1 representative anomaly per overcapacity location
  - Example: RECV-01 (capacity=10) with 12 pallets → **1 anomaly**

**Generator Strategy**: Uses special areas (RECV, AISLE, W-##) for predictable 1:1 anomaly mapping.

### Location Format Validation

**IMPORTANT**: Ensure your warehouse template supports all generated location formats:

- Storage: `001A` to `999D`
- Receiving: `RECV-01`, `RECV-02`
- Aisles: `AISLE-01` to `AISLE-10`
- Wall: `W-01` to `W-05`

If locations don't exist in template → False positive "Invalid Location" anomalies!

### Data Distribution

Generated data is **randomly shuffled** to mix anomalies with clean data, simulating real-world inventory reports.

---

## 🐛 Troubleshooting

### Problem: More than 30 anomalies detected

**Possible Causes**:
1. Storage locations used for overcapacity (multiplies anomalies)
2. Location format mismatch with warehouse template
3. Cross-contamination (pallets triggering multiple rules - this is OK!)

**Solution**:
- Verify warehouse template includes all generated location formats
- Check that only 6 rules are active (Rule 8 should be deprecated)
- Review overcapacity anomalies - should be in special areas only
- Note: Some overcounting is expected due to cross-rule detection (e.g., overcapacity pallet in AISLE >4h triggers both rules)

### Problem: Fewer than 30 anomalies detected

**Possible Causes**:
1. Some rules are inactive
2. Rule threshold configurations changed
3. Location classification issues

**Solution**:
- Verify 6 active rules are enabled in WareWise (Rules 1, 2, 3, 4, 5, 7)
- Check rule threshold settings (10h for stagnant, 4h for AISLE stuck, 80% for incomplete lots)
- Confirm Rule 8 is deprecated/inactive
- Verify system is auto-detecting location types correctly

### Problem: Generation fails

**Possible Causes**:
1. Missing dependencies (pandas, openpyxl)
2. Permission issues for output directory
3. Invalid configuration parameters

**Solution**:
```bash
# Install dependencies
pip install pandas openpyxl

# Check permissions
ls -l Tests/

# Verify configuration
python flexible_test_generator.py --help
```

---

## 📊 Performance Metrics

### Generation Speed

| Pallet Count | Generation Time | File Size |
|--------------|-----------------|-----------|
| 100 | <1 second | ~9 KB |
| 500 | ~1 second | ~35 KB |
| 1000 | ~2 seconds | ~68 KB |
| 2000 | ~3 seconds | ~135 KB |
| 5000 | ~7 seconds | ~330 KB |

### Memory Usage

- **Typical**: ~1 MB per 1000 pallets
- **Peak**: ~50 MB for 5000 pallets
- **Recommended**: 4+ GB RAM for 10,000+ pallet files

---

## 📝 Change Log

### Version 2.0 (2025-01-09) - Current
- ✅ **BREAKING**: Removed `location_type` column from generated files
- ✅ **BREAKING**: Deprecated Rule 8 (Location Mapping Errors)
- ✅ Reduced anomaly count from 35 to 30 (6 active rules)
- ✅ Updated documentation to reflect real-world inventory report format
- ✅ System now relies on auto-detection from location codes
- 🎯 **Why**: Real-world reports don't include location_type; auto-detection is more accurate

### Version 1.0 (2025-01-09)
- ✅ Initial release
- ✅ 7 rule types implemented
- ✅ Progressive scaling (100-10,000+ pallets)
- ✅ Format-aware location generation
- ✅ Detailed generation reports
- ✅ Command-line interface
- ✅ Comprehensive documentation

---

## 🎓 Best Practices

### ✅ Do This

1. **Start Small**: Always validate with 100-pallet file first
2. **Verify Template**: Ensure warehouse template matches location formats
3. **Progressive Testing**: Scale up systematically (100 → 500 → 1000 → 2000)
4. **Document Results**: Track anomaly counts for each test
5. **Version Control**: Keep test files for regression testing

### ❌ Avoid This

1. **Don't Skip Validation**: Never jump to large files without testing small ones first
2. **Don't Modify Anomaly Counts**: Keep at 5 per rule for consistency
3. **Don't Ignore Warnings**: If anomaly counts don't match, investigate immediately
4. **Don't Use Production Data**: Always use generated test files for validation
5. **Don't Forget Clean Pallets**: Clean data is as important as anomalies

---

## 🤝 Integration with WareWise

### Upload Workflow

1. **Generate File**:
   ```bash
   python flexible_test_generator.py --quick
   ```

2. **Upload to WareWise**:
   - Navigate to "New Analysis" in dashboard
   - Upload generated Excel file
   - Map columns (should auto-detect)

3. **Run Analysis**:
   - Click "Analyze"
   - Wait for rule engine to process

4. **Verify Results**:
   - Check total anomaly count (should be 30 for default config)
   - Review each rule type (should show 5 anomalies each, except Rule 8: 0)
   - Examine anomaly details for accuracy

### Expected Results (100-pallet file, v2.0)

```
=== ANALYSIS RESULTS ===
Total Anomalies Detected: 30

By Rule Type:
  - Stagnant Pallets: 5
  - Incomplete Lots: 5
  - Overcapacity: 5
  - Invalid Locations: 5
  - AISLE Stuck: 5
  - Scanner Errors: 5
  - Location Mapping Errors: 0 (deprecated)

Total Pallets Analyzed: 100
Clean Pallets: 70
```

---

## 📞 Support

For issues or questions:

1. **Check Documentation**: Review this guide thoroughly
2. **Verify Configuration**: Ensure warehouse template matches specifications
3. **Test Baseline**: Run `--quick` mode to validate basic functionality
4. **Review Output**: Check generation report for clues
5. **Inspect File**: Open Excel file manually to verify data

---

## 🚀 Future Enhancements

Potential improvements for future versions:

- [ ] Cold Chain Violations (Rule 6) support
- [ ] Custom anomaly distribution profiles
- [ ] JSON configuration files
- [ ] Multi-warehouse support
- [ ] Anomaly pattern templates
- [ ] Visual anomaly distribution reports
- [ ] CSV output format option
- [ ] Automated validation against WareWise API

---

**Document Version**: 2.0
**Last Updated**: 2025-01-09
**Maintained By**: WareWise Testing Team

---

**Ready to start testing?** Run your first test file:

```bash
cd Tests
python flexible_test_generator.py --quick
```

Upload the generated file to WareWise and verify all 30 anomalies are detected! 🎉

**Note**: If you're upgrading from v1.0, remember:
- Expected anomaly count changed: 35 → 30
- location_type column removed
- Rule 8 deprecated (no longer generates anomalies)
