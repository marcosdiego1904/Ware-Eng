# Test Session 002 - Scalability Test (500 Pallets)

**Test File**: `warewise_test_session_002.xlsx`
**Generated**: 2025-01-09
**Total Pallets**: 500
**Generator Version**: 2.0 (No location_type column)
**Test Type**: **Scalability Test** - Same anomalies, 5x more data

---

## 🎯 Test Objectives

### Primary Goal: **Scalability Validation**
Verify that WareWise rule engine maintains **precision** and **performance** when dataset size increases 5x (100 → 500 pallets) while anomaly count stays constant.

### Success Criteria:
- ✅ Same anomaly detection rate as Session 001 (~30 anomalies)
- ✅ All rules maintain precision (find their 5 injected anomalies)
- ✅ Performance: Analysis completes in <1 second
- ✅ No false positives on 470 clean pallets
- ✅ Rule 8 still shows 0 (deprecated)

---

## 📊 Expected Anomaly Count

### Total Expected: **~30-34 anomalies**

**Comparison to Session 001:**
```
Session 001: 100 pallets, 30 anomalies = 30% anomaly rate
Session 002: 500 pallets, 30 anomalies = 6% anomaly rate ✓ More realistic!
```

**Note**: Actual count may be 30-34 due to cross-contamination (same as Session 001).

---

## 🎯 Rule-by-Rule Expectations

### ✅ Rule 1: Stagnant Pallets (RECEIVING >10h)
**Expected**: **5 anomalies**

**What to look for**:
- Pallets in RECV-01 or RECV-02 locations
- Age: >10 hours (12-20 hours old)
- Pallet IDs: `STAGNANT-001` through `STAGNANT-005`

**Needle in haystack**: 5 stagnant pallets in ~500 total = 1% detection challenge

---

### ✅ Rule 2: Incomplete Lots (Stragglers)
**Expected**: **5 anomalies**

**What to look for**:
- 2-3 different lots (LOT5000, LOT5001, LOT5002)
- Each lot: 9 pallets in STORAGE, 1-2 stragglers in RECEIVING
- Detection threshold: >80% of lot already stored

**Expected stragglers**:
- LOT5000: 2 stragglers
- LOT5001: 2 stragglers
- LOT5002: 1 straggler
- **Total: 5 stragglers**

**Test**: Validates 90% threshold fix scales to larger datasets

---

### ✅ Rule 3: Overcapacity (Locations Exceeding Capacity)
**Expected**: **4-5 anomalies**

**What to look for**:
- RECV-01 or RECV-02 (capacity: 10, injected: 11-12 pallets)
- W-01 or W-02 (capacity: 1, injected: 2 pallets)
- Possibly AISLE-XX (capacity: 5, injected: 6-7 pallets)

**Expected count**: **4-5 overcapacity locations**

**Scalability test**: With 500 pallets in 440 unique locations, overcapacity detection should be just as precise.

---

### ✅ Rule 4: Invalid Locations
**Expected**: **5 anomalies** (if AISLE template issue fixed)

**What to look for**:
- Non-existent location codes:
  - `TEMP-HOLD`
  - `UNKNOWN`
  - `NO-LOCATION`
  - `XXX-999`
  - `999Z`

**Session 001 lesson**: Don't expect AISLE-XX to be flagged if you added them to template.

**Expected count**: **5 invalid locations**

---

### ✅ Rule 5: AISLE Stuck Pallets (>4h)
**Expected**: **5-12 anomalies** (Cross-contamination expected)

**What to look for**:
- Pallets in AISLE-01 through AISLE-10 locations
- Age: >4 hours (5-10 hours old)
- Pallet IDs: `AISLE-STUCK-001` through `AISLE-STUCK-005`

**⚠️ Cross-Contamination**: Overcapacity pallets in AISLE locations aged >4h trigger both Rule 3 AND Rule 5.

**Expected**: **5 intentional + up to 7 from cross-contamination = 5-12 total**

---

### ✅ Rule 7: Scanner Errors (Data Integrity)
**Expected**: **4-5 anomalies**

**What to look for**:

**Type 1: Duplicate Pallet IDs** (2-3 anomalies)
- `DUPLICATE-001`, `DUPLICATE-002`, `DUPLICATE-003`
- Each appears in 2+ different locations

**Type 2: Data Integrity Issues** (2-3 anomalies)
- Empty location field
- Future creation date
- `DATA-ERROR-001`, `DATA-ERROR-002`, `DATA-ERROR-003`

**Expected count**: **4-5 total scanner errors**

**Scalability test**: System should find duplicates even in 500-pallet dataset.

---

### ❌ Rule 8: Location Mapping Errors
**Expected**: **0 anomalies** (DEPRECATED)

