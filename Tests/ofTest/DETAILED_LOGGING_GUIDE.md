# Detailed Logging Guide - Rules 1 & 5

**Created**: 2025-10-22
**Purpose**: Guide to interpreting the enhanced debug logs for Rule 1 (Stagnant Pallets) and Rule 5 (AISLE Stuck)

---

## 📊 What Was Added

Comprehensive logging has been added to both evaluators to provide complete visibility into:
1. **Entry conditions** - What's being evaluated and with what criteria
2. **Filtering results** - How many pallets match location patterns
3. **Individual detections** - Each anomaly as it's detected with full context
4. **Pattern analysis** - Breakdown of detected pallets by ID pattern (injected vs cross-contamination)
5. **Summary statistics** - Complete evaluation metrics

---

## 🔍 Rule 1: Stagnant Pallets Debug Logs

### Log Format

```
[STAGNANT_DEBUG] ==================== STAGNANT PALLETS EVALUATION ====================
[STAGNANT_DEBUG] Total pallets to evaluate: 1000
[STAGNANT_DEBUG] Time threshold: 10.0h
[STAGNANT_DEBUG] Location criteria: location_types=['RECEIVING'], patterns=None, excluded=None
[STAGNANT_PALLETS] Converting location_types to patterns: ['RECEIVING']
[STAGNANT_DEBUG] Pallets matching location criteria: 45
[STAGNANT_DEBUG] Location distribution (top 10):
[STAGNANT_DEBUG]   RECV-02: 29 pallets
[STAGNANT_DEBUG]   RECV-01: 16 pallets
[STAGNANT_DEBUG] -------------------- EVALUATING PALLETS --------------------
[STAGNANT_DEBUG] ✅ ANOMALY #1: Pallet 'STAGNANT-001' in 'RECV-02' (age: 15.2h > 10.0h)
[STAGNANT_DEBUG] ✅ ANOMALY #2: Pallet 'STAGNANT-002' in 'RECV-02' (age: 18.7h > 10.0h)
[STAGNANT_DEBUG] ✅ ANOMALY #3: Pallet 'OVERCAP-03-01' in 'RECV-02' (age: 41.9h > 10.0h)
...
[STAGNANT_DEBUG] ==================== EVALUATION SUMMARY ====================
[STAGNANT_DEBUG] Total pallets evaluated: 45
[STAGNANT_DEBUG] Skipped (no creation_date): 0
[STAGNANT_DEBUG] Below threshold: 12
[STAGNANT_DEBUG] Anomalies detected: 33
[STAGNANT_DEBUG] -------------------- PATTERN BREAKDOWN --------------------
[STAGNANT_DEBUG] Pallet ID pattern analysis:
[STAGNANT_DEBUG]   STAGNANT-: 5 pallets (15.2%) ✅ INJECTED
[STAGNANT_DEBUG]   OVERCAP-: 20 pallets (60.6%) ⚠️ CROSS-CONTAMINATION
[STAGNANT_DEBUG]   LOT.*-STRAGGLER: 2 pallets (6.1%) ⚠️ CROSS-CONTAMINATION
[STAGNANT_DEBUG]   PLT-: 6 pallets (18.2%) ⚠️ CROSS-CONTAMINATION
[STAGNANT_DEBUG] Location breakdown:
[STAGNANT_DEBUG]   RECV-02: 28 anomalies
[STAGNANT_DEBUG]   RECV-01: 5 anomalies
[STAGNANT_DEBUG] ================================================================
```

### Key Metrics to Watch

1. **"Pallets matching location criteria"**: How many pallets are in RECEIVING locations
2. **"Location distribution"**: Which RECEIVING locations have the most pallets
3. **Individual anomaly lines**: Each detected pallet with its ID, location, and age
4. **Pattern breakdown**: Shows exactly how many STAGNANT-XXX (injected) vs others (cross-contamination)
5. **Location breakdown**: Where the anomalies are concentrated

---

## 🔍 Rule 5: AISLE Stuck Debug Logs

### Log Format

