# B.8 MPP + CPE + CAP Implementation Plan (SERVIR / Ley 30057 + DL 276/728)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Land Module 02 public-sector compliance — Cuadro de Puestos de la Entidad (CPE — Ley 30057 SERVIR), Manual de Perfiles de Puestos (MPP — Ley 30057 SERVIR), Cuadro de Asignación de Personal (CAP — DL 276/728 transitional régimen). Extend Position with SERVIR-specific fields. Generate MPP as on-demand PDF from CPE + PositionProfile.

**Architecture:** Single `PositionRegister` model serves both CPE and CAP variants via `register_type` discriminator. Child rows in `PositionRegisterEntry` carry both Ley 30057 fields (grupo_servidor, nivel_remunerativo, familia_puesto) and DL 276/728 fields (clasificacion_cap) — nullable, populated based on register_type. MPP is a rendering of CPE entries × PositionProfile (B.6) — no separate model. Position extended with `servir_group`, `servir_level`, `salary_tier` (all nullable, populated for public-sector tenants). UI-only sector gate via `useTenantSector()` hook (inverted from B.7: shows for public tenants).

**Branch:** `vyntia/B8-mpp-cpe`
**Backlog items in scope:** #107 (MPP), #108 (CPE — Ley 30057), #109 (CAP — DL 276/728, P2).
**User-confirmed scope decisions (2026-05-10):**
- All 3 documents (CPE + MPP + CAP) in B.8 (~2 weeks per roadmap).
- MPP rendered on-demand PDF from CPE + PositionProfile (no separate model).
- Position extended with SERVIR fields nullable (single source of truth).

**Out of scope (deferred):**
- SERVIR external registration API integration (manual process today) → post-B.
- Concurso público workflow (selection process under Ley 30057) → B.9 (Selección).
- Compensación priorizada / ajustada calculations → D (Vyntia Pay).
- Transition tracking (servidor migrating 276 → 30057) → B.10 (Vinculación).

**Test baselines (post-B.7 SHA `28265dcf`):**
- pytest 439/1/17, vitest 10/52, ESLint 278, tsc 1 (BlankEnum), build clean.

After B.8:
- pytest **460+/1/17** (~22 new tests across Position SERVIR fields + Register model + entries + PDF rendering + API).
- vitest **11+ files / 58+ tests** (publicPositionService + page snapshots).
- ESLint: held flat.

---

## Task 1: Branch + plan + scaffold

Branch already created. Place plan, commit, capture baselines.

---

## Task 2: Extend Position with SERVIR fields + system-wide reference

**Files:**
- `apps/api/apps/organization/models/position.py` — add `servir_group`, `servir_level`, `salary_tier`
- `apps/api/apps/organization/models/servir_classification.py` — new ServirGroup + ServirLevel reference models (system-wide, seeded)
- `apps/api/apps/organization/management/commands/seed_servir_data.py`

**Position additions:**
```python
SERVIR_GROUP_CHOICES = [
    ('fp', 'Funcionario Público'),
    ('dp', 'Directivo Público'),
    ('cc', 'Servidor Civil de Carrera'),
    ('cs', 'Servidor de Actividades Complementarias'),
    ('cf', 'Servidor de Confianza'),
]

# Ley 30057 carrera levels: CF-1..CF-4 (civil de carrera) + DP-1..DP-4 (directivo público)
SERVIR_LEVEL_CHOICES = [
    ('cf_1', 'CF-1 (Inicial)'),
    ('cf_2', 'CF-2 (Intermedio)'),
    ('cf_3', 'CF-3 (Avanzado)'),
    ('cf_4', 'CF-4 (Senior)'),
    ('dp_1', 'DP-1'),
    ('dp_2', 'DP-2'),
    ('dp_3', 'DP-3'),
    ('dp_4', 'DP-4'),
]

# D.S. 138-2014-EF compensation tier
SALARY_TIER_CHOICES = [
    ('principal', 'Principal'),
    ('ajustada', 'Ajustada'),
    ('priorizada', 'Priorizada'),
]

servir_group = models.CharField(max_length=10, choices=SERVIR_GROUP_CHOICES,
                                 null=True, blank=True, db_index=True)
servir_level = models.CharField(max_length=10, choices=SERVIR_LEVEL_CHOICES,
                                 null=True, blank=True)
salary_tier = models.CharField(max_length=20, choices=SALARY_TIER_CHOICES,
                                null=True, blank=True)
familia_puesto = models.CharField(max_length=100, null=True, blank=True,
                                   help_text='SERVIR familia de puestos.')
```

