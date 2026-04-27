# VYNTIA Foundation L3.10.3 — Split `Contract` into `Contract` + `ContractAmendment` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Splittear el modelo `Contract` (que actualmente mezcla contratos iniciales y adendas via `tipo_documento` choices `CAS_*`/`LEY_728_*`/`LEY_276_*` vs `ADENDA_*`) en dos modelos distintos: `Contract` (relaciones laborales originales) y `ContractAmendment` (modificaciones a un contrato existente con FK `parent_contract`). NUCLEAR DB regen — bd_vyntia tiene 0 contratos post-L3.10.2, así que data migration es trivial. Inbound FKs (ej. `VacationPeriod.contrato`) siguen apuntando a `Contract` (parent).

**Architecture:** L3.10.3 es el tercer sub-PR de L3.10. Solo toca el modelo Contract y sus consumers — no toca otros models, fields, frontend. La división lógica:
- `Contract` — contratos iniciales/principales. Choices `tipo_documento`: solo `CAS_*`, `LEY_728_*`, `LEY_276_*`. Sin `numero_adenda`. Sin properties `es_contrato_inicial`/`es_adenda`.
- `ContractAmendment` — adendas. Choices `tipo_documento`: solo `ADENDA_SALARIAL`, `ADENDA_CARGO`, `ADENDA_HORARIO`, `ADENDA_EXTENSION`. FK `parent_contract` to Contract. Con `numero_adenda` (sequential per parent).
- DB: `Contract.db_table = 'contratos_adendas'` (preservado de L3.x), `ContractAmendment.db_table = 'contract_amendments'` (nuevo). NUCLEAR regen crea ambas tablas físicamente.

**Tech Stack:** Django 5.2, NUCLEAR DB regen, ORM split queries, sed para identifier renames donde aplique.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.2 ("contracts → Contract + ContractAmendment (split)"), § 3.4 (URL structure resultante incluye `/api/v1/contracts/{id}/amendments`). VacationRequest split del spec § 3.2 se DESCARTA en L3.10.3 — el balance ya vive en VacationPeriod, no en VacationRequest (clarificación documentada en spec § 3.2.1).

**Scope decision (Option A — sub-PR de L3.10):**
- L3.10.1 ✅ Class names rename (33 clases) — merged `7bccc348`
- L3.10.2 ✅ Audit fields + state literales + PKs UUID — merged `a9ec4a80`
- **L3.10.3 (este plan)** — Contract split solamente. VacationRequest split del spec se descarta.
- L3.10.4 ⏳ Frontend rename + URL paths nuevos

**Pre-condiciones:**
- L3.10.2 mergeada a master (commit `06e40f67`)
- Django 5.2.13, las 8 apps de dominio operativas, 31 PKs UUID
- pytest baseline: **161 passed, 8 failed, 3 skipped** (mejorado en L3.10.2)
- `bd_vyntia` provisionada con esquema actual (0 contratos)
- venv en `D:/VYNTIA/.venv/`

---

## Tabla canónica del split

### Antes de L3.10.3 (post-L3.10.2)

| Modelo | Fields clave | tipo_documento choices |
|---|---|---|
| `Contract` (1 modelo) | `id` UUID, `empleado`, `area`, `numero_contrato`, **`numero_adenda` (nullable — non-null para adendas)**, `tipo_documento`, `fecha_inicio`, `fecha_fin`, `fecha_firma`, `salario_bruto`, `cargo`, `jornada_laboral`, `funciones`, `lugar_trabajo`, `horario_trabajo`, `observaciones`, `status`, `documento_generado`, `created_by`, `updated_by`, `created_at`, `updated_at`. Properties `es_contrato_inicial`, `es_adenda` | `CAS_*`, `LEY_728_*`, `LEY_276_*`, `ADENDA_*` (mixto) |

### Después de L3.10.3

| Modelo | Fields clave | tipo_documento choices | db_table |
|---|---|---|---|
| `Contract` | `id`, `empleado`, `area`, `numero_contrato` (unique), `tipo_documento`, `fecha_inicio`, `fecha_fin`, `fecha_firma`, `salario_bruto`, `cargo`, `jornada_laboral`, `funciones`, `lugar_trabajo`, `horario_trabajo`, `observaciones`, `status`, `documento_generado`, audit fields | Solo `CAS_INDETERMINADO`, `CAS_DETERMINADO`, `CAS_SUPLENCIA`, `LEY_728_FIJO`, `LEY_728_FIJO_SUPLENCIA`, `LEY_728_INDETERMINADO`, `LEY_276_INDETERMINADO` | `contratos_adendas` (preservado de L3.10.1) |
| `ContractAmendment` | `id`, `parent_contract` (FK to Contract, on_delete=CASCADE), `numero_adenda` (CharField), `tipo_documento`, `fecha_inicio` (vigencia), `fecha_fin` (vigencia), `fecha_firma`, `nuevo_salario` (nullable Decimal), `nuevo_cargo` (nullable CharField), `nuevo_horario` (nullable CharField), `nueva_jornada_laboral` (nullable CharField), `nueva_fecha_fin_contrato` (nullable Date — para extension), `motivo`, `observaciones`, `status`, `documento_generado`, audit fields | Solo `ADENDA_SALARIAL`, `ADENDA_CARGO`, `ADENDA_HORARIO`, `ADENDA_EXTENSION` | `contract_amendments` (nueva tabla física en inglés) |

**Decisión sobre `ContractAmendment.db_table`:** A diferencia de Contract (que preserva `contratos_adendas` legacy), ContractAmendment es un modelo NUEVO sin precedente físico. Por consistencia con la dirección futura (todo legacy ES via `db_column`/`db_table` cuando preserves, todo nuevo en EN), `ContractAmendment.db_table = 'contract_amendments'`.

