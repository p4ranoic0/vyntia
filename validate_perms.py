#!/usr/bin/env python
"""Validar sintaxis del archivo de permisos."""

import subprocess
import sys

try:
    # Validar sintaxis del archivo
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "api/v1/rrhh/permissions.py"],
        cwd="d:\\INTRANET\\back",
        capture_output=True,
        text=True,
        timeout=15,
    )

    if result.returncode == 0:
        print("✅ Sintaxis OK - No hay errores")
        sys.exit(0)
    else:
        print("❌ Error de sintaxis:")
        print(result.stderr)
        sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
