# VYNTIA Foundation L3.5 — Extract `contracts` App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extraer los 2 modelos del dominio contractual (`ContratosAdendas`, `DatosLaborales`) desde `app_rrhh/` hacia una nueva Django app en `apps/api/apps/contracts/`. Class names quedan en español — el rename a inglés (`ContratosAdendas → Contract`, `DatosLaborales → EmploymentData`) **y el split** (`ContratosAdendas → Contract + ContractAmendment`) son **L3.10**.

**Architecture:** L3.5 es **el más sencillo de los sub-PRs medios**: solo 2 modelos, ambos archivos `app_rrhh/models/{contratos_adendas,datos_laborales}.py` ya usan strings lazy correctos para sus FKs salientes (`'employees.Empleado'`, `'organization.Area'`, `'identity.Usuario'`). Los riesgos LR9/LR10 son menores que en L3.4: solo 2 stale refs entrantes (`'ContratosAdendas'` en `vacaciones.py`, `"DatosLaborales"` en `remuneracion.py` — LR10 double-quote). 2 inline imports en apps ya extraídos (`apps/employees/models/empleado.py`, `apps/organization/models/area.py`) que actualmente importan `DatosLaborales` desde `app_rrhh.models` deben re-apuntar a `apps.contracts.models`. Patrón NUCLEAR DB validado en L3.2/L3.3/L3.4 se re-aplica.

**Tech Stack:** Django 5.2 `AppConfig`, NUCLEAR DB strategy (validada en L3.2/L3.3/L3.4), Django management commands para reseed.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L3 — División de apps Django" sub-PR L3.5; § 3.2 "División de modelos"

**Scope decision (deviation from spec § 4 L3.5):**
- El spec menciona `ContratosAdendas → Contract + ContractAmendment (split)` y `DatosLaborales → EmploymentData (rename)` como parte de L3.5
- Patrón establecido en L3.1-L3.4: **mover modelos manteniendo nombres en español; rename a L3.10**
- Por consistencia, L3.5 hace **solo move**. El split de ContratosAdendas en dos modelos requiere data migration (más invasivo que rename) y debe coordinarse con la actualización de serializers/views/frontend; se difiere para post-L3.10 como sub-fase aparte (potencialmente L3.10.1) o incorporarse al rename masivo de L3.10
- Class names que quedan después de L3.5: `ContratosAdendas`, `DatosLaborales` (en `apps.contracts`)

**Pre-condiciones:**
- L3.4 mergeada a master (commit `2f71a8a0`)
- Django 5.2.13, `apps/api/apps/{core,identity,organization,employees}/` operativos
- pytest baseline: 125 passed, 44 failed, 3 skipped
- `bd_vyntia` provisionada con esquema actual; rol > 0, permiso > 0, modulos > 0, empleado = 0
- venv en `D:/VYNTIA/.venv/`

**Definition of Done:**
- [ ] `apps/api/apps/contracts/` existe con `apps.py`, `models/`, `migrations/`
- [ ] Modelos `ContratosAdendas`, `DatosLaborales` movidos a `apps/contracts/models/`
- [ ] `app_rrhh/models/{contratos_adendas,datos_laborales}.py` eliminados
- [ ] `ContractsConfig` en `LOCAL_APPS`
- [ ] FK string `'ContratosAdendas'` en `app_rrhh/models/vacaciones.py:177` → `'contracts.ContratosAdendas'`
- [ ] FK string `"DatosLaborales"` (DOUBLE-QUOTE — LR10) en `app_rrhh/models/remuneracion.py:231` → `"contracts.DatosLaborales"`
- [ ] Inline import en `apps/employees/models/empleado.py:263`: `from app_rrhh.models import DatosLaborales` → `from apps.contracts.models import DatosLaborales`
- [ ] Inline import en `apps/organization/models/area.py:106`: `from app_rrhh.models import DatosLaborales` → `from apps.contracts.models import DatosLaborales`
- [ ] Migraciones regeneradas: app_rrhh sin ContratosAdendas/DatosLaborales; contracts con ambos
- [ ] `bd_vyntia` recreada y reseeded (rol > 0, permiso > 0, modulos > 0)
- [ ] Imports actualizados across ~17 archivos (services, views, serializers, scripts, tests)
- [ ] `pyproject.toml` `packages` incluye `"apps.contracts"`
- [ ] `python manage.py check` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.5-contracts-app` mergeada a master con `--no-ff`

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/apps/contracts/__init__.py` | empty |
| Create | `apps/api/apps/contracts/apps.py` | `ContractsConfig(AppConfig)` con `name="apps.contracts"`, `label="contracts"` |
| Create | `apps/api/apps/contracts/models/__init__.py` | re-exporta los 2 modelos |
| Move | `app_rrhh/models/contratos_adendas.py` → `apps/api/apps/contracts/models/contratos_adendas.py` | FKs salientes ya son strings lazy correctas (`'employees.Empleado'`, `'organization.Area'`, `'identity.Usuario'`) — no se editan |
| Move | `app_rrhh/models/datos_laborales.py` → `apps/api/apps/contracts/models/datos_laborales.py` | FKs salientes ya son strings lazy correctas (`'employees.Empleado'`, `'organization.Area'`) — no se editan |
| Create | `apps/api/apps/contracts/migrations/__init__.py` | empty |
| Modify | `apps/api/app_rrhh/models/vacaciones.py` | FK `'ContratosAdendas'` → `'contracts.ContratosAdendas'` (línea 177, single-quote) |
| Modify | `apps/api/app_rrhh/models/remuneracion.py` | FK `"DatosLaborales"` → `"contracts.DatosLaborales"` (línea 231, **DOUBLE-QUOTE — LR10**) |
| Modify | `apps/api/app_rrhh/models/__init__.py` | quitar `from .contratos_adendas import ContratosAdendas`, `from .datos_laborales import DatosLaborales`, y entries en `__all__` (`"DatosLaborales"`, `"ContratosAdendas"`) |
| Modify | `apps/api/apps/employees/models/empleado.py` | inline import línea 263: `from app_rrhh.models import DatosLaborales` → `from apps.contracts.models import DatosLaborales` |
| Modify | `apps/api/apps/organization/models/area.py` | inline import línea 106: `from app_rrhh.models import DatosLaborales` → `from apps.contracts.models import DatosLaborales` |
| Modify | `apps/api/vyntia/settings/base.py` | añadir `"apps.contracts.apps.ContractsConfig"` a `LOCAL_APPS` (después de employees, antes de app_rrhh) |
| Modify | `apps/api/pyproject.toml` | añadir `"apps.contracts"` a `packages` |
| Modify (~15 files) | varios en `api/v1/`, `app_rrhh/services/`, `app_rrhh/{views,serializers,managers,tests}.py`, `scripts/`, `tests/` | replace `from app_rrhh.models import ... {ContratosAdendas\|DatosLaborales}` → `from apps.contracts.models import ...`. Submodule path `from app_rrhh.models.contratos_adendas import X` y `from app_rrhh.models.datos_laborales import X` también |
| Delete | `app_rrhh/migrations/0001_initial.py` + `0002_initial.py` | regenerated |
| Delete | `apps/identity/migrations/0001_initial.py` | regenerated |
| Delete | `apps/organization/migrations/0001_initial.py` | regenerated |
| Delete | `apps/employees/migrations/0001_initial.py` (+ `0002_initial.py` si existe) | regenerated |

