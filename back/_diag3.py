import os, sys
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE']='config.settings.development'
import django
django.setup()

# Try direct psycopg2 connection to see the full DSN
import psycopg2
from django.conf import settings
db = settings.DATABASES['default']

dsn = f"dbname={db['NAME']} user={db['USER']} password={db['PASSWORD']} host={db['HOST']} port={db['PORT']} sslmode=prefer connect_timeout=10 client_encoding=UTF8"
print('DSN repr:', repr(dsn))
print('DSN len:', len(dsn))

# Check each byte
dsn_bytes = dsn.encode('utf-8')
print('DSN bytes len:', len(dsn_bytes))
for i in range(max(0, 80), min(len(dsn_bytes), 95)):
    print(f'  byte[{i}]: {hex(dsn_bytes[i])} = {chr(dsn_bytes[i]) if dsn_bytes[i] < 128 else "?"}')

print()
print('Attempting direct connection...')
try:
    conn = psycopg2.connect(dsn)
    print('Connected!')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
