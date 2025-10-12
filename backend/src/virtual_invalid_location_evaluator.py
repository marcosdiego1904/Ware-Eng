"""
Virtual Invalid Location Evaluator
Replaces the traditional database-heavy InvalidLocationEvaluator with algorithmic validation
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from virtual_template_integration import get_virtual_engine_for_warehouse
from optimized_logging import get_logger, LogLevel, LogCategory


class VirtualInvalidLocationEvaluator:
    """
    ENHANCED: Invalid location evaluator using virtual location engine
    """
    
    def __init__(self, app=None):
        self.app = app
        self.name = "VirtualInvalidLocationEvaluator"
        self.logger = get_logger()
        if self.logger.should_log(LogLevel.DIAGNOSTIC, LogCategory.VIRTUAL_ENGINE):
            print(f"[{self.name}] Initialized with virtual location validation")
    
    def _parse_conditions(self, rule):
        """Parse rule conditions from JSON"""
        try:
            import json
            if hasattr(rule, 'conditions') and rule.conditions:
                return json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions
            return {}
        except (json.JSONDecodeError, AttributeError):
            return {}
    
    def evaluate(self, rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        """
        Evaluate invalid locations using virtual location engine
        """
        rule_name = getattr(rule, 'name', 'Unknown')
        rule_id = getattr(rule, 'id', 'Unknown')
        rule_priority = getattr(rule, 'priority', 'Unknown')
        
        if self.logger.should_log(LogLevel.ESSENTIAL, LogCategory.LOCATION_VALIDATION):
            print(f"\n[LOCATION_VALIDATION] Starting {rule_name} (ID: {rule_id}) - {len(inventory_df):,} records, {inventory_df['location'].nunique():,} unique locations")
        
        if self.logger.should_log(LogLevel.VERBOSE, LogCategory.VIRTUAL_ENGINE):
            sample_locations = list(inventory_df['location'].dropna().unique()[:10])
            print(f"[{self.name}_DEBUG] Sample locations: {sample_locations}")
            print(f"[{self.name}_DEBUG] Warehouse context: {warehouse_context}")
        
        conditions = self._parse_conditions(rule)
        warehouse_id = warehouse_context.get('warehouse_id') if warehouse_context else None
        
        if not warehouse_id:
            if self.logger.should_log(LogLevel.DIAGNOSTIC, LogCategory.VIRTUAL_ENGINE):
                print(f"[{self.name}] ❌ No warehouse context provided - falling back to basic validation")
                print(f"[{self.name}] Available context keys: {list(warehouse_context.keys()) if warehouse_context else 'None'}")
            return self._fallback_basic_validation(rule, inventory_df)
        
        if self.logger.should_log(LogLevel.DIAGNOSTIC, LogCategory.VIRTUAL_ENGINE):
            print(f"[{self.name}] Using warehouse_id: {warehouse_id}")
        
        # Get virtual location engine for this warehouse
        virtual_engine = get_virtual_engine_for_warehouse(warehouse_id)
        
        if not virtual_engine:
            if self.logger.should_log(LogLevel.DIAGNOSTIC, LogCategory.VIRTUAL_ENGINE):
                print(f"[{self.name}] ❌ No virtual engine available for warehouse {warehouse_id} - falling back to basic validation")
            return self._fallback_basic_validation(rule, inventory_df)
        
        if self.logger.should_log(LogLevel.VERBOSE, LogCategory.VIRTUAL_ENGINE):
            try:
                summary = virtual_engine.get_warehouse_summary()
                print(f"[{self.name}] Virtual warehouse summary: {summary}")
            except Exception as e:
                print(f"[{self.name}] Could not get warehouse summary: {e}")
        
        result = self._evaluate_with_virtual_engine(rule, inventory_df, virtual_engine)
        
        # Use the optimized location validation summary instead of verbose debugging
        invalid_count = len(set(anomaly['location'] for anomaly in result))
        total_locations = inventory_df['location'].nunique()
        self.logger.location_validation_summary(total_locations, invalid_count, 'virtual_engine')
        
        if self.logger.should_log(LogLevel.VERBOSE, LogCategory.LOCATION_VALIDATION) and result:
            print(f"[{self.name}] Sample anomaly: {result[0]}")
            
        return result
    
    def _evaluate_with_virtual_engine(self, rule, inventory_df: pd.DataFrame, virtual_engine) -> List[Dict[str, Any]]:
        """
        Perform virtual location validation using the virtual engine
        """
        anomalies = []
        processed_locations = set()  # Avoid duplicate processing
        invalid_locations = []  # Track invalid locations for logging
        
        if self.logger.should_log(LogLevel.VERBOSE, LogCategory.VIRTUAL_ENGINE):
            print(f"[{self.name}] Processing {len(inventory_df)} records, {inventory_df['location'].nunique()} unique locations")
        
        for _, pallet in inventory_df.iterrows():
            location = str(pallet.get('location', '')).strip()
            
            # Skip empty/null locations and already processed ones
            if pd.isna(pallet.get('location')) or not location or location in processed_locations:
                continue
            
            processed_locations.add(location)
            
            # CRITICAL FIX: Check physical special locations first (manually-created locations)
            # This ensures that locations created via "Add New Location" are recognized as valid
            is_valid, reason = self._validate_location_with_physical_fallback(location, virtual_engine)
            
            if not is_valid:
                # Only log invalid locations - this dramatically reduces output
                if self.logger.should_log(LogLevel.DIAGNOSTIC, LogCategory.LOCATION_VALIDATION):
                    print(f"[LOCATION_VALIDATION] ❌ Invalid: '{location}' -> {reason}")
                
                invalid_locations.append(location)
                
                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Invalid Location',
                    'priority': rule.priority,
                    'issue_description': f"Location '{location}' is invalid: {reason}",
                    'details': f"Location validation failed: {reason}",
                    'validation_method': 'virtual_engine',
                    'warehouse_context': virtual_engine.warehouse_id,
                    'enhanced_reason': reason
                })
        
        if self.logger.should_log(LogLevel.VERBOSE, LogCategory.LOCATION_VALIDATION):
            print(f"[{self.name}] Validation complete: {len(anomalies)} anomalies from {len(processed_locations)} locations")
        
        return anomalies
    
    def _fallback_basic_validation(self, rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Basic fallback validation when virtual engine is not available
        """
        if self.logger.should_log(LogLevel.ESSENTIAL, LogCategory.LOCATION_VALIDATION):
            print(f"[LOCATION_VALIDATION] Using basic pattern validation (no virtual engine)")
        
        anomalies = []
        # Enhanced validation patterns supporting enterprise-scale locations
        basic_invalid_patterns = [
            r'^$',                    # Empty strings
            r'^\s*$',                # Whitespace only  
            r'.*[@#$%^&*()!~`].*',   # Special characters
            r'^.{50,}$',             # Very long codes (database limit)
            r'INVALID',              # Contains "INVALID"
            r'ERROR',                # Contains "ERROR"
            r'NULL',                 # Contains "NULL"
            r'UNKNOWN'               # Contains "UNKNOWN"
        ]
        
        if self.logger.should_log(LogLevel.VERBOSE, LogCategory.LOCATION_VALIDATION):
            print(f"[{self.name}] Using {len(basic_invalid_patterns)} validation patterns")
        
        import re
        compiled_patterns = []
        for pattern in basic_invalid_patterns:
            try:
                compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                continue
        
        for _, pallet in inventory_df.iterrows():
            location = str(pallet.get('location', '')).strip()
            
            if pd.isna(pallet.get('location')) or not location:
                continue
            
            # Check against basic invalid patterns
            for pattern in compiled_patterns:
                if pattern.search(location):
                    if self.logger.should_log(LogLevel.DIAGNOSTIC, LogCategory.LOCATION_VALIDATION):
                        print(f"[LOCATION_VALIDATION] ❌ Pattern match: '{location}' (basic validation)")
                    
                    anomalies.append({
                        'pallet_id': pallet['pallet_id'],
                        'location': pallet['location'],
                        'anomaly_type': 'Invalid Location',
                        'priority': rule.priority,
                        'issue_description': f"Location '{location}' appears invalid (basic validation)",
                        'details': 'Basic pattern matching detected invalid location format',
                        'validation_method': 'basic_fallback'
                    })
                    break
        
        # Use the optimized summary
        self.logger.location_validation_summary(inventory_df['location'].nunique(), len(anomalies), 'basic_fallback')
        
        return anomalies

    def _validate_location_with_physical_fallback(self, location: str, virtual_engine) -> tuple:
        """
        Validate location using physical-first approach
        
        This ensures manually-created special locations are recognized as valid,
        matching the same logic used in virtual_compatibility_layer.py
        """
        # First, check if this is a physical special location (manually created)
        if self._is_physical_special_location(location):
            if self.logger.should_log(LogLevel.VERBOSE, LogCategory.LOCATION_VALIDATION):
                print(f"[LOCATION_VALIDATION] ✅ Physical special location recognized: '{location}'")
            return True, "Physical special location"
        
        # If not a physical special location, use virtual engine validation
        return virtual_engine.validate_location(location)
    
    def _is_physical_special_location(self, location: str) -> bool:
        """
        Check if location exists as a physical special location in the database
        
        This matches the same logic from virtual_compatibility_layer.py to ensure
        consistent behavior across the system.
        """
        try:
            # Import here to avoid circular imports
            from models import Location
            from database import db
            
            # Check if location exists as a physical special area
            physical_location = Location.query.filter(
                Location.code == location,
                Location.location_type.in_(['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL'])
            ).first()
            
            if physical_location:
                if self.logger.should_log(LogLevel.VERBOSE, LogCategory.LOCATION_VALIDATION):
                    print(f"[LOCATION_VALIDATION] Found physical special location: {location} (type: {physical_location.location_type})")
                return True
            
            return False
            
        except Exception as e:
            # If database check fails, fall back to virtual validation
            if self.logger.should_log(LogLevel.DIAGNOSTIC, LogCategory.LOCATION_VALIDATION):
                print(f"[LOCATION_VALIDATION] Physical location check failed for '{location}': {e}")
            return False


def create_virtual_invalid_location_evaluator(app=None):
    """Factory function to create virtual invalid location evaluator"""
    return VirtualInvalidLocationEvaluator(app)