**NO se toca en L3.5:**
- Class names (rename a inglés es L3.10)
- Field names
- Frontend
- Split de `ContratosAdendas` en `Contract + ContractAmendment` (deferido a L3.10/sub-fase)
- DocumentosDigitales / PlantillaDocumento (queda en app_rrhh hasta L3.6)
- Remuneracion / ConfiguracionUit (queda en app_rrhh hasta L3.7)
- Vacaciones (queda en app_rrhh hasta L3.8)
- Onboarding (queda en app_rrhh hasta L3.9)
- Manager `ContratosAdendasManager` está comentado en `contratos_adendas.py:217,399-400` y vive como orphan en `app_rrhh/managers/contratos_manager.py` — cleanup en L3.11

**Lecciones aplicadas (LR9, LR10) explícitamente:**
- **LR9** (stale `'app_rrhh.X'` strings en apps ya extraídas): grep `'app_rrhh.ContratosAdendas'` y `'app_rrhh.DatosLaborales'` (single + double quote) **across TODOS los apps** después del move. Inventario actual: 0 stale refs detectadas pre-move (los archivos `apps/{employees,organization}` usan inline `from app_rrhh.models import DatosLaborales` que se actualiza en Task 9).
- **LR10** (double-quote FK strings perdidos por sed `'X'`): `app_rrhh/models/remuneracion.py:231` usa `"DatosLaborales"` con DOUBLE-QUOTE. El sed bulk debe procesar **ambas** formas (`'X'` y `"X"`).

**Inventario de inbound FK strings (verificado pre-move):**
- `app_rrhh/models/vacaciones.py:177` → `'ContratosAdendas'` (single-quote)
- `app_rrhh/models/remuneracion.py:231` → `"DatosLaborales"` (DOUBLE-QUOTE)
- 0 ocurrencias de `'app_rrhh.ContratosAdendas'` o `'app_rrhh.DatosLaborales'` (single o double)

**Inventario de imports a actualizar (verificado pre-move, ~17 archivos):**

