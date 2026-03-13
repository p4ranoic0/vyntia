"""
Script de prueba para verificar el acceso de jgarcia después de refactorizar permisos
"""

import json

import requests

BASE_URL = "http://localhost:8000"


def test_jgarcia_login():
    """Test 1: Login de jgarcia"""
    print("=" * 60)
    print("TEST 1: Login de jgarcia")
    print("=" * 60)

    login_url = f"{BASE_URL}/api/v1/auth/login/"
    login_data = {"username": "jgarcia", "password": "Demo123!"}

    response = requests.post(login_url, json=login_data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login exitoso")
        token_data = data.get("data", data)  # Manejar estructura envuelta
        access_token = token_data.get("access")
        print(f"Access Token: {access_token[:50]}...")
        print(f"Usuario: {token_data.get('user', {}).get('username')}")
        return access_token
    else:
        print(f"❌ Login fallido: {response.text}")
        return None


def test_get_own_employee(token):
    """Test 2: Obtener datos del propio empleado"""
    print("\n" + "=" * 60)
    print("TEST 2: GET /api/v1/rrhh/empleados/1/ (propio empleado)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # jgarcia.empleado_id = 1
    url = f"{BASE_URL}/api/v1/rrhh/empleados/1/"
    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Acceso exitoso")
        print(f"Empleado: {data.get('nombres')} {data.get('apellido_paterno')}")
        print(f"DNI: {data.get('numero_documento')}")
    else:
        print(f"❌ Acceso denegado: {response.text}")


def test_get_other_employee(token):
    """Test 3: Intentar obtener datos de otro empleado"""
    print("\n" + "=" * 60)
    print("TEST 3: GET /api/v1/rrhh/empleados/2/ (otro empleado)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    url = f"{BASE_URL}/api/v1/rrhh/empleados/2/"
    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print(f"⚠️ Acceso permitido (debería estar bloqueado)")
    elif response.status_code == 403:
        print(f"✅ Correctamente bloqueado (403 Forbidden)")
    else:
        print(f"❓ Respuesta inesperada: {response.text}")


def test_list_employees(token):
    """Test 4: Listar empleados"""
    print("\n" + "=" * 60)
    print("TEST 4: GET /api/v1/rrhh/empleados/ (listado)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    url = f"{BASE_URL}/api/v1/rrhh/empleados/"
    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", data)
        print(f"✅ Listado obtenido: {len(results)} empleados")
        for emp in results[:3]:  # Mostrar primeros 3
            print(f"   - {emp.get('nombres')} {emp.get('apellido_paterno')}")
    else:
        print(f"❌ Acceso denegado: {response.text}")


def test_get_areas(token):
    """Test 5: Obtener áreas (necesario para dropdowns)"""
    print("\n" + "=" * 60)
    print("TEST 5: GET /api/v1/rrhh/areas/ (listado de áreas)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    url = f"{BASE_URL}/api/v1/rrhh/areas/"
    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", data)
        print(f"✅ Áreas obtenidas: {len(results)} áreas")
        for area in results[:3]:  # Mostrar primeras 3
            print(f"   - {area.get('nombre_area')}")
    else:
        print(f"❌ Acceso denegado: {response.text}")


def main():
    print("\n" + "█" * 60)
    print("PRUEBAS DE ACCESO - Usuario jgarcia")
    print(
        "Objetivo: Verificar que empleados normales pueden acceder con permisos granulares"
    )
    print("█" * 60 + "\n")

    # Test 1: Login
    token = test_jgarcia_login()

    if not token:
        print("\n❌ No se pudo obtener token. Abortando pruebas.")
        return

    # Test 2: Obtener propio empleado
    test_get_own_employee(token)

    # Test 3: Intentar obtener otro empleado (debería fallar)
    test_get_other_employee(token)

    # Test 4: Listar empleados
    test_list_employees(token)

    # Test 5: Obtener áreas
    test_get_areas(token)

    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS COMPLETADO")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
    main()
