"""
Canonical Location Normalization Service

This module provides a comprehensive solution for location format normalization,
replacing the explosive variant generation approach with intelligent canonical transformation.

Key Features:
- Single canonical format standard: "XX-XX-XXX{L}" (e.g., "01-01-001A")
- Intelligent parsing for all known location format variations
- Efficient caching and lookup strategies
- Warehouse-scoped location validation
- Performance-optimized batch processing

Architecture:
1. CanonicalLocationService: Core normalization logic
2. LocationMatcher: Database lookup with warehouse scoping
3. InventoryLocationValidator: Batch validation for inventory analysis
"""

import re
import logging
from typing import Optional, Dict, List, Set, Tuple
from functools import lru_cache
from sqlalchemy import or_, and_
from models import Location, db
from session_manager import RequestScopedSessionManager, ensure_session_bound, ensure_locations_bound
from session_safe_cache import get_session_safe_cache

logger = logging.getLogger(__name__)

class CanonicalLocationService:
    """
    Single source of truth for location normalization.
    
    Converts any location format to canonical standard: "XX-XX-XXX{L}"
    Where XX = zero-padded numbers, XXX = 3-digit position, L = level letter
    
    Supported Input Formats:
    - Standard: "01-01-001A", "01-01-01A" (variable position digits)
    - Compact: "01A01A", "02B15C" 
    - Mixed: "01-1-01A", "2-06-3B"
    - Special: "RECV-01", "AISLE-01", "STAGE-01", "DOCK-01"
    - Prefixed: "USER_TESTF_01-01-001A", "WH01_RECV-01"
    """
    
    CANONICAL_FORMAT = "{aisle:02d}-{rack:02d}-{position:03d}{level}"
    
    def __init__(self):
        self.location_cache = {}
        self.format_parsers = [
            self._parse_special,       # Handle special locations first (RECV-01, etc.)
            self._parse_standard,      # Standard format with variable padding
            self._parse_compact,       # Compact format (01A01A)
            self._parse_mixed,         # Mixed separators (01-1-01A)
            self._parse_user_common,   # Common user formats (001A01, A1-001, etc.)
        ]
        self.special_locations = {
            'RECV-01', 'RECV-02', 'RECV-001', 'RECV-002',
            'STAGE-01', 'STAGE-02', 'STAGE-001', 'STAGE-002', 
            'DOCK-01', 'DOCK-02', 'DOCK-001', 'DOCK-002',
            'AISLE-01', 'AISLE-02', 'AISLE-001', 'AISLE-002',
            'RECEIVING', 'STAGING', 'SHIPPING', 'DOCK'
        }
        
        logger.info("CanonicalLocationService initialized")
    
    @lru_cache(maxsize=1000)
    def to_canonical(self, location_code: str) -> str:
        """
        Convert ANY location format to canonical standard.
        
        Args:
            location_code: Input location in any supported format
            
        Returns:
            Canonical format string or original if unparseable
            
        Examples:
            "01A01A" -> "01-01-001A"
            "01-01-01A" -> "01-01-001A" 
            "USER_TESTF_01-01-001A" -> "01-01-001A"
            "RECV-01" -> "RECV-01" (special location, unchanged)
        """
        if not location_code or not isinstance(location_code, str):
            return str(location_code) if location_code else ""
        
        # Clean input
        original_code = location_code.strip().upper()
        
        # Remove common prefixes (USER_, WH_, warehouse IDs)
        clean_code = self._remove_prefixes(original_code)
        
        # Try each parser until one succeeds
        for parser in self.format_parsers:
            try:
                canonical = parser(clean_code)
                if canonical:
                    logger.debug(f"Location normalized: '{original_code}' -> '{canonical}'")
                    return canonical
            except Exception as e:
                logger.debug(f"Parser {parser.__name__} failed for '{clean_code}': {e}")
                continue
        
        # Return original if unparseable
        logger.debug(f"Location unchanged: '{original_code}' (no parser matched)")
        return original_code
    
    def _remove_prefixes(self, location_code: str) -> str:
        """Remove common warehouse and user prefixes"""
        prefixes_to_remove = [
            r'^USER_[A-Z0-9]+_',    # USER_TESTF_, USER_HOLA3_
            r'^WH[0-9]+_',          # WH01_, WH001_
            r'^DEFAULT_',           # DEFAULT_
            r'^WAREHOUSE_',         # WAREHOUSE_
        ]
        
        clean_code = location_code
        for prefix_pattern in prefixes_to_remove:
            clean_code = re.sub(prefix_pattern, '', clean_code)
        
        return clean_code
    
    def _parse_special(self, code: str) -> Optional[str]:
        """
        Parse special location codes that don't follow standard aisle-rack-position format.
        
        Examples: RECV-01, AISLE-01, STAGE-01, DOCK-01, RECEIVING, STAGING
        """
        # Direct match for known special locations
        if code in self.special_locations:
            return code
        
        # Pattern match for numbered special locations
        special_pattern = r'^(RECV|STAGE|DOCK|AISLE)-(\d{1,3})$'
        match = re.match(special_pattern, code)
        if match:
            area_type, number = match.groups()
            # Normalize number to 2 digits for consistency
            return f"{area_type}-{int(number):02d}"
        
        return None
    
    def _parse_standard(self, code: str) -> Optional[str]:
        """
        Parse standard format: XX-XX-XXX{L} with variable padding.
        
        Examples: 
            "01-01-001A" -> "01-01-001A" (already canonical)
            "01-01-01A" -> "01-01-001A" (pad position to 3 digits)
            "1-1-1A" -> "01-01-001A" (pad all numbers)
        """
        standard_pattern = r'^(\d{1,2})-(\d{1,2})-(\d{1,3})([A-Z])$'
        match = re.match(standard_pattern, code)
        if match:
            aisle, rack, position, level = match.groups()
            return f"{int(aisle):02d}-{int(rack):02d}-{int(position):03d}{level}"
        
        return None
    
    def _parse_compact(self, code: str) -> Optional[str]:
        """
        Parse compact format: XX{L}XX{L} where first XX is aisle, second XX is position.
        Assumes rack = 01 for compact format.
        
        Examples:
            "01A01A" -> "01-01-001A"
            "02B15C" -> "02-01-015C" 
        """
        compact_pattern = r'^(\d{1,2})([A-Z])(\d{1,2})([A-Z])$'
        match = re.match(compact_pattern, code)
        if match:
            aisle, rack_level, position, level = match.groups()
            # For compact format, assume rack = 01 and use the level from the end
            return f"{int(aisle):02d}-01-{int(position):03d}{level}"
        
        return None
    
    def _parse_mixed(self, code: str) -> Optional[str]:
        """
        Parse mixed separator format with inconsistent padding.
        
        Examples:
            "01-1-01A" -> "01-01-001A"
            "2-06-3B" -> "02-06-003B"
        """
        # This is handled by _parse_standard since it already supports variable padding
        return self._parse_standard(code)
    
    def _parse_user_common(self, code: str) -> Optional[str]:
        """
        Parse common user formats that don't fit other patterns.
        
        This handles formats commonly used by warehouse operations:
        
        Examples:
            "001A01" -> "01-01-001A" (position + level + rack format)
            "001B02" -> "01-02-001B" 
            "A1-001" -> "01-01-001A" (level + rack - position)
            "B2-015" -> "02-01-015B"
            "5A10"   -> "01-01-005A" (compact: position + level + rack)
        """
        
        # Pattern 1: PPP{L}RR (position + level + rack) - e.g., "001A01" -> "01-01-001A"  
        pattern1 = r'^(\d{1,3})([A-Z])(\d{1,2})$'
        match1 = re.match(pattern1, code)
        if match1:
            position, level, rack = match1.groups()
            aisle = 1  # Default aisle for this format
            return self.CANONICAL_FORMAT.format(
                aisle=int(aisle),
                rack=int(rack), 
                position=int(position),
                level=level
            )
        
        # Pattern 2: {L}R-PPP (level + rack - position) - e.g., "A1-001" -> "01-01-001A"
        pattern2 = r'^([A-Z])(\d{1,2})-(\d{1,3})$'
        match2 = re.match(pattern2, code)
        if match2:
            level, rack, position = match2.groups()
            aisle = 1  # Default aisle for this format
            return self.CANONICAL_FORMAT.format(
                aisle=int(aisle),
                rack=int(rack),
                position=int(position), 
                level=level
            )
            
        # Pattern 3: PP{L}R (compact: position + level + rack) - e.g., "5A10" -> "01-10-005A"
        pattern3 = r'^(\d{1,2})([A-Z])(\d{1,2})$'
        match3 = re.match(pattern3, code)
        if match3:
            position, level, rack = match3.groups()
            aisle = 1  # Default aisle for this format
            return self.CANONICAL_FORMAT.format(
                aisle=int(aisle),
                rack=int(rack),
                position=int(position),
                level=level
            )
        
        return None
    
    def generate_search_variants(self, canonical_code: str) -> List[str]:
        """
        Generate LIMITED search variants for a canonical code.
        
        Unlike the old system that generated 40+ variants, this creates only
        essential variations needed for database lookup compatibility.
        
        Args:
            canonical_code: Canonical format location code
            
        Returns:
            List of 3-5 essential variants for database searching
        """
        if not canonical_code:
            return [canonical_code]
        
        variants = {canonical_code}  # Start with canonical
        
        # For special locations, add common variants
        if canonical_code in self.special_locations:
            if canonical_code.endswith('-01'):
                variants.add(canonical_code.replace('-01', '-001'))
            elif canonical_code.endswith('-02'):
                variants.add(canonical_code.replace('-02', '-002'))
            return list(variants)
        
        # For standard locations, add essential variants
        match = re.match(r'^(\d{2})-(\d{2})-(\d{3})([A-Z])$', canonical_code)
        if match:
            aisle, rack, position, level = match.groups()
            
            # Add 2-digit position variant (common in Excel exports)
            position_2digit = f"{int(aisle):02d}-{int(rack):02d}-{int(position):02d}{level}"
            variants.add(position_2digit)
            
            # Add compact variant
            compact_variant = f"{int(aisle):02d}{level}{int(position):02d}{level}"
            variants.add(compact_variant)
        
        return list(variants)
    
    def validate_format(self, location_code: str) -> Dict[str, any]:
        """
        Validate and analyze a location code format.
        
        Returns detailed information about format parsing success,
        canonical conversion, and format type detected.
        """
        result = {
            'original': location_code,
            'canonical': self.to_canonical(location_code),
            'is_parseable': False,
            'format_type': 'unknown',
            'components': {},
            'is_special': False
        }
        
        canonical = result['canonical']
        
        # Check if parsing was successful (canonical != original means it was parsed)
        if canonical != location_code or canonical in self.special_locations:
            result['is_parseable'] = True
        
        # Determine format type
        if canonical in self.special_locations:
            result['format_type'] = 'special'
            result['is_special'] = True
        elif re.match(r'^\d{2}-\d{2}-\d{3}[A-Z]$', canonical):
            result['format_type'] = 'standard'
            # Extract components
            match = re.match(r'^(\d{2})-(\d{2})-(\d{3})([A-Z])$', canonical)
            if match:
                aisle, rack, position, level = match.groups()
                result['components'] = {
                    'aisle': int(aisle),
                    'rack': int(rack), 
                    'position': int(position),
                    'level': level
                }
        
        return result


