"""
Virtual Invalid Location Evaluator
Replaces the traditional database-heavy InvalidLocationEvaluator with algorithmic validation
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from virtual_template_integration import get_virtual_engine_for_warehouse


class VirtualInvalidLocationEvaluator:
    """
    ENHANCED: Invalid location evaluator using virtual location engine
    """
    
    def __init__(self, app=None):
        self.app = app
        self.name = "VirtualInvalidLocationEvaluator"
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
        print(f"\n[{self.name}_DEBUG] ========== VIRTUAL LOCATION VALIDATION START ==========")
        print(f"[{self.name}_DEBUG] Rule: {getattr(rule, 'name', 'Unknown')} (ID: {getattr(rule, 'id', 'Unknown')}) Priority: {getattr(rule, 'priority', 'Unknown')}")
        print(f"[{self.name}_DEBUG] Inventory records to validate: {len(inventory_df):,}")
        print(f"[{self.name}_DEBUG] Unique locations in inventory: {inventory_df['location'].nunique():,}")
        print(f"[{self.name}_DEBUG] Warehouse context: {warehouse_context}")
        
        sample_locations = list(inventory_df['location'].dropna().unique()[:10])
        print(f"[{self.name}_DEBUG] Sample locations: {sample_locations}")
        
        conditions = self._parse_conditions(rule)
        warehouse_id = warehouse_context.get('warehouse_id') if warehouse_context else None
        
        if not warehouse_id:
            print(f"[{self.name}_DEBUG] ❌ CRITICAL: No warehouse context provided - cannot perform virtual validation")
            print(f"[{self.name}_DEBUG] Available context keys: {list(warehouse_context.keys()) if warehouse_context else 'None'}")
            print(f"[{self.name}_DEBUG] Falling back to basic validation patterns")
            return self._fallback_basic_validation(rule, inventory_df)
        
        print(f"[{self.name}_DEBUG] ✅ Using warehouse_id: {warehouse_id}")
        
        # Get virtual location engine for this warehouse
        print(f"[{self.name}_DEBUG] Attempting to get virtual engine for warehouse {warehouse_id}...")
        virtual_engine = get_virtual_engine_for_warehouse(warehouse_id)
        
        if not virtual_engine:
            print(f"[{self.name}_DEBUG] ❌ No virtual engine available for warehouse {warehouse_id}")
            print(f"[{self.name}_DEBUG] This could indicate:")
            print(f"[{self.name}_DEBUG]   - Warehouse {warehouse_id} not configured for virtual locations")
            print(f"[{self.name}_DEBUG]   - Template not applied or missing")
            print(f"[{self.name}_DEBUG]   - Virtual location system disabled")
            print(f"[{self.name}_DEBUG] Falling back to basic validation patterns")
            return self._fallback_basic_validation(rule, inventory_df)
        
        print(f"[{self.name}_DEBUG] ✅ Virtual engine loaded successfully")
        print(f"[{self.name}_DEBUG] Engine warehouse_id: {getattr(virtual_engine, 'warehouse_id', 'Unknown')}")
        try:
            summary = virtual_engine.get_warehouse_summary()
            print(f"[{self.name}_DEBUG] Virtual warehouse summary: {summary}")
        except Exception as e:
            print(f"[{self.name}_DEBUG] Could not get warehouse summary: {e}")
        
        print(f"[{self.name}_DEBUG] Proceeding with virtual engine validation...")
        result = self._evaluate_with_virtual_engine(rule, inventory_df, virtual_engine)
        
        print(f"[{self.name}_DEBUG] ========== VIRTUAL LOCATION VALIDATION COMPLETE ===========")
        print(f"[{self.name}_DEBUG] Total anomalies found: {len(result)}")
        if result:
            print(f"[{self.name}_DEBUG] Sample anomaly: {result[0]}")
            
        return result
    
    def _evaluate_with_virtual_engine(self, rule, inventory_df: pd.DataFrame, virtual_engine) -> List[Dict[str, Any]]:
        """
        Perform virtual location validation using the virtual engine
        """
        anomalies = []
        processed_locations = set()  # Avoid duplicate processing
        
        print(f"[{self.name}_DEBUG] ---------- VIRTUAL ENGINE VALIDATION DETAILS ----------")
        print(f"[{self.name}_DEBUG] Virtual engine type: {type(virtual_engine).__name__}")
        print(f"[{self.name}_DEBUG] Processing {len(inventory_df)} inventory records against virtual warehouse")
        print(f"[{self.name}_DEBUG] Expected to validate {inventory_df['location'].nunique()} unique locations")
        
        for _, pallet in inventory_df.iterrows():
            location = str(pallet.get('location', '')).strip()
            
            # Skip empty/null locations and already processed ones
            if pd.isna(pallet.get('location')) or not location or location in processed_locations:
                continue
            
            processed_locations.add(location)
            
            # CORE VIRTUAL VALIDATION: Single algorithmic check
            print(f"[{self.name}_DEBUG] Validating location: '{location}'")
            is_valid, reason = virtual_engine.validate_location(location)
            print(f"[{self.name}_DEBUG] Result: {'✅ VALID' if is_valid else '❌ INVALID'} - {reason}")
            
            if not is_valid:
                print(f"[{self.name}_DEBUG] 🚨 ANOMALY: Location '{location}' is invalid -> {reason}")
                
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
        
        validation_stats = {
            'total_records_processed': len(inventory_df),
            'unique_locations_checked': len(processed_locations),
            'invalid_locations_found': len(set(a['location'] for a in anomalies)),
            'total_anomalies': len(anomalies),
            'validation_method': 'virtual_engine'
        }
        
        print(f"[{self.name}_DEBUG] ---------- VIRTUAL VALIDATION STATS ----------")
        for key, value in validation_stats.items():
            print(f"[{self.name}_DEBUG] {key}: {value}")
        
        print(f"[{self.name}_DEBUG] Virtual validation complete: {len(anomalies)} anomalies detected")
        
        return anomalies
    
    def _fallback_basic_validation(self, rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Basic fallback validation when virtual engine is not available
        """
        print(f"[{self.name}_DEBUG] ========== BASIC FALLBACK VALIDATION START ===========")
        print(f"[{self.name}_DEBUG] Reason: No virtual engine available")
        print(f"[{self.name}_DEBUG] Using pattern-based validation with {len(basic_invalid_patterns)} patterns")
        print(f"[{self.name}_DEBUG] Patterns: {basic_invalid_patterns}")
        
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
        
        fallback_stats = {
            'total_records_processed': len(inventory_df),
            'patterns_used': len(compiled_patterns),
            'anomalies_found': len(anomalies),
            'validation_method': 'basic_fallback'
        }
        
        print(f"[{self.name}_DEBUG] ---------- FALLBACK VALIDATION STATS ----------")
        for key, value in fallback_stats.items():
            print(f"[{self.name}_DEBUG] {key}: {value}")
        
        print(f"[{self.name}_DEBUG] ========== BASIC FALLBACK VALIDATION COMPLETE ===========")
        return anomalies


def create_virtual_invalid_location_evaluator(app=None):
    """Factory function to create virtual invalid location evaluator"""
    return VirtualInvalidLocationEvaluator(app)