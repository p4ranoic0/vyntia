#!/usr/bin/env python
"""
Script para generar schema OpenAPI completo y limpio
Captura stdout y filtra stderr (warnings)
"""
import json
import subprocess
import sys

# Ejecutar el comando spectacular
process = subprocess.Popen(
    [sys.executable, "manage.py", "spectacular", "--format", "openapi-json"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

# Capturar salidas
stdout, stderr = process.communicate()

# Verificar código de retorno
if process.returncode != 0:
    print(f"❌ El comando falló con código: {process.returncode}")
    print("\n📋 Últimas 20 líneas de stderr:")
    stderr_lines = stderr.strip().split("\n")
    for line in stderr_lines[-20:]:
        print(f"  {line}")
else:
    print(f"✅ Comando ejecutado exitosamente")

# Normalizar salida: si stdout contiene multiples documentos JSON concatenados,
# conservar solo el primer objeto JSON valido para evitar romper el generador TS.
normalized_stdout = stdout
try:
    decoder = json.JSONDecoder()
    _, end = decoder.raw_decode(stdout.lstrip())
    normalized_stdout = stdout.lstrip()[:end]
except json.JSONDecodeError:
    # Se conserva stdout completo para diagnóstico en caso de salida inesperada.
    pass

# Guardar solo stdout normalizado (el JSON) al archivo
output_path = r"d:\VYNTIA\apps\web\openapi-schema.json"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(normalized_stdout)

print(f"✅ Schema generado: {len(normalized_stdout)} caracteres")
print(f"📏 Archivo: {output_path}")

# Mostrar algunos warnings si los hay (opcional)
if stderr:
    stderr_lines = stderr.strip().split("\n")
    warning_count = len([l for l in stderr_lines if "Warning" in l])
    error_count = len([l for l in stderr_lines if "Error" in l])
    if warning_count > 0:
        print(f"⚠️  {warning_count} warnings (ver stderr para detalles)")
    if error_count > 0:
        print(f"❌ {error_count} errors")
        print("\n🔍 Mostrando errores:")
        for line in stderr_lines:
            if "Error" in line:
                print(f"  {line}")
