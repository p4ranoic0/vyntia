# VYNTIA Foundation L3.4 — Extract `employees` App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extraer los modelos del dominio empleado (`Empleado`, `DatosFamiliares`, `DatosAcademicos`, `CursosCertificaciones`) desde `app_rrhh/` hacia una nueva Django app en `apps/api/apps/employees/`. Class names quedan en español — el rename a inglés (`Empleado→Employee`, etc.) es L3.10.

**Architecture:** L3.4 es **el más grande de los sub-PRs medios** porque Empleado es el HUB del modelo de datos. Empleado en sí mismo no tiene FKs (no apunta a otros modelos), pero ~10 FKs en otros archivos de app_rrhh apuntan a `'Empleado'` y deben actualizarse a `'employees.Empleado'`. También DatosFamiliares es referenciado por documentos_digitales. Patrón establecido en L3.2/L3.3 ya validado: mover modelos, actualizar FK strings cross-app, NUCLEAR DB regenerate. Sin cambio de AUTH_USER_MODEL.

**Tech Stack:** Django 5.2 `AppConfig`, NUCLEAR DB strategy (validada en L3.2/L3.3), Django management commands para reseed.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L3 — División de apps Django" sub-PR L3.4; § 3.2 "División de modelos"

**Pre-condiciones:**
- L3.3 mergeado a master (commit `36573111`)
- Django 5.2.13, `apps/api/apps/{core,identity,organization}/` operativos
- pytest baseline: 125 passed, 44 failed, 3 skipped
- `bd_vyntia` provisionada con esquema actual; rol=5, permiso=23, modulos=31, usuarios=1, area=0
- venv en `D:/VYNTIA/.venv/`

**Definition of Done:**
- [ ] `apps/api/apps/employees/` existe con `apps.py`, `models/`, `migrations/`
- [ ] Modelos `Empleado`, `DatosFamiliares`, `DatosAcademicos`, `CursosCertificaciones` movidos a `apps/employees/models/`
- [ ] `app_rrhh/models/{empleado,datos_familiares,datos_academicos,cursos_certificaciones}.py` eliminados
- [ ] `EmployeesConfig` en `LOCAL_APPS`
- [ ] FK strings `'Empleado'` en 5 archivos de `app_rrhh/models/` actualizadas a `'employees.Empleado'` (10 ocurrencias totales)
- [ ] FK string `'DatosFamiliares'` en `documentos_digitales.py:153` actualizada a `'employees.DatosFamiliares'`
- [ ] FK strings `'DocumentosDigitales'` dentro de los archivos movidos (`datos_academicos.py:117`, `cursos_certificaciones.py:25`) actualizadas a `'app_rrhh.DocumentosDigitales'`
- [ ] `empleado.py:263` inline import: `from .datos_laborales import DatosLaborales` → `from app_rrhh.models import DatosLaborales`
- [ ] Migraciones regeneradas: app_rrhh y identity sin Empleado/DatosFamiliares/etc.; employees con los 4 modelos
- [ ] `bd_vyntia` recreada y reseeded (rol > 0, permiso > 0, modulos > 0)
- [ ] Imports actualizados across ~25 archivos
- [ ] `pyproject.toml` `packages` incluye `"apps.employees"`
- [ ] `python manage.py check` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.4-employees-app` mergeada a master con `--no-ff`

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/apps/employees/__init__.py` | empty |
| Create | `apps/api/apps/employees/apps.py` | `EmployeesConfig(AppConfig)` con `name="apps.employees"`, `label="employees"` |
| Create | `apps/api/apps/employees/models/__init__.py` | re-exporta los 4 modelos |
| Move | `app_rrhh/models/empleado.py` → `apps/api/apps/employees/models/empleado.py` | inline import `.datos_laborales` → `app_rrhh.models` |
| Move | `app_rrhh/models/datos_familiares.py` → `apps/api/apps/employees/models/datos_familiares.py` | FK `'Empleado'` queda same-app |
| Move | `app_rrhh/models/datos_academicos.py` → `apps/api/apps/employees/models/datos_academicos.py` | FK `'DocumentosDigitales'` → `'app_rrhh.DocumentosDigitales'` |
| Move | `app_rrhh/models/cursos_certificaciones.py` → `apps/api/apps/employees/models/cursos_certificaciones.py` | FK `'DocumentosDigitales'` → `'app_rrhh.DocumentosDigitales'` |
| Create | `apps/api/apps/employees/migrations/__init__.py` | empty |
| Modify | `apps/api/app_rrhh/models/contratos_adendas.py` | FK `'Empleado'` → `'employees.Empleado'` (1 ocurrencia) |
| Modify | `apps/api/app_rrhh/models/datos_laborales.py` | FK `'Empleado'` → `'employees.Empleado'` (2 ocurrencias) |
| Modify | `apps/api/app_rrhh/models/documentos_digitales.py` | FK `'Empleado'` → `'employees.Empleado'` (1) + `'DatosFamiliares'` → `'employees.DatosFamiliares'` (1) |
| Modify | `apps/api/app_rrhh/models/onboarding.py` | FK `'Empleado'` → `'employees.Empleado'` (1) |
| Modify | `apps/api/app_rrhh/models/vacaciones.py` | FK `'Empleado'` → `'employees.Empleado'` (5 ocurrencias) |
| Modify | `apps/api/app_rrhh/models/__init__.py` | quitar exports de Empleado, DatosFamiliares, DatosAcademicos, CursosCertificaciones |
| Modify | `apps/api/vyntia/settings/base.py` | añadir `"apps.employees.apps.EmployeesConfig"` a `LOCAL_APPS` |
| Modify | `apps/api/pyproject.toml` | añadir `"apps.employees"` a `packages` |
| Modify (~25 files) | varios en `api/v1/`, `app_rrhh/services/`, `apps/{identity,organization}/models/`, `scripts/`, `tests/` | replace `from app_rrhh.models import ... {Empleado|DatosFamiliares|DatosAcademicos|CursosCertificaciones}` → `from apps.employees.models import ...` |
| Delete | `app_rrhh/migrations/0001_initial.py` + `0002_initial.py` | regenerated |
| Delete | `apps/identity/migrations/0001_initial.py` | regenerated |
| Delete | `apps/organization/migrations/0001_initial.py` | regenerated |

