# VYNTIA Foundation L3.10.4d — State Fields Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the backend serializer JSON contract and the frontend TS interfaces for the 6 entities where backend post-L3.10.2 has platform `status` / `is_active` Python attributes (Contract, ContractAmendment, Compensation, AfpConfiguration, TaxParameter, MonthlyPayroll, MassDeduction, PaySlip, PaymentSchedule, VacationConfiguration). Backend serializer `Meta.fields` currently references the OLD `'estado'` / `'activo'` key names, which no longer exist as Python attributes — these fields are silently broken at runtime. This PR fixes the backend (~14 serializer entries + 1 method) and renames the corresponding frontend interfaces + consumers.

**Architecture:** Two-sided refactor in one branch. Two commits: (1) backend serializer fixes (changes JSON keys emitted by ~14 endpoints), (2) frontend interface + consumer rename to consume the new keys. Atomic merge keeps the two sides aligned. Strict Option B per spec § 3.6.1 — only entities the backend rename L3.10.2 already touched. Preserved-Spanish state fields (`estado_empleado`, `estado_civil`, `estado_rol`, `estado_modulo`, `estado_area`, `estado_periodo`, `estado_solicitud`, `estado_documento`, `estado_familiar`, `estado_estudios`, etc.) are NOT touched.

**Tech Stack:** Django 5.2 + DRF (backend), React 18 + TypeScript (frontend). No new dependencies.

**Spec source:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.6 (field convention) + § 3.6.1 (Option B scope).

**Audit source:** `docs/superpowers/research/api-contract-audit.md` (commit `30d0f44a`) — Interpretation A (Strict Option B), lines 1636-1686.

**Pre-conditions:**
- L3.10.4f merged (commit `3ed2e7d3`) + roadmap update (`8eec365e`) + audit (`30d0f44a`)
- Frontend baseline: vitest 7 passed, 1 file load-failure (Playwright e2e)
- Frontend `npm run build` passes
- Backend pytest baseline: 161 passed, 8 failed, 3 skipped
- Backend on Django 5.2.13, virtualenv at `D:/VYNTIA/.venv/`

**Scope decision (sub-PR de L3.10.4):**
- L3.10.4a ✅ Backend URL refactor
- L3.10.4b ✅ Frontend URL refactor
- L3.10.4c ✅ Frontend audit fields rename
- **L3.10.4d (este plan)** — State fields rename (backend serializer + frontend interfaces + consumers, strict Option B)
- L3.10.4e ⏸ Frontend PK type change (deferred — separate sub-PR after this)
- L3.10.4f ✅ Frontend file renames (already shipped out of order)

**Out of scope (NO hacer en L3.10.4d):**
- Aggressive Interpretation B from the audit: renaming preserved-Spanish state fields (`estado_area → status`, `estado_rol → status`, etc.) — explicitly deferred per audit recommendation.
- PK rename (`<entity>_id: number → id: string` UUID) — L3.10.4e
- File renames — already done in L3.10.4f
- Other backend bugs surfaced by the audit (duplicate `'id'` in `RolPermisosSerializer`, broken `source='contrato.contrato_id'` in vacation serializers, validator stale field names) — separate bugfix PR
- `creado_por_nombre`/`modificado_por_nombre` SerializerMethodField name mismatches — separate cleanup
- `apps/web/src/generated/` (auto-generated)

---

## Backend serializer changes table

Source: audit lines 1640-1658.

| File | Line | Serializer | Change |
|---|---|---|---|
| `apps/api/api/v1/rrhh/serializers.py` | ~360 | `ConfiguracionRemuneracionSerializer` (Compensation v1) | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/serializers.py` | ~425 | `ConfiguracionAfpSerializer` (Afp v1) | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~50 | `ConfiguracionAfpSerializer` (Afp v2) | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~82 | `ConfiguracionUitSerializer` (TaxParameter) | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~101 | `ConfiguracionUitSerializer.get_es_activo` method | `obj.estado` → `obj.status` (bug fix) |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~157 | `ConfiguracionRemuneracionSerializer` (Compensation v2) | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~196 | `PlanillaMensualListSerializer` | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~247 | `PlanillaMensualDetailSerializer` | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~535 | `DescuentoMasivoListSerializer` | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~570 | `DescuentoMasivoDetailSerializer` | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~649 | `BoletaPagoListSerializer` | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~684 | `BoletaPagoDetailSerializer` | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~729 | `CalendarioPagoListSerializer` | `'estado'` → `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py` | ~760 | `CalendarioPagoDetailSerializer` | `'estado'` → `'status'` |
| `apps/api/api/v1/vacaciones/serializers.py` | ~78 | `ConfiguracionVacacionesSerializer` | `'activo'` → `'is_active'` |

**Total:** 14 serializer Meta.fields entries + 1 method line = **15 backend changes**, across **3 files**.

**Note:** `apps/api/api/v1/rrhh/contratos_serializers.py` already uses `'status'` (verified in audit and pre-flight). NO backend change for Contract / ContractAmendment.

**Why `obj.estado == "activo"` becomes `obj.status == "activo"`:** The model has `status = models.CharField(...)` with `db_column='estado'`. The DB row still stores `"activo"` as the value (domain Spanish preserved). Only the Python attribute name changes — comparison against `"activo"` string is correct.

---

## Frontend interface changes table

Source: audit lines 1663-1672.

| File | Interface | Field rename |
|---|---|---|
| `apps/web/src/services/contractsService.ts:35` | `Contrato` | `estado: string → status: string` |
| `apps/web/src/services/contractsService.ts:64` | `ContratoListItem` | `estado: string → status: string` |
| `apps/web/src/services/contractsService.ts:92` | `ContratoFilters` | `estado?: string → status?: string` |
| `apps/web/src/services/payrollService.ts` | `ConfiguracionAfp` | `estado → status` |
| `apps/web/src/services/payrollService.ts` | `ConfiguracionUit` | `estado → status` |
| `apps/web/src/services/payrollService.ts` | `ConfiguracionRemuneracion` (or similar) | `estado → status` |
| `apps/web/src/services/payrollService.ts` | `PlanillaMensual` | `estado → status` |
| `apps/web/src/services/payrollService.ts` | `DetallePlanilla` (if it has estado) | `estado → status` (may be N/A) |
| `apps/web/src/services/payrollService.ts` | `DescuentoMasivo` | `estado → status` |
| `apps/web/src/services/payrollService.ts` | `BoletaPago` | `estado → status` |
| `apps/web/src/services/payrollService.ts` | `CalendarioPago` | `estado → status` |
| `apps/web/src/services/timeOffService.ts:7` | `ConfiguracionVacaciones` | `activo: boolean → is_active: boolean` |
| `apps/web/src/services/timeOffService.ts:154` | `ConfiguracionVacacionesForm` | `activo?: boolean → is_active?: boolean` |
| `apps/web/src/hooks/useRemuneraciones.ts` | various filter params | `activo?: boolean → is_active?: boolean` (if mapped to ConfiguracionVacaciones / Compensation) |

**Total:** ~13 interface field renames across 3 files.

---

## Frontend consumer files (must update access patterns)

After interface renames, TypeScript will emit errors like:
```
Property 'estado' does not exist on type 'Contrato'. Did you mean 'status'?
```

Fix each consumer by replacing the field access. Use `npm run build` to enumerate all error sites.

**Expected consumer files** (per audit + grep on services that consume contractsService / payrollService / timeOffService):

contractsService consumers (check for `.estado` access on Contract types):
- `apps/web/src/pages/contratos/ContratosPage.tsx`
- `apps/web/src/pages/Empleados.tsx`
- `apps/web/src/pages/HROverviewDashboard.tsx`
- `apps/web/src/pages/legajo/LegajoPage.tsx`

payrollService consumers (check for `.estado` access on Compensation/Afp/Uit/Planilla/Boleta/Calendario types):
- `apps/web/src/hooks/useRemuneraciones.ts`
- `apps/web/src/pages/remuneraciones/ConfiguracionRemuneracionesPage.tsx`
- `apps/web/src/pages/remuneraciones/ConfiguracionUitPage.tsx`
- `apps/web/src/pages/remuneraciones/DescuentosMasivosPage.tsx`
- `apps/web/src/pages/remuneraciones/PlanillasMensualesPage.tsx`

timeOffService consumers (check for `.activo` access on ConfiguracionVacaciones):
- `apps/web/src/components/vacaciones/ConfiguracionPanel.tsx` (uses `config.activo`, `formData.activo`, `configuracion.activo` — all `ConfiguracionVacaciones`)
- `apps/web/src/pages/vacaciones/ConfiguracionPage.tsx`

**Important:** Do NOT touch `.estado` access on entities that are NOT in scope (e.g., `area.estado_area`, `role.estado_rol`, `permiso.estado_permiso`, `empleado.estado_empleado`). Those are preserved-Spanish per Option B. The TypeScript compiler will guide: it only flags `.estado` access on the renamed interfaces (Contrato, ConfiguracionAfp, etc.).

---

## File Structure Overview

| Action | Path |
|---|---|
| Modify | `apps/api/api/v1/rrhh/serializers.py` (~2 entries: lines ~360, ~425) |
| Modify | `apps/api/api/v1/rrhh/remuneraciones_serializers.py` (~12 entries + 1 method) |
| Modify | `apps/api/api/v1/vacaciones/serializers.py` (1 entry: line ~78) |
| Modify | `apps/web/src/services/contractsService.ts` (3 interfaces) |
| Modify | `apps/web/src/services/payrollService.ts` (~7 interfaces) |
| Modify | `apps/web/src/services/timeOffService.ts` (2 interfaces) |
| Modify | `apps/web/src/hooks/useRemuneraciones.ts` (filter params, possibly interface fields) |
| Modify | Each consumer file with `.estado` or `.activo` access on a renamed entity |
| Create | (none — no new files) |

NO TOUCH:
- `apps/api/api/v1/rrhh/contratos_serializers.py` (already correct)
- Models (already correct post-L3.10.2)
- `apps/web/src/services/normalizers/apiNormalizers.ts` (no `estado`/`activo` mapping inside)
- Backend tests (let pytest tell us if they break)
- Frontend tests (let vitest tell us if they break)
- `apps/web/src/lib/api.ts` Role/Permission interfaces (those map to preserved-Spanish `estado_rol`/`estado_permiso` per audit)

---

## Definition of Done

- [ ] 14 backend serializer Meta.fields entries renamed (`'estado'` → `'status'` ×13, `'activo'` → `'is_active'` ×1)
- [ ] 1 backend method body fixed: `ConfiguracionUitSerializer.get_es_activo` reads `obj.status` instead of `obj.estado`
- [ ] ~13 frontend TS interface fields renamed
- [ ] All consumer `.estado` / `.activo` access patterns on renamed entities updated to `.status` / `.is_active`
- [ ] `grep -rEn "['\"]estado['\"]" apps/api/api/v1/rrhh/remuneraciones_serializers.py apps/api/api/v1/rrhh/serializers.py apps/api/api/v1/vacaciones/serializers.py` returns 0 matches IN A `Meta.fields` LIST CONTEXT (preserved-Spanish strings like `'estado_modulo'`, `'estado_rol'` may remain in other serializers and that's correct)
- [ ] `manage.py check` clean
- [ ] `npm run lint` 0 net new errors vs master baseline
- [ ] `npm run build` passes (no TypeScript errors)
- [ ] `npm test` (vitest) baseline preserved: 7 passed, 1 file load-failure
- [ ] Backend pytest: must NOT regress. Baseline was 161/8/3. Fixing serializer bugs could either preserve (161/8/3), or RECOVER some failures (e.g., 165/4/3) if any of the 8 failures were caused by these serializer mismatches.
- [ ] Branch `vyntia/L3.10.4d-state-fields` merged to master with `--no-ff`
- [ ] Roadmap updated: L3.10.4d ✅
- [ ] Memory updated

---

## Task 1: Pre-flight — branch, baseline, snapshot

- [ ] **Step 1: Confirm pwd and master clean post-L3.10.4f**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -5
```

