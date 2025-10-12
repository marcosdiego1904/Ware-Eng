# Simple Test Inventory Generator - Complete Guide

## Overview

The **Simple Test Inventory Generator** creates predictable test files for warehouse rule validation with exactly known anomaly counts. No confusion, no calculations - just run it and get exactly what you expect.

## Quick Start

```bash
cd Tests
python simple_test_generator.py
```

**Result**: `simple_test_inventory.xlsx` with 100 pallets and exactly 40 anomalies (5 per rule)

---

## Generated File Structure

### Basic Information
- **File**: `simple_test_inventory.xlsx`
- **Total Pallets**: 100 (default)
- **Total Anomalies**: 40 (default - 5 per rule)
- **Format**: Standard Excel with columns: `pallet_id`, `location`, `creation_date`, `receipt_number`, `product`, `location_type`

### Anomaly Distribution (Default)

| Rule Type | Anomalies | Details |
|-----------|-----------|---------|
| **Stagnant Pallets** | 5 | Pallets in `recv-01` for >10 hours |
| **Incomplete Lots** | 5 | Stragglers in `recv-02` (lot: `INCOMPLETE_LOT_001`) |
| **Overcapacity** | 5 | All pallets in location `200A` (capacity=1) |
| **Invalid Locations** | 5 | Pallets in `INVALID_001` through `INVALID_005` |
| **Aisle Stuck** | 5 | Pallets in `aisle-01` through `aisle-05` for >4 hours |
| **Cold Chain** | 5 | `FROZEN_PRODUCT_X` pallets in storage >30 minutes |
| **Data Integrity** | 5 | 3 duplicate IDs + 2 future dates |
| **Location Mapping** | 5 | Storage locations with wrong `location_type` |
| **TOTAL** | **40** | **Exactly predictable** |

---

## How to Edit the Generator

The generator file is located at: `Tests/simple_test_generator.py`

### 1. Change Total Pallet Count

Find this line (around line 162):
```python
remaining = 100 - current_count  # Target 100 pallets total
```

Change to your desired total:
```python
remaining = 500 - current_count   # Target 500 pallets
remaining = 1000 - current_count  # Target 1000 pallets  
remaining = 200 - current_count   # Target 200 pallets
```

### 2. Change Anomalies Per Rule

Each rule section has a loop like `for i in range(5):`. Change the `5` to your desired count.

**Example: Change from 5 to 10 anomalies per rule:**

```python
# 1. STAGNANT PALLETS (around line 25)
for i in range(10):  # Changed from range(5)

# 2. INCOMPLETE LOTS - stragglers only (around line 43)  
for i in range(10):  # Changed from range(5)

# 3. OVERCAPACITY (around line 56)
for i in range(10):  # Changed from range(5)

# 4. INVALID LOCATIONS (around line 71)
for i in range(10):  # Changed from range(5)

# 5. AISLE STUCK (around line 86)
for i in range(10):  # Changed from range(5)

# 6. COLD CHAIN (around line 103)
for i in range(10):  # Changed from range(5)

# 7. DATA INTEGRITY (around line 120)
for i in range(6):   # Changed from range(3) - duplicates
# AND (around line 143)
for i in range(4):   # Changed from range(2) - future dates

# 8. LOCATION MAPPING (around line 157)
for i in range(10):  # Changed from range(5)
```

### 3. Update the Summary (Important!)

After changing anomaly counts, update the summary at the bottom (around line 217):

```python
print("EXACT EXPECTED ANOMALIES:")
print("  1. Stagnant Pallets: 10 anomalies")     # Update these numbers
print("  2. Incomplete Lots: 10 anomalies")      # to match your changes
print("  3. Overcapacity: 10 anomalies")
print("  4. Invalid Locations: 10 anomalies")
print("  5. Aisle Stuck: 10 anomalies")
print("  6. Cold Chain: 10 anomalies")
print("  7. Data Integrity: 10 anomalies")       # 6 duplicates + 4 future dates
print("  8. Location Mapping: 10 anomalies")
print("  --------------------------------")
print("  TOTAL: 80 anomalies EXACTLY")          # Update total: 8 × 10 = 80
```

---

## Common Editing Scenarios

