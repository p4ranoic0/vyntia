# VYNTIA Foundation L3.7 — Extract `payroll` App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extraer los 9 modelos de remuneraciones (`PlanillaMensual`, `DetallePlanilla`, `ConceptoPlanilla`, `ConfiguracionAfp`, `ConfiguracionRemuneracion`, `DescuentoMasivo`, `BoletaPago`, `CalendarioPago`) + `ConfiguracionUit` **y sus 2 services** (`planilla_calculo_service.py`, `descuento_masivo_service.py`) desde `app_rrhh/` hacia una nueva Django app en `apps/api/apps/payroll/`. Class names quedan en español — el rename a inglés (`Remuneracion → Compensation`, `ConfiguracionUit → TaxParameter`) es L3.10.

**Architecture:** L3.7 es **el sub-PR con más modelos hasta ahora** (10 modelos en 2 archivos: 9 en `remuneracion.py` + 1 en `configuracion_uit.py`). Los modelos forman un grafo cohesivo (PlanillaMensual ← DetallePlanilla ← ConceptoPlanilla, BoletaPago, CalendarioPago) con FKs internas que se mantienen como referencias directas a clases (no string lazy) por estar same-module. Cross-app FKs salientes ya son strings lazy correctas (`'identity.Usuario'`, `'employees.Empleado'`, `'contracts.DatosLaborales'`). 2 services (`PlanillaCalculoService`, `DescuentoMasivoService`) tienen imports `from app_rrhh.models` que deben re-apuntar a `apps.payroll.models` (mismo patrón que L3.6 con PDF services). Sin AUTH_USER_MODEL changes ni splits de modelos.

**Tech Stack:** Django 5.2 `AppConfig`, NUCLEAR DB strategy (validada en L3.2-L3.6), Django management commands para reseed.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L3 — División de apps Django" sub-PR L3.7; § 3.2 "División de modelos"; § 3.3 "Mapeo de services" (`planilla_calculo_service.py`, `descuento_masivo_service.py` → `payroll`)

**Scope decision (alineada con L3.1-L3.6 pattern):**
- Class names en español; rename a inglés en L3.10 (`Remuneracion → Compensation`, `ConfiguracionUit → TaxParameter`)
- Spec § 3.2 menciona crear `MonthlyPayroll` nuevo si hace falta — **N/A**: ya existe `PlanillaMensual` que cumple la función. Sin nuevos modelos.
- NO incluye motor multi-régimen (Vyntia Pay sub-proyecto D) — solo movimiento mecánico

**Pre-condiciones:**
- L3.6 mergeada a master (commit `91581e7b`)
- Django 5.2.13, `apps/api/apps/{core,identity,organization,employees,contracts,documents}/` operativos
- pytest baseline: 125 passed, 44 failed, 3 skipped
- `bd_vyntia` provisionada con esquema actual; rol > 0, permiso > 0, modulos > 0
- venv en `D:/VYNTIA/.venv/`

**Definition of Done:**
- [ ] `apps/api/apps/payroll/` existe con `apps.py`, `models/`, `services/`, `migrations/`
- [ ] Modelos `PlanillaMensual`, `DetallePlanilla`, `ConceptoPlanilla`, `ConfiguracionAfp`, `ConfiguracionRemuneracion`, `DescuentoMasivo`, `BoletaPago`, `CalendarioPago` movidos a `apps/payroll/models/remuneracion.py`
- [ ] Modelo `ConfiguracionUit` movido a `apps/payroll/models/configuracion_uit.py`
- [ ] Services `planilla_calculo_service.py`, `descuento_masivo_service.py` movidos a `apps/payroll/services/`
- [ ] `app_rrhh/models/{remuneracion,configuracion_uit}.py` eliminados
- [ ] `app_rrhh/services/{planilla_calculo_service,descuento_masivo_service}.py` eliminados
- [ ] `PayrollConfig` en `LOCAL_APPS`
- [ ] **LR9 fix:** 0 stale `'app_rrhh.X'` strings (verificado pre-move — N/A para L3.7, se mantiene defensive grep)
- [ ] FK strings `'identity.Usuario'`, `'employees.Empleado'`, `'contracts.DatosLaborales'` dentro de modelos movidos preservados (ya correctos pre-move)
- [ ] Same-module FKs en remuneracion.py preservadas como referencias directas a clase (PlanillaMensual, DetallePlanilla, ConfiguracionRemuneracion, etc.)
- [ ] **LR11 defensive check:** verificar relative imports en `app_rrhh/{views,serializers,services.py,tests.py,managers.py}` (pre-move grep esperado: 0 hits)
- [ ] **LR13 defensive check:** verificar logger-name strings `logger='app_rrhh.services.{planilla_calculo_service|descuento_masivo_service}'` o `getLogger('app_rrhh.services.X')` (pre-move grep esperado: 0 hits)
- [ ] `app_rrhh/services/__init__.py` ya no exporta `DescuentoMasivoService` ni `PlanillaCalculoService`; nuevo re-export en `apps/payroll/services/__init__.py`
- [ ] Imports actualizados across ~6 archivos (services internos + remuneraciones_views + remuneraciones_serializers + views.py + serializers.py + 1 management command)
- [ ] Migraciones regeneradas: app_rrhh sin payroll models; payroll con 9 modelos
- [ ] `bd_vyntia` recreada y reseeded (rol > 0, permiso > 0, modulos > 0)
- [ ] `pyproject.toml` `packages` incluye `"apps.payroll"`
- [ ] **LR12 sequence:** drop → CREATE bd_vyntia → makemigrations → migrate (DB created BEFORE makemigrations)
- [ ] `python manage.py check` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.7-payroll-app` mergeada a master con `--no-ff`

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/apps/payroll/__init__.py` | empty |
| Create | `apps/api/apps/payroll/apps.py` | `PayrollConfig(AppConfig)` con `name="apps.payroll"`, `label="payroll"` |
| Create | `apps/api/apps/payroll/models/__init__.py` | re-exporta los 9 modelos |
| Create | `apps/api/apps/payroll/services/__init__.py` | re-exporta los 2 services |
| Move | `app_rrhh/models/remuneracion.py` → `apps/api/apps/payroll/models/remuneracion.py` | 8 modelos. FKs salientes ya correctas (`'identity.Usuario'`, `'employees.Empleado'`, `'contracts.DatosLaborales'`); same-module FKs son refs directas a clase |
| Move | `app_rrhh/models/configuracion_uit.py` → `apps/api/apps/payroll/models/configuracion_uit.py` | 1 modelo. FK saliente ya correcta (`'identity.Usuario'`) |
| Move | `app_rrhh/services/planilla_calculo_service.py` → `apps/api/apps/payroll/services/planilla_calculo_service.py` | Internal `from app_rrhh.models import (...)` → `from apps.payroll.models import (...)` |
| Move | `app_rrhh/services/descuento_masivo_service.py` → `apps/api/apps/payroll/services/descuento_masivo_service.py` | Internal `from app_rrhh.models import (...)` → `from apps.payroll.models import (...)` |
| Create | `apps/api/apps/payroll/migrations/__init__.py` | empty |
| Modify | `apps/api/app_rrhh/models/__init__.py` | quitar `from .configuracion_uit import ConfiguracionUit` y bloque `from .remuneracion import (BoletaPago, CalendarioPago, ConceptoPlanilla, ConfiguracionAfp, ConfiguracionRemuneracion, DescuentoMasivo, DetallePlanilla, PlanillaMensual,)`. Quitar 9 entries en `__all__` (`"ConfiguracionAfp"`, `"ConfiguracionRemuneracion"`, `"ConfiguracionUit"`, `"PlanillaMensual"`, `"DetallePlanilla"`, `"ConceptoPlanilla"`, `"DescuentoMasivo"`, `"BoletaPago"`, `"CalendarioPago"`) |
| Modify | `apps/api/app_rrhh/services/__init__.py` | quitar `from .descuento_masivo_service import DescuentoMasivoService` y `from .planilla_calculo_service import PlanillaCalculoService` líneas + 2 entries en `__all__` |
| Modify | `apps/api/vyntia/settings/base.py` | añadir `"apps.payroll.apps.PayrollConfig"` a `LOCAL_APPS` (después de documents, antes de app_rrhh) |
| Modify | `apps/api/pyproject.toml` | añadir `"apps.payroll"` a `packages` |
| Modify (~6 files) | `api/v1/rrhh/{views,serializers,remuneraciones_views,remuneraciones_serializers}.py`, `app_rrhh/management/commands/seed_remuneraciones_config.py` | replace `from app_rrhh.models import ... {payroll-models}` → `from apps.payroll.models import ...`; replace `from app_rrhh.services import ... {DescuentoMasivoService\|PlanillaCalculoService}` → `from apps.payroll.services import ...` |
| Delete | `app_rrhh/migrations/0001_initial.py` + `0002_initial.py` | regenerated |
| Delete | `apps/identity/migrations/0001_initial.py` | regenerated |
| Delete | `apps/organization/migrations/0001_initial.py` | regenerated |
| Delete | `apps/employees/migrations/0001_initial.py` (+ `0002_initial.py` si existe) | regenerated |
| Delete | `apps/contracts/migrations/0001_initial.py` + `0002_initial.py` | regenerated |
| Delete | `apps/documents/migrations/0001_initial.py` + `0002_initial.py` | regenerated |