**NO se toca en L3.4:**
- Class names (rename a inglés es L3.10)
- Field names
- Frontend
- DatosLaborales (queda en app_rrhh hasta L3.5 — contracts)
- ContratosAdendas (queda en app_rrhh hasta L3.5)
- Managers en `app_rrhh/managers.py` (EmpleadoManager, DatosFamiliaresManager, DatosAcademicosManager — comentados en los modelos, orphan code, cleanup en L3.11)

**Lecciones aplicadas de L3.3** (que el implementer debe anticipar):
- Buscar relative imports `from .X` dentro de los archivos movidos
- Buscar imports en `app_rrhh/{views,services,serializers,managers,tests}.py`
- Buscar submodule path imports `from app_rrhh.models.X import Y`
- Verificar inline imports dentro de funciones/métodos

---

## Task 1: Pre-flight — branch, baseline, backup

- [ ] **Step 1: Confirmar pwd y master limpio post-L3.3**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -3
```

Expected: HEAD = `5534abc3 docs(L3.3): mark L3.3 merged, L3.4 as next` o más reciente. `git status` vacío excepto este plan untracked.

- [ ] **Step 2: Activar venv y confirmar Django 5.2.13**

```bash
source .venv/Scripts/activate
python -c "import django; print(django.get_version())"
```

Expected: `5.2.13`.

- [ ] **Step 3: Confirmar baseline pytest**

```bash
cd apps/api
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: `125 passed, 44 failed, 3 skipped`.

- [ ] **Step 4: Backup bd_vyntia (paranoia)**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.4.dump 2>&1 | tail -3
ls -lh /tmp/bd_vyntia_pre_L3.4.dump
```

Expected: dump ~250-500 KB.

- [ ] **Step 5: Crear branch L3.4**

```bash
git checkout -b vyntia/L3.4-employees-app
git status --short
```

---

## Task 2: Comitear el plan en la branch

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.4-employees.md
git commit -m "docs(L3.4): add employees app extraction plan"
```

---

## Task 3: Crear estructura `apps/employees/`

- [ ] **Step 1: Crear directorios + empty `__init__.py`**

```bash
cd D:/VYNTIA
mkdir -p apps/api/apps/employees/models
mkdir -p apps/api/apps/employees/migrations
touch apps/api/apps/employees/__init__.py
touch apps/api/apps/employees/migrations/__init__.py
```

- [ ] **Step 2: Crear `apps/employees/apps.py`**

Use Write tool con contenido EXACTO:

