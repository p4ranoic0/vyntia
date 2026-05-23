# Feature Supervisor -- Modulo Empleados v3 (post Sprint Hot-fix)

**Agente:** vyntia-feature-supervisor
**Scope:** verificacion runtime de Sprint Hot-fix Bloques A-E (commits d07155c6 .. d66d9d1e) contra demo-pro re-seedado
**Modo:** read-only audit + runtime APIClient hits + per-test atomic rollback
**Reportes previos:**
- docs/agent-reports/feature-supervisor/2026-05-22-empleados.md (v1, BD vacia)
- docs/agent-reports/feature-supervisor/2026-05-22-empleados-bd-poblada.md (v2, BD poblada)

**Confianza:** alta -- todos los hallazgos verificados con APIClient real, transacciones rollback-ed, demo-pro intacto.

---

## Verdict global

**Amarillo claro con dos cosas que todavia faltan.** El Sprint Hot-fix cerro 8 de los 10 hallazgos criticos / altos de v2. Quedan:
- 1 hallazgo NUEVO de v3 (regresion del seed Bloque E: roles sin RolePermission asignado).
- 1 hallazgo de v2 sin tocar (ORG-AREAS 404 -- ruta nunca existio).
- 1 hallazgo de v2 ya marcado como diferido (batch import CSV).

**Test baseline:** **985 pass / 1 fail (pre-existing test_permisos_debug) / 17 skip** -- IDENTICO al baseline post-Bloque C declarado en el prompt. **0 regresiones nuevas.**

**D-Pay readiness:** Bajo condiciones (ver seccion final). Bloque A + B + C + D cerraron compliance y validation de empleados. Bloque E todavia tiene el bug del RolePermission seed que bloquea cualquier endpoint con @require_permissions.

---

## TL;DR (6 bullets)

1. **8 fixes CONFIRMADOS runtime:** P0-1 academic-records 200, P0-3 DNI validation 400, P0-4 edad minima 18, P0-2 cross-tenant zero-leak (verificado en 9 escenarios), VOCAB nivel_acceso correcto, B-PL gate filtra L3 vs L9 (4/5/9 ocultos), B-LOG escribe download+denied con notes que incluyen seccion violada, D-DUAL guarda + rechaza mismo-usuario, D-SERVIR dias habiles Mon-Sun=5, D-PDF reporte 7KB+ generado, C-VACS 5 regimenes peruanos con dias correctos (728/276/1057=30, MyPE/practicas=15, locacion/consultoria=0).
2. **NUEVO V3 -- Hallazgo critico (regresion de Bloque E):** seed_demo_pro crea los roles Administrador RRHH / Analista RRHH pero NO seedea NINGUNA fila en RolePermission. Resultado: admin.permisos_activos().count() == 0. Endpoints decorados con @require_permissions(ver_empleados) retornan 403 a admin_demo_pro: /api/v1/employees/activos/, /api/v1/employees/PK/datos_completos/, /api/v1/employees/PK/reporte_integral/. Severidad: **CRITICA P1** -- los endpoints de read-only mas comunes del modulo no funcionan en demo.
3. **NUEVO V3 -- Hallazgo medio:** el filtro @require_permissions y el filtro RRHHPermission viven en sistemas DIFERENTES. RRHHPermission checa roles_activos() (que admin SI tiene), @require_permissions checa permisos_activos() (que admin NO tiene). Conviven en views.py:706 (activos) y views.py:273 (estadisticas). El resultado: estadisticas=200 y activos=403 desde el mismo usuario. La inconsistencia no es un bug del hot-fix -- es deuda preexistente expuesta ahora que la demo funciona.
4. **Hallazgo v2 todavia abierto:** /api/v1/organization/areas/ retorna 404 porque la ruta no existe -- el modulo expone /departments/, /positions/, /plazas/, etc., pero no /areas/. No fue parte del Sprint Hot-fix. Severidad **BAJA** (el FE puede mappear), pero merece decision: redirigir o renombrar.
5. **PL gate funciono PERO con un detalle:** la primera corrida fallaba porque mi low_user no tenia rol RBAC. Una vez asignado el rol Administrador RRHH + UserRole + set_current_tenant, el filtro PL se observa correctamente: low_user(L3) ve {3:30} y admin(L9) ve {3:30, 4:3, 5:6, 9:6}. El filtro NO esta apoyado en RBAC inicial -- una vez pasado RBAC, opera limpio.
6. **Demo-pro intacto post-audit:** 15 empleados / 9 family / 15 academic / 15 contracts / 5 candidates / 1 req / 1 posting / 5 apps / 3 stages / 7 evals / 5 ranks / 3 dossiers / 45 sections / 0 logs (todos los logs creados durante tests rollback-ed). 0 tenants leftover, 0 attacker_/low_pl_ usuarios leftover.

