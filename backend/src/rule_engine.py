"""
Dynamic Rule Engine for Warehouse Rules System
Implementation Plan Phase 2: Rule Engine Refactoring

This module replaces the hardcoded detection logic in main.py with a
dynamic, database-driven rule evaluation system.
"""

import json
import time
import re
import fnmatch
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Import models (will be imported from app context)
from models import Rule, RuleCategory, RulePerformance, Location

@dataclass
class RuleEvaluationResult:
    """Result of rule evaluation"""
    anomalies: List[Dict[str, Any]]
    execution_time_ms: int
    rule_id: int
    success: bool
    error_message: Optional[str] = None

class RuleEngine:
    """
    Dynamic rule engine that evaluates database-stored rules against inventory data
    """
    
    def __init__(self, db_session, app=None):
        self.db = db_session
        self.app = app
        self.evaluators = self._initialize_evaluators()
    
    def _ensure_app_context(self):
        """Ensure we're running within Flask app context"""
        if self.app:
            return self.app.app_context()
        else:
            # Try to get current app context if available
            from flask import current_app
            try:
                current_app._get_current_object()
                return None  # Already in context
            except RuntimeError:
                # No context available, need to create one
                return None
        
    def _initialize_evaluators(self):
        """Initialize rule evaluator registry"""
        return {
            'STAGNANT_PALLETS': StagnantPalletsEvaluator(app=self.app),
            'UNCOORDINATED_LOTS': UncoordinatedLotsEvaluator(app=self.app),
            'OVERCAPACITY': OvercapacityEvaluator(app=self.app),
            'INVALID_LOCATION': InvalidLocationEvaluator(app=self.app),
            'LOCATION_SPECIFIC_STAGNANT': LocationSpecificStagnantEvaluator(app=self.app),
            'TEMPERATURE_ZONE_MISMATCH': TemperatureZoneMismatchEvaluator(app=self.app),
            'DATA_INTEGRITY': DataIntegrityEvaluator(app=self.app),
            'LOCATION_MAPPING_ERROR': LocationMappingErrorEvaluator(app=self.app),
            'MISSING_LOCATION': MissingLocationEvaluator(app=self.app),
            'PRODUCT_INCOMPATIBILITY': ProductIncompatibilityEvaluator(app=self.app)
        }
    
    def load_active_rules(self, category_filter: str = None) -> List[Rule]:
        """Load all active rules from database, optionally filtered by category"""
        context = self._ensure_app_context()
        if context:
            with context:
                return self._load_active_rules_internal(category_filter)
        else:
            return self._load_active_rules_internal(category_filter)
    
    def _load_active_rules_internal(self, category_filter: str = None) -> List[Rule]:
        """Internal method to load rules"""
        query = Rule.query.filter_by(is_active=True)
        
        if category_filter:
            category = RuleCategory.query.filter_by(name=category_filter).first()
            if category:
                query = query.filter_by(category_id=category.id)
        
        return query.order_by(Rule.priority.desc()).all()
    
    def evaluate_all_rules(self, inventory_df: pd.DataFrame, 
                          rule_ids: List[int] = None) -> List[RuleEvaluationResult]:
        """
        Evaluate all active rules against inventory data
        
        Args:
            inventory_df: Inventory data to analyze
            rule_ids: Optional list of specific rule IDs to evaluate
        
        Returns:
            List of evaluation results for each rule
        """
        context = self._ensure_app_context()
        if context:
            with context:
                return self._evaluate_all_rules_internal(inventory_df, rule_ids)
        else:
            return self._evaluate_all_rules_internal(inventory_df, rule_ids)
    
    def _evaluate_all_rules_internal(self, inventory_df: pd.DataFrame, 
                                   rule_ids: List[int] = None) -> List[RuleEvaluationResult]:
        """Internal method to evaluate rules"""
        if rule_ids:
            rules = Rule.query.filter(Rule.id.in_(rule_ids), Rule.is_active == True).all()
        else:
            rules = self.load_active_rules()
        
        results = []
        for rule in rules:
            result = self.evaluate_rule(rule, inventory_df)
            results.append(result)
        
        return results
    
    def evaluate_rule(self, rule: Rule, inventory_df: pd.DataFrame) -> RuleEvaluationResult:
        """
        Evaluate a single rule against inventory data
        
        Args:
            rule: Rule object to evaluate
            inventory_df: Inventory data to analyze
        
        Returns:
            RuleEvaluationResult with anomalies found
        """
        start_time = time.time()
        
        try:
            # Get appropriate evaluator
            evaluator = self._get_rule_evaluator(rule.rule_type)
            
            if not evaluator:
                return RuleEvaluationResult(
                    anomalies=[],
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    rule_id=rule.id,
                    success=False,
                    error_message=f"No evaluator found for rule type: {rule.rule_type}"
                )
            
            # Evaluate the rule
            anomalies = evaluator.evaluate(rule, inventory_df)
            
            # Add rule metadata to each anomaly
            for anomaly in anomalies:
                anomaly['rule_id'] = rule.id
                anomaly['rule_name'] = rule.name
                anomaly['rule_type'] = rule.rule_type
                if 'priority' not in anomaly:
                    anomaly['priority'] = rule.priority
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return RuleEvaluationResult(
                anomalies=anomalies,
                execution_time_ms=execution_time,
                rule_id=rule.id,
                success=True
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return RuleEvaluationResult(
                anomalies=[],
                execution_time_ms=execution_time,
                rule_id=rule.id,
                success=False,
                error_message=str(e)
            )
    
    def _get_rule_evaluator(self, rule_type: str):
        """Get appropriate rule evaluator for rule type"""
        return self.evaluators.get(rule_type, DefaultRuleEvaluator())
    
    def validate_rule(self, rule_conditions: str, sample_data: pd.DataFrame) -> tuple[bool, str]:
        """
        Validate rule conditions against sample data
        
        Args:
            rule_conditions: JSON string of rule conditions
            sample_data: Sample inventory data for validation
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            conditions = json.loads(rule_conditions)
            
            # Basic validation checks
            if not isinstance(conditions, dict):
                return False, "Rule conditions must be a JSON object"
            
            # Check for required fields if they reference data columns
            data_columns = sample_data.columns.tolist()
            
            # Validate field references
            for key, value in conditions.items():
                if key.endswith('_field') and value not in data_columns:
                    return False, f"Field '{value}' not found in data columns"
            
            return True, "Rule validation successful"
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def estimate_performance(self, rule: Rule, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Estimate rule performance based on historical data
        
        Args:
            rule: Rule to estimate performance for
            historical_data: Historical inventory data
        
        Returns:
            Performance estimation metrics
        """
        try:
            # Run rule on historical data
            result = self.evaluate_rule(rule, historical_data)
            
            estimated_detections = len(result.anomalies)
            data_size = len(historical_data)
            
            # Calculate confidence based on data size
            confidence_level = min(95, max(50, (data_size / 1000) * 100))
            
            return {
                'estimated_anomalies': estimated_detections,
                'confidence_level': int(confidence_level),
                'execution_time_ms': result.execution_time_ms,
                'detection_rate': (estimated_detections / data_size * 100) if data_size > 0 else 0,
                'performance_prediction': self._predict_effectiveness(rule, estimated_detections, data_size)
            }
            
        except Exception as e:
            return {
                'error': f"Performance estimation failed: {str(e)}",
                'estimated_anomalies': 0,
                'confidence_level': 0
            }
    
    def _predict_effectiveness(self, rule: Rule, detections: int, data_size: int) -> str:
        """Predict rule effectiveness based on detection metrics"""
        if data_size == 0:
            return "No data to analyze"
        
        detection_rate = detections / data_size
        
        if detection_rate > 0.1:
            return "High detection rate - may need tuning to reduce false positives"
        elif detection_rate > 0.01:
            return "Moderate detection rate - likely effective"
        elif detection_rate > 0:
            return "Low detection rate - may be very specific or data-dependent"
        else:
            return "No detections - check rule conditions or data compatibility"

# ==================== RULE EVALUATORS ====================

class BaseRuleEvaluator:
    """Base class for all rule evaluators"""
    
    def __init__(self, app=None):
        self.app = app
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Evaluate rule against inventory data
        
        Args:
            rule: Rule object with conditions
            inventory_df: Inventory data to analyze
        
        Returns:
            List of anomaly dictionaries
        """
        raise NotImplementedError("Subclasses must implement evaluate method")
    
    def _ensure_app_context(self):
        """Ensure we're running within Flask app context"""
        if self.app:
            return self.app.app_context()
        else:
            # Try to get current app context if available
            from flask import current_app
            try:
                current_app._get_current_object()
                return None  # Already in context
            except RuntimeError:
                # No context available, cannot proceed with DB operations
                return None
    
    def _parse_conditions(self, rule: Rule) -> Dict[str, Any]:
        """Parse rule conditions from JSON"""
        try:
            return json.loads(rule.conditions) if rule.conditions else {}
        except json.JSONDecodeError:
            return {}
    
    def _parse_parameters(self, rule: Rule) -> Dict[str, Any]:
        """Parse rule parameters from JSON"""
        try:
            return json.loads(rule.parameters) if rule.parameters else {}
        except json.JSONDecodeError:
            return {}
    
    def _normalize_location_code(self, location_code: str) -> str:
        """
        Normalize location codes by removing user prefixes and standardizing format
        
        Examples:
        - "ALICE_A-01-01A" -> "A-01-01A"
        - "USER_BOB_001A" -> "001A" 
        - "WH01_RECEIVING" -> "RECEIVING"
        - "A-01-01A" -> "A-01-01A" (unchanged)
        """
        if not location_code:
            return location_code
            
        code = str(location_code).strip().upper()
        
        # Remove common warehouse/user prefixes
        prefixes_to_remove = [
            # User-specific warehouse prefixes (USER_USERNAME_)
            r'^USER_[A-Z0-9]+_',
            # Simplified user prefixes (USERNAME_)  
            r'^[A-Z]{2,10}_',  # 2-10 letter username prefixes
            # Warehouse prefixes (WH01_, WH_)
            r'^WH\d*_',
            # Default warehouse prefixes
            r'^DEFAULT_',
        ]
        
        for prefix_pattern in prefixes_to_remove:
            code = re.sub(prefix_pattern, '', code)
            
        return code
    
    def _find_location_by_code(self, location_code: str) -> 'Location':
        """
        Find location in database using smart matching (handles user prefixes)
        
        Args:
            location_code: Location code from inventory data
            
        Returns:
            Location object if found, None otherwise
        """
        if not location_code:
            return None
            
        location_str = str(location_code).strip()
        
        # Get locations with proper context
        context = self._ensure_app_context()
        if context:
            with context:
                return self._find_location_by_code_internal(location_str)
        else:
            try:
                return self._find_location_by_code_internal(location_str)
            except RuntimeError:
                # No database context available
                return None
    
    def _find_location_by_code_internal(self, location_str: str) -> 'Location':
        """Internal method to find location"""
        # 1. Direct exact match
        location = Location.query.filter_by(code=location_str).first()
        if location:
            return location
        
        # 2. Try normalized matching
        normalized_input = self._normalize_location_code(location_str)
        
        # Search all locations and check if normalized versions match
        all_locations = Location.query.all()
        for loc in all_locations:
            # Check if normalized database code matches input
            if self._normalize_location_code(loc.code) == location_str:
                return loc
            # Check if input normalized matches database code
            if normalized_input == loc.code:
                return loc
            # Check if both normalized versions match
            if self._normalize_location_code(loc.code) == normalized_input:
                return loc
        
        return None
    
    def _matches_pattern(self, location: str, pattern: str) -> bool:
        """Check if location matches pattern"""
        try:
            # Convert wildcard pattern to regex
            regex_pattern = pattern.replace('*', '.*')
            return bool(re.match(f"^{regex_pattern}$", location, re.IGNORECASE))
        except re.error:
            return False

class StagnantPalletsEvaluator(BaseRuleEvaluator):
    """Evaluator for stagnant pallets detection"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        parameters = self._parse_parameters(rule)
        
        time_threshold = conditions.get('time_threshold_hours', 6)
        location_types = conditions.get('location_types', ['RECEIVING'])
        
        anomalies = []
        now = datetime.now()
        
        # Ensure location_type column exists
        if 'location_type' not in inventory_df.columns:
            inventory_df = self._assign_location_types(inventory_df)
        
        for location_type in location_types:
            pallets = inventory_df[inventory_df['location_type'] == location_type]
            for _, pallet in pallets.iterrows():
                if pd.isna(pallet.get('creation_date')):
                    continue
                    
                time_diff = now - pallet['creation_date']
                if time_diff > timedelta(hours=time_threshold):
                    anomalies.append({
                        'pallet_id': pallet['pallet_id'],
                        'location': pallet['location'],
                        'anomaly_type': 'Stagnant Pallet',
                        'priority': rule.priority,
                        'details': f"Pallet in {location_type} for {time_diff.total_seconds()/3600:.1f}h (threshold: {time_threshold}h)"
                    })
        
        return anomalies
    
    def _assign_location_types(self, inventory_df: pd.DataFrame) -> pd.DataFrame:
        """Assign location types based on location patterns with smart matching"""
        df = inventory_df.copy()
        
        # Get location mappings from database with proper context
        context = self._ensure_app_context()
        if context:
            with context:
                locations = Location.query.all()
        else:
            try:
                locations = Location.query.all()
            except RuntimeError:
                # Fallback if no database context available
                locations = []
        
        location_map = {}
        location_map_normalized = {}  # For handling prefixed codes
        
        for loc in locations:
            location_map[loc.code] = loc.location_type
            
            # Create normalized mapping for prefixed warehouse codes
            # Remove common prefixes like "ALICE_", "USER_", etc.
            normalized_code = self._normalize_location_code(loc.code)
            if normalized_code != loc.code:
                location_map_normalized[normalized_code] = loc.location_type
        
        def get_location_type(location):
            if pd.isna(location) or not str(location).strip():
                return 'MISSING'
            
            location_str = str(location).strip()
            
            # 1. Direct exact match
            if location_str in location_map:
                return location_map[location_str]
            
            # 2. Try normalized matching (handles user prefixes)
            normalized_input = self._normalize_location_code(location_str)
            if normalized_input in location_map_normalized:
                return location_map_normalized[normalized_input]
            
            # 3. Try reverse matching (inventory might have prefixed code, db might not)
            for db_code, loc_type in location_map.items():
                db_normalized = self._normalize_location_code(db_code)
                if db_normalized == location_str or location_str == db_normalized:
                    return loc_type
            
            # 4. Pattern matching
            for loc in locations:
                if loc.pattern:
                    if self._matches_pattern(location_str, loc.pattern):
                        return loc.location_type
                    # Also try pattern matching with normalized codes
                    if self._matches_pattern(normalized_input, loc.pattern):
                        return loc.location_type
            
            return 'UNKNOWN'
        
        df['location_type'] = df['location'].apply(get_location_type)
        return df
    
    def test_location_matching(self, test_codes: list = None) -> dict:
        """
        Test the location matching system with various code formats
        
        Args:
            test_codes: List of location codes to test. If None, uses default test cases
            
        Returns:
            Dictionary with test results and mapping information
        """
        if test_codes is None:
            test_codes = [
                "A-01-01A",
                "01-02-015C", 
                "001A",
                "RECEIVING",
                "ALICE_A-01-01A",
                "USER_BOB_001A",
                "WH01_RECEIVING"
            ]
        
        results = {
            'database_locations': [],
            'test_results': {},
            'normalization_examples': {},
            'recommendations': []
        }
        
        # Get all database locations
        all_locations = Location.query.all()
        results['database_locations'] = [
            {
                'code': loc.code,
                'normalized': self._normalize_location_code(loc.code),
                'type': loc.location_type,
                'warehouse_id': loc.warehouse_id
            }
            for loc in all_locations
        ]
        
        # Test each code
        for test_code in test_codes:
            normalized = self._normalize_location_code(test_code)
            found_location = self._find_location_by_code(test_code)
            
            results['test_results'][test_code] = {
                'normalized': normalized,
                'found_match': found_location is not None,
                'matched_code': found_location.code if found_location else None,
                'location_type': found_location.location_type if found_location else 'NOT_FOUND'
            }
            
            results['normalization_examples'][test_code] = normalized
        
        # Generate recommendations
        if len([r for r in results['test_results'].values() if not r['found_match']]) > 0:
            results['recommendations'].append(
                "Some test codes didn't find matches. Consider creating location mappings or patterns."
            )
        
        prefixed_count = len([loc for loc in all_locations if '_' in loc.code])
        if prefixed_count > 0:
            results['recommendations'].append(
                f"Found {prefixed_count} prefixed location codes in database. "
                "Ensure inventory reports use matching formats or rely on normalization."
            )
        
        return results

class UncoordinatedLotsEvaluator(BaseRuleEvaluator):
    """Evaluator for uncoordinated lots detection"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        
        completion_threshold = conditions.get('completion_threshold', 0.8)
        location_types = conditions.get('location_types', ['RECEIVING'])
        
        anomalies = []
        
        # Ensure location_type column exists
        if 'location_type' not in inventory_df.columns:
            inventory_df = StagnantPalletsEvaluator()._assign_location_types(inventory_df)
        
        lots = inventory_df.groupby('receipt_number')
        
        for receipt_number, lot_df in lots:
            final_pallets = lot_df[lot_df['location_type'] == 'FINAL'].shape[0]
            total_pallets = lot_df.shape[0]
            completion_ratio = final_pallets / total_pallets if total_pallets > 0 else 0
            
            if completion_ratio >= completion_threshold:
                stragglers = lot_df[lot_df['location_type'].isin(location_types)]
                for _, pallet in stragglers.iterrows():
                    anomalies.append({
                        'pallet_id': pallet['pallet_id'],
                        'location': pallet['location'],
                        'anomaly_type': 'Lot Straggler',
                        'priority': rule.priority,
                        'details': f"{completion_ratio:.0%} of lot '{receipt_number}' stored, but this pallet still in {pallet['location_type']}"
                    })
        
        return anomalies

class OvercapacityEvaluator(BaseRuleEvaluator):
    """Evaluator for overcapacity detection"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        
        anomalies = []
        
        # Count pallets per location
        location_counts = inventory_df['location'].value_counts()
        
        for location, count in location_counts.items():
            # Find location using smart matching to get capacity
            location_obj = self._find_location_by_code(str(location))
            capacity = location_obj.capacity if location_obj else 1  # Default capacity 1
            
            if count > capacity:
                # Find all pallets in overcapacity location
                pallets_in_loc = inventory_df[inventory_df['location'] == location]
                for _, pallet in pallets_in_loc.iterrows():
                    anomalies.append({
                        'pallet_id': pallet['pallet_id'],
                        'location': pallet['location'],
                        'anomaly_type': 'Overcapacity',
                        'priority': rule.priority,
                        'details': f"Location '{location}' has {count} pallets (capacity: {capacity})"
                    })
        
        return anomalies

class InvalidLocationEvaluator(BaseRuleEvaluator):
    """Evaluator for invalid location detection"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        
        anomalies = []
        
        # Get valid locations from database
        locations = Location.query.filter_by(is_active=True).all()
        valid_locations = set()
        valid_patterns = []
        
        for loc in locations:
            valid_locations.add(loc.code)
            if loc.pattern:
                valid_patterns.append(loc.pattern)
        
        for _, pallet in inventory_df.iterrows():
            location = str(pallet['location']).strip()
            
            # Skip empty/null locations
            if pd.isna(pallet['location']) or not location:
                continue
            
            # Check if location is valid
            is_valid = location in valid_locations
            
            # Check against patterns if not directly valid
            if not is_valid:
                for pattern in valid_patterns:
                    if self._matches_pattern(location, pattern):
                        is_valid = True
                        break
            
            if not is_valid:
                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Invalid Location',
                    'priority': rule.priority,
                    'details': f"Location '{location}' not defined in warehouse rules"
                })
        
        return anomalies