```python
"""AppConfig for the `apps.employees` Django app — VYNTIA employee personal data.

Owns the personal/HR-record entities of an employee:
- Empleado (the employee person itself, with personal info, IDs, contact data)
- DatosFamiliares (family members — spouse, children, dependents)
- DatosAcademicos (educational records — degrees, institutions)
- CursosCertificaciones (courses, certifications, professional development)

Bounded context boundary: employees defines WHO works at the organization
(personal data, qualifications). Employment relationship details (contract,
salary, work location) live in `apps.contracts` (L3.5) and `apps.payroll` (L3.7).
"""

from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    name = "apps.employees"
    label = "employees"
    verbose_name = "VYNTIA Employees"
```

- [ ] **Step 3: Crear placeholder `apps/employees/models/__init__.py`**

```python
"""Employees models — re-exports for backward-compatible imports.

Populated when models are physically moved.
"""
```

---

## Task 4: Mover los 4 model files con `git mv`

- [ ] **Step 1: Defensive — kill stale Python procs**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 2: `git mv` los 4 archivos**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/models/empleado.py apps/api/apps/employees/models/empleado.py
git mv apps/api/app_rrhh/models/datos_familiares.py apps/api/apps/employees/models/datos_familiares.py
git mv apps/api/app_rrhh/models/datos_academicos.py apps/api/apps/employees/models/datos_academicos.py
git mv apps/api/app_rrhh/models/cursos_certificaciones.py apps/api/apps/employees/models/cursos_certificaciones.py
```

- [ ] **Step 3: Verificar layout**

```bash
ls apps/api/apps/employees/models/
ls apps/api/app_rrhh/models/empleado.py 2>&1 || echo "OK: removed"
```

Expected: 4 model files + `__init__.py` en employees/models/. Originals removed.

---

## Task 5: Update FK strings DENTRO de los archivos movidos

**Files:**
- Modify: `apps/api/apps/employees/models/empleado.py`
- Modify: `apps/api/apps/employees/models/datos_academicos.py`
- Modify: `apps/api/apps/employees/models/cursos_certificaciones.py`
- (datos_familiares.py no necesita cambios — su FK `'Empleado'` queda same-app)

- [ ] **Step 1: Update inline import en `empleado.py:263`**

DatosLaborales se queda en `app_rrhh` (hasta L3.5). El import relative `.datos_laborales` ya no funciona porque empleado.py ahora vive en `apps/employees/models/`.

Use Edit tool en `apps/api/apps/employees/models/empleado.py`:
- old_string: `        from .datos_laborales import DatosLaborales`
- new_string: `        from app_rrhh.models import DatosLaborales`

Verifica que líneas 279 (`from .datos_familiares import DatosFamiliares`) y 285 (`from .datos_academicos import DatosAcademicos`) NO se tocan — son same-app post-move.

```bash
grep -n "from .datos_familiares\|from .datos_academicos\|from .datos_laborales\|from app_rrhh.models import DatosLaborales" apps/api/apps/employees/models/empleado.py
```

Expected:
- `from .datos_familiares import DatosFamiliares` (queda)
- `from .datos_academicos import DatosAcademicos` (queda)
- `from app_rrhh.models import DatosLaborales` (línea 263)
- 0 matches `from .datos_laborales`

- [ ] **Step 2: Update FK `'DocumentosDigitales'` en `datos_academicos.py:117`**

Use Edit tool en `apps/api/apps/employees/models/datos_academicos.py`:
- old_string:
```python
    documento = models.ForeignKey(
        'DocumentosDigitales',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='dato_academico',
    )
```
- new_string:
```python
    documento = models.ForeignKey(
        'app_rrhh.DocumentosDigitales',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='dato_academico',
    )
```

- [ ] **Step 3: Update FK `'DocumentosDigitales'` en `cursos_certificaciones.py:25`**

Use Edit tool en `apps/api/apps/employees/models/cursos_certificaciones.py`:
- old_string:
```python
    documento = models.ForeignKey(
        'DocumentosDigitales',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='curso_certificacion',
    )
```
- new_string:
```python
    documento = models.ForeignKey(
        'app_rrhh.DocumentosDigitales',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='curso_certificacion',
    )
