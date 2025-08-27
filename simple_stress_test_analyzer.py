#!/usr/bin/env python3
"""
SIMPLE STRESS TEST ANALYZER
===========================

Basic analysis tool for generated stress test inventories:
- File size and record count analysis
- Expected vs actual anomaly validation
- Basic performance metrics
- No external dependencies required
"""

import pandas as pd
import os
import time
from datetime import datetime

def analyze_stress_test_files():
    """Analyze all generated stress test files"""
    
    print("WAREWISE STRESS TEST ANALYSIS")
    print("=============================")
    
    # Find all stress test files
    test_files = [
        ('1K', 'stress_test_inventory_1K.csv', 52),
        ('5K', 'stress_test_inventory_5K.csv', 245), 
        ('10K', 'stress_test_inventory_10K.csv', 490),
        ('25K', 'stress_test_inventory_25K.csv', 1225),
        ('50K', 'stress_test_inventory_50K.csv', 2450)
    ]
    
    print("GENERATED FILES ANALYSIS:")
    print("=" * 50)
    
    results = []
    
    for label, filename, expected_anomalies in test_files:
        if os.path.exists(filename):
            # File size
            file_size_mb = os.path.getsize(filename) / (1024 * 1024)
            
            # Load and analyze
            print(f"\n{label} Dataset ({filename}):")
            print(f"  File size: {file_size_mb:.1f} MB")
            
            try:
                start_time = time.time()
                df = pd.read_csv(filename)
                load_time = time.time() - start_time
                
                record_count = len(df)
                print(f"  Records: {record_count:,}")
                print(f"  Load time: {load_time:.3f} seconds")
                print(f"  Load rate: {record_count/load_time:,.0f} records/sec")
                
                # Analyze content
                unique_locations = df['location'].nunique()
                unique_receipts = df['receipt_number'].nunique()
                
                print(f"  Unique locations: {unique_locations}")
                print(f"  Unique receipts: {unique_receipts}")
                
                # Detect actual anomalies using simple patterns
                actual_anomalies = detect_simple_anomalies(df)
                detection_rate = (actual_anomalies / expected_anomalies) * 100 if expected_anomalies > 0 else 0
                
                print(f"  Expected anomalies: {expected_anomalies}")
                print(f"  Detected anomalies: {actual_anomalies}")
                print(f"  Detection rate: {detection_rate:.1f}%")
                
                results.append({
                    'label': label,
                    'filename': filename,
                    'file_size_mb': file_size_mb,
                    'record_count': record_count,
                    'load_time': load_time,
                    'expected_anomalies': expected_anomalies,
                    'detected_anomalies': actual_anomalies,
                    'detection_rate': detection_rate
                })
                
            except Exception as e:
                print(f"  ERROR: {e}")
        else:
            print(f"\n{label} Dataset: FILE NOT FOUND ({filename})")
    
    # Summary analysis
    if results:
        print(f"\n" + "="*70)
        print(f"STRESS TEST SUMMARY")
        print(f"="*70)
        
        print(f"\nFILE SIZE SCALING:")
        for result in results:
            mb_per_k_records = result['file_size_mb'] / (result['record_count'] / 1000)
            print(f"  {result['label']}: {result['file_size_mb']:.1f} MB ({mb_per_k_records:.2f} MB/1K records)")
        
        print(f"\nLOAD PERFORMANCE:")
        for result in results:
            load_rate = result['record_count'] / result['load_time']
            print(f"  {result['label']}: {load_rate:,.0f} records/sec")
        
        print(f"\nANOMALY DETECTION ACCURACY:")
        for result in results:
            print(f"  {result['label']}: {result['detection_rate']:.1f}% ({result['detected_anomalies']}/{result['expected_anomalies']})")
        
        # Performance recommendations
        print(f"\nRECOMMENDAT IONS:")
        
        max_records = max(r['record_count'] for r in results)
        max_file_size = max(r['file_size_mb'] for r in results)
        
        if max_file_size < 10:
            print(f"✅ Excellent file sizes ({max_file_size:.1f} MB max) - suitable for web upload")
        elif max_file_size < 50:
            print(f"📊 Moderate file sizes ({max_file_size:.1f} MB max) - acceptable for most systems")  
        else:
            print(f"⚠️  Large file sizes ({max_file_size:.1f} MB max) - may need chunked processing")
        
        avg_load_rate = sum(r['record_count'] / r['load_time'] for r in results) / len(results)
        if avg_load_rate > 10000:
            print(f"✅ Excellent load performance ({avg_load_rate:,.0f} records/sec average)")
        elif avg_load_rate > 5000:
            print(f"📊 Good load performance ({avg_load_rate:,.0f} records/sec average)")
        else:
            print(f"⚠️  Slow load performance ({avg_load_rate:,.0f} records/sec average)")
        
        print(f"\nREADY FOR WAREWISE TESTING!")
        print(f"Upload these files to test system scalability:")
        for result in results:
            print(f"  - {result['filename']} ({result['record_count']:,} records, {result['expected_anomalies']} anomalies)")

