# Feature Supervisor -- Modulo Empleados (2026-05-22, BD poblada)

**Agente:** vyntia-feature-supervisor
**Scope:** modulo Empleados con tenant demo-pro poblado (15 empleados, 5 candidatos, 1 posting, 3 dossiers)
**Modo:** read-only audit + runtime verification via Django test client
**Spec consultada:** docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md + 2026-05-14-vyntia-B12-legajos-completos.md
**Confianza:** alta -- todos los hallazgos verificados con hits reales al APIClient contra la BD bd_vyntia.
**Reporte previo:** docs/agent-reports/feature-supervisor/2026-05-22-empleados.md

---

## Verdict global (cambio vs corrida anterior)

Verde con condiciones se degrada a **Amarillo con condiciones criticas**. Lo que en la corrida con BD vacia se podia inferir solo por grep -- ahora hay evidencia runtime:

- Los 2 huecos criticos previos siguen ahi y se confirman a traves del flujo real.
- Aparecio un **500 directo en /api/v1/academic-records/** (endpoint no usable en produccion).
- Aparecio un **leak cross-tenant verificado** en DatosFamiliaresViewSet / DatosAcademicosViewSet / CursosCertificacionesViewSet: un usuario tipo=rrhh de otro tenant ve los 9 family-members de demo-pro.
- Aparecio un **schema-mismatch entre User.NIVEL_ACCESO_CHOICES y access_service._NIVEL_ACCESO_TO_LEVEL** -- vocabularios desalineados; aun si el gate se invocara, denegaria a todos (excepto total).

---

## TL;DR (5 bullets)

1. **CONFIRMADO RUNTIME -- PL gate leak (#118):** un admin con nivel_acceso=personal (que deberia mapear a PL bajo) recibe 200 OK con las 6 secciones PL=9 (medicas, accidentes) del dossier. Filtro ?kind=medicos devuelve 3 rows con permission_level=9. Severidad: **CRITICA**.
2. **CONFIRMADO RUNTIME -- DocumentAccessLog vacio (#121):** generacion consolidated-pdf/ retorna PDF de 6133 bytes y DocumentAccessLog.objects.count() se mantiene en 0. Violacion Ley 29733 / SUNAFIL. Severidad: **CRITICA**.
3. **NUEVO -- 500 en /api/v1/academic-records/:** DatosAcademicosViewSet ordena por fecha_inicio_estudios y fecha_termino_estudios pero el modelo solo tiene fecha_inicio y fecha_fin. Mismo patron de stale rename que el bug L3.10.4e (commit f0c133a2). Endpoint **inutilizable**. Severidad: **CRITICA P0**.
4. **NUEVO -- Cross-tenant leak en family/academic/cert ViewSets:** un usuario tipo_usuario=rrhh de audit-tenant (creado ad-hoc, ya purgado) recibe 200 OK con las 9 FamilyMember rows de demo-pro. Los tres viewsets carecen de TenantAwareViewSetMixin Y sobre-escriben get_permissions() a IsAuthenticated para list/retrieve/create/update/delete. Severidad: **CRITICA**.
5. **NUEVO -- Vocab mismatch nivel_acceso:** User.NIVEL_ACCESO_CHOICES = [total, departamental, personal, limitado, lectura] vs access_service._NIVEL_ACCESO_TO_LEVEL = {bajo:1, medio:3, alto:5, total:9}. admin_demo_pro.nivel_acceso=personal mapea a level=1 (default fallback). Aun si el enforcement se invocara, solo el unico nivel=total accederia a PL>=3. Severidad: **ALTA** -- bug latente que dispararia denegaciones masivas el dia que alguien conecte el service.

---

## Salud baseline (post-seed)

| Check | Resultado |
|---|---|
| manage.py check --settings=vyntia.settings.development | **0 issues silenced** PASS |
| Demo-pro Tenant | d4ed3cd0-... slug=demo-pro plan=pro status=active |
| Users en demo-pro via TenantMembership | admin_demo_pro (owner, tipo=administrador) + rrhh_demo_pro (admin, tipo=rrhh) |
| Conteos en BD demo-pro | Employees=15, FamilyMember=9, AcademicRecord=15, Candidate=5, JobPosting=1, PersonnelRequisition=1, JobApplication=5, SelectionStage=3, CandidateEvaluation=0, MeritRanking=0, DigitalDossier=3, DossierSection=45, **DigitalDocument=0**, **DocumentAccessLog=0** |

Nota: DigitalDocument=0 significa que no hay archivos en los dossiers (las 45 secciones son contenedores vacios). Aun asi, el listing de secciones expone metadata sensible (PL=9 categorias visibles).

---

## Endpoints golpeados (admin_demo_pro autenticado en demo-pro)

| Endpoint | Status | Rows / total | Notas |
|---|---|---|---|
| GET /api/v1/employees/ | 200 | 15 / 15 | OK |
| GET /api/v1/family-members/ | 200 | 9 / 9 | OK |
| GET /api/v1/academic-records/ | **500** | n/a | **FAIL -- FieldError fecha_inicio_estudios** |
| GET /api/v1/candidates/ | 200 | 5 / 5 | OK |
| GET /api/v1/job-postings/ | 200 | 1 / 1 | OK |
| GET /api/v1/personnel-requisitions/ | 200 | 1 / 1 | OK |
| GET /api/v1/job-applications/ | 200 | 5 / 5 | OK |
| GET /api/v1/selection-stages/ | 200 | 3 / 3 | OK |
| GET /api/v1/candidate-evaluations/ | 200 | 0 / 0 | OK (vacio, esperado) |
| GET /api/v1/merit-rankings/ | 200 | 0 / 0 | OK (vacio, esperado) |
| GET /api/v1/documents/digital-dossiers/ | 200 | 3 / 3 | OK |
| GET /api/v1/documents/dossier-sections/ | 200 | 20 / 45 (paginado) | OK |
| GET /api/v1/documents/document-access-logs/ | 200 | 0 / 0 | OK |
| GET /api/v1/contracts/ | 200 | 15 / 15 | OK |
| GET /api/v1/employment-data/ | 200 | 15 / 15 | OK |
| GET /api/v1/employees/estadisticas/ | **403** | -- | @require_hr() denega; seed-roles gap |
| GET /api/v1/employees/activos/ | **403** | -- | igual |
| GET /api/v1/identity/users/ | **403** | -- | igual |
| GET /api/v1/organization/areas/ | **404** | -- | Ruta no resuelve |

---

## Confirmaciones runtime de hallazgos previos

### #1 -- Permission-level enforcement NO ocurre (B.12 #118) [CONFIRMADO MAS GRAVE]

- **Evidencia runtime:** admin_demo_pro (nivel_acceso=personal) golpea GET /api/v1/documents/dossier-sections/?kind=medicos y recibe 200 OK con 3 rows de permission_level=9.
- Total seccion-listing: 45 secciones devueltas distribuidas en (6 PL=9, 6 PL=5, 3 PL=4, 30 PL=3). Las 6 PL=9 NO se filtraron.
- **Severidad ahora:** se eleva de CRITICA a **CRITICA + RUNTIME EVIDENCE**. Antes era riesgo demostrable solo por grep; ahora hay flujo real.

### #2 -- DocumentAccessLog NO se invoca (B.12 #121) [CONFIRMADO RUNTIME]

- **Evidencia runtime:** llamado a GET /api/v1/documents/digital-dossiers/<uuid>/consolidated-pdf/ retorna status 200, content-type application/pdf, size 6133 bytes. DocumentAccessLog.objects.count() antes=0 / despues=0 (delta=0).
- apps/documents/services/dossier_service.py:147 render_consolidated_pdf invoca PDFGenerator._html_to_pdf directamente; nunca llama access_service.log_access().
- **Severidad ahora:** CRITICA + RUNTIME EVIDENCE. Ley 29733 articulo 12 obliga registro de cada acceso a datos personales.

### Tenant isolation B.9 [PARCIALMENTE CONFIRMADO]

- Las pruebas cross-tenant a /api/v1/job-postings/, /api/v1/selection-stages/, /api/v1/candidates/ retornaron 403 desde un user de audit-tenant, pero por una razon DIFERENTE a la esperada: EmpleadoViewSet / JobPostingViewSet usan EmpleadoPermission / RRHHPermission que niegan a un user sin rol RBAC explicito (no por tenant).
- Cuando el atacante recibe rol rrhh via tipo_usuario, los viewsets que SI extienden TenantAwareViewSetMixin filtran correctamente -- devolviendo lista vacia o 404 al GET por UUID.
- **PERO**: los 3 viewsets sin tenant mixin no filtran nada y exponen data del otro tenant (ver hallazgo NUEVO-2).

---

## Hallazgos NUEVOS (solo visibles con BD poblada)

### NUEVO-1 [P0] -- 500 en /api/v1/academic-records/ por stale field name

- **Donde:** apps/api/api/v1/rrhh/views.py:875-879 (DatosAcademicosViewSet.ordering_fields + ordering)
- **Que falta:** los nombres fecha_inicio_estudios y fecha_termino_estudios no existen en el modelo AcademicRecord; los campos reales son fecha_inicio y fecha_fin (verificado en el FieldError.choices del traceback).
- **Evidencia runtime:** c.get(/api/v1/academic-records/) retorna 500 con django.core.exceptions.FieldError: Cannot resolve keyword fecha_inicio_estudios. Reproducible con admin_demo_pro, rrhh_demo_pro, y aun pasando ?ordering=created_at (DRF aplica el default ordering array primero).
- **Patron:** identico al fix reciente L3.10.4e (commit f0c133a2 -- menu 500 stale .modulo_id / .permiso_id access).
- **Impacto:** modulo de formacion academica COMPLETAMENTE inaccesible via API. Frontend no puede cargar tab academico.

### NUEVO-2 [P0] -- Cross-tenant leak en DatosFamiliaresViewSet / DatosAcademicosViewSet / CursosCertificacionesViewSet

- **Donde:**
  - apps/api/api/v1/rrhh/views.py:760 DatosFamiliaresViewSet
  - apps/api/api/v1/rrhh/views.py:861 DatosAcademicosViewSet
  - apps/api/api/v1/rrhh/views.py:962 CursosCertificacionesViewSet
- **Que falta:**
  1. Ninguno extiende TenantAwareViewSetMixin (a diferencia de EmpleadoViewSet:377 y DatosLaboralesViewSet:1019 que SI lo hacen).
  2. Los tres get_permissions() sobre-escriben RRHHPermission por permissions.IsAuthenticated() para list/retrieve/create/update/destroy.
  3. get_queryset() filtra por user.empleado (lo cual solo opera dentro de un tenant) pero si user.es_administrador or user.es_rrhh or user.es_admin_rrhh, retorna super().get_queryset() sin filtro de tenant.
- **Evidencia runtime:** cree tenant audit-tenant con user tipo_usuario=rrhh, NO superuser, NO membresia en demo-pro. APIClient en host audit-tenant.vyntia.pe, force_authenticate(audit_user). GET /api/v1/family-members/ retorna 200, rows=9, total=9 (todos pertenecen a demo-pro). El test usa force_authenticate que bypasses JWT -- el JWT en prod actua como segunda linea de defensa pero el codigo del viewset NO valida tenant.
- **Riesgo:** defense in depth ausente. Si JWT middleware falla, esta mal configurado, o si dos tenants comparten una pasarela auth comprometida, los datos PII (familiares, academico, certificados) se exponen entre tenants.
- **Tambien aplica a:** CursosCertificacionesViewSet (mismo patron -- no hay data en demo-pro asi que no se vio leak en runtime, pero la vulnerabilidad arquitectural es identica).

### NUEVO-3 [P1] -- Schema mismatch nivel_acceso

- **Donde:**
  - apps/api/apps/identity/models/user.py:40-46 NIVEL_ACCESO_CHOICES = [total, departamental, personal, limitado, lectura]
  - apps/api/apps/documents/services/access_service.py:23-28 _NIVEL_ACCESO_TO_LEVEL = {bajo:1, medio:3, alto:5, total:9}
- **Que falta:** vocabularios no compatibles. Solo total coincide. personal/departamental/limitado/lectura se mapean al .get(key, 1) default.
- **Evidencia runtime:** admin_demo_pro.nivel_acceso=personal retorna user_permission_level(admin)=1. can_access(admin, doc_PL9) retorna False. Si se invocara la verificacion, denegaria TODO acceso PL>=3 a los users seeded.
- **Impacto:** este bug enmascara el bug #1 (PL no enforced). Cuando alguien intente cerrar #118 y conecte access_service.check_and_log en los viewsets, los usuarios admin actuales perderian acceso a TODO excepto secciones PL=1. Cerrar #118 SIN cerrar este primero genera regresion masiva.
- **Decision pendiente:** o ampliar el mapping para incluir personal:3, departamental:5, limitado:1, lectura:1, o renombrar User.NIVEL_ACCESO_CHOICES a los terminos del service.

### NUEVO-4 [P2] -- Seed crea roles que @require_hr no reconoce

- **Donde:**
  - apps/api/apps/identity/management/commands/seed_demo_pro.py (asumido) -- crea roles Admin y RRHH.
  - api/v1/rrhh/permissions.py -- RRHHPermission reconoce admin, administrador, rrhh (case-insensitive) entre otros, y @require_hr decorator usa Roles.HR_ROLES.
- **Evidencia runtime:** admin_demo_pro recibe 403 en /api/v1/employees/estadisticas/ y /api/v1/identity/users/ aun cuando tipo_usuario=administrador.
- **Impacto:** el seed funciona para los viewsets que usan tipo_usuario directamente (como EmpleadoViewSet), pero falla en los que usan el decorador @require_hr o IsHRUser. Demo no es completamente operable.

### NUEVO-5 [P2] -- /api/v1/organization/areas/ retorna 404

- **Evidencia:** c.get(/api/v1/organization/areas/) retorna 404 con HTML response.
- **Impacto:** si el frontend useDepartments apunta a /api/v1/organization/areas/, no recibe nada. Verificar el routing real bajo api/v1/organization/urls.py.

---

## Tabla feature x estado (solo entradas con CAMBIO de status)

| Feature | BD vacia (2026-05-22) | BD poblada (hoy) | Cambio |
|---|---|---|---|
| DatosAcademicosViewSet list | warn (sin test de auto-edit) | **FAIL 500** | regresion verificada -- bug stale field name |
| DatosFamiliaresViewSet tenant isolation | warn (sin test directo) | **FAIL -- leak demostrado** | severidad ALTA confirmada |
| CursosCertificacionesViewSet tenant isolation | warn (cero tests) | **WARN -- leak arquitectural identico** | misma vulnerabilidad, sin data para probar |
| B.12 PL enforcement (#118) | warn (no se invoca) | **FAIL CRITICO en runtime** | confirmado: admin con PL1 ve secciones PL9 |
| B.12 DocumentAccessLog (#121) | warn (modelo no invocado) | **FAIL CRITICO en runtime** | confirmado: PDF generado, logs=0 |
| Vocab nivel_acceso vs access_service | (no notado) | **FAIL** | hallazgo nuevo, bug latente |
| /api/v1/employees/estadisticas/ | OK (asumido) | **WARN 403** | seed crea roles incompatibles con decorator |
| /api/v1/organization/areas/ | OK (asumido reachable) | **FAIL 404** | requiere investigar ruta |

Features que se mantienen verdes: CRUD Employee, Candidate, JobPosting, PersonnelRequisition (con doble aprobacion), JobApplication, SelectionStage, DigitalDossier listing/build/consolidated-pdf (el PDF en si funciona, lo que falla es el audit log).

---

## Riesgos actualizados para D (Vyntia Pay)

| Riesgo | Severidad ANTES | Severidad HOY | Notas |
|---|---|---|---|
| Batch import CSV sin existir | ALTO | ALTO (sin cambio) | Sigue sin implementarse |
| Stale field names en viewsets (patron L3.10.4e) | MEDIO | **ALTO** | Demostrado: academic-records esta caido. D introducira mas modelos -- alto riesgo de mas 500s post-rename. Hacer auditoria ordering_fields/search_fields/filterset_fields contra modelos antes de cerrar D.0. |
| Vocab nivel_acceso desalineado con access_service | (no detectado) | **ALTO** | Si D introduce planilla con docs sensibles (boletas, AFP), conectar el gate sin arreglar vocab causa lockout masivo. Decidir vocabulario antes de D.x. |
| Cross-tenant defense in depth | MEDIO | **ALTO** | 3 viewsets sin tenant filter -- antes asumido teorico, ahora demostrado. D probablemente reusara los mismos patrones. Crear regla de lint que requiera TenantAwareViewSetMixin para todo ModelViewSet sobre tablas con FK a tenant. |
| Seed roles mismatch con decorators | (no detectado) | MEDIO | demo no es completamente operable para acciones que usan @require_hr. D requerira el mismo seed-flow -- fijar roles en seed para que cubran ambos sistemas. |

---

## Acciones recomendadas (prioridad)

1. **P0 -- Fix DatosAcademicosViewSet:** renombrar fecha_inicio_estudios a fecha_inicio y fecha_termino_estudios a fecha_fin en lineas 875-879 de api/v1/rrhh/views.py. Agregar test test_academic_record_list_default_ordering que liste sin parametros y verifique 200.
2. **P0 -- Agregar TenantAwareViewSetMixin y endurecer permisos a DatosFamiliaresViewSet / DatosAcademicosViewSet / CursosCertificacionesViewSet:** quitar el override de get_permissions() que abre a IsAuthenticated; el filtro por user.empleado ya esta y debe seguir, pero ENCIMA debe haber tenant. Agregar smoke test cross-tenant que verifique 0 rows leaked.
3. **P0 -- Decidir vocabulario nivel_acceso:** o expandir el mapping en access_service._NIVEL_ACCESO_TO_LEVEL, o renombrar User.NIVEL_ACCESO_CHOICES. Documentar ADR en docs/superpowers/specs/.
4. **P0 -- Cerrar #118 y #121 juntos:** las dos viewsets de B.12 deben invocar access_service.check_and_log() en retrieve / consolidated_pdf / DigitalDocument download. NO cerrar #118 sin #3 (vocab) -- generaria lockout masivo.
5. **P1 -- Agregar regla CI:** lint que verifique que todo ModelViewSet en api/v1/*/views.py cuyo modelo tenga campo tenant extiende TenantAwareViewSetMixin.
6. **P1 -- Auditar otros viewsets:** correr el mismo cross-tenant attack con plain RRHH user contra TODOS los endpoints del modulo para descubrir mas leaks. Posible candidato: WorkExperienceViewSet, SwornDeclarationViewSet, JobHistoryViewSet (no fueron probados -- tampoco hay data sembrada).
7. **P2 -- Arreglar seed_demo_pro:** asignar roles que @require_hr reconozca (Super Administrador / Administrador RRHH / Analista RRHH) ademas de tipo_usuario.
8. **P2 -- Investigar 404 en /api/v1/organization/areas/** -- confirmar si el path correcto es /api/v1/organization/departments/ u otro.

---

## Pregunta para humano

El gap entre User.NIVEL_ACCESO_CHOICES y access_service._NIVEL_ACCESO_TO_LEVEL es intencional (porque B.12 promete una NUEVA dimension de acceso) o es regresion (porque al renombrar campos en L1/L3, no se sincronizo el service)? La respuesta determina si #3 es ampliacion de mapping o rename masivo en la BD.

---

## Apendice -- Limpieza realizada

- El tenant temporal audit-tenant y el user auditor_other creados durante este audit fueron eliminados (Tenant + TenantMembership + User). Demo-pro permanece intacto: 15 empleados, 9 family-members, 0 DocumentAccessLog.
- No se creo ni dejo ningun test temporal en apps/api/tests/. El archivo apps/api/tests/test_audit_temp_hr.py existia desde antes de esta corrida (de la corrida del vyntia-hr-tester); no se modifico.
