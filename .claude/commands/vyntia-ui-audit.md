---
description: Audita una vista / módulo VYNTIA con lente de diseño + lente de modularidad comercial (feature flags por tenant)
argument-hint: "<vista o módulo> (ej: empleados, dashboard, feature-flags)"
---

Invoca al agente `vyntia-ui-modular` para auditar el scope: **$ARGUMENTS**

Si `$ARGUMENTS` está vacío, audita el módulo del sub-proyecto activo según `docs/ROADMAP_SUBPROJECTS.md`.

Lanza al agente con la herramienta `Agent` (subagent_type="vyntia-ui-modular") con un prompt que incluya:
- El scope a auditar
- Que aplique las dos lentes: diseño (con skill frontend-design) y modularidad comercial (feature flags / hide-not-contracted / upsell prompts)
- Que reporte en `docs/agent-reports/ui-modular/$(date +%Y-%m-%d)-{slug}.md`

Cuando termine, muéstrame el path del reporte y los 3 hallazgos de mayor impacto.
