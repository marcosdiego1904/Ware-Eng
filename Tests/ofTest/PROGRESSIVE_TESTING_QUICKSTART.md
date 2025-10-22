# Progressive Testing - Quick Start Guide

**Created**: 2025-10-21
**Purpose**: One-at-a-time progressive testing to validate WareWise rule engine accuracy and performance

---

## 🚀 Quick Start

### Generate Your First Test

```bash
cd Tests
python generate_single_test.py 100 5
```

**Output**: `test_100p_5a.xlsx` with detailed generation report

---

## 📋 Your Testing Workflow

### Step 1: Generate Test File

```bash
python generate_single_test.py <pallets> <anomalies_per_rule>
```

**Examples**:
- `python generate_single_test.py 100 5` - Baseline (100 pallets, 5 anomalies/rule)
- `python generate_single_test.py 500 5` - Medium scale
- `python generate_single_test.py 1000 5` - Large scale

### Step 2: Review Generation Report

The generator outputs a detailed report showing:
- ✅ Exact pallet IDs for each anomaly type
- ✅ Expected anomaly counts by rule
- ✅ Locations used
- ✅ Validation checklist

**Save this report** - you'll need it to compare with WareWise results!

### Step 3: Upload to WareWise

1. Open WareWise dashboard
2. Click "New Analysis"
3. Upload the generated `.xlsx` file
4. Run analysis

### Step 4: Validate Results

Compare WareWise detected anomalies with generation report:

| Rule | Expected | Actual | Match? | Notes |
|------|----------|--------|--------|-------|
| Rule 1 (Stagnant) | 5 | ___ | ☐ | |
| Rule 2 (Incomplete Lots) | 5 | ___ | ☐ | |
| Rule 3 (Overcapacity) | 5 | ___ | ☐ | |
| Rule 4 (Invalid Locations) | 5 | ___ | ☐ | |
| Rule 5 (AISLE Stuck) | 5 | ___ | ☐ | |
| Rule 7 (Scanner Errors) | 5 | ___ | ☐ | |
| **TOTAL** | **30** | ___ | ☐ | |

### Step 5: Decide Next Action

**If results match (30 anomalies detected)**:
```bash
# ✅ SUCCESS! Generate next test
python generate_single_test.py 500 5
```

**If results don't match**:
```
❌ STOP! Investigate discrepancy before proceeding
1. Compare detected pallet IDs with generation report
2. Check warehouse template includes all location formats
3. Verify rule thresholds (10h, 4h, 80%)
4. Review location type detection
5. Fix issue and retry before moving to next test
```

---

## 📊 Recommended Test Sequence (Phase 1-2)

### Test 1: Baseline Validation ✅ GENERATED
```bash
python generate_single_test.py 100 5
```
- **File**: `test_100p_5a.xlsx`
- **Expected**: 30 anomalies (5 × 6 rules)
- **Purpose**: Verify all rules work correctly

### Test 2: Medium Scale
```bash
python generate_single_test.py 500 5
```
- **File**: `test_500p_5a.xlsx`
- **Expected**: 30 anomalies (same as Test 1)
- **Purpose**: Verify anomaly detection scales with dataset

### Test 3: Large Scale
```bash
python generate_single_test.py 1000 5
```
- **File**: `test_1000p_5a.xlsx`
- **Expected**: 30 anomalies
- **Purpose**: Test performance at 1k pallets

### Test 4: Enterprise Scale ⚠️ EMERGENT OVERCAPACITY
```bash
python generate_single_test.py 2000 5
```
- **File**: `test_2000p_5a.xlsx`
- **Expected**: 30 injected + ~360 emergent overcapacity = ~390 total
- **Purpose**: Validate emergent overcapacity detection

### Test 5: Stress Test ⚠️ EMERGENT OVERCAPACITY
```bash
python generate_single_test.py 5000 5
```
- **File**: `test_5000p_5a.xlsx`
- **Expected**: 30 injected + ~530 emergent overcapacity = ~560 total
- **Purpose**: Maximum scale validation

---

## ⚠️ Important Notes

### Emergent Overcapacity (Tests 4-5)

For files with **2000+ pallets**, overcapacity will show **MORE than 5 injected anomalies**.

