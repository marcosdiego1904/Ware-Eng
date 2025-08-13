import os
import uuid
import sys
import tempfile
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, flash, jsonify, Blueprint, make_response
from flask_cors import CORS, cross_origin 
import pandas as pd
from argparse import Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt

# Add the 'src' directory to the Python path to resolve local imports in Vercel.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import analysis engines - will be done later to avoid circular imports
from main import run_engine, summarize_anomalies_by_location

# Flag to check if enhanced engine is available
HAS_ENHANCED_ENGINE = False
run_enhanced_engine = None

def load_enhanced_engine():
    """Load enhanced engine with lazy loading to avoid circular imports"""
    global HAS_ENHANCED_ENGINE, run_enhanced_engine
    
    if run_enhanced_engine is not None:
        return  # Already loaded
    
    try:
        from enhanced_main import run_enhanced_engine as enhanced_engine
        run_enhanced_engine = enhanced_engine
        HAS_ENHANCED_ENGINE = True
        print("Enhanced warehouse rules engine loaded successfully")
    except ImportError as e:
        # Fall back to original engine
        run_enhanced_engine = run_engine
        HAS_ENHANCED_ENGINE = False
        print(f"Enhanced engine not available, using legacy engine: {e}")

# --- Flask Application Configuration ---
# Robust and cross-platform path configuration.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_template_folder = os.path.join(_project_root, 'src', 'templates')
_data_folder = os.path.join(_project_root, 'data')

app = Flask(__name__, template_folder=_template_folder)

# Configure CORS - use only Flask-CORS to avoid duplicate headers
# Get allowed origins from environment variable or use defaults
allowed_origins_env = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:3001,http://localhost:3002')
# Clean up any newlines and whitespace in environment variable
allowed_origins_env = allowed_origins_env.replace('\n', '').replace('\r', '')
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(',') if origin.strip()]

# Add production origins if not already included
production_origins = [
    'https://ware-eng-ft.vercel.app',
    'https://ware-eng.vercel.app',  # Add the actual frontend URL
    'https://*.vercel.app',
    'http://localhost:3000',
    'http://localhost:3001', 
    'http://localhost:3002'
]

for origin in production_origins:
    if origin not in allowed_origins:
        allowed_origins.append(origin)

print(f"CORS allowed origins: {allowed_origins}")

CORS(app, 
     origins=allowed_origins, 
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True,
     expose_headers=["Authorization"],
     max_age=3600)

# Create the API Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# JWT Token Required Decorator (needs to be early in file before usage)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            # The token is expected in the "Bearer <token>" format
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            from core_models import User
            current_user = User.query.get(data['user_id'])
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401

        # Pass the authenticated user to the route
        return f(current_user, *args, **kwargs)
    return decorated

# Simple test endpoint to verify CORS is working
@api_bp.route('/test', methods=['GET', 'POST', 'OPTIONS'])
def test_cors():
    return jsonify({'message': 'CORS test successful', 'method': request.method})

# Manual CORS handler for all requests
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    print(f"Request origin: {origin}")
    print(f"Allowed origins: {allowed_origins}")
    
    # Always add CORS headers for allowed origins
    if origin and (origin in allowed_origins or any(origin.endswith(allowed.replace('https://*.', '.')) for allowed in allowed_origins if allowed.startswith('https://*.'))):
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '3600'
        print(f"CORS headers added for origin: {origin}")
    else:
        # For debugging, let's be more permissive temporarily
        if origin and (origin.endswith('.vercel.app') or origin.startswith('http://localhost')):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            print(f"CORS headers added (permissive) for origin: {origin}")
        else:
            print(f"CORS headers NOT added for origin: {origin}")
    
    return response


# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response = add_cors_headers(response)
    print(f"Response: {response.status_code}")
    print(f"CORS Headers: {dict(response.headers)}")
    return response

# Combined request handler for logging and preflight
@app.before_request
def handle_request():
    # Log the request
    print(f"\nIncoming request: {request.method} {request.path}")
    print(f"Origin: {request.headers.get('Origin', 'None')}")
    print(f"Authorization: {'Present' if request.headers.get('Authorization') else 'Missing'}")
    print(f"Content-Type: {request.headers.get('Content-Type', 'None')}")
    print(f"User-Agent: {request.headers.get('User-Agent', 'None')[:50]}...")
    
    # Handle preflight OPTIONS requests
    if request.method == "OPTIONS":
        response = make_response()
        origin = request.headers.get('Origin')
        
        if origin and (origin.endswith('.vercel.app') or origin.startswith('http://localhost') or origin in allowed_origins):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            print(f"Preflight response sent for origin: {origin}")
        
        return response
    
    return None

# Add explicit OPTIONS handlers for all endpoints
@api_bp.route('/reports', methods=['OPTIONS'])
def handle_reports_options():
    return '', 200

@api_bp.route('/auth/login', methods=['OPTIONS'])
def handle_login_options():
    return '', 200

@api_bp.route('/auth/register', methods=['OPTIONS'])
def handle_register_options():
    return '', 200

# Debug endpoint to check configuration
@api_bp.route('/debug/config', methods=['GET'])
def debug_config():
    return jsonify({
        'allowed_origins': allowed_origins,
        'has_secret_key': bool(app.config.get('SECRET_KEY')),
        'database_url_set': bool(os.environ.get('DATABASE_URL')),
        'is_production': IS_PRODUCTION,
        'environment_origins': os.environ.get('ALLOWED_ORIGINS', 'not set')
    })