class LocationSpecificStagnantEvaluator(BaseRuleEvaluator):
    """Evaluator for location-specific stagnant pallets"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        
        location_pattern = conditions.get('location_pattern', 'AISLE*')
        time_threshold = conditions.get('time_threshold_hours', 4)
        
        anomalies = []
        now = datetime.now()
        
        # Filter by location pattern
        matching_pallets = inventory_df[
            inventory_df['location'].astype(str).str.upper().str.match(
                location_pattern.upper().replace('*', '.*'), na=False
            )
        ]
        
        for _, pallet in matching_pallets.iterrows():
            if pd.isna(pallet.get('creation_date')):
                continue
                
            time_diff = now - pallet['creation_date']
            if time_diff > timedelta(hours=time_threshold):
                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Location-Specific Stagnant',
                    'priority': rule.priority,
                    'details': f"Pallet stuck in {pallet['location']} for {time_diff.total_seconds()/3600:.1f}h"
                })
        
        return anomalies

class TemperatureZoneMismatchEvaluator(BaseRuleEvaluator):
    """Evaluator for temperature zone violations"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        
        product_patterns = conditions.get('product_patterns', ['*FROZEN*', '*REFRIGERATED*'])
        prohibited_zones = conditions.get('prohibited_zones', ['AMBIENT', 'GENERAL'])
        
        anomalies = []
        
        for _, pallet in inventory_df.iterrows():
            if pd.isna(pallet.get('description')):
                continue
            
            description = str(pallet['description']).upper()
            
            # Check if product matches temperature-sensitive patterns
            is_temp_sensitive = any(
                fnmatch.fnmatch(description, pattern.upper()) 
                for pattern in product_patterns
            )
            
            if is_temp_sensitive:
                # Get location zone using smart matching
                location = self._find_location_by_code(str(pallet['location']))
                if location and location.zone in prohibited_zones:
                    anomalies.append({
                        'pallet_id': pallet['pallet_id'],
                        'location': pallet['location'],
                        'anomaly_type': 'Temperature Zone Violation',
                        'priority': rule.priority,
                        'details': f"Temperature-sensitive product '{pallet['description']}' in {location.zone} zone"
                    })
        
        return anomalies

