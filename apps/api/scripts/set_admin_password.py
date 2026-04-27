#!/usr/bin/env python
"""
Script para establecer una contraseña conocida al usuario admin
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development')
django.setup()

from apps.identity.models.user import User

def set_admin_password():
    """Establece una contraseña conocida para el usuario admin"""
    try:
        # Buscar el usuario admin
        admin_user = User.objects.get(username='admin')
        
        # Establecer nueva contraseña
        new_password = 'admin123'
        admin_user.set_password(new_password)
        admin_user.save()
        
        print(f"Contraseña establecida para {admin_user.username}: {new_password}")
        print(f"User activo: {admin_user.is_active}")
        
    except User.DoesNotExist:
        print("User admin no encontrado")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    set_admin_password()