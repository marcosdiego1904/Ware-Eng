"""
SimpleScopeService: Unit-Agnostic Warehouse Intelligence Scope Management

This service handles filtering inventory data to include only locations that are
within the warehouse's analysis scope, enabling unit-agnostic anomaly detection.
"""

import fnmatch
import logging
from typing import List, Tuple, Dict, Optional
import pandas as pd

# Import models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import Location, WarehouseScopeConfig

logger = logging.getLogger(__name__)


class SimpleScopeService:
    """
    Simplified scope management service for unit-agnostic warehouse intelligence.

    Key Features:
    - Filters inventory data based on excluded location patterns
    - Provides unit type information for locations
    - Caches scope configurations for performance
    - Graceful fallbacks for missing configurations
    """

    def __init__(self, warehouse_id: str):
        """
        Initialize scope service for a specific warehouse

        Args:
            warehouse_id (str): The warehouse identifier
        """
        self.warehouse_id = warehouse_id
        self._config_cache = None
        self._locations_cache = {}

    def filter_inventory_to_scope(self, inventory_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Apply scope filtering to inventory data to include only tracked locations.

        This is the core method that transforms raw inventory data into
        scope-filtered data ready for rule analysis.

        Args:
            inventory_df (pd.DataFrame): Raw inventory data with 'location' column

        Returns:
            Tuple[pd.DataFrame, Dict]: (filtered_dataframe, scope_metrics)
        """
        logger.info(f"[SCOPE] Filtering inventory for warehouse {self.warehouse_id}")

        if inventory_df.empty or 'location' not in inventory_df.columns:
            logger.warning("[SCOPE] Empty inventory or missing location column")
            return inventory_df, self._create_empty_metrics()

        # Get excluded patterns from configuration
        excluded_patterns = self._get_excluded_patterns()

        if not excluded_patterns:
            # No filtering needed - analyze everything
            logger.info("[SCOPE] No excluded patterns - analyzing all locations")
            return inventory_df, {
                'total_records': len(inventory_df),
                'in_scope_records': len(inventory_df),
                'out_of_scope_records': 0,
                'excluded_patterns': [],
                'scope_applied': False
            }

        # Apply filtering
        logger.info(f"[SCOPE] Applying exclusion patterns: {excluded_patterns}")

        # Create boolean mask for locations to keep (not excluded)
        mask = inventory_df['location'].apply(
            lambda loc: not self._is_location_excluded(str(loc), excluded_patterns)
        )

        filtered_df = inventory_df[mask]

        # Calculate metrics
        metrics = {
            'total_records': len(inventory_df),
            'in_scope_records': len(filtered_df),
            'out_of_scope_records': len(inventory_df) - len(filtered_df),
            'excluded_patterns': excluded_patterns,
            'scope_applied': True
        }

        logger.info(f"[SCOPE] Filtered {metrics['total_records']} → {metrics['in_scope_records']} records")
        logger.info(f"[SCOPE] Excluded {metrics['out_of_scope_records']} records using patterns: {excluded_patterns}")

        return filtered_df, metrics

    def get_location_unit_type(self, location_code: str) -> str:
        """
        Get the unit type for a specific location with intelligent fallbacks.

        Priority order:
        1. Database location record unit_type
        2. Warehouse default unit type
        3. System default ('pallets')

        Args:
            location_code (str): The location code to look up

        Returns:
            str: Unit type ('pallets', 'boxes', 'items', 'cases', 'mixed')
        """
        location_code = str(location_code).strip()

        if not location_code:
            return self._get_default_unit_type()

        # Check cache first
        if location_code in self._locations_cache:
            return self._locations_cache[location_code]['unit_type']

        # Query database for location record
        try:
            from app import db
            location_record = db.session.query(Location).filter_by(
                code=location_code,
                warehouse_id=self.warehouse_id
            ).first()

            if location_record and location_record.unit_type:
                unit_type = location_record.unit_type

                # Cache the result
                self._locations_cache[location_code] = {
                    'unit_type': unit_type,
                    'capacity': location_record.capacity
                }

                return unit_type

        except Exception as e:
            logger.warning(f"[SCOPE] Could not query location {location_code}: {e}")

        # Fallback to warehouse default
        default_unit_type = self._get_default_unit_type()

        # Cache the fallback
        self._locations_cache[location_code] = {
            'unit_type': default_unit_type,
            'capacity': None
        }

        return default_unit_type

    def get_location_capacity(self, location_code: str) -> Optional[int]:
        """
        Get the capacity for a specific location.

        Args:
            location_code (str): The location code to look up

        Returns:
            Optional[int]: Location capacity or None if not found
        """
        location_code = str(location_code).strip()

        if not location_code:
            return None

        # Check cache first
        if location_code in self._locations_cache:
            return self._locations_cache[location_code]['capacity']

        # Query database
        try:
            from app import db
            location_record = db.session.query(Location).filter_by(
                code=location_code,
                warehouse_id=self.warehouse_id
            ).first()

            if location_record:
                capacity = location_record.capacity

                # Update cache
                if location_code not in self._locations_cache:
                    self._locations_cache[location_code] = {}
                self._locations_cache[location_code]['capacity'] = capacity

                return capacity

        except Exception as e:
            logger.warning(f"[SCOPE] Could not query capacity for {location_code}: {e}")

        return None

    def is_location_in_scope(self, location_code: str) -> bool:
        """
        Check if a location is within the analysis scope.

        Args:
            location_code (str): The location code to check

        Returns:
            bool: True if location should be analyzed, False if excluded
        """
        excluded_patterns = self._get_excluded_patterns()
        return not self._is_location_excluded(str(location_code), excluded_patterns)

    def get_scope_summary(self) -> Dict:
        """
        Get a summary of the current scope configuration.

        Returns:
            Dict: Scope configuration summary
        """
        config = self._get_scope_config()

        return {
            'warehouse_id': self.warehouse_id,
            'excluded_patterns': config.get('excluded_patterns', []),
            'default_unit_type': config.get('default_unit_type', 'pallets'),
            'has_exclusions': bool(config.get('excluded_patterns')),
            'scope_configured': bool(config)
        }

    # Private helper methods

    def _get_excluded_patterns(self) -> List[str]:
        """Get list of excluded location patterns"""
        config = self._get_scope_config()
        return config.get('excluded_patterns', [])

    def _get_default_unit_type(self) -> str:
        """Get warehouse default unit type"""
        config = self._get_scope_config()
        return config.get('default_unit_type', 'pallets')

    def _is_location_excluded(self, location: str, excluded_patterns: List[str]) -> bool:
        """
        Check if location matches any excluded pattern using fnmatch.

        Args:
            location (str): Location code to check
            excluded_patterns (List[str]): List of exclusion patterns

        Returns:
            bool: True if location should be excluded
        """
        if not excluded_patterns or not location:
            return False

        location_upper = location.upper().strip()

        for pattern in excluded_patterns:
            if not pattern:
                continue

            pattern_upper = pattern.upper().strip()

            # Use fnmatch for pattern matching (supports * and ? wildcards)
            if fnmatch.fnmatch(location_upper, pattern_upper):
                logger.debug(f"[SCOPE] Location '{location}' excluded by pattern '{pattern}'")
                return True

        return False

    def _get_scope_config(self) -> Dict:
        """
        Get warehouse scope configuration with caching.

        Returns:
            Dict: Scope configuration
        """
        if self._config_cache is None:
            try:
                from app import db
                config_record = db.session.query(WarehouseScopeConfig).filter_by(
                    warehouse_id=self.warehouse_id
                ).first()

                if config_record:
                    self._config_cache = {
                        'excluded_patterns': config_record.excluded_patterns_list,  # Use property for JSON handling
                        'default_unit_type': config_record.default_unit_type or 'pallets',
                        'config_metadata': config_record.config_metadata_dict  # Use property for JSON handling
                    }
                    logger.info(f"[SCOPE] Loaded scope config for warehouse {self.warehouse_id}")
                else:
                    # Create default configuration
                    self._config_cache = {
                        'excluded_patterns': [],  # No exclusions = analyze everything
                        'default_unit_type': 'pallets',
                        'config_metadata': {}
                    }
                    logger.info(f"[SCOPE] Using default scope config for warehouse {self.warehouse_id}")

            except Exception as e:
                logger.error(f"[SCOPE] Failed to load scope config: {e}")
                self._config_cache = {
                    'excluded_patterns': [],
                    'default_unit_type': 'pallets',
                    'config_metadata': {}
                }

        return self._config_cache

    def _create_empty_metrics(self) -> Dict:
        """Create empty metrics for error cases"""
        return {
            'total_records': 0,
            'in_scope_records': 0,
            'out_of_scope_records': 0,
            'excluded_patterns': [],
            'scope_applied': False
        }

    def clear_cache(self):
        """Clear internal caches (useful for testing or configuration updates)"""
        self._config_cache = None
        self._locations_cache = {}
        logger.info(f"[SCOPE] Cleared cache for warehouse {self.warehouse_id}")


# Utility functions for external use

def create_scope_service(warehouse_id: str) -> SimpleScopeService:
    """
    Factory function to create a SimpleScopeService instance.

    Args:
        warehouse_id (str): Warehouse identifier

    Returns:
        SimpleScopeService: Configured scope service
    """
    return SimpleScopeService(warehouse_id)


def is_location_pattern_valid(pattern: str) -> bool:
    """
    Validate that a location pattern is properly formatted.

    Args:
        pattern (str): Pattern to validate

    Returns:
        bool: True if pattern is valid
    """
    if not pattern or not isinstance(pattern, str):
        return False

    pattern = pattern.strip()

    # Basic validation - should not be empty and should contain valid characters
    if not pattern:
        return False

    # Pattern should contain alphanumeric characters, hyphens, underscores, or wildcards
    import re
    if not re.match(r'^[A-Za-z0-9\-_*?]+$', pattern):
        return False

    return True


def validate_scope_configuration(excluded_patterns: List[str]) -> Dict:
    """
    Validate a scope configuration.

    Args:
        excluded_patterns (List[str]): List of exclusion patterns to validate

    Returns:
        Dict: Validation result with 'valid' (bool) and 'issues' (List[str])
    """
    issues = []

    if not isinstance(excluded_patterns, list):
        issues.append("excluded_patterns must be a list")
        return {"valid": False, "issues": issues}

    for i, pattern in enumerate(excluded_patterns):
        if not is_location_pattern_valid(pattern):
            issues.append(f"Invalid pattern at index {i}: '{pattern}'")

    # Check for overly broad patterns that might exclude everything
    dangerous_patterns = ['*', '**', '?*']
    for pattern in excluded_patterns:
        if pattern.strip() in dangerous_patterns:
            issues.append(f"Overly broad pattern detected: '{pattern}' - this might exclude all locations")

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }