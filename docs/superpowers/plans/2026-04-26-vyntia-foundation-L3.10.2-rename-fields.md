# VYNTIA Foundation L3.10.2 — Rename Audit Fields + PKs + State Literals ES → EN Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Renombrar fields **genéricos de plataforma** (audit timestamps + audit FKs + state literales + PKs) de español a inglés. Domain vocabulary HR peruano (`nombres_empleado`, `apellido_paterno`, `tipo_documento`, `numero_cuspp`, `apellido_materno`, etc.) se PRESERVA en español per decisión de scope. Esquema físico de bd_vyntia se preserva via `db_column` español en cada field renombrado (excepto PKs, donde el cambio AutoField→UUIDField requiere column rename y type change).

**Architecture:** L3.10.2 es el segundo sub-PR de L3.10. Solo toca **identificadores Python de fields**: 9 distinct rename mappings (6 audit + 1 state + 1 boolean state + 1 PK pattern). 54 audit fields + 9 state literals + 31 PKs = **94 field declarations** modificadas en 22 archivos modelo. Más actualizaciones en serializers, views, filters, services, tests, legacy `app_rrhh/`. **NUCLEAR DB regen** (patrón validado L3.2-L3.10.1) — drop bd_vyntia + delete migrations + makemigrations fresh + reseed.

**Tech Stack:** Django 5.2, GNU sed con word-boundaries `\bX\b`, `db_column` para preservar physical schema, UUIDField para PKs.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.6 "Convención de fields"; § 3.5 regla 6 "Naming en inglés"; § 3.5 regla 7 "Términos legales peruanos preservados" (decisión extendida en L3.10.2: domain vocabulary HR también se preserva en español).

**Scope decision (Option B — sub-PR de L3.10):**
- L3.10.1 ✅ Class names rename (33 clases) — merged `7bccc348`
- **L3.10.2 (este plan)** — audit fields + PKs + state literales. **Domain vocabulary HR queda en español.**
- L3.10.3 ⏳ Model splits (Contract+ContractAmendment, VacationRequest+VacationBalance) con data migration
- L3.10.4 ⏳ Frontend rename + nuevas URL paths

**Pre-condiciones:**
- L3.10.1 mergeada a master (commit `7bccc348`)
- Django 5.2.13, las 8 apps de dominio operativas con clases inglesas
- pytest baseline: 125 passed, 44 failed, 3 skipped
- `bd_vyntia` provisionada con esquema actual (33 tablas con nombres ES)
- venv en `D:/VYNTIA/.venv/`

---

## Tabla canónica de renombres (Option B — audit + state + PKs only)

**ESTA ES LA FUENTE DE VERDAD.** Cualquier desviación requiere autorización antes de ejecutar.

### Audit fields (54 occurrences, 6 distinct mappings)

| Field ES | Field EN | `db_column` (preservado) | Ocurrencias | Notas |
|---|---|---|---|---|
| `fecha_creacion` | `created_at` | `'fecha_creacion'` | 19 | DateTimeField |
| `fecha_actualizacion` | `updated_at` | `'fecha_actualizacion'` | 22 | DateTimeField |
| `fecha_registro` | `created_at` | `'fecha_registro'` | 6 | DateTimeField (alias semantic — algunos modelos usan "fecha_registro" en lugar de "fecha_creacion"; rename target es el mismo: `created_at`) |
| `fecha_modificacion` | `updated_at` | `'fecha_modificacion'` | 1 | DateTimeField (alias) |
| `creado_por` | `created_by` | `'creado_por_id'` o `'creado_por'` (verificar pre-rename) | 5 | ForeignKey to User |
| `modificado_por` | `updated_by` | `'modificado_por_id'` o `'modificado_por'` | 1 | ForeignKey to User (alias for actualizado_por) |

**Decisión sobre alias:** `fecha_registro → created_at` y `fecha_modificacion → updated_at` se mapean al mismo nombre EN. Los modelos que tienen AMBOS `fecha_creacion` y `fecha_registro` no existen (verified pre-write). Si surgiera conflicto, manual fix.

**NO incluido como audit field** (queda en español — vocabulario domain):
- `validado_por`, `digitalizado_por`, `subido_por`, `cancelado_por`, `rechazado_por`, `rrhh_aprobador`, `usuario_accion`, `usuario_aprobacion`, `usuario_generacion`, `usuario_carga`, `usuario_programacion`, `asignado_por_usuario` — son audit-like pero específicos al dominio (validar documento, digitalizar, subir, etc.)
- `fecha_inicio`, `fecha_fin`, `fecha_vencimiento`, `fecha_validacion`, `fecha_generacion`, `fecha_asignacion` — domain timestamps específicas (NO son creation/update genéricas)
- `fecha_nacimiento`, `fecha_ingreso`, `fecha_cese` — domain HR timestamps

### State literals (9 occurrences, 2 mappings)

| Field ES | Field EN | `db_column` (preservado) | Ocurrencias | Notas |
|---|---|---|---|---|
| `estado` | `status` | `'estado'` | 8 | CharField (solo cuando es exactamente `estado`, no `estado_X`) |
| `activo` | `is_active` | `'activo'` | 1 | BooleanField (solo cuando es exactamente `activo`, no `activo_X` ni similar) |

**NO incluido (queda en español — vocabulario domain):**
- `estado_empleado`, `estado_civil`, `estado_documento`, `estado_solicitud`, `estado_modulo`, `estado_rol`, `estado_usuario`, `estado_area`, `estado_datos`, `estado_planilla`, `estado_calendario`, `estado_concepto`, `estado_descuento`, `estado_seguro`, `vigencia_estado_seguro` — todos domain-specific
- `vigente`, `vigencia`, `es_activo` (computed property) — quedan
- `activo_X` (no existen como fields, pero defensive)

### PKs (31 fields → `id` UUID, type change)

Todos los modelos tienen PK custom (e.g., `empleado_id`, `usuario_id`). Se renombran a `id` y se cambia el tipo de `AutoField` a `UUIDField(default=uuid.uuid4)`. **Cambio de tipo INT → UUID** — frontend romperá hasta L3.10.4 que actualiza tipos TS.

