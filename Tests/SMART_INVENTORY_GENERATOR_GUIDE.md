# Smart Inventory Generator - Complete Usage Guide

## Overview

The **Smart Inventory Generator** is an enterprise-ready system for creating precise test inventory files (`inventoryfile.xlsx`) with controlled anomaly distribution. Built based on extensive testing sessions and rule system analysis, it ensures template compatibility and accurate rule testing.

## Key Features

✅ **Template-Aware Location Format** - Uses proper `###L` format for compatibility  
✅ **8 Default Rule Types** - Covers all warehouse rules from your system  
✅ **Precise Anomaly Control** - Exactly the number of anomalies you specify  
✅ **Performance Optimized** - Generates large files quickly  
✅ **Format Validation** - Built-in compatibility checking  
✅ **Configurable Scale** - From small tests (100 pallets) to enterprise (5000+)  

---

## Quick Start

### 1. Basic Usage (Most Common)
```bash
# Generate standard 800-pallet test file with 15 anomalies per rule
python smart_inventory_generator.py --quick
```

**Result**: Creates `inventoryfile.xlsx` with 800 pallets and 120 total anomalies (15 × 8 rules)

### 2. Custom Size
```bash
# Generate 500-pallet file with 10 anomalies per rule
python smart_inventory_generator.py --pallets 500 --anomalies 10
```

### 3. Overcapacity-Focused Testing
```bash
# Test overcapacity rule with 25 anomalies, minimal other rules
python smart_inventory_generator.py --overcapacity-test 25
```

### 4. Large-Scale Stress Testing
```bash
# Generate enterprise-scale 2000-pallet stress test
python smart_inventory_generator.py --stress-test 2000
```

---

## Advanced Configuration

### Template Compatibility

**Critical**: Always verify your warehouse template levels before generating large files!

```bash
# Use custom valid levels (if you've expanded your template)
python smart_inventory_generator.py --levels A B C D E F G H J --pallets 1000

# Safe default (works with standard 5-level template)
python smart_inventory_generator.py --levels A B C D E --pallets 800
```

### Rule-Specific Testing

For targeted rule validation, you can create focused test files:

```python
# Example: Python script for custom rule distribution
from smart_inventory_generator import create_targeted_config, SmartInventoryGenerator

# Create custom configuration
config = create_targeted_config({
    'overcapacity': 50,     # Test overcapacity rule heavily
    'stagnant': 25,         # Some stagnant pallets
    'invalid': 10,          # Few invalid locations
    # Other rules get 0 anomalies
}, total_pallets=1000, output_name='overcapacity_focus_test.xlsx')

# Generate and save
generator = SmartInventoryGenerator(config)
df = generator.generate_comprehensive_inventory()
generator.save_to_excel(df)
```

---

## Rule Types & Behavior

### 1. **Stagnant Pallets** (`STAGNANT_PALLETS`)
- **Purpose**: Pallets in RECEIVING areas >10 hours
- **Anomaly Count**: 1 per qualifying pallet
- **Generation**: Uses `recv-01`, `recv-02`, etc.

### 2. **Incomplete Lots** (`UNCOORDINATED_LOTS`) 
- **Purpose**: Stragglers when 80%+ of lot is stored
- **Anomaly Count**: 1 per straggler pallet
- **Generation**: Creates complete lots + stragglers in receiving

### 3. **Overcapacity** (`OVERCAPACITY`) ⚠️ **Critical Understanding**
- **Purpose**: Locations exceeding designated capacity
- **Anomaly Count**: **ALL pallets** in overcapacity storage locations
- **Generation**: Places all target anomalies in single storage location
- **Example**: 15 pallets in one location → 15 anomalies (not 14!)

### 4. **Invalid Locations** (`INVALID_LOCATION`)
- **Purpose**: Pallets in undefined locations  
- **Anomaly Count**: 1 per pallet in invalid location
- **Generation**: Uses predefined invalid location names

### 5. **AISLE Stuck** (`LOCATION_SPECIFIC_STAGNANT`)
- **Purpose**: Pallets in AISLE locations >4 hours
- **Anomaly Count**: 1 per qualifying pallet
- **Generation**: Uses `aisle-01`, `aisle-02`, etc.

### 6. **Cold Chain** (`TEMPERATURE_ZONE_MISMATCH`)
- **Purpose**: Temperature products in wrong zones
- **Anomaly Count**: 1 per qualifying pallet  
- **Generation**: `FROZEN_` and `REFRIGERATED_` products in storage