Expected: HEAD = `30d0f44a docs: add API contract audit unblocking L3.10.4d/4e` or later. Status shows ONLY the new plan file untracked.

- [ ] **Step 2: Confirm backend baseline (capture pytest output to file for diff later)**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tee /tmp/pytest_baseline.txt | tail -3
cd D:/VYNTIA
```

Expected: `System check identified no issues` + `161 passed, 8 failed, 3 skipped`.

The list of 8 failed tests is in `/tmp/pytest_baseline.txt`. We'll diff post-refactor to confirm we don't regress.

- [ ] **Step 3: Confirm frontend baseline build**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: build success.

- [ ] **Step 4: Confirm frontend baseline tests**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: `Tests 7 passed (7)`, `Test Files 1 failed | 2 passed (3)`.

- [ ] **Step 5: Snapshot legacy field counts**

```bash
cd D:/VYNTIA/apps/web

# Count bare 'estado' as TS field type in renamed services (target: 0 after refactor)
echo "=== Frontend interface 'estado:' declarations in renamed services ==="
grep -nE "^\s+estado\??\s*:" src/services/contractsService.ts src/services/payrollService.ts 2>/dev/null
echo ""
echo "=== Frontend interface 'activo:' declarations in renamed services ==="
grep -nE "^\s+activo\??\s*:" src/services/timeOffService.ts src/hooks/useRemuneraciones.ts 2>/dev/null

