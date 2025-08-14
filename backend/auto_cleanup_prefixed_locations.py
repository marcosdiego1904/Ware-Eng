#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Cleanup Script for Prefixed Locations - NO CONFIRMATION NEEDED
Removes locations with unwanted prefixes automatically
"""

import sys
import os
sys.path.append('src')

from app import app, db
from models import Location, WarehouseConfig

def auto_cleanup_prefixed_locations():
    """Remove locations with prefixes automatically"""
    
    print("Starting automatic location cleanup...")
    
    with app.app_context():
        # Find all locations with problematic prefixes
        print("Analyzing current locations...")
        
        # Count all locations by type
        all_locations = Location.query.all()
        location_types = {}
        prefixed_locations = []
        clean_locations = []
        
        for loc in all_locations:
            loc_type = loc.location_type
            if loc_type not in location_types:
                location_types[loc_type] = {'total': 0, 'prefixed': 0, 'clean': 0}
            
            location_types[loc_type]['total'] += 1
            
            # Check if location has problematic prefix
            has_prefix = False
            prefixes_to_check = ['USER_', 'HOLA', 'MARCOS', 'TMPL_', 'TEMPLATE_']
            for prefix in prefixes_to_check:
                if loc.code.startswith(prefix):
                    has_prefix = True
                    break
            
            if has_prefix:
                location_types[loc_type]['prefixed'] += 1
                prefixed_locations.append(loc)
            else:
                location_types[loc_type]['clean'] += 1
                clean_locations.append(loc)
        
        print(f"\nLocation Analysis:")
        print(f"{'Type':<12} {'Total':<8} {'Prefixed':<10} {'Clean':<8}")
        print("-" * 40)
        
        for loc_type, counts in location_types.items():
            print(f"{loc_type:<12} {counts['total']:<8} {counts['prefixed']:<10} {counts['clean']:<8}")
        
        print(f"\nFound {len(prefixed_locations)} locations with problematic prefixes")
        
        if len(prefixed_locations) > 0:
            print("\nSample prefixed locations to be removed:")
            for i, loc in enumerate(prefixed_locations[:10]):
                print(f"  {i+1:2d}. {loc.code:<30} ({loc.location_type})")
            
            if len(prefixed_locations) > 10:
                print(f"     ... and {len(prefixed_locations) - 10} more")
            
            # Auto cleanup - no confirmation needed
            print(f"\nAUTO-CLEANING: Deleting {len(prefixed_locations)} prefixed locations...")
            
            deleted_count = 0
            errors = []
            
            # Delete in batches to avoid memory issues
            batch_size = 100
            total_batches = (len(prefixed_locations) + batch_size - 1) // batch_size
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(prefixed_locations))
                batch_locations = prefixed_locations[start_idx:end_idx]
                
                print(f"   Processing batch {batch_num + 1}/{total_batches} ({len(batch_locations)} locations)...")
                
                for loc in batch_locations:
                    try:
                        db.session.delete(loc)
                        deleted_count += 1
                    except Exception as e:
                        errors.append(f"Error deleting {loc.code}: {str(e)}")
                
                # Commit each batch
                try:
                    db.session.commit()
                except Exception as commit_error:
                    db.session.rollback()
                    print(f"   ERROR in batch {batch_num + 1}: {commit_error}")
                    errors.append(f"Batch {batch_num + 1} commit failed: {commit_error}")
            
            print(f"\nSUCCESS: Deleted {deleted_count} prefixed locations!")
            
            if errors:
                print(f"\n{len(errors)} errors occurred:")
                for error in errors[:5]:  # Show first 5 errors
                    print(f"   - {error}")
                if len(errors) > 5:
                    print(f"   ... and {len(errors) - 5} more errors")
            
            # Show final stats
            remaining_locations = Location.query.count()
            print(f"\nCleanup complete!")
            print(f"   Deleted: {deleted_count} prefixed locations")
            print(f"   Remaining: {remaining_locations} total locations")
            
            # Show remaining special areas
            special_remaining = Location.query.filter(
                Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
            ).count()
            
            print(f"   Special areas remaining: {special_remaining}")
            
            if special_remaining == 0:
                print("\nAll special areas cleared! You can now recreate them with clean names.")
            else:
                remaining_special = Location.query.filter(
                    Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK'])
                ).all()
                print(f"\nRemaining special areas:")
                for loc in remaining_special:
                    print(f"   - {loc.code} ({loc.location_type})")
            
            return True
        else:
            print("\nNo prefixed locations found! Database is already clean.")
            return True

if __name__ == '__main__':
    print("Auto Location Cleanup Tool")
    print("=" * 50)
    
    success = auto_cleanup_prefixed_locations()
    
    if success:
        print("\nAfter cleanup, create these clean special areas:")
        print("   Receiving Areas:")
        print("      - RCV-001 (capacity: 10)")
        print("      - RCV-002 (capacity: 10)")
        print("      - RCV-003 (capacity: 8)")
        print("   Staging Areas:")
        print("      - STG-001 (capacity: 5)")
        print("      - STG-002 (capacity: 5)")
        print("   Dock Areas:")
        print("      - DOCK-01 (capacity: 3)")
        print("      - DOCK-02 (capacity: 3)")
        
        print(f"\nNext Steps:")
        print("   1. Go to your warehouse settings in the UI")
        print("   2. Use the setup wizard or manually add the special areas above")
        print("   3. Test your inventory with the clean location codes")
        print("   4. The rules engine should now work correctly!")
    else:
        print("\nCleanup failed. Check errors above.")
    
    print("\n" + "=" * 50)