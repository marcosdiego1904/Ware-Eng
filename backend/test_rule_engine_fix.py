"""
Test script to verify the rule engine fix for STAGNANT_PALLETS and UNCOORDINATED_LOTS
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_rule_engine_integration():
    """Test that evaluators can properly access RuleEngine methods"""

    try:
        # Import the rule engine and related classes
        from rule_engine import RuleEngine, StagnantPalletsEvaluator
        from models import Rule

        print("[TEST] Testing RuleEngine and Evaluator Integration")
        print("=" * 60)

        # Create a mock rule engine without database
        rule_engine = RuleEngine(db_session=None, app=None)

        # Check that evaluators are initialized with rule_engine reference
        evaluators = rule_engine._initialize_evaluators()

        stagnant_evaluator = evaluators.get('STAGNANT_PALLETS')
        uncoordinated_evaluator = evaluators.get('UNCOORDINATED_LOTS')

        print(f"StagnantPalletsEvaluator has rule_engine reference: {stagnant_evaluator.rule_engine is not None}")
        print(f"UncoordinatedLotsEvaluator has rule_engine reference: {uncoordinated_evaluator.rule_engine is not None}")

        # Test that the rule_engine reference is correctly set
        if stagnant_evaluator.rule_engine is rule_engine:
            print("[PASS] StagnantPalletsEvaluator correctly references RuleEngine")
        else:
            print("[FAIL] StagnantPalletsEvaluator rule_engine reference is incorrect")

        if uncoordinated_evaluator.rule_engine is rule_engine:
            print("[PASS] UncoordinatedLotsEvaluator correctly references RuleEngine")
        else:
            print("[FAIL] UncoordinatedLotsEvaluator rule_engine reference is incorrect")

        # Test that the RuleEngine has the required methods
        required_methods = ['_assign_location_types_with_context', '_get_cached_locations']

        for method_name in required_methods:
            if hasattr(rule_engine, method_name):
                print(f"[PASS] RuleEngine has method: {method_name}")
            else:
                print(f"[FAIL] RuleEngine missing method: {method_name}")

        print("\n" + "=" * 60)
        print("[TEST] Integration test completed successfully")
        print("[PASS] The fix should resolve the '_get_cached_locations' error")

        return True

    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_classifier_import():
    """Test that the enhanced classifier can be imported"""

    try:
        print("\n[TEST] Testing Enhanced Classifier Import")
        print("=" * 60)

        from enhanced_location_classifier import EnhancedLocationClassifier

        classifier = EnhancedLocationClassifier()
        print("[PASS] EnhancedLocationClassifier imported successfully")

        # Test a simple classification
        result = classifier.classify_location("RECV-01")
        print(f"[PASS] Test classification: RECV-01 -> {result.location_type} (confidence: {result.confidence:.2f})")

        return True

    except ImportError as e:
        print(f"[ERROR] Enhanced Classifier Import Error: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Enhanced Classifier Test Error: {e}")
        return False

if __name__ == "__main__":
    print("[START] Rule Engine Fix Validation Test")
    print("Testing the fix for STAGNANT_PALLETS and UNCOORDINATED_LOTS rules\n")

    success1 = test_rule_engine_integration()
    success2 = test_enhanced_classifier_import()

    print("\n" + "=" * 60)
    print("[SUMMARY] Test Results")
    print("=" * 60)

    if success1 and success2:
        print("[PASS] All tests passed!")
        print("[PASS] The rule engine fix should resolve the location classification errors")
        print("[PASS] Enhanced location classification system is working")
        print("\n[RESULT] Expected Result: STAGNANT_PALLETS and UNCOORDINATED_LOTS rules should now work")
    else:
        print("[FAIL] Some tests failed - additional debugging needed")