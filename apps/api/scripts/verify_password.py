#!/usr/bin/env python
"""Script para verificar la contraseña del usuario admin."""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development')
django.setup()

from apps.identity.models.usuario import Usuario
from django.contrib.auth.hashers import check_password

def verify_admin_password():
    """Verificar la contraseña del usuario admin."""
    try:
        # Obtener el usuario admin
        admin_user = Usuario.objects.get(username='admin')
        print(f"Usuario encontrado: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print(f"Activo: {admin_user.is_active}")
        print(f"Hash de contraseña: {admin_user.password[:50]}...")
        
        # Verificar contraseña
        password_to_test = 'admin123'
        is_valid = check_password(password_to_test, admin_user.password)
        print(f"¿La contraseña '{password_to_test}' es válida?: {is_valid}")
        
        # También probar con 'admin'
        password_to_test2 = 'admin'
        is_valid2 = check_password(password_to_test2, admin_user.password)
        print(f"¿La contraseña '{password_to_test2}' es válida?: {is_valid2}")
        
    except Usuario.DoesNotExist:
        print("Usuario admin no encontrado")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    verify_admin_password()