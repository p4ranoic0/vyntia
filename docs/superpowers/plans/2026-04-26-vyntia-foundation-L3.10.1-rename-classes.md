# VYNTIA Foundation L3.10.1 — Rename Model Classes ES → EN Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Renombrar las **33 clases de modelo** y archivos `apps/api/apps/*/models/*.py` de español a inglés (`Empleado → Employee`, `Usuario → User`, `Area → Department`, etc.), incluyendo todas las FK string refs cross-app, todos los imports en consumers (`apps/api/api/`, `apps/api/tests/`, services internos), `AUTH_USER_MODEL` setting, y `__init__.py` re-exports. **Field names + `db_table` permanecen en español** (eso es L3.10.2). **Splits diferidos** (`Contract+ContractAmendment`, `VacationRequest+VacationBalance`) son L3.10.3.

**Architecture:** L3.10.1 es el primer sub-PR de L3.10 (rename masivo). Solo toca **identificadores Python**: nombres de clase + nombres de archivo + FK strings + imports. Cero impacto en BD física porque todos los modelos tienen `Meta.db_table` Spanish explícito que se preserva. Se usa **NUCLEAR DB strategy** (drop bd_vyntia + delete migrations + makemigrations fresh + reseed) — proven en L3.2-L3.9. Las nuevas migraciones `0001_initial.py` se generan con clases inglesas pero `db_table='empleado'`, `db_table='usuario'`, etc. preservando exactamente el esquema físico actual.

**Tech Stack:** Django 5.2 `AppConfig`, NUCLEAR DB regenerate, GNU sed con word-boundaries `\bClass\b`, `git mv` para preservar history.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.2 "División de modelos" (mapeo de clases español → inglés); § 3.5 regla 6 "Naming en inglés"; § 4 sub-PR L3.10.

**Scope decision (L3.10 dividido en 4 sub-PRs):**
- **L3.10.1 (este plan)** — class names + file names + FK strings + imports + AUTH_USER_MODEL
- L3.10.2 — field names (`nombres → first_name`, `creado_en → created_at`, etc. con `db_column` español preservado)
- L3.10.3 — splits con data migration (`ContratosAdendas → Contract+ContractAmendment`, `SolicitudVacaciones → VacationRequest+VacationBalance`)
- L3.10.4 — frontend services + tipos TS + nuevas URL paths + remoción de redirects 301 legacy

**Pre-condiciones:**
- L3.9 mergeada a master (commit `8d9f575a`)
- Django 5.2.13, las 8 apps de dominio operativas (`apps.{core, identity, organization, employees, contracts, documents, payroll, time_off, onboarding}`)
- pytest baseline: 125 passed, 44 failed, 3 skipped
- `bd_vyntia` provisionada con esquema actual; rol > 0, permiso > 0, modulos > 0
- venv en `D:/VYNTIA/.venv/`
- `app_rrhh/models/__init__.py` con `__all__ = []` (último modelo de dominio extraído en L3.9)

---

## Tabla canónica de renombres

**ESTA ES LA FUENTE DE VERDAD.** Cualquier desviación durante ejecución debe documentarse y autorizarse antes de continuar.

### Identity (8 clases)

| File ES | Class ES | File EN | Class EN | `db_table` (preservado) |
|---|---|---|---|---|
| `usuario.py` | `Usuario` | `user.py` | `User` | `usuarios` |
| `roles.py` | `Rol` | `roles.py` (sin cambio) | `Role` | `rol` |
| `roles.py` | `Permiso` | `roles.py` (sin cambio) | `Permission` | `permiso` |
| `sistema.py` | `Modulos` | `rbac.py` | `Module` | `modulos` |
| `sistema.py` | `ModuloPermiso` | `rbac.py` | `ModulePermission` | `modulo_permisos` |
| `sistema.py` | `RolPermisos` | `rbac.py` | `RolePermission` | `rol_permisos` |
| `sistema.py` | `UsuarioRoles` | `rbac.py` | `UserRole` | `usuario_roles` |

### Organization (3 clases)

| File ES | Class ES | File EN | Class EN | `db_table` |
|---|---|---|---|---|
| `area.py` | `Area` | `department.py` | `Department` | `area` |
| `ubicacion.py` | `HistorialUbicaciones` | `location_history.py` | `LocationHistory` | `historial_ubicaciones` |
| `configuracion_empresa.py` | `ConfiguracionEmpresa` | `company.py` | `Company` | `configuracion_empresa` |

### Employees (4 clases)

| File ES | Class ES | File EN | Class EN | `db_table` |
|---|---|---|---|---|
| `empleado.py` | `Empleado` | `employee.py` | `Employee` | `empleado` |
| `datos_familiares.py` | `DatosFamiliares` | `family_member.py` | `FamilyMember` | `datos_familiares` |
| `datos_academicos.py` | `DatosAcademicos` | `academic_record.py` | `AcademicRecord` | `datos_academicos` |
| `cursos_certificaciones.py` | `CursosCertificaciones` | `certification.py` | `Certification` | `cursos_certificaciones` |

### Contracts (2 clases — split de `ContratosAdendas` deferido a L3.10.3)

| File ES | Class ES | File EN | Class EN | `db_table` |
|---|---|---|---|---|
| `contratos_adendas.py` | `ContratosAdendas` | `contract.py` | `Contract` | `contratos_adendas` |
| `datos_laborales.py` | `DatosLaborales` | `employment_data.py` | `EmploymentData` | `datos_laborales` |

### Documents (2 clases)

| File ES | Class ES | File EN | Class EN | `db_table` |
|---|---|---|---|---|
| `documentos_digitales.py` | `DocumentosDigitales` | `digital_document.py` | `DigitalDocument` | `documentos_digitales` |
| `plantilla_documento.py` | `PlantillaDocumento` | `document_template.py` | `DocumentTemplate` | `app_rrhh_plantilla_documento` |

### Payroll (9 clases — `remuneracion.py` consolida 8)

| File ES | Class ES | File EN | Class EN | `db_table` |
|---|---|---|---|---|
| `remuneracion.py` | `PlanillaMensual` | `compensation.py` | `MonthlyPayroll` | `planilla_mensual` |
| `remuneracion.py` | `DetallePlanilla` | `compensation.py` | `PayrollDetail` | `detalle_planilla` |
| `remuneracion.py` | `ConceptoPlanilla` | `compensation.py` | `PayrollConcept` | `concepto_planilla` |
| `remuneracion.py` | `ConfiguracionAfp` | `compensation.py` | `AfpConfiguration` | `configuracion_afp` |
| `remuneracion.py` | `ConfiguracionRemuneracion` | `compensation.py` | `CompensationConfiguration` | `configuracion_remuneracion` |
| `remuneracion.py` | `DescuentoMasivo` | `compensation.py` | `MassDeduction` | `descuento_masivo` |
| `remuneracion.py` | `BoletaPago` | `compensation.py` | `PaySlip` | `boleta_pago` |
| `remuneracion.py` | `CalendarioPago` | `compensation.py` | `PaymentSchedule` | `calendario_pago` |
| `configuracion_uit.py` | `ConfiguracionUit` | `tax_parameter.py` | `TaxParameter` | `configuracion_uit` |

### Time off (5 clases — splits de `SolicitudVacaciones` deferidos a L3.10.3)

| File ES | Class ES | File EN | Class EN | `db_table` |
|---|---|---|---|---|
| `vacaciones.py` | `ConfiguracionVacaciones` | `vacation.py` | `VacationConfiguration` | `configuracion_vacaciones` |
| `vacaciones.py` | `PeriodoVacacional` | `vacation.py` | `VacationPeriod` | `periodos_vacacionales` |
| `vacaciones.py` | `SolicitudVacaciones` | `vacation.py` | `VacationRequest` | `solicitudes_vacaciones` |
| `vacaciones.py` | `GoceVacaciones` | `vacation.py` | `VacationGrant` | `goces_vacaciones` |
| `vacaciones.py` | `HistorialSolicitudVacaciones` | `vacation.py` | `VacationRequestHistory` | `historial_solicitudes_vacaciones` |

### Onboarding (1 clase)

| File ES | Class ES | File EN | Class EN | `db_table` |
|---|---|---|---|---|
| `onboarding.py` | `OnboardingEmpleado` | `onboarding_process.py` | `OnboardingProcess` | `onboarding_empleado` |

**Total: 34 clases renombradas en 21 archivos (15 archivos renombrados + 6 sin cambio en filename pero con clases renombradas).**

**Orden de aplicación de sed (longest-match first dentro de cada app)** — crítico para evitar reemplazos parciales:

```text
# Identity — orden obligatorio
UsuarioRoles → UserRole       (antes de Usuario)
RolPermisos → RolePermission  (antes de Rol)
ModuloPermiso → ModulePermission (antes de Modulos)
Modulos → Module
Usuario → User
Permiso → Permission
Rol → Role

# Time-off — orden obligatorio
HistorialSolicitudVacaciones → VacationRequestHistory  (antes de SolicitudVacaciones)
ConfiguracionVacaciones → VacationConfiguration
PeriodoVacacional → VacationPeriod
SolicitudVacaciones → VacationRequest
GoceVacaciones → VacationGrant

# Onboarding
OnboardingEmpleado → OnboardingProcess  (antes de Empleado, en step de employees)

# Organization
HistorialUbicaciones → LocationHistory
ConfiguracionEmpresa → Company
Area → Department

# Employees
CursosCertificaciones → Certification  (antes de cualquier "Cursos")
DatosFamiliares → FamilyMember
DatosAcademicos → AcademicRecord
Empleado → Employee

# Contracts
ContratosAdendas → Contract
DatosLaborales → EmploymentData

# Documents
DocumentosDigitales → DigitalDocument
PlantillaDocumento → DocumentTemplate

# Payroll
ConfiguracionRemuneracion → CompensationConfiguration  (antes de ConfiguracionUit, ConfiguracionAfp)
ConfiguracionAfp → AfpConfiguration
ConfiguracionUit → TaxParameter
PlanillaMensual → MonthlyPayroll  (antes de DetallePlanilla, ConceptoPlanilla — defensive)
DetallePlanilla → PayrollDetail
ConceptoPlanilla → PayrollConcept
DescuentoMasivo → MassDeduction
BoletaPago → PaySlip
CalendarioPago → PaymentSchedule
```

**Reglas duras del sed:**
- Usar `\bX\b` (word-boundary) — nunca substring sed.
- Procesar **single-quote y double-quote** strings juntos (LR10).
- Procesar **una app a la vez** (Tasks 4–11) ANTES del bulk cross-app (Task 12) — facilita debug.
- `Rol` y `Modulos` son los renames más peligrosos porque son cortos. Word-boundary es no-negociable.
- `Empleado` aparece embedded en `OnboardingEmpleado`. Por eso `OnboardingEmpleado` se renombra ANTES de `Empleado` en el orden global del Task 12.

