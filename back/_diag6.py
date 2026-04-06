import ctypes, os

# Force the locale for this process to use UTF-8
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['LC_ALL'] = 'C'  
os.environ['LANG'] = 'C'

import psycopg2

# Try with raw bytes error handling
print('Trying connection with locale override...')
try:
    conn = psycopg2.connect(dbname='bd_rrhh_intranet', user='postgres', password='postgres', host='localhost', port='5432')
    print('Connected!')
    conn.close()
except UnicodeDecodeError as ude:
    print(f'UnicodeDecodeError: {ude}')
    # Try to get the raw bytes
    print(f'  encoding: {ude.encoding}')
    print(f'  reason: {ude.reason}')
    print(f'  start: {ude.start}')
    print(f'  end: {ude.end}')
    raw = ude.object
    print(f'  object type: {type(raw)}')
    print(f'  object repr (first 200): {repr(raw[:200])}')
    # Decode with cp1252 to see the actual message
    try:
        decoded = raw.decode('cp1252')
        print(f'  decoded cp1252: {decoded}')
    except:
        pass
except Exception as e:
    print(f'Other error: {e}')
