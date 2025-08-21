import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# --- Configuration ---
NOW = datetime.now()
NUM_PALLETS = 450
FILENAME = "small_rack_test_inventory.xlsx"

# Warehouse Layout
AISLES = [1, 2, 3]
RACKS = ['A', 'B']
POSITIONS = range(1, 21)
LEVELS = ['A', 'B', 'C', 'D']

RACK_LOCATIONS = [f"A{a}-R{r}-P{p:02d}-L{l}" for a in AISLES for r in RACKS for p in POSITIONS for l in LEVELS]
SPECIAL_LOCATIONS = {
    "RECV-01": {"type": "RECEIVING", "zone": "DOCK", "capacity": 10},
    "RECV-02": {"type": "RECEIVING", "zone": "RECEIVING", "capacity": 10},
    "STAGE-01": {"type": "STAGING", "zone": "STAGING", "capacity": 5},
    "DOCK-01": {"type": "DOCK", "zone": "DOCK", "capacity": 8},
}
VALID_LOCATIONS = RACK_LOCATIONS + list(SPECIAL_LOCATIONS.keys())
LOCATION_ZONES = {loc: "AMBIENT" for loc in RACK_LOCATIONS if loc.startswith("A1")}
LOCATION_ZONES.update({loc: "COOLER" for loc in RACK_LOCATIONS if loc.startswith("A2")})
LOCATION_ZONES.update({loc: "FROZEN" for loc in RACK_LOCATIONS if loc.startswith("A3")})
for loc, attrs in SPECIAL_LOCATIONS.items():
    LOCATION_ZONES[loc] = attrs["zone"]


# Product Mix
PRODUCT_MIX = {
    "GENERAL": 0.70,
    "HAZMAT": 0.15,
    "FROZEN": 0.10,
    "OTHER": 0.05
}
PRODUCT_DESCRIPTIONS = {
    "GENERAL": ["Standard Goods", "Dry Goods", "Packaged Items"],
    "HAZMAT": ["Cleaning Chemicals", "Industrial Solvents"],
    "FROZEN": ["Frozen Vegetables", "Ice Cream", "Frozen Meats"],
    "OTHER": ["Miscellaneous", "Special Order"]
}
PRODUCT_TEMPS = {
    "GENERAL": "AMBIENT",
    "HAZMAT": "AMBIENT",
    "FROZEN": "FROZEN",
    "OTHER": "AMBIENT"
}

# Lot Numbers
LOT_NUMBERS = [f"REC{1000 + i}" for i in range(30)]

# --- Pallet Generation ---
pallets = []
used_locations = set()
pallet_id_counter = 1

def get_pallet_id():
    global pallet_id_counter
    pid = f"PALLET{20250820 + pallet_id_counter:08d}"
    pallet_id_counter += 1
    return pid

def create_pallet(location, creation_date, product_type=None, receipt_number=None, description=None):
    if not product_type:
        product_type = np.random.choice(list(PRODUCT_MIX.keys()), p=list(PRODUCT_MIX.values()))
    if not receipt_number:
        receipt_number = random.choice(LOT_NUMBERS)
    if not description:
        description = random.choice(PRODUCT_DESCRIPTIONS[product_type])

    temp_req = PRODUCT_TEMPS[product_type]

    return {
        "Pallet ID": get_pallet_id(),
        "Location": location,
        "Description": description,
        "Receipt Number": receipt_number,
        "Creation Date": creation_date,
        "Product Type": product_type,
        "Temperature Requirement": temp_req
    }

# --- Violation Scenarios ---

# Rule 1: Forgotten Pallets
# Critical: 4+ days in RECEIVING (3 pallets)
for _ in range(3):
    pallets.append(create_pallet("RECV-01", NOW - timedelta(days=random.uniform(4, 6))))
# High: 2-4 days in RECEIVING (4 pallets)
for _ in range(4):
    pallets.append(create_pallet("RECV-02", NOW - timedelta(days=random.uniform(2, 4))))
# Medium: 12+ hours in STAGING (3 pallets)
for _ in range(3):
    pallets.append(create_pallet("STAGE-01", NOW - timedelta(hours=random.uniform(12, 24))))

# Rule 3 & Cross-Rule: Overcapacity (on RECV-01, which also has old pallets)
# RECV-01 capacity is 10. We already have 3 old pallets. Add 8 more new ones.
for _ in range(8):
    pallets.append(create_pallet("RECV-01", NOW - timedelta(minutes=random.uniform(30, 60))))

# Rule 2: Incomplete Lots (2 scenarios)
lot1 = "REC1001"
lot2 = "REC1002"
# Scenario 1: 9 in storage, 1 in receiving
for _ in range(9):
    loc = random.choice([l for l in RACK_LOCATIONS if l not in used_locations])
    used_locations.add(loc)
    pallets.append(create_pallet(loc, NOW - timedelta(days=3), "GENERAL", lot1))
pallets.append(create_pallet("RECV-01", NOW - timedelta(days=3), "GENERAL", lot1))
# Scenario 2: 12 in storage, 2 in receiving
for _ in range(12):
    loc = random.choice([l for l in RACK_LOCATIONS if l not in used_locations])
    used_locations.add(loc)
    pallets.append(create_pallet(loc, NOW - timedelta(days=4), "GENERAL", lot2))
