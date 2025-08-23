"""
Optimized Logging Configuration for WareWise Backend

This module provides clean, configurable logging that eliminates verbose debug noise
while preserving essential debugging capabilities for production troubleshooting.
"""

import os
import logging
from typing import Dict, List, Optional, Set
from contextlib import contextmanager
from enum import Enum


class LogLevel(Enum):
    """Logging levels optimized for warehouse rule engine debugging"""
    SILENT = "SILENT"              # Only critical errors
    ESSENTIAL = "ESSENTIAL"        # Key business logic and results
    DIAGNOSTIC = "DIAGNOSTIC"      # Error details and performance metrics  
    VERBOSE = "VERBOSE"            # Full debug information
    FLOOD = "FLOOD"                # Everything (current state)


class LogCategory(Enum):
    """Log categories for fine-grained control"""
    RULE_ENGINE = "RULE_ENGINE"
    VIRTUAL_ENGINE = "VIRTUAL_ENGINE" 
    LOCATION_VALIDATION = "LOCATION_VALIDATION"
    PERFORMANCE = "PERFORMANCE"
    ERRORS = "ERRORS"
    API_REQUESTS = "API_REQUESTS"


class OptimizedLogger:
    """
    Smart logger that reduces noise while preserving debugging capability
    """
    
    def __init__(self, level: LogLevel = None, categories: Set[LogCategory] = None):
        # Get log level from environment or default to ESSENTIAL
        self.level = level or LogLevel(os.getenv('WARE_LOG_LEVEL', 'ESSENTIAL'))
        
        # Get enabled categories from environment
        env_categories = os.getenv('WARE_LOG_CATEGORIES', '').split(',')
        self.enabled_categories = categories or {
            LogCategory(cat.strip()) for cat in env_categories 
            if cat.strip() and cat.strip() in [c.value for c in LogCategory]
        } or {LogCategory.RULE_ENGINE, LogCategory.ERRORS, LogCategory.PERFORMANCE}
        
        # Error aggregation to prevent spam
        self.error_counts: Dict[str, int] = {}
        self.error_samples: Dict[str, str] = {}
        self.max_error_repeats = 5
        
        # Performance tracking
        self.rule_timings: List[Dict] = []
        
    def should_log(self, level: LogLevel, category: LogCategory) -> bool:
        """Determine if a log message should be output"""
        if category not in self.enabled_categories:
            return False
            
        level_hierarchy = {
            LogLevel.SILENT: 0,
            LogLevel.ESSENTIAL: 1, 
            LogLevel.DIAGNOSTIC: 2,
            LogLevel.VERBOSE: 3,
            LogLevel.FLOOD: 4
        }
        
        return level_hierarchy[level] <= level_hierarchy[self.level]
    
    def rule_start(self, rule_name: str, rule_id: int, priority: str):
        """Log rule evaluation start - essential information only"""
        if self.should_log(LogLevel.ESSENTIAL, LogCategory.RULE_ENGINE):
            print(f"[RULE_{rule_id}] {rule_name} ({priority}) - Starting...")
    
    def rule_complete(self, rule_name: str, rule_id: int, anomaly_count: int, 
                     execution_time_ms: int, success: bool = True):
        """Log rule completion with key metrics"""
        if self.should_log(LogLevel.ESSENTIAL, LogCategory.RULE_ENGINE):
            status = "✅" if success else "❌"
            print(f"[RULE_{rule_id}] {status} {rule_name}: {anomaly_count} anomalies ({execution_time_ms}ms)")
            
        # Track performance
        if self.should_log(LogLevel.DIAGNOSTIC, LogCategory.PERFORMANCE):
            self.rule_timings.append({
                'rule_id': rule_id,
                'rule_name': rule_name, 
                'execution_time_ms': execution_time_ms,
                'anomaly_count': anomaly_count,
                'success': success
            })
    
    def virtual_engine_error(self, location: str, error: str):
        """Log virtual engine errors with smart aggregation"""
        error_key = f"virtual_classification_{type(Exception(error)).__name__}"
        
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Only log first few instances, then summarize
        if self.error_counts[error_key] <= self.max_error_repeats:
            if self.should_log(LogLevel.DIAGNOSTIC, LogCategory.VIRTUAL_ENGINE):
                print(f"[VIRTUAL_ENGINE] ⚠️  Classification failed for '{location}': {error}")
            self.error_samples[error_key] = f"'{location}': {error}"
        elif self.error_counts[error_key] == self.max_error_repeats + 1:
            if self.should_log(LogLevel.DIAGNOSTIC, LogCategory.VIRTUAL_ENGINE):
                print(f"[VIRTUAL_ENGINE] 🔇 Suppressing further '{error_key}' errors (will summarize at end)")
    
    def location_validation_summary(self, total_locations: int, invalid_count: int, 
                                  validation_method: str):
        """Summary of location validation - no per-location spam"""
        if self.should_log(LogLevel.ESSENTIAL, LogCategory.LOCATION_VALIDATION):
            validity_rate = ((total_locations - invalid_count) / total_locations * 100) if total_locations > 0 else 0
            print(f"[LOCATION_VALIDATION] {validation_method}: {invalid_count}/{total_locations} invalid ({validity_rate:.1f}% valid)")
    
    def analysis_summary(self, total_rules: int, total_anomalies: int, 
                        total_execution_time_ms: int):
        """High-level analysis summary"""
        if self.should_log(LogLevel.ESSENTIAL, LogCategory.RULE_ENGINE):
            avg_time = total_execution_time_ms / total_rules if total_rules > 0 else 0
            print(f"[ANALYSIS_COMPLETE] {total_rules} rules → {total_anomalies} anomalies ({total_execution_time_ms}ms total, {avg_time:.0f}ms avg)")
    
    def performance_report(self):
        """Generate performance report if diagnostic logging enabled"""
        if not self.should_log(LogLevel.DIAGNOSTIC, LogCategory.PERFORMANCE):
            return
            
        if not self.rule_timings:
            return
            
        print("\n[PERFORMANCE_REPORT]")
        print("=" * 50)
        
        # Sort by execution time
        sorted_timings = sorted(self.rule_timings, key=lambda x: x['execution_time_ms'], reverse=True)
        
        for timing in sorted_timings[:5]:  # Top 5 slowest
            rate = timing['anomaly_count'] / (timing['execution_time_ms'] / 1000) if timing['execution_time_ms'] > 0 else 0
            print(f"  {timing['rule_name']}: {timing['execution_time_ms']}ms ({rate:.1f} anomalies/sec)")
        
        print("=" * 50)
    
    def error_summary(self):
        """Summarize suppressed errors"""
        if not self.should_log(LogLevel.DIAGNOSTIC, LogCategory.ERRORS):
            return
            
        if not self.error_counts:
            return
            
        print("\n[ERROR_SUMMARY]")
        print("-" * 30)
        
        for error_key, count in self.error_counts.items():
            if count > self.max_error_repeats:
                sample = self.error_samples.get(error_key, "No sample available")
                print(f"  {error_key}: {count} occurrences (sample: {sample})")
        
        print("-" * 30)
    
    def request_info(self, method: str, endpoint: str, user: str = None):
        """Log API request information"""
        if self.should_log(LogLevel.ESSENTIAL, LogCategory.API_REQUESTS):
            user_info = f" [{user}]" if user else ""
            print(f"[API] {method} {endpoint}{user_info}")
    
    @contextmanager
    def rule_context(self, rule_name: str, rule_id: int, priority: str):
        """Context manager for rule evaluation with automatic timing"""
        start_time = time.time()
        self.rule_start(rule_name, rule_id, priority)
        
        try:
            yield
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.rule_complete(rule_name, rule_id, 0, execution_time, success=False)
            if self.should_log(LogLevel.DIAGNOSTIC, LogCategory.ERRORS):
                print(f"[RULE_{rule_id}] ❌ FAILED: {e}")
            raise
    
    def cleanup(self):
        """Generate final reports and cleanup"""
        self.error_summary()
        self.performance_report()


