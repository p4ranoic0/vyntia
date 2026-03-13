import json

import requests

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("VERIFICAR BACKEND RESPONDIENDO")
print("=" * 70)

# Test 1: Health check
print("\nTest 1: Health check (GET /api/v1/)")
try:
    resp = requests.get(f"{BASE_URL}/api/v1/", timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Text: {resp.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Login jgarcia
print("\n" + "-" * 70)
print("Test 2: Login con jgarcia")
login_resp = requests.post(
    f"{BASE_URL}/api/v1/auth/login/",
    json={"username": "jgarcia", "password": "Demo123!"},
    timeout=5,
)
print(f"Status: {login_resp.status_code}")
resp_data = login_resp.json()
print(f"Response: {json.dumps(resp_data, indent=2)[:500]}")

if login_resp.status_code == 200:
    access_token = resp_data.get("data", {}).get("access")
    print(f"\n" + "-" * 70)
    print("Test 3: GET /api/v1/rrhh/empleados/1/")

    headers = {"Authorization": f"Bearer {access_token}"}
    get_emp_resp = requests.get(
        f"{BASE_URL}/api/v1/rrhh/empleados/1/", headers=headers, timeout=5
    )
    print(f"Status: {get_emp_resp.status_code}")
    print(f"Response Text: {get_emp_resp.text[:1000]}")

    # If 500, try to get error details
    if get_emp_resp.status_code >= 500:
        try:
            error_data = get_emp_resp.json()
            print(f"\nError full response: {json.dumps(error_data, indent=2)}")
        except:
            pass
            pass
