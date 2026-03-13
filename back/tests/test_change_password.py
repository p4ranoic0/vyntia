#!/usr/bin/env python
"""
Script de prueba para el endpoint de cambio de contraseña
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login/"
CHANGE_PASSWORD_URL = f"{BASE_URL}/api/v1/auth/user-profile/change-password/"

# Credenciales de prueba
USERNAME = "admin"  # Cambiar por un usuario válido
PASSWORD = "admin123"  # Cambiar por la contraseña actual
NEW_PASSWORD = "newpassword123"

def test_change_password():
    """Prueba el endpoint de cambio de contraseña"""
    
    # 1. Hacer login para obtener el token
    print("1. Haciendo login...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"Error en login: {login_response.text}")
            return
            
        login_result = login_response.json()
        access_token = login_result['data']['access']
        print("Login exitoso")
        
    except Exception as e:
        print(f"Error en login: {e}")
        return
    
    # 2. Cambiar contraseña
    print("\n2. Cambiando contraseña...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    change_password_data = {
        "old_password": PASSWORD,
        "new_password": NEW_PASSWORD,
        "confirm_password": NEW_PASSWORD
    }
    
    try:
        change_response = requests.post(
            CHANGE_PASSWORD_URL, 
            json=change_password_data, 
            headers=headers
        )
        
        print(f"Change password status: {change_response.status_code}")
        print(f"Response: {change_response.text}")
        
        if change_response.status_code == 200:
            print("¡Contraseña cambiada exitosamente!")
        else:
            print(f"Error al cambiar contraseña: {change_response.text}")
            
    except Exception as e:
        print(f"Error en cambio de contraseña: {e}")

if __name__ == "__main__":
    test_change_password()