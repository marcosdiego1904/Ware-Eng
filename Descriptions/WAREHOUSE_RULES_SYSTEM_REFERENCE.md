# Warehouse Rules System - Complete Reference Guide

**Generated**: 2025-09-07  
**Status**: Comprehensive Investigation Complete  
**Purpose**: Complete reference for default rules system behavior and anomaly counting logic

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Default Rules Inventory](#default-rules-inventory)
3. [Rule Categories](#rule-categories)
4. [Anomaly Counting Logic](#anomaly-counting-logic)
5. [Rule Triggers](#rule-triggers)
6. [Performance Insights](#performance-insights)
7. [Testing Results](#testing-results)

---

## System Architecture

### Core Components
- **Rule Engine**: `backend/src/rule_engine.py:33-72`
- **Default Rules**: `backend/src/models.py:934-1045` 
- **Categories**: `backend/src/models.py:902-921`
- **Evaluators**: Specialized classes for each rule type

### Design Pattern
```
Dynamic, database-driven architecture that replaces hardcoded detection 
logic with configurable rules. Allows runtime rule management and 
sophisticated evaluator patterns.
```

---

## Default Rules Inventory (8 Rules Total)

### Core 4 Rules (Original Set)

#### 1. **Forgotten Pallets Alert**
- **Type**: `STAGNANT_PALLETS`
- **Category**: `FLOW_TIME` 
- **Priority**: `HIGH`
- **Location**: `backend/src/rule_engine.py:1210+`
- **Goal**: Detects pallets in RECEIVING areas for more than 10 hours
- **Business Logic**: Identifies workflow inefficiencies and forgotten items
- **Conditions**: `{"location_types": ["RECEIVING"], "time_threshold_hours": 10}`
- **Parameters**: Time threshold (1-24 hours, default: 10)
- **Anomaly Count**: 1 anomaly per qualifying pallet

#### 2. **Incomplete Lots Alert** 
- **Type**: `UNCOORDINATED_LOTS`
- **Category**: `FLOW_TIME`
- **Priority**: `VERY_HIGH` ⚠️ (Highest Priority)
- **Location**: `backend/src/rule_engine.py:1484+`
- **Goal**: Identifies pallets still in receiving when 80%+ of their lot has been stored
- **Business Logic**: Prevents lot fragmentation and coordination issues
- **Conditions**: `{"completion_threshold": 0.8, "location_types": ["RECEIVING"]}`
- **Parameters**: Completion threshold (0.5-1.0, default: 0.8)
- **Anomaly Count**: 1 anomaly per straggler pallet

#### 3. **Overcapacity Alert** ⚠️ **CRITICAL DISCOVERY**
- **Type**: `OVERCAPACITY`
- **Category**: `SPACE`
- **Priority**: `HIGH`
- **Location**: `backend/src/rule_engine.py:1528+`
- **Goal**: Detects locations exceeding their designated storage capacity
- **Business Logic**: Prevents safety issues and space management problems
- **Conditions**: `{"check_all_locations": True}`
- **Parameters**: No configurable parameters

##### **✅ OPTIMIZED ANOMALY COUNTING BEHAVIOR** (Updated 2025-09-10)
The overcapacity rule uses **location differentiation logic** with **alert fatigue optimization**:

**Storage Locations** (Optimized Approach):
```python
# Generate ONE representative alert per overcapacity storage location
# Includes metadata about all affected pallets for investigation
anomalies.append({
    'anomaly_type': 'Storage Overcapacity',
    'priority': 'Very High',  # CRITICAL
    'business_context': 'CRITICAL - Data integrity requires location investigation',
    'affected_pallets': location_count,  # Total pallets in location
    'excess_pallets': excess_count      # Pallets over capacity
})
```

**Special Locations** (Same as before):
```python
# Generate WARNING location-level alerts for Special areas
# Single alert per overcapacity special area (representative pallet)
anomalies.append({
    'anomaly_type': 'Special Area Capacity',
    'priority': 'High',  # WARNING
    'business_context': 'WARNING - Space management focus, expedite area processing'
})
```

**Anomaly Count** (Current Behavior):
- **Storage locations**: **1 representative alert** per overcapacity location (with affected_pallets metadata)
- **Special locations**: 1 representative alert per overcapacity location
- **Example**: Location with 10 pallets (capacity=1) → **1 anomaly** for storage + metadata, **1 anomaly** for special

**Benefits of Optimization**:
- **Reduced Alert Fatigue**: No longer floods operators with duplicate alerts
- **Maintained Precision**: All affected pallets tracked via metadata
- **Improved Usability**: Focus on location-level investigation rather than individual pallets
- **Better Performance**: Fewer anomaly objects to process and display

#### 4. **Invalid Locations Alert**
- **Type**: `INVALID_LOCATION` 
- **Category**: `SPACE`
- **Priority**: `HIGH`
- **Location**: Uses `VirtualInvalidLocationEvaluator`
- **Goal**: Finds pallets in locations not defined in warehouse rules
- **Business Logic**: Ensures inventory accuracy and location compliance
- **Conditions**: `{"check_undefined_locations": True}`
- **Parameters**: No configurable parameters
- **Anomaly Count**: 1 anomaly per pallet in invalid location

### Enhanced Rules (4 Additional Rules)

#### 5. **AISLE Stuck Pallets**
- **Type**: `LOCATION_SPECIFIC_STAGNANT`
- **Category**: `FLOW_TIME`
- **Priority**: `HIGH`
- **Location**: `backend/src/rule_engine.py:2406+`
- **Goal**: Detects pallets stuck in AISLE locations for 4+ hours
- **Business Logic**: Prevents aisle blockages and movement inefficiencies  
- **Conditions**: `{"location_pattern": "AISLE*", "time_threshold_hours": 4}`
- **Parameters**: Location pattern and time threshold (1-12 hours)
- **Anomaly Count**: 1 anomaly per qualifying pallet

#### 6. **Cold Chain Violations**
- **Type**: `TEMPERATURE_ZONE_MISMATCH`
- **Category**: `PRODUCT`
- **Priority**: `VERY_HIGH` ⚠️ (Highest Priority)
- **Location**: `backend/src/rule_engine.py:2448+`
- **Goal**: Identifies temperature-sensitive products in inappropriate zones
- **Business Logic**: Prevents product spoilage and compliance violations
- **Conditions**: `{"product_patterns": ["*FROZEN*", "*REFRIGERATED*"], "prohibited_zones": ["AMBIENT", "GENERAL"], "time_threshold_minutes": 30}`
- **Parameters**: Time threshold (5-120 minutes, default: 30)
- **Anomaly Count**: 1 anomaly per qualifying pallet

#### 7. **Scanner Error Detection**
- **Type**: `DATA_INTEGRITY`
- **Category**: `SPACE`
- **Priority**: `MEDIUM`
- **Location**: `backend/src/rule_engine.py:2485+`
- **Goal**: Detects data integrity issues from scanning errors
- **Business Logic**: Ensures data accuracy and system reliability
- **Conditions**: `{"check_impossible_locations": True, "check_duplicate_scans": True}`
- **Parameters**: No configurable parameters
- **Anomaly Count**: 1 anomaly per data integrity issue

#### 8. **Location Type Mismatches**
- **Type**: `LOCATION_MAPPING_ERROR`
- **Category**: `SPACE` 
- **Priority**: `HIGH`
- **Location**: `backend/src/rule_engine.py:2520+`
- **Goal**: Identifies inconsistencies in location type mapping
- **Business Logic**: Maintains location hierarchy and mapping accuracy
- **Conditions**: `{"validate_location_types": True, "check_pattern_consistency": True}`
- **Parameters**: No configurable parameters
- **Anomaly Count**: 1 anomaly per mapping inconsistency

---

## Rule Categories (Three Pillars Framework)

### 1. **FLOW_TIME** (Priority 1 - Maximum)
- **Purpose**: Detect stagnant pallets, uncoordinated lots, and time-based issues
- **Rules**: Forgotten Pallets, Incomplete Lots, AISLE Stuck Pallets
- **Focus**: Operational efficiency and movement optimization
- **Database Priority**: 1

### 2. **SPACE** (Priority 2 - High)  
- **Purpose**: Manage warehouse space, capacity, and location compliance
- **Rules**: Overcapacity, Invalid Locations, Scanner Errors, Location Mismatches
- **Focus**: Space utilization and location accuracy
- **Database Priority**: 2

### 3. **PRODUCT** (Priority 3 - Medium)
- **Purpose**: Ensure products are stored in appropriate locations
- **Rules**: Cold Chain Violations
- **Focus**: Product integrity and compliance  
- **Database Priority**: 3

### Priority Levels Within Rules
- `VERY_HIGH`: Most critical (Cold Chain, Incomplete Lots)
- `HIGH`: Important operational issues (most rules)
- `MEDIUM`: Data quality issues
- `LOW`: Not used in default set

---

## Anomaly Counting Logic

### Summary by Rule Type

| Rule Type | Counting Logic | Example |
|-----------|---------------|---------|
| **Stagnant Pallets** | 1 per qualifying pallet | 5 pallets >10hrs = 5 anomalies |
| **Incomplete Lots** | 1 per straggler pallet | 3 stragglers = 3 anomalies |
| **Overcapacity (Storage)** | **ALL pallets in location** | 10 pallets in location = **10 anomalies** |
| **Overcapacity (Special)** | 1 per overcapacity location | 3 special areas = 3 anomalies |
| **Invalid Location** | 1 per pallet | 5 invalid pallets = 5 anomalies |
| **AISLE Stuck** | 1 per qualifying pallet | 4 stuck pallets = 4 anomalies |
| **Cold Chain** | 1 per qualifying pallet | 5 violations = 5 anomalies |
| **Scanner Errors** | 1 per integrity issue | 6 issues = 6 anomalies |
| **Location Mapping** | 1 per mapping error | 5 errors = 5 anomalies |

### Critical Discovery: Overcapacity Multiplication Effect

**Traditional Understanding**: Overcapacity flags excess pallets only  
**Actual Behavior**: **ALL pallets** in overcapacity storage locations are flagged

**Impact**: 
- Location with capacity=1 and 10 pallets → **10 anomalies** (not 9)
- Creates significant anomaly multiplication in storage areas
- Special areas (recv, dock, aisle) only generate 1 representative anomaly per location

---

## Rule Triggers

### Evaluation Process (`backend/src/rule_engine.py:155-236`)

1. **Rule Loading**: System loads active rules from database (`load_active_rules()`)
2. **Data Normalization**: Inventory DataFrame columns normalized (`_normalize_dataframe_columns()`)
3. **Evaluator Selection**: Each rule type maps to specialized evaluator class
4. **Warehouse Context**: Rules evaluated with warehouse-specific context for performance
5. **Performance Tracking**: Execution time and success metrics recorded

### Required Data Columns
```python
# Normalized column names expected by rule engine
required_columns = {
    'pallet_id': 'Unique pallet identifier',
    'location': 'Current location code', 
    'creation_date': 'Timestamp when pallet entered location',
    'receipt_number': 'Lot/receipt identifier',
    'product': 'Product name/description',
    'location_type': 'Classified location type (RECEIVING, STORAGE, etc.)'
}
```

### Triggering Methods
1. **Inventory File Upload**: Primary trigger through web interface
2. **API Endpoints**: Direct rule evaluation via REST API  
3. **Manual Analysis**: Debug and testing interfaces
4. **Batch Processing**: Scheduled or bulk analysis runs

### Rule Initialization
- **Migration System**: `backend/src/migrations.py:229-314` creates default rules
- **Auto-Migration**: `backend/src/auto_migrate.py:103-239` handles rule seeding
- **Database Flag**: Rules marked with `is_default=True` flag

---

## Performance Optimizations

### System Enhancements
- **Warehouse-Scoped Queries**: Rules only load relevant warehouse locations
- **Location Caching**: Prevents repeated database queries  
- **Virtual Location System**: Enhanced invalid location detection
- **Execution Time Tracking**: Performance monitoring and optimization

### Location Cache (`backend/src/rule_engine.py:74-98`)
```python
def _get_warehouse_locations(self, warehouse_context: dict = None):
    """
    PERFORMANCE OPTIMIZATION: Get locations filtered by warehouse 
    instead of loading ALL locations. Fixes critical performance 
    issue where 12,080+ locations were loaded for every rule.
    """
```

---

## Testing Results

### Strategic Inventory File Test
**File**: `strategic_anomaly_inventory.xlsx`  
**Total Records**: 143  
**Expected vs Actual Anomalies**:

| Rule | Expected | Actual | Notes |
|------|----------|--------|--------|
| Forgotten Pallets | 5 | 5 | ✅ As expected |
| Incomplete Lots | 5 | 5 | ✅ As expected |
| **Overcapacity** | **5** | **109** | ⚠️ **Multiplication effect discovered** |
| Invalid Locations | 5 | 5 | ✅ As expected |
| AISLE Stuck | 5 | 5 | ✅ As expected |
| Cold Chain | 5 | 5 | ✅ As expected |
| Scanner Errors | 6 | 6 | ✅ As expected |
| Location Mapping | 5 | 5 | ✅ As expected |
| **TOTAL** | **40** | **145** | **+105 due to overcapacity logic** |

### Overcapacity Breakdown
- **Storage Locations**: 106 anomalies (every pallet in overcapacity storage)
- **Special Locations**: 3 anomalies (recv-1, aisle-01, aisle-02 representatives)
- **Key Insight**: `201A` with 10 pallets = 10 anomalies, not 1

---

## Key Insights

### 🔥 Critical Findings
1. **Overcapacity Multiplication**: Storage locations flag ALL pallets, not just excess
2. **Location Differentiation**: Storage vs Special areas have different anomaly patterns
3. **Priority Escalation**: Storage overcapacity gets `VERY_HIGH` priority vs `HIGH` for special areas
4. **Performance Impact**: More anomalies = longer processing time and more alerts

### 💡 Business Logic Understanding
1. **Data Integrity Focus**: Individual pallet tracking in storage areas for precise investigation
2. **Operational Focus**: Area-level alerts in special locations for space management
3. **Alert Fatigue Mitigation**: Different strategies prevent overwhelming users while maintaining precision

### 🎯 Testing Implications
- Creating "5 overcapacity anomalies" requires careful location selection
- Random distribution of inventory can create unintended overcapacity multiplication
- Special locations (recv, dock, aisle) are safer for controlled anomaly testing

---

## Conclusion

The warehouse rules system provides comprehensive anomaly detection with sophisticated 
location-aware logic. The **critical discovery** of overcapacity multiplication behavior 
significantly impacts anomaly volumes and must be considered in:

- **Test Data Design**: Careful inventory distribution planning
- **Alert Volume Planning**: Expected anomaly counts may be much higher
- **Performance Planning**: More anomalies require more processing resources
- **User Experience**: Alert presentation strategies for high-volume anomalies

This reference document should be consulted for all future rule system work, testing, 
and anomaly count estimations.

---

**Document Maintained By**: System Investigation  
**Last Updated**: 2025-09-07  
**Next Review**: When rule logic changes or new rules added