| Modelo | PK ES | PK EN | Type ES | Type EN |
|---|---|---|---|---|
| identity.User | `usuario_id` | `id` | AutoField | UUIDField |
| identity.Role | `rol_id` | `id` | AutoField | UUIDField |
| identity.Permission | `permiso_id` | `id` | AutoField | UUIDField |
| identity.Module | `modulo_id` | `id` | AutoField | UUIDField |
| identity.RolePermission | `rol_permiso_id` | `id` | AutoField | UUIDField |
| identity.ModulePermission | `modulo_permiso_id` | `id` | AutoField | UUIDField |
| identity.UserRole | `usuario_rol_id` | `id` | AutoField | UUIDField |
| organization.Department | `area_id` | `id` | AutoField | UUIDField |
| employees.Employee | `empleado_id` | `id` | AutoField | UUIDField |
| employees.FamilyMember | `familiar_id` | `id` | AutoField | UUIDField |
| employees.AcademicRecord | `academico_id` | `id` | AutoField | UUIDField |
| employees.Certification | `curso_id` | `id` | AutoField | UUIDField |
| contracts.Contract | `contrato_id` | `id` | AutoField | UUIDField |
| contracts.EmploymentData | `dato_laboral_id` | `id` | AutoField | UUIDField |
| documents.DigitalDocument | `documento_id` | `id` | AutoField | UUIDField |
| documents.DocumentTemplate | `plantilla_id` | `id` | AutoField | UUIDField |
| payroll.AfpConfiguration | `afp_config_id` | `id` | AutoField | UUIDField |
| payroll.CompensationConfiguration | `configuracion_id` | `id` | AutoField | UUIDField |
| payroll.MonthlyPayroll | `planilla_id` | `id` | AutoField | UUIDField |
| payroll.PayrollDetail | `detalle_id` | `id` | AutoField | UUIDField |
| payroll.PayrollConcept | `concepto_planilla_id` | `id` | AutoField | UUIDField |
| payroll.MassDeduction | `descuento_masivo_id` | `id` | AutoField | UUIDField |
| payroll.PaySlip | `boleta_id` | `id` | AutoField | UUIDField |
| payroll.PaymentSchedule | `calendario_id` | `id` | AutoField | UUIDField |
| payroll.TaxParameter | `configuracion_uit_id` | `id` | AutoField | UUIDField |
| time_off.VacationConfiguration | `configuracion_id` | `id` | AutoField | UUIDField |
| time_off.VacationPeriod | `periodo_id` | `id` | AutoField | UUIDField |
| time_off.VacationRequest | `solicitud_id` | `id` | AutoField | UUIDField |
| time_off.VacationGrant | `goce_id` | `id` | AutoField | UUIDField |
| time_off.VacationRequestHistory | `historial_id` | `id` | AutoField | UUIDField |
| onboarding.OnboardingProcess | `onboarding_id` | `id` | AutoField | UUIDField |

**`db_column` decision:** PKs DON'T preserve `db_column` (no `db_column='empleado_id'`). Reason: AutoField→UUIDField is a column type change anyway (int→uuid), so renaming the column to `id` is consistent. Physical column post-rename: `id` (uuid). FK columns referencing this PK auto-stay named `<field>_id` (e.g., `empleado_id` in `contratos_adendas` table) but type changes int→uuid.

**Frontend impact (deferred to L3.10.4):**
- 366 frontend references to PK fields (`empleado_id: number`, etc.) will need:
  - Field name change from `empleado_id` to `id` in TS interfaces
  - Type change from `number` to `string` (UUID)
  - URL path updates (`/empleados/123/` → `/empleados/<uuid>/`)
- Tests in `apps/web/` will break until L3.10.4

**Serializer strategy:**
- Update all serializer `fields = [...]` lists to use new field names (`'id'` instead of `'empleado_id'`, `'created_at'` instead of `'fecha_creacion'`)
- API JSON keys change from Spanish to English
- This BREAKS frontend until L3.10.4 lands
- **Accepted tradeoff** per Option B scope decision (no source= compat shims; clean break)
- Backend pytest baseline 125/44/3 must still hold (tests use ORM not API directly mostly)

---

## Orden de aplicación (longest-match-first per category)

```text
# Audit FK fields first (longer than audit timestamps)
modificado_por → updated_by
creado_por → created_by

# Audit timestamps
fecha_actualizacion → updated_at
fecha_modificacion → updated_at
fecha_creacion → created_at
fecha_registro → created_at

# State literals (very short — must use \b strict word-boundary)
estado → status
activo → is_active

# PK rename (last, since it generates default `id` field on every model)
# Per-app loop: for each model, replace its PK field name + type
```

**Reglas duras del sed:**
- Word-boundary `\bX\b` mandatorio. `\bestado\b` NO matchea `estado_empleado` (no boundary between `o` and `_`).
- PKs se renombran via Edit tool (no sed) para cambiar TIPO — `models.AutoField(primary_key=True)` → `models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`. Sed no puede inferir el cambio de tipo.
- Audit fields preservan `db_column` Spanish via Edit tool — el sed no agrega `db_column=` automáticamente. Por eso este plan usa **Edit tool por archivo modelo** (Tasks 4-11), no sed bulk.
- State literals preservan `db_column` Spanish via Edit tool, mismo argumento.

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Edit | `apps/api/apps/identity/models/*.py` (3 files) | rename fields + add db_column + add UUID PK |
| Edit | `apps/api/apps/organization/models/*.py` (3 files) | idem |
| Edit | `apps/api/apps/employees/models/*.py` (4 files) | idem |
| Edit | `apps/api/apps/contracts/models/*.py` (2 files) | idem |
| Edit | `apps/api/apps/documents/models/*.py` (2 files) | idem |
| Edit | `apps/api/apps/payroll/models/*.py` (2 files, 9 PKs) | idem |
| Edit | `apps/api/apps/time_off/models/vacation.py` (1 file, 5 PKs) | idem |
| Edit | `apps/api/apps/onboarding/models/onboarding_process.py` (1 file, 1 PK) | idem |
| Modify (sed) | `apps/api/api/v1/**/*.py` (~20 files) | rename field references in serializers, views, filters |
| Modify (sed) | `apps/api/tests/**/*.py` (~16 files) | rename field refs in tests |
| Modify (sed) | `apps/api/app_rrhh/**/*.py` (~20 files) | rename field refs in legacy code + management commands |
| Modify (sed) | `apps/api/apps/<name>/services/**/*.py` (~10 files) | rename field refs in services |
| Modify (sed) | `apps/api/scripts/*.py` (~7 files) | rename field refs in standalone scripts |
| Delete | `apps/api/apps/<name>/migrations/0001_initial.py` (+ 0002 if exists) | regenerated via NUCLEAR |

