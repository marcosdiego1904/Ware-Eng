"""
Test the virtual engine integration fix
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_virtual_engine_integration():
    """Test that the virtual engine integration handles tuple results correctly"""

    try:
        print("Testing virtual engine integration fix...")

        from enhanced_location_classifier import EnhancedLocationClassifier
        from virtual_location_engine import VirtualLocationEngine

        # Create a simple virtual engine configuration
        warehouse_config = {
            'warehouse_id': 'TEST_WAREHOUSE',
            'num_aisles': 2,
            'racks_per_aisle': 1,
            'positions_per_rack': 22,
            'levels_per_position': 4,
            'level_names': 'ABCD',
            'special_areas': ['RECV-01', 'RECV-02'],
            'default_capacity': 1,
            'default_zone': 'GENERAL'
        }

        # Initialize virtual engine
        virtual_engine = VirtualLocationEngine(warehouse_config)

        # Test what validate_location returns
        test_location = "001A"
        validation_result = virtual_engine.validate_location(test_location)

        print(f"validate_location result type: {type(validation_result)}")
        print(f"validate_location result: {validation_result}")

        # Test enhanced classifier with virtual engine
        classifier = EnhancedLocationClassifier(db_session=None, virtual_engine=virtual_engine)

        # Test the _check_virtual_engine method directly
        result = classifier._check_virtual_engine(test_location)

        if result:
            print(f"Classification result: {result.location_type} (confidence: {result.confidence})")
            print(f"Method: {result.method}")
            print(f"Reasoning: {result.reasoning}")
        else:
            print("No virtual engine classification result")

        print("[SUCCESS] Virtual engine integration test completed without errors!")
        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_virtual_engine_integration()