---

## File Structure Overview

| Acción | Path |
|---|---|
| `git mv` | `apps/api/apps/identity/models/usuario.py` → `user.py` |
| `git mv` | `apps/api/apps/identity/models/sistema.py` → `rbac.py` |
| Edit | `apps/api/apps/identity/models/roles.py` (rename Rol→Role, Permiso→Permission inside) |
| Edit | `apps/api/apps/identity/models/__init__.py` (re-exports) |
| Edit | `apps/api/apps/identity/auth.py` (uses Usuario) |
| Edit | `apps/api/apps/identity/managers.py` (uses Usuario) |
| Edit | `apps/api/apps/identity/apps.py` (docstring mentions Usuario) |
| `git mv` | `apps/api/apps/organization/models/area.py` → `department.py` |
| `git mv` | `apps/api/apps/organization/models/ubicacion.py` → `location_history.py` |
| `git mv` | `apps/api/apps/organization/models/configuracion_empresa.py` → `company.py` |
| Edit | `apps/api/apps/organization/models/__init__.py` |
| `git mv` | `apps/api/apps/employees/models/empleado.py` → `employee.py` |
| `git mv` | `apps/api/apps/employees/models/datos_familiares.py` → `family_member.py` |
| `git mv` | `apps/api/apps/employees/models/datos_academicos.py` → `academic_record.py` |
| `git mv` | `apps/api/apps/employees/models/cursos_certificaciones.py` → `certification.py` |
| Edit | `apps/api/apps/employees/models/__init__.py` |
| `git mv` | `apps/api/apps/contracts/models/contratos_adendas.py` → `contract.py` |
| `git mv` | `apps/api/apps/contracts/models/datos_laborales.py` → `employment_data.py` |
| Edit | `apps/api/apps/contracts/models/__init__.py` |
| `git mv` | `apps/api/apps/documents/models/documentos_digitales.py` → `digital_document.py` |
| `git mv` | `apps/api/apps/documents/models/plantilla_documento.py` → `document_template.py` |
| Edit | `apps/api/apps/documents/models/__init__.py` |
| Edit | `apps/api/apps/documents/services/{pdf_generator,template_service,word_template_service}.py` |
| `git mv` | `apps/api/apps/payroll/models/remuneracion.py` → `compensation.py` |
| `git mv` | `apps/api/apps/payroll/models/configuracion_uit.py` → `tax_parameter.py` |
| Edit | `apps/api/apps/payroll/models/__init__.py` |
| Edit | `apps/api/apps/payroll/services/{descuento_masivo_service,planilla_calculo_service}.py` |
| `git mv` | `apps/api/apps/time_off/models/vacaciones.py` → `vacation.py` |
| Edit | `apps/api/apps/time_off/models/__init__.py` |
| Edit | `apps/api/apps/time_off/managers.py` |
| Edit | `apps/api/apps/time_off/services/*.py` (5 files) |
| `git mv` | `apps/api/apps/onboarding/models/onboarding.py` → `onboarding_process.py` |
| Edit | `apps/api/apps/onboarding/models/__init__.py` |
| Edit | `apps/api/apps/onboarding/services/onboarding_service.py` |
| Edit | `apps/api/apps/core/{decorators,middleware,permissions}.py` |
| Edit | `apps/api/api/v1/auth/{views,serializers}.py` |
| Edit | `apps/api/api/v1/rrhh/{views,serializers,filters,contratos_views,contratos_serializers,remuneraciones_views,remuneraciones_serializers,usuario_roles_views,usuario_roles_serializers}.py` |
| Edit | `apps/api/api/v1/vacaciones/{views,serializers,filters,permissions,validators,tests}.py` |
| Edit | `apps/api/api/v1/app_rrhh/document_generation_views.py` |
| Edit | `apps/api/tests/*.py` (~9 test files) |
| Edit | `apps/api/app_rrhh/{filters,managers,managers.py,menu_service,permission_service,serializers,serializers_optimized,services.py,tests.py,urls,validators,views,models.py,services/empleado_report_service}.py` |
| Edit | `apps/api/app_rrhh/management/commands/{audit_rbac,seed_menu,seed_plantillas_default,seed_remuneraciones_config,setup_roles_permisos}.py` |
| Edit | `apps/api/app_rrhh/managers/{contratos_manager,usuario_manager}.py` |
| Edit | `apps/api/vyntia/settings/base.py` (`AUTH_USER_MODEL = "identity.User"`) |
| Delete | `apps/api/apps/{identity,organization,employees,contracts,documents,payroll,time_off,onboarding}/migrations/0001_initial.py` (+ 0002 si existe) |

**NO se toca en L3.10.1:**
- Field names (`nombres`, `apellido_paterno`, `creado_en`, etc.) — L3.10.2
- `db_table` Spanish — preserved on every Meta
- `db_column` on FK fields — campo se llama igual, columna no cambia
- PK names (`empleado_id`, `usuario_id`) — L3.10.2
- Splits `Contract+ContractAmendment`, `VacationRequest+VacationBalance` — L3.10.3
- Frontend (`apps/web/`) — L3.10.4
- `app_rrhh/services/empleado_report_service.py` y otros services legacy — siguen ahí pero referencias actualizadas (cleanup eliminación = L3.11)
- Legacy `app_rrhh/{views,serializers,managers,validators,tests}.py` — siguen ahí pero referencias actualizadas (cleanup = L3.11)

**Lecciones aplicadas (LR9-LR14):**
- **LR9** (stale `'app_rrhh.X'`): pre-move grep confirma 0 hits hoy — N/A. Defensive check al final.
- **LR10** (sed single + double quote): cubierto en cada Task de app (4–11) y en bulk Task 12.
- **LR11** (relative `from .models import`): grep defensive en Task 14 (consumers de app_rrhh legacy).
- **LR12** (sequence drop → CREATE → makemigrations → migrate): aplicada en Task 17.
- **LR13** (logger names): grep defensive `getLogger.*['"]app_rrhh\.` en Task 18 — esperado 0 (resuelto en L3.6/L3.7).
- **LR14** (sed Pattern B multi-line `from app_rrhh.services import (`): grep defensive `from apps\.[a-z]+\.models import (` multi-line en Task 13 antes del bulk replace.

---

## Definition of Done

- [ ] 33 model classes renombradas (Tabla canónica completa aplicada)
- [ ] 15 model files renombrados con `git mv` (history preservada)
- [ ] 6 model files mantienen filename pero con clases renombradas dentro (`roles.py`, modelos en `compensation.py`/`vacation.py` que tienen >1 clase)
- [ ] 35 single-quote FK strings cross-app actualizadas (`'employees.Empleado'` → `'employees.Employee'`, etc.)
- [ ] 8 double-quote FK strings cross-app actualizadas (LR10)
- [ ] 170+ imports actualizados across `apps/api/apps/`, `apps/api/api/`, `apps/api/tests/`, `apps/api/app_rrhh/`
- [ ] 8 `__init__.py` re-exports de `apps/<name>/models/` actualizados
- [ ] `AUTH_USER_MODEL = "identity.User"` en `vyntia/settings/base.py:134`
- [ ] `apps/api/apps/identity/apps.py` docstring menciona `User` (no `Usuario`)
- [ ] Migrations regeneradas vía NUCLEAR DB: 1 `0001_initial.py` por app de dominio con clases inglesas y `db_table` español
- [ ] `bd_vyntia` recreada y reseeded; rol > 0, permiso > 0, modulos > 0
- [ ] Verificación física: tablas `empleado`, `usuarios`, `rol`, `permiso`, `area`, etc. existen en bd_vyntia (mismos nombres físicos pre-L3.10.1)
- [ ] `python manage.py check` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] 0 stale `Empleado|Usuario|Rol|Permiso|Area|ContratosAdendas|...` (clases renombradas) en código no-migración
- [ ] 0 stale `'app_rrhh.X'` strings (LR9 defensive)
- [ ] Branch `vyntia/L3.10.1-rename-classes` mergeada a master con `--no-ff`
- [ ] Roadmap `2026-04-25-vyntia-foundation-L3-master-roadmap.md` actualizado: L3.10.1 ✅, L3.10.2 NEXT
- [ ] `MEMORY.md/active_subproject.md` actualizado con scope split L3.10.1–L3.10.4

---

## Task 1: Pre-flight — branch, baseline, backup

- [ ] **Step 1: Confirmar pwd, master limpio, HEAD post-L3.9**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -3
```

Expected: HEAD en `db250278 docs(L3.9): mark L3.9 merged, L3.10 (rename ES→EN masivo) as next` o más reciente. `git status` empty.

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

Si difiere, **detener** y diagnosticar antes de empezar L3.10.1.

- [ ] **Step 4: Backup bd_vyntia (paranoia — más crítico que sub-PRs anteriores)**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.10.1.dump 2>&1 | tail -3
ls -lh /tmp/bd_vyntia_pre_L3.10.1.dump
```

Expected: dump existe.

- [ ] **Step 5: Crear branch L3.10.1**

```bash
git checkout -b vyntia/L3.10.1-rename-classes
git status --short
```

---