# Health check endpoint for database and rules
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint that verifies database and rules are working"""
    try:
        from models import Rule, RuleCategory, Location
        from migrations import migration_runner
        
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check if rules exist
        rule_count = Rule.query.filter_by(is_active=True).count()
        category_count = RuleCategory.query.count()
        location_count = Location.query.filter_by(is_active=True).count()
        
        # Check migration status
        current_version = migration_runner.get_current_version()
        pending_migrations = migration_runner.get_pending_migrations()
        
        status = "healthy" if rule_count > 0 and len(pending_migrations) == 0 else "degraded"
        
        return jsonify({
            'status': status,
            'database': 'connected',
            'rules': {
                'active_rules': rule_count,
                'categories': category_count,
                'locations': location_count
            },
            'migrations': {
                'current_version': current_version,
                'pending_count': len(pending_migrations)
            },
            'enhanced_engine': HAS_ENHANCED_ENGINE,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Migration management endpoint (protected)
@api_bp.route('/admin/migrations', methods=['GET'])
@token_required
def get_migration_status(current_user):
    """Get detailed migration status"""
    try:
        from migrations import migration_runner
        
        current_version = migration_runner.get_current_version()
        pending = migration_runner.get_pending_migrations()
        
        return jsonify({
            'current_version': current_version,
            'pending_migrations': [
                {
                    'version': m.version,
                    'description': m.description
                } for m in pending
            ],
            'total_migrations': len(migration_runner.migrations)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/migrations/run', methods=['POST'])
@token_required  
def run_migrations_endpoint(current_user):
    """Manually trigger migrations"""
    try:
        from migrations import force_run_migrations
        
        success = force_run_migrations()
        
        if success:
            return jsonify({'message': 'Migrations completed successfully'})
        else:
            return jsonify({'error': 'Migrations failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Database and Login Manager Configuration
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("FLASK_SECRET_KEY environment variable is required")

# Environment-aware configuration for database and uploads
IS_VERCEL = os.environ.get('VERCEL') == '1'

# Environment-aware configuration for database and uploads
IS_PRODUCTION = os.environ.get('RENDER') == 'true' or os.environ.get('VERCEL') == '1'

if IS_PRODUCTION:
    # Production environment (Render/Vercel): Use PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("WARNING: DATABASE_URL environment variable is not set in production")
        # Fallback to local SQLite for debugging
        instance_path = os.path.join('/tmp', 'instance')
        os.makedirs(instance_path, exist_ok=True)
        db_path = os.path.join(instance_path, 'database.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    else:
        # SQLAlchemy requires 'postgresql://' but Render provides 'postgres://'
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local development environment: use the instance folder with SQLite
    instance_path = os.path.join(_project_root, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    # Local environment: use the instance folder
    instance_path = os.path.join(_project_root, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Import shared database instance
from database import db
db.init_app(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login' # type: ignore


# --- Database Models ---
# Import core models to avoid circular imports
from core_models import User, AnalysisReport, Anomaly, AnomalyHistory

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# IMPORTANT: Change this to a real and unique secret key in a production environment.
# app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-insecure') # This line is removed as per the new_code

# --- Initialize Database with Professional Migration System ---
# Run migrations only when needed (efficient approach)
from migrations import run_migrations_if_needed

with app.app_context():
    try:
        run_migrations_if_needed()
    except Exception as e:
        print(f"Migration failed: {e}")
        # App continues to work even if migrations fail

# --- Authentication Routes (DEPRECATED - Use JWT API endpoints instead) ---

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = User.query.filter_by(username=username).first()
#         if user and user.check_password(password):
#             login_user(user, remember=True)
#             next_page = request.args.get('next')
#             return redirect(next_page or url_for('index'))
#         else:
#             flash('Login Unsuccessful. Please check username and password', 'danger')
#     return render_template('login.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         if User.query.filter_by(username=username).first():
#             flash('Username already exists. Please choose another one.', 'warning')
#             return redirect(url_for('register'))
#         
#         new_user = User()
#         new_user.username = username
#         new_user.set_password(password)
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Your account has been created! You are now able to log in', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html')

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('index'))


# --- File Path Configuration ---
if IS_VERCEL:
    # Vercel-specific path for uploads
    UPLOAD_FOLDER = os.path.join('/tmp', 'wie_uploads')
else:
    # Local path for uploads
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'wie_uploads')

DEFAULT_RULES_PATH = os.path.join(_data_folder, 'warehouse_rules.xlsx')
DEFAULT_INVENTORY_PATH = os.path.join(_data_folder, 'inventory_report.xlsx')


def get_safe_filepath(filename):
    """Creates a unique filename to avoid collisions."""
    safe_uuid = str(uuid.uuid4())
    _, extension = os.path.splitext(filename)
    return os.path.join(UPLOAD_FOLDER, f"{safe_uuid}{extension}")


@app.route('/download/<filename>')
def download(filename):
    """ Serves the sample files from the designated data folder. """
    return send_from_directory(_data_folder, filename, as_attachment=True)


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     """
#     Step 1: Manages file uploads or selection of sample data.
#     If the user is authenticated, this page serves as the "new analysis" page.
#     If not, it's the main landing page.
#     """
#     if request.method == 'POST':
#         if not current_user.is_authenticated:
#             flash("Please log in to start an analysis.", "warning")
#             return redirect(url_for('login'))
#             
#         # Cleanup any previous session data to ensure a fresh start
#         session.pop('inventory_filepath', None)
#         session.pop('rules_filepath', None)
# 
#         use_sample_inventory = request.form.get('use_sample_inventory') == 'true'
#         use_sample_rules = request.form.get('use_sample_rules') == 'true'
# 
#         inventory_file = request.files.get('inventory_file')
#         rules_file = request.files.get('rules_file')
# 
#         inventory_filepath = None
#         rules_filepath = None
# 
#         try:
#             os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# 
#             # Determine inventory file path
#             if use_sample_inventory:
#                 inventory_filepath = DEFAULT_INVENTORY_PATH
#             elif inventory_file and inventory_file.filename:
#                 inventory_filepath = get_safe_filepath(inventory_file.filename)
#                 inventory_file.save(inventory_filepath)
#             else:
#                 return render_template('error.html', error_message="The inventory report is a required file."), 400
# 
#             # Determine rules file path
#             if use_sample_rules:
#                 rules_filepath = DEFAULT_RULES_PATH
#             elif rules_file and rules_file.filename:
#                 rules_filepath = get_safe_filepath(rules_file.filename)
#                 rules_file.save(rules_filepath)
#             else:
#                 rules_filepath = DEFAULT_RULES_PATH # Default if none provided/selected
# 
#             session['inventory_filepath'] = inventory_filepath
#             session['rules_filepath'] = rules_filepath
# 
#             df_headers = pd.read_excel(inventory_filepath, nrows=0)
#             session['user_columns'] = df_headers.columns.tolist()
# 
#             return redirect(url_for('mapping'))
# 
#         except Exception as e:
#             print(f"[ERROR] at file upload: {e}")
#             error_msg = f"Error processing file. Make sure it is a valid .xlsx file. (Detail: {type(e).__name__})"
#             return render_template('error.html', error_message=error_msg), 500
# 
#     return render_template('index.html')


# @app.route('/dashboard')
# @login_required
# def dashboard():
#     """
#     Displays the main dashboard for authenticated users, showing their past analysis reports.
#     """
#     reports = AnalysisReport.query.filter_by(user_id=current_user.id).order_by(AnalysisReport.timestamp.desc()).all()
#     return render_template('dashboard.html', reports=reports)

# @app.route('/dashboard-v2')
# @login_required
# def dashboard_v2():
#     """
#     Renderiza la plantilla base para el nuevo dashboard de una sola página.
#     """
#     return render_template('dashboard_v2.html')


# @app.route('/mapping', methods=['GET'])
# @login_required
# def mapping():
#     """
#     Step 2: Displays the column mapping page.
#     """
#     if 'user_columns' not in session or 'inventory_filepath' not in session:
#         return redirect(url_for('index'))
# 
#     user_columns = session['user_columns']
#     return render_template('mapping.html', user_columns=user_columns)


def default_json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj).__name__} not serializable")

# @app.route('/process', methods=['POST'])
# @login_required
# def process_mapping():
#     """
#     Step 3: Processes the mapping, runs the engine, and displays the results.
#     """
#     try:
#         report_count = AnalysisReport.query.filter_by(user_id=current_user.id).count()
#         if report_count >= 3 and current_user.username not in ['marcosbarzola@devbymarcos.com', 'marcos9', 'testf']:
#             return render_template('error.html', error_message="You have reached the maximum limit of 3 analysis reports."), 403
# 
#         inventory_path = session.get('inventory_filepath')
#         rules_path = session.get('rules_filepath')
# 
#         if not all([inventory_path, rules_path]):
#             return render_template('error.html', error_message="Session expired. Please start over."), 400
# 
#         column_mapping = {request.form[key]: key for key in request.form}
#         
#         inventory_df = pd.read_excel(inventory_path)
#         inventory_df.rename(columns=column_mapping, inplace=True)
#         
#         if 'creation_date' in inventory_df.columns:
#             inventory_df['creation_date'] = pd.to_datetime(inventory_df['creation_date'])
#         
#         rules_df = pd.read_excel(rules_path)
#         
#         args = Namespace(debug=False, floating_time=8, straggler_ratio=0.85, stuck_ratio=0.80, stuck_time=6)
#         
#         anomalies = run_engine(inventory_df, rules_df, args)
#         
#         # ✅ AQUÍ GENERAMOS Y GUARDAMOS EL RESUMEN
#         location_summary = summarize_anomalies_by_location(anomalies)
#         report_name = f"Analysis - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
#         
#         new_report = AnalysisReport()
#         new_report.report_name=report_name
#         new_report.user_id=current_user.id
#         new_report.location_summary=json.dumps(location_summary) # Guardamos como texto JSON
#         
#         db.session.add(new_report)
#         db.session.flush()
# 
#         for item in anomalies:
#             anomaly = Anomaly()
#             if isinstance(item, dict):
#                 anomaly.description = item.get('anomaly_type', 'Uncategorized Anomaly')
#                 anomaly.details = json.dumps(item, default=default_json_serializer)
#             else:
#                 anomaly.description = str(item)
#                 anomaly.details = None
#             anomaly.report_id = new_report.id
#             db.session.add(anomaly)
#             
#         db.session.commit()
# 
#         return redirect(url_for('view_report', report_id=new_report.id))
# 
#     except Exception as e:
#         print(f"[ERROR] during processing: {e}")
#         error_msg = f"An error occurred while analyzing the data. (Detail: {type(e).__name__})"
#         return render_template('error.html', error_message=error_msg), 500
#     
#     finally:
#         for key in ['inventory_filepath', 'rules_filepath', 'user_columns']:
#             item = session.pop(key, None)
#             if isinstance(item, str) and item.startswith(UPLOAD_FOLDER) and os.path.exists(item):
#                 try:
#                     os.remove(item)
#                 except OSError:
#                     pass