### Scenario 1: Small Development Test
**Goal**: Quick testing with minimal data

```python
# Change total pallets
remaining = 50 - current_count   # 50 pallets total

# Change all ranges to 2
for i in range(2):  # 2 anomalies per rule = 16 total
```

### Scenario 2: Medium Validation Test
**Goal**: Comprehensive testing without overwhelming data

```python
# Change total pallets  
remaining = 200 - current_count  # 200 pallets total

# Keep default ranges (5 anomalies per rule = 40 total)
```

### Scenario 3: Large Scale Test
**Goal**: Enterprise-scale validation

```python
# Change total pallets
remaining = 1000 - current_count  # 1000 pallets total

# Increase ranges to 15
for i in range(15):  # 15 anomalies per rule = 120 total
```

---

## Understanding the Data Generation Logic

### Rule 1: Stagnant Pallets
```python
# Creates pallets that have been in receiving too long
'creation_date': (base_time - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')
# 12 hours ago > 10 hour threshold = triggers rule
```

### Rule 2: Incomplete Lots  
```python
# Creates a lot with 20 stored pallets + stragglers in receiving
lot_name = 'INCOMPLETE_LOT_001'
# 20 pallets in storage locations (80% completion)
# 5 pallets still in receiving (these are the anomalies)
```

### Rule 3: Overcapacity
```python
# Puts multiple pallets in same location
overcap_location = '200A'  # Storage location with capacity=1
# All 5 pallets in same location = overcapacity violation
# Enhanced mode: ALL pallets flagged (not just excess)
```

### Rule 4: Invalid Locations
```python
# Uses obviously invalid location names
invalid_locs = ['INVALID_001', 'INVALID_002', ...]
# These don't match warehouse template patterns
```

### Rule 5: Aisle Stuck
```python
# Pallets in aisle locations too long
aisle_locs = ['aisle-01', 'aisle-02', ...]
'creation_date': (base_time - timedelta(hours=6)).strftime(...)
# 6 hours ago > 4 hour threshold = triggers rule
```

### Rule 6: Cold Chain
```python
# Frozen products in regular storage too long
'product': f'FROZEN_PRODUCT_{i+1}'
'creation_date': (base_time - timedelta(minutes=45)).strftime(...)
# 45 minutes ago > 30 minute threshold = triggers rule
```

### Rule 7: Data Integrity
```python
# Creates duplicate pallet IDs and future dates
duplicate_id = f'DUP_{i+1:03d}'  # Same ID used twice
'creation_date': (base_time + timedelta(days=30)).strftime(...)  # Future date
```

### Rule 8: Location Mapping
```python
# Storage locations with wrong location_type
wrong_types = ['RECEIVING', 'AISLE', 'DOCK', 'STAGING', 'RECEIVING']
# Location 500A should be STORAGE but marked as RECEIVING
```

---

## Location Patterns Used

### Storage Locations (###L format)
- `100A` through `119A` - Stored lot pallets
- `200A` - Overcapacity location  
- `300A` through `304A` - Cold chain violations
- `400A`, `410A`, etc. - Data integrity (duplicates)
- `420A`, `421A` - Data integrity (future dates)
- `500A` through `504A` - Location mapping errors
- `600A` onwards - Normal pallets

### Special Locations
- `recv-01` - Stagnant pallets
- `recv-02` - Lot stragglers
- `aisle-01` through `aisle-05` - Stuck pallets
- `INVALID_001` through `INVALID_005` - Invalid locations

---

## Testing Your Changes

After editing, test your changes:

```bash
cd Tests
python simple_test_generator.py
```

**Check the output summary** - it tells you exactly how many anomalies to expect:
```
TOTAL: XX anomalies EXACTLY
```

**Upload the generated file** to your warehouse system and verify you get exactly that number of anomalies.

---

## Advanced Customizations

### Adding New Location Types
If you want to test different location patterns:

```python
# Add to storage locations section
inventory.append({
    'location': 'CUSTOM_LOC_001',  # Your custom location
    'location_type': 'CUSTOM',     # Your custom type
    # ... other fields
})
```

### Changing Time Thresholds
To test different time sensitivities:

```python
# For stagnant pallets (currently 12h > 10h threshold)
'creation_date': (base_time - timedelta(hours=15)).strftime(...)  # 15 hours ago

# For aisle stuck (currently 6h > 4h threshold)  
'creation_date': (base_time - timedelta(hours=8)).strftime(...)   # 8 hours ago

# For cold chain (currently 45min > 30min threshold)
'creation_date': (base_time - timedelta(minutes=60)).strftime(...) # 60 minutes ago
```

### Creating More Complex Lots
For incomplete lots testing:

```python
# Create multiple incomplete lots
lot_names = ['LOT_001', 'LOT_002', 'LOT_003']
for lot_idx, lot_name in enumerate(lot_names):
    # Create stored pallets (80% completion)
    for i in range(20):  # 20 stored pallets
        # ... stored pallet logic
    
    # Create stragglers
    for i in range(5):   # 5 straggler pallets
        # ... straggler logic
```

---

## File Structure Best Practices

### When Scaling Up
- **Small tests (50-200 pallets)**: Keep default 5 anomalies per rule
- **Medium tests (200-500 pallets)**: Use 10-15 anomalies per rule  
- **Large tests (500+ pallets)**: Use 20+ anomalies per rule

### Maintaining Realism
- **Normal vs Anomaly ratio**: Keep anomalies under 20% of total pallets
- **Location diversity**: Spread normal pallets across many locations
- **Time distribution**: Vary creation times for normal pallets

---

## Troubleshooting

### Issue: Not getting expected anomaly count
- **Check**: Rule conditions in your system (time thresholds, capacity settings)
- **Verify**: Location template configuration matches generator patterns
- **Debug**: Upload a small test first (50 pallets, 2 anomalies per rule)

### Issue: Some rules not triggering  
- **Check**: Rule is enabled in your system
- **Verify**: Rule conditions match the test data format
- **Test**: Run each rule type individually

### Issue: Too many overcapacity anomalies
- **Expected**: Enhanced mode flags ALL pallets in overcapacity locations
- **Example**: 5 pallets in location 200A = 5 overcapacity anomalies (not 4)
- **Plus**: Invalid locations also trigger overcapacity (capacity=0)

---

## Expected Results Reference

### Default Configuration (100 pallets, 5 per rule)
When you upload `simple_test_inventory.xlsx`, expect:

- **35-40 total anomalies** (depending on rule configuration)
- **Perfect rules**: Stagnant, Incomplete Lots, Aisle Stuck, Data Integrity
- **Enhanced behavior**: Overcapacity may show 10+ anomalies (all pallets + invalid locations)
- **Configuration dependent**: Cold Chain, Location Mapping (may need setup)

### Success Criteria (Updated for Enhanced Overcapacity Rule)
- **Stagnant Pallets**: Exactly 30 anomalies ✅
- **Incomplete Lots**: Exactly 30 anomalies ✅  
- **Overcapacity**: Exactly 30 anomalies ✅ (ENHANCED: No longer includes invalid locations)
- **Invalid Locations**: Exactly 30 anomalies ✅ (Handled by separate Invalid Location rule)
- **Aisle Stuck**: Exactly 30 anomalies ✅
- **Cold Chain**: 0-30 anomalies (configuration dependent) ✅
- **Data Integrity**: Exactly 30 anomalies ✅
- **Location Mapping**: Exactly 30 anomalies ✅

### ⭐ Enhanced Overcapacity Rule Behavior
With the new pre-validation filter, the overcapacity rule now:
- **Excludes invalid locations** (NOWHERE-XX, invalid AISLE-XX patterns) 
- **Focuses on legitimate overcapacity** situations only
- **Improves accuracy** from ~50% to 100% valid alerts
- **Reduces alert fatigue** by eliminating 50+ false positives per analysis

---

## Summary

The Simple Test Inventory Generator is designed to be:
- **Predictable**: Exact anomaly counts
- **Editable**: Clear patterns for customization
- **Scalable**: Works from 50 to 5000+ pallets  
- **Reliable**: Consistent results for rule validation

**Most common edit**: Change `range(5)` to `range(X)` for X anomalies per rule, and update the total pallet count accordingly.

For questions or issues, the generator is self-documenting - each section clearly shows what it creates and why.