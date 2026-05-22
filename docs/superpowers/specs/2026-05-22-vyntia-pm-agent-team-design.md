# VYNTIA — PM Agent Team Design

**Fecha:** 2026-05-22
**Sub-proyecto:** Tooling transversal (no es parte del roadmap A–D, es soporte continuo)
**Autor:** Brainstorming Claude Code (Henrry Garcia)
**Estado:** SPEC para revisión

---

## Problema

VYNTIA está levantando con muchos bugs y el roadmap promete un producto modular (Empleados, Contratos, Pay, Vacaciones, Onboarding, etc.) que hoy se ve y se comporta como un monolito. Necesitamos un equipo de agentes especialistas que:

1. **Verifiquen continuamente** qué se entregó vs qué prometió el spec.
2. **Prueben los flujos** con conocimiento del negocio RRHH peruano.
3. **Auditen la UI** con criterio de diseño y de **modularidad comercial** (feature flags por tenant/plan).
4. **Vigilen la calidad** del código en horizontes corto y largo.
5. **Reporten al humano** desde un PM que orquesta y propone ajustes a los propios agentes.

## Decisiones de alcance (cerradas en brainstorming)

| # | Pregunta | Decisión |
|---|----------|----------|
| 1 | Composición | **5 agentes separados** |
| 2 | Ubicación | Repo (`.claude/agents/` versionado en git) |
| 3 | ¿Qué significa "modular"? | **Funcional + comercial**: feature flags por tenant/plan; la UI esconde lo no contratado |
| 4 | Modo PM | Reactivo, invocado a demanda (`/vyntia-pm …`) |
| 5 | Formato de reportes | Markdown estructurado en `docs/agent-reports/{agente}/YYYY-MM-DD-{scope}.md` |
| 6 | Slash commands | Uno por agente + uno para el PM |
| 7 | Skills compartidas | Cada agente reutiliza las skills existentes del proyecto (django-rrhh, react-rrhh, frontend-design, code-reviewer, chrome-devtools) |

---

## Arquitectura

```
Usuario
  │
  ├─ /vyntia-pm <tema>          → invoca al PM
  │      │
  │      └─ Agent tool (paralelo cuando aplica)
  │            ├─ vyntia-feature-supervisor
  │            ├─ vyntia-hr-tester
  │            ├─ vyntia-ui-modular
  │            └─ vyntia-code-quality
  │
  ├─ /vyntia-feature-check <módulo>   → invoca solo al supervisor
  ├─ /vyntia-test-hr <flujo>          → invoca solo al tester
  ├─ /vyntia-ui-audit <vista|módulo>  → invoca solo al ui-modular
  └─ /vyntia-quality <scope>          → invoca solo al code-quality

Cada agente escribe en:
  docs/agent-reports/{agente}/2026-05-22-{scope}.md

PM consume esos reportes + lanza nuevas corridas según necesite,
y entrega su reporte ejecutivo en:
  docs/agent-reports/pm/2026-05-22-{tema}.md
```

### Convención del formato de reporte (todos los agentes)

```markdown
# {Agente} — {Scope}

**Fecha:** YYYY-MM-DD
**Invocado por:** /vyntia-{cmd} {args}
**Confianza:** alta | media | baja
**Tiempo invertido:** ~Xmin

## Resumen ejecutivo
3–5 bullets máximo.

## Estado
| Item | Estado | Notas |
|------|--------|-------|
| ... | ✅ / ⚠️ / ❌ | ... |

## Hallazgos
### [SEV] Título corto
- **Dónde:** path:line
- **Qué:** descripción
- **Por qué importa:** impacto
- **Repro/evidencia:** comando o screenshot

## Acciones recomendadas
- [ ] CORTO PLAZO — …
- [ ] LARGO PLAZO — …

## Pregunta para humano (si aplica)
…
```

---

## Los 5 agentes

### 1. `vyntia-feature-supervisor`

**Misión:** Verificar que las features prometidas en specs y roadmap están implementadas y son alcanzables (ruta existe, vista renderiza, API responde sin 500, permisos correctos).

**No es** un tester de flujo completo — eso es del `hr-tester`. El supervisor mira **cobertura de la promesa**, no **corrección del comportamiento**.

