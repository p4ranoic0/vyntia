"""
Simple test para debuggear permisos sin dependencias de fixtures
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")
django.setup()

from api.v1.rrhh.permissions import EmpleadoPermission, RRHHPermission
from app_rrhh.models import Empleado, Permiso, Rol, Usuario
from django.contrib.auth.models import AnonymousUser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


def test_employee_permission():
    """Test employee permission directly"""

    print("\n" + "=" * 60)
    print("TEST: Employee Permission Logic")
    print("=" * 60)

    # Create test data
    print("\n1. Creating test data...")
    try:
        # Create test empleado
        empleado = Empleado.objects.create(
            nombres_empleado="Test",
            apellido_paterno="User",
            numero_documento="99999999",
            estado_empleado="activo",
        )
        print(f"  - Empleado created: {empleado.id}")

        # Create test role
        rol = Rol.objects.create(
            nombre_rol="Empleado",
            descripcion_rol="Test employee role",
            estado_rol="activo",
        )
        print(f"  - Rol created: {rol.id}")

        # Create test permission
        permiso = Permiso.objects.create(
            nombre_permiso="ver_empleado_propio", estado_permiso="activo"
        )
        rol.permisos_asignados.add(permiso)
        print(f"  - Permiso created: {permiso.id}")

        # Create test usuario
        usuario = Usuario.objects.create_user(
            username="testuser",
            password="test123",
            nombres_usuario="Test User",
            email="test@test.com",
            empleado=empleado,
        )
        usuario.roles_asignados.add(rol)
        usuario.save()
        print(f"  - Usuario created: {usuario.usuario_id}")

    except Exception as e:
        print(f"  ERROR creating test data: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n2. Testing RRHHPermission.has_permission()...")
    try:
        # Create mock request
        factory = APIRequestFactory()
        request = factory.get("/api/v1/rrhh/empleados/")
        drf_request = Request(request)
        drf_request.user = usuario

        # Mock view
        class MockView:
            pass

        view = MockView()

        # Test permission
        permission = RRHHPermission()
        result = permission.has_permission(drf_request, view)

        print(f"  Result: {result}")
        if result:
            print("  OK: RRHHPermission allows employee in GET")
        else:
            print("  FAIL: RRHHPermission blocked employee")
            return False

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n3. Testing EmpleadoPermission.has_object_permission()...")
    try:
        permission2 = EmpleadoPermission()
        result2 = permission2.has_object_permission(drf_request, view, empleado)

        print(f"  Result: {result2}")
        if result2:
            print("  OK: EmpleadoPermission allows access to own empleado")
        else:
            print("  FAIL: EmpleadoPermission blocked access")
            return False

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_employee_permission()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        import traceback

        traceback.print_exc()
