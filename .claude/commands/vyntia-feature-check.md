---
description: Audita qué features de un módulo / sub-proyecto VYNTIA están realmente implementadas vs lo prometido en la spec
argument-hint: "[módulo o spec — opcional, default: último sub-proyecto cerrado]"
---

Invoca al agente `vyntia-feature-supervisor` para auditar el scope: **$ARGUMENTS**

Si `$ARGUMENTS` está vacío, usa como scope el último sub-proyecto marcado COMPLETE en `docs/ROADMAP_SUBPROJECTS.md`.

Lanza al agente con la herramienta `Agent` (subagent_type="vyntia-feature-supervisor") con un prompt auto-contenido que incluya:
- El scope a auditar
- La ruta a la spec relevante en `docs/superpowers/specs/`
- Que escriba su reporte en `docs/agent-reports/feature-supervisor/$(date +%Y-%m-%d)-{slug}.md`

Cuando termine, muéstrame el path del reporte y un resumen de 3 bullets.
