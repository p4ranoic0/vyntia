# VYNTIA Foundation L3.10.4b — Frontend URL Refactor (consume English paths) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate todas las llamadas API en el frontend de las URLs legacy `/api/v1/rrhh/...` y `/api/v1/vacaciones/...` a las nuevas URLs canónicas en inglés agregadas por L3.10.4a (`/api/v1/employees/`, `/api/v1/identity/users/`, `/api/v1/payroll/...`, `/api/v1/time-off/...`, etc.). Después de este plan, las URLs legacy quedan sin uso desde el frontend — listas para ser eliminadas en L3.11.

**Architecture:** Frontend-only refactor. Reemplaza strings de URL en 19 archivos TS/TSX (services, lib/api.ts, pages, features/onboarding). NO toca componentes UI más allá de cambiar URL strings; NO renombra campos (`empleado_id`, `fecha_creacion`); NO renombra archivos service (`contratosService.ts` queda igual). Los ViewSets backend son los mismos — solo cambia el path. Custom actions en URLs (`/renovar_contrato/`, `/mi-onboarding/`, `/aprobar_planilla/`, `/reporte_integral/`) se preservan tal cual están: viven sobre el viewset y siguen accesibles vía la nueva URL base.

**Tech Stack:** React 18, TypeScript, axios via `apiClient` (alias de `axios.create()` en `lib/api.ts`), Vite proxy a `/api/*` → `http://127.0.0.1:8000/`.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.4 "URL structure resultante".

**Pre-condiciones:**
- L3.10.4a mergeada a master (commit `4aeee01e` — "Merge L3.10.4a: backend URL refactor (English paths in parallel)")
- Backend respondiendo en URLs nuevas — verificable con `manage.py check` y smoke test
- Frontend baseline vitest: **7 passed, 1 file load-failure** (Playwright e2e captured by vitest, pre-existing config bug)
- Frontend `npm run build` debe pasar
- venv activo en `D:/VYNTIA/.venv/`

**Scope decision (sub-PR de L3.10.4):**
- L3.10.4a ✅ Backend URL refactor (English paths in parallel, legacy preserved)
- **L3.10.4b (este plan)** — Frontend URL refactor: consume URLs nuevas
- L3.10.4c ⏳ Frontend field rename (`empleado_id → id`, `fecha_creacion → created_at`, `creado_por → created_by`)
- L3.10.4d ⏳ Frontend file renames (`contratosService.ts → contractsService.ts`, etc.)
- L3.11 ⏳ Cleanup — remueve URLs legacy de `api/v1/rrhh/urls.py` y `api/v1/vacaciones/urls.py` + carpeta vacía `app_rrhh/`

**Out of scope (NO hacer en L3.10.4b):**
- Renombrar TS interfaces o fields (`empleado_id`, `fecha_creacion`, `nombres_empleado`) — eso es L3.10.4c
- Renombrar archivos service (`contratosService.ts`, `areasService.ts`) — eso es L3.10.4d
- Tocar `apps/web/src/generated/api/services/*.ts` — generado por OpenAPI codegen; se regenera del schema en una tarea separada (potencialmente L3.10.4c o más adelante)
- Tocar legacy URLs `/api/v1/rrhh/...` en backend — eso es L3.11

---

## Tabla canónica URL legacy → URL nueva

Esta tabla es la fuente de verdad para todos los reemplazos. Confirmada contra `apps/api/api/v1/{identity,organization,employees,contracts,documents,payroll,time_off,onboarding}/urls.py` mergeados en L3.10.4a.

### identity (mounted at `/api/v1/identity/`)
| Legacy | Nueva |
|---|---|
| `/api/v1/rrhh/usuarios/` | `/api/v1/identity/users/` |
| `/api/v1/rrhh/usuarios/${id}/` | `/api/v1/identity/users/${id}/` |
| `/api/v1/rrhh/usuarios/${id}/change-password/` | `/api/v1/identity/users/${id}/change-password/` |
| `/api/v1/rrhh/usuarios/${id}/asignar_rol/` | `/api/v1/identity/users/${id}/asignar_rol/` |
| `/api/v1/rrhh/usuarios/${id}/remover_rol/` | `/api/v1/identity/users/${id}/remover_rol/` |
| `/api/v1/rrhh/usuarios/sin_login_reciente/` | `/api/v1/identity/users/sin_login_reciente/` |
| `/api/v1/rrhh/usuarios/estadisticas/` | `/api/v1/identity/users/estadisticas/` |
| `/api/v1/rrhh/roles/` | `/api/v1/identity/roles/` |
| `/api/v1/rrhh/roles/${id}/` | `/api/v1/identity/roles/${id}/` |
| `/api/v1/rrhh/roles/activos/` | `/api/v1/identity/roles/activos/` |
| `/api/v1/rrhh/permisos/` | `/api/v1/identity/permissions/` |
| `/api/v1/rrhh/permisos/${id}/` | `/api/v1/identity/permissions/${id}/` |
| `/api/v1/rrhh/modules/` | `/api/v1/identity/modules/` |
| `/api/v1/rrhh/modules/${id}/` | `/api/v1/identity/modules/${id}/` |
| `/api/v1/rrhh/role-permissions/` | `/api/v1/identity/role-permissions/` |
| `/api/v1/rrhh/rol-permisos/` | `/api/v1/identity/role-permissions/` |
| `/api/v1/rrhh/rol-permisos/${id}/` | `/api/v1/identity/role-permissions/${id}/` |
| `/api/v1/rrhh/rol-permisos/por_rol/` | `/api/v1/identity/role-permissions/por_rol/` |
| `/api/v1/rrhh/usuario-roles/` | `/api/v1/identity/user-roles/` |
| `/api/v1/rrhh/usuario-roles/asignar_multiple/` | `/api/v1/identity/user-roles/asignar_multiple/` |
| `/api/v1/rrhh/usuario-roles/buscar_usuarios_por_roles/` | `/api/v1/identity/user-roles/buscar_usuarios_por_roles/` |

### organization (mounted at `/api/v1/organization/`)
| Legacy | Nueva |
|---|---|
| `/api/v1/rrhh/areas/` | `/api/v1/organization/departments/` |
| `/api/v1/rrhh/areas/${id}/` | `/api/v1/organization/departments/${id}/` |
| `/api/v1/rrhh/areas/stats/` | `/api/v1/organization/departments/stats/` |
| `/api/v1/rrhh/areas/${areaId}/empleados/` | `/api/v1/organization/departments/${areaId}/empleados/` |
| `/api/v1/rrhh/areas/${areaId}/empleados/${empleadoId}/` | `/api/v1/organization/departments/${areaId}/empleados/${empleadoId}/` |
| `/api/v1/rrhh/areas/hierarchy/` | `/api/v1/organization/departments/hierarchy/` |
| `/api/v1/rrhh/areas/${areaId}/children/` | `/api/v1/organization/departments/${areaId}/children/` |
| `/api/v1/rrhh/areas/${areaId}/parent/` | `/api/v1/organization/departments/${areaId}/parent/` |
| `/api/v1/rrhh/areas/${areaId}/history/` | `/api/v1/organization/departments/${areaId}/history/` |
| `/api/v1/rrhh/areas/report/` | `/api/v1/organization/departments/report/` |
| `/api/v1/rrhh/areas/export/` | `/api/v1/organization/departments/export/` |
| `/api/v1/rrhh/areas/search/` | `/api/v1/organization/departments/search/` |
| `/api/v1/rrhh/areas/validate-siglas/` | `/api/v1/organization/departments/validate-siglas/` |
| `/api/v1/rrhh/areas/validate/` | `/api/v1/organization/departments/validate/` |
| `/api/v1/rrhh/areas/bulk-update/` | `/api/v1/organization/departments/bulk-update/` |
| `/api/v1/rrhh/areas/bulk-delete/` | `/api/v1/organization/departments/bulk-delete/` |
| `/api/v1/rrhh/areas/metadata/` | `/api/v1/organization/departments/metadata/` |
| `/api/v1/rrhh/configuracion-empresa/` | `/api/v1/organization/companies/` |

