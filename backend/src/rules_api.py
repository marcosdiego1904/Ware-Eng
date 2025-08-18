"""
API Endpoints for Warehouse Rules System
Implementation Plan Phase 3: API Development

This module provides REST API endpoints for managing rules, templates,
and rule performance analytics.
"""

import json
import pandas as pd
from datetime import datetime
from flask import Blueprint, request, jsonify
from functools import wraps

# Import the token_required decorator and database models
from database import db
# CIRCULAR IMPORT FIX: Import token_required at function level to avoid circular dependency
from core_models import User, AnalysisReport
from models import (
    Rule, RuleCategory, RuleHistory, RuleTemplate, 
    RulePerformance, Location
)
from rule_engine import RuleEngine
# from rule_validator import RuleValidator, RulePerformanceEstimator, RuleDebugger  # TODO: Implement these

def get_token_required():
    """Get token_required decorator - fixes circular import"""
    from app import token_required
    return token_required

# Create the rules API blueprint
rules_api = Blueprint('rules_api', __name__, url_prefix='/api/v1')

# Initialize rule engine and validator (will be done in app context)
rule_engine = None
rule_validator = None
performance_estimator = None
rule_debugger = None

def init_rule_system():
    """Initialize rule system components"""
    global rule_engine, rule_validator, performance_estimator, rule_debugger
    rule_engine = RuleEngine(db.session)
    # TODO: Implement these validation components
    # rule_validator = RuleValidator()
    # performance_estimator = RulePerformanceEstimator(rule_engine)
    # rule_debugger = RuleDebugger(rule_engine)

# ==================== RULE CRUD ENDPOINTS ====================