cd D:/VYNTIA/apps/api
echo ""
echo "=== Backend serializer Meta.fields with 'estado' (excluding domain like 'estado_modulo') ==="
grep -nE "['\"]estado['\"]" api/v1/rrhh/serializers.py api/v1/rrhh/remuneraciones_serializers.py api/v1/rrhh/contratos_serializers.py | head -20
echo ""
echo "=== Backend serializer Meta.fields with 'activo' ==="
grep -nE "['\"]activo['\"]" api/v1/vacaciones/serializers.py api/v1/rrhh/remuneraciones_serializers.py | head -10
echo ""
echo "=== Backend obj.estado access ==="
grep -rEn "obj\.estado\b" api/v1/ app_rrhh/ 2>/dev/null | grep -v __pycache__ | head -10
cd D:/VYNTIA
```

REPORT THE NUMBERS. Use them as targets for verification later.

- [ ] **Step 6: Create branch**

```bash
git checkout -b vyntia/L3.10.4d-state-fields
git status --short
```

---

## Task 2: Commit the plan

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-29-vyntia-foundation-L3.10.4d-state-fields.md
git commit -m "$(cat <<'EOF'
docs(L3.10.4d): add state fields rename plan

Two-sided refactor: 14 backend serializer Meta.fields entries +
1 method bug fix, plus ~13 frontend interface fields + consumer refs.
Strict Option B per audit (Interpretation A). Aligns serializer JSON
contract with backend Python attribute names post-L3.10.2.

Out of scope:
- Preserved-Spanish state fields (Department, Role, Permission, Module,
  Employee, etc.) — Interpretation B explicitly deferred
- PK type change -> L3.10.4e
- Other backend bugs (duplicate id in RolPermisos, broken contrato_id
  source paths, validator stale fields) -> separate bugfix PR

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Backend serializer fix — `apps/api/api/v1/rrhh/serializers.py`

**Files:**
- Modify: `apps/api/api/v1/rrhh/serializers.py` (~2 entries)

The audit located these at lines ~360 (Compensation v1) and ~425 (Afp v1). Verify exact line numbers before editing.

- [ ] **Step 1: Read context around the Compensation serializer**

```bash
grep -n "ConfiguracionRemuneracionSerializer\|class ConfiguracionAfpSerializer" D:/VYNTIA/apps/api/api/v1/rrhh/serializers.py | head -5
```

Note the line numbers and read the surrounding `Meta.fields` list.

- [ ] **Step 2: Edit Compensation serializer Meta.fields**

Use Edit tool. The exact `old_string` should be a unique block including surrounding context. Look at the file for the `Meta.fields` block of `ConfiguracionRemuneracionSerializer` and replace `'estado'` with `'status'` ONLY in that block (so we don't accidentally change another serializer's `'estado'` reference if it's preserved-Spanish-style).

Concrete recipe — use Edit with `old_string` being a unique multi-line snippet that includes context:

```
class ConfiguracionRemuneracionSerializer(serializers.ModelSerializer):
    ...
    class Meta:
        model = ConfiguracionRemuneracion  # or similar
        fields = [
            ...
            'estado',
```

And `new_string` is the same block with `'estado'` replaced by `'status'` on the relevant line. Apply per-serializer to avoid global collisions.

If the file is too large to grok in context, work serializer-by-serializer.

- [ ] **Step 3: Edit Afp serializer Meta.fields (same file)**

Same approach — find `ConfiguracionAfpSerializer.Meta.fields`, replace `'estado'` with `'status'` only in that list.

- [ ] **Step 4: Verify**

```bash
# Count remaining 'estado' refs in this file (some may legitimately remain — e.g., 'estado_modulo' for Module serializer)
grep -nE "['\"]estado['\"]" D:/VYNTIA/apps/api/api/v1/rrhh/serializers.py
# Expected: any remaining matches should NOT be in ConfiguracionRemuneracionSerializer or ConfiguracionAfpSerializer Meta.fields
```

Inspect by hand — confirm that the only remaining `'estado'` references are in entities the audit said keep preserved-Spanish (e.g., RoleSerializer, ModuleSerializer, etc., which have `'estado_rol'`, `'estado_modulo'` style names — those are NOT bare `'estado'`).

If any bare `'estado'` remains in a Compensation/Afp Meta.fields, fix it.

- [ ] **Step 5: `manage.py check`**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `System check identified no issues`. If it errors with `ImproperlyConfigured` or `Field 'status' does not exist`, the model attribute name might differ — investigate.

---

## Task 4: Backend serializer fix — `apps/api/api/v1/rrhh/remuneraciones_serializers.py`

**Files:**
- Modify: `apps/api/api/v1/rrhh/remuneraciones_serializers.py` (~12 Meta.fields entries + 1 method)

This file has the most serializers. Per audit, all 12 Meta.fields entries that have `'estado'` should be renamed.

- [ ] **Step 1: Inventory `'estado'` occurrences in the file**

```bash
grep -n "'estado'" D:/VYNTIA/apps/api/api/v1/rrhh/remuneraciones_serializers.py
```

Expected: ~12 lines, each inside a `Meta.fields` list of a serializer (Afp, TaxParameter, Compensation, MonthlyPayrollList/Detail, MassDeductionList/Detail, BoletaList/Detail, CalendarioList/Detail).

- [ ] **Step 2: Replace_all `'estado'` → `'status'` in this file**

Because every `'estado'` (with single quotes) in this file refers to a renamed entity's serializer, a bulk `replace_all` is safe in this specific file. Verify by inspecting the grep output first — if any `'estado'` is in a context other than `Meta.fields` of a renamed entity, do NOT use replace_all; switch to per-occurrence Edit.

If safe:
- File: `apps/api/api/v1/rrhh/remuneraciones_serializers.py`
- old: `'estado'`
- new: `'status'`
- replace_all: true

- [ ] **Step 3: Replace `obj.estado` in `get_es_activo` method**

This is at ~line 101.

```bash
grep -n "obj\.estado\b" D:/VYNTIA/apps/api/api/v1/rrhh/remuneraciones_serializers.py
```

Expected: 1 line — `return obj.estado == "activo"`.

Use Edit tool:
- File: `apps/api/api/v1/rrhh/remuneraciones_serializers.py`
- old: `return obj.estado == "activo"`
- new: `return obj.status == "activo"`
- replace_all: false (only 1 occurrence)

- [ ] **Step 4: Replace_all `'activo'` → `'is_active'`?**

CHECK FIRST: this file may have `'activo'` strings in Meta.fields too (the audit didn't specifically list this file for 'activo', but verify):

```bash
grep -n "'activo'" D:/VYNTIA/apps/api/api/v1/rrhh/remuneraciones_serializers.py
```

If 0 matches, skip this step. If matches exist in Meta.fields of relevant serializers, do `replace_all: 'activo' → 'is_active'`. If matches are in other contexts (e.g., comparison strings like `obj.status == "activo"`), do NOT use replace_all — use per-occurrence Edit only on the Meta.fields entries.

- [ ] **Step 5: Verify**

```bash
grep -n "'estado'\|obj\.estado\b" D:/VYNTIA/apps/api/api/v1/rrhh/remuneraciones_serializers.py || echo "OK: no legacy estado refs"
```

Expected: `OK`. If any remain, inspect — preserved-Spanish would not have bare `'estado'` so this should be 0.

- [ ] **Step 6: `manage.py check`**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: clean.

---

## Task 5: Backend serializer fix — `apps/api/api/v1/vacaciones/serializers.py`

**Files:**
- Modify: `apps/api/api/v1/vacaciones/serializers.py` (1 entry: `ConfiguracionVacacionesSerializer.Meta.fields`)

- [ ] **Step 1: Inventory**

```bash
grep -n "'activo'\|'estado'" D:/VYNTIA/apps/api/api/v1/vacaciones/serializers.py | head -10
```

Expected: at least 1 match for `'activo'` near line 78 (in `ConfiguracionVacacionesSerializer.Meta.fields`).

The `'estado'` matches in this file (if any) are likely preserved-Spanish (e.g., `'estado_solicitud'`) and should remain. Verify by reading context.

- [ ] **Step 2: Replace `'activo'` → `'is_active'` in ConfiguracionVacacionesSerializer.Meta.fields**

Use Edit tool with a unique multi-line `old_string` that anchors to the `ConfiguracionVacacionesSerializer` block:

```
class ConfiguracionVacacionesSerializer(serializers.ModelSerializer):
    ...
    class Meta:
        model = ConfiguracionVacaciones
        fields = [
            ...
            'activo',
```

If `'activo'` only appears once in this file in this context, you can use:
- old: `'activo',`  (with trailing comma)
- new: `'is_active',`
- replace_all: false (1 occurrence)

If unsure, do per-occurrence Edit with full surrounding context.

- [ ] **Step 3: Verify**

```bash
grep -n "'activo'" D:/VYNTIA/apps/api/api/v1/vacaciones/serializers.py || echo "OK: no 'activo' refs"
```

Expected: `OK`.

- [ ] **Step 4: `manage.py check`**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: clean.

---

## Task 6: Backend pytest — capture impact

- [ ] **Step 1: Run pytest**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tee /tmp/pytest_after_backend.txt | tail -3
cd D:/VYNTIA
```

Expected: ONE OF:
- `161 passed, 8 failed, 3 skipped` (baseline preserved — best case)
- `162-169 passed, 0-7 failed, 3 skipped` (some failures recovered — likely outcome since these serializers were silently broken)
- `158-160 passed, 9-11 failed, 3 skipped` (slight regression — investigate before continuing)

If REGRESSED, BLOCK. Diff `/tmp/pytest_baseline.txt` vs `/tmp/pytest_after_backend.txt` and identify which test newly fails.

If RECOVERED or PRESERVED, continue.

- [ ] **Step 2: Diff pytest baselines**

```bash
diff /tmp/pytest_baseline.txt /tmp/pytest_after_backend.txt | head -30
```

Take note of any tests that newly pass (improvement) or newly fail (need investigation).

- [ ] **Step 3: Atomic backend commit**

```bash
cd D:/VYNTIA
git status --short
git add apps/api/api/v1/rrhh/serializers.py apps/api/api/v1/rrhh/remuneraciones_serializers.py apps/api/api/v1/vacaciones/serializers.py
git diff --cached --stat | tail -5
git commit -m "$(cat <<'EOF'
fix(L3.10.4d): backend serializer JSON keys aligned with renamed Python attrs

Backend serializer Meta.fields referenced 'estado'/'activo' but the
underlying model Python attributes were renamed to status/is_active in
L3.10.2 (db_column preserves the Spanish DB column). DRF reads attribute
names — these fields were silently broken.

Fixes 14 Meta.fields entries across 3 serializer files:
- apps/api/api/v1/rrhh/serializers.py: ConfiguracionRemuneracion, ConfiguracionAfp
- apps/api/api/v1/rrhh/remuneraciones_serializers.py: 12 entries (Afp, UIT,
  Compensation, MonthlyPayroll list+detail, MassDeduction list+detail,
  PaySlip list+detail, PaymentSchedule list+detail)
- apps/api/api/v1/vacaciones/serializers.py: ConfiguracionVacaciones

Also fixes ConfiguracionUitSerializer.get_es_activo which read obj.estado
(non-existent attr) and silently returned False — now reads obj.status.

Out of scope (separate sub-PR):
- Preserved-Spanish state fields on other entities (estado_rol, estado_modulo,
  estado_area, etc.) — those are Interpretation B per audit
- Other unrelated serializer bugs (duplicate id in RolPermisosSerializer,
  broken source='contrato.contrato_id' in vacation serializers)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Frontend interface rename — `contractsService.ts`

**Files:**
- Modify: `apps/web/src/services/contractsService.ts`

- [ ] **Step 1: Inspect interfaces with `estado`**

```bash
grep -nE "^\s+estado\??\s*:" D:/VYNTIA/apps/web/src/services/contractsService.ts
```

Expected: 3 matches at ~lines 35, 64, 92 (Contrato, ContratoListItem, ContratoFilters).

- [ ] **Step 2: Replace `estado: string` and `estado?: string` with `status` variants**

Because all `estado:` declarations in this file are on Contract-related types (renamed), `replace_all` is safe. But the file ALSO has `estado_texto?: string` (Spanish, preserved) and possibly `estado_contrato`-style strings — check context.

```bash
grep -n "estado" D:/VYNTIA/apps/web/src/services/contractsService.ts | head -15
```

If only the 3 bare `estado:` declarations need rename and no other `estado` refs in the file body need changing, use:

- File: `apps/web/src/services/contractsService.ts`
- Edit 1: old `estado: string;` → new `status: string;` (replace_all: true if multiple)
- Edit 2: old `estado?: string;` → new `status?: string;` (replace_all: true if multiple)

If `estado` appears in other contexts (e.g., `ESTADO_CONTRATO_LABELS` constant key string `'activo'`, `'vencido'`, etc.), do NOT replace those — only the bare `estado:` field declarations.

Practical approach: do per-line Edit with `old_string` being the full declaration line, e.g.:
- old: `  estado: string;`  (with leading spaces)
- new: `  status: string;`

For each of the 3 lines.

- [ ] **Step 3: Verify**

```bash
grep -nE "^\s+estado\??\s*:" D:/VYNTIA/apps/web/src/services/contractsService.ts || echo "OK: no estado: declarations"
```

Expected: `OK`.

- [ ] **Step 4: TypeScript build to check downstream impact**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -30
cd D:/VYNTIA
```

Expected: build errors of the form `Property 'estado' does not exist on type 'Contrato'. Did you mean 'status'?` in consumer files. Note the file paths — they're consumer files for Contract.

If no errors, the rename was already self-consistent (all consumers use a generic typing or already-renamed fields). Continue.

---

## Task 8: Frontend interface rename — `payrollService.ts`

**Files:**
- Modify: `apps/web/src/services/payrollService.ts`

This file has the most renames (~7 interfaces).

- [ ] **Step 1: Inspect interfaces with `estado`**

```bash
grep -nE "^\s+estado\??\s*:" D:/VYNTIA/apps/web/src/services/payrollService.ts
```

Expected: ~7-9 matches, on interfaces ConfiguracionAfp, ConfiguracionUit, ConfiguracionRemuneracion, PlanillaMensual, DescuentoMasivo, BoletaPago, CalendarioPago.

Look for any `EstadoXxx` string-union types (e.g., `EstadoPlanilla`, `EstadoBoleta`) — these stay as type aliases. Only the FIELD `estado: EstadoXxx` is renamed to `status: EstadoXxx`.

- [ ] **Step 2: Per-interface Edit**

For each interface, use Edit tool with `old_string` being a multi-line block including the interface name and the line with `estado` to make it unique:

Example pattern:
- old:
  ```
  export interface PlanillaMensual {
    ...
    estado: EstadoPlanilla;
  ```
- new:
  ```
  export interface PlanillaMensual {
    ...
    status: EstadoPlanilla;
  ```

Repeat per interface.

Alternative: if all `estado:` declarations are on renamed interfaces (verify with manual inspection), use `replace_all: true` of:
- old: `estado: EstadoPlanilla` → new: `status: EstadoPlanilla`
- old: `estado?: EstadoPlanilla` → new: `status?: EstadoPlanilla`

For each EstadoXxx variant. Trickier than `contractsService.ts` because there are multiple types.

Safer: do per-occurrence Edit with full multi-line context.

- [ ] **Step 3: Verify**

```bash
grep -nE "^\s+estado\??\s*:" D:/VYNTIA/apps/web/src/services/payrollService.ts || echo "OK"
```

Expected: `OK` (or only the matches that should remain — none, in this case).

---

## Task 9: Frontend interface rename — `timeOffService.ts`

**Files:**
- Modify: `apps/web/src/services/timeOffService.ts`

- [ ] **Step 1: Inspect**

```bash
grep -nE "^\s+activo\??\s*:" D:/VYNTIA/apps/web/src/services/timeOffService.ts
```

Expected: 2 matches at ~lines 7 and 154 (ConfiguracionVacaciones, ConfiguracionVacacionesForm).

- [ ] **Step 2: Replace**

Use Edit tool with full line context:
- File: `apps/web/src/services/timeOffService.ts`
- Edit 1: old `  activo: boolean` → new `  is_active: boolean` (verify exact whitespace and trailing chars first)
- Edit 2: old `  activo?: boolean` → new `  is_active?: boolean`

If both lines look identical (no surrounding context to disambiguate), use the line-number-based Edit with surrounding context (1-2 lines above/below).

- [ ] **Step 3: Verify**

```bash
grep -nE "^\s+activo\??\s*:" D:/VYNTIA/apps/web/src/services/timeOffService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 10: Frontend interface rename — `useRemuneraciones.ts`

**Files:**
- Modify: `apps/web/src/hooks/useRemuneraciones.ts`

This hook has interface declarations referencing `estado?: EstadoXxx` patterns. Per audit, `useRemuneraciones.ts:74` has `activo?: boolean`. Also various `estado?: EstadoXxx` decls at lines 25, 73, 146, 196, 324, 390, 491, 551.

- [ ] **Step 1: Inspect**

```bash
grep -nE "^\s+(estado|activo)\??\s*:" D:/VYNTIA/apps/web/src/hooks/useRemuneraciones.ts
```

Expected: ~10 matches (mix of `estado` and `activo`).

- [ ] **Step 2: Determine which need rename**

These declarations are filter-params types. They map to the corresponding payroll service request payloads. Since payroll backend uses `status` / `is_active` post-this-PR, all should rename:
- `estado?: "activo" | "inactivo"` → `status?: "activo" | "inactivo"` (the values stay Spanish — domain literals — only the field name changes)
- `estado?: EstadoPlanilla` → `status?: EstadoPlanilla`
- `activo?: boolean` → `is_active?: boolean`

- [ ] **Step 3: Per-line Edit for each declaration**

Use Edit with full line context for each occurrence. Be careful: some `estado` references might be inside string-union types (`type EstadoBoleta = "activo" | "anulado"`) — those are TYPE NAMES, not field names. NOT renamed.

After each Edit, run grep to verify the next occurrence still exists (sanity check that you're not double-replacing).

- [ ] **Step 4: Verify**

```bash
grep -nE "^\s+(estado|activo)\??\s*:" D:/VYNTIA/apps/web/src/hooks/useRemuneraciones.ts || echo "OK"
```

Expected: `OK` (no field-name declarations remaining; type aliases like `EstadoPlanilla` remain in type positions, which is fine).

---

## Task 11: Frontend consumer fixes — TypeScript-driven

After the interface renames, run the TypeScript build to enumerate all consumer fixes needed.

- [ ] **Step 1: Run `npm run build` and capture errors**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tee /tmp/tsc_errors.txt | tail -50
cd D:/VYNTIA
```

Expected output: list of TS errors of the form:
```
src/pages/contratos/ContratosPage.tsx:NN:NN - error TS2551: Property 'estado' does not exist on type 'Contrato'. Did you mean 'status'?
```

- [ ] **Step 2: Inventory all error sites**

```bash
grep -E "error TS25[0-9][0-9].*'(estado|activo)'" /tmp/tsc_errors.txt | sort -u
```

This gives a per-file list of broken access patterns.

- [ ] **Step 3: Fix each error**

Per-file: open the file, find the `.estado` or `.activo` access, change to `.status` or `.is_active`. Use Edit with full context line.

For files with multiple errors on the same access pattern, `replace_all: true` may be safe IF the file only deals with renamed entities. Otherwise per-occurrence.

Examples:
- `solicitud.estado` (where `solicitud` is `SolicitudVacaciones` — preserved Spanish) → DO NOT TOUCH
- `boleta.estado` (where `boleta` is `BoletaPago` — renamed) → change to `boleta.status`

The TypeScript error message itself disambiguates: it tells you exactly which type is involved.

- [ ] **Step 4: Re-run build until clean**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -10
cd D:/VYNTIA
```

Expected: build success (or pre-existing TS errors only, NOT related to `estado`/`activo`).

Iterate Step 3 → 4 until all renamed-entity TS errors are gone.

- [ ] **Step 5: Spot-check unaffected entities**

Since `estado` is a common Spanish word, verify that consumers using preserved-Spanish entities (Role, Permission, Area, Empleado, EmploymentData, FamilyMember, AcademicRecord, DigitalDocument, OnboardingProcess, VacationPeriod, VacationRequest, VacationGrant) STILL access their state fields correctly:

```bash
cd D:/VYNTIA/apps/web
echo "=== Should still work — preserved-Spanish state field access ==="
grep -rEn "\.estado_(empleado|civil|rol|permiso|modulo|area|datos|documento|familiar|estudios|onboarding|periodo|solicitud|goce|usuario|laboral)\b" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l
cd D:/VYNTIA
```

Expected: count > 0 (these refs should still exist — they're correct).

---

## Task 12: Verification — global audit

- [ ] **Step 1: Backend `'estado'` / `'activo'` quote-string final state**

```bash
cd D:/VYNTIA/apps/api

echo "=== Bare 'estado' as Meta.fields entry in scope-relevant serializers ==="
grep -nE "^\s+'estado'," api/v1/rrhh/serializers.py api/v1/rrhh/remuneraciones_serializers.py api/v1/rrhh/contratos_serializers.py api/v1/vacaciones/serializers.py 2>/dev/null

echo ""
echo "=== Bare 'activo' as Meta.fields entry ==="
grep -nE "^\s+'activo'," api/v1/rrhh/serializers.py api/v1/rrhh/remuneraciones_serializers.py api/v1/vacaciones/serializers.py 2>/dev/null

cd D:/VYNTIA
```

Expected: empty results (no bare `'estado'` / `'activo'` Meta.fields remain in scope-relevant serializers).

If results show preserved-Spanish like `'estado_modulo'`, `'estado_rol'`, etc. — those are NOT bare `'estado'` and the regex `'estado'` (with quotes around just `estado`) wouldn't match them. So results should be truly empty.

- [ ] **Step 2: Backend `obj.estado` final state**

```bash
grep -rEn "obj\.estado\b" D:/VYNTIA/apps/api/api/v1/ D:/VYNTIA/apps/api/app_rrhh/ 2>/dev/null | grep -v __pycache__ || echo "OK: no obj.estado refs"
```

Expected: `OK`. (Compare to pre-flight Step 5 which had 1 ref at remuneraciones_serializers.py:101.)

- [ ] **Step 3: Frontend interfaces — bare `estado:` / `activo:` declarations**

```bash
cd D:/VYNTIA/apps/web

echo "=== bare 'estado:' interface declarations in services + hooks ==="
grep -nE "^\s+estado\??\s*:" src/services/contractsService.ts src/services/payrollService.ts src/hooks/useRemuneraciones.ts 2>/dev/null || echo "OK: no estado: declarations in renamed scope"

echo ""
echo "=== bare 'activo:' interface declarations in services + hooks ==="
grep -nE "^\s+activo\??\s*:" src/services/timeOffService.ts src/hooks/useRemuneraciones.ts 2>/dev/null || echo "OK: no activo: declarations in renamed scope"

cd D:/VYNTIA
```

Expected: both `OK`. (Other services may still have `estado: string` for preserved-Spanish entities — that's correct.)

- [ ] **Step 4: Confirm TS build clean**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: build success.

- [ ] **Step 5: Confirm `generated/` NOT touched**

```bash
cd D:/VYNTIA
git diff --name-only HEAD | grep "src/generated/" || echo "OK: generated/ untouched"
```

Expected: `OK`.

- [ ] **Step 6: Confirm preserved entities still typed correctly**

Check a few preserved-Spanish entity interfaces are intact:

```bash
cd D:/VYNTIA/apps/web
echo "=== Role.estado_rol (or equivalent) — should still exist as field name in some interface ==="
grep -nE "estado_rol|estado_permiso|estado_modulo|estado_area|estado_empleado" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | head -5
cd D:/VYNTIA
```

Expected: at least a few matches (these field names appear in lib/api.ts Role/Permission interfaces or similar). If 0 matches, that means we accidentally removed them — investigate.

---

## Task 13: Smoke — frontend lint + vitest

- [ ] **Step 1: ESLint delta**

```bash
cd D:/VYNTIA/apps/web
ERRORS_NOW=$(npm run lint 2>&1 | grep -E "^\s*[0-9]+:[0-9]+" | wc -l)
git stash push --include-untracked -m "lint-baseline-check" 2>&1 | tail -2
ERRORS_BASELINE=$(npm run lint 2>&1 | grep -E "^\s*[0-9]+:[0-9]+" | wc -l)
git stash pop 2>&1 | tail -2
echo "Lint errors now: $ERRORS_NOW"
echo "Lint errors on master: $ERRORS_BASELINE"
echo "Delta: $((ERRORS_NOW - ERRORS_BASELINE))"
cd D:/VYNTIA
```

Expected delta: `0`.

- [ ] **Step 2: Vitest**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: `Tests 7 passed (7)`, `Test Files 1 failed | 2 passed (3)`.

- [ ] **Step 3: Backend pytest final**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tee /tmp/pytest_final.txt | tail -3
cd D:/VYNTIA
```

Expected: same as Task 6 Step 1 (no further regression). Compare with `/tmp/pytest_baseline.txt`:

```bash
diff /tmp/pytest_baseline.txt /tmp/pytest_final.txt | head -30
```

If any test that was passing now fails, BLOCK. If we see RECOVERED tests (tests that were failing now pass), document them in the commit message.

---

## Task 14: Frontend atomic commit

- [ ] **Step 1: Stage frontend changes**

```bash
cd D:/VYNTIA
git status --short | head -30
git add apps/web/
```

- [ ] **Step 2: Confirm staged delta**

```bash
git diff --cached --stat | tail -10
```

Expected: ~5-10 files modified (3 services + 1 hook + 5-15 consumer files).

- [ ] **Step 3: Commit**

```bash
git commit -m "$(cat <<'EOF'
chore(L3.10.4d): frontend state fields rename — align with backend post-L3.10.2

Renames TS interface fields and consumer access patterns to consume the
new English JSON keys emitted by the backend serializer fix in the
previous commit.

Frontend changes:
- contractsService.ts: Contrato/ContratoListItem/ContratoFilters estado -> status
- payrollService.ts: ConfiguracionAfp/Uit/Remuneracion/PlanillaMensual/
  DescuentoMasivo/BoletaPago/CalendarioPago estado -> status
- timeOffService.ts: ConfiguracionVacaciones/Form activo -> is_active
- useRemuneraciones.ts: filter params + interface fields estado -> status, activo -> is_active
- Consumer components/pages: .estado -> .status / .activo -> .is_active
  on the renamed entities only (TypeScript-driven inventory)

Preserved Spanish (NOT touched per Option B):
- estado_empleado, estado_civil, estado_rol, estado_permiso, estado_modulo,
  estado_area, estado_familiar, estado_documento, estado_estudios,
  estado_periodo, estado_solicitud, estado_goce, estado_datos, estado_laboral,
  estado_onboarding, estado_usuario, vigencia_estado_seguro
- All EstadoXxx string-union type aliases (EstadoPlanilla, EstadoBoleta, etc.)
- Role.estado, Permission.estado in lib/api.ts (preserved-Spanish per audit)

Verification:
- grep "estado:|activo:" in renamed services -> 0 matches
- npm run build: success
- npm test: 7 passed (baseline preserved)
- npm run lint: 0 net new errors
- Backend pytest: $(if recovered, mention) / no regression vs baseline 161/8/3

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

(Adjust the pytest line to reflect actual outcome — preserved 161/8/3, or recovered to a higher passed count.)

- [ ] **Step 4: Verify branch state**

```bash
git log --oneline vyntia/L3.10.4d-state-fields ^master
git status --short
```

Expected: 3 commits on branch (`docs(L3.10.4d) plan` + `fix(L3.10.4d) backend` + `chore(L3.10.4d) frontend`), clean working tree.

---

## Task 15: Merge to master + roadmap update

- [ ] **Step 1: Confirm user authorization**

PAUSE before merge. Only proceed if user approves.

- [ ] **Step 2: Merge --no-ff**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/L3.10.4d-state-fields -m "Merge L3.10.4d: state fields rename (backend serializer fix + frontend rename)"
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

Expected: all baselines preserved or improved.

- [ ] **Step 4: Update roadmap**

Edit `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`:
- Mark L3.10.4d ✅ merged with commit hash
- If pytest baseline IMPROVED (failures recovered), document the new baseline (e.g., 165/4/3)
- Note that L3.10.4e remains pending (PK type change)

- [ ] **Step 5: Update memory**

Edit `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- L3.10.4d ✅ merged
- New pytest baseline if applicable
- Next: L3.10.4e (PK type change)

- [ ] **Step 6: Commit roadmap**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.10.4d): mark L3.10.4d merged"
```

---

## Notas para el ejecutor

- **Two-sided refactor.** Backend serializer fix (commit 1) + frontend rename (commit 2) in same branch. Atomic merge.
- **The backend fix repairs latent bugs.** The `'estado'` Meta.fields entries weren't just stylistic — they were broken. DRF `ModelSerializer` reads Python attribute names (not `db_column` values). After L3.10.2 renamed the model attributes, these serializers stopped emitting the `estado` field at all (or emitted garbage). Pytest may RECOVER some failures.
- **Strict Option B.** Only rename fields where backend already has `status`/`is_active` Python attribute. Preserved-Spanish (estado_rol, estado_modulo, etc.) NOT touched in this PR.
- **TypeScript-driven consumer fix.** After interface rename, `npm run build` enumerates every broken consumer. Fix each error with confidence — TS knows the type involved.
- **Don't over-rename.** `EstadoPlanilla`/`EstadoBoleta` are TYPE alias names (string unions), not field names. They stay. Only the FIELD `estado: EstadoXxx` becomes `status: EstadoXxx`.
- **`creado_por_nombre` SerializerMethodField mismatch out of scope.** Audit found the backend still emits `creado_por_nombre` while frontend (post-L3.10.4c) expects `created_by_nombre`. Separate cleanup PR.
- **Risk level:** Medium. Backend changes are mechanical but touch JSON contracts (live endpoints behavior changes). Frontend changes are TypeScript-checked (compiler catches consumer breakage).
