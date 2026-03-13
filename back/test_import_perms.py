#!/usr/bin/env python
"""Test if permissions module can be imported."""

import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, "/d/INTRANET/back")

try:
    django.setup()
    from api.v1.rrhh.permissions import (
        AreaPermission,
        AuditoriaPermission,
        DatosPersonalesPermission,
        DocumentosDigitalesPermission,
        EmpleadoPermission,
        ReportesPermission,
        RRHHPermission,
        UsuarioPermission,
    )

    print("✅ Módulo de permisos importado exitosamente")
    print("   Clases disponibles:")
    print("   - RRHHPermission")
    print("   - AreaPermission")
    print("   - EmpleadoPermission")
    print("   - DatosPersonalesPermission")
    print("   - DocumentosDigitalesPermission")
    print("   - UsuarioPermission")
    print("   - ReportesPermission")
    print("   - AuditoriaPermission")
except Exception as e:
    print(f"❌ Error al importar: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
