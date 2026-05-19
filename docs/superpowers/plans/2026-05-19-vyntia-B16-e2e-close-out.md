# Phase B.16 — E2E + close-out + tag `b-vyntia-core-complete`

**Branch:** `vyntia/B16-e2e-close-out`
**Spec:** `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md` (§ 3.2 — fase B.16; § 8 métricas de éxito)
**Master roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-B-vyntia-core-master-roadmap.md`
**Backlog item:** #132 (E2E close-out: Playwright lifecycle test per ADR-B.5)
**Predecessor:** B.15b merged `ce1534d1` 2026-05-17. Module 01 (Policies) cerrado.
**ADR referenciado:** ADR-B.5 (testing strategy — three-tier: pytest unit + pytest integration + Playwright lifecycle).

## Goal

Cerrar sub-proyecto B con la fase final de verificación end-to-end:

1. **Playwright lifecycle e2e** que ejerce el happy-path completo de Module 03 contra el stack real (backend + frontend + DB). Cumple ADR-B.5 entrega final:
   - **provision tenant** (login admin) → **crear empleado** → **emitir contrato** (Module 03.2) → **kick-off onboarding** (Module 03.3) → **registrar desplazamiento** (Module 03.6) → **iniciar desvinculación + liquidación** (Module 03.7).
   - Opt-in via `RUN_LIFECYCLE_E2E=1` — sigue el patrón de `tests/e2e/tenant-isolation.test.js` para no bloquear CI default.
2. **Seed command** (`seed_lifecycle_e2e`) reproducible que materializa el tenant + admin user + las catalogaciones mínimas (Department, Position, JobLevel, contratos types) necesarias para el test no dependa de fixtures legacy.
3. **Docs sweep** final del sub-proyecto:
   - Actualizar `docs/ROADMAP_SUBPROJECTS.md` marcando B (Vyntia Core) como ✅ COMPLETE.
   - Actualizar `CLAUDE.md` (sección Migration Roadmap + Active sub-project) para reflejar que el siguiente sub-proyecto es D (Vyntia Pay) — ya que A + C + B están done.
   - Actualizar `README.md` con métricas finales del sub-proyecto.
   - `docs/superpowers/plans/2026-05-09-vyntia-B-vyntia-core-master-roadmap.md`: marcar todas las fases ✅.
   - Generar `docs/superpowers/summaries/2026-05-19-vyntia-B-vyntia-core-summary.md` con el cierre de sub-proyecto B (replicando estilo de Foundation summary).
4. **Tag `b-vyntia-core-complete`** al merge final.
5. **Memoria**: actualizar `subproject_b_progress.md` con B.16 close-out + flip al sub-proyecto siguiente.

Out-of-scope (post-B):
- Sub-proyecto D (Vyntia Pay) — planilla peruana real. Empieza con brainstorm + spec separados.
- Crons reales (alertas compliance, probation, ack reminders) — diferidos a sub-proyecto `cron_celery`.
- CI default-on para el lifecycle e2e — sigue opt-in por ADR-B.5 (seed-heavy). El default CI corre pytest + vitest + build.
- Real DNS para subdominios `*.vyntia.pe` en local — se mockea con `Host` header o se usa `127.0.0.1:5173` con un tenant fijo seeded.

## Tasks

### Task 1 — Plan + branch (DONE post-merge a master de este plan)

Crear branch `vyntia/B16-e2e-close-out` desde master (post-B.15b SHA `ce1534d1`).

### Task 2 — Seed command `seed_lifecycle_e2e`

Crear `apps/api/apps/tenancy/management/commands/seed_lifecycle_e2e.py`:

Provisiona idempotentemente (re-runnable):
- Tenant `lifecycle.vyntia.pe` (slug `lifecycle`, plan `starter`, RUC dummy `20999999999`, name "Lifecycle E2E Test Co.").
- Admin user `admin@lifecycle.test` / password `LifecyclePass123!` (rol `Admin RRHH`, tenant-scoped).
- Department `Tecnología` (root, parent null).
- 1 Position `Desarrollador Senior` bajo Tecnología (depende del Module 02 — si el modelo viene de B.6, usar `apps.organization.Position`).
- 1 JobLevel `L3` (si aplica desde B.6).

Imprime al stdout las credenciales (admin email + password + tenant host) en formato leíble por Playwright (json una línea):
```
SEED_OUTPUT: {"tenant_host": "lifecycle.vyntia.pe", "admin_email": "admin@lifecycle.test", "admin_password": "LifecyclePass123!", "department_id": "...", "position_id": "..."}
```

Idempotencia: usar `get_or_create` / `update_or_create` para todos los recursos. Re-ejecución no debe duplicar.

### Task 3 — Pytest smoke para el seed command

Crear `apps/api/apps/tenancy/tests/test_seed_lifecycle_e2e.py` (≥ 4 tests):
- ejecuta el comando, verifica que crea tenant + admin + department + position;
- re-ejecuta, verifica idempotencia (mismos IDs);
- verifica que admin login funciona con las credenciales sembradas;
- verifica que el output stdout parsea como JSON válido.

### Task 4 — Playwright lifecycle e2e

Crear `apps/web/tests/e2e/employment-lifecycle.test.js` siguiendo el patrón de `tenant-isolation.test.js`:

```js
const RUN = process.env.RUN_LIFECYCLE_E2E === '1';