| Archivo | Pattern | Notas |
|---|---|---|
| `tests/test_contratos_integration.py:17-20` | multi-line: `from app_rrhh.models import (\n    DatosLaborales,\n    ContratosAdendas, DocumentosDigitales\n)` | mixed con DocumentosDigitales — split |
| `tests/test_area_model.py:12` | single-line: `from app_rrhh.models import DatosLaborales` | replace puro |
| `scripts/seed_vacaciones_reporte_demo.py:12,13` | submodule: `from app_rrhh.models.datos_laborales import DatosLaborales`, `from app_rrhh.models.contratos_adendas import ContratosAdendas` | replace path |
| `scripts/seed_vacaciones_historial_demo.py:26` | submodule: `from app_rrhh.models.contratos_adendas import ContratosAdendas` | replace path |
| `scripts/load_demo_data.py:56-58` | multi-line solo con DatosLaborales: `from app_rrhh.models import (\n    DatosLaborales,\n)` | replace módulo |
| `apps/organization/models/area.py:106` | inline en función: `from app_rrhh.models import DatosLaborales` | replace módulo |
| `apps/employees/models/empleado.py:263` | inline en función: `from app_rrhh.models import DatosLaborales` | replace módulo |
| `app_rrhh/services/template_service.py:16` | mixed: `from app_rrhh.models import ContratosAdendas, DocumentosDigitales` | split |
| `app_rrhh/services/pdf_generator.py:47` | mixed: `from app_rrhh.models import DocumentosDigitales, ContratosAdendas` | split |
| `app_rrhh/services/vacation_calculation_service.py:12` | single: `from app_rrhh.models import ContratosAdendas` | replace módulo |
| `app_rrhh/services/word_template_service.py:173` | inline: `from app_rrhh.models import ContratosAdendas` | replace módulo |
| `api/v1/rrhh/contratos_views.py:3` | single: `from app_rrhh.models import ContratosAdendas` | replace módulo |
| `api/v1/rrhh/contratos_serializers.py:15` | mixed: `from app_rrhh.models import ContratosAdendas, DocumentosDigitales` | split |
| `api/v1/rrhh/serializers.py:6-13` | multi-line mixed con varios: `from app_rrhh.models import (..., ContratosAdendas, DatosLaborales, ...)` | split |
| `api/v1/rrhh/views.py:9-15` | multi-line mixed con DatosLaborales | split |
| `api/v1/rrhh/remuneraciones_views.py:648` | inline submodule: `from app_rrhh.models.datos_laborales import DatosLaborales` | replace path |
| `api/v1/rrhh/filters.py:6` | single: `from app_rrhh.models import DatosLaborales` | replace módulo |

Adicionales a verificar por grep durante ejecución (Task 9 Step 1 inventario):
- `app_rrhh/models.py` (flat file legacy — verificar)
- `app_rrhh/views.py`, `app_rrhh/serializers.py`, `app_rrhh/serializers_optimized.py`
- `app_rrhh/managers.py`, `app_rrhh/managers/contratos_manager.py`
- `app_rrhh/services.py`, `app_rrhh/tests.py`
- `app_rrhh/urls.py`, `api/v1/rrhh/urls.py`, `api/v1/app_rrhh/urls.py`
- `api/v1/app_rrhh/document_generation_views.py:9-14` (verificado en preview: import multi-line con ambos)

---

## Task 1: Pre-flight — branch, baseline, backup

- [ ] **Step 1: Confirmar pwd y master limpio post-L3.4**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -3
```

Expected: HEAD = `363998f2 docs(L3.4): mark L3.4 merged, L3.5 as next` o más reciente. `git status` vacío excepto este plan untracked.

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
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.5.dump 2>&1 | tail -3
ls -lh /tmp/bd_vyntia_pre_L3.5.dump
```

Expected: dump ~250-500 KB.

- [ ] **Step 5: Crear branch L3.5**

```bash
git checkout -b vyntia/L3.5-contracts-app
git status --short
```

---

## Task 2: Comitear el plan en la branch

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.5-contracts.md
git commit -m "docs(L3.5): add contracts app extraction plan"
```

---

## Task 3: Crear estructura `apps/contracts/`

- [ ] **Step 1: Crear directorios + empty `__init__.py`**

```bash
cd D:/VYNTIA
mkdir -p apps/api/apps/contracts/models
mkdir -p apps/api/apps/contracts/migrations
touch apps/api/apps/contracts/__init__.py
touch apps/api/apps/contracts/migrations/__init__.py
```

- [ ] **Step 2: Crear `apps/contracts/apps.py`**

Use Write tool con contenido EXACTO:

```python
"""AppConfig for the `apps.contracts` Django app — VYNTIA employment relationship.

Owns the contractual/employment-relationship entities of an employee:
- ContratosAdendas (employment contract — initial contract or amendment/adenda;
  unified table that handles both via numero_adenda nullable)
- DatosLaborales (current employment data: position, work modality, salary base,
  schedule, direct supervisor, regimen laboral peruano)

Bounded context boundary: contracts captures HOW someone is employed —
the legal contract instrument and the operational employment terms. Personal
data of the employee lives in `apps.employees`. Compensation calculations
(payroll runs, deductions, AFP/SUNAT) live in `apps.payroll` (L3.7).

Future split (deferred to L3.10/post-rename):
- ContratosAdendas → Contract + ContractAmendment (model split + data migration)
- DatosLaborales → EmploymentData (rename only)
"""

from django.apps import AppConfig


class ContractsConfig(AppConfig):
    name = "apps.contracts"
    label = "contracts"
    verbose_name = "VYNTIA Contracts"
```

- [ ] **Step 3: Crear placeholder `apps/contracts/models/__init__.py`**

```python
"""Contracts models — re-exports for backward-compatible imports.

Populated when models are physically moved.
"""
```

---

## Task 4: Mover los 2 model files con `git mv`

- [ ] **Step 1: Defensive — kill stale Python procs**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 2: `git mv` los 2 archivos**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/models/contratos_adendas.py apps/api/apps/contracts/models/contratos_adendas.py
git mv apps/api/app_rrhh/models/datos_laborales.py apps/api/apps/contracts/models/datos_laborales.py
```

