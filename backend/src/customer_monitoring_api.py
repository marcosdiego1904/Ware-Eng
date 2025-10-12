"""
Customer Activity Monitoring API
Track and analyze customer demo account usage for sales insights
"""

from flask import Blueprint, jsonify, current_app, request
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from database import db
from core_models import User, AnalysisReport, Anomaly
from models import WarehouseTemplate, WarehouseConfig, Location

# Create blueprint
customer_monitoring_bp = Blueprint('customer_monitoring', __name__, url_prefix='/api/v1/customer-monitoring')

# Admin auth decorator
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
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

            # Check if user is admin (you can add an is_admin field to User model)
            # For now, we'll allow any authenticated user to view their own data
            # and only specific users to view all customer data

        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(current_user_obj, *args, **kwargs)
    return decorated


@customer_monitoring_bp.route('/demo-users', methods=['GET'])
@admin_required
def get_demo_users(current_user):
    """
    Get list of all demo users and their activity
    """
    try:
        # Find all demo users (username starts with 'demo_')
        demo_users = User.query.filter(User.username.like('demo_%')).all()

        users_data = []
        for user in demo_users:
            # Get activity stats
            report_count = AnalysisReport.query.filter_by(user_id=user.id).count()
            template_count = WarehouseTemplate.query.filter_by(
                created_by=user.id,
                is_active=True
            ).count()

            # Get last activity
            last_report = AnalysisReport.query.filter_by(user_id=user.id).order_by(
                desc(AnalysisReport.timestamp)
            ).first()

            # Calculate engagement score
            engagement_score = calculate_engagement_score(user.id)

            users_data.append({
                'user_id': user.id,
                'username': user.username,
                'activity': {
                    'reports_created': report_count,
                    'templates_created': template_count,
                    'last_activity': last_report.timestamp.isoformat() if last_report else None,
                    'engagement_score': engagement_score
                },
                'limits': {
                    'max_reports': user.max_reports,
                    'max_templates': user.max_templates,
                    'reports_remaining': max(0, user.max_reports - report_count),
                    'templates_remaining': max(0, user.max_templates - template_count)
                }
            })

        return jsonify({
            'demo_users': users_data,
            'total_count': len(users_data),
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting demo users: {str(e)}")
        return jsonify({'error': 'Failed to retrieve demo users'}), 500


@customer_monitoring_bp.route('/user/<int:user_id>/activity', methods=['GET'])
@admin_required
def get_user_detailed_activity(current_user, user_id):
    """
    Get detailed activity log for a specific customer demo user
    """
    try:
        user = User.query.get_or_404(user_id)

        # Get reports with details
        reports = AnalysisReport.query.filter_by(user_id=user_id).order_by(
            desc(AnalysisReport.timestamp)
        ).limit(50).all()

        reports_data = []
        for report in reports:
            anomaly_count = Anomaly.query.filter_by(report_id=report.id).count()
            reports_data.append({
                'id': report.id,
                'name': report.report_name,
                'created_at': report.timestamp.isoformat(),
                'anomaly_count': anomaly_count
            })

        # Get templates
        templates = WarehouseTemplate.query.filter_by(
            created_by=user_id,
            is_active=True
        ).order_by(desc(WarehouseTemplate.created_at)).all()

        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'name': template.name,
                'created_at': template.created_at.isoformat(),
                'usage_count': template.usage_count
            })

        # Get warehouse configs
        warehouses = WarehouseConfig.query.filter_by(created_by=user_id).all()
        warehouse_count = len(warehouses)

        # Calculate session statistics
        sessions = calculate_user_sessions(user_id)

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username
            },
            'activity_summary': {
                'total_reports': len(reports),
                'total_templates': len(templates),
                'total_warehouses': warehouse_count,
                'total_sessions': len(sessions),
                'avg_session_duration_minutes': sum(s['duration_minutes'] for s in sessions) / len(sessions) if sessions else 0
            },
            'recent_reports': reports_data[:10],
            'templates': templates_data,
            'sessions': sessions[-10:],  # Last 10 sessions
            'engagement_metrics': get_engagement_metrics(user_id),
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting user activity: {str(e)}")
        return jsonify({'error': 'Failed to retrieve user activity'}), 500


@customer_monitoring_bp.route('/user/<int:user_id>/timeline', methods=['GET'])
@admin_required
def get_user_timeline(current_user, user_id):
    """
    Get chronological timeline of all user actions
    """
    try:
        user = User.query.get_or_404(user_id)

        timeline = []

        # Get all reports
        reports = AnalysisReport.query.filter_by(user_id=user_id).all()
        for report in reports:
            timeline.append({
                'type': 'report_created',
                'timestamp': report.timestamp,
                'description': f"Created report: {report.report_name}",
                'details': {
                    'report_id': report.id,
                    'report_name': report.report_name
                }
            })

        # Get all templates
        templates = WarehouseTemplate.query.filter_by(created_by=user_id).all()
        for template in templates:
            timeline.append({
                'type': 'template_created',
                'timestamp': template.created_at,
                'description': f"Created template: {template.name}",
                'details': {
                    'template_id': template.id,
                    'template_name': template.name
                }
            })

        # Get all warehouse configs
        warehouses = WarehouseConfig.query.filter_by(created_by=user_id).all()
        for warehouse in warehouses:
            timeline.append({
                'type': 'warehouse_created',
                'timestamp': warehouse.created_at,
                'description': f"Created warehouse: {warehouse.warehouse_name}",
                'details': {
                    'warehouse_id': warehouse.warehouse_id,
                    'warehouse_name': warehouse.warehouse_name
                }
            })

        # Sort timeline by timestamp (newest first)
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)

        # Convert timestamps to ISO format
        for event in timeline:
            event['timestamp'] = event['timestamp'].isoformat()

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username
            },
            'timeline': timeline,
            'total_events': len(timeline),
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting user timeline: {str(e)}")
        return jsonify({'error': 'Failed to retrieve user timeline'}), 500


