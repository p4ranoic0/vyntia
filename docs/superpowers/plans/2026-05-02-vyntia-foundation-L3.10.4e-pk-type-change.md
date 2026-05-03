# VYNTIA Foundation L3.10.4e — Frontend PK Type Change Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename + retype all 22 entities' frontend interfaces from `<entity>_id: number` to `id: string` (UUID), fix the normalizers that silently coerce UUIDs to 0, update all 235+ consumer references, retype outbound POST/PATCH payloads, and verify with curl smoke.

**Architecture:** Big-bang single-PR refactor. TypeScript compiler enumerates the blast radius via `npm run build`. Four atomic commits — plan, normalizer rewrite, interface+consumer rename, outbound+parseInt cleanup. Backend already routes UUID PKs end-to-end (post-L3.10.4a), so this is frontend-only.

**Tech Stack:** TypeScript 5.x + React 18 + Vite (frontend). Django 5.2 + DRF (backend, no changes). curl + jq (smoke).

**Spec source:** `docs/superpowers/specs/2026-05-02-vyntia-foundation-L3.10.4e-pk-type-change-design.md` (commit `a0e443ad`).

**Audit source:** `docs/superpowers/research/api-contract-audit.md` § "L3.10.4e action plan" (lines 1689-1733).

**Pre-conditions:**
- Branch `master` clean at HEAD = `a0e443ad docs(L3.10.4e): add PK type change design spec`
- Backend pytest baseline: 161 passed, 8 failed, 3 skipped
- Frontend `npm run build` clean
- Frontend vitest: 7 passed, 1 file load failure (pre-existing)
- Backend Django 5.2.13 + bd_vyntia provisioned
- Virtualenv at `D:/VYNTIA/.venv/`

**Scope (this plan only):**
- Frontend TS interfaces: 96 declarations `<entity>_id: number` → `id: string` (where read-shape) or retype to `string` keeping key (where outbound form)
- Frontend consumers: 235 `.entity_id` accesses → `.id`
- Frontend object literals: 133 `entity_id:` entries — retype value to string (outbound) or rename key to `id` (read-shape) — TS-driven case-by-case
- Frontend normalizers: 4 ID-coercing functions in `apiNormalizers.ts` — `getNumber → getString`, drop duplicate `<entity>_id` emit
- Frontend `parseInt`/`Number()` removals: 6 sites total (4 in normalizer + 2 in consumers)
- Backend: NO CHANGES (only frontend)

**Out of scope (separate sub-PRs):**
- Backend serializer bugs from audit § "Out-of-scope discoveries" (RolPermisos duplicate `id`, vacation `source='contrato.contrato_id'`, validator stale fields)
- `creado_por_nombre` / `modificado_por_nombre` SerializerMethodField name mismatches (4c leftover)
- `Permission.modulo` typing irregularity (free-form string ID, not UUID FK)
- Three duplicate `Role` interfaces consolidation (`lib/api.ts` + `usersService.ts` + `securityService.ts`)
- `apps/web/src/generated/` (auto-generated)

---

## File Structure

Files modified (frontend only — `D:/VYNTIA/apps/web/src/`):

| File | Responsibility | Why touched |
|---|---|---|
| `services/normalizers/apiNormalizers.ts` | Read-shape adapter — bridges backend variation to canonical TS shapes | `getNumber→getString`, drop duplicate `<entity>_id` emit (4 functions) |
| `services/employeesService.ts` | Employee + nested datos types (Laborales, Familiares, Académicos) | Interfaces 1-4 from spec matrix |
| `services/departmentsService.ts` | Department/Area | Interface 5 |
| `services/usersService.ts` | User, Role, Permission shapes for /admin pages | Interfaces 6-8 |
| `services/securityService.ts` | Role, Permission, RolePermission shapes for security console | Same entities, different consumer |
| `services/contractsService.ts` | Contract + ContratoListItem + filters | Interface 12-13 |
| `services/legajoService.ts` | DigitalDocument | Interface 18 |
| `services/templatesService.ts` | DocumentTemplate | Interface 19 |
| `services/payrollService.ts` | 8 payroll entities (Compensation, Afp, UIT, MonthlyPayroll, Detail, MassDeduction, Payslip, PaymentSchedule) | Interfaces 20-28 |
| `services/timeOffService.ts` | 4 vacation entities (Config, Period, Request, Grant) | Interfaces 29-32 |
| `services/onboardingService.ts` | OnboardingStatus | Interface 33 |
| `services/authService.ts` | Auth shapes (User-related sessionData) | usuario_id, empleado_id, area_id, rol_id, permiso_id, modulo_id |
| `lib/api.ts` | Common API typing (User in api.ts) | usuario_id + nested empleado.area.id |
| `hooks/useRemuneraciones.ts` | Filter param interfaces for payroll hooks | filter param `_id` types |
| (consumer files — TS-driven) | Pages, components, features that read or write entity IDs | Property accesses `.entity_id` and outbound payloads |

**Approximate consumer files** (TS compiler enumerates exact list during execution):
- `pages/Empleados.tsx`, `pages/empleados/*`, `pages/HROverviewDashboard.tsx`
- `pages/contratos/ContratosPage.tsx`
- `pages/legajo/*`
- `pages/remuneraciones/*` (5 files)
- `pages/vacaciones/*` (3 files)
- `pages/seguridad/*` (Role/Permission admin)
- `components/empleados/Tab*.tsx` (3 files)
- `components/vacaciones/*`
- `features/empleados/*` (example/integration files)
- `features/onboarding/types/onboarding.ts`

---

## Definition of Done

