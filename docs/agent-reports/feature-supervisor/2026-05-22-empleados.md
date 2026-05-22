# Feature Supervisor — Módulo Empleados (2026-05-22)

**Agente:** `vyntia-feature-supervisor`
**Scope:** módulo Empleados (apps/employees + api/v1/employees + features/employees + features/recruitment + B.12 dossier)
**Modo:** read-only audit
**Orquestado por:** main agent (PM mode) — el feature-supervisor devolvió este contenido inline y el orquestador lo persistió a disco para mantener el contrato `docs/agent-reports/`.

---

## Verdict global

**Verde con condiciones.** Módulo Empleados core sólido; ATS B.9 funcional; Legajos B.12 tiene un agujero de permisos crítico.

**Salud técnica baseline:**
- `manage.py check --settings=vyntia.settings.development` → `0 issues silenced` (PASS)
- `makemigrations --check --dry-run` → `No changes detected` (PASS)
- 114 tests en `apps/employees/tests/` + 25 B.12 docs tests + 14 B.12 access-log tests

---

## TL;DR (5 bullets)

- **Routes + viewsets:** todas las URL prometidas (`/api/v1/employees/`, `family-members`, `academic-records`, `certifications`, `candidates`, `personnel-requisitions`, `job-postings`, `selection-stages`, `job-applications`, `candidate-evaluations`, `merit-rankings`, `work-experiences`, `sworn-declarations`, `job-histories`, `documents/digital-dossiers`) resuelven y son alcanzables.
- **Frontend:** las 9 páginas de `features/employees/pages/` + 3 de `features/recruitment/pages/` + `DigitalDossierListPage` están registradas en `App.tsx`. Sidebar (`seed_menu.py`) cubre Empleados, Selección e Inducción.
- **Agujero de seguridad (B.12):** `permission_level` (PL 1-9) está modelado y existe `access_service.can_access()` pero NINGUNA viewset lo invoca — secciones PL 9 (médicos, accidentes laborales) son visibles a cualquier RRHH. Spec lo promete explícitamente. **CRÍTICO** antes de comercializar Vyntia Core.
- **Backlog item caído:** Batch import de empleados desde CSV (B.4 plan, prioridad P1 según spec § 3.3) NO existe. Grep en `api/v1/rrhh|api/v1/employees` no encuentra `csv|batch|import`.
- **Tenant isolation parcial en B.9:** `SelectionStageViewSet`, `CandidateEvaluationViewSet`, `MeritRankingViewSet` no extienden `TenantAwareViewSetMixin` (los modelos relacionados no tienen tenant FK directo). Aislamiento depende de la cadena de FKs — funciona, pero rompe el patrón uniforme.

**Riesgo D (Vyntia Pay):** la base `Employee` + `EmploymentData` + `Contract` está sólida (tests de PK UUID, tenant uniqueness, area lookup), pero NO hay batch import → onboarding masivo de un nuevo cliente para arrancar planilla será doloroso.

---

## Tabla feature × estado

### Core empleados (B.4 + L3.x)