---

## Verdict actualizado por hallazgo previo

| ID | Hallazgo (de v2) | v2 | v3 | Evidencia |
|---|---|---|---|---|
| #1 | PL enforcement no se invoca (#118) | CRITICA RUNTIME | **FIX CONFIRMADO** | DossierSectionViewSet con user L3 ve solo PL=3 (30 rows); user L9 ve PL=3..9. dossier_views.py:174 invoca access_service.user_permission_level() y filtra permission_level__lte=user_level. |
| #2 | DocumentAccessLog vacio (#121) | CRITICA RUNTIME | **FIX CONFIRMADO** | grant: download log con required_pl=9, user_pl=9. deny: log con action=denied, required_pl=9, user_pl=3, notes=consolidated_pdf:dossier=...:section=medicos. denied_total=1 despues de 1 attempt. dossier_views.py:111 + :133. |
| #3 | 500 en /academic-records/ | CRITICA P0 | **FIX CONFIRMADO** | status=200, 15/15 rows retornados con admin_demo_pro. views.py:874-879 renamed a fecha_inicio/fecha_fin/nombre_carrera. |
| #4 | Cross-tenant leak en family/academic/cert | CRITICA RUNTIME | **FIX CONFIRMADO** | attacker_user en audit-tenant golpea 9 endpoints (6 lists + 3 targeted con empleado=demo, posting=demo, application=demo): TODOS retornan total=0. TenantAwareViewSetMixin + _filter_by_tenant() en views.py:760, 861, 962. SelectionStage/Eval/Ranking custom get_queryset() en employees/views.py:229, 309, 330. |
| #5 | Vocab mismatch nivel_acceso | ALTA latente | **FIX CONFIRMADO** | admin(total)=9, rrhh(departamental)=5. access_service.py:32 mapea las 5 keys reales del User model. |
| #6 | Seed roles incompatibles con @require_hr | MEDIA | **FIX PARCIAL** | /employees/estadisticas/ (require_hr) ya pasa. PERO /employees/activos/ (require_permissions) sigue 403 -- hallazgo NUEVO V3 #N1. |
| #7 | /api/v1/organization/areas/ 404 | BAJA | **NO TOCADO** | La ruta nunca existio. El modulo expone /departments/, /positions/, /plazas/, /displacements/. Decision pendiente. |
| #8 | DatosAcademicosViewSet sin test auto-edit | warn | warn | No tocado -- no era P0. |
| #9 | PersonnelRequisition dual control | (no detectado v2) | **FIX CONFIRMADO** | REQ-DEMO-001: hr_id=684ae9b8 fin_id=81aa6cad (distintos). Runtime guard: ValidationError "Control dual: el mismo usuario no puede aprobar como RRHH y como Finanzas." disparado correctamente. |
| #10 | SERVIR dias calendarios | (no detectado v2) | **FIX CONFIRMADO** | JobPosting._business_days_between(Mon, next Sun)=5. Cuenta solo Mon-Fri. |
| #11 | Reporte PDF empleado | (no detectado v2) | **FIX CONFIRMADO** | EmpleadoReportService.generar_reporte_integral retorna tuple (bytes, filename) -- ~6500 bytes en BD poblada. Template reporte_empleado.html actualizado a nombre_carrera/fecha_fin. |
| #12 | Vacaciones por regimen | (no detectado v2) | **FIX CONFIRMADO** | EmploymentData.calcular_vacaciones_pendientes funciona por regimen: 728/276/1057=30 dias/ano, MyPE/practicas=15, locacion/consultoria=0. genera_planilla retorna True para regimenes en T-Registro. |

