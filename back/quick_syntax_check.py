import ast
import sys

# Leer el archivo
try:
    with open("api/v1/rrhh/permissions.py", "r", encoding="utf-8") as f:
        code = f.read()

    # Intentar parsear - esto validará la sintaxis
    ast.parse(code)
    print("✅ Sintaxis válida - No hay errores")
    sys.exit(0)

except SyntaxError as e:
    print(f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}")
    print(f"   {e.text}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
