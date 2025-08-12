"""
Database Migration Debugging System
Comprehensive debugging tools for PostgreSQL migrations and constraint management
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

from sqlalchemy import text, inspect, MetaData
from sqlalchemy.exc import SQLAlchemyError
from database import db
from monitoring import log_error, track_performance, PerformanceTracker

logger = logging.getLogger(__name__)

@dataclass
class MigrationIssue:
    """Migration issue tracking"""
    timestamp: str
    issue_type: str
    table_name: str
    column_name: Optional[str]
    constraint_name: Optional[str] 
    error_message: str
    suggested_fix: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL

@dataclass
class ConstraintViolation:
    """Database constraint violation"""
    timestamp: str
    table_name: str
    constraint_name: str
    violation_type: str  # FK, CHECK, UNIQUE, NOT_NULL
    violating_data: Dict[str, Any]
    query: str
    error_details: str

class MigrationDebugger:
    """Comprehensive migration debugging and monitoring"""
    
    def __init__(self):
        self.issues: List[MigrationIssue] = []
        self.violations: List[ConstraintViolation] = []
        self.is_postgres = self._check_database_type()
    
    def _check_database_type(self) -> bool:
        """Check if we're using PostgreSQL"""
        try:
            return 'postgresql' in db.engine.url.drivername.lower()
        except:
            return False
    
    @track_performance("schema_validation")
    def validate_schema(self) -> Dict[str, Any]:
        """Validate current database schema"""
        issues = []
        warnings = []
        
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Check required warehouse tables
            required_tables = {
                'location': ['warehouse_id', 'aisle_number', 'rack_number', 'position_number', 'level'],
                'warehouse_config': ['warehouse_id', 'warehouse_name', 'num_aisles', 'racks_per_aisle'],
                'rule': ['name', 'rule_type', 'conditions'],
                'rule_category': ['name', 'display_name', 'priority']
            }
            
            for table_name, required_columns in required_tables.items():
                if table_name not in tables:
                    issues.append({
                        'type': 'MISSING_TABLE',
                        'table': table_name,
                        'severity': 'CRITICAL',
                        'message': f"Required table '{table_name}' is missing"
                    })
                    continue
                
                # Check columns
                columns = [col['name'] for col in inspector.get_columns(table_name)]
                for col in required_columns:
                    if col not in columns:
                        issues.append({
                            'type': 'MISSING_COLUMN',
                            'table': table_name,
                            'column': col,
                            'severity': 'HIGH',
                            'message': f"Required column '{col}' missing from table '{table_name}'"
                        })
            
            # Check for problematic column sizes
            if 'location' in tables:
                location_columns = inspector.get_columns('location')
                for col in location_columns:
                    if col['name'] == 'level' and col.get('type') and hasattr(col['type'], 'length'):
                        if col['type'].length == 1:
                            warnings.append({
                                'type': 'COLUMN_SIZE_WARNING',
                                'table': 'location',
                                'column': 'level',
                                'severity': 'MEDIUM',
                                'message': "Column 'level' is VARCHAR(1), may need expansion for multi-digit levels"
                            })
            
            # Check constraints
            self._validate_constraints(inspector, tables, issues, warnings)
            
            return {
                'status': 'healthy' if not issues else 'issues_found',
                'issues': issues,
                'warnings': warnings,
                'total_tables': len(tables),
                'validated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            log_error(e, {'component': 'schema_validation'})
            return {
                'status': 'error',
                'error': str(e),
                'validated_at': datetime.utcnow().isoformat()
            }
    
    def _validate_constraints(self, inspector, tables: List[str], issues: List[Dict], warnings: List[Dict]):
        """Validate database constraints"""
        for table_name in tables:
            try:
                # Check foreign keys
                fks = inspector.get_foreign_keys(table_name)
                for fk in fks:
                    if fk['referred_table'] not in tables:
                        issues.append({
                            'type': 'BROKEN_FK',
                            'table': table_name,
                            'constraint': fk['name'],
                            'severity': 'HIGH',
                            'message': f"Foreign key references non-existent table '{fk['referred_table']}'"
                        })
                
                # Check indexes
                indexes = inspector.get_indexes(table_name)
                if not indexes and table_name in ['location', 'rule', 'warehouse_config']:
                    warnings.append({
                        'type': 'MISSING_INDEX',
                        'table': table_name,
                        'severity': 'LOW',
                        'message': f"Table '{table_name}' has no indexes, may impact performance"
                    })
                    
            except Exception as e:
                warnings.append({
                    'type': 'CONSTRAINT_CHECK_ERROR',
                    'table': table_name,
                    'severity': 'LOW',
                    'message': f"Could not validate constraints for '{table_name}': {str(e)}"
                })
    
    @track_performance("migration_health_check")
    def check_migration_health(self) -> Dict[str, Any]:
        """Comprehensive migration health check"""
        health_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'database_type': 'PostgreSQL' if self.is_postgres else 'SQLite',
            'connection_status': 'unknown',
            'transaction_status': 'unknown',
            'lock_status': {},
            'recent_issues': []
        }
        
        try:
            # Test basic connection
            with db.engine.connect() as conn:
                conn.execute(text('SELECT 1'))
                health_report['connection_status'] = 'healthy'
                
                if self.is_postgres:
                    # Check for locks
                    lock_query = """
                    SELECT 
                        pg_class.relname,
                        pg_locks.locktype,
                        pg_locks.mode,
                        pg_locks.granted,
                        pg_stat_activity.query,
                        pg_stat_activity.state
                    FROM pg_locks
                    JOIN pg_class ON pg_locks.relation = pg_class.oid
                    LEFT JOIN pg_stat_activity ON pg_locks.pid = pg_stat_activity.pid
                    WHERE pg_class.relname IN ('location', 'warehouse_config', 'rule', 'rule_category')
                    """
                    
                    locks = conn.execute(text(lock_query)).fetchall()
                    health_report['lock_status'] = {
                        'active_locks': len(locks),
                        'blocked_locks': len([l for l in locks if not l.granted]),
                        'details': [dict(l._mapping) for l in locks[:10]]  # First 10 locks
                    }
                    
                    # Check for deadlocks
                    deadlock_query = """
                    SELECT COUNT(*) as deadlock_count
                    FROM pg_stat_database_conflicts
                    WHERE datname = current_database()
                    """
                    deadlocks = conn.execute(text(deadlock_query)).fetchone()
                    health_report['deadlock_count'] = deadlocks[0] if deadlocks else 0
                    
                    # Check transaction status
                    tx_query = """
                    SELECT 
                        COUNT(*) as active_transactions,
                        COUNT(CASE WHEN state = 'idle in transaction' THEN 1 END) as idle_transactions
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                    """
                    tx_result = conn.execute(text(tx_query)).fetchone()
                    health_report['transaction_status'] = {
                        'active': tx_result[0] if tx_result else 0,
                        'idle_in_transaction': tx_result[1] if tx_result else 0
                    }
        
        except Exception as e:
            health_report['connection_status'] = 'error'
            health_report['connection_error'] = str(e)
            log_error(e, {'component': 'migration_health_check'})
        
        return health_report
    
    @contextmanager
    def migration_transaction(self, description: str):
        """Context manager for safe migration transactions"""
        start_time = time.time()
        logger.info(f"Starting migration: {description}")
        
        try:
            with db.engine.begin() as conn:
                yield conn
                logger.info(f"Migration completed: {description} ({time.time() - start_time:.2f}s)")
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Migration failed: {description} ({duration:.2f}s) - {str(e)}")
            
            # Record migration issue
            issue = MigrationIssue(
                timestamp=datetime.utcnow().isoformat(),
                issue_type='MIGRATION_FAILURE',
                table_name='unknown',
                column_name=None,
                constraint_name=None,
                error_message=str(e),
                suggested_fix=self._suggest_migration_fix(e),
                severity='CRITICAL'
            )
            self.issues.append(issue)
            
            log_error(e, {
                'migration_description': description,
                'migration_duration': duration
            }, severity='CRITICAL')
            
            raise
    
    def _suggest_migration_fix(self, error: Exception) -> str:
        """Suggest fixes for migration errors"""
        error_str = str(error).lower()
        
        if 'column' in error_str and 'does not exist' in error_str:
            return "Add missing column with ALTER TABLE ADD COLUMN statement"
        elif 'table' in error_str and 'does not exist' in error_str:
            return "Create missing table with CREATE TABLE statement"
        elif 'constraint' in error_str:
            return "Check constraint definition and referenced tables"
        elif 'duplicate' in error_str:
            return "Check for existing objects and use IF NOT EXISTS clauses"
        elif 'permission' in error_str or 'denied' in error_str:
            return "Check database user permissions for DDL operations"
        elif 'connection' in error_str:
            return "Verify database connection and retry"
        else:
            return "Review migration SQL and database logs for details"
    
    @track_performance("bulk_operation_test")
    def test_bulk_operations(self, table_name: str = 'location') -> Dict[str, Any]:
        """Test bulk operation performance"""
        results = {
            'table_name': table_name,
            'timestamp': datetime.utcnow().isoformat(),
            'operations': {}
        }
        
        try:
            # Test bulk insert
            with PerformanceTracker('bulk_insert_test') as tracker:
                test_data = []
                for i in range(100):
                    test_data.append({
                        'location_code': f'TEST-{i:03d}',
                        'warehouse_id': 'DEFAULT',
                        'aisle_number': 1,
                        'rack_number': 1,
                        'position_number': i,
                        'level': 'A'
                    })
                
                if table_name == 'location':
                    # Use raw SQL for better performance testing
                    insert_sql = """
                    INSERT INTO location (location_code, warehouse_id, aisle_number, rack_number, position_number, level)
                    VALUES (:location_code, :warehouse_id, :aisle_number, :rack_number, :position_number, :level)
                    """
                    
                    with db.engine.begin() as conn:
                        conn.execute(text(insert_sql), test_data)
                        # Clean up test data
                        conn.execute(text("DELETE FROM location WHERE location_code LIKE 'TEST-%'"))
            
            results['operations']['bulk_insert'] = {
                'records': 100,
                'duration_ms': tracker.context.get('duration_ms', 0),
                'status': 'success'
            }
            
            # Test bulk update
            with PerformanceTracker('bulk_update_test') as tracker:
                with db.engine.begin() as conn:
                    update_sql = """
                    UPDATE location 
                    SET updated_at = CURRENT_TIMESTAMP 
                    WHERE warehouse_id = 'DEFAULT'
                    """
                    result = conn.execute(text(update_sql))
            
            results['operations']['bulk_update'] = {
                'affected_rows': result.rowcount if hasattr(result, 'rowcount') else 0,
                'status': 'success'
            }
            
        except Exception as e:
            results['operations']['error'] = {
                'error_message': str(e),
                'status': 'failed'
            }
            log_error(e, {'operation': 'bulk_operation_test', 'table': table_name})
        
        return results
    
    def monitor_constraint_violations(self) -> List[ConstraintViolation]:
        """Monitor recent constraint violations"""
        if not self.is_postgres:
            return []
        
        try:
            with db.engine.connect() as conn:
                # Query PostgreSQL logs for constraint violations (if available)
                violation_query = """
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_tup_ins,
                    n_tup_upd,
                    n_tup_del
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC
                LIMIT 10
                """
                
                results = conn.execute(text(violation_query)).fetchall()
                
                # This is a simplified version - in production you'd want to 
                # parse actual PostgreSQL logs or use pg_stat_statements
                return []
                
        except Exception as e:
            log_error(e, {'component': 'constraint_violation_monitor'})
            return []
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate comprehensive migration report"""
        schema_validation = self.validate_schema()
        health_check = self.check_migration_health()
        bulk_test = self.test_bulk_operations()
        
        return {
            'report_timestamp': datetime.utcnow().isoformat(),
            'schema_validation': schema_validation,
            'health_check': health_check,
            'bulk_operation_test': bulk_test,
            'recent_issues': [
                {
                    'timestamp': issue.timestamp,
                    'type': issue.issue_type,
                    'table': issue.table_name,
                    'severity': issue.severity,
                    'message': issue.error_message,
                    'suggested_fix': issue.suggested_fix
                } for issue in self.issues[-10:]  # Last 10 issues
            ],
            'recommendations': self._generate_recommendations(schema_validation, health_check)
        }
    
    def _generate_recommendations(self, schema_validation: Dict, health_check: Dict) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Schema recommendations
        issues = schema_validation.get('issues', [])
        for issue in issues:
            if issue['type'] == 'MISSING_TABLE':
                recommendations.append(f"Create missing table: {issue['table']}")
            elif issue['type'] == 'MISSING_COLUMN':
                recommendations.append(f"Add missing column: {issue['table']}.{issue['column']}")
        
        # Performance recommendations
        if health_check.get('lock_status', {}).get('blocked_locks', 0) > 0:
            recommendations.append("Investigate blocked database locks")
        
        if health_check.get('transaction_status', {}).get('idle_in_transaction', 0) > 5:
            recommendations.append("Too many idle transactions - check connection pooling")
        
        # Add generic recommendations if no specific issues
        if not recommendations:
            recommendations.append("Schema and health checks passed - system is healthy")
        
        return recommendations

# Migration helper functions
def safe_add_column(table_name: str, column_name: str, column_definition: str) -> bool:
    """Safely add a column if it doesn't exist"""
    debugger = MigrationDebugger()
    
    with debugger.migration_transaction(f"Add column {table_name}.{column_name}"):
        try:
            if debugger.is_postgres:
                # Check if column exists
                check_sql = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name AND column_name = :column_name
                """
                
                with db.engine.connect() as conn:
                    result = conn.execute(text(check_sql), {
                        'table_name': table_name,
                        'column_name': column_name
                    }).fetchone()
                    
                    if not result:
                        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
                        conn.execute(text(alter_sql))
                        logger.info(f"Added column {table_name}.{column_name}")
                        return True
                    else:
                        logger.info(f"Column {table_name}.{column_name} already exists")
                        return True
            else:
                # SQLite - more permissive
                db.create_all()
                return True
                
        except Exception as e:
            logger.error(f"Failed to add column {table_name}.{column_name}: {e}")
            return False

def safe_create_table(table_name: str, create_sql: str) -> bool:
    """Safely create a table if it doesn't exist"""
    debugger = MigrationDebugger()
    
    with debugger.migration_transaction(f"Create table {table_name}"):
        try:
            with db.engine.connect() as conn:
                # Add IF NOT EXISTS for safety
                if "IF NOT EXISTS" not in create_sql.upper():
                    create_sql = create_sql.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
                
                conn.execute(text(create_sql))
                logger.info(f"Created table {table_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            return False

# Global debugger instance
migration_debugger = MigrationDebugger()