- [ ] All 22 entities renamed per spec matrix (33 interface rows)
- [ ] `apiNormalizers.ts`: `getNumber → getString` (4 functions); duplicate `<entity>_id` emission dropped
- [ ] All 6 `parseInt(...)` / `Number(...)` calls on `_id` removed
- [ ] All 235 `.entity_id` property accesses migrated to `.id` (TS-driven)
- [ ] Outbound object-literal payloads retyped to string (key names preserved)
- [ ] Cross-entity nested refs propagated (`User.empleado.id`, `Contract.empleado.id`, etc.)
- [ ] `manage.py check` clean
- [ ] `npm run build` clean (no TS errors)
- [ ] `npm run lint` 0 net new errors vs master baseline
- [ ] vitest 7 passed (1 file load failure preserved)
- [ ] pytest baseline 161/8/3 preserved
- [ ] curl smoke: 5 endpoints return UUID `id` strings + 1 PATCH succeeds
- [ ] Branch `vyntia/L3.10.4e-pk-uuid` merged to master with `--no-ff`
- [ ] Roadmap updated: L3.10.4e ✅, L3.11 marked NEXT
- [ ] Memory `active_subproject.md` updated with merge commit + LR23+ if any new lessons

---

## Task 1: Pre-flight — branch, baseline, snapshot

- [ ] **Step 1: Confirm pwd + master clean state**

```bash
cd D:/VYNTIA
git status --short
git log --oneline -5
```

Expected: HEAD = `a0e443ad docs(L3.10.4e): add PK type change design spec`. Working tree clean.

- [ ] **Step 2: Backend baseline (capture pytest output for diff later)**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tee /tmp/pytest_baseline_4e.txt | tail -3
cd D:/VYNTIA
```

Expected: `System check identified no issues` + `161 passed, 8 failed, 3 skipped`.

- [ ] **Step 3: Frontend build baseline**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: build success.

- [ ] **Step 4: Frontend tests baseline**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: `Tests 7 passed (7)`, `Test Files 1 failed | 2 passed (3)`.

- [ ] **Step 5: Snapshot baseline counts**

```bash
cd D:/VYNTIA/apps/web

echo "=== <entity>_id: number declarations (target post-PR: 0) ==="
grep -rEn "^\s+[a-z_]+_id\??\s*:\s*number" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l

echo ""
echo "=== .entity_id property accesses (target post-PR: 0) ==="
grep -rEn "\.[a-z_]+_id\b" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l

echo ""
echo "=== entity_id: object literal property entries ==="
grep -rEn "[^.]\b[a-z_]+_id\s*:" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l

echo ""
echo "=== parseInt/Number() on _id (target post-PR: 0) ==="
grep -rEn "parseInt\([a-zA-Z_.]+_id|Number\([a-zA-Z_.]+_id" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l

cd D:/VYNTIA
```

Expected snapshot (current baseline):
- `<entity>_id: number`: **96**
- `.entity_id` accesses: **235**
- `entity_id:` literals: **133**
- `parseInt/Number(_id)`: **6**

Document any deviation from these numbers.

- [ ] **Step 6: Capture lint baseline**

```bash
cd D:/VYNTIA/apps/web
npm run lint 2>&1 | grep -E "^\s*[0-9]+:[0-9]+" | wc -l > /tmp/lint_baseline_4e.txt
cat /tmp/lint_baseline_4e.txt
cd D:/VYNTIA
```

Document this number — used for delta comparison post-PR.

- [ ] **Step 7: Create branch**

```bash
cd D:/VYNTIA
git checkout -b vyntia/L3.10.4e-pk-uuid
git status --short
```

Expected: on branch `vyntia/L3.10.4e-pk-uuid`, clean working tree.

---

## Task 2: Commit the plan

- [ ] **Step 1: Stage the plan file**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-02-vyntia-foundation-L3.10.4e-pk-type-change.md
```

- [ ] **Step 2: Commit**

