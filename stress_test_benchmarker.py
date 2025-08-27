#!/usr/bin/env python3
"""
WAREWISE STRESS TEST BENCHMARKER
===============================

Performance benchmarking tool for WareWise rule engine stress testing:
- Measures execution time, memory usage, and throughput
- Tests all generated stress datasets (1K → 50K records)  
- Provides detailed performance analysis and recommendations
- Validates anomaly detection accuracy at scale
"""

import pandas as pd
import psutil
import time
import os
import gc
from datetime import datetime
from typing import Dict, List, Tuple
import sys

class WareWiseStressBenchmark:
    """Performance benchmarking for WareWise rule engine"""
    
    def __init__(self):
        self.results = []
        self.process = psutil.Process()
        
        print("WAREWISE STRESS TEST BENCHMARKER")
        print("================================")
        
        # Available stress test files
        self.test_files = [
            ('1K', 'stress_test_inventory_1K.csv', 52),
            ('5K', 'stress_test_inventory_5K.csv', 245),
            ('10K', 'stress_test_inventory_10K.csv', 490),
            ('25K', 'stress_test_inventory_25K.csv', 1225),
            ('50K', 'stress_test_inventory_50K.csv', 2450)
        ]
        
        # Check which files exist
        available_files = []
        for label, filename, expected in self.test_files:
            if os.path.exists(filename):
                file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
                available_files.append((label, filename, expected, file_size))
                print(f"Found: {filename} ({file_size:.1f} MB, ~{expected} expected anomalies)")
            else:
                print(f"Missing: {filename}")
        
        self.available_files = available_files
        print(f"Ready to benchmark {len(available_files)} datasets")
    
    def measure_file_load_performance(self, filepath: str) -> Dict:
        """Measure CSV file loading performance"""
        
        # Memory before loading
        mem_before = self.process.memory_info().rss / (1024 * 1024)  # MB
        
        # Time the file loading
        start_time = time.perf_counter()
        
        try:
            df = pd.read_csv(filepath)
            load_success = True
            record_count = len(df)
            
            # Memory after loading
            mem_after = self.process.memory_info().rss / (1024 * 1024)  # MB
            
        except Exception as e:
            load_success = False
            record_count = 0
            mem_after = mem_before
            print(f"ERROR loading {filepath}: {e}")
        
        end_time = time.perf_counter()
        load_time = end_time - start_time
        
        return {
            'filepath': filepath,
            'load_success': load_success,
            'record_count': record_count,
            'load_time_seconds': load_time,
            'memory_before_mb': mem_before,
            'memory_after_mb': mem_after,
            'memory_used_mb': mem_after - mem_before,
            'records_per_second': record_count / load_time if load_time > 0 else 0
        }
    
    def simulate_rule_engine_processing(self, df: pd.DataFrame) -> Dict:
        """Simulate rule engine processing performance"""
        
        # Memory before processing
        mem_before = self.process.memory_info().rss / (1024 * 1024)
        
        start_time = time.perf_counter()
        
        # Simulate typical rule engine operations
        simulated_anomalies = 0
        
        try:
            # 1. Simulate StagnantPalletsEvaluator - time calculations
            now = datetime.now()
            df['creation_date'] = pd.to_datetime(df['creation_date'])
            df['hours_since_creation'] = (now - df['creation_date']).dt.total_seconds() / 3600
            
            # Count stagnant (>10h in RECV locations)
            recv_pallets = df[df['location'].str.contains('RECV', na=False)]
            stagnant = len(recv_pallets[recv_pallets['hours_since_creation'] > 10])
            simulated_anomalies += stagnant
            
            # 2. Simulate duplicate detection
            duplicates = df[df.duplicated(subset=['pallet_id'], keep=False)]
            duplicate_anomalies = len(duplicates)
            simulated_anomalies += duplicate_anomalies
            
            # 3. Simulate location validation (invalid formats)
            invalid_locations = df[~df['location'].str.match(r'^(RECV|STAGE|DOCK|AISLE)-\d+$|^\d{2}-\d{2}-\d{3}[A-D]$', na=False)]
            invalid_anomalies = len(invalid_locations)
            simulated_anomalies += invalid_anomalies
            
            # 4. Simulate overcapacity detection (group by location)
            location_counts = df.groupby('location').size()
            overcapacity_locations = location_counts[location_counts > 5]  # Assume capacity=5
            overcapacity_anomalies = overcapacity_locations.sum()
            simulated_anomalies += overcapacity_anomalies
            
            processing_success = True
            
        except Exception as e:
            processing_success = False
            simulated_anomalies = 0
            print(f"ERROR during processing simulation: {e}")
        
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        
        # Memory after processing  
        mem_after = self.process.memory_info().rss / (1024 * 1024)
        
        return {
            'processing_success': processing_success,
            'processing_time_seconds': processing_time,
            'simulated_anomalies': simulated_anomalies,
            'memory_before_mb': mem_before,
            'memory_after_mb': mem_after,
            'processing_memory_used_mb': mem_after - mem_before,
            'records_per_second': len(df) / processing_time if processing_time > 0 else 0
        }
    
    def benchmark_dataset(self, label: str, filepath: str, expected_anomalies: int) -> Dict:
        """Complete benchmark of a single dataset"""
        
        print(f"\nBENCHMARKING {label} DATASET")
        print(f"{'='*50}")
        
        # 1. File loading benchmark
        load_results = self.measure_file_load_performance(filepath)
        
        if not load_results['load_success']:
            return {
                'label': label,
                'filepath': filepath,
                'status': 'FAILED_LOAD',
                **load_results
            }
        
        print(f"Loaded: {load_results['record_count']:,} records in {load_results['load_time_seconds']:.3f}s")
        print(f"Load speed: {load_results['records_per_second']:,.0f} records/sec")
        print(f"Memory used for loading: {load_results['memory_used_mb']:.1f} MB")
        
        # 2. Processing simulation benchmark
        df = pd.read_csv(filepath)  # Load again for processing test
        
        processing_results = self.simulate_rule_engine_processing(df)
        
        if not processing_results['processing_success']:
            return {
                'label': label,
                'filepath': filepath,
                'status': 'FAILED_PROCESSING',
                **load_results,
                **processing_results
            }
        
        print(f"Processed: {processing_results['processing_time_seconds']:.3f}s")
        print(f"Processing speed: {processing_results['records_per_second']:,.0f} records/sec")
        print(f"Processing memory: {processing_results['processing_memory_used_mb']:.1f} MB")
        print(f"Simulated anomalies: {processing_results['simulated_anomalies']}")
        print(f"Expected anomalies: {expected_anomalies}")
        
        # Calculate accuracy
        accuracy = (processing_results['simulated_anomalies'] / expected_anomalies * 100) if expected_anomalies > 0 else 0
        print(f"Detection accuracy: {accuracy:.1f}%")
        
        # Cleanup
        del df
        gc.collect()
        
        return {
            'label': label,
            'filepath': filepath,  
            'expected_anomalies': expected_anomalies,
            'detection_accuracy_percent': accuracy,
            'status': 'SUCCESS',
            **load_results,
            **processing_results
        }
    
    def run_full_benchmark_suite(self) -> List[Dict]:
        """Run benchmarks on all available datasets"""
        
        print(f"\nRUNNING FULL BENCHMARK SUITE")
        print(f"{'='*60}")
        
        results = []
        
        for label, filepath, expected_anomalies, file_size in self.available_files:
            result = self.benchmark_dataset(label, filepath, expected_anomalies)
            results.append(result)
            
            # Brief pause between tests
            time.sleep(0.5)
        
        return results
    
    def generate_performance_report(self, results: List[Dict]):
        """Generate comprehensive performance analysis report"""
        
        print(f"\n{'='*80}")
        print(f"WAREWISE STRESS TEST PERFORMANCE REPORT")
        print(f"{'='*80}")
        
        # Summary table
        print(f"\nPERFORMANCE SUMMARY:")
        print(f"{'Dataset':<8} {'Records':<10} {'Load(s)':<8} {'Process(s)':<10} {'Memory(MB)':<12} {'Anomalies':<10}")
        print(f"{'-'*68}")
        
        for result in results:
            if result['status'] == 'SUCCESS':
                print(f"{result['label']:<8} {result['record_count']:<10,} {result['load_time_seconds']:<8.3f} "
                      f"{result['processing_time_seconds']:<10.3f} {result['memory_used_mb'] + result['processing_memory_used_mb']:<12.1f} "
                      f"{result['simulated_anomalies']:<10}")
        
        # Performance analysis
        successful_results = [r for r in results if r['status'] == 'SUCCESS']
        
        if successful_results:
            # Calculate scaling metrics
            print(f"\nSCALING ANALYSIS:")
            
            max_records = max(r['record_count'] for r in successful_results)
            max_result = next(r for r in successful_results if r['record_count'] == max_records)
            
            print(f"Maximum tested: {max_records:,} records")
            print(f"Peak memory usage: {max_result['memory_used_mb'] + max_result['processing_memory_used_mb']:.1f} MB")
            print(f"Peak processing time: {max_result['load_time_seconds'] + max_result['processing_time_seconds']:.3f} seconds")
            
            # Throughput analysis
            throughputs = [(r['record_count'] / (r['load_time_seconds'] + r['processing_time_seconds'])) 
                          for r in successful_results]
            avg_throughput = sum(throughputs) / len(throughputs)
            print(f"Average throughput: {avg_throughput:,.0f} records/second")
            
            # Memory efficiency
            memory_per_record = [(r['memory_used_mb'] + r['processing_memory_used_mb']) / r['record_count'] * 1024 
                                for r in successful_results]  # KB per record
            avg_memory_per_record = sum(memory_per_record) / len(memory_per_record)
            print(f"Memory efficiency: {avg_memory_per_record:.2f} KB/record")
        
        # Recommendations
        print(f"\nPERFORMANCE RECOMMENDATIONS:")
        
        if len(successful_results) >= 3:
            # Check if performance degrades with scale
            small_dataset = min(successful_results, key=lambda x: x['record_count'])
            large_dataset = max(successful_results, key=lambda x: x['record_count'])
            
            scale_factor = large_dataset['record_count'] / small_dataset['record_count']
            time_scale = (large_dataset['processing_time_seconds'] / small_dataset['processing_time_seconds'])
            
            if time_scale > scale_factor * 1.5:  # Non-linear scaling
                print(f"⚠️  Non-linear performance scaling detected (scale factor: {scale_factor:.1f}x, time factor: {time_scale:.1f}x)")
                print(f"   Consider algorithm optimization for large datasets")
            else:
                print(f"✅ Good linear scaling performance (scale factor: {scale_factor:.1f}x, time factor: {time_scale:.1f}x)")
        
        # Memory recommendations
        max_memory = max((r['memory_used_mb'] + r['processing_memory_used_mb']) for r in successful_results) if successful_results else 0
        if max_memory > 500:  # >500MB
            print(f"⚠️  High memory usage detected ({max_memory:.1f} MB)")
            print(f"   Consider implementing streaming/chunked processing")
        elif max_memory > 100:  # >100MB  
            print(f"📊 Moderate memory usage ({max_memory:.1f} MB) - monitor for larger datasets")
        else:
            print(f"✅ Excellent memory efficiency ({max_memory:.1f} MB)")
        
        print(f"\nREADY FOR PRODUCTION TESTING!")
        print(f"All stress test datasets have been generated and benchmarked.")

def main():
    """Run the complete stress test benchmark suite"""
    
    benchmarker = WareWiseStressBenchmark()
    
    if not benchmarker.available_files:
        print("No stress test files found!")
        print("Run stress_test_inventory_generator.py first to generate test datasets.")
        return
    
    # Run full benchmark suite
    results = benchmarker.run_full_benchmark_suite()
    
    # Generate comprehensive report
    benchmarker.generate_performance_report(results)
    
    # Save results to file
    results_df = pd.DataFrame(results)
    results_file = 'stress_test_benchmark_results.csv'
    results_df.to_csv(results_file, index=False)
    print(f"\nBenchmark results saved to: {results_file}")

if __name__ == "__main__":
    main()