**NO se toca en L3.10.2:**
- Domain vocabulary fields (`nombres_empleado`, `apellido_paterno`, `tipo_documento`, etc.) — quedan en español
- Domain audit-like fields (`validado_por`, `digitalizado_por`, etc.) — quedan en español
- Domain state fields (`estado_empleado`, `estado_civil`, etc.) — quedan en español
- Domain timestamps (`fecha_inicio`, `fecha_fin`, `fecha_nacimiento`, `fecha_ingreso`, etc.) — quedan en español
- FK field names (`empleado`, `usuario`, `area`, etc.) — quedan; cambian solo en L3.10.3 si parte del split, o en L3.10.4 si el frontend lo requiere
- `db_table` (preservado de L3.10.1)
- `apps/web/` (frontend rename = L3.10.4)

**Lecciones aplicadas:**
- **LR9-LR14** ya resueltas en L3.x previos.
- **LR15 (relative imports)** — N/A en L3.10.2 (no hay file renames).
- **LR16 (reverse-accessor)** — N/A en L3.10.2 (no hay class renames).
- **LR17 nueva (a documentar):** serializer `fields = [...]` lists hardcodean field names; rename de model field requiere actualizar TODAS las listas. Mitigación: bulk sed sobre serializers en Task 13.
- **LR18 nueva (a documentar):** ORM filter/order_by con field names hardcoded (`filter(fecha_creacion__gte=...)`, `order_by('estado')`) son string literals que el sed con `\b` SÍ matchea (porque están como kwargs). Defensive grep en Task 14.

---

## Definition of Done

- [ ] 54 audit fields renombrados (6 distinct mappings) con `db_column` ES preservado
- [ ] 9 state literal fields renombrados (`estado`, `activo`) con `db_column` ES preservado
- [ ] 31 PKs renombrados a `id`, tipo cambiado a UUIDField (sin `db_column` — column también renombrada)
- [ ] Serializer `fields = [...]` lists actualizadas en ~15 serializer classes
- [ ] ORM queries con field references actualizadas (filter, order_by, values, search_fields)
- [ ] Tests actualizados (~157 references estimated)
- [ ] Migrations regeneradas vía NUCLEAR DB
- [ ] `bd_vyntia` recreada y reseeded
- [ ] **Tablas físicas con audit columns ES preservadas** (`fecha_creacion`, `fecha_actualizacion`, `creado_por`, `estado`, `activo`)
- [ ] **Tablas físicas con PK columns EN** (`id` uuid en lugar de `<modelo>_id` int)
- [ ] **FK columns mantienen nombres ES** (`empleado_id`, `usuario_id`) pero TIPO cambia int → uuid
- [ ] `python manage.py check` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado — algunos tests pueden necesitar pequeños ajustes manuales)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.10.2-rename-fields` mergeada a master con `--no-ff`
- [ ] Roadmap + memory MEMORY.md/active_subproject.md actualizados

---

## Task 1: Pre-flight — branch, baseline, backup, snapshot

- [ ] **Step 1: Confirmar pwd, master limpio post-L3.10.1, HEAD post-merge**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -5
```

Expected: HEAD reciente con `170a5282 docs(L3.10.1): mark L3.10.1 merged...`. `git status` empty.

- [ ] **Step 2: Activar venv y confirmar Django**

```bash
source D:/VYNTIA/.venv/Scripts/activate
python -c "import django; print(django.get_version())"
```

Expected: `5.2.13`.

- [ ] **Step 3: Confirmar baseline pytest**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `125 passed, 44 failed, 3 skipped`. Si difiere, **detener**.

