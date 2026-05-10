# Sub-proyecto B — Vyntia Core Functional Design Spec

**Versión:** 1.0
**Fecha:** 2026-05-09
**Antecesor:** Sub-proyecto C (multi-tenancy + RLS) — completo (`c-multitenancy-complete`)
**Sucesor inmediato sugerido:** Sub-proyecto D (Vyntia Pay)

> Este documento define el alcance, arquitectura y plan de fases del sub-proyecto B. B parte de un codebase que ya tiene Foundation (A) + Multi-tenancy (C) terminados, y entrega Vyntia Core como producto HR limpio, sellable, dividido en módulos comerciales.

---

## 1. Contexto

VYNTIA es una plataforma HR SaaS multi-tenant para Perú. Después de Foundation (A) y Multi-tenancy + RLS (C), la base técnica está lista pero la oferta funcional es delgada: los 6 apps de Core (`identity`, `organization`, `employees`, `contracts`, `documents`, `onboarding`) están estructurados pero conservan parches del legacy `D:\INTRANET\`, gaps comparado con el catálogo maestro, y bugs conocidos que Foundation aceptó como deuda.

El sub-proyecto B cierra esa deuda y construye encima los módulos 01 (Políticas) y 02 (Organización extendida) + completa el módulo 03 (Gestión Empleo) según `docs/00_VYNTIA_MAESTRO.md`. Al finalizar, VYNTIA es un producto HR Core comercializable como tier Starter (sin Pay todavía — eso es D).

B absorbe los sub-proyectos que la roadmap previa llamaba **E (Extensión Organización)** y **F (Policies)**, simplificando la roadmap post-B.

---

## 2. Objetivos

### 2.1 Objetivo principal

Entregar Vyntia Core como producto HR comercializable: limpio, sin deuda heredada visible al cliente, con la cobertura funcional de los módulos 01, 02, 03 completos.

### 2.2 Objetivos específicos

| # | Objetivo | Métrica |
|---|---|---|
| O1 | Cerrar la deuda técnica heredada de A | 0 fallas pytest pre-existentes; 0 errores tsc; lint baseline reducido |
| O2 | Validar tenant-readiness en los 6 apps de Core | Cada app tiene tests de aislamiento ORM/RLS pasando |
| O3 | Completar paridad con INTRANET legacy donde aplique a Core | Inventario en B.0 lista features porteables; B.X las cierra |
| O4 | Implementar módulo 02 completo | Position, OrgChart, CCF (Ley 30709), SalaryBand, MPP/CPE (SERVIR) |
| O5 | Implementar módulo 03 completo | 7 sub-procesos: selección, vinculación, inducción, prueba, legajos, desplazamiento, desvinculación |
| O6 | Implementar módulo 01 (Policies) | Gestor documental, plan anual, matriz cumplimiento, alertas |
| O7 | E2E de flujo crítico end-to-end | Provisioning → org chart → empleado → onboarding → contrato → cese funciona en Playwright |

### 2.3 No-objetivos (explícitos)

- **Sub-proyecto D (Vyntia Pay)** — planilla, PLAME, T-Registro de pago, AFPnet, CTS, gratificaciones. NO en B; sigue siendo D.
- **Sub-proyecto N (Asistencia)** — control de tiempo, turnos, marcaje. Sigue siendo N.
- **Sub-proyectos H (Pulse), G (Learning/Career), Q (Hire)** — todos post-B.
- **Sub-proyecto P (App móvil)** — el portal móvil sigue siendo P.
- **Sub-proyectos transversales avanzados** (T, U, V, W, X) — workflow engine, doctype engine, permissions v2, notifications, audit log. B agrega capacidades mínimas inline cuando las necesite (ej. una mini-aprobación de desvinculación), sin construir motores completos.

---

## 3. Arquitectura general

### 3.1 Decisión clave: audit-first

El sub-proyecto arranca con una **fase de auditoría sin código (B.0)** que produce 4 documentos:

1. `INVENTORY.md` — qué hay en VYNTIA hoy, qué hay en INTRANET legacy, qué pide el maestro.
2. `BACKLOG.md` — items priorizados (P0/P1/P2) con dependencias y fase B.X estimada.
3. `ROADMAP-B.md` — confirma o ajusta la lista esperada de fases B.1–B.16.
4. `ADRS.md` — decisiones transversales (i18n, audit log, workflows, storage, testing).

B.0 timeboxed a 3-5 días. Las fases siguientes se planifican con datos reales del backlog, no con suposiciones.

### 3.2 Forma esperada de las fases (sujeta a confirmación post-B.0)

```
B.0  — Auditoría & inventory                            (NO code; produce backlog)
B.1  — Polish wave: bug-fix baseline                    (cierra deuda A: pytest, tsc, lint, tenant audit)
B.2  — Polish wave: identity                            (usuarios, roles, permisos, RBAC UI)
B.3  — Polish wave: organization                        (departments, locations, company config)
B.4  — Polish wave: employees                           (Employee + datos personales/familiares/académicos)
B.5  — Polish wave: contracts + documents + onboarding  (contratos, plantillas, expediente, onboarding actual)
B.6  — Módulo 02: Positions + OrgChart                  (Position, PositionProfile, OrgUnit jerárquico)
B.7  — Módulo 02: CCF + SalaryBand                      (Cuadro Categorías y Funciones, bandas salariales — Ley 30709)
B.8  — Módulo 02: MPP + CPE                             (Manual Perfiles de Puestos + Cuadro Puestos de la Entidad — SERVIR)
B.9  — Módulo 03.1: Selección                           (proceso de selección con fases, criterios, evaluaciones)
B.10 — Módulo 03.2: Vinculación + T-Registro            (generación contrato, firma electrónica, registro T-Registro)
B.11 — Módulo 03.3+4: Inducción + Período de prueba     (plan inducción RPE 265-2017-SERVIR-PE, evaluación período prueba)
B.12 — Módulo 03.5: Legajos digitales completos         (expediente digital con índice, búsqueda, retención)
B.13 — Módulo 03.6: Desplazamiento                      (rotación, encargatura, destaque, comisión, permuta, designación)
B.14 — Módulo 03.7: Desvinculación + liquidación        (renuncia, cese, despido, liquidación beneficios sociales)
B.15 — Módulo 01: Policies                              (gestor documental políticas, plan anual, matriz cumplimiento, alertas)
B.16 — E2E + docs + close-out                           (Playwright flows, runbooks, tag b-vyntia-core-complete)
```

El número y orden exactos pueden ajustarse en B.0 según hallazgos del audit. Por ejemplo:
- Si el INVENTORY revela que `documents` ya está bien y `onboarding` no, B.5 se divide en dos fases.
- Si Selección (03.1) requiere features de notificaciones que B no quería construir, baja a P2 y se difiere a Q.
- Si MPP/CPE comparten 80% del código con CCF, B.7 y B.8 se fusionan.

### 3.3 B.0 entregables detallados

**`INVENTORY.md`** — un capítulo por cada uno de los 6 apps de Core, con esta estructura:

```markdown
## App: <nombre>