## Task 2: Comitear el plan en la branch

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-26-vyntia-foundation-L3.10.1-rename-classes.md
git commit -m "docs(L3.10.1): add class names rename plan (first of 4 sub-PRs of L3.10)"
```

---

## Task 3: Pre-rename inventory snapshot

Antes de tocar código, capturar el estado actual para poder validar deltas tras el rename.

- [ ] **Step 1: Snapshot de class definitions actuales**

```bash
cd D:/VYNTIA/apps/api
echo "=== Pre-rename: class definitions ==="
grep -h "^class " apps/*/models/*.py | sort > /tmp/L3.10.1-pre-classes.txt
cat /tmp/L3.10.1-pre-classes.txt | wc -l
echo "Expected: 33 lines (one per model class)"
cd ../..
```

Expected: 33.

- [ ] **Step 2: Snapshot de `db_table` actuales**

```bash
cd D:/VYNTIA/apps/api
echo "=== Pre-rename: db_table values ==="
grep -hE "db_table\s*=" apps/*/models/*.py | sort > /tmp/L3.10.1-pre-dbtables.txt
cat /tmp/L3.10.1-pre-dbtables.txt | wc -l
cd ../..
```

Expected: 33 (same count as classes — every model has explicit `db_table`).

- [ ] **Step 3: Snapshot de FK strings cross-app**

```bash
cd D:/VYNTIA/apps/api
echo "=== Pre-rename: FK string refs (single + double quote) ==="
grep -rEn "'(employees|identity|organization|contracts|documents|payroll|time_off|onboarding)\.[A-Z][a-zA-Z]+'|\"(employees|identity|organization|contracts|documents|payroll|time_off|onboarding)\.[A-Z][a-zA-Z]+\"" apps/*/models/*.py > /tmp/L3.10.1-pre-fks.txt
cat /tmp/L3.10.1-pre-fks.txt | wc -l
cd ../..
```

Expected: 43 (35 single + 8 double).

- [ ] **Step 4: Confirmar AUTH_USER_MODEL state**

```bash
grep "AUTH_USER_MODEL" apps/api/vyntia/settings/base.py
```

Expected: `AUTH_USER_MODEL = "identity.Usuario"` (línea 134).

---

## Task 4: Rename `identity` app

**Files:**
- `git mv`: `apps/api/apps/identity/models/usuario.py` → `user.py`
- `git mv`: `apps/api/apps/identity/models/sistema.py` → `rbac.py`
- Modify (no rename): `apps/api/apps/identity/models/roles.py`
- Modify: `apps/api/apps/identity/models/__init__.py`
- Modify: `apps/api/apps/identity/auth.py`
- Modify: `apps/api/apps/identity/managers.py`
- Modify: `apps/api/apps/identity/apps.py`

- [ ] **Step 1: `git mv` ambos archivos a sus nombres ingleses**

```bash
cd D:/VYNTIA/apps/api
git mv apps/identity/models/usuario.py apps/identity/models/user.py
git mv apps/identity/models/sistema.py apps/identity/models/rbac.py
cd ../..
git status --short | head -10
```

Expected: 2 archivos `R` (rename) en `apps/identity/models/`.

- [ ] **Step 2: Aplicar sed en `apps/identity/` — orden longest-match-first**

Orden estricto: `UsuarioRoles → UserRole`, `RolPermisos → RolePermission`, `ModuloPermiso → ModulePermission`, `Modulos → Module`, `Usuario → User`, `Permiso → Permission`, `Rol → Role`. Usar `\b` word-boundary.

```bash
cd D:/VYNTIA/apps/api
find apps/identity -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -print0 | xargs -0 sed -i \
  -e 's|\bUsuarioRoles\b|UserRole|g' \
  -e 's|\bRolPermisos\b|RolePermission|g' \
  -e 's|\bModuloPermiso\b|ModulePermission|g' \
  -e 's|\bModulos\b|Module|g' \
  -e 's|\bUsuario\b|User|g' \
  -e 's|\bPermiso\b|Permission|g' \
  -e 's|\bRol\b|Role|g'
cd ../..
```

- [ ] **Step 3: Verificar clases renombradas en `apps/identity/`**

```bash
cd D:/VYNTIA/apps/api
echo "=== identity/ class defs (expected: User, Role, Permission, Module, ModulePermission, RolePermission, UserRole) ==="
grep -hE "^class " apps/identity/models/*.py | sort
echo ""
echo "=== Stale ES class names en apps/identity/ — should be 0 ==="
grep -rEn "\b(Usuario|Rol|Permiso|Modulos|ModuloPermiso|RolPermisos|UsuarioRoles)\b" apps/identity --include="*.py" | grep -v "__pycache__\|migrations" || echo "OK: cero"
cd ../..
```

Expected:
```
class Module(models.Model):
class ModulePermission(models.Model):
class Permission(models.Model):
class Role(models.Model):
class RolePermission(models.Model):
class User(AbstractBaseUser, PermissionsMixin):
class UserRole(models.Model):
```
Y `OK: cero` para stale check.

- [ ] **Step 4: Update `__init__.py` re-exports**

Use Edit tool en `apps/api/apps/identity/models/__init__.py`:
- old_string:
```python
"""Identity models — re-exports for backward-compatible imports."""

from .roles import Permiso, Rol
from .sistema import ModuloPermiso, Modulos, RolPermisos, UsuarioRoles
from .usuario import Usuario

__all__ = [
    "Modulos",
    "ModuloPermiso",
    "Permiso",
    "Rol",
    "RolPermisos",
    "Usuario",
    "UsuarioRoles",
]
```
- new_string:
```python
"""Identity models — re-exports for backward-compatible imports."""

from .rbac import Module, ModulePermission, RolePermission, UserRole
from .roles import Permission, Role
from .user import User

__all__ = [
    "Module",
    "ModulePermission",
    "Permission",
    "Role",
    "RolePermission",
    "User",
    "UserRole",
]
```

- [ ] **Step 5: Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.identity.models import User, Role, Permission, Module, ModulePermission, RolePermission, UserRole; print('OK')"
cd ../..
```

Expected: `OK`. Si falla, hay un import roto en algún archivo de identity (probablemente relative import a `usuario` o `sistema`).

---

## Task 5: Rename `organization` app

**Files:**
- `git mv`: `apps/api/apps/organization/models/area.py` → `department.py`
- `git mv`: `apps/api/apps/organization/models/ubicacion.py` → `location_history.py`
- `git mv`: `apps/api/apps/organization/models/configuracion_empresa.py` → `company.py`
- Modify: `apps/api/apps/organization/models/__init__.py`

- [ ] **Step 1: `git mv` files**

```bash
cd D:/VYNTIA/apps/api
git mv apps/organization/models/area.py apps/organization/models/department.py
git mv apps/organization/models/ubicacion.py apps/organization/models/location_history.py
git mv apps/organization/models/configuracion_empresa.py apps/organization/models/company.py
cd ../..
```

- [ ] **Step 2: Sed inside `apps/organization/`**

Orden: `HistorialUbicaciones`, `ConfiguracionEmpresa`, `Area`. (No solapan unos con otros pero la convención es longest-first.)

```bash
cd D:/VYNTIA/apps/api
find apps/organization -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -print0 | xargs -0 sed -i \
  -e 's|\bHistorialUbicaciones\b|LocationHistory|g' \
  -e 's|\bConfiguracionEmpresa\b|Company|g' \
  -e 's|\bArea\b|Department|g'
cd ../..
```

- [ ] **Step 3: Verificar**

```bash
cd D:/VYNTIA/apps/api
echo "=== organization class defs ==="
grep -hE "^class " apps/organization/models/*.py | sort
echo ""
echo "=== Stale ES en apps/organization/ — should be 0 ==="
grep -rEn "\b(Area|HistorialUbicaciones|ConfiguracionEmpresa)\b" apps/organization --include="*.py" | grep -v "__pycache__\|migrations" || echo "OK: cero"
cd ../..
```

Expected:
```
class Company(models.Model):
class Department(models.Model):
class LocationHistory(models.Model):
```
Y `OK: cero`.

- [ ] **Step 4: Update `__init__.py`**

Use Edit tool en `apps/api/apps/organization/models/__init__.py`:
- old_string:
```python
"""Organization models — re-exports for backward-compatible imports."""

from .area import Area
from .configuracion_empresa import ConfiguracionEmpresa
from .ubicacion import HistorialUbicaciones

__all__ = [
    "Area",
    "ConfiguracionEmpresa",
    "HistorialUbicaciones",
]
```
- new_string:
```python
"""Organization models — re-exports for backward-compatible imports."""

from .company import Company
from .department import Department
from .location_history import LocationHistory

__all__ = [
    "Company",
    "Department",
    "LocationHistory",
]
```

- [ ] **Step 5: Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.organization.models import Department, LocationHistory, Company; print('OK')"
cd ../..
```

Expected: `OK`.

---

## Task 6: Rename `employees` app

**Files:**
- `git mv`: 4 model files
- Modify: `__init__.py`

- [ ] **Step 1: `git mv` files**

```bash
cd D:/VYNTIA/apps/api
git mv apps/employees/models/empleado.py apps/employees/models/employee.py
git mv apps/employees/models/datos_familiares.py apps/employees/models/family_member.py
git mv apps/employees/models/datos_academicos.py apps/employees/models/academic_record.py
git mv apps/employees/models/cursos_certificaciones.py apps/employees/models/certification.py
cd ../..
```

- [ ] **Step 2: Sed inside `apps/employees/`**

Orden: `CursosCertificaciones`, `DatosFamiliares`, `DatosAcademicos`, `Empleado`. (Orden importa entre `Empleado` y los demás solo si algún otro contuviera `Empleado` como substring — no es el caso, pero es buena práctica.)

```bash
cd D:/VYNTIA/apps/api
find apps/employees -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -print0 | xargs -0 sed -i \
  -e 's|\bCursosCertificaciones\b|Certification|g' \
  -e 's|\bDatosFamiliares\b|FamilyMember|g' \
  -e 's|\bDatosAcademicos\b|AcademicRecord|g' \
  -e 's|\bEmpleado\b|Employee|g'
cd ../..
```

- [ ] **Step 3: Verificar**

```bash
cd D:/VYNTIA/apps/api
echo "=== employees class defs ==="
grep -hE "^class " apps/employees/models/*.py | sort
echo ""
echo "=== Stale ES en apps/employees/ — should be 0 ==="
grep -rEn "\b(Empleado|DatosFamiliares|DatosAcademicos|CursosCertificaciones)\b" apps/employees --include="*.py" | grep -v "__pycache__\|migrations" || echo "OK: cero"
cd ../..
```

Expected:
```
class AcademicRecord(models.Model):
class Certification(models.Model):
class Employee(models.Model):
class FamilyMember(models.Model):
```
Y `OK: cero`.

- [ ] **Step 4: Update `__init__.py`**

Use Edit tool en `apps/api/apps/employees/models/__init__.py`:
- old_string:
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
- new_string:
```python
"""Employees models — re-exports for backward-compatible imports."""

from .academic_record import AcademicRecord
from .certification import Certification
from .employee import Employee
from .family_member import FamilyMember

__all__ = [
    "AcademicRecord",
    "Certification",
    "Employee",
    "FamilyMember",
]
```

- [ ] **Step 5: Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.employees.models import Employee, FamilyMember, AcademicRecord, Certification; print('OK')"
cd ../..
```

Expected: `OK`.

---

## Task 7: Rename `contracts` app

- [ ] **Step 1: `git mv` files**

```bash
cd D:/VYNTIA/apps/api
git mv apps/contracts/models/contratos_adendas.py apps/contracts/models/contract.py
git mv apps/contracts/models/datos_laborales.py apps/contracts/models/employment_data.py
cd ../..
```

- [ ] **Step 2: Sed inside `apps/contracts/`**

```bash
cd D:/VYNTIA/apps/api
find apps/contracts -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -print0 | xargs -0 sed -i \
  -e 's|\bContratosAdendas\b|Contract|g' \
  -e 's|\bDatosLaborales\b|EmploymentData|g'
cd ../..
```

- [ ] **Step 3: Verificar**

```bash
cd D:/VYNTIA/apps/api
echo "=== contracts class defs ==="
grep -hE "^class " apps/contracts/models/*.py | sort
echo ""
echo "=== Stale ES en apps/contracts/ — should be 0 ==="
grep -rEn "\b(ContratosAdendas|DatosLaborales)\b" apps/contracts --include="*.py" | grep -v "__pycache__\|migrations" || echo "OK: cero"
cd ../..
```

Expected:
```
class Contract(models.Model):
class EmploymentData(models.Model):
```
Y `OK: cero`.

- [ ] **Step 4: Update `__init__.py`**

Use Edit tool en `apps/api/apps/contracts/models/__init__.py`:
- old_string:
```python
"""Contracts models — re-exports for backward-compatible imports."""

from .contratos_adendas import ContratosAdendas
from .datos_laborales import DatosLaborales

__all__ = [
    "ContratosAdendas",
    "DatosLaborales",
]
```
- new_string:
```python
"""Contracts models — re-exports for backward-compatible imports."""

from .contract import Contract
from .employment_data import EmploymentData

__all__ = [
    "Contract",
    "EmploymentData",
]
```

- [ ] **Step 5: Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.contracts.models import Contract, EmploymentData; print('OK')"
cd ../..
```

Expected: `OK`.

---

## Task 8: Rename `documents` app

- [ ] **Step 1: `git mv` files**

```bash
cd D:/VYNTIA/apps/api
git mv apps/documents/models/documentos_digitales.py apps/documents/models/digital_document.py
git mv apps/documents/models/plantilla_documento.py apps/documents/models/document_template.py
cd ../..
```

- [ ] **Step 2: Sed inside `apps/documents/`** (incluye services)

```bash
cd D:/VYNTIA/apps/api
find apps/documents -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -print0 | xargs -0 sed -i \
  -e 's|\bDocumentosDigitales\b|DigitalDocument|g' \
  -e 's|\bPlantillaDocumento\b|DocumentTemplate|g'
cd ../..
```

- [ ] **Step 3: Verificar**

```bash
cd D:/VYNTIA/apps/api
echo "=== documents class defs ==="
grep -hE "^class " apps/documents/models/*.py | sort
echo ""
echo "=== Stale ES en apps/documents/ — should be 0 ==="
grep -rEn "\b(DocumentosDigitales|PlantillaDocumento)\b" apps/documents --include="*.py" | grep -v "__pycache__\|migrations" || echo "OK: cero"
cd ../..
```

Expected:
```
class DigitalDocument(models.Model):
class DocumentTemplate(models.Model):
```
Y `OK: cero`.

Nota: services en `apps/documents/services/` también referencian `Empleado`, `ContratosAdendas`, `Area` — esas FK serán renombradas en Task 12 (bulk cross-app). Por ahora solo se renombra lo que es **propio** del app.

- [ ] **Step 4: Update `__init__.py`**

Use Edit tool en `apps/api/apps/documents/models/__init__.py`:
- old_string:
```python
"""Documents models — re-exports for backward-compatible imports."""

from .documentos_digitales import DocumentosDigitales
from .plantilla_documento import PlantillaDocumento

__all__ = [
    "DocumentosDigitales",
    "PlantillaDocumento",
]
```
- new_string:
```python
"""Documents models — re-exports for backward-compatible imports."""

from .digital_document import DigitalDocument
from .document_template import DocumentTemplate

__all__ = [
    "DigitalDocument",
    "DocumentTemplate",
]
```

- [ ] **Step 5: Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.documents.models import DigitalDocument, DocumentTemplate; print('OK')"
cd ../..
```

Expected: `OK`.

---

## Task 9: Rename `payroll` app

- [ ] **Step 1: `git mv` files**

```bash
cd D:/VYNTIA/apps/api
git mv apps/payroll/models/remuneracion.py apps/payroll/models/compensation.py
git mv apps/payroll/models/configuracion_uit.py apps/payroll/models/tax_parameter.py
cd ../..
```

- [ ] **Step 2: Sed inside `apps/payroll/`** (orden longest-match-first)

```bash
cd D:/VYNTIA/apps/api
find apps/payroll -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -print0 | xargs -0 sed -i \
  -e 's|\bConfiguracionRemuneracion\b|CompensationConfiguration|g' \
  -e 's|\bConfiguracionAfp\b|AfpConfiguration|g' \
  -e 's|\bConfiguracionUit\b|TaxParameter|g' \
  -e 's|\bPlanillaMensual\b|MonthlyPayroll|g' \
  -e 's|\bDetallePlanilla\b|PayrollDetail|g' \
  -e 's|\bConceptoPlanilla\b|PayrollConcept|g' \
  -e 's|\bDescuentoMasivo\b|MassDeduction|g' \
  -e 's|\bBoletaPago\b|PaySlip|g' \
  -e 's|\bCalendarioPago\b|PaymentSchedule|g'
cd ../..
```

- [ ] **Step 3: Verificar**

```bash
cd D:/VYNTIA/apps/api
echo "=== payroll class defs ==="
grep -hE "^class " apps/payroll/models/*.py | sort
echo ""
echo "=== Stale ES en apps/payroll/ — should be 0 ==="
grep -rEn "\b(PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago)\b" apps/payroll --include="*.py" | grep -v "__pycache__\|migrations" || echo "OK: cero"
cd ../..
```

Expected: 9 class defs:
```
class AfpConfiguration(models.Model):
class CompensationConfiguration(models.Model):
class MassDeduction(models.Model):
class MonthlyPayroll(models.Model):
class PaySlip(models.Model):
class PayrollConcept(models.Model):
class PayrollDetail(models.Model):
class PaymentSchedule(models.Model):
class TaxParameter(models.Model):
```
Y `OK: cero`.

- [ ] **Step 4: Update `__init__.py`**

Use Edit tool en `apps/api/apps/payroll/models/__init__.py`:
- old_string:
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
- new_string:
```python
"""Payroll models — re-exports for backward-compatible imports."""

from .compensation import (
    AfpConfiguration,
    CompensationConfiguration,
    MassDeduction,
    MonthlyPayroll,
    PaymentSchedule,
    PayrollConcept,
    PayrollDetail,
    PaySlip,
)
from .tax_parameter import TaxParameter

__all__ = [
    "AfpConfiguration",
    "CompensationConfiguration",
    "MassDeduction",
    "MonthlyPayroll",
    "PaymentSchedule",
    "PayrollConcept",
    "PayrollDetail",
    "PaySlip",
    "TaxParameter",
]
```

- [ ] **Step 5: Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.payroll.models import MonthlyPayroll, PayrollDetail, PayrollConcept, AfpConfiguration, CompensationConfiguration, MassDeduction, PaySlip, PaymentSchedule, TaxParameter; print('OK')"
cd ../..
```

Expected: `OK`.

---

## Task 10: Rename `time_off` app

- [ ] **Step 1: `git mv` file**

```bash
cd D:/VYNTIA/apps/api
git mv apps/time_off/models/vacaciones.py apps/time_off/models/vacation.py
cd ../..
```

- [ ] **Step 2: Sed inside `apps/time_off/`** (orden longest-match-first)

```bash
cd D:/VYNTIA/apps/api
find apps/time_off -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -print0 | xargs -0 sed -i \
  -e 's|\bHistorialSolicitudVacaciones\b|VacationRequestHistory|g' \
  -e 's|\bConfiguracionVacaciones\b|VacationConfiguration|g' \
  -e 's|\bPeriodoVacacional\b|VacationPeriod|g' \
  -e 's|\bSolicitudVacaciones\b|VacationRequest|g' \
  -e 's|\bGoceVacaciones\b|VacationGrant|g'
cd ../..
```

- [ ] **Step 3: Verificar**

```bash
cd D:/VYNTIA/apps/api
echo "=== time_off class defs ==="
grep -hE "^class " apps/time_off/models/*.py | sort
echo ""
echo "=== Stale ES en apps/time_off/ — should be 0 ==="
grep -rEn "\b(SolicitudVacaciones|GoceVacaciones|ConfiguracionVacaciones|HistorialSolicitudVacaciones|PeriodoVacacional)\b" apps/time_off --include="*.py" | grep -v "__pycache__\|migrations" || echo "OK: cero"
cd ../..
```

Expected:
```
class VacationConfiguration(models.Model):
class VacationGrant(models.Model):
class VacationPeriod(models.Model):
class VacationRequest(models.Model):
class VacationRequestHistory(models.Model):
```
Y `OK: cero`.

- [ ] **Step 4: Update `__init__.py`**

Use Edit tool en `apps/api/apps/time_off/models/__init__.py`:
- old_string:
```python
"""Time off models — re-exports for backward-compatible imports."""

from .vacaciones import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    HistorialSolicitudVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)

__all__ = [
    "ConfiguracionVacaciones",
    "GoceVacaciones",
    "HistorialSolicitudVacaciones",
    "PeriodoVacacional",
    "SolicitudVacaciones",
]
```
- new_string:
```python
"""Time off models — re-exports for backward-compatible imports."""

from .vacation import (
    VacationConfiguration,
    VacationGrant,
    VacationPeriod,
    VacationRequest,
    VacationRequestHistory,
)

__all__ = [
    "VacationConfiguration",
    "VacationGrant",
    "VacationPeriod",
    "VacationRequest",
    "VacationRequestHistory",
]
```

- [ ] **Step 5: Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.time_off.models import VacationRequest, VacationGrant, VacationConfiguration, VacationPeriod, VacationRequestHistory; print('OK')"
cd ../..
```

Expected: `OK`.

---

## Task 11: Rename `onboarding` app

- [ ] **Step 1: `git mv` file**

```bash
cd D:/VYNTIA/apps/api
git mv apps/onboarding/models/onboarding.py apps/onboarding/models/onboarding_process.py
cd ../..
```

- [ ] **Step 2: Sed inside `apps/onboarding/`**

```bash
cd D:/VYNTIA/apps/api
find apps/onboarding -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -print0 | xargs -0 sed -i \
  -e 's|\bOnboardingEmpleado\b|OnboardingProcess|g'
cd ../..
```

- [ ] **Step 3: Verificar**

```bash
cd D:/VYNTIA/apps/api
echo "=== onboarding class defs ==="
grep -hE "^class " apps/onboarding/models/*.py | sort
echo ""
echo "=== Stale ES en apps/onboarding/ — should be 0 ==="
grep -rEn "\bOnboardingEmpleado\b" apps/onboarding --include="*.py" | grep -v "__pycache__\|migrations" || echo "OK: cero"
cd ../..
```

Expected:
```
class OnboardingProcess(models.Model):
```
Y `OK: cero`.

- [ ] **Step 4: Update `__init__.py`**

Use Edit tool en `apps/api/apps/onboarding/models/__init__.py`:
- old_string:
```python
"""Onboarding models — re-exports for backward-compatible imports."""

from .onboarding import OnboardingEmpleado

__all__ = [
    "OnboardingEmpleado",
]
```
- new_string:
```python
"""Onboarding models — re-exports for backward-compatible imports."""

from .onboarding_process import OnboardingProcess

__all__ = [
    "OnboardingProcess",
]
```

- [ ] **Step 5: Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.onboarding.models import OnboardingProcess; print('OK')"
cd ../..
```

Expected: `OK`.

---

## Task 12: Bulk cross-app FK string updates (single + double quote — LR10)

**Por qué:** Las apps ya tienen sus clases internas renombradas (Tasks 4–11), pero las **FK strings cross-app** siguen apuntando al nombre español: `'employees.Empleado'`, `'identity.Usuario'`, etc. Ahora se actualizan en bulk.

- [ ] **Step 1: Inventory de FKs cross-app actuales (post Tasks 4–11)**

```bash
cd D:/VYNTIA/apps/api
echo "=== Current cross-app FK strings (single + double quote) ==="
grep -rEn "['\"](employees|identity|organization|contracts|documents|payroll|time_off|onboarding)\.[A-Z][a-zA-Z]+['\"]" apps/*/models/*.py | sort
echo ""
echo "=== Total count ==="
grep -rEcn "['\"](employees|identity|organization|contracts|documents|payroll|time_off|onboarding)\.[A-Z][a-zA-Z]+['\"]" apps/*/models/*.py | awk -F: '{s+=$2} END {print s}'
cd ../..
```

Expected: 43 (35 single + 8 double).

- [ ] **Step 2: Sed bulk replace — orden longest-match-first sobre TODOS los model files cross-app**

```bash
cd D:/VYNTIA/apps/api
find apps -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -print0 | xargs -0 sed -i \
  -e "s|'employees\.OnboardingEmpleado'|'onboarding.OnboardingProcess'|g" \
  -e 's|"employees\.OnboardingEmpleado"|"onboarding.OnboardingProcess"|g' \
  -e "s|'employees\.CursosCertificaciones'|'employees.Certification'|g" \
  -e 's|"employees\.CursosCertificaciones"|"employees.Certification"|g' \
  -e "s|'employees\.DatosFamiliares'|'employees.FamilyMember'|g" \
  -e 's|"employees\.DatosFamiliares"|"employees.FamilyMember"|g' \
  -e "s|'employees\.DatosAcademicos'|'employees.AcademicRecord'|g" \
  -e 's|"employees\.DatosAcademicos"|"employees.AcademicRecord"|g' \
  -e "s|'employees\.Empleado'|'employees.Employee'|g" \
  -e 's|"employees\.Empleado"|"employees.Employee"|g' \
  -e "s|'identity\.UsuarioRoles'|'identity.UserRole'|g" \
  -e 's|"identity\.UsuarioRoles"|"identity.UserRole"|g' \
  -e "s|'identity\.RolPermisos'|'identity.RolePermission'|g" \
  -e 's|"identity\.RolPermisos"|"identity.RolePermission"|g' \
  -e "s|'identity\.ModuloPermiso'|'identity.ModulePermission'|g" \
  -e 's|"identity\.ModuloPermiso"|"identity.ModulePermission"|g' \
  -e "s|'identity\.Modulos'|'identity.Module'|g" \
  -e 's|"identity\.Modulos"|"identity.Module"|g' \
  -e "s|'identity\.Usuario'|'identity.User'|g" \
  -e 's|"identity\.Usuario"|"identity.User"|g' \
  -e "s|'identity\.Permiso'|'identity.Permission'|g" \
  -e 's|"identity\.Permiso"|"identity.Permission"|g' \
  -e "s|'identity\.Rol'|'identity.Role'|g" \
  -e 's|"identity\.Rol"|"identity.Role"|g' \
  -e "s|'organization\.HistorialUbicaciones'|'organization.LocationHistory'|g" \
  -e 's|"organization\.HistorialUbicaciones"|"organization.LocationHistory"|g' \
  -e "s|'organization\.ConfiguracionEmpresa'|'organization.Company'|g" \
  -e 's|"organization\.ConfiguracionEmpresa"|"organization.Company"|g' \
  -e "s|'organization\.Area'|'organization.Department'|g" \
  -e 's|"organization\.Area"|"organization.Department"|g' \
  -e "s|'contracts\.ContratosAdendas'|'contracts.Contract'|g" \
  -e 's|"contracts\.ContratosAdendas"|"contracts.Contract"|g' \
  -e "s|'contracts\.DatosLaborales'|'contracts.EmploymentData'|g" \
  -e 's|"contracts\.DatosLaborales"|"contracts.EmploymentData"|g' \
  -e "s|'documents\.DocumentosDigitales'|'documents.DigitalDocument'|g" \
  -e 's|"documents\.DocumentosDigitales"|"documents.DigitalDocument"|g' \
  -e "s|'documents\.PlantillaDocumento'|'documents.DocumentTemplate'|g" \
  -e 's|"documents\.PlantillaDocumento"|"documents.DocumentTemplate"|g' \
  -e "s|'payroll\.ConfiguracionRemuneracion'|'payroll.CompensationConfiguration'|g" \
  -e 's|"payroll\.ConfiguracionRemuneracion"|"payroll.CompensationConfiguration"|g' \
  -e "s|'payroll\.ConfiguracionAfp'|'payroll.AfpConfiguration'|g" \
  -e 's|"payroll\.ConfiguracionAfp"|"payroll.AfpConfiguration"|g' \
  -e "s|'payroll\.ConfiguracionUit'|'payroll.TaxParameter'|g" \
  -e 's|"payroll\.ConfiguracionUit"|"payroll.TaxParameter"|g' \
  -e "s|'payroll\.PlanillaMensual'|'payroll.MonthlyPayroll'|g" \
  -e 's|"payroll\.PlanillaMensual"|"payroll.MonthlyPayroll"|g' \
  -e "s|'payroll\.DetallePlanilla'|'payroll.PayrollDetail'|g" \
  -e 's|"payroll\.DetallePlanilla"|"payroll.PayrollDetail"|g' \
  -e "s|'payroll\.ConceptoPlanilla'|'payroll.PayrollConcept'|g" \
  -e 's|"payroll\.ConceptoPlanilla"|"payroll.PayrollConcept"|g' \
  -e "s|'payroll\.DescuentoMasivo'|'payroll.MassDeduction'|g" \
  -e 's|"payroll\.DescuentoMasivo"|"payroll.MassDeduction"|g' \
  -e "s|'payroll\.BoletaPago'|'payroll.PaySlip'|g" \
  -e 's|"payroll\.BoletaPago"|"payroll.PaySlip"|g' \
  -e "s|'payroll\.CalendarioPago'|'payroll.PaymentSchedule'|g" \
  -e 's|"payroll\.CalendarioPago"|"payroll.PaymentSchedule"|g' \
  -e "s|'time_off\.HistorialSolicitudVacaciones'|'time_off.VacationRequestHistory'|g" \
  -e 's|"time_off\.HistorialSolicitudVacaciones"|"time_off.VacationRequestHistory"|g' \
  -e "s|'time_off\.ConfiguracionVacaciones'|'time_off.VacationConfiguration'|g" \
  -e 's|"time_off\.ConfiguracionVacaciones"|"time_off.VacationConfiguration"|g' \
  -e "s|'time_off\.PeriodoVacacional'|'time_off.VacationPeriod'|g" \
  -e 's|"time_off\.PeriodoVacacional"|"time_off.VacationPeriod"|g' \
  -e "s|'time_off\.SolicitudVacaciones'|'time_off.VacationRequest'|g" \
  -e 's|"time_off\.SolicitudVacaciones"|"time_off.VacationRequest"|g' \
  -e "s|'time_off\.GoceVacaciones'|'time_off.VacationGrant'|g" \
  -e 's|"time_off\.GoceVacaciones"|"time_off.VacationGrant"|g' \
  -e "s|'onboarding\.OnboardingEmpleado'|'onboarding.OnboardingProcess'|g" \
  -e 's|"onboarding\.OnboardingEmpleado"|"onboarding.OnboardingProcess"|g'
cd ../..
```

- [ ] **Step 3: Verificar — 0 stale FK strings con nombres ES**

```bash
cd D:/VYNTIA/apps/api
echo "=== Stale FK strings (any cross-app, ES class names) — should be 0 ==="
grep -rEn "['\"](employees|identity|organization|contracts|documents|payroll|time_off|onboarding)\.(Empleado|Usuario|Rol|Permiso|Modulos|ModuloPermiso|RolPermisos|UsuarioRoles|Area|HistorialUbicaciones|ConfiguracionEmpresa|ContratosAdendas|DatosLaborales|DocumentosDigitales|PlantillaDocumento|PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago|SolicitudVacaciones|GoceVacaciones|ConfiguracionVacaciones|HistorialSolicitudVacaciones|PeriodoVacacional|DatosFamiliares|DatosAcademicos|CursosCertificaciones|OnboardingEmpleado)['\"]" apps --include="*.py" | grep -v "__pycache__\|migrations" || echo "OK: cero"
echo ""
echo "=== Updated FK strings — count expected: 43 ==="
grep -rEcn "['\"](employees|identity|organization|contracts|documents|payroll|time_off|onboarding)\.(Employee|User|Role|Permission|Module|ModulePermission|RolePermission|UserRole|Department|LocationHistory|Company|Contract|EmploymentData|DigitalDocument|DocumentTemplate|MonthlyPayroll|PayrollDetail|PayrollConcept|AfpConfiguration|CompensationConfiguration|TaxParameter|MassDeduction|PaySlip|PaymentSchedule|VacationRequest|VacationGrant|VacationConfiguration|VacationRequestHistory|VacationPeriod|FamilyMember|AcademicRecord|Certification|OnboardingProcess)['\"]" apps/*/models/*.py | awk -F: '{s+=$2} END {print s}'
cd ../..
```

Expected: stale `OK: cero`. Updated count: 43.

- [ ] **Step 4: LR9 defensive check — 0 stale `'app_rrhh.X'`**

```bash
cd D:/VYNTIA/apps/api
echo "=== Stale 'app_rrhh.X' or \"app_rrhh.X\" (LR9) — should be 0 ==="
grep -rEn "['\"]app_rrhh\.[A-Z][a-zA-Z]+['\"]" apps --include="*.py" | grep -v "__pycache__\|migrations" || echo "OK: cero"
cd ../..
```

Expected: `OK: cero`.

---

## Task 13: Update consumer imports en `apps/api/api/v1/`

**Files (~12 files):**
- `apps/api/api/v1/auth/{views,serializers}.py`
- `apps/api/api/v1/rrhh/{views,serializers,filters,contratos_views,contratos_serializers,remuneraciones_views,remuneraciones_serializers,usuario_roles_views,usuario_roles_serializers}.py`
- `apps/api/api/v1/vacaciones/{views,serializers,filters,permissions,validators,tests}.py`
- `apps/api/api/v1/app_rrhh/document_generation_views.py`

- [ ] **Step 1: LR14 defensive — detectar multi-line `from apps.X.models import (\n...,\n)` blocks**

```bash
cd D:/VYNTIA/apps/api
echo "=== Multi-line import blocks en api/v1/ (LR14) ==="
grep -rEn "from apps\.[a-z_]+\.models import \(" api --include="*.py" | grep -v "__pycache__"
cd ../..
```

Expected: lista de archivos con multi-line imports. Estos NO se rompen con el sed ya aplicado en Tasks 4–11 porque el sed ya operó en cada archivo independientemente (no requiere matchear el patrón `from X import` — solo matchea los identifiers `Empleado`, `Usuario`, etc.).

**Confirmación:** El sed de Tasks 4–11 fue ejecutado solo sobre `apps/<name>/`, no sobre `api/`. Las clases ya están renombradas en los modelos pero los imports en `api/v1/` aún apuntan a los nombres ES. Step 2 los actualiza.

- [ ] **Step 2: Bulk sed sobre `api/v1/` — orden longest-match-first**

```bash
cd D:/VYNTIA/apps/api
find api -type f -name "*.py" -not -path "*/__pycache__/*" -print0 | xargs -0 sed -i \
  -e 's|\bOnboardingEmpleado\b|OnboardingProcess|g' \
  -e 's|\bCursosCertificaciones\b|Certification|g' \
  -e 's|\bDatosFamiliares\b|FamilyMember|g' \
  -e 's|\bDatosAcademicos\b|AcademicRecord|g' \
  -e 's|\bUsuarioRoles\b|UserRole|g' \
  -e 's|\bRolPermisos\b|RolePermission|g' \
  -e 's|\bModuloPermiso\b|ModulePermission|g' \
  -e 's|\bModulos\b|Module|g' \
  -e 's|\bHistorialUbicaciones\b|LocationHistory|g' \
  -e 's|\bConfiguracionEmpresa\b|Company|g' \
  -e 's|\bContratosAdendas\b|Contract|g' \
  -e 's|\bDatosLaborales\b|EmploymentData|g' \
  -e 's|\bDocumentosDigitales\b|DigitalDocument|g' \
  -e 's|\bPlantillaDocumento\b|DocumentTemplate|g' \
  -e 's|\bConfiguracionRemuneracion\b|CompensationConfiguration|g' \
  -e 's|\bConfiguracionAfp\b|AfpConfiguration|g' \
  -e 's|\bConfiguracionUit\b|TaxParameter|g' \
  -e 's|\bPlanillaMensual\b|MonthlyPayroll|g' \
  -e 's|\bDetallePlanilla\b|PayrollDetail|g' \
  -e 's|\bConceptoPlanilla\b|PayrollConcept|g' \
  -e 's|\bDescuentoMasivo\b|MassDeduction|g' \
  -e 's|\bBoletaPago\b|PaySlip|g' \
  -e 's|\bCalendarioPago\b|PaymentSchedule|g' \
  -e 's|\bHistorialSolicitudVacaciones\b|VacationRequestHistory|g' \
  -e 's|\bConfiguracionVacaciones\b|VacationConfiguration|g' \
  -e 's|\bPeriodoVacacional\b|VacationPeriod|g' \
  -e 's|\bSolicitudVacaciones\b|VacationRequest|g' \
  -e 's|\bGoceVacaciones\b|VacationGrant|g' \
  -e 's|\bEmpleado\b|Employee|g' \
  -e 's|\bUsuario\b|User|g' \
  -e 's|\bPermiso\b|Permission|g' \
  -e 's|\bRol\b|Role|g' \
  -e 's|\bArea\b|Department|g'
cd ../..
```

**ALERTA: posibles falsos positivos.** Identificadores como `Rol` y `Area` son cortos. Si algún archivo en `api/` tiene una variable o nombre que coincide pero no es un model, será afectado. Step 3 los detecta.

- [ ] **Step 3: Detectar regresiones en `api/` — buscar identificadores sospechosos**

```bash
cd D:/VYNTIA/apps/api
echo "=== Sospechosos: nombres de variables/funciones que pudieron renombrarse incorrectamente ==="
echo "--- Posible 'Role' en strings de UI/labels (no debería romper sino solo cambiar etiquetas) ---"
grep -rEn "\bRole\b" api --include="*.py" | grep -v "__pycache__\|import.*Role\|from.*Role\|: Role\|Role\.\|class.*Role\|isinstance.*Role" | head -10
echo ""
echo "--- Posible 'Department' en strings ---"
grep -rEn "\"Department\"|'Department'" api --include="*.py" | grep -v "__pycache__" | head -10
cd ../..
```

Si aparecen matches que parecen erróneos (ej: un label de UI que decía `"Area"` y ahora dice `"Department"`), revisar manualmente y revertir solo esos.

Nota: **Strings de UI en español SE PRESERVAN per spec § 3.5 regla 6.** Pero el sed con `\b` solo matchea palabras exactas — texto como `"Área de trabajo"` o `"el rol del empleado"` no se ve afectado (palabras en minúscula con tildes no matchean). El riesgo real es texto literal `"Area"` o `"Rol"` capitalizado en UI, que es raro.

- [ ] **Step 4: Verificación final — 0 stale ES en api/v1/**

```bash
cd D:/VYNTIA/apps/api
echo "=== Stale ES en imports/code de api/ ==="
grep -rEn "(from |import )(.*\b(Empleado|Usuario|Rol|Permiso|Area|ContratosAdendas|DatosLaborales|DocumentosDigitales|PlantillaDocumento|OnboardingEmpleado|HistorialUbicaciones|ConfiguracionEmpresa|PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago|SolicitudVacaciones|GoceVacaciones|ConfiguracionVacaciones|HistorialSolicitudVacaciones|PeriodoVacacional|DatosFamiliares|DatosAcademicos|CursosCertificaciones|Modulos|ModuloPermiso|RolPermisos|UsuarioRoles)\b)" api --include="*.py" | grep -v "__pycache__" || echo "OK: cero"
cd ../..
```

Expected: `OK: cero`.

---

## Task 14: Update consumer imports en `apps/api/tests/`

**Files (~9 test files):**
- `tests/test_area_model.py`, `test_auth_api.py`, `test_auth_system_integration.py`, `test_change_password.py`, `test_contratos_integration.py`, `test_documentos_digitales_onboarding.py`, `test_documentos_model.py`, `test_empleado_update_v2.py`, `test_login_api.py`, `test_login_authentication.py`, `test_onboarding_api.py`, `test_onboarding_self_update.py`, `test_onboarding_service.py`, `test_pdf_generation.py`, `test_usuario_model.py`, `conftest.py`

- [ ] **Step 1: Snapshot pre-rename**

```bash
cd D:/VYNTIA/apps/api
echo "=== Test refs to ES classes (before sed) ==="
grep -rEcn "\b(Empleado|Usuario|Rol|Permiso|Area|ContratosAdendas|DatosLaborales|DocumentosDigitales|PlantillaDocumento|OnboardingEmpleado|HistorialUbicaciones|ConfiguracionEmpresa|PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago|SolicitudVacaciones|GoceVacaciones|ConfiguracionVacaciones|HistorialSolicitudVacaciones|PeriodoVacacional|DatosFamiliares|DatosAcademicos|CursosCertificaciones|Modulos|ModuloPermiso|RolPermisos|UsuarioRoles)\b" tests --include="*.py" | awk -F: '{s+=$2} END {print s}'
cd ../..
```

Expected: ~247.

- [ ] **Step 2: Bulk sed sobre `tests/`** (mismo orden que Task 13)

```bash
cd D:/VYNTIA/apps/api
find tests -type f -name "*.py" -not -path "*/__pycache__/*" -print0 | xargs -0 sed -i \
  -e 's|\bOnboardingEmpleado\b|OnboardingProcess|g' \
  -e 's|\bCursosCertificaciones\b|Certification|g' \
  -e 's|\bDatosFamiliares\b|FamilyMember|g' \
  -e 's|\bDatosAcademicos\b|AcademicRecord|g' \
  -e 's|\bUsuarioRoles\b|UserRole|g' \
  -e 's|\bRolPermisos\b|RolePermission|g' \
  -e 's|\bModuloPermiso\b|ModulePermission|g' \
  -e 's|\bModulos\b|Module|g' \
  -e 's|\bHistorialUbicaciones\b|LocationHistory|g' \
  -e 's|\bConfiguracionEmpresa\b|Company|g' \
  -e 's|\bContratosAdendas\b|Contract|g' \
  -e 's|\bDatosLaborales\b|EmploymentData|g' \
  -e 's|\bDocumentosDigitales\b|DigitalDocument|g' \
  -e 's|\bPlantillaDocumento\b|DocumentTemplate|g' \
  -e 's|\bConfiguracionRemuneracion\b|CompensationConfiguration|g' \
  -e 's|\bConfiguracionAfp\b|AfpConfiguration|g' \
  -e 's|\bConfiguracionUit\b|TaxParameter|g' \
  -e 's|\bPlanillaMensual\b|MonthlyPayroll|g' \
  -e 's|\bDetallePlanilla\b|PayrollDetail|g' \
  -e 's|\bConceptoPlanilla\b|PayrollConcept|g' \
  -e 's|\bDescuentoMasivo\b|MassDeduction|g' \
  -e 's|\bBoletaPago\b|PaySlip|g' \
  -e 's|\bCalendarioPago\b|PaymentSchedule|g' \
  -e 's|\bHistorialSolicitudVacaciones\b|VacationRequestHistory|g' \
  -e 's|\bConfiguracionVacaciones\b|VacationConfiguration|g' \
  -e 's|\bPeriodoVacacional\b|VacationPeriod|g' \
  -e 's|\bSolicitudVacaciones\b|VacationRequest|g' \
  -e 's|\bGoceVacaciones\b|VacationGrant|g' \
  -e 's|\bEmpleado\b|Employee|g' \
  -e 's|\bUsuario\b|User|g' \
  -e 's|\bPermiso\b|Permission|g' \
  -e 's|\bRol\b|Role|g' \
  -e 's|\bArea\b|Department|g'
cd ../..
```

- [ ] **Step 3: Verificar — 0 stale ES en tests/**

```bash
cd D:/VYNTIA/apps/api
grep -rEn "\b(Empleado|Usuario|Rol|Permiso|Area|ContratosAdendas|DatosLaborales|DocumentosDigitales|PlantillaDocumento|OnboardingEmpleado|HistorialUbicaciones|ConfiguracionEmpresa|PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago|SolicitudVacaciones|GoceVacaciones|ConfiguracionVacaciones|HistorialSolicitudVacaciones|PeriodoVacacional|DatosFamiliares|DatosAcademicos|CursosCertificaciones|Modulos|ModuloPermiso|RolPermisos|UsuarioRoles)\b" tests --include="*.py" | grep -v "__pycache__" || echo "OK: cero"
cd ../..
```

Expected: `OK: cero` o solo matches en strings de fixtures (datos de prueba con valores en español, ej `"empleado@example.com"`) — esos son aceptables.

**Si aparecen matches en docstrings o comentarios:** dejarlos. Solo importan los identifiers ejecutables.

---

## Task 15: Update legacy `app_rrhh/` imports + `apps/<name>/services/` cross-references

**Por qué:** Los archivos legacy en `app_rrhh/` (filters, managers, validators, services, urls, views, serializers, management commands) y los services dentro de `apps/<name>/services/` aún referencian las clases en español.

**Files (~25 files):**
- `apps/api/app_rrhh/{filters,managers,managers.py,menu_service,permission_service,serializers,serializers_optimized,services.py,tests.py,urls,validators,views,models.py}.py`
- `apps/api/app_rrhh/management/commands/{audit_rbac,seed_menu,seed_plantillas_default,seed_remuneraciones_config,setup_roles_permisos}.py`
- `apps/api/app_rrhh/managers/{contratos_manager,usuario_manager}.py`
- `apps/api/app_rrhh/services/empleado_report_service.py`
- `apps/api/apps/core/{decorators,middleware,permissions}.py` (cross-app consumers de `identity.User`)

- [ ] **Step 1: Bulk sed sobre `app_rrhh/` y `apps/core/`**

```bash
cd D:/VYNTIA/apps/api
find app_rrhh apps/core -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -not -path "*/fixtures/*" -print0 | xargs -0 sed -i \
  -e 's|\bOnboardingEmpleado\b|OnboardingProcess|g' \
  -e 's|\bCursosCertificaciones\b|Certification|g' \
  -e 's|\bDatosFamiliares\b|FamilyMember|g' \
  -e 's|\bDatosAcademicos\b|AcademicRecord|g' \
  -e 's|\bUsuarioRoles\b|UserRole|g' \
  -e 's|\bRolPermisos\b|RolePermission|g' \
  -e 's|\bModuloPermiso\b|ModulePermission|g' \
  -e 's|\bModulos\b|Module|g' \
  -e 's|\bHistorialUbicaciones\b|LocationHistory|g' \
  -e 's|\bConfiguracionEmpresa\b|Company|g' \
  -e 's|\bContratosAdendas\b|Contract|g' \
  -e 's|\bDatosLaborales\b|EmploymentData|g' \
  -e 's|\bDocumentosDigitales\b|DigitalDocument|g' \
  -e 's|\bPlantillaDocumento\b|DocumentTemplate|g' \
  -e 's|\bConfiguracionRemuneracion\b|CompensationConfiguration|g' \
  -e 's|\bConfiguracionAfp\b|AfpConfiguration|g' \
  -e 's|\bConfiguracionUit\b|TaxParameter|g' \
  -e 's|\bPlanillaMensual\b|MonthlyPayroll|g' \
  -e 's|\bDetallePlanilla\b|PayrollDetail|g' \
  -e 's|\bConceptoPlanilla\b|PayrollConcept|g' \
  -e 's|\bDescuentoMasivo\b|MassDeduction|g' \
  -e 's|\bBoletaPago\b|PaySlip|g' \
  -e 's|\bCalendarioPago\b|PaymentSchedule|g' \
  -e 's|\bHistorialSolicitudVacaciones\b|VacationRequestHistory|g' \
  -e 's|\bConfiguracionVacaciones\b|VacationConfiguration|g' \
  -e 's|\bPeriodoVacacional\b|VacationPeriod|g' \
  -e 's|\bSolicitudVacaciones\b|VacationRequest|g' \
  -e 's|\bGoceVacaciones\b|VacationGrant|g' \
  -e 's|\bEmpleado\b|Employee|g' \
  -e 's|\bUsuario\b|User|g' \
  -e 's|\bPermiso\b|Permission|g' \
  -e 's|\bRol\b|Role|g' \
  -e 's|\bArea\b|Department|g'
cd ../..
```

- [ ] **Step 2: Defensive — `Roles` plural en `app_rrhh/constants.py` debe preservarse**

`apps/api/app_rrhh/constants.py` tiene `class Roles:` con strings legibles para el RBAC. El sed con `\bRol\b` (word-boundary) NO matchea `Roles` (porque `s` es word char). Verificar:

```bash
grep -n "class Roles\|EMPLEADO\|JEFE_AREA" apps/api/app_rrhh/constants.py
```

Expected: `class Roles:` intacto (NO debería ser `class Role:` después del sed). Las strings literales `"Empleado"`, `"Jefe de Area"` también deben preservarse — son labels en español, no clases. Si el sed las cambió, **revertir esos string literals** manualmente:

```bash
grep -n "\"Employee\"\|\"Jefe de Department\"" apps/api/app_rrhh/constants.py
```

Si los matches existen (sed sí les pegó porque están como tokens completos `Empleado`/`Area`), usar Edit tool para revertir esos VALORES (no class refs):
- `"Employee"` → `"Empleado"` (label de UI español)
- `"Jefe de Department"` → `"Jefe de Area"` (label de UI español)

**Por qué:** Spec § 3.5 regla 6 — strings UI en español, código Python en inglés. Esos son strings de label, no class references.

- [ ] **Step 3: Verificación general en `app_rrhh/` y `apps/core/`**

```bash
cd D:/VYNTIA/apps/api
echo "=== Stale ES class refs en app_rrhh/ ==="
grep -rEn "\b(Empleado|Usuario|Rol|Permiso|Area|ContratosAdendas|DatosLaborales|DocumentosDigitales|PlantillaDocumento|OnboardingEmpleado|HistorialUbicaciones|ConfiguracionEmpresa|PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago|SolicitudVacaciones|GoceVacaciones|ConfiguracionVacaciones|HistorialSolicitudVacaciones|PeriodoVacacional|DatosFamiliares|DatosAcademicos|CursosCertificaciones|Modulos|ModuloPermiso|RolPermisos|UsuarioRoles)\b" app_rrhh apps/core --include="*.py" | grep -v "__pycache__\|fixtures\|migrations" | grep -vE '("[^"]*"|'"'"'[^'"'"']*'"'"').*Empleado|.*"Jefe de' || echo "OK: cero"
cd ../..
```

**Acceptable matches:** strings literales en español preservados intencionalmente (constantes RBAC, mensajes de error UI, etc.). Estos NO deben sed-revertirse — los identifiers Python ejecutables sí.

Si el grep retorna **identifiers code-level** (no strings literales), revisar archivo a archivo con Edit tool.

---

## Task 16: Update `AUTH_USER_MODEL` y app docstrings

- [ ] **Step 1: AUTH_USER_MODEL setting**

Use Edit tool en `apps/api/vyntia/settings/base.py`:
- old_string: `AUTH_USER_MODEL = "identity.Usuario"`
- new_string: `AUTH_USER_MODEL = "identity.User"`

Verificar:
```bash
grep "AUTH_USER_MODEL" apps/api/vyntia/settings/base.py
```

Expected: `AUTH_USER_MODEL = "identity.User"`.

- [ ] **Step 2: `apps.identity.apps.IdentityConfig` docstring**

```bash
grep -n "Usuario" apps/api/apps/identity/apps.py
```

Si aparece, Edit tool para reemplazar `Usuario` → `User` en docstring/comments.

- [ ] **Step 3: Confirmar sed previo no rompió comentarios docstring**

```bash
cd D:/VYNTIA/apps/api
grep -rEn "(Usuario|Empleado|Rol|Permiso|Area|ContratosAdendas)" apps --include="*.py" | grep -v "__pycache__\|migrations" | head -20
cd ../..
```

Si hay matches, son comentarios o docstrings (no código). Aceptables — no rompen el código. Pero si quieres limpieza total, Edit tool manual file-by-file.

---

## Task 17: NUCLEAR DB regenerate

**Patrón validado en L3.2-L3.9.** Backup en `/tmp/bd_vyntia_pre_L3.10.1.dump`.

- [ ] **Step 1: Drop bd_vyntia (kill procs first)**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "DROP DATABASE IF EXISTS bd_vyntia;" 2>&1
```

- [ ] **Step 2: Eliminar migration files existentes**

```bash
cd D:/VYNTIA/apps/api
git rm apps/identity/migrations/0001_initial.py 2>&1 | tail -2
git rm apps/organization/migrations/0001_initial.py 2>&1 | tail -2
git rm apps/employees/migrations/0001_initial.py 2>&1 | tail -2 || echo "no 0001 employees"
git rm apps/employees/migrations/0002_initial.py 2>&1 | tail -2 || echo "no 0002 employees"
git rm apps/contracts/migrations/0001_initial.py 2>&1 | tail -2
git rm apps/contracts/migrations/0002_initial.py 2>&1 | tail -2 || echo "no 0002 contracts"
git rm apps/documents/migrations/0001_initial.py 2>&1 | tail -2
git rm apps/documents/migrations/0002_initial.py 2>&1 | tail -2 || echo "no 0002 documents"
git rm apps/payroll/migrations/0001_initial.py 2>&1 | tail -2
git rm apps/time_off/migrations/0001_initial.py 2>&1 | tail -2
git rm apps/onboarding/migrations/0001_initial.py 2>&1 | tail -2
cd ../..
```

- [ ] **Step 3: Recrear bd_vyntia (LR12 — antes de makemigrations)**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "CREATE DATABASE bd_vyntia WITH ENCODING 'UTF8' TEMPLATE template0;" 2>&1
```

Expected: `CREATE DATABASE`.

- [ ] **Step 4: Generar fresh migrations**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py makemigrations --settings=vyntia.settings.development 2>&1 | tail -40
cd ../..
```

Expected: cada app de dominio genera migrations con clases inglesas (`name='User'`, `name='Employee'`, `name='Department'`, etc.) y `db_table` en español preservado.

Verificar nombres de clases en migrations generadas:
```bash
cd D:/VYNTIA/apps/api
echo "=== identity 0001 ==="
grep -E "name='" apps/identity/migrations/0001_initial.py | head -10
echo ""
echo "=== employees 0001 (expected: Employee, FamilyMember, AcademicRecord, Certification) ==="
grep -E "name='" apps/employees/migrations/0001_initial.py | head -10
echo ""
echo "=== organization 0001 (expected: Department, LocationHistory, Company) ==="
grep -E "name='" apps/organization/migrations/0001_initial.py | head -10
echo ""
echo "=== db_table en migrations (deben ser ES) ==="
grep -h "db_table" apps/*/migrations/0001_initial.py | sort | head -10
cd ../..
```

Expected: clases en inglés, `db_table` en español.

- [ ] **Step 5: Aplicar migraciones**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -25
cd ../..
```