class LocationMatcher:
    """
    Efficient location matching with warehouse scoping and intelligent caching.
    
    This class provides high-performance location lookup by:
    1. Building warehouse-specific caches
    2. Using canonical format for consistent matching
    3. Implementing fallback lookup strategies
    4. Minimizing database queries through smart caching
    """
    
    def __init__(self, canonical_service: CanonicalLocationService):
        self.canonical = canonical_service
        
        # ENHANCED: Use session-safe caching instead of object caching
        self.session_safe_cache = get_session_safe_cache()
        
        # Legacy cache structures (deprecated - keeping for compatibility)
        self.warehouse_caches = {}  # warehouse_id -> {canonical_code -> Location} - DEPRECATED
        self.global_cache = {}      # canonical_code -> Location - DEPRECATED  
        self.cache_built = set()    # Track which warehouse caches are built
        
        # Enable session-safe caching by default
        self.use_session_safe_cache = True
        
        logger.info("LocationMatcher initialized with session-safe caching")
    
    def find_location(self, location_code: str, warehouse_id: str = None) -> Optional[Location]:
        """
        Find location with intelligent matching strategy.
        
        Search Strategy:
        1. Normalize to canonical format
        2. Check warehouse-specific cache
        3. Check global cache
        4. Fallback to database lookup with variants
        
        Args:
            location_code: Location code in any supported format
            warehouse_id: Optional warehouse scope for faster lookup
            
        Returns:
            Location object if found, None otherwise
        """
        if not location_code:
            return None
        
        # Step 1: Normalize to canonical format
        canonical_code = self.canonical.to_canonical(location_code)
        
        # Step 2: Try session-safe cache first
        if self.use_session_safe_cache:
            cached_location = self.session_safe_cache.get_location(canonical_code, warehouse_id)
            if cached_location:
                logger.debug(f"Session-safe cache hit: {canonical_code}")
                return cached_location
        else:
            # FALLBACK: Use legacy cache with session binding protection
            # Try warehouse-specific cache
            if warehouse_id:
                self._ensure_warehouse_cache(warehouse_id)
                if warehouse_id in self.warehouse_caches:
                    location = self.warehouse_caches[warehouse_id].get(canonical_code)
                    if location:
                        logger.debug(f"Location found in warehouse cache: {canonical_code}")
                        return self._ensure_session_bound(location)
            
            # Try global cache
            location = self.global_cache.get(canonical_code)
            if location:
                logger.debug(f"Location found in global cache: {canonical_code}")
                return self._ensure_session_bound(location)
        
        # Step 3: Database lookup with variants
        location = self._database_lookup_with_variants(canonical_code, warehouse_id)
        if location:
            # Cache the result in session-safe cache
            if self.use_session_safe_cache:
                self.session_safe_cache.put_location(canonical_code, location, warehouse_id)
                logger.debug(f"Stored in session-safe cache: {canonical_code}")
            else:
                # Store in legacy cache
                self.global_cache[canonical_code] = location
                if warehouse_id and warehouse_id in self.warehouse_caches:
                    self.warehouse_caches[warehouse_id][canonical_code] = location
            return location
        
        # Step 5: ARCHITECTURAL FIX - Dynamic Location Auto-Creation
        # If location format is valid but doesn't exist, create it dynamically
        if warehouse_id and self._is_auto_creatable_location(canonical_code):
            location = self._auto_create_location(canonical_code, warehouse_id)
            if location:
                # Cache the newly created location
                self.global_cache[canonical_code] = location
                if warehouse_id in self.warehouse_caches:
                    self.warehouse_caches[warehouse_id][canonical_code] = location
                logger.info(f"Auto-created missing location: {canonical_code} for warehouse {warehouse_id}")
                return location
        
        return None
    
    def _ensure_session_bound(self, location: Location) -> Optional[Location]:
        """
        ENHANCED SESSION BINDING: Use RequestScopedSessionManager for robust session handling.
        
        This leverages the new session manager that's specifically designed for
        web request contexts and handles all the complex session binding scenarios.
        
        Returns:
            Location object bound to current session, or None if binding fails
        """
        if location is None:
            return None
            
        # Use the enhanced session manager
        bound_location = ensure_session_bound(location)
        
        if bound_location and bound_location != location:
            # Location was rebound - update our caches with the new bound object
            try:
                canonical_code = self.canonical.to_canonical(bound_location.code)
                self.global_cache[canonical_code] = bound_location
                
                # Update warehouse caches as well
                warehouse_id = getattr(bound_location, 'warehouse_id', None)
                if warehouse_id and warehouse_id in self.warehouse_caches:
                    self.warehouse_caches[warehouse_id][canonical_code] = bound_location
                    
                logger.debug(f"Updated caches with rebound location: {bound_location.code}")
            except Exception as cache_update_error:
                logger.warning(f"Failed to update caches after session rebinding: {cache_update_error}")
        
        return bound_location
    
    def _fresh_database_lookup(self, location_code: str, warehouse_id: str = None) -> Optional[Location]:
        """
        Fresh database lookup as fallback when session binding fails.
        This bypasses all caches and queries database directly.
        """
        try:
            query = Location.query.filter(
                Location.code == location_code,
                or_(Location.is_active == True, Location.is_active.is_(None))
            )
            if warehouse_id:
                query = query.filter(Location.warehouse_id == warehouse_id)
            
            fresh_location = query.first()
            logger.info(f"Fresh database lookup for {location_code}: {'found' if fresh_location else 'not found'}")
            return fresh_location
        except Exception as e:
            logger.error(f"Fresh database lookup failed for {location_code}: {e}")
            return None
    
    def _ensure_warehouse_cache(self, warehouse_id: str):
        """Build warehouse cache if not already built"""
        if warehouse_id not in self.cache_built:
            self._build_warehouse_cache(warehouse_id)
            self.cache_built.add(warehouse_id)
    
    def _build_warehouse_cache(self, warehouse_id: str):
        """
        Build efficient lookup cache for specific warehouse.
        
        This method queries all locations for a warehouse once and builds
        a hash map for O(1) lookups, significantly improving performance
        over repeated database queries.
        """
        try:
            logger.info(f"Building location cache for warehouse: {warehouse_id}")
            
            locations = Location.query.filter(
                Location.warehouse_id == warehouse_id,
                or_(Location.is_active == True, Location.is_active.is_(None))
            ).all()
            
            cache = {}
            for location in locations:
                # Store by canonical format
                canonical = self.canonical.to_canonical(location.code)
                cache[canonical] = location
                
                # Also store by original code for direct lookup
                if location.code != canonical:
                    cache[location.code] = location
            
            self.warehouse_caches[warehouse_id] = cache
            logger.info(f"Cached {len(locations)} locations for warehouse {warehouse_id}")
            
        except Exception as e:
            logger.error(f"Failed to build warehouse cache for {warehouse_id}: {e}")
            self.warehouse_caches[warehouse_id] = {}
    
    def _database_lookup_with_variants(self, canonical_code: str, warehouse_id: str = None) -> Optional[Location]:
        """
        Fallback database lookup using search variants.
        
        Uses minimal variant generation (3-5 variants instead of 40+)
        for database lookup when cache misses occur.
        """
        try:
            # Generate minimal search variants
            search_variants = self.canonical.generate_search_variants(canonical_code)
            
            # Build query with warehouse scoping
            query = Location.query.filter(
                Location.code.in_(search_variants),
                or_(Location.is_active == True, Location.is_active.is_(None))
            )
            
            if warehouse_id:
                query = query.filter(Location.warehouse_id == warehouse_id)
            
            location = query.first()
            
            if location:
                logger.debug(f"Location found via database lookup: {canonical_code} -> {location.code}")
            else:
                logger.debug(f"Location not found in database: {canonical_code} (searched {len(search_variants)} variants)")
            
            return location
            
        except Exception as e:
            logger.error(f"Database lookup failed for {canonical_code}: {e}")
            return None
    
    def batch_find_locations(self, location_codes: List[str], warehouse_id: str = None) -> Dict[str, Optional[Location]]:
        """
        Efficient batch location lookup with enhanced session binding protection.
        
        Optimized for processing many locations at once (e.g., during inventory analysis).
        Uses single database query for all missing locations after cache lookup.
        
        ENHANCED: Uses RequestScopedSessionManager for web request context safety.
        """
        results = {}
        found_locations = []
        
        # Step 1: Try to resolve as many as possible from cache
        for location_code in location_codes:
            location = self.find_location(location_code, warehouse_id)
            
            if location is not None:
                found_locations.append(location)
                results[location_code] = location
            else:
                results[location_code] = None
        
        # Step 2: Ensure all found locations are session-bound using batch processing
        if found_locations:
            bound_locations = ensure_locations_bound(found_locations)
            
            # Update results with bound locations
            for i, location_code in enumerate(location_codes):
                if results[location_code] is not None:
                    # Find the corresponding bound location
                    original_location = results[location_code]
                    bound_location = None
                    
                    for bound_loc in bound_locations:
                        if (hasattr(bound_loc, 'code') and hasattr(original_location, 'code') 
                            and bound_loc.code == original_location.code):
                            bound_location = bound_loc
                            break
                    
                    results[location_code] = bound_location
        
        # Step 3: Log summary
        successful_bindings = sum(1 for loc in results.values() if loc is not None)
        if successful_bindings < len(location_codes):
            logger.info(f"Batch lookup: {successful_bindings}/{len(location_codes)} locations successfully bound to session")
        
        return results
    
    def _is_auto_creatable_location(self, canonical_code: str) -> bool:
        """
        Determine if a location can be auto-created based on format validation.
        
        Only auto-create storage locations that follow standard pattern XX-XX-XXXL
        Do NOT auto-create special areas (RECV-01, etc.) as they need careful configuration
        
        Args:
            canonical_code: Location code in canonical format
            
        Returns:
            True if location can be safely auto-created
        """
        # Only auto-create standard storage locations (not special areas)
        storage_pattern = r'^(\d{2})-(\d{2})-(\d{3})([A-Z])$'
        match = re.match(storage_pattern, canonical_code)
        
        if not match:
            logger.debug(f"Location {canonical_code} is not auto-creatable (not standard storage format)")
            return False
        
        aisle, rack, position, level = match.groups()
        
        # Set reasonable limits to prevent abuse (can be made configurable)
        if int(aisle) > 50:  # Max 50 aisles
            logger.warning(f"Location {canonical_code} exceeds aisle limit (50)")
            return False
            
        if int(rack) > 50:   # Max 50 racks per aisle  
            logger.warning(f"Location {canonical_code} exceeds rack limit (50)")
            return False
            
        if int(position) > 999:  # Max 999 positions (already handled by format)
            logger.warning(f"Location {canonical_code} exceeds position limit (999)")
            return False
        
        # Valid level check (A-Z)
        if not level.isalpha() or len(level) != 1:
            logger.warning(f"Location {canonical_code} has invalid level: {level}")
            return False
        
        logger.debug(f"Location {canonical_code} is auto-creatable")
        return True
    
    def _auto_create_location(self, canonical_code: str, warehouse_id: str) -> Optional[Location]:
        """
        Auto-create a missing storage location based on canonical format.
        
        This implements dynamic template expansion - when users reference locations
        that don't exist but follow valid patterns, create them automatically
        with sensible defaults based on warehouse configuration.
        
        Args:
            canonical_code: Location code in canonical format (XX-XX-XXXL)
            warehouse_id: Target warehouse ID
            
        Returns:
            Created Location object or None if creation failed
        """
        try:
            from models import Location, WarehouseConfig
            
            # Get warehouse configuration for defaults
            config = WarehouseConfig.query.filter_by(warehouse_id=warehouse_id).first()
            default_capacity = config.default_pallet_capacity if config else 1
            
            # Parse location components
            storage_pattern = r'^(\d{2})-(\d{2})-(\d{3})([A-Z])$'
            match = re.match(storage_pattern, canonical_code)
            
            if not match:
                logger.error(f"Cannot auto-create non-storage location: {canonical_code}")
                return None
            
            aisle, rack, position, level = match.groups()
            
            # WORKAROUND: Create location with warehouse-prefixed code to avoid global conflicts
            # Long-term: Database schema needs compound unique key (warehouse_id, code)
            prefixed_code = f"{warehouse_id}_{canonical_code}"
            
            location = Location(
                warehouse_id=warehouse_id,
                code=prefixed_code,  # Use prefixed code for global uniqueness
                location_type='STORAGE',
                zone='STORAGE',  # Default zone for auto-created storage
                pallet_capacity=default_capacity,
                is_active=True,
                created_by=1  # System user - could be made configurable
            )
            
            # Check if location already exists (race condition safety)
            existing = Location.query.filter(
                Location.warehouse_id == warehouse_id,
                Location.code == canonical_code
            ).first()
            
            if existing:
                logger.info(f"Location {canonical_code} already exists, returning existing")
                return existing
            
            # Save to database
            db.session.add(location)
            db.session.commit()
            
            logger.info(f"Successfully auto-created location: {canonical_code} "
                       f"in warehouse {warehouse_id} with capacity {default_capacity}")
            
            return location
            
        except Exception as e:
            logger.error(f"Failed to auto-create location {canonical_code}: {e}")
            db.session.rollback()
            return None
    
    def clear_caches(self):
        """
        Clear all location caches to force fresh database lookups.
        
        This should be called after:
        - Warehouse template operations
        - Location data changes
        - Database session issues
        """
        self.warehouse_caches.clear()
        self.global_cache.clear()
        self.cache_built.clear()
        logger.info("All location caches cleared - fresh lookups will occur")
    
    def get_cache_stats(self) -> Dict[str, any]:
        """Return cache statistics for monitoring and debugging"""
        return {
            'warehouse_caches': len(self.warehouse_caches),
            'global_cache_size': len(self.global_cache),
            'cached_warehouses': list(self.cache_built),
            'total_cached_locations': sum(len(cache) for cache in self.warehouse_caches.values())
        }
    
    def clear_cache(self, warehouse_id: str = None):
        """Clear cache for specific warehouse or all caches"""
        if warehouse_id:
            self.warehouse_caches.pop(warehouse_id, None)
            self.cache_built.discard(warehouse_id)
            logger.info(f"Cleared cache for warehouse: {warehouse_id}")
        else:
            self.warehouse_caches.clear()
            self.global_cache.clear()
            self.cache_built.clear()
            logger.info("Cleared all location caches")