test.describe('Employment Lifecycle (Module 03 full path)', () => {
  test.skip(!RUN, 'Heavy E2E; seed required. Set RUN_LIFECYCLE_E2E=1 + run seed_lifecycle_e2e first.');

  test('admin can drive an empleado through hire → onboarding → desplazamiento → cese', ...);
});
```

Steps que el test ejecuta (UI-driven, no API mocking):
1. **Login** como admin sembrado.
2. **Navegar a Empleados → Nuevo** y crear empleado (nombre, DNI dummy `99999999`, datos personales mínimos). Verificar redirect al detalle.
3. **Navegar a Contratos → Nuevo contrato**, seleccionar el empleado recién creado, llenar tipo `INDEFINIDO`, fecha inicio hoy, position FK al sembrado. Submit. Verificar que aparece en lista con status `vigente`.
4. **Navegar a Onboarding → Procesos** y disparar onboarding sobre ese empleado. Marcar al menos 1 step completado. Verificar progress > 0.
5. **Navegar a Desplazamiento → Nuevo** (Module 03.6 — B.13). Crear una rotación al mismo department (no-op semántico — el flujo importa). Verificar que se registra.
6. **Navegar a Desvinculación → Iniciar cese**. Causal `renuncia_voluntaria`, fecha hoy. Submit → status `in_progress`. Disparar `compute settlement` → verificar componentes (CTS + vac_truncas + grat_trunca) listados. Submit `complete` → status `completed`. Disparar `liquidate` con `paid_at=hoy` → status `liquidated`.
7. **Assertion final**: la página de detalle del empleado muestra "estado: cesado" o similar; el contrato muestra status `TERMINADO`.

Time budget: <3 min en CI gated; cada step usa `await page.waitForResponse` o `page.waitForSelector` con timeout específico (no `waitForTimeout` arbitrario). Selectors prefiere `getByRole` / `getByLabel` / `getByTestId` — no XPath.

Si una página no tiene `data-testid` para los selectors críticos, agregar `data-testid` en el componente como parte de esta tarea (mínimo invasivo).

### Task 5 — Documentación cómo ejecutar el lifecycle E2E

Crear `docs/operations/run-lifecycle-e2e.md` con:
- Prerequisites (DB local, dev servers running, hosts entry si se usa subdomain).
- Comando exacto:
  ```bash
  cd apps/api
  python manage.py seed_lifecycle_e2e --settings=vyntia.settings.development
  cd ../web
  RUN_LIFECYCLE_E2E=1 npx playwright test tests/e2e/employment-lifecycle.test.js
  ```
- Cómo limpiar tras correr el test (no hace falta — el seed es idempotente; pero documentar truncate manual si se quiere reset).
- Cómo interpretar fallos (trace + screenshot en `playwright-report/`).

### Task 6 — Docs sweep final del sub-proyecto B

Actualizar:

1. `docs/ROADMAP_SUBPROJECTS.md`:
   - Marcar **B (Vyntia Core Functional)** como ✅ COMPLETE con tag `b-vyntia-core-complete`.
   - Confirmar E + F absorbed in B (struck-through ya existente).
   - Próximo sub-proyecto: D (Vyntia Pay).

2. `CLAUDE.md`:
   - Active sub-project: pasar a "D — Vyntia Pay (planilla peruana real)" (status: not started, brainstorm pendiente).
   - Migration Roadmap: marcar B ✅ COMPLETE.
   - Test baselines: actualizar a los numbers finales post-B.16.

3. `README.md` (raíz):
   - Sección de estado del proyecto: 3 sub-proyectos completos (A, C, B). Próximo D.

4. `docs/superpowers/plans/2026-05-09-vyntia-B-vyntia-core-master-roadmap.md`:
   - Tabla de fases: todas en ✅ con merge SHA.
   - Sección "## Adjustments by audit" mantener; añadir "## Close-out" con la fecha + tag.

5. Crear `docs/superpowers/summaries/2026-05-19-vyntia-B-vyntia-core-summary.md` (nueva carpeta `summaries/` si no existe; modelar a Foundation summary si existe alguno, o estructura: timeline, módulos entregados, métricas, decisiones clave, lecciones, próximos pasos).

### Task 7 — Verificación baselines + memoria

Baselines a preservar (vs B.15b SHA `ce1534d1`):
- pytest: ≥ 978/1/17 (B.16 añade ≥ 4 tests del seed command → target ≥ 982).
- vitest: ≥ 28 files / 178 tests (B.16 no añade vitest tests — el lifecycle es Playwright, opt-in fuera de vitest).
- ESLint: ≤ 278 warnings.
- tsc: 1 (BlankEnum.ts pre-existing).
- Build: clean.
- `manage.py check`: 0 issues silenced.

Playwright lifecycle e2e: corre localmente con `RUN_LIFECYCLE_E2E=1` y completa los 7 pasos en <3 min sin flakes en 3 corridas consecutivas.

Actualizar memoria (`C:\Users\zeeke\.claude\projects\D--VYNTIA\memory\`):
- `subproject_b_progress.md`: B.16 close-out (5 commits + merge SHA + tag), métricas finales, mark B.16 ✅. Top-level state: "Sub-project B COMPLETE; next is D (Vyntia Pay)".
- `active_subproject.md`: flip a sub-proyecto D (status pending brainstorm).
- `test_baselines.md` (si existe): actualizar a los numbers finales post-B.16.

### Task 8 — Merge + tag

5 commits atómicos sugeridos (un commit por task lógico):
- `feat(B16): seed_lifecycle_e2e command + 4 tests` (Tasks 2-3).
- `test(B16): Playwright employment lifecycle E2E (opt-in)` (Task 4 — incluye los data-testid changes en componentes si aplican).
- `docs(B16): run-lifecycle-e2e operations guide` (Task 5).
- `docs(B16): sub-project B close-out — roadmap + summary + CLAUDE.md` (Task 6).
- `chore(B16): bump test baselines` (si el code review pide pequeños fixes).

Merge a master con `--no-ff` (sigue convención del sub-proyecto B). Mensaje de merge:
```
Merge B.16: E2E close-out + tag b-vyntia-core-complete