Expected: secuencia `Applying X.0001_initial... OK` para todos los apps. Sin errores.

- [ ] **Step 6: Verificación física de tablas (mismas que pre-L3.10.1)**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;" 2>&1 | head -50
```

Expected: tablas con nombres ES — `area`, `boleta_pago`, `calendario_pago`, `concepto_planilla`, `configuracion_afp`, `configuracion_empresa`, `configuracion_remuneracion`, `configuracion_uit`, `configuracion_vacaciones`, `contratos_adendas`, `cursos_certificaciones`, `datos_academicos`, `datos_familiares`, `datos_laborales`, `descuento_masivo`, `detalle_planilla`, `documentos_digitales`, `app_rrhh_plantilla_documento`, `empleado`, `goces_vacaciones`, `historial_solicitudes_vacaciones`, `historial_ubicaciones`, `modulo_permisos`, `modulos`, `onboarding_empleado`, `periodos_vacacionales`, `permiso`, `planilla_mensual`, `rol`, `rol_permisos`, `solicitudes_vacaciones`, `usuario_roles`, `usuarios`. **Mismas tablas que pre-L3.10.1.**

---

## Task 18: Re-seed

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py setup_roles_permisos --settings=vyntia.settings.development 2>&1 | tail -10
PGPASSWORD='Demenci4@' python manage.py seed_menu --settings=vyntia.settings.development 2>&1 | tail -10
cd ../..
```