**NO se toca en L3.7:**
- Class names (rename a inglés es L3.10)
- Field names
- Frontend
- Vacaciones (queda en app_rrhh hasta L3.8)
- Onboarding (queda en app_rrhh hasta L3.9)
- Motor multi-régimen / cálculo SUNAT real (Vyntia Pay sub-proyecto D)
- `seed_remuneraciones_config.py` se queda en `app_rrhh/management/commands/` — solo actualiza su import (los management commands se reorganizan en una fase posterior; no es scope L3)

**Lecciones aplicadas (LR9-LR13) explícitamente:**
- **LR9** (stale `'app_rrhh.X'` strings): pre-move grep confirma **0 hits** — N/A para L3.7. Defensive check se mantiene.
- **LR10** (sed con single + double quote): aplica defensive en Task 6 sed; pre-move bare-string grep retorna 0 hits fuera de migrations/__init__.
- **LR11** (relative imports `from .models import` en archivos legacy): pre-move grep en `app_rrhh/{views,serializers,services.py,tests.py,managers.py}` esperado **0 hits** — N/A para L3.7. Defensive check.
- **LR12** (sequence drop → CREATE → makemigrations → migrate): aplicada en Task 13.
- **LR13 NUEVA** (stale logger-name strings `logger='app_rrhh.services.X'` o `getLogger('app_rrhh.services.X')`): pre-move grep esperado **0 hits** — defensive check en Task 9 Step 11.

**Inventario de inbound FK strings (verificado pre-move):**
- 0 inbound `'PlanillaMensual'`, `'DetallePlanilla'`, etc. references desde modelos en otros apps (verificado por grep)
- 0 stale `'app_rrhh.{PlanillaMensual|...}'` strings (verificado por grep)
- Same-module FKs preservadas como referencias directas a clase (no string lazy):
  - `DetallePlanilla.planilla = models.ForeignKey(PlanillaMensual, ...)`
  - `ConceptoPlanilla.detalle_planilla = models.ForeignKey(DetallePlanilla, ...)`
  - `ConceptoPlanilla.configuracion_concepto = models.ForeignKey(ConfiguracionRemuneracion, ...)`
  - `DescuentoMasivo.configuracion_concepto = models.ForeignKey(ConfiguracionRemuneracion, ...)`
  - `BoletaPago.detalle_planilla = models.OneToOneField(DetallePlanilla, ...)`
  - `CalendarioPago.planilla = models.ForeignKey(PlanillaMensual, ...)`

**Inventario de imports a actualizar (verificado pre-move, ~6 archivos):**

| Archivo | Línea(s) | Pattern actual | Notas |
|---|---|---|---|
| `app_rrhh/services/planilla_calculo_service.py` | 9-14 | multi-line: `from app_rrhh.models import (\n    ConfiguracionAfp,\n    ConfiguracionUit,\n    DetallePlanilla,\n    PlanillaMensual,\n)` | **archivo se mueve** a apps.payroll/services/; cambiar a `from apps.payroll.models import (...)` (o relative `from ..models import (...)`) |
| `app_rrhh/services/descuento_masivo_service.py` | 18-23 | multi-line: `from app_rrhh.models import (\n    ConceptoPlanilla,\n    ConfiguracionRemuneracion,\n    DescuentoMasivo,\n    DetallePlanilla,\n)` | **archivo se mueve**; mismo trato |
| `app_rrhh/management/commands/seed_remuneraciones_config.py` | 10 | single-line: `from app_rrhh.models import ConfiguracionAfp, ConfiguracionUit` | replace módulo (mixed-line con 2 nombres → single-line replace) |
| `api/v1/rrhh/views.py` | 9-12 | multi-line block (mixto): `ConfiguracionAfp,\nConfiguracionRemuneracion,` (junto con DatosLaborales que ya está extraído — verificar) | split |
| `api/v1/rrhh/serializers.py` | 6-8 | multi-line block (mixto): `ConfiguracionAfp,\nConfiguracionRemuneracion,` | split |
| `api/v1/rrhh/remuneraciones_views.py` | 12-21 | multi-line block (todos 8 payroll models) + línea 23 service: `from app_rrhh.services import DescuentoMasivoService, PlanillaCalculoService` | full block replace + service Pattern B |
| `api/v1/rrhh/remuneraciones_serializers.py` | 11-21 | multi-line block (todos 9 payroll models incl. ConceptoPlanilla + ConfiguracionUit) | full block replace |

Adicionales a verificar por grep durante ejecución (Task 9 Step 1 inventario):
- `app_rrhh/models.py` (flat shadow file — likely dead, but verify)
- `app_rrhh/{views,serializers,serializers_optimized,services.py,tests.py,managers.py,managers/}.py`
- `app_rrhh/management/commands/seed_menu.py` (puede tener seeded modules)

---

## Task 1: Pre-flight — branch, baseline, backup

- [ ] **Step 1: Confirmar pwd y master limpio post-L3.6**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -3
```

Expected: HEAD = `328625d0 docs(L3.6): mark L3.6 merged, L3.7 as next; document LR13 stale logger-name lesson` o más reciente.

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
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.7.dump 2>&1 | tail -3
ls -lh /tmp/bd_vyntia_pre_L3.7.dump
```

