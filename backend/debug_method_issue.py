"""
Debug script to understand why _assign_location_types_with_context is not found
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_rule_engine_methods():
    try:
        from rule_engine import RuleEngine
        import inspect

        # Create instance
        rule_engine = RuleEngine(db_session=None, app=None)

        print("=== DEBUGGING RULE ENGINE METHODS ===")
        print(f"RuleEngine class: {RuleEngine}")
        print(f"RuleEngine instance: {rule_engine}")

        # Check all attributes
        all_attrs = dir(rule_engine)
        location_attrs = [attr for attr in all_attrs if 'location' in attr.lower()]

        print(f"\nAll attributes containing 'location':")
        for attr in location_attrs:
            attr_obj = getattr(rule_engine, attr)
            attr_type = type(attr_obj).__name__
            print(f"  {attr}: {attr_type}")

        # Check if the method name exists as attribute
        method_name = '_assign_location_types_with_context'

        print(f"\nChecking for method: {method_name}")
        print(f"hasattr result: {hasattr(rule_engine, method_name)}")
        print(f"In dir(): {method_name in dir(rule_engine)}")

        # Try to get the attribute directly
        try:
            method = getattr(rule_engine, method_name)
            print(f"getattr result: {method}")
            print(f"Method type: {type(method)}")
        except AttributeError as e:
            print(f"getattr failed: {e}")

        # Check class vs instance
        print(f"\nClass vs Instance check:")
        print(f"hasattr on class: {hasattr(RuleEngine, method_name)}")

        if hasattr(RuleEngine, method_name):
            class_method = getattr(RuleEngine, method_name)
            print(f"Class method: {class_method}")
            print(f"Class method type: {type(class_method)}")

        # Look for similar methods
        print(f"\nSimilar method names:")
        assign_methods = [attr for attr in all_attrs if 'assign' in attr.lower()]
        for method in assign_methods:
            print(f"  {method}")

        return rule_engine

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_rule_engine_methods()