Sub-proyecto B (Vyntia Core Functional) COMPLETE — 17 fases mergeadas
2026-05-09 → 2026-05-19. 132 backlog items cerrados. Next: D (Vyntia Pay).
```

Tag annotated:
```
git tag -a b-vyntia-core-complete -m "Sub-project B complete — Vyntia Core functional. \
Modules 01 (Policies) + 02 (Positions/CCF/MPP/CPE) + 03 (Selección → cese) + \
cross-cutting polish across all 6 Core apps. Module 03 full lifecycle covered by \
opt-in Playwright e2e (tests/e2e/employment-lifecycle.test.js)."
```

## Risk register

- **Playwright flakiness**: el lifecycle test toca 7 páginas con submits async. Usar `page.waitForResponse(/api\/v1\/.../i)` para anclar cada paso a la respuesta real, no a timeouts. Mantener el test opt-in evita bloquear CI por flake.
- **Seed command + RLS**: el seed corre fuera del request cycle → tiene que usar `set_tenant_context` o equivalente C.0 para que las inserciones tengan tenant. Verificar el patrón con `seed_remuneraciones_config` (que también corre fuera de request).
- **Module 02 dependencies**: si Position viene de B.6 pero el modelo está en `apps.organization`, confirmar import path antes de seedearlo. Si Position aún no tiene seed defaults, sembrar inline en el comando.
- **Desplazamiento en step 5**: B.13 implementó rotación/encargatura/destaque — el test debe usar el flujo más simple (rotación al mismo department) para evitar dependencias adicionales. Si el form requiere más fields que no estén en el seed, sembrarlos también.
- **Severance compute en step 6**: ADR-B.9 dice "minimum legal scope". B.14 implementó 4 componentes (CTS + vac_truncas + grat_trunca + indemnización). Para causal `renuncia_voluntaria` no hay indemnización → el test debe esperar 3 líneas, no 4.
- **`b-vyntia-core-complete` tag colision**: verificar que no exista. `git tag | grep b-vyntia` debe estar vacío antes del tag final.
- **Docs sweep — over-scope**: limitar el sweep a los 5 docs listados en Task 6. No tocar specs históricos. No editar plan files de fases mergeadas.
- **Memoria stale**: el archivo `subproject_b_progress.md` tiene 200+ líneas. Append-only para B.16 close-out, no re-escribir histórico.

## Definition of Done

- [ ] `seed_lifecycle_e2e` corre limpio + tests pasan.
- [ ] `RUN_LIFECYCLE_E2E=1 npx playwright test employment-lifecycle.test.js` pasa local en 3 corridas consecutivas (zero flakes).
- [ ] pytest ≥ 982/1/17. vitest = 28/178. ESLint ≤ 278. tsc = 1. Build clean. manage.py check 0 silenced.
- [ ] Docs actualizadas (5 archivos enumerados en Task 6).
- [ ] Summary nuevo creado en `docs/superpowers/summaries/`.
- [ ] Merge `--no-ff` a master con mensaje correcto.
- [ ] Tag `b-vyntia-core-complete` creado y verificable con `git tag -v`.
- [ ] Memoria actualizada (`subproject_b_progress.md` + `active_subproject.md`).
