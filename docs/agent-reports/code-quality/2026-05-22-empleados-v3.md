# Code Quality - Empleados v3 (post Sprint Hot-fix)

**Fecha:** 2026-05-22
**Scope:** mismo modulo (apps/api/apps/employees/, api/v1/employees/, api/v1/rrhh/views.py, apps/web/src/features/employees/) + verificacion de cambios commits d07155c6..d66d9d1e.
**Modo:** runtime - tenant demo-pro (15 emp / 7 eval / 5 rank / 3 dossier / 1 requisition aprobada via workflow real).

**Comandos:**
- pytest --no-header -q -> **985 passed, 1 failed (pre-existing test_permisos_debug), 17 skipped**. Baseline intacto.
- pytest apps/employees/tests/ -q --no-cov -> 114/114 PASS.
- npx tsc --noEmit -p tsconfig.app.json -> 1 pre-existing error (BlankEnum). Intacto.
- Runtime tests via manage.py shell sobre bd_vyntia con tenant demo-pro.
- Mutaciones de prueba envueltas en transaction.atomic() + savepoint_rollback. No se muto data persistente.

**Confianza:** alta. **Tiempo invertido:** ~50 min.

---

## TL;DR - Semaforo v3

| Eje | v1 | v2 | v3 | Comentario |
|---|---|---|---|---|
| Estabilidad runtime | AMBAR-ROJO | AMBAR | VERDE-PALIDO | Bloque A cerro las 4 P0 (academic-records 500, TenantAwareViewSetMixin x4, DNI validator Create, edad 18). |
| Seguridad / RBAC | AMBAR | ROJO | VERDE-PALIDO | Dual-control HR/Finance confirmado por runtime. Seed walks workflow real. |
| Compliance SERVIR | AMBAR | ROJO | AMBAR (parcial) | _business_days_between cuenta Mon-Fri. Sigue ignorando feriados peruanos (documentado interim; sin tests dedicados). |
| Compliance B.12 | n/a | n/a | VERDE | PL gate vivo en DigitalDossier.consolidated_pdf + DossierSectionViewSet + DocumentosDigitalesViewSet. _NIVEL_ACCESO_TO_LEVEL mapea total/departamental/personal/limitado/lectura a 9/5/3/2/1. DocumentAccessLog wired (migration 0009 hace document FK nullable para dossier-level events). |
| Multi-tenant | AMBAR | AMBAR | AMBAR | Sin cambios estructurales en los 4 modelos sin tenant FK. SelectionStage/CandidateEvaluation/MeritRanking filtran por padre. |
| Performance | VERDE-PALIDO | ROJO | ROJO (sin cambios) | Sprint no toco el N+1 (era LARGO/MED). Re-medido: 66 queries para 15 empleados (vs 73 v2). Patron identico. |
| Tech debt | ROJO | ROJO | ROJO | EmpleadosListPage sigue huerfano, boletas_recientes sigue stub muerto, 56 console.log sin tocar. |

---

## Verdict por hallazgo previo

### Hallazgos criticos / verificacion runtime de v2