**Critical validation**: If any Rule 8 anomalies appear, deprecation failed.

---

## 📋 Comparison to Session 001

| Metric | Session 001 (100p) | Session 002 (500p) | Change |
|--------|-------------------|-------------------|--------|
| **Total Pallets** | 100 | 500 | **5x** ↑ |
| **Clean Pallets** | 70 | 470 | **6.7x** ↑ |
| **Total Anomalies** | ~32 | ~30-34 | Same |
| **Anomaly Rate** | 32% | 6% | **More realistic** ↓ |
| **Unique Locations** | 58 | 440 | **7.6x** ↑ |
| **File Size** | 8.15 KB | 20.42 KB | **2.5x** ↑ |

### Key Validation:
✅ **Anomaly count stays constant** (30-34) despite 5x more pallets
✅ **Anomaly rate drops to realistic 6%** (typical for real warehouses)
✅ **Rules find needles in bigger haystack** (precision test)

---

## 🎓 What This Test Validates

`★ Insight ─────────────────────────────────────`

**Precision at Scale**: This test validates that WareWise rules maintain accuracy when the signal-to-noise ratio drops from 30% to 6%. Real warehouse anomaly rates are typically 1-6%, so finding 30 anomalies in 500 pallets (6% rate) is far more representative of production conditions than 30 in 100 (30% rate).

**Performance Under Load**: With 5x more data, analysis time should scale linearly or better. Target: <1 second for 500 pallets. If analysis takes >2 seconds, there may be performance bottlenecks in the rule engine that need optimization.

**Location Universe Growth**: 440 unique locations vs 58 in Session 001 (7.6x increase) tests whether location validation logic (Virtual Engine) scales efficiently. This is critical because large warehouses can have 10,000+ locations.

`─────────────────────────────────────────────────`

---

## 📊 Expected Analysis Output

```
=== ANALYSIS COMPLETE ===

Total Pallets Analyzed: 500
Total Anomalies Detected: 32

By Category:
  Core Operations: 22 anomalies
  Quality & Compliance: 10 anomalies

By Rule:
  ✓ Stagnant Pallets: 5
  ✓ Incomplete Lots: 5
  ✓ Overcapacity: 4
  ✓ Invalid Locations: 5
  ✓ AISLE Stuck: 9 (includes cross-contamination)
  ✓ Scanner Errors: 4
  ✓ Location Mapping: 0 (deprecated)

Clean Pallets: 468
Pallets with Issues: 32
Analysis Time: 0.25s ← Should be <1 second
```

---

## ✅ Success Criteria Checklist

### Detection Accuracy:
- [ ] **Total Anomalies**: 28-35 (acceptable with cross-contamination)
- [ ] **Rule 1 (Stagnant)**: 5 anomalies ✓
- [ ] **Rule 2 (Incomplete Lots)**: 5 anomalies ✓
- [ ] **Rule 3 (Overcapacity)**: 4-5 anomalies ✓
- [ ] **Rule 4 (Invalid)**: 5 anomalies ✓
- [ ] **Rule 5 (AISLE Stuck)**: 5-12 anomalies ✓
- [ ] **Rule 7 (Scanner Errors)**: 4-5 anomalies ✓
- [ ] **Rule 8 (Location Mapping)**: 0 anomalies ✓

### Performance:
- [ ] **Analysis Time**: <1 second (target: 0.2-0.5s)
- [ ] **File Upload**: <5 seconds
- [ ] **UI Responsiveness**: No lag when displaying 32 anomalies

### Data Quality:
- [ ] **No False Positives**: Clean pallets not flagged
- [ ] **Precision Maintained**: Same detection rate as Session 001
- [ ] **Location Validation**: 440 unique locations processed correctly

---

## 🔍 Performance Benchmarks

| Phase | Target Time | Acceptable |
|-------|-------------|------------|
| File Upload | <3 seconds | <5 seconds |
| Column Mapping | Instant (auto-detect) | <1 second |
| Rule Analysis | <0.5 seconds | <1 second |
| UI Rendering | <1 second | <2 seconds |
| **Total** | **<4.5 seconds** | **<9 seconds** |

**Session 001 baseline**: 0.13 seconds for 100 pallets
**Expected for 500 pallets**: 0.2-0.5 seconds (linear or sub-linear scaling)

---

## 📝 Test Instructions

### Step 1: Upload File
1. Go to WareWise dashboard
2. Navigate to "New Analysis"
3. Upload `warewise_test_session_002.xlsx`
4. Verify auto-detection of 5 columns (no location_type)

### Step 2: Monitor Performance
- Start timer when you click "Analyze"
- Record total analysis time
- Note any UI lag or delays

