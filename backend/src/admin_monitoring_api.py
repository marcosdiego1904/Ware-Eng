"""
Admin Monitoring API - Database Statistics and Health Checks
Provides read-only endpoints for monitoring database usage and growth
"""

from flask import Blueprint, jsonify, current_app
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
from database import db
from core_models import User, AnalysisReport, Anomaly
from models import WarehouseTemplate, WarehouseConfig, Location, Rule

# Create blueprint
admin_monitoring_bp = Blueprint('admin_monitoring', __name__, url_prefix='/api/v1/admin')

# Auth decorator - reuse from app.py pattern
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import request
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            import jwt
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user_obj = User.query.get(current_user_id)
            if not current_user_obj:
                return jsonify({'error': 'User not found'}), 401
        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(current_user_obj, *args, **kwargs)
    return decorated


@admin_monitoring_bp.route('/db-stats', methods=['GET'])
@token_required
def get_database_statistics(current_user):
    """
    Get comprehensive database statistics
    Read-only endpoint - safe for both SQLite and PostgreSQL
    """
    try:
        # Basic counts
        total_users = User.query.count()
        total_reports = AnalysisReport.query.count()
        total_anomalies = Anomaly.query.count()
        total_templates = WarehouseTemplate.query.count()
        total_locations = Location.query.count()
        total_warehouses = WarehouseConfig.query.count()
        total_rules = Rule.query.count() if hasattr(Rule, 'query') else 0

        # Active counts
        active_templates = WarehouseTemplate.query.filter_by(is_active=True).count()
        active_locations = Location.query.filter_by(is_active=True).count()

        # Per-user report distribution
        reports_per_user = db.session.query(
            User.username,
            func.count(AnalysisReport.id).label('report_count')
        ).outerjoin(AnalysisReport).group_by(User.id, User.username).all()

        # Per-user template distribution
        templates_per_user = db.session.query(
            User.username,
            func.count(WarehouseTemplate.id).label('template_count')
        ).outerjoin(WarehouseTemplate, WarehouseTemplate.created_by == User.id).group_by(User.id, User.username).all()

        # Recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_reports = AnalysisReport.query.filter(
            AnalysisReport.timestamp >= seven_days_ago
        ).count()

        recent_templates = WarehouseTemplate.query.filter(
            WarehouseTemplate.created_at >= seven_days_ago
        ).count()

        # Top users by activity
        top_users_by_reports = db.session.query(
            User.username,
            func.count(AnalysisReport.id).label('count')
        ).join(AnalysisReport).group_by(User.id, User.username).order_by(
            func.count(AnalysisReport.id).desc()
        ).limit(5).all()

        # Database type detection
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        db_type = 'PostgreSQL' if 'postgresql' in db_uri else 'SQLite'

        # Storage estimates (rough approximation)
        avg_report_size = 1024 * 10  # ~10KB per report (estimate)
        avg_template_size = 1024 * 5  # ~5KB per template (estimate)
        estimated_storage_mb = (
            (total_reports * avg_report_size +
             total_templates * avg_template_size) / (1024 * 1024)
        )

        stats = {
            'database': {
                'type': db_type,
                'estimated_storage_mb': round(estimated_storage_mb, 2)
            },
            'totals': {
                'users': total_users,
                'reports': total_reports,
                'anomalies': total_anomalies,
                'templates': {
                    'total': total_templates,
                    'active': active_templates,
                    'inactive': total_templates - active_templates
                },
                'locations': {
                    'total': total_locations,
                    'active': active_locations
                },
                'warehouses': total_warehouses,
                'rules': total_rules
            },
            'per_user': {
                'reports': [
                    {'username': username, 'count': count}
                    for username, count in reports_per_user
                ],
                'templates': [
                    {'username': username, 'count': count}
                    for username, count in templates_per_user
                ]
            },
            'recent_activity': {
                'reports_last_7_days': recent_reports,
                'templates_last_7_days': recent_templates
            },
            'top_users': {
                'by_reports': [
                    {'username': username, 'count': count}
                    for username, count in top_users_by_reports
                ]
            },
            'limits_check': {
                'users_at_report_limit': len([
                    u for u, count in reports_per_user if count >= 3
                ]),
                'users_with_5plus_templates': len([
                    u for u, count in templates_per_user if count >= 5
                ])
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        return jsonify(stats), 200

    except Exception as e:
        current_app.logger.error(f"Error getting database statistics: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve statistics',
            'details': str(e)
        }), 500


@admin_monitoring_bp.route('/db-health', methods=['GET'])
@token_required
def check_database_health(current_user):
    """
    Check database health and identify potential issues
    """
    try:
        issues = []
        warnings = []

        # Check 1: Users with too many reports
        users_with_many_reports = db.session.query(
            User.username,
            func.count(AnalysisReport.id).label('count')
        ).join(AnalysisReport).group_by(User.id, User.username).having(
            func.count(AnalysisReport.id) > 3
        ).all()

        if users_with_many_reports:
            warnings.append({
                'type': 'report_limit_exceeded',
                'message': f'{len(users_with_many_reports)} users have more than 3 reports',
                'users': [{'username': u, 'count': c} for u, c in users_with_many_reports]
            })

        # Check 2: Users with many templates
        users_with_many_templates = db.session.query(
            User.username,
            func.count(WarehouseTemplate.id).label('count')
        ).join(WarehouseTemplate, WarehouseTemplate.created_by == User.id).group_by(
            User.id, User.username
        ).having(func.count(WarehouseTemplate.id) > 5).all()

        if users_with_many_templates:
            warnings.append({
                'type': 'template_limit_exceeded',
                'message': f'{len(users_with_many_templates)} users have more than 5 templates',
                'users': [{'username': u, 'count': c} for u, c in users_with_many_templates]
            })

        # Check 3: Orphaned anomalies (anomalies without reports)
        orphaned_anomalies = db.session.query(Anomaly).outerjoin(AnalysisReport).filter(
            AnalysisReport.id == None
        ).count()

        if orphaned_anomalies > 0:
            issues.append({
                'type': 'orphaned_anomalies',
                'message': f'{orphaned_anomalies} anomalies without parent reports',
                'severity': 'medium'
            })

        # Check 4: Inactive templates taking space
        old_inactive_templates = WarehouseTemplate.query.filter(
            WarehouseTemplate.is_active == False,
            WarehouseTemplate.created_at < datetime.utcnow() - timedelta(days=180)
        ).count()

        if old_inactive_templates > 0:
            warnings.append({
                'type': 'old_inactive_templates',
                'message': f'{old_inactive_templates} inactive templates older than 180 days',
                'suggestion': 'Consider archiving or deleting these templates'
            })

        # Check 5: Very old reports
        old_reports = AnalysisReport.query.filter(
            AnalysisReport.timestamp < datetime.utcnow() - timedelta(days=90)
        ).count()

        if old_reports > 10:
            warnings.append({
                'type': 'old_reports',
                'message': f'{old_reports} reports older than 90 days',
                'suggestion': 'Consider implementing data retention policy'
            })

        health_status = 'healthy' if not issues else 'issues_found'
        if warnings and not issues:
            health_status = 'warnings'

        return jsonify({
            'status': health_status,
            'issues': issues,
            'warnings': warnings,
            'checks_performed': 5,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error checking database health: {str(e)}")
        return jsonify({
            'error': 'Health check failed',
            'details': str(e)
        }), 500


@admin_monitoring_bp.route('/user-stats/<int:user_id>', methods=['GET'])
@token_required
def get_user_statistics(current_user, user_id):
    """
    Get detailed statistics for a specific user
    """
    try:
        user = User.query.get_or_404(user_id)

        # Report stats
        report_count = AnalysisReport.query.filter_by(user_id=user_id).count()
        recent_reports = AnalysisReport.query.filter(
            AnalysisReport.user_id == user_id,
            AnalysisReport.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).count()

        # Template stats
        template_count = WarehouseTemplate.query.filter_by(
            created_by=user_id,
            is_active=True
        ).count()

        # Warehouse stats
        warehouse_count = WarehouseConfig.query.filter_by(created_by=user_id).count()

        # Activity timeline (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_activity = db.session.query(
            func.date(AnalysisReport.timestamp).label('date'),
            func.count(AnalysisReport.id).label('count')
        ).filter(
            AnalysisReport.user_id == user_id,
            AnalysisReport.timestamp >= thirty_days_ago
        ).group_by(func.date(AnalysisReport.timestamp)).all()

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username
            },
            'reports': {
                'total': report_count,
                'last_30_days': recent_reports,
                'limit': 3,
                'remaining': max(0, 3 - report_count)
            },
            'templates': {
                'total': template_count,
                'limit': 5,
                'remaining': max(0, 5 - template_count)
            },
            'warehouses': warehouse_count,
            'activity': {
                'daily': [
                    {'date': str(date), 'reports': count}
                    for date, count in daily_activity
                ]
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting user statistics: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve user statistics',
            'details': str(e)
        }), 500
