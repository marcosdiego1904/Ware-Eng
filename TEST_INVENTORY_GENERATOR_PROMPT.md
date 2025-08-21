# TEST INVENTORY GENERATOR - QUICK REFERENCE

## 🎯 **PROMPT FOR CREATING TEST INVENTORIES**

Use this prompt template whenever you need to generate a test inventory for validation:

---

## **INVENTORY GENERATION REQUEST**

```
Create a comprehensive test inventory Excel file with the following specifications:

WAREHOUSE CONFIGURATION:
- Layout Type: [SELECT: Traditional Rack / Flow-Through / Specialized Zones / Mixed 3PL / E-commerce]
- Size Category: [SELECT: Small (100-500 pallets) / Medium (500-2000 pallets) / Large (2000+ pallets)]
- Complexity Level: [SELECT: Basic / Intermediate / Advanced / Stress Test]

TESTING FOCUS:
- Primary Rules to Test: [SELECT: All Rules / Specific Rules (list them)]
- Cross-Rule Intelligence: [Yes/No - include scenarios that trigger multiple rules]
- Performance Testing: [Yes/No - include large dataset scenarios]

VIOLATION SCENARIOS TO INCLUDE:
✅ Rule 1 (Forgotten Pallets): 
   - Critical: 4+ days old in RECEIVING (2-3 pallets)
   - High: 2-4 days old in RECEIVING (3-5 pallets)  
   - Medium: 12+ hours in STAGING (2-4 pallets)

✅ Rule 2 (Incomplete Lots):
   - Lot with 80%+ pallets in STORAGE, stragglers in RECEIVING (1-2 scenarios)
   - Lot with mixed completion rates (1-2 scenarios)

✅ Rule 3 (Overcapacity):
   - RECEIVING: 1.5-2.0x capacity (10-20 pallets in 10-capacity location)
   - STORAGE: 2.0-4.0x capacity (2-4 pallets in 1-capacity locations)

✅ Rule 4 (Invalid Locations):
   - Format errors: INVALID-LOC-001, BAD-FORMAT, @#$%^& (3-5 pallets)
   - Non-existent codes: 99-99-999Z, FAKE-LOCATION (2-3 pallets)

✅ Rule 5 (Aisle Stuck) [if applicable]:
   - AISLE locations with pallets >4 hours old (2-4 pallets)

✅ Rule 7 (Scanner Errors):
   - Duplicate pallet IDs in different locations (1-2 scenarios)
   - Empty/corrupted pallet IDs (1-2 scenarios)

✅ Cross-Rule Scenarios:
   - Pallets triggering both Forgotten + Overcapacity (5-10 pallets)
   - Invalid locations contributing to capacity issues

NORMAL OPERATIONS (60-70% of inventory):
- Recent pallets in appropriate locations
- Proper lot distributions
- Realistic warehouse utilization patterns
- Mixed product types and temperature requirements

OUTPUT REQUIREMENTS:
- Excel format (.xlsx) with standard columns:
  * Pallet ID, Location, Description, Receipt Number, Creation Date, Product Type, Temperature Requirement
- Time spread: 7-day window with realistic creation timestamps
- Product mix: 70% GENERAL, 15% HAZMAT, 10% FROZEN, 5% other
- Lot diversity: 15-30 different receipt numbers
- Include summary of expected violations for validation

SPECIAL REQUIREMENTS:
[Add any specific testing needs, edge cases, or custom scenarios]
```

---

## **QUICK TEST SCENARIOS**

### **Scenario A: Basic Validation**
- 200-300 pallets
- All rule types represented
- Standard warehouse layout
- Focus: Core functionality validation

### **Scenario B: Cross-Rule Intelligence**
- 400-600 pallets  
- Emphasis on overlapping violations
- Complex operational scenarios
- Focus: Correlation accuracy testing

### **Scenario C: Performance Stress**
- 2000+ pallets
- Large-scale capacity violations
- Multiple concurrent issues
- Focus: System performance under load

### **Scenario D: Edge Case Testing**
- 100-200 pallets
- Unusual data formats
- Boundary conditions
- Focus: Error handling and robustness

---

## **VALIDATION CHECKLIST**

After generating each test inventory:

**Data Quality Check:**
- [ ] All required columns present
- [ ] Realistic pallet ID formats
- [ ] Valid location codes (mix of valid/invalid as designed)
- [ ] Appropriate date ranges
- [ ] Product type distributions realistic

**Violation Scenarios Check:**
- [ ] Expected violations documented
- [ ] Cross-rule scenarios included
- [ ] Severity levels appropriate
- [ ] Business logic realistic

**Technical Requirements Check:**
- [ ] File size appropriate for test goal
- [ ] Excel format compatibility
- [ ] No data corruption or formatting issues
- [ ] Performance expectations realistic

---

## **EXPECTED RESULTS TEMPLATE**

For each test inventory, document expected results:

```markdown
## Expected Violations Summary

**Test File**: [filename.xlsx]
**Total Pallets**: [X]
**Test Focus**: [Brief description]

### Rule 1 (Forgotten Pallets): [X] expected violations
- Critical: [X] pallets (>4 days in RECEIVING)
- High: [X] pallets (2-4 days in RECEIVING)  
- Medium: [X] pallets (>12h in STAGING)

### Rule 2 (Incomplete Lots): [X] expected violations
- [Lot Name]: [X] stragglers expected

### Rule 3 (Overcapacity): [X] expected violations
- [Location]: [X] pallets in [Y] capacity location
- Expected severity: [1.Xx or 2.Xx capacity]

### Rule 4 (Invalid Locations): [X] expected violations
- [List invalid location codes]

### Rule 5 (Aisle Stuck): [X] expected violations
- [AISLE locations with time violations]

### Rule 7 (Scanner Errors): [X] expected violations
- Duplicates: [Pallet IDs]
- Corrupted: [Issues]

### Cross-Rule Intelligence: [X] expected correlations
- [Specific scenarios that should trigger multiple rules]

### Performance Expectations:
- Processing time: <[X] seconds
- Memory usage: <[X] MB
- Response time: <[X] seconds
```

---

## **COMMON TESTING PATTERNS**

### **Weekly Testing Routine:**
1. **Monday**: Generate basic validation inventory
2. **Tuesday**: Test cross-rule intelligence scenarios  
3. **Wednesday**: Performance stress testing
4. **Thursday**: Edge case and error handling
5. **Friday**: New feature integration testing

### **Progressive Complexity:**
1. Start with 100-pallet simple scenarios
2. Progress to 500-pallet intermediate complexity
3. Advance to 2000+ pallet stress testing
4. Finish with edge case and boundary testing

---

**Usage**: Copy the main prompt template, fill in your specifications, and use it to generate test inventories. Keep this file open as a reference during Phase 1 testing.

**Last Updated**: [Current Date]