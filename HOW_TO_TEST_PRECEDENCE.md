# How to Test the Rule Precedence System

## Quick Tests (Command Line)

### Test 1: Direct Logic Test (Fastest)
```bash
cd C:\Users\juanb\Documents\Diego\Projects\ware2
python test_exclusion_logic.py
```
**Expected Output:**
```
SUCCESS: Precedence system correctly excluded the pallet!
All tests PASSED - Precedence system working correctly!
```

### Test 2: Custom Inventory Test (Most Comprehensive)
```bash
# Create test inventory
python test_double_counting_inventory.py

# Test with the inventory
python test_with_custom_inventory.py
```
**Expected Output:**
```
SUCCESS: No double-counting detected!
The precedence system correctly prevented invalid location pallets
from being flagged by overcapacity rules.
```

## Web Interface Test

### Step 1: Start the Backend Server
```bash
cd backend
python run_server.py
```

### Step 2: Upload Test Inventory
1. Open http://localhost:5000/dashboard
2. Upload `test_double_counting_inventory.xlsx` (created by the test script)
3. Run the analysis

### Step 3: Check Results
Look for these indicators that precedence is working:

**✅ Good Signs:**
- Invalid location anomalies: ~15 (from invalid locations)
- Overcapacity anomalies: ~15 (from RECV-01 only)
- **No pallets flagged by both INVALID_LOCATION and OVERCAPACITY rules**

**❌ Problem Signs:**
- Overcapacity anomalies: ~30 (if invalid locations are double-counted)
- Pallets appearing in both invalid location AND overcapacity results

## Understanding the Results

### Rule Precedence Hierarchy
1. **Level 1 (Data Integrity)**: Invalid Locations Alert, Scanner Error Detection
2. **Level 2 (Operational Safety)**: Overcapacity Alert, Cold Chain Violations  
3. **Level 3 (Process Efficiency)**: Stagnant Pallets, Incomplete Lots, AISLE Stuck Pallets
4. **Level 4 (Data Quality)**: Location Type Mismatches

### How Exclusion Works
- When a Level 1 rule flags a pallet, Level 2+ rules should exclude that pallet
- This prevents double-counting while preserving legitimate multi-rule scenarios
- You should see debug messages like: `[RULE_PRECEDENCE] Registered X anomalies from INVALID_LOCATION`

## Troubleshooting

### If Tests Fail
1. **Check precedence levels in database:**
   ```bash
   cd backend
   python -c "
   import sys, os
   sys.path.insert(0, 'src')
   from app import app
   from database import db  
   from models import Rule
   with app.app_context():
       rules = Rule.query.all()
       for rule in rules:
           print(f'{rule.name}: precedence={rule.precedence_level}')
   "
   ```

2. **Check if precedence system is enabled:**
   Look for log messages: `[RULE_PRECEDENCE] Rule precedence system ENABLED`

3. **Unicode encoding issues:**
   If you see encoding errors, set: `set PYTHONIOENCODING=utf-8`

### Common Issues
- **All rules have precedence=4**: Run the database migration again
- **Overcapacity rule failing**: Unicode encoding issues (check console output)  
- **No exclusion messages**: Precedence system might be disabled

## What Success Looks Like

When the precedence system is working correctly:

1. **Direct Test**: Shows exclusion working with test pallets
2. **Inventory Test**: Invalid location pallets are NOT double-flagged by overcapacity
3. **Production**: Significant reduction in total anomaly count due to eliminated double-counting
4. **Logs**: Clear precedence debug messages showing exclusions

The key metric: **Zero pallets flagged by both INVALID_LOCATION and OVERCAPACITY rules**