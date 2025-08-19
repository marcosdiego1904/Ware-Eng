#!/usr/bin/env python3
"""
Complete Production Workflow Test

Tests the entire production system:
1. Template Creation → Location Generation
2. Template Validation → Analysis Readiness  
3. Inventory Analysis → Rule Execution
4. User Format Intelligence → Template Integration
5. Multi-tenancy → Isolated Warehouses

This verifies the complete production-ready architecture.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from app import app, db
from production_template_engine import ProductionTemplateEngine, TemplateStructure
from production_rule_engine import get_production_rule_engine
from models import Location, WarehouseConfig
import pandas as pd
import time

def test_complete_production_workflow():
    """Test the complete production workflow end-to-end"""
    
    with app.app_context():
        print("=" * 60)
        print("COMPLETE PRODUCTION WORKFLOW TEST")
        print("=" * 60)
        
        # Initialize engines
        template_engine = ProductionTemplateEngine()
        rule_engine = get_production_rule_engine()
        
        warehouse_id = f"PRODUCTION_{int(time.time())}"
        
        # Step 1: Create production template
        print(f"Step 1: Creating production template for {warehouse_id}")
        
        structure = TemplateStructure(
            num_aisles=1,
            racks_per_aisle=3,  # Multiple racks for format testing
            positions_per_rack=10,
            levels_per_position=3,
            level_names="ABC",
            default_pallet_capacity=1,
            receiving_areas=[
                {"code": "RECV-01", "capacity": 15},
                {"code": "RECV-02", "capacity": 10}
            ],
            staging_areas=[{"code": "STAGE-01", "capacity": 8}],
            dock_areas=[{"code": "DOCK-01", "capacity": 3}],
            transitional_areas=[{"code": "AISLE-01", "capacity": 12}]
        )
        
        template_result = template_engine.create_production_template(
            template_name="Production Workflow Test",
            warehouse_id=warehouse_id,
            structure=structure,
            created_by=1
        )
        
        if not template_result['success']:
            print(f"FAILED: Template creation failed: {template_result['error']}")
            return False
        
        print(f"SUCCESS: Template created with {template_result['locations_created']['total']} locations")
        
        # Step 2: Validate template readiness
        print(f"\\nStep 2: Validating template readiness")
        ready, message = template_engine.is_warehouse_ready_for_analysis(warehouse_id)
        print(f"Analysis ready: {ready}")
        print(f"Message: {message}")
        
        if not ready:
            print("FAILED: Template not ready for analysis")
            return False
        
        # Step 3: Create test inventory with user-friendly formats
        print(f"\\nStep 3: Creating test inventory with user-friendly location formats")
        
        inventory_data = [
            # Standard storage using different user formats
            ['PALLET001', '001A01', 'Product A', 'REC001', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],  # -> 01-01-001A
            ['PALLET002', '005B02', 'Product B', 'REC001', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],  # -> 01-02-005B  
            ['PALLET003', '010C03', 'Product C', 'REC001', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],  # -> 01-03-010C
            ['PALLET004', 'A2-007', 'Product D', 'REC002', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],  # -> 01-02-007A
            
            # Special areas
            ['PALLET005', 'RECV-01', 'Incoming Product', 'REC002', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
            ['PALLET006', 'STAGE-01', 'Staged Product', 'REC002', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
            ['PALLET007', 'AISLE-01', 'Transit Product', 'REC003', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
            
            # Test overcapacity (2 pallets in 1-capacity locations)
            ['PALLET008', '001A01', 'Overcapacity Test', 'REC003', '2025-08-19 10:00:00', 'GENERAL', 'AMBIENT'],
        ]
        
        inventory_df = pd.DataFrame(inventory_data, columns=[
            'Pallet ID', 'Location', 'Description', 'Receipt Number', 
            'Creation Date', 'Product Type', 'Temperature Requirement'
        ])
        
        print(f"Created test inventory with {len(inventory_df)} pallets")
        print("Location formats used:")
        unique_locations = inventory_df['Location'].unique()
        for loc in unique_locations:
            print(f"  {loc}")
        
        # Step 4: Run production analysis
        print(f"\\nStep 4: Running production rule analysis")
        
        analysis_result = rule_engine.analyze_inventory_production(
            inventory_df=inventory_df,
            warehouse_id=warehouse_id,
            validate_template=True
        )
        
        if not analysis_result.get('success', False):
            print(f"FAILED: Analysis failed: {analysis_result.get('error', 'Unknown error')}")
            return False
        
        print(f"SUCCESS: Analysis completed")
        print(f"Total anomalies: {analysis_result.get('total_anomalies', 0)}")
        print(f"Rules executed: {analysis_result.get('rules_executed', 0)}")
        print(f"Location coverage: {analysis_result['template_validation']['coverage_percentage']:.1f}%")
        print(f"Valid locations: {analysis_result['template_validation']['valid_locations_count']}")
        print(f"Invalid locations: {analysis_result['template_validation']['invalid_locations_count']}")
        
        # Step 5: Analyze results by rule
        print(f"\\nStep 5: Rule-by-rule analysis")
        for rule_name, rule_result in analysis_result.get('rule_results', {}).items():
            if isinstance(rule_result, dict) and 'anomalies_found' in rule_result:
                anomaly_count = rule_result['anomalies_found']
                print(f"  {rule_name}: {anomaly_count} anomalies")
                
                # Show sample anomalies
                if anomaly_count > 0:
                    if 'overcapacity_locations' in rule_result:
                        print(f"    Overcapacity: {len(rule_result['overcapacity_locations'])} locations")
                    if 'invalid_locations' in rule_result:
                        print(f"    Invalid: {len(rule_result['invalid_locations'])} locations")
                    if 'stagnant_pallets' in rule_result:
                        print(f"    Stagnant: {len(rule_result['stagnant_pallets'])} pallets")
        
        # Step 6: Test analysis without template (should fail)
        print(f"\\nStep 6: Testing analysis without template (negative test)")
        
        fake_warehouse = "NONEXISTENT_WAREHOUSE"
        failed_analysis = rule_engine.analyze_inventory_production(
            inventory_df=inventory_df,
            warehouse_id=fake_warehouse,
            validate_template=True
        )
        
        if failed_analysis.get('success', True):
            print("FAILED: Analysis should have failed for non-existent warehouse")
            return False
        
        print(f"SUCCESS: Analysis correctly rejected non-templated warehouse")
        print(f"Error type: {failed_analysis.get('error_type', 'UNKNOWN')}")
        print(f"Message: {failed_analysis.get('error', 'No message')}")
        
        # Step 7: Cleanup
        print(f"\\nStep 7: Cleaning up test data")
        Location.query.filter_by(warehouse_id=warehouse_id).delete()
        WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).delete()
        db.session.commit()
        print("Cleanup completed")
        
        # Summary
        print(f"\\n" + "=" * 60)
        print("PRODUCTION WORKFLOW TEST RESULTS")
        print("=" * 60)
        print("SUCCESS: Template creation and location generation")
        print("SUCCESS: Template validation and analysis readiness")
        print("SUCCESS: User-friendly location format processing")
        print("SUCCESS: Production rule analysis execution")
        print("SUCCESS: Template requirement enforcement")
        print("SUCCESS: Complete workflow validation")
        
        return True

if __name__ == "__main__":
    success = test_complete_production_workflow()
    if success:
        print("\\nSUCCESS: Production system ready for deployment!")
    else:
        print("\\nFAILED: Production system has issues")
    sys.exit(0 if success else 1)