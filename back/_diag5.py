import psycopg2, locale, sys

print('Python version:', sys.version)
print('psycopg2 version:', psycopg2.__version__)
print('Default encoding:', sys.getdefaultencoding())
print('Filesystem encoding:', sys.getfilesystemencoding())
print('Locale:', locale.getlocale())
print('Preferred encoding:', locale.getpreferredencoding())

# Try connecting to postgres db instead
print()
print('Test: connect to postgres db...')
try:
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='localhost', port='5432')
    print('Connected to postgres!')
    conn.close()
except Exception as e:
    print(f'Error: {e}')

# Check if pg is running
print()
import subprocess
result = subprocess.run(['pg_isready', '-h', 'localhost', '-p', '5432'], capture_output=True, text=True)
print('pg_isready:', result.stdout.strip(), result.stderr.strip(), 'rc=', result.returncode)