class DataIntegrityEvaluator(BaseRuleEvaluator):
    """Evaluator for data integrity issues"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        
        anomalies = []
        
        if conditions.get('check_duplicate_scans', True):
            # Find duplicate pallet IDs
            duplicates = inventory_df[inventory_df.duplicated(subset=['pallet_id'], keep=False)]
            for _, pallet in duplicates.iterrows():
                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Duplicate Scan',
                    'priority': rule.priority,
                    'details': f"Pallet ID '{pallet['pallet_id']}' appears multiple times in data"
                })
        
        if conditions.get('check_impossible_locations', True):
            # Find impossible location codes (e.g., too long, invalid characters)
            for _, pallet in inventory_df.iterrows():
                location = str(pallet['location'])
                if len(location) > 20 or any(c in location for c in ['@', '#', '!', '?']):
                    anomalies.append({
                        'pallet_id': pallet['pallet_id'],
                        'location': pallet['location'],
                        'anomaly_type': 'Impossible Location',
                        'priority': rule.priority,
                        'details': f"Location '{location}' appears to be invalid or corrupted"
                    })
        
        return anomalies

class LocationMappingErrorEvaluator(BaseRuleEvaluator):
    """Evaluator for location mapping errors"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        
        anomalies = []
        
        # This is a placeholder for more complex location mapping validation
        # Could include checks like:
        # - Locations that should exist but don't
        # - Pattern inconsistencies
        # - Zone mismatches
        
        return anomalies