Migration: `organization.0009_b8_position_servir_fields`.

Tests: smoke create Position with SERVIR fields populated; backward compat (null on private tenant Position).

Commit:
```
feat(B8): extend Position with SERVIR fields (servir_group/level, salary_tier, familia)
```

---

## Task 3: Create PositionRegister + PositionRegisterEntry models

**Files:**
- `apps/api/apps/organization/models/position_register.py`
- `apps/api/apps/organization/models/position_register_entry.py`

**PositionRegister (CPE + CAP):**
```python
class PositionRegister(models.Model):
    REGISTER_TYPE_CHOICES = [
        ('cpe', 'Cuadro de Puestos de la Entidad (Ley 30057 SERVIR)'),
        ('cap', 'Cuadro de Asignación de Personal (DL 276/728)'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('approved', 'Aprobado'),
        ('registered_servir', 'Registrado SERVIR'),  # post-approval external registration
        ('superseded', 'Reemplazado'),
        ('archived', 'Archivado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                                null=True, blank=True, db_index=True, related_name='+')

    register_type = models.CharField(max_length=10, choices=REGISTER_TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Versioning per ADR-B.7
    version = models.PositiveIntegerField(default=1)
    parent_version = models.ForeignKey('self', on_delete=models.PROTECT,
                                        null=True, blank=True, related_name='successors')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft',
                               db_index=True)
    effective_date = models.DateField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('identity.User', on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='+')

    # SERVIR external registration tracking
    servir_registered_at = models.DateTimeField(null=True, blank=True)
    servir_registration_ref = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('identity.User', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='+')

    def approve(self, *, user, effective_date=None):
        """Mark register as approved. Sets approved_at/by + effective_date."""
        ...
    
    def register_in_servir(self, *, reference):
        """Mark CPE as externally registered in SERVIR (manual process)."""
        if self.register_type != 'cpe':
            raise ValidationError("Solo CPE se registra en SERVIR")
        ...
```

**PositionRegisterEntry (rows):**
```python
class PositionRegisterEntry(models.Model):
    CAP_CLASSIFICATION_CHOICES = [
        ('fp', 'FP - Funcionario Público'),
        ('ec', 'EC - Empleado de Confianza'),
        ('sp_ds', 'SP-DS - Directivo Superior'),
        ('sp_ej', 'SP-EJ - Ejecutivo'),
        ('sp_es', 'SP-ES - Especialista'),
        ('sp_ap', 'SP-AP - Apoyo'),
        ('re', 'RE - Régimen Especial'),
    ]
    SITUATION_CHOICES = [
        ('ocupada', 'Ocupada'),
        ('vacante', 'Vacante'),
        ('prevista', 'Prevista'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    register = models.ForeignKey('organization.PositionRegister',
                                  on_delete=models.CASCADE, related_name='entries')
    position = models.ForeignKey('organization.Position', on_delete=models.PROTECT,
                                  related_name='register_entries')

    # Generic entry metadata
    sequence = models.PositiveIntegerField(default=0)
    plaza_code = models.CharField(max_length=30, blank=True)
    plaza_count = models.PositiveIntegerField(default=1)
    situacion = models.CharField(max_length=20, choices=SITUATION_CHOICES, default='vacante')

    # CPE-specific (when register.register_type='cpe')
    nivel_organizacional = models.CharField(max_length=100, blank=True)
    nivel_remunerativo = models.CharField(max_length=50, blank=True)

    # CAP-specific (when register.register_type='cap')
    clasificacion_cap = models.CharField(max_length=10, choices=CAP_CLASSIFICATION_CHOICES,
                                          blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Migration: `organization.0010_b8_position_register`.

Tests: create CPE register + add entries; approve workflow; register_in_servir only on CPE; CAP cannot be servir-registered.

Commit:
```
feat(B8): PositionRegister + PositionRegisterEntry (CPE + CAP)
```

---

## Task 4: MPP rendering service

**Files:**
- `apps/api/apps/organization/services/mpp_service.py`

```python
def render_mpp_html(*, register_id: str, tenant=None) -> str:
    """Render the Manual de Perfiles de Puestos as HTML.

    Args:
        register_id: UUID of a CPE PositionRegister.
        tenant: Tenant for institution data.

    Returns:
        HTML string ready to convert to PDF.
    """
    from apps.organization.models import PositionRegister
    register = PositionRegister.objects.select_related('approved_by').get(
        pk=register_id, register_type='cpe'
    )
    entries = register.entries.select_related(
        'position',
        'position__profile',
        'position__department',
        'position__occupational_category',
    ).prefetch_related(
        'position__functions',
        'position__requirements',
    ).order_by('sequence')

    # Render via existing Django template at apps/api/templates/mpp/mpp.html
    return render_to_string('mpp/mpp.html', {
        'register': register,
        'entries': entries,
        'institucion': _resolve_institution(tenant),
    })


