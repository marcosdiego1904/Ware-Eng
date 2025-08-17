#!/usr/bin/env python3
"""
Quick test for environment monitoring system
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_environment_monitoring():
    """Test the environment monitoring system"""
    
    print("=== TESTING ENVIRONMENT MONITORING ===")
    
    from environment_monitoring_system import EnvironmentMonitor
    
    # Initialize monitor
    monitor = EnvironmentMonitor(monitoring_interval=5)  # Short interval for testing
    
    # Test validation suite
    print("\nStep 1: Running validation suite...")
    validation_results = monitor.run_validation_suite()
    
    # Test monitoring capabilities (without starting the thread)
    print("\nStep 2: Testing monitoring capabilities...")
    
    # Test metric collection
    monitor._collect_system_metrics()
    monitor._collect_application_metrics()
    monitor._validate_environment_health()
    
    # Get status
    status = monitor.get_environment_status()
    
    print(f"Health Status: {status['health_status']['overall']}")
    print(f"Components Tested: {len(status['health_status']['components'])}")
    print(f"Metrics Collected: {len(status['recent_metrics'])}")
    
    # Test health report generation
    print("\nStep 3: Testing health report...")
    report = monitor.generate_health_report()
    
    success_rate = sum(validation_results.values()) / len(validation_results)
    
    return success_rate >= 0.6 and status['health_status']['overall'] != 'CRITICAL'

def main():
    """Run monitoring test"""
    
    print("ENVIRONMENT MONITORING TEST")
    print("=" * 35)
    
    success = test_environment_monitoring()
    
    print(f"\nTest Result: {'SUCCESS' if success else 'FAILED'}")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)