Expected: ambos completan sin error.

Verificar:
```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'rol' AS t, COUNT(*) FROM rol UNION ALL SELECT 'permiso', COUNT(*) FROM permiso UNION ALL SELECT 'modulos', COUNT(*) FROM modulos UNION ALL SELECT 'empleado', COUNT(*) FROM empleado UNION ALL SELECT 'usuarios', COUNT(*) FROM usuarios;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0, empleado = 0, usuarios = 0.

---

## Task 19: Smoke tests

- [ ] **Step 1: Django check**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd ../..
```

Expected: `System check identified no issues (0 silenced).`

Si falla con `ImportError`/`AttributeError`, hay un import roto — revisar el archivo mencionado en el traceback con Edit tool.

- [ ] **Step 2: pytest baseline**

```bash
cd D:/VYNTIA/apps/api
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: `125 passed, 44 failed, 3 skipped`.

Si **passed < 125**: hay regresión — revisar tests fallidos y arreglar. Si passed sigue 125 pero **failed != 44**: investigar (posible que un nuevo error haya enmascarado un fail conocido o viceversa).

- [ ] **Step 3: runserver smoke**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l3101.log 2>&1 &
SERVER_PID=$!
sleep 8
curl -s -o /dev/null -w "HTTP %{http_code} /api/docs/\n" http://127.0.0.1:8000/api/docs/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/auth/login (expected 405 GET)\n" http://127.0.0.1:8000/api/v1/auth/login
kill $SERVER_PID 2>/dev/null
sleep 1
cd ../..
```

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

