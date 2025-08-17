#!/usr/bin/env python3
"""
Test Phase 2 multi-tenant improvements
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_index_performance():
    """Test that new indexes improve query performance"""
    
    print("=== TESTING INDEX PERFORMANCE ===")
    
    from app import app, db
    from models import Location
    from sqlalchemy import text
    
    with app.app_context():
        # Test tenant-specific queries that should benefit from new indexes
        test_queries = [
            "SELECT COUNT(*) FROM location WHERE warehouse_id = 'USER_TESTF'",
            "SELECT COUNT(*) FROM location WHERE warehouse_id = 'USER_TESTF' AND is_active = 1",
            "SELECT zone, COUNT(*) FROM location WHERE warehouse_id = 'USER_TESTF' GROUP BY zone",
            "SELECT * FROM location WHERE warehouse_id = 'USER_TESTF' AND code = '01-01-001A' LIMIT 1"
        ]
        
        performance_results = []
        
        for query in test_queries:
            start_time = datetime.now()
            try:
                result = db.session.execute(text(query))
                if 'COUNT' in query.upper():
                    count = result.scalar()
                else:
                    rows = result.fetchall()
                    count = len(rows)
            except Exception as e:
                count = f"ERROR: {str(e)}"
            end_time = datetime.now()
            
            duration_ms = (end_time - start_time).total_seconds() * 1000
            performance_results.append((query[:50] + "...", duration_ms, count))
            
            status = "EXCELLENT" if duration_ms < 5 else "GOOD" if duration_ms < 20 else "SLOW"
            print(f"  Query: {query[:50]}...")
            print(f"  Time: {duration_ms:.1f}ms ({status}), Results: {count}")
            print()
        
        # Check if we have good performance across the board
        avg_time = sum(result[1] for result in performance_results) / len(performance_results)
        print(f"Average query time: {avg_time:.1f}ms")
        
        return avg_time < 10  # Target: under 10ms average

def test_enhanced_detection():
    """Test the enhanced warehouse detection with current system"""
    
    print("=== TESTING ENHANCED DETECTION ===")
    
    from app import app, db
    from rule_engine import RuleEngine
    
    with app.app_context():
        rule_engine = RuleEngine(db.session)
        
        # Test with same inventory from Phase 1
        test_locations = [
            '02-1-011B', '01-1-007B', '01-1-019A', '02-1-003B', 
            '01-1-004C', 'RECV-01', 'STAGE-01'
        ]
        
        test_df = pd.DataFrame({'location': test_locations})
        
        print(f"Testing detection with {len(test_locations)} locations...")
        
        # Run detection
        start_time = datetime.now()
        detection_result = rule_engine._detect_warehouse_context(test_df)
        end_time = datetime.now()
        
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        print(f"Detection completed in {duration_ms:.1f}ms")
        print(f"Result: {detection_result.get('warehouse_id', 'None')}")
        print(f"Confidence: {detection_result.get('confidence_level', 'NONE')}")
        print(f"Score: {detection_result.get('match_score', 0):.1%}")
        
        # Check if detection is working well
        success = (
            detection_result.get('warehouse_id') is not None and
            detection_result.get('confidence_level') in ['HIGH', 'VERY_HIGH'] and
            detection_result.get('match_score', 0) > 0.5 and
            duration_ms < 100  # Should be fast
        )
        
        return success

def main():
    """Test Phase 2 improvements"""
    
    print("PHASE 2 IMPROVEMENT VALIDATION")
    print("=" * 40)
    
    # Test index performance
    print("\\nTesting database index performance...")
    index_performance = test_index_performance()
    
    # Test enhanced detection
    print("\\nTesting enhanced warehouse detection...")
    detection_enhanced = test_enhanced_detection()
    
    # Summary
    print("\\n" + "=" * 40)
    print("PHASE 2 TEST RESULTS")
    print("=" * 40)
    print(f"Index Performance: {'PASS' if index_performance else 'FAIL'}")
    print(f"Enhanced Detection: {'PASS' if detection_enhanced else 'FAIL'}")
    
    overall_success = (index_performance and detection_enhanced)
    print(f"\\nOverall Phase 2 Status: {'SUCCESS' if overall_success else 'NEEDS WORK'}")
    
    if overall_success:
        print("\\nPHASE 2 VALIDATION SUCCESSFUL - Ready for Phase 3!")
    else:
        print("\\nPHASE 2 VALIDATION NEEDS ATTENTION")
    
    return overall_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)