Expected: dump ~250-500 KB.

- [ ] **Step 5: Crear branch L3.7**

```bash
git checkout -b vyntia/L3.7-payroll-app
git status --short
```

---

## Task 2: Comitear el plan en la branch

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.7-payroll.md
git commit -m "docs(L3.7): add payroll app extraction plan"
```

---

## Task 3: Crear estructura `apps/payroll/`

- [ ] **Step 1: Crear directorios + empty `__init__.py`**

```bash
cd D:/VYNTIA
mkdir -p apps/api/apps/payroll/models
mkdir -p apps/api/apps/payroll/services
mkdir -p apps/api/apps/payroll/migrations
touch apps/api/apps/payroll/__init__.py
touch apps/api/apps/payroll/migrations/__init__.py
```

- [ ] **Step 2: Crear `apps/payroll/apps.py`**

Use Write tool con contenido EXACTO:

```python
"""AppConfig for the `apps.payroll` Django app — VYNTIA payroll & compensation.

Owns the payroll-processing entities of the HR system:
- ConfiguracionAfp (AFP rates per period for pension contribution calculation)
- ConfiguracionRemuneracion (catalog of payroll concepts: incomes + deductions)
- ConfiguracionUit (annual UIT value for SUNAT/legal calculations — renta 4ta tope, ESSALUD CAS)
- PlanillaMensual (monthly payroll header per period and modality)
- DetallePlanilla (per-employee payroll detail with AFP/ONP/EsSalud/renta calculations)
- ConceptoPlanilla (variable income/deduction concepts applied per detail)
- DescuentoMasivo (bulk Excel-loaded deduction batches)
- BoletaPago (generated payroll receipts as PDF)
- CalendarioPago (scheduled payment calendars)

Owned services (payroll calculation engines):
- planilla_calculo_service.py — full monthly payroll calculation per Peruvian regimens
- descuento_masivo_service.py — bulk Excel deduction processor

Bounded context boundary: payroll owns the compensation calculation, deduction
catalog, and payroll-period entities. Personal data lives in `apps.employees`,
contract/employment data in `apps.contracts`, document storage in `apps.documents`.

NOTE: This app does NOT include the multi-régimen calculation engine (CAS/728/276
detailed routing). That's the scope of sub-project D (Vyntia Pay).

Future rename (deferred to L3.10):
- ConfiguracionUit → TaxParameter
- Remuneracion-prefixed → Compensation-prefixed
- PlanillaMensual → MonthlyPayroll
"""

from django.apps import AppConfig


class PayrollConfig(AppConfig):
    name = "apps.payroll"
    label = "payroll"
    verbose_name = "VYNTIA Payroll"
```

- [ ] **Step 3: Crear placeholder `apps/payroll/models/__init__.py`**

```python
"""Payroll models — re-exports for backward-compatible imports.

Populated when models are physically moved.
"""
```

- [ ] **Step 4: Crear placeholder `apps/payroll/services/__init__.py`**

```python
"""Payroll services — re-exports for backward-compatible imports.

Populated when services are physically moved.
"""
```

---

## Task 4: Mover los 4 archivos con `git mv`

- [ ] **Step 1: Defensive — kill stale Python procs**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 2: `git mv` los 2 archivos de modelos**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/models/remuneracion.py apps/api/apps/payroll/models/remuneracion.py
git mv apps/api/app_rrhh/models/configuracion_uit.py apps/api/apps/payroll/models/configuracion_uit.py
```

- [ ] **Step 3: `git mv` los 2 services**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/services/planilla_calculo_service.py apps/api/apps/payroll/services/planilla_calculo_service.py
git mv apps/api/app_rrhh/services/descuento_masivo_service.py apps/api/apps/payroll/services/descuento_masivo_service.py
```

- [ ] **Step 4: Verificar layout**

```bash
ls apps/api/apps/payroll/models/
ls apps/api/apps/payroll/services/
ls apps/api/app_rrhh/models/remuneracion.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/models/configuracion_uit.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/services/planilla_calculo_service.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/services/descuento_masivo_service.py 2>&1 || echo "OK: removed"
```

Expected: 2 model files + `__init__.py` en payroll/models/. 2 service files + `__init__.py` en payroll/services/. 4 originales removidos.

---

## Task 5: Verify FK strings DENTRO de los archivos movidos (no editar)

Los 2 archivos movidos ya usan strings lazy correctos para FKs cross-app y referencias directas a clase para FKs same-module. Verificar:

- [ ] **Step 1: Verificar FKs salientes en `apps/payroll/models/remuneracion.py`**

```bash
cd D:/VYNTIA/apps/api
echo "=== Cross-app lazy FK strings (deben tener prefix) ==="
grep -n "ForeignKey\|OneToOneField" apps/payroll/models/remuneracion.py | head -30
echo ""
echo "=== Bare 'Empleado'/'Usuario'/'Area'/'DatosLaborales'/'DatosFamiliares' en payroll/models/ — should be 0 ==="
grep -rn "'Empleado'\b\|\"Empleado\"\|'Usuario'\b\|\"Usuario\"\|'Area'\b\|\"Area\"\|'DatosLaborales'\b\|\"DatosLaborales\"\|'DatosFamiliares'\b\|\"DatosFamiliares\"" apps/payroll/models/ --include="*.py" || echo "OK: cero"
cd ../..
```

Expected:
- Cross-app FKs usan prefixed lazy strings: `'identity.Usuario'`, `'employees.Empleado'`, `'contracts.DatosLaborales'`
- Same-module FKs son referencias directas a clase: `PlanillaMensual`, `DetallePlanilla`, `ConfiguracionRemuneracion` (sin quotes — Python class refs)
- "OK: cero" para bare cross-app strings

Si algún grep encuentra `'Empleado'`, `'Usuario'`, etc. sin prefix, **detener y corregir** antes de continuar.

- [ ] **Step 2: Verificar FK saliente en `apps/payroll/models/configuracion_uit.py`**

```bash
grep -n "ForeignKey" apps/api/apps/payroll/models/configuracion_uit.py
```

Expected: 1 FK con `'identity.Usuario'` (lazy string).

---

## Task 6: Update FK strings entrantes (LR9 defensive check — N/A para L3.7)

**Pre-move grep verificado: 0 stale `'app_rrhh.X'` refs.** Esta task se mantiene como verificación defensiva — si aparecen hits inesperados, hay regresión a corregir.

- [ ] **Step 1: Bulk sed defensivo (single + double quote — LR10)**

```bash
cd D:/VYNTIA/apps/api
find apps -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -not -path "*/payroll/*" -print0 | xargs -0 sed -i \
  -e "s|'app_rrhh\.PlanillaMensual'|'payroll.PlanillaMensual'|g" \
  -e 's|"app_rrhh\.PlanillaMensual"|"payroll.PlanillaMensual"|g' \
  -e "s|'app_rrhh\.DetallePlanilla'|'payroll.DetallePlanilla'|g" \
  -e 's|"app_rrhh\.DetallePlanilla"|"payroll.DetallePlanilla"|g' \
  -e "s|'app_rrhh\.ConceptoPlanilla'|'payroll.ConceptoPlanilla'|g" \
  -e 's|"app_rrhh\.ConceptoPlanilla"|"payroll.ConceptoPlanilla"|g' \
  -e "s|'app_rrhh\.ConfiguracionAfp'|'payroll.ConfiguracionAfp'|g" \
  -e 's|"app_rrhh\.ConfiguracionAfp"|"payroll.ConfiguracionAfp"|g' \
  -e "s|'app_rrhh\.ConfiguracionRemuneracion'|'payroll.ConfiguracionRemuneracion'|g" \
  -e 's|"app_rrhh\.ConfiguracionRemuneracion"|"payroll.ConfiguracionRemuneracion"|g' \
  -e "s|'app_rrhh\.ConfiguracionUit'|'payroll.ConfiguracionUit'|g" \
  -e 's|"app_rrhh\.ConfiguracionUit"|"payroll.ConfiguracionUit"|g' \
  -e "s|'app_rrhh\.DescuentoMasivo'|'payroll.DescuentoMasivo'|g" \
  -e 's|"app_rrhh\.DescuentoMasivo"|"payroll.DescuentoMasivo"|g' \
  -e "s|'app_rrhh\.BoletaPago'|'payroll.BoletaPago'|g" \
  -e 's|"app_rrhh\.BoletaPago"|"payroll.BoletaPago"|g' \
  -e "s|'app_rrhh\.CalendarioPago'|'payroll.CalendarioPago'|g" \
  -e 's|"app_rrhh\.CalendarioPago"|"payroll.CalendarioPago"|g'