### employees (mounted FLAT under `/api/v1/`)
| Legacy | Nueva |
|---|---|
| `/api/v1/rrhh/empleados/` | `/api/v1/employees/` |
| `/api/v1/rrhh/empleados/${id}/` | `/api/v1/employees/${id}/` |
| `/api/v1/rrhh/empleados/${id}/reporte_integral/` | `/api/v1/employees/${id}/reporte_integral/` |
| `/api/v1/rrhh/empleados/${id}/reporte_seccion/` | `/api/v1/employees/${id}/reporte_seccion/` |
| `/api/v1/rrhh/datos-familiares/` | `/api/v1/family-members/` |
| `/api/v1/rrhh/datos-familiares/${id}/` | `/api/v1/family-members/${id}/` |
| `/api/v1/rrhh/datos-academicos/` | `/api/v1/academic-records/` |
| `/api/v1/rrhh/datos-academicos/${id}/` | `/api/v1/academic-records/${id}/` |
| `/api/v1/rrhh/cursos-certificaciones/` | `/api/v1/certifications/` |
| `/api/v1/rrhh/cursos-certificaciones/${id}/` | `/api/v1/certifications/${id}/` |

### contracts (mounted FLAT under `/api/v1/`)
| Legacy | Nueva |
|---|---|
| `/api/v1/rrhh/contratos-adendas/` | `/api/v1/contracts/` |
| `/api/v1/rrhh/contratos-adendas/${id}/` | `/api/v1/contracts/${id}/` |
| `/api/v1/rrhh/contratos-adendas/estadisticas/` | `/api/v1/contracts/estadisticas/` |
| `/api/v1/rrhh/contratos-adendas/alertas_vencimiento/` | `/api/v1/contracts/alertas_vencimiento/` |
| `/api/v1/rrhh/contratos-adendas/${id}/renovar_contrato/` | `/api/v1/contracts/${id}/renovar_contrato/` |
| `/api/v1/rrhh/datos-laborales/` | `/api/v1/employment-data/` |
| `/api/v1/rrhh/datos-laborales/${id}/` | `/api/v1/employment-data/${id}/` |

### documents (mounted at `/api/v1/documents/`)
**Nota importante:** El backend monta el router de `DocumentosDigitalesViewSet` (registrado bajo `r"documents"`) DENTRO del prefix `/api/v1/documents/`, lo que produce el path `/api/v1/documents/documents/` — doble "documents". Mismo doble prefix aplica a las function-based views de generación. Esto fue verificado con smoke test en L3.10.4a.

| Legacy | Nueva |
|---|---|
| `/api/v1/rrhh/documentos-digitales/` | `/api/v1/documents/documents/` |
| `/api/v1/rrhh/documentos-digitales/${id}/` | `/api/v1/documents/documents/${id}/` |
| `/api/v1/rrhh/documentos-digitales/${id}/validar/` | `/api/v1/documents/documents/${id}/validar/` |
| `/api/v1/rrhh/documentos-digitales/${id}/rechazar/` | `/api/v1/documents/documents/${id}/rechazar/` |
| `/api/v1/rrhh/documentos-digitales/subir_institucional/` | `/api/v1/documents/documents/subir_institucional/` |
| `/api/v1/rrhh/documentos/generar-contrato/` | `/api/v1/documents/documents/generar-contrato/` |
| `/api/v1/rrhh/documentos/generar-adenda/` | `/api/v1/documents/documents/generar-adenda/` |
| `/api/v1/rrhh/documentos/generar-certificado/` | `/api/v1/documents/documents/generar-certificado/` |
| `/api/v1/rrhh/documentos/plantillas-word/` | `/api/v1/documents/documents/plantillas-word/` |
| `/api/v1/rrhh/documentos/plantillas-word/subir/` | `/api/v1/documents/documents/plantillas-word/subir/` |
| `/api/v1/rrhh/documentos/plantillas-word/${id}/eliminar/` | `/api/v1/documents/documents/plantillas-word/${id}/eliminar/` |
| `/api/v1/rrhh/documentos/plantillas-word/${id}/descargar/` | `/api/v1/documents/documents/plantillas-word/${id}/descargar/` |
| `/api/v1/rrhh/documentos/generar-desde-plantilla-word/` | `/api/v1/documents/documents/generar-desde-plantilla-word/` |

### payroll (mounted at `/api/v1/payroll/`)
| Legacy | Nueva |
|---|---|
| `/api/v1/rrhh/configuracion-remuneraciones/` | `/api/v1/payroll/compensation-configurations/` |
| `/api/v1/rrhh/configuracion-remuneraciones/${id}/` | `/api/v1/payroll/compensation-configurations/${id}/` |
| `/api/v1/rrhh/configuracion-afp/` | `/api/v1/payroll/afp-configurations/` |
| `/api/v1/rrhh/configuracion-afp/${id}/` | `/api/v1/payroll/afp-configurations/${id}/` |
| `/api/v1/rrhh/configuracion-uit/` | `/api/v1/payroll/tax-parameters/` |
| `/api/v1/rrhh/configuracion-uit/${id}/` | `/api/v1/payroll/tax-parameters/${id}/` |
| `/api/v1/rrhh/configuracion-uit/${id}/activar/` | `/api/v1/payroll/tax-parameters/${id}/activar/` |
| `/api/v1/rrhh/planillas-mensuales/` | `/api/v1/payroll/monthly-runs/` |
| `/api/v1/rrhh/planillas-mensuales/${id}/` | `/api/v1/payroll/monthly-runs/${id}/` |
| `/api/v1/rrhh/planillas-mensuales/${id}/generar_planilla/` | `/api/v1/payroll/monthly-runs/${id}/generar_planilla/` |
| `/api/v1/rrhh/planillas-mensuales/${id}/regenerar/` | `/api/v1/payroll/monthly-runs/${id}/regenerar/` |
| `/api/v1/rrhh/planillas-mensuales/${id}/calcular_planilla/` | `/api/v1/payroll/monthly-runs/${id}/calcular_planilla/` |
| `/api/v1/rrhh/planillas-mensuales/${id}/preview/` | `/api/v1/payroll/monthly-runs/${id}/preview/` |
| `/api/v1/rrhh/planillas-mensuales/${id}/aprobar_planilla/` | `/api/v1/payroll/monthly-runs/${id}/aprobar_planilla/` |
| `/api/v1/rrhh/planillas-mensuales/${id}/estadisticas/` | `/api/v1/payroll/monthly-runs/${id}/estadisticas/` |
| `/api/v1/rrhh/planillas-mensuales/${id}/generar_boletas/` | `/api/v1/payroll/monthly-runs/${id}/generar_boletas/` |
| `/api/v1/rrhh/detalles-planilla/` | `/api/v1/payroll/details/` |
| `/api/v1/rrhh/detalles-planilla/${id}/` | `/api/v1/payroll/details/${id}/` |
| `/api/v1/rrhh/descuentos-masivos/` | `/api/v1/payroll/mass-deductions/` |
| `/api/v1/rrhh/descuentos-masivos/${id}/` | `/api/v1/payroll/mass-deductions/${id}/` |
| `/api/v1/rrhh/descuentos-masivos/${id}/procesar/` | `/api/v1/payroll/mass-deductions/${id}/procesar/` |
| `/api/v1/rrhh/descuentos-masivos/${id}/anular/` | `/api/v1/payroll/mass-deductions/${id}/anular/` |
| `/api/v1/rrhh/boletas-pago/` | `/api/v1/payroll/payslips/` |
| `/api/v1/rrhh/boletas-pago/${id}/` | `/api/v1/payroll/payslips/${id}/` |
| `/api/v1/rrhh/boletas-pago/${id}/pdf/` | `/api/v1/payroll/payslips/${id}/pdf/` |
| `/api/v1/rrhh/boletas-pago/descarga-masiva/` | `/api/v1/payroll/payslips/descarga-masiva/` |
| `/api/v1/rrhh/calendarios-pago/` | `/api/v1/payroll/payment-schedules/` |
| `/api/v1/rrhh/calendarios-pago/${id}/` | `/api/v1/payroll/payment-schedules/${id}/` |