pallets.append(create_pallet("RECV-02", NOW - timedelta(days=4), "GENERAL", lot2))
pallets.append(create_pallet("RECV-02", NOW - timedelta(days=4), "GENERAL", lot2))


# Rule 4: Invalid Locations (3 pallets)
pallets.append(create_pallet("INVALID-LOC-01", NOW - timedelta(hours=2)))
pallets.append(create_pallet("AISLE-Z-99", NOW - timedelta(hours=3)))
pallets.append(create_pallet("RECV-99", NOW - timedelta(hours=4)))

# Rule 5: Location Specific Stagnant (AISLE*, > 4 hours) (4 pallets)
for _ in range(4):
    loc = random.choice([l for l in RACK_LOCATIONS if l.startswith('A') and l not in used_locations])
    used_locations.add(loc)
    pallets.append(create_pallet(loc, NOW - timedelta(hours=random.uniform(5, 10))))

# Rule 6: Temperature Zone Mismatch (3 pallets)
# Frozen product in Ambient (A1) or Cooler (A2) zone
ambient_loc = random.choice([l for l in RACK_LOCATIONS if l.startswith('A1') and l not in used_locations])
used_locations.add(ambient_loc)
pallets.append(create_pallet(ambient_loc, NOW - timedelta(days=1), "FROZEN"))
cooler_loc = random.choice([l for l in RACK_LOCATIONS if l.startswith('A2') and l not in used_locations])
used_locations.add(cooler_loc)
pallets.append(create_pallet(cooler_loc, NOW - timedelta(days=1), "FROZEN"))
dock_loc = "DOCK-01" # DOCK zone
pallets.append(create_pallet(dock_loc, NOW - timedelta(days=1), "FROZEN"))


# Rule 7: Data Integrity
# Duplicate Scan (1 pallet ID used twice)
dup_pallet = create_pallet("RECV-01", NOW - timedelta(minutes=10))
pallets.append(dup_pallet)
pallets.append(dup_pallet)
# Impossible Location (1 pallet)
pallets.append(create_pallet("!@#$%^&*", NOW - timedelta(hours=1)))


# Rule 8: Missing Location (2 pallets)
pallets.append(create_pallet(None, NOW - timedelta(days=2)))
pallets.append(create_pallet("", NOW - timedelta(days=3)))


# --- Fill with normal pallets ---
num_normal_pallets = NUM_PALLETS - len(pallets)
available_locations = [l for l in RACK_LOCATIONS if l not in used_locations]

for i in range(num_normal_pallets):
    loc = random.choice(available_locations)
    available_locations.remove(loc) # ensure unique locations for normal pallets
    creation_date = NOW - timedelta(days=random.uniform(0, 7), hours=random.uniform(0,23))
    pallets.append(create_pallet(loc, creation_date))


# --- Create DataFrame and Save ---
df = pd.DataFrame(pallets)
# Shuffle the dataframe to make it look more realistic
df = df.sample(frac=1).reset_index(drop=True)

# Ensure directory exists
output_dir = os.path.dirname(FILENAME)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

df.to_excel(FILENAME, index=False, engine='openpyxl')

print(f"Successfully created '{FILENAME}' with {len(df)} pallets.")

# --- Print Expected Violations Summary ---
print("\n--- Expected Violations Summary ---")
print(f"Test File: {FILENAME}")
print(f"Total Pallets: {len(df)}")
print("Test Focus: All default rules, Cross-Rule Intelligence, Performance")
print("-" * 20)
print("Rule 1 (Forgotten Pallets): 10 expected violations")
print("  - Critical: 3 pallets (>4 days in RECEIVING)")
print("  - High: 4 pallets (2-4 days in RECEIVING)")
print("  - Medium: 3 pallets (>12h in STAGING)")
print("-" * 20)
print("Rule 2 (Incomplete Lots): 2 scenarios (3 straggler pallets total)")
print("  - Lot REC1001: 1 straggler")
print("  - Lot REC1002: 2 stragglers")
print("-" * 20)
print("Rule 3 (Overcapacity): 1+ expected violations")
print("  - RECV-01: 11 pallets (capacity 10)")
print("-" * 20)
print("Rule 4 (Invalid Locations): 3 expected violations")
print("  - Pallets in INVALID-LOC-01, AISLE-Z-99, RECV-99")
print("-" * 20)
print("Rule 5 (Location Specific Stagnant): 4 expected violations")
print("  - Pallets in AISLE* locations > 4 hours old")
print("-" * 20)
print("Rule 6 (Temperature Zone Mismatch): 3 expected violations")
print("  - Frozen products in AMBIENT, COOLER, and DOCK zones")
print("-" * 20)
print("Rule 7 (Data Integrity): 2 expected violations")
print("  - Duplicate Scans: 1 pair of duplicate pallet IDs")
print("  - Impossible Locations: 1 pallet with junk location")
print("-" * 20)
print("Rule 8 (Missing Location): 2 expected violations")
print("  - Pallets with empty or null location")
print("-" * 20)
print("Cross-Rule Intelligence Scenarios:")
print("  - Pallets in RECV-01 are both 'Forgotten Pallets' and part of an 'Overcapacity' violation.")
print("  - One of the 'Incomplete Lots' stragglers is also a 'Forgotten Pallet'.")
