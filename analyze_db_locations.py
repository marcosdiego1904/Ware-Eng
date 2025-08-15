#!/usr/bin/env python3
"""
Analyze database location formats and compare with Excel formats
"""
import sys
import os

# Add the backend src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

try:
    from app import app, db
    from models import Location
    from sqlalchemy import text
    
    def analyze_database_locations():
        """Analyze location formats in the database"""
        print("Analyzing Database Locations")
        print("=" * 40)
        
        with app.app_context():
            # Get total count
            total_locations = Location.query.count()
            print(f"Total locations in database: {total_locations}")
            
            # Get active locations 
            active_locations = Location.query.filter(
                (Location.is_active == True) | (Location.is_active.is_(None))
            ).all()
            print(f"Active locations: {len(active_locations)}")
            
            # Sample location codes
            print(f"\nSample location codes (first 20):")
            for i, location in enumerate(active_locations[:20]):
                print(f"  {i+1:2d}. '{location.code}' (Type: {location.location_type}, Zone: {location.zone})")
            
            # Analyze location patterns
            location_codes = [loc.code for loc in active_locations]
            
            # Analyze formats
            formats = {
                'with_dashes': 0,
                'with_underscores': 0,
                'with_letters': 0,
                'with_numbers': 0,
                'with_user_prefix': 0,
                'with_other_prefix': 0
            }
            
            prefix_patterns = set()
            lengths = {}
            
            for code in location_codes:
                code_str = str(code)
                length = len(code_str)
                lengths[length] = lengths.get(length, 0) + 1
                
                if '-' in code_str:
                    formats['with_dashes'] += 1
                if '_' in code_str:
                    formats['with_underscores'] += 1
                if any(c.isalpha() for c in code_str):
                    formats['with_letters'] += 1
                if any(c.isdigit() for c in code_str):
                    formats['with_numbers'] += 1
                    
                # Check for prefixes
                if '_' in code_str:
                    prefix = code_str.split('_')[0]
                    prefix_patterns.add(prefix)
                    if prefix == 'USER':
                        formats['with_user_prefix'] += 1
                    else:
                        formats['with_other_prefix'] += 1
            
            print(f"\nDatabase location lengths: {dict(sorted(lengths.items()))}")
            print(f"Database format analysis: {formats}")
            
            if prefix_patterns:
                print(f"Database prefix patterns: {sorted(prefix_patterns)}")
            
            # Show examples by category
            print(f"\nDatabase Format Examples:")
            
            # With USER prefix
            user_examples = [code for code in location_codes if code.startswith('USER_')][:5]
            if user_examples:
                print(f"With USER prefix: {user_examples}")
            
            # Without prefixes  
            no_prefix_examples = [code for code in location_codes if not '_' in code][:5]
            if no_prefix_examples:
                print(f"Without prefixes: {no_prefix_examples}")
            
            # Location types breakdown
            print(f"\nLocation Types Breakdown:")
            type_counts = {}
            for loc in active_locations:
                loc_type = loc.location_type
                type_counts[loc_type] = type_counts.get(loc_type, 0) + 1
            
            for loc_type, count in sorted(type_counts.items()):
                print(f"  {loc_type}: {count}")
            
            # Zone breakdown
            print(f"\nZone Breakdown:")
            zone_counts = {}
            for loc in active_locations:
                zone = loc.zone or 'None'
                zone_counts[zone] = zone_counts.get(zone, 0) + 1
            
            for zone, count in sorted(zone_counts.items()):
                print(f"  {zone}: {count}")
                
    def test_location_extraction():
        """Test location extraction methods"""
        print("\n" + "=" * 40)
        print("Testing Location Extraction Methods")
        print("=" * 40)
        
        # Sample Excel locations from our analysis
        excel_locations = [
            '02-06-03A',    # Failing format from debug
            '04-04-06B',    # Failing format from debug  
            '03-05-03B',    # Failing format from debug
            '01-02-002A',   # Working format from Excel
            'RCV-001',      # Receiving format
            'USER_01-01-001A'  # User prefix format
        ]
        
        # Sample DB locations
        db_locations = [
            'USER_01-02-021A_1',
            '02-01-006C',
            '02-02-041B', 
            'USER_02-01-027C_2',
            '05-05-002A'
        ]
        
        print(f"Excel locations to test: {excel_locations}")
        print(f"DB locations for comparison: {db_locations[:3]}")
        
        # Import rule engine methods
        from rule_engine import BaseRuleEvaluator
        evaluator = BaseRuleEvaluator()
        
        print(f"\nTesting _extract_base_location_code method:")
        for loc in excel_locations + db_locations:
            base_code = evaluator._extract_base_location_code(loc)
            print(f"  '{loc}' -> '{base_code}'")
            
        print(f"\nTesting _normalize_location_code method:")
        for loc in excel_locations + db_locations:
            normalized = evaluator._normalize_location_code(loc)
            print(f"  '{loc}' -> '{normalized}'")
    
    if __name__ == "__main__":
        analyze_database_locations()
        test_location_extraction()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root and backend dependencies are installed")
except Exception as e:
    print(f"Error: {e}")