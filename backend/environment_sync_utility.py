#!/usr/bin/env python3
"""
Environment Data Synchronization Utility
Synchronizes warehouse location data between development and production environments
"""

import sys
import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import Location, WarehouseConfig
from sqlalchemy import text

class EnvironmentSyncUtility:
    """Utility for synchronizing warehouse data across environments"""
    
    def __init__(self):
        self.sync_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'environment_analysis': {},
            'sync_operations': [],
            'validation_results': {},
            'warnings': [],
            'errors': []
        }
    
    def analyze_environment_differences(self) -> Dict:
        """Analyze differences between current environment and expected data"""
        
        with app.app_context():
            print("=== ENVIRONMENT ANALYSIS ===")
            
            # Get current database info
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
            is_sqlite = 'sqlite' in db_uri.lower()
            is_postgresql = 'postgresql' in db_uri.lower()
            
            print(f"Database Type: {'SQLite' if is_sqlite else 'PostgreSQL' if is_postgresql else 'Unknown'}")
            print(f"Database URI: {db_uri}")
            
            # Analyze warehouse distribution
            from sqlalchemy import case
            warehouse_stats = db.session.query(
                Location.warehouse_id,
                db.func.count(Location.id).label('location_count'),
                db.func.count(case((Location.is_active == True, 1))).label('active_count'),
                db.func.min(Location.created_at).label('first_created'),
                db.func.max(Location.created_at).label('last_created')
            ).group_by(Location.warehouse_id).all()
            
            warehouse_analysis = {}
            total_locations = 0
            
            for warehouse_id, location_count, active_count, first_created, last_created in warehouse_stats:
                total_locations += location_count
                warehouse_analysis[warehouse_id] = {
                    'total_locations': location_count,
                    'active_locations': active_count,
                    'inactive_locations': location_count - active_count,
                    'first_created': first_created.isoformat() if first_created else None,
                    'last_created': last_created.isoformat() if last_created else None
                }
                print(f"  {warehouse_id}: {location_count} locations ({active_count} active)")
            
            # Analyze location format patterns
            format_analysis = self._analyze_location_formats()
            
            # Environment classification
            environment_type = self._classify_environment(warehouse_analysis, total_locations)
            
            analysis_result = {
                'database_type': 'SQLite' if is_sqlite else 'PostgreSQL' if is_postgresql else 'Unknown',
                'database_uri': db_uri,
                'environment_type': environment_type,
                'total_locations': total_locations,
                'warehouse_count': len(warehouse_analysis),
                'warehouse_distribution': warehouse_analysis,
                'location_format_patterns': format_analysis
            }
            
            self.sync_report['environment_analysis'] = analysis_result
            return analysis_result
    
    def _classify_environment(self, warehouse_analysis: Dict, total_locations: int) -> str:
        """Classify environment based on data characteristics"""
        
        if 'USER_TESTF' in warehouse_analysis and len(warehouse_analysis) == 1:
            return 'DEVELOPMENT'
        elif 'DEFAULT' in warehouse_analysis and total_locations > 1000:
            return 'PRODUCTION'
        elif total_locations < 500:
            return 'DEVELOPMENT_OR_STAGING'
        else:
            return 'PRODUCTION_OR_STAGING'
    
    def _analyze_location_formats(self) -> Dict:
        """Analyze location code format patterns"""
        
        import re
        
        # Sample location codes for pattern analysis
        sample_locations = db.session.query(Location.code).limit(50).all()
        
        format_patterns = {
            'standard_aisle_format': 0,  # XX-XX-XXXA
            'mixed_padding_format': 0,   # XX-X-XXXA
            'special_locations': 0,      # RECV-XX, STAGE-XX
            'dock_locations': 0,         # DOCK-XX
            'unknown_formats': 0
        }
        
        total_sampled = len(sample_locations)
        
        for location in sample_locations:
            code = location.code.upper()
            
            if re.match(r'^\d{2}-\d{2}-\d{3}[A-Z]$', code):
                format_patterns['standard_aisle_format'] += 1
            elif re.match(r'^\d{1,2}-\d{1,2}-\d{1,3}[A-Z]$', code):
                format_patterns['mixed_padding_format'] += 1
            elif re.match(r'^(RECV|STAGE|AISLE)-\d+$', code):
                format_patterns['special_locations'] += 1
            elif re.match(r'^DOCK-?\d+$', code):
                format_patterns['dock_locations'] += 1
            else:
                format_patterns['unknown_formats'] += 1
        
        # Convert to percentages
        if total_sampled > 0:
            for pattern in format_patterns:
                format_patterns[pattern] = round((format_patterns[pattern] / total_sampled) * 100, 1)
        
        return {
            'total_sampled': total_sampled,
            'pattern_percentages': format_patterns
        }
    
    def create_test_warehouse_from_production(self, target_warehouse_id: str = 'USER_TESTF', 
                                            sample_percentage: float = 0.2) -> bool:
        """Create a test warehouse with sampled production data"""
        
        with app.app_context():
            print(f"=== CREATING TEST WAREHOUSE: {target_warehouse_id} ===")
            
            try:
                # Check if DEFAULT warehouse exists
                default_locations = db.session.query(Location).filter_by(warehouse_id='DEFAULT').all()
                
                if not default_locations:
                    self.sync_report['errors'].append("No DEFAULT warehouse found to sample from")
                    return False
                
                print(f"Found {len(default_locations)} locations in DEFAULT warehouse")
                
                # Remove existing target warehouse
                existing_count = db.session.query(Location).filter_by(warehouse_id=target_warehouse_id).count()
                if existing_count > 0:
                    print(f"Removing {existing_count} existing locations from {target_warehouse_id}")
                    db.session.query(Location).filter_by(warehouse_id=target_warehouse_id).delete()
                    db.session.commit()
                
                # Sample locations intelligently (ensure format diversity)\n                sampled_locations = self._intelligent_location_sampling(default_locations, sample_percentage)
                
                print(f"Creating {len(sampled_locations)} locations in {target_warehouse_id} warehouse")
                
                # Create new locations with target warehouse_id
                created_count = 0
                for original_location in sampled_locations:
                    new_location = Location(
                        code=original_location.code,
                        warehouse_id=target_warehouse_id,
                        aisle_number=original_location.aisle_number,
                        rack_number=original_location.rack_number,
                        position_number=original_location.position_number,
                        level=original_location.level,
                        pallet_capacity=original_location.pallet_capacity,
                        zone=original_location.zone,
                        location_type=original_location.location_type,
                        is_active=True,
                        created_by=1  # System user
                    )
                    
                    db.session.add(new_location)
                    created_count += 1
                
                db.session.commit()
                
                operation_record = {
                    'operation': 'create_test_warehouse',
                    'target_warehouse': target_warehouse_id,
                    'source_locations': len(default_locations),
                    'created_locations': created_count,
                    'sample_percentage': sample_percentage,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self.sync_report['sync_operations'].append(operation_record)
                
                print(f"✅ Successfully created {created_count} locations in {target_warehouse_id} warehouse")
                return True
                
            except Exception as e:
                error_msg = f"Failed to create test warehouse: {str(e)}"
                print(f"❌ {error_msg}")
                self.sync_report['errors'].append(error_msg)
                return False
    
    def _intelligent_location_sampling(self, locations: List[Location], sample_percentage: float) -> List[Location]:
        """Intelligently sample locations to ensure format diversity"""
        
        import random
        
        # Categorize locations by type
        categories = {
            'standard_aisles': [],
            'special_areas': [],
            'dock_areas': [],
            'other': []
        }
        
        for location in locations:
            code = location.code.upper()
            if code.startswith(('RECV', 'STAGE', 'AISLE')):
                categories['special_areas'].append(location)
            elif code.startswith('DOCK'):
                categories['dock_areas'].append(location)
            elif '-' in code and any(c.isdigit() for c in code):
                categories['standard_aisles'].append(location)
            else:
                categories['other'].append(location)
        
        # Sample from each category proportionally
        sampled = []
        total_to_sample = int(len(locations) * sample_percentage)
        
        for category, locs in categories.items():
            if locs:
                category_sample_size = max(1, int(len(locs) * sample_percentage))
                category_sample_size = min(category_sample_size, len(locs))
                sampled.extend(random.sample(locs, category_sample_size))
        
        # If we need more locations, sample randomly from remaining
        if len(sampled) < total_to_sample:
            remaining = [loc for loc in locations if loc not in sampled]
            additional_needed = total_to_sample - len(sampled)
            if remaining and additional_needed > 0:
                additional_sample_size = min(additional_needed, len(remaining))
                sampled.extend(random.sample(remaining, additional_sample_size))
        
        return sampled[:total_to_sample]  # Ensure we don't exceed target
    
    def validate_warehouse_detection(self, test_inventory_locations: List[str]) -> Dict:
        """Validate warehouse detection with test inventory data"""
        
        with app.app_context():
            print("=== VALIDATING WAREHOUSE DETECTION ===")
            
            # Import rule engine for testing
            from rule_engine import RuleEngine
            import pandas as pd
            
            # Create test DataFrame
            test_df = pd.DataFrame({'location': test_inventory_locations})
            
            # Initialize rule engine
            rule_engine = RuleEngine(db.session)
            
            # Test detection
            detection_result = rule_engine._detect_warehouse_context(test_df)
            
            validation_result = {
                'test_locations_count': len(test_inventory_locations),
                'detection_result': detection_result,
                'validation_timestamp': datetime.utcnow().isoformat()
            }
            
            self.sync_report['validation_results'] = validation_result
            
            # Print results
            if detection_result.get('warehouse_id'):
                confidence = detection_result.get('confidence_level', 'UNKNOWN')
                score = detection_result.get('match_score', 0)
                print(f"✅ Detected warehouse: {detection_result['warehouse_id']} (confidence: {confidence}, score: {score:.1%})")
            else:
                print("❌ No warehouse detected")
            
            return validation_result
    
    def generate_sync_report(self, output_file: str = None) -> str:
        """Generate comprehensive synchronization report"""
        
        report_content = f"""
# Environment Synchronization Report
Generated: {self.sync_report['timestamp']}

## Environment Analysis
- Database Type: {self.sync_report['environment_analysis'].get('database_type', 'Unknown')}
- Environment Type: {self.sync_report['environment_analysis'].get('environment_type', 'Unknown')}
- Total Locations: {self.sync_report['environment_analysis'].get('total_locations', 0)}
- Warehouse Count: {self.sync_report['environment_analysis'].get('warehouse_count', 0)}

## Warehouse Distribution
"""
        
        for warehouse_id, stats in self.sync_report['environment_analysis'].get('warehouse_distribution', {}).items():
            report_content += f"- {warehouse_id}: {stats['total_locations']} locations ({stats['active_locations']} active)\\n"
        
        report_content += f"""
## Location Format Analysis
"""
        
        format_patterns = self.sync_report['environment_analysis'].get('location_format_patterns', {}).get('pattern_percentages', {})
        for pattern, percentage in format_patterns.items():
            report_content += f"- {pattern.replace('_', ' ').title()}: {percentage}%\\n"
        
        if self.sync_report['sync_operations']:
            report_content += f"""
## Synchronization Operations
"""
            for op in self.sync_report['sync_operations']:
                report_content += f"- {op['operation']}: {op.get('created_locations', 0)} locations created\\n"
        
        if self.sync_report['validation_results']:
            val_result = self.sync_report['validation_results']['detection_result']
            report_content += f"""
## Validation Results
- Detected Warehouse: {val_result.get('warehouse_id', 'None')}
- Confidence Level: {val_result.get('confidence_level', 'None')}
- Match Score: {val_result.get('match_score', 0):.1%}
"""
        
        if self.sync_report['warnings']:
            report_content += f"""
## Warnings
"""
            for warning in self.sync_report['warnings']:
                report_content += f"- {warning}\\n"
        
        if self.sync_report['errors']:
            report_content += f"""
## Errors
"""
            for error in self.sync_report['errors']:
                report_content += f"- {error}\\n"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_content)
            print(f"📄 Report saved to: {output_file}")
        
        return report_content

