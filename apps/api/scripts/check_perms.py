import os
import sys

import django

# Agregar el directorio back al path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


# Cargar .env con UTF-8
def load_env_file(env_path=".env"):
    """Cargar variables de entorno desde .env con encoding UTF-8."""
    env_file = os.path.join(BASE_DIR, env_path)
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


load_env_file()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vyntia.settings.development")
django.setup()

from apps.identity.models import Permiso

perms = list(Permiso.objects.values("nombre_permiso", "modulo")[:5])
for p in perms:
    print(f"{p['nombre_permiso']}: {p['modulo']}")
    print(f"{p['nombre_permiso']}: {p['modulo']}")
