"""
Debug script to check user templates and warehouse associations
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://ware_eng_db_user:fqvKdOGZEt1CGIeLF4J1AG8RTtCv0Zdu@dpg-d23244fg127c73fga10g-a.ohio-postgres.render.com/ware_eng_db'

from sqlalchemy import create_engine, text

engine = create_engine(os.environ['DATABASE_URL'])

print("=== Debugging User Templates and Warehouses ===\n")

with engine.connect() as conn:
    # Get user mtest
    result = conn.execute(text("SELECT id, username FROM users WHERE username = 'mtest'"))
    user = result.fetchone()

    if not user:
        print("❌ User 'mtest' not found!")
        exit(1)

    user_id = user[0]
    print(f"✓ User 'mtest' found: id={user_id}\n")

    # Get all templates for this user
    result2 = conn.execute(text("""
        SELECT id, name, template_code, created_by, is_active, created_at
        FROM warehouse_template
        WHERE created_by = :uid
        ORDER BY created_at DESC
    """), {'uid': user_id})
    templates = result2.fetchall()

    print(f"📋 Templates created by mtest (user_id={user_id}): {len(templates)}")
    for t in templates:
        active_status = "✓ ACTIVE" if t[4] else "✗ INACTIVE"
        print(f"  {active_status} | ID: {t[0]} | {t[1]:30s} | Code: {t[2]} | Created: {t[5]}")

    # Get all warehouse configs
    result3 = conn.execute(text("""
        SELECT warehouse_id, warehouse_name, created_by, created_at
        FROM warehouse_config
        ORDER BY created_at DESC
        LIMIT 10
    """))
    configs = result3.fetchall()

    print(f"\n🏢 Recent warehouse configs (last 10):")
    for c in configs:
        owner_mark = "👤 mtest's" if c[2] == user_id else f"   user_{c[2]}"
        print(f"  {owner_mark} | {c[0]:20s} | {c[1]:30s} | Created: {c[3]}")

    # Check if USER_MTEST warehouse exists
    result4 = conn.execute(text("""
        SELECT warehouse_id, warehouse_name, created_by
        FROM warehouse_config
        WHERE warehouse_id LIKE :pattern
    """), {'pattern': 'USER_M%'})
    user_mtest_configs = result4.fetchall()

    print(f"\n🔍 Warehouses matching 'USER_M*': {len(user_mtest_configs)}")
    for c in user_mtest_configs:
        owner_mark = "👤 mtest's" if c[2] == user_id else f"user_{c[2]}"
        print(f"  {owner_mark} | {c[0]} | {c[1]}")

    # Check DEFAULT warehouse
    result5 = conn.execute(text("""
        SELECT warehouse_id, warehouse_name, created_by
        FROM warehouse_config
        WHERE warehouse_id = 'DEFAULT'
    """))
    default_config = result5.fetchone()

    if default_config:
        owner_mark = "👤 mtest's" if default_config[2] == user_id else f"user_{default_config[2]}"
        print(f"\n📦 DEFAULT warehouse exists:")
        print(f"  {owner_mark} | {default_config[0]} | {default_config[1]}")
    else:
        print(f"\n⚠️ DEFAULT warehouse does NOT exist")

    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"User 'mtest' (ID={user_id}):")
    print(f"  - Has {len(templates)} templates")
    print(f"  - Has {len([c for c in configs if c[2] == user_id])} warehouses in recent configs")
    print(f"  - USER_MTEST* warehouses: {len(user_mtest_configs)}")

    if len(templates) >= 5:
        print(f"\n⚠️  ISSUE: User has {len(templates)} templates (limit is 5)")
        print(f"  This is why 'Maximum template limit reached' error appears!")

    if not user_mtest_configs:
        print(f"\n⚠️  ISSUE: No USER_MTEST warehouse found!")
        print(f"  Backend will return 'DEFAULT' as fallback")
