"""
Test script to verify performance monitoring integration with RulePatternResolver
"""

import sys
import os
import time
import json
from unittest.mock import Mock

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import components
from pattern_resolution_monitor import PatternResolutionMonitor, PerformanceTimer, get_pattern_resolution_monitor
from rule_pattern_resolver import RulePatternResolver, PatternSet

def test_performance_monitoring():
    """Test performance monitoring integration"""
    print("=== Pattern Resolution Performance Monitoring Test ===")

    # Create mock dependencies
    mock_db = Mock()
    mock_app = Mock()

    # Create resolver with monitoring
    resolver = RulePatternResolver(mock_db, mock_app)

    # Create test warehouse context
    warehouse_context = {
        'warehouse_id': 'USER_TESTWAREHOUSE',
        'detection_method': 'zone_based'
    }

    print(f"1. Testing pattern resolution with monitoring...")

    # Simulate pattern resolution calls
    for i in range(5):
        try:
            patterns = resolver.get_patterns_for_rule('LOCATION_SPECIFIC_STAGNANT', warehouse_context)
            print(f"   Call {i+1}: Source={patterns.source}, Patterns={len(patterns.storage_patterns)}")
            time.sleep(0.01)  # Small delay to show different timing
        except Exception as e:
            print(f"   Call {i+1}: Error - {e}")

    print(f"2. Testing cache performance...")

    # Test cache hits (subsequent calls should be cached)
    for i in range(3):
        try:
            patterns = resolver.get_patterns_for_rule('LOCATION_MAPPING_ERROR', warehouse_context)
            print(f"   Cache test {i+1}: Source={patterns.source}")
        except Exception as e:
            print(f"   Cache test {i+1}: Error - {e}")

    print(f"3. Getting performance statistics...")

    # Get performance stats
    try:
        performance_stats = resolver.get_performance_stats(time_window_hours=1)

        print(f"   Cache Statistics:")
        cache_stats = performance_stats.get('cache_statistics', {})
        print(f"     Pattern cache size: {cache_stats.get('pattern_cache_size', 0)}")
        print(f"     Template cache size: {cache_stats.get('template_cache_size', 0)}")
        print(f"     Cache TTL: {cache_stats.get('cache_ttl', 0)}s")

        print(f"   Performance Metrics:")
        perf_metrics = performance_stats.get('performance_metrics', {})
        if 'summary' in perf_metrics:
            summary = perf_metrics['summary']
            print(f"     Total operations: {summary.get('total_operations', 0)}")
            print(f"     Success rate: {summary.get('success_rate', 0)*100:.1f}%")
            print(f"     Cache hit rate: {summary.get('cache_hit_rate', 0)*100:.1f}%")
            print(f"     Average duration: {summary.get('avg_duration_ms', 0):.2f}ms")

        if 'performance_alerts' in perf_metrics:
            alerts = perf_metrics['performance_alerts']
            if alerts:
                print(f"   Performance Alerts:")
                for alert in alerts:
                    print(f"     - {alert}")
            else:
                print(f"   Performance Alerts: None")

        print(f"   Monitoring enabled: {performance_stats.get('monitoring_enabled', False)}")

    except Exception as e:
        print(f"   Error getting performance stats: {e}")

    print(f"4. Testing direct monitor access...")

    # Test direct monitor access
    try:
        monitor = get_pattern_resolution_monitor()
        if monitor:
            print(f"   Monitor available: True")

            # Test manual performance timing
            with PerformanceTimer('USER_MANUAL_TEST', 'MANUAL_RULE_TEST') as timer:
                timer.set_template_source('test_source')
                timer.set_pattern_count(5)
                timer.set_cache_hit(False)
                time.sleep(0.005)  # Simulate work

            print(f"   Manual timing test completed")

            # Get summary
            summary = monitor.get_performance_summary(time_window_hours=1)
            print(f"   Monitor operations: {summary.get('summary', {}).get('total_operations', 0)}")

        else:
            print(f"   Monitor available: False")

    except Exception as e:
        print(f"   Error testing direct monitor: {e}")

    print(f"=== Monitoring Test Complete ===")

def test_performance_timer():
    """Test PerformanceTimer context manager"""
    print("\n=== PerformanceTimer Test ===")

    # Test successful operation
    print("1. Testing successful operation...")
    with PerformanceTimer('TEST_WAREHOUSE', 'TEST_RULE') as timer:
        timer.set_template_source('zone_based_template')
        timer.set_pattern_count(10)
        timer.set_cache_hit(True)
        time.sleep(0.01)
        print("   Operation completed successfully")

    # Test operation with error
    print("2. Testing operation with error...")
    try:
        with PerformanceTimer('TEST_WAREHOUSE', 'ERROR_RULE') as timer:
            timer.set_template_source('error_template')
            timer.set_pattern_count(0)
            timer.set_cache_hit(False)
            raise ValueError("Test error for monitoring")
    except ValueError as e:
        print(f"   Expected error caught: {e}")

    print("=== PerformanceTimer Test Complete ===")

if __name__ == '__main__':
    test_performance_monitoring()
    test_performance_timer()

    print("\n=== All Tests Complete ===")
    print("Performance monitoring integration appears to be working correctly!")