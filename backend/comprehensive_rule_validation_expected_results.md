
# Expected Violations Summary

**Test File**: comprehensive_rule_validation_test.xlsx
**Total Pallets**: ~300
**Test Focus**: Comprehensive rule validation with cross-rule intelligence

## Rule 1 (Forgotten Pallets): 10 expected violations
- Critical: 3 pallets (4+ days in RECEIVING)
- High: 4 pallets (2-4 days in RECEIVING)  
- Medium: 3 pallets (12+ hours in STAGING)

## Rule 2 (Incomplete Lots): 1 expected violation
- RCP2024XXXX: 2 stragglers in RECEIVING (80% completion)

## Rule 3 (Overcapacity): 60+ expected violations
- RECV-01: 23+ pallets in 10-capacity location (2.3x overcapacity)
- Storage locations: 15 locations with 3-4 pallets in 2-capacity levels

## Rule 4 (Invalid Locations): 5 expected violations
- INVALID-LOC-001, BAD-FORMAT, @#$%^&, 99-99-999Z, FAKE-LOCATION

## Rule 5 (Aisle Stuck): 3 expected violations
- AISLE-01/AISLE-02 locations with pallets >4 hours old

## Rule 7 (Scanner Errors): 3 expected violations
- 1 duplicate pallet ID in different locations
- 2 corrupted/empty pallet ID entries

## Cross-Rule Intelligence: 8+ expected correlations
- 8 pallets triggering both Forgotten Pallets + Overcapacity in RECV-01
- Invalid locations contributing to overall warehouse inefficiency

## Performance Expectations:
- Processing time: <5 seconds
- Memory usage: <50 MB
- Response time: <3 seconds
- Rule execution: <1000ms per rule

## Data Quality Verification:
[✓] All required columns present
[✓] Realistic pallet ID formats (PLT######)
[✓] Valid location codes (mix of valid/invalid as designed)
[✓] 7-day date range with realistic timestamps
[✓] Product type distribution: 70% GENERAL, 15% HAZMAT, 10% FROZEN, 5% other
[✓] 25 different receipt numbers for lot diversity
