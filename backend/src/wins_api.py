"""
Track Your Wins API
Provides analytics and gamification data for the Track Your Wins dashboard
"""

import re
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from sqlalchemy import func, and_
from database import db
from core_models import User, AnalysisReport, Anomaly, AnomalyHistory
from models import WarehouseConfig, Location

# Create the wins API blueprint
wins_bp = Blueprint('wins_api', __name__, url_prefix='/api/v1/reports')

# JWT Token Required Decorator
def token_required(f):
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
        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(current_user_obj, *args, **kwargs)
    return decorated


class WinsAnalyzer:
    """
    Analyzes AnalysisReport and Anomaly data to generate Track Your Wins metrics
    """

    def __init__(self, report: AnalysisReport):
        self.report = report
        self.anomalies = report.anomalies
        self.total_pallets = report.inventory_count or 0

    def calculate_health_score(self) -> dict:
        """
        Calculate warehouse health score (0-100)
        Formula: 100 - weighted penalties for anomalies
        """
        if self.total_pallets == 0:
            return {
                'score': 0,
                'label': 'No Data',
                'color': '#718096'
            }

        total_anomalies = len(self.anomalies)

        # Count high-priority anomalies
        high_priority_count = sum(1 for a in self.anomalies
                                  if self._get_anomaly_priority(a.description) in ['VERY_HIGH', 'HIGH'])

        # Count unresolved anomalies
        unresolved_count = sum(1 for a in self.anomalies
                              if a.status not in ['Resolved', 'Cleared'])

        # Calculate penalties
        anomaly_rate_penalty = min((total_anomalies / self.total_pallets) * 100 * 0.4, 40)
        priority_penalty = (high_priority_count / max(total_anomalies, 1)) * 30 if total_anomalies > 0 else 0
        resolution_penalty = (unresolved_count / max(total_anomalies, 1)) * 30 if total_anomalies > 0 else 0

        # Calculate final score
        score = max(0, min(100, 100 - anomaly_rate_penalty - priority_penalty - resolution_penalty))

        # Determine label and color
        if score >= 85:
            label, color = 'Excellent Operations', '#38A169'
        elif score >= 70:
            label, color = 'Good Performance', '#F7DC6F'
        elif score >= 50:
            label, color = 'Needs Attention', '#FF6B35'
        else:
            label, color = 'Critical Focus', '#E53E3E'

        return {
            'score': int(score),
            'label': label,
            'color': color,
            'breakdown': {
                'total_pallets': self.total_pallets,
                'total_anomalies': total_anomalies,
                'high_priority_anomalies': high_priority_count,
                'unresolved_anomalies': unresolved_count
            }
        }

    def get_achievements(self) -> dict:
        """
        Determine which achievements are unlocked based on anomaly data
        Priority system: 1 = Highest (most impressive), 5 = Lowest (basic)
        """
        # Check for perfect warehouse (all zero-anomaly achievements)
        all_zero_anomaly_unlocked = all([
            self._check_no_anomaly_pattern(r'forgotten.*pallet|stagnant.*RECEIVING', case_insensitive=True),
            self._check_no_anomaly_pattern(r'stuck.*AISLE|transitional.*stuck', case_insensitive=True),
            self._check_no_anomaly_pattern(r'overcapacity|over capacity|capacity.*violation', case_insensitive=True),
            self._check_no_anomaly_pattern(r'lot.*straggler|incomplete.*lot|uncoordinated', case_insensitive=True),
            self._check_no_anomaly_pattern(r'invalid.*location|location.*invalid', case_insensitive=True),
            self._check_no_anomaly_pattern(r'duplicate.*scan|double.*count', case_insensitive=True),
            self._check_no_anomaly_pattern(r'format.*compliance|invalid.*format', case_insensitive=True),
            self._check_no_anomaly_pattern(r'invalid.*location', case_insensitive=True)
        ])

        achievements = [
            # PRIORITY 1: Ultimate achievements (most impressive)
            {
                'id': 12,
                'name': 'Perfect Warehouse',
                'icon': '🏆',
                'description': 'Zero anomalies across all categories',
                'unlocked': len(self.anomalies) == 0,
                'priority': 1
            },
            {
                'id': 13,
                'name': 'Warehouse Mastery',
                'icon': '👑',
                'description': 'All zero-anomaly achievements unlocked',
                'unlocked': all_zero_anomaly_unlocked,
                'priority': 1
            },

            # PRIORITY 2: High-value operational achievements
            {
                'id': 6,
                'name': 'Efficient Space',
                'icon': '📊',
                'description': 'Utilization in optimal 70-85% range',
                'unlocked': self._check_capacity_optimal(),
                'priority': 2
            },
            {
                'id': 3,
                'name': 'Perfect Capacity',
                'icon': '⚖️',
                'description': 'No overcapacity violations',
                'unlocked': self._check_no_anomaly_pattern(r'overcapacity|over capacity|capacity.*violation', case_insensitive=True),
                'priority': 2
            },

            # PRIORITY 3: Core operational achievements
            {
                'id': 1,
                'name': 'Clean Receiving',
                'icon': '📦',
                'description': 'Zero forgotten pallets detected',
                'unlocked': self._check_no_anomaly_pattern(r'forgotten.*pallet|stagnant.*RECEIVING', case_insensitive=True),
                'priority': 3
            },
            {
                'id': 2,
                'name': 'Clear AISLE Flow',
                'icon': '🚛',
                'description': 'Zero stuck pallets in transitional areas',
                'unlocked': self._check_no_anomaly_pattern(r'stuck.*AISLE|transitional.*stuck', case_insensitive=True),
                'priority': 3
            },
            {
                'id': 5,
                'name': 'Data Champion',
                'icon': '🎯',
                'description': '100% location validation rate',
                'unlocked': self._check_no_anomaly_pattern(r'invalid.*location|location.*invalid', case_insensitive=True),
                'priority': 3
            },

            # PRIORITY 4: Quality achievements
            {
                'id': 4,
                'name': 'Zero Stragglers',
                'icon': '📋',
                'description': 'No incomplete lots detected',
                'unlocked': self._check_no_anomaly_pattern(r'lot.*straggler|incomplete.*lot|uncoordinated', case_insensitive=True),
                'priority': 4
            },
            {
                'id': 7,
                'name': 'Perfect Scan',
                'icon': '🔍',
                'description': 'No duplicate scans detected',
                'unlocked': self._check_no_anomaly_pattern(r'duplicate.*scan|double.*count', case_insensitive=True),
                'priority': 4
            },
            {
                'id': 8,
                'name': 'Format Master',
                'icon': '✓',
                'description': '100% location format compliance',
                'unlocked': self._check_no_anomaly_pattern(r'format.*compliance|invalid.*format', case_insensitive=True),
                'priority': 4
            },
            {
                'id': 9,
                'name': 'Zero Invalid',
                'icon': '🛡️',
                'description': 'No invalid location errors',
                'unlocked': self._check_no_anomaly_pattern(r'invalid.*location', case_insensitive=True),
                'priority': 4
            },

            # PRIORITY 5: Performance/milestone achievements
            {
                'id': 11,
                'name': 'Rapid Processing',
                'icon': '🚀',
                'description': 'Processed 500+ records efficiently',
                'unlocked': self.total_pallets >= 500,
                'priority': 5
            },
            {
                'id': 10,
                'name': 'Lightning Fast',
                'icon': '⚡',
                'description': 'Analysis completed in under 2 seconds',
                'unlocked': False,  # Requires performance tracking (future)
                'priority': 5
            }
        ]

        unlocked_count = sum(1 for a in achievements if a['unlocked'])

        # Sort achievements by priority (lowest number = highest priority), then by unlock status
        sorted_achievements = sorted(achievements, key=lambda a: (a['priority'], not a['unlocked']))

        return {
            'unlocked': unlocked_count,
            'total': len(achievements),
            'details': sorted_achievements
        }

    def get_highlights(self) -> list:
        """
        Generate positive metric highlights
        """
        total_pallets = self.total_pallets
        invalid_location_count = self._count_anomaly_pattern(r'invalid.*location', case_insensitive=True)
        valid_locations = max(0, total_pallets - invalid_location_count)
        valid_percentage = int((valid_locations / max(total_pallets, 1)) * 100)

        # Calculate pallets needing attention (pallets with anomalies)
        # We estimate this by assuming each anomaly affects unique pallets
        # This is a conservative estimate - actual count would require pallet-level tracking
        total_anomalies = len(self.anomalies)
        pallets_with_issues = min(total_anomalies, total_pallets)  # Can't exceed total pallets
        issue_percentage = int((pallets_with_issues / max(total_pallets, 1)) * 100)

        # Calculate capacity utilization if warehouse config is available
        capacity_info = self._get_capacity_info()

        highlights = [
            {
                'icon': '✅',
                'number': valid_locations,
                'title': 'Pallets Properly Placed',
                'percentage': int((valid_locations / max(total_pallets, 1)) * 100),
                'context': 'Most inventory is exactly where it should be'
            },
            {
                'icon': '⚠️',
                'number': pallets_with_issues,
                'title': 'Pallets Need Attention',
                'percentage': issue_percentage,
                'context': 'Pallets with issues requiring action'
            }
        ]

        # Add capacity highlight if available
        if capacity_info:
            highlights.append({
                'icon': '🏪',
                'number': capacity_info['utilization_percentage'],
                'title': 'Capacity Utilized',
                'percentage': None,
                'context': f"{capacity_info['available_locations']} locations available for growth"
            })
        else:
            # Fallback without warehouse config
            highlights.append({
                'icon': '🏪',
                'number': f"{total_pallets}",
                'title': 'Pallets Tracked',
                'percentage': None,
                'context': 'All inventory accounted for'
            })

        return highlights

    def get_problem_scorecard(self) -> list:
        """
        Count problems by category with priority levels
        """
        scorecard = [
            {
                'type': 'Stagnant Pallets',
                'detected': self._count_anomaly_pattern(r'^stagnant pallet|forgotten.*pallet', case_insensitive=True),
                'priority': 'HIGH',
                'color': '#C53030',
                'bg': '#FED7D7'
            },
            {
                'type': 'Location Issues',
                'detected': self._count_anomaly_pattern(r'location.*specific.*stagnant|stuck.*AISLE|transitional', case_insensitive=True),
                'priority': 'HIGH',
                'color': '#C53030',
                'bg': '#FED7D7'
            },
            {
                'type': 'Overcapacity',
                'detected': self._count_anomaly_pattern(r'storage.*overcapacity', case_insensitive=True),
                'priority': 'MEDIUM',
                'color': '#B7791F',
                'bg': '#FFFBEB'
            },
            {
                'type': 'Invalid Locations',
                'detected': self._count_anomaly_pattern(r'invalid.*location', case_insensitive=True),
                'priority': 'HIGH',
                'color': '#C53030',
                'bg': '#FED7D7'
            },
            {
                'type': 'Duplicate Scans',
                'detected': self._count_anomaly_pattern(r'duplicate.*scan|double.*count', case_insensitive=True),
                'priority': 'LOW',
                'color': '#276749',
                'bg': '#F0FFF4'
            },
            {
                'type': 'Special Area Issues',
                'detected': self._count_anomaly_pattern(r'special.*area.*capacity', case_insensitive=True),
                'priority': 'MEDIUM',
                'color': '#B7791F',
                'bg': '#FFFBEB'
            }
        ]

        return scorecard

    def get_resolution_tracker(self) -> dict:
        """
        Track resolution progress by anomaly category
        """
        categories = [
            ('Stagnant Pallets', '📦', r'^stagnant pallet|forgotten.*pallet'),
            ('Location Issues', '🚛', r'location.*specific.*stagnant|stuck.*AISLE|transitional'),
            ('Overcapacity Issues', '⚖️', r'storage.*overcapacity'),
            ('Invalid Locations', '🛡️', r'invalid.*location'),
            ('Duplicate Scans', '🔄', r'duplicate.*scan|double.*count'),
            ('Special Area Issues', '⚠️', r'special.*area.*capacity')
        ]

        tracker = []
        for category_name, icon, pattern in categories:
            anomalies = self._get_anomalies_by_pattern(pattern, case_insensitive=True)
            total = len(anomalies)
            resolved = sum(1 for a in anomalies if a.status in ['Resolved', 'Cleared'])

            # Get last resolved timestamp
            last_resolved = None
            for anomaly in anomalies:
                if anomaly.status in ['Resolved', 'Cleared']:
                    history = AnomalyHistory.query.filter_by(
                        anomaly_id=anomaly.id
                    ).filter(
                        AnomalyHistory.new_status.in_(['Resolved', 'Cleared'])
                    ).order_by(AnomalyHistory.timestamp.desc()).first()

                    if history and (not last_resolved or history.timestamp > last_resolved):
                        last_resolved = history.timestamp

            # Format last resolved time
            last_resolved_str = self._format_time_ago(last_resolved) if last_resolved else 'Never'

            if total > 0:  # Only include categories with anomalies
                tracker.append({
                    'category': category_name,
                    'icon': icon,
                    'resolved': resolved,
                    'total': total,
                    'lastResolved': last_resolved_str
                })

        return tracker

    def get_special_location_performance(self) -> list:
        """
        Analyze performance by special location categories
        """
        location_categories = [
            ('🏪 RECEIVING AREAS', r'RECV[-_]?\d+', 'forgotten pallets'),
            ('🚛 AISLE/TRANSITIONAL', r'AISLE[-_]?\d+', 'stuck pallets'),
            ('📦 DOCK AREAS', r'DOCK[-_]?\d+', 'capacity issues'),
            ('🎯 STAGING ZONES', r'STAG(?:ING)?[-_]?\d+', 'staging delays')
        ]

        results = []
        for category_name, location_pattern, issue_type in location_categories:
            locations = self._analyze_location_category(location_pattern, issue_type)
            if locations:
                results.append({
                    'category': category_name,
                    'locations': locations
                })

        return results

    def get_operational_impact(self) -> dict:
        """
        Calculate operational impact metrics
        """
        total_anomalies = len(self.anomalies)
        resolved_count = sum(1 for a in self.anomalies if a.status in ['Resolved', 'Cleared'])

        return {
            'analysis_completed': {
                'icon': '📊',
                'title': 'Analysis Completed',
                'description': f"{self.total_pallets} pallets processed successfully"
            },
            'problems_prevented': {
                'icon': '🎯',
                'title': 'Problems Prevented',
                'description': f"{total_anomalies} issues caught before becoming urgent"
            },
            'issues_resolved': {
                'icon': '✅',
                'title': 'Issues Resolved',
                'description': f"{resolved_count} problems fixed and cleared"
            },
            'processing_efficiency': {
                'icon': '⚡',
                'title': 'Processing Efficiency',
                'description': f"{self.total_pallets} records analyzed (Excellent)"
            }
        }

    # Helper methods

    def _get_anomaly_priority(self, description: str) -> str:
        """Determine priority based on description keywords"""
        desc_lower = description.lower()
        if any(word in desc_lower for word in ['forgotten', 'stuck', 'invalid location']):
            return 'HIGH'
        elif any(word in desc_lower for word in ['overcapacity', 'straggler']):
            return 'MEDIUM'
        else:
            return 'LOW'

    def _check_no_anomaly_pattern(self, pattern: str, case_insensitive: bool = True) -> bool:
        """Check if no anomalies match the given pattern"""
        return self._count_anomaly_pattern(pattern, case_insensitive) == 0

    def _count_anomaly_pattern(self, pattern: str, case_insensitive: bool = True) -> int:
        """Count anomalies matching a regex pattern"""
        flags = re.IGNORECASE if case_insensitive else 0
        regex = re.compile(pattern, flags)
        return sum(1 for a in self.anomalies if regex.search(a.description))

    def _get_anomalies_by_pattern(self, pattern: str, case_insensitive: bool = True) -> list:
        """Get all anomalies matching a regex pattern"""
        flags = re.IGNORECASE if case_insensitive else 0
        regex = re.compile(pattern, flags)
        return [a for a in self.anomalies if regex.search(a.description)]

    def _check_capacity_optimal(self) -> bool:
        """Check if capacity utilization is in optimal 70-85% range"""
        capacity_info = self._get_capacity_info()
        if capacity_info:
            utilization = capacity_info['utilization_numeric']  # Use numeric value
            return 70 <= utilization <= 85
        return False

    def _get_capacity_info(self) -> dict:
        """Get warehouse capacity information"""
        if not self.report.warehouse_id:
            return None

        config = WarehouseConfig.query.filter_by(
            warehouse_id=self.report.warehouse_id,
            is_active=True
        ).first()

        if not config:
            return None

        total_capacity = config.calculate_total_capacity()
        occupied = self.total_pallets
        available = max(0, total_capacity - occupied)
        utilization = (occupied / max(total_capacity, 1)) * 100

        return {
            'total_capacity': total_capacity,
            'occupied': occupied,
            'available_locations': available,
            'utilization_percentage': f"{utilization:.1f}%",  # Formatted string for display
            'utilization_numeric': utilization  # Raw number for comparisons
        }

    def _analyze_location_category(self, location_pattern: str, issue_type: str) -> list:
        """Analyze specific location category for issues"""
        regex = re.compile(location_pattern, re.IGNORECASE)
        location_issues = {}

        # Search for locations in anomaly descriptions and details
        for anomaly in self.anomalies:
            search_text = f"{anomaly.description} {anomaly.details or ''}"
            matches = regex.findall(search_text)

            for location_code in matches:
                location_code = location_code.upper()
                if location_code not in location_issues:
                    location_issues[location_code] = 0
                location_issues[location_code] += 1

        # Format results
        locations = []
        for loc_code, issue_count in sorted(location_issues.items()):
            locations.append({
                'name': loc_code,
                'status': 'clean' if issue_count == 0 else 'warning',
                'issues': issue_count,
                'description': issue_type if issue_count > 0 else None
            })

        # Add clean locations if we have warehouse config
        if not locations and self.report.warehouse_id:
            # Show at least one clean location as example
            locations.append({
                'name': f"{location_pattern.split('[')[0]}01",
                'status': 'clean',
                'issues': 0
            })

        return locations[:5]  # Limit to 5 locations per category

    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as time ago (e.g., '5 minutes ago')"""
        if not timestamp:
            return 'Never'

        now = datetime.utcnow()
        diff = now - timestamp

        seconds = diff.total_seconds()
        if seconds < 60:
            return 'Just now'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"


# API Endpoints

@wins_bp.route('/<int:report_id>/wins', methods=['GET'])
@token_required
def get_wins_data(current_user, report_id):
    """
    Get Track Your Wins data for a specific analysis report

    GET /api/v1/reports/:report_id/wins
    """
    try:
        # Get the report
        report = AnalysisReport.query.filter_by(
            id=report_id,
            user_id=current_user.id
        ).first()

        if not report:
            return jsonify({'error': 'Report not found'}), 404

        # Create analyzer
        analyzer = WinsAnalyzer(report)

        # Generate all metrics
        health_score = analyzer.calculate_health_score()
        achievements = analyzer.get_achievements()
        highlights = analyzer.get_highlights()
        problem_scorecard = analyzer.get_problem_scorecard()
        resolution_tracker = analyzer.get_resolution_tracker()
        special_locations = analyzer.get_special_location_performance()
        operational_impact = analyzer.get_operational_impact()

        # Calculate total issues
        total_issues = sum(item['detected'] for item in problem_scorecard)
        total_resolved = sum(item['resolved'] for item in resolution_tracker)
        total_to_resolve = sum(item['total'] for item in resolution_tracker)

        response_data = {
            'report_id': report_id,
            'report_name': report.report_name,
            'timestamp': report.timestamp.isoformat(),
            'health_score': health_score,
            'achievements': achievements,
            'highlights': highlights,
            'problem_scorecard': problem_scorecard,
            'resolution_tracker': {
                'categories': resolution_tracker,
                'total_resolved': total_resolved,
                'total_to_resolve': total_to_resolve,
                'resolution_percentage': int((total_resolved / max(total_to_resolve, 1)) * 100)
            },
            'special_locations': special_locations,
            'operational_impact': operational_impact,
            'totals': {
                'total_pallets': analyzer.total_pallets,
                'total_anomalies': len(analyzer.anomalies),
                'total_issues_detected': total_issues,
                'total_resolved': total_resolved
            }
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': f'Failed to generate wins data: {str(e)}'}), 500


@wins_bp.route('/latest/wins', methods=['GET'])
@token_required
def get_latest_wins_data(current_user):
    """
    Get Track Your Wins data for the user's most recent analysis report

    GET /api/v1/reports/latest/wins
    """
    try:
        # Get the most recent report
        report = AnalysisReport.query.filter_by(
            user_id=current_user.id
        ).order_by(AnalysisReport.timestamp.desc()).first()

        if not report:
            return jsonify({
                'error': 'No reports found',
                'message': 'Please run an analysis first to see your wins'
            }), 404

        # Use the report ID to generate wins data (same logic as get_wins_data)
        report_id = report.id

        # Create analyzer
        analyzer = WinsAnalyzer(report)

        # Generate all metrics
        health_score = analyzer.calculate_health_score()
        achievements = analyzer.get_achievements()
        highlights = analyzer.get_highlights()
        problem_scorecard = analyzer.get_problem_scorecard()
        resolution_tracker = analyzer.get_resolution_tracker()
        special_locations = analyzer.get_special_location_performance()
        operational_impact = analyzer.get_operational_impact()

        # Calculate total issues
        total_issues = sum(item['detected'] for item in problem_scorecard)
        total_resolved = sum(item['resolved'] for item in resolution_tracker)
        total_to_resolve = sum(item['total'] for item in resolution_tracker)

        response_data = {
            'report_id': report_id,
            'report_name': report.report_name,
            'timestamp': report.timestamp.isoformat(),
            'health_score': health_score,
            'achievements': achievements,
            'highlights': highlights,
            'problem_scorecard': problem_scorecard,
            'resolution_tracker': {
                'categories': resolution_tracker,
                'total_resolved': total_resolved,
                'total_to_resolve': total_to_resolve,
                'resolution_percentage': int((total_resolved / max(total_to_resolve, 1)) * 100)
            },
            'special_locations': special_locations,
            'operational_impact': operational_impact,
            'totals': {
                'total_pallets': analyzer.total_pallets,
                'total_anomalies': len(analyzer.anomalies),
                'total_issues_detected': total_issues,
                'total_resolved': total_resolved
            }
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve latest wins: {str(e)}'}), 500
