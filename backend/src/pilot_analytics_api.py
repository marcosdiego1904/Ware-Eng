"""
Pilot Analytics API Blueprint
Admin-only endpoints for viewing pilot program metrics and analytics

All endpoints require JWT authentication and admin privileges
"""

from flask import Blueprint, jsonify, request, send_file
from flask_cors import cross_origin
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta
from io import BytesIO, StringIO
import csv
import json

from database import db
from core_models import User
from analytics_service import AnalyticsService
from analytics_models import (
    AnalyticsEvent,
    AnalyticsSession,
    AnalyticsFileUpload,
    AnalyticsAnomaly,
    AnalyticsTimeSavings
)

# Create blueprint
pilot_analytics_bp = Blueprint('pilot_analytics', __name__, url_prefix='/api/v1/pilot')

# JWT secret from environment - use same key as main app
JWT_SECRET = os.environ.get('FLASK_SECRET_KEY', os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-production'))


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            # Decode token
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])

            if not current_user:
                return jsonify({'error': 'User not found'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': f'Token validation failed: {str(e)}'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        # Check if user has admin flag
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403

        return f(current_user, *args, **kwargs)

    return decorated


def parse_date_range(request):
    """Parse start_date and end_date from request parameters"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            start_date = None

    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            end_date = None

    # Default to last 30 days if not specified
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    return start_date, end_date


@pilot_analytics_bp.route('/dashboard', methods=['GET', 'OPTIONS'])
@cross_origin()
@admin_required
def get_dashboard_metrics(current_user):
    """
    Get comprehensive dashboard metrics for pilot program

    Query params:
        - user_id (optional): Filter by specific user
        - warehouse_id (optional): Filter by warehouse
        - start_date (optional): ISO format datetime
        - end_date (optional): ISO format datetime

    Returns:
        JSON with usage, business, and technical metrics
    """
    try:
        # Get filters from query params
        user_id = request.args.get('user_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        start_date, end_date = parse_date_range(request)

        # Default to pilot user if no user_id specified
        if not user_id:
            user_id = AnalyticsService.get_pilot_user_id()
            if not user_id:
                return jsonify({'error': 'Pilot user not found'}), 404

        # Get all metrics (filtered by pilot user)
        usage_metrics = AnalyticsService.get_usage_metrics(
            user_id=user_id,
            warehouse_id=warehouse_id,
            start_date=start_date,
            end_date=end_date
        )

        business_metrics = AnalyticsService.get_business_metrics(
            user_id=user_id,
            warehouse_id=warehouse_id,
            start_date=start_date,
            end_date=end_date
        )

        technical_metrics = AnalyticsService.get_technical_metrics(
            user_id=user_id,
            warehouse_id=warehouse_id,
            start_date=start_date,
            end_date=end_date
        )

        return jsonify({
            'success': True,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'filters': {
                'user_id': user_id,
                'warehouse_id': warehouse_id
            },
            'usage': usage_metrics,
            'business': business_metrics,
            'technical': technical_metrics
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pilot_analytics_bp.route('/usage-metrics', methods=['GET', 'OPTIONS'])
@cross_origin()
@admin_required
def get_usage_metrics(current_user):
    """
    Get detailed usage metrics (logins, time spent, feature usage)

    Returns:
        JSON with login frequency, session duration, files uploaded, feature usage
    """
    try:
        user_id = request.args.get('user_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        start_date, end_date = parse_date_range(request)

        metrics = AnalyticsService.get_usage_metrics(
            user_id=user_id,
            warehouse_id=warehouse_id,
            start_date=start_date,
            end_date=end_date
        )

        return jsonify({
            'success': True,
            'data': metrics
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pilot_analytics_bp.route('/business-metrics', methods=['GET', 'OPTIONS'])
@cross_origin()
@admin_required
def get_business_metrics(current_user):
    """
    Get business impact metrics (issues flagged/resolved, time saved, cost impact)

    Returns:
        JSON with anomaly counts, resolution rates, time/cost savings
    """
    try:
        user_id = request.args.get('user_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        start_date, end_date = parse_date_range(request)

        metrics = AnalyticsService.get_business_metrics(
            user_id=user_id,
            warehouse_id=warehouse_id,
            start_date=start_date,
            end_date=end_date
        )

        return jsonify({
            'success': True,
            'data': metrics
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pilot_analytics_bp.route('/technical-metrics', methods=['GET', 'OPTIONS'])
@cross_origin()
@admin_required
def get_technical_metrics(current_user):
    """
    Get technical performance metrics (upload success, processing time, errors)

    Returns:
        JSON with upload success rate, processing times, error breakdown, browser/device stats
    """
    try:
        user_id = request.args.get('user_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        start_date, end_date = parse_date_range(request)

        metrics = AnalyticsService.get_technical_metrics(
            user_id=user_id,
            warehouse_id=warehouse_id,
            start_date=start_date,
            end_date=end_date
        )

        return jsonify({
            'success': True,
            'data': metrics
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pilot_analytics_bp.route('/sessions', methods=['GET', 'OPTIONS'])
@cross_origin()
@admin_required
def get_sessions(current_user):
    """
    Get detailed session history with login times and durations

    Returns:
        JSON array of sessions with timing data
    """
    try:
        user_id = request.args.get('user_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        start_date, end_date = parse_date_range(request)
        limit = request.args.get('limit', 100, type=int)

        query = AnalyticsSession.query

        if user_id:
            query = query.filter_by(user_id=user_id)
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        if start_date:
            query = query.filter(AnalyticsSession.login_time >= start_date)
        if end_date:
            query = query.filter(AnalyticsSession.login_time <= end_date)

        sessions = query.order_by(
            AnalyticsSession.login_time.desc()
        ).limit(limit).all()

        return jsonify({
            'success': True,
            'count': len(sessions),
            'data': [s.to_dict() for s in sessions]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pilot_analytics_bp.route('/events', methods=['GET', 'OPTIONS'])
@cross_origin()
@admin_required
def get_events(current_user):
    """
    Get detailed event log with user actions

    Query params:
        - event_type (optional): Filter by event type
        - limit (optional): Max events to return (default 100)

    Returns:
        JSON array of events
    """
    try:
        user_id = request.args.get('user_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        event_type = request.args.get('event_type')
        start_date, end_date = parse_date_range(request)
        limit = request.args.get('limit', 100, type=int)

        query = AnalyticsEvent.query

        if user_id:
            query = query.filter_by(user_id=user_id)
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        if event_type:
            query = query.filter_by(event_type=event_type)
        if start_date:
            query = query.filter(AnalyticsEvent.created_at >= start_date)
        if end_date:
            query = query.filter(AnalyticsEvent.created_at <= end_date)

        events = query.order_by(
            AnalyticsEvent.created_at.desc()
        ).limit(limit).all()

        return jsonify({
            'success': True,
            'count': len(events),
            'data': [e.to_dict() for e in events]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pilot_analytics_bp.route('/anomalies', methods=['GET', 'OPTIONS'])
@cross_origin()
@admin_required
def get_anomalies(current_user):
    """
    Get anomaly detection history with resolution tracking

    Returns:
        JSON array of anomalies with detection and resolution data
    """
    try:
        user_id = request.args.get('user_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        rule_type = request.args.get('rule_type')
        resolved = request.args.get('resolved')  # 'true', 'false', or None
        start_date, end_date = parse_date_range(request)
        limit = request.args.get('limit', 100, type=int)

        query = AnalyticsAnomaly.query

        if user_id:
            query = query.filter_by(user_id=user_id)
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        if rule_type:
            query = query.filter_by(rule_type=rule_type)
        if resolved == 'true':
            query = query.filter(AnalyticsAnomaly.resolved_at.isnot(None))
        elif resolved == 'false':
            query = query.filter(AnalyticsAnomaly.resolved_at.is_(None))
        if start_date:
            query = query.filter(AnalyticsAnomaly.detected_at >= start_date)
        if end_date:
            query = query.filter(AnalyticsAnomaly.detected_at <= end_date)

        anomalies = query.order_by(
            AnalyticsAnomaly.detected_at.desc()
        ).limit(limit).all()

        return jsonify({
            'success': True,
            'count': len(anomalies),
            'data': [a.to_dict() for a in anomalies]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pilot_analytics_bp.route('/export', methods=['GET', 'OPTIONS'])
@cross_origin()
@admin_required
def export_data(current_user):
    """
    Export analytics data to CSV for external analysis

    Query params:
        - format: 'csv' or 'json' (default: csv)
        - data_type: 'sessions', 'events', 'uploads', 'anomalies', 'time_savings', or 'all'

    Returns:
        CSV or JSON file download
    """
    try:
        export_format = request.args.get('format', 'csv')
        data_type = request.args.get('data_type', 'all')
        user_id = request.args.get('user_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        start_date, end_date = parse_date_range(request)

        # Collect data based on type
        export_data = {}

        if data_type in ['sessions', 'all']:
            query = AnalyticsSession.query
            if user_id:
                query = query.filter_by(user_id=user_id)
            if warehouse_id:
                query = query.filter_by(warehouse_id=warehouse_id)
            if start_date:
                query = query.filter(AnalyticsSession.login_time >= start_date)
            if end_date:
                query = query.filter(AnalyticsSession.login_time <= end_date)
            export_data['sessions'] = [s.to_dict() for s in query.all()]

        if data_type in ['events', 'all']:
            query = AnalyticsEvent.query
            if user_id:
                query = query.filter_by(user_id=user_id)
            if warehouse_id:
                query = query.filter_by(warehouse_id=warehouse_id)
            if start_date:
                query = query.filter(AnalyticsEvent.created_at >= start_date)
            if end_date:
                query = query.filter(AnalyticsEvent.created_at <= end_date)
            export_data['events'] = [e.to_dict() for e in query.limit(1000).all()]

        if data_type in ['uploads', 'all']:
            query = AnalyticsFileUpload.query
            if user_id:
                query = query.filter_by(user_id=user_id)
            if warehouse_id:
                query = query.filter_by(warehouse_id=warehouse_id)
            if start_date:
                query = query.filter(AnalyticsFileUpload.uploaded_at >= start_date)
            if end_date:
                query = query.filter(AnalyticsFileUpload.uploaded_at <= end_date)
            export_data['uploads'] = [u.to_dict() for u in query.all()]

        if data_type in ['anomalies', 'all']:
            query = AnalyticsAnomaly.query
            if user_id:
                query = query.filter_by(user_id=user_id)
            if warehouse_id:
                query = query.filter_by(warehouse_id=warehouse_id)
            if start_date:
                query = query.filter(AnalyticsAnomaly.detected_at >= start_date)
            if end_date:
                query = query.filter(AnalyticsAnomaly.detected_at <= end_date)
            export_data['anomalies'] = [a.to_dict() for a in query.all()]

        if data_type in ['time_savings', 'all']:
            query = AnalyticsTimeSavings.query
            if user_id:
                query = query.filter_by(user_id=user_id)
            if warehouse_id:
                query = query.filter_by(warehouse_id=warehouse_id)
            if start_date:
                query = query.filter(AnalyticsTimeSavings.date >= start_date.date())
            if end_date:
                query = query.filter(AnalyticsTimeSavings.date <= end_date.date())
            export_data['time_savings'] = [t.to_dict() for t in query.all()]

        # Format and return
        if export_format == 'json':
            response = jsonify(export_data)
            response.headers['Content-Disposition'] = f'attachment; filename=pilot_analytics_{datetime.now().strftime("%Y%m%d")}.json'
            return response
        else:  # CSV
            # For CSV, combine all data into a single file or create separate sheets
            output = StringIO()

            if data_type == 'all':
                # Write summary statistics
                writer = csv.writer(output)
                writer.writerow(['Pilot Analytics Export'])
                writer.writerow(['Generated:', datetime.now().isoformat()])
                writer.writerow(['Date Range:', f'{start_date.date()} to {end_date.date()}'])
                writer.writerow([])

                # Write each data type
                for key, records in export_data.items():
                    if records:
                        writer.writerow([f'--- {key.upper()} ---'])
                        if records:
                            headers = records[0].keys()
                            writer.writerow(headers)
                            for record in records:
                                writer.writerow([record.get(h) for h in headers])
                        writer.writerow([])
            else:
                # Single data type
                records = export_data.get(data_type, [])
                if records:
                    writer = csv.DictWriter(output, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)

            output.seek(0)
            return send_file(
                BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'pilot_analytics_{data_type}_{datetime.now().strftime("%Y%m%d")}.csv'
            )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Health check endpoint
@pilot_analytics_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'pilot-analytics-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
