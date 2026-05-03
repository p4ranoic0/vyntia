# VYNTIA Foundation L3.10.4e — Frontend PK Type Change Design Spec

**Date:** 2026-05-02
**Sub-PR:** L3.10.4e (5th of 6 in L3.10.4 frontend rename series)
**Spec source:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.6 + § 3.6.1
**Audit source:** `docs/superpowers/research/api-contract-audit.md` § "L3.10.4e action plan" (lines 1689-1733)
**Predecessor merges:** L3.10.4d ✅ `c7be13c2`, L3.10.4f ✅ `3ed2e7d3`

---

## Goal

Align the frontend TypeScript type system with the backend's UUID-string primary keys (post-L3.10.2). All 22 entities with UUID PKs currently have frontend interfaces declaring `<entity>_id: number` — both the field name and the type are wrong. The backend stopped emitting `<entity>_id` and started emitting `id: '<uuid-string>'` post-L3.10.2; the normalizers in `apiNormalizers.ts` paper-cracked this by silently coercing UUID strings to `0` via `getNumber(...)`, which is a latent runtime bug.

This PR renames + retypes simultaneously: `<entity>_id: number` → `id: string`, fixes the normalizers, and updates all consumers.

## Non-goals

- Backend serializer bugs surfaced by the audit (duplicate `'id'` in `RolPermisosSerializer`, broken `source='contrato.contrato_id'` in vacation serializers, validator stale field names) — separate bugfix PR
- `creado_por_nombre` / `modificado_por_nombre` SerializerMethodField name mismatches — separate cleanup
- `Permission.modulo` typing irregularity (audit § 5: backend stores `modulo` as free-form string referencing `MODULES_CONFIG`, not an FK) — separate investigation
- Field renames covered by 4c/4d (audit fields, state fields)
- File renames covered by 4f
- Runtime form ergonomics changes (e.g., switching from controlled `<Select>` to async-search) — out of scope
- `apps/web/src/generated/` (auto-generated from OpenAPI schema)

## Architecture decisions (from brainstorming, 2026-05-02)

### D1 — Scope strategy: Big bang (single PR)

All 22 entities renamed atomically in one branch. **Rejected alternatives:**
- Split by bounded context (5 PRs): cross-entity refs are pervasive — `User.empleado.area.id` ties identity + employees + organization. Splitting creates intermediate broken TS states.
- Entity-by-entity (~22 PRs): the very first one breaks (e.g., Contract has `empleado: { id: ... }` from Employee).

**Why big bang works:** the TypeScript compiler enumerates the complete blast radius via `npm run build`. The backend already accepts UUID PKs end-to-end (post-L3.10.4a URL refactor routes UUID-based endpoints). One merge produces one stable state.

### D2 — Normalizers: Fix in place

`apps/web/src/services/normalizers/apiNormalizers.ts` does more than ID coercion — it aliases backend variation in field names (`nombres_empleado ?? nombres`, `apellido_paterno ?? ape_paterno`, etc.), derives `is_active ↔ estado_rol`, and reconstructs nested structures (`area` from `ubicacion_actual`). **Keep these.**

Changes:
- The 4 ID-coercing functions (`getNumber(empleado_id ?? id)`, etc.) become `getString(...)` — UUIDs flow through as strings.
- The duplicate emission `{ id: X, empleado_id: X }` becomes `{ id: X }` — drop the legacy `<entity>_id` alias from the normalizer output. This forces TS to flag every consumer that still reads `.empleado_id` on a normalized entity.

**Rejected:** ripping out normalizers entirely (mixes scope; legitimate alias work is hidden in them).

### D3 — Outbound payload strategy: Retype, keep key name

Frontend POST/PATCH payloads currently send `{ empleado_id: X, area_id: Y }`. Backend serializer Meta.fields use FK relation names (e.g., `'empleado', 'area'` in `contratos_serializers.py:43`), but several action endpoints read `request.data.get('empleado_id')` directly. Outbound semantics are mixed and not fully audited.

**Decision:** retype outbound types to `: string` keeping the key name unchanged (`empleado_id`, `area_id`). Trust either tolerance or action-data path. Verify with curl smoke in same PR. If smoke surfaces an endpoint that strictly requires the FK relation name, fix as post-review.

**Rejected:**
- Per-endpoint backend serializer audit (1-2 days extra exploration; outbound is the smaller risk vector — pytest already covers this).
- Defer outbound to a follow-up sub-PR (impossible — the 96 `<entity>_id: number` interface declarations include outbound form types alongside read shapes; touching one means touching the other).

### D4 — Verification: Curl smoke added

The 4d PR shipped with code review pescando 3 bugs that pytest+build did not catch (stale ORM refs, filter-types mismatch, declared-Spanish revert). For 4e, runtime risks are higher (UUID coercion paths, outbound payload mismatches), so add curl smoke against ~5 representative endpoints. This complements (not replaces) pytest+build+lint+vitest.

## Inventory (current snapshot)