Expected: `HTTP 200 /api/docs/`. Si `/api/docs/` falla, schema generation roto — drf-spectacular probablemente falló al introspectar un serializer con un modelo renombrado.

- [ ] **Step 4: LR13 defensive — logger names hardcoded a `app_rrhh.X` con clases ES**

```bash
cd D:/VYNTIA/apps/api
echo "=== Stale logger names ==="
grep -rEn "logger\s*=\s*['\"]app_rrhh\.|getLogger\([^)]*['\"]app_rrhh\." --include="*.py" apps tests | grep -v "__pycache__\|migrations" || echo "OK: cero"
cd ../..
```

Expected: `OK: cero` (esto se resolvió en L3.6/L3.7).

- [ ] **Step 5: Cleanup greps finales — 0 stale ES anywhere**

```bash
cd D:/VYNTIA/apps/api
echo "=== Final cleanup: stale ES class identifiers en código ejecutable ==="
grep -rEn "\b(Empleado|Usuario|Rol|Permiso|Area|ContratosAdendas|DatosLaborales|DocumentosDigitales|PlantillaDocumento|OnboardingEmpleado|HistorialUbicaciones|ConfiguracionEmpresa|PlanillaMensual|DetallePlanilla|ConceptoPlanilla|ConfiguracionAfp|ConfiguracionRemuneracion|ConfiguracionUit|DescuentoMasivo|BoletaPago|CalendarioPago|SolicitudVacaciones|GoceVacaciones|ConfiguracionVacaciones|HistorialSolicitudVacaciones|PeriodoVacacional|DatosFamiliares|DatosAcademicos|CursosCertificaciones|Modulos|ModuloPermiso|RolPermisos|UsuarioRoles)\b" --include="*.py" \
  --exclude-dir=__pycache__ \
  --exclude-dir=migrations \
  --exclude-dir=fixtures \
  --exclude-dir=.venv \
  apps tests app_rrhh api | grep -vE '"[^"]*"\s*$|: *#|"""|'"'"'[^'"'"']*'"'"'$' || echo "OK: cero"
echo ""
echo "=== FK strings — 0 stale 'app_rrhh.X' (LR9) ==="
grep -rEn "['\"]app_rrhh\.[A-Z][a-zA-Z]+['\"]" --include="*.py" \
  --exclude-dir=__pycache__ \
  --exclude-dir=migrations \
  --exclude-dir=.venv \
  apps tests app_rrhh api || echo "OK: cero"
cd ../..
```