### time-off (mounted at `/api/v1/time-off/`)
| Legacy | Nueva |
|---|---|
| `/api/v1/vacaciones/configuraciones/` | `/api/v1/time-off/configurations/` |
| `/api/v1/vacaciones/configuraciones/${id}/` | `/api/v1/time-off/configurations/${id}/` |
| `/api/v1/vacaciones/periodos/` | `/api/v1/time-off/periods/` |
| `/api/v1/vacaciones/periodos/${id}/` | `/api/v1/time-off/periods/${id}/` |
| `/api/v1/vacaciones/periodos/generar-masivo/` | `/api/v1/time-off/periods/generar-masivo/` |
| `/api/v1/vacaciones/periodos/${id}/ajustar-dias/` | `/api/v1/time-off/periods/${id}/ajustar-dias/` |
| `/api/v1/vacaciones/solicitudes/` | `/api/v1/time-off/requests/` |
| `/api/v1/vacaciones/solicitudes/${id}/` | `/api/v1/time-off/requests/${id}/` |
| `/api/v1/vacaciones/solicitudes/${id}/enviar/` | `/api/v1/time-off/requests/${id}/enviar/` |
| `/api/v1/vacaciones/solicitudes/${id}/aprobar-jefe/` | `/api/v1/time-off/requests/${id}/aprobar-jefe/` |
| `/api/v1/vacaciones/solicitudes/${id}/aprobar-rrhh/` | `/api/v1/time-off/requests/${id}/aprobar-rrhh/` |
| `/api/v1/vacaciones/solicitudes/${id}/cancelar/` | `/api/v1/time-off/requests/${id}/cancelar/` |
| `/api/v1/vacaciones/solicitudes/pendientes-rrhh/` | `/api/v1/time-off/requests/pendientes-rrhh/` |
| `/api/v1/vacaciones/solicitudes/pendientes-jefe/` | `/api/v1/time-off/requests/pendientes-jefe/` |
| `/api/v1/vacaciones/solicitudes/mis-solicitudes/` | `/api/v1/time-off/requests/mis-solicitudes/` |
| `/api/v1/vacaciones/goces/` | `/api/v1/time-off/grants/` |
| `/api/v1/vacaciones/goces/${id}/` | `/api/v1/time-off/grants/${id}/` |
| `/api/v1/vacaciones/historial/` | `/api/v1/time-off/history/` |
| `/api/v1/vacaciones/reportes/estadisticas/` | `/api/v1/time-off/reports/estadisticas/` |
| `/api/v1/vacaciones/reportes/dias-vencidos/` | `/api/v1/time-off/reports/dias-vencidos/` |

### onboarding (mounted at `/api/v1/onboarding/`)
| Legacy | Nueva |
|---|---|
| `/api/v1/rrhh/onboarding/` | `/api/v1/onboarding/processes/` |
| `/api/v1/rrhh/onboarding/${id}/` | `/api/v1/onboarding/processes/${id}/` |
| `/api/v1/rrhh/onboarding/mi-onboarding/` | `/api/v1/onboarding/processes/mi-onboarding/` |
| `/api/v1/rrhh/onboarding/${id}/validar/` | `/api/v1/onboarding/processes/${id}/validar/` |
| `/api/v1/rrhh/onboarding/${id}/reenviar_email/` | `/api/v1/onboarding/processes/${id}/reenviar_email/` |
| `/api/v1/rrhh/onboarding/${id}/actualizar-estado/` | `/api/v1/onboarding/processes/${id}/actualizar-estado/` |
| `/api/v1/rrhh/onboarding/subir-foto/` | `/api/v1/onboarding/processes/subir-foto/` |
| `/api/v1/rrhh/onboarding/subir-documento/` | `/api/v1/onboarding/processes/subir-documento/` |
| `/api/v1/rrhh/onboarding/${id}/corregir-correo/` | `/api/v1/onboarding/processes/${id}/corregir-correo/` |
| `/api/v1/rrhh/onboarding/${id}/documentos/${docId}/aprobar/` | `/api/v1/onboarding/processes/${id}/documentos/${docId}/aprobar/` |
| `/api/v1/rrhh/onboarding/${id}/documentos/${docId}/rechazar/` | `/api/v1/onboarding/processes/${id}/documentos/${docId}/rechazar/` |

### auth (sin cambios — preserved)
`/api/v1/auth/login/`, `/api/v1/auth/logout/`, `/api/v1/auth/forgot-password/`, `/api/v1/auth/reset-password/`, `/api/v1/auth/change-password/` — NO se tocan.

---

## File Structure Overview

| Acción | Path | Refs aprox |
|---|---|---|
| Modify | `apps/web/src/lib/api.ts` | 21 |
| Modify | `apps/web/src/services/areasService.ts` | 23 |
| Modify | `apps/web/src/services/contratosService.ts` | 10 |
| Modify | `apps/web/src/services/employeesService.ts` | 19 |
| Modify | `apps/web/src/services/empresaService.ts` | 3 |
| Modify | `apps/web/src/services/legajoService.ts` | 7 |
| Modify | `apps/web/src/services/onboardingService.ts` | 7 |
| Modify | `apps/web/src/services/plantillasService.ts` | 5 |
| Modify | `apps/web/src/services/remuneracionesService.ts` | 47 |
| Modify | `apps/web/src/services/securityService.ts` | 12 |
| Modify | `apps/web/src/services/usersService.ts` | 21 |
| Modify | `apps/web/src/services/vacacionesService.ts` | 29 |
| Modify | `apps/web/src/features/onboarding/services/onboardingDataService.ts` | 12 |
| Modify | `apps/web/src/features/onboarding/services/onboardingUploadService.ts` | 4 |
| Modify | `apps/web/src/features/onboarding/services/__tests__/onboardingUploadService.test.ts` | 1 |
| Modify | `apps/web/src/features/onboarding/pages/OnboardingEmployeePage.tsx` | 2 |
| Modify | `apps/web/src/features/onboarding/components/OnboardingTabPersonal.tsx` | 1 |
| Modify | `apps/web/src/pages/HROverviewDashboard.tsx` | 4 |
| Modify | `apps/web/src/pages/onboarding/OnboardingAdminPage.tsx` | 2 |

