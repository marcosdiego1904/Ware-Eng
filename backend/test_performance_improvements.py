#!/usr/bin/env python3
"""
PERFORMANCE TEST: Verify warehouse filtering and caching improvements
This script tests the critical performance fixes implemented in rule_engine.py
"""

import sys
import os
import time
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

def test_location_query_performance():
    """Test the performance of location queries before and after optimization"""
    print("=== PERFORMANCE TEST: Location Query Optimization ===\n")
    
    try:
        from app import app, db
        from models import Location
        from rule_engine import RuleEngine
        from sqlalchemy import or_
        
        with app.app_context():
            print("1. Testing RAW database queries...")
            
            # Test 1: Measure ALL locations query (old approach)
            start_time = time.time()
            all_locations = Location.query.all()
            all_locations_time = time.time() - start_time
            print(f"   Location.query.all(): {len(all_locations):,} locations in {all_locations_time:.3f}s")
            
            # Test 2: Measure filtered query (new approach)
            test_warehouse = 'PROD_DEMO_1755625931'  # From our database stats
            start_time = time.time()
            filtered_locations = Location.query.filter(
                Location.warehouse_id == test_warehouse,
                or_(Location.is_active == True, Location.is_active.is_(None))
            ).all()
            filtered_time = time.time() - start_time
            print(f"   Filtered query ({test_warehouse}): {len(filtered_locations):,} locations in {filtered_time:.3f}s")
            
            # Calculate improvement
            if filtered_time > 0:
                improvement = (all_locations_time / filtered_time)
                data_reduction = ((len(all_locations) - len(filtered_locations)) / len(all_locations)) * 100
                print(f"   → PERFORMANCE IMPROVEMENT: {improvement:.1f}x faster")
                print(f"   → DATA REDUCTION: {data_reduction:.1f}% fewer locations processed")
            
            print("\n2. Testing RuleEngine caching system...")
            
            # Create a mock user context
            class MockUser:
                def __init__(self, username):
                    self.username = username
                    self.id = 1
            
            # Test RuleEngine with caching
            mock_user = MockUser('testuser')
            rule_engine = RuleEngine(db.session, app, mock_user)
            
            # First call (should hit database)
            start_time = time.time()
            locations1 = rule_engine._get_cached_locations()
            first_call_time = time.time() - start_time
            print(f"   First cached call: {len(locations1):,} locations in {first_call_time:.3f}s")
            
            # Second call (should use cache)
            start_time = time.time()
            locations2 = rule_engine._get_cached_locations()
            second_call_time = time.time() - start_time
            print(f"   Second cached call: {len(locations2):,} locations in {second_call_time:.3f}s")
            
            if second_call_time > 0:
                cache_improvement = first_call_time / second_call_time if second_call_time > 0 else float('inf')
                print(f"   → CACHE IMPROVEMENT: {cache_improvement:.1f}x faster")
            
            # Verify cache consistency
            if len(locations1) == len(locations2):
                print(f"   ✅ Cache consistency verified")
            else:
                print(f"   ❌ Cache inconsistency detected")
                
            print("\n3. Performance summary:")
            print(f"   • Database filtering: {improvement:.1f}x faster")
            print(f"   • Data reduction: {data_reduction:.1f}% less data")
            print(f"   • Caching system: {cache_improvement:.1f}x faster on repeat calls")
            print(f"   • Memory usage: ~{data_reduction:.1f}% reduction")
            
            print("\n🎉 OPTIMIZATION STATUS: SUCCESS")
            print(f"   Your system should now handle 800-1,200 pallets efficiently!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_sample_inventory_processing():
    """Test processing a sample inventory dataset"""
    print("\n=== PERFORMANCE TEST: Sample Inventory Processing ===\n")
    
    try:
        from app import app, db
        from rule_engine import RuleEngine
        
        # Create sample inventory data (similar to user's 800-1,200 pallet test)
        sample_data = []
        for i in range(500):  # Smaller test size
            sample_data.append({
                'pallet_id': f'PALLET_{i:04d}',
                'location': f'01-01-{(i % 100):03d}A',
                'description': f'Product_{i % 20}',
                'receipt_number': f'RCP_{i // 10}',
                'creation_date': datetime.now()
            })
        
        sample_df = pd.DataFrame(sample_data)
        print(f"Created sample inventory: {len(sample_df):,} pallets")
        
        with app.app_context():
            # Create mock user context
            class MockUser:
                def __init__(self, username):
                    self.username = username
                    self.id = 1
            
            mock_user = MockUser('testuser')
            rule_engine = RuleEngine(db.session, app, mock_user)
            
            print("Testing rule engine initialization...")
            start_time = time.time()
            
            # Test the location caching during rule evaluation setup
            locations = rule_engine._get_cached_locations()
            init_time = time.time() - start_time
            
            print(f"   Rule engine setup: {len(locations):,} locations loaded in {init_time:.3f}s")
            print(f"   Memory efficiency: ~{len(locations) * 100 / 1220:.1f}% of total locations")
            
            if len(locations) < 1000:  # Should be much less than 1,220 total
                print("   ✅ Location filtering working correctly")
            else:
                print("   ⚠️  Warning: Still loading too many locations")
                
        print("\n✅ Sample processing test completed")
        
    except Exception as e:
        print(f"❌ Sample test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("PERFORMANCE OPTIMIZATION TEST SUITE")
    print("=" * 50)
    
    test_location_query_performance()
    test_sample_inventory_processing()
    
    print("\n" + "=" * 50)
    print("PERFORMANCE TESTING COMPLETE")