# PM — Audit Empleados v3 post Sprint Hot-fix (2026-05-22)

**Orquestador:** main agent en rol PM (siguiendo playbook `.claude/agents/vyntia-pm.md`).
**Scope:** verificación runtime de los Bloques A-E del Sprint Empleados Hot-fix (5 commits: `d07155c6`, `78a6895a`, `9ebef339`, `59fa55d8`, `d66d9d1e`).
**Especialistas lanzados (4, en paralelo):** feature-supervisor, code-quality, ui-modular, hr-tester.
**Reportes fuente:** todos persistidos en `docs/agent-reports/{agente}/2026-05-22-empleados-v3.md`.

---

## TL;DR — Verdict ejecutivo

🟡 **AMARILLO claro.** Pasamos de 🔴 (v2) a 🟡 con bordes verdes. **11 de los 12 hallazgos críticos/altos del v2 cerrados en runtime** (confirmado por 4 especialistas independientes ejecutando código real). **Surgieron 4 hallazgos NUEVOS**, todos CORTO PLAZO (~1.5 h total).

**Lo bueno:**
- Los 4 P0 NUEVOS del v2 (academic-records 500, cross-tenant leak en 4 viewsets, DNI inválidos persistentes, menores ilegales) están **cerrados runtime con evidencia HTTP**.
- B.12 compliance (PL gate + DocumentAccessLog) funciona end-to-end.
- Dual control PersonnelRequisition rechaza correctamente.
- Vacaciones por régimen, locación excluida de planilla, reporte PDF empleado (7126 bytes, no crash) — todos confirmados.
- Suite: **985/1/17** sin regresiones.
- N+1 en `EmpleadoListSerializer`: 73 → 66 queries (mejora colateral, no fix dirigido).
- **D-Pay-ready peruano** (hr-tester).

**Lo crítico que apareció ahora:**
1. **🔴 P1 NUEVO — Seed `demo-pro` no tiene RolePermission rows.** El Bloque E rebautizó los roles ("Administrador RRHH" / "Analista RRHH") pero NO los relacionó con permisos. `admin.permisos_activos().count() == 0` → cualquier endpoint con `@require_permissions(["ver_empleados"])` devuelve 403 al admin del demo. Existe el command `setup_roles_permisos` que el seed debería invocar.
2. **🟠 ALTO NUEVO — `validate_numero_documento` sin scope tenant.** Mi validator del Bloque A hace `Employee.objects.filter(numero_documento=value).exists()` sin filtrar por tenant. Falso-positivo cross-tenant: tenant B no puede crear empleado con DNI ya usado en tenant A, aunque el constraint DB lo permita (es `unique_together` con tenant). Rompe primer alta multi-cliente.
3. **🟠 ALTO NUEVO — Seed `--fresh` no borra DocumentAccessLog.** El Bloque B agregó AccessLog rows en `consolidated_pdf`. `_wipe_demo_tenant` del Bloque E no las borra. Próximo `--fresh` después de un download deja huérfanos o falla por PROTECT.
4. **🟠 ALTO frontend NUEVO — Mismatch con sprint backend.** `dossierService.downloadConsolidatedPdf` no parsea 403 Blob → user ve "status code 403" en lugar del mensaje legible del PL gate. `NuevoEmpleadoDialog` sin validación inline → depende 100% del 400 del backend (UX mala).

---

## Hallazgos top (consolidado de los 4 especialistas)

### ✅ Cerrados runtime (verificados independientemente por 2+ especialistas)