cd ../..
```

- [ ] **Step 2: Verify (defensive — esperado: 0 hits new prefixed, 0 stale)**

```bash
cd D:/VYNTIA/apps/api
echo "=== payroll.X refs (expected: 0 — N/A para L3.7) ==="
grep -rn "'payroll\.\(PlanillaMensual\|DetallePlanilla\|ConceptoPlanilla\|ConfiguracionAfp\|ConfiguracionRemuneracion\|ConfiguracionUit\|DescuentoMasivo\|BoletaPago\|CalendarioPago\)'\|\"payroll\.\(PlanillaMensual\|DetallePlanilla\|ConceptoPlanilla\|ConfiguracionAfp\|ConfiguracionRemuneracion\|ConfiguracionUit\|DescuentoMasivo\|BoletaPago\|CalendarioPago\)\"" apps --include="*.py" || echo "OK: cero (N/A)"
echo ""
echo "=== Stale 'app_rrhh.X' anywhere — should be 0 ==="
grep -rn "'app_rrhh\.\(PlanillaMensual\|DetallePlanilla\|ConceptoPlanilla\|ConfiguracionAfp\|ConfiguracionRemuneracion\|ConfiguracionUit\|DescuentoMasivo\|BoletaPago\|CalendarioPago\)'\|\"app_rrhh\.\(PlanillaMensual\|DetallePlanilla\|ConceptoPlanilla\|ConfiguracionAfp\|ConfiguracionRemuneracion\|ConfiguracionUit\|DescuentoMasivo\|BoletaPago\|CalendarioPago\)\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=migrations || echo "OK: cero"
cd ../..
```

Expected: ambos OK (0 hits cada uno, since LR9 was N/A).

- [ ] **Step 3: Bare-string sanity check (defensive)**

```bash
cd D:/VYNTIA/apps/api
grep -rn "'PlanillaMensual'\b\|\"PlanillaMensual\"\|'DetallePlanilla'\b\|\"DetallePlanilla\"\|'ConceptoPlanilla'\b\|\"ConceptoPlanilla\"\|'ConfiguracionAfp'\b\|\"ConfiguracionAfp\"\|'ConfiguracionRemuneracion'\b\|\"ConfiguracionRemuneracion\"\|'ConfiguracionUit'\b\|\"ConfiguracionUit\"\|'DescuentoMasivo'\b\|\"DescuentoMasivo\"\|'BoletaPago'\b\|\"BoletaPago\"\|'CalendarioPago'\b\|\"CalendarioPago\"" apps app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK: cero"
cd ../..
```

Expected: `OK: cero`. Inbound FK strings desde modelos que se quedan en `app_rrhh` deberían ser 0 — pre-move verified.

---

## Task 7: Crear `apps/payroll/models/__init__.py` con re-exports

Use Write tool en `apps/api/apps/payroll/models/__init__.py`:

```python
"""Payroll models — re-exports for backward-compatible imports."""

from .configuracion_uit import ConfiguracionUit
from .remuneracion import (
    BoletaPago,
    CalendarioPago,
    ConceptoPlanilla,
    ConfiguracionAfp,
    ConfiguracionRemuneracion,
    DescuentoMasivo,
    DetallePlanilla,
    PlanillaMensual,
)

__all__ = [
    "BoletaPago",
    "CalendarioPago",
    "ConceptoPlanilla",
    "ConfiguracionAfp",
    "ConfiguracionRemuneracion",
    "ConfiguracionUit",
    "DescuentoMasivo",
    "DetallePlanilla",
    "PlanillaMensual",
]
```

- [ ] **Smoke parse check (app no registrada todavía hasta Phase 3)**

```bash
cd D:/VYNTIA/apps/api
python -c "import ast; ast.parse(open('apps/payroll/models/__init__.py').read()); print('OK parse __init__')"
python -c "import ast; ast.parse(open('apps/payroll/models/remuneracion.py').read()); print('OK parse remuneracion')"
python -c "import ast; ast.parse(open('apps/payroll/models/configuracion_uit.py').read()); print('OK parse configuracion_uit')"
cd ../..
```

Expected: 3x `OK parse`.

---

## Task 8: Update services internos + `apps/payroll/services/__init__.py`

Los 2 services se movieron en Task 4 pero sus imports referencian `app_rrhh.models`. Necesitan actualizarse para apuntar a `apps.payroll.models`.

- [ ] **Step 1: Update `apps/payroll/services/planilla_calculo_service.py:9-14`**

Use Edit tool:
- old_string:
```python
from app_rrhh.models import (
    ConfiguracionAfp,
    ConfiguracionUit,
    DetallePlanilla,
    PlanillaMensual,
)
```
- new_string:
```python
from apps.payroll.models import (
    ConfiguracionAfp,
    ConfiguracionUit,
    DetallePlanilla,
    PlanillaMensual,
)
```

- [ ] **Step 2: Update `apps/payroll/services/descuento_masivo_service.py:18-23`**

Use Edit tool:
- old_string:
```python
from app_rrhh.models import (
    ConceptoPlanilla,
    ConfiguracionRemuneracion,
    DescuentoMasivo,
    DetallePlanilla,
)
```
- new_string:
```python
from apps.payroll.models import (
    ConceptoPlanilla,
    ConfiguracionRemuneracion,
    DescuentoMasivo,
    DetallePlanilla,
)
```

- [ ] **Step 3: Verify both services (no app_rrhh.models leftover)**

```bash
grep -n "from app_rrhh\.models\|from apps.payroll.models" apps/api/apps/payroll/services/planilla_calculo_service.py
grep -n "from app_rrhh\.models\|from apps.payroll.models" apps/api/apps/payroll/services/descuento_masivo_service.py
```

Expected: each shows `from apps.payroll.models import (...)`. 0 hits de app_rrhh.models.

- [ ] **Step 4: Crear `apps/payroll/services/__init__.py` con re-exports**

Use Write tool:

```python
"""Payroll services — re-exports for backward-compatible imports.

Calculation engines for the Peruvian payroll workflow.
"""