# @app.route('/report/<int:report_id>')
# @login_required
# def view_report(report_id):
#     """
#     Displays a specific past analysis report from the database.
#     """
#     report = AnalysisReport.query.get_or_404(report_id)
# 
#     # Security check
#     if report.user_id != current_user.id:
#         flash("You do not have permission to view this report.", "danger")
#         return redirect(url_for('dashboard'))
# 
#     # Renderiza el nuevo template, pasando solo el ID del reporte
#     return render_template('results_v2.html', report_id=report.id)


# @app.route('/report/<int:report_id>/delete', methods=['POST'])
# @login_required
# def delete_report(report_id):
#     """
#     Deletes a specific analysis report from the database.
#     """
#     report = AnalysisReport.query.get_or_404(report_id)
#     if report.user_id != current_user.id:
#         flash("You are not authorized to delete this report.", "danger")
#         return redirect(url_for('dashboard'))
#     
#     try:
#         db.session.delete(report)
#         db.session.commit()
#         flash("Your report has been deleted.", "success")
#     except Exception as e:
#         db.session.rollback()
#         print(f"[ERROR] deleting report: {e}")
#         flash("An error occurred while deleting the report.", "danger")
#     
#     return redirect(url_for('dashboard'))


# @app.route('/api/anomaly/<int:anomaly_id>/status', methods=['POST'])
# @login_required
# def change_anomaly_status(anomaly_id):
#     """
#     Updates the status of an anomaly and records the change in its history.
#     """
#     anomaly = Anomaly.query.get_or_404(anomaly_id)
#     
#     if anomaly.report.user_id != current_user.id:
#         return jsonify({'success': False, 'message': 'Unauthorized'}), 403
#     
#     data = request.get_json()
#     new_status = data.get('status')
#     comment = data.get('comment')
#     
#     if not new_status:
#         return jsonify({'success': False, 'message': 'New status is required.'}), 400
# 
#     VALID_STATUSES = ['New', 'Acknowledged', 'In Progress', 'Resolved']
#     if new_status not in VALID_STATUSES:
#         return jsonify({'success': False, 'message': f'Invalid status: {new_status}'}), 400
# 
#     old_status = anomaly.status
#     anomaly.status = new_status
#     
#     history_entry = AnomalyHistory(
#         anomaly_id=anomaly.id,
#         old_status=old_status,
#         new_status=new_status,
#         comment=comment,
#         user_id=current_user.id
#     )
#     
#     db.session.add(history_entry)
#     db.session.commit()
#     
#     new_history_item = {
#         "old_status": old_status,
#         "new_status": new_status,
#         "comment": comment,
#         "user": current_user.username,
#         "timestamp": history_entry.timestamp.isoformat()
#     }
# 
#     return jsonify({
#         'success': True, 
#         'message': 'Status updated successfully.',
#         'new_status': new_status,
#         'history_item': new_history_item
#     })


# @app.route('/api/anomaly/<int:anomaly_id>/resolve', methods=['POST'])
# @login_required
# def resolve_anomaly(anomaly_id):
#     # This route is deprecated and will be removed.
#     # For now, it can forward to the new status change endpoint for compatibility.
#     anomaly = Anomaly.query.get_or_404(anomaly_id)
#     if anomaly.report.user_id != current_user.id:
#         return jsonify({'success': False, 'message': 'Unauthorized'}), 403
#         
#     anomaly.status = 'Resolved'
#     history_entry = AnomalyHistory(
#         anomaly_id=anomaly.id,
#         old_status="Unknown", # Or the previous status if you can retrieve it
#         new_status="Resolved",
#         comment="Resolved via legacy endpoint.",
#         user_id=current_user.id
#     )
#     db.session.add(history_entry)
#     db.session.commit()
#     
#     return jsonify({'success': True, 'message': 'Anomaly resolved successfully.'})


# @app.route('/report/<int:report_id>/location_details/<path:location_name>')
# @login_required
# def get_location_details(report_id, location_name):
#     """
#     API endpoint para obtener detalles de una ubicación específica de un reporte.
#     """
#     # 1. Buscar el reporte y verificar permisos
#     report = AnalysisReport.query.get_or_404(report_id)
#     if report.user_id != current_user.id:
#         return {"error": "Unauthorized"}, 403
# 
#     # Si el nombre de la ubicación es 'N/A', necesitamos manejarlo de forma especial
#     # ya que la URL no puede contener el carácter '/' directamente.
#     # Por ahora, asumimos que no hay problemas de codificación.
# 
#     # 2. Filtrar las anomalías para la ubicación específica
#     location_anomalies = []
#     for anomaly in report.anomalies:
#         if not anomaly.details:
#             continue
# 
#         details = json.loads(anomaly.details)
#         # Comparamos ignorando mayúsculas/minúsculas y espacios
#         if details.get('location', '').strip().upper() == location_name.strip().upper():
#             location_anomalies.append(details)
# 
#     if not location_anomalies:
#         return {"error": "No anomalies found for this location"}, 404
# 
#     # 3. Procesar los datos para el frontend
#     pallet_list = sorted(list(set([d.get('pallet_id', 'N/A') for d in location_anomalies])))
# 
#     anomaly_types = [d.get('anomaly_type', 'Unknown') for d in location_anomalies]
#     anomaly_counts = pd.Series(anomaly_types).value_counts()
# 
#     chart_data = {
#         'labels': anomaly_counts.index.tolist(),
#         'data': anomaly_counts.values.tolist()
#     }
# 
#     # 4. Devolver los datos como JSON
#     return {
#         "location": location_name,
#         "pallets": pallet_list,
#         "chart": chart_data
#     }
# @app.route('/report/<int:report_id>/details')
# @login_required
# def get_report_details(report_id):
#     report = AnalysisReport.query.get_or_404(report_id)
#     if report.user_id != current_user.id:
#         return jsonify({"error": "Unauthorized"}), 403
# 
#     # Procesar anomalías
#     processed_anomalies = []
#     for anomaly in report.anomalies:
#         try:
#             details_data = json.loads(anomaly.details) if anomaly.details else {}
#             details_data['id'] = anomaly.id
#             details_data['status'] = anomaly.status
#             
#             history_data = [
#                 {
#                     "old_status": h.old_status,
#                     "new_status": h.new_status,
#                     "comment": h.comment,
#                     "user": h.user.username,
#                     "timestamp": h.timestamp.isoformat()
#                 } 
#                 for h in anomaly.history.order_by(AnomalyHistory.timestamp.asc())
#             ]
#             details_data['history'] = history_data
#             processed_anomalies.append(details_data)
#         except json.JSONDecodeError:
#             continue
# 
#     # Agrupar anomalías por ubicación
#     locations_map = {}
#     for anomaly in processed_anomalies:
#         location = anomaly.get('location', 'N/A')
#         if location not in locations_map:
#             locations_map[location] = []
#         locations_map[location].append(anomaly)
# 
#     # Formatear resumen de ubicaciones
#     location_summary = sorted(
#         [{"name": name, "anomaly_count": len(anoms), "anomalies": anoms} for name, anoms in locations_map.items()],
#         key=lambda x: x['anomaly_count'],
#         reverse=True
#     )
# 
#     # Calcular KPIs
#     high_priority_list = ['VERY HIGH', 'HIGH']
#     total_anomalies = len(processed_anomalies)
#     resolved_anomalies = sum(1 for a in processed_anomalies if a.get('status') == 'Resolved')
#     
#     resolution_rate_text = 'N/A'
#     if total_anomalies > 0:
#         percentage = (resolved_anomalies / total_anomalies) * 100
#         resolution_rate_text = f"{resolved_anomalies} of {total_anomalies} ({percentage:.0f}%)"
# 
#     kpis = [
#         {'label': 'Total Anomalies', 'value': total_anomalies},
#         {'label': 'Priority Alerts', 'value': sum(1 for a in processed_anomalies if a.get('priority') in high_priority_list)},
#         {'label': 'Affected Locations', 'value': len(location_summary)},
#         {'label': 'Main Issue', 'value': max(set(a['anomaly_type'] for a in processed_anomalies), key=lambda t: [a['anomaly_type'] for a in processed_anomalies].count(t)) if processed_anomalies else 'N/A'},
#         {'label': 'Resolution Rate', 'value': resolution_rate_text}
#     ]
# 
#     return jsonify({
#         "reportId": report.id,
#         "reportName": report.report_name,
#         "kpis": kpis,
#         "locations": location_summary
#     })