def render_mpp_pdf(*, register_id: str, tenant=None) -> bytes:
    """Convert MPP HTML to PDF via existing PDFGenerator infrastructure."""
    html = render_mpp_html(register_id=register_id, tenant=tenant)
    from apps.documents.services import PDFGenerator
    return PDFGenerator()._html_to_pdf(html)
```

Template: `apps/api/templates/mpp/mpp.html` — institutional header + per-Position profile sections (mission, functions, requirements, salary tier).

Tests: smoke render with a fake CPE register; verify HTML contains expected Position data.

Commit:
```
feat(B8): MPP rendering service (HTML + PDF from CPE + PositionProfile)
```

---

## Task 5: API ViewSets + URL routing

**Files:**
- `apps/api/api/v1/organization/views.py` — add PositionRegisterViewSet + PositionRegisterEntryViewSet + MPP download view
- `apps/api/api/v1/organization/serializers.py` — add 4 serializers
- `apps/api/api/v1/organization/urls.py` — register new routes

Routes (under `/api/v1/organization/`):
- `position-registers/` — PositionRegisterViewSet (CRUD + `/approve/` + `/register-in-servir/`)
- `position-register-entries/` — PositionRegisterEntryViewSet (CRUD)
- `position-registers/<id>/mpp-pdf/` — download MPP as PDF
- `position-registers/<id>/mpp-html/` — render MPP as HTML preview

Permission gating: RRHHPermission + TenantAwareViewSetMixin.

Tests: smoke routing + auth + custom actions.

Commit:
```
feat(B8): API surface for CPE/CAP + MPP rendering
```

---

## Task 6: Frontend service + types

**Files:**
- `apps/web/src/features/organization/services/publicPositionService.ts`
- `apps/web/src/features/organization/services/index.ts` (extend)

Methods:
- `listRegisters(type?: 'cpe' | 'cap')`, `getRegister(id)`, `createRegister`, `approveRegister`, `registerInServir(id, ref)`
- `listEntries(registerId)`, `upsertEntry`
- `downloadMPP(registerId)` (blob)

Vitest tests (≥6).

Commit:
```
feat(B8): frontend service publicPositionService.ts
```

---

## Task 7: Frontend pages (public-sector gated)

**Files:**
- `apps/web/src/features/organization/pages/PositionRegisterListPage.tsx` — list with `?type=cpe|cap` tabs
- `apps/web/src/features/organization/pages/PositionRegisterEditorPage.tsx` — header + entries table + Approve/Register-SERVIR actions + Download MPP button
- Route registration in App.tsx: `/organizacion/registros/{cpe,cap}` (AdminRoute, lazy)
- Sector gate: shows for `useTenantSector() === 'public'`, info card otherwise (inverted from B.7)

Commit:
```
feat(B8): frontend CPE + CAP admin pages + MPP download (public-sector gated)
```

---

## Task 8: Final verification + merge

Verify baselines (pytest 460+, vitest 11+ files, ESLint 278, tsc 1, build clean, manage.py check 0).
Update memory + test_baselines.
Merge to master with comprehensive message.

---

## Self-Review

| # | Item | Task |
|---|---|---|
| 107 | MPP — sector público SERVIR | Tasks 4, 7 |
| 108 | CPE — Ley 30057 SERVIR | Tasks 3, 5, 7 |
| 109 | CAP — 276/728 público | Tasks 3, 5, 7 |
| ADR-B.6 sector gating | UI-only via useTenantSector() (inverted: public-only) | Task 7 |
| ADR-B.7 versioning | PositionRegister inline version + parent_version + status | Task 3 |
| Position single source of truth | SERVIR fields nullable on Position | Task 2 |

**Deferred:** SERVIR external API integration (manual today), concurso público workflow (B.9), compensación calculations (D), transition tracking (B.10).