**Decisión sobre fields:** ContractAmendment NO duplica todos los fields de Contract — solo lleva los que el amendment efectivamente cambia. Si un amendment cambia múltiples cosas (salario + cargo a la vez), el frontend agrega ambos en una operación.

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/apps/contracts/models/contract_amendment.py` | Nuevo modelo `ContractAmendment` con todos sus fields + FK `parent_contract` |
| Modify | `apps/api/apps/contracts/models/contract.py` | Remover `numero_adenda`, remover ADENDA_* de TIPO_DOCUMENTO_CHOICES, remover properties `es_contrato_inicial`/`es_adenda` (siempre True/False ahora — innecesarias) |
| Modify | `apps/api/apps/contracts/models/__init__.py` | Re-exportar `Contract` y `ContractAmendment` |
| Delete | `apps/api/apps/contracts/migrations/0001_initial.py`, `0002_initial.py` | Regenerados via NUCLEAR |
| Modify | `apps/api/api/v1/rrhh/contratos_serializers.py` | `ContratosAdendasSerializer` (legacy) → solo Contract. Nuevo `ContractAmendmentSerializer`. Remover `numero_adenda`, `es_contrato_inicial`, `es_adenda` de Contract serializer |
| Modify | `apps/api/api/v1/rrhh/contratos_views.py` | `ContratosAdendasViewSet` (legacy) → solo Contract. Nuevo `ContractAmendmentViewSet` (read-only por ahora). Remover filtros que separaban adendas |
| Modify | `apps/api/api/v1/rrhh/urls.py` | Registrar nuevo viewset `/contracts/<contract_id>/amendments/` y `/amendments/` |
| Modify | `apps/api/app_rrhh/managers/contratos_manager.py` | Remover métodos `.adendas()` (ahora ContractAmendment.objects.all()). Métodos `.contratos()` con choice list stale (CONTRATO_INDEFINIDO etc. — limpiar al subset CAS_/LEY_*). NOTA: este manager es legacy code para cleanup en L3.11 |
| Modify | `apps/api/apps/time_off/services/vacation_calculation_service.py:32,45` | Remover `tipo_documento__startswith='CONTRATO'` (stale string anyway). Usar Contract model directamente sin filtros — Contract ya solo contiene contratos no adendas |
| Modify | `apps/api/apps/documents/services/template_service.py`, `pdf_generator.py` | `template_service.generar_adenda(adenda.pk, tipo_adenda=adenda.tipo_documento)` ahora recibe ContractAmendment instance, no Contract |
| Modify | `apps/api/api/v1/app_rrhh/document_generation_views.py` | `generar_adenda()` recibe `adenda_id` que ahora es un ContractAmendment.id, no un Contract.id |
| Modify | `apps/api/tests/test_contratos_integration.py` | Tests con `tipo_documento='ADENDA_*'` ahora deben crear ContractAmendment, no Contract. Tests de `Contract` solo CAS_/LEY_* |
| Modify | `apps/api/docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.2.1 | Documentar que VacationRequest split del spec se descarta |

**NO se toca en L3.10.3:**
- `VacationPeriod` (ya cumple rol de balance — no rename, no split)
- `VacationRequest` — split descartado
- Otros modelos
- Frontend (`apps/web/`) — L3.10.4
- URL paths nuevos `/api/v1/contracts/...` (espera L3.10.4)
- `app_rrhh/services/empleado_report_service.py` (L3.11 cleanup)

**Lecciones aplicadas:**
- LR9-LR20 ya internalizadas — el split usa el patrón conocido.
- **LR21 nueva (a documentar):** model split requiere actualizar consumers que querían el modelo unificado para que ahora consulten ambos. Los managers legacy con choice lists hardcoded (ej. `tipo_documento__in=['ADENDA_SALARIAL', 'ADENDA_CARGO', ...]`) ya no necesitan filtrar — la separación es a nivel de modelo. **Defensive grep** en plan template para `tipo_documento__in=` y `tipo_documento__startswith=` antes y después.

---

## Definition of Done

