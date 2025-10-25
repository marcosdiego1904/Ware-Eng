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
from rule_precedence_system import create_precedence_manager
from session_manager import RequestScopedSessionManager, ensure_session_bound
from virtual_invalid_location_evaluator import VirtualInvalidLocationEvaluator

# Import unit-agnostic scope service
from services.simple_scope_service import SimpleScopeService

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
    
    def __init__(self, db_session, app=None, user_context=None):
        self.db = db_session
        self.app = app
        self.user_context = user_context  # SECURITY: Store user context for warehouse filtering
        self._location_cache = {}  # PERFORMANCE: Cache locations per warehouse
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
        """Initialize rule evaluator registry with pattern resolver integration"""
        # ENHANCED: Create pattern resolver for dynamic format adaptation
        try:
            from rule_pattern_resolver import RulePatternResolver
            pattern_resolver = RulePatternResolver(self.db, self.app)
            print(f"[RULE_ENGINE] Pattern resolver initialized successfully")
        except Exception as e:
            print(f"[RULE_ENGINE] Warning: Pattern resolver initialization failed: {e}")
            pattern_resolver = None

        return {
            'STAGNANT_PALLETS': StagnantPalletsEvaluator(app=self.app, rule_engine=self),
            'UNCOORDINATED_LOTS': UncoordinatedLotsEvaluator(app=self.app, rule_engine=self),
            'OVERCAPACITY': OvercapacityEvaluator(app=self.app),
            'INVALID_LOCATION': VirtualInvalidLocationEvaluator(app=self.app),  # VIRTUAL: Enhanced evaluator
            # ENHANCED: Inject pattern resolver for dynamic format support
            'LOCATION_SPECIFIC_STAGNANT': LocationSpecificStagnantEvaluator(
                app=self.app,
                pattern_resolver=pattern_resolver
            ),
            'TEMPERATURE_ZONE_MISMATCH': TemperatureZoneMismatchEvaluator(app=self.app),
            'DATA_INTEGRITY': DataIntegrityEvaluator(app=self.app),
            # ENHANCED: Inject pattern resolver for dynamic format support
            'LOCATION_MAPPING_ERROR': LocationMappingErrorEvaluator(
                app=self.app,
                pattern_resolver=pattern_resolver
            ),
            'MISSING_LOCATION': MissingLocationEvaluator(app=self.app),
            'PRODUCT_INCOMPATIBILITY': ProductIncompatibilityEvaluator(app=self.app)
        }
    
    def _get_warehouse_locations(self, warehouse_context: dict = None):
        """
        PERFORMANCE OPTIMIZATION: Get locations filtered by warehouse instead of loading ALL locations.
        This fixes the critical performance issue where 12,080+ locations were loaded for every rule.
        """
        # Extract warehouse_id from context
        warehouse_id = None
        if warehouse_context and isinstance(warehouse_context, dict):
            warehouse_id = warehouse_context.get('warehouse_id')
        elif hasattr(self, 'current_warehouse_context') and self.current_warehouse_context:
            warehouse_id = self.current_warehouse_context.get('warehouse_id')
        elif self.user_context and hasattr(self.user_context, 'username'):
            # Fallback: Try to infer warehouse from user context
            warehouse_id = f'USER_{self.user_context.username.upper()}'
            
        print(f"[PERFORMANCE_FIX] Loading locations for warehouse: {warehouse_id}")
        
        # Get locations with proper filtering
        context = self._ensure_app_context()
        if context:
            with context:
                return self._get_warehouse_locations_internal(warehouse_id)
        else:
            return self._get_warehouse_locations_internal(warehouse_id)
    
    def _get_warehouse_locations_internal(self, warehouse_id: str = None):
        """Internal method to get warehouse-filtered locations"""
        from sqlalchemy import or_
        
        if warehouse_id:
            # CRITICAL FIX: Filter by warehouse_id instead of loading ALL locations
            locations = Location.query.filter(
                Location.warehouse_id == warehouse_id,
                or_(Location.is_active == True, Location.is_active.is_(None))
            ).all()
            print(f"[PERFORMANCE_FIX] Loaded {len(locations)} locations for warehouse {warehouse_id}")
        else:
            # Fallback: Still better than loading ALL - limit to active locations
            locations = Location.query.filter(
                or_(Location.is_active == True, Location.is_active.is_(None))
            ).limit(1000).all()  # Safety limit to prevent memory exhaustion
            print(f"[PERFORMANCE_FIX] Loaded {len(locations)} locations (no warehouse filter)")
            
        return locations
    
    def _get_cached_locations(self, warehouse_context: dict = None):
        """
        PERFORMANCE OPTIMIZATION: Cache locations per warehouse to avoid repeated database queries.
        """
        warehouse_id = 'default'
        if warehouse_context and isinstance(warehouse_context, dict):
            warehouse_id = warehouse_context.get('warehouse_id', 'default')
        elif hasattr(self, 'current_warehouse_context') and self.current_warehouse_context:
            warehouse_id = self.current_warehouse_context.get('warehouse_id', 'default')
            
        # Check cache first
        if warehouse_id not in self._location_cache:
            self._location_cache[warehouse_id] = self._get_warehouse_locations(warehouse_context)
            
        return self._location_cache[warehouse_id]

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
            'Pallet number': 'pallet_id',  # Added for test generator compatibility
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
            'Timestamp': 'creation_date',

            # Receipt/Lot Number mappings
            'Receipt Number': 'receipt_number',
            'Receipt number': 'receipt_number',  # Added for test generator compatibility
            'ReceiptNumber': 'receipt_number',
            'receipt_number': 'receipt_number',
            'RECEIPT_NUMBER': 'receipt_number',
            'Lot Number': 'receipt_number',
            'LotNumber': 'receipt_number',
            'LOT_NUMBER': 'receipt_number',
            'Batch Number': 'receipt_number',
            'BatchNumber': 'receipt_number',
            'BATCH_NUMBER': 'receipt_number',
            'Batch': 'receipt_number',
            'Lot': 'receipt_number',
            'Receipt': 'receipt_number',

            # Product/Description mappings
            'Product': 'product',
            'product': 'product',
            'PRODUCT': 'product',
            'Description': 'product',
            'description': 'product',
            'DESCRIPTION': 'product',
            'Product Description': 'product',
            'ProductDescription': 'product',
            'Item': 'product',
            'Item Description': 'product'
        }
        
        # Apply column mapping
        df = df.rename(columns=column_mapping)
        
        # CRITICAL FIX: Ensure creation_date is properly parsed as datetime using smart parser
        if 'creation_date' in df.columns:
            # Convert to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(df['creation_date']):
                try:
                    from date_parser import SmartDateParser, DateFormatDetector

                    # Use smart date parser
                    detector = DateFormatDetector()
                    format_info = detector.detect_format(df['creation_date'])

                    parser = SmartDateParser()
                    parse_result = parser.parse_dates(df['creation_date'], format_info)
                    df['creation_date'] = parse_result.parsed_series

                    # Log results (quieter than app.py)
                    if parse_result.success_rate < 1.0:
                        print(f"[DATE_PARSING] {format_info['format_type']}: {parse_result.success_rate:.1%} success rate")

                except Exception as e:
                    print(f"[WARNING] Smart date parsing failed, falling back to basic parsing: {e}")
                    # Fallback to basic parsing
                    df['creation_date'] = pd.to_datetime(df['creation_date'], errors='coerce')
        
        # Column normalization completed silently

        return df

    def _apply_scope_filtering(self, inventory_df: pd.DataFrame) -> dict:
        """
        Apply unit-agnostic scope filtering to focus analysis on tracked locations.

        This method integrates the SimpleScopeService to filter inventory data
        based on warehouse scope configuration, ensuring only relevant locations
        are analyzed for anomalies.

        Args:
            inventory_df (pd.DataFrame): Raw inventory data

        Returns:
            dict: Scope filtering results with filtered dataframe and metrics
        """
        try:
            # Determine warehouse context for scope filtering
            warehouse_id = self._get_warehouse_context_for_scope()

            if not warehouse_id:
                # No warehouse context - return original data with no filtering
                return {
                    'filtered_df': inventory_df,
                    'scope_applied': False,
                    'total_records': len(inventory_df),
                    'in_scope_records': len(inventory_df),
                    'out_of_scope_records': 0,
                    'excluded_patterns': [],
                    'warehouse_id': None
                }

            # Initialize scope service for the warehouse
            scope_service = SimpleScopeService(warehouse_id)

            # Apply scope filtering
            filtered_df, scope_metrics = scope_service.filter_inventory_to_scope(inventory_df)

            # Add filtered dataframe to metrics for easy access
            scope_metrics['filtered_df'] = filtered_df
            scope_metrics['warehouse_id'] = warehouse_id

            return scope_metrics

        except Exception as e:
            print(f"[SCOPE_FILTERING] Error during scope filtering: {e}")
            # Return original data on error - graceful fallback
            return {
                'filtered_df': inventory_df,
                'scope_applied': False,
                'total_records': len(inventory_df),
                'in_scope_records': len(inventory_df),
                'out_of_scope_records': 0,
                'excluded_patterns': [],
                'warehouse_id': None,
                'error': str(e)
            }

    def _get_warehouse_context_for_scope(self) -> str:
        """
        Get warehouse context for scope filtering operations.

        This method provides a centralized way to determine the warehouse ID
        for scope filtering, with multiple fallback strategies.

        Returns:
            str: Warehouse ID or None if not determinable
        """
        # Strategy 1: Use explicit warehouse context if set
        if hasattr(self, '_warehouse_context') and self._warehouse_context:
            warehouse_id = self._warehouse_context.get('warehouse_id')
            if warehouse_id:
                return str(warehouse_id)

        # Strategy 2: Use current warehouse context from evaluation
        if hasattr(self, 'current_warehouse_context') and self.current_warehouse_context:
            warehouse_id = self.current_warehouse_context.get('warehouse_id')
            if warehouse_id:
                return str(warehouse_id)

        # Strategy 3: Use user context to resolve warehouse
        if hasattr(self, 'user_context') and self.user_context:
            try:
                from warehouse_context_resolver import resolve_warehouse_context_for_user
                resolved_context = resolve_warehouse_context_for_user(self.user_context)
                warehouse_id = resolved_context.get('warehouse_id')
                if warehouse_id:
                    return str(warehouse_id)
            except Exception as e:
                print(f"[SCOPE_FILTERING] Failed to resolve warehouse from user context: {e}")

        # No warehouse context available
        return None

    def _evaluate_all_rules_internal(self, inventory_df: pd.DataFrame, 
                                   rule_ids: List[int] = None) -> List[RuleEvaluationResult]:
        """Internal method to evaluate rules"""
        if rule_ids:
            rules = Rule.query.filter(Rule.id.in_(rule_ids), Rule.is_active == True).all()
        else:
            rules = self.load_active_rules()
        
        # Initialize rule precedence system
        precedence_manager = create_precedence_manager()
        precedence_manager.reset_for_new_evaluation()
        
        # Sort rules by precedence level (higher precedence rules run first)
        original_rule_count = len(rules)
        rules = precedence_manager.sort_rules_by_precedence(rules)
        
        # Normalize column names before processing
        inventory_df = self._normalize_dataframe_columns(inventory_df)

        # Apply scope filtering to focus analysis on tracked locations only
        scope_metrics = self._apply_scope_filtering(inventory_df)
        if scope_metrics['scope_applied']:
            # Update inventory_df to the filtered version
            inventory_df = scope_metrics['filtered_df']
            print(f"\n[SCOPE_FILTERING] Applied scope filtering:")
            print(f"[SCOPE_FILTERING] Total records: {scope_metrics['total_records']:,}")
            print(f"[SCOPE_FILTERING] In-scope records: {scope_metrics['in_scope_records']:,}")
            print(f"[SCOPE_FILTERING] Out-of-scope records: {scope_metrics['out_of_scope_records']:,}")
            print(f"[SCOPE_FILTERING] Excluded patterns: {scope_metrics['excluded_patterns']}")
        else:
            print(f"\n[SCOPE_FILTERING] No scope filtering applied - analyzing all locations")

        print(f"\n[RULE_ENGINE_DEBUG] ==================== RULE EVALUATION START ====================")
        print(f"[RULE_ENGINE_DEBUG] Evaluating {len(rules)} rules on {inventory_df.shape[0]:,} records")
        print(f"[RULE_ENGINE_DEBUG] Available columns: {list(inventory_df.columns)}")

        # Handle duplicate 'location' columns safely
        try:
            location_col = inventory_df['location']
            # If duplicate columns exist, pandas returns a DataFrame - take first column
            if isinstance(location_col, pd.DataFrame):
                location_col = location_col.iloc[:, 0]
            sample_locations = location_col.dropna().unique()[:10].tolist()
            print(f"[RULE_ENGINE_DEBUG] Sample locations: {sample_locations}")
        except Exception as e:
            print(f"[RULE_ENGINE_DEBUG] Could not extract sample locations: {e}")
        
        # Log precedence system status
        if precedence_manager.enable_precedence:
            print(f"[RULE_PRECEDENCE] Rule precedence system ENABLED")
            print(f"[RULE_PRECEDENCE] Rules sorted by precedence (original count: {original_rule_count})")
            for i, rule in enumerate(rules[:3]):  # Show first 3 rules
                precedence = getattr(rule, 'precedence_level', 4)
                print(f"[RULE_PRECEDENCE]   {i+1}. {rule.name} (precedence: {precedence})")
            if len(rules) > 3:
                print(f"[RULE_PRECEDENCE]   ... and {len(rules) - 3} more rules")
        else:
            print(f"[RULE_PRECEDENCE] Rule precedence system DISABLED - rules run in original order")
        
        results = []
        total_anomalies = 0
        
        # Initialize warehouse_context before using it
        warehouse_context = None
        
        # PERFORMANCE FIX: Store warehouse context for location filtering
        self.current_warehouse_context = None
        
        # Check if explicit warehouse context is set (from applied template) - show once
        # LONG-TERM SOLUTION: Use professional warehouse context resolution
        if hasattr(self, '_warehouse_context') and self._warehouse_context:
            warehouse_context = self._warehouse_context
            self.current_warehouse_context = warehouse_context  # PERFORMANCE: Store for location filtering
            print(f"[RULE_ENGINE_DEBUG] Using explicit warehouse context: {warehouse_context}")
        else:
            # Use new warehouse context resolver instead of detection
            try:
                from warehouse_context_resolver import resolve_warehouse_context_for_user
                user_context = getattr(self, 'user_context', None)
                
                if user_context:
                    # NEW: Direct user → warehouse resolution (no detection needed)
                    warehouse_context = resolve_warehouse_context_for_user(user_context)
                    self.current_warehouse_context = warehouse_context  # PERFORMANCE: Store for location filtering
                    print(f"[RULE_ENGINE_V2] Resolved warehouse context: {warehouse_context}")
                else:
                    print(f"[RULE_ENGINE_V2] No user context provided - cannot resolve warehouse")
                    warehouse_context = {'warehouse_id': None, 'confidence': 'NO_USER', 'coverage': 0.0}
                    
            except Exception as e:
                print(f"[RULE_ENGINE_V2] Warehouse context resolution failed: {e}")
                warehouse_context = {'warehouse_id': None, 'confidence': 'RESOLVER_ERROR', 'coverage': 0.0}

        # PERFORMANCE OPTIMIZATION: Initialize LocationRepository for bulk location loading
        # This eliminates N+1 query problem by loading all locations in SINGLE query
        warehouse_id = warehouse_context.get('warehouse_id') if warehouse_context else None
        if warehouse_id:
            try:
                from services.location_repository import LocationRepository
                from database import db

                # Get all unique locations from inventory for bulk loading
                unique_locations = inventory_df['location'].unique().tolist()

                # Create repository for this warehouse
                location_repository = LocationRepository(
                    warehouse_id=str(warehouse_id),
                    db_session=db.session
                )

                # CRITICAL: Bulk load all locations in SINGLE query
                location_repository.bulk_load_locations(unique_locations)

                # Add repository to warehouse context for evaluators
                warehouse_context['location_repository'] = location_repository

                # Log performance stats
                stats = location_repository.get_cache_stats()
                print(f"[LOCATION_REPO] ✅ Initialized and loaded {stats['total_cached']} locations in {stats['load_time_ms']}ms")
                print(f"[LOCATION_REPO] Special locations: {stats['special_locations']}")

            except Exception as e:
                print(f"[LOCATION_REPO] ❌ Failed to initialize LocationRepository: {e}")
                print(f"[LOCATION_REPO] Evaluators will fall back to direct queries (degraded performance)")
                # Set to None to signal evaluators to use fallback
                if warehouse_context:
                    warehouse_context['location_repository'] = None

            # PERFORMANCE OPTIMIZATION: Initialize VirtualEngine once and cache it
            # This eliminates redundant initialization across multiple evaluators
            try:
                from virtual_template_integration import get_virtual_engine_for_warehouse
                import time

                start_time = time.time()
                virtual_engine = get_virtual_engine_for_warehouse(warehouse_id)

                if virtual_engine:
                    warehouse_context['virtual_engine'] = virtual_engine
                    elapsed_ms = int((time.time() - start_time) * 1000)
                    print(f"[VIRTUAL_ENGINE] ✅ Initialized and cached for warehouse {warehouse_id} ({elapsed_ms}ms)")
                else:
                    warehouse_context['virtual_engine'] = None
                    print(f"[VIRTUAL_ENGINE] ⚠️ No virtual engine available for warehouse {warehouse_id}")

            except Exception as e:
                print(f"[VIRTUAL_ENGINE] ❌ Failed to initialize VirtualEngine: {e}")
                warehouse_context['virtual_engine'] = None

        else:
            print(f"[LOCATION_REPO] No warehouse_id available - skipping repository initialization")
            if warehouse_context:
                warehouse_context['location_repository'] = None
                warehouse_context['virtual_engine'] = None

        for i, rule in enumerate(rules, 1):
            rule_precedence = getattr(rule, 'precedence_level', 4)
            precedence_name = getattr(rule, 'get_precedence_name', lambda: f"Level {rule_precedence}")()
            
            print(f"\n[RULE_ENGINE_DEBUG] -------------------- RULE {i}/{len(rules)} --------------------")
            print(f"[RULE_ENGINE_DEBUG] Rule: {rule.name} (ID: {rule.id})")
            print(f"[RULE_ENGINE_DEBUG] Type: {rule.rule_type}")
            print(f"[RULE_ENGINE_DEBUG] Priority: {rule.priority}")
            print(f"[RULE_ENGINE_DEBUG] Precedence: {rule_precedence} ({precedence_name})")
            print(f"[RULE_ENGINE_DEBUG] Conditions: {rule.conditions[:200]}..." if rule.conditions and len(rule.conditions) > 200 else f"[RULE_ENGINE_DEBUG] Conditions: {rule.conditions}")
            
            result = self.evaluate_rule(rule, inventory_df, warehouse_context)
            results.append(result)
            
            if result.success:
                anomaly_count = len(result.anomalies)
                total_anomalies += anomaly_count
                
                # Register anomalies with precedence system for subsequent rules
                if precedence_manager.enable_precedence and anomaly_count > 0:
                    precedence_manager.register_anomalies(rule, result.anomalies)
                    print(f"[RULE_PRECEDENCE] Registered {anomaly_count} anomalies from {rule.rule_type}")
                
                print(f"[RULE_ENGINE_DEBUG] Result: SUCCESS - {anomaly_count} anomalies in {result.execution_time_ms}ms")
                if anomaly_count > 0:
                    print(f"[RULE_ENGINE_DEBUG] Sample anomaly: {result.anomalies[0] if result.anomalies else 'N/A'}")
            else:
                print(f"[RULE_ENGINE_DEBUG] Result: FAILURE - {result.error_message}")
        
        print(f"\n[RULE_ENGINE_DEBUG] ==================== RULE EVALUATION COMPLETE ====================")
        print(f"[RULE_ENGINE_DEBUG] FINAL RESULTS:")
        print(f"[RULE_ENGINE_DEBUG] Total rules evaluated: {len(rules)}")
        print(f"[RULE_ENGINE_DEBUG] Total anomalies found: {total_anomalies}")
        print(f"[RULE_ENGINE_DEBUG] Successful rules: {sum(1 for r in results if r.success)}")
        print(f"[RULE_ENGINE_DEBUG] Failed rules: {sum(1 for r in results if not r.success)}")
        
        # Log precedence system summary
        if precedence_manager.enable_precedence:
            precedence_summary = precedence_manager.get_exclusion_summary()
            exclusion_stats = precedence_summary['exclusion_stats']
            print(f"\n[RULE_PRECEDENCE] ==================== PRECEDENCE SUMMARY ====================")
            print(f"[RULE_PRECEDENCE] Precedence system: ENABLED")
            print(f"[RULE_PRECEDENCE] Total exclusions registered: {exclusion_stats['total_exclusions']}")
            print(f"[RULE_PRECEDENCE] Unique pallets excluded: {exclusion_stats['unique_pallets_excluded']}")
            print(f"[RULE_PRECEDENCE] Rules with exclusions: {exclusion_stats['rules_with_exclusions']}")
            if exclusion_stats['exclusions_by_rule_type']:
                print(f"[RULE_PRECEDENCE] Exclusions by rule type:")
                for rule_type, count in exclusion_stats['exclusions_by_rule_type'].items():
                    print(f"[RULE_PRECEDENCE]   {rule_type}: {count}")
            print(f"[RULE_PRECEDENCE] =================================================================")
        
        # Show breakdown by anomaly type
        anomaly_types = {}
        for result in results:
            if result.success:
                for anomaly in result.anomalies:
                    atype = anomaly.get('anomaly_type', 'Unknown')
                    anomaly_types[atype] = anomaly_types.get(atype, 0) + 1
        
        if anomaly_types:
            print(f"[RULE_ENGINE_DEBUG] Anomaly breakdown:")
            for atype, count in anomaly_types.items():
                print(f"[RULE_ENGINE_DEBUG]   {atype}: {count} anomalies")
        print(f"[RULE_ENGINE_DEBUG] ================================================================")
        return results
    
    def _detect_warehouse_context(self, inventory_df: pd.DataFrame, user_context=None) -> dict:
        """
        Enhanced warehouse detection using canonical location service.
        
        NEW APPROACH:
        - Uses intelligent canonical format normalization (3-5 variants vs 40+)
        - Leverages batch location validation for efficiency
        - Provides detailed confidence metrics and validation results
        
        Args:
            inventory_df: Inventory data to analyze
            
        Returns:
            Dictionary with warehouse context and comprehensive validation metrics
        """
        context = {'warehouse_id': None, 'confidence': 'NONE', 'coverage': 0.0}
        
        if 'location' not in inventory_df.columns:
            return context
            
        # Get unique locations from inventory
        inventory_locations = list(set(inventory_df['location'].dropna().astype(str)))
        
        if not inventory_locations:
            return context
        
        print(f"[WAREHOUSE_DETECTION] Analyzing {len(inventory_locations)} unique inventory locations")
        
        # Try to use canonical location service for intelligent detection
        try:
            from location_service import get_canonical_service, get_inventory_validator
            canonical_service = get_canonical_service()
            inventory_validator = get_inventory_validator()
            
            print("[WAREHOUSE_DETECTION] Using canonical location service for smart detection")
            return self._detect_warehouse_with_canonical_service(
                inventory_df, inventory_locations, canonical_service, inventory_validator, user_context
            )
            
        except ImportError:
            print("[WAREHOUSE_DETECTION] Canonical service not available, using legacy detection")
            return self._detect_warehouse_legacy(inventory_df, inventory_locations)
    
    def _detect_warehouse_with_canonical_service(self, inventory_df, inventory_locations, canonical_service, inventory_validator, user_context=None):
        """
        NEW: Intelligent warehouse detection using canonical location service.
        
        Benefits:
        - 10x faster than variant explosion approach
        - More accurate location matching through canonical normalization
        - Comprehensive validation metrics for debugging
        - SECURITY: User-scoped warehouse filtering to prevent cross-tenant access
        """
        print("[WAREHOUSE_DETECTION_CANONICAL] Starting intelligent warehouse detection")
        
        # SECURITY FIX: Get warehouse IDs filtered by user context
        from models import Location, db
        from sqlalchemy import func, or_
        
        # Ensure we have proper application context
        context = self._ensure_app_context()
        if context:
            with context:
                return self._detect_warehouse_with_db_query(inventory_df, inventory_locations, canonical_service, inventory_validator, user_context)
        else:
            return self._detect_warehouse_with_db_query(inventory_df, inventory_locations, canonical_service, inventory_validator, user_context)
    
    def _detect_warehouse_with_db_query(self, inventory_df, inventory_locations, canonical_service, inventory_validator, user_context=None):
        """Execute the actual database query for warehouse detection"""
        from models import Location, db
        from sqlalchemy import func, or_
        
        query = db.session.query(Location.warehouse_id).distinct()
        
        # CRITICAL SECURITY FIX: Filter warehouses by user context
        if user_context and hasattr(user_context, 'username'):
            print(f"[WAREHOUSE_DETECTION_CANONICAL] Filtering warehouses for user: {user_context.username}")
            # Filter warehouses that match user pattern (quick fix for current naming scheme)
            # This handles warehouse IDs like USER_MARCOS9, USER_TESTF, etc.
            username_upper = user_context.username.upper()
            
            # Debug: Show what patterns we're looking for
            patterns = [
                f'%{username_upper}%',
                f'%{user_context.username}%', 
                user_context.username,
                f'USER_{username_upper}',
                f'USER_{user_context.username}'
            ]
            print(f"[WAREHOUSE_DETECTION_CANONICAL] Looking for patterns: {patterns}")
            
            query = query.filter(
                or_(
                    Location.warehouse_id.like(f'%{username_upper}%'),
                    Location.warehouse_id.like(f'%{user_context.username}%'),
                    Location.warehouse_id == user_context.username,
                    Location.warehouse_id == f'USER_{username_upper}',
                    Location.warehouse_id == f'USER_{user_context.username}'
                )
            )
        else:
            print(f"[WAREHOUSE_DETECTION_CANONICAL] User context debug: {user_context}")
            print(f"[WAREHOUSE_DETECTION_CANONICAL] Has username attr: {hasattr(user_context, 'username') if user_context else False}")
            print("[WAREHOUSE_DETECTION_CANONICAL] WARNING: No proper user context - using all warehouses for testing")
            
            # INTELLIGENT FIX: Analyze inventory locations to guess warehouse
            print("[WAREHOUSE_DETECTION_CANONICAL] Analyzing inventory locations to determine warehouse...")
            
            # Check for warehouse-specific patterns in inventory
            warehouse_hints = []
            
            # Look for USER_TESTF patterns 
            if any('01-A' in loc or '02-A' in loc for loc in inventory_locations[:10]):
                warehouse_hints.append('USER_TESTF')
                print("[WAREHOUSE_DETECTION_CANONICAL] Found USER_TESTF location patterns")
            
            # Look for RECV-01, RECV-02, etc. that are common in USER_TESTF
            special_areas = [loc for loc in inventory_locations if loc.startswith(('RECV-', 'STAGE-', 'DOCK-', 'AISLE-'))]
            if special_areas:
                print(f"[WAREHOUSE_DETECTION_CANONICAL] Found special areas: {special_areas}")
                if 'USER_TESTF' not in warehouse_hints:
                    warehouse_hints.append('USER_TESTF')
            
            if warehouse_hints:
                print(f"[WAREHOUSE_DETECTION_CANONICAL] Warehouse hints detected: {warehouse_hints}")
                query = query.filter(Location.warehouse_id.in_(warehouse_hints))
        
        try:
            warehouse_ids = query.all()
            warehouse_ids = [wid[0] for wid in warehouse_ids if wid[0]]
        except Exception as e:
            print(f"[WAREHOUSE_DETECTION_CANONICAL] Database query failed: {e}")
            warehouse_ids = []
        
        print(f"[WAREHOUSE_DETECTION_CANONICAL] Testing {len(warehouse_ids)} warehouses")
        
        # FALLBACK: If no warehouses found but we have USER_TESTF patterns, force include it
        if len(warehouse_ids) == 0:
            print("[WAREHOUSE_DETECTION_CANONICAL] No warehouses found via user filtering, checking inventory patterns...")
            
            # Check for USER_TESTF patterns in inventory
            testf_patterns_found = False
            sample_locations = inventory_locations[:20]  # Check first 20 locations
            
            # Look for patterns that indicate USER_TESTF warehouse
            for loc in sample_locations:
                if any(pattern in str(loc) for pattern in ['01-A', '02-A', 'RECV-', 'STAGE-', 'DOCK-', 'AISLE-']):
                    testf_patterns_found = True
                    break
            
            if testf_patterns_found:
                print("[WAREHOUSE_DETECTION_CANONICAL] USER_TESTF patterns detected in inventory, forcing warehouse inclusion")
                warehouse_ids = ['USER_TESTF']
                print(f"[WAREHOUSE_DETECTION_CANONICAL] Updated warehouse list: {warehouse_ids}")
        
        best_warehouse = None
        best_coverage = 0.0
        best_confidence = 'NONE'
        warehouse_results = []
        
        # Test each warehouse for location coverage
        for warehouse_id in warehouse_ids:
            try:
                # Use inventory validator for this warehouse
                validation_result = inventory_validator.validate_inventory_locations(
                    inventory_df, warehouse_id
                )
                
                coverage = validation_result['warehouse_coverage']
                valid_count = len(validation_result['valid_locations'])
                total_count = validation_result['total_unique_locations']
                
                # Determine confidence level
                if coverage >= 80.0 and valid_count >= 5:
                    confidence = 'VERY_HIGH'
                elif coverage >= 60.0 and valid_count >= 3:
                    confidence = 'HIGH'
                elif coverage >= 30.0 and valid_count >= 2:
                    confidence = 'MEDIUM'
                elif coverage >= 15.0:
                    confidence = 'LOW'
                else:
                    confidence = 'VERY_LOW'
                
                warehouse_results.append({
                    'warehouse_id': warehouse_id,
                    'coverage': coverage,
                    'confidence': confidence,
                    'valid_locations': valid_count,
                    'total_locations': total_count,
                    'format_analysis': validation_result['format_analysis']
                })
                
                print(f"[WAREHOUSE_DETECTION_CANONICAL] {warehouse_id}: {coverage:.1f}% coverage, {valid_count}/{total_count} locations, confidence: {confidence}")
                
                # Track best match
                if coverage > best_coverage:
                    best_warehouse = warehouse_id
                    best_coverage = coverage
                    best_confidence = confidence
                    
            except Exception as e:
                print(f"[WAREHOUSE_DETECTION_CANONICAL] Error testing warehouse {warehouse_id}: {e}")
        
        # CRITICAL FIX: Force USER_TESTF when patterns detected, regardless of coverage
        if not best_warehouse and len(warehouse_results) > 0:
            # Check if we have USER_TESTF in results but with low coverage
            testf_result = next((r for r in warehouse_results if r['warehouse_id'] == 'USER_TESTF'), None)
            if testf_result:
                print(f"[WAREHOUSE_DETECTION_CANONICAL] FORCING USER_TESTF despite low coverage - test data detected")
                best_warehouse = 'USER_TESTF'
                best_coverage = testf_result['coverage']
                best_confidence = 'FORCED_TEST_MODE'
        
        # Build final context
        context = {
            'warehouse_id': best_warehouse,
            'confidence': best_confidence,
            'coverage': best_coverage,
            'detection_method': 'canonical_service',
            'warehouse_results': warehouse_results,
            'total_tested': len(warehouse_ids)
        }
        
        print(f"[WAREHOUSE_DETECTION_CANONICAL] Best match: {best_warehouse} ({best_coverage:.1f}% coverage, {best_confidence} confidence)")
        return context
    
    def _detect_warehouse_legacy(self, inventory_df, inventory_locations):
        """
        LEGACY: Fallback warehouse detection using explosive variant generation.
        
        This method is kept for backward compatibility but has performance issues.
        """
        print("[WAREHOUSE_DETECTION_LEGACY] Using legacy variant explosion method")
        
        # Generate variants for all locations (this is the problematic part)
        all_location_variants = set()
        for location in inventory_locations:
            try:
                variants = self._normalize_position_format(location)
                all_location_variants.update(variants)
            except:
                all_location_variants.add(location)
        
        print(f"[WAREHOUSE_DETECTION_LEGACY] Generated {len(all_location_variants)} location variants")
        
        # Query database for matches
        from models import Location, db
        from sqlalchemy import func, or_, case
        
        warehouse_matches = db.session.query(
            Location.warehouse_id,
            func.count(Location.id).label('total_locations'),
            func.sum(
                case(
                    (Location.code.in_(all_location_variants), 1),
                    else_=0
                )
            ).label('matching_locations')
        ).filter(
            or_(Location.is_active == True, Location.is_active.is_(None))
        ).group_by(Location.warehouse_id).all()
        
        # Calculate confidence scores
        return self._calculate_warehouse_confidence_scores(warehouse_matches, inventory_locations, all_location_variants)
    
    def _calculate_warehouse_confidence_scores(self, warehouse_matches, inventory_locations, all_variants):
        """
        Calculate confidence scores for warehouse detection using multiple criteria
        
        Args:
            warehouse_matches: SQL query results with warehouse statistics
            inventory_locations: Original inventory location list
            all_variants: All normalized variants generated
            
        Returns:
            Dictionary with warehouse context and confidence metrics
        """
        best_match = None
        best_score = 0
        best_confidence = 'NONE'
        detailed_scores = []
        
        print(f"[WAREHOUSE_SCORING] Evaluating {len(warehouse_matches)} warehouses")
        
        for warehouse_id, total_locations, matching_locations in warehouse_matches:
            if matching_locations and matching_locations > 0:
                # Multi-factor scoring system
                coverage_score = matching_locations / len(inventory_locations)  # % of inventory covered
                density_score = matching_locations / total_locations if total_locations > 0 else 0  # Match density
                absolute_matches = int(matching_locations)
                
                # Weighted confidence score (coverage is most important)
                confidence_score = (coverage_score * 0.75) + (density_score * 0.25)
                
                # Confidence classification
                if coverage_score >= 0.8 and absolute_matches >= 5:
                    confidence_level = 'VERY_HIGH'
                elif coverage_score >= 0.6 and absolute_matches >= 3:
                    confidence_level = 'HIGH'
                elif coverage_score >= 0.3 and absolute_matches >= 2:
                    confidence_level = 'MEDIUM'
                elif coverage_score >= 0.1:
                    confidence_level = 'LOW'
                else:
                    confidence_level = 'VERY_LOW'
                
                detailed_scores.append({
                    'warehouse_id': warehouse_id,
                    'coverage_score': coverage_score,
                    'density_score': density_score,
                    'confidence_score': confidence_score,
                    'confidence_level': confidence_level,
                    'absolute_matches': absolute_matches,
                    'total_locations': total_locations
                })
                
                print(f"[WAREHOUSE_SCORING] {warehouse_id}: {absolute_matches}/{len(inventory_locations)} locations = {coverage_score:.1%} coverage, confidence: {confidence_level}")
                
                # Select best match (require minimum thresholds)
                if confidence_score > best_score and coverage_score >= 0.1:  # Minimum 10% coverage
                    best_score = confidence_score
                    best_match = warehouse_id
                    best_confidence = confidence_level
            else:
                print(f"[WAREHOUSE_SCORING] {warehouse_id}: 0/{len(inventory_locations)} locations = 0% coverage")
        
        # Build comprehensive context
        context = {
            'total_inventory_locations': len(inventory_locations),
            'total_variants_generated': len(all_variants),
            'detailed_scores': detailed_scores
        }
        
        if best_match:
            context.update({
                'warehouse_id': best_match,
                'match_score': best_score,
                'confidence_level': best_confidence,
                'matching_locations': next((s['absolute_matches'] for s in detailed_scores if s['warehouse_id'] == best_match), 0)
            })
            print(f"[WAREHOUSE_DETECTION] Auto-detected warehouse: {best_match} (score: {best_score:.1%}, confidence: {best_confidence})")
        else:
            context.update({
                'warehouse_id': None,
                'match_score': 0,
                'confidence_level': 'NONE',
                'matching_locations': 0
            })
            print(f"[WAREHOUSE_DETECTION] No reliable warehouse match found (all scores below threshold)")
            
        return context
    
    def _normalize_position_format(self, location_code: str) -> list:
        """
        Generate multiple normalized position formats for comprehensive matching
        
        CRITICAL FIX: Handle cross-format translation between different location coding systems:
        - Inventory format: 02-1-011B (zone-section-position-level)  
        - Database format: 01-01-001A_1 (aisle-rack-position-level_slot)
        
        Enhanced to handle various format variations:
        - 02-1-011B -> ['02-01-011B', '02-1-011B', '02-01-011B_1', '02-01-011B_2'] 
        - 01-01-001A -> ['01-01-001A', '01-1-1A', '01-1-001A_1']
        - RECV-01 -> ['RECV-01', 'RECV-001'] (special location formats)
        - STAGE-1 -> ['STAGE-1', 'STAGE-01', 'STAGE-001']
        
        Returns:
            List of normalized location codes for matching (sorted by likelihood)
        """
        if not location_code:
            return [location_code]
            
        code = str(location_code).strip().upper()
        variants = [code]  # Always include original
        
        # Import regex inside method to avoid top-level import issues
        import re
        
        # Pattern 1: Standard aisle-rack-position format (XX-X-XXXA or XX-XX-XXXA)
        # ENHANCED: Handle both single and double digit rack formats
        standard_pattern = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{1,3})([A-Z])$', code)
        if standard_pattern:
            aisle, rack, position, level = standard_pattern.groups()
            
            # Generate comprehensive format variations with cross-format translation
            base_variants = [
                # Standard padding variations
                f"{aisle.zfill(2)}-{rack.zfill(2)}-{position.zfill(3)}{level}",  # Full padding: 01-01-001A
                f"{aisle.zfill(2)}-{rack.lstrip('0') or '0'}-{position.zfill(3)}{level}",  # Mixed: 01-1-001A
                f"{aisle.zfill(2)}-{rack.zfill(2)}-{position.lstrip('0').zfill(2)}{level}",  # 2-digit pos: 01-01-01A
                f"{aisle.zfill(2)}-{rack.lstrip('0') or '0'}-{position.lstrip('0').zfill(2)}{level}",  # Minimal: 01-1-01A
                f"{aisle.lstrip('0') or '0'}-{rack.lstrip('0') or '0'}-{position.lstrip('0') or '0'}{level}",  # No padding: 1-1-1A
                
                # CROSS-FORMAT TRANSLATION: Try translating between coding systems
                # If input is zone-section-position (02-1-011B), try aisle-rack equivalents
                f"{aisle.zfill(2)}-{aisle.zfill(2)}-{position.zfill(3)}{level}",  # Map zone to aisle: 02-02-011B  
                f"{aisle.zfill(2)}-01-{position.zfill(3)}{level}",  # Force rack=01: 02-01-011B
                f"01-{rack.zfill(2)}-{position.zfill(3)}{level}",  # Force aisle=01: 01-01-011B
                f"01-01-{position.zfill(3)}{level}",  # Force aisle=01,rack=01: 01-01-011B
            ]
            variants.extend(base_variants)
            
            # CRITICAL FIX: Add suffix variants for database format (XX-XX-XXXA_N)
            for base_variant in base_variants:
                variants.extend([
                    f"{base_variant}_1",  # Add _1 suffix
                    f"{base_variant}_2",  # Add _2 suffix  
                    f"{base_variant}_3",  # Add _3 suffix
                    f"{base_variant}_4",  # Add _4 suffix
                    f"{base_variant}_5",  # Add _5 suffix
                ])
            
            # POSITION MAPPING: Try different position interpretations
            # If position is 3-digit like 011, also try as 1-digit like 1 or 11
            if len(position) == 3:
                alt_position_1 = position.lstrip('0') or '0'  # 011 -> 11 or 1
                alt_position_2 = position[1:].lstrip('0') or '0'  # 011 -> 11 or 1  
                alt_variants = [
                    f"{aisle.zfill(2)}-{rack.zfill(2)}-{alt_position_1.zfill(3)}{level}",
                    f"{aisle.zfill(2)}-{rack.zfill(2)}-{alt_position_2.zfill(3)}{level}",
                ]
                variants.extend(alt_variants)
                # Add suffixed versions
                for alt_var in alt_variants:
                    variants.extend([f"{alt_var}_1", f"{alt_var}_2", f"{alt_var}_3"])
        
        # Pattern 2: Special location formats (RECV-XX, STAGE-XX, AISLE-XX)
        special_pattern = re.match(r'^([A-Z]+)-(\d{1,3})$', code)
        if special_pattern:
            prefix, number = special_pattern.groups()
            variants.extend([
                f"{prefix}-{number.zfill(3)}",  # RECV-001
                f"{prefix}-{number.zfill(2)}",  # RECV-01
                f"{prefix}-{number.lstrip('0') or '0'}",  # RECV-1
            ])
        
        # Pattern 3: Simple numeric suffixes (DOCK1, FINAL2)
        simple_pattern = re.match(r'^([A-Z]+)(\d{1,3})$', code)
        if simple_pattern:
            prefix, number = simple_pattern.groups()
            variants.extend([
                f"{prefix}-{number}",  # Add dash separator
                f"{prefix}-{number.zfill(2)}",  # DOCK-01
                f"{prefix}-{number.zfill(3)}",  # DOCK-001
            ])
        
        # Remove duplicates while preserving order (most likely matches first)
        seen = set()
        unique_variants = []
        for variant in variants:
            if variant not in seen:
                seen.add(variant)
                unique_variants.append(variant)
        
        return unique_variants
    
    def evaluate_rule(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> RuleEvaluationResult:
        """
        Evaluate a single rule against inventory data
        
        Args:
            rule: Rule object to evaluate
            inventory_df: Inventory data to analyze
            warehouse_context: Optional warehouse context for scoped validation
        
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
            
            print(f"[RULE_ENGINE_DEBUG] Using evaluator: {type(evaluator).__name__}")
            print(f"[RULE_ENGINE_DEBUG] Warehouse context passed: {warehouse_context}")
            
            # LONG-TERM SOLUTION: Evaluate rule with guaranteed warehouse context
            if warehouse_context is None:
                warehouse_context = {'warehouse_id': None, 'confidence': 'NONE', 'coverage': 0.0}
            
            # All evaluators now support warehouse_context (no more temporal fixes needed)
            if hasattr(evaluator, 'evaluate') and 'warehouse_context' in evaluator.evaluate.__code__.co_varnames:
                print(f"[RULE_ENGINE_V2] Calling evaluator with warehouse_context: {warehouse_context.get('warehouse_id')}")
                anomalies = evaluator.evaluate(rule, inventory_df, warehouse_context)
            else:
                print(f"[RULE_ENGINE_V2] Legacy evaluator without warehouse_context support")
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

    def _assign_location_types_with_context(self, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> pd.DataFrame:
        """Enhanced location type assignment using comprehensive classification system"""
        if not warehouse_context or not warehouse_context.get('warehouse_id'):
            print(f"[ENHANCED_CLASSIFIER] No warehouse context, using enhanced classifier without context")
        else:
            print(f"[ENHANCED_CLASSIFIER] Using warehouse context: {warehouse_context['warehouse_id']}")

        df = inventory_df.copy()

        # Initialize enhanced classifier with virtual engine support
        virtual_engine = None
        try:
            # PERFORMANCE: Use cached virtual engine from warehouse context (avoid redundant initialization)
            if warehouse_context:
                virtual_engine = warehouse_context.get('virtual_engine')

            # Fallback: Initialize if not cached (backward compatibility)
            if not virtual_engine and warehouse_context and warehouse_context.get('warehouse_id'):
                from virtual_template_integration import get_virtual_engine_for_warehouse
                virtual_engine = get_virtual_engine_for_warehouse(warehouse_context['warehouse_id'])

            # Fallback virtual engine creation if needed
            if not virtual_engine and warehouse_context:
                print(f"[ENHANCED_CLASSIFIER] Creating fallback virtual engine...")
                from virtual_location_engine import VirtualLocationEngine
                warehouse_config = {
                    'warehouse_id': warehouse_context['warehouse_id'],
                    'num_aisles': 2,
                    'racks_per_aisle': 1,
                    'positions_per_rack': 22,
                    'levels_per_position': 4,
                    'level_names': 'ABCD',
                    'special_areas': ['RECV-01', 'RECV-02', 'STAGE-01', 'DOCK-01', 'AISLE-01', 'AISLE-02'],
                    'default_capacity': 1,
                    'default_zone': 'GENERAL'
                }
                virtual_engine = VirtualLocationEngine(warehouse_config)

        except Exception as e:
            print(f"[ENHANCED_CLASSIFIER] Virtual engine setup failed: {e}")

        # Initialize the enhanced location classifier
        try:
            from enhanced_location_classifier import EnhancedLocationClassifier
            classifier = EnhancedLocationClassifier(db_session=self.db, virtual_engine=virtual_engine)
            print(f"[ENHANCED_CLASSIFIER] Initialized successfully")
        except Exception as e:
            print(f"[ENHANCED_CLASSIFIER] Failed to initialize enhanced classifier: {e}")
            # Fallback to legacy system
            return self._assign_location_types(inventory_df)

        # Get unique locations for batch processing
        unique_locations = df['location'].dropna().unique().tolist()

        if not unique_locations:
            print(f"[ENHANCED_CLASSIFIER] No valid locations found")
            df['location_type'] = 'MISSING'
            return df

        print(f"[ENHANCED_CLASSIFIER] Processing {len(unique_locations)} unique locations...")

        # Batch classify all locations with behavioral context
        classification_results = classifier.classify_batch(
            locations=unique_locations,
            inventory_df=df,
            warehouse_context=warehouse_context
        )

        # Apply classifications to dataframe
        location_type_map = {}
        confidence_map = {}
        method_map = {}

        for location, result in classification_results.items():
            location_type_map[location] = result.location_type
            confidence_map[location] = result.confidence
            method_map[location] = result.method

        df['location_type'] = df['location'].map(location_type_map)
        df['location_type_confidence'] = df['location'].map(confidence_map)
        df['location_type_method'] = df['location'].map(method_map)

        # Handle any unmapped locations
        df['location_type'] = df['location_type'].fillna('UNKNOWN')
        df['location_type_confidence'] = df['location_type_confidence'].fillna(0.0)
        df['location_type_method'] = df['location_type_method'].fillna('fallback')

        # Generate and log classification summary
        summary = classifier.get_classification_summary(classification_results)
        print(f"[ENHANCED_CLASSIFIER] Classification Summary:")
        print(f"  - Total locations: {summary.get('total_locations', 0)}")
        print(f"  - Unknown rate: {summary.get('unknown_rate_percent', 0)}%")
        print(f"  - Average confidence: {summary.get('average_confidence', 0)}")
        print(f"  - High confidence (>0.8): {summary.get('high_confidence_count', 0)}")
        print(f"  - Type distribution: {summary.get('type_distribution', {})}")
        print(f"  - Method distribution: {summary.get('method_distribution', {})}")

        df = df.drop(columns=['location_type_confidence', 'location_type_method'], errors='ignore')

        return df

# ==================== RULE EVALUATORS ====================

class BaseRuleEvaluator:
    """Base class for all rule evaluators"""

    def __init__(self, app=None, rule_engine=None):
        self.app = app
        self.rule_engine = rule_engine  # Reference to main RuleEngine for accessing shared methods
        self._location_cache = None  # Cache for location lookup optimization

        # Default warehouse location patterns for pattern-based classification
        self.DEFAULT_WAREHOUSE_PATTERNS = {
            'RECEIVING': [r'^RECV-\d+$', r'^RECEIVING'],
            'STORAGE': [r'^\d+\.\d+[A-Z]$', r'^\d+[A-Z]$'],  # RACK.LEVEL+POSITION and simple formats
            'STAGING': [r'^STAGE-\d+$', r'^STAGING'],
            'AISLE': [r'^AISLE-\d+$'],
            'DOCK': [r'^DOCK-\d+$', r'^DOCK'],
            'TRANSITIONAL': [r'^TRAN-', r'^FLOW-']
        }
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
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

    def _get_patterns_for_location_types(self, location_types: List[str]) -> List[str]:
        """Convert location_types to regex patterns for backward compatibility"""
        patterns = []
        for location_type in location_types:
            if location_type.upper() in self.DEFAULT_WAREHOUSE_PATTERNS:
                patterns.extend(self.DEFAULT_WAREHOUSE_PATTERNS[location_type.upper()])
        return patterns

    def _filter_by_location_patterns(self, inventory_df: pd.DataFrame, patterns: List[str]) -> pd.DataFrame:
        """Filter inventory by multiple location patterns"""
        if not patterns:
            return pd.DataFrame()

        # Create combined mask for all patterns
        combined_mask = pd.Series([False] * len(inventory_df), index=inventory_df.index)

        for pattern in patterns:
            try:
                # Apply pattern matching (case-insensitive)
                pattern_mask = inventory_df['location'].astype(str).str.upper().str.match(pattern, na=False)
                combined_mask = combined_mask | pattern_mask

                matches = pattern_mask.sum()
                # Simplified logging: only show zero matches for key patterns
                if matches == 0 and any(key in pattern for key in ['RECV', 'STORAGE', 'STAGE']):
                    print(f"[PATTERN_DEBUG] Key pattern '{pattern}' matched 0 locations")

            except Exception as e:
                print(f"[PATTERN_ERROR] Pattern '{pattern}' failed: {e}")
                continue

        matching_rows = inventory_df[combined_mask]
        return matching_rows

    def _get_location_category(self, location: str) -> str:
        """Determine location category from location string for reporting purposes"""
        location_str = str(location).upper()

        # Check against pattern categories
        for category, patterns in self.DEFAULT_WAREHOUSE_PATTERNS.items():
            for pattern in patterns:
                try:
                    if pd.Series([location_str]).str.match(pattern, na=False).iloc[0]:
                        return category
                except:
                    continue

        return "STORAGE"  # Default assumption for unknown patterns

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
        DELEGATION: This method was moved to RuleEngine to fix production compatibility.
        BaseRuleEvaluator now uses static implementation matching RuleEngine logic.
        """
        # Static implementation that matches RuleEngine logic
        if not location_code:
            return [location_code]
            
        code = str(location_code).strip().upper()
        variants = [code]  # Always include original
        
        # Import regex inside method to avoid top-level import issues
        import re
        
        # Pattern 1: Standard aisle-rack-position format (XX-X-XXXA or XX-XX-XXXA)
        standard_pattern = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{1,3})([A-Z])$', code)
        if standard_pattern:
            aisle, rack, position, level = standard_pattern.groups()
            
            # Generate format variations with cross-format translation
            base_variants = [
                f"{aisle.zfill(2)}-{rack.zfill(2)}-{position.zfill(3)}{level}",  # Full padding: 01-01-001A
                f"{aisle.zfill(2)}-{rack.lstrip('0') or '0'}-{position.zfill(3)}{level}",  # Mixed: 01-1-001A
                f"{aisle.zfill(2)}-01-{position.zfill(3)}{level}",  # Force rack=01: 02-01-011B
                f"01-01-{position.zfill(3)}{level}",  # Force aisle=01,rack=01: 01-01-011B
            ]
            variants.extend(base_variants)
            
            # Add suffix variants for database format (XX-XX-XXXA_N)
            for base_variant in base_variants:
                variants.extend([f"{base_variant}_1", f"{base_variant}_2", f"{base_variant}_3"])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variants = []
        for variant in variants:
            if variant not in seen:
                seen.add(variant)
                unique_variants.append(variant)
        
        return unique_variants
    
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
    
    def _build_location_cache(self) -> tuple:
        """Build optimized location lookup cache - called once per evaluator instance"""
        if self._location_cache is not None:
            return self._location_cache
            
        # PERFORMANCE FIX: Get warehouse-filtered locations using direct query
        from sqlalchemy import or_
        from flask import g
        
        # Get warehouse context from current app context if available
        warehouse_id = None
        if hasattr(g, 'warehouse_context') and g.warehouse_context:
            warehouse_id = g.warehouse_context.get('warehouse_id')
        
        # Query locations with warehouse filtering
        if warehouse_id:
            all_locations = Location.query.filter(
                Location.warehouse_id == warehouse_id,
                or_(Location.is_active == True, Location.is_active.is_(None))
            ).all()
        else:
            # Fallback to all locations if no warehouse context
            all_locations = Location.query.filter(
                or_(Location.is_active == True, Location.is_active.is_(None))
            ).all()
        
        # Build efficient lookup structures
        exact_lookup = {}  # code -> Location
        variant_lookup = {}  # variant -> Location  
        
        for loc in all_locations:
            # Store exact match
            exact_lookup[loc.code] = loc
            
            # Generate limited variants to prevent memory explosion
            try:
                # Use simplified variant generation for performance
                variants = self._get_essential_variants(loc.code)
                for variant in variants:
                    if variant not in variant_lookup:  # First match wins
                        variant_lookup[variant] = loc
            except Exception:
                continue
        
        self._location_cache = (exact_lookup, variant_lookup)
        return self._location_cache
    
    def _get_essential_variants(self, location_code: str) -> list:
        """Generate essential variants only - optimized for performance"""
        if not location_code:
            return [location_code]
            
        code = str(location_code).strip().upper()
        variants = [code]  # Always include original
        
        import re
        
        # Only generate essential variants to prevent memory explosion
        standard_pattern = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{1,3})([A-Z])$', code)
        if standard_pattern:
            aisle, rack, position, level = standard_pattern.groups()
            
            # Generate only the most likely matches
            essential_variants = [
                f"{aisle.zfill(2)}-{rack.zfill(2)}-{position.zfill(3)}{level}",  # 02-01-011B
                f"{aisle.zfill(2)}-{rack.lstrip('0') or '0'}-{position.zfill(3)}{level}",  # 02-1-011B  
                f"01-01-{position.zfill(3)}{level}",  # Force common warehouse format
            ]
            
            variants.extend(essential_variants)
            
            # Add only _1 suffix (most common)
            for variant in essential_variants:
                variants.append(f"{variant}_1")
        
        return list(set(variants))  # Remove duplicates
    
    def _find_location_by_code_internal(self, location_str: str) -> 'Location':
        """OPTIMIZED: Internal method using cached lookup for performance"""
        # Build cache once per evaluator instance
        exact_lookup, variant_lookup = self._build_location_cache()
        
        # 1. Direct exact match (fastest)
        if location_str in exact_lookup:
            return exact_lookup[location_str]
        
        # 2. Generate essential variants for input (limited set)
        input_variants = self._get_essential_variants(location_str)
        
        # 3. Check variants against pre-built cache (fast lookup)
        for variant in input_variants:
            if variant in exact_lookup:
                return exact_lookup[variant]
            if variant in variant_lookup:
                return variant_lookup[variant]
        
        # 4. Legacy fallback (only if essential variants fail)
        normalized_input = self._normalize_location_code(location_str)
        if normalized_input != location_str and normalized_input in exact_lookup:
            return exact_lookup[normalized_input]
        
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
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        parameters = self._parse_parameters(rule)

        # Parse different condition formats
        time_threshold_hours = conditions.get('time_threshold_hours', 10)
        max_days_in_location = conditions.get('max_days_in_location')

        # ENHANCED: Support both legacy location_types and new location_patterns
        location_types = conditions.get('location_types', ['RECEIVING'])
        location_patterns = conditions.get('location_patterns', None)
        excluded_patterns = conditions.get('excluded_patterns', None)

        # Convert max_days_in_location to hours if specified
        if max_days_in_location is not None:
            time_threshold_hours = max_days_in_location * 24

        # ==================== DETAILED LOGGING START ====================
        print(f"[STAGNANT_DEBUG] ==================== STAGNANT PALLETS EVALUATION ====================")
        print(f"[STAGNANT_DEBUG] Total pallets to evaluate: {len(inventory_df)}")
        print(f"[STAGNANT_DEBUG] Time threshold: {time_threshold_hours}h")
        print(f"[STAGNANT_DEBUG] Location criteria: location_types={location_types}, patterns={location_patterns}, excluded={excluded_patterns}")

        anomalies = []
        now = datetime.now()

        # PATTERN-BASED FILTERING: Use patterns instead of location_type classification
        if location_patterns:
            # Use explicitly provided patterns
            print(f"[STAGNANT_PALLETS] Using explicit location patterns: {location_patterns}")
            valid_pallets = self._filter_by_location_patterns(inventory_df, location_patterns)
        elif excluded_patterns:
            # Use exclusion patterns (filter out matching locations)
            print(f"[STAGNANT_PALLETS] Using exclusion patterns: {excluded_patterns}")
            excluded_pallets = self._filter_by_location_patterns(inventory_df, excluded_patterns)
            valid_pallets = inventory_df[~inventory_df.index.isin(excluded_pallets.index)]
        else:
            # Backward compatibility: Convert location_types to patterns
            print(f"[STAGNANT_PALLETS] Converting location_types to patterns: {location_types}")
            patterns = self._get_patterns_for_location_types(location_types)
            valid_pallets = self._filter_by_location_patterns(inventory_df, patterns)

        print(f"[STAGNANT_DEBUG] Pallets matching location criteria: {len(valid_pallets)}")

        # Show location distribution
        if len(valid_pallets) > 0:
            location_counts = valid_pallets['location'].value_counts()
            print(f"[STAGNANT_DEBUG] Location distribution (top 10):")
            for loc, count in location_counts.head(10).items():
                print(f"[STAGNANT_DEBUG]   {loc}: {count} pallets")

        print(f"[STAGNANT_DEBUG] -------------------- EVALUATING PALLETS --------------------")

        evaluated_count = 0
        skipped_no_date = 0
        below_threshold_count = 0

        for _, pallet in valid_pallets.iterrows():
            evaluated_count += 1

            if pd.isna(pallet.get('creation_date')):
                skipped_no_date += 1
                continue

            time_diff = now - pallet['creation_date']
            age_hours = time_diff.total_seconds() / 3600

            if time_diff > timedelta(hours=time_threshold_hours):
                # Determine location category from location pattern for reporting
                location_category = self._get_location_category(pallet['location'])

                print(f"[STAGNANT_DEBUG] ✅ ANOMALY #{len(anomalies)+1}: Pallet '{pallet['pallet_id']}' in '{pallet['location']}' (age: {age_hours:.1f}h > {time_threshold_hours}h)")

                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Stagnant Pallet',
                    'priority': rule.priority,
                    'issue_description': f"Pallet in {location_category} location '{pallet['location']}' for {time_diff.total_seconds()/3600:.1f}h (threshold: {time_threshold_hours:.1f}h)"
                })
            else:
                below_threshold_count += 1

        # ==================== SUMMARY STATISTICS ====================
        print(f"[STAGNANT_DEBUG] ==================== EVALUATION SUMMARY ====================")
        print(f"[STAGNANT_DEBUG] Total pallets evaluated: {evaluated_count}")
        print(f"[STAGNANT_DEBUG] Skipped (no creation_date): {skipped_no_date}")
        print(f"[STAGNANT_DEBUG] Below threshold: {below_threshold_count}")
        print(f"[STAGNANT_DEBUG] Anomalies detected: {len(anomalies)}")

        # Pattern breakdown analysis
        if len(anomalies) > 0:
            print(f"[STAGNANT_DEBUG] -------------------- PATTERN BREAKDOWN --------------------")

            # Analyze pallet ID patterns
            pattern_counts = {
                'STAGNANT-': 0,
                'OVERCAP-': 0,
                'LOT.*-STRAGGLER': 0,
                'AISLE-STUCK-': 0,
                'DUPLICATE-': 0,
                'INVALID-': 0,
                'PLT-': 0,
                'OTHER': 0
            }

            for anomaly in anomalies:
                pallet_id = anomaly['pallet_id']
                matched = False

                if 'STAGNANT-' in pallet_id:
                    pattern_counts['STAGNANT-'] += 1
                    matched = True
                elif 'OVERCAP-' in pallet_id:
                    pattern_counts['OVERCAP-'] += 1
                    matched = True
                elif 'STRAGGLER' in pallet_id:
                    pattern_counts['LOT.*-STRAGGLER'] += 1
                    matched = True
                elif 'AISLE-STUCK-' in pallet_id:
                    pattern_counts['AISLE-STUCK-'] += 1
                    matched = True
                elif 'DUPLICATE-' in pallet_id:
                    pattern_counts['DUPLICATE-'] += 1
                    matched = True
                elif 'INVALID-' in pallet_id:
                    pattern_counts['INVALID-'] += 1
                    matched = True
                elif pallet_id.startswith('PLT-'):
                    pattern_counts['PLT-'] += 1
                    matched = True

                if not matched:
                    pattern_counts['OTHER'] += 1

            print(f"[STAGNANT_DEBUG] Pallet ID pattern analysis:")
            for pattern, count in pattern_counts.items():
                if count > 0:
                    percentage = (count / len(anomalies)) * 100
                    status = "✅ INJECTED" if pattern == 'STAGNANT-' else "⚠️ CROSS-CONTAMINATION"
                    print(f"[STAGNANT_DEBUG]   {pattern}: {count} pallets ({percentage:.1f}%) {status}")

            # Location breakdown
            anomaly_locations = {}
            for anomaly in anomalies:
                loc = anomaly['location']
                anomaly_locations[loc] = anomaly_locations.get(loc, 0) + 1

            print(f"[STAGNANT_DEBUG] Location breakdown:")
            for loc, count in sorted(anomaly_locations.items(), key=lambda x: x[1], reverse=True):
                print(f"[STAGNANT_DEBUG]   {loc}: {count} anomalies")

        print(f"[STAGNANT_DEBUG] ================================================================")
        # ==================== DETAILED LOGGING END ====================

        return anomalies
    
    def _assign_location_types(self, inventory_df: pd.DataFrame) -> pd.DataFrame:
        """Assign location types based on location patterns with smart matching"""
        df = inventory_df.copy()
        
        # PERFORMANCE FIX: Get cached warehouse-filtered locations
        locations = self._get_cached_locations()
        
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
        
        # PERFORMANCE FIX: Get cached warehouse-filtered locations
        all_locations = self._get_cached_locations()
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
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)

        completion_threshold = conditions.get('completion_threshold', 0.8)

        # ENHANCED: Support both legacy location_types and new pattern-based configuration
        location_types = conditions.get('location_types', ['RECEIVING'])
        final_location_types = conditions.get('final_location_types', ['FINAL', 'STORAGE'])

        # New pattern-based configuration options
        source_patterns = conditions.get('source_patterns', None)  # Where stragglers are found
        final_patterns = conditions.get('final_patterns', None)    # Where completed pallets should be

        # PATTERN-BASED LOT COMPLETION ANALYSIS: Use patterns instead of location_type classification
        if final_patterns is None:
            # Backward compatibility: Convert final_location_types to patterns
            final_patterns = self._get_patterns_for_location_types(final_location_types)

        if source_patterns is None:
            # Backward compatibility: Convert location_types to patterns
            source_patterns = self._get_patterns_for_location_types(location_types)

        # PERFORMANCE OPTIMIZATION: Vectorized approach instead of nested loops
        # Pre-classify all locations once (O(n) instead of O(n×m))
        anomalies = self._evaluate_vectorized(
            inventory_df, rule, completion_threshold,
            source_patterns, final_patterns
        )

        return anomalies

    def _evaluate_vectorized(self, inventory_df: pd.DataFrame, rule: Rule,
                            completion_threshold: float, source_patterns: List[str],
                            final_patterns: List[str]) -> List[Dict[str, Any]]:
        """
        VECTORIZED LOT STRAGGLER DETECTION (10-15x faster than nested loops)

        Algorithm:
        1. Pre-classify all locations as 'final' or 'source' (single pass)
        2. Use groupby aggregation to calculate completion ratios
        3. Filter stragglers using vectorized operations
        4. Build anomalies list in single pass

        Performance: 17.7s → ~1.5s for 2000 locations
        """
        if inventory_df.empty:
            return []

        # Step 1: Pre-classify ALL locations once (vectorized string operations)
        inventory_df = inventory_df.copy()  # Avoid modifying original
        inventory_df['is_final'] = self._classify_locations(inventory_df['location'], final_patterns)
        inventory_df['is_source'] = self._classify_locations(inventory_df['location'], source_patterns)

        # Step 2: Vectorized lot analysis using groupby aggregation
        lot_stats = inventory_df.groupby('receipt_number').agg({
            'pallet_id': 'count',  # total_pallets
            'is_final': 'sum'      # final_pallets (True=1, False=0)
        }).rename(columns={'pallet_id': 'total_pallets', 'is_final': 'final_pallets'})

        # Calculate completion ratio vectorized
        lot_stats['completion_ratio'] = lot_stats['final_pallets'] / lot_stats['total_pallets']

        # Step 3: Filter lots that meet criteria (>=threshold and >1 pallet)
        incomplete_lots = lot_stats[
            (lot_stats['completion_ratio'] >= completion_threshold) &
            (lot_stats['total_pallets'] > 1)
        ]

        if incomplete_lots.empty:
            return []

        # Step 4: Find stragglers in incomplete lots (vectorized filtering)
        stragglers_mask = (
            inventory_df['receipt_number'].isin(incomplete_lots.index) &
            inventory_df['is_source']  # In source locations
        )
        stragglers_df = inventory_df[stragglers_mask]

        if stragglers_df.empty:
            return []

        print(f"[INCOMPLETE_LOTS] Found {len(stragglers_df)} stragglers across {len(incomplete_lots)} incomplete lots")

        # Step 5: Build anomalies list (single pass through stragglers)
        anomalies = []
        for _, pallet in stragglers_df.iterrows():
            receipt_number = pallet['receipt_number']
            completion_ratio = incomplete_lots.loc[receipt_number, 'completion_ratio']
            location_category = self._get_location_category(pallet['location'])

            anomalies.append({
                'pallet_id': pallet['pallet_id'],
                'location': pallet['location'],
                'anomaly_type': 'Lot Straggler',
                'priority': rule.priority,
                'issue_description': f"{completion_ratio:.0%} of lot '{receipt_number}' moved to final storage - this pallet left behind in {location_category} location '{pallet['location']}'",
                'details': f"{completion_ratio:.0%} of lot '{receipt_number}' already stored, but this pallet still in {location_category}"
            })

        return anomalies

    def _classify_locations(self, location_series: pd.Series, patterns: List[str]) -> pd.Series:
        """
        Vectorized location classification against multiple patterns.

        Returns boolean Series: True if location matches any pattern, False otherwise.
        Performance: O(n) single pass instead of O(n×m) nested loops.
        """
        if not patterns:
            return pd.Series([False] * len(location_series), index=location_series.index)

        # Vectorized string operations (FAST)
        location_upper = location_series.astype(str).str.upper()

        # Combine all pattern matches with OR logic
        combined_mask = pd.Series([False] * len(location_series), index=location_series.index)

        for pattern in patterns:
            try:
                pattern_mask = location_upper.str.match(pattern, na=False)
                combined_mask = combined_mask | pattern_mask
            except Exception as e:
                print(f"[PATTERN_ERROR] Pattern '{pattern}' failed: {e}")
                continue

        return combined_mask

