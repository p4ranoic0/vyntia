# PM — Audit Empleados v2 con BD poblada (2026-05-22)

**Orquestador:** main agent en rol PM (siguiendo playbook `.claude/agents/vyntia-pm.md`).
**Scope:** módulo Empleados, segunda corrida contra `bd_vyntia` con tenant `demo-pro` seedado (15 empleados peruanos régimen 728, 5 candidatos B.9, 1 posting con 5 apps, 3 DigitalDossiers con 15 secciones c/u).
**Diferencia vs v1 (`2026-05-22-empleados.md`):** ahora los especialistas ejecutaron código real contra data realista, no solo análisis estático.
**Especialistas lanzados (4, en paralelo):** feature-supervisor, code-quality, ui-modular, hr-tester.
**Reportes fuente:** todos persistidos en `docs/agent-reports/{agente}/2026-05-22-empleados-bd-poblada.md`.

---

## TL;DR — Verdict ejecutivo

🔴 **ROJO con bordes amarillos.** Antes era amarillo. La BD poblada destapó **4 hallazgos P0 nuevos** que no se veían en análisis estático, **confirmó 7 hallazgos críticos previos en runtime** (algunos peor de lo estimado), y **refutó/reclasificó 3**.

**Lo crítico real:**
1. **`/api/v1/academic-records/` retorna 500** — endpoint completamente inutilizable. Stale field names `fecha_inicio_estudios`/`fecha_termino_estudios` en `DatosAcademicosViewSet.ordering` (mismo patrón que el fix L3.10.4e ya pasado). Tu CRM/frontend rompe al entrar a la pestaña Académicos.
2. **Cross-tenant leak confirmado runtime:** un user RRHH de otro tenant ve los 9 FamilyMembers + AcademicRecords + Certifications de `demo-pro`. 4 viewsets sin `TenantAwareViewSetMixin` + sobre-escriben permissions a `IsAuthenticated`.
3. **`EmpleadoCreateSerializer` acepta basura como DNI:** `"1234567"` (7 dígitos) y `"ABC12345"` (letras) → **status 201 persistente en BD**. El validator solo aplica en Update, no en Create.
4. **Menores ilegales pasan en POST:** 15, 16, 17 años se aceptan; `validate_fecha_nacimiento` NO se invoca en CreateSerializer. Riesgo Ley 28518 directo.