Expected: ambos `OK: cero`. Si quedan matches, son strings/comments (aceptable) o un identifier que necesita Edit manual.

---

## Task 20: Atomic commit

```bash
cd D:/VYNTIA
git status --short | head -50
git add apps/api/
git commit -m "chore(L3.10.1): rename 33 model classes ES→EN — fresh migrations after BD nuke + reseed"
```

Verificar:
```bash
git log --oneline vyntia/L3.10.1-rename-classes ^master
git status --short
```

Expected: 2 commits (`docs(L3.10.1)` + `chore(L3.10.1)`), `git status` empty.

---

## Task 21: Merge a master

- [ ] **Step 1: Confirmar autorización del usuario.**

**NO mergear sin autorización.**

- [ ] **Step 2: Merge `--no-ff`**

```bash
git checkout master
git merge --no-ff vyntia/L3.10.1-rename-classes -m "Merge L3.10.1: rename 33 model classes ES→EN (Empleado→Employee, Usuario→User, etc.)"
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

Update `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`:
- Modificar la fila L3.10 en la tabla Sub-PR Index para marcar el sub-split:
  - L3.10.1 ✅ merged `<sha>` 2026-04-XX
  - L3.10.2 ⏳ NEXT — field names rename
  - L3.10.3 ⏳ — splits con data migration
  - L3.10.4 ⏳ — frontend rename + URL paths
  - L3.11 ⏳ — depends on L3.10.4

Update `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- Status L3 sub-PR list: agregar L3.10.1 ✅ merged
- "Próximo paso" → generar plan L3.10.2 (field names rename)