**Total:** 19 archivos modificados, ~230 referencias de URL reemplazadas.

**NO se toca:**
- `apps/web/src/generated/api/services/*.ts` — auto-generado por OpenAPI codegen, se regenera del schema actualizado en una tarea separada (probablemente L3.10.4c)
- TS interfaces, fields, ni nombres de archivo
- `apps/web/src/services/authService.ts` — no usa URLs legacy (todas son `/api/v1/auth/...`, preservadas)
- `apps/web/src/services/normalizers/rrhhNormalizers.ts` — el nombre tiene "rrhh" pero el archivo no contiene URLs (es lógica de normalización), queda igual; se renombrará en L3.10.4d
- `apps/web/src/services/menuService.ts` — no usa URLs legacy

---

## Definition of Done

- [ ] 19 archivos modificados — todas las URLs legacy reemplazadas por las nuevas English paths
- [ ] `grep -rn "/api/v1/rrhh\|/api/v1/vacaciones" apps/web/src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated` retorna **0 matches**
- [ ] `npm run lint` clean (no nuevos warnings/errors)
- [ ] `npm run build` produce un bundle exitoso (artifact en `apps/web/dist/`)
- [ ] `npm test` (vitest) preserva baseline: **7 passed, 1 file load-failure** (Playwright capture)
- [ ] Smoke test runtime: dev server `npm run dev` arranca; `/api/v1/employees/`, `/api/v1/identity/users/`, `/api/v1/payroll/monthly-runs/`, `/api/v1/time-off/requests/` responden 401 con backend `runserver` corriendo en background
- [ ] `manage.py check` clean (backend no afectado)
- [ ] Backend pytest baseline: **161 passed, 8 failed, 3 skipped** (no se tocó backend, debe estar idéntico)
- [ ] Branch `vyntia/L3.10.4b-frontend-url-refactor` mergeada a master con `--no-ff`
- [ ] Roadmap (`docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`) actualizado: L3.10.4b ✅, L3.10.4c (frontend field rename) NEXT
- [ ] Memory `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md` actualizado

---

## Task 1: Pre-flight — branch, baseline, snapshot

- [ ] **Step 1: Confirmar pwd y master limpio post-L3.10.4a**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -5
```

Expected: HEAD = `f0e826ea docs(L3.10.4a): mark L3.10.4a merged, L3.10.4b (frontend rename) as next` o más reciente. `git status` shows ONLY plan file untracked (este plan recién creado).

- [ ] **Step 2: Confirmar backend funcional con URLs nuevas**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 3: Confirmar frontend baseline build**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -10
cd D:/VYNTIA
```

Expected: build exitosa (output `dist/` generado, sin errores TypeScript fatales).

- [ ] **Step 4: Confirmar frontend baseline tests**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | tail -10
cd D:/VYNTIA
```

Expected: `7 passed`. 1 file load-failure (`onboardingUploadService.test.ts` o similar) — pre-existing, no regresar.

- [ ] **Step 5: Snapshot of legacy URL count**

```bash
cd D:/VYNTIA/apps/web
echo "=== Refs to /api/v1/rrhh/ (excluding generated) ==="
grep -rn "/api/v1/rrhh" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "=== Refs to /api/v1/vacaciones/ (excluding generated) ==="
grep -rn "/api/v1/vacaciones" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
cd D:/VYNTIA
```

Expected counts pre-refactor: `/api/v1/rrhh` ~ 200, `/api/v1/vacaciones` ~ 29. Save these numbers — post-refactor must be 0.

- [ ] **Step 6: Crear branch L3.10.4b**

```bash
git checkout -b vyntia/L3.10.4b-frontend-url-refactor
git status --short
```

---

## Task 2: Comitear el plan

- [ ] **Step 1: Add y commit plan file**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-28-vyntia-foundation-L3.10.4b-frontend-url-refactor.md
git commit -m "$(cat <<'EOF'
docs(L3.10.4b): add frontend URL refactor plan (consume English paths)

Frontend-only sub-PR of L3.10.4. Updates 19 files to consume the new
English URLs added by L3.10.4a. Out of scope: field renames, file renames,
generated/* — those are L3.10.4c/d and L3.11.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Update `apps/web/src/services/areasService.ts` (organization)

**Files:**
- Modify: `apps/web/src/services/areasService.ts`

`areasService.ts` apunta a `/api/v1/rrhh/areas/` y todas sus sub-acciones. Migra al path canónico `/api/v1/organization/departments/`.

- [ ] **Step 1: Read file**

```bash
sed -n '1,5p' D:/VYNTIA/apps/web/src/services/areasService.ts
```

- [ ] **Step 2: Replace URL prefix**

Use Edit tool with `replace_all: true`:

- File: `apps/web/src/services/areasService.ts`
- old_string: `/api/v1/rrhh/areas/`
- new_string: `/api/v1/organization/departments/`
- replace_all: true

- [ ] **Step 3: Verify zero remaining legacy refs in this file**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/areasService.ts || echo "OK: no legacy URLs in areasService.ts"
```

Expected: `OK: no legacy URLs in areasService.ts`.

- [ ] **Step 4: Verify new URLs are reachable in shape**

```bash
grep -c "/api/v1/organization/departments/" D:/VYNTIA/apps/web/src/services/areasService.ts
```

Expected: ~23 (matches the legacy ref count from pre-flight).

---

## Task 4: Update `apps/web/src/services/usersService.ts` (identity)

**Files:**
- Modify: `apps/web/src/services/usersService.ts`

`usersService.ts` toca tres prefijos: `usuarios`, `roles`, `permisos`, `usuario-roles`. Cada uno se migra a su path nuevo bajo `/api/v1/identity/`.

- [ ] **Step 1: Replace `usuarios`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/usersService.ts`
- old: `/api/v1/rrhh/usuarios/`
- new: `/api/v1/identity/users/`
- replace_all: true

- [ ] **Step 2: Replace `roles`**

- old: `/api/v1/rrhh/roles/`
- new: `/api/v1/identity/roles/`
- replace_all: true

- [ ] **Step 3: Replace `permisos`**

- old: `/api/v1/rrhh/permisos/`
- new: `/api/v1/identity/permissions/`
- replace_all: true

- [ ] **Step 4: Replace `usuario-roles`**

- old: `/api/v1/rrhh/usuario-roles/`
- new: `/api/v1/identity/user-roles/`
- replace_all: true

- [ ] **Step 5: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/usersService.ts || echo "OK: no legacy URLs in usersService.ts"
```

Expected: `OK`.

---

## Task 5: Update `apps/web/src/services/securityService.ts` (identity)