from .descuento_masivo_service import DescuentoMasivoService
from .planilla_calculo_service import PlanillaCalculoService

__all__ = [
    "DescuentoMasivoService",
    "PlanillaCalculoService",
]
```

- [ ] **Step 5: Smoke parse check**

```bash
cd D:/VYNTIA/apps/api
python -c "import ast; ast.parse(open('apps/payroll/services/__init__.py').read()); print('OK parse __init__')"
python -c "import ast; ast.parse(open('apps/payroll/services/planilla_calculo_service.py').read()); print('OK parse planilla_calculo_service')"
python -c "import ast; ast.parse(open('apps/payroll/services/descuento_masivo_service.py').read()); print('OK parse descuento_masivo_service')"
cd ../..
```

Expected: 3x `OK parse`.

---

## Task 9: Bulk update absolute imports across the codebase

**Pattern A:** `from app_rrhh.models import {payroll-models}` → `from apps.payroll.models import ...`
**Pattern B:** `from app_rrhh.services import {DescuentoMasivoService|PlanillaCalculoService}` → `from apps.payroll.services import ...`

- [ ] **Step 1: Inventario completo (incluye LR11 + LR13 defensive)**

```bash
cd D:/VYNTIA/apps/api
echo "=== ABSOLUTE imports model (~5 expected) ==="
grep -rn "from app_rrhh\.models" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago" | sort
echo ""
echo "=== ABSOLUTE imports services (~1 expected — remuneraciones_views.py:23) ==="
grep -rn "from app_rrhh\.services" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "DescuentoMasivoService|PlanillaCalculoService|descuento_masivo_service|planilla_calculo_service" | sort
echo ""
echo "=== LR11 — RELATIVE imports en app_rrhh/*.py (expected: 0) ==="
grep -rn "from \.models import\|from \.services import" app_rrhh --include="*.py" \
  | grep -E "PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago|DescuentoMasivoService|PlanillaCalculoService" | sort || echo "OK: cero (LR11 N/A)"
echo ""
echo "=== LR13 — Stale logger-name strings (expected: 0) ==="
grep -rn "logger=['\"]app_rrhh\.services\.\(planilla_calculo_service\|descuento_masivo_service\)\|getLogger(['\"]app_rrhh\.services\.\(planilla_calculo_service\|descuento_masivo_service\)" --include="*.py" || echo "OK: cero (LR13 N/A)"
cd ../..
```

Expected: ~5 model imports, 1 service import, LR11 OK, LR13 OK.

- [ ] **Step 2: Sed para imports puros models (single-import lines)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/payroll/*" \
  -print0 | xargs -0 sed -i \
  -e 's|^from app_rrhh\.models import \(PlanillaMensual\)$|from apps.payroll.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(DetallePlanilla\)$|from apps.payroll.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(ConceptoPlanilla\)$|from apps.payroll.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(ConfiguracionAfp\)$|from apps.payroll.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(ConfiguracionRemuneracion\)$|from apps.payroll.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(ConfiguracionUit\)$|from apps.payroll.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(DescuentoMasivo\)$|from apps.payroll.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(BoletaPago\)$|from apps.payroll.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(CalendarioPago\)$|from apps.payroll.models import \1|g'
cd ../..
```

