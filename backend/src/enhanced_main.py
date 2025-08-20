"""
Enhanced Analysis Engine with Dynamic Rules Support
Implementation Plan Phase 2: Rule Engine Integration

This module provides backward compatibility with the existing main.py
while adding support for database-driven dynamic rules.
"""

import pandas as pd
import os
import json
import argparse 
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from rule_engine import RuleEngine
from models import Rule, RuleCategory, RulePerformance
from database import db
from app import AnalysisReport
from session_manager import RequestScopedSessionManager, invalidate_cache
from session_safe_cache import get_session_safe_cache

def run_enhanced_engine(inventory_df: pd.DataFrame, 
                       rules_df: pd.DataFrame = None, 
                       args: argparse.Namespace = None,
                       use_database_rules: bool = True,
                       rule_ids: List[int] = None,
                       report_id: int = None) -> List[Dict[str, Any]]:
    """
    Enhanced warehouse intelligence engine that supports both Excel rules (legacy)
    and database rules (new dynamic system).
    
    Args:
        inventory_df: Inventory data to analyze
        rules_df: Excel rules (for backward compatibility)
        args: Command line arguments (for backward compatibility)
        use_database_rules: Whether to use database rules instead of Excel
        rule_ids: Specific rule IDs to use (if None, uses all active rules)
        report_id: Analysis report ID for performance tracking
    
    Returns:
        List of anomaly dictionaries
    """
    print("\nRunning enhanced warehouse intelligence engine...")
    
    if use_database_rules:
        return _run_database_rules_engine(inventory_df, rule_ids, report_id)
    else:
        # Fall back to legacy Excel-based engine
        from main import run_engine as legacy_run_engine
        return legacy_run_engine(inventory_df, rules_df, args)

def _run_database_rules_engine(inventory_df: pd.DataFrame, 
                             rule_ids: List[int] = None,
                             report_id: int = None) -> List[Dict[str, Any]]:
    """
    Execute analysis using database-stored rules with enhanced session management
    """
    try:
        # ENHANCED: Invalidate request-scoped caches to prevent cross-request contamination
        invalidate_cache()
        
        # Invalidate session-safe cache for this request
        cache = get_session_safe_cache()
        cache.invalidate_request_cache()
        
        # Get current session using the session manager
        current_session = RequestScopedSessionManager.get_current_session()
        
        # Initialize rule engine with request-scoped session
        rule_engine = RuleEngine(current_session)
        
        # Load and evaluate rules
        print(f"Loading rules from database...")
        evaluation_results = rule_engine.evaluate_all_rules(inventory_df, rule_ids)
        
        # Collect all anomalies
        all_anomalies = []
        rules_used = []
        
        for result in evaluation_results:
            if result.success:
                all_anomalies.extend(result.anomalies)
                rules_used.append(result.rule_id)
                
                # Record performance metrics if report_id provided
                if report_id:
                    _record_rule_performance(result, report_id)
                
                # Get rule name for better debug output
                try:
                    rule = Rule.query.get(result.rule_id)
                    rule_name = rule.name if rule else f"Unknown Rule {result.rule_id}"
                    print(f"Rule {result.rule_id} ({rule_name}): {len(result.anomalies)} anomalies found in {result.execution_time_ms}ms")
                except Exception:
                    print(f"Rule {result.rule_id}: {len(result.anomalies)} anomalies found in {result.execution_time_ms}ms")
            else:
                try:
                    rule = Rule.query.get(result.rule_id)
                    rule_name = rule.name if rule else f"Unknown Rule {result.rule_id}"
                    print(f"Rule {result.rule_id} ({rule_name}) failed: {result.error_message}")
                except Exception:
                    print(f"Rule {result.rule_id} failed: {result.error_message}")
        
        # Update report with rules used
        if report_id and rules_used:
            _update_report_rules_used(report_id, rules_used)
        
        # Remove duplicates and prioritize
        unique_anomalies = _deduplicate_and_prioritize(all_anomalies)
        
        print(f"Enhanced engine finished. Found {len(unique_anomalies)} unique anomalies using {len(rules_used)} rules.")
        
        return unique_anomalies
        
    except Exception as e:
        print(f"Error in database rules engine: {e}")
        print(f"Database rules engine failed. Please ensure:")
        print("1. Database is properly connected and migrated")
        print("2. Rules are properly configured in the database")
        print("3. All required environment variables are set")
        
        # Check if we have any fallback environment variable set
        import os
        allow_excel_fallback = os.getenv('ALLOW_EXCEL_FALLBACK', 'false').lower() == 'true'
        
        if allow_excel_fallback:
            print("ALLOW_EXCEL_FALLBACK is enabled. Attempting Excel fallback...")
            try:
                from main import run_engine as legacy_run_engine
                import pandas as pd
                
                # Look for fallback rules file
                rules_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse_rules.xlsx.backup')
                if os.path.exists(rules_path):
                    print(f"Using Excel fallback rules from: {rules_path}")
                    rules_df = pd.read_excel(rules_path)
                    import argparse
                    args = argparse.Namespace(debug=False, floating_time=8, straggler_ratio=0.85, stuck_ratio=0.80, stuck_time=6)
                    return legacy_run_engine(inventory_df, rules_df, args)
                else:
                    print("No Excel fallback file found.")
                    raise Exception("No fallback rules available")
            except Exception as fallback_error:
                print(f"Excel fallback also failed: {fallback_error}")
                raise Exception(f"Both database and Excel fallback failed: {e}, {fallback_error}")
        else:
            print("Excel fallback is disabled. Set ALLOW_EXCEL_FALLBACK=true to enable.")
            raise Exception(f"Database rules engine failed and fallback is disabled: {e}")

