"""
Rule Validation and Debugging Tools
Implementation Plan Phase 2: Rule Validation & Performance

This module provides tools for validating rules, debugging execution,
and analyzing rule performance.
"""

import json
import time
import traceback
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

from models import Rule, RulePerformance
from rule_engine import RuleEngine

@dataclass
class ValidationResult:
    """Result of rule validation"""
    is_valid: bool
    error_message: Optional[str] = None
    warnings: List[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.suggestions is None:
            self.suggestions = []

@dataclass
class DebugResult:
    """Result of rule debugging"""
    rule_id: int
    rule_status: str
    data_compatibility: Dict[str, Any]
    condition_analysis: Dict[str, Any]
    execution_trace: List[str]
    suggestions: List[str]
    performance_metrics: Dict[str, Any]

class RuleValidator:
    """
    Validates rule syntax, logic, and compatibility with data
    """
    
    def __init__(self):
        self.required_columns = [
            'pallet_id', 'location', 'creation_date', 
            'receipt_number', 'description'
        ]
    
    def validate_conditions(self, rule_conditions: str, sample_data: pd.DataFrame) -> ValidationResult:
        """
        Validates rule conditions against sample data
        
        Args:
            rule_conditions: JSON string of rule conditions
            sample_data: Sample inventory data for validation
        
        Returns:
            ValidationResult with validation status and messages
        """
        try:
            # Parse JSON
            conditions = json.loads(rule_conditions)
            
            if not isinstance(conditions, dict):
                return ValidationResult(
                    is_valid=False,
                    error_message="Rule conditions must be a JSON object"
                )
            
            warnings = []
            suggestions = []
            
            # Check field references
            data_columns = sample_data.columns.tolist()
            for key, value in conditions.items():
                if key.endswith('_field') and value not in data_columns:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Field '{value}' not found in data columns. Available: {data_columns}"
                    )
            
            # Validate specific condition types
            validation_checks = [
                self._validate_time_conditions(conditions, warnings, suggestions),
                self._validate_location_conditions(conditions, data_columns, warnings, suggestions),
                self._validate_threshold_conditions(conditions, warnings, suggestions),
                self._validate_pattern_conditions(conditions, warnings, suggestions)
            ]
            
            # Check if any validation failed
            for check_result in validation_checks:
                if not check_result:
                    return ValidationResult(
                        is_valid=False,
                        error_message="One or more condition validations failed",
                        warnings=warnings,
                        suggestions=suggestions
                    )
            
            # Check data compatibility
            compatibility_result = self._check_data_compatibility(conditions, sample_data)
            if compatibility_result['warnings']:
                warnings.extend(compatibility_result['warnings'])
            if compatibility_result['suggestions']:
                suggestions.extend(compatibility_result['suggestions'])
            
            return ValidationResult(
                is_valid=True,
                warnings=warnings,
                suggestions=suggestions
            )
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid JSON format: {str(e)}"
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Validation error: {str(e)}"
            )
    
    def _validate_time_conditions(self, conditions: Dict, warnings: List[str], suggestions: List[str]) -> bool:
        """Validate time-related conditions"""
        time_fields = ['time_threshold_hours', 'time_threshold_minutes']
        
        for field in time_fields:
            if field in conditions:
                value = conditions[field]
                if not isinstance(value, (int, float)) or value <= 0:
                    warnings.append(f"Time threshold '{field}' should be a positive number")
                    return False
                
                if field == 'time_threshold_hours' and value > 72:
                    warnings.append(f"Time threshold of {value} hours seems very high")
                    suggestions.append("Consider if such a long threshold is intentional")
                
                if field == 'time_threshold_minutes' and value > 1440:
                    warnings.append(f"Time threshold of {value} minutes is over 24 hours")
                    suggestions.append("Consider using hours instead of minutes for clarity")
        
        return True
    
    def _validate_location_conditions(self, conditions: Dict, data_columns: List[str], 
                                    warnings: List[str], suggestions: List[str]) -> bool:
        """Validate location-related conditions"""
        if 'location_types' in conditions:
            location_types = conditions['location_types']
            valid_types = ['RECEIVING', 'FINAL', 'TRANSITIONAL', 'UNKNOWN', 'MISSING']
            
            if not isinstance(location_types, list):
                warnings.append("location_types should be a list")
                return False
            
            for loc_type in location_types:
                if loc_type not in valid_types:
                    warnings.append(f"Unknown location type: '{loc_type}'. Valid types: {valid_types}")
                    suggestions.append("Use standard location types for better compatibility")
        
        if 'location_pattern' in conditions:
            pattern = conditions['location_pattern']
            if not isinstance(pattern, str):
                warnings.append("location_pattern should be a string")
                return False
            
            # Check if pattern contains wildcard
            if '*' not in pattern and '?' not in pattern:
                suggestions.append("Consider using wildcards (*) in location patterns for flexibility")
        
        return True
    
    def _validate_threshold_conditions(self, conditions: Dict, warnings: List[str], suggestions: List[str]) -> bool:
        """Validate threshold-related conditions"""
        threshold_fields = ['completion_threshold', 'capacity_threshold']
        
        for field in threshold_fields:
            if field in conditions:
                value = conditions[field]
                if not isinstance(value, (int, float)):
                    warnings.append(f"Threshold '{field}' should be a number")
                    return False
                
                if 'completion' in field or 'capacity' in field:
                    if not 0 <= value <= 1:
                        warnings.append(f"Threshold '{field}' should be between 0 and 1 (percentage)")
                        return False
                    
                    if value < 0.1:
                        suggestions.append(f"Very low threshold ({value}) may generate many false positives")
                    elif value > 0.95:
                        suggestions.append(f"Very high threshold ({value}) may miss important cases")
        
        return True
    
    def _validate_pattern_conditions(self, conditions: Dict, warnings: List[str], suggestions: List[str]) -> bool:
        """Validate pattern-related conditions"""
        pattern_fields = ['product_patterns', 'allowed_products']
        
        for field in pattern_fields:
            if field in conditions:
                patterns = conditions[field]
                if not isinstance(patterns, list):
                    warnings.append(f"Pattern field '{field}' should be a list")
                    return False
                
                for pattern in patterns:
                    if not isinstance(pattern, str):
                        warnings.append(f"Pattern '{pattern}' should be a string")
                        return False
                    
                    # Check for common pattern issues
                    if pattern == '*':
                        warnings.append("Wildcard-only pattern '*' matches everything - may be too broad")
                    elif not any(char in pattern for char in ['*', '?', '[', ']']):
                        suggestions.append(f"Pattern '{pattern}' has no wildcards - consider if exact match is intended")
        
        return True
    
    def _check_data_compatibility(self, conditions: Dict, sample_data: pd.DataFrame) -> Dict[str, List[str]]:
        """Check if conditions are compatible with the provided data"""
        warnings = []
        suggestions = []
        
        # Check data size
        if len(sample_data) < 10:
            warnings.append("Sample data is very small - validation may not be comprehensive")
            suggestions.append("Provide a larger sample dataset for better validation")
        
        # Check required columns
        missing_columns = [col for col in self.required_columns if col not in sample_data.columns]
        if missing_columns:
            warnings.append(f"Missing recommended columns: {missing_columns}")
            suggestions.append("Ensure all required columns are present for optimal rule performance")
        
        # Check data quality
        if 'creation_date' in sample_data.columns:
            null_dates = sample_data['creation_date'].isna().sum()
            if null_dates > 0:
                warnings.append(f"{null_dates} rows have missing creation_date")
                suggestions.append("Consider handling missing dates in your data preprocessing")
        
        if 'location' in sample_data.columns:
            null_locations = sample_data['location'].isna().sum()
            empty_locations = (sample_data['location'].astype(str).str.strip() == '').sum()
            if null_locations + empty_locations > 0:
                warnings.append(f"{null_locations + empty_locations} rows have missing/empty locations")
        
        return {'warnings': warnings, 'suggestions': suggestions}
    
    def validate_rule_object(self, rule: Rule) -> ValidationResult:
        """
        Validate a complete rule object
        
        Args:
            rule: Rule object to validate
        
        Returns:
            ValidationResult with validation status
        """
        warnings = []
        suggestions = []
        
        # Basic field validation
        if not rule.name or not rule.name.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Rule name is required"
            )
        
        if not rule.rule_type or not rule.rule_type.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Rule type is required"
            )
        
        if not rule.conditions:
            return ValidationResult(
                is_valid=False,
                error_message="Rule conditions are required"
            )
        
        # Validate conditions JSON
        try:
            conditions = json.loads(rule.conditions)
        except json.JSONDecodeError:
            return ValidationResult(
                is_valid=False,
                error_message="Rule conditions must be valid JSON"
            )
        
        # Check rule type compatibility
        valid_rule_types = [
            'STAGNANT_PALLETS', 'UNCOORDINATED_LOTS', 'OVERCAPACITY', 
            'INVALID_LOCATION', 'LOCATION_SPECIFIC_STAGNANT',
            'TEMPERATURE_ZONE_MISMATCH', 'DATA_INTEGRITY',
            'LOCATION_MAPPING_ERROR', 'MISSING_LOCATION',
            'PRODUCT_INCOMPATIBILITY'
        ]
        
        if rule.rule_type not in valid_rule_types:
            warnings.append(f"Unknown rule type: {rule.rule_type}")
            suggestions.append(f"Valid rule types: {valid_rule_types}")
        
        # Check priority
        valid_priorities = ['VERY_HIGH', 'HIGH', 'MEDIUM', 'LOW']
        if rule.priority not in valid_priorities:
            warnings.append(f"Invalid priority: {rule.priority}")
            suggestions.append(f"Valid priorities: {valid_priorities}")
        
        return ValidationResult(
            is_valid=True,
            warnings=warnings,
            suggestions=suggestions
        )

