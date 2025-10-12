#!/usr/bin/env python
"""Test script for wins API"""
import sys
sys.path.insert(0, 'src')

from database import db
from core_models import AnalysisReport, User
from src.wins_api import WinsAnalyzer
from app import app

def test_wins_analyzer():
    with app.app_context():
        # Get latest report
        report = AnalysisReport.query.order_by(AnalysisReport.timestamp.desc()).first()

        if not report:
            print("No reports found in database")
            return

        print(f"Testing report ID: {report.id}")
        print(f"User ID: {report.user_id}")
        print(f"Inventory count: {report.inventory_count}")
        print(f"Anomaly count: {len(report.anomalies)}")

        try:
            # Create analyzer
            analyzer = WinsAnalyzer(report)

            # Test each method
            print("\n1. Testing health score calculation...")
            health_score = analyzer.calculate_health_score()
            print(f"   OK Health Score: {health_score['score']}")

            print("\n2. Testing achievements...")
            achievements = analyzer.get_achievements()
            print(f"   OK Achievements: {achievements['unlocked']}/{achievements['total']}")

            print("\n3. Testing highlights...")
            highlights = analyzer.get_highlights()
            print(f"   OK Highlights: {len(highlights)} items")

            print("\n4. Testing problem scorecard...")
            scorecard = analyzer.get_problem_scorecard()
            print(f"   OK Problem Scorecard: {len(scorecard)} categories")

            print("\n5. Testing resolution tracker...")
            tracker = analyzer.get_resolution_tracker()
            print(f"   OK Resolution Tracker: {len(tracker)} categories")

            print("\n6. Testing special locations...")
            locations = analyzer.get_special_location_performance()
            print(f"   OK Special Locations: {len(locations)} categories")

            print("\n7. Testing operational impact...")
            impact = analyzer.get_operational_impact()
            print(f"   OK Operational Impact: {len(impact)} metrics")

            print("\nSUCCESS All tests passed!")

        except Exception as e:
            print(f"\nERROR Error occurred:")
            print(f"   {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_wins_analyzer()