class MissingLocationEvaluator(BaseRuleEvaluator):
    """Evaluator for missing location detection"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        
        anomalies = []
        
        # Find pallets with missing/null locations
        missing_location_pallets = inventory_df[
            inventory_df['location'].isna() | 
            (inventory_df['location'].astype(str).str.strip() == '') |
            (inventory_df['location'].astype(str).str.upper() == 'NAN')
        ]
        
        for _, pallet in missing_location_pallets.iterrows():
            anomalies.append({
                'pallet_id': pallet['pallet_id'],
                'location': 'N/A',
                'anomaly_type': 'Missing Location',
                'priority': rule.priority,
                'details': "Pallet has no location assigned"
            })
        
        return anomalies

class ProductIncompatibilityEvaluator(BaseRuleEvaluator):
    """Evaluator for product-location compatibility"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        
        anomalies = []
        
        # Get location restrictions
        locations = Location.query.all()
        
        for _, pallet in inventory_df.iterrows():
            if pd.isna(pallet.get('description')) or pd.isna(pallet.get('location')):
                continue
            
            location = self._find_location_by_code(str(pallet['location']))
            if not location:
                continue
            
            allowed_products = location.get_allowed_products()
            if allowed_products:
                description = str(pallet['description']).upper()
                
                # Check if product matches any allowed pattern
                is_allowed = any(
                    fnmatch.fnmatch(description, pattern.upper()) 
                    for pattern in allowed_products
                )
                
                if not is_allowed:
                    anomalies.append({
                        'pallet_id': pallet['pallet_id'],
                        'location': pallet['location'],
                        'anomaly_type': 'Product Incompatibility',
                        'priority': rule.priority,
                        'details': f"Product '{pallet['description']}' not allowed in location '{pallet['location']}'"
                    })
        
        return anomalies

class DefaultRuleEvaluator(BaseRuleEvaluator):
    """Default evaluator for unhandled rule types"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        return []  # Return empty list for unknown rule types