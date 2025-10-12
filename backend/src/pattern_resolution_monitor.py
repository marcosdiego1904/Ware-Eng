"""
Pattern Resolution Performance Monitor
Tracks and analyzes RulePatternResolver performance metrics for optimization and debugging.

This component provides:
1. Performance metrics collection for pattern resolution operations
2. Cache hit/miss ratio analysis
3. Template resolution timing and success rates
4. Pattern generation performance tracking
5. Automated performance alerts and recommendations
"""

import time
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Container for pattern resolution performance metrics"""
    operation: str
    warehouse_id: str
    rule_type: str
    start_time: float
    end_time: float
    success: bool
    cache_hit: bool
    template_source: str
    pattern_count: int
    error_message: Optional[str] = None

    @property
    def duration_ms(self) -> float:
        """Get operation duration in milliseconds"""
        return (self.end_time - self.start_time) * 1000

    @property
    def timestamp(self) -> datetime:
        """Get operation timestamp"""
        return datetime.fromtimestamp(self.start_time)


class PatternResolutionMonitor:
    """
    Performance monitoring system for RulePatternResolver operations.

    Tracks metrics, analyzes performance trends, and provides optimization insights.
    """

    def __init__(self, max_metrics_history: int = 10000):
        self.max_metrics_history = max_metrics_history

        # Thread-safe metrics storage
        self._lock = threading.Lock()
        self._metrics_history = deque(maxlen=max_metrics_history)

        # Performance counters
        self._counters = defaultdict(int)
        self._timing_stats = defaultdict(list)

        # Cache performance tracking
        self._cache_stats = {
            'pattern_cache_hits': 0,
            'pattern_cache_misses': 0,
            'template_cache_hits': 0,
            'template_cache_misses': 0,
            'cache_evictions': 0
        }

        # Template resolution tracking
        self._template_resolution_stats = defaultdict(lambda: {
            'success_count': 0,
            'failure_count': 0,
            'avg_duration_ms': 0.0,
            'max_duration_ms': 0.0
        })

        # Performance thresholds (configurable)
        self.thresholds = {
            'slow_operation_ms': 100,
            'very_slow_operation_ms': 500,
            'low_cache_hit_ratio': 0.7,
            'high_failure_rate': 0.1
        }

        logger.info("PatternResolutionMonitor initialized with performance tracking")

    def record_pattern_resolution(self, warehouse_id: str, rule_type: str,
                                start_time: float, end_time: float,
                                success: bool, cache_hit: bool = False,
                                template_source: str = "unknown",
                                pattern_count: int = 0,
                                error_message: str = None):
        """Record a pattern resolution operation"""
        metric = PerformanceMetric(
            operation="pattern_resolution",
            warehouse_id=warehouse_id,
            rule_type=rule_type,
            start_time=start_time,
            end_time=end_time,
            success=success,
            cache_hit=cache_hit,
            template_source=template_source,
            pattern_count=pattern_count,
            error_message=error_message
        )

        with self._lock:
            self._metrics_history.append(metric)

            # Update counters
            self._counters['total_operations'] += 1
            if success:
                self._counters['successful_operations'] += 1
            else:
                self._counters['failed_operations'] += 1

            if cache_hit:
                self._cache_stats['pattern_cache_hits'] += 1
            else:
                self._cache_stats['pattern_cache_misses'] += 1

            # Track timing stats
            duration_ms = metric.duration_ms
            self._timing_stats[f"{warehouse_id}:{rule_type}"].append(duration_ms)

            # Update template resolution stats
            template_stats = self._template_resolution_stats[template_source]
            if success:
                template_stats['success_count'] += 1
            else:
                template_stats['failure_count'] += 1

            # Update average duration
            total_ops = template_stats['success_count'] + template_stats['failure_count']
            old_avg = template_stats['avg_duration_ms']
            template_stats['avg_duration_ms'] = (old_avg * (total_ops - 1) + duration_ms) / total_ops
            template_stats['max_duration_ms'] = max(template_stats['max_duration_ms'], duration_ms)

        # Check for performance issues
        self._check_performance_thresholds(metric)

    def record_cache_operation(self, operation_type: str, hit: bool = True):
        """Record cache hit/miss operations"""
        with self._lock:
            if operation_type == 'pattern_cache':
                if hit:
                    self._cache_stats['pattern_cache_hits'] += 1
                else:
                    self._cache_stats['pattern_cache_misses'] += 1
            elif operation_type == 'template_cache':
                if hit:
                    self._cache_stats['template_cache_hits'] += 1
                else:
                    self._cache_stats['template_cache_misses'] += 1
            elif operation_type == 'cache_eviction':
                self._cache_stats['cache_evictions'] += 1

    def get_performance_summary(self, time_window_hours: int = 1) -> Dict[str, Any]:
        """Get performance summary for specified time window"""
        cutoff_time = time.time() - (time_window_hours * 3600)

        with self._lock:
            # Filter metrics by time window
            recent_metrics = [m for m in self._metrics_history if m.start_time >= cutoff_time]

            if not recent_metrics:
                return {
                    'time_window_hours': time_window_hours,
                    'total_operations': 0,
                    'message': 'No operations in time window'
                }

            # Calculate summary statistics
            total_ops = len(recent_metrics)
            successful_ops = sum(1 for m in recent_metrics if m.success)
            cache_hits = sum(1 for m in recent_metrics if m.cache_hit)

            durations = [m.duration_ms for m in recent_metrics]
            avg_duration = sum(durations) / len(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            min_duration = min(durations) if durations else 0

            # Template source breakdown
            template_sources = defaultdict(int)
            for m in recent_metrics:
                template_sources[m.template_source] += 1

            # Warehouse performance breakdown
            warehouse_stats = defaultdict(lambda: {'count': 0, 'avg_duration': 0, 'failures': 0})
            for m in recent_metrics:
                ws = warehouse_stats[m.warehouse_id]
                ws['count'] += 1
                ws['avg_duration'] = (ws['avg_duration'] * (ws['count'] - 1) + m.duration_ms) / ws['count']
                if not m.success:
                    ws['failures'] += 1

            return {
                'time_window_hours': time_window_hours,
                'summary': {
                    'total_operations': total_ops,
                    'successful_operations': successful_ops,
                    'success_rate': successful_ops / total_ops if total_ops > 0 else 0,
                    'cache_hit_rate': cache_hits / total_ops if total_ops > 0 else 0,
                    'avg_duration_ms': round(avg_duration, 2),
                    'max_duration_ms': round(max_duration, 2),
                    'min_duration_ms': round(min_duration, 2)
                },
                'cache_performance': dict(self._cache_stats),
                'template_sources': dict(template_sources),
                'warehouse_performance': {
                    wid: {
                        'operations': stats['count'],
                        'avg_duration_ms': round(stats['avg_duration'], 2),
                        'failure_rate': stats['failures'] / stats['count'] if stats['count'] > 0 else 0
                    }
                    for wid, stats in warehouse_stats.items()
                },
                'performance_alerts': self._generate_performance_alerts(recent_metrics)
            }

    def get_detailed_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get detailed metrics for analysis"""
        with self._lock:
            recent_metrics = list(self._metrics_history)[-limit:]
            return [asdict(metric) for metric in recent_metrics]

    def _check_performance_thresholds(self, metric: PerformanceMetric):
        """Check metric against performance thresholds and log warnings"""
        duration_ms = metric.duration_ms

        if duration_ms > self.thresholds['very_slow_operation_ms']:
            logger.warning(
                f"Very slow pattern resolution: {duration_ms:.2f}ms for "
                f"{metric.warehouse_id}:{metric.rule_type} (template: {metric.template_source})"
            )
        elif duration_ms > self.thresholds['slow_operation_ms']:
            logger.info(
                f"Slow pattern resolution: {duration_ms:.2f}ms for "
                f"{metric.warehouse_id}:{metric.rule_type}"
            )

    def _generate_performance_alerts(self, metrics: List[PerformanceMetric]) -> List[str]:
        """Generate performance alerts based on recent metrics"""
        alerts = []

        if not metrics:
            return alerts

        # Check overall success rate
        success_rate = sum(1 for m in metrics if m.success) / len(metrics)
        if success_rate < (1 - self.thresholds['high_failure_rate']):
            alerts.append(f"High failure rate: {(1-success_rate)*100:.1f}% of operations failed")

        # Check cache hit rate
        cache_hit_rate = sum(1 for m in metrics if m.cache_hit) / len(metrics)
        if cache_hit_rate < self.thresholds['low_cache_hit_ratio']:
            alerts.append(f"Low cache hit rate: {cache_hit_rate*100:.1f}% (threshold: {self.thresholds['low_cache_hit_ratio']*100:.1f}%)")

        # Check for very slow operations
        slow_ops = [m for m in metrics if m.duration_ms > self.thresholds['very_slow_operation_ms']]
        if len(slow_ops) > len(metrics) * 0.05:  # More than 5% very slow
            alerts.append(f"{len(slow_ops)} very slow operations detected (>{self.thresholds['very_slow_operation_ms']}ms)")

        # Check for template resolution issues
        template_failures = defaultdict(int)
        template_counts = defaultdict(int)

        for m in metrics:
            template_counts[m.template_source] += 1
            if not m.success:
                template_failures[m.template_source] += 1

        for template_source, failure_count in template_failures.items():
            failure_rate = failure_count / template_counts[template_source]
            if failure_rate > self.thresholds['high_failure_rate']:
                alerts.append(
                    f"High failure rate for {template_source}: {failure_rate*100:.1f}% "
                    f"({failure_count}/{template_counts[template_source]} operations)"
                )

        return alerts

    def reset_metrics(self):
        """Reset all performance metrics (use with caution)"""
        with self._lock:
            self._metrics_history.clear()
            self._counters.clear()
            self._timing_stats.clear()
            self._cache_stats = {
                'pattern_cache_hits': 0,
                'pattern_cache_misses': 0,
                'template_cache_hits': 0,
                'template_cache_misses': 0,
                'cache_evictions': 0
            }
            self._template_resolution_stats.clear()

        logger.info("Performance metrics reset")

    def export_metrics_to_json(self, filepath: str, limit: int = 1000):
        """Export recent metrics to JSON file for analysis"""
        try:
            metrics_data = {
                'export_timestamp': datetime.now().isoformat(),
                'summary': self.get_performance_summary(time_window_hours=24),
                'detailed_metrics': self.get_detailed_metrics(limit=limit)
            }

            with open(filepath, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)

            logger.info(f"Metrics exported to {filepath}")

        except Exception as e:
            logger.error(f"Failed to export metrics to {filepath}: {e}")


