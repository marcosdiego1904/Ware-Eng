#!/usr/bin/env python3
"""
Template-Based Validation System Integration Guide
Comprehensive guide and utilities for integrating the refactored validation architecture

This module provides:
1. Step-by-step integration instructions
2. Testing utilities for multiple warehouse templates
3. Performance comparison tools
4. Rollback procedures if needed

INTEGRATION SUMMARY:
- Replace hardcoded InvalidLocationEvaluator with TemplateBasedInvalidLocationEvaluator
- Ensure warehouse_context contains warehouse_id during rule evaluation
- Add warehouse template resolution to rule engine initialization
- Test with different warehouse configurations
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class TemplateValidationIntegrationGuide:
    """
    Comprehensive integration guide for template-based validation system
    """
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.integration_steps = self._define_integration_steps()
        self.test_scenarios = self._define_test_scenarios()
    
    def _define_integration_steps(self):
        """Define the step-by-step integration process"""
        return [
            {
                'step': 1,
                'title': 'Backup Current System',
                'description': 'Create backup of current rule_engine.py and related files',
                'actions': [
                    'Copy rule_engine.py to rule_engine_backup.py',
                    'Document current InvalidLocationEvaluator behavior',
                    'Create rollback procedure'
                ],
                'validation': 'Confirm backup files exist and are functional'
            },
            {
                'step': 2, 
                'title': 'Deploy Template Resolution System',
                'description': 'Add warehouse template resolution modules',
                'actions': [
                    'Deploy warehouse_template_resolver.py',
                    'Deploy template_based_invalid_location_evaluator.py',
                    'Ensure imports are available to rule engine'
                ],
                'validation': 'Import test: from warehouse_template_resolver import get_template_resolver'
            },
            {
                'step': 3,
                'title': 'Update Rule Engine Initialization',
                'description': 'Modify rule engine to use template-based evaluators',
                'actions': [
                    'Replace InvalidLocationEvaluator with TemplateBasedInvalidLocationEvaluator',
                    'Update evaluator factory/registry if used',
                    'Ensure db_session is passed to template evaluator'
                ],
                'validation': 'Rule engine initializes without errors'
            },
            {
                'step': 4,
                'title': 'Verify Warehouse Context Propagation',
                'description': 'Ensure warehouse_id reaches evaluators',
                'actions': [
                    'Check _detect_warehouse_context method includes warehouse_id',
                    'Verify warehouse_context passed to all evaluator.evaluate() calls',
                    'Add logging to track warehouse_context propagation'
                ],
                'validation': 'Logs show warehouse_context with warehouse_id in evaluator calls'
            },
            {
                'step': 5,
                'title': 'Test Template Resolution',
                'description': 'Verify templates resolve correctly for different warehouses',
                'actions': [
                    'Test USER_* pattern → DEFAULT template',
                    'Test database lookup for configured warehouses',
                    'Test fallback behavior for unknown warehouses'
                ],
                'validation': 'All warehouse types resolve to appropriate templates'
            },
            {
                'step': 6,
                'title': 'Validate Against Test Data',
                'description': 'Compare results using test datasets',
                'actions': [
                    'Run test4.xlsx (46 positions) - should find ~10 anomalies, not 386',
                    'Run test1.xlsx, test2.xlsx, test3.xlsx for regression testing',
                    'Compare anomaly counts before/after integration'
                ],
                'validation': 'Anomaly counts match expected template-based validation'
            },
            {
                'step': 7,
                'title': 'Performance Monitoring',
                'description': 'Monitor system performance with new validation',
                'actions': [
                    'Measure evaluation time for large inventories',
                    'Monitor memory usage during template resolution',
                    'Log template resolution cache hits/misses'
                ],
                'validation': 'Performance within acceptable bounds'
            },
            {
                'step': 8,
                'title': 'Production Deployment',
                'description': 'Deploy to production with monitoring',
                'actions': [
                    'Deploy with feature flag for rollback capability',
                    'Monitor error rates and anomaly detection accuracy',
                    'Set up alerts for template resolution failures'
                ],
                'validation': 'Production system stable with improved accuracy'
            }
        ]
    
    def _define_test_scenarios(self):
        """Define test scenarios for different warehouse configurations"""
        return [
            {
                'scenario': 'DEFAULT Template Validation',
                'warehouse_id': 'USER_MARCOS9', 
                'expected_template': 'DEFAULT',
                'dimensions': '4×2×46×4',
                'total_storage_locations': 1472,
                'test_locations': [
                    ('1-01-001A', True, 'Valid storage location'),
                    ('4-02-046D', True, 'Maximum valid position'),
                    ('1-01-047A', False, 'Position exceeds template (47 > 46)'),
                    ('5-01-001A', False, 'Aisle exceeds template (5 > 4)'),
                    ('RECV-01', True, 'Valid special area'),
                    ('INVALID-ZONE', False, 'Invalid location code')
                ]
            },
            {
                'scenario': 'SMALL Template Validation',
                'warehouse_id': 'SMALL_WAREHOUSE',
                'expected_template': 'SMALL',
                'dimensions': '2×1×20×3',
                'total_storage_locations': 120,
                'test_locations': [
                    ('1-01-001A', True, 'Valid storage location'),
                    ('2-01-020C', True, 'Maximum valid position'),
                    ('1-01-021A', False, 'Position exceeds template (21 > 20)'),
                    ('3-01-001A', False, 'Aisle exceeds template (3 > 2)'),
                    ('1-01-001D', False, 'Level exceeds template (D > C)')
                ]
            },
            {
                'scenario': 'LARGE Template Validation', 
                'warehouse_id': 'LARGE_DISTRIBUTION_CENTER',
                'expected_template': 'LARGE',
                'dimensions': '6×3×60×5',
                'total_storage_locations': 5400,
                'test_locations': [
                    ('6-03-060E', True, 'Maximum valid location'),
                    ('6-03-061A', False, 'Position exceeds template (61 > 60)'),
                    ('7-01-001A', False, 'Aisle exceeds template (7 > 6)')
                ]
            },
            {
                'scenario': 'Database Configuration Override',
                'warehouse_id': 'CUSTOM_CONFIGURED',
                'expected_template': 'Database',
                'note': 'Requires database entry in WarehouseConfig table',
                'test_locations': [
                    ('Database-specific locations based on actual configuration', None, 'Depends on database config')
                ]
            },
            {
                'scenario': 'Fallback Behavior',
                'warehouse_id': 'UNKNOWN_WAREHOUSE_123',
                'expected_template': 'DEFAULT (fallback)',
                'dimensions': '4×2×46×4',
                'test_locations': [
                    ('1-01-001A', True, 'Should use DEFAULT fallback template')
                ]
            }
        ]
    
    def get_integration_checklist(self) -> Dict[str, Any]:
        """Get comprehensive integration checklist"""
        return {
            'integration_guide': {
                'title': 'Template-Based Validation System Integration',
                'total_steps': len(self.integration_steps),
                'estimated_time': '2-4 hours',
                'risk_level': 'Medium (with rollback capability)',
                'steps': self.integration_steps
            },
            'test_scenarios': self.test_scenarios,
            'critical_success_factors': [
                'Template resolution works for all warehouse types',
                'Warehouse context propagates correctly to evaluators', 
                'Performance impact is acceptable',
                'Anomaly detection accuracy improves',
                'Rollback procedure is tested and ready'
            ],
            'rollback_procedure': self._get_rollback_procedure()
        }
    
    def _get_rollback_procedure(self) -> Dict[str, Any]:
        """Define rollback procedure if integration fails"""
        return {
            'title': 'Template Validation System Rollback',
            'when_to_rollback': [
                'Template resolution failures > 5%',
                'Performance degradation > 20%',
                'Critical anomaly detection failures',
                'System instability or crashes'
            ],
            'rollback_steps': [
                {
                    'step': 1,
                    'action': 'Restore rule_engine.py from rule_engine_backup.py',
                    'verification': 'System uses original InvalidLocationEvaluator'
                },
                {
                    'step': 2, 
                    'action': 'Remove template resolution module imports',
                    'verification': 'No import errors on system restart'
                },
                {
                    'step': 3,
                    'action': 'Restart application services',
                    'verification': 'System returns to baseline performance'
                },
                {
                    'step': 4,
                    'action': 'Verify anomaly detection returns to original behavior',
                    'verification': 'Test datasets produce original anomaly counts'
                }
            ],
            'post_rollback_analysis': [
                'Analyze logs to identify integration failure root cause',
                'Plan fixes for identified issues',
                'Schedule retry with fixes applied'
            ]
        }
    
    def run_template_resolution_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive tests for template resolution system
        
        Returns detailed test results for all scenarios
        """
        logger.info("[INTEGRATION_TEST] Starting template resolution system tests")
        
        test_results = {
            'test_timestamp': datetime.now().isoformat(),
            'scenarios_tested': len(self.test_scenarios),
            'results': [],
            'overall_status': 'PENDING'
        }
        
        success_count = 0
        
        for scenario in self.test_scenarios:
            logger.info(f"[INTEGRATION_TEST] Testing scenario: {scenario['scenario']}")
            
            scenario_result = self._test_scenario(scenario)
            test_results['results'].append(scenario_result)
            
            if scenario_result['status'] == 'SUCCESS':
                success_count += 1
        
        # Calculate overall status
        success_rate = success_count / len(self.test_scenarios)
        if success_rate == 1.0:
            test_results['overall_status'] = 'ALL_PASSED'
        elif success_rate >= 0.8:
            test_results['overall_status'] = 'MOSTLY_PASSED'
        else:
            test_results['overall_status'] = 'FAILED'
        
        test_results['success_rate'] = f"{success_rate:.1%}"
        
        logger.info(f"[INTEGRATION_TEST] Tests complete: {test_results['overall_status']} ({test_results['success_rate']})")
        
        return test_results
    
    def _test_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single template resolution scenario"""
        try:
            from warehouse_template_resolver import get_template_resolver
            
            # Test template resolution
            resolver = get_template_resolver(self.db_session)
            warehouse_context = {'warehouse_id': scenario['warehouse_id']}
            
            resolution_result = resolver.resolve_warehouse_template(warehouse_context)
            
            scenario_result = {
                'scenario': scenario['scenario'],
                'warehouse_id': scenario['warehouse_id'],
                'status': 'SUCCESS',
                'resolution_method': resolution_result.resolution_method,
                'confidence': resolution_result.confidence,
                'template_source': resolution_result.template_source,
                'location_tests': []
            }
            
            # Test location validation if test_locations provided
            if 'test_locations' in scenario:
                scenario_result['location_tests'] = self._test_location_validation(
                    resolution_result, scenario['test_locations']
                )
            
            # Verify expected dimensions if provided
            if 'dimensions' in scenario:
                config = resolution_result.warehouse_config
                actual_dimensions = f"{config['num_aisles']}×{config['racks_per_aisle']}×{config['positions_per_rack']}×{config['levels_per_position']}"
                
                scenario_result['dimensions_test'] = {
                    'expected': scenario['dimensions'],
                    'actual': actual_dimensions,
                    'match': actual_dimensions == scenario['dimensions']
                }
            
            return scenario_result
            
        except Exception as e:
            logger.error(f"[INTEGRATION_TEST] Scenario {scenario['scenario']} failed: {e}")
            return {
                'scenario': scenario['scenario'],
                'warehouse_id': scenario['warehouse_id'],
                'status': 'FAILED',
                'error': str(e)
            }
    
    def _test_location_validation(self, resolution_result, test_locations):
        """Test location validation for a resolved template"""
        from virtual_location_engine import VirtualLocationEngine
        
        virtual_engine = VirtualLocationEngine(resolution_result.warehouse_config)
        validation_results = []
        
        for location_code, expected_valid, description in test_locations:
            if location_code is None:  # Skip placeholder entries
                continue
                
            is_valid, reason = virtual_engine.validate_location(location_code)
            
            test_result = {
                'location': location_code,
                'expected_valid': expected_valid,
                'actual_valid': is_valid,
                'test_passed': (is_valid == expected_valid),
                'reason': reason,
                'description': description
            }
            
            validation_results.append(test_result)
        
        return validation_results
    
    def generate_integration_report(self) -> str:
        """Generate comprehensive integration report"""
        
        # Run tests
        test_results = self.run_template_resolution_tests()
        
        # Generate report
        report_lines = [
            "=" * 80,
            "TEMPLATE-BASED VALIDATION SYSTEM INTEGRATION REPORT", 
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Test Status: {test_results['overall_status']} ({test_results['success_rate']})",
            "",
            "INTEGRATION BENEFITS:",
            "• Solves hardcoded 29 vs 46 position validation mismatch",
            "• Enables multiple warehouse layouts without code changes",  
            "• Provides template-specific validation constraints",
            "• Improves anomaly detection accuracy and specificity",
            "",
            "INTEGRATION STEPS:",
        ]
        
        for step in self.integration_steps:
            report_lines.append(f"{step['step']}. {step['title']}")
            report_lines.append(f"   {step['description']}")
            report_lines.append("")
        
        report_lines.extend([
            "TEST RESULTS:",
            "=" * 40
        ])
        
        for result in test_results['results']:
            status_symbol = "PASS" if result['status'] == 'SUCCESS' else "FAIL"
            report_lines.append(f"{status_symbol} {result['scenario']}")
            
            if result['status'] == 'SUCCESS':
                report_lines.append(f"  Template: {result['resolution_method']} ({result['confidence']})")
                
                if 'dimensions_test' in result:
                    dims = result['dimensions_test']
                    dim_symbol = "PASS" if dims['match'] else "FAIL"
                    report_lines.append(f"  Dimensions: {dim_symbol} {dims['actual']} (expected: {dims['expected']})")
                
                if 'location_tests' in result:
                    passed_tests = sum(1 for test in result['location_tests'] if test['test_passed'])
                    total_tests = len(result['location_tests'])
                    report_lines.append(f"  Location Tests: {passed_tests}/{total_tests} passed")
                    
                    # Show failed location tests
                    failed_tests = [test for test in result['location_tests'] if not test['test_passed']]
                    for failed_test in failed_tests:
                        report_lines.append(f"    FAIL {failed_test['location']}: Expected {failed_test['expected_valid']}, got {failed_test['actual_valid']}")
            else:
                report_lines.append(f"  Error: {result.get('error', 'Unknown error')}")
            
            report_lines.append("")
        
        report_lines.extend([
            "NEXT STEPS:",
            "1. Review test results above",
            "2. Fix any failed test scenarios",
            "3. Follow integration steps in order",
            "4. Monitor system after deployment",
            "5. Use rollback procedure if needed",
            "",
            "=" * 80
        ])
        
        return "\n".join(report_lines)


def main():
    """Main function to run integration guide and tests"""
    print("Template-Based Validation System Integration Guide")
    print("=" * 60)
    
    # Initialize integration guide
    guide = TemplateValidationIntegrationGuide()
    
    # Generate and display integration report
    report = guide.generate_integration_report()
    print(report)
    
    # Get integration checklist
    checklist = guide.get_integration_checklist()
    
    # Save detailed results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'template_integration_report_{timestamp}.txt'
    
    with open(report_file, 'w') as f:
        f.write(report)
        f.write("\n\nDETAILED INTEGRATION CHECKLIST:\n")
        f.write("=" * 40 + "\n")
        f.write(json.dumps(checklist, indent=2))
    
    print(f"\nDetailed integration guide saved to: {report_file}")
    print("\nREADY FOR INTEGRATION!")

if __name__ == "__main__":
    main()