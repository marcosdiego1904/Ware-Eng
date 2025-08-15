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
import math
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
    
    def _normalize_dataframe_columns(self, inventory_df: pd.DataFrame) -> pd.DataFrame:
        """Normalize DataFrame column names and data types to match expected format"""
        df = inventory_df.copy()
        
        # Define column mapping from common variations to expected names
        column_mapping = {
            'Pallet ID': 'pallet_id',
            'pallet_id': 'pallet_id',
            'PALLET_ID': 'pallet_id',
            'PalletID': 'pallet_id',
            'Pallet': 'pallet_id',
            
            'Location': 'location',
            'location': 'location',
            'LOCATION': 'location',
            'Current Location': 'location',
            'Current_Location': 'location',
            'LocationCode': 'location',
            
            'Created Date': 'creation_date',
            'CreatedDate': 'creation_date',
            'creation_date': 'creation_date',
            'CREATED_DATE': 'creation_date',
            'Date Created': 'creation_date',
            'Last Activity': 'creation_date',
            'LastActivity': 'creation_date',
            'Timestamp': 'creation_date'
        }
        
        # Apply column mapping
        df = df.rename(columns=column_mapping)
        
        # CRITICAL FIX: Ensure creation_date is properly parsed as datetime
        if 'creation_date' in df.columns:
            # Convert to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(df['creation_date']):
                try:
                    df['creation_date'] = pd.to_datetime(df['creation_date'])
                    print(f"[RULE_ENGINE_DEBUG] Converted creation_date from {type(inventory_df['creation_date'].iloc[0] if len(inventory_df) > 0 else 'empty')} to datetime")
                except Exception as e:
                    print(f"[RULE_ENGINE_WARNING] Failed to convert creation_date to datetime: {e}")
        
        print(f"[RULE_ENGINE_DEBUG] Column normalization:")
        print(f"   Original columns: {list(inventory_df.columns)}")
        print(f"   Normalized columns: {list(df.columns)}")
        
        return df
    
    def _evaluate_all_rules_internal(self, inventory_df: pd.DataFrame, 
                                   rule_ids: List[int] = None) -> List[RuleEvaluationResult]:
        """Internal method to evaluate rules"""
        if rule_ids:
            rules = Rule.query.filter(Rule.id.in_(rule_ids), Rule.is_active == True).all()
        else:
            rules = self.load_active_rules()
        
        # Normalize column names before processing
        inventory_df = self._normalize_dataframe_columns(inventory_df)
        
        print(f"[RULE_ENGINE_DEBUG] Evaluating {len(rules)} active rules")
        print(f"[RULE_ENGINE_DEBUG] Inventory DataFrame shape: {inventory_df.shape}")
        
        results = []
        total_anomalies = 0
        
        for rule in rules:
            print(f"\n[RULE_ENGINE_DEBUG] Evaluating Rule ID {rule.id}: {rule.name}")
            print(f"   Type: {rule.rule_type}, Priority: {rule.priority}")
            print(f"   Conditions: {rule.conditions}")
            
            result = self.evaluate_rule(rule, inventory_df)
            results.append(result)
            
            if result.success:
                anomaly_count = len(result.anomalies)
                total_anomalies += anomaly_count
                print(f"   SUCCESS: Rule executed successfully: {anomaly_count} anomalies found")
                if anomaly_count > 0:
                    print(f"   ANOMALIES:")
                    for i, anomaly in enumerate(result.anomalies):
                        print(f"      {i+1}. {anomaly.get('pallet_id', 'N/A')} - {anomaly.get('issue_description', 'N/A')}")
            else:
                print(f"   FAILED: Rule failed: {result.error_message}")
        
        print(f"\n[RULE_ENGINE_DEBUG] Total anomalies found: {total_anomalies}")
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
        Conservative normalization - keep database format intact
        Based on debug output showing locations like: USER_02-01-042A, 01-01-017C
        """
        if not location_code:
            return location_code
            
        code = str(location_code).strip().upper()
        
        # Only remove WH/DEFAULT prefixes, keep USER_ prefixes intact
        simple_prefixes = ['WH01_', 'WH02_', 'WH03_', 'WH04_', 'WH_', 'DEFAULT_']
        for prefix in simple_prefixes:
            if code.startswith(prefix):
                code = code[len(prefix):]
                break
            
        return code
    
    def _extract_base_location_code(self, location_code: str) -> str:
        """
        Extract base location code by removing common prefixes and suffixes
        Examples: 
        - USER_02-01-042A -> 02-01-042A
        - USER_01-01-014C_2 -> 01-01-014C  
        - 02-02-003A_1 -> 02-02-003A
        - 01-02-03A -> 01-02-03A (unchanged)
        """
        if not location_code:
            return location_code
            
        code = str(location_code).strip().upper()
        
        # Remove common prefixes
        prefixes_to_remove = ['USER_', 'WH01_', 'WH02_', 'WH03_', 'WH04_', 'WH_', 'DEFAULT_', 'ALICE_']
        for prefix in prefixes_to_remove:
            if code.startswith(prefix):
                code = code[len(prefix):]
                break
        
        # Remove numerical suffixes like _1, _2, _3
        import re
        code = re.sub(r'_\d+$', '', code)
        
        return code
    
    def _normalize_position_format(self, location_code: str) -> list:
        """
        Generate multiple normalized position formats for comprehensive matching
        
        Examples:
        - 02-06-03A -> ['02-06-03A', '02-06-003A'] (2-digit to 3-digit)
        - 02-06-003A -> ['02-06-003A', '02-06-03A'] (3-digit to 2-digit)
        - FINAL-006 -> ['FINAL-006'] (special locations unchanged)
        
        Returns:
            List of normalized location codes for matching
        """
        if not location_code:
            return [location_code]
            
        code = str(location_code).strip().upper()
        
        # Import regex inside method to avoid top-level import issues
        import re
        
        # Pattern for aisle-rack-position format: XX-XX-XXXA or XX-XX-XXXXA
        aisle_pattern = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{2,3})([A-Z])$', code)
        
        if aisle_pattern:
            aisle, rack, position, level = aisle_pattern.groups()
            
            # Generate both 2-digit and 3-digit position formats
            position_2digit = position.lstrip('0').zfill(2) if len(position) > 2 else position
            position_3digit = position.zfill(3)
            
            format_2digit = f"{aisle.zfill(2)}-{rack.zfill(2)}-{position_2digit}{level}"
            format_3digit = f"{aisle.zfill(2)}-{rack.zfill(2)}-{position_3digit}{level}"
            
            # Return both formats, removing duplicates
            return list(set([format_2digit, format_3digit]))
        
        # For non-standard formats, return as-is
        return [code]
    
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
        
        # 3. If normalization didn't change anything, skip expensive search
        if normalized_input == location_str:
            return None
        
        # 4. Search all locations and check if normalized versions match
        all_locations = Location.query.all()  # Search all locations for comprehensive matching
        for loc in all_locations:
            try:
                # Check if normalized database code matches input
                normalized_db_code = self._normalize_location_code(loc.code)
                if normalized_db_code == location_str:
                    return loc
                # Check if input normalized matches database code
                if normalized_input == loc.code:
                    return loc
                # Check if both normalized versions match
                if normalized_db_code == normalized_input:
                    return loc
            except Exception:
                # Skip problematic location codes
                continue
        
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
        
        # Parse different condition formats
        time_threshold_hours = conditions.get('time_threshold_hours', 6)
        max_days_in_location = conditions.get('max_days_in_location')
        location_types = conditions.get('location_types', ['RECEIVING'])
        excluded_locations = conditions.get('excluded_locations', [])
        
        # Convert max_days_in_location to hours if specified
        if max_days_in_location is not None:
            time_threshold_hours = max_days_in_location * 24
        
        anomalies = []
        now = datetime.now()
        
        # Ensure location_type column exists
        if 'location_type' not in inventory_df.columns:
            inventory_df = self._assign_location_types(inventory_df)
        
        # Filter pallets based on included and excluded locations
        if excluded_locations:
            # If exclusions specified, check all pallets except those in excluded locations
            valid_pallets = inventory_df[~inventory_df['location_type'].isin(excluded_locations)]
        else:
            # Otherwise, filter by included location types  
            valid_pallets = inventory_df[inventory_df['location_type'].isin(location_types)]
        
        for _, pallet in valid_pallets.iterrows():
            if pd.isna(pallet.get('creation_date')):
                continue
                
            time_diff = now - pallet['creation_date']
            if time_diff > timedelta(hours=time_threshold_hours):
                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'location_type': pallet['location_type'],
                    'anomaly_type': 'Stagnant Pallet',
                    'priority': rule.priority,
                    'issue_description': f"Pallet in {pallet['location_type']} for {time_diff.total_seconds()/3600:.1f}h (threshold: {time_threshold_hours:.1f}h)"
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
            # Count pallets that have reached final storage locations
            final_pallets = lot_df[lot_df['location_type'] == 'FINAL'].shape[0]
            total_pallets = lot_df.shape[0]
            completion_ratio = final_pallets / total_pallets if total_pallets > 0 else 0
            
            # FIXED: Only flag stragglers from mostly-complete lots (>=80% completion)
            if completion_ratio >= completion_threshold and total_pallets > 1:
                # Only flag multi-pallet lots where most pallets have been moved to final storage
                # but some stragglers remain in receiving/staging areas
                stragglers = lot_df[lot_df['location_type'].isin(location_types)]
                for _, pallet in stragglers.iterrows():
                    anomalies.append({
                        'pallet_id': pallet['pallet_id'],
                        'location': pallet['location'],
                        'anomaly_type': 'Lot Straggler',
                        'priority': rule.priority,
                        'issue_description': f"{completion_ratio:.0%} of lot '{receipt_number}' moved to final storage - this pallet left behind in {pallet['location_type']}",
                        'details': f"{completion_ratio:.0%} of lot '{receipt_number}' already stored, but this pallet still in {pallet['location_type']}"
                    })
        
        return anomalies

class OvercapacityEvaluator(BaseRuleEvaluator):
    """Evaluator for smart overcapacity detection with statistical analysis"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        parameters = self._parse_parameters(rule)
        
        # Check if statistical analysis is enabled (default: True for new behavior)
        use_statistical_analysis = parameters.get('use_statistical_analysis', True)
        significance_threshold = parameters.get('significance_threshold', 1.0)  # LOWERED: Flag if 1x expected (was 2.0)
        min_severity_ratio = parameters.get('min_severity_ratio', 1.2)  # LOWERED: Minimum severity to report (was 1.5)
        
        if use_statistical_analysis:
            return self._evaluate_with_statistical_analysis(
                rule, inventory_df, significance_threshold, min_severity_ratio
            )
        else:
            # Legacy behavior for backward compatibility
            return self._evaluate_legacy(rule, inventory_df)
    
    def _evaluate_with_statistical_analysis(self, rule: Rule, inventory_df: pd.DataFrame, 
                                          significance_threshold: float, min_severity_ratio: float) -> List[Dict[str, Any]]:
        """Enhanced overcapacity detection with statistical analysis"""
        anomalies = []
        
        # Calculate warehouse statistics
        warehouse_stats = self._calculate_warehouse_statistics(inventory_df)
        
        # Calculate expected overcapacity using statistical model
        expected_overcapacity = self._calculate_expected_overcapacity(inventory_df, warehouse_stats)
        
        # Count pallets per location
        location_counts = inventory_df['location'].value_counts()
        
        # Find actual overcapacity locations
        actual_overcapacity_locations = []
        for location, count in location_counts.items():
            location_obj = self._find_location_by_code(str(location))
            capacity = self._get_location_capacity(location_obj, str(location))
            
            if count > capacity:
                actual_overcapacity_locations.append({
                    'location': location,
                    'count': count,
                    'capacity': capacity,
                    'excess': count - capacity
                })
        
        actual_overcapacity_count = len(actual_overcapacity_locations)
        
        # Calculate severity ratio
        severity_ratio = (actual_overcapacity_count / expected_overcapacity['count']) if expected_overcapacity['count'] > 0 else float('inf')
        
        # Determine if this is a systematic issue or natural collision
        overcapacity_category = self._categorize_overcapacity(
            actual_overcapacity_count, expected_overcapacity, warehouse_stats, severity_ratio
        )
        
        # CRITICAL FIX: Add obvious violation bypass before statistical analysis
        should_flag_anomalies = False
        bypass_reason = None
        
        # 1. Obvious violations bypass (>2x capacity) - always flag these regardless of statistics
        obvious_violations = [loc for loc in actual_overcapacity_locations if loc['count'] > loc['capacity'] * 2]
        if obvious_violations:
            should_flag_anomalies = True
            bypass_reason = f"Obvious violations detected: {len(obvious_violations)} locations with >2x capacity"
        
        # 2. Statistical analysis for borderline cases
        elif severity_ratio >= min_severity_ratio and actual_overcapacity_count >= significance_threshold * expected_overcapacity['count']:
            should_flag_anomalies = True
            bypass_reason = f"Statistical significance: {severity_ratio:.1f}x severity ratio"
        
        if should_flag_anomalies:
            # Adjust priority based on severity
            adjusted_priority = self._adjust_priority_by_severity(rule.priority, severity_ratio)
            
            for overcap_loc in actual_overcapacity_locations:
                # Determine if this is an obvious violation
                is_obvious = overcap_loc['count'] > overcap_loc['capacity'] * 2
                violation_severity = overcap_loc['count'] / overcap_loc['capacity'] if overcap_loc['capacity'] > 0 else float('inf')
                
                # Find all pallets in overcapacity location
                pallets_in_loc = inventory_df[inventory_df['location'] == overcap_loc['location']]
                for _, pallet in pallets_in_loc.iterrows():
                    anomalies.append({
                        'pallet_id': pallet['pallet_id'],
                        'location': pallet['location'],
                        'anomaly_type': 'Obvious Violation' if is_obvious else 'Smart Overcapacity',
                        'priority': 'Very High' if is_obvious else adjusted_priority,
                        'details': f"Location '{overcap_loc['location']}' has {overcap_loc['count']} pallets (capacity: {overcap_loc['capacity']})",
                        'issue_description': f"{'Obvious overcapacity violation' if is_obvious else 'Systematic overcapacity detected'} - {violation_severity:.1f}x capacity",
                        # Enhanced statistical fields
                        'utilization_rate': warehouse_stats['utilization_rate'],
                        'expected_overcapacity_count': expected_overcapacity['count'],
                        'actual_overcapacity_count': actual_overcapacity_count,
                        'anomaly_severity_ratio': severity_ratio,
                        'overcapacity_category': 'Obvious Violation' if is_obvious else overcapacity_category,
                        'warehouse_total_pallets': warehouse_stats['total_pallets'],
                        'warehouse_total_capacity': warehouse_stats['total_capacity'],
                        'statistical_model': 'Obvious violation bypass' if is_obvious else expected_overcapacity['model_used'],
                        'excess_pallets': overcap_loc['excess'],
                        'violation_severity': violation_severity,
                        'bypass_reason': bypass_reason
                    })
        
        return anomalies
    
    def _calculate_warehouse_statistics(self, inventory_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate warehouse utilization and capacity statistics"""
        
        # Get all unique locations and their capacities
        unique_locations = inventory_df['location'].unique()
        total_capacity = 0
        valid_locations = 0
        
        for location in unique_locations:
            location_obj = self._find_location_by_code(str(location))
            capacity = self._get_location_capacity(location_obj, str(location))
            total_capacity += capacity
            valid_locations += 1
        
        total_pallets = len(inventory_df)
        utilization_rate = total_pallets / total_capacity if total_capacity > 0 else 0
        
        # Calculate distribution metrics
        location_counts = inventory_df['location'].value_counts()
        avg_pallets_per_location = location_counts.mean()
        std_pallets_per_location = location_counts.std()
        
        return {
            'total_pallets': total_pallets,
            'total_locations': valid_locations,
            'total_capacity': total_capacity,
            'utilization_rate': utilization_rate,
            'avg_pallets_per_location': avg_pallets_per_location,
            'std_pallets_per_location': std_pallets_per_location,
            'occupied_locations': len(location_counts)
        }
    
    def _calculate_expected_overcapacity(self, inventory_df: pd.DataFrame, 
                                       warehouse_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate expected random overcapacity using statistical models"""
        
        utilization_rate = warehouse_stats['utilization_rate']
        total_pallets = warehouse_stats['total_pallets']
        total_locations = warehouse_stats['total_locations']
        
        if utilization_rate <= 1.0:
            # Low to moderate utilization: Use Poisson-like distribution
            # Expected random collisions based on utilization rate
            # Formula: For random distribution, probability of collision ≈ utilization_rate²
            expected_count = total_locations * (utilization_rate ** 2) / 2
            model_used = "Poisson-based random distribution"
            
            # For very low utilization, expect minimal random overcapacity
            if utilization_rate < 0.3:
                expected_count = max(1, expected_count * 0.5)
                
        else:
            # High utilization: Most locations will be at or over capacity
            # Expected overcapacity locations increases dramatically
            if utilization_rate <= 1.5:
                # Moderate overcapacity - linear increase
                expected_count = total_locations * 0.3 * (utilization_rate - 1.0) + total_locations * 0.1
            else:
                # High overcapacity - most locations affected
                expected_count = total_locations * 0.8
            
            model_used = "High utilization linear model"
        
        # Ensure minimum expected value for statistical comparison
        expected_count = max(1.0, expected_count)
        
        return {
            'count': expected_count,
            'model_used': model_used,
            'utilization_basis': utilization_rate,
            'confidence_level': min(95, max(60, 100 - (abs(utilization_rate - 0.7) * 50)))
        }
    
    def _categorize_overcapacity(self, actual_count: int, expected_overcapacity: Dict[str, Any], 
                               warehouse_stats: Dict[str, Any], severity_ratio: float) -> str:
        """Categorize overcapacity as Natural vs Systematic"""
        
        # Natural: Within expected statistical variance
        if severity_ratio <= 1.5:
            return "Natural"
        
        # Check utilization patterns
        utilization_rate = warehouse_stats['utilization_rate']
        
        # Very high overcapacity or unusual distribution patterns suggest systematic issues
        if severity_ratio >= 3.0:
            return "Systematic"
        
        # Medium severity - depends on utilization context
        if utilization_rate > 1.2 and severity_ratio >= 2.0:
            return "Systematic"  # High utilization with significant excess suggests process issues
        
        return "Elevated Natural"  # Higher than expected but possibly still random
    
    def _adjust_priority_by_severity(self, base_priority: str, severity_ratio: float) -> str:
        """Adjust priority based on severity ratio"""
        priority_map = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}
        reverse_map = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
        
        current_level = priority_map.get(base_priority, 2)
        
        # Increase priority for high severity ratios
        if severity_ratio >= 5.0:
            adjusted_level = min(4, current_level + 2)
        elif severity_ratio >= 3.0:
            adjusted_level = min(4, current_level + 1)
        else:
            adjusted_level = current_level
        
        return reverse_map[adjusted_level]
    
    def _get_location_capacity(self, location_obj, location_str: str) -> int:
        """Get location capacity with intelligent defaults"""
        if location_obj and location_obj.capacity:
            return location_obj.capacity
        
        # Intelligent defaults based on location naming patterns
        location_upper = location_str.upper()
        if any(x in location_upper for x in ['RECEIVING', 'STAGING', 'DOCK', 'LOADING']):
            return 20  # Special handling areas
        elif any(x in location_upper for x in ['AISLE', 'RACK', 'SHELF']):
            return 5   # Standard storage
        elif any(x in location_upper for x in ['BULK', 'FLOOR']):
            return 15  # Floor storage areas
        else:
            return 5   # Default capacity
    
    def _evaluate_legacy(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Legacy overcapacity detection for backward compatibility"""
        conditions = self._parse_conditions(rule)
        anomalies = []
        
        # Count pallets per location
        location_counts = inventory_df['location'].value_counts()
        
        for location, count in location_counts.items():
            # Find location using smart matching to get capacity
            location_obj = self._find_location_by_code(str(location))
            capacity = self._get_location_capacity(location_obj, str(location))
            
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
        
        # Get valid locations from database (include both is_active=True and NULL)
        context = self._ensure_app_context()
        if context:
            with context:
                from sqlalchemy import or_
                locations = Location.query.filter(
                    or_(Location.is_active == True, Location.is_active.is_(None))
                ).all()
        else:
            try:
                from sqlalchemy import or_
                locations = Location.query.filter(
                    or_(Location.is_active == True, Location.is_active.is_(None))
                ).all()
            except RuntimeError:
                locations = []
        
        print(f"[INVALID_LOCATION_DEBUG] Found {len(locations)} valid locations in database")
        valid_patterns = []
        
        for loc in locations:
            if loc.pattern:
                valid_patterns.append(loc.pattern)
        
        # Create comprehensive lookup sets for all possible location formats
        valid_locations = set()
        valid_base_codes = set()  # Base codes without prefixes/suffixes
        valid_position_normalized = set()  # Position-normalized codes
        
        for loc in locations:
            # Add exact database code
            valid_locations.add(loc.code)
            
            # Extract base code patterns from database locations
            base_code = self._extract_base_location_code(loc.code)
            if base_code:
                valid_base_codes.add(base_code)
                valid_locations.add(base_code)  # Also add to main set
                
                # Generate position-normalized variants for database locations
                position_variants = self._normalize_position_format(base_code)
                for variant in position_variants:
                    valid_position_normalized.add(variant)
                    valid_locations.add(variant)
            
            # Add normalized version
            normalized = self._normalize_location_code(loc.code)
            if normalized != loc.code:
                valid_locations.add(normalized)
                # Also add base and position variants of normalized
                base_normalized = self._extract_base_location_code(normalized)
                if base_normalized:
                    valid_base_codes.add(base_normalized)
                    position_variants = self._normalize_position_format(base_normalized)
                    for variant in position_variants:
                        valid_position_normalized.add(variant)
                        valid_locations.add(variant)
        
        # Debug: Show what we're looking for vs what's available
        print(f"[INVALID_LOCATION_DEBUG] Sample valid locations: {list(valid_locations)[:10]}")
        print(f"[INVALID_LOCATION_DEBUG] Sample base codes: {list(valid_base_codes)[:10]}")
        print(f"[INVALID_LOCATION_DEBUG] Sample position normalized: {list(valid_position_normalized)[:10]}")
        print(f"[INVALID_LOCATION_DEBUG] Total lookup sets - locations: {len(valid_locations)}, base: {len(valid_base_codes)}, position: {len(valid_position_normalized)}")
        
        for _, pallet in inventory_df.iterrows():
            location = str(pallet['location']).strip()
            
            # Skip empty/null locations
            if pd.isna(pallet['location']) or not location:
                continue
            
            # Enhanced location validation with multiple matching strategies
            is_valid = False
            
            # 1. Direct lookup
            if location in valid_locations:
                is_valid = True
            
            # 2. Try base code lookup (removes prefixes/suffixes from inventory location)
            if not is_valid:
                base_location = self._extract_base_location_code(location)
                if base_location and base_location in valid_base_codes:
                    is_valid = True
            
            # 3. Try position format normalization (CRITICAL FIX for 2-digit vs 3-digit position)
            if not is_valid:
                position_variants = self._normalize_position_format(location)
                for variant in position_variants:
                    if variant in valid_position_normalized:
                        is_valid = True
                        break
                    # Also try base extraction on variants
                    base_variant = self._extract_base_location_code(variant)
                    if base_variant and base_variant in valid_base_codes:
                        is_valid = True
                        break
            
            # 4. Try normalized lookup
            if not is_valid:
                normalized_location = self._normalize_location_code(location)
                if normalized_location in valid_locations:
                    is_valid = True
                # Also try base of normalized with position variants
                base_normalized = self._extract_base_location_code(normalized_location)
                if base_normalized:
                    position_variants = self._normalize_position_format(base_normalized)
                    for variant in position_variants:
                        if variant in valid_position_normalized:
                            is_valid = True
                            break
            
            # 5. Check against patterns if not directly valid
            if not is_valid:
                for pattern in valid_patterns:
                    if self._matches_pattern(location, pattern):
                        is_valid = True
                        break
            
            if not is_valid:
                # Enhanced debug: Show all transformation attempts
                normalized = self._normalize_location_code(location)
                base_location = self._extract_base_location_code(location)
                position_variants = self._normalize_position_format(location)
                print(f"[LOCATION_VALIDATION_FAILED] '{location}' -> Normalized: '{normalized}' -> Base: '{base_location}' -> Position variants: {position_variants} -> NOT FOUND in valid set")
                
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