@customer_monitoring_bp.route('/engagement-report', methods=['GET'])
@admin_required
def get_engagement_report(current_user):
    """
    Get comprehensive engagement report for all demo users
    """
    try:
        demo_users = User.query.filter(User.username.like('demo_%')).all()

        engagement_data = []
        for user in demo_users:
            metrics = get_engagement_metrics(user.id)
            engagement_data.append({
                'user_id': user.id,
                'username': user.username,
                'metrics': metrics,
                'risk_level': calculate_risk_level(metrics)
            })

        # Sort by engagement score
        engagement_data.sort(key=lambda x: x['metrics']['engagement_score'], reverse=True)

        return jsonify({
            'demo_users_engagement': engagement_data,
            'summary': {
                'total_demo_users': len(engagement_data),
                'highly_engaged': len([u for u in engagement_data if u['risk_level'] == 'low']),
                'moderately_engaged': len([u for u in engagement_data if u['risk_level'] == 'medium']),
                'at_risk': len([u for u in engagement_data if u['risk_level'] == 'high'])
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error generating engagement report: {str(e)}")
        return jsonify({'error': 'Failed to generate engagement report'}), 500


# Helper Functions

def calculate_engagement_score(user_id):
    """
    Calculate engagement score (0-100) based on user activity
    """
    score = 0

    # Reports created (40 points max)
    report_count = AnalysisReport.query.filter_by(user_id=user_id).count()
    score += min(40, report_count * 10)

    # Templates created (30 points max)
    template_count = WarehouseTemplate.query.filter_by(
        created_by=user_id,
        is_active=True
    ).count()
    score += min(30, template_count * 10)

    # Recency (30 points max)
    last_report = AnalysisReport.query.filter_by(user_id=user_id).order_by(
        desc(AnalysisReport.timestamp)
    ).first()

    if last_report:
        days_since_activity = (datetime.utcnow() - last_report.timestamp).days
        if days_since_activity == 0:
            score += 30
        elif days_since_activity <= 3:
            score += 20
        elif days_since_activity <= 7:
            score += 10

    return min(100, score)


def calculate_user_sessions(user_id):
    """
    Estimate user sessions based on report creation timestamps
    A new session starts if gap > 30 minutes between reports
    """
    reports = AnalysisReport.query.filter_by(user_id=user_id).order_by(
        AnalysisReport.timestamp
    ).all()

    if not reports:
        return []

    sessions = []
    session_start = reports[0].timestamp
    last_activity = reports[0].timestamp

    for i, report in enumerate(reports[1:], 1):
        time_gap = (report.timestamp - last_activity).total_seconds() / 60  # minutes

        if time_gap > 30:  # New session
            sessions.append({
                'session_start': session_start.isoformat(),
                'session_end': last_activity.isoformat(),
                'duration_minutes': int((last_activity - session_start).total_seconds() / 60),
                'actions_count': i
            })
            session_start = report.timestamp

        last_activity = report.timestamp

    # Add final session
    sessions.append({
        'session_start': session_start.isoformat(),
        'session_end': last_activity.isoformat(),
        'duration_minutes': int((last_activity - session_start).total_seconds() / 60),
        'actions_count': len(reports) - len(sessions)
    })

    return sessions


def get_engagement_metrics(user_id):
    """Get detailed engagement metrics for a user"""
    report_count = AnalysisReport.query.filter_by(user_id=user_id).count()
    template_count = WarehouseTemplate.query.filter_by(
        created_by=user_id,
        is_active=True
    ).count()

    last_report = AnalysisReport.query.filter_by(user_id=user_id).order_by(
        desc(AnalysisReport.timestamp)
    ).first()

    days_since_last_activity = None
    if last_report:
        days_since_last_activity = (datetime.utcnow() - last_report.timestamp).days

    return {
        'engagement_score': calculate_engagement_score(user_id),
        'reports_created': report_count,
        'templates_created': template_count,
        'days_since_last_activity': days_since_last_activity,
        'is_active': days_since_last_activity is not None and days_since_last_activity <= 7
    }


def calculate_risk_level(metrics):
    """Determine customer risk level based on engagement"""
    score = metrics['engagement_score']
    days_inactive = metrics['days_since_last_activity']

    if days_inactive is None or days_inactive > 14:
        return 'high'  # Not using the platform
    elif score >= 70:
        return 'low'  # Highly engaged
    elif score >= 40:
        return 'medium'  # Moderately engaged
    else:
        return 'high'  # At risk of churning
