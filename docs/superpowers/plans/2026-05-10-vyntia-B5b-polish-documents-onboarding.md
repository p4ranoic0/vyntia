# B.5b Polish Documents + Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Polish the documents and onboarding bounded contexts — fix the long list of L3.10.x/L3.11 stale consumer bugs in `DocumentGenerationViewSet`, `TemplateService`, `WordTemplateService`, `pdf_generator`; rebrand 5 email templates from "Intranet" to "VYNTIA"; close `OnboardingService.reenviar_email_bienvenida` lookup bug; harden onboarding ViewSet/Service tenant scoping; migrate `OnboardingViewSet` and `DocumentGenerationViewSet` to their bounded-context modules; lint-clean `features/onboarding`+`features/documents`; co-locate document/onboarding tests into per-app `tests/` dirs.

**Architecture:** Pure bug-fix + cleanup wave. Affects:
- `apps/api/api/v1/app_rrhh/document_generation_views.py` → migrated to `apps/api/api/v1/documents/views.py`
- `apps/api/api/v1/rrhh/views.py` (OnboardingViewSet section) → moved to `apps/api/api/v1/onboarding/views.py`
- `apps/api/apps/documents/services/{template_service,word_template_service,pdf_generator}.py` (stale field refs)
- `apps/api/apps/onboarding/services/onboarding_service.py` (lookup field, tenant scoping)
- `apps/api/templates/emails/*.{html,txt}` (rebrand "Intranet" → "VYNTIA")
- `apps/web/src/features/onboarding/`+`features/documents/` (lint cleanup)
- `apps/api/apps/{documents,onboarding}/tests/` (test co-location, partial — items #86)

No new infrastructure (TenantAwareViewSetMixin and TenantStorage already shipped in B.1).

**Branch:** `vyntia/B5b-polish-documents-onboarding`
**Backlog items in scope:** #22, #23, #24, #25, #26, #27, #28, #29, #30, #31, #32, #33, #80, #81, #82, #83, #84, #85, #86 + lint piece of #90 (~17 items, P0–P2). The #76, #77, #78, #79 from documents are also addressed inline.
**Out of scope:**
- Per-tenant `frontend_url` (subdomain routing) — depends on C.4 deployment, deferred.
- Username uniqueness scoped `(tenant, username)` — coordinated as part of identity B.2 in a future polish round (Role tenant lookup is what we fix here in #81).
- ESLint warnings outside `features/onboarding`+`features/documents` — covered by other B.x phases.
- DocumentTemplate ambiguity (system-wide vs per-tenant) #79 — design ADR, deferred until first real consumer needs it.

**Test baselines (post-B.5 SHA `c5e152d1`):**
- pytest **337/3/17** (3 fails: 2 onboarding bugs we will fix here + 1 unrelated `test_permisos_debug`).
- vitest 7 files / 32, ESLint **291** (273 err / 18 warn), tsc 1 (`BlankEnum.ts` pre-existing), build clean.

After B.5b:
- pytest **339+/1/17** (test_corregir_correo + test_employee_cannot_patch_restricted_fields turn green; new tests landed for fixes in this phase).
- ESLint dropped by ~14 (target: <280).

---

## Task 1: Branch + plan + per-app tests dir scaffolding

```bash
cd D:/VYNTIA
git checkout -b vyntia/B5b-polish-documents-onboarding   # already created
git add docs/superpowers/plans/2026-05-10-vyntia-B5b-polish-documents-onboarding.md
git commit -m "docs(B5b): plan for polish documents + onboarding (~17 backlog items in scope)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"

# Co-locate test dirs per #86
mkdir -p apps/api/apps/documents/tests apps/api/apps/onboarding/tests
touch apps/api/apps/documents/tests/__init__.py
touch apps/api/apps/onboarding/tests/__init__.py
```

Capture pytest baseline 337/3/17. Capture ESLint baseline 291.

---

## Task 2: Fix `DocumentGenerationViewSet` stale field refs (#22, #23, #24, #25, #26, #27)

**Files:** `apps/api/api/v1/app_rrhh/document_generation_views.py` (will be migrated to documents in Task 11; fix in place first to keep diff isolation).

Bugs (per BACKLOG audit):
- **#22** line 110: `Contract.objects.get(contrato_id=contrato_id)` — Contract has no `contrato_id` field post-rename. PK is `id` UUID. Fix: `get_object_or_404(Contract, pk=contrato_id)`.
- **#23** line 318: same pattern for Employee — `Employee.objects.get(empleado_id=...)`. Fix: `pk=empleado_id`.
- **#24** lines 148, 245, 367, 474, 740: 5 callsites of `documento.documento_id` — `DigitalDocument` PK is `id` UUID. Fix: `documento.id` (or `documento.pk`).
- **#25** line 595: `creada_por=request.user` — `DocumentTemplate` model uses `created_by`, not `creada_por`. Fix: `created_by=request.user`.
- **#26** URL regex on `eliminar_plantilla_word`/`descargar_plantilla_word`: kwargs use `[0-9]+` regex but PK is UUID. Fix: change URL regex to UUID pattern OR drop the regex constraint and rely on action signature (default DRF action handles UUID).
- **#27** lines 667-668 in `generar_desde_plantilla_word`: `empleado_id = request.data.get("id")` AND `contrato_id = request.data.get("id")` BOTH read the same `id` query param. Fix: read distinct params (`empleado_id`, `contrato_id`).

**Verification (current state):**

```bash
grep -n "contrato_id=contrato_id\|empleado_id=empleado_id\|documento.documento_id\|creada_por=" apps/api/api/v1/app_rrhh/document_generation_views.py
```

Expected matches (before fix): line 110, 148, 245, 318, 367, 474, 595, 740 + #27 ambiguity around 667-668.

**Tests (apps/api/apps/documents/tests/test_document_generation_viewset.py):**

```python
"""Tests for DocumentGenerationViewSet stale-consumer fixes (B.5b #22-#27)."""
import inspect


class TestDocumentGenerationViewSetFieldRefs:
    def test_generar_contrato_uses_pk_lookup_not_legacy_field(self):
        """Contract has no `contrato_id` field post-rename — must use pk= lookup (#22)."""
        from api.v1.app_rrhh.document_generation_views import DocumentGenerationViewSet

        src = inspect.getsource(DocumentGenerationViewSet.generar_contrato)
        assert "contrato_id=contrato_id" not in src
        assert "Contract" in src and ("pk=" in src or "id=" in src)

    def test_generar_certificado_uses_pk_lookup_not_legacy_empleado_id(self):
        """Employee has no `empleado_id` field post-rename (#23)."""
        from api.v1.app_rrhh.document_generation_views import DocumentGenerationViewSet

        src = inspect.getsource(DocumentGenerationViewSet.generar_certificado)
        assert "empleado_id=empleado_id" not in src

    def test_no_documento_documento_id_attribute_access(self):
        """DigitalDocument PK is `id` UUID — `documento.documento_id` is AttributeError (#24)."""
        from api.v1.app_rrhh import document_generation_views as mod

        src = inspect.getsource(mod)
        assert "documento.documento_id" not in src

    def test_subir_plantilla_word_uses_created_by_not_creada_por(self):
        """DocumentTemplate field is `created_by` (#25)."""
        from api.v1.app_rrhh.document_generation_views import DocumentGenerationViewSet

        src = inspect.getsource(DocumentGenerationViewSet.subir_plantilla_word)
        assert "creada_por=" not in src
        assert "created_by=" in src

    def test_generar_desde_plantilla_word_reads_distinct_query_params(self):
        """Two IDs must NOT both read from `id` (#27)."""
        from api.v1.app_rrhh.document_generation_views import DocumentGenerationViewSet

        src = inspect.getsource(DocumentGenerationViewSet.generar_desde_plantilla_word)
        # Bug: both empleado_id and contrato_id reading request.data.get("id")
        # After fix: distinct keys
        assert (
            'request.data.get("empleado_id")' in src or 'request.data.get("empleado")' in src
        )
        assert (
            'request.data.get("contrato_id")' in src or 'request.data.get("contrato")' in src
        )
```

Run tests (RED), then fix in `document_generation_views.py`:
1. Replace `contrato_id=contrato_id`/`empleado_id=empleado_id` with `pk=...`.
2. Replace `documento.documento_id` (5 sites) with `documento.id`.
3. Replace `creada_por=request.user` with `created_by=request.user`.
4. In `generar_desde_plantilla_word` body: read `empleado_id = request.data.get("empleado_id")` and `contrato_id = request.data.get("contrato_id")` (distinct keys; back-compat `or request.data.get("id")` only on whichever is the existing single-ID flow).

For #26, edit `apps/api/api/v1/app_rrhh/document_generation_urls.py`: drop `[0-9]+` regex and let DRF default kwarg handling take over.

Commit:
```
fix(B5b): DocumentGenerationViewSet stale L3.10.x/L3.11 consumer bugs (#22-#27)
```

---

## Task 3: Fix `TemplateService` stale field refs (#28, #29, plus inventory bugs at lines 230, 254, 433, 439)

**Files:** `apps/api/apps/documents/services/template_service.py`

Bugs (per audit):
- **line 216** `getattr(contrato, 'numero_adenda', None)` — silent stale (#28 cluster). For Contract this is dead path (always None). For ContractAmendment it should be `adenda.numero_adenda` (already correct on lines 129/132). Refactor: split the variable bag — Contract path drops `numero_adenda` entirely; ContractAmendment path sets it from `adenda.numero_adenda`. Pure cleanup.
- **line 230** `contrato.get_estado_display()` — Contract field is `status`. Django auto-generates `get_status_display`, NOT `get_estado_display`. AttributeError. Fix: `contrato.get_status_display()`.
- **line 254** `if contrato.creado_por_id else 'Sistema'` — Python attr is `created_by_id` (db_column legacy `creado_por_id`). Fix: `created_by_id`.
- **line 433** `c.numero_contrato or c.contrato_id` in fallback — Contract has `id` UUID, no `contrato_id`. Fix: `c.numero_contrato or str(c.id)`.
- **line 439** `c.get_estado_display()` — same status fix.

**Test (apps/api/apps/documents/tests/test_template_service.py):**

```python
"""Tests for TemplateService stale-consumer fixes (B.5b #28, #29)."""
import inspect


class TestTemplateServiceFieldRefs:
    def test_no_legacy_get_estado_display(self):
        """Contract field renamed to `status`; auto-method is get_status_display (#28)."""
        from apps.documents.services import template_service

        src = inspect.getsource(template_service)
        assert ".get_estado_display()" not in src
        assert ".get_status_display()" in src

    def test_no_legacy_creado_por_id_attr(self):
        """Python attr is created_by_id, not creado_por_id (#29)."""
        from apps.documents.services import template_service

        src = inspect.getsource(template_service)
        # The legacy attr access is the bug
        assert ".creado_por_id" not in src

    def test_no_legacy_contrato_id_attr(self):
        """Contract PK is `id` UUID, not `contrato_id`."""
        from apps.documents.services import template_service

        src = inspect.getsource(template_service)
        # Variable name `contrato_id` (parameter) is fine; .contrato_id (attribute) is not.
        # Heuristic: `.contrato_id` after a Contract reference is bad.
        assert ".contrato_id" not in src
```

Apply fixes after RED. Commit:
```
fix(B5b): TemplateService stale field refs status/created_by/PK (#28, #29)
```

---

## Task 4: Fix `WordTemplateService` stale refs + tenant data leak (#30, #31, #74)

**Files:** `apps/api/apps/documents/services/word_template_service.py`

Bugs:
- **line 139** `'NUMERO_ADENDA': contrato.numero_adenda or ''` — Contract has no `numero_adenda` (split L3.10.3). AttributeError. Fix: `'NUMERO_ADENDA': getattr(contrato, 'numero_adenda', '')` for safety, OR move to ContractAmendment-only path. Use `getattr(..., '')`. Document inline that for Contract this is empty.
- **line 175** `Contract.objects.filter(empleado=empleado, estado='ACTIVO')` — field is `status`. FieldError. Fix: `status='activo'` (lowercase per L3.10.4d post-rename).
- **lines 121-123** hardcoded `EMPRESA_NOMBRE='Institución Pública'`, `EMPRESA_RUC='20123456789'`, `EMPRESA_DIRECCION='Av. Principal 123, Lima, Perú'` — should read `Company.get_config(tenant)`. (#74 — covered here).

**Approach for #74:** Add a `tenant` kwarg to `construir_variables_empleado` and `construir_variables_contrato`/`construir_variables_certificado`. Read `Company.get_config(tenant=tenant)` — pass through from caller. Keep hardcoded fallback for the no-tenant case (admin commands), but log a warning.

```python
from apps.organization.models import Company

def construir_variables_empleado(self, empleado, datos_adicionales=None, tenant=None):
    cfg = None
    if tenant is not None:
        try:
            cfg = Company.get_config(tenant=tenant)
        except Exception:
            cfg = None
    ...
    'EMPRESA_NOMBRE': cfg.razon_social if cfg else 'Institución Pública',
    'EMPRESA_RUC': cfg.ruc if cfg else '20123456789',
    'EMPRESA_DIRECCION': cfg.direccion_fiscal if cfg else 'Av. Principal 123, Lima, Perú',
    'CIUDAD': cfg.ciudad if cfg else 'Lima',
```

Verify Company API:

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.testing')
django.setup()
from apps.organization.models import Company
cfg = Company._meta.get_fields()
print([f.name for f in cfg if hasattr(f, 'name')][:20])
"
```

Map to actual fields. (Spec said `razon_social`, `ruc`, `direccion`, etc. — verify.)

**Tests (apps/api/apps/documents/tests/test_word_template_service.py):**

```python
"""Tests for WordTemplateService field refs + tenant config (B.5b #30, #31, #74)."""
import inspect


class TestWordTemplateServiceFieldRefs:
    def test_no_direct_numero_adenda_access(self):
        """contrato.numero_adenda is AttributeError on Contract (#30)."""
        from apps.documents.services import word_template_service

        src = inspect.getsource(word_template_service)
        # Direct access bug pattern
        assert "contrato.numero_adenda or" not in src

    def test_no_legacy_estado_filter(self):
        """Contract.objects.filter(estado='ACTIVO') is FieldError (#31)."""
        from apps.documents.services import word_template_service

        src = inspect.getsource(word_template_service)
        assert "estado='ACTIVO'" not in src
        assert 'estado="ACTIVO"' not in src

    def test_construir_variables_empleado_accepts_tenant_kwarg(self):
        """Per #74, must accept tenant for Company.get_config lookup."""
        from apps.documents.services.word_template_service import WordTemplateService

        sig = inspect.signature(WordTemplateService.construir_variables_empleado)
        assert "tenant" in sig.parameters
```

Apply fixes after RED. Commit:
```
fix(B5b): WordTemplateService stale refs + tenant-aware Company config (#30, #31, #74)
```

---

## Task 5: Fix `template_service._obtener_datos_institucion` tenant param (#75)

**Files:** `apps/api/apps/documents/services/template_service.py:324`

Bug: `cfg = Company.get_config(tenant=None)` always reads default tenant — **C-multitenancy data leak**: tenant_a's documents render with tenant_b's institution data if tenant_b's record happens to be the "default" seed.

Fix: Add `tenant` kwarg to `_obtener_datos_institucion(self, tenant=None)`. Pass through from callers. Add `tenant` kwargs to `generar_contrato`/`generar_certificado`/`generar_reporte_*` methods, propagated from the ViewSet (Task 11).

Signature change is breaking; the ViewSet caller (Task 11) supplies it. Keep `tenant=None` default for backwards-compat.

**Test (apps/api/apps/documents/tests/test_template_service.py — extend existing):**

```python
class TestObtenerDatosInstitucionTenantParam:
    def test_obtener_datos_institucion_accepts_tenant(self):
        from apps.documents.services.template_service import TemplateService

        ts = TemplateService()
        # The signature must permit tenant kwarg
        sig = inspect.signature(ts._obtener_datos_institucion)
        assert "tenant" in sig.parameters
```

Apply. Commit:
```
fix(B5b): TemplateService _obtener_datos_institucion accepts tenant kwarg (#75)
```

---

## Task 6: Fix `pdf_generator.generar_pdf_adenda` signature mismatch + tenant-orphaned DigitalDocument (#78 partial, plus pdf_generator audit)

**Files:** `apps/api/apps/documents/services/pdf_generator.py:137-139, 482-495`

Bugs:
- Line 137-139: `generar_pdf_adenda` calls `template_service.generar_adenda(contrato_id, tipo_adenda)`. Post-split, `template_service.generar_adenda(adenda_id, tipo)` expects `adenda_id` (UUID of ContractAmendment). Caller passes `contrato_id`. Documents render with parent contract data, not the amendment's. Fix: rename param to `adenda_id` and pass through unchanged.
- Lines 482-495: `_guardar_documento_digital` creates DigitalDocument **without** `tenant` field set — orphan document. Fix: accept `tenant` kwarg from caller and set `DigitalDocument.objects.create(tenant=tenant, ...)`.

**Test (apps/api/apps/documents/tests/test_pdf_generator.py):**

```python
"""Tests for pdf_generator orphan tenant + signature fixes (B.5b #78 partial)."""
import inspect


class TestPDFGeneratorSignatures:
    def test_generar_pdf_adenda_param_named_adenda_id(self):
        """Post-split, the call expects amendment PK, not contract PK."""
        from apps.documents.services.pdf_generator import PDFGenerator

        sig = inspect.signature(PDFGenerator.generar_pdf_adenda)
        # First positional after self should be the amendment ID
        params = list(sig.parameters.keys())
        assert "adenda_id" in params or "amendment_id" in params

    def test_guardar_documento_digital_accepts_tenant(self):
        from apps.documents.services.pdf_generator import PDFGenerator

        sig = inspect.signature(PDFGenerator._guardar_documento_digital)
        assert "tenant" in sig.parameters
```

Apply. Commit:
```
fix(B5b): pdf_generator adenda signature + tenant-aware DigitalDocument create
```

---

## Task 7: Fix `OnboardingService.reenviar_email_bienvenida` lookup + `corregir_correo` test (#32, plus test_corregir_correo_updates_email)

**Files:** `apps/api/apps/onboarding/services/onboarding_service.py:499`

Bug: `OnboardingProcess.objects.get(onboarding_id=onboarding_id)` — model PK is `id` UUID. Lookup field doesn't exist. `OnboardingProcess.DoesNotExist` raised, caller catches → returns None → endpoint silently returns 400.

Fix: `OnboardingProcess.objects.get(pk=onboarding_id)`.

**Tests:** the existing `tests/test_onboarding_api.py::TestCorregirCorreo::test_corregir_correo_updates_email` is already RED on master (one of our 3 baseline failures). Fix the lookup; the test should turn GREEN automatically.

Add a unit test in the new co-located dir:

```python
# apps/api/apps/onboarding/tests/test_onboarding_service.py
"""OnboardingService.reenviar_email_bienvenida + corregir_correo regression tests (B.5b #32)."""
import inspect


class TestReenviarEmailBienvenida:
    def test_uses_pk_lookup_not_legacy_onboarding_id_field(self):
        """OnboardingProcess PK is `id` UUID; legacy `onboarding_id=` lookup is FieldError."""
        from apps.onboarding.services.onboarding_service import OnboardingService

        src = inspect.getsource(OnboardingService.reenviar_email_bienvenida)
        assert "onboarding_id=onboarding_id" not in src
        # Must use pk= or id= lookup
        assert "pk=onboarding_id" in src or "id=onboarding_id" in src
```

Apply fix. Run pytest to verify the legacy `test_corregir_correo_updates_email` now passes. Commit:
```
fix(B5b): OnboardingService.reenviar_email_bienvenida uses pk lookup (#32)
```

---

## Task 8: Rebrand 11 "Intranet" strings in 5 email templates (#33)

**Files:**
- `apps/api/templates/emails/bienvenida.html` (4 occurrences)
- `apps/api/templates/emails/bienvenida.txt` (3 occurrences)
- `apps/api/templates/emails/documento_rechazado.html` (1 occurrence)
- `apps/api/templates/emails/onboarding_aprobado.html` (1 occurrence)
- `apps/api/templates/emails/onboarding_observado.html` (1 occurrence)

Strings to replace:
- `"Bienvenido - Intranet RRHH"` → `"Bienvenido - VYNTIA"` (title tag)
- `"Bienvenido a la Intranet"` → `"Bienvenido a VYNTIA"` (h1)
- `"sistema de Intranet"` → `"plataforma VYNTIA"` (paragraph)
- `"Intranet RRHH"` → `"VYNTIA"` (footer in 5 templates)
- `"sistema de Intranet"` → `"plataforma VYNTIA"` (txt template)

**Verification (no false positives):**

```bash
grep -r "Intranet" apps/api/templates/emails/   # before fix → 11 hits
grep -r "Intranet" apps/api/templates/emails/   # after → 0 hits
```

**Test:**

```python
# apps/api/apps/onboarding/tests/test_email_branding.py
"""Email-template branding regression test (B.5b #33)."""
from pathlib import Path


class TestEmailTemplateBranding:
    def test_no_intranet_strings_in_email_templates(self):
        templates_dir = Path(__file__).resolve().parents[4] / "templates" / "emails"
        offenders = []
        for path in templates_dir.glob("**/*"):
            if path.is_file() and path.suffix in (".html", ".txt"):
                content = path.read_text(encoding="utf-8")
                if "Intranet" in content:
                    offenders.append(str(path))
        assert offenders == [], f"Templates still contain 'Intranet': {offenders}"
```

Apply rebrand (per-file Edit). Commit:
```
chore(B5b): rebrand 11 "Intranet" strings in 5 email templates → VYNTIA (#33)
```

---

## Task 9: Fix `OnboardingService` tenant scoping — username + Role lookup (#81)

**Files:** `apps/api/apps/onboarding/services/onboarding_service.py:104, 262`

Bugs:
- Line 104: `User.objects.filter(username=username).exists()` — global enumeration. **For B.5b we DO NOT scope `username` per-tenant** (that requires identity-app coordination — out of scope). Instead, this task focuses on the simpler issue:
- Line 262: `Role.objects.filter(nombre_rol__in=["Employee","empleado"])` — global lookup, may return wrong-tenant Role. Fix: `Role.objects.filter(tenant=tenant, nombre_rol__in=["Employee","empleado"]).first()`. If `tenant` is None, fall through to None and skip role assignment with a warning log (admin-mode creation paths).

**Defer:** username-uniqueness-per-tenant is out of B.5b scope. Add an inline `# TODO(B-future): scope username uniqueness to (tenant, username) when identity model adds tenant FK constraint` for traceability.

**Test:**

```python
# apps/api/apps/onboarding/tests/test_onboarding_service_tenant.py
"""OnboardingService.crear_onboarding_completo Role tenant scoping (B.5b #81)."""
import inspect


class TestRoleLookupTenantScoped:
    def test_role_lookup_filters_by_tenant(self):
        from apps.onboarding.services.onboarding_service import OnboardingService

        src = inspect.getsource(OnboardingService)
        # Bug pattern: Role.objects.filter without tenant
        # After fix: tenant filter is paired with the role lookup
        # Heuristic: any Role.objects.filter() must mention tenant within 80 chars
        assert "Role.objects.filter" in src
        # Look for the tenant filter pattern
        assert "tenant=" in src  # Either passed to filter or in the function signature
```

Apply fix. Commit:
```
fix(B5b): OnboardingService Role lookup is tenant-scoped (#81)
```

---

## Task 10: Fix `OnboardingNotificationService._enviar_notificacion` silent exception (#83)

**Files:** `apps/api/apps/onboarding/services/onboarding_notification_service.py:522` (per audit; verify exact path)

Bug: try/except silences SMTP failures with no log. Fix: log the exception via `logger.exception(...)` before falling through.

**Verify location:**

```bash
grep -nE "_enviar_notificacion|except Exception" apps/api/apps/onboarding/services/*.py
```

Add logger import if missing. Commit:
```
fix(B5b): OnboardingNotificationService logs SMTP exceptions instead of silencing (#83)
```

---

## Task 11: Migrate `DocumentGenerationViewSet` from `app_rrhh/` to `apps/api/api/v1/documents/views.py` (#76, #82-mirror)

**Files:**
- Source: `apps/api/api/v1/app_rrhh/document_generation_views.py` (757 lines)
- Source: `apps/api/api/v1/app_rrhh/document_generation_urls.py`
- Target: `apps/api/api/v1/documents/views.py` (new file)
- Target: `apps/api/api/v1/documents/urls.py` (extend existing)

**Steps:**
1. `git mv apps/api/api/v1/app_rrhh/document_generation_views.py apps/api/api/v1/documents/views.py`
2. Update target imports (none should change since absolute imports `apps.documents.services` etc.).
3. Inline the `app_rrhh/document_generation_urls.py` registrations into `api/v1/documents/urls.py` (the actions are already mounted there via `include`; replace the `include('api.v1.app_rrhh.document_generation_urls')` line with direct `register` calls).
4. Delete `apps/api/api/v1/app_rrhh/document_generation_urls.py`.
5. Verify routes still resolve: hit `/api/v1/documents/documents/generar-contrato/` and check 401 (auth-walled, expected).

**ViewSet should also gain tenant-awareness** — wire it as `class DocumentGenerationViewSet(TenantAwareViewSetMixin, ViewSet)`. NOTE: `TenantAwareViewSetMixin` assumes `serializer.save()` and `super().get_queryset()`, which a plain `ViewSet` (not ModelViewSet) doesn't have. So inheriting the mixin is a no-op here — instead, wire tenant via `request.tenant` directly in each `action` method when creating DigitalDocument or DocumentTemplate. We pass `tenant=request.tenant` to `_guardar_documento_digital` and to `DocumentTemplate.objects.create(tenant=request.tenant, ...)`.

**Test:**

```python
# apps/api/apps/documents/tests/test_document_generation_routing.py
"""DocumentGenerationViewSet routing migration (B.5b #76)."""


class TestDocumentGenerationRouting:
    def test_view_set_lives_in_documents_module(self):
        # Smoke import — module must exist after migration
        from api.v1.documents import views as docs_views
        assert hasattr(docs_views, "DocumentGenerationViewSet")
```

Smoke routes via curl post-fix:

```bash
cd D:/VYNTIA && D:/VYNTIA/.venv/Scripts/python.exe apps/api/manage.py check --settings=vyntia.settings.development
```

Commit:
```
refactor(B5b): migrate DocumentGenerationViewSet to apps/documents/ + tenant-aware (#76)
```

---

## Task 12: Migrate `OnboardingViewSet` from `api/v1/rrhh/views.py` to `api/v1/onboarding/views.py` (#82)

**Files:**
- Source: `apps/api/api/v1/rrhh/views.py` (lines 1640+, ~`OnboardingViewSet` block)
- Target: `apps/api/api/v1/onboarding/views.py` (new file)
- Source: `apps/api/api/v1/onboarding/urls.py` (already imports from rrhh — update to local)

**Steps:**
1. Identify the OnboardingViewSet block in `views.py` and any onboarding-only serializer-block dependencies.
2. Create `apps/api/api/v1/onboarding/views.py`. Move the class (cut from `views.py`, paste into new file). Pull only the imports the class uses; leave shared imports untouched.
3. Update `api/v1/onboarding/urls.py` to import the ViewSet from local `.views`, not from `..rrhh.views`.
4. Verify `manage.py check --settings=vyntia.settings.development` passes.
5. The ViewSet already inherits `TenantAwareViewSetMixin` (verified in B.1). For #80, `get_queryset` filtering and `retrieve` ownership check should already inherit the mixin behavior — verify and add an explicit `tenant=request.tenant` filter in `retrieve`'s ownership check if missing.

**Test:**

```python
# apps/api/apps/onboarding/tests/test_onboarding_routing.py
"""OnboardingViewSet routing migration (B.5b #82)."""


class TestOnboardingRouting:
    def test_view_set_lives_in_onboarding_module(self):
        from api.v1.onboarding import views as ob_views
        assert hasattr(ob_views, "OnboardingViewSet")
```

Commit:
```
refactor(B5b): migrate OnboardingViewSet to api/v1/onboarding/views.py (#82, #80 verification)
```

---

## Task 13: Fix `test_employee_cannot_patch_restricted_fields` security gap (B.1 carryover)

**Files:** Identify which serializer / ViewSet handles employee self-update; add field-level write guard.

The test in `tests/test_onboarding_self_update.py::TestEmpleadoSelfUpdate::test_employee_cannot_patch_restricted_fields` is RED on master baseline. It expects 403 when an employee patches restricted fields like `nombres_empleado`/`apellido_paterno` during onboarding self-update; current behavior returns 200.

**Investigation step (per superpowers:systematic-debugging):**

```bash
grep -nE "self_update|self-update|EmpleadoSelfUpdate|patch.*nombres_empleado" apps/api/api/v1/ -r
```

Likely fix sites:
- An employee-self serializer (under `api/v1/employees/` or `rrhh/serializers.py`) that lists too many `Meta.fields`.
- Or a permission class that doesn't restrict fields on `partial_update`.

The pattern: add an `EMPLOYEE_SELF_PATCH_ALLOWED_FIELDS` whitelist (e.g., `correo_personal`, `telefono_celular`) and reject any other field names with 403.

Apply minimal fix to make the test green without breaking the 6 passing related tests.

Commit:
```
fix(B5b): block employee self-patch on restricted identity fields (B.1 carryover)
```

---

## Task 14: Cleanup `onboardingUploadService.ts` duplicate functions (#85)

**Files:** `apps/web/src/features/onboarding/services/onboardingUploadService.ts`

Bug: 3 functions (`uploadDocument`, `subirDocumento`, `uploadFoto`) target the same `/subir-documento/` endpoint with different signatures.

**Inspection:**

```bash
grep -nE "function uploadDocument|function subirDocumento|function uploadFoto|/subir-documento" apps/web/src/features/onboarding/services/onboardingUploadService.ts
```

**Approach:** Pick the most-used variant as canonical. Rename the others to deprecated-aliases that delegate to the canonical, with `@deprecated` JSDoc tags. Update consumers to use canonical name. Vitest must continue to pass.

OR if the variants serve genuinely different shapes (foto vs document), keep them separate but extract the shared `axios.post(...)` body into a private helper.

Decide based on code reading. Commit:
```
refactor(B5b): dedupe onboardingUploadService 3-way uploader functions (#85)
```

---

## Task 15: Refactor `OnboardingAdminPage.tsx` 1047-line monolith (#84)

**Files:** `apps/web/src/features/onboarding/pages/OnboardingAdminPage.tsx`

Bug: 1047 LOC, 5 `any` lints (lines 87, 424, 624, 870, 887), unused imports (CardHeader, CardTitle).

**Approach:**
1. Type the 5 `any` instances correctly. Most are React event handlers, modal state, or API response shapes — read context and replace.
2. Remove unused imports.
3. Extract 2-3 sub-components if natural seams exist (per-doc approval modal, observation modal, header bar). Stop at 3 — full refactor is out of B.5b scope; goal is `<800 LOC` and `0 any` lints.

Build/vitest must remain green throughout.

Commit:
```
refactor(B5b): trim OnboardingAdminPage monolith + type any lints (#84)
```

---

## Task 16: Frontend lint cleanup `features/onboarding`+`features/documents` (part of #90)

Same pattern as B.2-B.5. Fix as many `no-explicit-any`/`react-hooks/exhaustive-deps`/unused-import issues as possible in these two folders. Target: `features/onboarding`+`features/documents` lint count → 0 (was 15 pre-B.5b, ≤6 after Tasks 14+15).

Capture before/after lint count. Build/vitest preserved.

Commit:
```
chore(B5b): lint cleanup features/onboarding + features/documents (#90 partial)
```

---

## Task 17: Final verification + close-out

- Capture final baselines:
  - pytest: should be 339+/1/17.
  - vitest: 7 files / 32.
  - ESLint: <280.
  - tsc: 1 (preserved).
  - Build: clean.
- Audit no stale field refs remain:
  ```bash
  grep -rE "creado_por_id|\.documento_id|contrato_id=contrato_id|empleado_id=empleado_id|get_estado_display|onboarding_id=onboarding_id|estado='ACTIVO'|estado=\"ACTIVO\"" apps/api/
  ```
  Expected: empty (or only legacy db_column declarations, not attribute access).
- Audit no "Intranet" strings remain in `apps/api/templates/emails/`.
- Update memory pointer.

Commit any cleanup. No final commit needed if no changes.

---

## Self-Review

| # | Item | Task |
|---|---|---|
| 22 | DocumentGenerationViewSet.generar_contrato Contract.contrato_id | Task 2 |
| 23 | DocumentGenerationViewSet.generar_certificado Employee.empleado_id | Task 2 |
| 24 | DocumentGenerationViewSet documento.documento_id (5 sites) | Task 2 |
| 25 | DocumentGenerationViewSet.subir_plantilla_word creada_por kwarg | Task 2 |
| 26 | DocumentGenerationViewSet URL regex `[0-9]+` doesn't match UUIDs | Task 2 |
| 27 | DocumentGenerationViewSet.generar_desde_plantilla_word duplicate `id` query param | Task 2 |
| 28 | template_service.py:230 `get_estado_display` AttributeError | Task 3 |
| 29 | template_service.py:254 `creado_por_id` attribute doesn't exist | Task 3 |
| 30 | word_template_service.py:139 `contrato.numero_adenda` AttributeError | Task 4 |
| 31 | word_template_service.py:175 `Contract.filter(estado='ACTIVO')` FieldError | Task 4 |
| 32 | OnboardingService.reenviar_email_bienvenida `onboarding_id=` lookup field | Task 7 |
| 33 | 11 "Intranet" strings in 5 email templates | Task 8 |
| 74 | WordTemplateService EMPRESA_NOMBRE etc. hardcoded — read tenant Company config | Task 4 |
| 75 | template_service _obtener_datos_institucion needs tenant kwarg | Task 5 |
| 76 | DocumentGenerationViewSet migration to api/v1/documents/views.py | Task 11 |
| 78 | pdf_generator orphan tenant DigitalDocument + adenda signature | Task 6 |
| 80 | OnboardingViewSet queryset/retrieve tenant filter | Task 12 (verified inherits) |
| 81 | OnboardingService Role lookup tenant-scoped | Task 9 |
| 82 | OnboardingViewSet migration to api/v1/onboarding/views.py | Task 12 |
| 83 | OnboardingNotificationService silent exception | Task 10 |
| 84 | OnboardingAdminPage.tsx 1047-line monolith refactor | Task 15 |
| 85 | onboardingUploadService 3-way duplicate functions | Task 14 |
| 86 | Co-locate documents+onboarding tests under apps/X/tests/ | Task 1 (dirs scaffolded; new tests in 2-12 land there) |
| 90 (onboarding+documents piece) | Lint cleanup | Task 16 |
| B.1-carry | test_employee_cannot_patch_restricted_fields | Task 13 |

Coverage: 24 in-scope items + 1 carryover.

**Out of scope (deferred):**
- #77 (filesystem auth-walled `/media/`) — deployment hardening, deferred.
- #79 (DocumentTemplate per-tenant ambiguity ADR) — design decision, deferred.
- Per-tenant `frontend_url` (subdomain routing in `bienvenida.html`) — depends on C.4 deployment.
- Username uniqueness scoped `(tenant, username)` — coordinated as part of identity B.x in a future polish round.