- [ ] `ContractAmendment` model definido en `apps/contracts/models/contract_amendment.py` con FK `parent_contract` to Contract
- [ ] `Contract` model limpio: sin `numero_adenda`, sin ADENDA_* choices, sin properties `es_contrato_inicial`/`es_adenda`
- [ ] `apps/contracts/models/__init__.py` re-exporta `Contract`, `ContractAmendment`
- [ ] Migrations regeneradas vía NUCLEAR: `Contract` con `db_table='contratos_adendas'`, `ContractAmendment` con `db_table='contract_amendments'`
- [ ] Inbound FK `VacationPeriod.contrato → 'contracts.Contract'` PRESERVADO (apunta a parent contract, no amendment)
- [ ] `ContractAmendmentSerializer` y `ContractAmendmentViewSet` creados
- [ ] `ContratosAdendasViewSet` (legacy) ahora retorna solo Contract (sin amendments)
- [ ] `app_rrhh/managers/contratos_manager.py` métodos `.contratos()` y `.adendas()` actualizados/limpiados (stale CONTRATO_* removidos; `.adendas()` deprecated)
- [ ] `vacation_calculation_service.py:32,45` removido filter `tipo_documento__startswith='CONTRATO'` (Contract ya solo es contratos)
- [ ] `template_service.generar_adenda()` y `document_generation_views.generar_adenda()` reciben ContractAmendment, no Contract
- [ ] Tests `test_contratos_integration.py` separan creación de Contract vs ContractAmendment
- [ ] `bd_vyntia` recreada con tablas `contratos_adendas` (Contract) + `contract_amendments` (ContractAmendment)
- [ ] `python manage.py check` clean
- [ ] `pytest`: 161 passed, 8 failed, 3 skipped (baseline preservado o mejorado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.10.3-contract-split` mergeada a master con `--no-ff`
- [ ] Roadmap + memory MEMORY.md/active_subproject.md actualizados — L3.10.3 ✅, L3.10.4 NEXT

---

## Task 1: Pre-flight — branch, baseline, backup

- [ ] **Step 1: Confirmar pwd, master limpio post-L3.10.2, HEAD post-merge**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -5
```

Expected: HEAD = `06e40f67 docs(L3.10.2): mark L3.10.2 merged, L3.10.3 (model splits) as next` o más reciente. `git status` shows ONLY the L3.10.3 plan file untracked.

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

Expected: `161 passed, 8 failed, 3 skipped`. Si difiere, **STOP report BLOCKED**.

- [ ] **Step 4: Backup bd_vyntia**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.10.3.dump 2>&1 | tail -3
ls -lh /tmp/bd_vyntia_pre_L3.10.3.dump
```

Expected: dump file exists.

- [ ] **Step 5: Snapshot pre-split inventory**

```bash
cd D:/VYNTIA/apps/api
echo "=== Contract.tipo_documento choices in current model ==="
grep -A 14 "TIPO_DOCUMENTO_CHOICES = \[" apps/contracts/models/contract.py | head -20
echo ""
echo "=== References to ADENDA_*, numero_adenda, es_adenda, es_contrato_inicial ==="
grep -rEcn "ADENDA_|numero_adenda|es_adenda|es_contrato_inicial" \
  --include="*.py" apps tests app_rrhh api 2>/dev/null \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | awk -F: '{s+=$2} END {print s}'
echo ""
echo "=== Inbound FK refs to 'contracts.Contract' ==="
grep -rEn "['\"]contracts\.Contract['\"]" apps --include="*.py" 2>/dev/null
cd D:/VYNTIA
```

Snapshot for later comparison.

- [ ] **Step 6: Crear branch L3.10.3**

```bash
git checkout -b vyntia/L3.10.3-contract-split
git status --short
```

---

## Task 2: Comitear el plan

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-27-vyntia-foundation-L3.10.3-contract-split.md
git commit -m "docs(L3.10.3): add Contract split plan (Option A — VacationRequest split discarded)"
```

---

## Task 3: Update spec § 3.2 — clarify VacationRequest split discard

Read `D:/VYNTIA/docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.2 (lines around 156-170).

Use Edit tool to add a new sub-section `### 3.2.1 Scope clarification (L3.10.3)` immediately after the División de modelos table:

```markdown

### 3.2.1 Scope clarification (L3.10.3)

L3.10.3 implementa solo el split `Contract → Contract + ContractAmendment`. El split listado en § 3.2 para `VacationRequest → VacationRequest + VacationBalance` se DESCARTA por análisis posterior:

- `VacationRequest` actual NO contiene fields de balance — solo solicitud/aprobación/rechazo/cancelación con `dias_solicitados`, `motivo_solicitud`, `estado_solicitud`, etc.
- Los fields de balance (`dias_correspondientes`, `dias_adicionales`, `dias_totales`, `dias_gozados`, `dias_pendientes`, `dias_vencidos`) ya viven en `VacationPeriod`. `VacationPeriod` cumple efectivamente el rol de "balance" por período anual.
- Crear un nuevo `VacationBalance` separado de `VacationPeriod` agregaría complejidad sin valor — sería un modelo 1:1 OneToOne con VacationPeriod.

**Decisión:** mantener la estructura actual de 5 modelos en time_off (`VacationConfiguration`, `VacationPeriod`, `VacationRequest`, `VacationGrant`, `VacationRequestHistory`). VacationPeriod es el balance per period.
```

Commit:
```bash
cd D:/VYNTIA
git add docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md
git commit -m "docs(L3.10.3): clarify spec § 3.2 — VacationRequest split discarded (VacationPeriod is the balance)"
```

---

## Task 4: Define `ContractAmendment` model

**Files:** Create `apps/api/apps/contracts/models/contract_amendment.py`

Use Write tool with EXACT content:

```python
# -*- coding: utf-8 -*-
"""
Modelo ContractAmendment — Adendas a contratos laborales

Representa modificaciones a un Contract existente. Cada amendment se asocia
a un parent_contract via FK y captura solo los fields que cambian (salario,
cargo, horario, fecha de fin, etc.) — no duplica todos los campos del contrato.
"""

import uuid

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class ContractAmendment(models.Model):
    """
    Adenda a un contrato laboral.

    Una adenda modifica uno o más aspectos de un Contract activo:
    salario, cargo, horario, jornada o fecha de fin. Mantiene FK al
    contrato padre y guarda solo los nuevos valores que cambian.
    """

    TIPO_DOCUMENTO_CHOICES = [
        ('ADENDA_SALARIAL', 'Adenda Salarial'),
        ('ADENDA_CARGO', 'Adenda de Cambio de Cargo'),
        ('ADENDA_HORARIO', 'Adenda de Cambio de Horario'),
        ('ADENDA_EXTENSION', 'Adenda de Extension'),
    ]

    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('PENDIENTE', 'Pendiente de Firma'),
        ('ACTIVO', 'Activo'),
        ('VENCIDO', 'Vencido'),
        ('TERMINADO', 'Terminado'),
        ('ANULADO', 'Anulado'),
    ]

    JORNADA_CHOICES = [
        ('COMPLETA', 'Jornada Completa'),
        ('PARCIAL', 'Jornada Parcial'),
        ('REDUCIDA', 'Jornada Reducida'),
        ('FLEXIBLE', 'Jornada Flexible'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    parent_contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='amendments',
        help_text='Contrato padre al que esta adenda modifica',
    )

    numero_adenda = models.CharField(
        max_length=20,
        help_text='Número secuencial de la adenda dentro del parent_contract',
    )

    tipo_documento = models.CharField(
        max_length=25,
        choices=TIPO_DOCUMENTO_CHOICES,
        help_text='Tipo de adenda',
    )

    fecha_inicio = models.DateField(
        help_text='Fecha de inicio de vigencia de la modificacion',
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de fin de vigencia de la modificacion',
    )

    fecha_firma = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de firma de la adenda',
    )

    # Nuevos valores (solo el que aplica al tipo de adenda)
    nuevo_salario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Nuevo salario bruto (para ADENDA_SALARIAL)',
    )

    nuevo_cargo = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text='Nuevo cargo (para ADENDA_CARGO)',
    )

    nuevo_horario = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Nuevo horario (para ADENDA_HORARIO)',
    )

    nueva_jornada_laboral = models.CharField(
        max_length=15,
        choices=JORNADA_CHOICES,
        null=True,
        blank=True,
        help_text='Nueva jornada (para ADENDA_HORARIO)',
    )

    nueva_fecha_fin_contrato = models.DateField(
        null=True,
        blank=True,
        help_text='Nueva fecha de fin del contrato padre (para ADENDA_EXTENSION)',
    )

    motivo = models.TextField(
        null=True,
        blank=True,
        help_text='Motivo de la adenda',
    )

    observaciones = models.TextField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='BORRADOR',
        db_column='estado',
        help_text='Estado actual de la adenda',
    )

    documento_generado = models.FileField(
        upload_to='adendas/%Y/',
        null=True,
        blank=True,
        help_text='PDF de la adenda firmada',
    )

    # Auditoria
    created_by = models.ForeignKey(
        'identity.User',
        on_delete=models.PROTECT,
        related_name='adendas_creadas',
        null=True,
        blank=True,
        db_column='creado_por_id',
    )
    updated_by = models.ForeignKey(
        'identity.User',
        on_delete=models.PROTECT,
        related_name='adendas_modificadas',
        null=True,
        blank=True,
        db_column='modificado_por_id',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='fecha_creacion',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='fecha_modificacion',
    )

    class Meta:
        db_table = 'contract_amendments'
        unique_together = [['parent_contract', 'numero_adenda']]
        indexes = [
            models.Index(fields=['parent_contract']),
            models.Index(fields=['tipo_documento']),
            models.Index(fields=['status']),
            models.Index(fields=['fecha_inicio']),
        ]
        ordering = ['parent_contract', 'numero_adenda']

    def __str__(self):
        return f"{self.parent_contract.numero_contrato}-{self.numero_adenda} ({self.get_tipo_documento_display()})"
```

Verify file structure:
```bash
grep -nE "^class |^\s+id = |^\s+parent_contract = |^\s+numero_adenda = |^\s+tipo_documento = |db_table" apps/api/apps/contracts/models/contract_amendment.py
```

---

## Task 5: Update `Contract` model — remove ADENDA_* and `numero_adenda`

Read `apps/api/apps/contracts/models/contract.py` first to see exact current state.

Use Edit tool to apply 3 changes:

### Change 1: Remove ADENDA_* from TIPO_DOCUMENTO_CHOICES

Find the TIPO_DOCUMENTO_CHOICES list (around line 28-44) and remove the 4 ADENDA entries plus the `# Adendas` comment:

- old_string (the entire ADENDA section):
```python
        # D.Leg. 276
        ('LEY_276_INDETERMINADO', 'Ley 276 a Plazo Indeterminado'),
        # Adendas
        ('ADENDA_SALARIAL', 'Adenda Salarial'),
        ('ADENDA_CARGO', 'Adenda de Cambio de Cargo'),
        ('ADENDA_HORARIO', 'Adenda de Cambio de Horario'),
        ('ADENDA_EXTENSION', 'Adenda de Extension'),
    ]
```

- new_string:
```python
        # D.Leg. 276
        ('LEY_276_INDETERMINADO', 'Ley 276 a Plazo Indeterminado'),
    ]
```

### Change 2: Remove `numero_adenda` field

Read the file to see the exact declaration of `numero_adenda` (around line 89-93) and remove it entirely. The exact lines (including help_text) form the old_string.

- old_string (exact lines for `numero_adenda` declaration):
```python
    numero_adenda = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='Número de adenda (NULL si es contrato inicial)'
    )
```

- new_string: empty (just delete those lines)

To delete cleanly with Edit tool, replace with a single newline marker that gets the lines removed. Strategy: include 1 surrounding line for context.

Better approach: Use Edit with old_string including 2 surrounding lines and new_string keeping only those surrounding lines.

### Change 3: Remove `es_contrato_inicial` and `es_adenda` properties

Read around line 342-352 to see the properties.

- old_string (the two property blocks together, including the @property decorators):
```python
    @property
    def es_contrato_inicial(self):
        """Indica si es un contrato inicial (no adenda)."""
        return self.numero_adenda is None or self.numero_adenda == ''

    @property
    def es_adenda(self):
```

(continue with rest of `es_adenda` definition until the next method or end)

Read first to see exact structure, then apply Edit.

### Change 4: Update unique_together

In Meta:
- old_string: `unique_together = [['numero_contrato', 'numero_adenda']]`
- new_string: `unique_together = [['numero_contrato']]` OR set `numero_contrato` directly to `unique=True` field-level. Choose: change Meta line to:
```python
        # numero_contrato is unique on its own field (no need for unique_together)
```

Actually simplest: make `numero_contrato` field have `unique=True` (find the field declaration around line 87) and remove `unique_together` entirely.

### Change 5: Update `__str__` if it uses `numero_adenda`

Read the `__str__` method (around line 244-247):
```python
def __str__(self):
    if self.numero_adenda:
        return f"{self.numero_contrato}-{self.numero_adenda} - {self.empleado.nombre_completo}"
    ...
```

Simplify to:
```python
def __str__(self):
    return f"{self.numero_contrato} - {self.empleado.nombre_completo}"
```

### Verification

```bash
cd D:/VYNTIA/apps/api
echo "=== Contract.py post-cleanup ==="
echo "Remaining ADENDA_ in choices:"
grep -nE "ADENDA_" apps/contracts/models/contract.py || echo "OK: cero"
echo ""
echo "Remaining numero_adenda field:"
grep -nE "^\s+numero_adenda\s*=" apps/contracts/models/contract.py || echo "OK: cero"
echo ""
echo "Remaining es_adenda/es_contrato_inicial:"
grep -nE "es_adenda|es_contrato_inicial" apps/contracts/models/contract.py || echo "OK: cero"
echo ""
echo "TIPO_DOCUMENTO_CHOICES count (expected: 7 — CAS×3 + LEY_728×3 + LEY_276×1):"
grep -cE "^\s+\('(CAS_|LEY_)" apps/contracts/models/contract.py
cd D:/VYNTIA
```

Expected: `OK: cero` for all stale checks. 7 contract type choices.

---

## Task 6: Update `apps/contracts/models/__init__.py` re-exports

Read current state of `apps/api/apps/contracts/models/__init__.py`.

Use Edit tool to update content:

- old_string:
```python
"""Contracts models — re-exports for backward-compatible imports."""

from .contract import Contract
from .employment_data import EmploymentData

__all__ = [
    "Contract",
    "EmploymentData",
]
```

- new_string:
```python
"""Contracts models — re-exports for backward-compatible imports."""

from .contract import Contract
from .contract_amendment import ContractAmendment
from .employment_data import EmploymentData

__all__ = [
    "Contract",
    "ContractAmendment",
    "EmploymentData",
]
```

### Smoke import

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development'); import django; django.setup(); from apps.contracts.models import Contract, ContractAmendment, EmploymentData; print('OK')"
cd D:/VYNTIA
```

Expected: `OK`. If `manage.py check` complains about unmigrated changes, that's expected — Task 12 NUCLEAR DB regen handles it.

---

## Task 7: Update `app_rrhh/managers/contratos_manager.py`

This file is legacy code (will be cleaned up in L3.11) but its `.adendas()` method now references stale ADENDA_* choices that exist as a separate model. The `.contratos()` method has stale CONTRATO_* values that don't exist post-rename.

Read current state of the file.

Apply minimal cleanup (full removal is L3.11):

Use Edit tool:

### Change 1: Update `.contratos()` method

Replace the stale CONTRATO_* values list with the actual current Contract types:

- old_string:
```python
    def contratos(self):
        """Retorna solo los documentos de tipo contrato."""
        return self.filter(
            tipo_documento__in=[
                'CONTRATO_INDEFINIDO',
                'CONTRATO_FIJO',
                'CONTRATO_OBRA',
                'CONTRATO_HONORARIOS',
                'CONTRATO_PRACTICA'
            ]
        )
```

- new_string:
```python
    def contratos(self):
        """
        DEPRECATED post-L3.10.3: Contract model now contains only contracts
        (no amendments). All Contract instances are contracts; this filter
        is a no-op kept for backward compatibility.
        """
        return self.all()
```

### Change 2: Update `.adendas()` method

- old_string:
```python
    def adendas(self):
        """Retorna solo los documentos de tipo adenda."""
        return self.filter(
            tipo_documento__in=[
                'ADENDA_SALARIAL',
                'ADENDA_CARGO',
                'ADENDA_HORARIO',
                'ADENDA_EXTENSION'
            ]
        )
```

- new_string:
```python
    def adendas(self):
        """
        DEPRECATED post-L3.10.3: Amendments now live in apps.contracts.ContractAmendment.
        Returns empty queryset — callers should query ContractAmendment.objects directly.
        """
        return self.none()
```

### Verify

```bash
grep -A 6 "def contratos\|def adendas" D:/VYNTIA/apps/api/app_rrhh/managers/contratos_manager.py
```

---

## Task 8: Update `apps/time_off/services/vacation_calculation_service.py`

Lines 32 and 45 use `tipo_documento__startswith='CONTRATO'` to filter Contract for actual contracts. Since post-split Contract only contains contracts (no amendments), this filter is moot.

Read the file context first:
```bash
sed -n '25,55p' D:/VYNTIA/apps/api/apps/time_off/services/vacation_calculation_service.py
```

Apply Edit to remove the `tipo_documento__startswith='CONTRATO'` filter from both queries. The exact context will guide the Edit.

If the filter is `qs.filter(empleado=X, tipo_documento__startswith='CONTRATO')`, change to `qs.filter(empleado=X)`. Keep all other filters intact.

### Verify

```bash
grep -nE "tipo_documento__startswith" D:/VYNTIA/apps/api/apps/time_off/services/vacation_calculation_service.py || echo "OK: cero"
```

Expected: `OK: cero`.

---

## Task 9: Add `ContractAmendmentSerializer` and `ContractAmendmentViewSet`

**Files:** `apps/api/api/v1/rrhh/contratos_serializers.py`, `apps/api/api/v1/rrhh/contratos_views.py`, `apps/api/api/v1/rrhh/urls.py`

### Step 1: Update `contratos_serializers.py`

Read the current file. Apply 3 changes:

#### Change 1: Remove `numero_adenda`, `es_contrato_inicial`, `es_adenda` from existing Contract serializers

For `ContratosAdendasSerializer` (around line 22-83):
- Remove field references: `'numero_adenda'`, `'es_contrato_inicial'`, `'es_adenda'` from `Meta.fields` lists
- Remove the `es_contrato_inicial = serializers.ReadOnlyField()`, `es_adenda = serializers.ReadOnlyField()` field declarations

Same for `ContratosAdendasCreateSerializer` (around line 86-130) and `ContratosAdendasUpdateSerializer` (around line 142-167) — remove `'numero_adenda'` from their fields lists.

For `ContratosAdendasListSerializer` (around line 168+) — remove same.

Use Read to see exact current state, then Edit each Meta.fields list.

#### Change 2: Add new `ContractAmendmentSerializer`

At the end of the file (or after the existing serializers), add:

```python


class ContractAmendmentSerializer(serializers.ModelSerializer):
    """Serializer para adendas contractuales."""

    parent_contract_numero = serializers.CharField(
        source='parent_contract.numero_contrato', read_only=True
    )
    parent_contract_empleado = serializers.CharField(
        source='parent_contract.empleado.nombre_completo', read_only=True
    )
    tipo_documento_texto = serializers.CharField(
        source='get_tipo_documento_display', read_only=True
    )
    estado_texto = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = ContractAmendment
        fields = [
            'id', 'parent_contract', 'parent_contract_numero', 'parent_contract_empleado',
            'numero_adenda', 'tipo_documento', 'tipo_documento_texto',
            'fecha_inicio', 'fecha_fin', 'fecha_firma',
            'nuevo_salario', 'nuevo_cargo', 'nuevo_horario', 'nueva_jornada_laboral',
            'nueva_fecha_fin_contrato',
            'motivo', 'observaciones', 'status', 'estado_texto',
            'documento_generado',
            'created_at', 'updated_at',
            'created_by', 'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
```

Add the import at the top of the file:
- old (likely): `from apps.contracts.models import Contract, EmploymentData`
- new: `from apps.contracts.models import Contract, ContractAmendment, EmploymentData`

(Or whatever the existing import line is — match it exactly.)

#### Change 3: Verify

```bash
cd D:/VYNTIA/apps/api
echo "=== Stale 'numero_adenda' / 'es_adenda' in serializers (should be 0 in fields lists) ==="
grep -nE "'numero_adenda'|'es_contrato_inicial'|'es_adenda'" api/v1/rrhh/contratos_serializers.py || echo "OK: cero"
echo "=== ContractAmendmentSerializer present ==="
grep -n "class ContractAmendmentSerializer" api/v1/rrhh/contratos_serializers.py
cd D:/VYNTIA
```

### Step 2: Update `contratos_views.py`

Read current state.

#### Change 1: Update `ContratosAdendasViewSet` to query Contract only (no amendments)

Find any filtering that relied on `tipo_documento` mixing contracts and amendments. The current ViewSet around lines 100-110, 220-225 has `filter(tipo_documento=tipo_documento)` from query params. This still works post-split (Contract only has contract types now). No change needed there.

But the queryset name `contratos_adendas` is now misleading. Rename related context if useful, but for minimal change just leave as-is.

#### Change 2: Add `ContractAmendmentViewSet`

At the end of the file, add a new ViewSet:

```python


class ContractAmendmentViewSet(viewsets.ModelViewSet):
    """ViewSet para CRUD de adendas contractuales."""

    queryset = ContractAmendment.objects.select_related(
        'parent_contract', 'parent_contract__empleado'
    ).all()
    serializer_class = ContractAmendmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        parent_contract_id = self.request.query_params.get('parent_contract')
        if parent_contract_id:
            qs = qs.filter(parent_contract_id=parent_contract_id)
        empleado_id = self.request.query_params.get('empleado')
        if empleado_id:
            qs = qs.filter(parent_contract__empleado_id=empleado_id)
        return qs.order_by('-created_at')
```

Add imports at top:
- `from apps.contracts.models import ContractAmendment` (if not already imported)
- `from .contratos_serializers import ContractAmendmentSerializer` (or whatever the relative import pattern is)

#### Change 3: Verify

```bash
grep -n "class ContractAmendmentViewSet\|class ContratosAdendasViewSet" D:/VYNTIA/apps/api/api/v1/rrhh/contratos_views.py
```

### Step 3: Register `ContractAmendmentViewSet` in URL conf

Read `apps/api/api/v1/rrhh/urls.py` to see the router pattern.

Add a new router registration:
```python
from .contratos_views import ContratosAdendasViewSet, ContractAmendmentViewSet

router.register(r'adendas', ContractAmendmentViewSet, basename='contract-amendment')
```

### Smoke check

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd D:/VYNTIA
```

May fail because migrations don't yet exist for ContractAmendment — Task 12 NUCLEAR regen handles. If failure mentions `ContractAmendmentSerializer` or `ContractAmendmentViewSet` import error, fix the import path.

---

## Task 10: Update `template_service.py` and `document_generation_views.py`

Both use `Contract` for `generar_adenda()` calls. After split, amendments are `ContractAmendment` instances.

### Step 1: Inspect

```bash
cd D:/VYNTIA/apps/api
echo "=== template_service.generar_adenda usage ==="
grep -nB2 -A 8 "def generar_adenda\|generar_adenda(" apps/documents/services/template_service.py | head -30
echo ""
echo "=== document_generation_views generar_adenda ==="
grep -nB2 -A 30 "def generar_adenda" api/v1/app_rrhh/document_generation_views.py | head -50
cd D:/VYNTIA
```

### Step 2: Update `template_service.py`

The `generar_adenda` method takes an ID and queries Contract. Update to query ContractAmendment.

Read the function. The change is:
- `Contract.objects.get(id=adenda_id)` → `ContractAmendment.objects.get(id=adenda_id)`

Apply Edit.

Add import at top if needed:
- `from apps.contracts.models import ContractAmendment` (if not present)

### Step 3: Update `document_generation_views.py`

Around line 210: `adenda = get_object_or_404(Contract, contrato_id=adenda_id)` — needs to be `get_object_or_404(ContractAmendment, id=adenda_id)`.

Around line 213-222: `template_service.generar_adenda(adenda.pk, tipo_adenda=adenda.tipo_documento)` — `adenda` is now ContractAmendment instance. The method signature stays.

Around line 227: `nombre_doc = f"Adenda {adenda.numero_adenda or adenda.pk}"` — `numero_adenda` exists on ContractAmendment, OK.

Around line 230: `empleado=adenda.empleado` — ContractAmendment has no direct `empleado`; use `adenda.parent_contract.empleado`.

Apply Edits. Add import at top:
- `from apps.contracts.models import Contract, ContractAmendment`

### Verify

```bash
cd D:/VYNTIA/apps/api
grep -nE "ContractAmendment|adenda\.empleado|adenda\.parent_contract" \
  apps/documents/services/template_service.py \
  api/v1/app_rrhh/document_generation_views.py | head -20
cd D:/VYNTIA
```

---

## Task 11: Update tests

**File:** `apps/api/tests/test_contratos_integration.py`

Tests that create amendments with `tipo_documento='ADENDA_*'` on Contract now need to create ContractAmendment instances.

### Step 1: Inspect tests

```bash
cd D:/VYNTIA/apps/api
echo "=== Tests with ADENDA_* type creation ==="
grep -nB1 -A 8 "tipo_documento.*ADENDA\|numero_adenda" tests/test_contratos_integration.py | head -40
echo ""
echo "=== Tests with es_adenda or es_contrato_inicial ==="
grep -nE "es_adenda|es_contrato_inicial" tests/test_contratos_integration.py
cd D:/VYNTIA
```

### Step 2: Update tests

For each test that creates a Contract with `tipo_documento='ADENDA_*'` or sets `numero_adenda='X'`:

Convert to creating a ContractAmendment instance. Example transformation:

- old test code:
```python
adenda = Contract.objects.create(
    empleado=self.empleado,
    area=self.area,
    numero_contrato='CONT-001',
    numero_adenda='A001',
    tipo_documento='ADENDA_SALARIAL',
    fecha_inicio='2026-01-01',
    salario_bruto=2500.00,
    ...
)
```

- new test code:
```python
adenda = ContractAmendment.objects.create(
    parent_contract=self.contrato_principal,
    numero_adenda='A001',
    tipo_documento='ADENDA_SALARIAL',
    fecha_inicio='2026-01-01',
    nuevo_salario=Decimal('2500.00'),
    motivo='Aumento de sueldo',
    ...
)
```

Add `from apps.contracts.models import ContractAmendment` to test imports if not present.

For tests using `es_adenda`/`es_contrato_inicial` properties on Contract — replace with model-level discrimination (instance is Contract or ContractAmendment).

### Verify

```bash
cd D:/VYNTIA/apps/api
grep -nE "ADENDA_|numero_adenda|es_adenda|es_contrato_inicial" tests/test_contratos_integration.py | head -10
cd D:/VYNTIA
```

Acceptable matches: now references should be to ContractAmendment.tipo_documento and ContractAmendment.numero_adenda. Stale references on Contract are bugs.

---

## Task 12: NUCLEAR DB regenerate

### Step 1: Drop bd_vyntia (kill procs first)

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "DROP DATABASE IF EXISTS bd_vyntia;" 2>&1
```

### Step 2: Eliminar migration files (8 apps)

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
git status --short | grep migrations | head -15
```

### Step 3: Recrear bd_vyntia

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

Expected: contracts app has 0001_initial.py with BOTH `Contract` and `ContractAmendment` models.

### Step 5: Verify

```bash
cd D:/VYNTIA/apps/api
echo "=== Contract + ContractAmendment in contracts migration ==="
grep -E "name='Contract|name='ContractAmendment|db_table" apps/contracts/migrations/0001_initial.py | head -15
echo ""
echo "=== ADENDA_* count in Contract migration (should be 0) ==="
grep -hE "ADENDA_" apps/contracts/migrations/0001_initial.py | wc -l
cd D:/VYNTIA
```

Expected: `name='Contract'` and `name='ContractAmendment'`, `db_table='contratos_adendas'` for Contract, `db_table='contract_amendments'` for ContractAmendment. ADENDA_* count = 4 (only in ContractAmendment choices).

### Step 6: Aplicar migraciones

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -25
cd D:/VYNTIA
```

Expected: all apps migrate clean.

### Step 7: Verify physical schema

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "\dt" 2>&1 | grep -E "contratos|contract" | head -5
echo ""
echo "=== contract_amendments columns ==="
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "\d contract_amendments" 2>&1 | head -25
```

Expected:
- Table `contratos_adendas` (Contract): no `numero_adenda` column anymore
- Table `contract_amendments` (ContractAmendment): with `parent_contract_id`, `numero_adenda`, `tipo_documento`, etc.

### Step 8: Reseed

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py setup_roles_permisos --settings=vyntia.settings.development 2>&1 | tail -5
PGPASSWORD='Demenci4@' python manage.py seed_menu --settings=vyntia.settings.development 2>&1 | tail -5
cd D:/VYNTIA
```

Verify:
```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'rol' AS t, COUNT(*) FROM rol UNION ALL SELECT 'permiso', COUNT(*) FROM permiso UNION ALL SELECT 'modulos', COUNT(*) FROM modulos;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0.

---

## Task 13: Smoke tests

### Step 1: Django check

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: `System check identified no issues (0 silenced).`

If error mentions `numero_adenda`, `es_adenda`, `es_contrato_inicial` references, find them in production code and fix iteratively.

### Step 2: pytest

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: `161 passed, 8 failed, 3 skipped` (baseline preservado) OR improved.

If tests fail with patterns like:
- `Contract has no field 'numero_adenda'` → Fix the test that still uses old field
- `ContractAmendment.objects has no method` → Fix the test using ContractAmendment incorrectly
- `tipo_documento contains 'ADENDA_SALARIAL'` rejected as choice → Fix test creating Contract with ADENDA_* type (should create ContractAmendment instead)

Iterate fixes until baseline restored.

### Step 3: runserver smoke

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l3103.log 2>&1 &
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

Expected: `HTTP 200 /api/docs/`. If 500, schema generation broken.

### Step 4: Final stale check

```bash
cd D:/VYNTIA/apps/api
echo "=== Stale 'numero_adenda' references in Contract context (should not exist) ==="
grep -rEn "Contract\.[a-zA-Z_]*\.numero_adenda|contrato\.numero_adenda" \
  --include="*.py" apps tests app_rrhh api 2>/dev/null \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | head -10 || echo "OK: cero"
echo ""
echo "=== Stale ADENDA_* in tipo_documento Contract context ==="
grep -rEn "Contract\.objects\.create.*tipo_documento.*ADENDA\|Contract\.objects\.filter.*tipo_documento.*ADENDA" \
  --include="*.py" apps tests app_rrhh api 2>/dev/null \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | head -10 || echo "OK: cero"
cd D:/VYNTIA
```

Expected: both `OK: cero` (or only ContractAmendment context refs, which are correct).

---

## Task 14: Atomic commit

```bash
cd D:/VYNTIA
git status --short | head -30
git add apps/api/
git commit -m "$(cat <<'EOF'
chore(L3.10.3): split Contract into Contract + ContractAmendment

Contract model:
- Removed ADENDA_* values from TIPO_DOCUMENTO_CHOICES (keep only CAS_*, LEY_728_*, LEY_276_*)
- Removed numero_adenda field
- Removed es_contrato_inicial and es_adenda properties (no longer needed)
- numero_contrato now unique=True at field level

ContractAmendment model (NEW):
- Lives at apps/contracts/models/contract_amendment.py
- FK parent_contract → Contract (CASCADE)
- Fields: numero_adenda, tipo_documento (only ADENDA_*), fecha_inicio, fecha_fin,
  fecha_firma, nuevo_salario, nuevo_cargo, nuevo_horario, nueva_jornada_laboral,
  nueva_fecha_fin_contrato, motivo, observaciones, status, documento_generado, audit
- db_table='contract_amendments' (new physical table, English name)
- unique_together(parent_contract, numero_adenda)

Consumer updates:
- contratos_serializers.py: ContractAmendmentSerializer added; numero_adenda/es_*
  removed from Contract serializers
- contratos_views.py: ContractAmendmentViewSet added (read-only, filterable by
  parent_contract or empleado); ContratosAdendasViewSet now returns Contract only
- urls.py: registered /api/v1/rrhh/adendas/ endpoint
- app_rrhh/managers/contratos_manager.py: .contratos() and .adendas() deprecated
  (.contratos() is no-op, .adendas() returns empty queryset — callers should use
  ContractAmendment.objects directly; full removal in L3.11)
- vacation_calculation_service.py: removed stale tipo_documento__startswith='CONTRATO'
  filter (Contract now contains only contracts)
- template_service.generar_adenda() and document_generation_views.generar_adenda()
  now query ContractAmendment instead of Contract for amendment IDs
- tests/test_contratos_integration.py: amendment creation moved to ContractAmendment

VacationRequest split discarded — VacationPeriod already serves as the balance
(see spec § 3.2.1 clarification).

NUCLEAR DB regen: bd_vyntia recreated. Tables 'contratos_adendas' (Contract,
contracts only) + 'contract_amendments' (ContractAmendment) coexist.

LR21 nueva: model split requires updating consumers that queried unified model
to query split models separately. Defensive grep for hardcoded tipo_documento
choice lists (e.g., manager methods filtering by ADENDA_*) is mandatory.

Pytest baseline preservado: 161 passed, 8 failed, 3 skipped.
manage.py check clean. /api/docs/ HTTP 200.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Verify:
```bash
git log --oneline vyntia/L3.10.3-contract-split ^master
git status --short
```

Expected: 3 commits (`docs(L3.10.3) plan`, `docs(L3.10.3) spec clarification`, `chore(L3.10.3)`), `git status` clean.

---

## Task 15: Merge a master + roadmap update

- [ ] **Confirmar autorización del usuario.**

```bash
git checkout master
git merge --no-ff vyntia/L3.10.3-contract-split -m "Merge L3.10.3: split Contract into Contract + ContractAmendment"
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

### Update roadmap

Edit `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`:
- L3.10.3 → ✅ merged `<sha>` 2026-04-XX
- L3.10.4 → ⏳ NEXT

Update memory `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- Document L3.10.3 completion
- Update "Próximo paso" → L3.10.4 frontend rename

Commit:
```bash
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.10.3): mark L3.10.3 merged, L3.10.4 (frontend rename) as next"
```

---

## Después de L3.10.3

**Próximo plan:** L3.10.4 — frontend rename. Es el último sub-PR de L3.10:
- 14 services TS (`contratosService.ts` → `contractsService.ts`, etc.)
- Tipos TS (`empleado_id: number` → `id: string` UUID, `fecha_creacion → created_at`, etc.)
- API URL paths nuevos (`/api/v1/employees/`, `/api/v1/contracts/`, `/api/v1/contracts/{id}/amendments/`, etc.)
- Eliminar redirects 301 legacy de L3.2-L3.9 cuando ya no se necesiten
- Coordinar con apps/web/ React refactor

Después L3.11 (cleanup `app_rrhh/`).

---

## Notas para el ejecutor

- **NUCLEAR DB regen** sigue siendo el patrón. bd_vyntia tiene 0 contratos así que data migration es trivial.
- **`db_table` ES preservado en Contract** (`contratos_adendas`) — consistencia con L3.10.1. ContractAmendment usa nombre físico EN (`contract_amendments`) por ser tabla nueva.
- **`db_column` ES preservado en audit fields** de ContractAmendment (`fecha_creacion`, `fecha_modificacion`, `creado_por_id`, `modificado_por_id`, `estado`) per patrón L3.10.2.
- **PK de ContractAmendment es UUID** (consistencia L3.10.2).
- **Inbound FK `VacationPeriod.contrato → 'contracts.Contract'`** preservado — apunta a parent contract, no amendment. No requiere cambio.
- **ContractAmendmentViewSet endpoints:** `/api/v1/rrhh/adendas/` (legacy URL prefix). Nueva URL `/api/v1/contracts/{id}/amendments/` se agrega en L3.10.4 cuando frontend se actualice.
- **Frontend romperá** parcialmente: `/api/v1/rrhh/contratos/` ya no devuelve adendas mezcladas. Frontend debe llamar `/api/v1/rrhh/adendas/` separadamente. Defer a L3.10.4.
- **Tests integration:** crear Contract con choices `LEY_728_FIJO`/`CAS_DETERMINADO`/etc., crear ContractAmendment con choices `ADENDA_*` y `parent_contract` FK.
- **Lecciones aplicadas** (LR9-LR21): el split usa el patrón conocido; defensive greps en cada Task.
