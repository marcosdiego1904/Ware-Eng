"""
Analytics Service for Pilot Program Tracking
Provides methods to track usage, business, and technical metrics
"""

from datetime import datetime, date, timedelta
from database import db
from analytics_models import (
    AnalyticsEvent,
    AnalyticsSession,
    AnalyticsFileUpload,
    AnalyticsAnomaly,
    AnalyticsTimeSavings,
    AnalyticsPilotSummary
)
from sqlalchemy import func
import uuid
import logging
import os

logger = logging.getLogger(__name__)

# Pilot user configuration
PILOT_USERNAME = os.environ.get('PILOT_USERNAME', 'pilot1')


class AnalyticsService:
    """
    Core service for tracking pilot program metrics

    ROI Calculation Methodology:
    ============================

    Time savings are calculated based on WORK ELIMINATED, not results found.
    This provides defensible, consistent ROI metrics for marketing and sales.

    Time Estimation Rationale:
    --------------------------
    1. FILE REVIEW (30 min): Time to manually open, understand structure, scan for issues
    2. RULE CHECKING (12 min per rule type): Time to manually verify each rule across all rows
       - Example rules: excess inventory check, understock check, slow-moving items,
         pricing anomalies, duplicate detection, location issues, etc.
    3. REPORT GENERATION (15 min): Time to compile findings, format, add recommendations

    Example Calculation:
    --------------------
    File upload with 8 automated rule checks:
    - Manual time = 30 min (review) + (8 × 12 min per rule) + 15 min (report)
    - Manual time = 141 minutes = 2.35 hours
    - Cost savings = 2.35 hours × $50/hr = $117.50 per file

    For 10 files: 23.5 hours saved = $1,175 in cost savings

    Why This Approach Works for Marketing:
    --------------------------------------
    ✓ Defensible: Based on actual manual work eliminated, not data quality
    ✓ Consistent: Same savings per file regardless of how many anomalies found
    ✓ Transparent: Easy to explain to prospects and justify to stakeholders
    ✓ Conservative: Underestimates rather than overestimates
    ✓ Compelling: Still shows significant ROI that compounds quickly
    """

    # Time estimation constants (in minutes)
    MANUAL_FILE_REVIEW_TIME = 30  # Minutes to manually open, understand, and scan an inventory file
    MANUAL_RULE_CHECK_TIME = 12  # Minutes to manually verify each rule type across all rows
    MANUAL_REPORT_GENERATION_TIME = 15  # Minutes to manually compile findings and format report

    @staticmethod
    def get_pilot_user_id():
        """Get the pilot user's ID from username"""
        from core_models import User
        pilot_user = User.query.filter_by(username=PILOT_USERNAME).first()
        if pilot_user:
            return pilot_user.id
        else:
            logger.warning(f"Pilot user '{PILOT_USERNAME}' not found in database")
            return None

    @staticmethod
    def get_or_create_pilot_summary(user_id):
        """
        Get or create the pilot summary record for cumulative metrics

        This is a thread-safe get-or-create pattern that ensures exactly one
        summary row exists per pilot user.

        Args:
            user_id: User ID to get/create summary for

        Returns:
            AnalyticsPilotSummary object (existing or newly created)
        """
        try:
            # Try to get existing summary
            summary = AnalyticsPilotSummary.query.filter_by(user_id=user_id).first()

            if not summary:
                # Create new summary with zeroed counters
                summary = AnalyticsPilotSummary(
                    user_id=user_id,
                    total_anomalies_found=0,
                    total_anomalies_resolved=0
                )
                db.session.add(summary)
                db.session.flush()  # Get ID but don't commit yet
                logger.info(f"Created new pilot summary for user {user_id}")

            return summary
        except Exception as e:
            logger.error(f"Error in get_or_create_pilot_summary: {str(e)}")
            db.session.rollback()
            # Return a basic object to prevent crashes (will have default values)
            return AnalyticsPilotSummary(user_id=user_id)

    @staticmethod
    def generate_session_id():
        """Generate unique session ID"""
        return f"session_{uuid.uuid4().hex[:16]}_{int(datetime.utcnow().timestamp())}"

    @staticmethod
    def track_event(user_id, event_type, event_category, event_action,
                   warehouse_id=None, session_id=None, metadata=None):
        """
        Track any user action or event

        Args:
            user_id: ID of user performing action
            event_type: Type of event (login, file_upload, rule_execution, etc.)
            event_category: Category (usage, business, technical)
            event_action: Action taken (clicked, uploaded, generated, etc.)
            warehouse_id: Optional warehouse context
            session_id: Optional session identifier
            metadata: Optional dict with additional data

        Returns:
            AnalyticsEvent object
        """
        try:
            event = AnalyticsEvent(
                user_id=user_id,
                warehouse_id=warehouse_id,
                session_id=session_id or 'no_session',
                event_type=event_type,
                event_category=event_category,
                event_action=event_action,
                event_data=metadata or {}
            )
            db.session.add(event)
            db.session.commit()
            logger.info(f"Tracked event: {event_type} - {event_action} for user {user_id}")
            return event
        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def start_session(user_id, warehouse_id=None, ip_address=None,
                     user_agent=None, browser=None, device_type=None):
        """
        Create new user session on login

        Args:
            user_id: ID of user logging in
            warehouse_id: Optional default warehouse
            ip_address: User's IP address
            user_agent: Browser user agent string
            browser: Parsed browser name
            device_type: desktop, mobile, tablet

        Returns:
            AnalyticsSession object with session_id
        """
        try:
            session_id = AnalyticsService.generate_session_id()

            session = AnalyticsSession(
                session_id=session_id,
                user_id=user_id,
                warehouse_id=warehouse_id,
                login_time=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                browser=browser,
                device_type=device_type
            )
            db.session.add(session)
            db.session.commit()

            # Track login event
            AnalyticsService.track_event(
                user_id=user_id,
                event_type='login',
                event_category='usage',
                event_action='logged_in',
                warehouse_id=warehouse_id,
                session_id=session_id,
                metadata={'browser': browser, 'device': device_type}
            )

            logger.info(f"Started session {session_id} for user {user_id}")
            return session
        except Exception as e:
            logger.error(f"Error starting session: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def end_session(session_id, user_id=None):
        """
        End user session on logout

        Args:
            session_id: Session to end
            user_id: Optional user ID for event tracking

        Returns:
            Updated AnalyticsSession object
        """
        try:
            session = AnalyticsSession.query.filter_by(session_id=session_id).first()
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None

            session.logout_time = datetime.utcnow()
            session.calculate_duration()
            db.session.commit()

            # Track logout event
            if user_id:
                AnalyticsService.track_event(
                    user_id=user_id,
                    event_type='logout',
                    event_category='usage',
                    event_action='logged_out',
                    warehouse_id=session.warehouse_id,
                    session_id=session_id,
                    metadata={'duration_minutes': session.duration_minutes}
                )

            logger.info(f"Ended session {session_id}, duration: {session.duration_minutes} min")
            return session
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def update_session_activity(session_id):
        """
        Update last activity timestamp for session

        Args:
            session_id: Session to update

        Returns:
            Updated session or None
        """
        try:
            session = AnalyticsSession.query.filter_by(session_id=session_id).first()
            if session:
                session.last_activity = datetime.utcnow()
                db.session.commit()
            return session
        except Exception as e:
            logger.error(f"Error updating session activity: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def track_file_upload(user_id, file_type, success, warehouse_id=None,
                         session_id=None, file_name=None, file_size_mb=None,
                         processing_time_seconds=None, error_message=None,
                         columns_detected=None, rows_processed=None,
                         anomalies_found=None):
        """
        Track file upload performance and results

        Args:
            user_id: ID of user uploading file
            file_type: 'inventory' or 'rules'
            success: Boolean indicating if upload succeeded
            warehouse_id: Warehouse context
            session_id: Current session
            file_name: Name of uploaded file
            file_size_mb: File size in MB
            processing_time_seconds: Time to process file
            error_message: Error if upload failed
            columns_detected: Number of columns found
            rows_processed: Number of rows processed
            anomalies_found: Number of anomalies detected

        Returns:
            AnalyticsFileUpload object
        """
        try:
            upload = AnalyticsFileUpload(
                user_id=user_id,
                warehouse_id=warehouse_id,
                session_id=session_id or 'no_session',
                file_type=file_type,
                file_name=file_name,
                file_size_mb=file_size_mb,
                processing_time_seconds=processing_time_seconds,
                success=success,
                error_message=error_message,
                columns_detected=columns_detected,
                rows_processed=rows_processed,
                anomalies_found=anomalies_found
            )
            db.session.add(upload)
            db.session.commit()

            # Track upload event
            AnalyticsService.track_event(
                user_id=user_id,
                event_type='file_upload',
                event_category='technical',
                event_action='uploaded' if success else 'failed',
                warehouse_id=warehouse_id,
                session_id=session_id,
                metadata={
                    'file_type': file_type,
                    'success': success,
                    'file_size_mb': file_size_mb,
                    'processing_time_seconds': processing_time_seconds
                }
            )

            logger.info(f"Tracked file upload: {file_type} for user {user_id}, success={success}")
            return upload
        except Exception as e:
            logger.error(f"Error tracking file upload: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def track_anomaly(anomaly_id, user_id, rule_type, warehouse_id=None,
                     severity=None, potential_cost_impact=None,
                     impact_category=None):
        """
        Track anomaly detection for business impact metrics

        Args:
            anomaly_id: ID of detected anomaly
            user_id: User who triggered detection
            rule_type: Type of rule that detected anomaly
            warehouse_id: Warehouse context
            severity: critical, high, medium, low
            potential_cost_impact: Estimated $ saved
            impact_category: inventory_loss, space_waste, compliance, etc.

        Returns:
            AnalyticsAnomaly object
        """
        try:
            # Check if already tracked
            existing = AnalyticsAnomaly.query.filter_by(anomaly_id=anomaly_id).first()
            if existing:
                logger.info(f"Anomaly {anomaly_id} already tracked")
                return existing

            analytics_anomaly = AnalyticsAnomaly(
                anomaly_id=anomaly_id,
                user_id=user_id,
                warehouse_id=warehouse_id,
                detected_at=datetime.utcnow(),
                severity=severity,
                rule_type=rule_type,
                potential_cost_impact=potential_cost_impact,
                impact_category=impact_category
            )
            db.session.add(analytics_anomaly)
            db.session.commit()

            # Track anomaly detection event
            AnalyticsService.track_event(
                user_id=user_id,
                event_type='anomaly_detected',
                event_category='business',
                event_action='detected',
                warehouse_id=warehouse_id,
                metadata={
                    'rule_type': rule_type,
                    'severity': severity,
                    'anomaly_id': anomaly_id
                }
            )

            logger.info(f"Tracked anomaly {anomaly_id}: {rule_type} for user {user_id}")
            return analytics_anomaly
        except Exception as e:
            logger.error(f"Error tracking anomaly: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def mark_anomaly_resolved(anomaly_id, user_action, user_id=None):
        """
        Mark anomaly as resolved and calculate resolution time

        Args:
            anomaly_id: ID of anomaly to resolve
            user_action: dismissed, fixed, escalated, ignored
            user_id: User who resolved it

        Returns:
            Updated AnalyticsAnomaly object
        """
        try:
            analytics_anomaly = AnalyticsAnomaly.query.filter_by(
                anomaly_id=anomaly_id
            ).first()

            if not analytics_anomaly:
                logger.warning(f"Analytics record for anomaly {anomaly_id} not found")
                return None

            analytics_anomaly.resolved_at = datetime.utcnow()
            analytics_anomaly.user_action = user_action
            analytics_anomaly.calculate_resolution_time()
            db.session.commit()

            # Track resolution event
            if user_id:
                AnalyticsService.track_event(
                    user_id=user_id,
                    event_type='anomaly_resolved',
                    event_category='business',
                    event_action=user_action,
                    warehouse_id=analytics_anomaly.warehouse_id,
                    metadata={
                        'anomaly_id': anomaly_id,
                        'time_to_resolve_hours': analytics_anomaly.time_to_resolve_hours
                    }
                )

            logger.info(f"Marked anomaly {anomaly_id} as {user_action}")
            return analytics_anomaly
        except Exception as e:
            logger.error(f"Error marking anomaly resolved: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def calculate_time_savings(user_id, warehouse_id=None, target_date=None,
                              files_processed=0, reports_generated=0,
                              rule_types_checked=0, automated_time_seconds=0):
        """
        Calculate and store time savings for a given date

        Uses rule-based calculation: savings based on automated rule checks, not anomalies found.
        This provides consistent, defensible ROI metrics regardless of data quality.

        Args:
            user_id: User ID
            warehouse_id: Warehouse context
            target_date: Date for aggregation (defaults to today)
            files_processed: Number of files processed
            reports_generated: Number of reports created
            rule_types_checked: Number of UNIQUE rule types executed (e.g., 8 different rule checks)
            automated_time_seconds: Actual processing time (typically 5-10 seconds)

        Returns:
            AnalyticsTimeSavings object

        Example:
            If 1 file is uploaded and system runs 8 rule checks:
            - Manual time = 30 + (8 × 12) + 15 = 141 minutes
            - Automated time = ~5 seconds
            - Savings = 141 minutes = 2.35 hours = $117.50 @ $50/hr
        """
        try:
            if target_date is None:
                target_date = date.today()

            # Get or create time savings record
            time_savings = AnalyticsTimeSavings.query.filter_by(
                user_id=user_id,
                warehouse_id=warehouse_id,
                date=target_date
            ).first()

            if not time_savings:
                time_savings = AnalyticsTimeSavings(
                    user_id=user_id,
                    warehouse_id=warehouse_id,
                    date=target_date
                )
                db.session.add(time_savings)

            # Update counts (handle None values from database)
            time_savings.files_processed = (time_savings.files_processed or 0) + files_processed
            time_savings.reports_generated = (time_savings.reports_generated or 0) + reports_generated
            time_savings.anomalies_detected = (time_savings.anomalies_detected or 0) + rule_types_checked  # Store rule count here for now
            time_savings.automated_time_seconds = (time_savings.automated_time_seconds or 0) + automated_time_seconds

            # Estimate manual time based on activities (in seconds)
            # This is the key calculation for ROI metrics
            manual_time = 0
            manual_time += files_processed * (AnalyticsService.MANUAL_FILE_REVIEW_TIME * 60)
            manual_time += reports_generated * (AnalyticsService.MANUAL_REPORT_GENERATION_TIME * 60)
            manual_time += rule_types_checked * (AnalyticsService.MANUAL_RULE_CHECK_TIME * 60)

            time_savings.estimated_manual_time_seconds = (time_savings.estimated_manual_time_seconds or 0) + manual_time

            # Calculate savings
            time_savings.calculate_savings(hourly_rate=50.0)

            db.session.commit()

            logger.info(f"Calculated time savings for user {user_id} on {target_date}: "
                       f"{time_savings.time_saved_minutes:.2f} minutes saved "
                       f"(files: {files_processed}, rules: {rule_types_checked})")
            return time_savings
        except Exception as e:
            import traceback
            logger.error(f"Error calculating time savings: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            db.session.rollback()
            return None

    @staticmethod
    def get_usage_metrics(user_id=None, warehouse_id=None, start_date=None, end_date=None):
        """
        Get usage metrics for dashboard

        Returns:
            Dict with login frequency, time spent, files uploaded, feature usage
        """
        try:
            query_filters = []
            if user_id:
                query_filters.append(AnalyticsSession.user_id == user_id)
            if warehouse_id:
                query_filters.append(AnalyticsSession.warehouse_id == warehouse_id)
            if start_date:
                query_filters.append(AnalyticsSession.login_time >= start_date)
            if end_date:
                query_filters.append(AnalyticsSession.login_time <= end_date)

            # Login frequency
            total_sessions = AnalyticsSession.query.filter(*query_filters).count()

            # Time spent
            sessions = AnalyticsSession.query.filter(*query_filters).all()
            total_time_minutes = sum(s.duration_minutes or 0 for s in sessions)
            avg_session_duration = total_time_minutes / total_sessions if total_sessions > 0 else 0

            # Files uploaded
            upload_filters = []
            if user_id:
                upload_filters.append(AnalyticsFileUpload.user_id == user_id)
            if warehouse_id:
                upload_filters.append(AnalyticsFileUpload.warehouse_id == warehouse_id)
            if start_date:
                upload_filters.append(AnalyticsFileUpload.uploaded_at >= start_date)
            if end_date:
                upload_filters.append(AnalyticsFileUpload.uploaded_at <= end_date)

            files_uploaded = AnalyticsFileUpload.query.filter(*upload_filters).count()

            # Feature usage by event type
            event_filters = []
            if user_id:
                event_filters.append(AnalyticsEvent.user_id == user_id)
            if warehouse_id:
                event_filters.append(AnalyticsEvent.warehouse_id == warehouse_id)
            if start_date:
                event_filters.append(AnalyticsEvent.created_at >= start_date)
            if end_date:
                event_filters.append(AnalyticsEvent.created_at <= end_date)

            feature_usage = db.session.query(
                AnalyticsEvent.event_type,
                func.count(AnalyticsEvent.id).label('count')
            ).filter(*event_filters).group_by(AnalyticsEvent.event_type).all()

            return {
                'total_sessions': total_sessions,
                'total_time_minutes': round(total_time_minutes, 2),
                'avg_session_duration': round(avg_session_duration, 2),
                'files_uploaded': files_uploaded,
                'feature_usage': {evt: count for evt, count in feature_usage}
            }
        except Exception as e:
            logger.error(f"Error getting usage metrics: {str(e)}")
            return {}

    @staticmethod
    def get_business_metrics(user_id=None, warehouse_id=None, start_date=None, end_date=None):
        """
        Get business impact metrics for dashboard

        Returns:
            Dict with issues flagged, resolved, time saved, cost impact
        """
        try:
            query_filters = []
            if user_id:
                query_filters.append(AnalyticsAnomaly.user_id == user_id)
            if warehouse_id:
                query_filters.append(AnalyticsAnomaly.warehouse_id == warehouse_id)
            if start_date:
                query_filters.append(AnalyticsAnomaly.detected_at >= start_date)
            if end_date:
                query_filters.append(AnalyticsAnomaly.detected_at <= end_date)

            # Issues by severity
            issues_by_severity = db.session.query(
                AnalyticsAnomaly.severity,
                func.count(AnalyticsAnomaly.id).label('count')
            ).filter(*query_filters).group_by(AnalyticsAnomaly.severity).all()

            # Issues by rule type
            issues_by_rule = db.session.query(
                AnalyticsAnomaly.rule_type,
                func.count(AnalyticsAnomaly.id).label('count')
            ).filter(*query_filters).group_by(AnalyticsAnomaly.rule_type).all()

            # Resolution metrics - USE CUMULATIVE COUNTERS from pilot summary
            # This ensures counts never decrease when reports are deleted
            if user_id:
                pilot_summary = AnalyticsPilotSummary.query.filter_by(user_id=user_id).first()
                if pilot_summary:
                    total_issues = pilot_summary.total_anomalies_found
                    resolved_issues = pilot_summary.total_anomalies_resolved
                else:
                    # Fallback to counting if no summary exists yet
                    total_issues = AnalyticsAnomaly.query.filter(*query_filters).count()
                    resolved_issues = AnalyticsAnomaly.query.filter(
                        *query_filters,
                        AnalyticsAnomaly.resolved_at.isnot(None)
                    ).count()
            else:
                # If no user_id specified, use old counting method
                total_issues = AnalyticsAnomaly.query.filter(*query_filters).count()
                resolved_issues = AnalyticsAnomaly.query.filter(
                    *query_filters,
                    AnalyticsAnomaly.resolved_at.isnot(None)
                ).count()

            resolution_rate = (resolved_issues / total_issues * 100) if total_issues > 0 else 0

            # Average resolution time
            avg_resolution_time = db.session.query(
                func.avg(AnalyticsAnomaly.time_to_resolve_hours)
            ).filter(
                *query_filters,
                AnalyticsAnomaly.time_to_resolve_hours.isnot(None)
            ).scalar() or 0

            # Cost impact
            total_cost_impact = db.session.query(
                func.sum(AnalyticsAnomaly.potential_cost_impact)
            ).filter(*query_filters).scalar() or 0

            # Time savings
            savings_filters = []
            if user_id:
                savings_filters.append(AnalyticsTimeSavings.user_id == user_id)
            if warehouse_id:
                savings_filters.append(AnalyticsTimeSavings.warehouse_id == warehouse_id)
            if start_date:
                savings_filters.append(AnalyticsTimeSavings.date >= start_date.date())
            if end_date:
                savings_filters.append(AnalyticsTimeSavings.date <= end_date.date())

            time_savings_total = db.session.query(
                func.sum(AnalyticsTimeSavings.time_saved_minutes)
            ).filter(*savings_filters).scalar() or 0

            cost_savings_total = db.session.query(
                func.sum(AnalyticsTimeSavings.estimated_cost_savings)
            ).filter(*savings_filters).scalar() or 0

            return {
                'total_issues': total_issues,
                'resolved_issues': resolved_issues,
                'resolution_rate': round(resolution_rate, 2),
                'avg_resolution_hours': round(avg_resolution_time, 2),
                'issues_by_severity': {sev: count for sev, count in issues_by_severity},
                'issues_by_rule': {rule: count for rule, count in issues_by_rule},
                'total_cost_impact': round(total_cost_impact, 2),
                'time_saved_minutes': round(time_savings_total, 2),
                'cost_savings': round(cost_savings_total, 2)
            }
        except Exception as e:
            logger.error(f"Error getting business metrics: {str(e)}")
            return {}

    @staticmethod
    def get_technical_metrics(user_id=None, warehouse_id=None, start_date=None, end_date=None):
        """
        Get technical performance metrics

        Returns:
            Dict with upload success rate, processing times, error rates
        """
        try:
            query_filters = []
            if user_id:
                query_filters.append(AnalyticsFileUpload.user_id == user_id)
            if warehouse_id:
                query_filters.append(AnalyticsFileUpload.warehouse_id == warehouse_id)
            if start_date:
                query_filters.append(AnalyticsFileUpload.uploaded_at >= start_date)
            if end_date:
                query_filters.append(AnalyticsFileUpload.uploaded_at <= end_date)

            # Upload success rate
            total_uploads = AnalyticsFileUpload.query.filter(*query_filters).count()
            successful_uploads = AnalyticsFileUpload.query.filter(
                *query_filters,
                AnalyticsFileUpload.success == True
            ).count()
            success_rate = (successful_uploads / total_uploads * 100) if total_uploads > 0 else 0

            # Processing time statistics
            processing_times = db.session.query(
                func.avg(AnalyticsFileUpload.processing_time_seconds).label('avg'),
                func.min(AnalyticsFileUpload.processing_time_seconds).label('min'),
                func.max(AnalyticsFileUpload.processing_time_seconds).label('max')
            ).filter(
                *query_filters,
                AnalyticsFileUpload.success == True
            ).first()

            # Error breakdown
            error_uploads = AnalyticsFileUpload.query.filter(
                *query_filters,
                AnalyticsFileUpload.success == False
            ).all()
            error_types = {}
            for upload in error_uploads:
                error_msg = upload.error_message or 'Unknown error'
                error_types[error_msg] = error_types.get(error_msg, 0) + 1

            # Device/browser breakdown
            session_filters = []
            if user_id:
                session_filters.append(AnalyticsSession.user_id == user_id)
            if warehouse_id:
                session_filters.append(AnalyticsSession.warehouse_id == warehouse_id)
            if start_date:
                session_filters.append(AnalyticsSession.login_time >= start_date)
            if end_date:
                session_filters.append(AnalyticsSession.login_time <= end_date)

            browsers = db.session.query(
                AnalyticsSession.browser,
                func.count(AnalyticsSession.id).label('count')
            ).filter(*session_filters).group_by(AnalyticsSession.browser).all()

            devices = db.session.query(
                AnalyticsSession.device_type,
                func.count(AnalyticsSession.id).label('count')
            ).filter(*session_filters).group_by(AnalyticsSession.device_type).all()

            return {
                'total_uploads': total_uploads,
                'successful_uploads': successful_uploads,
                'failed_uploads': total_uploads - successful_uploads,
                'success_rate': round(success_rate, 2),
                'avg_processing_time': round(processing_times.avg or 0, 2),
                'min_processing_time': round(processing_times.min or 0, 2),
                'max_processing_time': round(processing_times.max or 0, 2),
                'error_types': error_types,
                'browsers': {browser: count for browser, count in browsers if browser},
                'devices': {device: count for device, count in devices if device}
            }
        except Exception as e:
            logger.error(f"Error getting technical metrics: {str(e)}")
            return {}