```
[AISLE_STUCK_DEBUG] ==================== LOCATION-SPECIFIC STAGNANT EVALUATION ====================
[AISLE_STUCK_DEBUG] Total pallets to evaluate: 1000
[AISLE_STUCK_DEBUG] Time threshold: 4.0h
[AISLE_STUCK_DEBUG] Rule conditions: {'location_pattern': 'AISLE*', 'time_threshold_hours': 4}
[AISLE_STUCK_DEBUG] Location patterns to match: ['^AISLE-\\d+$']
[AISLE_STUCK_DEBUG] Pallets matching location patterns: 15
[AISLE_STUCK_DEBUG] Location distribution:
[AISLE_STUCK_DEBUG]   AISLE-06: 3 pallets
[AISLE_STUCK_DEBUG]   AISLE-03: 2 pallets
[AISLE_STUCK_DEBUG]   AISLE-01: 2 pallets
...
[AISLE_STUCK_DEBUG] -------------------- EVALUATING PALLETS --------------------
[AISLE_STUCK_DEBUG] ✅ ANOMALY #1: Pallet 'AISLE-STUCK-001' in 'AISLE-06' (age: 7.2h > 4.0h)
[AISLE_STUCK_DEBUG] ✅ ANOMALY #2: Pallet 'AISLE-STUCK-002' in 'AISLE-03' (age: 8.5h > 4.0h)
[AISLE_STUCK_DEBUG] ✅ ANOMALY #3: Pallet 'OVERCAP-04-05' in 'AISLE-01' (age: 41.9h > 4.0h)
...
[AISLE_STUCK_DEBUG] ==================== EVALUATION SUMMARY ====================
[AISLE_STUCK_DEBUG] Total pallets evaluated: 15
[AISLE_STUCK_DEBUG] Skipped (no creation_date): 0
[AISLE_STUCK_DEBUG] Below threshold: 3
[AISLE_STUCK_DEBUG] Anomalies detected: 12
[AISLE_STUCK_DEBUG] -------------------- PATTERN BREAKDOWN --------------------
[AISLE_STUCK_DEBUG] Pallet ID pattern analysis:
[AISLE_STUCK_DEBUG]   AISLE-STUCK-: 5 pallets (41.7%) ✅ INJECTED
[AISLE_STUCK_DEBUG]   OVERCAP-: 7 pallets (58.3%) ⚠️ CROSS-CONTAMINATION
[AISLE_STUCK_DEBUG] Location breakdown:
[AISLE_STUCK_DEBUG]   AISLE-06: 4 anomalies
[AISLE_STUCK_DEBUG]   AISLE-03: 3 anomalies
[AISLE_STUCK_DEBUG]   AISLE-01: 5 anomalies
[AISLE_STUCK_DEBUG] ================================================================
```

### Key Metrics to Watch

1. **"Location patterns to match"**: Shows the regex pattern used (e.g., `^AISLE-\d+$`)
2. **"Pallets matching location patterns"**: How many pallets are in AISLE locations
3. **"Location distribution"**: Which AISLE locations have pallets
4. **Pattern breakdown**: Shows AISLE-STUCK-XXX (injected) vs others (cross-contamination)

---

## 📈 How to Interpret the Results

### ✅ PASS Criteria

**For Rule 1 (Stagnant Pallets)**:
- Pattern breakdown should show **5 STAGNANT-XXX pallets** (✅ INJECTED)
- Total anomalies may be > 5 due to cross-contamination (acceptable)
- All detected pallets should be in RECEIVING locations (RECV-01, RECV-02)
- All detected pallets should have age > 10h

**For Rule 5 (AISLE Stuck)**:
- Pattern breakdown should show **5 AISLE-STUCK-XXX pallets** (✅ INJECTED)
- Total anomalies may be > 5 due to cross-contamination (acceptable)
- All detected pallets should be in AISLE locations (AISLE-01 through AISLE-10)
- All detected pallets should have age > 4h

### ⚠️ Cross-Contamination Analysis

**Cross-contamination is EXPECTED and CORRECT**. It occurs when:

1. **OVERCAP-XX-XX pallets in RECV-02** → Trigger Rule 1 if age > 10h
   - These are overcapacity test anomalies that also happen to be stagnant
   - **Verdict**: ✅ Both rules are working correctly

2. **LOT-STRAGGLER pallets in RECV** → Trigger Rule 1 if age > 10h
   - These are incomplete lot test anomalies that also happen to be stagnant
   - **Verdict**: ✅ Both rules are working correctly

3. **OVERCAP-XX-XX pallets in AISLE** → Trigger Rule 5 if age > 4h
   - These are overcapacity test anomalies that also happen to be stuck in AISLE
   - **Verdict**: ✅ Both rules are working correctly