class RulePerformanceEstimator:
    """
    Estimates rule performance and effectiveness
    """
    
    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine
    
    def estimate(self, rule: Rule, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Estimate rule performance based on historical data
        
        Args:
            rule: Rule to estimate performance for
            historical_data: Historical inventory data
        
        Returns:
            Performance estimation metrics
        """
        return self.rule_engine.estimate_performance(rule, historical_data)
    
    def benchmark_rule(self, rule: Rule, test_datasets: List[pd.DataFrame]) -> Dict[str, Any]:
        """
        Benchmark rule performance across multiple datasets
        
        Args:
            rule: Rule to benchmark
            test_datasets: List of test datasets
        
        Returns:
            Benchmark results
        """
        results = []
        total_execution_time = 0
        total_detections = 0
        total_records = 0
        
        for i, dataset in enumerate(test_datasets):
            start_time = time.time()
            result = self.rule_engine.evaluate_rule(rule, dataset)
            execution_time = time.time() - start_time
            
            results.append({
                'dataset_index': i,
                'dataset_size': len(dataset),
                'detections': len(result.anomalies),
                'execution_time_ms': int(execution_time * 1000),
                'detection_rate': len(result.anomalies) / len(dataset) if len(dataset) > 0 else 0
            })
            
            total_execution_time += execution_time
            total_detections += len(result.anomalies)
            total_records += len(dataset)
        
        avg_execution_time = total_execution_time / len(test_datasets) if test_datasets else 0
        overall_detection_rate = total_detections / total_records if total_records > 0 else 0
        
        return {
            'rule_id': rule.id,
            'rule_name': rule.name,
            'total_datasets': len(test_datasets),
            'total_records': total_records,
            'total_detections': total_detections,
            'average_execution_time_ms': int(avg_execution_time * 1000),
            'overall_detection_rate': overall_detection_rate,
            'dataset_results': results,
            'performance_rating': self._rate_performance(overall_detection_rate, avg_execution_time)
        }
    
    def _rate_performance(self, detection_rate: float, execution_time: float) -> str:
        """Rate rule performance based on metrics"""
        if execution_time > 5:  # More than 5 seconds
            return "SLOW"
        elif detection_rate > 0.1:  # More than 10% detection rate
            return "HIGH_DETECTION"
        elif detection_rate > 0.01:  # 1-10% detection rate
            return "MODERATE"
        elif detection_rate > 0:  # Some detections
            return "LOW_DETECTION"
        else:
            return "NO_DETECTION"

class RuleDebugger:
    """
    Provides debugging capabilities for rule execution
    """
    
    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine
    
    def analyze_rule_execution(self, rule_id: int, inventory_df: pd.DataFrame) -> DebugResult:
        """
        Comprehensive analysis of rule execution for debugging
        
        Args:
            rule_id: ID of rule to debug
            inventory_df: Inventory data to analyze
        
        Returns:
            DebugResult with detailed analysis
        """
        from models import Rule  # Import here to avoid circular imports
        
        rule = Rule.query.get(rule_id)
        if not rule:
            return DebugResult(
                rule_id=rule_id,
                rule_status="NOT_FOUND",
                data_compatibility={},
                condition_analysis={},
                execution_trace=[f"Rule {rule_id} not found in database"],
                suggestions=["Check if rule ID is correct"],
                performance_metrics={}
            )
        
        execution_trace = []
        suggestions = []
        
        # Analyze rule status
        rule_status = "ACTIVE" if rule.is_active else "INACTIVE"
        if not rule.is_active:
            suggestions.append("Rule is inactive - activate it to see results")
        
        execution_trace.append(f"Rule '{rule.name}' status: {rule_status}")
        
        # Analyze data compatibility
        data_compatibility = self._analyze_data_compatibility(rule, inventory_df, execution_trace)
        
        # Analyze conditions
        condition_analysis = self._analyze_conditions(rule, inventory_df, execution_trace)
        
        # Performance analysis
        performance_metrics = self._analyze_performance(rule, inventory_df, execution_trace)
        
        # Generate suggestions
        suggestions.extend(self._generate_debug_suggestions(rule, data_compatibility, condition_analysis))
        
        return DebugResult(
            rule_id=rule_id,
            rule_status=rule_status,
            data_compatibility=data_compatibility,
            condition_analysis=condition_analysis,
            execution_trace=execution_trace,
            suggestions=suggestions,
            performance_metrics=performance_metrics
        )
    
    def _analyze_data_compatibility(self, rule: Rule, inventory_df: pd.DataFrame, 
                                  trace: List[str]) -> Dict[str, Any]:
        """Analyze compatibility between rule and data"""
        compatibility = {
            'data_size': len(inventory_df),
            'required_columns_present': True,
            'missing_columns': [],
            'data_quality_issues': []
        }
        
        # Check required columns
        required_cols = ['pallet_id', 'location', 'creation_date', 'receipt_number', 'description']
        missing_cols = [col for col in required_cols if col not in inventory_df.columns]
        
        if missing_cols:
            compatibility['required_columns_present'] = False
            compatibility['missing_columns'] = missing_cols
            trace.append(f"Missing required columns: {missing_cols}")
        
        # Check data quality
        if 'creation_date' in inventory_df.columns:
            null_dates = inventory_df['creation_date'].isna().sum()
            if null_dates > 0:
                compatibility['data_quality_issues'].append(f"{null_dates} null creation dates")
        
        if 'location' in inventory_df.columns:
            null_locations = inventory_df['location'].isna().sum()
            if null_locations > 0:
                compatibility['data_quality_issues'].append(f"{null_locations} null locations")
        
        trace.append(f"Data compatibility check: {len(compatibility['data_quality_issues'])} issues found")
        
        return compatibility
    
    def _analyze_conditions(self, rule: Rule, inventory_df: pd.DataFrame, 
                          trace: List[str]) -> Dict[str, Any]:
        """Analyze rule conditions in context of data"""
        try:
            conditions = json.loads(rule.conditions) if rule.conditions else {}
        except json.JSONDecodeError:
            trace.append("ERROR: Invalid JSON in rule conditions")
            return {'error': 'Invalid JSON in conditions'}
        
        analysis = {
            'conditions_parsed': True,
            'condition_count': len(conditions),
            'field_matches': {},
            'pattern_matches': {}
        }
        
        # Analyze field-based conditions
        for key, value in conditions.items():
            if key.endswith('_field') and isinstance(value, str):
                if value in inventory_df.columns:
                    analysis['field_matches'][key] = True
                    trace.append(f"Field condition '{key}': {value} found in data")
                else:
                    analysis['field_matches'][key] = False
                    trace.append(f"Field condition '{key}': {value} NOT found in data")
        
        # Analyze pattern-based conditions
        if 'location_pattern' in conditions and 'location' in inventory_df.columns:
            pattern = conditions['location_pattern']
            regex_pattern = pattern.replace('*', '.*')
            matches = inventory_df['location'].astype(str).str.match(regex_pattern, na=False).sum()
            analysis['pattern_matches']['location_pattern'] = {
                'pattern': pattern,
                'matches': int(matches),
                'total_locations': len(inventory_df)
            }
            trace.append(f"Location pattern '{pattern}' matches {matches} locations")
        
        return analysis
    
    def _analyze_performance(self, rule: Rule, inventory_df: pd.DataFrame, 
                           trace: List[str]) -> Dict[str, Any]:
        """Analyze rule performance metrics"""
        start_time = time.time()
        
        try:
            result = self.rule_engine.evaluate_rule(rule, inventory_df)
            execution_time = time.time() - start_time
            
            metrics = {
                'execution_time_ms': int(execution_time * 1000),
                'anomalies_found': len(result.anomalies),
                'success': result.success,
                'detection_rate': len(result.anomalies) / len(inventory_df) if len(inventory_df) > 0 else 0
            }
            
            if not result.success:
                metrics['error'] = result.error_message
                trace.append(f"Rule execution failed: {result.error_message}")
            else:
                trace.append(f"Rule executed successfully: {len(result.anomalies)} anomalies in {metrics['execution_time_ms']}ms")
            
            return metrics
            
        except Exception as e:
            execution_time = time.time() - start_time
            trace.append(f"Rule execution error: {str(e)}")
            return {
                'execution_time_ms': int(execution_time * 1000),
                'anomalies_found': 0,
                'success': False,
                'error': str(e)
            }
    
    def _generate_debug_suggestions(self, rule: Rule, data_compatibility: Dict, 
                                  condition_analysis: Dict) -> List[str]:
        """Generate debugging suggestions based on analysis"""
        suggestions = []
        
        # Data compatibility suggestions
        if not data_compatibility.get('required_columns_present', True):
            suggestions.append("Add missing required columns to your data")
        
        if data_compatibility.get('data_quality_issues'):
            suggestions.append("Clean up data quality issues (null values, etc.)")
        
        if data_compatibility.get('data_size', 0) < 10:
            suggestions.append("Provide more data rows for better testing")
        
        # Condition analysis suggestions
        field_matches = condition_analysis.get('field_matches', {})
        if any(not match for match in field_matches.values()):
            suggestions.append("Check field references in rule conditions")
        
        pattern_matches = condition_analysis.get('pattern_matches', {})
        for pattern_name, pattern_data in pattern_matches.items():
            if pattern_data.get('matches', 0) == 0:
                suggestions.append(f"Pattern '{pattern_data.get('pattern')}' matches no data - check pattern syntax")
            elif pattern_data.get('matches', 0) == pattern_data.get('total_locations', 0):
                suggestions.append(f"Pattern '{pattern_data.get('pattern')}' matches all data - might be too broad")
        
        # Performance suggestions
        if not suggestions:  # If no other issues found
            suggestions.append("Rule appears to be working correctly")
        
        return suggestions