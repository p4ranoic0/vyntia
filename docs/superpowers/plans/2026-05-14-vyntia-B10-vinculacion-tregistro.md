# B.10 Vinculación + T-Registro Implementation Plan (Module 03.2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Land Module 03.2 — Vinculación — covering formalization of the labor link
from selection ganador (B.9 outcome) through contract emission, electronic signature,
obligatory hiring document bundle delivery + acuse, and T-Registro SUNAT declaration
generation (Anexo 3) + PVS validation. Backend + API + admin HR pages.

**Architecture:** 3 new models across contracts (1) and documents (2) apps:
`TRegistroDeclaration` (contracts) for SUNAT alta/baja flow with Anexo 3 fields and
state machine; `DocumentSignature` (documents) as generic signature record attachable
to any DigitalDocument with lifecycle requested → signed/rejected/expired;
`HiringDocumentBundle` + `HiringBundleItem` (documents) as orchestrator of the
obligatory hiring documents (Contract + RIT + Reglamento SST + Código de ética +
Política protección datos + Manual funciones) per Module 03.2 § 3.2.

Services: `tregistro_service` (build_anexo3_txt, validate_pvs, submit, register status),
`signature_service` (request, capture canvas/text, verify, expire), `bundle_service`
(build_for_employee, attach_acuse, mark_acknowledged).

Sector-agnostic: both private (Ley 728/CAS DL 1057) and public (DL 276/Ley 30057)
share the same models. T-Registro applies primarily to private sector (728/CAS); public
sector uses SERVIR Aplicativo de Recursos Humanos and is out-of-scope for B.10
(deferred to a future module).

**Branch:** `vyntia/B10-vinculacion-tregistro`
**Backlog items in scope:**
- #111 — Module 03.2: T-Registro SUNAT integration (TRegistroDeclaration + Anexo 3 txt + PVS validation)
- #112 — Module 03.2: DocumentSignature + e-signature flow UI
- #113 — Module 03.2: Hiring document bundle automation (RIT, Reglamento SST, etc. + acuse)

**User-confirmed scope decisions (work-without-pause mode 2026-05-14):**
- Single B.10 PR covering all 3 backlog items.
- T-Registro real integration with SUNAT/PVS infrastructure deferred — B.10 ships
  TXT generation per Anexo 3 spec + a local PVS-style validator (header/field
  rules). Wire-level submission API mocked behind a service boundary so future
  integration is a single seam.
- DocumentSignature is canvas-base64 + signer metadata (name, doc, IP, UA, timestamp).
  Full PKI/digital cert per Reg. Firmas Digitales deferred — out-of-scope.
- Hiring bundle is template-driven (the template_codes that the tenant chooses to
  include become items). Manual functions / policies generation reused from B.5b
  doc-gen flow (no new templates created in B.10).

**Out of scope (deferred):**
- SUNAT PVS real submission API client → post-B (separate sub-project).
- PKI / digital certificate signing per Reg. Firmas Digitales (DS 052-2008-PCM) → M-firma later.
- T-Registro alta workflow steps with AFP/ONP affiliation, EsSalud/EPS, SCTR. We
  ship the TRegistroDeclaration data model + Anexo 3 file; the affiliation flows
  remain manual (per Module 03.2 § 3.2 they are explicit funcionalidades but
  external — typical real-world handling is via T-Registro receipts uploaded back).
