---
description: PM orquesta a los 4 especialistas VYNTIA (feature-supervisor, hr-tester, ui-modular, code-quality), agrega sus reportes y entrega un reporte ejecutivo con acciones priorizadas
argument-hint: "[tema] (ej: audit empleados, bugs-vivos, calidad, afinar-agentes — sin args = estado general)"
---

Invoca al agente `vyntia-pm` para gestionar: **$ARGUMENTS**

Si `$ARGUMENTS` está vacío, pídele un reporte ejecutivo del estado general del sub-proyecto activo (lee `docs/ROADMAP_SUBPROJECTS.md`).

Lanza al agente con la herramienta `Agent` (subagent_type="vyntia-pm") con un prompt que incluya:
- El tema/scope
- Que decida qué especialistas lanzar según la tabla en su prompt
- Que lance a los especialistas en paralelo con su propia herramienta `Agent`
- Que sintetice los reportes y escriba el suyo en `docs/agent-reports/pm/$(date +%Y-%m-%d)-{slug}.md`
- Que me devuelva: resumen 5-bullets, links a todos los reportes, 3 acciones priorizadas, y opcionalmente 1 sugerencia para tunear agentes

Cuando termine, muéstrame el resumen tal cual lo devolvió el PM.
