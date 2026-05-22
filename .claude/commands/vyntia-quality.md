---
description: Audita calidad de código VYNTIA — bugs latentes, deuda, performance, seguridad. Clasifica por severidad y horizonte (corto/largo plazo)
argument-hint: "<scope> (ej: cambios-recientes, apps/payroll, deuda-tecnica)"
---

Invoca al agente `vyntia-code-quality` para auditar el scope: **$ARGUMENTS**

Si `$ARGUMENTS` está vacío, usa `cambios-recientes` (git diff master).

Lanza al agente con la herramienta `Agent` (subagent_type="vyntia-code-quality") con un prompt que incluya:
- El scope a auditar
- Que corra ruff, mypy, tsc, eslint y pytest del scope
- Que compare contra los baselines en CLAUDE.md (982 pytest passed, 178 vitest, 1 tsc error, ≤278 eslint warnings)
- Que clasifique cada hallazgo por severidad (crítico/alto/medio/bajo) Y horizonte (corto/largo plazo)
- Que reporte en `docs/agent-reports/code-quality/$(date +%Y-%m-%d)-{slug}.md`

Cuando termine, muéstrame el path del reporte, las regresiones (si las hay) y los hallazgos críticos de corto plazo.
