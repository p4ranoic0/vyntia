---
description: Prueba un flujo de RRHH peruano (contratar, vacaciones, planilla, etc.) con conocimiento del dominio
argument-hint: "<flujo> (ej: contratar-empleado, vacaciones, planilla-mensual, gratificacion-julio)"
---

Invoca al agente `vyntia-hr-tester` para probar el flujo: **$ARGUMENTS**

Si `$ARGUMENTS` está vacío, pregunta al humano qué flujo quiere probar antes de lanzar el agente.

Lanza al agente con la herramienta `Agent` (subagent_type="vyntia-hr-tester") con un prompt que incluya:
- El flujo target
- Que diseñe casos golden + edge (con foco en normativa peruana cuando aplique)
- Que ejecute pytest / Playwright según corresponda
- Que escriba/edite tests faltantes en `apps/api/tests/` o `apps/web/playwright/`
- Que reporte en `docs/agent-reports/hr-tester/$(date +%Y-%m-%d)-{slug}.md`

Cuando termine, muéstrame el path del reporte y los casos que fallaron (si los hay).