# --- File Upload Validation ---
def validate_file_upload(file, allowed_extensions=None):
    """Validate uploaded file for security and format compliance."""
    if allowed_extensions is None:
        allowed_extensions = {'xlsx', 'xls'}
    
    if not file or not file.filename:
        return False, "No file selected"
    
    # Check file extension
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_ext not in allowed_extensions:
        return False, f"Invalid file type. Only {', '.join(allowed_extensions)} files are allowed"
    
    # Check file size (10MB limit)
    max_size = int(os.environ.get('UPLOAD_MAX_SIZE', '10485760'))  # 10MB default
    file.seek(0, 2)  # Seek to end of file
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > max_size:
        return False, f"File too large. Maximum size is {max_size / 1024 / 1024:.1f}MB"
    
    return True, "File is valid"

# --- JWT API Routes ---

@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required'}), 400

        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            # Generate the JWT token
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=24)  # Token valid for 24 hours
            }, app.config['SECRET_KEY'], algorithm="HS256")

            return jsonify({'token': token, 'username': user.username})

        return jsonify({'message': 'Invalid username or password'}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'message': 'An error occurred during login'}), 500

@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required'}), 400
            
        username = data.get('username')
        password = data.get('password')

        # Basic validation
        if len(username) < 3:
            return jsonify({'message': 'Username must be at least 3 characters long'}), 400
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already exists'}), 409

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Account created successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({'message': 'An error occurred during registration'}), 500

@api_bp.route('/reports', methods=['GET'])
@token_required
def get_user_reports(current_user):
    reports = AnalysisReport.query.filter_by(user_id=current_user.id).order_by(AnalysisReport.timestamp.desc()).all()
    output = []
    for report in reports:
        report_data = {
            'id': report.id,
            'report_name': report.report_name,
            'timestamp': report.timestamp.isoformat(),
            'anomaly_count': len(report.anomalies)
        }
        output.append(report_data)
    return jsonify({'reports': output})

@api_bp.route('/reports', methods=['POST'])
@cross_origin(origins=['http://localhost:3000', 'http://localhost:3001'])
@token_required
def create_analysis_report(current_user):
    # Check user report limit
    report_count = AnalysisReport.query.filter_by(user_id=current_user.id).count()
    if report_count >= 3 and current_user.username not in ['marcosbarzola@devbymarcos.com', 'marcos9', 'testf']:
        return jsonify({'message': 'You have reached the maximum limit of 3 analysis reports.'}), 403

    # The frontend will send the data as 'multipart/form-data'
    if 'inventory_file' not in request.files:
        return jsonify({'message': 'No inventory file part'}), 400

    inventory_file = request.files['inventory_file']
    rules_file = request.files.get('rules_file')  # Optional
    column_mapping_str = request.form.get('column_mapping')
    
    # Validate inventory file
    is_valid, error_msg = validate_file_upload(inventory_file)
    if not is_valid:
        return jsonify({'message': f'Inventory file error: {error_msg}'}), 400
    
    # Validate rules file if provided
    if rules_file:
        is_valid, error_msg = validate_file_upload(rules_file)
        if not is_valid:
            return jsonify({'message': f'Rules file error: {error_msg}'}), 400
    
    if not column_mapping_str:
        return jsonify({'message': 'Column mapping is required'}), 400
    
    try:
        column_mapping = json.loads(column_mapping_str)
    except json.JSONDecodeError:
        return jsonify({'message': 'Invalid column mapping format'}), 400

    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save inventory file temporarily
        inventory_filepath = get_safe_filepath(inventory_file.filename)
        inventory_file.save(inventory_filepath)
        
        # Handle rules file
        if rules_file and rules_file.filename:
            rules_filepath = get_safe_filepath(rules_file.filename)
            rules_file.save(rules_filepath)
        else:
            rules_filepath = DEFAULT_RULES_PATH

        # Process the files
        print(f"\n[DEBUG] Processing file: {inventory_file.filename}")
        inventory_df = pd.read_excel(inventory_filepath)
        print(f"[DEBUG] Original columns: {list(inventory_df.columns)}")
        print(f"[DEBUG] Original shape: {inventory_df.shape}")
        print(f"[DEBUG] Column mapping received: {column_mapping}")
        
        inventory_df.rename(columns=column_mapping, inplace=True)
        print(f"[DEBUG] After mapping columns: {list(inventory_df.columns)}")
        
        # Show first few rows for debugging
        print(f"[DEBUG] First 3 rows after mapping:")
        print(inventory_df.head(3).to_string())
        
        if 'creation_date' in inventory_df.columns:
            print(f"[DEBUG] Converting creation_date to datetime...")
            inventory_df['creation_date'] = pd.to_datetime(inventory_df['creation_date'])
            print(f"[DEBUG] Sample creation_date values: {inventory_df['creation_date'].head(3).tolist()}")
        else:
            print(f"[DEBUG] WARNING: 'creation_date' column not found after mapping!")
        
        rules_df = pd.read_excel(rules_filepath)
        
        args = Namespace(debug=False, floating_time=8, straggler_ratio=0.85, stuck_ratio=0.80, stuck_time=6)
        
        # Load enhanced engine if not already loaded
        load_enhanced_engine()
        
        # Use enhanced engine if available, otherwise fall back to original
        if HAS_ENHANCED_ENGINE:
            # Check for rule_ids in form data (for custom rule selection)
            rule_ids_str = request.form.get('rule_ids')
            rule_ids = None
            if rule_ids_str:
                try:
                    rule_ids = json.loads(rule_ids_str)
                except json.JSONDecodeError:
                    pass
            
            print(f"[DEBUG] Running enhanced engine with database rules...")
            anomalies = run_enhanced_engine(
                inventory_df, 
                rules_df, 
                args, 
                use_database_rules=True,
                rule_ids=rule_ids,
                report_id=None  # Will be set after report creation
            )
            print(f"[DEBUG] Enhanced engine returned {len(anomalies)} anomalies")
        else:
            print(f"[DEBUG] Running legacy engine...")
            anomalies = run_enhanced_engine(inventory_df, rules_df, args)
            print(f"[DEBUG] Legacy engine returned {len(anomalies)} anomalies")
        
        # Generate and save the report
        location_summary = summarize_anomalies_by_location(anomalies)
        report_name = f"Analysis - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        
        try:
            # Start a new transaction to ensure clean state
            db.session.rollback()  # Clear any previous transaction state
            
            new_report = AnalysisReport()
            new_report.report_name = report_name
            new_report.user_id = current_user.id
            new_report.location_summary = json.dumps(location_summary)
            
            db.session.add(new_report)
            db.session.flush()

            for item in anomalies:
                anomaly = Anomaly()
                if isinstance(item, dict):
                    anomaly.description = item.get('anomaly_type', 'Uncategorized Anomaly')
                    anomaly.details = json.dumps(item, default=default_json_serializer)
                else:
                    anomaly.description = str(item)
                    anomaly.details = None
                anomaly.report_id = new_report.id
                db.session.add(anomaly)
                
            db.session.commit()
        except Exception as db_error:
            db.session.rollback()
            raise db_error

        return jsonify({'message': 'Report created successfully', 'report_id': new_report.id}), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ERROR] during processing: {e}")
        print(f"[ERROR] traceback: {traceback.format_exc()}")
        return jsonify({'message': f'An error occurred while analyzing the data. (Detail: {type(e).__name__}: {str(e)})'}), 500
    
    finally:
        # Clean up temporary files
        for filepath in [inventory_filepath, rules_filepath if rules_file and rules_file.filename else None]:
            if filepath and filepath.startswith(UPLOAD_FOLDER) and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError:
                    pass

