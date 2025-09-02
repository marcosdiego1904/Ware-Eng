"""
Debug Format Detection Endpoint

This creates a simple test endpoint that bypasses authentication and database operations
to test if the Smart Configuration format detection works in production.
"""

from flask import Blueprint, jsonify, request
from smart_format_detector import SmartFormatDetector
import logging

logger = logging.getLogger(__name__)

# Create debug blueprint
debug_format_bp = Blueprint('debug_format', __name__, url_prefix='/api/debug')


@debug_format_bp.route('/test-format-detection', methods=['POST'])
def test_format_detection():
    """
    Simple format detection test without authentication or database
    
    POST /api/debug/test-format-detection
    {
        "examples": ["010A", "325B", "245D"]
    }
    """
    try:
        data = request.get_json()
        if not data or 'examples' not in data:
            return jsonify({
                'error': 'Missing examples field',
                'usage': 'POST with JSON: {"examples": ["010A", "325B", "245D"]}'
            }), 400
        
        examples = data['examples']
        if not isinstance(examples, list) or len(examples) == 0:
            return jsonify({
                'error': 'Examples must be a non-empty list'
            }), 400
        
        logger.info(f"Testing format detection with {len(examples)} examples")
        
        # Test format detection without any database operations
        detector = SmartFormatDetector()
        result = detector.detect_format(examples)
        
        # Add debug information
        debug_info = {
            'input_examples': examples,
            'analyzer_count': len(detector.analyzers),
            'analyzer_types': [analyzer.__class__.__name__ for analyzer in detector.analyzers]
        }
        
        response = {
            'success': True,
            'detection_result': result,
            'debug_info': debug_info,
            'message': 'Format detection test completed successfully'
        }
        
        logger.info(f"Format detection test successful: {result.get('detected_pattern', {}).get('pattern_type', 'None')}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Format detection test failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Format detection test failed'
        }), 500


@debug_format_bp.route('/test-database-connection', methods=['GET'])
def test_database_connection():
    """
    Test database connectivity for Smart Configuration tables
    
    GET /api/debug/test-database-connection
    """
    try:
        from database import db
        from models import WarehouseTemplate, LocationFormatHistory
        
        tests = []
        
        # Test 1: Basic database connection
        try:
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1"))
                row = result.fetchone()
            tests.append({
                'test': 'Basic database connection',
                'status': 'PASS',
                'result': f'Connected successfully, test query returned: {row[0]}'
            })
        except Exception as e:
            tests.append({
                'test': 'Basic database connection',
                'status': 'FAIL',
                'error': str(e)
            })
        
        # Test 2: WarehouseTemplate table access
        try:
            template_count = WarehouseTemplate.query.count()
            tests.append({
                'test': 'WarehouseTemplate table access',
                'status': 'PASS',
                'result': f'Found {template_count} templates'
            })
        except Exception as e:
            tests.append({
                'test': 'WarehouseTemplate table access',
                'status': 'FAIL',
                'error': str(e)
            })
        
        # Test 3: Smart Configuration columns
        try:
            db_type = db.engine.dialect.name.lower()
            if db_type == 'postgresql':
                check_sql = """
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'warehouse_template' 
                    AND column_name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                """
            else:
                check_sql = """
                    SELECT name, type 
                    FROM pragma_table_info('warehouse_template')
                    WHERE name IN ('location_format_config', 'format_confidence', 'format_examples', 'format_learned_date')
                """
            
            with db.engine.connect() as connection:
                result = connection.execute(db.text(check_sql))
                columns = result.fetchall()
            
            tests.append({
                'test': 'Smart Configuration columns',
                'status': 'PASS' if len(columns) >= 4 else 'PARTIAL',
                'result': f'Found {len(columns)}/4 columns: {[col[0] for col in columns]}'
            })
        except Exception as e:
            tests.append({
                'test': 'Smart Configuration columns',
                'status': 'FAIL',
                'error': str(e)
            })
        
        # Test 4: LocationFormatHistory table
        try:
            history_count = LocationFormatHistory.query.count()
            tests.append({
                'test': 'LocationFormatHistory table access',
                'status': 'PASS',
                'result': f'Found {history_count} format history records'
            })
        except Exception as e:
            tests.append({
                'test': 'LocationFormatHistory table access',
                'status': 'FAIL',
                'error': str(e)
            })
        
        # Summary
        passed = sum(1 for test in tests if test['status'] == 'PASS')
        failed = sum(1 for test in tests if test['status'] == 'FAIL')
        
        return jsonify({
            'database_type': db.engine.dialect.name.lower(),
            'database_url': str(db.engine.url).split('@')[0] + '@[HIDDEN]',
            'summary': {
                'total_tests': len(tests),
                'passed': passed,
                'failed': failed,
                'status': 'HEALTHY' if failed == 0 else 'ISSUES' if passed > 0 else 'CRITICAL'
            },
            'tests': tests
        }), 200
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Database connection test failed'
        }), 500


# Register the blueprint (add this to your main app)
def register_debug_format_blueprint(app):
    """Register the debug format blueprint with the Flask app"""
    app.register_blueprint(debug_format_bp)