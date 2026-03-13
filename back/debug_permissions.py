import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, "/d/INTRANET/back")
django.setup()

from app_rrhh.models import Empleado, Usuario
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

print("=" * 60)
print("DEBUGGING: Probar metodos en jgarcia")
print("=" * 60)

try:
    # Get jgarcia user
    user = Usuario.objects.get(nombres_usuario="jgarcia")
    print(f"OK: Usuario encontrado: {user.nombres_usuario}")
    print(f"    - usuario_id: {user.usuario_id}")
    print(f"    - is_active: {user.is_active}")
    print(f"    - empleado_id: {user.empleado.id if user.empleado else 'None'}")
except Exception as e:
    print(f"ERROR al obtener usuario: {e}")
    sys.exit(1)

print("\n" + "-" * 60)
print("Test 1: roles_activos()")
print("-" * 60)
try:
    roles = user.roles_activos()
    print(f"OK: roles_activos() ejecutado")
    print(f"    Roles: {list(roles.values_list('nombre_rol', flat=True))}")
except Exception as e:
    print(f"ERROR en roles_activos(): {e}")
    import traceback

    traceback.print_exc()

print("\n" + "-" * 60)
print("Test 2: permisos_activos()")
print("-" * 60)
try:
    permisos = user.permisos_activos()
    print(f"OK: permisos_activos() ejecutado")
    print(f"    Permisos: {list(permisos.values_list('nombre_permiso', flat=True))}")
except Exception as e:
    print(f"ERROR en permisos_activos(): {e}")
    import traceback

    traceback.print_exc()

print("\n" + "-" * 60)
print("Test 3: empleado.ubicacion_actual()")
print("-" * 60)
try:
    if user.empleado:
        ubicacion = user.empleado.ubicacion_actual()
        print(f"OK: ubicacion_actual() ejecutado")
        print(f"    Ubicacion: {ubicacion}")
        if ubicacion:
            print(
                f"    Area: {ubicacion.area if hasattr(ubicacion, 'area') else 'No tiene area'}"
            )
except Exception as e:
    print(f"ERROR en ubicacion_actual(): {e}")
    import traceback

    traceback.print_exc()

print("\n" + "-" * 60)
print("Test 4: Simular permission check")
print("-" * 60)
try:
    factory = APIRequestFactory()
    request = factory.get(
        "/api/v1/rrhh/empleados/", HTTP_AUTHORIZATION="Bearer fake-token"
    )
    drf_request = Request(request)
    drf_request.user = user

    print(f"OK: Request creado")
    print(f"    - user: {drf_request.user}")
    print(f"    - method: {drf_request.method}")
    print(f"    - authenticated: {drf_request.user.is_authenticated}")
except Exception as e:
    print(f"ERROR al crear request: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("PRUEBAS COMPLETADAS")
print("=" * 60)
print("=" * 60)
