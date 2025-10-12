# Overcapacity Rule Test Suite

## Overview
Complete test suite for validating 100% accurate overcapacity rule detection in the Warehouse Intelligence Engine.

## Test Files Created

### 1. Surgical Precision Test (`overcapacity_surgical_test.xlsx`)
**Purpose**: Exact test case as requested with specific location format
- **Location 010A**: 2 pallets (capacity=1) → **SHOULD detect overcapacity**
- **Location 123C**: 1 pallet (capacity=1) → should NOT detect
- **Location 234E**: 1 pallet (capacity=1) → should NOT detect
- **Expected Result**: 2 anomalies (both pallets in 010A)

### 2. Edge Cases Test (`overcapacity_edge_cases_test.xlsx`)  
**Purpose**: Boundary conditions and location type variations
- **Boundary tests**: 1 vs 2 pallets in storage locations
- **Pattern tests**: Different storage location formats (###L, ##-##-###L)
- **Location type tests**: Storage vs Staging vs Receiving vs Unknown
- **Expected Result**: 16 total anomalies across multiple violation types

### 3. Stress Test (`overcapacity_stress_test.xlsx`)
**Purpose**: High-volume scenarios and extreme cases
- **Extreme overcapacity**: 10 pallets in single location (capacity=1)
- **Multiple violations**: 5 locations with 3 pallets each
- **Graduated severity**: 2, 4, 6, 8 pallets in different locations
- **High-volume normals**: 20 locations with exact capacity (should not trigger)
- **Expected Result**: 59 total anomalies with severity categorization

### 4. Mode Comparison Test (`overcapacity_mode_comparison_test.xlsx`)
**Purpose**: Validate consistency across different evaluation modes
- **Clear violations**: Multiple pallets in storage locations
- **Boundary cases**: Exact capacity matches
- **Special areas**: Staging area overcapacity
- **Expected Result**: All modes should detect same 11 anomalies

## Rule Engine Understanding

### Capacity Determination Logic
1. **Database lookup**: `pallet_capacity` field preferred over `capacity`  
2. **Location type defaults**:
   - `STORAGE`: capacity = 1 ✅ (Perfect for your requirement!)
   - `STAGING`: capacity = 5
   - `RECEIVING`: capacity = 10
   - `DOCK`: capacity = 2
3. **Pattern matching fallbacks**:
   - `###L` patterns (010A, 123C, 234E): capacity = 1 ✅
   - Hyphenated patterns with `-`: capacity = 1
   - Unknown patterns: capacity = 5 (conservative)

### Evaluation Modes
1. **Legacy Mode**: Simple `count > capacity` detection
2. **Enhanced Mode**: Location differentiation (currently active by default)
3. **Statistical Mode**: Advanced analysis with severity ratios (premium feature)

## Expected Test Results Summary

| Test File | Total Pallets | Violation Locations | Expected Anomalies | Key Focus |
|-----------|---------------|--------------------|--------------------|-----------|
| Surgical | 4 | 1 | 2 | Exact format compliance |
| Edge Cases | 20 | 7 | 16 | Boundary conditions |
| Stress Test | 80 | 12 | 59 | High-volume performance |
| Mode Comparison | 15 | 3 | 11 | Mode consistency |

## Validation Process

1. **Upload each test file** to the warehouse application
2. **Run the overcapacity rule** and capture results
3. **Compare actual vs expected anomalies**:
   - ✅ **Perfect accuracy**: Actual matches expected exactly
   - ⚠️ **False negatives**: Expected anomalies not detected  
   - ⚠️ **False positives**: Unexpected anomalies detected
4. **Analyze discrepancies** and refine rule logic if needed
5. **Iterate** until 100% accuracy is achieved

## Key Success Criteria

- **Surgical Test**: Must detect exactly 2 anomalies in location 010A
- **Edge Cases**: Must distinguish boundary conditions correctly
- **Stress Test**: Must handle high-volume scenarios without missing violations
- **Mode Comparison**: All evaluation modes must produce consistent core results

## Location Pattern Validation

All test files use the exact location patterns requested:
- ✅ **010A, 123C, 234E format**: `###L` pattern → capacity = 1
- ✅ **Systematic overcapacity**: 2+ pallets in capacity=1 locations
- ✅ **Clear expectations**: Explicit expected vs actual result tracking

Ready for comprehensive overcapacity rule validation! 🎯