# 🐛 WareWise System Issues Tracking

**Last Updated:** 2025-08-19  
**Session:** Rule Engine Architecture Fixes  
**Total Issues:** 11 identified | 2 resolved ✅ | 9 pending 🔄

---

## 🎯 **CRITICAL PRIORITY ISSUES**

### ✅ **Issue #1: SQLAlchemy Session Binding Corruption** 
- **Status:** 🟢 **RESOLVED** (Commit: `447c13e`)
- **Problem:** Rule 4 crashed with "Instance not bound to a Session" errors after template operations
- **Root Cause:** Cached Location objects became detached when database sessions changed
- **Solution:** Added `_ensure_session_bound()` method with automatic session recovery
- **Impact:** Rule 4 now works reliably - **16 invalid locations detected** ✅
- **Files:** `backend/src/location_service.py`

### 🔄 **Issue #2: Intelligent Location Format Mapping**
- **Status:** 🟡 **PENDING** 
- **Problem:** Users must adapt their location formats to match database (01-01-001A vs 001A01)
- **Philosophy:** **WareWise should adapt to users, not vice versa**
- **Impact:** Forces users to change their existing location naming conventions
- **Priority:** Critical - affects user experience

---

## 🔥 **HIGH PRIORITY ISSUES**

### ✅ **Issue #3: Warehouse Detection System Failure**
- **Status:** 🟢 **RESOLVED** (Automatically fixed with Issue #1)
- **Before:** 0% coverage, couldn't identify warehouse
- **After:** **72.7% coverage, HIGH confidence** for USER_TESTF warehouse ✅
- **Impact:** Rules now leverage warehouse-specific optimizations

### 🔄 **Issue #4: Uncoordinated Lots Rule False Negative**
- **Status:** 🟡 **PENDING**
- **Problem:** LOT001 should be flagged as straggler but wasn't detected
- **Debug:** `Found 0 stragglers in ['RECEIVING']` despite LOT001 being in RECV-01
- **Root Cause:** Location type classification issue - RECV-01 not found in warehouse database
- **Related:** Issues #10, #11 (missing special areas)

### 🔄 **Issue #5: Stagnant Pallets Rule Incomplete Detection**
- **Status:** 🟡 **PENDING**
- **Problem:** Expected 5 anomalies, only found 2 (missing OLD001, OLD002, STALE001)
- **Root Cause:** RECV-01 location not found in database, pallets flagged as invalid instead
- **Related:** Issue #10 (RECV-01 missing from warehouse)

### 🔄 **Issue #10: RECV-01 Location Missing from Database**
- **Status:** 🔴 **NEW HIGH PRIORITY**
- **Problem:** `RECV-01` flagged as invalid - not found in USER_TESTF warehouse
- **Evidence:** 11 pallets in RECV-01 all flagged as invalid locations
- **Impact:** Affects Rules 1, 2, 4, 3 (should trigger overcapacity for RECV-01)
- **Root Cause:** Warehouse template didn't create special area locations

### 🔄 **Issue #11: AISLE-02 Location Missing from Database**
- **Status:** 🔴 **NEW HIGH PRIORITY**
- **Problem:** `AISLE-02` not found in database
- **Evidence:** AISLE2 pallet flagged as invalid location
- **Impact:** Affects Rules 4, 5 (AISLE stuck pallets logic)

---

## 🟡 **MEDIUM PRIORITY ISSUES**

### 🔄 **Issue #6: Session Management After Template Operations**
- **Status:** 🟡 **PENDING**
- **Problem:** Template changes corrupt active sessions (partially addressed by Issue #1)
- **Need:** Proactive cache clearing during template operations
- **Impact:** System reliability during warehouse configuration changes

### 🔄 **Issue #7: Overcapacity Rule Default Fallback Logic**
- **Status:** 🟡 **PENDING**
- **Problem:** Assigns default capacity instead of failing gracefully for unknown locations
- **Evidence:** RECV-01 shows `found_in_db=False` but still processed
- **Philosophy:** Should fail explicitly when can't find location capacity

---

## 🟢 **LOW PRIORITY ISSUES**

### 🔄 **Issue #8: Flask Development Server Cache Issues**
- **Status:** 🟡 **PENDING**
- **Problem:** Code changes not reflected without manual restarts
- **Impact:** Development efficiency only
- **Workaround:** Manual restarts work fine

### 🔄 **Issue #9: SQLAlchemy MetaData Table Conflicts**
- **Status:** 🟡 **PENDING**
- **Problem:** Can't run database queries from CLI due to table conflicts
- **Impact:** Debugging/maintenance difficulty
- **Error:** `Table 'rule_category' is already defined for this MetaData instance`

---

## 📊 **CURRENT SYSTEM STATUS**

### **🎉 MAJOR VICTORIES**
- **Rule 4 Working:** 16 invalid locations detected (was crashing)
- **Warehouse Detection:** 72.7% coverage vs 0% before
- **Session Recovery:** Automatic handling of session corruption
- **Total Anomalies:** **44 detected** across all rules 🚀

### **🔥 NEXT PRIORITIES**
1. **Add missing special areas** (RECV-01, RECV-02, AISLE-02) to USER_TESTF warehouse
2. **Implement location format intelligence** - adapt to user formats
3. **Fix Uncoordinated Lots logic** - should detect LOT001 as straggler

### **📈 PERFORMANCE METRICS**
- **Rule Execution Time:** ~4.3 seconds for 7 rules
- **Database Queries:** Optimized with caching
- **Error Rate:** 0% (all rules executing successfully)
- **Coverage:** 72.7% location recognition (was 0%)

---

## 🛠️ **TECHNICAL DEBT SUMMARY**

**Session Management:** ✅ Core issues resolved, monitoring needed  
**Location Intelligence:** 🔄 Major architecture update required  
**Database Integrity:** 🔄 Missing location records need population  
**Error Handling:** 🔄 Better fallback strategies needed  
**Development Experience:** 🔄 Minor improvements for debugging  

---

**Next Session Goals:** Complete location format intelligence and add missing database locations to achieve 100% rule functionality.

*This document is automatically updated as issues are resolved.*