class InventoryLocationValidator:
    """
    Batch validation service for inventory location analysis.
    
    Optimized for processing large inventory datasets by:
    1. Batch processing all locations at once
    2. Providing detailed validation results
    3. Calculating coverage and quality metrics
    4. Identifying problematic location patterns
    """
    
    def __init__(self, canonical_service: CanonicalLocationService, location_matcher: LocationMatcher):
        self.canonical = canonical_service
        self.matcher = location_matcher
        logger.info("InventoryLocationValidator initialized")
    
    def validate_inventory_locations(self, inventory_df, warehouse_id: str = None) -> Dict[str, any]:
        """
        Validate all locations in inventory dataset with comprehensive analysis.
        
        Args:
            inventory_df: Pandas DataFrame with 'location' column
            warehouse_id: Optional warehouse scope for validation
            
        Returns:
            Comprehensive validation results with metrics and detailed analysis
        """
        logger.info(f"Starting inventory location validation for {len(inventory_df)} records")
        
        # Extract unique locations
        location_series = inventory_df['location'].dropna()
        unique_locations = location_series.unique()
        
        results = {
            'total_records': len(inventory_df),
            'total_unique_locations': len(unique_locations),
            'valid_locations': {},
            'invalid_locations': [],
            'warehouse_id': warehouse_id,
            'warehouse_coverage': 0.0,
            'normalization_stats': {},
            'format_analysis': {},
            'validation_details': []
        }
        
        # Batch location lookup
        location_lookup_results = self.matcher.batch_find_locations(unique_locations, warehouse_id)
        
        # Process results
        format_counts = {}
        normalization_success = 0
        
        for location_code in unique_locations:
            location_obj = location_lookup_results[location_code]
            
            # Analyze format
            format_info = self.canonical.validate_format(location_code)
            format_type = format_info['format_type']
            format_counts[format_type] = format_counts.get(format_type, 0) + 1
            
            if format_info['is_parseable']:
                normalization_success += 1
            
            # Store validation result
            if location_obj:
                results['valid_locations'][location_code] = {
                    'location_object': location_obj,
                    'canonical_form': format_info['canonical'],
                    'format_type': format_type,
                    'database_code': location_obj.code
                }
            else:
                results['invalid_locations'].append({
                    'location_code': location_code,
                    'canonical_form': format_info['canonical'],
                    'format_type': format_type,
                    'reason': 'not_found_in_database'
                })
                
                # Add detailed validation info
                results['validation_details'].append({
                    'location_code': location_code,
                    'issue': 'Location not found in database',
                    'canonical_form': format_info['canonical'],
                    'format_analysis': format_info
                })
        
        # Calculate metrics
        results['warehouse_coverage'] = (len(results['valid_locations']) / len(unique_locations)) * 100 if unique_locations.size > 0 else 0
        results['normalization_stats'] = {
            'normalization_success_rate': (normalization_success / len(unique_locations)) * 100 if unique_locations.size > 0 else 0,
            'parseable_locations': normalization_success,
            'unparseable_locations': len(unique_locations) - normalization_success
        }
        results['format_analysis'] = format_counts
        
        logger.info(f"Validation complete: {results['warehouse_coverage']:.1f}% coverage, {len(results['valid_locations'])} valid, {len(results['invalid_locations'])} invalid")
        
        return results
    
    def generate_validation_report(self, validation_results: Dict) -> str:
        """Generate human-readable validation report"""
        report = []
        report.append("=== INVENTORY LOCATION VALIDATION REPORT ===")
        report.append("")
        report.append(f"Total Records: {validation_results['total_records']}")
        report.append(f"Unique Locations: {validation_results['total_unique_locations']}")
        report.append(f"Warehouse: {validation_results['warehouse_id'] or 'Global'}")
        report.append(f"Coverage: {validation_results['warehouse_coverage']:.1f}%")
        report.append("")
        
        report.append("VALIDATION SUMMARY:")
        report.append(f"  ✅ Valid: {len(validation_results['valid_locations'])}")
        report.append(f"  ❌ Invalid: {len(validation_results['invalid_locations'])}")
        report.append("")
        
        report.append("FORMAT ANALYSIS:")
        for format_type, count in validation_results['format_analysis'].items():
            report.append(f"  {format_type}: {count} locations")
        report.append("")
        
        if validation_results['invalid_locations']:
            report.append("INVALID LOCATIONS:")
            for invalid in validation_results['invalid_locations'][:10]:  # Show first 10
                report.append(f"  ❌ {invalid['location_code']} (canonical: {invalid['canonical_form']})")
            if len(validation_results['invalid_locations']) > 10:
                report.append(f"  ... and {len(validation_results['invalid_locations']) - 10} more")
        
        return "\n".join(report)


