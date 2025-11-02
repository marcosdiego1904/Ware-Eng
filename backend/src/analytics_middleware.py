"""
Analytics Middleware for API Performance Tracking
Automatically tracks request/response metrics for technical monitoring
"""

from flask import request, g
from functools import wraps
import time
import logging
from analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


def track_api_performance(app):
    """
    Add API performance tracking to Flask app

    Tracks:
    - Request duration
    - HTTP status codes
    - Endpoints called
    - User making request (if authenticated)

    Usage:
        track_api_performance(app)
    """

    @app.before_request
    def before_request():
        """Start timing the request"""
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        """Track request completion and performance"""
        try:
            # Calculate duration
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                duration_ms = duration * 1000

                # Get request info
                endpoint = request.endpoint or 'unknown'
                method = request.method
                path = request.path
                status_code = response.status_code

                # Get user if authenticated (from JWT or session)
                user_id = None
                if hasattr(g, 'current_user') and g.current_user:
                    user_id = g.current_user.id

                # Log slow requests (>1 second)
                if duration > 1.0:
                    logger.warning(
                        f"Slow request: {method} {path} took {duration_ms:.2f}ms "
                        f"(status {status_code})"
                    )

                # Track API call event for analytics (only for API routes)
                if path.startswith('/api/') and user_id:
                    try:
                        AnalyticsService.track_event(
                            user_id=user_id,
                            event_type='api_call',
                            event_category='technical',
                            event_action='request_completed',
                            metadata={
                                'endpoint': endpoint,
                                'method': method,
                                'path': path,
                                'status_code': status_code,
                                'duration_ms': round(duration_ms, 2)
                            }
                        )
                    except Exception as e:
                        # Don't fail requests due to analytics errors
                        logger.error(f"Error tracking API call: {str(e)}")

        except Exception as e:
            # Don't fail requests due to middleware errors
            logger.error(f"Error in analytics middleware: {str(e)}")

        return response


def track_errors(app):
    """
    Add error tracking to Flask app

    Tracks:
    - Unhandled exceptions
    - HTTP error responses (4xx, 5xx)

    Usage:
        track_errors(app)
    """

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Track unhandled exceptions"""
        try:
            # Get user if authenticated
            user_id = None
            if hasattr(g, 'current_user') and g.current_user:
                user_id = g.current_user.id

            # Track error event
            if user_id:
                AnalyticsService.track_event(
                    user_id=user_id,
                    event_type='error',
                    event_category='technical',
                    event_action='exception_occurred',
                    metadata={
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'endpoint': request.endpoint,
                        'path': request.path,
                        'method': request.method
                    }
                )

            logger.error(f"Unhandled exception: {type(e).__name__}: {str(e)}")

        except Exception as tracking_error:
            logger.error(f"Error tracking exception: {str(tracking_error)}")

        # Re-raise the original exception
        raise e

    @app.errorhandler(404)
    def handle_404(e):
        """Track 404 errors"""
        logger.warning(f"404 Not Found: {request.path}")
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def handle_500(e):
        """Track 500 errors"""
        logger.error(f"500 Internal Server Error: {str(e)}")
        return {'error': 'Internal server error'}, 500


def setup_analytics_middleware(app):
    """
    Setup all analytics middleware on Flask app

    Usage:
        from analytics_middleware import setup_analytics_middleware
        setup_analytics_middleware(app)
    """
    track_api_performance(app)
    track_errors(app)
    logger.info("Analytics middleware initialized")