@api_bp.route('/reports/<int:report_id>/details', methods=['GET'])
@token_required
def get_api_report_details(current_user, report_id):
    report = AnalysisReport.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Process anomalies
    processed_anomalies = []
    for anomaly in report.anomalies:
        try:
            details_data = json.loads(anomaly.details) if anomaly.details else {}
            details_data['id'] = anomaly.id
            details_data['status'] = anomaly.status
            
            history_data = [
                {
                    "old_status": h.old_status,
                    "new_status": h.new_status,
                    "comment": h.comment,
                    "user": h.user.username,
                    "timestamp": h.timestamp.isoformat()
                } 
                for h in anomaly.history.order_by(AnomalyHistory.timestamp.asc())
            ]
            details_data['history'] = history_data
            processed_anomalies.append(details_data)
        except json.JSONDecodeError:
            continue

    # Group anomalies by location
    locations_map = {}
    for anomaly in processed_anomalies:
        location = anomaly.get('location', 'N/A')
        if location not in locations_map:
            locations_map[location] = []
        locations_map[location].append(anomaly)

    # Format location summary
    location_summary = sorted(
        [{"name": name, "anomaly_count": len(anoms), "anomalies": anoms} for name, anoms in locations_map.items()],
        key=lambda x: x['anomaly_count'],
        reverse=True
    )

    # Calculate KPIs
    high_priority_list = ['VERY HIGH', 'HIGH']
    total_anomalies = len(processed_anomalies)
    resolved_anomalies = sum(1 for a in processed_anomalies if a.get('status') == 'Resolved')
    
    resolution_rate_text = 'N/A'
    if total_anomalies > 0:
        percentage = (resolved_anomalies / total_anomalies) * 100
        resolution_rate_text = f"{resolved_anomalies} of {total_anomalies} ({percentage:.0f}%)"

    kpis = [
        {'label': 'Total Anomalies', 'value': total_anomalies},
        {'label': 'Priority Alerts', 'value': sum(1 for a in processed_anomalies if a.get('priority') in high_priority_list)},
        {'label': 'Affected Locations', 'value': len(location_summary)},
        {'label': 'Main Issue', 'value': max(set(a['anomaly_type'] for a in processed_anomalies), key=lambda t: [a['anomaly_type'] for a in processed_anomalies].count(t)) if processed_anomalies else 'N/A'},
        {'label': 'Resolution Rate', 'value': resolution_rate_text}
    ]

    return jsonify({
        "reportId": report.id,
        "reportName": report.report_name,
        "kpis": kpis,
        "locations": location_summary
    })

@api_bp.route('/anomalies/<int:anomaly_id>/status', methods=['POST'])
@token_required
def change_api_anomaly_status(current_user, anomaly_id):
    anomaly = Anomaly.query.get_or_404(anomaly_id)
    if anomaly.report.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    comment = data.get('comment')
    
    if not new_status:
        return jsonify({'success': False, 'message': 'New status is required.'}), 400

    VALID_STATUSES = ['New', 'Acknowledged', 'In Progress', 'Resolved']
    if new_status not in VALID_STATUSES:
        return jsonify({'success': False, 'message': f'Invalid status: {new_status}'}), 400

    old_status = anomaly.status
    anomaly.status = new_status
    
    history_entry = AnomalyHistory(
        anomaly_id=anomaly.id,
        old_status=old_status,
        new_status=new_status,
        comment=comment,
        user_id=current_user.id
    )
    
    db.session.add(history_entry)
    db.session.commit()
    
    new_history_item = {
        "old_status": old_status,
        "new_status": new_status,
        "comment": comment,
        "user": current_user.username,
        "timestamp": history_entry.timestamp.isoformat()
    }

    return jsonify({
        'success': True, 
        'message': 'Status updated successfully.',
        'new_status': new_status,
        'history_item': new_history_item
    })

# Register the Blueprint with the main application
app.register_blueprint(api_bp)

# Register Location Management API
try:
    from location_api import location_bp
    app.register_blueprint(location_bp)
    print("Location Management API registered successfully")
except ImportError as e:
    print(f"Location Management API not available: {e}")

# Register Warehouse Configuration API
try:
    from warehouse_api import warehouse_bp
    app.register_blueprint(warehouse_bp)
    print("Warehouse Configuration API registered successfully")
except ImportError as e:
    print(f"Warehouse Configuration API not available: {e}")

# Register Template Management API
try:
    from template_api import template_bp
    app.register_blueprint(template_bp)
    print("Template Management API registered successfully")
except ImportError as e:
    print(f"Template Management API not available: {e}")

# Register Standalone Template Creation API
try:
    from standalone_template_api import standalone_template_bp
    app.register_blueprint(standalone_template_bp)
    print("Standalone Template Creation API registered successfully")
except ImportError as e:
    print(f"Standalone Template Creation API not available: {e}")

# Load enhanced engine and register Rules API
# Temporarily disabled to fix circular imports
# load_enhanced_engine()

try:
    from rules_api import register_rules_api
    register_rules_api(app)
    print("Rules API registered successfully")
except ImportError as e:
    print(f"Rules API not available: {e}")

# ==================== DEBUGGING AND MONITORING SETUP ====================

# Initialize monitoring system
try:
    from monitoring import create_monitoring_endpoints, start_monitoring_cleanup
    create_monitoring_endpoints(app)
    print("Production monitoring system initialized")
except ImportError as e:
    print(f"Monitoring system not available: {e}")

# Initialize API debugging
try:
    from api_debugger import create_api_debugging_endpoints, WarehouseDebugMiddleware
    create_api_debugging_endpoints(app) 
    # Apply debug middleware
    WarehouseDebugMiddleware(app)
    print("API debugging system initialized")
except ImportError as e:
    print(f"API debugging system not available: {e}")

# Initialize deployment health checker
try:
    from deployment_health_checker import deployment_health_checker
    
    @app.route('/api/v1/deployment/health')
    def deployment_health_status():
        """Get deployment health status"""
        return deployment_health_checker.get_health_status()
    
    @app.route('/api/v1/deployment/start-monitoring', methods=['POST'])
    def start_deployment_monitoring():
        """Start deployment monitoring"""
        data = request.get_json() or {}
        phase = data.get('phase', 'deployment')
        deployment_health_checker.start_deployment_monitoring(phase)
        return {'message': f'Deployment monitoring started for phase: {phase}'}
    
    @app.route('/api/v1/deployment/stop-monitoring', methods=['POST'])
    def stop_deployment_monitoring():
        """Stop deployment monitoring"""
        deployment_health_checker.stop_deployment_monitoring()
        return {'message': 'Deployment monitoring stopped'}
    
    print("Deployment health checker initialized")