**Files:**
- Modify: `apps/web/src/services/securityService.ts`

`securityService.ts` mezcla nombres en español e inglés (`modules`, `role-permissions`, `rol-permisos`, `roles`, `permisos`). Hay que normalizar todo a `/api/v1/identity/...`.

- [ ] **Step 1: Replace `modules` (legacy ya está en inglés en el path pero bajo /rrhh/)**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/securityService.ts`
- old: `/api/v1/rrhh/modules/`
- new: `/api/v1/identity/modules/`
- replace_all: true

- [ ] **Step 2: Replace `role-permissions` (legacy English)**

- old: `/api/v1/rrhh/role-permissions/`
- new: `/api/v1/identity/role-permissions/`
- replace_all: true

- [ ] **Step 3: Replace `rol-permisos` (legacy Spanish)**

- old: `/api/v1/rrhh/rol-permisos/`
- new: `/api/v1/identity/role-permissions/`
- replace_all: true

- [ ] **Step 4: Replace `roles`**

- old: `/api/v1/rrhh/roles/`
- new: `/api/v1/identity/roles/`
- replace_all: true

- [ ] **Step 5: Replace `permisos`**

- old: `/api/v1/rrhh/permisos/`
- new: `/api/v1/identity/permissions/`
- replace_all: true

- [ ] **Step 6: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/securityService.ts || echo "OK: no legacy URLs in securityService.ts"
```

Expected: `OK`.

---

## Task 6: Update `apps/web/src/services/employeesService.ts` (employees)

**Files:**
- Modify: `apps/web/src/services/employeesService.ts`

`employeesService.ts` toca cuatro prefijos: `empleados`, `datos-laborales`, `datos-familiares`, `datos-academicos`. Empleados se monta FLAT (`/api/v1/employees/`), los otros también flat (`/api/v1/family-members/`, etc.) per L3.10.4a.

- [ ] **Step 1: Replace `empleados`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/employeesService.ts`
- old: `/api/v1/rrhh/empleados/`
- new: `/api/v1/employees/`
- replace_all: true

- [ ] **Step 2: Replace `datos-laborales`**

- old: `/api/v1/rrhh/datos-laborales/`
- new: `/api/v1/employment-data/`
- replace_all: true

- [ ] **Step 3: Replace `datos-familiares`**

- old: `/api/v1/rrhh/datos-familiares/`
- new: `/api/v1/family-members/`
- replace_all: true

- [ ] **Step 4: Replace `datos-academicos`**

- old: `/api/v1/rrhh/datos-academicos/`
- new: `/api/v1/academic-records/`
- replace_all: true

- [ ] **Step 5: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/employeesService.ts || echo "OK: no legacy URLs in employeesService.ts"
```

Expected: `OK`.

---

## Task 7: Update `apps/web/src/services/contratosService.ts` (contracts + documents)

**Files:**
- Modify: `apps/web/src/services/contratosService.ts`

`contratosService.ts` toca `contratos-adendas` (→ `/api/v1/contracts/`) y los endpoints de generación de documentos (`/documentos/generar-contrato/` etc., que migran a `/api/v1/documents/documents/generar-*`).

- [ ] **Step 1: Replace `contratos-adendas`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/contratosService.ts`
- old: `/api/v1/rrhh/contratos-adendas/`
- new: `/api/v1/contracts/`
- replace_all: true

- [ ] **Step 2: Replace `documentos/generar-certificado`**

- old: `/api/v1/rrhh/documentos/generar-certificado/`
- new: `/api/v1/documents/documents/generar-certificado/`
- replace_all: true

- [ ] **Step 3: Replace `documentos/generar-contrato`**

- old: `/api/v1/rrhh/documentos/generar-contrato/`
- new: `/api/v1/documents/documents/generar-contrato/`
- replace_all: true

- [ ] **Step 4: Replace `documentos/generar-adenda`**

- old: `/api/v1/rrhh/documentos/generar-adenda/`
- new: `/api/v1/documents/documents/generar-adenda/`
- replace_all: true

- [ ] **Step 5: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/contratosService.ts || echo "OK: no legacy URLs in contratosService.ts"
```

Expected: `OK`.

---

## Task 8: Update `apps/web/src/services/empresaService.ts` (organization companies)

**Files:**
- Modify: `apps/web/src/services/empresaService.ts`

- [ ] **Step 1: Replace `configuracion-empresa`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/empresaService.ts`
- old: `/api/v1/rrhh/configuracion-empresa/`
- new: `/api/v1/organization/companies/`
- replace_all: true

- [ ] **Step 2: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/empresaService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 9: Update `apps/web/src/services/legajoService.ts` (documents)

**Files:**
- Modify: `apps/web/src/services/legajoService.ts`

`legajoService.ts` toca `documentos-digitales` que migra al doble prefix `/api/v1/documents/documents/`.

- [ ] **Step 1: Replace `documentos-digitales`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/legajoService.ts`
- old: `/api/v1/rrhh/documentos-digitales/`
- new: `/api/v1/documents/documents/`
- replace_all: true

- [ ] **Step 2: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/legajoService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 10: Update `apps/web/src/services/onboardingService.ts` (onboarding)

**Files:**
- Modify: `apps/web/src/services/onboardingService.ts`

`onboardingService.ts` apunta al ViewSet de onboarding que migra a `/api/v1/onboarding/processes/`.

- [ ] **Step 1: Replace `onboarding`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/onboardingService.ts`
- old: `/api/v1/rrhh/onboarding/`
- new: `/api/v1/onboarding/processes/`
- replace_all: true

- [ ] **Step 2: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/onboardingService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 11: Update `apps/web/src/services/plantillasService.ts` (documents/templates)

**Files:**
- Modify: `apps/web/src/services/plantillasService.ts`

`plantillasService.ts` toca dos prefijos sobre `/documentos/`: `plantillas-word` (con sub-acciones) y `generar-desde-plantilla-word`. Ambos migran al doble prefix `/api/v1/documents/documents/`.

- [ ] **Step 1: Replace `documentos/plantillas-word`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/plantillasService.ts`
- old: `/api/v1/rrhh/documentos/plantillas-word/`
- new: `/api/v1/documents/documents/plantillas-word/`
- replace_all: true

- [ ] **Step 2: Replace `documentos/generar-desde-plantilla-word`**

- old: `/api/v1/rrhh/documentos/generar-desde-plantilla-word/`
- new: `/api/v1/documents/documents/generar-desde-plantilla-word/`
- replace_all: true

- [ ] **Step 3: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/plantillasService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 12: Update `apps/web/src/services/remuneracionesService.ts` (payroll)

**Files:**
- Modify: `apps/web/src/services/remuneracionesService.ts`

Archivo más grande de la migración (47 refs). Toca 8 prefijos distintos. Aplicar replace_all en orden.

