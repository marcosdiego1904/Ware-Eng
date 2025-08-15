#!/usr/bin/env python3
"""
Comprehensive analysis of location mismatch patterns
"""
import sys
import os

# Add the backend src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def detailed_pattern_analysis():
    """Analyze the exact pattern matching issues"""
    print("LOCATION MISMATCH ROOT CAUSE ANALYSIS")
    print("=" * 50)
    
    # Failing Excel locations from debug output  
    failing_excel = [
        '02-06-03A',    # 9 characters
        '04-04-06B',    # 9 characters  
        '03-05-03B',    # 9 characters
        '01-03-04A',    # 9 characters
        '05-02-01B',    # 9 characters
    ]
    
    # Working database locations from debug output
    working_db = [
        'USER_01-02-021A_1',  # 15 characters
        '02-01-006C',         # 10 characters  
        '02-02-041B',         # 10 characters
        'USER_02-01-027C_2',  # 15 characters
        '05-05-002A',         # 10 characters
    ]
    
    # Successful Excel locations
    working_excel = [
        '01-02-002A',   # 10 characters 
        '02-01-004A',   # 10 characters
        'RCV-001',      # 7 characters
        '01-01-001A',   # 10 characters
    ]
    
    print(f"FAILING Excel locations: {failing_excel}")
    print(f"WORKING Database locations: {working_db}")  
    print(f"WORKING Excel locations: {working_excel}")
    
    # Pattern Analysis
    print(f"\nPATTERN LENGTH ANALYSIS:")
    print(f"Failing Excel lengths: {[len(loc) for loc in failing_excel]}")
    print(f"Working DB lengths: {[len(loc) for loc in working_db]}")
    print(f"Working Excel lengths: {[len(loc) for loc in working_excel]}")
    
    # Digit analysis
    print(f"\nDIGIT PATTERN ANALYSIS:")
    
    def analyze_digits(locations, label):
        print(f"{label}:")
        for loc in locations:
            # Extract digit segments between dashes
            if '-' in loc:
                parts = loc.split('-')
                if len(parts) >= 3:
                    # Assuming format: XX-YY-ZZZ
                    aisle = parts[0].replace('USER_', '') if parts[0] else ""
                    rack = parts[1] if parts[1] else ""
                    position = parts[2].replace('_1', '').replace('_2', '') if parts[2] else ""
                    
                    print(f"  '{loc}' -> Aisle: '{aisle}' ({len(aisle)}), Rack: '{rack}' ({len(rack)}), Position: '{position}' ({len(position)})")
    
    analyze_digits(failing_excel, "FAILING Excel")
    analyze_digits(working_db[:3], "WORKING Database") 
    analyze_digits(working_excel, "WORKING Excel")
    
    # The pattern emerges!
    print(f"\nKEY INSIGHT:")
    print(f"FAILING: 02-06-03A (2-2-3 digit pattern)")
    print(f"WORKING: 02-01-006C (2-2-4 digit pattern)")
    print(f"The issue appears to be POSITION FIELD LENGTH!")
    
    # Test the hypothesis
    print(f"\nHYPOTHESIS TESTING:")
    
    # Import location extraction methods
    try:
        from rule_engine import BaseRuleEvaluator
        evaluator = BaseRuleEvaluator()
        
        test_locations = [
            '02-06-03A',     # Should fail: 2-2-3 pattern
            '02-06-003A',    # Should work: 2-2-4 pattern  
            '04-04-06B',     # Should fail: 2-2-3 pattern
            '04-04-006B',    # Should work: 2-2-4 pattern
            '02-01-006C',    # Known working: 2-2-4 pattern
        ]
        
        print(f"Testing position field length hypothesis:")
        for loc in test_locations:
            base = evaluator._extract_base_location_code(loc)
            parts = loc.split('-') if '-' in loc else [loc]
            if len(parts) >= 3:
                pos_length = len(parts[2].replace('A', '').replace('B', '').replace('C', ''))
                print(f"  '{loc}' -> Base: '{base}', Position digits: {pos_length}")
            else:
                print(f"  '{loc}' -> Base: '{base}', Not standard format")
                
    except ImportError:
        print("Could not import rule engine for testing")

def environment_difference_analysis():
    """Analyze why production has 4,427 vs test 647 locations"""
    print(f"\n" + "=" * 50)
    print("ENVIRONMENT DIFFERENCE ANALYSIS")  
    print("=" * 50)
    
    print(f"TEST Environment: 647 locations")
    print(f"PRODUCTION Environment: 4,427 locations")
    print(f"Difference: {4427 - 647} = 3,780 additional locations")
    
    print(f"\nPossible causes:")
    print(f"1. Production has real warehouse data with more location variants")
    print(f"2. Production database has accumulated location prefixes (USER_, etc.)")
    print(f"3. Different database seeding/migration scripts")
    print(f"4. Multiple warehouses or customers in production")
    print(f"5. Location import from Excel files created duplicate entries")
    
    print(f"\nLocation prefix analysis shows:")
    print(f"- Test DB: No USER_ prefixes in sample")
    print(f"- Production debug: USER_ prefixes present") 
    print(f"- This suggests production data has user-specific location variants")

if __name__ == "__main__":
    detailed_pattern_analysis()
    environment_difference_analysis()