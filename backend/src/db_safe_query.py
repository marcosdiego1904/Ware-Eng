"""
Database Safe Query Helper - Smart Configuration Hotfix

Provides safe database query methods that don't fail when tables/columns don't exist yet.
This is part of the Smart Configuration hotfix for production compatibility.
"""

from sqlalchemy.exc import OperationalError, ProgrammingError
import logging

logger = logging.getLogger(__name__)


def safe_table_exists(db_engine, table_name):
    """
    Check if a table exists in the database
    
    Args:
        db_engine: SQLAlchemy engine
        table_name: Name of table to check
        
    Returns:
        bool: True if table exists, False otherwise
    """
    try:
        from sqlalchemy import text
        
        # Get database type
        db_type = db_engine.dialect.name.lower()
        
        if db_type == 'postgresql':
            query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = :table_name
                );
            """)
        else:  # SQLite
            query = text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=:table_name;
            """)
        
        with db_engine.connect() as connection:
            result = connection.execute(query, {"table_name": table_name})
            
            if db_type == 'postgresql':
                return result.fetchone()[0]
            else:
                return result.fetchone() is not None
                
    except Exception as e:
        logger.warning(f"Error checking if table {table_name} exists: {e}")
        return False


def safe_query_location_format_history(query_func, default_return=None):
    """
    Safely execute a LocationFormatHistory query with fallback
    
    Args:
        query_func: Function that performs the query
        default_return: Value to return if query fails
        
    Returns:
        Query result or default_return if table doesn't exist
    """
    try:
        return query_func()
    except (OperationalError, ProgrammingError) as e:
        # Table doesn't exist yet (expected in production before migration)
        if 'no such table' in str(e).lower() or 'does not exist' in str(e).lower():
            logger.info("LocationFormatHistory table not available - using fallback")
            return default_return or []
        else:
            # Re-raise unexpected errors
            raise
    except Exception as e:
        logger.error(f"Unexpected error in safe query: {e}")
        return default_return or []


def safe_count_location_format_history():
    """
    Safely get count of LocationFormatHistory records
    
    Returns:
        int: Count of records, or 0 if table doesn't exist
    """
    def query_func():
        from models import LocationFormatHistory
        return LocationFormatHistory.query.count()
    
    return safe_query_location_format_history(query_func, 0)


def safe_get_pending_evolutions(user_id):
    """
    Safely get pending format evolutions for a user
    
    Args:
        user_id: User ID to get evolutions for
        
    Returns:
        list: List of pending evolutions, or empty list if table doesn't exist
    """
    def query_func():
        from models import LocationFormatHistory, WarehouseTemplate
        
        return LocationFormatHistory.query.join(WarehouseTemplate).filter(
            WarehouseTemplate.created_by == user_id,
            LocationFormatHistory.user_confirmed == False,
            LocationFormatHistory.reviewed_at.is_(None)
        ).all()
    
    return safe_query_location_format_history(query_func, [])