#!/usr/bin/env python3
"""
Debug statistical overcapacity analysis
"""
import sys
import os
sys.path.append('backend/src')

from models import db, Rule, Location
from app import app
import pandas as pd

def debug_statistical_analysis():
    """Debug statistical overcapacity calculation"""
    
    with app.app_context():
        # Load test inventory
        df = pd.read_excel('CentralDC_Compact_Inventory.xlsx', sheet_name='Inventory')
        
        # Calculate warehouse statistics manually like the evaluator does
        total_pallets = len(df)
        unique_locations = df['location'].nunique()
        utilization_rate = total_pallets / unique_locations if unique_locations > 0 else 0
        
        print("=== WAREHOUSE STATISTICS ===")
        print(f"Total pallets: {total_pallets}")
        print(f"Total unique locations: {unique_locations}")
        print(f"Utilization rate: {utilization_rate:.3f}")
        
        # Calculate expected overcapacity using the same logic as the evaluator
        print("\n=== EXPECTED OVERCAPACITY CALCULATION ===")
        if utilization_rate <= 1.0:
            # Low to moderate utilization: Use Poisson-like distribution
            expected_count = unique_locations * (utilization_rate ** 2) / 2
            model_used = "Poisson-based random distribution"
            
            # For very low utilization, expect minimal random overcapacity
            if utilization_rate < 0.3:
                expected_count = max(1, expected_count * 0.5)
        else:
            # High utilization logic (shouldn't apply here)
            expected_count = unique_locations * 0.3 * (utilization_rate - 1.0) + unique_locations * 0.1
            model_used = "High utilization linear model"
            
        print(f"Model used: {model_used}")
        print(f"Expected overcapacity count: {expected_count:.2f}")
        
        # Count actual overcapacity
        location_counts = df['location'].value_counts()
        actual_overcapacity_count = 0
        
        for location, count in location_counts.items():
            location_obj = Location.query.filter_by(code=location).first()
            if location_obj:
                capacity = location_obj.capacity
                if count > capacity:
                    actual_overcapacity_count += 1
        
        print(f"Actual overcapacity count: {actual_overcapacity_count}")
        
        # Calculate severity ratio
        severity_ratio = (actual_overcapacity_count / expected_count) if expected_count > 0 else float('inf')
        print(f"Severity ratio: {severity_ratio:.2f}")
        
        # Check thresholds (updated values)
        significance_threshold = 0.5  # Updated from 2.0
        min_severity_ratio = 0.5      # Updated from 1.5
        
        print(f"\n=== THRESHOLD ANALYSIS ===")
        print(f"Significance threshold: {significance_threshold}")
        print(f"Required actual count: {significance_threshold * expected_count:.2f}")
        print(f"Min severity ratio: {min_severity_ratio}")
        
        threshold_met = (severity_ratio >= min_severity_ratio and 
                        actual_overcapacity_count >= significance_threshold * expected_count)
        
        print(f"Threshold met: {threshold_met}")
        
        if not threshold_met:
            print("\n=== WHY NOT DETECTED ===")
            if severity_ratio < min_severity_ratio:
                print(f"X Severity ratio {severity_ratio:.2f} < {min_severity_ratio}")
            if actual_overcapacity_count < significance_threshold * expected_count:
                print(f"X Actual count {actual_overcapacity_count} < required {significance_threshold * expected_count:.2f}")
                
        print(f"\n=== RECOMMENDATION ===")
        print("To detect the 5 overcapacity locations, you could:")
        print("1. Lower significance_threshold to 1.0 or less")
        print("2. Lower min_severity_ratio to 1.0 or less") 
        print("3. Use legacy mode (use_statistical_analysis: false)")

if __name__ == "__main__":
    debug_statistical_analysis()