- [ ] **Step 1: Replace `configuracion-remuneraciones`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/remuneracionesService.ts`
- old: `/api/v1/rrhh/configuracion-remuneraciones/`
- new: `/api/v1/payroll/compensation-configurations/`
- replace_all: true

- [ ] **Step 2: Replace `configuracion-afp`**

- old: `/api/v1/rrhh/configuracion-afp/`
- new: `/api/v1/payroll/afp-configurations/`
- replace_all: true

- [ ] **Step 3: Replace `configuracion-uit`**

- old: `/api/v1/rrhh/configuracion-uit/`
- new: `/api/v1/payroll/tax-parameters/`
- replace_all: true

- [ ] **Step 4: Replace `planillas-mensuales`**

- old: `/api/v1/rrhh/planillas-mensuales/`
- new: `/api/v1/payroll/monthly-runs/`
- replace_all: true

- [ ] **Step 5: Replace `detalles-planilla`**

- old: `/api/v1/rrhh/detalles-planilla/`
- new: `/api/v1/payroll/details/`
- replace_all: true

- [ ] **Step 6: Replace `descuentos-masivos`**

- old: `/api/v1/rrhh/descuentos-masivos/`
- new: `/api/v1/payroll/mass-deductions/`
- replace_all: true

- [ ] **Step 7: Replace `boletas-pago`**

- old: `/api/v1/rrhh/boletas-pago/`
- new: `/api/v1/payroll/payslips/`
- replace_all: true

- [ ] **Step 8: Replace `calendarios-pago`**

- old: `/api/v1/rrhh/calendarios-pago/`
- new: `/api/v1/payroll/payment-schedules/`
- replace_all: true

- [ ] **Step 9: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/remuneracionesService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 13: Update `apps/web/src/services/vacacionesService.ts` (time-off)

**Files:**
- Modify: `apps/web/src/services/vacacionesService.ts`

Único service con prefix `/api/v1/vacaciones/`. Toca 6 sub-prefijos: `configuraciones`, `periodos`, `solicitudes`, `goces`, `historial`, `reportes`.

- [ ] **Step 1: Replace `configuraciones`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/vacacionesService.ts`
- old: `/api/v1/vacaciones/configuraciones/`
- new: `/api/v1/time-off/configurations/`
- replace_all: true

- [ ] **Step 2: Replace `periodos`**

- old: `/api/v1/vacaciones/periodos/`
- new: `/api/v1/time-off/periods/`
- replace_all: true

- [ ] **Step 3: Replace `solicitudes`**

- old: `/api/v1/vacaciones/solicitudes/`
- new: `/api/v1/time-off/requests/`
- replace_all: true

- [ ] **Step 4: Replace `goces`**

- old: `/api/v1/vacaciones/goces/`
- new: `/api/v1/time-off/grants/`
- replace_all: true

- [ ] **Step 5: Replace `historial`**

- old: `/api/v1/vacaciones/historial/`
- new: `/api/v1/time-off/history/`
- replace_all: true

- [ ] **Step 6: Replace `reportes`**

- old: `/api/v1/vacaciones/reportes/`
- new: `/api/v1/time-off/reports/`
- replace_all: true

- [ ] **Step 7: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/services/vacacionesService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 14: Update `apps/web/src/lib/api.ts` (legacy URL helpers)

**Files:**
- Modify: `apps/web/src/lib/api.ts`

`lib/api.ts` define el axios instance + helpers tipo "URL alias" que en la práctica duplican lo que hacen los services. Los `/api/v1/auth/...` quedan intactos (no son legacy). Los demás se migran a sus paths nuevos.

- [ ] **Step 1: Replace `empleados`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/lib/api.ts`
- old: `/api/v1/rrhh/empleados/`
- new: `/api/v1/employees/`
- replace_all: true

- [ ] **Step 2: Replace `areas`**

- old: `/api/v1/rrhh/areas/`
- new: `/api/v1/organization/departments/`
- replace_all: true

- [ ] **Step 3: Replace `usuarios`**

- old: `/api/v1/rrhh/usuarios/`
- new: `/api/v1/identity/users/`
- replace_all: true

- [ ] **Step 4: Replace `roles`**

- old: `/api/v1/rrhh/roles/`
- new: `/api/v1/identity/roles/`
- replace_all: true

- [ ] **Step 5: Replace `permisos`**

- old: `/api/v1/rrhh/permisos/`
- new: `/api/v1/identity/permissions/`
- replace_all: true

- [ ] **Step 6: Verify**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/lib/api.ts || echo "OK"
```

Expected: `OK`. `/api/v1/auth/` refs siguen presentes — eso está bien.

---

## Task 15: Update onboarding feature services + tests

**Files:**
- Modify: `apps/web/src/features/onboarding/services/onboardingDataService.ts`
- Modify: `apps/web/src/features/onboarding/services/onboardingUploadService.ts`
- Modify: `apps/web/src/features/onboarding/services/__tests__/onboardingUploadService.test.ts`

Estos archivos viven bajo `features/onboarding/` (estructura legacy de "feature folders" — se reorganiza en L4) y comparten URLs con los services raíz.

- [ ] **Step 1: `onboardingDataService.ts` — Replace `datos-familiares`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/features/onboarding/services/onboardingDataService.ts`
- old: `/api/v1/rrhh/datos-familiares/`
- new: `/api/v1/family-members/`
- replace_all: true

- [ ] **Step 2: `onboardingDataService.ts` — Replace `datos-academicos`**

- old: `/api/v1/rrhh/datos-academicos/`
- new: `/api/v1/academic-records/`
- replace_all: true

- [ ] **Step 3: `onboardingDataService.ts` — Replace `cursos-certificaciones`**

- old: `/api/v1/rrhh/cursos-certificaciones/`
- new: `/api/v1/certifications/`
- replace_all: true

- [ ] **Step 4: `onboardingDataService.ts` — Replace `documentos-digitales`**

- old: `/api/v1/rrhh/documentos-digitales/`
- new: `/api/v1/documents/documents/`
- replace_all: true

- [ ] **Step 5: `onboardingUploadService.ts` — Replace `onboarding`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/features/onboarding/services/onboardingUploadService.ts`
- old: `/api/v1/rrhh/onboarding/`
- new: `/api/v1/onboarding/processes/`
- replace_all: true

- [ ] **Step 6: Update test file expectations**

The test file `__tests__/onboardingUploadService.test.ts` asserts the URL passed to `apiClient.post`. After Step 5 the actual call is `/api/v1/onboarding/processes/subir-documento/` — update the test assertion to match.

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/features/onboarding/services/__tests__/onboardingUploadService.test.ts`
- old: `/api/v1/rrhh/onboarding/`
- new: `/api/v1/onboarding/processes/`
- replace_all: true

- [ ] **Step 7: Verify both files + test**

```bash
grep -rn "/api/v1/rrhh\|/api/v1/vacaciones" D:/VYNTIA/apps/web/src/features/onboarding/ || echo "OK: no legacy URLs in features/onboarding/"
```

Expected: `OK`.

---

## Task 16: Update pages and components with inline URLs

**Files:**
- Modify: `apps/web/src/pages/HROverviewDashboard.tsx`
- Modify: `apps/web/src/pages/onboarding/OnboardingAdminPage.tsx`
- Modify: `apps/web/src/features/onboarding/pages/OnboardingEmployeePage.tsx`
- Modify: `apps/web/src/features/onboarding/components/OnboardingTabPersonal.tsx`

Algunas páginas y componentes hacen llamadas directas vía `apiClient.get/patch` con URL inline (anti-patrón legacy — debería ir vía service). Por consistencia con esta refactor migramos las URLs sin reorganizar el code (eso queda para L4).

- [ ] **Step 1: `HROverviewDashboard.tsx` — Replace `empleados`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/HROverviewDashboard.tsx`
- old: `/api/v1/rrhh/empleados/`
- new: `/api/v1/employees/`
- replace_all: true