- [ ] **Step 3: Sed para inline imports en funciones (whitespace-prefix, `-E` con `#` per L3.5/L3.6 lesson)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/payroll/*" \
  -print0 | xargs -0 sed -i -E \
  -e 's#^([[:space:]]+)from app_rrhh\.models import (PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago)$#\1from apps.payroll.models import \2#g'
cd ../..
```

- [ ] **Step 4: Sed para submodule path imports**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/payroll/*" \
  -print0 | xargs -0 sed -i \
  -e 's|from app_rrhh\.models\.remuneracion import |from apps.payroll.models import |g' \
  -e 's|from app_rrhh\.models\.configuracion_uit import |from apps.payroll.models import |g'
cd ../..
```

Verify:
```bash
grep -rn "from app_rrhh\.models\.\(remuneracion\|configuracion_uit\)" apps/api --include="*.py" || echo "OK: cero"
```

- [ ] **Step 5: Sed para imports puros services (Pattern B)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/payroll/*" \
  -print0 | xargs -0 sed -i \
  -e 's|^from app_rrhh\.services import \(DescuentoMasivoService\)$|from apps.payroll.services import \1|g' \
  -e 's|^from app_rrhh\.services import \(PlanillaCalculoService\)$|from apps.payroll.services import \1|g' \
  -e 's|^from app_rrhh\.services\.descuento_masivo_service import \(DescuentoMasivoService\)$|from apps.payroll.services import \1|g' \
  -e 's|^from app_rrhh\.services\.planilla_calculo_service import \(PlanillaCalculoService\)$|from apps.payroll.services import \1|g'
cd ../..
```

- [ ] **Step 6: Manual fix para imports mezclados (single-line con coma)**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models import.*\(PlanillaMensual\|DetallePlanilla\|ConceptoPlanilla\|ConfiguracionAfp\|ConfiguracionRemuneracion\|ConfiguracionUit\|DescuentoMasivo\|BoletaPago\|CalendarioPago\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | head -30
echo ""
echo "=== Service mixed-line ==="
grep -rn "from app_rrhh\.services import.*\(DescuentoMasivoService\|PlanillaCalculoService\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | head -10
cd ../..
```

Casos esperados:
- `app_rrhh/management/commands/seed_remuneraciones_config.py:10` — `from app_rrhh.models import ConfiguracionAfp, ConfiguracionUit` (single-line con 2 nombres del MISMO destino) → `from apps.payroll.models import ConfiguracionAfp, ConfiguracionUit`. Se puede arreglar con un Edit directo.
- `api/v1/rrhh/remuneraciones_views.py:23` — `from app_rrhh.services import DescuentoMasivoService, PlanillaCalculoService` (single-line con 2 services del MISMO destino) → `from apps.payroll.services import DescuentoMasivoService, PlanillaCalculoService`. Edit directo.

Para cada uno:
- Read context
- Edit con replacement directo

- [ ] **Step 7: Manual fix para imports multi-línea con parens**

```bash
cd D:/VYNTIA/apps/api
grep -rn -B 0 -A 15 "from app_rrhh\.models import (" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations 2>&1 | head -120
cd ../..
```

Casos esperados:
- `api/v1/rrhh/views.py:9-12` — bloque mixto: contiene `ConfiguracionAfp,\nConfiguracionRemuneracion,` junto con otros — split: extraer payroll models, mantener resto en app_rrhh
- `api/v1/rrhh/serializers.py:6-8` — bloque mixto similar — split
- `api/v1/rrhh/remuneraciones_views.py:12-21` — bloque ENTERO con 8 payroll models → replace ENTIRE block to `from apps.payroll.models import (BoletaPago, CalendarioPago, ConfiguracionAfp, ConfiguracionRemuneracion, ConfiguracionUit, DescuentoMasivo, DetallePlanilla, PlanillaMensual,)` (alfabético)
- `api/v1/rrhh/remuneraciones_serializers.py:11-21` — bloque ENTERO con 9 payroll models incl. ConceptoPlanilla → replace ENTIRE block

Para cada uno: Read + Edit.

- [ ] **Step 8: Self-absolute import check en moved files**

```bash
cd D:/VYNTIA/apps/api
echo "=== Models self-absolute (should be cero) ==="
grep -rn "from apps\.payroll\.models import" apps/payroll/models --include="*.py" || echo "OK: cero"
echo ""
echo "=== Services to apps.payroll.models (preferred over app_rrhh.models) ==="
grep -rn "from apps\.payroll\.models\|from app_rrhh\.models" apps/payroll/services --include="*.py"
cd ../..
```

Expected: 0 self-absolute en models. Services importan de `apps.payroll.models`. 0 imports de `app_rrhh.models`.

- [ ] **Step 9: Update `app_rrhh/services/__init__.py` — quitar exports payroll services**

Read current state primero:
```bash
cat apps/api/app_rrhh/services/__init__.py
```

Use Edit tool en `apps/api/app_rrhh/services/__init__.py`:
- old_string:
```python
# Servicios de vacaciones
# Servicios de remuneraciones
from .descuento_masivo_service import DescuentoMasivoService
from .planilla_calculo_service import PlanillaCalculoService

from .vacation_admin_service import VacationAdminService
```
- new_string:
```python
# Servicios de vacaciones
from .vacation_admin_service import VacationAdminService
```

(Quita las 4 líneas: comentario `# Servicios de remuneraciones`, 2 imports, blank line. Mantiene `# Servicios de vacaciones` y el resto.)

Use Edit tool segundo para el `__all__`:
- old_string:
```python
    "VacationReportService",
    "DescuentoMasivoService",
    "PlanillaCalculoService",
]
```
- new_string:
```python
    "VacationReportService",
]
```

Verify:
```bash
grep -n "DescuentoMasivoService\|PlanillaCalculoService\|descuento_masivo_service\|planilla_calculo_service" apps/api/app_rrhh/services/__init__.py || echo "OK: removed"
```

Expected: `OK: removed`.

- [ ] **Step 10: LR11 defensive check (relative imports en app_rrhh/*.py)**

**Pre-move grep verificado: 0 hits.**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep -E "PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago" || echo "OK: cero (LR11 N/A para L3.7)"
cd ../..
```

Expected: `OK: cero (LR11 N/A para L3.7)`.

Si aparecen matches inesperados, son regresiones — para cada uno:
- Read context
- Edit: remove la(s) línea(s) del bloque relative
- Add new line `from apps.payroll.models import <models>` (alfabético)

- [ ] **Step 11: LR13 defensive check (stale logger-name strings)**

**Pre-move grep verificado: 0 hits.**

```bash
cd D:/VYNTIA/apps/api
grep -rn "logger=['\"]app_rrhh\.services\.\(planilla_calculo_service\|descuento_masivo_service\)\|getLogger(['\"]app_rrhh\.services\.\(planilla_calculo_service\|descuento_masivo_service\)" --include="*.py" || echo "OK: cero (LR13 N/A para L3.7)"
cd ../..
```

Expected: `OK: cero (LR13 N/A para L3.7)`.

Si aparecen matches inesperados, son regresiones — actualizar a `apps.payroll.services.X`.

- [ ] **Step 12: Verificación final exhaustiva**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models import {payroll-models} ==="
grep -rn "from app_rrhh\.models import" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago" || echo "OK"
echo ""
echo "=== B: from app_rrhh.models.remuneracion / .configuracion_uit submodule path ==="
grep -rn "from app_rrhh\.models\.\(remuneracion\|configuracion_uit\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== C: from .models import {payroll-models} (LR11) ==="
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep -E "PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago" || echo "OK"
echo ""
echo "=== D: from app_rrhh.services import {payroll-services} (Pattern B) ==="
grep -rn "from app_rrhh\.services" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "DescuentoMasivoService|PlanillaCalculoService|descuento_masivo_service|planilla_calculo_service" || echo "OK"
echo ""
echo "=== E: bare 'X' / \"X\" FK strings en app_rrhh non-migrations (payroll models) ==="
grep -rn "'PlanillaMensual'\b\|\"PlanillaMensual\"\|'DetallePlanilla'\b\|\"DetallePlanilla\"\|'ConceptoPlanilla'\b\|\"ConceptoPlanilla\"\|'ConfiguracionAfp'\b\|\"ConfiguracionAfp\"\|'ConfiguracionRemuneracion'\b\|\"ConfiguracionRemuneracion\"\|'ConfiguracionUit'\b\|\"ConfiguracionUit\"\|'DescuentoMasivo'\b\|\"DescuentoMasivo\"\|'BoletaPago'\b\|\"BoletaPago\"\|'CalendarioPago'\b\|\"CalendarioPago\"" app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK"
echo ""
echo "=== F: stale 'app_rrhh.X' anywhere (LR9) ==="
grep -rn "'app_rrhh\.\(PlanillaMensual\|DetallePlanilla\|ConceptoPlanilla\|ConfiguracionAfp\|ConfiguracionRemuneracion\|ConfiguracionUit\|DescuentoMasivo\|BoletaPago\|CalendarioPago\)'\|\"app_rrhh\.\(PlanillaMensual\|DetallePlanilla\|ConceptoPlanilla\|ConfiguracionAfp\|ConfiguracionRemuneracion\|ConfiguracionUit\|DescuentoMasivo\|BoletaPago\|CalendarioPago\)\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== G: LR13 stale logger-name strings ==="
grep -rn "logger=['\"]app_rrhh\.services\.\(planilla_calculo_service\|descuento_masivo_service\)\|getLogger(['\"]app_rrhh\.services\.\(planilla_calculo_service\|descuento_masivo_service\)" --include="*.py" || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 10: Update `app_rrhh/models/__init__.py` — quitar exports

- [ ] **Step 1: Read current state**

```bash
sed -n '1,55p' apps/api/app_rrhh/models/__init__.py
```

Verifica las líneas relevantes:
- línea 11: `from .configuracion_uit import ConfiguracionUit`
- líneas 13-22: bloque `from .remuneracion import (...)`
- líneas 42-50 área: `__all__` con 9 entries de payroll models

- [ ] **Step 2: Use Edit tool — remove `from .configuracion_uit` import line**

Use Edit tool en `apps/api/app_rrhh/models/__init__.py`:
- old_string:
```python
from .configuracion_uit import ConfiguracionUit
from .onboarding import OnboardingEmpleado
```
- new_string:
```python
from .onboarding import OnboardingEmpleado
```

- [ ] **Step 3: Use Edit tool — remove the `from .remuneracion import (...)` block**

Use Edit tool. Read first to get exact context:
```bash
sed -n '11,25p' apps/api/app_rrhh/models/__init__.py
```

- old_string:
```python
from .onboarding import OnboardingEmpleado
from .remuneracion import (
    BoletaPago,
    CalendarioPago,
    ConceptoPlanilla,
    ConfiguracionAfp,
    ConfiguracionRemuneracion,
    DescuentoMasivo,
    DetallePlanilla,
    PlanillaMensual,
)
from .vacaciones import (
```
- new_string:
```python
from .onboarding import OnboardingEmpleado
from .vacaciones import (
```

- [ ] **Step 4: Use Edit tool — remove 9 entries from `__all__`**

Read the file to see exact `__all__` block context. Use Edit tool to remove the relevant entries. Use multiple Edits if needed for exact uniqueness.

Probable bloque:
- old_string (with surrounding context for uniqueness):
```python
    # Modelos de remuneraciones
    "ConfiguracionAfp",
    "ConfiguracionRemuneracion",
    "ConfiguracionUit",
    "PlanillaMensual",
    "DetallePlanilla",
    "ConceptoPlanilla",
    "DescuentoMasivo",
    "BoletaPago",
    "CalendarioPago",
]
```
- new_string:
```python
]
```

Read first to confirm exact format.

- [ ] **Step 5: Verificar limpieza**

```bash
grep -n "PlanillaMensual\|DetallePlanilla\|ConceptoPlanilla\|ConfiguracionAfp\|ConfiguracionRemuneracion\|ConfiguracionUit\|DescuentoMasivo\|BoletaPago\|CalendarioPago\|configuracion_uit\|remuneracion" apps/api/app_rrhh/models/__init__.py || echo "OK: removed"
```

Expected: `OK: removed`.

---

## Task 11: Update settings — registrar `PayrollConfig`

Use Edit tool en `apps/api/vyntia/settings/base.py`:
- old_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "apps.employees.apps.EmployeesConfig",
    "apps.contracts.apps.ContractsConfig",
    "apps.documents.apps.DocumentsConfig",
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
    "apps.documents.apps.DocumentsConfig",
    "apps.payroll.apps.PayrollConfig",
    "app_rrhh",
]
```

Verify:
```bash
grep -A 9 "LOCAL_APPS = \[" apps/api/vyntia/settings/base.py
```

---

## Task 12: Update `pyproject.toml`

```bash
grep "packages" apps/api/pyproject.toml
```

Expected current: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts", "apps.documents"]`

Use Edit tool en `apps/api/pyproject.toml`:
- old_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts", "apps.documents"]`
- new_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts", "apps.documents", "apps.payroll"]`

Reinstall:
```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
pip install -e ".[dev]" 2>&1 | tail -3
cd ../..
```

Expected: `Successfully installed vyntia-api-0.1.0`.

Smoke check:
```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd ../..
```

Expected: `System check identified no issues (0 silenced).`

Si falla con ImportError o RuntimeError, **investigar** — algún import o legacy file no fue actualizado.

---

## Task 13: NUCLEAR DB regenerate (LR12 sequence: drop → CREATE → makemigrations → migrate)

**LR12:** sequence is `drop → CREATE bd_vyntia → makemigrations → migrate`. **NO** `drop → makemigrations → CREATE → migrate`.

- [ ] **Step 1: Drop bd_vyntia (kill procs first)**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "DROP DATABASE IF EXISTS bd_vyntia;" 2>&1
```

- [ ] **Step 2: CREATE bd_vyntia (LR12 — antes de makemigrations)**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "CREATE DATABASE bd_vyntia WITH ENCODING 'UTF8' TEMPLATE template0;" 2>&1
```

- [ ] **Step 3: Eliminar migration files existentes**

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

cd D:/VYNTIA/apps/api/apps/contracts/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"

cd D:/VYNTIA/apps/api/apps/documents/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"

cd D:/VYNTIA
```

NOTE: NO se borra `apps/payroll/migrations/` (solo contiene `__init__.py` empty — primera migration genera en Step 4).

- [ ] **Step 4: Generar fresh migrations (DB ya existe per LR12)**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py makemigrations --settings=vyntia.settings.development 2>&1 | tail -30
cd ../..
```

Expected:
- `Migrations for 'app_rrhh':` (sin payroll models; con OnboardingEmpleado, Vacaciones)
- `Migrations for 'identity':` (con Usuario, Rol, etc.)
- `Migrations for 'organization':` (con Area, HistorialUbicaciones, ConfiguracionEmpresa)
- `Migrations for 'employees':` (con Empleado, DatosFamiliares, DatosAcademicos, CursosCertificaciones)
- `Migrations for 'contracts':` (con ContratosAdendas, DatosLaborales)
- `Migrations for 'documents':` (con DocumentosDigitales, PlantillaDocumento)
- `Migrations for 'payroll':` con 9 modelos — **NEW**
- Posibles `0002_initial.py` para FK ordering cross-app

Verify:
```bash
echo "=== payroll 0001 (expected: 9 model definitions) ==="
grep -E "name='(PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago)'" apps/api/apps/payroll/migrations/0001_initial.py | wc -l
echo "=== app_rrhh 0001 (expected: 0 payroll models) ==="
grep -E "name='(PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago)'" apps/api/app_rrhh/migrations/0001_initial.py | wc -l
```

Expected: `9` y `0`.

- [ ] **Step 5: Aplicar migraciones**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -25
cd ../..
```

Expected: secuencia `Applying X.0001_initial... OK` para todos los apps. Sin errors.

---

## Task 14: Re-seed

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py setup_roles_permisos --settings=vyntia.settings.development 2>&1 | tail -10
PGPASSWORD='Demenci4@' python manage.py seed_menu --settings=vyntia.settings.development 2>&1 | tail -10
cd ../..
```

Verificar `seed_remuneraciones_config` discoverable (do NOT execute — requires explicit args):
```bash
cd D:/VYNTIA/apps/api
python manage.py help seed_remuneraciones_config --settings=vyntia.settings.development 2>&1 | tail -3
cd ../..
```

Expected: comando reconocido (sin error). Verifica que el move no rompió la discovery del management command (que vive en `app_rrhh/management/commands/` y solo cambió su import).

Verify counts:
```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'rol' AS t, COUNT(*) FROM rol UNION ALL SELECT 'permiso', COUNT(*) FROM permiso UNION ALL SELECT 'modulos', COUNT(*) FROM modulos UNION ALL SELECT 'planilla_mensual', COUNT(*) FROM planilla_mensual UNION ALL SELECT 'detalle_planilla', COUNT(*) FROM detalle_planilla UNION ALL SELECT 'configuracion_uit', COUNT(*) FROM configuracion_uit UNION ALL SELECT 'configuracion_afp', COUNT(*) FROM configuracion_afp;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0, planilla_mensual = 0, detalle_planilla = 0, configuracion_uit = 0, configuracion_afp = 0.

---

## Task 15: Smoke tests

- [ ] **Step 1: Django check + pytest baseline**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected:
- check: `System check identified no issues (0 silenced).`
- pytest: `125 passed, 44 failed, 3 skipped` — baseline preservado

Si pytest divergir, **investigar** — algún import legacy hardcoded a `app_rrhh.X` paths.

- [ ] **Step 2: runserver smoke**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l37.log 2>&1 &
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

- [ ] **Step 3: Cleanup greps finales (todos los patterns LR9-LR13)**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models import {payroll-models} ==="
grep -rn "from app_rrhh\.models import" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago" || echo "OK"
echo ""
echo "=== B: from .remuneracion / .configuracion_uit (relative en app_rrhh) ==="
grep -rn "from \.remuneracion\|from \.configuracion_uit" app_rrhh --include="*.py" || echo "OK"
echo ""
echo "=== C: same-app 'X' bare en app_rrhh non-migrations ==="
grep -rn "'PlanillaMensual'\b\|\"PlanillaMensual\"\|'DetallePlanilla'\b\|\"DetallePlanilla\"\|'ConceptoPlanilla'\b\|\"ConceptoPlanilla\"\|'ConfiguracionAfp'\b\|\"ConfiguracionAfp\"\|'ConfiguracionRemuneracion'\b\|\"ConfiguracionRemuneracion\"\|'ConfiguracionUit'\b\|\"ConfiguracionUit\"\|'DescuentoMasivo'\b\|\"DescuentoMasivo\"\|'BoletaPago'\b\|\"BoletaPago\"\|'CalendarioPago'\b\|\"CalendarioPago\"" app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK"
echo ""
echo "=== D: app_rrhh.models.{remuneracion|configuracion_uit} submodule path ==="
grep -rn "app_rrhh\.models\.\(remuneracion\|configuracion_uit\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== E: stale 'app_rrhh.X' (LR9) ==="
grep -rn "'app_rrhh\.\(PlanillaMensual\|DetallePlanilla\|ConceptoPlanilla\|ConfiguracionAfp\|ConfiguracionRemuneracion\|ConfiguracionUit\|DescuentoMasivo\|BoletaPago\|CalendarioPago\)'\|\"app_rrhh\.\(PlanillaMensual\|DetallePlanilla\|ConceptoPlanilla\|ConfiguracionAfp\|ConfiguracionRemuneracion\|ConfiguracionUit\|DescuentoMasivo\|BoletaPago\|CalendarioPago\)\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== F: from app_rrhh.services import {payroll-services} ==="
grep -rn "from app_rrhh\.services" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "DescuentoMasivoService|PlanillaCalculoService|descuento_masivo_service|planilla_calculo_service" || echo "OK"
echo ""
echo "=== G: LR11 — from .models import {payroll-models} (relative en app_rrhh) ==="
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep -E "PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago" || echo "OK"
echo ""
echo "=== H: LR13 — stale logger-name strings ==="
grep -rn "logger=['\"]app_rrhh\.services\.\(planilla_calculo_service\|descuento_masivo_service\)\|getLogger(['\"]app_rrhh\.services\.\(planilla_calculo_service\|descuento_masivo_service\)" --include="*.py" || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 16: Atomic commit

```bash
cd D:/VYNTIA
git status --short | head -50
git add apps/api/
git commit -m "chore(L3.7): extract payroll app (9 models + 2 services: planilla_calculo, descuento_masivo) — fresh migrations after BD nuke + reseed"
```

Verificar:
```bash
git log --oneline vyntia/L3.7-payroll-app ^master | head -5
git status --short
```

Expected: 2 commits (`docs(L3.7)` + `chore(L3.7)`), `git status` empty.

---

## Task 17: Merge a master

- [ ] **Step 1: Confirmar autorización del usuario.**

**NO mergear sin autorización.**

- [ ] **Step 2: Merge `--no-ff`**

```bash
git checkout master
git merge --no-ff vyntia/L3.7-payroll-app -m "Merge L3.7: extract payroll app (9 models + 2 calculation services)"
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

Update `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md` Status column: L3.7 → ✅ con merge SHA. L3.8 → ⏳ NEXT.

Commit:
```bash
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.7): mark L3.7 merged, L3.8 as next in roadmap"
```

---

## Definition of Done — checklist final

- [ ] `apps/api/apps/payroll/{__init__.py, apps.py, models/{__init__.py, remuneracion.py, configuracion_uit.py}, services/{__init__.py, planilla_calculo_service.py, descuento_masivo_service.py}, migrations/{__init__.py, 0001_initial.py}}`
- [ ] `app_rrhh/models/{remuneracion, configuracion_uit}.py` removidos
- [ ] `app_rrhh/services/{planilla_calculo_service, descuento_masivo_service}.py` removidos
- [ ] `app_rrhh/services/__init__.py` ya no exporta `DescuentoMasivoService` ni `PlanillaCalculoService`
- [ ] `apps/payroll/services/__init__.py` exporta `DescuentoMasivoService` y `PlanillaCalculoService`
- [ ] LOCAL_APPS incluye `PayrollConfig`; pyproject incluye `apps.payroll`
- [ ] LR12 fix: makemigrations corrió DESPUÉS de CREATE DATABASE
- [ ] Migrations regenerated; payroll con 9 modelos; app_rrhh sin ellos
- [ ] bd_vyntia recreada; rol > 0, permiso > 0, modulos > 0, planilla_mensual = 0
- [ ] `manage.py check` clean; pytest 125/44/3; `/api/docs/` HTTP 200
- [ ] 0 stale `'app_rrhh.{payroll-models}'` strings (LR9 N/A)
- [ ] 0 bare `'X'`/`"X"` strings en `app_rrhh/` non-migrations (LR10)
- [ ] 0 relative `from .models import` en `app_rrhh/*.py` con payroll models (LR11)
- [ ] 0 `from app_rrhh.services import {payroll-services}` anywhere (Pattern B)
- [ ] 0 stale logger-name strings (LR13)
- [ ] Branch mergeada a master con `--no-ff`
- [ ] Memoria + roadmap actualizados post-merge: L3.7 ✅, L3.8 NEXT

---

## Después de L3.7

**Próximo plan:** L3.8 — extract `time_off` app (5 modelos `Vacaciones` + 5 services de vacaciones).

L3.8 será el sub-PR con más services hasta ahora (5 services: `vacation_admin_service`, `vacation_approval_service`, `vacation_calculation_service`, `vacation_report_service`, `vacation_service`). Los modelos viven en un solo archivo `app_rrhh/models/vacaciones.py` (5 modelos: ConfiguracionVacaciones, PeriodoVacacional, SolicitudVacaciones, GoceVacaciones, HistorialSolicitudVacaciones).

---

## Notas para el ejecutor

- **Patrón NUCLEAR + LR12 sequence** — drop → CREATE → makemigrations → migrate. Ordering crítico.
- **PGPASSWORD env var** explícito por known issue.
- **Class names en español** — rename inglés en L3.10.
- **Sub-PR más grande hasta ahora por # de modelos** (10 modelos en 2 archivos). Los modelos forman un grafo cohesivo same-module — FKs internas son references directas a clase, no string lazy.
- **2 services se mueven** — patrón validado en L3.6 (3 services PDF/Word).
- **`app_rrhh/services/__init__.py`** debe limpiarse (quitar 2 service re-exports).
- **`seed_remuneraciones_config.py` queda en app_rrhh** — solo actualiza su import. Management commands se reorganizan en una fase posterior; no es scope L3.
- **LR9 N/A** confirmado pre-move (0 stale `'app_rrhh.X'` refs).
- **LR11 N/A** confirmado pre-move (0 relative imports).
- **LR12** — Task 13 ordena CREATE DATABASE antes de makemigrations.
- **LR13 N/A** confirmado pre-move (0 stale logger strings) — defensive grep en Task 9 Step 11.
- **Manager `BoletaManager`** (eliminado per comment en `app_rrhh/managers.py:312`) y otros managers de remuneraciones — están orphan (comentados), cleanup en L3.11.
- **Stale Python procs:** Si `psql DROP` falla con "in use", PowerShell kill primero.
- **`api/v1/rrhh/remuneraciones_views.py` y `remuneraciones_serializers.py`** son los consumers principales — verificar que ambos se actualicen correctamente con los blocks multi-line.