### 7. **Data Integrity** (`DATA_INTEGRITY`)
- **Purpose**: Scanner errors, duplicate IDs, future dates
- **Anomaly Count**: 1 per data quality issue
- **Generation**: Mix of duplicates, future dates, empty locations

### 8. **Location Mapping** (`LOCATION_MAPPING_ERROR`)
- **Purpose**: Wrong location_type assignments
- **Anomaly Count**: 1 per mapping inconsistency
- **Generation**: Storage locations with wrong types

---

## File Output Structure

Generated files follow the exact format expected by your rule engine:

```
Columns: [pallet_id, location, creation_date, receipt_number, product, location_type]
```

### Location Format Compliance
- **Storage**: `###L` format (e.g., `100A`, `234E`, `567C`)
- **Special**: Pattern-based (e.g., `recv-01`, `STAGING_AREA_01`)  
- **Invalid**: Test locations (e.g., `999Z`, `FAKE-LOC`)

### Data Types
- **pallet_id**: Unique string identifiers
- **location**: Location codes (string)
- **creation_date**: Timestamp strings (`YYYY-MM-DD HH:MM:SS`)
- **receipt_number**: Lot/batch identifiers (string)
- **product**: Product descriptions (string)
- **location_type**: Categories (`RECEIVING`, `STORAGE`, `AISLE`, etc.)

---

## Performance & Scale Guidelines

### Recommended Sizes

| Test Type | Pallets | Anomalies/Rule | Generation Time | Use Case |
|-----------|---------|----------------|-----------------|----------|
| **Quick Test** | 100-300 | 5-10 | <1 second | Rule debugging |
| **Standard Test** | 500-1000 | 10-20 | 1-2 seconds | Comprehensive validation |
| **Stress Test** | 1500-3000 | 25-50 | 3-5 seconds | Performance testing |
| **Enterprise Scale** | 3000+ | 50+ | 5-10 seconds | Production simulation |

### Memory Usage
- **Typical**: ~1MB per 1000 pallets
- **Peak**: ~50MB during generation for 5000 pallets
- **Excel Output**: ~500KB per 1000 pallets

---

## Common Usage Patterns

### 1. Rule Development Workflow
```bash
# Small precise test for development
python smart_inventory_generator.py --pallets 100 --anomalies 5 --output rule_dev_test.xlsx

# Medium test for validation  
python smart_inventory_generator.py --pallets 500 --anomalies 15 --output validation_test.xlsx

# Large test for performance
python smart_inventory_generator.py --stress-test 2000 --output performance_test.xlsx
```

### 2. Regression Testing
```bash
# Create consistent test suite
python smart_inventory_generator.py --quick --output regression_baseline.xlsx
python smart_inventory_generator.py --overcapacity-test 30 --output regression_overcapacity.xlsx  
python smart_inventory_generator.py --stress-test 1500 --output regression_scale.xlsx
```

### 3. Customer Demo Preparation
```bash
# Realistic warehouse scenario
python smart_inventory_generator.py --pallets 1200 --anomalies 20 --output customer_demo.xlsx
```

---

## Troubleshooting

### Common Issues

#### ❌ **Over-Detection of Anomalies**
**Symptoms**: Getting way more anomalies than expected
**Cause**: Location format incompatibility → capacity=0 assignments
**Solution**: 
- Check your warehouse template configuration
- Verify valid levels with `--levels` parameter
- Use `--quick` for template-safe defaults

#### ❌ **Under-Detection of Anomalies**
**Symptoms**: Getting fewer anomalies than expected  
**Cause**: Enhanced mode consolidation behavior
**Solution**:
- Understand that special areas may consolidate alerts
- Use storage locations for predictable 1:1 anomaly mapping
- Refer to WAREHOUSE_RULES_SYSTEM_REFERENCE.md for counting logic

#### ❌ **Invalid Location Alerts**
**Symptoms**: Unexpected invalid location violations
**Cause**: Template format mismatch
**Solution**:
- Use only 3-digit + level format (`###L`)
- Stay within configured valid levels
- Test with small file first

### Debug Mode

For investigating issues, generate small diagnostic files:

```bash
# Minimal test for format validation
python smart_inventory_generator.py --pallets 50 --anomalies 2 --output debug_format.xlsx

# Single-rule focus
python smart_inventory_generator.py --overcapacity-test 3 --output debug_overcapacity.xlsx
```

---

## Integration with Testing Workflow

### 1. Pre-Test Validation
```bash
# Always validate template compatibility first
python smart_inventory_generator.py --pallets 100 --anomalies 3 --output template_check.xlsx
# → Upload to system and verify 0 invalid location alerts
```

