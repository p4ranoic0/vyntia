import json

from django.test import Client

# Crear client
client = Client()

# Test de login
print("\n1. Testing login with jgarcia...")
login_data = {"username": "jgarcia", "password": "Demo123!"}
response = client.post(
    "/api/v1/auth/token/", data=json.dumps(login_data), content_type="application/json"
)
print(f"   Login status: {response.status_code}")

if response.status_code == 200:
    data = json.loads(response.content)
    token = data.get("access")
    print(f"   Token obtained: {token[:20]}...")

    # Test endpoint empleados/1
    print("\n2. Testing GET /api/v1/rrhh/empleados/1/...")
    response = client.get(
        "/api/v1/rrhh/empleados/1/", HTTP_AUTHORIZATION=f"Bearer {token}"
    )
    print(f"   Status: {response.status_code}")

    if response.status_code != 200:
        resp_data = json.loads(response.content)
        print(f"   Response: {resp_data}")
    else:
        print(f"   ✅ SUCCESS: Got empleado data")
else:
    print(f"   ERROR: Login failed")
    resp_data = json.loads(response.content)
    print(f"   Response: {resp_data}")

print("\n3. Testing debug endpoint /api/v1/auth/test-permisos/...")
response = client.get("/api/v1/auth/test-permisos/")
print(f"   Status: {response.status_code}")
resp_data = json.loads(response.content)
print(f"   Response: {resp_data}")
print(f"   Response: {resp_data}")
