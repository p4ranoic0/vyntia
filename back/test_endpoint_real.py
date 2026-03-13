"""
Test endpoint real con jgarcia
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from app_rrhh.models import Area, Empleado, Rol, Usuario
from django.test import Client

# Crear client
client = Client()

# Test de login
print("\n1. Testing login with jgarcia...")
login_data = {"username": "jgarcia", "password": "Demo123!"}
response = client.post(
    "/api/v1/auth/token/", login_data, content_type="application/json"
)
print(f"   Login status: {response.status_code}")

if response.status_code == 200:
    token = response.json().get("access")
    print(f"   Token obtained: {token[:20]}...")

    # Test endpoint empleados/1
    print("\n2. Testing GET /api/v1/rrhh/empleados/1/...")
    headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
    response = client.get("/api/v1/rrhh/empleados/1/", **headers)
    print(f"   Status: {response.status_code}")

    if response.status_code != 200:
        print(f"   Response: {response.json()}")
    else:
        print(f"   ✅ SUCCESS: Got empleado data")
        print(f"   Nombres: {response.json().get('nombres')}")
else:
    print(f"   ERROR: Login failed")
    print(f"   Response: {response.json()}")

print("\n3. Testing debug endpoint /api/v1/auth/test-permisos/...")
response = client.get("/api/v1/auth/test-permisos/")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")