- Baja T-Registro (used in B.14 Desvinculación per backlog #127) → reuses the
  same client/model with `declaration_type='baja'`; B.10 ships only alta.
- Frontend "Vinculación workflow wizard" orchestrating selección ganador → contract
  generation → bundle → signature → T-Registro alta. B.10 ships the building-block
  pages; the wizard is a follow-up if requested.

**Test baselines (post-B.9 SHA `48c93ab7`):**
- pytest 568/1/17, vitest 12/75, ESLint 278, tsc 1 (BlankEnum), build clean.

After B.10:
- pytest **620+/1/17** (~52+ new tests across 3 models + 3 services + 3 API smoke).
- vitest **15+ files / 90+ tests** (3 service tests + page snapshots).
- ESLint: held flat (278).

---

## Task 1: Branch + plan + scaffold

Branch already created from master at `48c93ab7`. Place this plan, commit, capture
baselines.

**Verification:**
- `git log --oneline -1` shows the plan commit.
- `git status` clean afterward.

---

## Task 2: TRegistroDeclaration model + Anexo 3 fields

**Files:**
- `apps/api/apps/contracts/models/t_registro_declaration.py`
- `apps/api/apps/contracts/models/__init__.py` (add export)
- `apps/api/apps/contracts/migrations/0005_b10_t_registro_declaration.py`
- `apps/api/apps/contracts/tests/test_b10_t_registro_declaration.py`

**Model shape:**
```python
class TRegistroDeclaration(models.Model):
    """SUNAT T-Registro declaration (alta/baja/modificación de trabajador).

    Stores all the fields the Anexo 3 plain-text format demands. Real submission
    to SUNAT is out-of-scope; this model captures the prepared declaration and
    its lifecycle (draft → validated → submitted → accepted | rejected).
    """

    DECLARATION_TYPES = [
        ('alta', 'Alta'),
        ('baja', 'Baja'),
        ('modificacion', 'Modificación'),
    ]
    STATUSES = [
        ('draft', 'Borrador'),
        ('validated', 'Validado PVS'),
        ('submitted', 'Enviado SUNAT'),
        ('accepted', 'Aceptado'),
        ('rejected', 'Rechazado'),
    ]
    REGIMEN_PENSIONARIO = [
        ('snp', 'SNP (ONP)'),
        ('spp', 'SPP (AFP)'),
        ('decreto_19990', 'DL 19990'),
        ('decreto_20530', 'DL 20530'),
        ('sin_regimen', 'Sin régimen'),
    ]
    REGIMEN_SALUD = [
        ('essalud', 'EsSalud'),
        ('eps', 'EPS'),
        ('sct_riesgo', 'SCTR'),
        ('ninguno', 'Ninguno'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                               null=True, blank=True, db_index=True, related_name='+')

    declaration_type = models.CharField(max_length=20, choices=DECLARATION_TYPES, default='alta')
    status = models.CharField(max_length=20, choices=STATUSES, default='draft', db_index=True)

    # Links: the contract this declaration covers
    contract = models.ForeignKey('contracts.Contract', on_delete=models.PROTECT,
                                  related_name='t_registro_declarations')
    employee = models.ForeignKey('employees.Employee', on_delete=models.PROTECT,
                                  related_name='t_registro_declarations')

    # Employer (cached from tenant.CompanyConfig at draft time)
    employer_ruc = models.CharField(max_length=11)
    employer_razon_social = models.CharField(max_length=200)

    # Worker
    worker_doc_type = models.CharField(max_length=4, default='01',
                                       help_text='01=DNI 04=CE 07=PAS')
    worker_doc_number = models.CharField(max_length=20)
    worker_apellido_paterno = models.CharField(max_length=80)
    worker_apellido_materno = models.CharField(max_length=80, blank=True)
    worker_nombres = models.CharField(max_length=100)
    worker_birth_date = models.DateField()
    worker_gender = models.CharField(max_length=1, default='M')  # M / F
    worker_nationality_code = models.CharField(max_length=3, default='604')  # PER
    worker_address = models.CharField(max_length=300, blank=True)

    # Contract
    contract_start_date = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True)
    work_modality_code = models.CharField(max_length=3,
                                          help_text='SUNAT modalidad code per Tabla 8')
    occupation_code = models.CharField(max_length=6, blank=True,
                                       help_text='CIUO-08 per Tabla 24')

    # Régimen
    regimen_laboral_code = models.CharField(max_length=3, default='728')
    regimen_pensionario = models.CharField(max_length=20, choices=REGIMEN_PENSIONARIO, default='snp')
    pension_provider_code = models.CharField(max_length=10, blank=True,
                                              help_text='AFP code if SPP')
    cuspp = models.CharField(max_length=20, blank=True, help_text='CUSPP del trabajador SPP')
    regimen_salud = models.CharField(max_length=20, choices=REGIMEN_SALUD, default='essalud')
    eps_code = models.CharField(max_length=10, blank=True)

    # Compensation snapshot
    remuneracion_basica = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    jornada_horas_semanales = models.PositiveSmallIntegerField(default=48)

    # SUNAT response
    anexo3_txt = models.TextField(blank=True, help_text='Generated Anexo 3 plain text')
    pvs_errors = models.JSONField(default=list, blank=True)
    sunat_reference = models.CharField(max_length=64, blank=True,
                                        help_text='Número de constancia SUNAT')
    sunat_response_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey('identity.User', null=True, blank=True,
                                      on_delete=models.SET_NULL, related_name='+')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_registro_declaration'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'declaration_type']),
            models.Index(fields=['contract']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'contract', 'declaration_type'],
                condition=models.Q(status__in=['submitted', 'accepted']),
                name='unique_active_t_registro_per_contract',
            ),
        ]

    def __str__(self):
        return f'T-Registro {self.get_declaration_type_display()} — {self.worker_doc_number}'

    # State transitions
    def mark_validated(self, errors=None):
        self.pvs_errors = errors or []
        if errors:
            raise ValidationError('Cannot mark validated with errors. Use save() with status=draft and pvs_errors set.')
        self.status = 'validated'
        self.save(update_fields=['status', 'pvs_errors', 'updated_at'])

    def mark_submitted(self, *, user, reference=''):
        if self.status not in ('validated', 'draft'):
            raise ValidationError(f'Cannot submit from status={self.status}')
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.submitted_by = user
        self.sunat_reference = reference
        self.save(update_fields=['status', 'submitted_at', 'submitted_by', 'sunat_reference', 'updated_at'])

    def mark_accepted(self, *, reference=''):
        if self.status != 'submitted':
            raise ValidationError(f'Cannot mark accepted from status={self.status}')
        self.status = 'accepted'
        self.sunat_response_at = timezone.now()
        if reference:
            self.sunat_reference = reference
        self.save(update_fields=['status', 'sunat_response_at', 'sunat_reference', 'updated_at'])

    def mark_rejected(self, *, reason):
        if self.status != 'submitted':
            raise ValidationError(f'Cannot mark rejected from status={self.status}')
        self.status = 'rejected'
        self.rejection_reason = reason
        self.sunat_response_at = timezone.now()
        self.save(update_fields=['status', 'rejection_reason', 'sunat_response_at', 'updated_at'])
```

**Migration:** add table + indexes + uniqueness constraint. Reference `tenancy.Tenant`,
`contracts.Contract`, `employees.Employee`, `identity.User`.

**Tests (~10):**
- create_alta_declaration_sets_defaults
- doc_type_dni_validation
- status_transitions_draft_to_validated_to_submitted
- mark_submitted_rejects_non_validated (raises ValidationError)
- mark_accepted_only_from_submitted
- mark_rejected_only_from_submitted
- unique_active_declaration_per_contract (alta) — submitting a second one with same (contract, declaration_type='alta') while first is submitted/accepted raises IntegrityError
- baja_declaration_can_coexist_with_alta
- tenant_isolation (different tenant can have same contract+type — covered by tenant column in unique constraint)

**Verification:**
- `D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development` exits 0.
- `pytest apps/contracts/tests/test_b10_t_registro_declaration.py -v` all green.

---

## Task 3: tregistro_service (Anexo 3 txt + PVS validation)

**Files:**
- `apps/api/apps/contracts/services/__init__.py`
- `apps/api/apps/contracts/services/tregistro_service.py`
- `apps/api/apps/contracts/tests/test_b10_tregistro_service.py`

**Service shape:**
```python
def build_anexo3_txt(declaration: TRegistroDeclaration) -> str:
    """Build the Anexo 3 plain-text declaration per SUNAT spec.

    Format (simplified per known fields, real SUNAT spec has 80+ columns):
      Header line: TRREG|<ruc>|<razon_social>|<declaration_type>|<period>|<created_at iso>
      Worker line: <doc_type>|<doc_number>|<apellido_paterno>|<apellido_materno>|<nombres>
                   |<birth_date YYYYMMDD>|<gender>|<nationality_code>|<address>
      Contract line: <start_date>|<end_date or 99999999>|<modality_code>|<regimen>|<occupation_code>
      Régimen line: <pension_code>|<pension_provider>|<cuspp>|<salud_code>|<eps_code>
      Compensation line: <basic_remuneration>|<jornada_horas_semanales>
      Trailer: COUNT|1

    Returns the joined string with newline separators.
    """

def validate_pvs(declaration: TRegistroDeclaration) -> list[str]:
    """Run local PVS-style validation rules. Returns list of errors (empty if valid)."""

@transaction.atomic
def submit_declaration(declaration_id, *, user, reference='') -> TRegistroDeclaration:
    """Atomic: re-validate, store generated txt, transition draft|validated → submitted."""
```

**PVS rules (~10):**
- RUC employer must be 11 digits.
- Worker doc_number length validation per doc_type (DNI=8, CE=9-12, Pasaporte=6-12).
- Worker apellido_paterno + nombres required.
- birth_date must be ≥18 years before contract_start_date (working-age).
- contract_start_date must be ≤ today + 30 days.
- contract_end_date (if present) must be > contract_start_date.
- work_modality_code in known SUNAT Tabla 8 codes set.
- regimen_laboral_code in known set (728, 1057, 276, 1024, 1153, 30057).
- regimen_pensionario consistency: if 'spp' then pension_provider_code + cuspp required.
- regimen_salud consistency: if 'eps' then eps_code required.

**Tests (~8):**
- build_anexo3_txt_header_format_correct
- build_anexo3_txt_includes_worker_contract_regimen_lines
- validate_pvs_passes_clean_declaration
- validate_pvs_flags_ruc_wrong_length
- validate_pvs_flags_invalid_doc_number_length
- validate_pvs_flags_spp_missing_provider
- validate_pvs_flags_eps_missing_code
- submit_declaration_atomic_persists_txt_and_status

**Verification:**
- Service file exists; tests pass.

---

## Task 4: DocumentSignature model + signature_service

**Files:**
- `apps/api/apps/documents/models/document_signature.py`
- `apps/api/apps/documents/models/__init__.py` (add export)
- `apps/api/apps/documents/services/signature_service.py`
- `apps/api/apps/documents/services/__init__.py` (add export)
- `apps/api/apps/documents/migrations/0004_b10_document_signature.py`
- `apps/api/apps/documents/tests/test_b10_document_signature.py`

**Model shape:**
```python
class DocumentSignature(models.Model):
    """Electronic signature record attachable to any DigitalDocument.

    Lifecycle: requested → signed | rejected | expired. Signature payload is a
    base64-encoded canvas image plus signer metadata (name, doc number, IP, UA,
    timestamp). Full PKI digital signing deferred.
    """

    STATUSES = [
        ('requested', 'Solicitada'),
        ('signed', 'Firmada'),
        ('rejected', 'Rechazada'),
        ('expired', 'Vencida'),
    ]
    SIGNATURE_KINDS = [
        ('canvas', 'Trazo manuscrito'),
        ('checkbox', 'Acuse simple (acepta términos)'),
        ('typed', 'Nombre tipeado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                               null=True, blank=True, db_index=True, related_name='+')

    document = models.ForeignKey('documents.DigitalDocument', on_delete=models.CASCADE,
                                  related_name='signatures')
    signer_user = models.ForeignKey('identity.User', null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='+')
    signer_name = models.CharField(max_length=200)
    signer_doc_number = models.CharField(max_length=20)
    signer_email = models.EmailField(blank=True)

    kind = models.CharField(max_length=20, choices=SIGNATURE_KINDS, default='canvas')
    status = models.CharField(max_length=20, choices=STATUSES, default='requested')

    canvas_base64 = models.TextField(blank=True, help_text='base64 PNG when kind=canvas')
    typed_name = models.CharField(max_length=200, blank=True)
    checkbox_text = models.CharField(max_length=500, blank=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    signer_ip = models.GenericIPAddressField(null=True, blank=True)
    signer_user_agent = models.CharField(max_length=400, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_signature'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['document']),
        ]
```

**Service shape:**
```python
def request_signature(*, document, signer_user=None, signer_name, signer_doc_number,
                      signer_email='', kind='canvas', expires_in_days=30, tenant=None) -> DocumentSignature: ...

def capture_signature(*, signature_id, signer_ip, signer_user_agent, canvas_base64='',
                       typed_name='', checkbox_text='') -> DocumentSignature: ...

def reject_signature(*, signature_id, reason) -> DocumentSignature: ...

def expire_overdue_signatures(now=None) -> int:
    """Cron-friendly: flip status='requested' rows with expires_at<now → 'expired'."""

def verify_signature(signature: DocumentSignature) -> bool: ...
```

**Tests (~8):**
- request_signature_creates_requested_record
- capture_signature_canvas_persists_base64_and_timestamps
- capture_signature_checkbox_requires_checkbox_text
- capture_signature_typed_requires_typed_name
- reject_signature_persists_reason
- expire_overdue_signatures_flips_status
- expire_overdue_signatures_skips_signed
- verify_signature_returns_true_for_signed_canvas

**Verification:**
- `manage.py check` exits 0.
- `pytest apps/documents/tests/test_b10_document_signature.py -v` all green.

---

## Task 5: HiringDocumentBundle + bundle_service

**Files:**
- `apps/api/apps/documents/models/hiring_bundle.py`
- `apps/api/apps/documents/models/__init__.py` (add exports)
- `apps/api/apps/documents/services/bundle_service.py`
- `apps/api/apps/documents/services/__init__.py` (add export)
- `apps/api/apps/documents/migrations/0005_b10_hiring_bundle.py`
- `apps/api/apps/documents/tests/test_b10_hiring_bundle.py`

**Model shape:**
```python
class HiringDocumentBundle(models.Model):
    """Bundle of obligatory hiring documents per Module 03.2 § 3.2.

    Lifecycle: draft → sent → acknowledged. The bundle materializes which
    DigitalDocuments belong to a vinculación event for an Employee (e.g.,
    contrato + RIT + Reglamento SST + Código de ética + etc.) and records
    the acuse de recibo via DocumentSignature for each item.
    """

    STATUSES = [
        ('draft', 'Borrador'),
        ('sent', 'Enviado al colaborador'),
        ('acknowledged', 'Acusado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                               null=True, blank=True, db_index=True, related_name='+')

    employee = models.ForeignKey('employees.Employee', on_delete=models.PROTECT,
                                  related_name='hiring_bundles')
    contract = models.ForeignKey('contracts.Contract', null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name='hiring_bundles')

    title = models.CharField(max_length=200, default='Documentos de vinculación')
    status = models.CharField(max_length=20, choices=STATUSES, default='draft', db_index=True)

    sent_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey('identity.User', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hiring_document_bundle'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['employee']),
        ]


class HiringBundleItem(models.Model):
    """Single item inside a HiringDocumentBundle, optionally with its acuse signature."""

    ITEM_KINDS = [
        ('contrato', 'Contrato'),
        ('rit', 'Reglamento Interno de Trabajo'),
        ('reglamento_sst', 'Reglamento Interno de SST'),
        ('codigo_etica', 'Código de Ética'),
        ('politica_datos', 'Política de Protección de Datos'),
        ('manual_funciones', 'Manual de Funciones del Puesto'),
        ('otro', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bundle = models.ForeignKey('documents.HiringDocumentBundle', on_delete=models.CASCADE,
                                related_name='items')

    kind = models.CharField(max_length=30, choices=ITEM_KINDS)
    document = models.ForeignKey('documents.DigitalDocument', null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name='+')
    signature = models.OneToOneField('documents.DocumentSignature', null=True, blank=True,
                                      on_delete=models.SET_NULL, related_name='bundle_item')

    required = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'hiring_bundle_item'
        ordering = ['order', 'kind']
        unique_together = [('bundle', 'kind')]
```

**Service shape:**
```python
DEFAULT_BUNDLE_ITEMS = ['contrato', 'rit', 'reglamento_sst', 'codigo_etica',
                        'politica_datos', 'manual_funciones']

def build_bundle(*, employee, contract=None, tenant=None, item_kinds=None,
                  created_by=None) -> HiringDocumentBundle:
    """Create a bundle in draft with one HiringBundleItem per item_kind."""

def attach_document(*, bundle_item_id, document) -> HiringBundleItem: ...

def attach_acuse(*, bundle_item_id, signature) -> HiringBundleItem: ...

def mark_sent(*, bundle_id) -> HiringDocumentBundle:
    """Move bundle from draft → sent. Requires at least one item with a document."""

def mark_acknowledged_if_complete(*, bundle_id) -> HiringDocumentBundle:
    """Move bundle from sent → acknowledged if all required items have signed signatures."""
```

**Tests (~10):**
- build_bundle_creates_items_in_draft
- build_bundle_default_six_kinds
- build_bundle_with_custom_kinds
- attach_document_persists
- attach_acuse_links_signature
- mark_sent_requires_documents (raises ValidationError if no items have document)
- mark_sent_succeeds_with_items
- mark_acknowledged_no_op_when_required_items_unsigned
- mark_acknowledged_flips_when_all_required_signed
- bundle_item_unique_per_kind_per_bundle (raises IntegrityError on duplicate kind)

**Verification:**
- `manage.py check` exits 0.
- `pytest apps/documents/tests/test_b10_hiring_bundle.py -v` all green.

---

## Task 6: API surface (3 ViewSets + custom actions)

**Files:**
- `apps/api/api/v1/contracts/views.py` (new) — TRegistroDeclarationViewSet
- `apps/api/api/v1/contracts/urls.py` (extend)
- `apps/api/api/v1/contracts/serializers.py` (new)
- `apps/api/api/v1/documents/signature_views.py` (new) — DocumentSignatureViewSet
- `apps/api/api/v1/documents/bundle_views.py` (new) — HiringDocumentBundleViewSet, HiringBundleItemViewSet
- `apps/api/api/v1/documents/urls.py` (extend)
- `apps/api/api/v1/documents/serializers_b10.py` (new) — keep separate from existing
- `apps/api/apps/contracts/tests/test_b10_api_smoke.py`
- `apps/api/apps/documents/tests/test_b10_api_smoke.py`

**Endpoints:**

```
GET    /api/v1/contracts/t-registro-declarations/
POST   /api/v1/contracts/t-registro-declarations/
GET    /api/v1/contracts/t-registro-declarations/<uuid>/
PATCH  /api/v1/contracts/t-registro-declarations/<uuid>/
DELETE /api/v1/contracts/t-registro-declarations/<uuid>/
POST   /api/v1/contracts/t-registro-declarations/<uuid>/generate-anexo3/
POST   /api/v1/contracts/t-registro-declarations/<uuid>/validate-pvs/
POST   /api/v1/contracts/t-registro-declarations/<uuid>/submit/
POST   /api/v1/contracts/t-registro-declarations/<uuid>/mark-accepted/
POST   /api/v1/contracts/t-registro-declarations/<uuid>/mark-rejected/
GET    /api/v1/contracts/t-registro-declarations/<uuid>/anexo3-txt/    (text/plain download)

GET    /api/v1/documents/signatures/
POST   /api/v1/documents/signatures/
GET    /api/v1/documents/signatures/<uuid>/
POST   /api/v1/documents/signatures/<uuid>/capture/
POST   /api/v1/documents/signatures/<uuid>/reject/
POST   /api/v1/documents/signatures/expire-overdue/    (HR-triggered cron substitute)

GET    /api/v1/documents/hiring-bundles/
POST   /api/v1/documents/hiring-bundles/
GET    /api/v1/documents/hiring-bundles/<uuid>/
PATCH  /api/v1/documents/hiring-bundles/<uuid>/
POST   /api/v1/documents/hiring-bundles/<uuid>/send/
POST   /api/v1/documents/hiring-bundles/<uuid>/acknowledge/

GET    /api/v1/documents/hiring-bundle-items/
POST   /api/v1/documents/hiring-bundle-items/<uuid>/attach-document/
POST   /api/v1/documents/hiring-bundle-items/<uuid>/attach-acuse/
```

**ViewSet decisions:**
- TenantAwareViewSetMixin on all tenant-scoped models (TRegistro + Bundle; Signature
  is also tenant-scoped via FK to DigitalDocument tenant — explicit `tenant` field too).
- `RRHHPermission` on all (HR-only — no public exposure even for self-service in B.10).
- Custom actions return APIResponse.success / APIResponse.error per project convention.
- `anexo3-txt` returns `HttpResponse(content_type='text/plain', body=txt)` with
  Content-Disposition attachment filename pattern `tregistro_<ruc>_<period>.txt`.

**Tests — API smoke (~18):**
Per app, parametrized + auth gating + happy-path + state-machine misuse.

**Verification:**
- `manage.py check` clean.
- `pytest apps/contracts/tests/test_b10_api_smoke.py apps/documents/tests/test_b10_api_smoke.py -v` all green.

---

## Task 7: Frontend services + types

**Files:**
- `apps/web/src/features/contracts/services/tRegistroService.ts`
- `apps/web/src/features/contracts/services/__tests__/tRegistroService.test.ts`
- `apps/web/src/features/documents/services/documentSignatureService.ts`
- `apps/web/src/features/documents/services/__tests__/documentSignatureService.test.ts`
- `apps/web/src/features/documents/services/hiringBundleService.ts`
- `apps/web/src/features/documents/services/__tests__/hiringBundleService.test.ts`

Typed clients with TS interfaces matching the API shape; thin wrappers around
`apiClient` (axios from `shared/api/api.ts`). Vitest tests check method names,
return shape, and URL building.

**Verification:**
- `npm test -- --run` shows 3 new files green; total ≥ 88 tests across ≥ 15 files.

---

## Task 8: Admin pages

**Files (lazy-loaded, AdminRoute-gated):**
- `apps/web/src/features/contracts/pages/TRegistroListPage.tsx` — grid filtered by
  status/declaration_type with row actions (Generate Anexo3 → download, Validate PVS
  → show errors, Submit, Mark Accepted, Mark Rejected).
- `apps/web/src/features/contracts/pages/TRegistroDetailPage.tsx` — full declaration
  form (worker/contract/régimen) + status timeline + Anexo3 preview pane.
- `apps/web/src/features/documents/pages/DocumentSignatureListPage.tsx` — signatures
  table with kind, status, signer; row link to detail.
- `apps/web/src/features/documents/pages/DocumentSignatureDetailPage.tsx` — preview
  canvas/typed/checkbox value, capture (HR portal only — typed/checkbox; canvas
  via embedded react-signature-canvas), reject flow.
- `apps/web/src/features/documents/pages/HiringBundleListPage.tsx` — bundle grid by
  employee/status; create new (selecting employee + contract + checking items).
- `apps/web/src/features/documents/pages/HiringBundleDetailPage.tsx` — items table
  with per-row attach-document + attach-acuse actions, Send + Acknowledge.
- Routes added to `App.tsx`:
  - `/contracts/t-registro` + `/contracts/t-registro/:id`
  - `/documents/signatures` + `/documents/signatures/:id`
  - `/documents/hiring-bundles` + `/documents/hiring-bundles/:id`

**Verification:**
- `npm run build` exit 0.
- `npx tsc --noEmit -p tsconfig.app.json` only the pre-existing BlankEnum error.
- `npm run lint` count ≤ 278.

---

## Task 9: Final verification + merge

Steps:
1. Activate venv, run `pytest -q` from `apps/api/`.
2. Run `cd apps/web && npm test -- --run`, `npm run lint`, `npx tsc --noEmit -p tsconfig.app.json`, `npm run build`.
3. Run `D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development`.
4. Compare numbers:
   - pytest ≥ 620 passing (was 568).
   - vitest ≥ 90 tests / ≥ 15 files (was 75 / 12).
   - ESLint ≤ 278 (was 278).
   - tsc 1 error (BlankEnum, pre-existing).
   - build clean.
5. Update `MEMORY.md` pointer + `subproject_b_progress.md`.
6. `git checkout master && git merge --no-ff vyntia/B10-vinculacion-tregistro -m "Merge B.10: Vinculación + T-Registro (Module 03.2) — 3 backlog items, contracts + documents apps"`.

**Done criteria:**
- All 3 backlog items #111, #112, #113 closed.
- Baselines preserved or improved per § Test baselines above.
- Memory file updated with the close-out summary and merge SHA.
