# Vyntia Core — Backlog (B.0 audit)

> Prioritized list of actionable items derived from `INVENTORY.md`. Each item maps to a phase B.X.
> Audit date: 2026-05-09.
> Total items: 132. Total estimated effort: ~22-25 weeks across phases B.1-B.16.

## Priority legend

- **P0** — blocks commercial launch of Vyntia Core
- **P1** — important but not launch-blocking; can ship in later phase
- **P2** — nice-to-have; may be deferred to post-B sub-project

## Type legend

- **bug** — defect in existing code
- **parity** — feature in INTRANET legacy not yet ported to VYNTIA
- **new** — feature from maestro that doesn't exist in VYNTIA or legacy
- **tenant** — multi-tenant readiness fix
- **deuda** — technical debt (lint, tests, docs, refactor)

## Distribution summary

- By priority: 38 P0, 56 P1, 38 P2
- By phase: B.1=22, B.2=12, B.3=11, B.4=14, B.5=20, B.6=8, B.7=4, B.8=4, B.9=4, B.10=8, B.11=6, B.12=8, B.13=4, B.14=6, B.15=10, B.16=4 (totals double-count items spanning multiple phases)

## Backlog

| # | Item | App | Type | Prio | Phase | Deps | Est. |
|---|------|-----|------|:----:|:-----:|------|:----:|
| 1 | Fix login bypass — `test_login_usuario_bloqueado` (estado_usuario=bloqueado not enforced in JWT login) | identity | bug | P0 | B.1 | — | 1d |
| 2 | Fix `intentos_fallidos` counter not incremented on failed JWT login (`test_multiples_intentos_login_fallidos`) | identity | bug | P0 | B.1 | — | 1d |
| 3 | Fix `LoginAPIView` returns 401 instead of 400 on missing fields (`test_login_datos_faltantes`) | identity | bug | P0 | B.1 | — | 0.5d |
| 4 | Fix `LogoutAPIView` accepts invalid refresh tokens (`test_logout_token_invalido`) | identity | bug | P0 | B.1 | — | 0.5d |
| 5 | Fix `UserUpdateSerializer` doesn't persist nombres/apellidos (`test_actualizar_perfil_exitoso`) | identity | bug | P0 | B.1 | — | 0.5d |
| 6 | Introduce `TenantAwareViewSetMixin` setting tenant in perform_create across the 6 Core apps | core | tenant | P0 | B.1 | — | 1d |
| 7 | Fix `Department.perform_create` orphans rows (tenant=NULL) — apply tenant mixin | organization | tenant | P0 | B.1 | #6 | 0.5d |
| 8 | Fix `EmpleadoViewSet.perform_create` orphans rows (tenant=NULL) — apply tenant mixin | employees | tenant | P0 | B.1 | #6 | 0.5d |
| 9 | Fix `EmpleadoCreateSerializer.create()` propagates tenant to nested EmploymentData/FamilyMember/AcademicRecord | employees | tenant | P0 | B.1 | #6 | 1d |
| 10 | Fix `ContratosAdendasViewSet.perform_create` orphans Contract (tenant=NULL) | contracts | tenant | P0 | B.1 | #6 | 0.5d |
| 11 | Fix `ContractAmendmentViewSet.perform_create` orphans Amendment (tenant=NULL) | contracts | tenant | P0 | B.1 | #6 | 0.5d |
| 12 | Fix `ContractAmendmentViewSet` permission gap — anyone authenticated can CRUD amendments (add `@require_hr`) | contracts | bug | P0 | B.1 | — | 0.5d |
| 13 | Fix `DatosLaboralesViewSet.perform_create` orphans EmploymentData (tenant=NULL) | contracts | tenant | P0 | B.1 | #6 | 0.5d |
| 14 | Fix `DocumentosDigitalesViewSet.perform_create` + `subir_institucional` orphan documents (tenant=NULL) | documents | tenant | P0 | B.1 | #6 | 1d |
| 15 | Fix `OnboardingService.crear_onboarding_completo` doesn't propagate tenant to Employee/User/OnboardingProcess | onboarding | tenant | P0 | B.1 | #6 | 1d |
| 16 | Fix `EmpleadoReportService` uses `Employee.objects.get(empleado_id=...)` — endpoint reporte_integral 100% broken | employees | bug | P0 | B.1 | — | 0.5d |
| 17 | Fix `EmpleadoCreateSerializer.area_inicial` IntegerField + `Department.objects.get(area_id=...)` — endpoint create 100% broken | employees | bug | P0 | B.1 | — | 1d |
| 18 | Fix `EmpleadoFilter.filter_area*` uses non-existent `area_id` / `ubicaciones_destino` paths — filters broken | employees | bug | P0 | B.1 | — | 0.5d |
| 19 | Fix `EmpleadoViewSet.transferir` action uses `area_id` field that doesn't exist | employees | bug | P0 | B.1 | — | 0.5d |
| 20 | Fix `EmpleadoViewSet.estadisticas` counts cross-tenant (Employee.objects.count() with no tenant filter) | employees | tenant | P0 | B.1 | — | 0.5d |
| 21 | Fix `Employee.correo_personal` unique=True global — must be (tenant, correo_personal) per-tenant | employees | tenant | P0 | B.1 | — | 0.5d |
| 22 | Fix `DocumentGenerationViewSet.generar_contrato` — Contract.objects.get(contrato_id=) field gone (rename L3.11) | documents | bug | P0 | B.1 | — | 0.5d |
| 23 | Fix `DocumentGenerationViewSet.generar_certificado` — Employee.objects.get(empleado_id=) field gone | documents | bug | P0 | B.1 | — | 0.5d |
| 24 | Fix `DocumentGenerationViewSet` — multiple `documento.documento_id` AttributeErrors (5 callsites) | documents | bug | P0 | B.1 | — | 0.5d |
| 25 | Fix `DocumentGenerationViewSet.subir_plantilla_word` — TypeError `creada_por` kwarg renamed `created_by` | documents | bug | P0 | B.1 | — | 0.5d |
| 26 | Fix `DocumentGenerationViewSet.eliminar/descargar_plantilla_word` — URL regex `[0-9]+` doesn't match UUIDs | documents | bug | P0 | B.1 | — | 0.5d |
| 27 | Fix `DocumentGenerationViewSet.generar_desde_plantilla_word` — 3 IDs read from same `id` query param | documents | bug | P0 | B.1 | — | 1d |
| 28 | Fix `template_service.py` — `get_estado_display()` should be `get_status_display()` (Contract field renamed) | documents | bug | P0 | B.1 | — | 0.5d |
| 29 | Fix `template_service.py:254` — `creado_por_id` attribute doesn't exist (Python attr is `created_by_id`) | documents | bug | P0 | B.1 | — | 0.5d |
| 30 | Fix `word_template_service.py:139` — `contrato.numero_adenda` AttributeError (L3.10.3 stale post-split) | documents | bug | P0 | B.1 | — | 0.5d |
| 31 | Fix `word_template_service.py:175` — `Contract.filter(estado='ACTIVO')` field is `status` | documents | bug | P0 | B.1 | — | 0.5d |
| 32 | Fix `OnboardingService.reenviar_email_bienvenida` uses `.get(onboarding_id=...)` field gone | onboarding | bug | P0 | B.1 | — | 0.5d |
| 33 | Rebrand 11 "Intranet" strings in onboarding email templates (bienvenida, documento_rechazado, onboarding_aprobado, onboarding_observado) | onboarding | bug | P0 | B.1 | — | 0.5d |
| 34 | Fix `test_employee_cannot_patch_restricted_fields` (security: empleado can patch nombres/apellido) | onboarding | bug | P0 | B.1 | — | 1d |
| 35 | Fix `test_corregir_correo_updates_email` — endpoint returns 400 (root cause: bug #32) | onboarding | bug | P0 | B.1 | #32 | 0.5d |
| 36 | Add `.eslintignore` for `src/generated/api/` — eliminates 202 auto-generated lint warnings | core | deuda | P1 | B.1 | — | 0.5d |
| 37 | Fix `BlankEnum.ts:6:5` — regenerate openapi-typescript or add ESLint disable rule | core | deuda | P1 | B.1 | — | 0.5d |
| 38 | Add smoke tests for `DocumentGenerationViewSet` (now-broken endpoints once fixed) | documents | deuda | P1 | B.1 | #22-#27 | 1d |
| 39 | Add smoke tests for `DatosLaboralesViewSet` and ContratosAdendasViewSet (no current ViewSet tests) | contracts | deuda | P1 | B.1 | — | 1d |
| 40 | Fix `EmpleadoFilter.filter_remuneracion_min/max` — field is `sueldo_basico` not `sueldo_basico` | employees | bug | P1 | B.2 | — | 0.5d |
| 41 | Fix `EmpleadoFilter.filter_tiene_conyuge` — parentesco choice is `conyuge` not `esposo`/`esposa` | employees | bug | P1 | B.2 | — | 0.5d |
| 42 | Fix `EmpleadoViewSet.get_queryset filter_by_area` uses `area_id` (FieldError on ?area=) | employees | bug | P1 | B.2 | — | 0.5d |
| 43 | Fix frontend `employeesService.datosLaborales` URL `/api/v1/employment-data/` — actual is `/api/v1/contracts/employment-data/` (audit reconciliation: URL is mounted FLAT at `/api/v1/employment-data/`, frontend is correct; remove this item per Task 12 cross-correction note) | employees | bug | P1 | B.4 | — | 0d |
| 44 | Fix `User.tiempo_desde_ultimo_login` legacy fall-through bug (elif branch returns None implicit) | identity | bug | P1 | B.2 | — | 0.5d |
| 45 | Fix `UsuarioManager.activos()` filters by non-existent `estado` field (FieldError) | identity | bug | P1 | B.2 | — | 0.5d |
| 46 | Fix `Permission.modulo` is CharField legacy — convert to FK to Module model (or document decision) | identity | deuda | P1 | B.2 | — | 1d |
| 47 | Migrate identity ViewSets from `api/v1/rrhh/views.py` to `api/v1/identity/views.py` (L3 split incomplete) | identity | deuda | P1 | B.2 | — | 1d |
| 48 | Add tenant filtering on `PermissionService` and `MenuService` (currently relies 100% on RLS) | identity | tenant | P1 | B.2 | — | 1d |
| 49 | Decide and document `UserRole` vs `TenantMembership.role` source-of-truth (currently both exist) | identity | deuda | P1 | B.2 | — | 0.5d |
| 50 | Fix `AreaSerializer.get_empleados_activos_count` calls non-existent `get_empleados_activos_count()` method | organization | bug | P1 | B.3 | — | 0.5d |
| 51 | Fix `AreaViewSet.empleados()` action calls `area.empleados_actuales()` — method doesn't exist | organization | bug | P1 | B.3 | — | 0.5d |
| 52 | Fix `AreaViewSet.activas()` filters `estado="activa"` — field is `estado_area`, choice is `activo` | organization | bug | P1 | B.3 | — | 0.5d |
| 53 | Fix `LocationHistory.movimiento_completo` and `codigo_movimiento` reference non-existent `nombre_area`/`codigo_area` | organization | bug | P1 | B.3 | — | 0.5d |
| 54 | Fix `Company.get_config(tenant=None)` legacy fallback — risk of cross-tenant leak if middleware fails | organization | tenant | P1 | B.3 | — | 1d |
| 55 | Fix `AreaSerializer.validate_siglas_area` doesn't filter by tenant — blocks legitimate cross-tenant siglas | organization | bug | P1 | B.3 | — | 0.5d |
| 56 | Fix `AreaViewSet.perform_destroy` sets `estado_area="inactiva"` — invalid choice (valid: `inactivo`) | organization | bug | P1 | B.3 | — | 0.5d |
| 57 | Trim ~15 phantom endpoints in frontend `departmentsService` (getAreasStats, getAreaHierarchy, etc.) | organization | deuda | P1 | B.3 | — | 1d |
| 58 | Fix `Department.empleados_activos_count` discrepancy with `estadisticas` (uses distinct vs not) | organization | bug | P2 | B.3 | — | 0.5d |
| 59 | Fix `EmploymentData.generar_codigo_empleado()` uses `self.empleado.empleado_id` — field gone | contracts | bug | P1 | B.4 | — | 0.5d |
| 60 | Fix `ContratosAdendasViewSet.get_queryset` reads empleado_id and area_id from same query param `id` | contracts | bug | P1 | B.5 | — | 0.5d |
| 61 | Fix `ContratosAdendasViewSet.estadisticas` counts cross-tenant (Contract.objects.count() global) | contracts | tenant | P1 | B.5 | — | 0.5d |
| 62 | Fix `ContratosAdendasViewSet.renovar_contrato` doesn't propagate tenant on new contract | contracts | tenant | P1 | B.5 | #6 | 0.5d |
| 63 | Fix `DatosLaboralesViewSet.search_fields/ordering_fields` reference non-existent fields | contracts | bug | P1 | B.5 | — | 0.5d |
| 64 | Fix `DatosLaboralesViewSet.estadisticas_remuneracion` uses non-existent `estado_laboral`/`remuneracion_mensual` fields | contracts | bug | P1 | B.5 | — | 0.5d |
| 65 | Rewrite `DatosLaboralesFilter` — 5 filters reference non-existent fields (reg_laboral, condicion, grupo_ocupacional, puesto, estado, remuneracion) | contracts | bug | P1 | B.5 | — | 1d |
| 66 | Fix `DatosLaboralesSerializer` — `antiguedad_años` (with tilde) and `tiempo_servicio` ReadOnlyField don't resolve | contracts | bug | P1 | B.5 | — | 0.5d |
| 67 | Fix `DatosLaboralesViewSet.queryset` declared twice (first JOINs are dead code) | contracts | bug | P2 | B.5 | — | 0.5d |
| 68 | Fix `pdf_generator.generar_pdf_adenda` passes contrato_id where adenda_id expected (post-split L3.10.3) | documents | bug | P1 | B.5 | — | 0.5d |
| 69 | Fix `pdf_generator._guardar_documento_digital` doesn't set tenant on created DigitalDocument | documents | tenant | P1 | B.5 | #6 | 0.5d |
| 70 | Add `clean()` validation on ContractAmendment (ADENDA_SALARIAL requires nuevo_salario, etc.) | contracts | new | P2 | B.5 | — | 0.5d |
| 71 | Cleanup stale `Contrato` interface fields (numero_adenda, es_contrato_inicial, es_adenda) post-L3.10.3 | contracts | deuda | P2 | B.5 | — | 0.5d |
| 72 | Add UI for ContractAmendment (create/edit/list adendas) — missing post-L3.10.3 split | contracts | new | P1 | B.5 | — | 1w |
| 73 | Fix `apps/contracts/apps.py` docstring is stale (describes pre-split unified model) | contracts | deuda | P3 | B.5 | — | 0.5d |
| 74 | Fix `WordTemplateService` hardcoded EMPRESA_NOMBRE/RUC/DIRECCION/CIUDAD — should read Company.get_config(tenant) | documents | tenant | P1 | B.5 | — | 1d |
| 75 | Fix `TemplateService._obtener_datos_institucion` calls Company.get_config(tenant=None) — needs tenant from request | documents | tenant | P1 | B.5 | — | 1d |
| 76 | Migrate `DocumentGenerationViewSet` from `api/v1/app_rrhh/` to `api/v1/documents/views.py` (L3.11 incomplete) | documents | deuda | P1 | B.5 | — | 1d |
| 77 | Filesystem-level tenant segregation for media uploads (prefix tenant_id in upload_to or auth-walled /media/) | documents | tenant | P1 | B.5 | — | 2d |
| 78 | Fix `DigitalDocument` classmethods (documentos_vencidos, proximos_a_vencer, estadisticas_por_tipo) don't filter tenant | documents | tenant | P2 | B.5 | — | 0.5d |
| 79 | Resolve DocumentTemplate ambiguity (system-wide vs per-tenant) — design decision + filtering | documents | tenant | P2 | B.5 | — | 1d |
| 80 | Fix `OnboardingViewSet` doesn't filter queryset by tenant + retrieve doesn't verify tenant | onboarding | tenant | P1 | B.5 | — | 1d |
| 81 | Fix `OnboardingService.generar_username` not tenant-scoped — username enumeration cross-tenant | onboarding | tenant | P1 | B.5 | — | 0.5d |
| 82 | Migrate `OnboardingViewSet` from `api/v1/rrhh/views.py` to `api/v1/onboarding/views.py` (L3 split incomplete) | onboarding | deuda | P1 | B.5 | — | 1d |
| 83 | Fix `OnboardingNotificationService._enviar_notificacion` silences exceptions without log | onboarding | bug | P1 | B.5 | — | 0.5d |
| 84 | Refactor `OnboardingAdminPage.tsx` (1047-line monolith with 5 `any` lints) | onboarding | deuda | P2 | B.5 | — | 2d |
| 85 | Fix duplicate functions in `onboardingUploadService.ts` (uploadDocument/subirDocumento/uploadFoto target same endpoint) | onboarding | deuda | P2 | B.5 | — | 0.5d |
| 86 | Co-locate tests into `apps/<app>/tests/` (currently all in `apps/api/tests/` root) | core | deuda | P2 | B.5 | — | 1d |
| 87 | Lint cleanup features/identity (15 warnings) | identity | deuda | P2 | B.2 | — | 0.5d |
| 88 | Lint cleanup features/organization (6 warnings) | organization | deuda | P2 | B.3 | — | 0.5d |
| 89 | Lint cleanup features/employees (16 warnings) | employees | deuda | P2 | B.4 | — | 0.5d |
| 90 | Lint cleanup features/contracts + documents + onboarding | contracts | deuda | P2 | B.5 | — | 0.5d |
| 91 | Add `Employee.ruta_fotografia` ImageField (currently CharField — no upload, no validation) | employees | deuda | P2 | B.4 | — | 1d |
| 92 | Add UI for `Certification` (cursos/certificaciones) — model+API exist, no frontend | employees | new | P2 | B.4 | — | 2d |
| 93 | Add encryption AES-256 for sensitive Employee fields (tipo_sangre, talla, peso, centro_salud) — Ley 29733 | employees | new | P1 | B.4 | — | 1w |
| 94 | Add `WorkExperience`/`PreviousJob` model — maestro § 03.5 #3 (legajo content) | employees | new | P1 | B.12 | — | 2d |
| 95 | Add `SwornDeclaration`/`Declaration` model — maestro § 03.5 #5 (declaraciones juradas) | employees | new | P1 | B.12 | — | 2d |
| 96 | Add `JobHistory` model + UI for puestos ocupados timeline — maestro § 03.5 #7 | employees | new | P2 | B.12 | — | 2d |
| 97 | Extend Contract.tipo_documento to 11 régimen 728 types per maestro (Inicio/Incremento, Necesidad mercado, etc.) | contracts | new | P1 | B.10 | B.5 | 2d |
| 98 | Implement Art. 77 LPCL desnaturalización logic (5-year cumulative cap → indeterminado) | contracts | new | P1 | B.10 | #97 | 1w |
| 99 | Add `Contract.regimen_laboral` field explicit (currently implicit via tipo_documento prefix) | contracts | deuda | P2 | B.10 | — | 1d |
| 100 | Add status auto-update job (VENCIDO when fecha_fin<today) + email notifications | contracts | new | P2 | B.10 | — | 2d |
| 101 | Add LocationHistory REST endpoints + frontend UI (model exists, no API/UI) | organization | parity | P1 | B.13 | — | 1w |
| 102 | Module 02: Position + PositionProfile + OrgUnit + Plaza + RiskProfile + CIUOCode + OccupationalCategory | organization | new | P1 | B.6 | B.3 | 2w |
| 103 | Module 02: Org chart UI (drag-drop, parent-child, search, PDF export) — uses ADR-B.8 | organization | new | P1 | B.6 | #102 | 1w |
| 104 | Module 02: Migration EmploymentData.cargo (string) → EmploymentData.position (FK) with backfill | organization | new | P1 | B.6 | #102 | 2d |
| 105 | Module 02: CategoryFunctionTable (CCF) — Ley 30709 compliance | organization | new | P1 | B.7 | B.6 | 1w |
| 106 | Module 02: SalaryBand (min/medio/max) + análisis brechas Ley 30709 + import Excel | organization | new | P1 | B.7 | #105 | 1w |
| 107 | Module 02: MPP (Manual Perfiles) — sector público SERVIR | organization | new | P1 | B.8 | B.6 | 1w |
| 108 | Module 02: CPE (Cuadro Puestos Entidad) — Ley 30057 SERVIR | organization | new | P1 | B.8 | #107 | 1w |
| 109 | Module 02: CAP (Cuadro Asignación Personal) — sector público 276/728 | organization | new | P2 | B.8 | #107 | 0.5w |
| 110 | Module 03.1: Selección — PersonnelRequisition, JobPosting, JobApplication, Candidate, SelectionStage, CandidateEvaluation, MeritRanking | employees | new | P1 | B.9 | B.6 | 2w |
| 111 | Module 03.2: T-Registro SUNAT integration — TRegistroDeclaration model + Anexo 3 txt + PVS validation | contracts | new | P1 | B.10 | B.5 | 2w |
| 112 | Module 03.2: DocumentSignature + e-signature flow UI | documents | new | P1 | B.10 | — | 1w |
| 113 | Module 03.2: Hiring document bundle automation (RIT, Reglamento SST, etc. + acuse) | documents | new | P1 | B.10 | — | 1w |
| 114 | Module 03.3: Inducción RPE 265-2017 — InductionPlan, InductionTask, InductionMaterial, InductionMentor, InductionEvaluation | onboarding | new | P1 | B.11 | B.10 | 1w |
| 115 | Module 03.3: Generation of certificado de inducción finalización (RPE 265 obligatorio) | onboarding | new | P1 | B.11 | #114 | 0.5w |
| 116 | Module 03.4: ProbationPeriod model with régimen-specific plazos + alertas + evaluación + ratificación | contracts | new | P1 | B.11 | B.10 | 1w |
| 117 | Module 03.5: DigitalDossier + 13 sections + DocumentAccessLog + retention 5y + full-text search + cifrado AES-256 | documents | new | P1 | B.12 | B.5 | 2w |
| 118 | Module 03.5: Permission level enforcement per document type (granular RBAC, médicos permlevel 9) | documents | new | P1 | B.12 | — | 1w |
| 119 | Module 03.5: Exportación consolidada PDF del legajo (fix `EmpleadoReportService` first — see #16) | documents | new | P1 | B.12 | #16 | 0.5w |
| 120 | Module 03.5: Add `DigitalDocument.contrato` direct FK (currently inferred indirectly) | documents | deuda | P2 | B.12 | — | 1d |
| 121 | Module 03.5: Document access audit trail (DocumentAccessLog) — Ley 29733 + SUNAFIL | documents | new | P1 | B.12 | — | 1w |
| 122 | Module 03.6: Desplazamiento (Displacement model + 7 tipos rotación/encargatura/destaque/comisión/permuta/designación/transferencia) + workflow | organization | new | P1 | B.13 | B.6 #101 | 2w |
| 123 | Module 03.7: Termination model (728 + 276 + CAS causales) + cease workflow | contracts | new | P1 | B.14 | B.10 | 1w |
| 124 | Module 03.7: SeveranceSettlement minimum legal (CTS+vacaciones truncas+gratificación trunca+indemnización 1.5/año) per ADR-B.9 | contracts | new | P1 | B.14 | #123 | 1w |
| 125 | Module 03.7: WorkCertificate auto-gen (Art. 45 LPCL) | documents | new | P1 | B.14 | #123 | 0.5w |
| 126 | Module 03.7: SystemsOffboarding integration + ExitInterview + HandoverChecklist | core | new | P2 | B.14 | #123 | 1w |
| 127 | Module 03.7: Baja T-Registro (reusa cliente B.10) + 48h SLA pago alerta | contracts | new | P1 | B.14 | B.10 | 0.5w |
| 128 | Module 01: Policies (Policy + PolicyVersion + PolicyApprovalFlow + PolicyPublication + PolicyAcknowledgment) | core | new | P1 | B.15 | ADR-B.4 | 1w |
| 129 | Module 01: HRStrategicPlan + StrategicObjective + KPI | core | new | P1 | B.15 | — | 0.5w |
| 130 | Module 01: WorkforcePlan + HeadcountProjection + SuccessionPlan + KeyPosition + SuccessorCandidate | core | new | P1 | B.15 | — | 0.5w |
| 131 | Module 01: ComplianceMatrix + ComplianceObligation + Evidence with vencimiento alerts | core | new | P1 | B.15 | — | 0.5w |
| 132 | E2E close-out: Playwright lifecycle test (provision tenant → empleado → contrato → onboarding → cese) per ADR-B.5 | core | deuda | P1 | B.16 | all | 1w |

## Notes on synthesis

- **Cross-correction applied (Task 12 note):** `/api/v1/employment-data/` IS the correct URL (mounted flat per `apps/api/api/v1/urls.py:30`); the original Task 4 inventory note about a broken URL has been removed from this backlog (item #43 reduced to 0d, retained for traceability).
- **TenantAwareViewSetMixin (#6)** is the umbrella fix that replaces ~10 individual `perform_create` patches across apps. It is listed first in B.1 because items #7-#15 depend on it.
- **Phase B.16 (E2E close-out)** is intentionally light (1 item) — it consumes verification effort, not new feature delivery.
- **Module 02 (B.6-B.8) and Module 03 (B.9-B.14)** dominate the volume; items #102-#127 represent ~60% of total effort.
- **Severance scope (#124)** is intentionally minimum-legal-only per ADR-B.9; the full payroll engine ships in sub-project D.
- **L3.x consumer audit pattern:** items #22-#34 cluster around the same root cause — incomplete consumer updates after model renames in L3.10.x and L3.11. They are batched into B.1 fast-track.