| Hallazgo | Verdict v3 | Evidencia |
|---|---|---|
| dual_control (v2 N2 + v1 #4): PersonnelRequisition aceptaba mismo user HR+Finance; seed creaba status=approved directo. | FIX CONFIRMADO | Runtime: req.approve_hr(user=admin); req.approve_finance(user=admin) -> ValidationError 'Control dual...' (rolled back). Seed ahora walks submit_for_approval -> approve_hr(rrhh) -> approve_finance(admin), deja hr y fin distintos. |
| SERVIR business days (v1 #5): MIN_PUBLIC_OPEN_BUSINESS_DAYS=7 vs dias calendario. | FIX PARCIAL | _business_days_between(2026-05-01, 2026-05-08) = 5 correcto. Validacion con 7 cal=5 biz falla con '5 dias habiles'. PERO docstring confiesa: no considera feriados peruanos. Sin tests dedicados. |
| boletas_recientes stub (v1 #2): metodo retornaba [] con codigo muerto. | NO FUE TOCADO | Bloque D no lo abordo. Runtime: Employee.objects.first().boletas_recientes() -> []. Sin callers vivos en backend ni frontend. El riesgo (dev de D construye UI sobre []) sigue vigente. Recomendacion firme: borrar el metodo ANTES de iniciar D. |
| EmpleadosListPage huerfano (v1 #1): ReferenceError isRRHH/isSupervisor pero no enrutado. | SIGUE HUERFANO | Grep en App.tsx: 0 matches a EmpleadosListPage. Solo Empleados (Empleados.tsx) esta enrutado. Cambios recientes no anaden la pagina. MED - deuda de borrado. |
| N+1 en EmpleadoListSerializer (v2 N1): 73 queries para 15 empleados. | NO FIXED, parcialmente reducido por efectos colaterales | Re-medido: 66 queries (delta -7). Distribucion: 31x datos_laborales, 16x area, 16x historial_ubicaciones, 1x empleado, 1x datos_familiares, 1x datos_academicos. Patron identico: helpers construyen QuerySets nuevos que no respetan prefetch_related. Sin regresion, pero sin fix. |

### Otros hallazgos v1/v2 - status

| Hallazgo | Verdict v3 |
|---|---|
| v1 #3 (boilerplate triplicado DatosFamiliares/Academicos/Cursos) | Sin cambios (era LARGO). |
| v1 #6 (transferir sin atomic) | Sin cambios (no re-verificado). |
| v1 #7 (4 modelos seleccion sin tenant FK) | Sin cambios. Filtran via padre. |
| v1 #8 (suma weights seleccion) | Sin cambios. |
| v1 #9 (urls.py acoplamiento api/v1/employees importa de api.v1.rrhh) | Sin cambios. |
| v1 #10 (canAccessEmployeeData(number) vs UUID) | Sin cambios. |
| v1 #11 (56 console.log) | Sin cambios. |
| v1 #12 (JobPosting.application_count N+1) | Sin cambios. |
| v1 #13 (SelectionStage/CandidateEvaluation sin TenantAwareViewSetMixin) | Bloque A claimo 'mixin x4'. Inspeccion: SelectionStageViewSet/CandidateEvaluationViewSet/MeritRankingViewSet NO usan el mixin todavia - usan get_queryset con filtro manual via posting.tenant. Funciona pero diverge del patron. Reclasifico a FIX PARCIAL / patron divergente. |
| v2 N3 (seed sin CandidateEvaluations ni MeritRankings) | FIX CONFIRMADO. _seed_evaluations() + _seed_ranking() corren. Demo-pro tiene 7 eval y 5 rank. |

---

## Hallazgos NUEVOS introducidos por el sprint

### [ALTO - CORTO] N1. validate_numero_documento no scope tenant - falso-positivo cross-tenant

- Donde: api/v1/rrhh/serializers.py:543, 728-747, 1343-1348. Hay TRES validadores validate_numero_documento (EmpleadoSerializer, EmpleadoCreateSerializer, OnboardingCompleteCreateSerializer).
- Que: Los tres hacen Employee.objects.filter(numero_documento=value).exists() sin filtrar por tenant. La constraint DB (unique_employee_doc_per_tenant) si es por-tenant (employee.py:204-207).
- Por que importa: Si tenant A registra DNI 12345678 y tenant B intenta crear OTRO empleado con el mismo DNI, el validator rechaza ANTES de que llegue la constraint DB. Resultado: imposible registrar peruanos con DNIs comunes en tenants distintos. Rompera el primer alta cross-tenant en produccion SaaS multi-cliente.
- Como arreglar: Employee.objects.filter(tenant=self.context[request].tenant, numero_documento=value).exists(). Esfuerzo ~15 min.

### [MEDIO - CORTO] N2. EmpleadoSerializer.validate_fecha_nacimiento usa calculo edad incorrecto

- Donde: api/v1/rrhh/serializers.py:588-593.
- Que: edad_minima = timezone.now().date() - timedelta(days=18*365) son 6,570 dias, ignorando anos bisiestos. Un empleado nacido exactamente hace 18 anos en ano post-bisiesto puede ser rechazado. El EmpleadoCreateSerializer (Bloque A) usa today.replace(year=today.year - 18) correcto.
- Dos serializers, dos calculos. Inconsistencia que puede aceptar/rechazar arbitrariamente al borde.
- Como arreglar: reemplazar linea 589 por edad_minima = today.replace(year=today.year - 18). Esfuerzo 10 min.

### [MEDIO - CORTO] N3. _business_days_between sin tests + sin catalogo de feriados

- Donde: apps/employees/models/job_posting.py:112-128.
- Que: Helper cuenta Mon-Fri OK, pero docstring confiesa 'no considera feriados peruanos'. No hay tests en apps/employees/tests/ que verifiquen Mon-Fri ni caso feriados. Regresion silenciosa posible (cambiar < 5 por <= 5).
- Por que importa: SERVIR Art. 5 cuenta dias habiles DESCONTANDO feriados nacionales (Ley 29408) y regionales. En un mes con 1-2 feriados, una convocatoria publicada segun este helper queda CORTA del minimo legal, y un postulante rechazado puede impugnar por vicio de procedimiento.
- Como arreglar (CORTO): test_b9_business_days.py con casos Mon-Fri puros, finde, semana puente (~30 min). Documentar feriados como deuda explicita para D. (LARGO): catalogo de feriados en apps/core/ (1-2 dias).

### [ALTO - CORTO] N4. Wipe en seed_demo_pro --fresh NO borra DocumentAccessLog

- Donde: apps/tenancy/management/commands/seed_demo_pro.py:235-271.
- Que: _wipe_demo_tenant() borra MeritRanking, CandidateEvaluation, JobApplication, SelectionStage, JobPosting, PersonnelRequisition, Candidate, DigitalDossier, AcademicRecord, FamilyMember, Contract, EmploymentData, Employee, Position, Department, roles/perms/memberships/users. Pero NO DocumentAccessLog ni DigitalDocument explicitamente.
- Por que importa: DocumentAccessLog.tenant es on_delete=PROTECT. Si demo se usa (alguien descarga consolidated_pdf -> log creado), el SIGUIENTE seed_demo_pro --fresh fallara con ProtectedError al intentar tenant.delete(). DigitalDocument cascade via empleado (OK), DossierSection cascade via DigitalDossier (OK), pero DocumentAccessLog NO.
- Como arreglar: DocumentAccessLog.objects.filter(tenant=tenant).delete() ANTES de DigitalDossier. Idealmente tambien DigitalDocument.objects.filter(tenant=tenant).delete() defensive. Esfuerzo 5 min.

### [BAJO - LARGO] N5. 3 ViewSets seleccion divergen del patron TenantAwareViewSetMixin

- Donde: api/v1/employees/views.py:220-336 (SelectionStageViewSet, CandidateEvaluationViewSet, MeritRankingViewSet).
- Que: Implementan filtro tenant via get_queryset con filter(posting__tenant=tenant) en lugar de heredar del mixin. Funciona pero diverge del patron de 8/11 viewsets. Motivo: estos modelos no tienen FK tenant directa (v1 #7).
- Por que importa: Hereda riesgo de v1 #7 - defensa en profundidad solo en RLS + override manual. Si nuevo dev agrega @action que skip-ea get_queryset, no hay tenant filter.
- Como arreglar: spec de D-Pay decide: o promover a tenant FK (1-2h refactor + migration) o documentar la doctrina en CLAUDE.md (5 min).

---

## Top 5 hallazgos NUEVOS

1. [ALTO] N1 - validate_numero_documento falso-positivo cross-tenant. Triple validator sin tenant scope. Rompe primer alta cross-tenant en SaaS multi-cliente. Critico para D (PaySlips por DNI desde tenants distintos). Fix 15 min.
2. [ALTO] N4 - seed_demo_pro --fresh orphan-blocks por DocumentAccessLog. Latente hasta usar el dossier consolidated_pdf, luego ProtectedError. Fix 5 min.
3. [MEDIO] N2 - Dos calculos de edad minima distintos (EmpleadoSerializer vs EmpleadoCreateSerializer). Inconsistencia que puede rechazar/aceptar arbitrariamente al borde. Fix 10 min.
4. [MEDIO] N3 - _business_days_between sin tests + sin catalogo feriados. Tests rapidos 30 min; feriados 1-2 dias (paquete para D).
5. [BAJO] N5 - 3 ViewSets seleccion divergen del patron TenantAwareViewSetMixin. Decision arquitectonica.

---

## Suite de tests y baselines

| Metrica | Baseline post-B.16 | Post-Sprint Hot-fix | Delta |
|---|---|---|---|
| pytest backend total | 982 passed / 1 failed / 17 skipped | 985 passed / 1 failed / 17 skipped | +3 PASS |
| pytest apps/employees/tests/ | 114 passed | 114 passed | 0 |
| frontend tsc | 1 (BlankEnum) | 1 (BlankEnum) | 0 |
| Empleados list cold queries | 73 (v2) | 66 | -7 (efecto colateral, no fix dirigido) |
| seed counts (emp/eval/rank/dossier) | 15/0/0/3 | 15/7/5/3 | +7 eval, +5 rank |

No hay regresiones. Sprint Hot-fix aporta +3 tests netos y +12 filas de seed utiles.

---

## Performance - N+1 actualizado

| Endpoint | Empleados | Queries v2 | Queries v3 | Distribucion |
|---|---|---|---|---|
| GET /api/v1/employees/empleados/ (effective queryset) | 15 | 73 | 66 | 31x datos_laborales, 16x area, 16x historial_ubicaciones, 1x empleado, 1x datos_familiares, 1x datos_academicos |

El N+1 sigue identico en topologia. Delta -7 viene de prefetches mejorados del queryset base, no fix dirigido. Con 100 empleados sigue escalando a ~430 queries.

---

## Veredicto: Puede D (Vyntia Pay) arrancar HOY?

SI, CON DOS FIXES OBLIGATORIOS DE 20 MINUTOS.

Razones tecnicas:
- Dual-control PersonnelRequisition VIVO y confirmado.
- SERVIR business days VIVO (con deuda explicita de feriados).
- PL gate + DocumentAccessLog VIVOS (B.12 compliance closed).
- Baseline 985/1/17 intacto, +3 PASS netos.
- Seed demo-pro reproducible via workflow real (no mas bypass).
- Counts y data alineados con la sintesis (15/7/5/3).

Bloqueos antes de abrir D:
1. OBLIGATORIO (15 min): N1 - scope tenant en validate_numero_documento (x3). D va a buscar empleados por DNI; un falso-positivo cross-tenant romperia el flujo de alta de PaySlip cuando un nuevo cliente intente onboardear con DNIs comunes.
2. OBLIGATORIO (5 min): N4 - anadir DocumentAccessLog wipe en seed_demo_pro --fresh. Sin esto, el demo se rompe tras la primera descarga de legajo.
3. RECOMENDADO (5 min): borrar Employee.boletas_recientes(). D lo va a reescribir; evitar collision.
4. RECOMENDADO (10 min): N2 - unificar calculo de edad minima.

Total bloqueante: 20 min. Total recomendado: 35 min. Cabe en sprint actual sin problema.

Deuda para milestone D o paralela:
- N+1 EmpleadoListSerializer (fix con Prefetch + helpers que usen self.datos_laborales.all() en vez de .objects.filter). ~30 min CORTO.
- N3 - tests + catalogo feriados peruanos. CORTO tests (30 min); LARGO feriados.
- N5 - decision arquitectonica sobre tenant FK en modelos hijos de JobPosting.

---

## Pregunta para humano

No hay preguntas bloqueantes. Todos los hallazgos criticos son accionables sin esperar input.