- [ ] **Step 4: Backup bd_vyntia**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.10.2.dump 2>&1 | tail -3
ls -lh /tmp/bd_vyntia_pre_L3.10.2.dump
```

Expected: dump file exists.

- [ ] **Step 5: Snapshot pre-rename**

```bash
cd D:/VYNTIA/apps/api
echo "=== Audit fields count (expected: 54) ==="
grep -hE "^\s+(fecha_creacion|fecha_actualizacion|fecha_registro|fecha_modificacion|creado_por|modificado_por)\s*=" apps/*/models/*.py | wc -l
echo "=== State literals 'estado' (expected: 8) ==="
grep -hnE "^\s+estado\s*=" apps/*/models/*.py | wc -l
echo "=== State literals 'activo' (expected: 1) ==="
grep -hnE "^\s+activo\s*=" apps/*/models/*.py | wc -l
echo "=== PKs (expected: 31) ==="
grep -hE "^\s+[a-z_]+_id\s*=\s*models\.AutoField\(primary_key=True" apps/*/models/*.py | wc -l
cd D:/VYNTIA
```

Expected: 54, 8, 1, 31.

- [ ] **Step 6: Crear branch L3.10.2**

```bash
git checkout -b vyntia/L3.10.2-rename-fields
git status --short
```

---

## Task 2: Comitear el plan en la branch

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-26-vyntia-foundation-L3.10.2-rename-fields.md
git commit -m "docs(L3.10.2): add audit fields + PKs + state literals rename plan (Option B scope)"
```

---

## Task 3: Update spec § 3.6 con decisión de scope

El spec § 3.6 lista patrones generales pero no documentaba la decisión de qué fields se renombran y cuáles no. Esta task agrega clarificación.

Read `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.6. Use Edit tool para agregar después de la tabla un párrafo:

```markdown
### 3.6.1 Scope decision (L3.10.2 Option B)

L3.10.2 aplica § 3.6 SOLO a fields **genéricos de plataforma**:
- Audit timestamps (`fecha_creacion`, `fecha_actualizacion`, `fecha_registro`, `fecha_modificacion`)
- Audit FKs (`creado_por`, `modificado_por`)
- State literales (`estado`, `activo`)
- PKs (`<modelo>_id` → `id` UUID)

**Domain vocabulary HR peruano se PRESERVA en español** (`nombres_empleado`, `apellido_paterno`, `tipo_documento`, `numero_cuspp`, `estado_empleado`, `estado_civil`, `vigencia_estado_seguro`, etc.). Esta es una extensión natural de la regla 7 ("términos legales peruanos preservados") aplicada al vocabulario de dominio HR. Domain audit-like fields (`validado_por`, `digitalizado_por`, `subido_por`) también quedan en español.

Frontend rename de los fields renombrados se hace en L3.10.4. Entre L3.10.2 merge y L3.10.4 merge, el frontend romperá en uses de `empleado_id`, `fecha_creacion`, etc. — accepted tradeoff (solo dev, no production users).
```

Commit:
```bash
cd D:/VYNTIA
git add docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md
git commit -m "docs(L3.10.2): clarify spec § 3.6 scope — domain HR vocabulary stays Spanish"
```

---

## Task 4: Rename fields in `apps/identity/` (3 model files, 7 PKs)

**Files:** `apps/api/apps/identity/models/{user,roles,rbac}.py`

### Step 1: Read each model file to inventory fields to rename

```bash
cd D:/VYNTIA/apps/api
for f in apps/identity/models/{user,roles,rbac}.py; do
  echo "=== $f ==="
  grep -nE "^\s+(usuario_id|rol_id|permiso_id|modulo_id|rol_permiso_id|modulo_permiso_id|usuario_rol_id|fecha_creacion|fecha_actualizacion|fecha_registro|creado_por|modificado_por|estado|activo)\s*=" $f
  echo ""
done
cd D:/VYNTIA
```

This shows per-file the fields to rename.

### Step 2: Edit each file — apply renames

For **each** of the 3 files (`user.py`, `roles.py`, `rbac.py`), use the Edit tool with these patterns:

**Pattern A: PK rename**

For each occurrence of `<name>_id = models.AutoField(primary_key=True)`:
- Old:
  ```python
  usuario_id = models.AutoField(primary_key=True)
  ```
- New:
  ```python
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  ```

Add `import uuid` at top of file if not present.

**Pattern B: Audit timestamp rename (preserve column name)**

- Old:
  ```python
  fecha_creacion = models.DateTimeField(auto_now_add=True)
  ```
- New:
  ```python
  created_at = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
  ```

Same for `fecha_actualizacion → updated_at` (db_column='fecha_actualizacion'), `fecha_registro → created_at` (db_column='fecha_registro'), `fecha_modificacion → updated_at` (db_column='fecha_modificacion').

**Pattern C: Audit FK rename (preserve column name)**

- Old:
  ```python
  creado_por = models.ForeignKey(
      'identity.User',
      on_delete=models.SET_NULL,
      null=True, blank=True,
      related_name='usuarios_creados',
  )
  ```
- New:
  ```python
  created_by = models.ForeignKey(
      'identity.User',
      on_delete=models.SET_NULL,
      null=True, blank=True,
      related_name='usuarios_creados',
      db_column='creado_por_id',  # or 'creado_por' — verify pre-edit by reading current file
  )
  ```

**IMPORTANT:** Before editing, run `grep -B2 -A6 "creado_por\|modificado_por" <file>` to see the EXACT structure of each FK declaration (some have `related_name`, some don't, some are double-quoted strings, etc.). Preserve all original kwargs.

For `creado_por` and `modificado_por`: Django auto-generates the FK column as `creado_por_id` (field name + `_id`). After rename to `created_by`, the auto column would be `created_by_id`. To preserve `creado_por_id`, use `db_column='creado_por_id'`.

**Pattern D: State literal rename (preserve column name)**

- Old:
  ```python
  estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="activo")
  ```
- New:
  ```python
  status = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="activo", db_column='estado')
  ```

For `activo`:
- Old:
  ```python
  activo = models.BooleanField(default=True)
  ```
- New:
  ```python
  is_active = models.BooleanField(default=True, db_column='activo')
  ```

### Step 3: Verify per file

```bash
cd D:/VYNTIA/apps/api
for f in apps/identity/models/{user,roles,rbac}.py; do
  echo "=== $f ==="
  echo "PKs (expected 1 per file):"
  grep -nE "^\s+id\s*=\s*models\.UUIDField\(primary_key=True" $f
  echo "Audit fields renamed:"
  grep -nE "^\s+(created_at|updated_at|created_by|updated_by)\s*=" $f
  echo "State renamed:"
  grep -nE "^\s+(status|is_active)\s*=" $f
  echo "Stale ES (should be 0):"
  grep -nE "^\s+(usuario_id|rol_id|permiso_id|modulo_id|rol_permiso_id|modulo_permiso_id|usuario_rol_id|fecha_creacion|fecha_actualizacion|fecha_registro|fecha_modificacion|creado_por|modificado_por|^\s+estado\s*=|^\s+activo\s*=)" $f || echo "OK: cero"
  echo ""
done
cd D:/VYNTIA
```

Expected: each file shows 1 UUID PK, the audit/state fields renamed, 0 stale ES.

### Step 4: Smoke import

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development'); import django; django.setup(); from apps.identity.models import User, Role, Permission, Module, ModulePermission, RolePermission, UserRole; print('OK')"
cd D:/VYNTIA
```

Expected: `OK`. Si error, leer traceback (probablemente `import uuid` faltante o sintaxis Edit incorrecta).

---

## Task 5: Rename fields in `apps/organization/` (3 model files, 1 PK)

**Files:** `apps/api/apps/organization/models/{department,location_history,company}.py`

Same pattern as Task 4. Models in this app:
- `Department.area_id` → `id` UUID
- `LocationHistory.<pk>_id` — verify pre-edit
- `Company.<pk>_id` — verify pre-edit
- Plus audit fields, state literals where present

### Step 1: Inventory

```bash
cd D:/VYNTIA/apps/api
for f in apps/organization/models/*.py; do
  echo "=== $f ==="
  grep -nE "^\s+([a-z_]+_id|fecha_creacion|fecha_actualizacion|fecha_registro|fecha_modificacion|creado_por|modificado_por|^\s+estado\s*=|^\s+activo\s*=)" $f
  echo ""
done
cd D:/VYNTIA
```

### Step 2-4: Same as Task 4 (Edit per file, verify, smoke import)

```bash
python -c "...; from apps.organization.models import Department, LocationHistory, Company; print('OK')"
```

---

## Task 6: Rename fields in `apps/employees/` (4 model files, 4 PKs)

**Files:** `apps/api/apps/employees/models/{employee,family_member,academic_record,certification}.py`

PKs:
- `Employee.empleado_id` → `id` UUID
- `FamilyMember.familiar_id` → `id` UUID
- `AcademicRecord.academico_id` → `id` UUID
- `Certification.curso_id` → `id` UUID

Same pattern as Task 4. Inventory + Edit + Verify + Smoke import.

```bash
python -c "...; from apps.employees.models import Employee, FamilyMember, AcademicRecord, Certification; print('OK')"
```

---

## Task 7: Rename fields in `apps/contracts/` (2 model files, 2 PKs)

**Files:** `apps/api/apps/contracts/models/{contract,employment_data}.py`

PKs:
- `Contract.contrato_id` → `id` UUID
- `EmploymentData.dato_laboral_id` → `id` UUID

Same pattern.

```bash
python -c "...; from apps.contracts.models import Contract, EmploymentData; print('OK')"
```

---

## Task 8: Rename fields in `apps/documents/` (2 model files, 2 PKs)

**Files:** `apps/api/apps/documents/models/{digital_document,document_template}.py`

PKs:
- `DigitalDocument.documento_id` → `id` UUID
- `DocumentTemplate.plantilla_id` → `id` UUID

Same pattern.

```bash
python -c "...; from apps.documents.models import DigitalDocument, DocumentTemplate; print('OK')"
```

---

## Task 9: Rename fields in `apps/payroll/` (2 model files, 9 PKs)

**Files:** `apps/api/apps/payroll/models/{compensation,tax_parameter}.py`

`compensation.py` has 8 classes with 8 PKs (each class's own PK). `tax_parameter.py` has 1.

PKs:
- `MonthlyPayroll.planilla_id` → `id` UUID
- `PayrollDetail.detalle_id` → `id` UUID
- `PayrollConcept.concepto_planilla_id` → `id` UUID
- `AfpConfiguration.afp_config_id` → `id` UUID
- `CompensationConfiguration.configuracion_id` → `id` UUID
- `MassDeduction.descuento_masivo_id` → `id` UUID
- `PaySlip.boleta_id` → `id` UUID
- `PaymentSchedule.calendario_id` → `id` UUID
- `TaxParameter.configuracion_uit_id` → `id` UUID

**Watch out:** `compensation.py` is a large file (8 classes). When editing, inventory first to ensure correct field belongs to correct class. Use Read tool to see the structure.

Same pattern. Smoke import:
```bash
python -c "...; from apps.payroll.models import MonthlyPayroll, PayrollDetail, PayrollConcept, AfpConfiguration, CompensationConfiguration, MassDeduction, PaySlip, PaymentSchedule, TaxParameter; print('OK')"
```

---

## Task 10: Rename fields in `apps/time_off/` (1 model file, 5 PKs)

**Files:** `apps/api/apps/time_off/models/vacation.py`

PKs (5 classes in 1 file):
- `VacationConfiguration.configuracion_id` → `id` UUID
- `VacationPeriod.periodo_id` → `id` UUID
- `VacationRequest.solicitud_id` → `id` UUID
- `VacationGrant.goce_id` → `id` UUID
- `VacationRequestHistory.historial_id` → `id` UUID

**Note:** `configuracion_id` collides with `payroll.CompensationConfiguration.configuracion_id` in name only — they're in different files/classes, no conflict.

Same pattern.

```bash
python -c "...; from apps.time_off.models import VacationRequest, VacationGrant, VacationConfiguration, VacationPeriod, VacationRequestHistory; print('OK')"
```

---

## Task 11: Rename fields in `apps/onboarding/` (1 model file, 1 PK)

**Files:** `apps/api/apps/onboarding/models/onboarding_process.py`

PK:
- `OnboardingProcess.onboarding_id` → `id` UUID

Same pattern.

```bash
python -c "...; from apps.onboarding.models import OnboardingProcess; print('OK')"
```

---

## Task 12: Verify all model field renames complete

```bash
cd D:/VYNTIA/apps/api
echo "=== UUID PKs total (expected: 31) ==="
grep -hE "^\s+id\s*=\s*models\.UUIDField\(primary_key=True" apps/*/models/*.py | wc -l
echo ""
echo "=== Audit fields renamed (created_at + updated_at + created_by + updated_by, total: 54) ==="
grep -hE "^\s+(created_at|updated_at|created_by|updated_by)\s*=" apps/*/models/*.py | wc -l
echo ""
echo "=== State renamed (status + is_active, total: 9) ==="
grep -hE "^\s+(status|is_active)\s*=" apps/*/models/*.py | wc -l
echo ""
echo "=== Stale ES audit/state/PK fields (should be 0) ==="
grep -rEn "^\s+(fecha_creacion|fecha_actualizacion|fecha_registro|fecha_modificacion|creado_por|modificado_por)\s*=|^\s+estado\s*=|^\s+activo\s*=|^\s+[a-z_]+_id\s*=\s*models\.AutoField\(primary_key=True" apps/*/models/*.py || echo "OK: cero"
cd D:/VYNTIA
```

Expected: 31, 54, 9, OK: cero.

If counts diverge, **STOP** — investigate before proceeding to Task 13.

---

## Task 13: Update serializers — bulk sed across `api/v1/`

**Files:** `apps/api/api/v1/**/*.py` (~20 files including `serializers.py`, `contratos_serializers.py`, etc.)

### Step 1: Inventory current field references

```bash
cd D:/VYNTIA/apps/api
echo "=== Field references in api/v1/ ==="
grep -rEcn "\b(empleado_id|usuario_id|rol_id|permiso_id|modulo_id|rol_permiso_id|modulo_permiso_id|usuario_rol_id|area_id|familiar_id|academico_id|curso_id|contrato_id|dato_laboral_id|documento_id|plantilla_id|afp_config_id|configuracion_id|planilla_id|detalle_id|concepto_planilla_id|descuento_masivo_id|boleta_id|calendario_id|configuracion_uit_id|periodo_id|solicitud_id|goce_id|historial_id|onboarding_id|fecha_creacion|fecha_actualizacion|fecha_registro|fecha_modificacion|creado_por|modificado_por)\b" api --include="*.py" | awk -F: '{s+=$2} END {print s}'
cd D:/VYNTIA
```

### Step 2: Bulk sed — PKs

PK rename is per-model, but in serializer field lists they appear as bare strings (e.g., `'empleado_id'`). Sed at this level: each `<old_pk> → 'id'`.

**WARNING:** Multiple PKs map to the same target `'id'`. When `'empleado_id'` appears in `EmpleadoSerializer.Meta.fields`, replace with `'id'`. When `'usuario_id'` appears in `UserSerializer.Meta.fields`, also replace with `'id'`. Sed handles both since `'<model>_id' → 'id'` is the rule.

**BUT:** In code like `Empleado.objects.filter(empleado_id=empleado.empleado_id)`, the field name `empleado_id` is the FK column name on the **OTHER** model (e.g., `ContratosAdendas.empleado_id`). After PK rename, FK columns auto-derive based on FK field names (e.g., `empleado` field → column `empleado_id`). So the Python attribute name on FK is still `empleado_id` (Django magic). **NOT all `empleado_id` references should be renamed to `id`** — only those that refer to the PK of `Empleado` itself.

This means **bulk sed is risky for PKs**. Better: leave PK references in code as-is when they're FK column accessors (`employee.empleado_id` where `employee.empleado` is the FK), and only rename when they're PK accessors of the target model (`empleado.empleado_id` where `empleado` is an Empleado instance).

The cleanest path is to use Django's `pk` alias everywhere it makes sense. Replace `empleado.empleado_id` (PK accessor) with `empleado.pk` or `empleado.id`. This is much safer than sed.

**Decision for Task 13:** sed only the audit fields and state literals (low-risk). PK references stay AS-IS in this task — they get cleaned up as needed during smoke tests in Task 18.

```bash
cd D:/VYNTIA/apps/api
find api -type f -name "*.py" -not -path "*/__pycache__/*" -print0 | xargs -0 sed -i \
  -e 's|\bfecha_creacion\b|created_at|g' \
  -e 's|\bfecha_actualizacion\b|updated_at|g' \
  -e 's|\bfecha_registro\b|created_at|g' \
  -e 's|\bfecha_modificacion\b|updated_at|g' \
  -e 's|\bcreado_por\b|created_by|g' \
  -e 's|\bmodificado_por\b|updated_by|g'
