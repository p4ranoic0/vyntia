import psycopg2

# Try minimal connection without SSL
print('Test 1: Minimal connection, no SSL...')
try:
    conn = psycopg2.connect(dbname='bd_rrhh_intranet', user='postgres', password='postgres', host='localhost', port='5432', sslmode='disable')
    print('Connected!')
    cur = conn.cursor()
    cur.execute('SHOW server_encoding')
    print('server_encoding:', cur.fetchone())
    cur.execute('SHOW client_encoding')
    print('client_encoding:', cur.fetchone())
    cur.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

print()
print('Test 2: With sslmode=prefer...')
try:
    conn = psycopg2.connect(dbname='bd_rrhh_intranet', user='postgres', password='postgres', host='localhost', port='5432', sslmode='prefer')
    print('Connected!')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
