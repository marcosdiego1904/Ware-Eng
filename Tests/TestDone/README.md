# Tests Folder - Inventory Generation Tools

This folder contains inventory generation tools for creating precise test inventory files.

## 🆕 FLEXIBLE GENERATOR (Recommended - Latest)

**Best for**: Progressive testing, scalable validation, precise anomaly control

```bash
# Navigate to Tests folder
cd Tests

# Quick test (100 pallets, 5 anomalies per rule)
python flexible_test_generator.py --quick

# Custom size
python flexible_test_generator.py --pallets 500

# Stress test
python flexible_test_generator.py --stress-test 2000
```

**Flexible generator gives you:**
- Progressive scaling: 100 → 10,000+ pallets
- Fixed anomaly count (5 per rule × 7 rules = 35 total)
- Format-aware location generation (###L pattern)
- Warehouse-specific special areas (RECV-01, AISLE-01, W-01, etc.)
- Detailed generation reports

📖 **Full Documentation**: See `FLEXIBLE_GENERATOR_GUIDE.md`

---

## SIMPLE OPTION (Alternative)

```bash
# Navigate to Tests folder
cd Tests

# Generate simple, predictable test file
python simple_test_generator.py
# → Creates simple_test_inventory.xlsx with EXACTLY 40 anomalies (5 per rule)
```

**Simple test gives you:**
- 100 pallets total
- EXACTLY 5 anomalies per rule (40 total)
- Predictable, easy to validate results
- Perfect for rule testing and validation

## Advanced Options (If needed)

```bash
# Generate standard test file
python smart_inventory_generator.py --quick

# Small test for development
python smart_inventory_generator.py --pallets 100 --anomalies 5

# Overcapacity testing (mixed storage + special locations)
python smart_inventory_generator.py --overcapacity-test 20

# Special location overcapacity only (RECEIVING, AISLE, STAGING, DOCK)
python smart_inventory_generator.py --special-overcapacity-test 4

# Large stress test
python smart_inventory_generator.py --stress-test 2000
```

## Files

### Latest (Recommended)
- **`flexible_test_generator.py`** 🆕 - Flexible, scalable generator with precise control
- **`FLEXIBLE_GENERATOR_GUIDE.md`** 🆕 - Complete usage and testing guide

### Legacy Options
- **`simple_test_generator.py`** - Simple, predictable generator
- **`SIMPLE_TEST_INVENTORY_GUIDE.md`** - Complete editing guide for simple generator
- **`smart_inventory_generator.py`** - Advanced generator with many options
- **`SMART_INVENTORY_GENERATOR_GUIDE.md`** - Complete usage documentation

### Other
- **`README.md`** - This file (quick reference)

## Output

Generated files will be created in the Tests folder unless you specify a different output path.

Example: `inventoryfile.xlsx` (default), `test_from_tests_folder.xlsx`, etc.

## Key Features

✅ **Template-Compatible** - Uses ###L format for your warehouse system  
✅ **8 Rule Types** - All warehouse rules with precise anomaly control  
✅ **Fast Generation** - 800 pallets in ~2 seconds  
✅ **Configurable** - From 100 to 5000+ pallets  

For detailed usage, see `SMART_INVENTORY_GENERATOR_GUIDE.md`.