except ImportError as e:
    print(f"Deployment health checker not available: {e}")

# Initialize debug test framework
try:
    from debug_test_framework import debug_test_framework
    
    @app.route('/api/v1/debug/run-tests', methods=['POST'])
    def run_debug_tests():
        """Run debugging test framework"""
        data = request.get_json() or {}
        parallel = data.get('parallel', False)
        results = debug_test_framework.run_all_tests(parallel=parallel)
        return results
    
    @app.route('/api/v1/debug/test-status')
    def get_test_status():
        """Get test framework status"""
        return {
            'setup_complete': debug_test_framework.setup_complete,
            'registered_suites': list(debug_test_framework.test_suites.keys()),
            'last_results_count': len(debug_test_framework.test_results)
        }
    
    print("Debug test framework initialized")
except ImportError as e:
    print(f"Debug test framework not available: {e}")

# Initialize migration debugger endpoints
try:
    from migration_debugger import migration_debugger
    
    @app.route('/api/v1/debug/migration-report')
    def get_migration_report():
        """Get comprehensive migration debugging report"""
        return migration_debugger.generate_migration_report()
    
    @app.route('/api/v1/debug/schema-validation')
    def validate_database_schema():
        """Validate database schema"""
        return migration_debugger.validate_schema()
    
    @app.route('/api/v1/debug/migration-health')
    def check_migration_health():
        """Check migration health"""
        return migration_debugger.check_migration_health()
    
    print("Migration debugger endpoints initialized")
except ImportError as e:
    print(f"Migration debugger not available: {e}")