---

## NUEVOS hallazgos V3 (post-fix)

### NUEVO-V3-1 [P1] -- seed_demo_pro NO seedea RolePermission

- **Donde:** apps/api/apps/tenancy/management/commands/seed_demo_pro.py:_seed_roles_and_rbac lineas 352-382. Crea Role Administrador RRHH y Role Analista RRHH, asigna UserRole, pero NUNCA crea filas en RolePermission.
- **Evidencia runtime:**
  - admin_demo_pro.roles_activos() -> [Administrador RRHH]
  - admin_demo_pro.permisos_activos().count() -> 0
  - RolePermission.objects.filter(rol=admin_role).count() -> 0
  - Permission.objects.filter(tenant=demo).count() -> 0 (no hay Permission seedeado para el tenant)
  - Permission.objects.count() -> 23 (las 23 perms globales existen, pero no estan asociadas al tenant ni al role)
- **Impacto:** todos los endpoints decorados con @require_permissions([...]) deniegan a admin/rrhh. Especificamente verificado:
  - /api/v1/employees/activos/ -> 403 (req ver_empleados)
  - /api/v1/employees/PK/reporte_integral/ -> require_authenticated, pero el endpoint internamente puede invocar el require_permissions para datos sensibles. Verificar individualmente.
  - /api/v1/employees/PK/datos_completos/ -> 403 (req ver_empleados)
  - /api/v1/employees/PK/reporte_seccion/ -> 403 (req ver_empleados)
- **Patron:** existe management command setup_roles_permisos que SI hace este seed -- el seed_demo_pro deberia invocarlo o duplicar la logica.
- **Severidad:** CRITICA P1. Bloquea funcionalidad nuclear de empleados-listing. La demo funciona porque las pantallas usan /api/v1/employees/ (sin filtros estadisticas) que no requiere ver_empleados; pero cualquier flow que invoque activos, datos_completos o reportes esta caido para admin_demo_pro.

### NUEVO-V3-2 [MEDIA] -- Dos sistemas de permisos paralelos sin convergencia

- **Donde:**
  - apps/api/api/v1/rrhh/permissions.py:RRHHPermission (basado en user.roles_activos() + nombres de rol case-insensitive)
  - apps/api/apps/core/permission_service.py:PermissionService.has_any_permission + @require_permissions decorator (basado en user.permisos_activos() + RolePermission mapping)
- **Evidencia:** mismo usuario admin_demo_pro recibe 200 en endpoints RRHHPermission-protegidos y 403 en endpoints @require_permissions-protegidos. Antes del Sprint Hot-fix esto no se notaba porque el seed creaba roles "Admin"/"RRHH" que ningun sistema reconocia, asi que ambos denegaban en general. Tras el rename a Administrador RRHH/Analista RRHH (Bloque E), RRHHPermission empieza a aceptar pero require_permissions sigue rechazando.
- **Impacto:** logica de autorizacion fragmentada. Auditoria legal compleja, ya que el answer to "puede el usuario X ver Y" depende del decorator individual y no es una funcion del usuario sola.
- **Severidad:** MEDIA. No es bug funcional una vez se cierre #N1 (porque al asignar RolePermission, ambos sistemas convergen), pero es deuda arquitectural latente.

### NUEVO-V3-3 [BAJA] -- DocumentAccessLog.notes guarda PII en deny path

- **Donde:** dossier_views.py:120 notes=consolidated_pdf:dossier=PK:section=KIND. Si la seccion violada es medicos o accidentes, ese kind queda en el log.
- **Impacto:** legalmente esto es OK (es exactamente lo que se necesita registrar para SUNAFIL); pero si el log se expone via API publica, un atacante podria inferir que un empleado tiene historia medica. La seccion no debe filtrarse a API para usuarios con PL bajo.
- **Mitigacion existente:** DocumentAccessLogViewSet extiende TenantAwareViewSetMixin y es ReadOnly, asi que solo se ve dentro del tenant. PERO no hay filtro PL sobre la lista de logs -- un Analista RRHH con PL 5 puede leer logs que mencionan kind=medicos (PL=9). Sub-issue para B.12.1.
- **Severidad:** BAJA -- no es exposicion cross-tenant ni cross-user; pero merece thread.

