# Feature Supervisor — Empleados v4 (post Bloque F)

**Fecha:** 2026-05-22
**Invocado por:** verificación runtime de commits `92c79ef2` (backend N1+N2+N3+N7) y `c35aebfe` (frontend N4+N5+p.estado+tsconfig)
**Confianza:** alta — todas las verificaciones corridas contra demo-pro vivo + transacciones rollback-ed
**Tiempo:** ~50min
**Persistencia:** este archivo lo escribió el orquestador (main agent) — el especialista devolvió el contenido inline tras un system reminder del harness que le indicó no escribir reportes. Meta-finding registrado en el PM v4.

---

## Verdict global

**Casi-verde con un blocker oculto: N1 NO funciona en runtime.** El fix aparenta funcionar (`admin.permisos_activos().count() == 17` cuando NO hay tenant context), pero `roles_activos()` y `permisos_activos()` filtran Role/Permission por `tenant=request.tenant` cuando el middleware está activo, y el seed pone los roles a `tenant=None` (global). Resultado: bajo el flujo HTTP real (subdomain demo-pro), admin sigue teniendo 0 permisos y los endpoints con `@require_permissions` siguen retornando 403. **El commit message es engañoso** — "Runtime verified" se hizo sin tenant context.

## Tabla N1–N7 × verdict

| ID | Hallazgo | Verdict | Evidencia |
|---|---|---|---|
| **N1** | Seed sin RolePermission | **❌ NO FUNCIONÓ en runtime** | Sin tenant context: admin.permisos_activos()=17 ✅. **Bajo tenant context (set_current_tenant(demo)): admin.roles_activos()=0, admin.permisos_activos()=0**. APIClient con Host=demo-pro.localhost + JWT admin a `/api/v1/employees/activos/` → **403** (igual que v3). Los 17 permisos del admin están todos asociados a Role con tenant=None, y `roles_activos()` los filtra fuera bajo tenant context (apps/identity/models/user.py:436 y :458, :464). |
| **N2** | validate_numero_documento sin scope tenant | **✅ FIX CONFIRMADO** | Con tenant t2 + DNI existente en demo-pro: EmpleadoCreateSerializer.validate_numero_documento → PASS. OnboardingIniciarSerializer.validate_numero_documento / validate_correo_personal → PASS. Mismo tenant duplicado: REJECTED ✅. Sin tenant (admin subdomain): REJECTED globalmente ✅ (no permisivo en exceso). |
| **N3** | Wipe AccessLog | **✅ FIX CONFIRMADO (inspección)** | `seed_demo_pro.py:247` invoca `DocumentAccessLog.objects.filter(tenant=tenant).delete()` ANTES de `DigitalDocument` (línea 257 borra `DigitalDossier`). `DocumentAccessLog.tenant` es FK on_delete=PROTECT a Tenant → orden correcto evita PROTECT. No corrí `--fresh` runtime para no destruir demo-pro. |
| **N7** | Cálculo de edad unificado | **⚠️ PARCIAL** | `api/v1/rrhh/serializers.py:589, 773` ambos usan `today.replace(year=today.year - 18)` ✅. **PERO** sobrevive `apps/employees/models/family_member.py:404`: `date.today() - timedelta(days=18*365)` (método `hijos_menores`, no era P0 v3 pero es leap-drifty). |

## Hallazgos NUEVOS de v4

