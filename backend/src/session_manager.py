"""
REQUEST-SCOPED SESSION MANAGEMENT

This module provides robust session management for web request contexts,
ensuring Location objects are always bound to the current request's session.

Key Features:
- Request-scoped session binding
- Automatic session refresh for cached objects  
- Web request context detection
- Comprehensive session recovery strategies
"""

import logging
from typing import Optional, Any
from flask import g, current_app
from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemy.exc import InvalidRequestError
from models import db, Location

logger = logging.getLogger(__name__)

class RequestScopedSessionManager:
    """
    Manages SQLAlchemy sessions in web request contexts.
    
    This class ensures that Location objects remain bound to the current
    request's active session, preventing the "Instance not bound to a Session"
    errors that occur when cached objects become detached.
    """
    
    @staticmethod
    def is_web_request_context() -> bool:
        """
        Detect if we're running in a Flask web request context.
        
        Returns:
            True if in web request, False if in CLI/script context
        """
        try:
            # Try to access Flask's application context
            current_app._get_current_object()
            # Try to access Flask's request context globals
            _ = g
            return True
        except RuntimeError:
            # No Flask context available - we're in CLI/script mode
            return False
    
    @staticmethod
    def get_current_session():
        """
        Get the current SQLAlchemy session for this request context.
        
        Returns:
            Current active session
        """
        if RequestScopedSessionManager.is_web_request_context():
            # In web request context, use Flask-SQLAlchemy's request-scoped session
            return db.session
        else:
            # In CLI context, return the standard session
            return db.session
    
    @staticmethod
    def ensure_object_session_bound(obj: Any, max_retries: int = 3) -> Optional[Any]:
        """
        Ensure a SQLAlchemy object is bound to the current request session.
        
        This is the core function that fixes session binding issues by:
        1. Detecting if object is detached
        2. Merging object with current session if needed
        3. Providing fallback strategies if merge fails
        
        Args:
            obj: SQLAlchemy model object (e.g., Location)
            max_retries: Maximum number of recovery attempts
            
        Returns:
            Object bound to current session, or None if all recovery fails
        """
        if obj is None:
            return None
            
        session = RequestScopedSessionManager.get_current_session()
        
        for attempt in range(max_retries):
            try:
                # Test if object is bound by accessing a simple property
                _ = obj.id
                _ = getattr(obj, 'code', None)
                
                # If we get here, object is properly bound
                logger.debug(f"Object {getattr(obj, 'code', 'unknown')} is session-bound (attempt {attempt + 1})")
                return obj
                
            except (DetachedInstanceError, InvalidRequestError) as e:
                logger.warning(f"Object detached from session (attempt {attempt + 1}): {e}")
                
                try:
                    # Strategy 1: Merge object with current session
                    merged_obj = session.merge(obj)
                    logger.info(f"Successfully merged object with session (attempt {attempt + 1})")
                    return merged_obj
                    
                except Exception as merge_error:
                    logger.error(f"Session merge failed (attempt {attempt + 1}): {merge_error}")
                    
                    # Strategy 2: Fresh database lookup by primary key
                    try:
                        if hasattr(obj, 'id') and hasattr(obj, '__class__'):
                            obj_id = getattr(obj, 'id', None)
                            if obj_id:
                                fresh_obj = session.get(obj.__class__, obj_id)
                                if fresh_obj:
                                    logger.info(f"Fresh lookup successful (attempt {attempt + 1})")
                                    return fresh_obj
                    except Exception as lookup_error:
                        logger.error(f"Fresh lookup failed (attempt {attempt + 1}): {lookup_error}")
                    
                    # Strategy 3: For Location objects, try lookup by code
                    if isinstance(obj, Location):
                        try:
                            location_code = getattr(obj, 'code', None)
                            warehouse_id = getattr(obj, 'warehouse_id', None)
                            
                            if location_code:
                                query = session.query(Location).filter(Location.code == location_code)
                                if warehouse_id:
                                    query = query.filter(Location.warehouse_id == warehouse_id)
                                
                                fresh_location = query.first()
                                if fresh_location:
                                    logger.info(f"Location lookup by code successful: {location_code}")
                                    return fresh_location
                                    
                        except Exception as location_lookup_error:
                            logger.error(f"Location lookup by code failed: {location_lookup_error}")
            
            except Exception as unexpected_error:
                logger.error(f"Unexpected session binding error: {unexpected_error}")
        
        # All recovery strategies failed
        logger.error(f"All session recovery strategies failed for object")
        return None
    
    @staticmethod  
    def ensure_locations_session_bound(locations: list, max_retries: int = 3) -> list:
        """
        Ensure a list of Location objects are all bound to current session.
        
        Args:
            locations: List of Location objects
            max_retries: Maximum recovery attempts per object
            
        Returns:
            List of session-bound Location objects (may be shorter if some fail)
        """
        if not locations:
            return []
        
        bound_locations = []
        failed_count = 0
        
        for location in locations:
            bound_location = RequestScopedSessionManager.ensure_object_session_bound(
                location, max_retries
            )
            
            if bound_location:
                bound_locations.append(bound_location)
            else:
                failed_count += 1
                logger.warning(f"Failed to bind location to session")
        
        if failed_count > 0:
            logger.warning(f"Session binding failed for {failed_count}/{len(locations)} locations")
        else:
            logger.debug(f"Successfully bound {len(bound_locations)} locations to session")
            
        return bound_locations
    
    @staticmethod
    def create_session_safe_location_cache() -> dict:
        """
        Create a location cache that's safe for web request contexts.
        
        Unlike regular caches that store object references, this returns
        a cache structure that stores only the data needed for reconstruction.
        
        Returns:
            Empty cache structure optimized for session safety
        """
        return {
            'warehouse_caches': {},  # warehouse_id -> {location_code -> location_data}
            'global_cache': {},      # location_code -> location_data  
            'cache_metadata': {
                'created_at': None,
                'request_context': RequestScopedSessionManager.is_web_request_context(),
                'total_cached': 0
            }
        }
    
    @staticmethod
    def invalidate_request_cache():
        """
        Invalidate all request-scoped caches.
        
        Should be called at the start of each web request to ensure
        fresh data and prevent cross-request cache contamination.
        """
        if RequestScopedSessionManager.is_web_request_context():
            # Store a flag in Flask's g object to track cache invalidation
            g.location_cache_invalidated = True
            logger.debug("Request-scoped location cache invalidated")

# Convenience functions for easy integration
def ensure_session_bound(obj: Any) -> Optional[Any]:
    """Convenience function to ensure object is session-bound"""
    return RequestScopedSessionManager.ensure_object_session_bound(obj)

def ensure_locations_bound(locations: list) -> list:
    """Convenience function to ensure Location list is session-bound"""
    return RequestScopedSessionManager.ensure_locations_session_bound(locations)

def is_web_request() -> bool:
    """Convenience function to check if in web request context"""
    return RequestScopedSessionManager.is_web_request_context()

def get_session():
    """Convenience function to get current session"""
    return RequestScopedSessionManager.get_current_session()

def invalidate_cache():
    """Convenience function to invalidate request cache"""
    RequestScopedSessionManager.invalidate_request_cache()