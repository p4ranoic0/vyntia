#!/usr/bin/env python
"""Direct test of Empleado retrieval."""
import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
django.setup()

from app_rrhh.models import Empleado

try:
    print("Retrieving Empleado...")
    emp = Empleado.objects.first()
    if emp:
        print(f"Found: {emp.nombres_empleado}")
        print(f"Serializing...")
        from api.v1.rrhh.serializers import EmpleadoSerializer

        serializer = EmpleadoSerializer(emp)
        print(f"Serialized successfully")
        print(f"Data keys: {list(serializer.data.keys())[:10]}")
    else:
        print("No empleado found")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()
    traceback.print_exc()
