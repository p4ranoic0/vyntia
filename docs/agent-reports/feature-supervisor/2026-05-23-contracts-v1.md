# Feature Supervisor — CONTRACTS (v1)

**Fecha:** 2026-05-23
**Invocado por:** /vyntia-feature-check contracts (pre-D readiness audit)
**Spec consultada:** `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md` (B.5/B.10/B.11/B.14) + `docs/superpowers/summaries/2026-05-19-vyntia-B-vyntia-core-summary.md`
**Confianza:** alta (cobertura estructural verificada; sin runtime contra BD por bug local utf-8 documentado)
**Tiempo invertido:** ~18min

## Resumen ejecutivo
- **Veredicto: 🟢 VERDE** — módulo contracts completo y alcanzable. Sin bloqueadores para iniciar D.
- 7 features auditadas: **7 ✅ / 1 ⚠️ (sub-feature) / 0 ❌**
- `manage.py check`: **0 issues (0 silenced)** ✅
- `makemigrations contracts --dry-run --check`: **No changes detected** (sin migraciones pendientes) ✅
- Las 7 rutas backend registradas + 5 rutas frontend en App.tsx + 6 entradas de menú seedeadas (`seed_menu.py`).
- 12 archivos de tests en `apps/contracts/tests/` (B.10/B.11/B.14 + polish).
- **Único hallazgo (no bloqueante):** endpoint `/contract-amendments/` (CRUD) registrado pero sin consumidor frontend; las adendas se crean vía generación PDF (`generar-adenda`), no vía el endpoint CRUD.

## Estado por feature
| Feature | Backend | Frontend | Permiso | Tests | Estado |
|---------|---------|----------|---------|-------|--------|
| Contract CRUD + renovación + tipos (rég. 728/CAS/276) | ✅ ContratosAdendasViewSet | ✅ ContratosPage (1269 ln) | ✅ TenantAware + RRHH | ✅ test_contratos_polish | ✅ |
| ContractAmendment (adendas) | ✅ ContractAmendmentViewSet | ⚠️ sin consumidor CRUD; solo PDF generar-adenda | ✅ | ✅ | ⚠️ |
| EmploymentData (datos laborales, FK área) | ✅ DatosLaboralesViewSet + FK area | ✅ (via empleados) | ✅ | ✅ | ✅ |
| TRegistroDeclaration: alta/baja/modificación | ✅ TRegistroDeclarationViewSet (8 actions) | ✅ TRegistroListPage | ✅ RRHHPermission | ✅ test_b10_* | ✅ |
| ProbationPeriod (período de prueba por régimen) | ✅ ProbationPeriodViewSet (5 actions) | ✅ ProbationPeriodListPage | ✅ RRHHPermission | ✅ test_b11_* | ✅ |
| SeveranceSettlement (liquidación ADR-B.9) | ✅ SeveranceSettlementViewSet (compute/mark-paid) | ✅ SeveranceSettlementListPage | ✅ RRHHPermission | ✅ test_b14_severance* | ✅ |
| Termination (cese) | ✅ TerminationViewSet (initiate/complete/liquidate/cancel) | ✅ TerminationListPage | ✅ RRHHPermission | ✅ test_b14_termination* | ✅ |

## Hallazgos detallados

### [⚠️] ContractAmendment CRUD sin consumidor frontend
- **Dónde:** ruta `api/v1/contracts/urls.py:22` (`router.register(r"contract-amendments", ContractAmendmentViewSet)`); FE `apps/web/src/features/contracts/services/contractsService.ts` solo invoca `/api/v1/documents/documents/generar-adenda/` (línea 321).
- **Qué falta:** no hay service/page frontend que consuma `/api/v1/contract-amendments/` (GET/POST/PATCH). Las adendas se crean exclusivamente por el flujo de generación PDF.
- **Por qué importa:** D (Vyntia Pay) consume `Contract` + `EmploymentData`, no la lista CRUD de adendas — impacto bajo para D. Pero el endpoint queda "huérfano" en superficie HTTP: existe, responde, sin UI que lo use. Riesgo: drift entre modelo adenda y datos que Pay lea.
- **Evidencia:** `grep -rln "contract-amendments|ContractAmendment" apps/web/src/` → 0 resultados.

### [Nota positiva — relevante para D] Régimen 728 y tipos de contrato completos
- **Dónde:** `apps/api/apps/contracts/models/contract.py:34-37,260,267`.
- Cubre `LEY_728_FIJO`, `LEY_728_FIJO_SUPLENCIA`, `LEY_728_INDETERMINADO`, además de CAS y Ley 276; clasificación determinado/indeterminado lista para cálculo de planilla en D.

### [Nota — manejo de errores correcto]
- Todos los viewsets (`views.py`, `probation_views.py`, `termination_views.py`) envuelven excepciones de servicio en `APIResponse.error(... status_code=400)`; no se filtran 500. Initiate-termination y compute-settlement validan FK con 404 explícito.

### [Nota — legacy contratos_views VIVO, no deprecado]
- `api/v1/rrhh/contratos_views.py` provee `ContratosAdendasViewSet` (Contract CRUD + `renovar_contrato` línea 366 + `alertas_vencimiento` + `estadisticas`) y `ContractAmendmentViewSet`. La urls.py "nueva" de contracts los importa y reexpone bajo `/api/v1/contracts/`. NO está muerto — es la fuente real del CRUD de contratos. Cualquier refactor en D debe respetarlo.

## Acciones recomendadas
- [ ] CORTO — Decidir si `/contract-amendments/` CRUD necesita UI o debe deprecarse/documentarse como API-only (evita endpoint huérfano antes de D).
- [ ] CORTO (antes de D) — Confirmar que `SeveranceSettlement` (4 componentes legales B.9: CTS + vac_truncas + grat_trunca + indemnización) expone su contrato de datos estable; D extenderá, no reimplementará (ADR-B.9 / RB7).
- [ ] LARGO — Versionado de Contract (ADR-B.7 abierto: inline `replaces` FK vs django-simple-history). D leerá historial de contratos para retro-cálculo; resolver antes de planilla retroactiva.

## Pregunta para humano
- ¿El endpoint `/contract-amendments/` debe tener UI propia en este sub-proyecto, o se acepta como API-only consumida solo por automatizaciones/generación documental? (Define si el ⚠️ se cierra como diseño o como gap.)

---
**Baseline preservada (read-only audit):** no se ejecutó suite completa; `manage.py check` 0 issues, `makemigrations --check` sin pendientes. No se modificó código de producto.
