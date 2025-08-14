#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup Script for Prefixed Locations
Removes locations with unwanted prefixes to allow clean recreation
"""

import sys
import os
sys.path.append('src')

from app import app, db
from models import Location, WarehouseConfig

def cleanup_prefixed_locations():
    """Remove locations with prefixes that should be clean"""
    
    print("Starting location cleanup...")
    
    with app.app_context():
        # Find all locations with problematic prefixes
        prefixed_patterns = [
            '%USER_%',
            '%HOLA%_%',
            '%MARCOS%_%', 
            '%TMPL_%',
            '%_RCV%',
            '%_STG%',
            '%_STAGE%',
            '%_DOCK%',
            '%_RECEIVING%',
            '%_STAGING%'
        ]
        
        print("\nAnalyzing current locations...")
        
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
            for pattern in ['USER_', 'HOLA', 'MARCOS', 'TMPL_']:
                if loc.code.startswith(pattern):
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
            
            # Ask for confirmation
            print(f"\nWARNING: This will DELETE {len(prefixed_locations)} prefixed locations")
            print("After cleanup, you can recreate them with clean names through the UI")
            
            confirm = input("\nProceed with cleanup? (y/N): ").strip().lower()
            
            if confirm == 'y':
                print("\nStarting deletion...")
                
                deleted_count = 0
                errors = []
                
                for loc in prefixed_locations:
                    try:
                        print(f"   Deleting: {loc.code}")
                        db.session.delete(loc)
                        deleted_count += 1
                    except Exception as e:
                        errors.append(f"Error deleting {loc.code}: {str(e)}")
                
                try:
                    db.session.commit()
                    print(f"\nSUCCESS: Deleted {deleted_count} prefixed locations!")
                    
                    if errors:
                        print(f"\n{len(errors)} errors occurred:")
                        for error in errors:
                            print(f"   - {error}")
                    
                except Exception as commit_error:
                    db.session.rollback()
                    print(f"\nERROR: Failed to commit deletions: {commit_error}")
                    return False
                
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
                print("\nCleanup cancelled.")
                return False
        else:
            print("\nNo prefixed locations found! Database is already clean.")
            return True

def show_clean_special_areas():
    """Show what clean special areas should look like"""
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

if __name__ == '__main__':
    print("Location Cleanup Tool")
    print("=" * 50)
    
    success = cleanup_prefixed_locations()
    
    if success:
        show_clean_special_areas()
        print(f"\nNext Steps:")
        print("   1. Go to your warehouse settings in the UI")
        print("   2. Use the setup wizard or manually add the special areas above")
        print("   3. Test your inventory with the clean location codes")
        print("   4. The rules engine should now work correctly!")
    else:
        print("\nCleanup failed. Check errors above.")
    
    print("\n" + "=" * 50)