def main():
    """Main execution function"""
    
    sync_util = EnvironmentSyncUtility()
    
    # Step 1: Analyze current environment
    print("Step 1: Analyzing current environment...")
    analysis = sync_util.analyze_environment_differences()
    
    # Step 2: Create test data if in development
    if analysis['environment_type'] in ['DEVELOPMENT', 'DEVELOPMENT_OR_STAGING']:
        print("\\nStep 2: Creating test warehouse data...")
        sync_util.create_test_warehouse_from_production('USER_TESTF', sample_percentage=0.3)
    else:
        print("\\nStep 2: Skipping test warehouse creation (production environment)")
    
    # Step 3: Validate detection with sample data
    print("\\nStep 3: Validating warehouse detection...")
    test_locations = [
        '02-1-011B', '01-1-007B', '01-1-019A', '02-1-003B', 
        '01-1-004C', '02-1-021A', '01-1-014C', '01-1-001C',
        'RECV-01', 'RECV-02', 'STAGE-01', 'AISLE-01', 'AISLE-02'
    ]
    sync_util.validate_warehouse_detection(test_locations)
    
    # Step 4: Generate report
    print("\\nStep 4: Generating sync report...")
    report_file = f"environment_sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    sync_util.generate_sync_report(report_file)
    
    print("\\n✅ Environment synchronization complete!")

if __name__ == '__main__':
    main()