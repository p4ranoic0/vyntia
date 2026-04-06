import os, sys
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE']='config.settings.development'
import django
django.setup()
from django.conf import settings
pw = settings.DATABASES['default']['PASSWORD']
print('Password repr:', repr(pw))
for i, c in enumerate(pw):
    print(f'  char {i}: {repr(c)} ord={ord(c)} hex={hex(ord(c))}')
