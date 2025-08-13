#!/usr/bin/env python3
"""
Simple debug script to check rules configuration
"""
import sys
import pandas as pd
import sqlite3

def check_rules():
    print("=== SIMPLE RULE DEBUG ===")
    
    # Load test data
    try:
        df = pd.read_excel('test_inventory_corrected.xlsx')
        print(f"[OK] Loaded test data: {len(df)} records")
        print(f"[DATA] Columns: {list(df.columns)}")
        print()
    except Exception as e:
        print(f"[ERROR] Failed to load test data: {e}")
        return
    
    # Check database rules directly
    try:
        conn = sqlite3.connect('backend/warehouse.db')
        cursor = conn.cursor()
        
        # Check if rule tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%rule%'")
        tables = cursor.fetchall()
        print(f"[DB] Rule-related tables: {[t[0] for t in tables]}")
        
        # Check active rules
        try:
            cursor.execute("SELECT id, name, rule_type, is_active, conditions FROM rule WHERE is_active = 1")
            rules = cursor.fetchall()
            print(f"[RULES] Found {len(rules)} active rules:")
            
            for rule in rules:
                rule_id, name, rule_type, is_active, conditions = rule
                print(f"  - {name} ({rule_type})")
                print(f"    ID: {rule_id}, Active: {is_active}")
                print(f"    Conditions: {conditions}")
                print()
        
        except sqlite3.OperationalError as e:
            print(f"[ERROR] No rules table or different schema: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Database access failed: {e}")
    
    # Analyze test data for expected anomalies
    print("[ANALYSIS] Expected anomalies in test data:")
    
    # 1. RECEIVING pallets (should be >8 hours old)
    receiving_pallets = df[df['location'] == 'RECEIVING']
    print(f"  RECEIVING pallets: {len(receiving_pallets)}")
    if len(receiving_pallets) > 0:
        print(f"    Timestamps: {receiving_pallets['creation_date'].tolist()}")
    
    # 2. STAGING pallets (should be >2 hours old) 
    staging_pallets = df[df['location'].str.startswith('STAGING-', na=False)]
    print(f"  STAGING pallets: {len(staging_pallets)}")
    if len(staging_pallets) > 0:
        print(f"    Timestamps: {staging_pallets['creation_date'].tolist()}")
    
    # 3. AISLETEST pallets (Location-Specific Stagnant)
    aisle_pallets = df[df['location'] == 'AISLETEST']
    print(f"  AISLETEST pallets: {len(aisle_pallets)}")
    if len(aisle_pallets) > 0:
        print(f"    Timestamps: {aisle_pallets['creation_date'].tolist()}")
    
    # 4. Dock overcapacity
    dock_counts = df[df['location'].str.startswith('DOCK-', na=False)]['location'].value_counts()
    print(f"  DOCK locations: {dict(dock_counts)}")
    
    # 5. Invalid locations
    invalid_locs = df[df['location'].isin(['INVALIDLOC', 'PLT041', 'PLT042'])]
    print(f"  Invalid locations: {len(invalid_locs)}")
    if len(invalid_locs) > 0:
        print(f"    Locations: {invalid_locs['location'].tolist()}")

if __name__ == "__main__":
    check_rules()