```

- [ ] **Step 4: Verificar updates**

```bash
grep -rn "'DocumentosDigitales'\|'app_rrhh.DocumentosDigitales'" apps/api/apps/employees/models/ --include="*.py"
```

Expected: 2 matches con `'app_rrhh.DocumentosDigitales'`. Ningún match `'DocumentosDigitales'` sin prefijo.

---

## Task 6: Update FK strings `'Empleado'` y `'DatosFamiliares'` en archivos de `app_rrhh` que se quedan

**Files:**
- Modify: `apps/api/app_rrhh/models/contratos_adendas.py` (1 FK)
- Modify: `apps/api/app_rrhh/models/datos_laborales.py` (2 FKs)
- Modify: `apps/api/app_rrhh/models/documentos_digitales.py` (Empleado + DatosFamiliares)
- Modify: `apps/api/app_rrhh/models/onboarding.py` (1 FK)
- Modify: `apps/api/app_rrhh/models/vacaciones.py` (5 FKs)

**Por qué:** Después del move, Empleado vive en `employees`. Los modelos que quedan en app_rrhh deben usar string lazy `'employees.Empleado'`.

- [ ] **Step 1: Bulk replace `'Empleado'` → `'employees.Empleado'` en app_rrhh/models/**

Como el patrón es exacto y no aparece en otros contextos (no hay clases llamadas Empleado en app_rrhh post-move), un bulk sed funciona:

```bash
cd D:/VYNTIA/apps/api
find app_rrhh/models -type f -name "*.py" -not -path "*/__pycache__/*" -print0 | xargs -0 sed -i \
  -e "s|'Empleado'|'employees.Empleado'|g" \
  -e "s|'DatosFamiliares'|'employees.DatosFamiliares'|g"
```

- [ ] **Step 2: Verificar updates**

```bash
cd D:/VYNTIA/apps/api
echo "=== employees.Empleado refs (should be 10+) ==="
grep -rn "'employees\.Empleado'" app_rrhh/models --include="*.py" | wc -l
echo ""
echo "=== employees.DatosFamiliares refs (should be 1) ==="
grep -rn "'employees\.DatosFamiliares'" app_rrhh/models --include="*.py" | wc -l
echo ""
echo "=== Bare 'Empleado' refs (should be 0) ==="
grep -rn "'Empleado'\b" app_rrhh/models --include="*.py" || echo "OK: cero"
echo ""
echo "=== Bare 'DatosFamiliares' refs (should be 0) ==="
grep -rn "'DatosFamiliares'\b" app_rrhh/models --include="*.py" || echo "OK: cero"
```

Expected: 10+ employees.Empleado, 1 employees.DatosFamiliares, 0 bare strings.

---

## Task 7: Crear `apps/employees/models/__init__.py` con re-exports

```python
"""Employees models — re-exports for backward-compatible imports."""

from .cursos_certificaciones import CursosCertificaciones
from .datos_academicos import DatosAcademicos
from .datos_familiares import DatosFamiliares
from .empleado import Empleado

__all__ = [
    "CursosCertificaciones",
    "DatosAcademicos",
    "DatosFamiliares",
    "Empleado",
]
```

- [ ] **Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.employees.models import Empleado, DatosFamiliares, DatosAcademicos, CursosCertificaciones; print('OK')"
cd ../..
```

Expected: `OK`. Si falla, hay imports rotos en algún model file (probablemente relative imports a otros archivos).

---

## Task 8: Update `app_rrhh/models/__init__.py` — quitar exports de employees

- [ ] **Step 1: Read current state**

```bash
grep -n "from .empleado\|from .datos_familiares\|from .datos_academicos\|from .cursos_certificaciones\|\"Empleado\"\|\"DatosFamiliares\"\|\"DatosAcademicos\"\|\"CursosCertificaciones\"" apps/api/app_rrhh/models/__init__.py
```

- [ ] **Step 2: Use Edit tool para eliminar las 4 líneas import + entries en `__all__`**

Lines a eliminar (exact match):
- `from .cursos_certificaciones import CursosCertificaciones`
- `from .datos_academicos import DatosAcademicos`
- `from .datos_familiares import DatosFamiliares`
- `from .empleado import Empleado`

En `__all__` list, eliminar `"Empleado"`, `"DatosFamiliares"`, `"DatosAcademicos"`, `"CursosCertificaciones"`.

Use Read tool primero para ver contexto exacto, luego Edit con surrounding lines suficientes.

- [ ] **Step 3: Verificar limpieza**