| Feature | BE | FE | Permiso | Tests | Estado |
|---|---|---|---|---|---|
| CRUD Employee + `estadisticas` + `activos` | `api/v1/rrhh/views.py:377-755` | `Empleados.tsx`, `EmpleadosListPage.tsx` | `EmpleadoPermission` + `@require_hr()`/`@require_authenticated()` | `test_employee_viewset.py`, `test_employee_correo_unique.py`, `test_employee_create_serializer.py`, `test_employee_filter.py` | ✅ |
| `datos_completos` + `reporte_integral` PDF | `views.py:605, 722, 740` + `apps/employees/services/employee_report_service.py` | `EmpleadoReportPage.tsx` | `@require_permissions(["ver_empleados"])` | `test_employee_report_service.py` | ✅ |
| Transferir empleado (acción) | `views.py:626-674` | (no UI directa) | `@require_hr()` | ⚠️ sin test | ⚠️ |
| Datos personales (auto-edit campos limitados) | `views.py:441-498` whitelist `_SELF_EDITABLE_FIELDS` | `DatosPersonalesPage.tsx`, `TabPersonales.tsx` | `IsAuthenticated` para `partial_update` con whitelist | (parte del viewset test) | ✅ |
| Datos laborales | `DatosLaboralesViewSet views.py:1019` | `DatosLaboralesPage.tsx`, `TabLaborales.tsx` | `@require_hr`/`@require_authenticated` | `test_employment_data.py` | ✅ |
| Datos familiares (auto-CRUD para el propio empleado) | `DatosFamiliaresViewSet views.py:760-859` | `DatosFamiliaresPage.tsx`, `TabFamiliares.tsx` | check inline `user.empleado == instance.empleado` | ⚠️ sin test directo de auto-edit | ⚠️ |
| Datos académicos | `DatosAcademicosViewSet views.py:861` | `DatosAcademicosPage.tsx`, `TabAcademicos.tsx` | check inline | ⚠️ sin test directo | ⚠️ |
| Cursos / certificaciones | `CursosCertificacionesViewSet views.py:962` | (parte del Tab académicos) | check inline | ❌ sin test | ⚠️ |
| Batch import CSV (#130 B.4 plan) | ❌ no existe | ❌ | n/a | ❌ | ❌ |
| `Employee.ruta_fotografia` ImageField (#91) | ⚠️ deferred per B.4 plan task 1 — sigue diferido | ⚠️ | n/a | n/a | ⚠️ deferred |
| HR Overview dashboard (KPIs) | usa `employees/activos` + `contratos/estadisticas` | `HROverviewDashboard.tsx` | `<AdminRoute>` | ❌ sin test e2e | ⚠️ |

### B.9 — Selección (ATS Module 03.1)

| Feature | BE | FE | Permiso | Tests | Estado |
|---|---|---|---|---|---|
| Candidate (decoupled de User) | `models/candidate.py`, `views.py:44` | (form en `CandidateDashboardPage`) | `RRHHPermission` + tenant mixin | `test_b9_candidate.py` (6) + smoke | ✅ |
| PersonnelRequisition + doble aprobación (HR + Finanzas) | `views.py:56-135`, actions submit/approve-hr/approve-finance/reject/cancel | `RequisitionListPage.tsx` | `RRHHPermission` | `test_b9_personnel_requisition.py` (12) + smoke | ✅ |
| JobPosting (privado + público SERVIR) + lifecycle | `views.py:138-217`, actions publish/start-evaluation/close/declare-void/compute-ranking | `JobPostingEditorPage.tsx` | `RRHHPermission` | `test_b9_job_posting.py` (13) cubre plazos SERVIR ≥7d, nota ≥14, transparency flag | ✅ |
| SelectionStage configurable | `views.py:220-227` | (sub-form en editor) | `RRHHPermission` | `test_b9_selection_stage.py` (8) | ✅ (sin TenantAwareMixin) |
| JobApplication + advance/eliminate/withdraw | `views.py:230-288` | `CandidateDashboardPage.tsx` | `RRHHPermission` + tenant | `test_b9_job_application.py` (10) | ✅ |
| CandidateEvaluation (score → passed auto) | `views.py:291-302` | (parte del dashboard) | `RRHHPermission` | `test_b9_candidate_evaluation.py` (7) | ✅ (sin TenantAwareMixin) |
| MeritRanking (compute via service) | `views.py:305-312` + `services/ranking_service.py` (`compute_merit_ranking`) | (rendered) | `RRHHPermission` (read-only) | `test_b9_merit_ranking.py` (8) cubre ties, eliminatoria, requested_count, idempotente | ✅ |
| Frontend `selectionService` | n/a | `features/recruitment/services/selectionService.ts` | n/a | `selectionService.test.ts` | ✅ |
| Comité de Selección con RBAC (spec 11 ATS § 2.2) | ❌ no implementado (deferred per B.9 plan: "simplified to evaluator FK") | ❌ | n/a | n/a | ⚠️ diferido a M11 |
| Portal público de candidatos | ❌ deferred per B.9 plan | ❌ | n/a | n/a | ⚠️ diferido a B.9.1/M11 |
| Multi-portal posting (LinkedIn, Computrabajo) | ❌ M11 | ❌ | n/a | n/a | ⚠️ diferido |

### B.12 — Legajos Digitales (Module 03.5)

| Feature | BE | FE | Permiso | Tests | Estado |
|---|---|---|---|---|---|
| WorkExperience CRUD | `legajo_views.py:16` | `legajoContentService.ts` | `RRHHPermission` + tenant | `test_b12_legajo_content.py` + `test_b12_api_smoke.py` | ✅ |
| SwornDeclaration (4 tipos) | `legajo_views.py:26` | `legajoContentService.ts` | `RRHHPermission` | `test_b12_api_smoke.py::test_create_4_kinds` | ✅ |
| JobHistory timeline | `legajo_views.py:36` | `legajoContentService.ts` | `RRHHPermission` | `test_b12_api_smoke.py::TestJobHistoryCRUD` | ✅ |
| DigitalDossier (15 secciones seeded) + build idempotente | `apps/documents/services/dossier_service.py`, `dossier_views.py:25` | `DigitalDossierListPage.tsx` (lazy en App.tsx:112) | `RRHHPermission` | `test_b12_dossier_models.py` (10) + smoke | ✅ |
| Consolidated PDF | `dossier_views.py:70-78` | (download trigger) | `RRHHPermission` | `test_b12_api_smoke.py::test_consolidated_pdf_download` | ✅ |
| DocumentAccessLog (Ley 29733 / SUNAFIL) | `apps/documents/models/document_access_log.py` + `access_service.py` | (no UI viewer todavía) | `RRHHPermission` (read-only) | `test_b12_access_log.py` (14) | ✅ modelo / ⚠️ no se invoca en flujo |
| **Permission level enforcement (#118)** | ⚠️ existe en `access_service.can_access()` pero NO se invoca en `DossierSectionViewSet`/`DigitalDossierViewSet`/`DocumentGenerationViewSet` | ❌ FE no filtra por PL | `RRHHPermission` (granularidad PL 9 ignorada) | unit tests del service OK, ❌ no hay integration test que verifique que un user PL3 reciba 403 al pedir un doc PL9 | ❌ **CRÍTICO** |
| Sidebar item "Legajos Digitales" → `/legajos-digitales` | n/a | ⚠️ ruta existe en `App.tsx:526` pero `seed_menu.py` NO la registra (solo `/legajo` user-facing) | n/a | n/a | ⚠️ |
| AES-256 at rest + OCR + FTS | ❌ deferred per plan | ❌ | n/a | n/a | ⚠️ diferido (declarado out-of-scope) |
| ARCO portability export | ❌ deferred | ❌ | n/a | n/a | ⚠️ diferido |

### B.11 — Inducción + Período prueba (cross-module)

| Feature | BE | FE | Estado |
|---|---|---|---|
| InductionPlan CRUD + lifecycle + certificate-pdf | `apps/onboarding/...` + `api/v1/onboarding/induction-plans/` | `InductionPlanListPage.tsx` (lazy) | ✅ — vive en `onboarding`, no `employees`, pero ligado por FK |
| ProbationPeriod | `apps/contracts/...` | `ProbationPeriodListPage.tsx` | ✅ — vive en `contracts` |

---

## Huecos críticos (lo que la spec/maestro prometen y no está en código)

1. **B.12 #118 — Permission-level enforcement en API.** El spec lo lista como P1 en `2026-05-14-vyntia-B12-legajos-completos.md:34`. El servicio `apps/documents/services/access_service.py:39 can_access()` y `:68 check_and_log()` existen pero NINGUNA viewset los invoca. Riesgo legal directo: cualquier RRHH puede leer fichas médicas / accidentes (PL 9). Evidencia: `grep -n permission_level api/v1/documents/dossier_views.py api/v1/employees/legajo_views.py` → 0 matches.

2. **B.12 #121 — DocumentAccessLog audit trail.** El modelo y el servicio existen y son llamables, pero los viewsets de descarga (`consolidated_pdf`, `DigitalDocument`) no llaman `log_access()` ni `check_and_log()`. Ley 29733 + SUNAFIL exigen registro de cada acceso a datos personales. Evidencia: `grep -rn log_access apps/documents/services/access_service.py api/v1/documents/` → solo aparece dentro del propio service, ningún caller.

3. **B.4 backlog #130 — Batch import CSV de empleados.** Marcado P1 en `2026-05-09-vyntia-B-vyntia-core-functional-design.md:130`. No implementado. Sin esto, onboarding inicial de un cliente con 200+ empleados (típico para vender Starter) requiere CRUD manual.

4. **Menu/sidebar gap — `/legajos-digitales`.** Ruta registrada en `App.tsx:526` y página existe, pero `apps/api/apps/identity/management/commands/seed_menu.py` no incluye un item del sidebar que lleve al usuario allí. UX-blocker: feature inalcanzable salvo escribiendo URL.

5. **Doble registro de `/desplazamiento`.** `App.tsx:539` declara la página real (DisplacementListPage lazy) y `App.tsx:650` declara un stub "Modulo en desarrollo". React Router toma la primera coincidencia: el primer match resuelve, pero el stub es residuo del menu seed que apunta a la misma ruta — confuso para futuras mantenciones. No bloquea pero merece limpieza.

6. **B.9 TenantAwareMixin inconsistencia.** `SelectionStageViewSet` (`views.py:220`), `CandidateEvaluationViewSet` (`views.py:291`) y `MeritRankingViewSet` (`views.py:305`) no extienden `TenantAwareViewSetMixin`. Sus modelos no tienen tenant FK propio (cadena vía posting/application), así que el aislamiento depende de filterset_fields enviados por el cliente. Si un atacante autenticado consulta `/api/v1/selection-stages/?posting=<id-de-otro-tenant>`, no hay validación cross-tenant explícita. Verificar manualmente.

---

## Tests faltantes top-5

1. **Integration test: PL 9 negar a usuario PL 3.** Spec B.12 promete enforcement; modelo y service tienen unit tests pero falta el smoke que pegue a `/api/v1/documents/digital-documents/<id>/` con un usuario `nivel_acceso='medio'` esperando 403/denied-log. Cubre #118 + #121 a la vez.
2. **EmpleadoViewSet `transferir` action.** `views.py:626` no tiene test. Es una acción que mueve un empleado entre áreas — relevante para D (Vyntia Pay) si se cambia área a mitad de planilla.
3. **DatosAcademicos / Cursos auto-edit.** Hay tests para correo único y para filter, pero el flow "empleado edita su formación" (PATCH `/api/v1/academic-records/<id>/`) no tiene test que verifique permisos contra otros empleados (cross-employee leak).
4. **`CursosCertificacionesViewSet` entero.** Cero tests dedicados (`grep test_certif` en `apps/employees/tests/` → 0).
5. **Cross-tenant isolation para B.9 stages/evaluations/rankings.** Falta test que reproduce ataque: usuario del tenant A consulta `?posting=<uuid del tenant B>` y verifique queryset filtering.

---

## Riesgos para arrancar D (Vyntia Pay)

| Riesgo | Severidad | Mitigación |
|---|---|---|
| Sin batch import CSV, onboarding de cliente con 200+ trabajadores antes de correr planilla = trabajo manual semanas | **ALTO** | Cerrar #130 antes de D.0 o crear command `manage.py import_employees_csv` |
| `Employee.fecha_cese` y `motivo_cese` viven en `EmploymentData` (no en `Employee`) — el query path para planilla "trabajadores activos al cierre del periodo" es no obvio. Hay test `test_no_stale_area_destino_chain_in_get_queryset` pero no un test "obtener planilla de mes X" | **MEDIO** | Documentar el join `Employee.datos_laborales.filter(estado_datos='activo')` en CLAUDE.md (ya lo está) y agregar smoke test "snapshot planilla por mes" en D.0 |
| `Employee.tenant` FK existe y unique constraints están bien (`unique_employee_doc_per_tenant`, `unique_tenant_correo`), pero los modelos B.9 sin tenant FK directo (SelectionStage, CandidateEvaluation, MeritRanking) podrían filtrar al armar reportes de "candidato → hire → boleta" | **BAJO** | Agregar TenantAwareViewSetMixin a esos 3 viewsets antes de D, o validar `posting.tenant == request.tenant` en `get_queryset` |
| Sin enforcement de `permission_level`, un Analista RRHH puede leer fichas médicas → si D agrega historial salarial sensible sin pasar por dossier, ese gap se propaga | **MEDIO** | Cerrar #118 (enforcement en viewsets) antes de D.0 |
| `EmpleadoReportService` depende de `apps.documents.services.pdf_generator.PDFGenerator` que en Windows solo tiene ReportLab → reporte PDF actual es stub. D necesitará boletas PDF reales | **MEDIO** | Decidir vendor (xhtml2pdf vs WeasyPrint vs ReportLab) en D.0 ADR — no es bloqueante para empleados pero sí para Pay |