### Step 3: Verify Results
Compare to Session 001:
```
Session 001 Results:
  Rule 1: 5 ✓
  Rule 2: 5 ✓
  Rule 3: 4 ✓
  Rule 4: 8 (AISLE template issue)
  Rule 5: 8 ✓
  Rule 7: 4 ✓
  Rule 8: 0 ✓
  Total: 34 anomalies in 0.13s

Session 002 Expected:
  Rule 1: 5 (same)
  Rule 2: 5 (same)
  Rule 3: 4-5 (same)
  Rule 4: 5 (if AISLE fixed)
  Rule 5: 5-12 (same cross-contamination)
  Rule 7: 4-5 (same)
  Rule 8: 0 (same - deprecated)
  Total: ~30-34 anomalies in <1s
```

### Step 4: Spot Check
Verify a few anomalies manually:
- STAGNANT-001: Should be in RECV with >10h age
- LOT5000-STRAGGLER-01: Should show incomplete lot
- DUPLICATE-001: Should appear twice
- Check 5-10 clean pallets: Should NOT be flagged

### Step 5: Report Results
```
Session 002 Results:
  Rule 1: ___ anomalies (expected: 5)
  Rule 2: ___ anomalies (expected: 5)
  Rule 3: ___ anomalies (expected: 4-5)
  Rule 4: ___ anomalies (expected: 5)
  Rule 5: ___ anomalies (expected: 5-12)
  Rule 7: ___ anomalies (expected: 4-5)
  Rule 8: ___ anomalies (expected: 0)
  Total: ___ anomalies (expected: 30-34)

  Analysis Time: ___ seconds (target: <1s)

  PASS / FAIL: ___
```

---

## 🎯 What We're Testing

### 1. **Scalability** (Primary)
- Can system handle 5x more pallets?
- Does performance scale linearly?
- Do rules maintain precision with more noise?

### 2. **Precision** (Secondary)
- Same anomaly count despite 5x more data
- No false positives on 470 clean pallets
- Cross-contamination still works correctly

### 3. **Realism** (Tertiary)
- 6% anomaly rate mirrors real warehouses
- 440 unique locations tests real-world complexity
- Tests if UI can display results clearly at scale

---

## 🚀 Next Steps After Session 002

### If PASS (Expected):
**Phase 3**: Increase anomaly depth
```bash
python flexible_test_generator.py --pallets 500 --anomalies 15
```
- Tests rule logic with 15 examples per rule
- Validates edge case handling
- 90 total anomalies in 500 pallets

### If Performance Issues (<1s not achieved):
**Investigate**:
- Check database query optimization
- Review Virtual Engine performance
- Consider adding indexes
- Profile rule evaluation logic

### If Detection Issues (Anomalies missed):
**Debug**:
- Review specific rule that failed
- Check threshold configurations
- Validate location template coverage
- Examine rule precedence conflicts

---

## 📊 File Contents

**Columns** (5 total):
```
1. pallet_id
2. location
3. creation_date
4. receipt_number
5. product
```

**Statistics**:
- Total rows: 500
- Unique locations: 440
- Anomaly pallets: 30
- Clean pallets: 470
- File size: 20.42 KB

**Sample Data**:
```csv
pallet_id,location,creation_date,receipt_number,product
PLT-000850,245B,2025-01-09 16:40:03,RCV-12345,Widget Assembly Kit
STAGNANT-001,RECV-01,2025-01-08 22:40:03,RCV-67890,Component Box A
LOT5000-STRAGGLER-01,RECV-02,2025-01-09 14:40:03,RCV-LOT-5000,Finished Product
OVERCAP-01-01,W-01,2025-01-09 15:40:03,RCV-23456,Packaging Supplies
AISLE-STUCK-002,AISLE-05,2025-01-09 09:40:03,RCV-34567,Hardware Kit
```

---

## ✅ Expected Outcome

**Test PASSES if**:
1. ✅ Total anomalies: 28-35 (same as Session 001)
2. ✅ Analysis time: <1 second (vs 0.13s for 100 pallets)
3. ✅ All rules detect their injected anomalies (±1 variance OK)
4. ✅ Rule 8: 0 anomalies (deprecated)
5. ✅ No false positives on 470 clean pallets
6. ✅ UI displays results smoothly

**Test FAILS if**:
1. ❌ Total anomalies: <25 or >40 (precision loss)
2. ❌ Analysis time: >2 seconds (performance issue)
3. ❌ Any rule completely fails (0 detections when 5 injected)
4. ❌ Rule 8 shows anomalies (deprecation broken)
5. ❌ Clean pallets flagged (false positives)
6. ❌ System crashes or errors

---

**Ready to test!** 🚀

Upload `warewise_test_session_002.xlsx` and compare results to Session 001 baseline.

**File Location**: `Tests/warewise_test_session_002.xlsx`