**Inputs típicos:**
- `/vyntia-feature-check empleados` → audita todo el módulo Empleados contra B-spec
- `/vyntia-feature-check sub-proyecto-D` → audita feature flags de Pay según D-spec
- `/vyntia-feature-check` (sin args) → audita el último sub-proyecto cerrado

**Lo que hace:**
1. Lee la spec del scope (`docs/superpowers/specs/…`) o `ROADMAP_SUBPROJECTS.md`.
2. Para cada feature listado:
   - Grep de rutas en `apps/api/api/v1/**/urls.py` y `apps/web/src/**/router*.tsx`.
   - Grep de modelos/serializers esperados.
   - `manage.py check --settings=vyntia.settings.development` para validar el árbol.
   - `pytest -k <feature>` si hay tests asociados.
3. Marca ✅ / ⚠️ (existe pero incompleto) / ❌ (no existe).
4. Escribe reporte.

**Tools:** `Read, Grep, Glob, Bash` (solo `pytest`, `manage.py check`, `npm run build`).
**Conocimiento embebido:** estructura post-L3 (9 apps), convención de `APIResponse`, paginación estándar, ubicación de specs.

---

### 2. `vyntia-hr-tester`

**Misión:** Diseñar y ejecutar tests end-to-end con flujos reales de RRHH peruano. Es el agente con dominio de negocio.

**Conocimiento RRHH-PE embebido en el prompt:**
- Jornada legal (8h/día, 48h/sem), horas extra (25% primeras 2h, 35% siguientes).
- Vacaciones: 30 días por año (Ley 31188 acumulación máxima 2 años), record vacacional.
- Gratificaciones: julio y diciembre, bonificación extraordinaria 9%.
- CTS: mayo y noviembre, cálculo sobre remuneración computable.
- Régimen general vs MyPE (REMYPE).
- Planilla electrónica T-Registro / PLAME (SUNAT).
- Tipos de contrato peruanos: indefinido, plazo fijo, intermitente, locación de servicios, etc.

**Inputs típicos:**
- `/vyntia-test-hr contratar-empleado` → prueba flujo completo: crear empleado → asignar área → emitir contrato PDF → activar en planilla
- `/vyntia-test-hr vacaciones` → solicitar, aprobar, rechazar, validar acumulación
- `/vyntia-test-hr planilla-mensual` → cierre de mes con cálculo correcto

**Lo que hace:**
1. Lee el flujo target (o lo deriva de las B-spec/D-spec).
2. Diseña casos de prueba (golden path + bordes: empleado con vacaciones pendientes, contrato vencido, datos faltantes).
3. Ejecuta:
   - `pytest tests/` con marcadores específicos.
   - Si hay Playwright (`apps/web/playwright`), corre el suite relevante.
   - Si no hay test automatizado, propone uno y lo escribe.
4. Reporta casos pasados/fallidos con repro steps.

**Tools:** `Read, Write, Edit, Grep, Glob, Bash, chrome-devtools-mcp` (para inspección de UI cuando un flujo falla).
**Skills:** `django-rrhh`, `react-rrhh`, `pw:playwright-pro`.

---

### 3. `vyntia-ui-modular`

**Misión:** Auditar la UI con dos lentes:
1. **Diseño/UX** (consistencia con brand kit VYNTIA, accesibilidad, jerarquía visual).
2. **Modularidad comercial** — la decisión #3 del brainstorming: cada módulo debe poder activarse/desactivarse por tenant, la UI debe esconder lo no contratado, y guiar al upsell cuando se intenta tocar algo no disponible.

**Inputs típicos:**
- `/vyntia-ui-audit empleados` → audita módulo completo
- `/vyntia-ui-audit dashboard` → audita una vista
- `/vyntia-ui-audit feature-flags` → audita estado del sistema de flags

**Lo que hace:**
1. Carga la skill `frontend-design`.
2. Lee el módulo (`apps/web/src/features/{módulo}/`).
3. **Lente diseño:** consistencia con `vyntia_brand_ui.md`, uso correcto de tokens, jerarquía, micro-interacciones, estados vacíos/cargando/error.
4. **Lente modularidad:**
   - ¿Existe un feature flag por módulo? Grep de `FEATURE_FLAGS`, `useFeatureFlag`, `tenant.modules`.
   - ¿El sidebar/menu lo respeta? Lee `MenuService` (backend) y `menuService.ts` (frontend).
   - Si se navega a `/empleados` sin tener el módulo contratado → ¿muestra upgrade prompt o crashea?
   - ¿La nomenclatura es "módulo Empleados" o solo está mezclado con todo?
