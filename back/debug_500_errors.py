"""Debugging profundo del error 500 en RRHH endpoints."""

import os
import sys
import traceback

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, "d:\\INTRANET\\back")

try:
    django.setup()
    print("✅ Django initialized\n")

    # Import models
    import json

    from app_rrhh.models import Area, Empleado, Rol, Usuario
    from django.test import Client

    # Test 1: Direct model access
    print("=" * 60)
    print("TEST 1: Direct Model Access")
    print("=" * 60)

    try:
        areas = Area.objects.all()[:5]
        print(f"✅ Areas queryset works: {areas.count()} areas found")
        for area in areas:
            print(f"   - {area.nombre_organo}")
    except Exception as e:
        print(f"❌ Area query FAILED:")
        traceback.print_exc()

    # Test 2: Roles query
    print("\n" + "=" * 60)
    print("TEST 2: Roles Query")
    print("=" * 60)

    try:
        roles = Rol.objects.all()[:5]
        print(f"✅ Roles queryset works: {roles.count()} roles found")
        for rol in roles:
            print(f"   - {rol.nombre_rol}")
    except Exception as e:
        print(f"❌ Rol query FAILED:")
        traceback.print_exc()

    # Test 3: Empleados
    print("\n" + "=" * 60)
    print("TEST 3: Empleados Query")
    print("=" * 60)

    try:
        empleados = Empleado.objects.all()[:5]
        print(f"✅ Empleados queryset works: {empleados.count()} empleados found")
        for emp in empleados:
            print(f"   - {emp.nombres_empleado}")
    except Exception as e:
        print(f"❌ Empleado query FAILED:")
        traceback.print_exc()

    # Test 4: API endpoint simulation
    print("\n" + "=" * 60)
    print("TEST 4: API Endpoint Simulation")
    print("=" * 60)

    client = Client()

    # Try GET /api/v1/rrhh/areas/
    print("\nAttempting: GET /api/v1/rrhh/areas/")
    try:
        response = client.get("/api/v1/rrhh/areas/")
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            data = json.loads(response.content) if response.content else {}
            print(f"Response: {data}")
    except Exception as e:
        print(f"❌ Request FAILED:")
        traceback.print_exc()

    # Try GET /api/v1/rrhh/roles/
    print("\nAttempting: GET /api/v1/rrhh/roles/")
    try:
        response = client.get("/api/v1/rrhh/roles/")
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            data = json.loads(response.content) if response.content else {}
            print(f"Response: {data}")
    except Exception as e:
        print(f"❌ Request FAILED:")
        traceback.print_exc()

    # Try GET /api/v1/rrhh/empleados/
    print("\nAttempting: GET /api/v1/rrhh/empleados/")
    try:
        response = client.get("/api/v1/rrhh/empleados/")
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            data = json.loads(response.content) if response.content else {}
            print(f"Response: {data}")
    except Exception as e:
        print(f"❌ Request FAILED:")
        traceback.print_exc()

except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
    traceback.print_exc()
    sys.exit(1)