**This is CORRECT BEHAVIOR, not a bug!**

**Why?**
- At 88% warehouse utilization, statistical distribution (Poisson λ=1.76) causes ~18-19% of locations to naturally exceed capacity
- Session 005 testing confirmed: 5,000 pallets → 531 emergent overcapacity violations

**Expected Counts**:
- 2,000 pallets: ~360 emergent + 5 injected = ~365 total overcapacity
- 5,000 pallets: ~530 emergent + 5 injected = ~535 total overcapacity

### Total Pallet Count May Vary

The generator creates:
- **Requested pallets** (e.g., 100)
- **Plus anomaly pallets** (e.g., incomplete lot stored pallets, scanner duplicates)

**Example**: 100-pallet request might generate 104-106 total pallets.

**This is normal** - focus on anomaly counts, not total pallet count.

---

## 📝 Tracking Progress

Use **`TEST_VALIDATION_TRACKER.md`** to document:
- ✅ Test results (expected vs actual)
- ✅ Upload dates and analysis times
- ✅ Discrepancies and investigation notes
- ✅ Overall progress through test sequence

---

## 🔍 Troubleshooting

### "More than 30 anomalies detected"

**Possible Causes**:
1. **Emergent overcapacity** (expected for 2000p+)
2. **Cross-contamination** (pallet triggers multiple rules - count unique pallets)
3. **Overcapacity multiplication** (if generator used storage locations - check report)

**Action**: Compare detected pallet IDs with generation report

### "Fewer than 30 anomalies detected"

**Possible Causes**:
1. **Rule inactive** (check WareWise settings)
2. **Threshold changed** (verify 10h, 4h, 80%)
3. **Location type detection issue** (check pattern matching)

**Action**: Review rule configurations and thresholds

### "Generation fails"

**Possible Causes**:
1. **Not in Tests folder** (run from `Tests/` directory)
2. **Missing dependencies** (`pip install pandas openpyxl`)
3. **Missing flexible_test_generator.py** (should be in `Tests/TestDone/`)

**Action**: Check error message and verify setup

---

## 📈 Performance Benchmarks

**Expected Analysis Times** (from Session 005):

| Pallets | Expected Time | Per-Pallet | Status |
|---------|---------------|------------|--------|
| 100 | <1 second | 1.30ms | ✅ Baseline |
| 500 | <2 seconds | 1.62ms | ✅ Good |
| 1,000 | ~1.5 seconds | 1.50ms | ✅ Good |
| 2,000 | <5 seconds | 1.39ms | ✅ Improving |
| 5,000 | <10 seconds | 1.27ms | ✅ Best |

**Trend**: Performance IMPROVES at scale (sub-linear) ✅

---

## 🎯 Success Criteria

**A test PASSES if**:
- ✅ Total anomaly count matches expected (±2 tolerance)
- ✅ Each rule shows expected count (±1 tolerance)
- ✅ Analysis completes in expected time
- ✅ No system errors or crashes

**Proceed to next test only after current test PASSES**

---

## 📞 Files Created

- **`generate_single_test.py`** - Single test file generator
- **`test_100p_5a.xlsx`** - First test file (ready to upload!)
- **`TEST_VALIDATION_TRACKER.md`** - Results tracking template
- **`PROGRESSIVE_TESTING_QUICKSTART.md`** - This guide

---

## 🚀 Next Steps

### Right Now:
1. ✅ **Test 1 generated**: `test_100p_5a.xlsx`
2. 📤 **Upload to WareWise**
3. 🔍 **Validate results** (expect 30 anomalies)
4. ✅ **If PASS**: Generate Test 2 (`python generate_single_test.py 500 5`)
5. ❌ **If FAIL**: Investigate using generation report

### After All 5 Tests Pass:
- **Phase 3: Density Testing** (optional)
  - `python generate_single_test.py 1000 10`
  - `python generate_single_test.py 1000 20`

- **Phase 4: Combined Stress** (optional)
  - `python generate_single_test.py 5000 20`
  - `python generate_single_test.py 10000 10`

---

**Ready to start?** Upload `test_100p_5a.xlsx` to WareWise now! 🎉

---

**Document Version**: 1.0
**Created**: 2025-10-21
**Status**: Ready for Testing