| # | Hallazgo | Sev | Horizonte | Dónde / Evidencia |
|---|---|---|---|---|
| V4-1 | **N1 no funciona bajo tenant context** | 🔴 P1 (mismo blocker original) | CORTO (~30min) | `apps/identity/models/user.py:434-437, 457-464` — `roles_activos()` y `permisos_activos()` filtran por tenant cuando hay tenant context, y rechazan los roles globales que el seed creó. Dos fixes posibles: (a) hacer que `roles_activos()` incluya roles globales (`Q(tenant=tenant) | Q(tenant__isnull=True)`); (b) cambiar el seed para crear copias tenant-scoped de los 17 RolePermission rows. La opción (a) es más arquitectural (alinea con concepto "roles de sistema globales"); (b) es más quirúrgica. |
| V4-2 | **N4 frontend: bug lógico — el `throw new Error()` dentro del try es comido por el inner catch** | 🟠 ALTO | CORTO (5min) | `dossierService.ts:146-153` — `JSON.parse` succeeds, `throw new Error(parsed.message)` se lanza INSIDE the inner try, y el inner `catch (parseErr) { /* fall through */ }` lo captura (cuerpo vacío) → cae al `throw err` original. El user sigue viendo "Request failed with status code 403". Fix: declarar `let parsed; try { parsed = JSON.parse(text); } catch {...}; if (parsed) throw new Error(parsed.message)` — separar parsing de throw. |
| V4-3 | **Patrón Blob-403 no generalizado** | 🟡 MEDIO | MEDIO | Hay 7 otros endpoints con `responseType: 'blob'` (ccfService, tRegistroService, workCertificateService, inductionService, displacementService, publicPositionService): ninguno tiene el catch/parse del Blob. Si algún backend agrega PL gate, el user verá "status code 403". Sugerencia: helper en `apiClient` (`downloadBlob` wrapper que parsea body de error). |
| V4-4 | **HROverviewDashboard.tsx:738 sigue refiriéndose a `latestPlanilla.status`** | 🟡 BAJO | CORTO (2min) | El Bloque F cambió 4 sitios (líneas 479, 496, 589, 658) pero quedó `sub={... latestPlanilla.estado_texto ?? latestPlanilla.status ?? '—'}`. No bloquea KPI %, pero la sub-leyenda muestra `"undefined"` o `"—"` en lugar del estado real. |
| V4-5 | **N7 sobrevive en apps/employees/models/family_member.py:404** | 🟡 BAJO | CORTO (3min) | Mismo cálculo leap-drifty (`days=18*365`) en `FamilyMember.hijos_menores()`. No es serializer ni v3, pero el N7 era "unificar edad" — quedó pendiente. |
| V4-6 | **Script untracked en repo: `tests/test_audit_temp_hr_v4.py`** | 🟡 BAJO | CORTO (1min) | El agente HR-tester dejó su script de auditoría en `apps/api/tests/test_audit_temp_hr_v4.py` sin tracking (git status). Si se queda y se trackea por accidente, pollute la suite (importa al setup y crea Permission rows con `call_command('setup_roles_permisos')`). Decisión: borrarlo o commitearlo bajo `tests/_tmp/`. |
| V4-7 | **`setup_roles_permisos` crea User admin/Admin123! con `is_superuser=True`** | 🟡 BAJO/AUDIT | MEDIO | Side-effect del fix N1: el seed_demo_pro ahora invoca `setup_roles_permisos`, el cual crea un superuser global llamado `admin` con password literal `Admin123!` (línea 195). Cualquier `seed_demo_pro` desde ahora siembra ese usuario en la BD compartida, expandiendo superficie de auth global. Documentar como decisión consciente o pasar `--no-create-admin`. |

## Side-effects revisados

- **¿setup_roles_permisos interfiere con tests?** No detecté tests que invoquen ese command ni `seed_demo_pro` desde el suite real. Los tests usan transactional fixtures (pytest-django) y limpian. Confirmado: 985 pass / 1 fail / 17 skip — **0 regresiones**.
- **¿Patrón 403→Blob debería propagarse?** SÍ — 7 servicios FE blob lo necesitan (ver V4-3).
- **¿validate_numero_documento permisivo cuando tenant=None?** No — cae a `Employee.objects.filter(numero_documento=value)` sin filtro (global). En el admin subdomain (donde tenant=None es normal), rechaza si el DNI ya existe en CUALQUIER tenant. Defensa estricta ✅.

## Baseline pytest

```
1 failed, 985 passed, 17 skipped in 36.19s
```

Test que falla: `tests/test_permisos_debug` (pre-existente). Igual a v3. **0 regresiones nuevas.**

## Veredicto D-Pay readiness

🟡 **AMARILLO — sealed-for-D NO, casi.** El módulo Empleados sería sealed si N1 funcionara realmente, pero al no funcionar bajo tenant context, **cualquier demo via subdomain demo-pro tiene 403 en endpoints clave**.

**Bloqueador crítico antes de D:**
1. Fix V4-1 (N1 real): ajustar `roles_activos()`/`permisos_activos()` para aceptar roles globales bajo tenant context, O cambiar el seed para crear copias tenant-scoped.
2. Fix V4-2 (N4 lógica catch anidado): mover `throw new Error` fuera del inner try.

Sin estos dos fixes (~35min total), D no debería arrancar.

## Acciones recomendadas (orden)

1. **P1 (30min) — V4-1 / N1 real fix:** ajustar `permisos_activos()` y `roles_activos()` para que `tenant__isnull=True` esté incluido bajo tenant context. Self-check del seed post-creación: `admin.permisos_activos().count() == 17` *con `set_current_tenant(demo)` activo*.
2. **P1 (5min) — V4-2 / N4 fix lógico:** separar `JSON.parse` del `throw new Error` para que el inner catch no se coma el friendly error.
3. **P2 (15min) — V4-3:** helper `downloadBlob` en `apiClient` que parsea body en errores, aplicado a los 7 services.
4. **P3 (2min) — V4-4:** quitar `?? latestPlanilla.status` en HROverviewDashboard:738.
5. **P3 (3min) — V4-5:** unificar `family_member.py:404` con `today.replace(year=year-18)`.
6. **P3 (1min) — V4-6:** decidir destino de `tests/test_audit_temp_hr_v4.py` (borrar o reubicar).

## Pregunta para humano

El commit `92c79ef2` declara "Runtime verified: admin.permisos_activos().count() == 17", pero ese check se hizo sin `set_current_tenant()` activo. La verdadera prueba runtime (HTTP via subdomain) sigue dando 403. **¿Quieres que la siguiente iteración del Bloque F (F.2) cambie `roles_activos()/permisos_activos()` para incluir roles globales bajo tenant context, o prefieres que el seed cree filas tenant-scoped duplicadas?** La primera es más limpia (los roles de sistema deberían ser globales por diseño), la segunda evita tocar identity/models y es localmente seguro.