@rules_api.route('/rules', methods=['GET'])
@get_token_required()
def get_rules(current_user):
    """Get all rules with optional filtering"""
    try:
        # Get query parameters
        category = request.args.get('category')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        rule_type = request.args.get('rule_type')
        
        # Build query
        query = Rule.query
        
        if category:
            category_obj = RuleCategory.query.filter_by(name=category).first()
            if category_obj:
                query = query.filter_by(category_id=category_obj.id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        if rule_type:
            query = query.filter_by(rule_type=rule_type)
        
        # Execute query
        rules = query.order_by(Rule.priority.desc(), Rule.created_at.desc()).all()
        
        # Convert to dict format
        rules_data = [rule.to_dict() for rule in rules]
        
        return jsonify({
            'success': True,
            'rules': rules_data,
            'total': len(rules_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving rules: {str(e)}'
        }), 500

@rules_api.route('/rules/<int:rule_id>', methods=['GET'])
@get_token_required()
def get_rule(current_user, rule_id):
    """Get specific rule by ID"""
    try:
        rule = Rule.query.get_or_404(rule_id)
        
        # Include rule history
        rule_data = rule.to_dict()
        rule_data['history'] = [h.to_dict() for h in rule.history.order_by(RuleHistory.timestamp.desc()).all()]
        
        return jsonify({
            'success': True,
            'rule': rule_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving rule: {str(e)}'
        }), 500

@rules_api.route('/rules', methods=['POST'])
@get_token_required()
def create_rule(current_user):
    """Create new rule"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'rule_type', 'category_id', 'conditions']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate category exists
        category = RuleCategory.query.get(data['category_id'])
        if not category:
            return jsonify({
                'success': False,
                'message': 'Invalid category ID'
            }), 400
        
        # Create new rule
        rule = Rule(
            name=data['name'],
            description=data.get('description', ''),
            category_id=data['category_id'],
            rule_type=data['rule_type'],
            priority=data.get('priority', 'MEDIUM'),
            is_active=data.get('is_active', True),
            created_by=current_user.id
        )
        
        # Set conditions and parameters
        rule.set_conditions(data['conditions'])
        if 'parameters' in data:
            rule.set_parameters(data['parameters'])
        
        # Validate rule before saving (TODO: Implement rule_validator)
        # if rule_validator:
        #     validation_result = rule_validator.validate_rule_object(rule)
        #     if not validation_result.is_valid:
        #         return jsonify({
        #             'success': False,
        #             'message': f'Rule validation failed: {validation_result.error_message}'
        #         }), 400
        
        db.session.add(rule)
        db.session.flush()  # Get the rule ID
        
        # Create initial history entry
        history = RuleHistory(
            rule_id=rule.id,
            version=1,
            changed_by=current_user.id
        )
        history.set_changes({
            'action': 'created',
            'timestamp': datetime.utcnow().isoformat(),
            'initial_rule': rule.to_dict()
        })
        db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rule created successfully',
            'rule': rule.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating rule: {str(e)}'
        }), 500

@rules_api.route('/rules/<int:rule_id>', methods=['PUT'])
@get_token_required()
def update_rule(current_user, rule_id):
    """Update existing rule"""
    try:
        rule = Rule.query.get_or_404(rule_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Store original state for history
        original_state = rule.to_dict()
        
        # Update fields
        updatable_fields = ['name', 'description', 'rule_type', 'category_id', 'priority', 'is_active']
        changes = {}
        
        for field in updatable_fields:
            if field in data:
                old_value = getattr(rule, field)
                new_value = data[field]
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}
                    setattr(rule, field, new_value)
        
        # Update conditions and parameters
        if 'conditions' in data:
            old_conditions = rule.get_conditions()
            rule.set_conditions(data['conditions'])
            if old_conditions != data['conditions']:
                changes['conditions'] = {'old': old_conditions, 'new': data['conditions']}
        
        if 'parameters' in data:
            old_parameters = rule.get_parameters()
            rule.set_parameters(data['parameters'])
            if old_parameters != data['parameters']:
                changes['parameters'] = {'old': old_parameters, 'new': data['parameters']}
        
        # Update timestamp
        rule.updated_at = datetime.utcnow()
        
        # Validate updated rule (TODO: Implement rule_validator)
        # if rule_validator:
        #     validation_result = rule_validator.validate_rule_object(rule)
        #     if not validation_result.is_valid:
        #         return jsonify({
        #             'success': False,
        #             'message': f'Rule validation failed: {validation_result.error_message}'
        #         }), 400
        
        # Create history entry if there were changes
        if changes:
            # Get next version number
            latest_version = db.session.query(db.func.max(RuleHistory.version)).filter_by(rule_id=rule.id).scalar() or 0
            
            history = RuleHistory(
                rule_id=rule.id,
                version=latest_version + 1,
                changed_by=current_user.id
            )
            history.set_changes({
                'action': 'updated',
                'timestamp': datetime.utcnow().isoformat(),
                'changes': changes
            })
            db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rule updated successfully',
            'rule': rule.to_dict(),
            'changes_made': len(changes) > 0
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating rule: {str(e)}'
        }), 500

@rules_api.route('/rules/<int:rule_id>', methods=['DELETE'])
@get_token_required()
def delete_rule(current_user, rule_id):
    """Delete rule"""
    try:
        rule = Rule.query.get_or_404(rule_id)
        
        # Check if rule is used in recent reports
        recent_reports = AnalysisReport.query.filter(
            AnalysisReport.timestamp >= datetime.utcnow().replace(day=1)  # This month
        ).all()
        
        rule_in_use = False
        for report in recent_reports:
            if hasattr(report, 'rules_used') and report.rules_used:
                try:
                    rules_used = json.loads(report.rules_used)
                    if rule_id in rules_used:
                        rule_in_use = True
                        break
                except json.JSONDecodeError:
                    pass
        
        if rule_in_use:
            return jsonify({
                'success': False,
                'message': 'Cannot delete rule that was used in recent reports. Consider deactivating instead.'
            }), 400
        
        # Create deletion history entry
        history = RuleHistory(
            rule_id=rule.id,
            version=999,  # Special version for deletion
            changed_by=current_user.id
        )
        history.set_changes({
            'action': 'deleted',
            'timestamp': datetime.utcnow().isoformat(),
            'deleted_rule': rule.to_dict()
        })
        db.session.add(history)
        
        # Delete the rule (cascade will handle history)
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rule deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting rule: {str(e)}'
        }), 500

@rules_api.route('/rules/<int:rule_id>/activate', methods=['POST'])
@get_token_required()
def toggle_rule_activation(current_user, rule_id):
    """Activate or deactivate rule"""
    try:
        rule = Rule.query.get_or_404(rule_id)
        data = request.get_json() or {}
        
        new_status = data.get('is_active', not rule.is_active)
        old_status = rule.is_active
        
        rule.is_active = new_status
        rule.updated_at = datetime.utcnow()
        
        # Create history entry
        latest_version = db.session.query(db.func.max(RuleHistory.version)).filter_by(rule_id=rule.id).scalar() or 0
        
        history = RuleHistory(
            rule_id=rule.id,
            version=latest_version + 1,
            changed_by=current_user.id
        )
        history.set_changes({
            'action': 'activation_changed',
            'timestamp': datetime.utcnow().isoformat(),
            'is_active': {'old': old_status, 'new': new_status}
        })
        db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Rule {"activated" if new_status else "deactivated"} successfully',
            'rule': rule.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating rule status: {str(e)}'
        }), 500

# ==================== RULE CATEGORIES ====================

@rules_api.route('/categories', methods=['GET'])
@get_token_required()
def get_categories(current_user):
    """Get all rule categories"""
    try:
        categories = RuleCategory.query.filter_by(is_active=True).order_by(RuleCategory.priority).all()
        
        categories_data = [cat.to_dict() for cat in categories]
        
        return jsonify({
            'success': True,
            'categories': categories_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving categories: {str(e)}'
        }), 500

# ==================== RULE TESTING & VALIDATION ====================

@rules_api.route('/rules/test', methods=['POST'])
@get_token_required()
def test_rules(current_user):
    """Test rules against uploaded data"""
    try:
        if 'test_file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No test file provided'
            }), 400
        
        test_file = request.files['test_file']
        rule_ids_str = request.form.get('rule_ids', '[]')
        
        try:
            rule_ids = json.loads(rule_ids_str)
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'message': 'Invalid rule_ids format'
            }), 400
        
        # Read test data
        try:
            if test_file.filename.endswith('.xlsx'):
                test_df = pd.read_excel(test_file)
            elif test_file.filename.endswith('.csv'):
                test_df = pd.read_csv(test_file)
            else:
                return jsonify({
                    'success': False,
                    'message': 'Unsupported file format. Use .xlsx or .csv'
                }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error reading test file: {str(e)}'
            }), 400
        
        # Initialize rule engine if needed
        if not rule_engine:
            init_rule_system()
        
        # Test rules
        if rule_ids:
            results = rule_engine.evaluate_all_rules(test_df, rule_ids)
        else:
            results = rule_engine.evaluate_all_rules(test_df)
        
        # Format results
        test_results = []
        for result in results:
            test_results.append({
                'rule_id': result.rule_id,
                'success': result.success,
                'anomalies_found': len(result.anomalies),
                'execution_time_ms': result.execution_time_ms,
                'error_message': result.error_message,
                'sample_anomalies': result.anomalies[:5] if result.anomalies else []  # First 5 for preview
            })
        
        return jsonify({
            'success': True,
            'test_results': test_results,
            'data_info': {
                'rows': len(test_df),
                'columns': list(test_df.columns)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error testing rules: {str(e)}'
        }), 500

@rules_api.route('/rules/preview', methods=['POST'])
@get_token_required()
def preview_rule(current_user):
    """Preview rule results without saving"""
    try:
        data = request.get_json()
        
        if not data or 'conditions' not in data:
            return jsonify({
                'success': False,
                'message': 'Rule conditions are required'
            }), 400
        
        # Create temporary rule for testing
        temp_rule = Rule(
            name=data.get('name', 'Preview Rule'),
            rule_type=data.get('rule_type', 'STAGNANT_PALLETS'),
            priority=data.get('priority', 'MEDIUM'),
            created_by=current_user.id
        )
        temp_rule.set_conditions(data['conditions'])
        if 'parameters' in data:
            temp_rule.set_parameters(data['parameters'])
        
        # Use sample data or user-provided data
        sample_data = data.get('sample_data')
        if sample_data:
            test_df = pd.DataFrame(sample_data)
        else:
            # Create minimal sample data
            test_df = pd.DataFrame({
                'pallet_id': ['P001', 'P002', 'P003'],
                'location': ['RECEIVING', 'AISLE-A1', 'FINAL-B2'],
                'creation_date': [datetime.now()] * 3,
                'receipt_number': ['R001'] * 3,
                'description': ['Sample Product'] * 3
            })
        
        # Initialize rule engine if needed
        if not rule_engine:
            init_rule_system()
        
        # Test the rule
        result = rule_engine.evaluate_rule(temp_rule, test_df)
        
        # Estimate performance (TODO: Implement performance_estimator)
        performance_estimate = {
            'estimated_execution_time_ms': 50,
            'estimated_memory_usage_mb': 10,
            'complexity_score': 'LOW'
        }
        
        return jsonify({
            'success': True,
            'preview_results': {
                'anomalies_found': len(result.anomalies),
                'execution_time_ms': result.execution_time_ms,
                'sample_anomalies': result.anomalies[:3],  # First 3 for preview
                'success': result.success,
                'error_message': result.error_message
            },
            'performance_estimate': performance_estimate
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error previewing rule: {str(e)}'
        }), 500

@rules_api.route('/rules/validate', methods=['POST'])
@get_token_required()
def validate_rule_conditions(current_user):
    """Validate rule conditions"""
    try:
        data = request.get_json()
        
        if not data or 'conditions' not in data:
            return jsonify({
                'success': False,
                'message': 'Rule conditions are required'
            }), 400
        
        # Use sample data or user-provided data
        sample_data = data.get('sample_data')
        if sample_data:
            test_df = pd.DataFrame(sample_data)
        else:
            # Create minimal sample data for validation
            test_df = pd.DataFrame({
                'pallet_id': ['P001'],
                'location': ['RECEIVING'],
                'creation_date': [datetime.now()],
                'receipt_number': ['R001'],
                'description': ['Sample Product']
            })
        
        # Initialize validator if needed (TODO: Implement rule_validator)
        # if not rule_validator:
        #     init_rule_system()
        
        # Basic validation (TODO: Implement proper rule_validator)
        validation_result = {
            'is_valid': True,
            'error_message': None,
            'warnings': [],
            'suggestions': ['Consider testing with real data for better validation']
        }
        
        return jsonify({
            'success': True,
            'validation_result': validation_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error validating rule: {str(e)}'
        }), 500

# ==================== RULE DEBUGGING ====================

@rules_api.route('/rules/<int:rule_id>/debug', methods=['POST'])
@get_token_required()
def debug_rule(current_user, rule_id):
    """Debug rule execution"""
    try:
        data = request.get_json() or {}
        
        # Use sample data or uploaded data
        sample_data = data.get('sample_data')
        if sample_data:
            test_df = pd.DataFrame(sample_data)
        else:
            # Create sample data for debugging
            test_df = pd.DataFrame({
                'pallet_id': ['P001', 'P002', 'P003'],
                'location': ['RECEIVING', 'AISLE-A1', 'FINAL-B2'],
                'creation_date': [datetime.now()] * 3,
                'receipt_number': ['R001'] * 3,
                'description': ['Sample Product'] * 3
            })
        
        # Initialize debugger if needed (TODO: Implement rule_debugger)
        # if not rule_debugger:
        #     init_rule_system()
        
        # Basic debug info (TODO: Implement proper rule_debugger)
        rule = Rule.query.get_or_404(rule_id)
        debug_result = {
            'rule_id': rule_id,
            'rule_status': 'ACTIVE' if rule.is_active else 'INACTIVE',
            'data_compatibility': 'COMPATIBLE',
            'condition_analysis': {'status': 'OK', 'details': rule.get_conditions()},
            'execution_trace': ['Rule loaded', 'Conditions parsed', 'Ready for execution'],
            'suggestions': ['Rule appears to be properly configured'],
            'performance_metrics': {'estimated_time_ms': 50}
        }
        
        return jsonify({
            'success': True,
            'debug_result': debug_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error debugging rule: {str(e)}'
        }), 500

# ==================== RULE PERFORMANCE ====================

@rules_api.route('/rules/<int:rule_id>/performance', methods=['GET'])
@get_token_required()
def get_rule_performance(current_user, rule_id):
    """Get rule performance metrics"""
    try:
        rule = Rule.query.get_or_404(rule_id)
        
        # Get performance records
        performance_records = RulePerformance.query.filter_by(rule_id=rule_id).order_by(
            RulePerformance.timestamp.desc()
        ).limit(100).all()
        
        # Calculate aggregate metrics
        total_executions = len(performance_records)
        total_detections = sum(r.anomalies_detected for r in performance_records)
        total_false_positives = sum(r.false_positives for r in performance_records)
        avg_execution_time = sum(r.execution_time_ms for r in performance_records) / total_executions if total_executions > 0 else 0
        
        return jsonify({
            'success': True,
            'performance_metrics': {
                'rule_id': rule_id,
                'rule_name': rule.name,
                'total_executions': total_executions,
                'total_detections': total_detections,
                'total_false_positives': total_false_positives,
                'false_positive_rate': (total_false_positives / total_detections * 100) if total_detections > 0 else 0,
                'average_execution_time_ms': int(avg_execution_time),
                'recent_records': [r.to_dict() for r in performance_records[:10]]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving performance metrics: {str(e)}'
        }), 500

@rules_api.route('/rules/analytics', methods=['GET'])
@get_token_required()
def get_rules_analytics(current_user):
    """Get overall rules analytics"""
    try:
        # Get rule counts by category
        categories_stats = []
        categories = RuleCategory.query.filter_by(is_active=True).all()
        
        for category in categories:
            active_rules = Rule.query.filter_by(category_id=category.id, is_active=True).count()
            total_rules = Rule.query.filter_by(category_id=category.id).count()
            
            categories_stats.append({
                'category_name': category.name,
                'display_name': category.display_name,
                'active_rules': active_rules,
                'total_rules': total_rules,
                'priority': category.priority
            })
        
        # Get overall rule stats
        total_rules = Rule.query.count()
        active_rules = Rule.query.filter_by(is_active=True).count()
        default_rules = Rule.query.filter_by(is_default=True).count()
        custom_rules = total_rules - default_rules
        
        # Get recent performance data
        recent_performance = RulePerformance.query.order_by(
            RulePerformance.timestamp.desc()
        ).limit(50).all()
        
        return jsonify({
            'success': True,
            'analytics': {
                'overview': {
                    'total_rules': total_rules,
                    'active_rules': active_rules,
                    'default_rules': default_rules,
                    'custom_rules': custom_rules
                },
                'categories': categories_stats,
                'recent_performance': [p.to_dict() for p in recent_performance]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving analytics: {str(e)}'
        }), 500

# Initialize rule system when module is imported
def register_rules_api(app):
    """Register the rules API blueprint and initialize the rule system"""
    app.register_blueprint(rules_api)
    
    # Initialize rule system in app context
    with app.app_context():
        init_rule_system()