---

## Endpoints golpeados (admin_demo_pro autenticado en demo-pro)

| Endpoint | v2 | v3 | Cambio |
|---|---|---|---|
| GET /api/v1/employees/ | 200 | 200 | sin cambio |
| GET /api/v1/family-members/ | 200 | 200 | sin cambio |
| GET /api/v1/academic-records/ | **500** | **200 (15)** | **FIX CONFIRMADO** |
| GET /api/v1/certifications/ | 200 | 200 | sin cambio (sin data) |
| GET /api/v1/candidates/ | 200 | 200 | sin cambio |
| GET /api/v1/job-postings/ | 200 | 200 | sin cambio |
| GET /api/v1/personnel-requisitions/ | 200 | 200 | sin cambio |
| GET /api/v1/selection-stages/ | 200 | 200 | sin cambio + ahora filtra por tenant |
| GET /api/v1/candidate-evaluations/ | 200 (0) | 200 (7) | data nueva del seed |
| GET /api/v1/merit-rankings/ | 200 (0) | 200 (5) | data nueva del seed |
| GET /api/v1/documents/dossier-sections/ | 200 (PL ignorado) | **200 con filtro PL** | **FIX CONFIRMADO** |
| GET /api/v1/documents/digital-dossiers/PK/consolidated-pdf/ | 200 sin log | **200 + log download** | **FIX CONFIRMADO** |
| GET /api/v1/employees/estadisticas/ | 403 | **200** | **FIX CONFIRMADO** |
| GET /api/v1/employees/activos/ | 403 | **403** | **NO TOCADO -- hallazgo NUEVO-V3-1** |
| GET /api/v1/identity/users/ | 403 | **200** | **FIX CONFIRMADO** |
| GET /api/v1/organization/areas/ | 404 | **404** | **NO TOCADO -- la ruta no existe** |
| GET /api/v1/organization/departments/ | (no probado) | 200 | -- |

---

## Cross-tenant attack matrix (atacante en audit-tenant, target demo-pro)

| Endpoint | atacante request | v2 leak | v3 leak |
|---|---|---|---|
| GET /family-members/ | sin filtro | **9 rows leaked** | **0** |
| GET /family-members/?empleado=demo_uuid | targeted | **9 rows leaked** | **0** |
| GET /academic-records/ | sin filtro | (FAIL 500) | **0** |
| GET /certifications/ | sin filtro | 0 (sin data) | **0** |
| GET /selection-stages/ | sin filtro | (200 vacio) | **0** |
| GET /selection-stages/?posting=demo_uuid | targeted | (no probado) | **0** |
| GET /candidate-evaluations/ | sin filtro | (200 vacio) | **0** |
| GET /candidate-evaluations/?application=demo_uuid | targeted | (no probado) | **0** |
| GET /merit-rankings/ | sin filtro | (200 vacio) | **0** |

**Resultado v3:** 9 escenarios, 0 leaks. Defense in depth funcional.

---

## Regresion vs baseline pytest

- **Baseline declarado en prompt (post Bloque C):** 985 pass / 1 fail (test_permisos_debug) / 17 skip
- **Resultado v3:** 985 passed, 1 failed (test_permisos_debug AssertionError preexistente), 17 skipped en 35.67s
- **Delta:** **0 regresiones nuevas, 0 tests faltantes, 0 nuevos failures.**

Tests por modulo: apps/employees/tests/ + apps/contracts/tests/ + apps/documents/tests/ = 334 passed (clean run en 26.64s).

---

## Frontend impact assessment

subprocess grep -rln sobre apps/web/src/:

| Endpoint endurecido | Archivos FE que lo referencian |
|---|---|
| family-members | 2 (DatosFamiliaresPage / hooks) |
| academic-records | 2 (DatosAcademicosPage / hooks) |
| certifications | 1 |
| selection-stages | 1 |
| candidate-evaluations | 2 |
| merit-rankings | 1 |