**Lo crítico ya conocido, ahora confirmado runtime:**
- PL gate leak (#118) — admin `nivel_acceso=personal` recibe PL 9 (médicos, accidentes).
- DocumentAccessLog vacío (#121) — `consolidated-pdf/` genera PDF de 6133 bytes; access log queda en 0.
- `calcular_vacaciones_pendientes()` retorna 150 días para 728, 276 Y prácticas — hardcoded, ignora régimen.
- Locación de servicios aparece en query naive de planilla (`Employee.datos_laborales.filter(estado_datos='activo')`) — riesgo SUNAT/T-Registro.
- `PersonnelRequisition` dual control roto — mismo `user_id` puede ser `approved_by_hr` y `approved_by_finance` y el estado pasa a `approved`.
- Reporte PDF integral de empleado: `carrera_especialidad` VariableDoesNotExist + ImportError de `pdf_generator` — el reporte que `EmpleadoReportPage.tsx` invoca **no genera nada legible**.

**D (Vyntia Pay) NO puede arrancar encima de Empleados hoy.** Faltan ~5-8 horas de fixes de seguridad + validación.

---

## Hallazgos top (consolidado de los 4 especialistas)

### 🔴 P0 NUEVOS (solo visibles con BD poblada)

| # | Hallazgo | Fuente | Evidencia | Horizonte |
|---|----------|--------|-----------|-----------|
| 1 | `/api/v1/academic-records/` retorna **500** | feature-supervisor | Stale field names en `DatosAcademicosViewSet.ordering` líneas 875-879 (`fecha_inicio_estudios`, `fecha_termino_estudios` ya no existen) | CORTO — 15 min |
| 2 | **Cross-tenant leak runtime confirmado** en 4 viewsets | feature-supervisor + hr-tester | User RRHH de `audit-tenant` lista 9 FamilyMembers de `demo-pro`. `DatosFamiliaresViewSet`, `DatosAcademicosViewSet`, `CursosCertificacionesViewSet` y `SelectionStageViewSet` sin `TenantAwareViewSetMixin` y sobreescriben permissions a `IsAuthenticated` | CORTO — 1 h |
| 3 | `EmpleadoCreateSerializer` acepta DNI inválidos con **201 persistente** | hr-tester | `POST /api/v1/empleados/ {"numero_documento": "1234567"}` → 201; `"ABC12345"` → 201; ambos persisten en BD | CORTO — 30 min |
| 4 | Menores de edad (15-17 años) **aceptan** en POST | hr-tester | `validate_fecha_nacimiento` no se invoca en CreateSerializer → riesgo Ley 28518 (practicantes) y trabajo infantil | CORTO — 15 min |

### 🔴 P0/P1 CONFIRMADOS RUNTIME (eran solo estáticos en v1)

| # | Hallazgo | Fuente | Evidencia runtime | Horizonte |
|---|----------|--------|-------------------|-----------|
| 5 | PL gate leak (#118) | feature-supervisor | Admin `nivel_acceso=personal` lista dossier-sections con `permission_level=9` → 200 OK con 6 PL9 expuestas (médicos, accidentes) | CORTO |
| 6 | DocumentAccessLog vacío (#121) | feature-supervisor | `DocumentAccessLog.objects.count()` antes=0 / después de `consolidated-pdf` (6133 bytes) =0 | CORTO |
| 7 | `calcular_vacaciones_pendientes()` hardcoded | hr-tester | Devuelve 150 días para 728, 276 Y prácticas — ignora régimen totalmente | CORTO |
| 8 | Locación mezclada en planilla | hr-tester | Empleado `regimen_laboral='locacion'` aparece en `Employee.datos_laborales.filter(estado_datos='activo')` | CORTO |
| 9 | Dual control roto en `PersonnelRequisition` | code-quality | `req.approve_hr(admin); req.approve_finance(admin)` → `hr_id==fin_id`, `status='approved'` sin error | CORTO |
| 10 | SERVIR Art. 5 confunde días | code-quality | Posting con 7 días calendario (≈5 hábiles) pasa `_validate_servir_publication_requirements` | CORTO |
| 11 | Reporte PDF empleado: 2 bugs runtime | hr-tester | `carrera_especialidad` VariableDoesNotExist + ImportError de `pdf_generator` — el reporte que `EmpleadoReportPage.tsx` invoca no genera nada legible | CORTO |
| 12 | `boletas_recientes()` stub silencioso | code-quality | Devuelve `[]` siempre contra empleado real — código muerto en producción | CORTO (5 min) |

### 🟠 NUEVOS ALTOS

| # | Hallazgo | Fuente | Evidencia | Horizonte |
|---|----------|--------|-----------|-----------|
| 13 | N+1 severo en `EmpleadoListSerializer` | code-quality | 15 empleados = **73 queries**. `obj.datos_laborales_actuales()` + `obj.ubicacion_actual()` bypassean el `prefetch_related` ya definido | CORTO (30 min) |
| 14 | Vocab mismatch — bug latente | feature-supervisor | `User.NIVEL_ACCESO_CHOICES=[total/departamental/personal/limitado/lectura]` vs `access_service._NIVEL_ACCESO_TO_LEVEL={bajo/medio/alto/total}`. Si #118 se cierra sin arreglar este map primero → **lockout masivo** | CORTO (antes de #118) |
| 15 | Seed `demo-pro` crea roles que no satisfacen `@require_hr` | hr-tester | Roles "Admin"/"RRHH" — el decorator es case-sensitive y espera otro string | CORTO (fix en mi seed) |
| 16 | Seed bypassea workflow PersonnelRequisition | code-quality | REQ-DEMO-001 creado con `status='approved'` direct, sin invocar `approve_hr`/`approve_finance` | CORTO (fix en mi seed) |
| 17 | Seed sin CandidateEvaluations / MeritRankings | code-quality | 0 filas → vacía el showcase comercial; B.9 demo incompleto | CORTO (fix en mi seed) |

### ✅ REFUTADOS / RECLASIFICADOS

| # | Hallazgo previo | Status actualizado |
|---|-----------------|---------------------|
| - | `EmpleadosListPage.tsx:100` ReferenceError → CRÍTICO | **MEDIO**: la página es huérfana, NO está enrutada (la enrutada es `Empleados.tsx`). Es código muerto. Borrar. |
| - | B.9 lifecycle transitions | **PASS**: 5 applications atravesaron `received → reviewing → in_evaluation → finalist/eliminated` con state machine respetada |
| - | `/api/v1/employees/` cross-tenant | **PASS**: aísla tenants correctamente vía `TenantAwareViewSetMixin` |
| - | `validate_fecha_nacimiento` bloquea practicantes 16-17 ilegalmente | **REFUTADO + EMPEORADO**: NO bloquea — al revés, **acepta** 15-17 años. Hallazgo previo era inverso a la realidad. |

### ✅ Lo que SÍ se mantiene bien

- Tests suite intacta: 982/1/17 backend, 178 vitest, sin regresiones.
- `manage.py check` 0 issues.
- `/api/v1/employees/` y otras URL principales responden 200 con data poblada.
- B.9 state machine respetada.
- DigitalDossier `build_dossier_for_employee` crea 15 secciones automáticamente.
- Tenant isolation **sí funciona** en endpoints que usan `TenantAwareViewSetMixin`.

---

## Trends que cambian la lectura del módulo

1. **El patrón "TenantAwareViewSetMixin sí o no" es más severo de lo que parecía.** No es una opción de diseño — es la diferencia entre aislar tenants y exponerlos. 4 viewsets sin él demostraron leak runtime; los que lo usan, no. Esto es trabajo sistemático: auditar TODOS los viewsets del proyecto y agregar el mixin donde falte, antes de comercializar.
2. **"Validators en Update pero no en Create" es un anti-pattern repetido.** DNI, edad mínima, posiblemente otros. Hipótesis: cuando se escribió el Update se agregaron validators; cuando se escribió el Create se asumió que estaban en el modelo (y no estaban). Auditar TODOS los serializers Create del proyecto.
3. **"Skeleton built, call sites missing" se confirmó en runtime y es más amplio.** PL gate, AccessLog, validators del modelo — patron de "tenemos el código pero no lo invocamos". Sugerencia para D: agregar al checklist de cierre "para cada service/validator implementado, demostrar 1 call site real, no solo unit test".
4. **El seed que entregué tiene 3 bugs reales detectados por los agentes.** Es metarelevante: el equipo PM funcionó cuando la BD estaba poblada, y mi propio output entró al pipeline de calidad. Tengo que fixearlos antes de que el seed sea referencia canónica.

---

## 3 acciones priorizadas

### 1. CORTO INMEDIATO — Sprint "Empleados Hot-fix" (~5-8 horas)

Bloque de 4 P0 + reporte PDF + fixes del seed. Antes de tocar D.

**Tareas concretas:**
- [ ] (15 min) Fix `DatosAcademicosViewSet.ordering` — quitar field names obsoletos
- [ ] (1 h) Agregar `TenantAwareViewSetMixin` a 4 viewsets sin él: DatosFamiliaresViewSet, DatosAcademicosViewSet, CursosCertificacionesViewSet, SelectionStageViewSet
- [ ] (30 min) Mover validator de DNI y `validate_fecha_nacimiento` al modelo o a `EmpleadoCreateSerializer`
- [ ] (15 min) Cap mínimo de edad (18 años con excepción documentada para Ley 28518 practicantes 16-17 con flag explícito)
- [ ] (1 h) Cerrar #118 — invocar `access_service.can_access()` en 3 viewsets B.12. **Antes** arreglar el `_NIVEL_ACCESO_TO_LEVEL` map para evitar lockout (#14).
- [ ] (30 min) Invocar `log_access()` en `consolidated_pdf` y descarga DigitalDocument (#121)
- [ ] (30 min) Parametrizar `calcular_vacaciones_pendientes` por régimen (28d 728 indefinido / 30d funcionario / 15d MyPE / 0 locación) — temporal hasta que D haga el modelo definitivo
- [ ] (30 min) Excluir `regimen_laboral='locacion'` de queries de planilla (filtro explícito en service de Pay)
- [ ] (15 min) Validar `req.approved_by_hr != req.approved_by_finance` en `PersonnelRequisition.approve_finance()`
- [ ] (45 min) Fix runtime errors del reporte PDF de empleado (`carrera_especialidad` + ImportError pdf_generator)
- [ ] (30 min) Fix seed: roles correctos, `approve_hr/approve_finance` en lugar de status direct, agregar CandidateEvaluations + MeritRanking

### 2. MEDIO — Decisión sub-proyecto E (Modularidad)

ui-modular ahora trae **un sketch concreto de ~2 días y ~80 LOC**: `Tenant.plan` ya existe en BD (sub-proyecto C lo dejó listo), `/api/v1/workspaces/` ya lo expone, falta `<ModuleGate>` + `useFeature()` + cablearlo al `TenantContext`. Esto es más liviano que lo que pensábamos en v1. Brainstorm formal sigue siendo necesario para decidir secuencia (antes/después/paralelo con D), pero el costo bajó.

### 3. LARGO — D.0 ADR (cuando D arranque)

Sin cambios vs v1: vendor PDF, régimen laboral parametrizado, batch import CSV, snapshot planilla por mes. **Agregar:** N+1 fix en `EmpleadoListSerializer` (#13) entra como prerequisito si Pay va a hacer joins similares.

---

## Sugerencia para afinar el propio equipo de agentes

### Tune-up para `vyntia-code-quality`

**Observación:** durante esta corrida, el agente usó un savepoint para test pero **mutó REQ-DEMO-001 del tenant demo-pro** sin envoltura `transaction.atomic + rollback`. Lo restauró manualmente al final y reportó la advertencia, pero el patrón es peligroso — en una corrida concurrente o si el agente aborta mid-task, la data del tenant referencia queda inconsistente.

**Cambio textual propuesto:** en `.claude/agents/vyntia-code-quality.md`, bajo "Restricciones", agregar:

> **CRÍTICO — Mutaciones ORM:** si necesitas escribir/modificar/borrar via ORM para verificar runtime, **DEBES envolver TODO en `transaction.atomic()`** y forzar rollback al final con `transaction.set_rollback(True)` o `raise Exception("rollback intencional")`. NUNCA dejes commits a la BD del proyecto durante una corrida read-only. Si necesitas data para tu test, créala en el savepoint, no asumas data preexistente como mutable.

**Bonus — feature-supervisor + hr-tester:** ambos crearon segundos tenants temporales y los borraron al final. **Hicieron bien.** Esto debería ser regla explícita para todos los especialistas que crean tenants temporales — registrarlo en `.claude/agents/{specialist}.md` como buena práctica.

### Observación de proceso (sin tune-up directo)

El segundo run vs el primero arrojó **4 P0 nuevos**. Hipótesis: el primer audit con BD vacía gastó tokens en analizar grep/glob de cosas que con BD real se invalidaban en segundos. Recomendación operativa para futuras corridas: **siempre correr `seed_demo_pro` antes de invocar /vyntia-pm audit X** si el sub-módulo lo soporta. Es 1-2 min de setup que reposiciona toda la corrida.
