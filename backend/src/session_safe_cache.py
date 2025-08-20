"""
SESSION-SAFE CACHE ARCHITECTURE

This module implements a caching system that prevents SQLAlchemy session binding issues
by storing only the data needed to reconstruct objects, not the objects themselves.

Key Features:
- Stores object data, not object references
- Automatically reconstructs objects with current session
- Web request context awareness
- Automatic cache invalidation strategies
- Performance monitoring and debugging
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from flask import g
from session_manager import RequestScopedSessionManager, get_session

logger = logging.getLogger(__name__)

@dataclass
class CachedLocationData:
    """
    Data structure for cached location information.
    
    This stores only the essential data needed to reconstruct a Location object,
    preventing session binding issues while maintaining cache efficiency.
    """
    id: int
    code: str
    location_type: str
    warehouse_id: str
    zone: Optional[str] = None
    pallet_capacity: Optional[int] = 1
    capacity: Optional[int] = 1
    is_active: bool = True
    
    # Metadata
    cached_at: Optional[datetime] = None
    cache_hits: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_location(cls, location) -> 'CachedLocationData':
        """Create cached data from a Location object"""
        return cls(
            id=location.id,
            code=location.code,
            location_type=location.location_type,
            warehouse_id=location.warehouse_id,
            zone=getattr(location, 'zone', None),
            pallet_capacity=getattr(location, 'pallet_capacity', 1),
            capacity=getattr(location, 'capacity', 1),
            is_active=getattr(location, 'is_active', True),
            cached_at=datetime.utcnow(),
            cache_hits=0
        )

class SessionSafeLocationCache:
    """
    Session-safe caching system for Location objects.
    
    This cache stores location data instead of object references, preventing
    the "Instance not bound to a Session" errors that plague the current system.
    """
    
    def __init__(self, max_cache_size: int = 1000, cache_ttl_hours: int = 24):
        self.max_cache_size = max_cache_size
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # Cache structures (store data, not objects)
        self.global_cache: Dict[str, CachedLocationData] = {}
        self.warehouse_caches: Dict[str, Dict[str, CachedLocationData]] = {}
        
        # Cache metadata
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'reconstructions': 0,
            'evictions': 0,
            'created_at': datetime.utcnow()
        }
        
        logger.info(f"SessionSafeLocationCache initialized (max_size: {max_cache_size}, ttl: {cache_ttl_hours}h)")
    
    def get_location(self, location_code: str, warehouse_id: str = None) -> Optional[Any]:
        """
        Get a Location object from cache, reconstructed with current session.
        
        Args:
            location_code: Location code to lookup
            warehouse_id: Optional warehouse scope
            
        Returns:
            Location object bound to current session, or None if not cached
        """
        # Try warehouse-specific cache first if warehouse_id provided
        if warehouse_id and warehouse_id in self.warehouse_caches:
            cached_data = self.warehouse_caches[warehouse_id].get(location_code)
            if cached_data:
                return self._reconstruct_location(cached_data, source='warehouse_cache')
        
        # Try global cache
        cached_data = self.global_cache.get(location_code)
        if cached_data:
            return self._reconstruct_location(cached_data, source='global_cache')
        
        # Cache miss
        self.cache_stats['misses'] += 1
        return None
    
    def put_location(self, location_code: str, location_obj: Any, warehouse_id: str = None) -> bool:
        """
        Store a Location object in cache as data.
        
        Args:
            location_code: Location code for lookup
            location_obj: Location object to cache
            warehouse_id: Optional warehouse scope
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not location_obj:
            return False
        
        try:
            # Convert Location object to cacheable data
            cached_data = CachedLocationData.from_location(location_obj)
            
            # Store in appropriate cache
            if warehouse_id:
                if warehouse_id not in self.warehouse_caches:
                    self.warehouse_caches[warehouse_id] = {}
                self.warehouse_caches[warehouse_id][location_code] = cached_data
            
            # Always store in global cache as well
            self.global_cache[location_code] = cached_data
            
            # Perform cache maintenance if needed
            self._maintain_cache_size()
            
            logger.debug(f"Cached location data: {location_code} (warehouse: {warehouse_id or 'global'})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache location {location_code}: {e}")
            return False
    
    def _reconstruct_location(self, cached_data: CachedLocationData, source: str = 'unknown') -> Optional[Any]:
        """
        Reconstruct a Location object from cached data using current session.
        
        Args:
            cached_data: Cached location data
            source: Cache source for debugging
            
        Returns:
            Location object bound to current session
        """
        try:
            # Check if cached data is still valid (TTL)
            if cached_data.cached_at and datetime.utcnow() - cached_data.cached_at > self.cache_ttl:
                logger.debug(f"Cache data expired for location {cached_data.code}")
                self._evict_location(cached_data.code)
                self.cache_stats['evictions'] += 1
                return None
            
            # Get current session
            current_session = get_session()
            
            # Reconstruct Location object using current session
            from models import Location
            
            # Try to get fresh object from database using cached ID
            location_obj = current_session.get(Location, cached_data.id)
            
            if location_obj:
                # Update cache stats
                cached_data.cache_hits += 1
                self.cache_stats['hits'] += 1
                self.cache_stats['reconstructions'] += 1
                
                logger.debug(f"Reconstructed location {cached_data.code} from {source} (hits: {cached_data.cache_hits})")
                return location_obj
            else:
                # Object no longer exists in database - evict from cache
                logger.warning(f"Cached location {cached_data.code} no longer exists in database")
                self._evict_location(cached_data.code)
                return None
                
        except Exception as e:
            logger.error(f"Failed to reconstruct location {cached_data.code}: {e}")
            # Don't evict on reconstruction errors - might be temporary session issues
            return None
    
    def _evict_location(self, location_code: str):
        """Remove location from all caches"""
        # Remove from global cache
        if location_code in self.global_cache:
            del self.global_cache[location_code]
        
        # Remove from warehouse caches
        for warehouse_cache in self.warehouse_caches.values():
            if location_code in warehouse_cache:
                del warehouse_cache[location_code]
    
    def _maintain_cache_size(self):
        """Maintain cache size limits using LRU-like eviction"""
        if len(self.global_cache) <= self.max_cache_size:
            return
        
        # Find least recently used items (lowest cache_hits, oldest cached_at)
        items_by_usage = sorted(
            self.global_cache.items(),
            key=lambda x: (x[1].cache_hits, x[1].cached_at or datetime.min)
        )
        
        # Evict oldest/least used items
        evict_count = len(self.global_cache) - self.max_cache_size + int(self.max_cache_size * 0.1)  # Evict 10% extra
        
        for location_code, _ in items_by_usage[:evict_count]:
            self._evict_location(location_code)
            self.cache_stats['evictions'] += 1
        
        logger.info(f"Cache maintenance: evicted {evict_count} locations")
    
    def invalidate_request_cache(self):
        """
        Invalidate cache for current request context.
        
        In web request contexts, we want to ensure fresh data for each request
        to prevent cross-request contamination.
        """
        if RequestScopedSessionManager.is_web_request_context():
            # Mark current request as having fresh cache
            g.cache_invalidated = True
            logger.debug("Request-scoped cache invalidation completed")
    
    def clear_cache(self, warehouse_id: str = None):
        """
        Clear cache completely or for specific warehouse.
        
        Args:
            warehouse_id: If provided, clear only this warehouse's cache
        """
        if warehouse_id:
            if warehouse_id in self.warehouse_caches:
                del self.warehouse_caches[warehouse_id]
            logger.info(f"Cleared cache for warehouse: {warehouse_id}")
        else:
            self.global_cache.clear()
            self.warehouse_caches.clear()
            self.cache_stats['hits'] = 0
            self.cache_stats['misses'] = 0
            self.cache_stats['reconstructions'] = 0
            logger.info("Cleared all caches")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_stats': self.cache_stats.copy(),
            'hit_rate_percent': round(hit_rate, 2),
            'total_cached_locations': len(self.global_cache),
            'total_warehouses': len(self.warehouse_caches),
            'cache_size_limit': self.max_cache_size,
            'cache_ttl_hours': self.cache_ttl.total_seconds() / 3600,
            'uptime_hours': (datetime.utcnow() - self.cache_stats['created_at']).total_seconds() / 3600
        }
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get detailed debug information"""
        warehouse_stats = {}
        for warehouse_id, cache in self.warehouse_caches.items():
            warehouse_stats[warehouse_id] = {
                'location_count': len(cache),
                'total_hits': sum(data.cache_hits for data in cache.values()),
                'avg_hits_per_location': sum(data.cache_hits for data in cache.values()) / len(cache) if cache else 0
            }
        
        return {
            'global_cache_size': len(self.global_cache),
            'warehouse_caches': warehouse_stats,
            'performance': self.get_cache_stats(),
            'is_web_request': RequestScopedSessionManager.is_web_request_context()
        }

# Global cache instance
_global_cache: Optional[SessionSafeLocationCache] = None

def get_session_safe_cache() -> SessionSafeLocationCache:
    """Get the global session-safe cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = SessionSafeLocationCache()
    return _global_cache

def clear_global_cache():
    """Clear the global cache instance"""
    global _global_cache
    if _global_cache:
        _global_cache.clear_cache()
        
def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    cache = get_session_safe_cache()
    return cache.get_cache_stats()