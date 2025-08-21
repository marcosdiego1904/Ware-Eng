"""
Virtual Invalid Location Evaluator
Replaces the traditional database-heavy InvalidLocationEvaluator with algorithmic validation
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from rule_engine import BaseRuleEvaluator, Rule
from virtual_template_integration import get_virtual_engine_for_warehouse


class VirtualInvalidLocationEvaluator(BaseRuleEvaluator):
    """
    ENHANCED: Invalid location evaluator using virtual location engine
    """
    
    def __init__(self, app=None):
        super().__init__(app)
        self.name = "VirtualInvalidLocationEvaluator"
        print(f"[{self.name}] Initialized with virtual location validation")
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        """
        Evaluate invalid locations using virtual location engine
        """
        print(f"[{self.name}] Starting virtual location validation")
        
        conditions = self._parse_conditions(rule)
        warehouse_id = warehouse_context.get('warehouse_id') if warehouse_context else None
        
        if not warehouse_id:
            print(f"[{self.name}] No warehouse context provided - cannot perform virtual validation")
            return self._fallback_basic_validation(rule, inventory_df)
        
        # Get virtual location engine for this warehouse
        virtual_engine = get_virtual_engine_for_warehouse(warehouse_id)
        
        if not virtual_engine:
            print(f"[{self.name}] No virtual engine available for warehouse {warehouse_id} - using fallback")
            return self._fallback_basic_validation(rule, inventory_df)
        
        return self._evaluate_with_virtual_engine(rule, inventory_df, virtual_engine)
    
    def _evaluate_with_virtual_engine(self, rule: Rule, inventory_df: pd.DataFrame, virtual_engine) -> List[Dict[str, Any]]:
        """
        Perform virtual location validation using the virtual engine
        """
        anomalies = []
        processed_locations = set()  # Avoid duplicate processing
        
        print(f"[{self.name}] Validating {len(inventory_df)} inventory records against virtual warehouse")
        
        for _, pallet in inventory_df.iterrows():
            location = str(pallet.get('location', '')).strip()
            
            # Skip empty/null locations and already processed ones
            if pd.isna(pallet.get('location')) or not location or location in processed_locations:
                continue
            
            processed_locations.add(location)
            
            # CORE VIRTUAL VALIDATION: Single algorithmic check
            is_valid, reason = virtual_engine.validate_location(location)
            
            if not is_valid:
                print(f"[{self.name}] Invalid location detected: '{location}' -> {reason}")
                
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
        
        unique_invalid_locations = len(processed_locations) - (len(inventory_df) - len(anomalies))
        print(f"[{self.name}] Virtual validation complete: {len(anomalies)} anomalies from {unique_invalid_locations} invalid locations")
        
        return anomalies
    
    def _fallback_basic_validation(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Basic fallback validation when virtual engine is not available
        """
        print(f"[{self.name}] Using basic fallback validation (no warehouse context)")
        
        anomalies = []
        basic_invalid_patterns = [
            r'^$',                    # Empty strings
            r'^\s*$',                # Whitespace only  
            r'.*[@#$%^&*()!~`].*',   # Special characters
            r'^.{50,}$',             # Very long codes
            r'INVALID',              # Contains "INVALID"
            r'ERROR',                # Contains "ERROR"
            r'NULL',                 # Contains "NULL"
            r'UNKNOWN'               # Contains "UNKNOWN"
        ]
        
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
        
        print(f"[{self.name}] Basic validation found {len(anomalies)} obviously invalid locations")
        return anomalies


def create_virtual_invalid_location_evaluator(app=None):
    """Factory function to create virtual invalid location evaluator"""
    return VirtualInvalidLocationEvaluator(app)