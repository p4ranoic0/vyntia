#!/usr/bin/env python
"""Test script to diagnose the new permisos_activos() method."""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
sys.path.insert(0, "d:\\INTRANET\\back")
django.setup()

from app_rrhh.models import Usuario

try:
    # Get jgarcia user
    user = Usuario.objects.get(nombres_usuario__icontains="jgarcia")
    print(f"✅ Usuario encontrado: {user.nombres_usuario}")

    # Test roles_activos()
    print("\n🔍 Probando roles_activos()...")
    roles = user.roles_activos()
    print(f"✅ Roles activos: {[r.nombre_rol for r in roles]}")

    # Test permisos_activos()
    print("\n🔍 Probando permisos_activos()...")
    permisos = user.permisos_activos()
    print(f"✅ Permisos: {permisos}")
    print(f"  Tipo: {type(permisos)}")

    # Test check
    if permisos == "*":
        print("  Admin access (wildcard)")
    elif isinstance(permisos, set):
        print(f"  Recursos con permiso: {permisos}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
    traceback.print_exc()