# Global monitor instance
_global_monitor = None

def get_pattern_resolution_monitor() -> PatternResolutionMonitor:
    """Get global pattern resolution monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PatternResolutionMonitor()
    return _global_monitor


class PerformanceTimer:
    """Context manager for timing pattern resolution operations"""

    def __init__(self, warehouse_id: str, rule_type: str, monitor: PatternResolutionMonitor = None):
        self.warehouse_id = warehouse_id
        self.rule_type = rule_type
        self.monitor = monitor or get_pattern_resolution_monitor()
        self.start_time = None
        self.template_source = "unknown"
        self.pattern_count = 0
        self.cache_hit = False
        self.error_message = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        success = exc_type is None

        if exc_val:
            self.error_message = str(exc_val)

        self.monitor.record_pattern_resolution(
            warehouse_id=self.warehouse_id,
            rule_type=self.rule_type,
            start_time=self.start_time,
            end_time=end_time,
            success=success,
            cache_hit=self.cache_hit,
            template_source=self.template_source,
            pattern_count=self.pattern_count,
            error_message=self.error_message
        )

    def set_template_source(self, template_source: str):
        """Set the template source for this operation"""
        self.template_source = template_source
        return self

    def set_pattern_count(self, pattern_count: int):
        """Set the number of patterns generated"""
        self.pattern_count = pattern_count
        return self

    def set_cache_hit(self, cache_hit: bool):
        """Set whether this was a cache hit"""
        self.cache_hit = cache_hit
        return self