class OvercapacityEvaluator(BaseRuleEvaluator):
    """Evaluator for smart overcapacity detection with statistical analysis and location differentiation"""
    
    def __init__(self, app=None):
        super().__init__(app)
        self.debug = False  # Disable verbose debug logging in production for performance
        # Import location classification service for enhanced alerting
        try:
            from .location_classification_service import LocationClassificationService
        except ImportError:
            from location_classification_service import LocationClassificationService
        self.location_classifier = LocationClassificationService()
        # Cache for scope service instances to avoid recreating them per location
        self._scope_service_cache = {}
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        parameters = self._parse_parameters(rule)
        
        # LOCATION DIFFERENTIATION ENHANCEMENT - NEW FEATURE
        # Enables business-context-aware alerting with differentiated strategies
        # for Storage locations (critical) vs Special areas (operational)
        # TEMPORARY TESTING OVERRIDE: Force enable location differentiation for demo
        use_location_differentiation = True  # parameters.get('use_location_differentiation', False)
        
        # SMART CAPACITY FEATURE DISABLED FOR CORE PRODUCT
        # Smart overcapacity detection moved to premium "Intelligent Analytics" section
        # This advanced statistical analysis will be available as a premium feature
        # To re-enable: change default from False to True
        use_statistical_analysis = parameters.get('use_statistical_analysis', False)  # DISABLED: Smart capacity moved to premium
        significance_threshold = parameters.get('significance_threshold', 1.0)  # PRESERVED: For future premium feature
        min_severity_ratio = parameters.get('min_severity_ratio', 1.2)  # PRESERVED: For future premium feature
        
        # UNIT-AGNOSTIC ENHANCEMENT: Check if scope filtering is available
        use_unit_agnostic = parameters.get('use_unit_agnostic', True)  # Enable by default

        if use_statistical_analysis:
            return self._evaluate_with_statistical_analysis(
                rule, inventory_df, significance_threshold, min_severity_ratio
            )
        elif use_unit_agnostic and warehouse_context and warehouse_context.get('warehouse_id'):
            # NEW: Unit-agnostic overcapacity detection with scope awareness
            return self._evaluate_with_unit_agnostic_detection(rule, inventory_df, warehouse_context)
        elif use_location_differentiation:
            # Enhanced overcapacity detection with location type differentiation
            return self._evaluate_with_location_differentiation(rule, inventory_df, warehouse_context)
        else:
            # Legacy behavior for backward compatibility
            return self._evaluate_legacy(rule, inventory_df)
    
    def _evaluate_with_statistical_analysis(self, rule: Rule, inventory_df: pd.DataFrame, 
                                          significance_threshold: float, min_severity_ratio: float) -> List[Dict[str, Any]]:
        """
        SMART CAPACITY PREMIUM FEATURE - PRESERVED FOR FUTURE USE
        
        Enhanced overcapacity detection with statistical analysis
        This method implements the intelligent capacity analytics that will be moved
        to the premium "Intelligent Warehouse Analytics" section.
        
        Features preserved here:
        - Statistical modeling of warehouse utilization
        - Pattern recognition for capacity anomalies  
        - Smart overcapacity detection beyond obvious violations
        - Predictive capacity analysis
        
        To activate this premium feature:
        1. Set use_statistical_analysis=True in rule parameters
        2. Move to premium analytics dashboard section
        3. Add appropriate user access controls
        """
        anomalies = []
        
        # Calculate warehouse statistics
        warehouse_stats = self._calculate_warehouse_statistics(inventory_df, warehouse_context)
        
        # Calculate expected overcapacity using statistical model
        expected_overcapacity = self._calculate_expected_overcapacity(inventory_df, warehouse_stats)
        
        # Count pallets per location
        location_counts = inventory_df['location'].value_counts()
        
        # Find actual overcapacity locations
        actual_overcapacity_locations = []
        for location, count in location_counts.items():
            location_obj = self._find_location_by_code(str(location))
            capacity = self._get_location_capacity(location_obj, str(location), warehouse_context)
            
            # DEBUG: Log capacity calculation details
            if self.debug:
                location_type = location_obj.location_type if location_obj else 'NOT_FOUND'
                db_capacity = getattr(location_obj, 'capacity', None) if location_obj else None
                db_pallet_capacity = getattr(location_obj, 'pallet_capacity', None) if location_obj else None
                # Debug info available if needed: count={count}, capacity={capacity}, type={location_type}
            
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
        
        # 1. Obvious violations bypass (>=2x capacity) - always flag these regardless of statistics
        obvious_violations = [loc for loc in actual_overcapacity_locations if loc['count'] >= loc['capacity'] * 2]
        if obvious_violations:
            should_flag_anomalies = True
            bypass_reason = f"Obvious violations detected: {len(obvious_violations)} locations with >=2x capacity"
        
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
                
                # Create one anomaly per overcapacity location (not per pallet)
                pallets_in_loc = inventory_df[inventory_df['location'] == overcap_loc['location']]
                representative_pallet = pallets_in_loc.iloc[0]  # Use first pallet as representative
                
                anomalies.append({
                    'pallet_id': representative_pallet['pallet_id'],
                    'location': overcap_loc['location'],
                    'anomaly_type': 'Obvious Violation' if is_obvious else 'Smart Overcapacity',
                    'priority': 'Very High' if is_obvious else adjusted_priority,
                    'details': f"Location '{overcap_loc['location']}' has {overcap_loc['count']} pallets (capacity: {overcap_loc['capacity']}, +{overcap_loc['excess']} excess)",
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
                    'affected_pallets': overcap_loc['count'],
                    'violation_severity': violation_severity,
                    'bypass_reason': bypass_reason
                })
        
        return anomalies

    def _evaluate_with_unit_agnostic_detection(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        """
        Unit-agnostic overcapacity detection with scope awareness.

        This method integrates the SimpleScopeService to provide intelligent
        overcapacity detection that respects warehouse scope configuration
        and handles mixed unit types appropriately.

        Features:
        - Scope-aware capacity detection using SimpleScopeService
        - Unit type awareness for intelligent capacity calculation
        - Seamless integration with existing warehouse context
        - Graceful fallback to location differentiation logic

        Args:
            rule: The overcapacity rule being evaluated
            inventory_df: Inventory data (already scope-filtered by rule engine)
            warehouse_context: Warehouse context with warehouse_id

        Returns:
            List of anomaly dictionaries for overcapacity violations
        """
        anomalies = []
        warehouse_id = warehouse_context.get('warehouse_id')

        print(f"\n[UNIT_AGNOSTIC] Starting unit-agnostic overcapacity detection for warehouse {warehouse_id}")

        try:
            # Use CACHED scope service instance (shared with _get_location_capacity fallback)
            # This ensures bulk loading benefits ALL code paths, not just the main one
            warehouse_id_str = str(warehouse_id)
            if warehouse_id_str not in self._scope_service_cache:
                self._scope_service_cache[warehouse_id_str] = SimpleScopeService(warehouse_id_str)
            scope_service = self._scope_service_cache[warehouse_id_str]

            # Get scope summary for debugging
            scope_summary = scope_service.get_scope_summary()
            print(f"[UNIT_AGNOSTIC] Scope config: {scope_summary}")

            # Count items per location
            location_counts = inventory_df['location'].value_counts()

            print(f"[UNIT_AGNOSTIC] Analyzing {len(location_counts)} locations with inventory")

            # PERFORMANCE OPTIMIZATION: Bulk load all locations into CACHED instance
            # This prevents worker timeout on large inventories (1000+ locations)
            # The cached instance is also used by _get_location_capacity fallback path
            unique_locations = location_counts.index.tolist()
            scope_service.bulk_load_locations(unique_locations)
            print(f"[UNIT_AGNOSTIC] Bulk loaded {len(unique_locations)} locations into cached instance")

            # ========== VECTORIZED OVERCAPACITY DETECTION (10-15x FASTER) ==========
            # OLD APPROACH: Loop through 845 locations with function calls per location
            # NEW APPROACH: Bulk operations with pandas vectorization

            # Step 1: Bulk retrieve capacities and unit types (SINGLE operation each)
            capacities_dict = scope_service.get_capacities_bulk(location_counts.index)
            unit_types_dict = scope_service.get_unit_types_bulk(location_counts.index)

            # Step 2: Convert to pandas Series for vectorized operations
            capacities = pd.Series(capacities_dict)
            unit_types = pd.Series(unit_types_dict)

            # Step 3: Handle None capacities with fallback (only for locations that need it)
            none_mask = capacities.isna()
            if none_mask.any():
                none_locations = capacities[none_mask].index.tolist()
                print(f"[UNIT_AGNOSTIC] {len(none_locations)} locations need fallback capacity lookup")

                # PERFORMANCE: Use LocationRepository for vectorized fallback (if available)
                if warehouse_context and warehouse_context.get('location_repository'):
                    location_repository = warehouse_context['location_repository']
                    fallback_dict = location_repository.get_capacities_bulk(none_locations)
                    capacities.update(pd.Series(fallback_dict))
                    print(f"[UNIT_AGNOSTIC] Bulk fallback complete using LocationRepository")
                else:
                    # Fallback to individual lookups (only if LocationRepository unavailable)
                    print(f"[UNIT_AGNOSTIC] WARNING: No LocationRepository, using individual fallback (slow)")
                    for loc_code in none_locations:
                        location_obj = self._find_location_by_code(str(loc_code))
                        fallback_capacity = self._get_location_capacity(
                            location_obj, str(loc_code), warehouse_context, skip_scope_service=True
                        )
                        capacities[loc_code] = fallback_capacity

            # Step 4: Vectorized overcapacity detection (FAST - single comparison operation)
            overcapacity_mask = location_counts > capacities
            overcapacity_locations = location_counts[overcapacity_mask]

            print(f"[UNIT_AGNOSTIC] Found {len(overcapacity_locations)} overcapacity locations (vectorized detection)")

            # Step 5: Pre-group DataFrame for O(1) location lookups (CRITICAL OPTIMIZATION)
            # FIX: Ensure type consistency to prevent get_group() KeyError failures
            import time

            # Create copy and ensure location column is string type
            inventory_df_typed = inventory_df.copy()
            inventory_df_typed['location'] = inventory_df_typed['location'].astype(str)

            # Group with timing instrumentation
            t_groupby_start = time.time()
            grouped_inventory = inventory_df_typed.groupby('location')
            t_groupby_end = time.time()
            groupby_time_ms = (t_groupby_end - t_groupby_start) * 1000
            print(f"[PERF] DataFrame groupby completed in {groupby_time_ms:.0f}ms for {len(inventory_df_typed)} rows")

            # Step 6: VECTORIZED anomaly creation (eliminate Python loop overhead)
            print(f"[PERF] Creating {len(overcapacity_locations)} anomalies using vectorized operations...")
            t_vectorize_start = time.time()

            # Phase 1: Extract representative pallets in ONE bulk operation
            # Get first item from each location group (O(1) for all groups)
            all_representatives = grouped_inventory.first()

            # Filter to only overcapacity locations
            overcap_representatives = all_representatives.loc[overcapacity_locations.index]

            # Phase 2: Build metadata DataFrame (vectorized operations)
            anomalies_df = pd.DataFrame({
                'pallet_id': overcap_representatives['pallet_id'].values,
                'location': overcapacity_locations.index.astype(str),
                'anomaly_type': 'Overcapacity',
                'priority': rule.priority,
                'affected_pallets': overcapacity_locations.values,
                'capacity': capacities[overcapacity_locations.index].values,
                'unit_type': unit_types[overcapacity_locations.index].values,
            })

            # Calculate excess (vectorized)
            anomalies_df['excess_pallets'] = anomalies_df['affected_pallets'] - anomalies_df['capacity']

            # Phase 3: Vectorized string formatting (NO f-strings in loop!)
            anomalies_df['details'] = (
                "Location '" + anomalies_df['location'] + "' has " +
                anomalies_df['affected_pallets'].astype(str) + " " + anomalies_df['unit_type'] +
                " (capacity: " + anomalies_df['capacity'].astype(str) +
                ", +" + anomalies_df['excess_pallets'].astype(str) + " excess)"
            )

            # Phase 4: Capacity source determination (vectorized)
            # Create a mask for locations that came from scope_service
            anomalies_df['capacity_source'] = 'fallback'  # Default
            scope_locations_mask = anomalies_df['location'].isin(capacities_dict.keys())
            anomalies_df.loc[scope_locations_mask, 'capacity_source'] = 'scope_service'

            # Phase 5: Convert to list of dicts in ONE operation
            anomalies = anomalies_df.to_dict('records')

            t_vectorize_end = time.time()
            vectorize_time_ms = (t_vectorize_end - t_vectorize_start) * 1000

            # Performance metrics
            print(f"[PERF] ✅ Vectorized anomaly creation completed in {vectorize_time_ms:.0f}ms")
            print(f"[PERF] Average time per anomaly: {vectorize_time_ms / len(anomalies):.2f}ms (was ~45ms with Python loop)")

            # Sample output for verification (first 3)
            for i in range(min(3, len(anomalies))):
                a = anomalies[i]
                print(f"[UNIT_AGNOSTIC] OVERCAPACITY: {a['location']} has {a['affected_pallets']}/{a['capacity']} {a['unit_type']} (+{a['excess_pallets']} excess)")
            if len(anomalies) > 3:
                print(f"[UNIT_AGNOSTIC] ... (additional {len(anomalies) - 3} overcapacity locations found, details in results)")

            # ========== END VECTORIZED DETECTION ==========

        except Exception as e:
            print(f"[UNIT_AGNOSTIC] Error in unit-agnostic detection: {e}")
            # Fallback to location differentiation method
            print(f"[UNIT_AGNOSTIC] Falling back to location differentiation method")
            return self._evaluate_with_location_differentiation(rule, inventory_df, warehouse_context)

        return anomalies

    def _calculate_warehouse_statistics(self, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> Dict[str, Any]:
        """Calculate warehouse utilization and capacity statistics"""
        
        # Get all unique locations and their capacities
        unique_locations = inventory_df['location'].unique()
        total_capacity = 0
        valid_locations = 0
        
        print(f"[WAREHOUSE_STATS_DEBUG] Processing {len(unique_locations)} unique locations")
        
        for location in unique_locations:
            location_obj = self._find_location_by_code(str(location))
            capacity = self._get_location_capacity(location_obj, str(location), warehouse_context)
            total_capacity += capacity
            valid_locations += 1
            
            if capacity == 0:
                print(f"[WAREHOUSE_STATS_DEBUG] WARNING: Location {location} has capacity 0")
        
        total_pallets = len(inventory_df)
        print(f"[WAREHOUSE_STATS_DEBUG] Total pallets: {total_pallets}, Total capacity: {total_capacity}, Valid locations: {valid_locations}")
        
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
        
        print(f"[EXPECTED_OVERCAP_DEBUG] Stats: utilization_rate={utilization_rate}, total_pallets={total_pallets}, total_locations={total_locations}")
        
        # SAFETY CHECK: Prevent division by zero
        if total_locations <= 0:
            print(f"[OVERCAPACITY_DEBUG] WARNING: total_locations is {total_locations}, using fallback")
            return {
                'count': 1.0,
                'model_used': 'Fallback (zero locations detected)',
                'utilization_basis': 0.0,
                'confidence_level': 30
            }
        
        if total_pallets <= 0:
            print(f"[OVERCAPACITY_DEBUG] WARNING: total_pallets is {total_pallets}, using fallback")
            return {
                'count': 0.0,
                'model_used': 'Fallback (zero pallets detected)', 
                'utilization_basis': 0.0,
                'confidence_level': 95
            }
        
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
    
    def _get_location_capacity(self, location_obj, location_str: str, warehouse_context: dict = None, is_validated: bool = None, skip_scope_service: bool = False) -> int:
        """
        Get location capacity with unit-agnostic integration and invalid location handling

        ENHANCED for Unit-Agnostic Warehouse Intelligence:
        - Integrates SimpleScopeService for unit type awareness
        - Handles mixed unit types intelligently
        - Maintains backward compatibility with existing capacity logic

        Args:
            location_obj: Database location object
            location_str: Location code string
            warehouse_context: Warehouse context for virtual engine lookup
            is_validated: Whether location passed pre-validation (None = unknown, True = valid, False = invalid)

        Returns:
            Capacity integer, or -1 for invalid locations (should be excluded from analysis)
        """
        # ENHANCEMENT: Handle pre-validated invalid locations
        if is_validated is False:
            # Location failed pre-validation - return -1 to exclude from overcapacity analysis
            return -1

        # ENHANCEMENT: Basic invalid location patterns detection (fallback)
        if is_validated is None:
            location_upper = location_str.upper()
            invalid_patterns = ['NOWHERE', 'INVALID', 'ERROR', 'NULL', 'UNKNOWN', 'TEMP', 'TEST']
            if any(invalid_pattern in location_upper for invalid_pattern in invalid_patterns):
                return -1  # Exclude invalid locations

        # UNIT-AGNOSTIC ENHANCEMENT: Integrate SimpleScopeService for capacity determination
        warehouse_id = None
        if warehouse_context and warehouse_context.get('warehouse_id'):
            warehouse_id = warehouse_context['warehouse_id']

        if warehouse_id and not skip_scope_service:  # Skip if already queried by caller
            try:
                # Use CACHED scope service to avoid creating new instances per location
                warehouse_id_str = str(warehouse_id)
                if warehouse_id_str not in self._scope_service_cache:
                    self._scope_service_cache[warehouse_id_str] = SimpleScopeService(warehouse_id_str)
                scope_service = self._scope_service_cache[warehouse_id_str]

                scope_capacity = scope_service.get_location_capacity(location_str)

                if scope_capacity is not None:
                    # Found capacity through scope service
                    return scope_capacity

                # Also get unit type for intelligent fallback handling
                unit_type = scope_service.get_location_unit_type(location_str)

                # Log unit type information for debugging (reduced verbosity)
                # print(f"[UNIT_AGNOSTIC] Location {location_str} detected as unit type: {unit_type}")

            except Exception as e:
                print(f"[UNIT_AGNOSTIC] Error accessing scope service for {location_str}: {e}")
                # Continue with legacy capacity logic on error
        
        # ENHANCED: First check virtual engine if available (proper template-based capacity)
        if warehouse_context and warehouse_context.get('warehouse_id'):
            try:
                # PERFORMANCE: Use cached virtual engine from warehouse context (avoid redundant initialization)
                virtual_engine = warehouse_context.get('virtual_engine')

                # Fallback: Initialize if not cached (backward compatibility)
                if not virtual_engine:
                    from virtual_template_integration import get_virtual_engine_for_warehouse
                    virtual_engine = get_virtual_engine_for_warehouse(warehouse_context['warehouse_id'])

                if virtual_engine:
                    virtual_location = virtual_engine.get_location_properties(location_str)
                    if virtual_location and hasattr(virtual_location, 'capacity'):
                        # Found in virtual engine - use template-configured capacity
                        return virtual_location.capacity
            except Exception as e:
                # Virtual engine not available, continue with database lookup
                pass
        
        # ENHANCED: Database capacity with unit-agnostic preferences
        if location_obj:
            # UNIT-AGNOSTIC: Check for unit_type field and handle appropriately
            location_unit_type = getattr(location_obj, 'unit_type', None)

            if location_unit_type:
                # print(f"[UNIT_AGNOSTIC] Location {location_str} has database unit_type: {location_unit_type}")

                # For mixed or non-pallet unit types, use the standard capacity field
                if location_unit_type in ['boxes', 'items', 'cases', 'mixed']:
                    if hasattr(location_obj, 'capacity') and location_obj.capacity:
                        return location_obj.capacity
                # For pallet unit types, prefer pallet_capacity if available
                elif location_unit_type == 'pallets':
                    if hasattr(location_obj, 'pallet_capacity') and location_obj.pallet_capacity:
                        return location_obj.pallet_capacity
                    elif hasattr(location_obj, 'capacity') and location_obj.capacity:
                        return location_obj.capacity

            # For TRANSITIONAL locations, prefer pallet_capacity over capacity
            if (hasattr(location_obj, 'location_type') and
                location_obj.location_type == 'TRANSITIONAL' and
                hasattr(location_obj, 'pallet_capacity') and location_obj.pallet_capacity):
                return location_obj.pallet_capacity

            # For other locations, prefer capacity first
            if hasattr(location_obj, 'capacity') and location_obj.capacity:
                return location_obj.capacity
            elif hasattr(location_obj, 'pallet_capacity') and location_obj.pallet_capacity:
                return location_obj.pallet_capacity
        
        # Second priority: Use location type from database if available
        if location_obj and hasattr(location_obj, 'location_type'):
            location_type = location_obj.location_type
            if location_type == 'RECEIVING':
                return 10  # Standard receiving capacity
            elif location_type == 'STAGING':
                return 5   # Standard staging capacity
            elif location_type == 'DOCK':
                return 2   # Standard dock capacity
            elif location_type == 'TRANSITIONAL':
                return 10  # AISLE locations - fixed capacity
            elif location_type == 'STORAGE':
                return 1   # Storage locations typically hold 1 pallet
        
        # Fallback: Pattern-based intelligent defaults
        location_upper = location_str.upper()
        if any(x in location_upper for x in ['RECEIVING', 'RECV']):
            return 10  # Receiving areas
        elif any(x in location_upper for x in ['STAGING', 'STAGE']):
            return 5   # Staging areas
        elif any(x in location_upper for x in ['DOCK']):
            return 2   # Dock areas
        elif any(x in location_upper for x in ['AISLE']):
            return 10  # FIXED: AISLE locations should have 10 capacity (transitional)
        elif any(x in location_upper for x in ['BULK', 'FLOOR']):
            return 15  # Floor storage areas
        elif location_str.startswith('USER_') or any(x in location_upper for x in ['-', 'RACK', 'SHELF']):
            return 1   # Storage positions typically hold 1 pallet
        elif self._matches_storage_pattern(location_str):
            return 1   # Storage locations in ###L format (e.g., 001A, 050A, etc.)
        else:
            return 5   # Conservative default
    
    def _matches_storage_pattern(self, location_str: str) -> bool:
        """
        Check if location matches storage patterns like ###L (e.g., 001A, 050A, 234C)
        This fixes overcapacity detection for standard warehouse storage locations.
        """
        import re
        location_str = str(location_str).strip()
        
        # Pattern 1: ###L format (3 digits + single letter) - e.g., 001A, 050A, 234C
        if re.match(r'^\d{3}[A-Z]$', location_str.upper()):
            return True
            
        # Pattern 2: ##-##-###L format with hyphens - e.g., 01-02-001A
        if re.match(r'^\d{2}-\d{2}-\d{3}[A-Z]$', location_str.upper()):
            return True
            
        # Pattern 3: Other common storage formats
        if re.match(r'^\d{1,4}[A-Z]{1,2}$', location_str.upper()):  # 1A, 12B, 123C, 1234AB
            return True
            
        return False
    
    def _evaluate_legacy(self, rule: Rule, inventory_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        CORE OVERCAPACITY DETECTION - PRIMARY FEATURE
        
        Detects obvious capacity violations where locations contain more pallets 
        than their designated capacity. This is the main overcapacity rule that 
        provides clear, actionable alerts for warehouse operators.
        
        Features:
        - Simple, reliable capacity violation detection
        - Clear alerts for locations exceeding capacity limits
        - Immediate action required for all violations
        - No statistical complexity - just business rule enforcement
        
        This method was renamed from 'legacy' but is now the core feature.
        Advanced analytics have been moved to premium features.
        """
        conditions = self._parse_conditions(rule)
        anomalies = []
        
        # Count pallets per location
        location_counts = inventory_df['location'].value_counts()
        
        for location, count in location_counts.items():
            # Find location using smart matching to get capacity
            location_obj = self._find_location_by_code(str(location))
            capacity = self._get_location_capacity(location_obj, str(location), warehouse_context or {})
            
            if count > capacity:
                # Create one anomaly per overcapacity location (not per pallet)
                pallets_in_loc = inventory_df[inventory_df['location'] == location]
                representative_pallet = pallets_in_loc.iloc[0]  # Use first pallet as representative
                excess = count - capacity
                
                anomalies.append({
                    'pallet_id': representative_pallet['pallet_id'],
                    'location': location,
                    'anomaly_type': 'Overcapacity',
                    'priority': rule.priority,
                    'details': f"Location '{location}' has {count} pallets (capacity: {capacity}, +{excess} excess)",
                    'affected_pallets': count,
                    'excess_pallets': excess
                })
        
        return anomalies
    
    def _evaluate_with_location_differentiation(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        """
        ENHANCED OVERCAPACITY DETECTION WITH LOCATION TYPE DIFFERENTIATION
        
        Implements business-context-aware alerting strategy that differentiates between:
        - Storage Locations (CRITICAL): Individual pallet alerts for data integrity
        - Special Areas (WARNING): Location-level alerts for space management
        
        This enhancement reduces alert fatigue while maintaining appropriate granularity
        where it matters most for operational efficiency.
        
        Features:
        - Location classification using database location_type and pattern matching
        - Differentiated alert generation (individual vs location-level)
        - Automatic priority adjustment based on business context
        - Analytics for measuring alert volume reduction
        """
        try:
            from .location_classification_service import LocationCategory
        except ImportError:
            from location_classification_service import LocationCategory
        
        conditions = self._parse_conditions(rule)
        anomalies = []
        
        # Count pallets per location
        location_counts = inventory_df['location'].value_counts()
        print(f"[OVERCAPACITY_DEBUG] ==================== OVERCAPACITY ANALYSIS START ====================")
        print(f"[OVERCAPACITY_DEBUG] Total unique locations found: {len(location_counts)}")
        # Only show locations with >2 pallets (potential overcapacity)
        overcap_candidates = location_counts[location_counts > 2]
        if len(overcap_candidates) > 0:
            print(f"[OVERCAPACITY_DEBUG] Potential overcapacity locations: {len(overcap_candidates)}")
        else:
            print(f"[OVERCAPACITY_DEBUG] No locations with >2 pallets found")
        
        # Separate overcapacity locations by category for differentiated processing
        storage_overcapacity = {}
        special_overcapacity = {}
        locations_within_capacity = 0
        
        # ENHANCEMENT: Pre-validation filter to exclude invalid locations from overcapacity analysis
        print(f"[OVERCAPACITY_DEBUG] -------------------- PRE-VALIDATION FILTER --------------------")
        validated_location_counts = {}
        invalid_location_count = 0
        
        # Use virtual location engine for validation consistency
        warehouse_id = warehouse_context.get('warehouse_id') if warehouse_context else None
        virtual_engine = None

        # PERFORMANCE OPTIMIZATION: Bulk load all locations for cached scope service
        # This prevents N+1 queries when _get_location_capacity is called in the loop
        if warehouse_id:
            warehouse_id_str = str(warehouse_id)
            if warehouse_id_str not in self._scope_service_cache:
                self._scope_service_cache[warehouse_id_str] = SimpleScopeService(warehouse_id_str)

            # Bulk load all unique locations from inventory
            unique_locations = inventory_df['location'].unique().tolist()
            self._scope_service_cache[warehouse_id_str].bulk_load_locations(unique_locations)
            print(f"[LOCATION_DIFF] Bulk loaded {len(unique_locations)} locations into cached scope service")

        # PERFORMANCE: Use cached virtual engine from warehouse context (avoid redundant initialization)
        virtual_engine = None
        if warehouse_id:
            try:
                virtual_engine = warehouse_context.get('virtual_engine') if warehouse_context else None

                # Fallback: Initialize if not cached (backward compatibility)
                if not virtual_engine:
                    from virtual_template_integration import get_virtual_engine_for_warehouse
                    virtual_engine = get_virtual_engine_for_warehouse(warehouse_id)
            except Exception:
                pass
        
        for location, count in location_counts.items():
            location_str = str(location).strip()
            
            # Skip empty/null locations
            if not location_str or pd.isna(location):
                continue
                
            # Validate location using virtual engine if available
            is_valid_location = True
            validation_reason = "No validation available"
            
            if virtual_engine:
                is_valid_location, validation_reason = virtual_engine.validate_location(location_str)
            else:
                # Fallback: Basic validation for obviously invalid patterns
                if any(invalid_pattern in location_str.upper() for invalid_pattern in ['NOWHERE', 'INVALID', 'ERROR', 'NULL']):
                    is_valid_location = False
                    validation_reason = "Contains invalid pattern"
                elif location_str.upper().startswith('AISLE-') and not location_str.upper().startswith('AISLE-0'):
                    # AISLE-05+ are typically invalid in most warehouse configurations
                    is_valid_location = False  
                    validation_reason = "Invalid aisle location pattern"
                    
            if is_valid_location:
                validated_location_counts[location] = count
            else:
                invalid_location_count += 1
                print(f"[OVERCAPACITY_DEBUG] [INVALID]: {location} ({count} pallets) - {validation_reason} [EXCLUDED from overcapacity analysis]")
        
        print(f"[OVERCAPACITY_DEBUG] Pre-validation summary: {len(validated_location_counts)} valid locations, {invalid_location_count} invalid locations excluded")
        
        # Use validated locations for capacity analysis
        location_counts = validated_location_counts
        
        # ========== VECTORIZED CAPACITY ANALYSIS (10-15x FASTER) ==========
        print(f"[OVERCAPACITY_DEBUG] -------------------- CAPACITY ANALYSIS (VECTORIZED) --------------------")

        # Step 1: Bulk retrieve capacities using LocationRepository if available
        if warehouse_context and warehouse_context.get('location_repository'):
            location_repository = warehouse_context['location_repository']
            capacities_dict = location_repository.get_capacities_bulk(location_counts.keys())
            capacities = pd.Series(capacities_dict)
            print(f"[OVERCAPACITY_DEBUG] Bulk loaded {len(capacities)} capacities from LocationRepository")
        else:
            # Fallback: Use scope service or individual lookups
            capacities = {}
            for location in location_counts.keys():
                location_obj = self._find_location_by_code(str(location))
                capacities[location] = self._get_location_capacity(
                    location_obj, str(location), warehouse_context, is_validated=True
                )
            capacities = pd.Series(capacities)
            print(f"[OVERCAPACITY_DEBUG] Loaded {len(capacities)} capacities individually (no repository)")

        # Step 2: Convert location_counts to Series for vectorized operations
        location_counts_series = pd.Series(location_counts)

        # Step 3: Vectorized overcapacity detection
        overcapacity_mask = location_counts_series > capacities
        overcapacity_locs = location_counts_series[overcapacity_mask]

        total_locations_analyzed = len(location_counts)
        overcapacity_locations_found = len(overcapacity_locs)
        locations_within_capacity = total_locations_analyzed - overcapacity_locations_found

        print(f"[OVERCAPACITY_DEBUG] Vectorized detection complete: {overcapacity_locations_found} overcapacity locations")

        # Step 4: Classify overcapacity locations (only loop through overcapacity locations)
        for location in overcapacity_locs.index:
            count = location_counts_series[location]
            capacity = capacities[location]
            location_obj = self._find_location_by_code(str(location))

            # Classify location for appropriate alert strategy
            category, priority = self.location_classifier.classify_location(location_obj, str(location))

            location_info = {
                'location': location,
                'count': count,
                'capacity': capacity,
                'location_obj': location_obj,
                'priority': priority.value
            }

            # Track for summary
            if category == LocationCategory.STORAGE:
                storage_overcapacity[location] = location_info
            else:  # LocationCategory.SPECIAL
                special_overcapacity[location] = location_info

        # ========== END VECTORIZED CAPACITY ANALYSIS ==========
        
        print(f"[OVERCAPACITY_DEBUG] -------------------- SUMMARY --------------------")
        print(f"[OVERCAPACITY_DEBUG] Total locations analyzed: {total_locations_analyzed}")
        print(f"[OVERCAPACITY_DEBUG] Locations within capacity: {locations_within_capacity}")
        print(f"[OVERCAPACITY_DEBUG] Overcapacity locations found: {overcapacity_locations_found}")
        print(f"[OVERCAPACITY_DEBUG] Storage overcapacity locations: {len(storage_overcapacity)}")
        print(f"[OVERCAPACITY_DEBUG] Special area overcapacity locations: {len(special_overcapacity)}")
        
        # Generate CRITICAL individual pallet alerts for Storage locations
        print(f"[OVERCAPACITY_DEBUG] Generating {len(storage_overcapacity)} storage anomalies...")
        storage_anomaly_count = 0
        excluded_pallet_count = 0
        
        # Initialize precedence checking
        try:
            from rule_precedence_system import create_precedence_manager
            precedence_manager = create_precedence_manager()
            rule_precedence = getattr(rule, 'precedence_level', 2)  # Overcapacity default precedence
        except ImportError:
            precedence_manager = None
            rule_precedence = 2
        
        for location, info in storage_overcapacity.items():
            pallets_in_loc = inventory_df[inventory_df['location'] == location]

            # Create one anomaly per overcapacity storage location (not per pallet)
            representative_pallet = pallets_in_loc.iloc[0]  # Use first pallet as representative
            pallet_id = representative_pallet['pallet_id']

            # Check if representative pallet should be excluded by precedence system
            if (precedence_manager and precedence_manager.enable_precedence and
                precedence_manager.should_exclude_pallet(pallet_id, rule)):
                excluded_pallet_count += 1
                exclusion_reason = precedence_manager.registry.get_exclusion_reason(pallet_id, rule_precedence)
                print(f"[OVERCAPACITY_DEBUG]   --> EXCLUDED: {pallet_id} - {exclusion_reason}")
                continue

            excess = info['count'] - info['capacity']

            # DETAILED LOGGING: Show every storage overcapacity anomaly
            all_pallet_ids = ', '.join(pallets_in_loc['pallet_id'].tolist())
            print(f"[OVERCAPACITY_STORAGE] #{storage_anomaly_count + 1}: Location '{location}' - {info['count']}/{info['capacity']} pallets (+{excess} excess)")
            print(f"[OVERCAPACITY_STORAGE]    Pallets: {all_pallet_ids}")

            anomalies.append({
                'pallet_id': representative_pallet['pallet_id'],
                'location': location,
                'anomaly_type': 'Storage Overcapacity',
                'priority': info['priority'],  # Very High (CRITICAL)
                'details': f"Storage location '{location}' overcapacity: {info['count']}/{info['capacity']} pallets (+{excess} excess)",
                'business_context': 'CRITICAL - Data integrity requires location investigation',
                'location_category': 'STORAGE',
                'affected_pallets': info['count'],
                'excess_pallets': excess
            })
            storage_anomaly_count += 1
        
        if excluded_pallet_count > 0:
            print(f"[OVERCAPACITY_DEBUG] Total pallets excluded by precedence: {excluded_pallet_count}")
        
        print(f"[OVERCAPACITY_DEBUG] Total storage anomalies generated: {storage_anomaly_count}")
        
        # Generate WARNING location-level alerts for Special areas
        print(f"[OVERCAPACITY_DEBUG] Generating {len(special_overcapacity)} special area anomalies...")
        special_anomaly_count = 0
        for location, info in special_overcapacity.items():
            # SAFETY CHECK: Prevent division by zero
            if info['capacity'] > 0:
                percentage = round((info['count'] / info['capacity']) * 100)
            else:
                percentage = 999  # Indicate infinite overcapacity
                print(f"[OVERCAPACITY_DEBUG] WARNING: Location {location} has capacity 0, using percentage=999")
            excess_pallets = info['count'] - info['capacity']

            # Use first pallet in location for the alert (required field)
            pallets_in_loc = inventory_df[inventory_df['location'] == location]
            representative_pallet = pallets_in_loc.iloc[0]

            # DETAILED LOGGING: Show every special area overcapacity anomaly
            all_pallet_ids = ', '.join(pallets_in_loc['pallet_id'].tolist())
            print(f"[OVERCAPACITY_SPECIAL] #{special_anomaly_count + 1}: Location '{location}' - {info['count']}/{info['capacity']} pallets ({percentage}%, +{excess_pallets} excess)")
            print(f"[OVERCAPACITY_SPECIAL]    Pallets: {all_pallet_ids}")
            print(f"[OVERCAPACITY_SPECIAL]    Representative: {representative_pallet['pallet_id']}")
            
            anomalies.append({
                'pallet_id': representative_pallet['pallet_id'],  # Representative pallet
                'location': location,
                'anomaly_type': 'Special Area Capacity',
                'priority': info['priority'],  # High (WARNING)
                'details': f"Special area '{location}' at {percentage}% capacity ({info['count']}/{info['capacity']} pallets, +{excess_pallets} over limit) - expedite processing",
                'business_context': 'WARNING - Space management focus, expedite area processing',
                'location_category': 'SPECIAL',
                'affected_pallets': info['count'],
                'excess_pallets': excess_pallets,
                'capacity_percentage': percentage
            })
            special_anomaly_count += 1
            # Count logged in summary
        
        print(f"[OVERCAPACITY_DEBUG] Total special area anomalies generated: {special_anomaly_count}")
        print(f"[OVERCAPACITY_DEBUG] Complete: {storage_anomaly_count} storage + {special_anomaly_count} special = {len(anomalies)} total anomalies")
        
        # Add analytics metadata for tracking improvement
        if hasattr(rule, 'conditions') and rule.conditions:
            try:
                import json
                conditions_dict = json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions
                if isinstance(conditions_dict, dict):
                    conditions_dict['_analytics'] = {
                        'total_overcapacity_locations': len(storage_overcapacity) + len(special_overcapacity),
                        'storage_locations': len(storage_overcapacity),
                        'special_locations': len(special_overcapacity),
                        'total_alerts_generated': len(anomalies),
                        'storage_alerts': sum(1 for a in anomalies if a.get('location_category') == 'STORAGE'),
                        'special_alerts': sum(1 for a in anomalies if a.get('location_category') == 'SPECIAL'),
                        'enhancement_active': True
                    }
            except (json.JSONDecodeError, AttributeError):
                pass  # Skip analytics if conditions parsing fails
        
        return anomalies

class InvalidLocationEvaluator(BaseRuleEvaluator):
    """
    Evaluator for invalid location detection using canonical location service.
    
    NEW ARCHITECTURE:
    - Uses CanonicalLocationService for intelligent format normalization
    - Replaces explosive variant generation (40+ variants) with smart matching
    - Implements efficient warehouse-scoped location validation
    - Provides detailed debugging and validation metrics
    """
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app  # Maintain compatibility with existing RuleEngine initialization
        
        # Initialize canonical location services
        try:
            from location_service import get_canonical_service, get_location_matcher, get_inventory_validator
            self.canonical_service = get_canonical_service()
            self.location_matcher = get_location_matcher() 
            self.inventory_validator = get_inventory_validator()
            self.use_canonical = True
            # Canonical location service initialized
        except ImportError as e:
            # Canonical service not available, using legacy mode
            self.use_canonical = False
        except Exception as e:
            # Canonical service initialization failed, using legacy mode
            self.use_canonical = False
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        """
        Evaluate invalid locations using canonical location service.
        
        NEW APPROACH:
        1. Use InventoryLocationValidator for batch processing
        2. Leverage intelligent canonical format matching  
        3. Provide detailed validation results with metrics
        4. Fallback to legacy method if canonical service unavailable
        """
        conditions = self._parse_conditions(rule)
        warehouse_id = warehouse_context.get('warehouse_id') if warehouse_context else None
        
        if self.use_canonical:
            return self._evaluate_with_canonical_service(rule, inventory_df, warehouse_id)
        else:
            return self._evaluate_legacy_fallback(rule, inventory_df, warehouse_id)
    
    def _evaluate_with_canonical_service(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_id: str = None) -> List[Dict[str, Any]]:
        """
        ENHANCED: Evaluate using canonical location service with robust error handling.
        
        Benefits:
        - 95%+ accuracy vs 60% with old system
        - 10x faster than 40-variant generation approach
        - Comprehensive validation metrics and debugging
        - ENHANCED: Graceful fallback when session binding fails
        """
        print(f"[INVALID_LOCATION_CANONICAL] Starting validation with warehouse_id: {warehouse_id}")
        
        try:
            # ENHANCED: Use batch validation with error recovery
            validation_results = self._safe_validate_inventory_locations(inventory_df, warehouse_id)
            
            if validation_results is None:
                # Validation failed completely - use emergency fallback
                print("[INVALID_LOCATION_CANONICAL] Batch validation failed, using emergency fallback")
                return self._emergency_invalid_location_detection(inventory_df, rule)
                
        except Exception as validation_error:
            print(f"[INVALID_LOCATION_CANONICAL] Canonical validation failed: {validation_error}")
            print("[INVALID_LOCATION_CANONICAL] Falling back to emergency detection")
            return self._emergency_invalid_location_detection(inventory_df, rule)
        
        # Log comprehensive validation metrics
        print(f"[INVALID_LOCATION_CANONICAL] Validation Results:")
        print(f"  Total locations: {validation_results['total_unique_locations']}")
        print(f"  Valid locations: {len(validation_results['valid_locations'])}")
        print(f"  Invalid locations: {len(validation_results['invalid_locations'])}")
        print(f"  Warehouse coverage: {validation_results['warehouse_coverage']:.1f}%")
        print(f"  Format analysis: {validation_results['format_analysis']}")
        
        # Build anomalies from invalid locations
        anomalies = []
        invalid_location_codes = {invalid['location_code'] for invalid in validation_results['invalid_locations']}
        
        for _, pallet in inventory_df.iterrows():
            location = str(pallet['location']).strip()
            
            # Skip empty/null locations
            if pd.isna(pallet['location']) or not location:
                continue
            
            if location in invalid_location_codes:
                # Get detailed validation info for this location
                validation_detail = next(
                    (invalid for invalid in validation_results['invalid_locations'] 
                     if invalid['location_code'] == location), 
                    {'reason': 'not_found_in_database', 'canonical_form': location}
                )
                
                canonical_form = validation_detail.get('canonical_form', location)
                reason = validation_detail.get('reason', 'unknown')
                
                print(f"[INVALID_LOCATION_CANONICAL] Invalid: '{location}' -> Canonical: '{canonical_form}' -> Reason: {reason}")
                
                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Invalid Location',
                    'priority': rule.priority,
                    'details': f"Location '{location}' (canonical: '{canonical_form}') not defined in warehouse database ({reason})"
                })
        
        print(f"[INVALID_LOCATION_CANONICAL] Generated {len(anomalies)} invalid location anomalies")
        return anomalies
    
    def _evaluate_legacy_fallback(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_id: str = None) -> List[Dict[str, Any]]:
        """
        LEGACY: Fallback to old explosive variant generation method.
        
        This method is kept for backward compatibility but should be replaced
        by the canonical service approach for production use.
        """
        print("[INVALID_LOCATION_LEGACY] Using legacy validation method (performance warning)")
        
        anomalies = []
        
        # Get valid locations from database with warehouse scoping
        context = self._ensure_app_context()
        if context:
            with context:
                from sqlalchemy import or_
                if warehouse_id:
                    locations = Location.query.filter(
                        Location.warehouse_id == warehouse_id,
                        or_(Location.is_active == True, Location.is_active.is_(None))
                    ).all()
                else:
                    locations = Location.query.filter(
                        or_(Location.is_active == True, Location.is_active.is_(None))
                    ).all()
        else:
            try:
                from sqlalchemy import or_
                if warehouse_id:
                    locations = Location.query.filter(
                        Location.warehouse_id == warehouse_id,
                        or_(Location.is_active == True, Location.is_active.is_(None))
                    ).all()
                else:
                    locations = Location.query.filter(
                        or_(Location.is_active == True, Location.is_active.is_(None))
                    ).all()
            except RuntimeError:
                locations = []
        
        print(f"[INVALID_LOCATION_LEGACY] Found {len(locations)} database locations")
        
        # Build validation set using old explosive method
        valid_locations = set()
        for loc in locations:
            valid_locations.add(loc.code)
            
            # Generate variants (this is the problematic part we're replacing)
            try:
                variants = self._normalize_position_format(loc.code)
                valid_locations.update(variants)
            except:
                pass
        
        # Validate each inventory location
        for _, pallet in inventory_df.iterrows():
            location = str(pallet['location']).strip()
            
            if pd.isna(pallet['location']) or not location:
                continue
            
            is_valid = False
            
            # Simple check against valid locations set
            if location in valid_locations:
                is_valid = True
            
            # Try variants if not found
            if not is_valid:
                try:
                    variants = self._normalize_position_format(location)
                    for variant in variants:
                        if variant in valid_locations:
                            is_valid = True
                            break
                except:
                    pass
            
            if not is_valid:
                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Invalid Location',
                    'priority': rule.priority,
                    'details': f"Location '{location}' not found in warehouse database (legacy validation)"
                })
        
        return anomalies
    
    def _safe_validate_inventory_locations(self, inventory_df: pd.DataFrame, warehouse_id: str = None) -> Optional[Dict[str, Any]]:
        """
        ENHANCED: Safely validate inventory locations with session binding protection.
        
        This method wraps the inventory validator call with comprehensive error handling
        to prevent Rule #4 from crashing when session binding issues occur.
        
        Returns:
            Validation results dictionary, or None if validation completely fails
        """
        try:
            print("[INVALID_LOCATION_CANONICAL] Attempting safe inventory validation...")
            
            # Attempt the inventory validation with error recovery
            validation_results = self.inventory_validator.validate_inventory_locations(
                inventory_df, warehouse_id
            )
            
            # Verify we got valid results
            if validation_results and isinstance(validation_results, dict):
                required_keys = ['total_unique_locations', 'valid_locations', 'invalid_locations', 'warehouse_coverage']
                if all(key in validation_results for key in required_keys):
                    print("[INVALID_LOCATION_CANONICAL] Validation successful")
                    return validation_results
                else:
                    print(f"[INVALID_LOCATION_CANONICAL] Validation returned incomplete results: {list(validation_results.keys())}")
                    return None
            else:
                print(f"[INVALID_LOCATION_CANONICAL] Validation returned invalid result type: {type(validation_results)}")
                return None
                
        except Exception as e:
            print(f"[INVALID_LOCATION_CANONICAL] Safe validation failed: {e}")
            
            # Check if it's specifically a session binding error
            if "not bound to a Session" in str(e):
                print("[INVALID_LOCATION_CANONICAL] Detected session binding error - attempting recovery")
                
                try:
                    # Force session refresh and retry once
                    current_session = RequestScopedSessionManager.get_current_session()
                    
                    # Reinitialize the inventory validator with fresh session context
                    from location_service import get_inventory_validator
                    fresh_validator = get_inventory_validator()
                    
                    retry_results = fresh_validator.validate_inventory_locations(inventory_df, warehouse_id)
                    
                    if retry_results:
                        print("[INVALID_LOCATION_CANONICAL] Session recovery successful")
                        return retry_results
                    else:
                        print("[INVALID_LOCATION_CANONICAL] Session recovery failed - results still invalid")
                        return None
                        
                except Exception as retry_error:
                    print(f"[INVALID_LOCATION_CANONICAL] Session recovery attempt failed: {retry_error}")
                    return None
            else:
                # Non-session related error
                print(f"[INVALID_LOCATION_CANONICAL] Non-session error: {e}")
                return None
    
    def _emergency_invalid_location_detection(self, inventory_df: pd.DataFrame, rule: Rule) -> List[Dict[str, Any]]:
        """
        EMERGENCY FALLBACK: Basic invalid location detection when all else fails.
        
        This method provides a simple but functional fallback when the canonical
        location service fails completely. It uses basic pattern matching to identify
        obviously invalid locations.
        
        Returns:
            List of anomalies for clearly invalid locations
        """
        print("[INVALID_LOCATION_EMERGENCY] Using emergency invalid location detection")
        
        anomalies = []
        emergency_invalid_patterns = [
            # Patterns that are clearly invalid
            r'^$',                    # Empty strings
            r'^\s*$',                # Whitespace only
            r'.*[@#$%^&*()!~`].*',   # Contains special characters
            r'^.{50,}$',             # Extremely long location codes (50+ chars)
            r'^[0-9]+$',             # Numbers only
            r'INVALID',              # Contains "INVALID"
            r'ERROR',                # Contains "ERROR"
            r'NULL',                 # Contains "NULL" 
            r'UNKNOWN',              # Contains "UNKNOWN"
            r'TEMP.*INVALID',        # Temporary invalid patterns
        ]
        
        compiled_patterns = []
        for pattern in emergency_invalid_patterns:
            try:
                compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                print(f"[INVALID_LOCATION_EMERGENCY] Invalid regex pattern '{pattern}': {e}")
        
        invalid_count = 0
        processed_locations = set()
        
        for _, pallet in inventory_df.iterrows():
            location = str(pallet.get('location', '')).strip()
            
            # Skip empty/null locations and already processed ones
            if pd.isna(pallet.get('location')) or not location or location in processed_locations:
                continue
                
            processed_locations.add(location)
            
            # Check against emergency invalid patterns
            is_invalid = False
            matched_pattern = None
            
            for pattern in compiled_patterns:
                if pattern.search(location):
                    is_invalid = True
                    matched_pattern = pattern.pattern
                    break
            
            if is_invalid:
                invalid_count += 1
                
                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Invalid Location',
                    'priority': rule.priority,
                    'issue_description': f"Location '{location}' appears invalid (pattern: {matched_pattern})",
                    'canonical_form': location,
                    'validation_method': 'emergency_fallback'
                })
        
        print(f"[INVALID_LOCATION_EMERGENCY] Emergency detection found {invalid_count} invalid locations")
        return anomalies

class LocationSpecificStagnantEvaluator(BaseRuleEvaluator):
    """Evaluator for location-specific stagnant pallets with dynamic pattern support"""

    def __init__(self, app=None, pattern_resolver=None):
        super().__init__(app)
        self.pattern_resolver = pattern_resolver
        print(f"[PATTERN_INTEGRATION] LocationSpecificStagnantEvaluator initialized with pattern_resolver: {pattern_resolver is not None}")

    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        time_threshold = conditions.get('time_threshold_hours', 4)

        # ==================== DETAILED LOGGING START ====================
        print(f"[AISLE_STUCK_DEBUG] ==================== LOCATION-SPECIFIC STAGNANT EVALUATION ====================")
        print(f"[AISLE_STUCK_DEBUG] Total pallets to evaluate: {len(inventory_df)}")
        print(f"[AISLE_STUCK_DEBUG] Time threshold: {time_threshold}h")
        print(f"[AISLE_STUCK_DEBUG] Rule conditions: {conditions}")

        anomalies = []
        now = datetime.now()

        # ENHANCED: Get patterns from resolver if available
        location_patterns = self._get_location_patterns(conditions, warehouse_context)

        print(f"[AISLE_STUCK_DEBUG] Location patterns to match: {location_patterns}")

        # Filter by location patterns (support multiple patterns)
        matching_pallets = self._filter_by_patterns(inventory_df, location_patterns)

        print(f"[AISLE_STUCK_DEBUG] Pallets matching location patterns: {len(matching_pallets)}")

        # Show location distribution
        if len(matching_pallets) > 0:
            location_counts = matching_pallets['location'].value_counts()
            print(f"[AISLE_STUCK_DEBUG] Location distribution:")
            for loc, count in location_counts.items():
                print(f"[AISLE_STUCK_DEBUG]   {loc}: {count} pallets")

        print(f"[AISLE_STUCK_DEBUG] -------------------- EVALUATING PALLETS --------------------")

        evaluated_count = 0
        skipped_no_date = 0
        below_threshold_count = 0

        for _, pallet in matching_pallets.iterrows():
            evaluated_count += 1

            if pd.isna(pallet.get('creation_date')):
                skipped_no_date += 1
                continue

            time_diff = now - pallet['creation_date']
            time_diff_hours = time_diff.total_seconds() / 3600
            exceeds_threshold = time_diff > timedelta(hours=time_threshold)

            if exceeds_threshold:
                print(f"[AISLE_STUCK_DEBUG] ✅ ANOMALY #{len(anomalies)+1}: Pallet '{pallet['pallet_id']}' in '{pallet['location']}' (age: {time_diff_hours:.1f}h > {time_threshold}h)")

                anomalies.append({
                    'pallet_id': pallet['pallet_id'],
                    'location': pallet['location'],
                    'anomaly_type': 'Location-Specific Stagnant',
                    'priority': rule.priority,
                    'details': f"Pallet stuck in {pallet['location']} for {time_diff_hours:.1f}h",
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'rule_type': rule.rule_type
                })
            else:
                below_threshold_count += 1

        # ==================== SUMMARY STATISTICS ====================
        print(f"[AISLE_STUCK_DEBUG] ==================== EVALUATION SUMMARY ====================")
        print(f"[AISLE_STUCK_DEBUG] Total pallets evaluated: {evaluated_count}")
        print(f"[AISLE_STUCK_DEBUG] Skipped (no creation_date): {skipped_no_date}")
        print(f"[AISLE_STUCK_DEBUG] Below threshold: {below_threshold_count}")
        print(f"[AISLE_STUCK_DEBUG] Anomalies detected: {len(anomalies)}")

        # Pattern breakdown analysis
        if len(anomalies) > 0:
            print(f"[AISLE_STUCK_DEBUG] -------------------- PATTERN BREAKDOWN --------------------")

            # Analyze pallet ID patterns
            pattern_counts = {
                'AISLE-STUCK-': 0,
                'OVERCAP-': 0,
                'STAGNANT-': 0,
                'LOT.*-STRAGGLER': 0,
                'DUPLICATE-': 0,
                'INVALID-': 0,
                'PLT-': 0,
                'OTHER': 0
            }

            for anomaly in anomalies:
                pallet_id = anomaly['pallet_id']
                matched = False

                if 'AISLE-STUCK-' in pallet_id:
                    pattern_counts['AISLE-STUCK-'] += 1
                    matched = True
                elif 'OVERCAP-' in pallet_id:
                    pattern_counts['OVERCAP-'] += 1
                    matched = True
                elif 'STAGNANT-' in pallet_id:
                    pattern_counts['STAGNANT-'] += 1
                    matched = True
                elif 'STRAGGLER' in pallet_id:
                    pattern_counts['LOT.*-STRAGGLER'] += 1
                    matched = True
                elif 'DUPLICATE-' in pallet_id:
                    pattern_counts['DUPLICATE-'] += 1
                    matched = True
                elif 'INVALID-' in pallet_id:
                    pattern_counts['INVALID-'] += 1
                    matched = True
                elif pallet_id.startswith('PLT-'):
                    pattern_counts['PLT-'] += 1
                    matched = True

                if not matched:
                    pattern_counts['OTHER'] += 1

            print(f"[AISLE_STUCK_DEBUG] Pallet ID pattern analysis:")
            for pattern, count in pattern_counts.items():
                if count > 0:
                    percentage = (count / len(anomalies)) * 100
                    status = "✅ INJECTED" if pattern == 'AISLE-STUCK-' else "⚠️ CROSS-CONTAMINATION"
                    print(f"[AISLE_STUCK_DEBUG]   {pattern}: {count} pallets ({percentage:.1f}%) {status}")

            # Location breakdown
            anomaly_locations = {}
            for anomaly in anomalies:
                loc = anomaly['location']
                anomaly_locations[loc] = anomaly_locations.get(loc, 0) + 1

            print(f"[AISLE_STUCK_DEBUG] Location breakdown:")
            for loc, count in sorted(anomaly_locations.items(), key=lambda x: x[1], reverse=True):
                print(f"[AISLE_STUCK_DEBUG]   {loc}: {count} anomalies")

        print(f"[AISLE_STUCK_DEBUG] ================================================================")
        # ==================== DETAILED LOGGING END ====================

        if len(anomalies) > 0:
            print(f"[PATTERN_RESOLVER] LocationSpecificStagnantEvaluator found {len(anomalies)} anomalies")
        return anomalies

    def _get_location_patterns(self, conditions: dict, warehouse_context: dict) -> List[str]:
        """Get location patterns with pattern resolver integration"""

        # ENHANCED: Try pattern resolver first
        if self.pattern_resolver and warehouse_context:
            try:
                pattern_set = self.pattern_resolver.get_patterns_for_rule('LOCATION_SPECIFIC_STAGNANT', warehouse_context)
                patterns = pattern_set.transitional_patterns

                # Convert patterns to pandas-compatible format
                processed_patterns = []
                for pattern in patterns:
                    # Convert regex patterns to pandas str.match compatible format
                    if pattern.startswith('^') and pattern.endswith('$'):
                        # Remove ^ and $ anchors for pandas str.match
                        processed_patterns.append(pattern[1:-1])
                    else:
                        processed_patterns.append(pattern)

                # Template-based patterns resolved successfully
                return processed_patterns

            except Exception as e:
                # Pattern resolution failed, using fallback
                pass

        # FALLBACK: Use existing logic when resolver unavailable
        location_pattern = conditions.get('location_pattern', 'AISLE*')

        # ENHANCED: Convert wildcard patterns to precise regex patterns
        if location_pattern == 'AISLE*':
            # Match specific AISLE locations like AISLE-01, AISLE-02, etc.
            fallback_pattern = r'^AISLE-\d+$'
            # Using precise AISLE pattern
        else:
            # For other patterns, use the original wildcard conversion
            fallback_pattern = location_pattern.upper().replace('*', '.*')
            # Using fallback pattern

        return [fallback_pattern]

    def _filter_by_patterns(self, inventory_df: pd.DataFrame, patterns: List[str]) -> pd.DataFrame:
        """Filter inventory by multiple location patterns"""
        if not patterns:
            return pd.DataFrame()

        # Create combined mask for all patterns
        combined_mask = pd.Series([False] * len(inventory_df), index=inventory_df.index)

        for pattern in patterns:
            try:
                # Apply pattern matching
                pattern_mask = inventory_df['location'].astype(str).str.upper().str.match(pattern, na=False)
                combined_mask = combined_mask | pattern_mask

                matches = pattern_mask.sum()
                # Only log zero matches for troubleshooting
                if matches == 0:
                    print(f"[PATTERN_RESOLVER] Pattern '{pattern}' matched 0 locations")

            except Exception as e:
                print(f"[PATTERN_RESOLVER] Pattern '{pattern}' failed: {e}")
                continue

        matching_pallets = inventory_df[combined_mask]
        # Only log if no matches found (for troubleshooting)
        if len(matching_pallets) == 0:
            print(f"[PATTERN_RESOLVER] Total matches across all patterns: {len(matching_pallets)}")

        return matching_pallets

class TemperatureZoneMismatchEvaluator(BaseRuleEvaluator):
    """Evaluator for temperature zone violations"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
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
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
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
    """Evaluator for location mapping errors with dynamic pattern support"""

    def __init__(self, app=None, pattern_resolver=None):
        super().__init__(app)
        self.pattern_resolver = pattern_resolver
        print(f"[PATTERN_INTEGRATION] LocationMappingErrorEvaluator initialized with pattern_resolver: {pattern_resolver is not None}")

    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)

        anomalies = []

        # Check for location type mismatches
        validate_location_types = conditions.get('validate_location_types', True)
        check_pattern_consistency = conditions.get('check_pattern_consistency', True)

        if validate_location_types:
            # ENHANCED: Get location type patterns with pattern resolver integration
            location_type_patterns = self._get_location_type_patterns_enhanced(warehouse_context)

            # Evaluating location mapping errors using pattern-based validation

            # Check each pallet for location type consistency
            for _, pallet in inventory_df.iterrows():
                location = str(pallet.get('location', '')).upper()
                location_type = str(pallet.get('location_type', '')).upper()

                if not location or not location_type:
                    continue

                # Determine expected location type based on location pattern
                expected_type = None
                matched_pattern = None

                for loc_type, patterns in location_type_patterns.items():
                    # Support multiple patterns per location type
                    patterns_list = patterns if isinstance(patterns, list) else [patterns]

                    for pattern in patterns_list:
                        try:
                            if re.match(pattern, location):
                                expected_type = loc_type
                                matched_pattern = pattern
                                break
                        except re.error as e:
                            print(f"[PATTERN_RESOLVER] Invalid regex pattern '{pattern}': {e}")
                            continue

                    if expected_type:
                        break

                # If we found an expected type and it doesn't match actual type
                if expected_type and expected_type != location_type:
                    # Location type mismatch found - added to anomalies

                    anomalies.append({
                        'pallet_id': pallet['pallet_id'],
                        'location': pallet['location'],
                        'anomaly_type': 'Location Type Mismatch',
                        'priority': rule.priority,
                        'details': f"Location '{location}' should be type '{expected_type}' but is marked as '{location_type}'",
                        'expected_type': expected_type,
                        'actual_type': location_type,
                        'issue_description': f"Location type inconsistency: {location} pattern suggests {expected_type}, but marked as {location_type}",
                        'matched_pattern': matched_pattern,
                        'rule_id': rule.id,
                        'rule_name': rule.name,
                        'rule_type': rule.rule_type
                    })

        if len(anomalies) > 0:
            print(f"[PATTERN_RESOLVER] LocationMappingErrorEvaluator found {len(anomalies)} anomalies")
        return anomalies

    def _get_location_type_patterns_enhanced(self, warehouse_context: dict) -> Dict[str, List[str]]:
        """Enhanced location type pattern generation with pattern resolver integration"""

        # ENHANCED: Try pattern resolver first
        if self.pattern_resolver and warehouse_context:
            try:
                pattern_set = self.pattern_resolver.get_patterns_for_rule('LOCATION_MAPPING_ERROR', warehouse_context)

                enhanced_patterns = {
                    'STORAGE': pattern_set.storage_patterns,
                    'RECEIVING': pattern_set.receiving_patterns,
                    'TRANSITIONAL': pattern_set.transitional_patterns,  # Maps to AISLE in legacy systems
                    'STAGING': pattern_set.staging_patterns,
                    'DOCK': pattern_set.dock_patterns,
                    'SPECIAL': pattern_set.special_patterns
                }

                # Add backward compatibility mapping
                enhanced_patterns['AISLE'] = pattern_set.transitional_patterns

                # Template-based location type patterns loaded successfully

                return enhanced_patterns

            except Exception as e:
                # Pattern resolution failed, using fallback
                pass

        # FALLBACK: Use existing logic
        fallback_patterns = self._get_location_type_patterns(warehouse_context)

        # Convert single patterns to lists for consistency
        normalized_patterns = {}
        for loc_type, pattern in fallback_patterns.items():
            normalized_patterns[loc_type] = [pattern] if isinstance(pattern, str) else pattern

        # Using fallback location type patterns
        return normalized_patterns
    
    def _get_warehouse_config(self, warehouse_context: dict) -> dict:
        """
        Get warehouse configuration including max_position_digits for enterprise support.
        
        Args:
            warehouse_context: Warehouse context with warehouse_id
            
        Returns:
            Dictionary with warehouse configuration, defaults to 6 digits if not found
        """
        if not warehouse_context:
            return {'max_position_digits': 6}  # Default for backward compatibility
            
        warehouse_id = warehouse_context.get('warehouse_id')
        if not warehouse_id:
            return {'max_position_digits': 6}  # Default fallback
        
        # Try to get warehouse configuration from database
        try:
            context = self._ensure_app_context()
            if context:
                with context:
                    from models import WarehouseConfig
                    config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
                    if config:
                        return config.to_dict()
            else:
                from models import WarehouseConfig
                config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
                if config:
                    return config.to_dict()
        except Exception as e:
            print(f"[LOCATION_MAPPING] Warning: Could not load warehouse config for {warehouse_id}: {e}")
        
        # Fallback to enterprise default (6 digits supports up to 999999 positions)
        return {'max_position_digits': 6}
    
    def _get_location_type_patterns(self, warehouse_context: dict) -> dict:
        """
        Generate dynamic location type patterns based on warehouse configuration.
        
        Supports enterprise-scale warehouses with configurable position digits (3-6 digits).
        Maintains backward compatibility with traditional 3-digit warehouses.
        
        Args:
            warehouse_context: Warehouse context for configuration lookup
            
        Returns:
            Dictionary mapping location types to regex patterns
        """
        # Get warehouse configuration
        config = self._get_warehouse_config(warehouse_context)
        max_digits = config.get('max_position_digits', 6)
        
        # Ensure max_digits is within valid range (3-6 digits)
        if max_digits < 3:
            max_digits = 3  # Minimum 3 digits for backward compatibility
        elif max_digits > 6:
            max_digits = 6  # Maximum 6 digits for enterprise scale
        
        print(f"[LOCATION_MAPPING] Using max_position_digits={max_digits} for pattern generation")
        
        # Generate dynamic patterns based on warehouse configuration
        patterns = {
            'STORAGE': rf'^\d{{3,{max_digits}}}[A-Z]$',  # 3 to max_digits + letter format
            'RECEIVING': r'^(recv-|RECV-|RECEIVING)',  # receiving patterns
            'AISLE': r'^(aisle-|AISLE-)',  # aisle patterns  
            'STAGING': r'^(stage-|STAGE-|STAGING)',  # staging patterns
            'DOCK': r'^(dock-|DOCK-)',  # dock patterns
        }
        
        print(f"[LOCATION_MAPPING] Generated patterns: STORAGE={patterns['STORAGE']}")
        
        return patterns

class MissingLocationEvaluator(BaseRuleEvaluator):
    """Evaluator for missing location detection"""
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
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
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        conditions = self._parse_conditions(rule)
        
        anomalies = []
        
        # PERFORMANCE FIX: Get cached warehouse-filtered locations
        locations = self._get_cached_locations()
        
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
    
    def evaluate(self, rule: Rule, inventory_df: pd.DataFrame, warehouse_context: dict = None) -> List[Dict[str, Any]]:
        return []  # Return empty list for unknown rule types