# Global logger instance - can be imported and used throughout the application
logger = OptimizedLogger()


def configure_logging(level: str = None, categories: str = None):
    """
    Configure logging from environment variables or parameters
    
    Examples:
        configure_logging("DIAGNOSTIC", "RULE_ENGINE,PERFORMANCE") 
        configure_logging("ESSENTIAL", "")  # Only essential logs
        configure_logging("SILENT", "")     # Almost no logs
    """
    global logger
    
    if level:
        os.environ['WARE_LOG_LEVEL'] = level
    if categories:
        os.environ['WARE_LOG_CATEGORIES'] = categories
        
    logger = OptimizedLogger()


def get_logger() -> OptimizedLogger:
    """Get the global logger instance"""
    return logger


if __name__ == "__main__":
    # Test different logging levels
    import time
    
    print("Testing OptimizedLogger...")
    
    # Test ESSENTIAL level (default)
    print("\n=== ESSENTIAL Level ===")
    configure_logging("ESSENTIAL", "RULE_ENGINE,PERFORMANCE")
    test_logger = get_logger()
    
    test_logger.rule_start("Test Rule", 1, "HIGH")
    test_logger.virtual_engine_error("01-A-01-A", "'tuple' object has no attribute 'get'")
    test_logger.rule_complete("Test Rule", 1, 5, 150)
    
    # Test error aggregation
    print("\n=== Error Aggregation Test ===")
    for i in range(10):
        test_logger.virtual_engine_error(f"LOC-{i}", "'tuple' object has no attribute 'get'")
    
    test_logger.cleanup()