```
Frontend (D:/VYNTIA/apps/web):
  <entity>_id: number declarations         96
  .entity_id property access refs         235
  entity_id: <value> object property      133
  parseInt(...)/Number(...) on _id          6
```

The 6 `parseInt/Number` sites:
1. `src/components/empleados/TabLaborales.tsx:81` — `Number(form.area_id)` outbound
2. `src/pages/vacaciones/NuevaSolicitudPage.tsx:323` — `parseInt(data.periodo_vacacional_id)` outbound
3-6. `src/services/normalizers/apiNormalizers.ts:25,63,95,118` — internal `getNumber(...)` ID coercion

All 6 must be removed (UUID strings flow through unchanged).

## Per-entity rename matrix (22 entities)

Sourced from `docs/superpowers/research/api-contract-audit.md` lines 1693-1722. Each row: `<old field> → <new field>`. All `: number → : string`.

| # | Entity | File | Field rename(s) |
|---|---|---|---|
| 1 | Employee | `services/employeesService.ts:10` | `id: number → id: string` |
| 2 | DatosLaborales | `services/employeesService.ts:69-73` | `id?, empleado_id, area_id, supervisor_id` |
| 3 | DatosFamiliares | `services/employeesService.ts:85-88` | `id?, empleado_id` |
| 4 | DatosAcademicos | `services/employeesService.ts:98-100` | `id?, empleado_id` |
| 5 | Department/Area | `services/departmentsService.ts:5` | `area_id: number → id: string` |
| 6 | User | `services/usersService.ts:11-14`, `lib/api.ts:25-44` | `id, usuario_id, empleado.id, empleado.area.id` |
| 7 | Role | `services/usersService.ts:41-43`, `services/securityService.ts:28-65` | `id, rol_id` |
| 8 | Permission | `services/usersService.ts:53-54`, `services/securityService.ts` | `id, permiso_id` |
| 9 | Module | (audit § 6) | `id` |
| 10 | RolePermission | `services/securityService.ts` | `id, rol_permiso_id` |
| 11 | UserRole | (audit § 8) | `id, usuario_rol_id` |
| 12 | Contract | `services/contractsService.ts:5-9` | `contrato_id, empleado, area, area_detalle.area_id` |
| 13 | ContractAmendment | (audit § 10) | `id, contrato_padre.id` |
| 14 | EmploymentData | (audit § 11) | `id, empleado.id, area.id` |
| 15 | FamilyMember | (audit § 12) | `id, empleado.id` |
| 16 | AcademicRecord | (audit § 13) | `id, empleado.id` |
| 17 | Certification | (audit § 14) | `id, empleado.id` |
| 18 | DigitalDocument | `services/legajoService.ts:5-7` | `documento_id, empleado, subido_por, validado_por` |
| 19 | DocumentTemplate | `services/templatesService.ts:11` | `plantilla_id → id: string` |
| 20 | Company | (audit § 17) | `id` |
| 21 | MonthlyPayroll | `services/payrollService.ts:115` | `planilla_id → id: string` |
| 22 | PayrollDetail | `services/payrollService.ts:151-160` | `detalle_id, planilla.planilla_id, empleado.empleado_id` |
| 23 | Compensation | `services/payrollService.ts:6` | `configuracion_id → id: string` |
| 24 | AfpConfiguration | `services/payrollService.ts:40` | `afp_config_id → id: string` |
| 25 | TaxParameter (UIT) | `services/payrollService.ts:66` | `configuracion_uit_id → id: string` |
| 26 | MassDeduction | `services/payrollService.ts:206-220` | `descuento_masivo_id, configuracion_concepto.configuracion_id, usuario_carga.usuario_id` |
| 27 | Payslip | `services/payrollService.ts:238-246` | `boleta_id, detalle_planilla.detalle_id, empleado.empleado_id` |
| 28 | PaymentSchedule | `services/payrollService.ts:264-274` | `calendario_id, created_by.usuario_id` |
| 29 | VacationConfiguration | `services/timeOffService.ts:4` | `configuracion_id → id: string` |
| 30 | VacationPeriod | `services/timeOffService.ts:11-12` | `id, periodo_id, empleado, contrato, contrato_id` |
| 31 | VacationRequest | `services/timeOffService.ts:36-49` | `id, solicitud_id, empleado.id, periodo_vacacional.id` |
| 32 | VacationGrant | `services/timeOffService.ts:70-73` | `goce_id, empleado, solicitud_vacaciones, periodo_vacacional` |
| 33 | OnboardingProcess | `services/onboardingService.ts:5-9` | `onboarding_id, empleado, usuario, validado_por` |

(Note: 33 rows because some entities have multiple interfaces. The "22 entities" count is at the model level.)

## Normalizer changes (`apiNormalizers.ts`)