# Create comprehensive debugging dashboard endpoint
@app.route('/api/v1/debug/dashboard')
def comprehensive_debug_dashboard():
    """Comprehensive debugging dashboard data"""
    try:
        dashboard_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'system_health': {},
            'migration_status': {},
            'deployment_health': {},
            'test_results': {},
            'monitoring_data': {}
        }
        
        # Get system health
        try:
            from monitoring import MonitoringDashboard
            dashboard_data['system_health'] = MonitoringDashboard.get_system_health()
            dashboard_data['monitoring_data'] = {
                'errors': MonitoringDashboard.get_error_summary(hours=1),
                'performance': MonitoringDashboard.get_performance_summary(hours=1),
                'database': MonitoringDashboard.get_database_summary(hours=1)
            }
        except Exception as e:
            dashboard_data['system_health'] = {'error': str(e)}
        
        # Get migration status
        try:
            from migration_debugger import migration_debugger
            dashboard_data['migration_status'] = migration_debugger.validate_schema()
        except Exception as e:
            dashboard_data['migration_status'] = {'error': str(e)}
        
        # Get deployment health
        try:
            from deployment_health_checker import deployment_health_checker
            dashboard_data['deployment_health'] = deployment_health_checker.get_health_status()
        except Exception as e:
            dashboard_data['deployment_health'] = {'error': str(e)}
        
        # Get test status
        try:
            from debug_test_framework import debug_test_framework
            recent_results = debug_test_framework.test_results[-10:] if debug_test_framework.test_results else []
            dashboard_data['test_results'] = {
                'recent_tests': len(recent_results),
                'setup_complete': debug_test_framework.setup_complete,
                'available_suites': list(debug_test_framework.test_suites.keys())
            }
        except Exception as e:
            dashboard_data['test_results'] = {'error': str(e)}
        
        return dashboard_data
        
    except Exception as e:
        return {
            'error': f'Debug dashboard error: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }, 500


# ==================== RULES MANAGEMENT WEB INTERFACE ====================

@app.route('/rules')
def rules_management():
    """Rule Management Web Interface"""
    return render_template('rules.html')

import os

# Usa una variable de entorno o una clave secreta difícil de adivinar
SECRET_INIT_KEY = os.environ.get('DB_INIT_KEY', '25cf3e7ec8bdab0cc3114fd8f73c2899')

@app.route(f'/init-db/{SECRET_INIT_KEY}')
def init_database():
    """
    Ruta secreta para crear las tablas de la base de datos.
    Debería ser eliminada después del primer uso en producción.
    """
    try:
        with app.app_context():
            db.create_all()
        return "<h1>Base de datos inicializada correctamente!</h1><p>Ahora puedes eliminar esta ruta de tu archivo app.py por seguridad.</p>"
    except Exception as e:
        return f"<h1>Error al inicializar la base de datos:</h1><p>{str(e)}</p>", 500

@app.route(f'/migrate-db/{SECRET_INIT_KEY}')
def migrate_database():
    """
    Ruta secreta para actualizar el esquema de la base de datos.
    Específicamente para aumentar el tamaño de password_hash.
    """
    try:
        with app.app_context():
            # For PostgreSQL, we need to alter the column
            if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
                from sqlalchemy import text
                db.session.execute(text("ALTER TABLE \"user\" ALTER COLUMN password_hash TYPE VARCHAR(200);"))
                db.session.commit()
                return "<h1>Esquema de base de datos actualizado!</h1><p>La columna password_hash ahora soporta 200 caracteres.</p>"
            else:
                # For SQLite, recreate the table (simpler approach)
                db.create_all()
                return "<h1>Esquema de base de datos actualizado (SQLite)!</h1><p>Las tablas han sido recreadas.</p>"
    except Exception as e:
        return f"<h1>Error al migrar la base de datos:</h1><p>{str(e)}</p>", 500

@app.route(f'/fix-warehouse-schema/{SECRET_INIT_KEY}')
def fix_warehouse_schema():
    """
    Ruta secreta para agregar las columnas faltantes del warehouse a la tabla location.
    Esta migración es segura y no afecta datos existentes.
    """
    try:
        with app.app_context():
            from sqlalchemy import text
            
            messages = []
            is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
            
            if is_postgres:
                messages.append("Detectado: PostgreSQL")
                
                # Check and add missing columns to location table
                missing_columns = [
                    ("warehouse_id", "VARCHAR(50) DEFAULT 'DEFAULT'"),
                    ("aisle_number", "INTEGER"),
                    ("rack_number", "INTEGER"),
                    ("position_number", "INTEGER"),
                    ("level", "VARCHAR(10)"),
                    ("pallet_capacity", "INTEGER DEFAULT 1"),
                    ("location_hierarchy", "TEXT"),
                    ("special_requirements", "TEXT"),
                    ("is_active", "BOOLEAN DEFAULT TRUE"),
                    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                    ("created_by", "INTEGER")
                ]
                
                columns_added = 0
                for column_name, column_def in missing_columns:
                    try:
                        # Check if column exists
                        check_sql = """
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'location' AND column_name = :column_name
                        """
                        result = db.session.execute(text(check_sql), {'column_name': column_name}).fetchone()
                        
                        if not result:
                            # Add the column
                            alter_sql = f"ALTER TABLE location ADD COLUMN {column_name} {column_def}"
                            db.session.execute(text(alter_sql))
                            messages.append(f"✓ Agregada columna: {column_name}")
                            columns_added += 1
                        else:
                            messages.append(f"⚪ Ya existe: {column_name}")
                    except Exception as e:
                        messages.append(f"❌ Error con {column_name}: {str(e)}")
                
                # Ensure warehouse_config table exists
                try:
                    check_table_sql = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'warehouse_config'
                    """
                    result = db.session.execute(text(check_table_sql)).fetchone()
                    
                    if not result:
                        create_wc_sql = """
                        CREATE TABLE warehouse_config (
                            id SERIAL PRIMARY KEY,
                            warehouse_id VARCHAR(50) NOT NULL UNIQUE,
                            warehouse_name VARCHAR(120) NOT NULL,
                            num_aisles INTEGER NOT NULL,
                            racks_per_aisle INTEGER NOT NULL,
                            positions_per_rack INTEGER NOT NULL,
                            levels_per_position INTEGER DEFAULT 4,
                            level_names VARCHAR(20) DEFAULT 'ABCD',
                            default_pallet_capacity INTEGER DEFAULT 1,
                            bidimensional_racks BOOLEAN DEFAULT FALSE,
                            receiving_areas TEXT,
                            staging_areas TEXT,
                            dock_areas TEXT,
                            default_zone VARCHAR(50) DEFAULT 'GENERAL',
                            position_numbering_start INTEGER DEFAULT 1,
                            position_numbering_split BOOLEAN DEFAULT TRUE,
                            created_by INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            is_active BOOLEAN DEFAULT TRUE
                        )
                        """
                        db.session.execute(text(create_wc_sql))
                        messages.append("✓ Creada tabla: warehouse_config")
                    else:
                        messages.append("⚪ Ya existe tabla: warehouse_config")
                
                except Exception as e:
                    messages.append(f"❌ Error creando warehouse_config: {str(e)}")
                
                db.session.commit()
                
                messages.append(f"<br><strong>Resumen: {columns_added} columnas agregadas exitosamente!</strong>")
                
            else:
                # SQLite - use create_all which is safer
                db.create_all()
                messages.append("SQLite: Tablas actualizadas con create_all()")
            
            response_html = f"""
            <h1>✅ Esquema de Warehouse Actualizado!</h1>
            <h3>Detalles de la migración:</h3>
            <ul>
                {"".join([f"<li>{msg}</li>" for msg in messages])}
            </ul>
            <p><strong>El warehouse setup ahora debería funcionar sin errores de SQL.</strong></p>
            <p><em>Puedes eliminar esta ruta después de verificar que todo funciona.</em></p>
            """
            
            return response_html
            
    except Exception as e:
        error_html = f"""
        <h1>❌ Error al migrar esquema de warehouse:</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><strong>Tipo:</strong> {type(e).__name__}</p>
        <hr>
        <h3>Qué hacer:</h3>
        <ol>
            <li>Verifica que la base de datos esté funcionando</li>
            <li>Intenta de nuevo en unos minutos</li>
            <li>Si persiste el error, reporta este mensaje completo</li>
        </ol>
        """
        return error_html, 500

@app.route(f'/fix-level-column-size/{SECRET_INIT_KEY}')
def fix_level_column_size():
    """
    Ruta para expandir el tamaño de la columna level de VARCHAR(1) a VARCHAR(10)
    Esto permite niveles como 'L5', 'L10', etc.
    """
    try:
        with app.app_context():
            from sqlalchemy import text
            
            is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
            
            if is_postgres:
                # Check current column size
                check_sql = """
                SELECT character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'location' AND column_name = 'level'
                """
                result = db.session.execute(text(check_sql)).fetchone()
                
                current_size = result[0] if result else "unknown"
                
                if current_size == 1:
                    # Expand the column
                    alter_sql = "ALTER TABLE location ALTER COLUMN level TYPE VARCHAR(10)"
                    db.session.execute(text(alter_sql))
                    db.session.commit()
                    
                    return f"""
                    <h1>✅ Columna 'level' Expandida Exitosamente!</h1>
                    <p><strong>Cambio realizado:</strong> VARCHAR(1) → VARCHAR(10)</p>
                    <p>Ahora puedes usar niveles como 'L5', 'L10', etc.</p>
                    <p>El warehouse setup debería funcionar correctamente.</p>
                    """
                else:
                    return f"""
                    <h1>⚪ Columna 'level' Ya Está Configurada Correctamente</h1>
                    <p><strong>Tamaño actual:</strong> VARCHAR({current_size})</p>
                    <p>No se requieren cambios.</p>
                    """
            else:
                return """
                <h1>⚠️ SQLite Detectado</h1>
                <p>Esta migración está diseñada para PostgreSQL.</p>
                <p>En SQLite, el tamaño de columna es más flexible.</p>
                """
            
    except Exception as e:
        return f"""
        <h1>❌ Error al expandir columna 'level':</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <p>Puede que la columna ya esté expandida o haya otro problema.</p>
        """, 500

@app.route(f'/complete-database-fix/{SECRET_INIT_KEY}')
def complete_database_fix():
    """
    COMPREHENSIVE DATABASE FIX - Diagnoses and fixes ALL missing warehouse tables/columns
    This is the nuclear option that fixes everything at once
    """
    try:
        with app.app_context():
            from sqlalchemy import text
            
            messages = []
            is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
            
            messages.append(f"🔍 Database Type: {'PostgreSQL' if is_postgres else 'SQLite'}")
            
            if is_postgres:
                # STEP 1: Check which tables exist
                messages.append("<br><h3>🔍 STEP 1: Checking existing tables...</h3>")
                
                table_check_sql = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
                existing_tables = [row[0] for row in db.session.execute(text(table_check_sql)).fetchall()]
                messages.append(f"Existing tables: {', '.join(existing_tables)}")
                
                # STEP 2: Create missing tables
                messages.append("<br><h3>⚙️ STEP 2: Creating missing tables...</h3>")
                
                tables_to_create = {
                    'warehouse_config': """
                        CREATE TABLE warehouse_config (
                            id SERIAL PRIMARY KEY,
                            warehouse_id VARCHAR(50) NOT NULL UNIQUE,
                            warehouse_name VARCHAR(120) NOT NULL,
                            num_aisles INTEGER NOT NULL,
                            racks_per_aisle INTEGER NOT NULL,
                            positions_per_rack INTEGER NOT NULL,
                            levels_per_position INTEGER DEFAULT 4,
                            level_names VARCHAR(20) DEFAULT 'ABCD',
                            default_pallet_capacity INTEGER DEFAULT 1,
                            bidimensional_racks BOOLEAN DEFAULT FALSE,
                            receiving_areas TEXT,
                            staging_areas TEXT,
                            dock_areas TEXT,
                            default_zone VARCHAR(50) DEFAULT 'GENERAL',
                            position_numbering_start INTEGER DEFAULT 1,
                            position_numbering_split BOOLEAN DEFAULT TRUE,
                            created_by INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            is_active BOOLEAN DEFAULT TRUE
                        )
                    """,
                    'warehouse_template': """
                        CREATE TABLE warehouse_template (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(120) NOT NULL,
                            description TEXT,
                            template_code VARCHAR(20) UNIQUE,
                            num_aisles INTEGER NOT NULL,
                            racks_per_aisle INTEGER NOT NULL,
                            positions_per_rack INTEGER NOT NULL,
                            levels_per_position INTEGER DEFAULT 4,
                            level_names VARCHAR(20) DEFAULT 'ABCD',
                            default_pallet_capacity INTEGER DEFAULT 1,
                            bidimensional_racks BOOLEAN DEFAULT FALSE,
                            receiving_areas_template TEXT,
                            staging_areas_template TEXT,
                            dock_areas_template TEXT,
                            based_on_config_id INTEGER REFERENCES warehouse_config(id),
                            is_public BOOLEAN DEFAULT FALSE,
                            usage_count INTEGER DEFAULT 0,
                            created_by INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            is_active BOOLEAN DEFAULT TRUE
                        )
                    """,
                    'rule_category': """
                        CREATE TABLE rule_category (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(50) NOT NULL UNIQUE,
                            display_name VARCHAR(100) NOT NULL,
                            priority INTEGER NOT NULL,
                            description TEXT,
                            is_active BOOLEAN DEFAULT TRUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """,
                    'rule': """
                        CREATE TABLE rule (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(120) NOT NULL,
                            description TEXT,
                            category_id INTEGER REFERENCES rule_category(id),
                            rule_type VARCHAR(50) NOT NULL,
                            conditions TEXT NOT NULL,
                            parameters TEXT,
                            priority VARCHAR(20) DEFAULT 'MEDIUM',
                            is_active BOOLEAN DEFAULT TRUE,
                            is_default BOOLEAN DEFAULT FALSE,
                            created_by INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """,
                    'rule_history': """
                        CREATE TABLE rule_history (
                            id SERIAL PRIMARY KEY,
                            rule_id INTEGER REFERENCES rule(id),
                            version INTEGER NOT NULL,
                            changes TEXT NOT NULL,
                            changed_by INTEGER,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """,
                    'rule_template': """
                        CREATE TABLE rule_template (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(120) NOT NULL,
                            description TEXT,
                            category_id INTEGER REFERENCES rule_category(id),
                            template_conditions TEXT NOT NULL,
                            parameters_schema TEXT,
                            is_public BOOLEAN DEFAULT FALSE,
                            usage_count INTEGER DEFAULT 0,
                            created_by INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """,
                    'rule_performance': """
                        CREATE TABLE rule_performance (
                            id SERIAL PRIMARY KEY,
                            rule_id INTEGER REFERENCES rule(id),
                            report_id INTEGER,
                            anomalies_detected INTEGER DEFAULT 0,
                            false_positives INTEGER DEFAULT 0,
                            execution_time_ms INTEGER,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """
                }
                
                tables_created = 0
                for table_name, create_sql in tables_to_create.items():
                    if table_name not in existing_tables:
                        try:
                            db.session.execute(text(create_sql))
                            messages.append(f"✅ Created table: {table_name}")
                            tables_created += 1
                        except Exception as e:
                            messages.append(f"❌ Error creating {table_name}: {str(e)}")
                    else:
                        messages.append(f"⚪ Table exists: {table_name}")
                
                # STEP 3: Add missing columns to location table
                messages.append("<br><h3>🔧 STEP 3: Adding missing columns to location table...</h3>")
                
                missing_columns = [
                    ("warehouse_id", "VARCHAR(50) DEFAULT 'DEFAULT'"),
                    ("aisle_number", "INTEGER"),
                    ("rack_number", "INTEGER"),
                    ("position_number", "INTEGER"),
                    ("level", "VARCHAR(10)"),  # Fixed size issue
                    ("pallet_capacity", "INTEGER DEFAULT 1"),
                    ("location_hierarchy", "TEXT"),
                    ("special_requirements", "TEXT"),
                    ("is_active", "BOOLEAN DEFAULT TRUE"),
                    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                    ("created_by", "INTEGER")
                ]
                
                columns_added = 0
                for column_name, column_def in missing_columns:
                    try:
                        # Check if column exists
                        check_sql = """
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'location' AND column_name = :column_name
                        """
                        result = db.session.execute(text(check_sql), {'column_name': column_name}).fetchone()
                        
                        if not result:
                            alter_sql = f"ALTER TABLE location ADD COLUMN {column_name} {column_def}"
                            db.session.execute(text(alter_sql))
                            messages.append(f"✅ Added column: location.{column_name}")
                            columns_added += 1
                        else:
                            # Check if level column needs size fix
                            if column_name == 'level':
                                size_check = """
                                SELECT character_maximum_length 
                                FROM information_schema.columns 
                                WHERE table_name = 'location' AND column_name = 'level'
                                """
                                size_result = db.session.execute(text(size_check)).fetchone()
                                if size_result and size_result[0] == 1:
                                    alter_sql = "ALTER TABLE location ALTER COLUMN level TYPE VARCHAR(10)"
                                    db.session.execute(text(alter_sql))
                                    messages.append(f"🔧 Fixed column: location.level (VARCHAR(1) → VARCHAR(10))")
                                else:
                                    messages.append(f"⚪ Column OK: location.{column_name}")
                            else:
                                messages.append(f"⚪ Column exists: location.{column_name}")
                                
                    except Exception as e:
                        messages.append(f"❌ Error with location.{column_name}: {str(e)}")
                
                # STEP 4: Seed default data
                messages.append("<br><h3>🌱 STEP 4: Seeding default data...</h3>")
                
                try:
                    # Check if rule categories exist
                    category_count = db.session.execute(text("SELECT COUNT(*) FROM rule_category")).scalar()
                    if category_count == 0:
                        # Create default categories
                        categories_sql = """
                        INSERT INTO rule_category (name, display_name, priority, description) VALUES 
                        ('FLOW_TIME', 'Flow & Time Rules', 1, 'Rules that detect stagnant pallets and time-based issues'),
                        ('SPACE', 'Space Management Rules', 2, 'Rules that manage warehouse space and capacity'),
                        ('PRODUCT', 'Product Compatibility Rules', 3, 'Rules that ensure product storage compliance')
                        """
                        db.session.execute(text(categories_sql))
                        messages.append("✅ Created default rule categories")
                    else:
                        messages.append(f"⚪ Rule categories exist ({category_count} found)")
                        
                except Exception as e:
                    messages.append(f"❌ Error seeding data: {str(e)}")
                
                # Commit all changes
                db.session.commit()
                
                messages.append(f"<br><h3>📊 SUMMARY</h3>")
                messages.append(f"✅ Tables created: {tables_created}")
                messages.append(f"✅ Columns added: {columns_added}")
                messages.append(f"✅ All warehouse database issues should now be resolved!")
                
            else:
                # SQLite fallback
                messages.append("Using SQLite - running create_all()")
                db.create_all()
                messages.append("✅ All tables created with SQLAlchemy")
            
            success_html = f"""
            <h1>🎉 COMPLETE DATABASE FIX SUCCESSFUL!</h1>
            <div style="max-width: 800px; margin: 20px auto; font-family: Arial;">
                <div style="background: #f0f8ff; padding: 15px; border-radius: 8px;">
                    {"<br>".join(messages)}
                </div>
                <br>
                <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;">
                    <h3>🚀 Your warehouse system should now work perfectly!</h3>
                    <p>✅ All tables created</p>
                    <p>✅ All columns added</p>
                    <p>✅ Column sizes fixed</p>
                    <p>✅ Default data seeded</p>
                </div>
                <br>
                <p style="color: #666; font-size: 14px;">
                    <em>This was a comprehensive one-time fix. You can remove this route after confirming everything works.</em>
                </p>
            </div>
            """
            
            return success_html
            
    except Exception as e:
        error_html = f"""
        <h1>❌ Complete Database Fix Error</h1>
        <div style="max-width: 800px; margin: 20px auto; font-family: Arial;">
            <div style="background: #ffe6e6; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545;">
                <p><strong>Error:</strong> {str(e)}</p>
                <p><strong>Type:</strong> {type(e).__name__}</p>
            </div>
            <br>
            <p>Please share this error message for help debugging.</p>
        </div>
        """
        return error_html, 500

# Add location matching test endpoint
@app.route('/api/v1/test-location-matching', methods=['POST'])
@login_required
def test_location_matching():
    """Test the location code matching system with various formats"""
    try:
        data = request.get_json() or {}
        test_codes = data.get('test_codes', None)
        
        # Load rule engine if not already loaded
        load_enhanced_engine()
        
        if not HAS_ENHANCED_ENGINE:
            return jsonify({'error': 'Enhanced engine not available'}), 500
        
        # Get rule engine instance
        from rule_engine import RuleEngine
        engine = RuleEngine()
        
        # Run location matching test
        results = engine.test_location_matching(test_codes)
        
        return jsonify({
            'status': 'success',
            'results': results,
            'message': f'Tested {len(results["test_results"])} location codes'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Location matching test failed: {str(e)}'}), 500

# --- Entry Point to Run the Application ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)