"""
Test para debuggear permisos de jgarcia
"""

import os

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from api.v1.rrhh.permissions import EmpleadoPermission, RRHHPermission
from app_rrhh.models import Empleado, Usuario
from django.contrib.auth.models import AnonymousUser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


@pytest.mark.django_db
def test_rrhh_permission_for_employee():
    """Test RRHHPermission allows employees in read operations"""

    # Get jgarcia user
    user = Usuario.objects.get(username="jgarcia")

    # Create a mock request
    factory = APIRequestFactory()
    request = factory.get("/api/v1/rrhh/empleados/")
    drf_request = Request(request)
    drf_request.user = user
    drf_request.method = "GET"

    # Create a mock view
    class MockView:
        pass

    view = MockView()

    # Test RRHHPermission
    permission = RRHHPermission()

    print(f"\n=== Testing RRHHPermission.has_permission ===")
    print(f"User: {user.username} ({user.nombres_usuario})")
    print(f"Empleado: {user.empleado}")
    print(f"HasEmpleado: {hasattr(user, 'empleado') and user.empleado}")
    print(f"Method: {drf_request.method}")

    try:
        result = permission.has_permission(drf_request, view)
        print(f"Result: {result}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False

    assert result == True, "RRHHPermission should allow employees in GET requests"
    print("OK: RRHHPermission allows employees in GET requests")

    # Test EmpleadoPermission with object
    if user.empleado:
        print(f"\n=== Testing EmpleadoPermission.has_object_permission ===")
        empleado = user.empleado

        permission2 = EmpleadoPermission()

        try:
            result2 = permission2.has_object_permission(drf_request, view, empleado)
            print(f"Result: {result2}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback

            traceback.print_exc()
            return False

        print(f"OK: EmpleadoPermission result for own empleado: {result2}")

    return True


if __name__ == "__main__":
    test_rrhh_permission_for_employee()
    print("\nDone!")
    print("\nDone!")
