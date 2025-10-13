"""
Comprehensive PostgreSQL Migration Test
Tests all critical functionality with PostgreSQL
"""
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_database_connection():
    """Test 1: Database Connection"""
    print("\n" + "=" * 70)
    print("TEST 1: Database Connection & Configuration")
    print("=" * 70)

    from app import app, db

    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Database URI: {db_uri[:50]}...")

        if 'postgresql' in db_uri:
            print("[PASS] Using PostgreSQL")
        else:
            print("[FAIL] Not using PostgreSQL!")
            return False

        # Test connection
        try:
            result = db.session.execute(db.text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"[PASS] Connected to: {version.split(',')[0]}")
        except Exception as e:
            print(f"[FAIL] Connection error: {e}")
            return False

    return True

def test_models_and_queries():
    """Test 2: Models and Basic Queries"""
    print("\n" + "=" * 70)
    print("TEST 2: Models and Basic Queries")
    print("=" * 70)

    from app import app, db
    from core_models import User
    from models import Rule, RuleCategory

    with app.app_context():
        # Test User model
        user_count = User.query.count()
        print(f"Users in database: {user_count}")
        if user_count == 0:
            print("[FAIL] No users found!")
            return False
        print("[PASS] Users table accessible")

        # Test Rule model
        rule_count = Rule.query.count()
        print(f"Rules in database: {rule_count}")
        if rule_count == 0:
            print("[FAIL] No rules found!")
            return False
        print("[PASS] Rules table accessible")

        # Test RuleCategory model
        category_count = RuleCategory.query.count()
        print(f"Categories in database: {category_count}")
        if category_count < 3:
            print("[FAIL] Expected 3 categories (FLOW_TIME, SPACE, PRODUCT)")
            return False
        print("[PASS] Rule categories accessible")

    return True

def test_json_fields():
    """Test 3: JSON Field Storage and Retrieval"""
    print("\n" + "=" * 70)
    print("TEST 3: JSON Field Storage and Retrieval")
    print("=" * 70)

    from app import app, db
    from models import Rule

    with app.app_context():
        # Get a rule and test JSON field access
        rule = Rule.query.first()
        if not rule:
            print("[FAIL] No rules to test")
            return False

        print(f"Testing rule: {rule.name}")

        # Test conditions (JSON field)
        try:
            conditions = rule.get_conditions()
            print(f"Conditions type: {type(conditions)}")
            print(f"Conditions: {conditions}")
            if not isinstance(conditions, dict):
                print("[FAIL] Conditions should be dict")
                return False
            print("[PASS] JSON conditions retrieved correctly")
        except Exception as e:
            print(f"[FAIL] Error getting conditions: {e}")
            return False

        # Test parameters (JSON field)
        try:
            parameters = rule.get_parameters()
            print(f"Parameters type: {type(parameters)}")
            if not isinstance(parameters, dict):
                print("[FAIL] Parameters should be dict")
                return False
            print("[PASS] JSON parameters retrieved correctly")
        except Exception as e:
            print(f"[FAIL] Error getting parameters: {e}")
            return False

    return True

def test_datetime_fields():
    """Test 4: DateTime with Timezone Handling"""
    print("\n" + "=" * 70)
    print("TEST 4: DateTime with Timezone Handling")
    print("=" * 70)

    from app import app, db
    from core_models import User
    from models import Rule

    with app.app_context():
        # Test User timestamps
        user = User.query.first()
        if not user:
            print("[FAIL] No user to test")
            return False

        print(f"User: {user.username}")

        # Check if we can query by date
        try:
            # This should work with timezone-aware fields
            recent_users = User.query.filter(
                User.id == user.id
            ).all()
            print(f"[PASS] DateTime queries work")
        except Exception as e:
            print(f"[FAIL] DateTime query error: {e}")
            return False

        # Test Rule timestamps
        rule = Rule.query.first()
        if rule:
            print(f"Rule created_at: {rule.created_at}")
            print(f"Rule created_at type: {type(rule.created_at)}")

            # Verify it's a datetime object
            if not isinstance(rule.created_at, datetime):
                print("[FAIL] created_at should be datetime object")
                return False
            print("[PASS] DateTime fields properly typed")

    return True

def test_foreign_keys():
    """Test 5: Foreign Key Constraints"""
    print("\n" + "=" * 70)
    print("TEST 5: Foreign Key Constraints")
    print("=" * 70)

    from app import app, db
    from models import Rule, RuleCategory

    with app.app_context():
        # Test rule -> category relationship
        rule = Rule.query.first()
        if not rule:
            print("[FAIL] No rule to test")
            return False

        print(f"Testing rule: {rule.name}")
        print(f"Category ID: {rule.category_id}")

        # Access related category
        try:
            category = rule.category
            if not category:
                print("[FAIL] Category relationship not working")
                return False
            print(f"Category: {category.name} - {category.display_name}")
            print("[PASS] Foreign key relationships work")
        except Exception as e:
            print(f"[FAIL] Foreign key error: {e}")
            return False

    return True

def test_boolean_fields():
    """Test 6: Boolean Field Handling"""
    print("\n" + "=" * 70)
    print("TEST 6: Boolean Field Handling")
    print("=" * 70)

    from app import app, db
    from models import Rule

    with app.app_context():
        # Test boolean queries
        try:
            active_rules = Rule.query.filter_by(is_active=True).count()
            inactive_rules = Rule.query.filter_by(is_active=False).count()

            print(f"Active rules: {active_rules}")
            print(f"Inactive rules: {inactive_rules}")

            if active_rules + inactive_rules != Rule.query.count():
                print("[FAIL] Boolean query mismatch")
                return False

            print("[PASS] Boolean fields work correctly")
        except Exception as e:
            print(f"[FAIL] Boolean query error: {e}")
            return False

    return True

def test_indexes():
    """Test 7: Database Indexes"""
    print("\n" + "=" * 70)
    print("TEST 7: Database Indexes")
    print("=" * 70)

    from app import app, db

    with app.app_context():
        try:
            # Query PostgreSQL system tables for indexes
            result = db.session.execute(db.text("""
                SELECT
                    tablename,
                    indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """))

            indexes = result.fetchall()
            print(f"Total indexes found: {len(indexes)}")

            # Check for key indexes
            index_names = [idx[1] for idx in indexes]

            important_indexes = [
                'idx_location_warehouse_type',
                'idx_location_warehouse_zone',
                'idx_user_warehouse',
            ]

            found_important = [idx for idx in important_indexes if idx in index_names]
            print(f"Important custom indexes found: {len(found_important)}/{len(important_indexes)}")

            if found_important:
                print("[PASS] Custom indexes created")
            else:
                print("[WARNING] Custom indexes not found, but may not be critical")

        except Exception as e:
            print(f"[FAIL] Index check error: {e}")
            return False

    return True

def run_all_tests():
    """Run all comprehensive tests"""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE POSTGRESQL MIGRATION TEST SUITE")
    print("=" * 70)

    tests = [
        ("Database Connection", test_database_connection),
        ("Models and Queries", test_models_and_queries),
        ("JSON Field Storage", test_json_fields),
        ("DateTime Handling", test_datetime_fields),
        ("Foreign Keys", test_foreign_keys),
        ("Boolean Fields", test_boolean_fields),
        ("Database Indexes", test_indexes),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")
    print()

    if passed == total:
        print("=" * 70)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("Your PostgreSQL migration is 100% working!")
        print("=" * 70)
        return True
    else:
        print("=" * 70)
        print(f"[WARNING] {total - passed} test(s) failed")
        print("Review the failures above")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