def _record_rule_performance(result, report_id: int):
    """Record rule performance metrics"""
    try:
        performance = RulePerformance(
            rule_id=result.rule_id,
            report_id=report_id,
            anomalies_detected=len(result.anomalies),
            execution_time_ms=result.execution_time_ms,
            timestamp=datetime.utcnow()
        )
        db.session.add(performance)
        db.session.flush()  # Don't commit yet, let the main transaction handle it
    except Exception as e:
        print(f"Warning: Could not record performance for rule {result.rule_id}: {e}")

def _update_report_rules_used(report_id: int, rules_used: List[int]):
    """Update analysis report with list of rules used"""
    try:
        report = AnalysisReport.query.get(report_id)
        if report:
            # Assuming rules_used column was added in migration
            if hasattr(report, 'rules_used'):
                report.rules_used = json.dumps(rules_used)
            db.session.flush()
    except Exception as e:
        print(f"Warning: Could not update report rules: {e}")

def _deduplicate_and_prioritize(anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate anomalies and sort by priority
    """
    # Remove duplicates based on pallet_id and anomaly_type
    unique_anomalies = []
    seen_anomalies = set()
    
    for anomaly in anomalies:
        # Create unique signature
        signature = (anomaly.get('pallet_id'), anomaly.get('anomaly_type'))
        
        if signature not in seen_anomalies:
            unique_anomalies.append(anomaly)
            seen_anomalies.add(signature)
    
    # Sort by priority
    priority_map = {'VERY_HIGH': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    unique_anomalies.sort(
        key=lambda x: priority_map.get(x.get('priority', 'MEDIUM'), 2), 
        reverse=True
    )
    
    return unique_anomalies

def get_available_rules() -> List[Dict[str, Any]]:
    """
    Get list of available rules for UI selection
    """
    try:
        rules = Rule.query.filter_by(is_active=True).order_by(
            Rule.priority.desc(), Rule.name
        ).all()
        
        rules_by_category = {}
        for rule in rules:
            category_name = rule.category.name if rule.category else 'UNCATEGORIZED'
            
            if category_name not in rules_by_category:
                rules_by_category[category_name] = {
                    'category_name': category_name,
                    'display_name': rule.category.display_name if rule.category else 'Uncategorized',
                    'priority': rule.category.priority if rule.category else 999,
                    'rules': []
                }
            
            rules_by_category[category_name]['rules'].append({
                'id': rule.id,
                'name': rule.name,
                'description': rule.description,
                'rule_type': rule.rule_type,
                'priority': rule.priority,
                'is_default': rule.is_default,
                'parameters': rule.get_parameters()
            })
        
        # Sort categories by priority
        sorted_categories = sorted(
            rules_by_category.values(), 
            key=lambda x: x['priority']
        )
        
        return sorted_categories
        
    except Exception as e:
        print(f"Error getting available rules: {e}")
        return []

def test_rule_with_sample_data(rule_id: int, sample_data_path: str = None) -> Dict[str, Any]:
    """
    Test a specific rule with sample data
    
    Args:
        rule_id: ID of rule to test
        sample_data_path: Path to sample data file (optional)
    
    Returns:
        Test results dictionary
    """
    try:
        # Get the rule
        rule = Rule.query.get(rule_id)
        if not rule:
            return {'error': f'Rule {rule_id} not found'}
        
        # Load sample data
        if sample_data_path and os.path.exists(sample_data_path):
            inventory_df = pd.read_excel(sample_data_path)
        else:
            # Create minimal sample data
            inventory_df = pd.DataFrame({
                'pallet_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
                'location': ['RECEIVING', 'AISLE-A1', 'RECEIVING', 'FINAL-B2', 'AISLE-C3'],
                'creation_date': [
                    datetime.now() - timedelta(hours=10),  # Old pallet
                    datetime.now() - timedelta(hours=2),   # Recent pallet
                    datetime.now() - timedelta(hours=12),  # Very old pallet
                    datetime.now() - timedelta(hours=1),   # Fresh pallet
                    datetime.now() - timedelta(hours=6)    # Medium age pallet
                ],
                'receipt_number': ['R001', 'R002', 'R001', 'R002', 'R003'],
                'description': ['Frozen Food', 'General Item', 'Refrigerated', 'Ambient Product', 'General Item']
            })
        
        # Initialize rule engine and test
        rule_engine = RuleEngine(db.session)
        result = rule_engine.evaluate_rule(rule, inventory_df)
        
        return {
            'rule_id': rule_id,
            'rule_name': rule.name,
            'test_data_rows': len(inventory_df),
            'anomalies_found': len(result.anomalies),
            'execution_time_ms': result.execution_time_ms,
            'success': result.success,
            'error_message': result.error_message,
            'sample_anomalies': result.anomalies[:3],  # First 3 for preview
            'detection_rate': len(result.anomalies) / len(inventory_df) * 100 if len(inventory_df) > 0 else 0
        }
        
    except Exception as e:
        return {'error': f'Error testing rule: {str(e)}'}

def create_rule_from_template(template_id: int, parameters: Dict[str, Any], 
                            user_id: int, name: str = None) -> Dict[str, Any]:
    """
    Create a new rule from a template
    
    Args:
        template_id: ID of template to use
        parameters: Parameter values for the template
        user_id: ID of user creating the rule
        name: Custom name for the rule (optional)
    
    Returns:
        Result dictionary with new rule info or error
    """
    try:
        from models import RuleTemplate
        
        # Get the template
        template = RuleTemplate.query.get(template_id)
        if not template:
            return {'error': f'Template {template_id} not found'}
        
        # Parse template conditions
        template_conditions = template.get_template_conditions()
        
        # Replace placeholders with parameters
        conditions = _replace_template_placeholders(template_conditions, parameters)
        
        # Create new rule
        rule = Rule(
            name=name or f"{template.name} - Custom",
            description=f"Created from template: {template.name}",
            category_id=template.category_id,
            rule_type=template.name.upper().replace(' ', '_'),
            priority='MEDIUM',
            is_active=True,
            created_by=user_id
        )
        
        rule.set_conditions(conditions)
        rule.set_parameters(parameters)
        
        db.session.add(rule)
        db.session.commit()
        
        # Update template usage count
        template.usage_count += 1
        db.session.commit()
        
        return {
            'success': True,
            'rule_id': rule.id,
            'rule': rule.to_dict()
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error creating rule from template: {str(e)}'}

def _replace_template_placeholders(template_conditions: Dict[str, Any], 
                                 parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replace template placeholders with actual parameter values
    """
    conditions = template_conditions.copy()
    
    def replace_in_value(value):
        if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
            placeholder = value[2:-2]  # Remove {{ and }}
            return parameters.get(placeholder, value)
        elif isinstance(value, dict):
            return {k: replace_in_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [replace_in_value(item) for item in value]
        else:
            return value
    
    return {k: replace_in_value(v) for k, v in conditions.items()}

# Backward compatibility functions

def run_engine(inventory_df: pd.DataFrame, rules_df: pd.DataFrame, args: argparse.Namespace):
    """
    Backward compatibility wrapper for the original run_engine function
    """
    # Check if database rules are available and should be preferred
    try:
        active_rules_count = Rule.query.filter_by(is_active=True).count()
        if active_rules_count > 0:
            print("Using enhanced database rules engine...")
            return run_enhanced_engine(inventory_df, rules_df, args, use_database_rules=True)
    except Exception as e:
        print(f"Database rules not available, falling back to Excel rules: {e}")
    
    # Fall back to original Excel-based engine
    print("Using legacy Excel rules engine...")
    return run_enhanced_engine(inventory_df, rules_df, args, use_database_rules=False)

def summarize_anomalies_by_location(anomalies):
    """
    Backward compatibility: same function as in original main.py
    """
    from main import summarize_anomalies_by_location as legacy_summarize
    return legacy_summarize(anomalies)

# Command line interface for testing
def main():
    """
    Command line interface for testing the enhanced engine
    """
    parser = argparse.ArgumentParser(
        description="Enhanced Warehouse Intelligence Engine: Supports both Excel and database rules.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('-i', '--inventory', default='data/inventory_report.xlsx', 
                       help='Path to the inventory .xlsx file. (Default: data/inventory_report.xlsx)')
    parser.add_argument('--use-database', action='store_true', 
                       help='Use database rules instead of Excel rules')
    parser.add_argument('--rule-ids', type=str, 
                       help='Comma-separated list of rule IDs to use (database mode only)')
    parser.add_argument('--test-rule', type=int, 
                       help='Test a specific rule ID with sample data')
    parser.add_argument('--list-rules', action='store_true', 
                       help='List all available database rules')
    
    args = parser.parse_args()
    
    # Handle special operations
    if args.list_rules:
        print("\nAvailable Rules:")
        print("=" * 50)
        categories = get_available_rules()
        for category in categories:
            print(f"\n{category['display_name']} (Priority: {category['priority']})")
            print("-" * len(category['display_name']))
            for rule in category['rules']:
                status = "✓" if rule['is_default'] else "●"
                print(f"  {status} [{rule['id']}] {rule['name']} ({rule['priority']})")
                if rule['description']:
                    print(f"      {rule['description']}")
        return
    
    if args.test_rule:
        print(f"\nTesting Rule {args.test_rule}:")
        print("=" * 50)
        result = test_rule_with_sample_data(args.test_rule)
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Rule: {result['rule_name']}")
            print(f"Test Data: {result['test_data_rows']} rows")
            print(f"Anomalies Found: {result['anomalies_found']}")
            print(f"Detection Rate: {result['detection_rate']:.1f}%")
            print(f"Execution Time: {result['execution_time_ms']}ms")
            if result['sample_anomalies']:
                print("\nSample Anomalies:")
                for i, anomaly in enumerate(result['sample_anomalies'], 1):
                    print(f"  {i}. {anomaly.get('anomaly_type')}: {anomaly.get('details')}")
        return
    
    # Regular analysis
    print("Starting Enhanced Warehouse Intelligence Engine...")
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    inventory_file = os.path.join(base_path, args.inventory)
    
    if not os.path.exists(inventory_file):
        print(f"Error: Inventory file not found: {inventory_file}")
        return
    
    # Load inventory data
    inventory_df = pd.read_excel(inventory_file, parse_dates=['creation_date'])
    print(f"Inventory file '{os.path.basename(inventory_file)}' loaded.")
    
    # Parse rule IDs if provided
    rule_ids = None
    if args.rule_ids:
        try:
            rule_ids = [int(x.strip()) for x in args.rule_ids.split(',')]
            print(f"Using specific rules: {rule_ids}")
        except ValueError:
            print("Error: Invalid rule IDs format. Use comma-separated integers.")
            return
    
    # Run analysis
    anomalies = run_enhanced_engine(
        inventory_df, 
        use_database_rules=args.use_database,
        rule_ids=rule_ids
    )
    
    # Display results
    print("\n\n" + "="*50)
    print("FINAL ANOMALY REPORT (PRIORITIZED)")
    print("="*50)
    
    if not anomalies:
        print("\nNo anomalies found! Everything is in order.\n")
        return
        
    for anomaly in anomalies:
        print(f"\n[ PRIORITY: {anomaly.get('priority', 'UNKNOWN')} ]")
        print(f"  - TYPE:      {anomaly.get('anomaly_type', 'Unknown')}")
        print(f"  - PALLET:    {anomaly.get('pallet_id', 'N/A')}")
        print(f"  - LOCATION:  {anomaly.get('location', 'N/A')}")
        print(f"  - DETAILS:   {anomaly.get('details', 'No details available')}")
        if 'rule_name' in anomaly:
            print(f"  - RULE:      {anomaly['rule_name']}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    # Set up Flask app context for database access
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from app import app
    with app.app_context():
        main()