5. Reporta hallazgos + propone mockups si la mejora es visual.

**Tools:** `Read, Edit, Write, Grep, Glob, Bash` (`npm run dev` + `npm run build`), `chrome-devtools-mcp` para inspección visual.
**Skills:** `frontend-design`, `react-rrhh`, `chrome-devtools-mcp:a11y-debugging`.

---

### 4. `vyntia-code-quality`

**Misión:** Auditar el código por bugs latentes, deuda técnica, performance, seguridad. Clasifica hallazgos en **CORTO PLAZO** (refactor que cabe en este sprint) y **LARGO PLAZO** (decisiones arquitectónicas / próxima milestone).

**Inputs típicos:**
- `/vyntia-quality cambios-recientes` → revisa solo lo modificado desde el último merge a master
- `/vyntia-quality apps/payroll` → audita un app completo
- `/vyntia-quality deuda-tecnica` → barrido global por TODOs, FIXMEs, complejidad ciclomática alta, archivos > 500 líneas

**Lo que hace:**
1. Carga skills `django-rrhh`, `react-rrhh`, `code-reviewer`, `simplify`.
2. Corre linters: `ruff check`, `mypy`, `npx tsc --noEmit`, `npm run lint`.
3. Corre tests rápidos del scope: `pytest tests/<scope>/`.
4. Audita patrones conocidos del repo (Empleado→DatosLaborales para área, `Count('contrato_id')`, etc — ver CLAUDE.md).
5. Marca hallazgos por severidad (crítico/alto/medio/bajo) **y horizonte** (corto/largo).
6. **No aplica cambios automáticamente** — solo reporta. El humano decide qué se va a `/gsd-fast`, qué a un phase nuevo.

**Tools:** `Read, Grep, Glob, Bash` (linters y tests; **sin Edit/Write** para mantenerlo read-only).
**Skills:** `django-rrhh`, `react-rrhh`, `fullstack-dev-skills:code-reviewer`, `simplify`.

---

### 5. `vyntia-pm`

**Misión:** Orquestar a los 4 especialistas, agregar sus reportes, identificar tendencias, y proponer ajustes a la propia composición de agentes.

**Inputs típicos:**
- `/vyntia-pm` (sin args) → reporte ejecutivo del estado general (corre los 4 en paralelo)
- `/vyntia-pm audit empleados` → audita un módulo completo (los 4 sobre `empleados`)
- `/vyntia-pm bugs-vivos` → solo dispara feature-supervisor + hr-tester y consolida
- `/vyntia-pm afinar-agentes` → no dispara especialistas; lee últimos N reportes y propone tunes a los prompts

**Lo que hace:**
1. Decide qué especialistas correr según el input.
2. Los lanza con la herramienta `Agent` (en paralelo cuando son independientes).
3. Lee los reportes recién generados de `docs/agent-reports/*/`.
4. Sintetiza un reporte ejecutivo: top 5 hallazgos, módulos en riesgo, propuesta de próximos pasos.
5. **Auto-mejora:** si detecta que un agente reportó información poco útil o redundante, sugiere un cambio concreto a su prompt (en la sección "Pregunta para humano").

**Tools:** `Agent, Read, Write, Grep, Glob, TaskCreate, TaskUpdate, TaskList`.
**Sin Edit/Bash:** el PM no toca código directamente. Si necesita acción, delega.

---

## Slash commands

Todos viven en `.claude/commands/` y son thin-wrappers que invocan al agente correspondiente con instrucciones cortas.

| Comando | Argumentos | Agente disparado |
|---------|------------|------------------|
| `/vyntia-feature-check` | `[módulo o spec]` opcional | `vyntia-feature-supervisor` |
| `/vyntia-test-hr` | `<flujo>` | `vyntia-hr-tester` |
| `/vyntia-ui-audit` | `<vista o módulo>` | `vyntia-ui-modular` |
| `/vyntia-quality` | `<scope>` | `vyntia-code-quality` |
| `/vyntia-pm` | `[tema]` opcional | `vyntia-pm` (que a su vez dispara los otros 4) |