- [ ] **Step 2: `HROverviewDashboard.tsx` — Replace `areas`**

- old: `/api/v1/rrhh/areas/`
- new: `/api/v1/organization/departments/`
- replace_all: true

- [ ] **Step 3: `HROverviewDashboard.tsx` — Replace `planillas-mensuales`**

- old: `/api/v1/rrhh/planillas-mensuales/`
- new: `/api/v1/payroll/monthly-runs/`
- replace_all: true

- [ ] **Step 4: `OnboardingAdminPage.tsx` — Replace `onboarding`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/onboarding/OnboardingAdminPage.tsx`
- old: `/api/v1/rrhh/onboarding/`
- new: `/api/v1/onboarding/processes/`
- replace_all: true

- [ ] **Step 5: `OnboardingEmployeePage.tsx` — Replace `documentos-digitales`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/features/onboarding/pages/OnboardingEmployeePage.tsx`
- old: `/api/v1/rrhh/documentos-digitales/`
- new: `/api/v1/documents/documents/`
- replace_all: true

- [ ] **Step 6: `OnboardingEmployeePage.tsx` — Replace `empleados`**

- old: `/api/v1/rrhh/empleados/`
- new: `/api/v1/employees/`
- replace_all: true

- [ ] **Step 7: `OnboardingTabPersonal.tsx` — Replace `empleados`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/features/onboarding/components/OnboardingTabPersonal.tsx`
- old: `/api/v1/rrhh/empleados/`
- new: `/api/v1/employees/`
- replace_all: true

- [ ] **Step 8: Verify all 4 files**

```bash
grep -n "/api/v1/rrhh\|/api/v1/vacaciones" \
  D:/VYNTIA/apps/web/src/pages/HROverviewDashboard.tsx \
  D:/VYNTIA/apps/web/src/pages/onboarding/OnboardingAdminPage.tsx \
  D:/VYNTIA/apps/web/src/features/onboarding/pages/OnboardingEmployeePage.tsx \
  D:/VYNTIA/apps/web/src/features/onboarding/components/OnboardingTabPersonal.tsx \
  || echo "OK: no legacy URLs in pages/components"
```

Expected: `OK`.

---

## Task 17: Global verification — zero legacy refs in non-generated code

Esta es la verificación crítica: la suma de todos los reemplazos debe dejar 0 referencias legacy fuera de `generated/`.

- [ ] **Step 1: Count legacy refs (excluding generated)**

```bash
cd D:/VYNTIA/apps/web
echo "=== Legacy /api/v1/rrhh/ refs (excluding generated) ==="
grep -rn "/api/v1/rrhh" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo ""
echo "=== Legacy /api/v1/vacaciones/ refs (excluding generated) ==="
grep -rn "/api/v1/vacaciones" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
cd D:/VYNTIA
```

Expected: ambos contadores = `0`.

If non-zero:
- Read the offending file with the listed line number
- Identify the prefix not yet replaced
- Add a Step in the relevant Task above to replace it (don't fix here — keep the plan and the actual fix in the same Task)
- Re-run this verification

- [ ] **Step 2: Confirm new English URLs are present**

```bash
cd D:/VYNTIA/apps/web
echo "=== Refs to new English paths (excluding generated) ==="
grep -rn "/api/v1/employees\|/api/v1/identity\|/api/v1/organization\|/api/v1/contracts\|/api/v1/employment-data\|/api/v1/family-members\|/api/v1/academic-records\|/api/v1/certifications\|/api/v1/documents\|/api/v1/payroll\|/api/v1/time-off\|/api/v1/onboarding/processes" \
  src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
cd D:/VYNTIA
```

Expected: ~230 (matches the legacy count from pre-flight Task 1 Step 5).

- [ ] **Step 3: Confirm `generated/` was NOT touched**

```bash
git status --short apps/web/src/generated/ || echo "generated/ clean (not modified)"
```

Expected: empty output (no changes to `generated/`).

---

## Task 18: Frontend smoke — lint, type-check, build, vitest

- [ ] **Step 1: ESLint**

```bash
cd D:/VYNTIA/apps/web
npm run lint 2>&1 | tail -20
cd D:/VYNTIA
```

Expected: clean. Si hay nuevos warnings sobre URLs no usadas o imports rotos, leer el output e investigar antes de proceguir.

- [ ] **Step 2: TypeScript build (also catches type errors)**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -30
cd D:/VYNTIA
```

Expected: build exitosa. Cualquier error de TS aquí es crítico — inspeccionar y resolver antes de seguir.

- [ ] **Step 3: Vitest unit tests**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | tail -20
cd D:/VYNTIA
```

Expected: `7 passed` (o el baseline pre-refactor). 1 file load-failure pre-existing — no debe agregarse otro nuevo failure.

If `__tests__/onboardingUploadService.test.ts` falla con "expected URL ... to match ...":
- El Step 6 del Task 15 debió actualizar la assertion a la nueva URL
- Si falló, abrir el archivo, encontrar la assertion sobre URL, y actualizar manualmente

---

## Task 19: Runtime smoke — dev server hits new URLs end-to-end

- [ ] **Step 1: Start backend in background**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l3104b.log 2>&1 &
SERVER_PID=$!
sleep 10
echo "Backend PID: $SERVER_PID"
cd D:/VYNTIA
```

- [ ] **Step 2: Curl new URLs (expect 401 unauthenticated, NOT 404)**

```bash
echo "=== Sample new URLs respond with 401 (auth required) ==="
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/employees/\n" http://127.0.0.1:8000/api/v1/employees/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/identity/users/\n" http://127.0.0.1:8000/api/v1/identity/users/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/organization/departments/\n" http://127.0.0.1:8000/api/v1/organization/departments/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/contracts/\n" http://127.0.0.1:8000/api/v1/contracts/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/payroll/monthly-runs/\n" http://127.0.0.1:8000/api/v1/payroll/monthly-runs/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/time-off/requests/\n" http://127.0.0.1:8000/api/v1/time-off/requests/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/documents/documents/\n" http://127.0.0.1:8000/api/v1/documents/documents/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/onboarding/processes/\n" http://127.0.0.1:8000/api/v1/onboarding/processes/
```

Expected: cada uno `HTTP 401` (auth required) — confirma que el endpoint EXISTE. Cualquier `HTTP 404` significa que la URL en el plan no coincide con la URL real registrada en backend.

- [ ] **Step 3: Stop backend**

```bash
kill $SERVER_PID 2>/dev/null
sleep 2
```

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 4: Confirm backend baseline preserved (sanity)**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `161 passed, 8 failed, 3 skipped`. Backend nunca se tocó — debe seguir idéntico.

---

## Task 20: Atomic commit

- [ ] **Step 1: Stage frontend changes**

```bash
cd D:/VYNTIA
git status --short | head -30
git add apps/web/
```

- [ ] **Step 2: Confirm staged delta**

```bash
git diff --cached --stat | tail -25
```

Expected: ~19 files modified, ~230 line changes (1 changed line per replaced URL ref).

- [ ] **Step 3: Commit**