```bash
git commit -m "$(cat <<'EOF'
docs(L3.10.4e): add PK type change implementation plan

Step-by-step plan for the big-bang frontend refactor: 22 entities
renamed/retyped (<entity>_id: number → id: string) + normalizer fix +
consumer + outbound + curl smoke. Predecessor: L3.10.4d c7be13c2.

Spec: 2026-05-02-vyntia-foundation-L3.10.4e-pk-type-change-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 3: Verify**

```bash
git log --oneline -3
```

Expected: HEAD on branch with `docs(L3.10.4e): add PK type change implementation plan`.

---

## Task 3: Normalizer rewrite — `apiNormalizers.ts`

**File:**
- Modify: `apps/web/src/services/normalizers/apiNormalizers.ts`

**Goal:** `getNumber → getString` for ID coercion paths; drop duplicate `<entity>_id` emission from output.

- [ ] **Step 1: Read the current file**

```bash
cat D:/VYNTIA/apps/web/src/services/normalizers/apiNormalizers.ts
```

Confirm the structure matches:
- `getNumber` defined at line 12-13
- `normalizeRole` at line 23-45 — has `roleId = getNumber(...)` and `rol_id: roleId` in output
- `normalizeUser` at line 61-90 — has `userId = getNumber(...)` and `usuario_id: userId` in output
- `normalizeEmployee` at line 92-128 — has `employeeId = getNumber(...)` and `empleado_id: employeeId` in output, AND `getNumber(ubicacionActual.area_id)` at line 118

If structure has drifted, adjust the edits below to match actual line numbers.

- [ ] **Step 2: Edit `normalizeRole` — getNumber→getString + drop rol_id duplicate**

Use Edit tool:
- File: `apps/web/src/services/normalizers/apiNormalizers.ts`
- old:
  ```
  export const normalizeRole = (role: unknown) => {
    const roleObj = asRecord(role);
    const roleId = getNumber(roleObj.rol_id ?? roleObj.id);
    const isActive = roleObj.is_active === true;
    const estadoRol = getString(
      roleObj.estado_rol,
      isActive ? "activo" : "inactivo",
    );

    return {
      id: roleId,
      rol_id: roleId,
      nombre_rol: getString(roleObj.nombre_rol ?? roleObj.nombre),
  ```
- new:
  ```
  export const normalizeRole = (role: unknown) => {
    const roleObj = asRecord(role);
    const roleId = getString(roleObj.rol_id ?? roleObj.id);
    const isActive = roleObj.is_active === true;
    const estadoRol = getString(
      roleObj.estado_rol,
      isActive ? "activo" : "inactivo",
    );

    return {
      id: roleId,
      nombre_rol: getString(roleObj.nombre_rol ?? roleObj.nombre),
  ```

- [ ] **Step 3: Edit `normalizeUser` — getNumber→getString + drop usuario_id duplicate**

- File: `apps/web/src/services/normalizers/apiNormalizers.ts`
- old:
  ```
    const userObj = asRecord(user);
    const userId = getNumber(userObj.usuario_id ?? userObj.id);
  ```
- new:
  ```
    const userObj = asRecord(user);
    const userId = getString(userObj.usuario_id ?? userObj.id);
  ```

Then drop the duplicate output line:
- old:
  ```
    return {
      id: userId,
      usuario_id: userId,
      username: getString(userObj.username ?? userObj.nombre_usuario),
  ```
- new:
  ```
    return {
      id: userId,
      username: getString(userObj.username ?? userObj.nombre_usuario),
  ```

- [ ] **Step 4: Edit `normalizeEmployee` — getNumber→getString + drop empleado_id duplicate + ubicacionActual.area_id**

- File: `apps/web/src/services/normalizers/apiNormalizers.ts`
- old:
  ```
    const employeeObj = asRecord(employee);
    const ubicacionActual = asRecord(employeeObj.ubicacion_actual);
    const employeeId = getNumber(employeeObj.empleado_id ?? employeeObj.id);

    return {
      id: employeeId,
      empleado_id: employeeId,
      nombres: getString(employeeObj.nombres_empleado ?? employeeObj.nombres),
  ```
- new:
  ```
    const employeeObj = asRecord(employee);
    const ubicacionActual = asRecord(employeeObj.ubicacion_actual);
    const employeeId = getString(employeeObj.empleado_id ?? employeeObj.id);

    return {
      id: employeeId,
      nombres: getString(employeeObj.nombres_empleado ?? employeeObj.nombres),
  ```

Then the inner `area` reconstruction:
- old:
  ```
              id: getNumber(ubicacionActual.area_id),
              organo: getString(ubicacionActual.area_nombre),
              siglas: getString(ubicacionActual.area_siglas),
  ```
- new:
  ```
              id: getString(ubicacionActual.area_id),
              organo: getString(ubicacionActual.area_nombre),
              siglas: getString(ubicacionActual.area_siglas),
  ```

- [ ] **Step 5: Remove now-unused `getNumber` declaration**

After steps 2-4, `getNumber` should have zero usages. Verify:

```bash
grep -n "getNumber" D:/VYNTIA/apps/web/src/services/normalizers/apiNormalizers.ts
```

Expected: 1 line (the declaration). If 0 lines, already gone. If >1, find the missed usage and convert to `getString`.

If `getNumber` is unused, delete its declaration:
- File: `apps/web/src/services/normalizers/apiNormalizers.ts`
- old:
  ```
  const getNumber = (value: unknown, fallback = 0): number =>
    typeof value === "number" ? value : fallback;
  ```
- new: (empty — delete the two lines)

(Keep `getString`, `asRecord`, `asArray`, `extractCollection` — they're still used.)

- [ ] **Step 6: Verify normalizer file compiles in isolation**

```bash
cd D:/VYNTIA/apps/web
npx tsc --noEmit src/services/normalizers/apiNormalizers.ts 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: no errors specific to this file. (May still report errors in importing files — that's expected and Task 4+ will fix them.)

- [ ] **Step 7: Run full build to enumerate downstream errors**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tee /tmp/tsc_after_normalizer.txt | tail -30
cd D:/VYNTIA
```

Expected: build FAILS with TS errors. Common patterns:
- `Property 'rol_id' does not exist on type` (consumers reading `.rol_id` from normalizer output)
- `Property 'usuario_id' does not exist on type` (consumers reading `.usuario_id` from normalizeUser)
- `Property 'empleado_id' does not exist on type` (consumers reading `.empleado_id` from normalizeEmployee)
- Any consumer that compares the normalizer output ID to a number literal will fail

Capture the error count for reference but DO NOT fix consumers in this task — they get fixed in Task 4 alongside their interface renames.

- [ ] **Step 8: Commit (foundational change — even though build is broken)**

This is a deliberate intermediate state. The next commits will resolve TS errors. The plan documents this; reviewers will see the chain.

```bash
cd D:/VYNTIA
git add apps/web/src/services/normalizers/apiNormalizers.ts
git diff --cached --stat | tail -3
git commit -m "$(cat <<'EOF'
chore(L3.10.4e): normalizer rewrite — getString + drop duplicate _id emit

Foundational change for PK type rename (L3.10.4e). Backend post-L3.10.2
emits id as UUID string but normalizer was silently coercing via
getNumber (returning 0). Switch to getString throughout the 4 ID-coerce
paths (normalizeRole, normalizeUser, normalizeEmployee, ubicacionActual.area_id).

Also drops the duplicate <entity>_id field emission from the normalized
output (keeps only id) — forces TS to enumerate consumers that still
read the legacy alias. Subsequent commits in this PR fix those consumers
plus retype their interfaces.

INTERMEDIATE STATE: TS build is broken after this commit. Resolved by
the interface + consumer rename commit that follows.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git log --oneline -3
```

---

## Task 4: Service interface renames

**Approach:** edit each service file's interfaces, then run `npm run build` to enumerate consumer errors and fix them. Repeat per service file. All commits collapse into one logical change (one commit at end of Task 5).

The order processes files from least cross-referenced (leaf entities) to most (Employee/User which appear nested in many other entities). Within each step, leverage the spec matrix in `2026-05-02-vyntia-foundation-L3.10.4e-pk-type-change-design.md` for exact rename mapping.

- [ ] **Step 1: Rename `templatesService.ts` (DocumentTemplate)**

```bash
grep -nE "^\s+[a-z_]+_id\??\s*:\s*number" D:/VYNTIA/apps/web/src/services/templatesService.ts
```

Expected: `plantilla_id: number` near line 11.

Edit:
- File: `apps/web/src/services/templatesService.ts`
- old: `  plantilla_id: number;`
- new: `  id: string;`

If interface also has `id: number` already (unlikely but possible), prefer rename `plantilla_id → id` and retype to `string`. Verify by reading 5 lines of context.

- [ ] **Step 2: Rename `departmentsService.ts` (Department/Area)**

```bash
grep -nE "^\s+[a-z_]+_id\??\s*:\s*number" D:/VYNTIA/apps/web/src/services/departmentsService.ts
```

Expected: `area_id: number` at ~line 5.

Edit:
- File: `apps/web/src/services/departmentsService.ts`
- old: `  area_id: number;` (or with optional `?`)
- new: `  id: string;`

Verify with grep that no other `<entity>_id: number` remains in this file.

- [ ] **Step 3: Rename `legajoService.ts` (DigitalDocument)**

```bash
grep -nE "[a-z_]+_id\s*:" D:/VYNTIA/apps/web/src/services/legajoService.ts | head -10
```

Expected: `documento_id: number`, plus possibly nested `subido_por`, `validado_por` (these may or may not be present as `_id` types — read context).

For each `<entity>_id: number` declaration in interfaces:
- `documento_id: number` → `id: string`
- Nested `subido_por: { ... }` and `validado_por: { ... }` — if their `id` field is `number`, retype to `string`
- Any `empleado: { id: number; ... }` nested ref → `id: string`

Use Edit tool with multi-line context anchor for each interface.

- [ ] **Step 4: Rename `onboardingService.ts` (OnboardingStatus)**

Audit § 30 says: `onboarding_id, empleado, usuario, validado_por` → all string.

```bash
grep -nE "[a-z_]+_id\s*:\s*number" D:/VYNTIA/apps/web/src/services/onboardingService.ts | head -10
```

Edit the interface(s) at the matched lines:
- `onboarding_id: number` → `id: string`
- Nested `empleado.id: number` → `string`
- Nested `usuario.id: number` → `string`
- Nested `validado_por.id: number` → `string`

- [ ] **Step 5: Rename `securityService.ts` (Role, Permission, RolePermission)**

```bash
grep -nE "[a-z_]+_id\s*:\s*number" D:/VYNTIA/apps/web/src/services/securityService.ts | head -15
```

Per audit § "L3.10.4e action plan" line 1723: all `_id: number → id: string`. Multiple interfaces in this file (Role, Permission, RolePermission). Walk each interface, rename per spec matrix.

Note: this file may consume normalizers — check for `.rol_id` / `.permiso_id` reads that came from the normalizer output (which we dropped in Task 3). Those reads must change to `.id`.

- [ ] **Step 6: Rename `usersService.ts` (User, Role, Permission)**

```bash
grep -nE "[a-z_]+_id\s*:\s*number" D:/VYNTIA/apps/web/src/services/usersService.ts | head -15
```

Per audit lines 1701-1703:
- User interface: `id, usuario_id, empleado.id, empleado.area.id` → all string. **Drop** the `usuario_id` redundant field (was paper-cracking the legacy alias).
- Role interface: `id, rol_id` → string. Drop `rol_id`.
- Permission interface: `id, permiso_id` → string. Drop `permiso_id`.

Three interfaces. Walk each.

- [ ] **Step 7: Rename `lib/api.ts` (User in api.ts)**

```bash
grep -nE "[a-z_]+_id\??\s*:\s*number" D:/VYNTIA/apps/web/src/lib/api.ts | head -15
```

Per audit line 1721: `id, usuario_id, empleado.id, empleado.area.id, roles[].id, permisos[].id` → all string. Drop `usuario_id`.

- [ ] **Step 8: Rename `authService.ts`**

```bash
grep -nE "[a-z_]+_id\??\s*:\s*number" D:/VYNTIA/apps/web/src/services/authService.ts | head -15
```

Expected (from baseline grep): `usuario_id, empleado_id, area_id, rol_id, permiso_id, modulo_id` — multiple session-related shape fields.

For each: retype `: number → : string`. **Note:** these fields are session/auth context, the `_id` suffix is the field NAME from backend response. The backend session payload may emit them by these specific names. For READ side, retype value to string. Do NOT rename `usuario_id` → `id` here (it's a session token claim, not a primary entity ID).

- [ ] **Step 9: Rename `contractsService.ts` (Contract + ContratoListItem + filters)**

Per audit lines 1704-1705: 2 interfaces (Contrato, ContratoListItem) + ContratoFilters. Multiple `_id: number` declarations including nested.

```bash
grep -nE "[a-z_]+_id\??\s*:\s*number" D:/VYNTIA/apps/web/src/services/contractsService.ts | head -15
```

Walk each:
- `contrato_id: number` → `id: string`
- Nested `empleado: { empleado_id: number; ... }` → `{ id: string; ... }`
- Nested `area: { area_id: number; ... }` → `{ id: string; ... }`
- `area_detalle.area_id` → `area_detalle.id` (string)
- `ContratoFilters.empleado_id?: number` → consider: this is a query parameter sent to backend. If backend filter accepts UUID, retype to `: string`. **Important:** the L3.10.4d post-review fix at commit `75d590f7` reverted some `ContratoFilters` field types to Spanish — preserve those. Read the file carefully before editing.

- [ ] **Step 10: Rename `payrollService.ts` (8 entities)**

Most complex file. Per audit lines 1708-1715, 8 entities × multiple nested refs.

```bash
grep -nE "[a-z_]+_id\??\s*:\s*number" D:/VYNTIA/apps/web/src/services/payrollService.ts
```

Per audit:
- ConfiguracionRemuneracion (Compensation): `configuracion_id → id`
- ConfiguracionAfp: `afp_config_id → id`
- ConfiguracionUit: `configuracion_uit_id → id`, also `created_by` nested
- PlanillaMensual: `planilla_id → id`
- DetallePlanilla: `detalle_id → id`, plus nested `planilla.planilla_id → planilla.id` and `empleado.empleado_id → empleado.id`
- DescuentoMasivo: `descuento_masivo_id → id`, plus nested
- BoletaPago: `boleta_id → id`, plus `detalle_planilla.detalle_id → detalle_planilla.id`, `empleado.empleado_id → empleado.id`
- CalendarioPago: `calendario_id → id`, plus `created_by.usuario_id → created_by.id`

Walk each interface; use Edit with full multi-line context to disambiguate (multiple interfaces with similar nested shapes).

- [ ] **Step 11: Rename `timeOffService.ts` (4 entities)**

```bash
grep -nE "[a-z_]+_id\??\s*:\s*number" D:/VYNTIA/apps/web/src/services/timeOffService.ts
```

Per audit lines 1716-1719:
- ConfiguracionVacaciones: `configuracion_id → id`
- PeriodoVacacional: `id, periodo_id, empleado, contrato, contrato_id` — all string. Drop redundant `periodo_id`.
- SolicitudVacaciones: `id, solicitud_id, empleado.id, periodo_vacacional.id` — all string. Drop `solicitud_id`.
- GoceVacaciones: `goce_id → id`, nested `empleado, solicitud_vacaciones, periodo_vacacional` → string.

- [ ] **Step 12: Rename `employeesService.ts` (Employee + Datos types)**

LAST and most cross-referenced (Employee appears nested in many other entities).

```bash
grep -nE "[a-z_]+_id\??\s*:\s*number" D:/VYNTIA/apps/web/src/services/employeesService.ts
```

Per audit lines 1696-1700:
- Employee: `id: number → id: string`
- DatosLaborales: `id?, empleado_id, area_id, supervisor_id` → all string
- DatosFamiliares: `id?, empleado_id` → string
- DatosAcademicos: `id?, empleado_id` → string

The `empleado_id` and `area_id` fields here are FK references inside DatosLaborales/etc. — they're outbound to backend AND read from backend. Retype to string, **keep the key name** (per D3 — outbound payload key names preserved).

- [ ] **Step 13: Rename `hooks/useRemuneraciones.ts`**

```bash
grep -nE "[a-z_]+_id\??\s*:\s*number" D:/VYNTIA/apps/web/src/hooks/useRemuneraciones.ts | head -10
```

This file has filter param types and possibly hook-internal interfaces. For each `_id: number`, retype to `string`. Filter params sent as query strings to backend already serialize string→string fine.

- [ ] **Step 14: Build and capture remaining errors**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tee /tmp/tsc_after_interfaces.txt | tail -50
cd D:/VYNTIA
```

Expected: many TS errors of the form:
- `Property 'empleado_id' does not exist on type 'Employee'. Did you mean 'id'?`
- `Type 'number' is not assignable to type 'string'.`
- `This comparison appears to be unintentional because the types 'string' and 'number' have no overlap.`

These are the consumers needing fixes. Continue to Task 5.

---

## Task 5: Consumer fixes (TS-driven)

**Approach:** iterate `npm run build` to enumerate errors, fix per error, repeat until clean.

- [ ] **Step 1: Inventory error sites**

```bash
grep -E "error TS[0-9]+" /tmp/tsc_after_interfaces.txt | head -100
grep -E "error TS[0-9]+" /tmp/tsc_after_interfaces.txt | sed -E 's|^([^:]+):.*|\1|' | sort -u
```

The second command lists unique files with errors. Use this as the work queue.

- [ ] **Step 2: Fix each consumer file**

For each file in the work queue, apply this pattern:

a. Read the file region where errors occur.
b. Identify the error type:
   - **Property does not exist on type X. Did you mean 'id'?** → consumer was reading `.entity_id`. Change to `.id`. Use Edit with line context; if multiple sites in same file with same access pattern, consider `replace_all` carefully.
   - **Type 'number' is not assignable to type 'string'** → consumer was passing a number literal or `Number(...)` value. Drop the `Number(...)` call or change literal to string. If literal is a placeholder like `0` (form initial state), change to `""` empty string.
   - **Comparison string vs number** → consumer was comparing `.id === 5` or similar. Change to string equality (`.id === "5"` or pass UUID directly).

c. After each file edit, run build again to confirm:

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -20 && cd D:/VYNTIA
```

If errors resolved for that file → proceed to next. If new errors appear → continue iterating.

- [ ] **Step 3: Common consumer patterns to fix**

Watch for these specific patterns (sample sites from baseline grep):

**Pattern 1: `.empleado_id` or `.usuario_id` on entity**
- `pages/Empleados.tsx:317` — `empleado.empleado_id` → `empleado.id`
- `pages/empleados/EmpleadoReportPage.tsx:32` — interface field `empleado_id: number`. If this is for a local form, retype to string. If reading from API, switch to `.id`.

**Pattern 2: `useState<number | null>` for entity selection**
```typescript
// Before:
const [selectedId, setSelectedId] = useState<number | null>(null)
setSelectedId(empleado.empleado_id)

// After:
const [selectedId, setSelectedId] = useState<string | null>(null)
setSelectedId(empleado.id)
```

**Pattern 3: URL builders with template literal**
```typescript
// Before (still works runtime, but TS may flag):
api.get(`/api/v1/employees/${empleado.empleado_id}/`)

// After:
api.get(`/api/v1/employees/${empleado.id}/`)
```

**Pattern 4: Object spread / form submit payloads**
```typescript
// Before:
mutate({ empleado_id: empleado.empleado_id, area_id: form.area_id })

// After (key name preserved per D3, value comes from .id):
mutate({ empleado_id: empleado.id, area_id: form.area_id })
```

Note: the OUTBOUND key (`empleado_id`) stays as the key name. The VALUE source switches from `.empleado_id` (no longer exists) to `.id`. The mutation payload TYPE will be retyped in Task 6.

**Pattern 5: `.find(e => e.id === someId)`**
String equality works the same syntactically; just ensure both sides are strings now.

**Pattern 6: Zod schemas**
- `pages/vacaciones/ConfiguracionPage.tsx:68` — `empleado_id: z.number().min(1, ...)` → `empleado_id: z.string().uuid({ message: 'Empleado requerido' })` or `z.string().min(1, ...)`. Choose based on whether validation should require UUID format.

- [ ] **Step 4: Local form-state interfaces**

Files with locally-declared interfaces that mirror entity shapes:
- `components/empleados/TabPersonales.tsx:16` — `empleado_id: number` interface field. Retype to `string`. If this is a prop type, ensure all callers pass string.
- `pages/empleados/DatosPersonalesPage.tsx:18` — same pattern
- `pages/empleados/EmpleadoReportPage.tsx:32, 54, 70, 89` — multiple local interfaces with nested `_id: number`. Retype each.
- `features/empleados/INTEGRATION_EXAMPLE.ts`, `REACT_QUERY_EXAMPLE.ts` — example/teaching files. Retype to keep them coherent. (If they're documentation samples, no functional impact.)
- `features/onboarding/types/onboarding.ts:28, 38, 58` — onboarding-specific shapes. Retype.

- [ ] **Step 5: Rebuild and verify clean**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -10
cd D:/VYNTIA
```

Expected: build success.

If errors remain that are NOT related to `_id` rename (e.g., a pre-existing TS issue surfaced by the changes), document them and decide case-by-case. Ideally 0 new errors related to this PR.

- [ ] **Step 6: Verify normalizer + interface counts**

```bash
cd D:/VYNTIA/apps/web

echo "=== <entity>_id: number declarations remaining ==="
grep -rEn "^\s+[a-z_]+_id\??\s*:\s*number" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l

echo ""
echo "=== .entity_id property accesses remaining ==="
grep -rEn "\.[a-z_]+_id\b" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l

cd D:/VYNTIA
```

Expected:
- `<entity>_id: number` declarations: should drop significantly. The remainders are likely outbound form payload types (handled in Task 6) or false-positive matches in non-FK contexts (like `tracking_id: number` for an internal counter — these stay).
- `.entity_id` accesses: should drop to ~0 or to a small remainder of legitimate non-FK uses (e.g., `request_id`, `correlation_id` type fields that are unrelated to entity PKs).

If counts are unexpectedly high, investigate before continuing.

- [ ] **Step 7: Commit interface + consumer rename**

```bash
cd D:/VYNTIA
git add apps/web/
git diff --cached --stat | tail -10
git commit -m "$(cat <<'EOF'
chore(L3.10.4e): interface renames + consumer access patterns

Renames frontend TS interface fields from <entity>_id: number to
id: string for all 22 entities with UUID PKs (post-L3.10.2 backend).
TypeScript-driven consumer fixes update all .entity_id property reads
to .id across pages/, components/, features/, hooks/.

Service interfaces touched (33 interface rows):
- employeesService: Employee, DatosLaborales, DatosFamiliares, DatosAcademicos
- departmentsService: Department/Area
- usersService: User, Role, Permission
- securityService: Role, Permission, RolePermission
- contractsService: Contract, ContratoListItem
- legajoService: DigitalDocument
- templatesService: DocumentTemplate
- payrollService: Compensation, Afp, UIT, MonthlyPayroll, Detail,
  MassDeduction, Payslip, PaymentSchedule
- timeOffService: VacationConfig, Period, Request, Grant
- onboardingService: OnboardingStatus
- authService: session shapes (usuario_id, empleado_id, area_id,
  rol_id, permiso_id, modulo_id retyped to string)
- lib/api.ts: User in api.ts
- hooks/useRemuneraciones.ts: filter params

Consumers fixed: per-file via TS error inventory (npm run build).
Drops legacy <entity>_id alias from normalizer output (was paper-
cracking the dead field).

Out of scope (next commit): outbound payload types + parseInt/Number
removals.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git log --oneline -3
```

---

## Task 6: Outbound payloads + parseInt/Number removals

**Goal:** retype outbound POST/PATCH payload types from `: number` to `: string` (keeping key names per D3); remove the 6 `parseInt`/`Number` calls.

- [ ] **Step 1: Inventory remaining `_id: number` (outbound types)**

```bash
cd D:/VYNTIA/apps/web
grep -rEn "[a-z_]+_id\??\s*:\s*number" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated
cd D:/VYNTIA
```

Expected: a remainder of outbound mutation payload types and form-state types not yet touched. Examples from baseline:
- `pages/contratos/ContratosPage.tsx:672` — `mutationFn: (data: { empleado_id: number; ...})`
- `pages/empleados/DatosPersonalesPage.tsx:72` — payload object
- `pages/Empleados.tsx:87` — `area_id: number` form state
- `pages/HROverviewDashboard.tsx:57, 67` — `area_id`, `planilla_id`
- `components/empleados/TabLaborales.tsx:30, 50, 107` — form state `area_id: ''`

For each: retype to `string`, **keep the key name** (per D3).

- [ ] **Step 2: Edit each remaining outbound site**

Per file:

**Example: `pages/contratos/ContratosPage.tsx:672`**

- File: `apps/web/src/pages/contratos/ContratosPage.tsx`
- old: `    mutationFn: (data: { empleado_id: number; proposito?: string; incluir_salario?: boolean }) =>`
- new: `    mutationFn: (data: { empleado_id: string; proposito?: string; incluir_salario?: boolean }) =>`

**Example: `pages/Empleados.tsx:87`**

- File: `apps/web/src/pages/Empleados.tsx`
- Read context first (line 80-95) to identify if this is a form-state interface or a backend response shape.
- If form-state: retype `area_id: number` → `area_id: string`.

For form initial values that were `area_id: 0`, change to `area_id: ''` (empty string is the equivalent of "not selected" for UUID).

Repeat for all sites in the inventory.

- [ ] **Step 3: Remove `parseInt`/`Number()` calls on `_id` fields**

The 6 sites:

a. `apps/web/src/components/empleados/TabLaborales.tsx:81`

```bash
grep -n "Number(form.area_id" D:/VYNTIA/apps/web/src/components/empleados/TabLaborales.tsx
```

Read line 75-90 for context. The pattern is something like:
```typescript
area: form.area_id ? Number(form.area_id) : undefined,
```

Edit:
- old: `        area: form.area_id ? Number(form.area_id) : undefined,`
- new: `        area: form.area_id || undefined,`

(UUID strings flow through unchanged; empty string `''` is falsy.)

b. `apps/web/src/pages/vacaciones/NuevaSolicitudPage.tsx:323`

```bash
grep -n "parseInt(data.periodo_vacacional_id" D:/VYNTIA/apps/web/src/pages/vacaciones/NuevaSolicitudPage.tsx
```

Read line 315-330 for context. Pattern:
```typescript
periodo_vacacional_id: parseInt(data.periodo_vacacional_id),
```

Edit:
- old: `        periodo_vacacional_id: parseInt(data.periodo_vacacional_id),`
- new: `        periodo_vacacional_id: data.periodo_vacacional_id,`

c-f. The 4 normalizer sites were already handled in Task 3 by `getString` conversion.

- [ ] **Step 4: Verify all parseInt/Number on _id removed**

```bash
cd D:/VYNTIA/apps/web
grep -rEn "parseInt\([a-zA-Z_.]+_id|Number\([a-zA-Z_.]+_id" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated
cd D:/VYNTIA
```

Expected: 0 results.

- [ ] **Step 5: Build verification**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -10
cd D:/VYNTIA
```

Expected: build success.

- [ ] **Step 6: Commit outbound + parseInt cleanup**

```bash
cd D:/VYNTIA
git add apps/web/
git diff --cached --stat | tail -10
git commit -m "$(cat <<'EOF'
chore(L3.10.4e): outbound payload retype + parseInt/Number removals

Retypes outbound mutation/form payload types from <entity>_id: number
to <entity>_id: string (key names preserved per D3 — backend tolerates
the alias or reads via request.data.get). Removes the 6 parseInt/
Number() coercion calls on _id fields:
- 4 in apiNormalizers.ts (handled in earlier commit via getString)
- TabLaborales.tsx:81 — Number(form.area_id) -> form.area_id || undefined
- NuevaSolicitudPage.tsx:323 — parseInt(data.periodo_vacacional_id) -> data.periodo_vacacional_id

Form initial values changed from 0 to '' (empty string represents
"not selected" for UUID PK fields).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git log --oneline -5
```

---

## Task 7: Final verification suite

- [ ] **Step 1: Run full pytest**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tee /tmp/pytest_4e_final.txt | tail -3
cd D:/VYNTIA
```

Expected: `161 passed, 8 failed, 3 skipped` (baseline preserved).

If REGRESSED, BLOCK. Compare:

```bash
diff /tmp/pytest_baseline_4e.txt /tmp/pytest_4e_final.txt | head -30
```

Identify newly-failing tests and investigate. Most likely cause: a test was reading `.empleado_id` or similar through normalized output in the test code; fix and re-run.

If PRESERVED, continue.

- [ ] **Step 2: Frontend build**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: success.

- [ ] **Step 3: Vitest**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: `Tests 7 passed (7)`, `Test Files 1 failed | 2 passed (3)`.

- [ ] **Step 4: Lint delta**

```bash
cd D:/VYNTIA/apps/web
ERRORS_NOW=$(npm run lint 2>&1 | grep -E "^\s*[0-9]+:[0-9]+" | wc -l)
ERRORS_BASELINE=$(cat /tmp/lint_baseline_4e.txt)
echo "Lint errors now: $ERRORS_NOW"
echo "Lint errors on master: $ERRORS_BASELINE"
echo "Delta: $((ERRORS_NOW - ERRORS_BASELINE))"
cd D:/VYNTIA
```

Expected delta: `0`.

If delta > 0, investigate the new lint errors. Common cause: unused `getNumber` import not cleaned up, or unused legacy variable name from a renamed access.

- [ ] **Step 5: Final inventory grep**

```bash
cd D:/VYNTIA/apps/web

echo "=== <entity>_id: number declarations (target: 0) ==="
grep -rEn "^\s+[a-z_]+_id\??\s*:\s*number" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l

echo ""
echo "=== .entity_id property accesses (acceptable: ~0 or only non-FK refs like correlation_id) ==="
grep -rEn "\.[a-z_]+_id\b" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated

echo ""
echo "=== parseInt/Number on _id (target: 0) ==="
grep -rEn "parseInt\([a-zA-Z_.]+_id|Number\([a-zA-Z_.]+_id" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l

cd D:/VYNTIA
```

Expected:
- `<entity>_id: number`: 0
- `parseInt/Number on _id`: 0
- `.entity_id` accesses: small remainder of non-FK refs (e.g., logging correlation IDs); review each, accept if not FK-related

- [ ] **Step 6: Confirm `generated/` not touched**

```bash
cd D:/VYNTIA
git diff --name-only master vyntia/L3.10.4e-pk-uuid | grep "src/generated/" || echo "OK: generated/ untouched"
```

Expected: `OK: generated/ untouched`.

---

## Task 8: Curl smoke (NEW per spec D4)

**Goal:** verify the rename didn't break the actual end-to-end runtime path. Backend must be running.

- [ ] **Step 1: Start backend (if not already running)**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_4e.log 2>&1 &
sleep 4
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/docs/ && echo " <- /api/docs/ status"
cd D:/VYNTIA
```

Expected: `200 <- /api/docs/ status`.

If runserver fails with `UnicodeDecodeError`, set `PGPASSWORD` differently or use a workaround documented in CLAUDE.md ("Known issue: local runserver fails..."). If still blocked, skip curl smoke and document as DEFERRED.

- [ ] **Step 2: Get auth token**

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<DEV-PASS>"}' | jq -r .data.access)
echo "Token length: ${#TOKEN}"
```

Replace `<DEV-PASS>` with the actual dev password (capture from `.env` or ask user). Expected: token length ~200+ chars.

- [ ] **Step 3: Smoke 5 representative endpoints**

```bash
echo "=== GET /api/v1/employees/ — first record id ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/employees/" | jq '.data.results[0] | {id, nombres_empleado}'

# Capture an actual UUID for next call
EMPLOYEE_UUID=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/employees/" | jq -r '.data.results[0].id')
echo "Employee UUID: $EMPLOYEE_UUID"

echo ""
echo "=== GET /api/v1/employees/{uuid}/ ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/employees/$EMPLOYEE_UUID/" | jq '{id, nombres_empleado, status: .status}'

echo ""
echo "=== GET /api/v1/contracts/ — first id ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/contracts/" | jq '.data.results[0].id'

echo ""
echo "=== GET /api/v1/payroll/monthly/ — first id ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/payroll/monthly/" | jq '.data.results[0].id'

echo ""
echo "=== GET /api/v1/identity/users/ — first id ==="
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/identity/users/" | jq '.data.results[0].id'
```

Expected: each `id` is a UUID string (36 chars, dash-separated, e.g., `"3fa85f64-5717-4562-b3fc-2c963f66afa6"`), not a number.

If any returns `"id": 0` or a numeric, this is the latent normalizer bug confirming itself — it means the backend serializer is not yet emitting UUID for that endpoint, OR the frontend is reading a different field. Investigate and fix.

- [ ] **Step 4: Outbound smoke — PATCH employee**

```bash
echo "=== PATCH /api/v1/employees/{uuid}/ telefono_celular ==="
curl -s -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"telefono_celular":"999000111"}' "http://localhost:8000/api/v1/employees/$EMPLOYEE_UUID/" | jq '{success, error: .error // null, telefono: .data.telefono_celular}'
```

Expected: `{ "success": true, "error": null, "telefono": "999000111" }`.

If returns 400/422 with field validation error, the backend rejected something — read the error message. If returns 404, the UUID URL routing is broken. If returns 500, server-side bug.

- [ ] **Step 5: Stop backend**

```bash
pkill -f "manage.py runserver" 2>/dev/null || true
echo "Backend stopped"
```

- [ ] **Step 6: Document smoke results**

If all 5 endpoints + 1 PATCH succeed: smoke ✅. Continue to merge.

If any fail: document the failure mode in a follow-up commit:
- Log the failed request + response
- Investigate: backend serializer issue? frontend payload issue?
- Fix in same PR if it's frontend; defer to bugfix PR if it's backend.

---

## Task 9: Merge to master

- [ ] **Step 1: Confirm user authorization**

PAUSE. Show user the branch state and request explicit merge approval. Do not proceed until approved.

```bash
cd D:/VYNTIA
git log --oneline master..vyntia/L3.10.4e-pk-uuid
git diff --stat master vyntia/L3.10.4e-pk-uuid | tail -10
```

- [ ] **Step 2: Merge --no-ff**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/L3.10.4e-pk-uuid -m "Merge L3.10.4e: PK type change (number -> UUID string + normalizer fix)"
git log --oneline -7
```

- [ ] **Step 3: Post-merge smoke**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: all baselines preserved (check 0 issues, pytest 161/8/3, build success, vitest 7 passed).

---

## Task 10: Update roadmap + memory

- [ ] **Step 1: Update roadmap**

Edit `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`:
- Mark L3.10.4e ✅ with merge commit hash
- Mark L3.11 as `⏳ NEXT`
- Update L3.10.4e row with brief summary of actual outcomes (file count, lessons learned)

- [ ] **Step 2: Update memory `active_subproject.md`**

Edit `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- Add the L3.10.4e ✅ merged entry with commit hash and brief outcomes
- Update "How to apply" footer: next pending sub-PR is L3.11 (cleanup `app_rrhh/` + remove legacy URLs)
- Document any new lessons learned (LR23+) — particularly anything surfaced during execution that wasn't anticipated

- [ ] **Step 3: Commit roadmap + memory metadata**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git diff --cached --stat
git commit -m "$(cat <<'EOF'
docs(L3.10.4e): mark L3.10.4e merged

PK type change shipped — 22 entities renamed/retyped from
<entity>_id: number to id: string. Normalizer rewrite fixed silent
UUID-to-0 coercion. 4 atomic commits + curl smoke verified.

Pytest 161/8/3 + vitest 7 + build clean baselines preserved.
Next: L3.11 (cleanup app_rrhh/ + remove legacy /api/v1/rrhh/ URLs).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git log --oneline -3
```

(Memory file is outside the repo, no commit needed — Edit tool persists it directly.)

---

## Notas para el ejecutor

- **Big bang, no half-shipping.** This PR delivers the entire 22-entity rename atomically. Do not skip entities or defer "just one" to a follow-up — the cross-entity refs make partial work unstable.
- **TS compiler is the safety net.** After interface renames, every consumer breaks at compile time. Iterate `npm run build` between edits to keep the error surface small and tractable.
- **Normalizer commit is intermediate-broken-state.** The first commit (Task 3) deliberately leaves TS broken because the normalizer drops `<entity>_id` emission while consumers still read it. The next commit (Task 5) resolves the breakage. Reviewers will see this chain — document clearly in commit messages.
- **Outbound payloads keep their key names.** D3 says retype value to string but preserve `empleado_id`/`area_id` as the OUTBOUND key (matches whatever the backend tolerates). Only INBOUND (read) shapes use `id`.
- **Curl smoke is non-negotiable for L3.10.4e.** The 4d post-review fixes pescaron 3 bugs that pytest+build didn't catch. For 4e the runtime risks are higher (UUID coercion paths). 5 endpoints + 1 PATCH is cheap insurance.
- **Form initial values: `0` → `''`.** UUID PK fields with empty/unselected state should use empty string, not the number 0 (which would be coerced to a UUID-shaped string `"0"` — invalid).
- **Risk level: HIGH.** Big-bang rename. Code review essential post-merge. Same workflow as 4d (atomic merge, post-review fixes if reviewer surfaces issues).