### Estado actual en VYNTIA (post-A + C)
- Modelos: lista de tablas, campos clave
- Endpoints: lista de URLs públicas (`/api/v1/...`)
- UI: páginas que consumen los endpoints
- Tests: cobertura actual

### Gaps vs INTRANET legacy (D:\INTRANET, bd_rrhh_intranet)
- Features que existían en el legacy y NO están en VYNTIA
- Tipo: bug fix / feature port / opcional
- Prioridad: P0 (bloquea venta) / P1 (importante) / P2 (nice to have)

### Gaps vs maestro módulo 0X
- Features del catálogo maestro que NO existen ni en VYNTIA ni en legacy
- Cuál sub-fase B.X la construye

### Bugs y deuda técnica conocidos
- Pytest failures atribuibles a este app
- TS errors atribuibles
- Lint warnings atribuibles
- Tenant-readiness gaps específicos

### Notas
- Decisiones tomadas durante A o C que afectan a este app
- Riesgos específicos de tocarlo
```

**`BACKLOG.md`** — tabla maestra:

```markdown
| Item | App | Tipo | Prioridad | Fase | Dependencias | Estimación |
|------|-----|------|-----------|------|--------------|-----------|
| Fix duplicate 'id' key in CustomTokenObtainPairSerializer.validate() | identity | bug | P1 | B.1 | — | 0.5d |
| Implementar Position model | organization | new | P0 | B.6 | — | 2d |
| Port batch import de empleados desde CSV | employees | parity | P1 | B.4 | — | 1d |
... (~50-100 items)
```

**`ROADMAP-B.md`** — sigue el formato de `2026-05-09-vyntia-C-multitenancy-master-roadmap.md`:

```markdown
| Fase | Branch | Scope | Necesita | Plan detallado |
|------|--------|-------|----------|----------------|
| B.0  | vyntia/B0-audit | ... | A, C | (este sub-proyecto auto-referencia) |
| B.1  | vyntia/B1-polish-baseline | ... | B.0 | TBD post-B.0 |
...
```

**`ADRS.md`** — decisiones transversales con formato ADR ligero:

- ADR-B.1: i18n strategy
- ADR-B.2: Audit log scope
- ADR-B.3: Approval workflow strategy (esperar T o construir mini)
- ADR-B.4: Document storage backend
- ADR-B.5: Testing strategy para flujo empleo (pytest only vs pytest + Playwright)
- ADR-B.6: SERVIR vs LCT — manejo en UI (toggle, separación, ambos)
- ADR-B.7: Versionado de modelos críticos (Position, Contract) — historial inline o paquete `django-simple-history`?

### 3.4 Convenciones técnicas (heredadas)

Sigue las reglas establecidas en A y C:

1. **Bounded contexts**: cada feature nueva vive en el app que le corresponde. FKs cross-app vía string lazy (`'employees.Employee'`). Imports cross-app prohibidos — se llama a la public API en `apps/<context>/services/`.
2. **Multi-tenant**: cualquier modelo de negocio nuevo extiende `TenantScopedModel` (apps/core/models.py). Tests de aislamiento RLS siguen el patrón de `apps/api/tests/test_tenant_isolation.py`. La política RLS se aplica automáticamente vía `manage.py setup_rls` (descubre modelos via introspección).
3. **APIResponse**: todos los endpoints retornan vía `apps.core.responses.APIResponse.success/error`. Paginación vía `StandardResultsSetPagination` (20/page) o `LargeResultsSetPagination` (50/page).
4. **English en código, español en UI**: nombres de clases/funciones/variables en inglés. Strings visibles al usuario en español. (i18n multi-idioma queda como decisión de B.0 ADR.)
5. **Términos legales peruanos preservados**: DNI, RUC, CTS, PLAME, T-Registro, AFP, ONP, ESSALUD, SUNAT, SERVIR, MPP, CPE, CCF.
6. **Tests obligatorios**: cada modelo nuevo tiene tests de creación + isolation. Cada endpoint nuevo tiene smoke test (200/4xx/5xx). Cada flow crítico tiene Playwright e2e.
7. **Commits**: `feat(BX): ...`, `test(BX): ...`, `docs(BX): ...`, `ci(BX): ...`, `chore(BX): ...`, `fix(BX): ...`.
8. **Branch + plan + merge**: cada fase es su propia branch `vyntia/BX-<nombre>`, plan en `docs/superpowers/plans/2026-05-09-vyntia-BX-<nombre>.md`, merge a master con `git merge --no-ff` y mensaje `Merge B.X: ...`.
9. **Baselines preservadas**: cada fase respeta o mejora pytest passing count, vitest count, build clean, tsc 0 NEW errors.

### 3.5 Tier comercial al cierre de B

| Tier | Cobertura post-B | Bloqueo |
|------|------------------|---------|
| Starter privado | Empleados + contratos + onboarding + organigrama + CCF + selección + cese + liquidación | Pay (D) — sin planilla no hay venta plena |
| Starter público (SERVIR) | Lo anterior + MPP/CPE + desplazamiento + designación | Pay (D) |
| Pro | Lo de Starter + políticas (módulo 01) | Pulse (H), Learning (G) |
| Enterprise | Pro + multi-empresa avanzada | Insights (R), Workflow (T), Permissions v2 (V) |

Sub-proyecto D (Vyntia Pay) es el siguiente unlock comercial obligatorio para venta Starter completa. Después de D + B, VYNTIA puede venderse a clientes reales.

---

## 4. Riesgos y mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|:---:|:---:|---|
| RB1 | El audit B.0 expone más gaps de los esperados; el alcance se infla | Alta | Medio | B.0 timeboxed 3-5 días. Backlog cap: solo P0+P1 entran en B.X; P2 se difiere. |
| RB2 | INTRANET legacy es tan desordenado que el inventory es lento | Media | Bajo | Maestro > legacy como fuente. Legacy se revisa solo donde el maestro es ambiguo. |
| RB3 | Features SERVIR vs LCT se mezclan mal en código compartido | Media | Alto | ADR-B.6 fija el patrón. Tests por sector. UI condicionada por `tenant.sector`. |
| RB4 | Tests crecen mucho; CI rebasa timeout 5 min | Media | Medio | Cada fase mide su contribución al runtime. Si rompe budget, paralelizar pytest workers en CI. |
| RB5 | El ciclo 16-fase se hace eterno; pierdes tracción | Alta | Medio | Cada fase mergeable. Pausa en cualquier punto deja un producto coherente. Re-priorización post-B.5. |
| RB6 | Modelos compartidos entre fases (ej. Position usado por Contract y Selección) generan rebases dolorosos | Media | Medio | Roadmap de fases respeta dependencias declaradas en BACKLOG. Si B.10 necesita Position, B.6 va antes. |
| RB7 | Liquidación de beneficios sociales (B.14) toca cálculos que después rompe Pay (D) | Media | Alto | B.14 implementa solo cálculo legal mínimo; Pay (D) lo extiende con regímenes completos. ADR explícito. |
| RB8 | Frontend para módulo 02 (orgchart visual) requiere libs nuevas; explosion de bundle | Media | Bajo | ADR-B.X evalúa libs (react-d3-tree, etc.) en B.6. Lazy-load. Bundle size budget revisado. |
| RB9 | Performance de queries con muchas joins (empleado + contrato + cargo + área + tenant) degrada | Baja | Medio | Cada fase mide N+1 queries con `django-debug-toolbar` localmente. Cuando aplique, agrega `select_related`/`prefetch_related`. |
| RB10 | Audit log distribuido sin sub-proyecto X causa esfuerzo duplicado en B | Media | Bajo | ADR-B.2 fija scope mínimo. Lo que B necesite hoy se hace inline; X después generaliza. |

---

## 5. Definition of Done — Sub-proyecto B

Sub-proyecto B se considera **completo** cuando TODAS estas condiciones se cumplen:

### 5.1 Calidad técnica

- [ ] Todas las fases B.0–B.N mergeadas a master
- [ ] Tag `b-vyntia-core-complete` aplicado al merge final
- [ ] `pytest tests/ apps/<each>/tests/` ≥ 350 passed (target — se ajusta tras B.0; baseline post-C es 271)
- [ ] 0 fallas pytest pre-existentes sin justificar (las 7 actuales se cierran o se reclasifican explícitamente)
- [ ] `manage.py setup_rls --check` clean — toda nueva tabla tenant-scoped tiene política RLS
- [ ] `npx tsc --noEmit -p tsconfig.app.json` clean (los errores de `BlankEnum.ts` se cierran o se documentan como wontfix)
- [ ] `npm run build` exit 0
- [ ] `npm test -- --run` ≥ 50 passed (target — actual baseline es 32)
- [ ] CI workflow verde en todos los jobs

### 5.2 Cobertura funcional

- [ ] Módulo 01 (Políticas) implementado: gestor documental, plan anual, matriz cumplimiento, alertas
- [ ] Módulo 02 (Organización) extendido: Position, OrgChart, CCF, SalaryBand, MPP/CPE
- [ ] Módulo 03 (Gestión Empleo) completo: 7 sub-procesos funcionando end-to-end
- [ ] Los 6 apps de Core (identity, organization, employees, contracts, documents, onboarding) auditados y pulidos: 0 features INTRANET-paritarias P0 pendientes

### 5.3 Documentación

- [ ] `docs/operations/` actualizado con runbooks de los flows nuevos:
  - `provision-position.md`
  - `seleccion-process.md`
  - `legajo-restore.md`
  - `desvinculacion-liquidacion.md`
  - `policy-publish.md`
- [ ] `docs/00_VYNTIA_MAESTRO.md` actualizado: módulos 01, 02, 03 marcados ✅
- [ ] `docs/ROADMAP_SUBPROJECTS.md` actualizado: B ✅, E y F absorbidos en B
- [ ] `CLAUDE.md` actualizado: active sub-project = D (siguiente)
- [ ] README operativo: cliente prospectivo entiende qué tier le corresponde

### 5.4 Smoke test manual

- [ ] Provisionar tenant nuevo desde `admin.vyntia.pe`
- [ ] Activar invitación, crear primer admin
- [ ] Crear estructura organizativa: departamentos, posiciones, organigrama
- [ ] Crear empleado, asignar posición, generar contrato
- [ ] Iniciar onboarding, completar inducción, evaluar período de prueba
- [ ] Mover empleado (desplazamiento) y luego cesarlo (desvinculación)
- [ ] Generar legajo digital descargable
- [ ] Publicar una política con versión inicial

### 5.5 Performance & escala

- [ ] Tenant con 1000 empleados + 5 años de datos sigue cargando dashboard < 2s
- [ ] Listado de empleados con filtros + paginación < 500ms p95
- [ ] Generación de contrato (PDF) < 5s
- [ ] No hay queries N+1 detectadas en flows críticos

---

## 6. Roadmap post-B

Al cerrar B, los sub-proyectos restantes mantienen su orden con E y F absorbidos:

| Orden | Sub-proyecto | Necesita |
|---|---|---|
| Cerrado | A — Foundation | — |
| Cerrado | C — Multi-tenancy + RLS | A |
| **Actual** | **B — Vyntia Core funcional + módulos 01/02/03** | A, C |
| Siguiente | D — Vyntia Pay | B |
| Después | N — Asistencia + turnos | D |
| Paralelo a D | S — Billing SaaS | C |
| Paralelo a D | V — Permissions v2 | C |
| Después | P — App móvil | B |
| Después | H — Vyntia Pulse | B |
| Después | G — Learning + Career | B |
| Después | Q — Vyntia Hire (ATS) | B |
| Después | I, J, K, L, M, O — Relaciones HH + Discipline | B |
| Después | R — Vyntia Insights | B + datos reales |
| Después | T — Workflow Engine | B |
| Después | U — DocType Engine | B |
| Después | W — Notifications | B |
| Después | X — Audit Log | B |

---

## 7. Decisiones diferidas a B.0 (ADRs)

Estas se cierran durante la fase B.0 antes de entrar a B.1:

- **ADR-B.1 i18n**: ¿solo español o multi-idioma? Si multi, ¿qué idiomas (EN para internacional)?
- **ADR-B.2 Audit log**: ¿esperamos sub-proyecto X o agregamos un mini audit log en B? (Riesgo: regulación SUNAT/SERVIR puede exigir trazabilidad temprana.)
- **ADR-B.3 Approval workflows**: ¿esperamos sub-proyecto T o construimos mini-aprobaciones inline en cada flow que lo necesite (cese, ascenso, etc.)?
- **ADR-B.4 Document storage**: filesystem local (actual) vs S3/Azure Blob con signed URLs (production-ready). Decisión afecta despliegue.
- **ADR-B.5 Testing strategy**: ¿flows críticos cubren con Playwright e2e desde el inicio o cierre B.16 hace todos?
- **ADR-B.6 SERVIR vs LCT en UI**: toggle por tenant, sección separada, o features condicionadas por `tenant.sector`?
- **ADR-B.7 Versionado de modelos críticos**: Position y Contract necesitan historial. ¿Inline (campo `replaces` FK) o paquete `django-simple-history`?
- **ADR-B.8 Org chart frontend**: ¿react-d3-tree, dagre-d3, react-flow, otro? Decisión de bundle.
- **ADR-B.9 Liquidación de beneficios**: scope mínimo en B.14 vs scope completo (que arrastra Pay). Cuánto cálculo legal en B y cuánto en D.

---

## 8. Métricas de éxito

Al cierre de B medimos:

| Métrica | Baseline (post-C) | Target (post-B) |
|---|:---:|:---:|
| Apps Django con tests de aislamiento | 1 (tenancy) | 7 (tenancy + 6 Core) |
| Modelos tenant-scoped | ~20 | ~50 |
| Endpoints REST documentados | ~80 | ~200 |
| Páginas UI funcionales | ~30 | ~80 |
| Pytest passed | 271 | ≥ 350 |
| Vitest passed | 32 | ≥ 50 |
| Playwright e2e cases | 3 (skipped) | ≥ 8 (running) |
| Lint warnings | 641 | ≤ 600 |
| TS errors | 1 (BlankEnum) | 0 |
| Runbooks ops | 5 | ≥ 12 |
| Tier comercial vendible | Pre-MVP | Starter (con D) |

---

## 9. Próximo paso inmediato

1. Aprobar esta spec.
2. Invocar `superpowers:writing-plans` para escribir `docs/superpowers/plans/2026-05-09-vyntia-B0-audit.md`.
3. Ejecutar B.0 (3-5 días estimados).
4. Con los entregables de B.0 (`INVENTORY.md`, `BACKLOG.md`, `ROADMAP-B.md`, `ADRS.md`), planear B.1.
5. Iterar B.1 → B.16, mergeando cada fase a master con `--no-ff` mirroring el flujo C.
6. Tag `b-vyntia-core-complete` al cerrar B.16.

---

**Spec status:** READY FOR IMPLEMENTATION PLANNING
**Next step:** invoke `superpowers:writing-plans` to draft `docs/superpowers/plans/2026-05-09-vyntia-B0-audit.md`.