```bash
git commit -m "$(cat <<'EOF'
chore(L3.10.4b): frontend URL refactor — consume English paths from L3.10.4a

Migrates all frontend API calls from legacy Spanish URLs (/api/v1/rrhh/...,
/api/v1/vacaciones/...) to canonical English URLs added by L3.10.4a:
- /api/v1/identity/{users,roles,permissions,modules,role-permissions,user-roles}/
- /api/v1/organization/{departments,companies}/
- /api/v1/{employees,family-members,academic-records,certifications}/
- /api/v1/{contracts,employment-data}/
- /api/v1/documents/documents/{,generate-*,plantillas-word/*}/
- /api/v1/payroll/{monthly-runs,details,mass-deductions,payslips,payment-schedules,afp-configurations,tax-parameters,compensation-configurations}/
- /api/v1/time-off/{configurations,periods,requests,grants,history,reports}/
- /api/v1/onboarding/processes/

Files modified (19):
- apps/web/src/lib/api.ts
- apps/web/src/services/{areas,contratos,employees,empresa,legajo,onboarding,plantillas,remuneraciones,security,users,vacaciones}Service.ts
- apps/web/src/features/onboarding/services/onboarding{Data,Upload}Service.ts (+ test)
- apps/web/src/features/onboarding/pages/OnboardingEmployeePage.tsx
- apps/web/src/features/onboarding/components/OnboardingTabPersonal.tsx
- apps/web/src/pages/HROverviewDashboard.tsx
- apps/web/src/pages/onboarding/OnboardingAdminPage.tsx

Out of scope (deferred to L3.10.4c+):
- TS field renames (empleado_id → id, fecha_creacion → created_at, etc.)
- Service file renames (contratosService.ts → contractsService.ts)
- generated/api/services/* (auto-regenerated from updated OpenAPI schema)

Verification:
- grep "/api/v1/rrhh|/api/v1/vacaciones" apps/web/src/ (excluding generated/) → 0 matches
- npm run lint: clean
- npm run build: success
- npm test: 7 passed (baseline preserved)
- Backend pytest: 161 passed, 8 failed, 3 skipped (untouched)
- Runtime curl smoke: all new URLs respond 401 (endpoints exist)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 4: Verify commits on branch**

```bash
git log --oneline vyntia/L3.10.4b-frontend-url-refactor ^master
git status --short
```

Expected: 2 commits (`docs(L3.10.4b) plan`, `chore(L3.10.4b)`), `git status` clean.

---

## Task 21: Merge a master + roadmap update

- [ ] **Step 1: Confirmar autorización del usuario**

Pause antes del merge. Solo proceder si el usuario aprueba.

- [ ] **Step 2: Merge --no-ff**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/L3.10.4b-frontend-url-refactor -m "Merge L3.10.4b: frontend URL refactor (consume English paths)"
git log --oneline -5
```

- [ ] **Step 3: Post-merge smoke**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -5
npm test -- --run 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: backend baseline preserved, frontend build success, tests pass.

- [ ] **Step 4: Update roadmap**

Edit `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`:
- Mark L3.10.4b ✅ merged with commit hash
- Update "Next" pointer to L3.10.4c (frontend field rename: `empleado_id` → `id`, `fecha_creacion` → `created_at`)
- Document split rationale (URL refactor done; field rename next)

Use Edit tool to find and update the L3.10.4 section. Preserve the rest of the roadmap structure.

- [ ] **Step 5: Update memory**

Edit `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- L3.10.4b ✅ merged
- Next: L3.10.4c — frontend field rename (TS interfaces + components)

- [ ] **Step 6: Commit roadmap + memory**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.10.4b): mark L3.10.4b merged, L3.10.4c (frontend field rename) as next"
```

(Memory file is in `C:/Users/zeeke/.claude/...` outside the repo — not git-tracked; just save the file.)

---

## Después de L3.10.4b

**Próximo plan:** L3.10.4c — frontend field rename. Aplica § 3.6 al frontend para los fields que ya se renombraron en backend (L3.10.2):
- TS interfaces: `empleado_id: number` → `id: string` UUID
- TS interfaces: `fecha_creacion`, `fecha_actualizacion` → `created_at`, `updated_at`
- TS interfaces: `creado_por`, `modificado_por` → `created_by`, `updated_by`
- TS interfaces: `estado`/`activo` → `status`/`is_active`
- 50+ component refs a estos fields
- 366 frontend refs identificadas pre-L3.10.2

Domain HR vocabulario español SE PRESERVA (L3.10.2 § 3.6.1 Option B): `nombres_empleado`, `apellido_paterno`, `tipo_documento`, `numero_cuspp`, `estado_civil`, etc. NO se traducen.

Después L3.10.4d — frontend file renames (`contratosService.ts` → `contractsService.ts`, `areasService.ts` → `departmentsService.ts`, etc.) y `generated/api/services/*` regenerado del schema actualizado.

Después L3.11 — cleanup final: remover URLs legacy en `api/v1/rrhh/urls.py` + `api/v1/vacaciones/urls.py`, vaciar `app_rrhh/` (carpeta morirá vacía), grep dead-code refs.

---

## Notas para el ejecutor

- **Frontend-only refactor.** Backend no se toca; debe quedar exactamente como estaba post-L3.10.4a. Si pytest baseline cambia, algo se tocó por error.
- **Custom actions preservadas tal cual.** `/renovar_contrato/`, `/mi-onboarding/`, `/aprobar_planilla/`, `/reporte_integral/`, `/asignar_rol/`, etc. — siguen siendo sub-paths de los viewsets, accesibles bajo la nueva URL base. Frontend NO debe traducir el nombre del action (esos son `@action(url_path=...)` en backend; renombrarlos sería un refactor backend separado).
- **Doble prefix `/documents/documents/`** es correcto. L3.10.4a Task 7 lo eligió así para mantener `DocumentosDigitalesViewSet` separado de las function-based generation views, ambas bajo `/api/v1/documents/`. Si se ve raro al ejecutar, recordar que es lo que el backend acepta hoy.
- **`generated/api/services/*` NO se toca.** Esos files son output de OpenAPI codegen sobre el schema. Regenerar tras correr smoke tests es trabajo de L3.10.4c o más adelante. El runtime usa los services manuales, no los generated, así que no afecta la migration.
- **`features/onboarding/` parece duplicar lógica de `services/`** — eso es legacy de la estructura "feature folders" que se reorganiza en L4. Por ahora ambos coexisten. Cualquier llamada inline a `apiClient` en pages/components también se migra (anti-patrón de organización pero el URL string sí se actualiza).
- **`replace_all: true`** es seguro porque cada URL legacy es un substring único en el contexto del archivo (no hay falsos positivos esperados). Si Edit reporta "string not found", verificar el file path o si la URL ya fue reemplazada.
- **Riesgo bajo runtime** — si el dev server arranca y los curls retornan 401 (no 404), todas las URLs son válidas. Sólo debugger es necesario si una pantalla específica empieza a fallar — eso indicaría un URL string que escapó el grep (e.g., concatenado dinámicamente: `\`${BASE}/${kind}/\``). Audit con `grep -rn "rrhh\|vacaciones" apps/web/src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated` no encontró ninguna así pre-plan, pero vale verificar si aparece runtime errors.
