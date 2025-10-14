import os
os.environ['DATABASE_URL'] = 'postgresql://ware_eng_db_user:fqvKdOGZEt1CGIeLF4J1AG8RTtCv0Zdu@dpg-d23244fg127c73fga10g-a.ohio-postgres.render.com/ware_eng_db'

from sqlalchemy import create_engine, text

engine = create_engine(os.environ['DATABASE_URL'])

with engine.connect() as conn:
    # Get user mtest
    result = conn.execute(text("SELECT id, username FROM users WHERE username = 'mtest'"))
    user = result.fetchone()

    if user:
        user_id = user[0]
        print(f'✓ User mtest found: id={user_id}')
    else:
        print('✗ User mtest not found!')
        exit(1)

    # Get all warehouses
    result2 = conn.execute(text('SELECT warehouse_id, warehouse_name, created_by FROM warehouse_config'))
    warehouses = result2.fetchall()

    print(f'\n📦 All warehouses in database ({len(warehouses)}):')
    for w in warehouses:
        print(f'  - {w[0]:20s} | name: {w[1]:30s} | created_by: {w[2]}')

    # Get warehouses created by mtest
    result3 = conn.execute(text('SELECT warehouse_id, warehouse_name FROM warehouse_config WHERE created_by = :uid'), {'uid': user_id})
    user_warehouses = result3.fetchall()

    print(f'\n🏢 Warehouses created by mtest (user_id={user_id}): {len(user_warehouses)}')
    for w in user_warehouses:
        print(f'  - {w[0]} | {w[1]}')

    # Check if USER_MTEST exists
    result4 = conn.execute(text("SELECT warehouse_id, created_by FROM warehouse_config WHERE warehouse_id LIKE 'USER_M%'"))
    user_mtest_warehouses = result4.fetchall()

    print(f'\n🔍 Warehouses matching USER_M* pattern: {len(user_mtest_warehouses)}')
    for w in user_mtest_warehouses:
        print(f'  - {w[0]} | created_by: {w[1]}')