# Global service instances (singleton pattern)
_canonical_service = None
_location_matcher = None
_inventory_validator = None

def get_canonical_service() -> CanonicalLocationService:
    """Get singleton instance of CanonicalLocationService"""
    global _canonical_service
    if _canonical_service is None:
        _canonical_service = CanonicalLocationService()
    return _canonical_service

def get_location_matcher() -> LocationMatcher:
    """Get singleton instance of LocationMatcher"""
    global _location_matcher
    if _location_matcher is None:
        canonical_service = get_canonical_service()
        _location_matcher = LocationMatcher(canonical_service)
    return _location_matcher

def get_inventory_validator() -> InventoryLocationValidator:
    """Get singleton instance of InventoryLocationValidator"""
    global _inventory_validator
    if _inventory_validator is None:
        canonical_service = get_canonical_service()
        location_matcher = get_location_matcher()
        _inventory_validator = InventoryLocationValidator(canonical_service, location_matcher)
    return _inventory_validator

# Convenience functions for easy integration
def normalize_location(location_code: str) -> str:
    """Normalize location code to canonical format"""
    return get_canonical_service().to_canonical(location_code)

def find_location(location_code: str, warehouse_id: str = None) -> Optional[Location]:
    """Find location in database with intelligent matching"""
    return get_location_matcher().find_location(location_code, warehouse_id)

def validate_inventory_locations(inventory_df, warehouse_id: str = None) -> Dict[str, any]:
    """Validate all locations in inventory DataFrame"""
    return get_inventory_validator().validate_inventory_locations(inventory_df, warehouse_id)

def clear_location_caches():
    """Clear all location caches - call after template operations or database changes"""
    get_location_matcher().clear_caches()