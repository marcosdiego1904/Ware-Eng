# Test Session 001 - Expected Results

**Test File**: `warewise_test_session_001.xlsx`
**Generated**: 2025-01-09
**Total Pallets**: 100
**Generator Version**: 2.0 (No location_type column)

---

## 📊 Expected Anomaly Count

### Total Expected: **~30 anomalies**

**Note**: Actual count may be 30-34 due to cross-contamination (some pallets trigger multiple rules).

---

## 🎯 Rule-by-Rule Expectations

### ✅ Rule 1: Stagnant Pallets (RECEIVING >10h)
**Expected**: **5 anomalies**

**What to look for**:
- Pallets in RECV-01 or RECV-02 locations
- Age: >10 hours (12-20 hours old)
- Pallet IDs: `STAGNANT-001` through `STAGNANT-005`

**Example anomaly**:
```
Pallet ID: STAGNANT-001
Location: RECV-01
Age: 15 hours
Rule: Stagnant Pallets
```

---

### ✅ Rule 2: Incomplete Lots (Stragglers)
**Expected**: **5 anomalies**

**What to look for**:
- 2-3 different lots (LOT5000, LOT5001, LOT5002)
- Each lot has 10 total pallets:
  - 9 pallets in STORAGE locations (###L format)
  - 1-2 stragglers stuck in RECV-01 or RECV-02
- Stragglers are >80% of lot (90% to be precise)

**Example anomaly**:
```
Pallet ID: LOT5000-STRAGGLER-01
Location: RECV-02
Receipt: RCV-LOT-5000
Rule: Incomplete Lots
Issue: 2 pallets left behind (90% of lot already in storage)
```

**Expected stragglers**:
- LOT5000: 2 stragglers
- LOT5001: 2 stragglers
- LOT5002: 1 straggler
- **Total: 5 stragglers**

---

### ✅ Rule 3: Overcapacity (Locations Exceeding Capacity)
**Expected**: **4-5 anomalies**

**What to look for**:
- Special area locations with MORE pallets than capacity allows
- Locations used:
  - RECV-01 or RECV-02 (capacity: 10, injected: 11-12 pallets)
  - W-01 or W-02 (capacity: 1, injected: 2 pallets)
  - Possibly AISLE-XX (capacity: 5, injected: 6-7 pallets)

**Example anomaly**:
```
Location: W-01
Capacity: 1 pallet
Actual Count: 2 pallets
Pallets: OVERCAP-01-01, OVERCAP-01-02
Rule: Overcapacity
```

**Note**: System reports **1 representative anomaly per overcapacity location**, not all pallets.

**Expected count**: **4-5 locations flagged** (2 RECV + 2 W + possibly 1 AISLE)

---

### ✅ Rule 4: Invalid Locations
**Expected**: **4-5 anomalies**

**What to look for**:
- Pallets in non-existent location codes:
  - `TEMP-HOLD`
  - `UNKNOWN`
  - `NO-LOCATION`
  - `XXX-999`
  - `999Z`
  - `MISSING`
  - Empty location string

**Example anomaly**:
```
Pallet ID: INVALID-003
Location: TEMP-HOLD
Rule: Invalid Locations
Issue: Location code not found in warehouse template
```

**Expected count**: **4-5 invalid locations**

**Why not 5/5?** One might be filtered as empty location (data integrity instead of invalid location).

---

### ✅ Rule 5: AISLE Stuck Pallets (>4h)
**Expected**: **5-12 anomalies** ⚠️ (Cross-contamination expected)

**What to look for**:
- Pallets in AISLE-01 through AISLE-10 locations
- Age: >4 hours (5-10 hours old)
- Pallet IDs: `AISLE-STUCK-001` through `AISLE-STUCK-005`

**Example anomaly**:
```
Pallet ID: AISLE-STUCK-002
Location: AISLE-05
Age: 7 hours
Rule: AISLE Stuck Pallets
```

**⚠️ Cross-Contamination Warning**:
If overcapacity pallets are placed in AISLE locations AND aged >4h, they will trigger BOTH:
- Rule 3: Overcapacity
- Rule 5: AISLE Stuck

**Expected**: **5 intentional + up to 7 from cross-contamination = 5-12 total**

---

### ✅ Rule 7: Scanner Errors (Data Integrity)
**Expected**: **4-5 anomalies**

**What to look for**:
Two types of errors injected:

**Type 1: Duplicate Pallet IDs** (2-3 anomalies)
- Same pallet ID appears in 2+ different locations
- Pallet IDs: `DUPLICATE-001`, `DUPLICATE-002`, `DUPLICATE-003`
- Each duplicate appears twice in the file

**Example**:
```
Pallet ID: DUPLICATE-001
Location 1: 245A
Location 2: 678C
Rule: Scanner Errors
Issue: Duplicate pallet ID in multiple locations
```

**Type 2: Data Integrity Issues** (2-3 anomalies)
- Empty location field (location = "")
- Future creation date (impossible timestamp)
- Pallet IDs: `DATA-ERROR-001`, `DATA-ERROR-002`, `DATA-ERROR-003`

**Example**:
```
Pallet ID: DATA-ERROR-001
Location: (empty)
Rule: Scanner Errors
Issue: Missing location data
```

**Expected count**: **4-5 total scanner errors**

---

### ❌ Rule 8: Location Mapping Errors
**Expected**: **0 anomalies** (DEPRECATED)

**Why zero?**
- Rule 8 is deprecated (inactive in database)
- Test generator v2.0 doesn't inject location_type column
- System auto-detects location types from location codes

**If you see any Rule 8 anomalies**: Something is wrong - the rule should be inactive.

---

## 📋 Summary Checklist

When you upload `warewise_test_session_001.xlsx`, verify:

- [ ] **Total Anomalies**: 30-34 (acceptable range)
- [ ] **Rule 1 (Stagnant)**: 5 anomalies ✓
- [ ] **Rule 2 (Incomplete Lots)**: 5 anomalies ✓
- [ ] **Rule 3 (Overcapacity)**: 4-5 anomalies ✓
- [ ] **Rule 4 (Invalid)**: 4-5 anomalies ✓
- [ ] **Rule 5 (AISLE Stuck)**: 5-12 anomalies ✓ (cross-contamination OK)
- [ ] **Rule 7 (Scanner Errors)**: 4-5 anomalies ✓
- [ ] **Rule 8 (Location Mapping)**: 0 anomalies ✓
- [ ] **No False Positives**: All flagged pallets are intentional anomalies

---

## 🎓 Understanding Cross-Contamination

**What is it?**
Some pallets violate multiple rules simultaneously.

**Example**:
```
Pallet: OVERCAP-03-05
Location: AISLE-08
Capacity: 5 pallets
Actual: 7 pallets in AISLE-08
Age: 8 hours

This pallet triggers:
✓ Rule 3: Overcapacity (location has >5 pallets)
✓ Rule 5: AISLE Stuck (pallet in AISLE >4 hours)
```

**Is this a problem?** NO! ✅
- This is **correct multi-dimensional detection**
- Real warehouses have pallets with multiple issues
- WareWise should detect ALL applicable problems

**Result**: Total anomaly count (30-34) may be higher than injected count (30) due to cross-detection.

---

## 🔍 Detailed Anomaly Breakdown

### Core Operations (4 rules = 20-27 anomalies)

| Rule | Expected | Acceptable Range | Notes |
|------|----------|------------------|-------|
| Stagnant Pallets | 5 | 5 | Exact count expected |
| Incomplete Lots | 5 | 5 | Fixed: 90% threshold now works |
| Overcapacity | 5 | 4-5 | Special areas only (1 per location) |
| AISLE Stuck | 5 | 5-12 | Cross-contamination with overcapacity |

### Quality & Compliance (2 rules = 8-10 anomalies)

| Rule | Expected | Acceptable Range | Notes |
|------|----------|------------------|-------|
| Invalid Locations | 5 | 4-5 | One may be empty location (data integrity) |
| Scanner Errors | 5 | 4-5 | Duplicates + data issues |

### Deprecated (0 rules = 0 anomalies)

| Rule | Expected | Acceptable Range | Notes |
|------|----------|------------------|-------|
| Location Mapping | 0 | 0 | Deprecated - should be inactive |

---

## 📊 File Contents Verification

### Expected Columns (5 total):
```
1. pallet_id
2. location
3. creation_date
4. receipt_number
5. product
```

**Note**: NO `location_type` column! System auto-detects from location codes.

### Sample Data Preview:
```csv
pallet_id,location,creation_date,receipt_number,product
STAGNANT-001,RECV-01,2025-01-08 22:40:03,RCV-12345,Component Box A
LOT5000-STRAGGLER-01,RECV-02,2025-01-09 14:40:03,RCV-LOT-5000,Widget Assembly Kit
OVERCAP-01-01,W-01,2025-01-09 16:40:03,RCV-67890,Packaging Supplies
INVALID-002,TEMP-HOLD,2025-01-09 15:40:03,RCV-23456,Hardware Kit
AISLE-STUCK-003,AISLE-07,2025-01-09 10:40:03,RCV-34567,Finished Product SKU-001
DUPLICATE-001,245A,2025-01-09 13:40:03,RCV-45678,Raw Material Bundle
```

---

## ✅ Success Criteria

**Test PASSES if**:
1. Total anomalies: 28-35 (acceptable with cross-contamination)
2. Each rule detects its injected anomalies (±1 variance OK)
3. Rule 8: 0 anomalies (deprecated)
4. No false positives on clean pallets
5. All anomaly descriptions are accurate

**Test FAILS if**:
1. Total anomalies: <25 or >40
2. Any rule completely fails (0 detections when 5 injected)
3. Rule 8 shows any anomalies (should be inactive)
4. Clean pallets flagged as anomalies
5. System crashes or errors during analysis

---

## 🎯 Expected Analysis Output

When WareWise finishes analyzing the file, you should see:

```
=== ANALYSIS COMPLETE ===

Total Pallets Analyzed: 100
Total Anomalies Detected: 32

By Category:
  Core Operations: 22 anomalies
  Quality & Compliance: 10 anomalies

By Rule:
  ✓ Stagnant Pallets: 5
  ✓ Incomplete Lots: 5
  ✓ Overcapacity: 4
  ✓ Invalid Locations: 4
  ✓ AISLE Stuck: 10 (includes cross-contamination)
  ✓ Scanner Errors: 4
  ✓ Location Mapping: 0 (deprecated)

Clean Pallets: 68
Pallets with Issues: 32 (some pallets have multiple issues)
```

---

## 📝 Test Instructions

### Step 1: Upload File
1. Go to WareWise dashboard
2. Navigate to "New Analysis"
3. Upload `warewise_test_session_001.xlsx`
4. Wait for column mapping (should auto-detect 5 columns)

### Step 2: Verify Analysis
1. Check total anomaly count: **30-34 expected**
2. Review each rule's detections
3. Verify no Rule 8 anomalies (deprecated)

### Step 3: Spot Check Anomalies
Click on a few anomalies to verify details:
- STAGNANT-001 should show >10h in RECV
- LOT5000-STRAGGLER-01 should show incomplete lot
- DUPLICATE-001 should appear twice
- W-01 should show overcapacity (2 pallets, capacity 1)

### Step 4: Report Results
Compare actual vs expected:
```
Rule 1: Expected 5, Got ___
Rule 2: Expected 5, Got ___
Rule 3: Expected 4-5, Got ___
Rule 4: Expected 4-5, Got ___
Rule 5: Expected 5-12, Got ___
Rule 7: Expected 4-5, Got ___
Rule 8: Expected 0, Got ___
Total: Expected 30-34, Got ___
```

---

**Good luck with your test!** 🎉

The file is ready to upload at:
`Tests/warewise_test_session_001.xlsx`