- [ ] **Step 3: Verificar layout**

```bash
ls apps/api/apps/contracts/models/
ls apps/api/app_rrhh/models/contratos_adendas.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/models/datos_laborales.py 2>&1 || echo "OK: removed"
```

Expected: 2 model files + `__init__.py` en contracts/models/. Originals removed.

---

## Task 5: Verificar FK strings DENTRO de los archivos movidos (no editar)

Los dos archivos `contratos_adendas.py` y `datos_laborales.py` ya usan strings lazy correctas para sus FKs salientes — heredado del trabajo de L3.2/L3.3/L3.4. No se requieren cambios internos.

- [ ] **Step 1: Confirmar que NO hay FKs malas (regression check)**

```bash
cd D:/VYNTIA/apps/api
echo "=== Outbound FKs en contratos_adendas.py (deben ser strings lazy con app prefix) ==="
grep -n "ForeignKey" apps/contracts/models/contratos_adendas.py
echo ""
echo "=== Outbound FKs en datos_laborales.py ==="
grep -n "ForeignKey" apps/contracts/models/datos_laborales.py
echo ""
echo "=== Bare 'Empleado' (sin app prefix) en contracts/models/ — should be 0 ==="
grep -rn "'Empleado'\b\|\"Empleado\"" apps/contracts/models/ --include="*.py" || echo "OK: cero"
echo ""
echo "=== Bare 'Area' (sin app prefix) en contracts/models/ — should be 0 ==="
grep -rn "'Area'\b\|\"Area\"" apps/contracts/models/ --include="*.py" || echo "OK: cero"
echo ""
echo "=== Bare 'Usuario' (sin app prefix) en contracts/models/ — should be 0 ==="
grep -rn "'Usuario'\b\|\"Usuario\"" apps/contracts/models/ --include="*.py" || echo "OK: cero"
cd ../..
```

Expected:
- Todas las FKs con prefix: `'employees.Empleado'`, `'organization.Area'`, `'identity.Usuario'`
- Tres "OK: cero"

Si algún grep encuentra match sin prefix, **detener y corregir** antes de continuar (esto sería un stale ref pre-existente que L3.4 dejó, equivalente a LR9).

---

## Task 6: Update FK strings entrantes en archivos `app_rrhh/models/` que se quedan

**Files:**
- Modify: `apps/api/app_rrhh/models/vacaciones.py:177` (single-quote `'ContratosAdendas'`)
- Modify: `apps/api/app_rrhh/models/remuneracion.py:231` (**DOUBLE-QUOTE `"DatosLaborales"`** — LR10)

**Por qué:** Después del move, ContratosAdendas y DatosLaborales viven en `contracts`. Los modelos que quedan en app_rrhh deben usar string lazy con prefix `'contracts.X'`.

- [ ] **Step 1: Bulk replace ambas formas (single + double quote) — LR10**

Esta es la lección más fuerte de L3.4. NO se puede usar solo single-quote sed — `remuneracion.py:231` tiene double-quote.

```bash
cd D:/VYNTIA/apps/api
find app_rrhh/models -type f -name "*.py" -not -path "*/__pycache__/*" -print0 | xargs -0 sed -i \
  -e "s|'ContratosAdendas'|'contracts.ContratosAdendas'|g" \
  -e 's|"ContratosAdendas"|"contracts.ContratosAdendas"|g' \
  -e "s|'DatosLaborales'|'contracts.DatosLaborales'|g" \
  -e 's|"DatosLaborales"|"contracts.DatosLaborales"|g'
```

- [ ] **Step 2: Verificar updates (single + double quote, ambos modelos)**

```bash
cd D:/VYNTIA/apps/api
echo "=== contracts.ContratosAdendas refs (expected: 1) ==="
grep -rn "'contracts\.ContratosAdendas'\|\"contracts\.ContratosAdendas\"" app_rrhh/models --include="*.py"
echo ""
echo "=== contracts.DatosLaborales refs (expected: 1) ==="
grep -rn "'contracts\.DatosLaborales'\|\"contracts\.DatosLaborales\"" app_rrhh/models --include="*.py"
echo ""
echo "=== Bare 'ContratosAdendas' refs (should be 0) ==="
grep -rn "'ContratosAdendas'\b\|\"ContratosAdendas\"" app_rrhh/models --include="*.py" || echo "OK: cero"
echo ""
echo "=== Bare 'DatosLaborales' refs (should be 0) ==="
grep -rn "'DatosLaborales'\b\|\"DatosLaborales\"" app_rrhh/models --include="*.py" || echo "OK: cero"
cd ../..
```

Expected:
- 1 hit `'contracts.ContratosAdendas'` (vacaciones.py:177)
- 1 hit `"contracts.DatosLaborales"` (remuneracion.py:231 — preserva double-quote)
- 0 bare refs.

- [ ] **Step 3: Sanity check across TODOS los apps (LR9 — stale `'app_rrhh.X'` from previously moved apps)**