Commit:
```bash
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.10.1): mark L3.10.1 merged, L3.10.2 (field rename) as next"
```

---

## Después de L3.10.1

**Próximo plan:** **L3.10.2** — field names rename (`nombres → first_name`, `apellido_paterno → last_name`, `creado_en → created_at`, `estado → status`, `activo → is_active`, `creado_por → created_by`, etc.) preservando `db_column` español.

L3.10.2 es estructuralmente similar a L3.10.1 (sed masivo) pero opera en la **dimensión de fields** dentro de cada modelo. Estimación ~25 tasks. Riesgo medio (mucho ruido pero patrón conocido). Después viene L3.10.3 (splits con data migration — riesgo crítico) y L3.10.4 (frontend).

---

## Notas para el ejecutor

- **Patrón NUCLEAR validado** — re-aplicar igual que L3.4–L3.9. El backup `/tmp/bd_vyntia_pre_L3.10.1.dump` existe por paranoia, pero la BD se regenera fresca.
- **Word-boundary `\b` no negociable** — clases cortas (`Rol`, `Area`) son peligrosas con sed substring. Usar `\bX\b` SIEMPRE.
- **Orden longest-match-first** — si no se aplica este orden, `Empleado → Employee` ejecutado antes que `OnboardingEmpleado → OnboardingProcess` produciría `OnboardingEmployee` (corrupto).
- **Strings UI en español SE PRESERVAN** — el sed con `\b` no toca palabras en minúscula, frases multi-palabra, ni texto con tildes/cedillas. Solo riesgo: literales como `"Empleado"`, `"Rol"`, `"Area"` capitalizados que sed sí matchea. Step 16 Task 15 verifica `app_rrhh/constants.py` específicamente; si encuentras otros, Edit manual para revertir solo esos string values.
- **`AUTH_USER_MODEL`** — es la única referencia hard-coded a `identity.Usuario`. Task 16 Step 1 lo cambia. Si no se cambia, todo falla porque Django no encuentra el modelo de usuario.
- **PGPASSWORD env var** explícito por known issue (Windows env con caracteres no-ASCII).
- **LR9-LR14** — todos los grep defensivos están incluidos. LR9 (stale `'app_rrhh.X'`) en Task 12 Step 4. LR10 (single + double quote) en Tasks 4-12. LR11 (relative imports `from .models`) implícito en sed que cubre `app_rrhh/`. LR12 (DB before makemigrations) en Task 17 Step 3. LR13 (logger strings) en Task 19 Step 4. LR14 (multi-line imports) inocuo aquí — el sed por identifier no requiere matchear el patrón de import; los matches simplemente reemplazan el identifier en cualquier contexto.
- **Si `manage.py check` falla post-Task 11** (después de los renames per-app pero antes del bulk cross-app), es esperado — los FK strings cross-app aún están en español. **No debugguear ahí**; continuar a Task 12 que arregla los FKs cross-app.
- **Si `manage.py check` falla post-Task 12** pero antes de Task 13–15, también esperado — los consumers en `api/`, `tests/`, `app_rrhh/` aún están en español. **Continuar a Tasks 13–15**.
- **Primer manage.py check exitoso debe ser después de Task 15** (todos los consumers actualizados). Si falla ahí, hay un identifier no-renombrado — usar el traceback para localizarlo.
- **drf-spectacular**: las 254 W001 deprecation warnings que veníamos arrastrando desde L2 deberían persistir igual o reducirse (los serializers consolidados ahora usan los mismos nombres entre apps — pero eso es L4 territorio).