---

## Flujo de datos completo

```
1. Humano:   /vyntia-pm audit empleados
2. PM:       lanza en paralelo
             ├─ Agent(vyntia-feature-supervisor, "empleados")
             ├─ Agent(vyntia-hr-tester, "flujos clave de empleados")
             ├─ Agent(vyntia-ui-modular, "empleados")
             └─ Agent(vyntia-code-quality, "apps/employees + features/employees")
3. Cada especialista escribe su reporte en docs/agent-reports/{n}/2026-05-22-empleados.md
4. PM lee los 4 reportes, sintetiza, escribe:
   docs/agent-reports/pm/2026-05-22-empleados.md
5. PM retorna al humano:
   - Resumen ejecutivo en chat
   - Links a los 5 reportes
   - 3 acciones recomendadas priorizadas
   - 1 sugerencia opcional para afinar agentes
```

---

## Estructura de archivos a crear

```
.claude/
├── agents/
│   ├── vyntia-feature-supervisor.md
│   ├── vyntia-hr-tester.md
│   ├── vyntia-ui-modular.md
│   ├── vyntia-code-quality.md
│   └── vyntia-pm.md
└── commands/
    ├── vyntia-feature-check.md
    ├── vyntia-test-hr.md
    ├── vyntia-ui-audit.md
    ├── vyntia-quality.md
    └── vyntia-pm.md

docs/
└── agent-reports/
    ├── feature-supervisor/.gitkeep
    ├── hr-tester/.gitkeep
    ├── ui-modular/.gitkeep
    ├── code-quality/.gitkeep
    └── pm/.gitkeep
```

---

## Out of scope (explícitamente NO se hace en esta entrega)

- **Hooks automáticos** (post-commit, pre-push). Se descartó en pregunta #4: PM es reactivo.
- **Agentes haciendo Edit/Write de código de producción**. Los 4 especialistas son read-only sobre el código; solo el `hr-tester` puede escribir tests (`tests/` y `apps/web/playwright/`).
- **Dashboard web de reportes**. Por ahora son archivos `.md` revisables como PR. Si más adelante hace falta, se hace otro sub-proyecto.
- **Integración con Jira/Linear**. Los hallazgos quedan en markdown; el humano decide qué promover a issue.
- **Implementación del sistema de feature flags por tenant** propiamente. El `vyntia-ui-modular` lo **audita** pero la **construcción** del sistema de flags es un sub-proyecto aparte (probablemente parte de D o E).

---

## Testing del propio equipo de agentes

- **Smoke test inicial:** después de crear los 5 agentes, correr `/vyntia-pm` sin args en un repo limpio y validar que:
  1. Los 5 reportes se escriben en sus carpetas.
  2. Ningún agente edita archivos fuera de `docs/agent-reports/` y `tests/` (excepción del hr-tester).
  3. El reporte del PM agrega los otros 4 sin perder información clave.
- **Iteración:** primer `afinar-agentes` después de 1 semana de uso real.

---

## Decisiones técnicas que se asumieron sin preguntar (durante el "no stopping" mode)

| Asunción | Por qué |
|----------|---------|
| Cada agente recibe `tools:` específicas en su frontmatter | Para que el PM no pueda editar código y el code-quality no pueda mutar el repo — least privilege |
| Reports en `docs/` (no en `.planning/` ni `.claude/`) | Versionables, revisables en PR, visibles para humanos no técnicos del equipo |
| Una carpeta de reportes por agente, no un archivo único por día | Facilita encontrar histórico de un agente y permite que el PM lea solo lo que le interesa |
| Slash commands son thin-wrappers, no replican el prompt del agente | Si quiero cambiar el comportamiento, edito el `.md` del agente, no 5 lugares |
| Feature flags por tenant: solo se **audita**, no se construye en esta entrega | Para no inflar el scope; construir flags es un sub-proyecto |

---

## Self-review (post-escritura)

- [x] Placeholders / TODOs: ninguno
- [x] Consistencia interna: los 5 agentes y los 5 commands son coherentes en nombres
- [x] Scope: una sola entrega — crear los 10 archivos + estructura de carpetas. Implementación cabe en 1 phase.
- [x] Ambigüedades: cada agente tiene tools/skills/inputs/outputs explícitos
