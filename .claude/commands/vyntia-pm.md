---
description: PM orquesta a los 4 especialistas VYNTIA (feature-supervisor, hr-tester, ui-modular, code-quality), agrega sus reportes y entrega un reporte ejecutivo con acciones priorizadas
argument-hint: "[tema] (ej: audit empleados, bugs-vivos, calidad, afinar-agentes — sin args = estado general)"
---

# /vyntia-pm — Audit ejecutivo de VYNTIA

**Tema/scope:** $ARGUMENTS

## Cómo ejecutar (instrucciones para ti, el main agent)

⚠️ **No invoques al agente `vyntia-pm` con la herramienta `Agent`.** Claude Code no permite que un sub-agente lance otros sub-agentes; el PM como sub-agente no puede delegar a los 4 especialistas (smoke test confirmado en `docs/agent-reports/pm/2026-05-22-smoke-test-status-general.md`). El patrón correcto es **tú (main agent) actúas como PM** siguiendo el playbook.

### Paso 1 — Carga el playbook

Lee `.claude/agents/vyntia-pm.md` y sigue sus instrucciones. Ese archivo es la fuente de verdad del rol PM (qué especialistas lanzar según el input, cómo lanzarlos, cómo sintetizar, formato del reporte).

### Paso 2 — Resuelve el scope

- Si `$ARGUMENTS` está vacío → reporte ejecutivo del estado general del sub-proyecto activo (lee `docs/ROADMAP_SUBPROJECTS.md` y `CLAUDE.md`).
- Si `$ARGUMENTS` es `audit <módulo>` → audit completo del módulo (los 4 especialistas en paralelo).
- Si `$ARGUMENTS` es `bugs-vivos` → solo feature-supervisor + hr-tester.
- Si `$ARGUMENTS` es `calidad` → solo code-quality + ui-modular.
- Si `$ARGUMENTS` es `afinar-agentes` → no lances especialistas; lee últimos N reportes en `docs/agent-reports/*/` y propone tunes a los `.md` de los agentes.

### Paso 3 — Mini-reconnaissance

Antes de lanzar especialistas, haz un `ls`/`Glob` rápido del scope para enumerar paths concretos (pages, models, views). Pasarás esos paths en los prompts de los especialistas — prompts precisos producen mejores reportes.

### Paso 4 — Lanza a los especialistas EN PARALELO

Usa la herramienta `Agent` con varios tool calls en un solo mensaje. Cada prompt debe incluir:
- Scope con paths concretos
- Restricciones (read-only / no escribir tests / etc.)
- Baseline a no regresar
- Ruta exacta donde debe persistir el reporte: `docs/agent-reports/{agente}/$(date +%Y-%m-%d)-{scope}.md`

### Paso 5 — Verifica persistencia + Sintetiza

- Verifica que cada especialista escribió su reporte en disco. Si alguno solo devolvió inline, persístelo tú con `Write` al archivo esperado (y regístralo como tune-up).
- Escribe tu reporte PM en `docs/agent-reports/pm/$(date +%Y-%m-%d)-{slug}.md`.

### Paso 6 — Responde en chat

Devuélveme:
- Resumen 5-bullets (puedes pasarte si hay verdicts duales)
- Links a TODOS los reportes (4 especialistas + PM)
- 3 acciones priorizadas (con horizonte CORTO/MEDIO/LARGO)
- Opcional: 1 sugerencia para tunear agentes si detectaste algún patrón (pregunta `¿Aplico el tune?`)