### 2. Systematic Rule Testing
```bash
# Test each rule individually
python smart_inventory_generator.py --overcapacity-test 10 --output test_overcapacity.xlsx
# → Verify exactly 10 anomalies detected

# Then test combinations
python smart_inventory_generator.py --quick --output test_comprehensive.xlsx  
# → Verify all 8 rules working correctly
```

### 3. Performance Validation
```bash
# Scale up systematically  
python smart_inventory_generator.py --pallets 500 --output perf_500.xlsx    # Baseline
python smart_inventory_generator.py --pallets 1000 --output perf_1000.xlsx  # 2x scale
python smart_inventory_generator.py --pallets 2000 --output perf_2000.xlsx  # 4x scale
```

---

## Best Practices

### ✅ **Do This**
- Always start with small test files to validate template compatibility
- Use `--quick` for standard testing scenarios
- Verify anomaly counts match expectations before scaling up
- Keep test files organized with descriptive names
- Document your template configuration (valid levels, special areas)

### ❌ **Avoid This**
- Don't generate large files without validating format compatibility first
- Don't assume anomaly counts without understanding enhanced mode behavior
- Don't use invalid levels without expanding your warehouse template  
- Don't ignore invalid location alerts - they indicate format issues
- Don't generate massive files for simple rule testing

---

## Integration Examples

### Python Script Integration
```python
from smart_inventory_generator import SmartInventoryGenerator, create_quick_config

# Create configuration
config = create_quick_config(total_pallets=800, anomalies_per_rule=15)

# Customize specific rules
for rule in config.rules:
    if rule.rule_type == "OVERCAPACITY":
        rule.target_anomalies = 30  # More overcapacity testing
    elif rule.rule_type == "STAGNANT_PALLETS":
        rule.target_anomalies = 5   # Fewer stagnant pallets

# Generate
generator = SmartInventoryGenerator(config)
df = generator.generate_comprehensive_inventory()
filepath = generator.save_to_excel(df)

print(f"Generated test file: {filepath}")
```

### Automated Testing Pipeline
```bash
#!/bin/bash
# Automated test generation pipeline

echo "Generating test suite..."

# Small validation test
python smart_inventory_generator.py --pallets 100 --anomalies 3 --output pipeline_small.xlsx

# Standard comprehensive test  
python smart_inventory_generator.py --quick --output pipeline_standard.xlsx

# Overcapacity focus test
python smart_inventory_generator.py --overcapacity-test 25 --output pipeline_overcapacity.xlsx

# Scale test
python smart_inventory_generator.py --stress-test 1500 --output pipeline_scale.xlsx

echo "Test suite generation complete!"
```

---

## Advanced Features

### Custom Rule Configurations

For advanced users, you can create completely custom rule distributions:

```python
from smart_inventory_generator import GeneratorConfig, RuleConfig, SmartInventoryGenerator

# Create custom configuration
config = GeneratorConfig(
    total_pallets=1200,
    output_filename="custom_distribution.xlsx",
    valid_levels=['A', 'B', 'C', 'D', 'E', 'F'],  # Expanded levels
    rules=[
        RuleConfig("Custom Stagnant Test", "STAGNANT_PALLETS", True, 40),
        RuleConfig("Custom Overcapacity Test", "OVERCAPACITY", True, 60),
        RuleConfig("Custom Invalid Test", "INVALID_LOCATION", True, 20),
        # Enable only specific rules for focused testing
    ]
)

# Generate with custom configuration
generator = SmartInventoryGenerator(config)
df = generator.generate_comprehensive_inventory()
generator.save_to_excel(df)
```

---

## Summary

The Smart Inventory Generator provides:

🎯 **Precise Control** - Exactly the anomalies you need  
⚡ **Fast Generation** - Seconds, not minutes  
🔧 **Template Compatible** - Works with your existing setup  
📊 **Comprehensive Testing** - All 8 rule types covered  
🛡️ **Validation Built-in** - Catches format issues early  

**Most Common Command**:
```bash
python smart_inventory_generator.py --quick
```

This creates a standard 800-pallet test file with 120 total anomalies (15 per rule) that's ready for immediate testing with your warehouse rule system.

For questions or issues, refer to the troubleshooting section or examine the detailed comments in the `smart_inventory_generator.py` source code.

---

**Generated by**: Smart Inventory Generator System  
**Compatible with**: Warehouse Rules System v2.0+  
**Last Updated**: Based on MEGA_TEST_SESSION_REPORT_20250905.md insights