### ❌ FAIL Criteria

**Detection Bug Signs**:
- Pallets detected with age < threshold (e.g., 8h pallet detected when threshold is 10h)
- Pallets detected in wrong location types (e.g., storage locations in Rule 1)
- Pattern breakdown shows 0 injected patterns (STAGNANT-XXX or AISLE-STUCK-XXX)

**Generator Bug Signs**:
- Pattern breakdown shows fewer than 5 injected patterns
- Location distribution shows unexpected locations

---

## 🎯 Expected Pattern Counts (1000-pallet test)

Based on test generator design:

### Rule 1 Expected Breakdown:
```
STAGNANT-: 5 pallets (✅ INJECTED)
OVERCAP-: ~20 pallets (⚠️ CROSS-CONTAMINATION from RECV-02 overcapacity)
LOT.*-STRAGGLER: ~2 pallets (⚠️ CROSS-CONTAMINATION from incomplete lots)
PLT-: ~6 pallets (⚠️ CROSS-CONTAMINATION from other anomalies)
TOTAL: ~33 pallets
```

### Rule 5 Expected Breakdown:
```
AISLE-STUCK-: 5 pallets (✅ INJECTED)
OVERCAP-: ~7 pallets (⚠️ CROSS-CONTAMINATION from AISLE overcapacity)
TOTAL: ~12 pallets
```

---

## 🔧 Using the Logs for Debugging

### Scenario 1: "Too many anomalies detected"

**Step 1**: Check pattern breakdown
```
[STAGNANT_DEBUG]   STAGNANT-: 5 pallets (15.2%) ✅ INJECTED
```
✅ If you see exactly 5 STAGNANT- pallets → Detection engine is correct

**Step 2**: Check cross-contamination sources
```
[STAGNANT_DEBUG]   OVERCAP-: 20 pallets (60.6%) ⚠️ CROSS-CONTAMINATION
```
✅ These are legitimate detections (overcapacity pallets in RECV-02 are also stagnant)

**Verdict**: Accept the results. The "extra" detections are correct.

---

### Scenario 2: "Too few anomalies detected"

**Step 1**: Check pattern breakdown
```
[STAGNANT_DEBUG]   STAGNANT-: 3 pallets (100%) ✅ INJECTED
```
❌ Only 3 STAGNANT- pallets detected (expected 5) → Generator or detection issue

**Step 2**: Check total pallets matching criteria
```
[STAGNANT_DEBUG] Pallets matching location criteria: 10
```
❌ If this is < 5, the generator didn't create enough stagnant pallets

**Verdict**: Investigate generator logic or detection filtering.

---

### Scenario 3: "Wrong locations detected"

**Step 1**: Check location breakdown
```
[STAGNANT_DEBUG] Location breakdown:
[STAGNANT_DEBUG]   123A: 15 anomalies
[STAGNANT_DEBUG]   456B: 10 anomalies
```
❌ Storage locations (123A, 456B) should NOT appear in Rule 1 (only RECEIVING)

**Verdict**: Detection bug - location filtering is broken.

---

## 📝 Quick Validation Checklist

After running analysis with the new logs, verify:

### Rule 1 (Stagnant Pallets):
- [ ] Pattern breakdown shows exactly 5 STAGNANT-XXX pallets
- [ ] All detected pallets are in RECEIVING locations (RECV-XX)
- [ ] All detected pallets have age > 10h
- [ ] Cross-contamination patterns (OVERCAP-, LOT-STRAGGLER) are explained

### Rule 5 (AISLE Stuck):
- [ ] Pattern breakdown shows exactly 5 AISLE-STUCK-XXX pallets
- [ ] All detected pallets are in AISLE locations (AISLE-XX)
- [ ] All detected pallets have age > 4h
- [ ] Cross-contamination patterns (OVERCAP-) are explained

---

## 🚀 Next Steps

1. **Commit the code changes** to rule_engine.py
2. **Re-upload the test file** (test_1000p_5a.xlsx)
3. **Run the analysis** and capture the full console output
4. **Review the logs** using this guide
5. **Make a determination**:
   - ✅ PASS if 5 injected pallets are detected per rule
   - ⚠️ CONDITIONAL PASS if cross-contamination is high but explainable
   - ❌ FAIL if injected pallets are missing or wrong locations detected

---

**Document Version**: 1.0
**Created**: 2025-10-22
**Status**: Ready for Testing