```diff
-const getNumber = (value: unknown, fallback = 0): number =>
-  typeof value === "number" ? value : fallback;

  // (existing) const getString = (value: unknown, fallback = ""): string => ...

 export const normalizeRole = (role: unknown) => {
   const roleObj = asRecord(role);
-  const roleId = getNumber(roleObj.rol_id ?? roleObj.id);
+  const roleId = getString(roleObj.rol_id ?? roleObj.id);
   ...
   return {
     id: roleId,
-    rol_id: roleId,                           // DROP
     ...
   };
 };

 // Same pattern for normalizeUser (line 63), normalizeEmployee (line 95)
 // ubicacionActual.area_id (line 118) → getString(...)
```

After this change, `getNumber` may become unused — remove it.

## Verification commands

Pre-flight:
```bash
cd D:/VYNTIA
git checkout -b vyntia/L3.10.4e-pk-uuid
source D:/VYNTIA/.venv/Scripts/activate

# Backend baseline
cd apps/api && PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3

# Frontend baseline
cd ../web && npm run build 2>&1 | tail -3 && npm test -- --run 2>&1 | grep Tests
```

Post-implementation (per commit + final):
```bash
# Same as pre-flight, must preserve baselines

# NEW: curl smoke (after backend is up)
cd D:/VYNTIA/apps/api && python manage.py runserver --settings=vyntia.settings.development &
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<dev-pass>"}' | jq -r .data.access)

# 5 representative endpoints
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/employees/" | jq '.data.results[0] | {id, nombres_empleado}'
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/employees/<uuid>/" | jq '.data.id'
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/contracts/" | jq '.data.results[0].id'
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/payroll/monthly/" | jq '.data.results[0].id'

# Outbound smoke: PATCH an employee
curl -s -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"telefono_celular":"999000111"}' "http://localhost:8000/api/v1/employees/<uuid>/" | jq '.success'
```

All curl responses should show: `id` is a UUID string, not a number; PATCH returns `success: true`.

## Definition of done

- [ ] All 22 entities (33 interface rows) renamed `<entity>_id: number → id: string` per matrix
- [ ] Normalizer `getNumber → getString`, duplicate `<entity>_id` emission dropped
- [ ] All 6 `parseInt`/`Number()` calls on `_id` removed
- [ ] All 235 `.entity_id` property accesses migrated to `.id` (TS compiler enumerates)
- [ ] Outbound object-literal payloads retyped to string (key names preserved)
- [ ] Cross-entity nested refs propagated (`User.empleado.id`, `Contract.empleado.id`, etc.)
- [ ] `manage.py check` clean
- [ ] `npm run build` clean (no TS errors)
- [ ] `npm run lint` 0 net new errors
- [ ] vitest 7 passed (1 file load failure preserved)
- [ ] pytest baseline 161/8/3 preserved
- [ ] curl smoke: 5 representative endpoints respond with UUID `id` strings + 1 PATCH succeeds
- [ ] Branch merged to master with `--no-ff`
- [ ] Roadmap updated (L3.10.4e ✅, mark L3.11 NEXT)
- [ ] Memory updated

## Commit structure

1. `docs(L3.10.4e): add PK type change plan`
2. `chore(L3.10.4e): normalizer rewrite — getString + drop duplicate _id emit`
3. `chore(L3.10.4e): interface renames + consumer access patterns`
4. `chore(L3.10.4e): outbound payload retype + parseInt/Number removals`
5. (Cn) post-review fixes as needed

Each commit: `npm run build` + `manage.py check` clean. Final commit: full verification + curl smoke.

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| TS rename leaves silent runtime bugs (UUID coerced to 0 in untouched normalizer paths) | Med | curl smoke + post-review code review |
| Outbound payload key mismatch (backend rejects `empleado_id: '<uuid>'`, expects `empleado`) | Low-Med | curl PATCH smoke + post-review fix loop |
| `parseInt/Number()` removal misses a site | Low | grep verification + TS errors on stringly-typed FormData |
| Form state hardcoded `useState<number \| null>(0)` for entity ID | Med | TS errors when value passed to URL builder or query key — compiler-driven |
| React Query keys break (cache invalidation) | Very Low | Query keys accept any serializable value; UUIDs work fine |
| Existing dead-code refs to `<entity>_id` in tests | Low | vitest catches; fix in same PR |

## Out-of-scope discoveries log (for follow-up)

From audit lines 1737+ — these surface during 4e implementation but are NOT addressed:
- `RolPermisosSerializer` has duplicate `'id'` in Meta.fields (backend bug)
- Vacation serializers use broken `source='contrato.contrato_id'` (post-L3.10.2 should be `source='contrato.id'`)
- `Permission.modulo` is a free-form string referencing `MODULES_CONFIG`, not a UUID FK
- `creado_por_nombre`/`modificado_por_nombre` SerializerMethodField name mismatches with frontend `created_by_nombre` (4c left over)
- Three duplicate `Role` interfaces in `lib/api.ts` / `usersService.ts` / `securityService.ts` — consolidate

These go to a separate `vyntia/L3.10.x-cleanup` sub-PR after L3.10.4e + L3.11.

---

**Status:** Spec authored 2026-05-02 by brainstorming session. Awaits user review before invoking `superpowers:writing-plans`.
