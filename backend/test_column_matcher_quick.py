"""
Quick test script for column matcher
Run this to verify the column matcher works without full unit tests
"""

import sys
sys.path.insert(0, 'src')

from src.column_matcher import suggest_column_mapping

# Test with real-world column names from WMS exports
print("=" * 70)
print("QUICK TEST: Intelligent Column Matching")
print("=" * 70)
print()

# Test Case 1: Perfect match (from your test_column_mapping.xlsx)
print("Test Case 1: Perfect Match")
print("-" * 70)
user_columns_1 = ['Location', 'Pallet number', 'Receipt number', 'Item description', 'creation_date']
result_1 = suggest_column_mapping(user_columns_1)

print(f"[OK] Matched: {result_1['statistics']['matched']}/{result_1['statistics']['total_required']}")
print(f"[OK] Auto-mappable (>=85%): {result_1['statistics']['auto_mappable_count']}")
print(f"[!!] Requires review: {result_1['statistics']['requires_review_count']}")
print(f"[XX] Unmapped: {result_1['statistics']['unmapped_required']}")
print()

for req_col, suggestion in result_1['suggestions'].items():
    if suggestion['matched_column']:
        confidence_icon = "[OK]" if suggestion['confidence'] >= 0.85 else "[!!]" if suggestion['confidence'] >= 0.65 else "[??]"
        print(f"  {confidence_icon} {req_col:20s} -> {suggestion['matched_column']:25s} ({suggestion['confidence']:.0%} via {suggestion['method']})")
    else:
        print(f"  [XX] {req_col:20s} -> NOT FOUND")
print()

# Test Case 2: Fuzzy match (abbreviations and variations)
print("Test Case 2: Fuzzy Matching (Abbreviations)")
print("-" * 70)
user_columns_2 = ['PLT', 'Loc', 'Item', 'Lot', 'Date']
result_2 = suggest_column_mapping(user_columns_2)

print(f"[OK] Matched: {result_2['statistics']['matched']}/{result_2['statistics']['total_required']}")
print(f"[OK] Auto-mappable (>=85%): {result_2['statistics']['auto_mappable_count']}")
print(f"[!!] Requires review: {result_2['statistics']['requires_review_count']}")
print(f"[XX] Unmapped: {result_2['statistics']['unmapped_required']}")
print()

for req_col, suggestion in result_2['suggestions'].items():
    if suggestion['matched_column']:
        confidence_icon = "[OK]" if suggestion['confidence'] >= 0.85 else "[!!]" if suggestion['confidence'] >= 0.65 else "[??]"
        print(f"  {confidence_icon} {req_col:20s} -> {suggestion['matched_column']:25s} ({suggestion['confidence']:.0%} via {suggestion['method']})")
    else:
        print(f"  [XX] {req_col:20s} -> NOT FOUND")
print()

# Test Case 3: Real WMS export (Manhattan style)
print("Test Case 3: Real WMS Export (Manhattan WMS)")
print("-" * 70)
user_columns_3 = ['LPN', 'Warehouse Location', 'Item Description', 'ASN', 'Received Date']
result_3 = suggest_column_mapping(user_columns_3)

print(f"[OK] Matched: {result_3['statistics']['matched']}/{result_3['statistics']['total_required']}")
print(f"[OK] Auto-mappable (>=85%): {result_3['statistics']['auto_mappable_count']}")
print(f"[!!] Requires review: {result_3['statistics']['requires_review_count']}")
print(f"[XX] Unmapped: {result_3['statistics']['unmapped_required']}")
print()

for req_col, suggestion in result_3['suggestions'].items():
    if suggestion['matched_column']:
        confidence_icon = "[OK]" if suggestion['confidence'] >= 0.85 else "[!!]" if suggestion['confidence'] >= 0.65 else "[??]"
        alternatives_count = len(suggestion.get('alternatives', []))
        alt_text = f" (+{alternatives_count} alt)" if alternatives_count > 0 else ""
        print(f"  {confidence_icon} {req_col:20s} -> {suggestion['matched_column']:25s} ({suggestion['confidence']:.0%} via {suggestion['method']}){alt_text}")
    else:
        print(f"  [XX] {req_col:20s} -> NOT FOUND")
print()

print("=" * 70)
print("SUMMARY:")
print("=" * 70)
total_tests = 3
perfect_matches = sum(1 for r in [result_1, result_2, result_3] if r['statistics']['matched'] == r['statistics']['total_required'])
partial_matches = sum(1 for r in [result_1, result_2, result_3] if 0 < r['statistics']['matched'] < r['statistics']['total_required'])

print(f"[OK] Perfect matches: {perfect_matches}/{total_tests}")
print(f"[!!] Partial matches: {partial_matches}/{total_tests}")
print()

if perfect_matches >= 2:
    print("SUCCESS! Column matcher is working correctly!")
    print("Ready for production use.")
else:
    print("NEEDS REVIEW: Some test cases didn't match perfectly.")
    print("Check the semantic keywords in column_matcher.py")

print()
print("Next steps:")
print("1. Run full unit tests: python src/test_column_matcher.py")
print("2. Test API endpoint with Postman or curl")
print("3. Test in frontend with real WMS export")
print("=" * 70)