cd D:/VYNTIA
```

**WARNING re: `estado` and `activo`:** These are short identifiers and risky. They'll match many false positives (e.g., variable names `estado_actual`, dictionary keys `'estado': 'activo'`). **Skip bulk sed for `estado` and `activo`** — handle case-by-case in Tasks 14-15 only where they're definitively model field references.

### Step 3: Update serializer Meta.fields lists (PK references)

Bulk sed `'empleado_id'` → `'id'`, `'usuario_id'` → `'id'`, etc. inside serializer field lists is safe IF and ONLY IF the file context is a Meta.fields list. Since serializers are typically clean (each Meta is for one model), the risk is low.

```bash
cd D:/VYNTIA/apps/api
find api -type f -name "*.py" -not -path "*/__pycache__/*" -print0 | xargs -0 sed -i \
  -e "s|'empleado_id'|'id'|g" \
  -e "s|'usuario_id'|'id'|g" \
  -e "s|'rol_id'|'id'|g" \
  -e "s|'permiso_id'|'id'|g" \
  -e "s|'modulo_id'|'id'|g" \
  -e "s|'rol_permiso_id'|'id'|g" \
  -e "s|'modulo_permiso_id'|'id'|g" \
  -e "s|'usuario_rol_id'|'id'|g" \
  -e "s|'area_id'|'id'|g" \
  -e "s|'familiar_id'|'id'|g" \
  -e "s|'academico_id'|'id'|g" \
  -e "s|'curso_id'|'id'|g" \
  -e "s|'contrato_id'|'id'|g" \
  -e "s|'dato_laboral_id'|'id'|g" \
  -e "s|'documento_id'|'id'|g" \
  -e "s|'plantilla_id'|'id'|g" \
  -e "s|'afp_config_id'|'id'|g" \
  -e "s|'configuracion_id'|'id'|g" \
  -e "s|'planilla_id'|'id'|g" \
  -e "s|'detalle_id'|'id'|g" \
  -e "s|'concepto_planilla_id'|'id'|g" \
  -e "s|'descuento_masivo_id'|'id'|g" \
  -e "s|'boleta_id'|'id'|g" \
  -e "s|'calendario_id'|'id'|g" \
  -e "s|'configuracion_uit_id'|'id'|g" \
  -e "s|'periodo_id'|'id'|g" \
  -e "s|'solicitud_id'|'id'|g" \
  -e "s|'goce_id'|'id'|g" \
  -e "s|'historial_id'|'id'|g" \
  -e "s|'onboarding_id'|'id'|g"