def detect_simple_anomalies(df):
    """Simple anomaly detection simulation"""
    anomaly_count = 0
    
    try:
        # Convert dates
        df['creation_date'] = pd.to_datetime(df['creation_date'])
        now = datetime.now()
        df['hours_ago'] = (now - df['creation_date']).dt.total_seconds() / 3600
        
        # 1. Stagnant pallets (>10h in RECV)
        recv_pallets = df[df['location'].str.contains('RECV', na=False)]
        stagnant = len(recv_pallets[recv_pallets['hours_ago'] > 10])
        anomaly_count += stagnant
        
        # 2. Duplicates
        duplicates = len(df[df.duplicated(subset=['pallet_id'], keep=False)])
        anomaly_count += duplicates
        
        # 3. Invalid location patterns (simple check)
        # Valid: RECV-XX, STAGE-XX, DOCK-XX, AISLE-XX, XX-XX-XXXL
        valid_pattern = df['location'].str.match(r'^(RECV|STAGE|DOCK|AISLE)-\d+$|^\d{2}-\d{2}-\d{3}[A-D]$', na=False)
        invalid = len(df[~valid_pattern])
        anomaly_count += invalid
        
        # 4. Aisle stagnant (>4h in AISLE)
        aisle_pallets = df[df['location'].str.contains('AISLE', na=False)]
        aisle_stagnant = len(aisle_pallets[aisle_pallets['hours_ago'] > 4])
        anomaly_count += aisle_stagnant
        
        # 5. Overcapacity (simple: >8 pallets per location)
        location_counts = df.groupby('location').size()
        overcapacity = len(location_counts[location_counts > 8])
        anomaly_count += overcapacity
        
    except Exception as e:
        print(f"    Anomaly detection error: {e}")
        anomaly_count = 0
    
    return anomaly_count

def show_sample_records(filename, count=5):
    """Show sample records from a stress test file"""
    
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return
    
    print(f"\nSAMPLE RECORDS from {filename}:")
    print("-" * 60)
    
    df = pd.read_csv(filename)
    
    # Show first few records
    for i, row in df.head(count).iterrows():
        print(f"Record {i+1}:")
        print(f"  Pallet: {row['pallet_id']}")
        print(f"  Location: {row['location']}")
        print(f"  Created: {row['creation_date']}")
        print(f"  Receipt: {row['receipt_number']}")
        print()

def main():
    """Main analysis function"""
    
    # Analyze all files
    analyze_stress_test_files()
    
    # Show samples from smallest dataset
    if os.path.exists('stress_test_inventory_1K.csv'):
        show_sample_records('stress_test_inventory_1K.csv', 3)

if __name__ == "__main__":
    main()