```bash
cd D:/VYNTIA/apps/api
echo "=== Stale 'app_rrhh.ContratosAdendas' anywhere — should be 0 ==="
grep -rn "'app_rrhh\.ContratosAdendas'\|\"app_rrhh\.ContratosAdendas\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=migrations || echo "OK: cero"
echo ""
echo "=== Stale 'app_rrhh.DatosLaborales' anywhere — should be 0 ==="
grep -rn "'app_rrhh\.DatosLaborales'\|\"app_rrhh\.DatosLaborales\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=migrations || echo "OK: cero"
cd ../..
```

Expected: ambos `OK: cero`.

Si algún match aparece, es un stale ref de L3.2/L3.3/L3.4 (LR9) y debe actualizarse a `'contracts.X'`.

---

## Task 7: Crear `apps/contracts/models/__init__.py` con re-exports

Use Write tool en `apps/api/apps/contracts/models/__init__.py`:

```python
"""Contracts models — re-exports for backward-compatible imports."""

from .contratos_adendas import ContratosAdendas
from .datos_laborales import DatosLaborales

__all__ = [
    "ContratosAdendas",
    "DatosLaborales",
]
```

- [ ] **Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.contracts.models import ContratosAdendas, DatosLaborales; print('OK')"
cd ../..
```

Expected: `OK`. Si falla, hay imports rotos en algún model file (probablemente relative imports a otros archivos que ya no existen).

---

## Task 8: Update `app_rrhh/models/__init__.py` — quitar exports de contracts

- [ ] **Step 1: Read current state**

```bash
grep -n "from .contratos_adendas\|from .datos_laborales\|\"ContratosAdendas\"\|\"DatosLaborales\"" apps/api/app_rrhh/models/__init__.py
```

Expected:
- línea 12: `from .contratos_adendas import ContratosAdendas`
- línea 13: `from .datos_laborales import DatosLaborales`
- línea 38: `    "DatosLaborales",`
- línea 48: `    "ContratosAdendas",`

- [ ] **Step 2: Use Edit tool para eliminar las 2 líneas import**

Use Edit tool en `apps/api/app_rrhh/models/__init__.py`:
- old_string:
```python
from .configuracion_uit import ConfiguracionUit
from .contratos_adendas import ContratosAdendas
from .datos_laborales import DatosLaborales
from .documentos_digitales import DocumentosDigitales
```
- new_string:
```python
from .configuracion_uit import ConfiguracionUit
from .documentos_digitales import DocumentosDigitales
```

- [ ] **Step 3: Use Edit tool para eliminar `"DatosLaborales"` del `__all__`**

Use Edit tool en `apps/api/app_rrhh/models/__init__.py`:
- old_string:
```python
__all__ = [
    # Modelos principales
    "DatosLaborales",
    "DocumentosDigitales",
```
- new_string:
```python
__all__ = [
    # Modelos principales
    "DocumentosDigitales",
```

- [ ] **Step 4: Use Edit tool para eliminar `"ContratosAdendas"` + comentario de la sección "Modelos de contratos"**

Read primero el bloque exacto:

```bash
sed -n '45,52p' apps/api/app_rrhh/models/__init__.py
```

Luego Edit. La sección actual:
```python
    # Modelos de contratos
    # 'ContratoAdenda',  # Comentado para evitar conflicto de tabla
    "ContratosAdendas",
    # Modelo de onboarding
```

Use Edit:
- old_string:
```python
    # Modelos de contratos
    # 'ContratoAdenda',  # Comentado para evitar conflicto de tabla
    "ContratosAdendas",
    # Modelo de onboarding
```
- new_string:
```python
    # Modelo de onboarding
```

- [ ] **Step 5: Verificar limpieza**

```bash
grep -n "ContratosAdendas\|DatosLaborales\|contratos_adendas\|datos_laborales" apps/api/app_rrhh/models/__init__.py || echo "OK: removed"
```

Expected: `OK: removed`.

---

## Task 9: Bulk update absolute imports across the codebase

**Pattern:** `from app_rrhh.models import {ContratosAdendas|DatosLaborales}` → `from apps.contracts.models import ...`. Y submodule paths `from app_rrhh.models.{contratos_adendas|datos_laborales} import X` → `from apps.contracts.models import X`.

- [ ] **Step 1: Inventario completo (re-verificación pre-edit)**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "ContratosAdendas|DatosLaborales|contratos_adendas|datos_laborales"
cd ../..
```

Expected: ~17 hits, distribuidos across los archivos del File Structure Overview.

- [ ] **Step 2: Sed para imports puros (single-import lines exactos)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/contracts/*" \
  -print0 | xargs -0 sed -i \
  -e 's|^from app_rrhh\.models import \(ContratosAdendas\)$|from apps.contracts.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(DatosLaborales\)$|from apps.contracts.models import \1|g'
cd ../..
```

- [ ] **Step 3: Sed para inline imports en funciones (whitespace-prefix)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/contracts/*" \
  -print0 | xargs -0 sed -i -E \
  -e 's|^([[:space:]]+)from app_rrhh\.models import (ContratosAdendas|DatosLaborales)$|\1from apps.contracts.models import \2|g'
cd ../..
```

Verificar específicamente:
```bash
grep -n "from app_rrhh.models import\|from apps.contracts.models import" apps/api/apps/employees/models/empleado.py
grep -n "from app_rrhh.models import\|from apps.contracts.models import" apps/api/apps/organization/models/area.py
```

Expected: ambos archivos ahora con `from apps.contracts.models import DatosLaborales` (mantiene indentación).

- [ ] **Step 4: Sed para submodule path imports**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/contracts/*" \
  -print0 | xargs -0 sed -i \
  -e 's|from app_rrhh\.models\.contratos_adendas import \(ContratosAdendas\)|from apps.contracts.models import \1|g' \
  -e 's|from app_rrhh\.models\.datos_laborales import \(DatosLaborales\)|from apps.contracts.models import \1|g'
cd ../..
```

Verificar:
```bash
grep -rn "from app_rrhh\.models\.contratos_adendas\|from app_rrhh\.models\.datos_laborales" apps/api --include="*.py" || echo "OK: cero"
```

Expected: `OK: cero`.

- [ ] **Step 5: Manual fix para imports mezclados (single-line con coma)**

Cualquier línea como `from app_rrhh.models import A, ContratosAdendas, B` no fue tocada por el sed (que solo matchea single-import). Identificarlas:

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models import.*\(ContratosAdendas\|DatosLaborales\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | head -30
cd ../..
```

Para cada match:
- Si línea es `from app_rrhh.models import A, ContratosAdendas, B` → split en `from app_rrhh.models import A, B` + nueva línea `from apps.contracts.models import ContratosAdendas`
- Si tiene ambos (ContratosAdendas y DatosLaborales) → split en una sola nueva línea `from apps.contracts.models import ContratosAdendas, DatosLaborales` (alfabético)
- Mantener orden alfabético dentro de cada paréntesis

Contracts model names a reconocer: `ContratosAdendas`, `DatosLaborales`.

Casos esperados a procesar manualmente con Edit:
- `app_rrhh/services/template_service.py:16` — `from app_rrhh.models import ContratosAdendas, DocumentosDigitales` → split
- `app_rrhh/services/pdf_generator.py:47` — `from app_rrhh.models import DocumentosDigitales, ContratosAdendas` → split
- `api/v1/rrhh/contratos_serializers.py:15` — `from app_rrhh.models import ContratosAdendas, DocumentosDigitales` → split

Para cada uno, leer el archivo, luego Edit con el bloque exacto.

- [ ] **Step 6: Manual fix para imports multi-línea con parens**

```bash
cd D:/VYNTIA/apps/api
grep -rn -B 0 -A 12 "from app_rrhh\.models import (" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations 2>&1 | head -120
cd ../..
```

Para cada match con `ContratosAdendas` o `DatosLaborales` dentro del paréntesis:
- Eliminar la(s) línea(s) `    ContratosAdendas,` y/o `    DatosLaborales,` del bloque
- Añadir nueva import line **después** del bloque cerrado: `from apps.contracts.models import ContratosAdendas, DatosLaborales` (alfabético, solo los que aplican)

Casos esperados:
- `tests/test_contratos_integration.py:17-20` — bloque mixto
- `scripts/load_demo_data.py:56-58` — solo DatosLaborales (paréntesis con un único modelo)
- `api/v1/rrhh/serializers.py:6-13` — bloque mixto con ambos
- `api/v1/rrhh/views.py:9-15` — bloque mixto con DatosLaborales
- `api/v1/app_rrhh/document_generation_views.py:9-14` — bloque mixto con ambos

Para cada uno, Read + Edit.

- [ ] **Step 7: Self-absolute import check en moved files**

Verifica que `apps/contracts/models/{contratos_adendas,datos_laborales}.py` no se autoreferencien con paths absolutos:

```bash
grep -rn "from apps\.contracts\.models import\|from app_rrhh\.models import" apps/api/apps/contracts/models --include="*.py" || echo "OK: cero"
```

Expected: 0 self-absolute imports en contracts/models/. (Estos archivos no deberían tener este patrón; pero L3.4 enseñó a verificar.)

- [ ] **Step 8: Verificación final exhaustiva**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models import {contracts-models} (post-update) ==="
grep -rn "from app_rrhh\.models import" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "ContratosAdendas|DatosLaborales" || echo "OK"
echo ""
echo "=== B: from app_rrhh.models.contratos_adendas / .datos_laborales (submodule) ==="
grep -rn "from app_rrhh\.models\.contratos_adendas\|from app_rrhh\.models\.datos_laborales" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== C: bare 'ContratosAdendas' / 'DatosLaborales' FK strings en app_rrhh ==="
grep -rn "'ContratosAdendas'\b\|\"ContratosAdendas\"\|'DatosLaborales'\b\|\"DatosLaborales\"" app_rrhh --include="*.py" || echo "OK"
echo ""
echo "=== D: stale 'app_rrhh.ContratosAdendas' / 'app_rrhh.DatosLaborales' anywhere ==="
grep -rn "'app_rrhh\.ContratosAdendas'\|'app_rrhh\.DatosLaborales'\|\"app_rrhh\.ContratosAdendas\"\|\"app_rrhh\.DatosLaborales\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 10: Update settings — registrar `ContractsConfig`

Use Edit tool en `apps/api/vyntia/settings/base.py`:
- old_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "apps.employees.apps.EmployeesConfig",
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
    "apps.contracts.apps.ContractsConfig",
    "app_rrhh",
]
```

Verificar:
```bash
grep -A 7 "LOCAL_APPS = \[" apps/api/vyntia/settings/base.py
```

---

## Task 11: Update `pyproject.toml`

```bash
grep "packages" apps/api/pyproject.toml
```

Expected: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees"]`

Use Edit tool en `apps/api/pyproject.toml`:
- old_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees"]`
- new_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts"]`

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

**Patrón validado en L3.2, L3.3, L3.4.** Backup en `/tmp/bd_vyntia_pre_L3.5.dump`.

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

cd D:/VYNTIA/apps/api/apps/employees/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"

cd D:/VYNTIA
```

- [ ] **Step 3: Generar fresh migrations**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py makemigrations --settings=vyntia.settings.development 2>&1 | tail -25
cd ../..
```

Expected:
- `Migrations for 'app_rrhh':` (sin ContratosAdendas, DatosLaborales; con DocumentosDigitales, OnboardingEmpleado, Vacaciones, ConfiguracionUit, Remuneracion, PlantillaDocumento)
- `Migrations for 'identity':` (con Usuario, Rol, Permiso, UsuarioRoles, RolPermisos, Modulos, ModuloPermiso)
- `Migrations for 'organization':` (con Area, HistorialUbicaciones, ConfiguracionEmpresa)
- `Migrations for 'employees':` (con Empleado, DatosFamiliares, DatosAcademicos, CursosCertificaciones)
- `Migrations for 'contracts':` con ContratosAdendas, DatosLaborales
- Posibles `0002_initial.py` para FK ordering

Verificar:
```bash
echo "=== contracts 0001 (expected: 2 — ContratosAdendas + DatosLaborales) ==="
grep -E "name='(ContratosAdendas|DatosLaborales)'" apps/api/apps/contracts/migrations/0001_initial.py | wc -l
echo "=== app_rrhh 0001 (expected: 0 contracts models) ==="
grep -E "name='(ContratosAdendas|DatosLaborales)'" apps/api/app_rrhh/migrations/0001_initial.py | wc -l
```

- [ ] **Step 4: Recrear bd_vyntia**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "CREATE DATABASE bd_vyntia WITH ENCODING 'UTF8' TEMPLATE template0;" 2>&1
```

- [ ] **Step 5: Aplicar migraciones**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -25
cd ../..
```

Expected: secuencia `Applying X.0001_initial... OK` para todos los apps. Sin errores. La tabla física conserva los nombres `contratos_adendas` y `datos_laborales` (definidos en `Meta.db_table`).

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
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'rol' AS t, COUNT(*) FROM rol UNION ALL SELECT 'permiso', COUNT(*) FROM permiso UNION ALL SELECT 'modulos', COUNT(*) FROM modulos UNION ALL SELECT 'empleado', COUNT(*) FROM empleado UNION ALL SELECT 'contratos_adendas', COUNT(*) FROM contratos_adendas UNION ALL SELECT 'datos_laborales', COUNT(*) FROM datos_laborales;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0, empleado = 0, contratos_adendas = 0, datos_laborales = 0.

---

## Task 14: Smoke tests

- [ ] **Step 1: Django check + pytest baseline**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected:
- check: clean
- pytest: `125 passed, 44 failed, 3 skipped`

Si pytest divergir del baseline, **investigar** antes de continuar — algún import o FK no fue actualizado.

- [ ] **Step 2: runserver smoke**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l35.log 2>&1 &
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

Expected: `HTTP 200 /api/docs/`.

- [ ] **Step 3: Cleanup greps finales**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models import {contracts-models} ==="
grep -rn "from app_rrhh\.models import" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "ContratosAdendas|DatosLaborales" || echo "OK"
echo ""
echo "=== B: from .contratos_adendas / .datos_laborales (relative en app_rrhh) ==="
grep -rn "from \.contratos_adendas\|from \.datos_laborales" app_rrhh --include="*.py" || echo "OK"
echo ""
echo "=== C: same-app 'ContratosAdendas'/'DatosLaborales' bare en app_rrhh ==="
grep -rn "'ContratosAdendas'\b\|\"ContratosAdendas\"\|'DatosLaborales'\b\|\"DatosLaborales\"" app_rrhh --include="*.py" || echo "OK"
echo ""
echo "=== D: app_rrhh.models.{contratos_adendas|datos_laborales} submodule path ==="
grep -rn "app_rrhh\.models\.\(contratos_adendas\|datos_laborales\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== E: stale 'app_rrhh.ContratosAdendas' / 'app_rrhh.DatosLaborales' (LR9) ==="
grep -rn "'app_rrhh\.ContratosAdendas'\|'app_rrhh\.DatosLaborales'\|\"app_rrhh\.ContratosAdendas\"\|\"app_rrhh\.DatosLaborales\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 15: Atomic commit

```bash
cd D:/VYNTIA
git status --short | head -40
git add apps/api/
git commit -m "chore(L3.5): extract contracts app (ContratosAdendas, DatosLaborales) — fresh migrations after BD nuke + reseed"
```

Verificar:
```bash
git log --oneline vyntia/L3.5-contracts-app ^master | head -5
git status --short
```

Expected: 2 commits (`docs(L3.5)` + `chore(L3.5)`), `git status` empty.

---

## Task 16: Merge a master

- [ ] **Step 1: Confirmar autorización del usuario.**

**NO mergear sin autorización.**

- [ ] **Step 2: Merge `--no-ff`**

```bash
git checkout master
git merge --no-ff vyntia/L3.5-contracts-app -m "Merge L3.5: extract contracts app (ContratosAdendas, DatosLaborales)"
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

- [ ] **Step 4: Update roadmap + memoria post-merge**

Update `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md` Status column: L3.5 → ✅ con merge SHA. L3.6 → ⏳ NEXT.

Commit:
```bash
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.5): mark L3.5 merged, L3.6 as next in roadmap"
```

---

## Definition of Done — checklist final

- [ ] `apps/api/apps/contracts/{__init__.py, apps.py, models/{__init__.py, contratos_adendas.py, datos_laborales.py}, migrations/{__init__.py, 0001_initial.py}}`
- [ ] `app_rrhh/models/{contratos_adendas, datos_laborales}.py` removidos
- [ ] FK `'ContratosAdendas'` en `app_rrhh/models/vacaciones.py:177` → `'contracts.ContratosAdendas'`
- [ ] FK `"DatosLaborales"` en `app_rrhh/models/remuneracion.py:231` → `"contracts.DatosLaborales"` (DOUBLE-QUOTE preservada)
- [ ] Inline import `from app_rrhh.models import DatosLaborales` en `apps/employees/models/empleado.py:263` y `apps/organization/models/area.py:106` → `from apps.contracts.models import DatosLaborales`
- [ ] LOCAL_APPS incluye `ContractsConfig`; pyproject incluye `apps.contracts`
- [ ] Migrations regenerated; contracts con 2 modelos; app_rrhh sin ellos
- [ ] bd_vyntia recreada; rol > 0, permiso > 0, modulos > 0, contratos_adendas = 0, datos_laborales = 0
- [ ] `manage.py check` clean; pytest 125/44/3; `/api/docs/` HTTP 200
- [ ] 0 stale `'app_rrhh.{ContratosAdendas|DatosLaborales}'` strings (single + double-quote) anywhere (LR9)
- [ ] 0 bare `'ContratosAdendas'` / `"DatosLaborales"` strings en `app_rrhh/` (LR10 sed cubrió ambas formas)
- [ ] Branch mergeada a master con `--no-ff`
- [ ] Memoria + roadmap actualizados post-merge: L3.5 ✅, L3.6 NEXT

---

## Después de L3.5

**Próximo plan:** L3.6 — extract `documents` app (`DocumentosDigitales`, `PlantillaDocumento` + services PDF/Word).

L3.6 incluye 3 services (`pdf_generator.py`, `template_service.py`, `word_template_service.py`) que actualmente dependen de `ContratosAdendas` (ahora `contracts.ContratosAdendas`) y `DatosLaborales`. Esto será un cross-app **service** dependency, no una FK — el patrón aquí será mantener las imports cross-app via service public API o inline imports controlados.

---

## Notas para el ejecutor

- **Patrón NUCLEAR validado** — re-aplicar igual que L3.4.
- **PGPASSWORD env var** explícito por known issue (Windows env con caracteres no-ASCII).
- **Class names en español** — rename inglés en L3.10. **Split `ContratosAdendas → Contract + ContractAmendment` deferido** — requiere data migration y debe coordinarse con L3.10 o sub-fase posterior.
- **Manager `ContratosAdendasManager` está orphan** en `app_rrhh/managers/contratos_manager.py` — se queda allí (cleanup en L3.11).
- **LR10 (double-quote FK)** — `remuneracion.py:231` usa `"DatosLaborales"` con DOUBLE-QUOTE. El sed bulk en Task 6 procesa ambas formas. Verificar post-sed con grep que cubra ambas.
- **LR9 (stale `app_rrhh.X`)** — pre-move detectó 0 stale refs heredados, pero el grep en Task 6 Step 3 + Task 9 Step 8 valida que no se introduzcan nuevos.
- **Inbound FKs son solo 2** — este sub-PR es más pequeño que L3.4 (que tenía 10+ FKs entrantes a Empleado).
- **Outbound FKs son CORRECTAS pre-move** — los archivos `contratos_adendas.py` y `datos_laborales.py` heredaron strings lazy correctas de updates anteriores. Verificación en Task 5 confirma.
- **Stale Python procs:** Si `psql DROP` falla con "in use", PowerShell kill primero.
- **Inline imports en moved files** — los archivos `contratos_adendas.py` y `datos_laborales.py` no contienen inline imports de otros modelos (verificable con `grep "    from " apps/api/apps/contracts/models/*.py`). Esto simplifica el move vs L3.4 (donde `empleado.py:263` requirió fix).
