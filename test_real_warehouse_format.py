#!/usr/bin/env python3
"""
Test Real Warehouse Format: 010A, 325B, 245D, 001A, 145C
Testing if current CanonicalLocationService can handle this specific format
"""

import sys
import os
import re

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def test_current_parsers():
    """Test the current canonical location service parsers against the real format"""
    
    # Real warehouse format examples
    real_locations = ['010A', '325B', '245D', '001A', '145C']
    
    print("TESTING REAL WAREHOUSE FORMAT: NNN{L}")
    print("=" * 50)
    print("Format Pattern: 3-digit number + single letter")
    print("Examples:", real_locations)
    print()
    
    # Simulate the current parser logic
    results = []
    
    for location in real_locations:
        print(f"Testing location: '{location}'")
        
        # Test against current parsers
        canonical_result = test_against_current_parsers(location)
        
        results.append({
            'original': location,
            'canonical': canonical_result,
            'success': canonical_result != location  # If changed, parser worked
        })
        
        print(f"  Current result: '{canonical_result}'")
        print(f"  Status: {'PARSED' if canonical_result != location else 'UNPARSED'}")
        print()
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print("SUMMARY")
    print("-" * 30)
    print(f"Successfully parsed: {successful}/{total} ({successful/total*100:.0f}%)")
    status = "READY" if successful == total else "PARTIALLY READY" if successful > 0 else "NOT READY"
    print(f"Status: {status}")
    
    return results

def test_against_current_parsers(location_code: str) -> str:
    """Simulate the current CanonicalLocationService parsers"""
    
    code = location_code.strip().upper()
    
    # Test Parser 1: _parse_special - Won't match NNN{L} format
    if test_parse_special(code):
        return f"SPECIAL:{code}"
    
    # Test Parser 2: _parse_standard - Won't match NNN{L} format (expects XX-XX-XXX{L})
    standard_result = test_parse_standard(code)
    if standard_result:
        return standard_result
    
    # Test Parser 3: _parse_compact - Won't match NNN{L} format (expects XX{L}XX{L})
    compact_result = test_parse_compact(code)
    if compact_result:
        return compact_result
    
    # Test Parser 4: _parse_user_common - This MIGHT match!
    user_common_result = test_parse_user_common(code)
    if user_common_result:
        return user_common_result
    
    # No parser matched - return original
    return code

def test_parse_special(code: str) -> bool:
    """Test special location parser"""
    special_locations = {
        'RECV-01', 'RECV-02', 'STAGE-01', 'DOCK-01', 'AISLE-01', 'RECEIVING'
    }
    return code in special_locations

def test_parse_standard(code: str) -> str:
    """Test standard parser: XX-XX-XXX{L}"""
    pattern = r'^(\d{1,2})-(\d{1,2})-(\d{1,3})([A-Z])$'
    match = re.match(pattern, code)
    if match:
        aisle, rack, position, level = match.groups()
        return f"{int(aisle):02d}-{int(rack):02d}-{int(position):03d}{level}"
    return None

def test_parse_compact(code: str) -> str:
    """Test compact parser: XX{L}XX{L}"""
    pattern = r'^(\d{1,2})([A-Z])(\d{1,2})([A-Z])$'
    match = re.match(pattern, code)
    if match:
        aisle, rack_level, position, level = match.groups()
        return f"{int(aisle):02d}-01-{int(position):03d}{level}"
    return None

def test_parse_user_common(code: str) -> str:
    """Test user common parser - this is our best hope!"""
    
    # Pattern 1: PPP{L}RR (position + level + rack)
    pattern1 = r'^(\d{1,3})([A-Z])(\d{1,2})$'
    match1 = re.match(pattern1, code)
    if match1:
        position, level, rack = match1.groups()
        aisle = 1
        return f"{aisle:02d}-{int(rack):02d}-{int(position):03d}{level}"
    
    # Pattern 2: {L}R-PPP (level + rack - position)
    pattern2 = r'^([A-Z])(\d{1,2})-(\d{1,3})$'
    match2 = re.match(pattern2, code)
    if match2:
        level, rack, position = match2.groups()
        aisle = 1
        return f"{aisle:02d}-{int(rack):02d}-{int(position):03d}{level}"
    
    # Pattern 3: PP{L}R (compact: position + level + rack)
    pattern3 = r'^(\d{1,2})([A-Z])(\d{1,2})$'
    match3 = re.match(pattern3, code)
    if match3:
        position, level, rack = match3.groups()
        aisle = 1
        return f"{aisle:02d}-{int(rack):02d}-{int(position):03d}{level}"
    
    return None

def propose_solution():
    """Propose a solution for this specific format"""
    
    print("\nPROPOSED SOLUTION")
    print("=" * 50)
    
    print("Current Issue:")
    print("• Format NNN{L} (e.g., '010A', '325B') doesn't match any existing parser")
    print("• This is a common warehouse format: Position Number + Level Letter")
    print("• Pattern: 3-digit position + single level letter")
    print()
    
    print("Solution: Add NNN{L} Parser")
    print("Add this parser to CanonicalLocationService:")
    print()
    print("```python")
    print("def _parse_position_level(self, code: str) -> Optional[str]:")
    print('    """')
    print("    Parse position-level format: NNN{L}")
    print("    Examples: '010A' -> '01-01-010A', '325B' -> '01-01-325B'")
    print('    """')
    print("    pattern = r'^(\d{1,3})([A-Z])$'")
    print("    match = re.match(pattern, code)")
    print("    if match:")
    print("        position, level = match.groups()")
    print("        aisle = 1  # Default aisle")
    print("        rack = 1   # Default rack")
    print("        return f'{aisle:02d}-{rack:02d}-{int(position):03d}{level}'")
    print("    return None")
    print("```")
    print()
    
    print("Integration:")
    print("• Add this parser to format_parsers list in CanonicalLocationService")
    print("• Place it after special location parser but before standard parser")
    print("• Test with real warehouse data")
    print()
    
    print("Expected Results After Fix:")
    print("• '010A' -> '01-01-010A' SUCCESS")
    print("• '325B' -> '01-01-325B' SUCCESS") 
    print("• '001A' -> '01-01-001A' SUCCESS")
    print("• '145C' -> '01-01-145C' SUCCESS")

def main():
    """Run the test"""
    
    print("REAL WAREHOUSE FORMAT COMPATIBILITY TEST")
    print("=" * 60)
    print("Testing format used at warehouses you've worked at: NNN{L}")
    print()
    
    # Test current parsers
    results = test_current_parsers()
    
    # Propose solution
    propose_solution()
    
    # Final assessment
    successful = sum(1 for r in results if r['success'])
    
    print(f"\nFINAL ASSESSMENT")
    print("=" * 30)
    if successful == 0:
        print("SYSTEM NOT READY for this format")
        print("BUT: Easy fix - add one new parser method")
        print("Implementation time: ~1 hour")
    else:
        print(f"PARTIALLY READY ({successful}/{len(results)} locations)")
        print("Some locations parse, refinement needed")
    
    return successful > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)