| # | Hallazgo previo | Verificación runtime | Fuente |
|---|-----------------|----------------------|--------|
| 1 | `/api/v1/academic-records/` 500 | 200 OK con 15 records | feat + hr |
| 2 | Cross-tenant leak FamilyMembers/Academic/Cursos/SelectionStage | 9 escenarios con 0 leak | feat + hr |
| 3 | DNI inválidos persistentes (`"1234567"`, `"ABC12345"`) | 400 con mensaje correcto | feat + hr |
| 4 | Menores ilegales aceptados | 17 años → 400, mención Ley 28518 | feat + hr |
| 5 | PL gate `permission_level` no enforced (#118) | nivel=personal lee solo PL ≤3, total lee todo | feat |
| 6 | DocumentAccessLog vacío en flujo real (#121) | Download + denied registrados con notes y user_agent | feat |
| 7 | Dual control PersonnelRequisition roto | `ValidationError("Control dual...")` correcto | code + hr |
| 8 | SERVIR Art. 5 días calendario | 5 hábiles falla con mensaje "días hábiles" | code + hr |
| 9 | `calcular_vacaciones_pendientes` hardcoded 30 | 728/276/1057=30, prácticas=15, locación=0 | hr |
| 10 | Locación mezclada en planilla | `genera_planilla()=False`, `REGIMENES_PLANILLA` excluye | hr |
| 11 | Reporte PDF empleado: ImportError + VariableDoesNotExist | 7126 bytes `%PDF-1.4` válido | hr |

### 🔴🟠 Hallazgos NUEVOS de v3

| # | Hallazgo | Severidad | Horizonte | Fuente | Evidencia |
|---|----------|-----------|-----------|--------|-----------|
| N1 | Seed sin `RolePermission` — admin no tiene permisos en BD | 🔴 P1 | CORTO (20 min) | feature-supervisor | `admin.permisos_activos().count() == 0`; `@require_permissions` retorna 403; existe command `setup_roles_permisos` que se debería invocar |
| N2 | `validate_numero_documento` sin filtro tenant — falso positivo cross-tenant | 🟠 ALTO | CORTO (15 min) | code-quality | El check `Employee.objects.filter(numero_documento=value).exists()` no filtra por tenant; rompe primer alta multi-cliente |
| N3 | Seed `--fresh` no borra `DocumentAccessLog` | 🟠 ALTO | CORTO (5 min) | code-quality | Bloque B agregó rows en consolidated_pdf; `_wipe_demo_tenant` no las borra → PROTECT o huérfanos |
| N4 | Frontend `dossierService.downloadConsolidatedPdf` no parsea 403 Blob | 🟠 ALTO | CORTO (15 min) | ui-modular | User ve "status code 403" en vez del mensaje legible del PL gate |
| N5 | `NuevoEmpleadoDialog` sin validación inline DNI/edad | 🟠 ALTO | CORTO (30 min) | ui-modular | Depende 100% del 400 backend — UX inferior; el usuario solo recibe error después de submit |
| N6 | 3 viewsets B.9 (SelectionStage/CandidateEvaluation/MeritRanking) divergen del patrón TenantAwareViewSetMixin | 🟡 MEDIO | MEDIO | code-quality | Usan custom `posting__tenant` filter — funciona pero rompe consistencia |
| N7 | Dos cálculos de edad mínima distintos en código (`18*365` vs `today.replace(year=-18)`) | 🟡 MEDIO | CORTO (5 min) | code-quality | Riesgo de off-by-one en años bisiestos |
| N8 | `_business_days_between` sin tests dedicados ni catálogo feriados | 🟡 MEDIO | CORTO (30 min para tests) | code-quality | Docstring marca como interim; ningún test garantiza el comportamiento |

### 📋 Pendientes del v2 que NO se tocaron (deuda explícita)

- `EmpleadosListPage.tsx:100` ReferenceError — confirmado huérfano (no enrutado). **Seguro borrar.**
- `HROverviewDashboard.tsx:479,496,589,658` `p.status` vs `p.estado` — KPI 10% siempre. 10 min fix.
- 5 imports rotos `@/shared/ui/loading-spinner` — invisibles por `tsconfig.json:8` que aborta tsc con TS5103.
- 29 console.log debug en frontend empleados.
- Batch import CSV (#130) — bloqueador onboarding masivo.
- Sidebar `/legajos-digitales` falta en `seed_menu.py` — UX-blocker.

### 🆕 Out-of-scope mapped por hr-tester

- **CTS + Gratificación** → SCOPE D-Pay (D.1 + D.2). No es regresión.
- **DNI módulo 11 (dígito verificador)** → GAP largo plazo, no regulatorio.
- **Practicantes 16-17 Ley 28518 flujo dedicado** → scope post-D ("sub-proyecto I — Onboarding extendido").
- **MyPE en vacaciones** → TODO documentado en docstring; entrará en D.0 ADR como `RegimenLaboralConfig`.

---

## Trends que cruzan los 4 reportes

1. **El patrón "validator sin scope tenant" se repitió.** El primer caso (DNI validator del Bloque A) fue el fix del v2. Ahora aparece otra vez en `validate_numero_documento` mismo. Cuando agregamos validators únicos en serializers multi-tenant, **siempre** deben filtrar por `tenant=self.context['request'].tenant`. Sugerencia: agregar un helper `unique_per_tenant_check(model, field, value, request)` en `apps/core/`.

2. **Backend evolucionó, frontend se quedó.** El sprint tocó 5 áreas críticas backend; el frontend no recibió ningún cambio. Esto generó 2 mismatches runtime (N4, N5) y abre la pregunta: ¿debemos meter un mini-sprint frontend (`Bloque F`) antes de D? El sketch refinado de ui-modular (4.5h para `<ModuleGate>`) sugiere que sí.

3. **El seed sigue siendo fuente de bugs detectables solo cuando funciona.** El v2 detectó 3 bugs del seed (roles incorrectos, workflow saltado, sin evaluations/ranking). El v3 detecta 2 más (sin RolePermission, sin wipe AccessLog). Sugerencia: agregar al seed un self-check post-creación que verifique permisos efectivos del admin.

4. **`tsconfig.json:8` ciega el tooling.** ui-modular confirmó que los 5 imports rotos del v2 siguen invisibles porque `tsc` aborta con TS5103. Esto es **infraestructura crítica**: arreglar `tsconfig` debe ser el primer item del próximo sprint, antes que cualquier fix UI.

---

## 3 acciones priorizadas

### 1. CORTO INMEDIATO — Sprint "Empleados Hot-fix v2" (~1.5-2 h)

8 fixes atómicos. Sin dependencias entre ellos. Pueden hacerse en paralelo y commitearse atómicos.

- [ ] (20 min) **N1**: integrar `setup_roles_permisos` al final de `seed_demo_pro`, o seedear `RolePermission` inline. Self-check: `admin.permisos_activos().count() > 0`.
- [ ] (15 min) **N2**: agregar filtro tenant en `validate_numero_documento`, `validate_correo_personal`, y cualquier otro validator de unicidad que tenga el mismo bug.
- [ ] (5 min) **N3**: agregar `DocumentAccessLog.objects.filter(document__empleado__tenant=tenant).delete()` al `_wipe_demo_tenant`.
- [ ] (15 min) **N4**: en `dossierService.downloadConsolidatedPdf`, parsear el blob 403 a JSON y mostrar `APIResponse.error.message`.
- [ ] (30 min) **N5**: validaciones inline en `NuevoEmpleadoDialog` espejando los validators del Create serializer (DNI 8 dig numéricos, edad >= 18).
- [ ] (5 min) **N7**: unificar cálculo de edad — usar `today.replace(year=-18)` consistente. Buscar el otro call site.
- [ ] (10 min) **HROverviewDashboard p.status→p.estado** (deuda v1/v2 que no atendimos).
- [ ] (5 min) **tsconfig.json:8** quitar `"ignoreDeprecations": "6.0"` (causa TS5103 abort) — destrabar tsc para que finalmente vea los imports rotos.

**Impacto:** desbloquea demo operativo (N1), aísla multi-tenant correctamente (N2), seed reutilizable (N3), UX legible (N4+N5), tooling sano (tsconfig).

### 2. MEDIO — Sub-proyecto E (Modularidad) — costo refinado

ui-modular bajó la estimación de 5-8 días a **4.5 h / ~305 LOC** reusando `workspaceService` ya existente:
- `<ModuleGate plan="pro" feature="ats">` component (~50 LOC)
- `useFeature(featureName)` hook conectado al `TenantContext` (~30 LOC)
- Backend: `Plan.features` JSONField + endpoint `/api/v1/tenants/me/features/` (~150 LOC)
- Frontend wiring en `App.tsx` + 3 páginas críticas (ATS, Legajos, Pay placeholder) (~75 LOC)

Sigue requiriendo brainstorm formal para validar el shape de `Plan.features`, pero el camino es mucho más corto que lo estimado en v2.

### 3. LARGO — D.0 ADR (cuando D arranque)

Sin cambios mayores vs v2. Reafirmado por hr-tester:
- Contrato D-Pay: `EmploymentData.objects.filter(tenant=t, estado_datos='activo', regimen_laboral__in=EmploymentData.REGIMENES_PLANILLA)`
- Vendor PDF (ReportLab interim funciona pero limitado)
- `RegimenLaboralConfig` configurable por tenant (MyPE flag, especialmente)
- CTS + Gratificación = D.1 + D.2 nativos
- Batch import CSV (#130) como prerequisito (sigue pendiente)

---

## Tune-up sugerido — NINGUNO

**Por primera vez los 4 especialistas cumplieron el contrato sin tuneo necesario.** Observaciones:

- ✅ `feature-supervisor` persistió su reporte en disco (contrato Bloque A del tune-up de hoy mantuvo).
- ✅ `code-quality` envolvió todas sus mutaciones ORM en `transaction.atomic + rollback` (contrato del tune-up aplicado hoy mantuvo).
- ✅ `hr-tester` limpió su script temporal y no persistió tests al repo.
- ✅ `ui-modular` persistió y mantuvo análisis estático limpio.

El equipo de agentes está estable en este punto. Próximos tunes solo si detectamos drift en futuras corridas.

---

## Veredicto D-Pay readiness

🟢 **READY-CON-CONDICIONES.** El módulo Empleados tiene la base funcional, peruana y de seguridad para que D arranque. **Pero antes de mergear D.0 deberíamos sellar N1-N3 (~40 min)** porque:
- N1 (seed sin permisos) bloquea poder DEMOSTRAR el módulo a stakeholders → riesgo comercial inmediato
- N2 (DNI cross-tenant) hace que el primer cliente real que cargue empleados por API se rompa
- N3 (seed wipe) es trivial pero acumula deuda silenciosa

N4-N5 (frontend) son UX-críticos pero no bloquean D — pueden ir en paralelo.