```bash
grep -n "from .empleado\|from .datos_familiares\|from .datos_academicos\|from .cursos_certificaciones" apps/api/app_rrhh/models/__init__.py || echo "OK: removed"
```

Expected: `OK`.

---

## Task 9: Bulk update absolute imports across the codebase

**Pattern:** `from app_rrhh.models import {Empleado|DatosFamiliares|DatosAcademicos|CursosCertificaciones}` → `from apps.employees.models import ...`

Esto es la TASK MÁS GRANDE de imports en L3 (~25 archivos, muchos mezclados).

- [ ] **Step 1: Inventario completo**

```bash
cd D:/VYNTIA/apps/api
grep -rln "from app_rrhh\.models import" --include="*.py" 2>&1 | sort
```

Expected: ~30+ files. Filtra:

```bash
grep -rln "from app_rrhh\.models import" --include="*.py" | xargs grep -l -E "Empleado|DatosFamiliares|DatosAcademicos|CursosCertificaciones" 2>&1 | sort
```

Expected: ~20-25 files con employees-models.

- [ ] **Step 2: Sed para imports puros (single-import lines)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" -not -path "*/migrations/*" -not -path "*/__pycache__/*" -not -path "*/apps/employees/*" -print0 | xargs -0 sed -i \
  -e 's|^from app_rrhh\.models import \(Empleado\)$|from apps.employees.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(DatosFamiliares\)$|from apps.employees.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(DatosAcademicos\)$|from apps.employees.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(CursosCertificaciones\)$|from apps.employees.models import \1|g'
```

- [ ] **Step 3: Manual fix para imports mezclados (single-line con coma)**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models import" --include="*.py" | grep -E "Empleado|DatosFamiliares|DatosAcademicos|CursosCertificaciones" | head -30
```

Para cada match:
- Si línea es `from app_rrhh.models import A, Empleado, B` → split en `from app_rrhh.models import A, B` + `from apps.employees.models import Empleado`
- Mantener orden alfabético

Employees model names a reconocer: `Empleado`, `DatosFamiliares`, `DatosAcademicos`, `CursosCertificaciones`.

- [ ] **Step 4: Manual fix para imports multi-línea con parens**

```bash
cd D:/VYNTIA/apps/api
grep -rn -B 0 -A 12 "from app_rrhh\.models import (" --include="*.py" 2>&1 | head -100
```

Para cada match: split similar pattern. Multi-import preserva orden alfabético dentro de cada paréntesis.

- [ ] **Step 5: Update inline imports dentro de funciones (whitespace-prefix)**

```bash
cd D:/VYNTIA/apps/api
grep -rn "    from app_rrhh\.models import" --include="*.py" | grep -E "Empleado|DatosFamiliares|DatosAcademicos|CursosCertificaciones"
```

Para cada match, Edit replacing `app_rrhh.models` → `apps.employees.models` preservando indentación.

- [ ] **Step 6: Submodule path imports**

```bash
grep -rn "from app_rrhh\.models\.\(empleado\|datos_familiares\|datos_academicos\|cursos_certificaciones\)" --include="*.py"
```

Para cada match, replace con `from apps.employees.models import X`.

- [ ] **Step 7: Relative imports en archivos dentro de app_rrhh (services, views, etc.)**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from \.models import" app_rrhh --include="*.py" | grep -E "Empleado|DatosFamiliares|DatosAcademicos|CursosCertificaciones"
```

Si aparecen, son los archivos `app_rrhh/{views,services,serializers,managers,tests}.py` u otros similares. Update a `from apps.employees.models import X`.

- [ ] **Step 8: Inline imports dentro de moved files mismos**

Verifica que `apps/employees/models/{empleado,datos_familiares,datos_academicos,cursos_certificaciones}.py` no se autoreferencien con paths absolutos:

```bash
grep -rn "from apps\.employees\.models import\|from app_rrhh\.models import" apps/api/apps/employees/models --include="*.py"
```

Expected: 0 self-absolute imports en employees/models/. Cualquier import same-app debe ser `from .X import Y`.

- [ ] **Step 9: Verificación final**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models import.*\(Empleado\|DatosFamiliares\|DatosAcademicos\|CursosCertificaciones\)" --include="*.py" || echo "OK: cero matches"
```

Expected: `OK: cero matches`.

---

## Task 10: Update settings — registrar `EmployeesConfig`

```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "apps.employees.apps.EmployeesConfig",
    "app_rrhh",
]
```

Use Edit tool en `apps/api/vyntia/settings/base.py`:
- old_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "app_rrhh",
]
```
- new_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "apps.employees.apps.EmployeesConfig",
    "app_rrhh",
]
```

---

## Task 11: Update `pyproject.toml`

```bash
grep "packages" apps/api/pyproject.toml
```

Use Edit tool:
- old_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization"]`
- new_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees"]`

Reinstall:
```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
pip install -e ".[dev]" 2>&1 | tail -3
cd ../..
```

Expected: `Successfully installed vyntia-api-0.1.0`.

---

## Task 12: NUCLEAR DB regenerate

**Patrón validado en L3.2 y L3.3.** Backup en `/tmp/bd_vyntia_pre_L3.4.dump`.

- [ ] **Step 1: Drop bd_vyntia (kill procs first)**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "DROP DATABASE IF EXISTS bd_vyntia;" 2>&1
```

- [ ] **Step 2: Eliminar migration files existentes**

```bash
cd D:/VYNTIA/apps/api/app_rrhh/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"

cd D:/VYNTIA/apps/api/apps/identity/migrations
git rm 0001_initial.py 2>&1 | tail -2

cd D:/VYNTIA/apps/api/apps/organization/migrations
git rm 0001_initial.py 2>&1 | tail -2

cd D:/VYNTIA
```

- [ ] **Step 3: Generar fresh migrations**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py makemigrations --settings=vyntia.settings.development 2>&1 | tail -25
cd ../..
```

Expected:
- `Migrations for 'app_rrhh':` (sin Empleado, DatosFamiliares, etc.; con DatosLaborales, ContratosAdendas, DocumentosDigitales, OnboardingEmpleado, Vacaciones, ConfiguracionUit, Remuneracion, PlantillaDocumento)
- `Migrations for 'identity':` (con Usuario, Rol, Permiso, UsuarioRoles, RolPermisos, Modulos, ModuloPermiso)
- `Migrations for 'organization':` (con Area, HistorialUbicaciones, ConfiguracionEmpresa)
- `Migrations for 'employees':` con Empleado, DatosFamiliares, DatosAcademicos, CursosCertificaciones
- Posibles `0002_initial.py` para FK ordering

Verificar:
```bash
echo "=== employees 0001 (expected: 4) ==="
grep -E "name='(Empleado|DatosFamiliares|DatosAcademicos|CursosCertificaciones)'" apps/api/apps/employees/migrations/0001_initial.py | wc -l
echo "=== app_rrhh 0001 (expected: 0 employee models) ==="
grep -E "name='(Empleado|DatosFamiliares|DatosAcademicos|CursosCertificaciones)'" apps/api/app_rrhh/migrations/0001_initial.py | wc -l
```

- [ ] **Step 4: Recrear bd_vyntia**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "CREATE DATABASE bd_vyntia WITH ENCODING 'UTF8' TEMPLATE template0;" 2>&1
```

- [ ] **Step 5: Aplicar migraciones**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -20
cd ../..
```

Expected: secuencia `Applying X.0001_initial... OK`. Sin errors.

---

## Task 13: Re-seed

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py setup_roles_permisos --settings=vyntia.settings.development 2>&1 | tail -10
PGPASSWORD='Demenci4@' python manage.py seed_menu --settings=vyntia.settings.development 2>&1 | tail -10
cd ../..
```

Verificar:
```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'rol' AS t, COUNT(*) FROM rol UNION ALL SELECT 'permiso', COUNT(*) FROM permiso UNION ALL SELECT 'modulos', COUNT(*) FROM modulos UNION ALL SELECT 'empleado', COUNT(*) FROM empleado;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0, empleado = 0.

---

## Task 14: Smoke tests

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected:
- check: clean
- pytest: `125 passed, 44 failed, 3 skipped`

runserver smoke:
```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l34.log 2>&1 &
SERVER_PID=$!
sleep 8
curl -s -o /dev/null -w "HTTP %{http_code} /api/docs/\n" http://127.0.0.1:8000/api/docs/
kill $SERVER_PID 2>/dev/null
sleep 1
cd ../..
```

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

Expected: HTTP 200.

Cleanup greps:
```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models import {employees-models} ==="
grep -rn "from app_rrhh\.models import" --include="*.py" | grep -E "Empleado|DatosFamiliares|DatosAcademicos|CursosCertificaciones" || echo "OK"
echo ""
echo "=== B: from .empleado / .datos_familiares / etc. (relative) ==="
grep -rn "from \.empleado\|from \.datos_familiares\|from \.datos_academicos\|from \.cursos_certificaciones" --include="*.py" || echo "OK"
echo ""
echo "=== C: same-app 'Empleado' bare in app_rrhh ==="
grep -rn "'Empleado'\b" apps/api/app_rrhh --include="*.py" || echo "OK"
echo ""
echo "=== D: app_rrhh.models.empleado submodule path ==="
grep -rn "app_rrhh\.models\.\(empleado\|datos_familiares\|datos_academicos\|cursos_certificaciones\)" --include="*.py" || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 15: Atomic commit

```bash
cd D:/VYNTIA
git status --short | head -30
git add apps/api/
git commit -m "chore(L3.4): extract employees app (Empleado, DatosFamiliares, DatosAcademicos, CursosCertificaciones) — fresh migrations after BD nuke + reseed"
```

Verificar:
```bash
git log --oneline vyntia/L3.4-employees-app ^master | head -5
git status --short
```

Expected: 2 commits (`docs(L3.4)` + `chore(L3.4)`), `git status` empty.

---

## Task 16: Merge a master

- [ ] **Step 1: Confirmar autorización del usuario.**

**NO mergear sin autorización.**

- [ ] **Step 2: Merge `--no-ff`**

```bash
git checkout master
git merge --no-ff vyntia/L3.4-employees-app -m "Merge L3.4: extract employees app (Empleado, DatosFamiliares, DatosAcademicos, CursosCertificaciones)"
git log --oneline -5
```

- [ ] **Step 3: Smoke test post-merge**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: ambos verdes con baseline 125/44/3.

---

## Definition of Done — checklist final

- [ ] `apps/api/apps/employees/{__init__.py, apps.py, models/{__init__.py, empleado.py, datos_familiares.py, datos_academicos.py, cursos_certificaciones.py}, migrations/{__init__.py, 0001_initial.py}}`
- [ ] `app_rrhh/models/{empleado, datos_familiares, datos_academicos, cursos_certificaciones}.py` removidos
- [ ] FKs `'Empleado'` en 5 archivos de `app_rrhh/models/` actualizadas a `'employees.Empleado'` (10 ocurrencias)
- [ ] FK `'DatosFamiliares'` en `documentos_digitales.py:153` → `'employees.DatosFamiliares'`
- [ ] FKs `'DocumentosDigitales'` dentro de `apps/employees/models/datos_academicos.py:117` y `cursos_certificaciones.py:25` → `'app_rrhh.DocumentosDigitales'`
- [ ] `empleado.py:263` inline import: `from .datos_laborales import DatosLaborales` → `from app_rrhh.models import DatosLaborales`
- [ ] LOCAL_APPS incluye `EmployeesConfig`; pyproject incluye `apps.employees`
- [ ] Migrations regenerated; employees con 4 modelos; app_rrhh sin ellos
- [ ] bd_vyntia recreada; rol > 0, permiso > 0, modulos > 0
- [ ] `manage.py check` clean; pytest 125/44/3; `/api/docs/` HTTP 200
- [ ] Branch mergeada a master con `--no-ff`
- [ ] Memoria + roadmap actualizados post-merge: L3.4 ✅, L3.5 NEXT

---

## Después de L3.4

**Próximo plan:** L3.5 — extract `contracts` app (ContratosAdendas split → Contract + ContractAmendment, DatosLaborales → EmploymentData).

L3.5 introduce un cambio de modelo de datos: split de ContratosAdendas en dos modelos. Más invasivo que L3.4 (requiere data migration). Plan dedicado.

---

## Notas para el ejecutor

- **Patrón NUCLEAR validado** — re-aplicar.
- **PGPASSWORD env var** explícito por known issue.
- **Class names en español** — rename inglés en L3.10.
- **Managers comentados quedan en `app_rrhh/managers.py`** — orphan code, cleanup en L3.11.
- **Empleado no tiene FKs propios** — solo recibe FKs. Eso simplifica este sub-PR.
- **Lección de L3.3:** buscar relative imports `from .X` dentro de los movidos archivos, imports en `app_rrhh/{views,services,serializers,managers,tests}.py`, submodule path imports `from app_rrhh.models.X import Y`. Anticipar plan-missed locations.
- **Stale Python procs:** Si `psql DROP` falla con "in use", PowerShell kill primero.