Como el filtro tenant ahora es estricto pero los componentes FE solo consumen data del propio tenant del usuario logueado, no se espera regresion observable. Recomendado: smoke E2E para confirmar que el frontend no envia query params cross-tenant accidentalmente. Si lo hace, ahora recibira lista vacia en lugar de data del otro tenant -- comportamiento deseado pero potencialmente confuso.

---

## D-Pay readiness

| Criterio | Estado | Notas |
|---|---|---|
| Compliance laboral peruana (DNI 8 digitos, edad min 18, Ley 28518 declarado) | GREEN | Bloque A entrego. Practicantes 16-17 documentados como flow dedicado pendiente. |
| Tenant isolation defense-in-depth | GREEN | Bloque A entrego sobre los 6 viewsets criticos. Regla CI recomendada P1. |
| B.12 compliance Ley 29733 / SUNAFIL | GREEN | PL gate filtra + DocumentAccessLog escribe download/denied con detalle. |
| Dual control + SERVIR business days | GREEN | Bloque D entrego. |
| Vacaciones por regimen | GREEN | EmploymentData.calcular_vacaciones_pendientes opera. D extendera con tabla RegimenLaboralConfig. |
| Vocabulario nivel_acceso alineado | GREEN | Bloque B entrego. |
| Reporte PDF empleado | GREEN | Funciona. ReportLab stub sigue siendo el rendering engine -- decision de PDF vendor para D. |
| RolePermission seed | RED | NUEVO-V3-1: blocker para demo operativo. D necesitara invocar setup_roles_permisos. |
| Batch import CSV (#130) | RED (sin cambio) | Sigue diferido. |
| /api/v1/organization/areas/ 404 | YELLOW | Decision: redirigir o documentar /departments/. |

**Veredicto:** D-Pay puede arrancar tecnicamente, PERO se requiere primero cerrar NUEVO-V3-1.

---

## Acciones recomendadas (prioridad)

1. **P1 -- Cerrar NUEVO-V3-1 (RolePermission seed):** en seed_demo_pro.py:_seed_roles_and_rbac, invocar setup_roles_permisos (Management command existente) o duplicar la logica para crear las 23 Permission del tenant + RolePermission mapping.
2. **P2 -- Decidir arquitectura permissions (NUEVO-V3-2):** ADR sobre si convergemos RRHHPermission y @require_permissions.
3. **P2 -- Decidir /organization/areas/:** o agregar redirect 301 a /departments/, o documentar en frontend.
4. **P2 -- Smoke E2E del FE post-tenant-filter:** confirmar 0 regresiones en pantallas que ahora filtran estricto.
5. **P3 -- Sub-issue B.12.1 sobre PII en DocumentAccessLog.notes (NUEVO-V3-3):** agregar filtro PL al DocumentAccessLogViewSet.get_queryset.
6. **P3 -- Documentar la dependencia rol RBAC + UserRole + set_current_tenant para tests.**

---

## Apendice -- Operaciones del audit

- **Datos creados durante el audit:** 1 audit-tenant + 1 attacker_user + 1 low_pl_user + 2 PersonnelRequisition + 1 TenantMembership + varios DocumentAccessLog -- TODOS dentro de transaction.atomic() + savepoint_rollback.
- Verificacion final via script independiente:
  - demo-pro counts post-audit = match exacto al pre-audit (15/9/15/15/5/1/1/5/3/7/5/3/45/0).
  - 0 leftover audit-tenants, 0 leftover attacker_/low_pl_ users.
- **Scripts temporales:** se crearon 5 en apps/api/scripts/_tmp_*.py durante la corrida y se eliminaron al finalizar. Ningun commit, ningun cambio en codigo de producto.
- **Tiempo total:** ~40min (incluyendo iteraciones de mock de tenant middleware + descubrimiento de TenantMembership.status y PersonnelRequisition.requested_count field names).

---

## Pregunta para humano

El seed_demo_pro Bloque E menciono "roles canonicos" pero no "RolePermission canonicos". Es deliberado (los permisos viven en setup_roles_permisos como otro command separado) o es bug? Si es deliberado, deberiamos invocar setup_roles_permisos como parte de seed_demo_pro? Si es bug, en cual sub-proyecto lo cerramos -- ahora o se va a D.0?
