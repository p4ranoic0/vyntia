"""Final validation before testing endpoints."""

import ast
import os
import sys


def validate_file(filepath):
    """Validate Python file syntax."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


# Test files
files_to_check = [
    "api/v1/rrhh/permissions.py",
    "core/roles_config.py",
    "core/permissions.py",
]

print("=== File Syntax Validation ===\n")

all_valid = True
for filepath in files_to_check:
    full_path = f"d:\\INTRANET\\back\\{filepath}"
    valid, msg = validate_file(full_path)
    status = "✅" if valid else "❌"
    print(f"{status} {filepath}")
    if not valid:
        print(f"   {msg}")
        all_valid = False

print()
if all_valid:
    print("✅ All files have valid syntax!")
    print("\nNext: Run 'python manage.py check' from d:\\INTRANET\\back")
    sys.exit(0)
else:
    print("❌ Some files have syntax errors")
    sys.exit(1)
    sys.exit(1)
