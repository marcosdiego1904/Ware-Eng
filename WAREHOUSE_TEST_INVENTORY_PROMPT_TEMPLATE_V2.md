# Warehouse Test Inventory Generation Prompt Template V2.0
## Enhanced with Architectural Findings & Template-Based Validation

**IMPORTANT**: This template incorporates critical findings from overcapacity rule architecture investigation. The warehouse rule engine now uses **template-based capacity configuration** through the Virtual Engine system, not pattern matching fallbacks.

---

## System Architecture Understanding

### Rule Engine Architecture (VALIDATED ✅)
- **Virtual Engine Integration**: Rules now use warehouse templates for capacity configuration
- **Smart Configuration Support**: Supports `position_level` format (###L patterns like 001A, 050A)
- **Template-Based Capacity**: STORAGE locations get `capacity=1` from warehouse templates, not pattern matching
- **Performance**: Virtual engine processing takes ~15ms with full template validation

### Critical Discovery: Data Contamination Issue
⚠️ **MAJOR FINDING**: Random data generation creates **accidental anomaly contamination**. When generating "normal" pallets, random location assignment can create:
- Multiple pallets in same STORAGE location (accidental overcapacity)
- Unintentional stagnant pallets from random timestamps
- False lot completion patterns from random lot assignments

**SOLUTION**: Use **controlled assignment patterns** instead of random generation.

---

## Prompt Template for Test Inventory Generation

```
You are tasked with creating a comprehensive warehouse inventory test file (.xlsx format) to validate a sophisticated warehouse rule engine. The system uses template-based capacity configuration through a Virtual Engine.

### CRITICAL REQUIREMENTS:

#### 1. Data Contamination Prevention
**NEVER use random location assignment for normal pallets**. Instead, use controlled patterns:
- STORAGE locations (###L format): ONE pallet per location for normal data
- RECEIVING areas: Use RECV-01, RECV-02, RECV-03 (capacity=10 each)  
- STAGING areas: Use STAGE-01, STAGE-02 (capacity=5 each)
- DOCK areas: Use DOCK-01, DOCK-02 (capacity=2 each)
- AISLE areas: Use AISLE-01, AISLE-02 (capacity=10 each)

#### 2. Smart Configuration Support
The system uses **position_level** format with template-based capacity:
- STORAGE locations: `001A`, `002A`, `003A`... `050A`, `051A`, etc. (capacity=1 each)
- Warehouse layout: 4 aisles × 3 racks × 34 positions × 5 levels = 2,040 total locations
- Template configuration: Applied automatically through Virtual Engine

#### 3. Rule Engine Validation (12 Evaluator Types)

**SPACE Category (Template-Based Capacity):**
- **OvercapacityEvaluator**: ✅ FIXED - Now uses Virtual Engine template capacity
- **LocationMappingEvaluator**: Validates location existence in templates
- **TemperatureZoneEvaluator**: Checks temperature-controlled area compliance

**FLOW_TIME Category:**
- **StagnantPalletsEvaluator**: General stagnation (12+ hours)
- **LocationSpecificStagnantEvaluator**: Area-specific timing (8+ hrs AISLE, 4+ hrs DOCK)
- **UncoordinatedLotsEvaluator**: Lot completion violations (<80% stored)

**PRODUCT Category:**
- **DataIntegrityEvaluator**: Duplicate IDs, missing fields
- **VirtualInvalidLocationEvaluator**: Virtual engine location validation

**Advanced Features:**
- **DuplicateShipmentEvaluator**: Cross-shipment validation
- **ConsistencyEvaluator**: Cross-rule pattern analysis
- **ComplianceEvaluator**: Business rule adherence
- **HighVelocityItemEvaluator**: Movement pattern analysis

### GENERATION PARAMETERS:

#### File Configuration:
- **Total Pallets**: [USER_SPECIFIED] (recommended: 100-500 for controlled testing)
- **Format**: Excel (.xlsx) with proper column types and formatting
- **Required Columns**: 
  - `pallet_id` (string): Unique identifier
  - `location` (string): Smart Configuration format (###L for storage)
  - `creation_date` (datetime): ISO format timestamp
  - `receipt_number` (string): Shipment/lot identifier  
  - `description` (string): Pallet contents description
  - `location_type` (string): STORAGE, RECEIVING, STAGING, DOCK, AISLE

#### Targeted Anomaly Generation:

**Overcapacity Anomalies** (NOW WORKING ✅):
- Count: [USER_SPECIFIED] locations with excess pallets
- Implementation: Place exactly 2+ pallets in specific STORAGE locations (###L format)
- Expected Detection: Each pallet in overcapacity location flagged individually
- Example: Location `050A` with 2 pallets = 2 anomalies detected

**Stagnant Pallets**:
- Count: [USER_SPECIFIED] pallets with old timestamps
- RECEIVING areas: 12+ hours ago
- AISLE areas: 8+ hours ago  
- DOCK areas: 4+ hours ago
- STAGING areas: 6+ hours ago

**Lot Coordination Issues**:
- Count: [USER_SPECIFIED] lots with <80% completion
- Implementation: Create lot with N stored + M stragglers in RECEIVING
- Calculation: M/(N+M) > 20% triggers violation

**Location Validity**:
- Count: [USER_SPECIFIED] pallets in invalid locations
- Examples: `999Z`, `FAKE-LOC`, `INVALID`, `ERROR-01`
- Mix obvious invalids with subtle format violations

**Data Integrity**:
- Count: [USER_SPECIFIED] duplicate IDs, empty locations, malformed data
- Examples: Same pallet_id used twice, empty location field

#### Warehouse Layout Distribution:
- **STORAGE**: 70-80% of pallets (use sequential ###L assignment)
- **RECEIVING**: 10-15% of pallets (controlled area assignment)  
- **STAGING**: 5-10% of pallets
- **DOCK**: 2-5% of pallets
- **AISLE**: 2-5% of pallets

### CONTROLLED ASSIGNMENT STRATEGY:

Instead of random assignment:

```python
# CORRECT: Controlled assignment prevents contamination
storage_locations = [f"{i:03d}A" for i in range(1, normal_pallet_count + 1)]
for i, pallet in enumerate(normal_pallets):
    pallet['location'] = storage_locations[i]  # One pallet per location

# WRONG: Random assignment creates contamination  
pallet['location'] = random.choice(all_locations)  # Causes accidental overcapacity
```

### EXPECTED DETECTION RATES:

Based on architectural validation:
- **Overcapacity**: 100% detection rate (template-based capacity working)
- **Stagnant Pallets**: ~90% detection (timestamp-based)
- **Invalid Locations**: ~95% detection (virtual engine validation)
- **Data Integrity**: ~100% detection (schema validation)
- **Lot Coordination**: ~85% detection (completion ratio calculation)

### OUTPUT REQUIREMENTS:

1. **Excel File**: Formatted .xlsx with proper data types
2. **Anomaly Summary**: Detailed breakdown of targeted vs detected anomalies
3. **Test Report**: Location distribution, timestamp analysis, validation results
4. **Architecture Compatibility**: Confirm Smart Configuration format usage

### SUCCESS CRITERIA:

- **Precision Testing**: Detected anomalies should match targeted anomalies (±5%)
- **Template Integration**: System should use Virtual Engine for capacity detection  
- **Performance**: Rule evaluation should complete in <50ms for 100-500 pallets
- **No False Positives**: Normal data should not trigger unintended rule violations

Generate a warehouse inventory test file following these specifications, ensuring surgical precision in anomaly targeting and zero data contamination from random assignment patterns.
```

---

## Architecture Validation Summary

### What Was Fixed ✅
1. **Template Integration**: OvercapacityEvaluator now uses Virtual Engine for template-based capacity
2. **Method Signatures**: Updated all `_get_location_capacity()` calls to pass `warehouse_context`
3. **Smart Configuration**: System properly detects `position_level` format and applies template capacity
4. **Performance**: Virtual Engine integration maintains <50ms processing time

### What Was Discovered 🔍
1. **Data Contamination**: Random location assignment in test generators causes false positives
2. **Surgical Testing**: Minimal controlled tests (3-5 pallets) provide better validation than large random sets
3. **Template Architecture**: System architecture was already correct - just needed proper integration
4. **Fallback Graceful**: System gracefully handles Virtual Engine failures with enhanced pattern matching

### Production Validation ✅
- **File**: `controlled_test_inventory_100.xlsx` processed successfully
- **Virtual Engine**: Smart Configuration detected and initialized
- **Performance**: 75 anomalies detected in 15ms  
- **Template System**: Warehouse DEFAULT with 2,040 storage locations configured

This template now incorporates all architectural learnings and provides guidance for creating test files that work optimally with the template-based warehouse rule engine system.