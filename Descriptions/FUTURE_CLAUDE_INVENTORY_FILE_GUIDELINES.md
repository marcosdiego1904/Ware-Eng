# Future Claude: Critical Guidelines for Creating Inventory Test Files

## Overview
This document contains essential learnings from our overcapacity rule testing session. Follow these guidelines to avoid format compatibility issues and ensure accurate test results.

---

## 🚨 CRITICAL: Location Format Requirements

### Virtual Engine Location Format Constraints
The system uses a **virtual engine with strict location format validation**. Before creating ANY inventory test file, understand the warehouse template configuration:

#### **Storage Location Format: `###L` (3-digit + level)**
- **Correct Format**: `050A`, `123C`, `234E` (3 digits + single letter)
- **WRONG Format**: `1000A`, `2087B` (4+ digits will be flagged as invalid locations)

#### **Level Constraints (CRITICAL)**
The virtual engine only accepts specific levels defined in the warehouse template:
- **Default levels**: A, B, C, D, E (5 levels)
- **Expanded levels**: A, B, C, D, E, F, G, H, J (9 levels) - after user added missing levels
- **Invalid levels**: K (and potentially others not in template)

**⚠️ WARNING**: Using invalid levels (like F, G, H, J, K when not configured) will result in:
- Locations flagged as "Invalid Location" 
- Capacity assignments of 0 instead of expected values
- Every pallet becoming an "overcapacity violation" due to capacity=0
- Massive over-detection of anomalies

---

## 📋 Pre-Test Validation Checklist

### Before Creating ANY Inventory Test File:

1. **Ask the user about current warehouse template configuration**:
   - "What levels are currently valid in your warehouse template?"
   - "Are you using the default 5 levels (A-E) or expanded configuration?"

2. **Validate location format compatibility**:
   - Use only 3-digit storage locations: `###L` format
   - Stay within valid level constraints
   - Test a small sample first to verify recognition

3. **Understand special area handling**:
   - Special areas (STAGING_*, RECEIVING_*) use pattern matching
   - They may need to be configured in the template or rely on pattern recognition
   - Pattern matching may fail and default to capacity=0

---

## 🎯 Location Format Best Practices

### Storage Locations (Recommended Patterns)
```
✅ CORRECT FORMATS:
- 050A, 051B, 052C, 053D, 054E (3-digit + level)
- 100A, 101B, 102C (sequential numbering)
- 200A, 201A, 202A (same level, different numbers)

❌ AVOID THESE FORMATS:
- 1000A, 2087B (4+ digits - will be invalid)
- 050F, 051G (if levels F,G not in template)
- 050I (letter I often skipped to avoid confusion with 1)
- 050O, 050Q (some letters may be reserved/invalid)
```

### Special Areas (Pattern-Based)
```
✅ RECOMMENDED FORMATS:
- STAGING_AREA_01, STAGING_LARGE_01 (STAGING* pattern)
- RECEIVING_DOCK_A, MAIN_RECEIVING_01 (RECEIVING* pattern)
- BULK_STAGING_AREA_05 (includes STAGING for recognition)

⚠️ CAUTION - MAY NEED TEMPLATE CONFIGURATION:
- Custom special area names
- Areas not matching standard patterns
```

---

## 🔧 Template Configuration Understanding

### Virtual Engine Behavior
The virtual engine validates locations against a configured template:
- **position_level format**: Expects `###L` format with specific levels
- **Level validation**: Only accepts levels defined in template
- **Capacity assignment**: Uses template-defined capacity or pattern matching
- **Fallback behavior**: capacity=0 for unrecognized locations (safety mechanism)

### Enhanced Mode vs Legacy Mode
- **Enhanced Mode** (current default): Different alert strategies for storage vs special areas
  - Storage locations: Individual pallet alerts
  - Special areas: Consolidated location alerts
- **Legacy Mode**: All violations get individual pallet alerts

---

## 📊 Expected Results Calculation

### Storage Locations (Enhanced Mode)
- **Capacity**: Always 1 for storage locations (`###L` pattern)
- **Alert Strategy**: Individual pallet alerts
- **Calculation**: If location has N pallets > 1, expect N anomalies

### Special Areas (Enhanced Mode) 
- **Capacity**: Pattern-based (STAGING=5, RECEIVING=10) or configured
- **Alert Strategy**: Single consolidated alert per location
- **Calculation**: If location exceeds capacity, expect 1 anomaly (not N)

---

## 🚨 Red Flags to Watch For

### During Test Execution
If you see these in logs, investigate immediately:
- `capacity 0, using percentage=999` - Location not recognized
- `Level 'X' not valid (available: A, B, C, D, E)` - Invalid level used
- `Location doesn't match position_level format pattern` - Format issue
- Much higher anomaly count than expected - Likely capacity=0 issues

### Invalid Location Alerts
- Should be ZERO for properly formatted locations
- If present, indicates format compatibility problems
- Each invalid location will also likely trigger overcapacity due to capacity=0

---

## 🎯 Recommended Testing Strategy

### Phase 1: Format Validation
1. Create small diagnostic test with known valid formats
2. Verify no invalid location alerts
3. Confirm expected capacity assignments

### Phase 2: Rule-Specific Testing  
1. Use validated location formats from Phase 1
2. Focus on rule behavior without format complications
3. Calculate expected results based on enhanced vs legacy mode

### Phase 3: Scale Testing
1. Expand to larger volumes using proven formats
2. Test performance and accuracy under load

---

## 💡 Pro Tips for Future Testing

### Location Generation Strategy
```python
# SAFE: Generate locations within known valid levels
valid_levels = ['A', 'B', 'C', 'D', 'E']  # Always verify this list with user first
location = f'{base_number:03d}{valid_levels[index % len(valid_levels)]}'
```

### Special Area Naming
```python
# RECOMMENDED: Use clear pattern-based names
staging_areas = [
    'STAGING_AREA_01', 'STAGING_LARGE_01', 'BULK_STAGING_AREA_01'
]
receiving_areas = [
    'RECEIVING_DOCK_A', 'MAIN_RECEIVING_01', 'RECEIVING_AREA_01'  
]
```

### Template Compatibility Check
Always ask the user:
1. "What location format does your warehouse template expect?"
2. "What levels are valid in your current configuration?"
3. "Should we test with small diagnostic file first?"

---

## 📈 Success Metrics

### Perfect Test File Characteristics:
- ✅ Zero invalid location alerts
- ✅ All storage locations get capacity=1
- ✅ Special areas get expected capacity (5 for staging, 10 for receiving)
- ✅ Anomaly count matches mathematical expectations
- ✅ Performance under 100ms for 500+ pallets

### Validation Questions:
- Are we getting the expected number of anomalies?
- Are all locations being recognized properly?
- Is the capacity assignment logic working as expected?
- Are we testing the rule behavior or fighting format issues?

---

## 🎯 Remember: Rule Testing vs Format Debugging

The goal is to test **rule behavior**, not debug **format compatibility**.
Always ensure format compatibility FIRST, then focus on rule accuracy.

**Future Claude: Save yourself hours of debugging by validating location format compatibility before creating large test files!**

---

## 📝 Session Summary Reference

From our overcapacity rule testing session, we learned:
- Virtual engine has strict 3-digit + level format requirements
- Invalid levels cause capacity=0 assignments and false overcapacity alerts
- Template configuration directly impacts location recognition
- Enhanced mode uses different alert strategies for storage vs special areas
- Small diagnostic tests are invaluable for understanding system behavior

**Use this knowledge to create better tests from the start! 🚀**