cd D:/VYNTIA
```

This affects `read_only_fields = ['empleado_id']`, `fields = ['empleado_id', ...]`, etc.

**Caveat:** This doesn't cover FK column references like `'empleado_id'` when used as a FK lookup pattern (`{'empleado_id': 5}`). Those need manual fix during smoke tests.

### Step 4: Verify

```bash
cd D:/VYNTIA/apps/api
echo "=== Stale audit/state field refs in api/ (should be 0 except domain audit-like) ==="
grep -rEn "\b(fecha_creacion|fecha_actualizacion|fecha_registro|fecha_modificacion|creado_por|modificado_por)\b" api --include="*.py" | grep -v "__pycache__" | head -20 || echo "OK: cero"
cd D:/VYNTIA
```

Expected: 0 stale audit field refs.

---

## Task 14: Update tests — bulk sed across `tests/`

**Files:** `apps/api/tests/*.py` (~16 test files + conftest)

Same approach as Task 13:

```bash
cd D:/VYNTIA/apps/api
find tests -type f -name "*.py" -not -path "*/__pycache__/*" -print0 | xargs -0 sed -i \
  -e 's|\bfecha_creacion\b|created_at|g' \
  -e 's|\bfecha_actualizacion\b|updated_at|g' \
  -e 's|\bfecha_registro\b|created_at|g' \
  -e 's|\bfecha_modificacion\b|updated_at|g' \
  -e 's|\bcreado_por\b|created_by|g' \
  -e 's|\bmodificado_por\b|updated_by|g' \
  -e "s|'empleado_id'|'id'|g" \
  -e "s|'usuario_id'|'id'|g" \
  -e "s|'rol_id'|'id'|g" \
  -e "s|'permiso_id'|'id'|g" \
  -e "s|'modulo_id'|'id'|g" \
  -e "s|'rol_permiso_id'|'id'|g" \
  -e "s|'modulo_permiso_id'|'id'|g" \
  -e "s|'usuario_rol_id'|'id'|g" \
  -e "s|'area_id'|'id'|g" \
  -e "s|'familiar_id'|'id'|g" \
  -e "s|'academico_id'|'id'|g" \
  -e "s|'curso_id'|'id'|g" \
  -e "s|'contrato_id'|'id'|g" \
  -e "s|'dato_laboral_id'|'id'|g" \
  -e "s|'documento_id'|'id'|g" \
  -e "s|'plantilla_id'|'id'|g" \
  -e "s|'afp_config_id'|'id'|g" \
  -e "s|'configuracion_id'|'id'|g" \
  -e "s|'planilla_id'|'id'|g" \
  -e "s|'detalle_id'|'id'|g" \
  -e "s|'concepto_planilla_id'|'id'|g" \
  -e "s|'descuento_masivo_id'|'id'|g" \
  -e "s|'boleta_id'|'id'|g" \
  -e "s|'calendario_id'|'id'|g" \
  -e "s|'configuracion_uit_id'|'id'|g" \
  -e "s|'periodo_id'|'id'|g" \
  -e "s|'solicitud_id'|'id'|g" \
  -e "s|'goce_id'|'id'|g" \
  -e "s|'historial_id'|'id'|g" \
  -e "s|'onboarding_id'|'id'|g"
cd D:/VYNTIA
```

**Note:** Tests often use `.empleado_id` (PK attribute) directly, e.g., `assert response.data['empleado_id'] == empleado.empleado_id`. These need manual fix in Task 18 if pytest fails.

---

## Task 15: Update legacy `app_rrhh/` + `apps/core/` + cross-app services + scripts

**Files:** `app_rrhh/**/*.py`, `apps/core/**/*.py`, `apps/<name>/services/**/*.py`, `scripts/*.py`

```bash
cd D:/VYNTIA/apps/api
find app_rrhh apps/core apps/*/services scripts -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -not -path "*/fixtures/*" -print0 | xargs -0 sed -i \
  -e 's|\bfecha_creacion\b|created_at|g' \
  -e 's|\bfecha_actualizacion\b|updated_at|g' \
  -e 's|\bfecha_registro\b|created_at|g' \
  -e 's|\bfecha_modificacion\b|updated_at|g' \
  -e 's|\bcreado_por\b|created_by|g' \
  -e 's|\bmodificado_por\b|updated_by|g' \
  -e "s|'empleado_id'|'id'|g" \
  -e "s|'usuario_id'|'id'|g" \
  -e "s|'rol_id'|'id'|g" \
  -e "s|'permiso_id'|'id'|g" \
  -e "s|'modulo_id'|'id'|g" \
  -e "s|'rol_permiso_id'|'id'|g" \
  -e "s|'modulo_permiso_id'|'id'|g" \
  -e "s|'usuario_rol_id'|'id'|g" \
  -e "s|'area_id'|'id'|g" \
  -e "s|'familiar_id'|'id'|g" \
  -e "s|'academico_id'|'id'|g" \
  -e "s|'curso_id'|'id'|g" \
  -e "s|'contrato_id'|'id'|g" \
  -e "s|'dato_laboral_id'|'id'|g" \
  -e "s|'documento_id'|'id'|g" \
  -e "s|'plantilla_id'|'id'|g" \
  -e "s|'afp_config_id'|'id'|g" \
  -e "s|'configuracion_id'|'id'|g" \
  -e "s|'planilla_id'|'id'|g" \
  -e "s|'detalle_id'|'id'|g" \
  -e "s|'concepto_planilla_id'|'id'|g" \
  -e "s|'descuento_masivo_id'|'id'|g" \
  -e "s|'boleta_id'|'id'|g" \
  -e "s|'calendario_id'|'id'|g" \
  -e "s|'configuracion_uit_id'|'id'|g" \
  -e "s|'periodo_id'|'id'|g" \
  -e "s|'solicitud_id'|'id'|g" \
  -e "s|'goce_id'|'id'|g" \
  -e "s|'historial_id'|'id'|g" \
  -e "s|'onboarding_id'|'id'|g"
cd D:/VYNTIA
```

---

## Task 16: NUCLEAR DB regenerate

**Patrón validado en L3.2-L3.10.1.**

### Step 1: Drop bd_vyntia (kill procs first)

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "DROP DATABASE IF EXISTS bd_vyntia;" 2>&1
```

### Step 2: Eliminar migration files existentes (8 apps)

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
cd D:/VYNTIA
```

### Step 3: Recrear bd_vyntia (LR12)

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "CREATE DATABASE bd_vyntia WITH ENCODING 'UTF8' TEMPLATE template0;" 2>&1
```

### Step 4: Generar fresh migrations

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py makemigrations --settings=vyntia.settings.development 2>&1 | tail -50
cd D:/VYNTIA
```

Expected: each app's `0001_initial.py` regenerated with English field names, UUID PKs, `db_column` ES preserved on audit/state fields.

Verify migrations contain expected:
```bash
cd D:/VYNTIA/apps/api
echo "=== UUID fields in migrations (should be ~31, one per model) ==="
grep -hE "models\.UUIDField" apps/*/migrations/0001_initial.py | wc -l
echo ""
echo "=== db_column='fecha_creacion' refs (should be ~19) ==="
grep -hE "db_column='fecha_creacion'" apps/*/migrations/0001_initial.py | wc -l
echo ""
echo "=== Stale 'fecha_creacion' as field name (should be 0) ==="
grep -hE "'fecha_creacion'," apps/*/migrations/0001_initial.py | wc -l
cd D:/VYNTIA
```

### Step 5: Aplicar migraciones

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -25
cd D:/VYNTIA
```

Expected: all apps migrate clean.

### Step 6: Verify physical schema

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "\d empleado" 2>&1 | head -30
```

Expected output should show:
- `id` column (uuid type) — PK renamed
- `fecha_creacion` column (timestamp) — audit preserved physically
- `fecha_actualizacion` column (timestamp) — audit preserved
- `estado_empleado` column (varchar) — domain field preserved (NOT renamed in this PR)

### Step 7: Reseed

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py setup_roles_permisos --settings=vyntia.settings.development 2>&1 | tail -10
PGPASSWORD='Demenci4@' python manage.py seed_menu --settings=vyntia.settings.development 2>&1 | tail -10
cd D:/VYNTIA
```

Verify:
```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'rol' AS t, COUNT(*) FROM rol UNION ALL SELECT 'permiso', COUNT(*) FROM permiso UNION ALL SELECT 'modulos', COUNT(*) FROM modulos;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0.

If reseed fails because management commands reference old PK names (`Empleado.objects.create(empleado_id=...)`), the sed in Task 15 should have fixed them. If not, manual fix.

---

## Task 17: Smoke tests

### Step 1: Django check

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: `System check identified no issues (0 silenced).`

If failure with `FieldError` or `AttributeError`, the smoke test will tell us where. Most common culprits:
- `Empleado.objects.filter(empleado_id=...)` — needs to be `.filter(id=...)` or `.filter(pk=...)`
- ORM lookup `<related>__empleado_id` — needs `<related>__id`
- `search_fields = ['fecha_creacion']` — needs `'created_at'`

Fix manually with Edit tool. **Iterative** — run `manage.py check`, fix the FIRST error, re-run, repeat until clean.

### Step 2: pytest

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: `125 passed, 44 failed, 3 skipped` (baseline preserved).

If passed < 125, look at the FIRST 5 fail messages and identify the field name issue. Common patterns:
- Test uses `empleado.empleado_id` — change to `empleado.id` or `empleado.pk`
- Test uses `Empleado.objects.filter(empleado_id=...)` — change kwarg to `id=...` or `pk=...`
- Test sets `data = {'empleado_id': 5, ...}` for serializer input — keep if serializer expects `empleado_id` JSON key OR change to `'id'` if serializer was updated

Fix iteratively. Run pytest, fix 1-3 failures, re-run, repeat.

### Step 3: runserver smoke

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l3102.log 2>&1 &
SERVER_PID=$!
sleep 10
curl -s -o /dev/null -w "HTTP %{http_code} /api/docs/\n" http://127.0.0.1:8000/api/docs/
kill $SERVER_PID 2>/dev/null
sleep 1
cd D:/VYNTIA
```

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

Expected: `HTTP 200 /api/docs/`. If 500, check the log for serializer schema generation errors.

### Step 4: Final stale check

```bash
cd D:/VYNTIA/apps/api
echo "=== Stale audit/state field refs in code (excluding migrations and string-literal preserved) ==="
grep -rEn "\b(fecha_creacion|fecha_actualizacion|fecha_registro|fecha_modificacion|creado_por|modificado_por)\b" --include="*.py" \
  --exclude-dir=__pycache__ \
  --exclude-dir=migrations \
  --exclude-dir=fixtures \
  --exclude-dir=.venv \
  apps tests app_rrhh api scripts 2>&1 | grep -v "db_column='fecha\|db_column='creado\|db_column='modificado\|db_column='actualizado" | head -20 || echo "OK: cero"
cd D:/VYNTIA
```

Expected: only `db_column=` references remain (those are intentional preservation).

---

## Task 18: Atomic commit

```bash
cd D:/VYNTIA
git status --short | head -30
git add apps/api/
git commit -m "$(cat <<'EOF'
chore(L3.10.2): rename audit fields + state literals + PKs ES→EN

Audit fields (54 fields, 6 mappings):
- fecha_creacion → created_at (db_column preserved)
- fecha_actualizacion → updated_at (db_column preserved)
- fecha_registro → created_at (db_column preserved)
- fecha_modificacion → updated_at (db_column preserved)
- creado_por → created_by (db_column preserved)
- modificado_por → updated_by (db_column preserved)

State literals (9 fields, 2 mappings):
- estado → status (db_column='estado')
- activo → is_active (db_column='activo')

PKs (31 fields):
- <model>_id → id (UUIDField, type changed AutoField→UUIDField)
- Physical column also renamed to 'id' (no db_column preservation; type change anyway)

Domain vocabulary HR PRESERVADO en español per Option B scope:
- nombres_empleado, apellido_paterno, tipo_documento, numero_cuspp, etc.
- estado_empleado, estado_civil, vigencia_estado_seguro
- fecha_inicio, fecha_fin, fecha_nacimiento, fecha_ingreso
- validado_por, digitalizado_por, subido_por

NUCLEAR DB regen: bd_vyntia recreated with English audit fields
+ Spanish db_column preservation. Frontend will break for PK uses
(empleado_id → id, int → uuid) — fix in L3.10.4.

Baseline pytest preservado. manage.py check clean. /api/docs/ HTTP 200.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 19: Merge a master

- [ ] **Confirmar autorización del usuario.**

```bash
git checkout master
git merge --no-ff vyntia/L3.10.2-rename-fields -m "Merge L3.10.2: rename audit fields + state literals + PKs ES→EN"
git log --oneline -5
```

Post-merge smoke:
```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

---

## Task 20: Update roadmap + memory

Update `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`:
- L3.10.2 → ✅ merged `<sha>` 2026-04-XX
- L3.10.3 → ⏳ NEXT

Update `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- L3.10.2 ✅ merged
- Próximo paso: L3.10.3 (model splits con data migration)

Commit:
```bash
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.10.2): mark L3.10.2 merged, L3.10.3 (splits) as next"
```

---

## Después de L3.10.2

**Próximo plan:** L3.10.3 — model splits con data migration:
- `Contract` → `Contract` + `ContractAmendment` (partition por field `tipo='contrato'` vs `'adenda'`)
- `VacationRequest` → `VacationRequest` + `VacationBalance` (refactor lógico)
- Data migration vía `RunPython` (NUCLEAR DB strategy still applies — but split tables created)
- Riesgo crítico (data integrity)

---

## Notas para el ejecutor

- **Patrón Edit-tool por modelo**, NO sed bulk para fields. Razón: agregar `db_column=` preservando args originales requiere context awareness que sed no tiene.
- **PK type change int→uuid** rompe FK column types en cascada. NUCLEAR DB regen lo maneja sin data migration.
- **Frontend BREAKS**: `empleado_id: number` ya no es válido cuando JSON envía UUID strings bajo key `id`. Aceptado per Option B; L3.10.4 lo arregla.
- **Iteración esperada**: Task 17 Steps 1-2 (manage.py check + pytest) tendrán failures iniciales por references PK que el sed no captura (ej: `empleado.empleado_id` access). Iterar fix-and-retest hasta verde.
- **`db_column` mandatorio** en cada audit/state field renombrado — sin él, columna física se renombraría también, rompiendo el principio de preservar physical schema.
- **`db_column` AUSENTE en PKs** — porque type change requiere column recreation; renombrar columna también es la opción consistente.
- **PGPASSWORD env var** explícito por known issue (Windows env con caracteres no-ASCII).
- **Lecciones de L3.10.1 aplicadas**: NUCLEAR DB sequence (LR12), word-boundary sed (general), domain vocabulary preservation (extensión de spec § 3.5 regla 7).
- **Lecciones nuevas (LR17, LR18)**: documentar post-merge en active_subproject.md.
