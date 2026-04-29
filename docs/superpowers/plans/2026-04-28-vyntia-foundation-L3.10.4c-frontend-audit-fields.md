# VYNTIA Foundation L3.10.4c — Frontend Audit Fields Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Renombrar 42 referencias frontend a audit fields legacy españoles (`fecha_creacion`, `fecha_actualizacion`, `fecha_modificacion`, `creado_por`, `modificado_por`) por sus equivalentes en inglés (`created_at`, `updated_at`, `created_by`, `updated_by`) — alineando los TS interfaces y JSX consumers con el contrato API que el backend ya expone post-L3.10.2.

**Architecture:** Frontend-only refactor mecánico. Reemplaza nombres de propiedad en TS interfaces, accesos a propiedades, y JSX renderings. NO toca state fields (`estado`/`activo` — diferido a L3.10.4d). NO toca PKs (`empleado_id`→`id` UUID — diferido a L3.10.4e). NO renombra archivos de servicio. NO toca dominio HR (`fecha_nacimiento`, `fecha_ingreso`, `fecha_inicio_suspension_renta`, etc. — preservados en español per spec § 3.6.1 Option B).

**Tech Stack:** React 18 + TypeScript + Vite. Modificaciones puramente sintácticas — no nuevos imports, no nuevos paquetes.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.6 (convención de fields) + § 3.6.1 (Option B scope).

**Pre-condiciones:**
- L3.10.4b mergeada a master (commit `8d3666e8` "Merge L3.10.4b: frontend URL refactor (consume English paths)") + commit `d5f004e9` (roadmap update)
- Frontend: 0 legacy URL refs, todas las llamadas API consumen `/api/v1/<inglés>/...`
- Frontend baseline: vitest 7 passed, 1 file load-failure (Playwright e2e capture, pre-existing)
- Frontend `npm run build` debe pasar
- Backend pytest baseline: 161 passed, 8 failed, 3 skipped

**Scope decision (sub-PR de L3.10.4):**
- L3.10.4a ✅ Backend URL refactor
- L3.10.4b ✅ Frontend URL refactor
- **L3.10.4c (este plan)** — Frontend audit fields rename (mecánico, ~42 refs)
- L3.10.4d ⏳ Frontend state fields rename (`estado`/`activo` — requiere audit per-occurrence)
- L3.10.4e ⏳ Frontend PK type change (`<entity>_id: number` → `id: string` UUID, ~309 refs, semantic migration)
- L3.10.4f ⏳ Frontend file renames (`contratosService.ts → contractsService.ts`, etc.)
- L3.11 ⏳ Cleanup app_rrhh/ + remove legacy URLs

**Out of scope (NO hacer en L3.10.4c):**
- State field renames `estado: string` → `status: string`, `activo: boolean` → `is_active: boolean` (L3.10.4d) — requires careful per-file audit to distinguish backend platform state from local UI state, design tokens, label keys
- PK rename `<entity>_id: number` → `id: string` UUID (L3.10.4e) — type change with semantic propagation
- File renames (L3.10.4f)
- Domain Spanish vocabulary (`fecha_nacimiento`, `fecha_ingreso`, `fecha_cese`, `fecha_inicio_suspension_renta`, `nombres`, `apellido_paterno`, `tipo_documento`, `numero_cuspp`, `estado_empleado`, `estado_civil`, `vigencia_estado_seguro`, `validado_por`, `digitalizado_por`, `subido_por`, etc.) — preservados en español per spec § 3.6.1 Option B
- `apps/web/src/generated/api/services/*.ts` — auto-generado del schema OpenAPI, no se toca

---

## Audit field rename table (canonical)

Backend post-L3.10.2 expone los siguientes Python attribute names (los que serializa DRF). La columna SQL real (`db_column='fecha_creacion'` etc.) está oculta para el frontend.

| Legacy Spanish field | New English field | Backend mapping |
|---|---|---|
| `fecha_creacion` | `created_at` | `models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')` |
| `fecha_actualizacion` | `updated_at` | `models.DateTimeField(auto_now=True, db_column='fecha_actualizacion')` |
| `fecha_modificacion` | `updated_at` | `models.DateTimeField(auto_now=True, db_column='fecha_modificacion')` (Contract, ContractAmendment) |
| `creado_por` | `created_by` | `models.ForeignKey(User, db_column='creado_por_id')` |
| `modificado_por` | `updated_by` | `models.ForeignKey(User, db_column='modificado_por_id')` |

**Nota:** `fecha_registro` no aparece en el frontend (verificado con grep — 0 matches), aunque es otro alias backend para `created_at` (Empleado lo usa). No requiere acción.

**Nota:** `fecha_modificacion` y `fecha_actualizacion` ambos mapean a `updated_at` en backend. En frontend solo aparece `fecha_modificacion` en 2 archivos (UserDetailsModal, contratosService) — ambos se renombran a `updated_at`.

---

## Files inventory

| Archivo | `fecha_creacion` | `fecha_actualizacion` | `fecha_modificacion` | `creado_por`/`modificado_por` | Total refs |
|---|:---:|:---:|:---:|:---:|:---:|
| `src/components/areas/DeleteAreaDialog.tsx` | 1 | 0 | 0 | 0 | 1 |
| `src/components/users/modals/RoleManagementModal.tsx` | 2 | 0 | 0 | 0 | 2 |
| `src/components/users/modals/UserDetailsModal.tsx` | 2 | 0 | 1 | 0 | 3 |
| `src/components/vacaciones/CalendarioVacaciones.tsx` | 1 | 0 | 0 | 0 | 1 |
| `src/pages/PlantillasDocumentosPage.tsx` | 1 | 0 | 0 | 0 | 1 |
| `src/pages/vacaciones/ConfiguracionPage.tsx` | ? | ? | 0 | 0 | ? |
| `src/pages/vacaciones/PeriodosPage.tsx` | ? | ? | 0 | 0 | ? |
| `src/pages/vacaciones/ReportesPage.tsx` | ? | 0 | 0 | 0 | ? |
| `src/pages/vacaciones/SolicitudesPage.tsx` | ? | 0 | 0 | 0 | ? |
| `src/services/contratosService.ts` | ? | 0 | ? | 0 | ? |
| `src/services/normalizers/rrhhNormalizers.ts` | ? | 0 | 0 | 0 | ? |
| `src/services/plantillasService.ts` | ? | 0 | 0 | 0 | ? |
| `src/services/remuneracionesService.ts` | ? | ? | 0 | ? | ? |
| `src/services/securityService.ts` | ? | ? | 0 | 0 | ? |
| `src/services/vacacionesService.ts` | ? | 0 | 0 | 0 | ? |

**Total verified:** 42 audit field refs across 15 files (UserDetailsModal also counts; some `?` cells = exact ref count not pre-checked but file definitely contains the field). Pre-flight Step 5 will confirm exact counts per-file.

**File scope note:**
- 6 service files (`contratosService`, `plantillasService`, `remuneracionesService`, `securityService`, `vacacionesService`, `normalizers/rrhhNormalizers`)
- 9 page/component files (4 vacaciones pages + UserDetailsModal/RoleManagementModal/DeleteAreaDialog/CalendarioVacaciones + PlantillasDocumentosPage)

**NO se toca:**
- `apps/web/src/generated/` (auto-generated)
- Cualquier campo dominio HR español (`fecha_nacimiento`, `fecha_ingreso`, `fecha_cese`, `fecha_inicio_suspension_renta`, `fecha_fin_suspension_renta`)
- Variables/parámetros locales con substring `fecha_` (e.g., `selectedFecha`, `fechaInicio`, `fechaFin`) — esos son state local, no fields del API
- Cualquier ocurrencia bajo `apps/web/src/generated/`

---

## Definition of Done

- [ ] 15 archivos modificados — todas las 42 audit field refs renombradas a inglés
- [ ] `grep -rn "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" apps/web/src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated` retorna **0 matches** (excluyendo dominio preservado, comentarios, etc. — verificar cuidadosamente)
- [ ] Domain Spanish fields preservados: grep para `fecha_nacimiento|fecha_ingreso|fecha_cese|fecha_inicio_suspension|fecha_fin_suspension` debe seguir retornando los counts pre-refactor
- [ ] `npm run lint` clean (no nuevos warnings/errors vs baseline)
- [ ] `npm run build` produce un bundle exitoso
- [ ] `npm test` (vitest) preserva baseline: **7 passed, 1 file load-failure**
- [ ] Backend pytest baseline preservado: **161 passed, 8 failed, 3 skipped** (no se toca backend)
- [ ] Branch `vyntia/L3.10.4c-frontend-audit-fields` mergeada a master con `--no-ff`
- [ ] Roadmap (`docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`) actualizado: L3.10.4c ✅, L3.10.4d (state fields) NEXT
- [ ] Memory `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md` actualizado

---

## Task 1: Pre-flight — branch, baseline, snapshot

- [ ] **Step 1: Confirmar pwd y master limpio post-L3.10.4b**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -5
```

Expected: HEAD = `d5f004e9 docs(L3.10.4b): mark L3.10.4b merged, L3.10.4c (frontend field rename) as next` o más reciente. `git status` muestra ÚNICAMENTE el plan file untracked (`docs/superpowers/plans/2026-04-28-vyntia-foundation-L3.10.4c-frontend-audit-fields.md`).

- [ ] **Step 2: Confirmar backend baseline**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `System check identified no issues` + `161 passed, 8 failed, 3 skipped`.

- [ ] **Step 3: Confirmar frontend baseline build**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: build success.

- [ ] **Step 4: Confirmar frontend baseline tests**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: `Tests 7 passed (7)`, `Test Files 1 failed | 2 passed (3)`.

- [ ] **Step 5: Snapshot of audit field counts (target = 0 after refactor)**

```bash
cd D:/VYNTIA/apps/web
echo "=== fecha_creacion (target: 0) ==="
grep -rn "fecha_creacion" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "=== fecha_actualizacion (target: 0) ==="
grep -rn "fecha_actualizacion" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "=== fecha_modificacion (target: 0) ==="
grep -rn "fecha_modificacion" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "=== fecha_registro (target: 0, expected current = 0) ==="
grep -rn "fecha_registro" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "=== creado_por / modificado_por (target: 0) ==="
grep -rEn "creado_por|modificado_por" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l

echo ""
echo "=== Domain fields preservados (must NOT change post-refactor) ==="
echo "fecha_nacimiento:"
grep -rn "fecha_nacimiento" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "fecha_ingreso:"
grep -rn "fecha_ingreso" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "fecha_cese:"
grep -rn "fecha_cese" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "fecha_inicio_suspension / fecha_fin_suspension:"
grep -rEn "fecha_(inicio|fin)_suspension" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
cd D:/VYNTIA
```

Save these counts. The first 5 must drop to 0; the domain counts must remain unchanged post-refactor.

- [ ] **Step 6: Crear branch L3.10.4c**

```bash
git checkout -b vyntia/L3.10.4c-frontend-audit-fields
git status --short
```

---

## Task 2: Comitear el plan

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-28-vyntia-foundation-L3.10.4c-frontend-audit-fields.md
git commit -m "$(cat <<'EOF'
docs(L3.10.4c): add frontend audit fields rename plan

Frontend-only sub-PR of L3.10.4. Renames 42 audit field refs
(fecha_creacion -> created_at, fecha_actualizacion -> updated_at,
fecha_modificacion -> updated_at, creado_por -> created_by,
modificado_por -> updated_by) across 15 files. Mechanical, low risk.

Out of scope:
- State fields (estado/activo) — deferred to L3.10.4d
- PK type change (entity_id -> id UUID) — deferred to L3.10.4e
- File renames — deferred to L3.10.4f

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Service files — `contratosService.ts`

**Files:**
- Modify: `apps/web/src/services/contratosService.ts`

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/contratosService.ts`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Replace `fecha_modificacion`**

- old: `fecha_modificacion`
- new: `updated_at`
- replace_all: true

- [ ] **Step 3: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/services/contratosService.ts || echo "OK"
```

Expected: `OK` (no matches).

---

## Task 4: Service files — `plantillasService.ts`

**Files:**
- Modify: `apps/web/src/services/plantillasService.ts`

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/plantillasService.ts`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/services/plantillasService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 5: Service files — `remuneracionesService.ts`

**Files:**
- Modify: `apps/web/src/services/remuneracionesService.ts`

This file has multiple audit fields including `creado_por`/`modificado_por`.

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Replace `fecha_actualizacion`**

- old: `fecha_actualizacion`
- new: `updated_at`
- replace_all: true

- [ ] **Step 3: Replace `creado_por`**

- old: `creado_por`
- new: `created_by`
- replace_all: true

- [ ] **Step 4: Replace `modificado_por`**

- old: `modificado_por`
- new: `updated_by`
- replace_all: true

- [ ] **Step 5: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/services/remuneracionesService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 6: Service files — `securityService.ts`

**Files:**
- Modify: `apps/web/src/services/securityService.ts`

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Replace `fecha_actualizacion`**

- old: `fecha_actualizacion`
- new: `updated_at`
- replace_all: true

- [ ] **Step 3: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/services/securityService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 7: Service files — `vacacionesService.ts`

**Files:**
- Modify: `apps/web/src/services/vacacionesService.ts`

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/services/vacacionesService.ts || echo "OK"
```

Expected: `OK`.

---

## Task 8: Service files — `normalizers/rrhhNormalizers.ts`

**Files:**
- Modify: `apps/web/src/services/normalizers/rrhhNormalizers.ts`

The filename keeps "rrhh" (file rename is L3.10.4f); only file CONTENTS change.

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/normalizers/rrhhNormalizers.ts`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/services/normalizers/rrhhNormalizers.ts || echo "OK"
```

Expected: `OK`.

---

## Task 9: Component — `DeleteAreaDialog.tsx`

**Files:**
- Modify: `apps/web/src/components/areas/DeleteAreaDialog.tsx`

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/components/areas/DeleteAreaDialog.tsx`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/components/areas/DeleteAreaDialog.tsx || echo "OK"
```

Expected: `OK`.

---

## Task 10: Component — `RoleManagementModal.tsx`

**Files:**
- Modify: `apps/web/src/components/users/modals/RoleManagementModal.tsx`

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/components/users/modals/RoleManagementModal.tsx`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/components/users/modals/RoleManagementModal.tsx || echo "OK"
```

Expected: `OK`.

---

## Task 11: Component — `UserDetailsModal.tsx`

**Files:**
- Modify: `apps/web/src/components/users/modals/UserDetailsModal.tsx`

This component has both `fecha_creacion` (2 refs) and `fecha_modificacion` (1 ref).

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/components/users/modals/UserDetailsModal.tsx`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Replace `fecha_modificacion`**

- old: `fecha_modificacion`
- new: `updated_at`
- replace_all: true

- [ ] **Step 3: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/components/users/modals/UserDetailsModal.tsx || echo "OK"
```

Expected: `OK`.

---

## Task 12: Component — `vacaciones/CalendarioVacaciones.tsx`

**Files:**
- Modify: `apps/web/src/components/vacaciones/CalendarioVacaciones.tsx`

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/components/vacaciones/CalendarioVacaciones.tsx`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/components/vacaciones/CalendarioVacaciones.tsx || echo "OK"
```

Expected: `OK`.

---

## Task 13: Page — `PlantillasDocumentosPage.tsx`

**Files:**
- Modify: `apps/web/src/pages/PlantillasDocumentosPage.tsx`

- [ ] **Step 1: Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/PlantillasDocumentosPage.tsx`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: Verify**

```bash
grep -n "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/pages/PlantillasDocumentosPage.tsx || echo "OK"
```

Expected: `OK`.

---

## Task 14: Vacaciones pages — 4 files

**Files:**
- Modify: `apps/web/src/pages/vacaciones/ConfiguracionPage.tsx`
- Modify: `apps/web/src/pages/vacaciones/PeriodosPage.tsx`
- Modify: `apps/web/src/pages/vacaciones/ReportesPage.tsx`
- Modify: `apps/web/src/pages/vacaciones/SolicitudesPage.tsx`

`ConfiguracionPage` y `PeriodosPage` tienen `fecha_creacion` Y `fecha_actualizacion`. `ReportesPage` y `SolicitudesPage` solo tienen `fecha_creacion`.

- [ ] **Step 1: ConfiguracionPage — Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/vacaciones/ConfiguracionPage.tsx`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 2: ConfiguracionPage — Replace `fecha_actualizacion`**

- old: `fecha_actualizacion`
- new: `updated_at`
- replace_all: true

- [ ] **Step 3: PeriodosPage — Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/vacaciones/PeriodosPage.tsx`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 4: PeriodosPage — Replace `fecha_actualizacion`**

- old: `fecha_actualizacion`
- new: `updated_at`
- replace_all: true

- [ ] **Step 5: ReportesPage — Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/vacaciones/ReportesPage.tsx`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 6: SolicitudesPage — Replace `fecha_creacion`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/vacaciones/SolicitudesPage.tsx`
- old: `fecha_creacion`
- new: `created_at`
- replace_all: true

- [ ] **Step 7: Verify all 4 files**

```bash
grep -rn "fecha_creacion\|fecha_actualizacion\|fecha_modificacion\|creado_por\|modificado_por" D:/VYNTIA/apps/web/src/pages/vacaciones/ || echo "OK: no audit refs in vacaciones pages"
```

Expected: `OK`.

---

## Task 15: Global verification — zero audit refs in non-generated code

- [ ] **Step 1: Count audit refs (excluding generated)**

```bash
cd D:/VYNTIA/apps/web
echo "=== Legacy audit field refs in src/ (excluding generated) — target: 0 ==="
grep -rEn "fecha_creacion|fecha_actualizacion|fecha_modificacion|fecha_registro|creado_por|modificado_por" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
cd D:/VYNTIA
```

Expected: `0`.

If non-zero, list them and add a Step in the relevant Task above to handle the leftover. Do not fix outside the task structure.

- [ ] **Step 2: Confirm new English audit fields are present**

```bash
cd D:/VYNTIA/apps/web
echo "=== created_at refs (new) ==="
grep -rEn "\bcreated_at\b" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "=== updated_at refs (new) ==="
grep -rEn "\bupdated_at\b" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "=== created_by refs (new) ==="
grep -rEn "\bcreated_by\b" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "=== updated_by refs (new) ==="
grep -rEn "\bupdated_by\b" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
cd D:/VYNTIA
```

Expected: `created_at` ~30, `updated_at` ~9, `created_by` and `updated_by` ~1 each. Sum should equal the pre-flight legacy count (~42).

- [ ] **Step 3: Confirm domain fields preserved (must match pre-flight Step 5)**

```bash
cd D:/VYNTIA/apps/web
echo "=== Domain fields preserved (must match pre-flight Step 5) ==="
echo "fecha_nacimiento:"
grep -rn "fecha_nacimiento" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "fecha_ingreso:"
grep -rn "fecha_ingreso" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "fecha_cese:"
grep -rn "fecha_cese" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
echo "fecha_inicio_suspension / fecha_fin_suspension:"
grep -rEn "fecha_(inicio|fin)_suspension" src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated | wc -l
cd D:/VYNTIA
```

Expected: identical counts to pre-flight Step 5 (no domain fields touched).

- [ ] **Step 4: Confirm `generated/` was NOT modified**

```bash
cd D:/VYNTIA
git status --short apps/web/src/generated/ || echo "generated/ clean (not modified)"
```

Expected: empty output (no changes to `generated/`).

---

## Task 16: Frontend smoke — lint, build, vitest

- [ ] **Step 1: ESLint**

```bash
cd D:/VYNTIA/apps/web
npm run lint 2>&1 | tail -20
cd D:/VYNTIA
```

Expected: same baseline (~403 pre-existing errors), 0 net new errors. To verify the delta is 0:

```bash
cd D:/VYNTIA/apps/web
ERRORS_NOW=$(npm run lint 2>&1 | grep -E "^\s*[0-9]+:[0-9]+" | wc -l)
git stash
ERRORS_BASELINE=$(npm run lint 2>&1 | grep -E "^\s*[0-9]+:[0-9]+" | wc -l)
git stash pop
echo "Lint errors now: $ERRORS_NOW"
echo "Lint errors on master: $ERRORS_BASELINE"
echo "Delta: $((ERRORS_NOW - ERRORS_BASELINE))"
cd D:/VYNTIA
```

Expected delta: `0`.

- [ ] **Step 2: TypeScript build**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -10
cd D:/VYNTIA
```

Expected: build success (~25s). Any TypeScript error here is critical — investigate.

If build fails with a type error like "Property 'fecha_creacion' does not exist on type X" then a consumer is reading the old field name from a renamed interface — find it and update it. If the error is about a domain field that this plan should NOT have touched, an over-eager Edit replaced it incorrectly — fix it.

- [ ] **Step 3: Vitest**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: `Tests 7 passed (7)`, `Test Files 1 failed | 2 passed (3)` (the 1 failed is the pre-existing Playwright capture).

- [ ] **Step 4: Backend baseline preserved**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `161 passed, 8 failed, 3 skipped`. Backend wasn't touched — must be identical.

---

## Task 17: Atomic commit

- [ ] **Step 1: Stage frontend changes**

```bash
cd D:/VYNTIA
git status --short | head -25
git add apps/web/
```

- [ ] **Step 2: Confirm staged delta**

```bash
git diff --cached --stat | tail -20
```

Expected: ~15 files modified, ~42 line changes (1:1 insertions/deletions).

- [ ] **Step 3: Commit**

```bash
git commit -m "$(cat <<'EOF'
chore(L3.10.4c): frontend audit fields rename — align with backend post-L3.10.2

Renames 42 audit field refs across 15 frontend files:
- fecha_creacion -> created_at
- fecha_actualizacion -> updated_at
- fecha_modificacion -> updated_at (Contract, ContractAmendment)
- creado_por -> created_by
- modificado_por -> updated_by

Domain Spanish fields preserved per spec § 3.6.1 Option B:
- fecha_nacimiento, fecha_ingreso, fecha_cese, fecha_inicio_suspension_renta,
  fecha_fin_suspension_renta — UNCHANGED
- nombres, apellido_paterno, tipo_documento, numero_cuspp,
  estado_empleado, estado_civil, vigencia_estado_seguro,
  validado_por, digitalizado_por, subido_por — UNCHANGED

Files modified (15):
- apps/web/src/components/areas/DeleteAreaDialog.tsx
- apps/web/src/components/users/modals/RoleManagementModal.tsx
- apps/web/src/components/users/modals/UserDetailsModal.tsx
- apps/web/src/components/vacaciones/CalendarioVacaciones.tsx
- apps/web/src/pages/PlantillasDocumentosPage.tsx
- apps/web/src/pages/vacaciones/{Configuracion,Periodos,Reportes,Solicitudes}Page.tsx
- apps/web/src/services/{contratos,plantillas,remuneraciones,security,vacaciones}Service.ts
- apps/web/src/services/normalizers/rrhhNormalizers.ts

Out of scope (deferred):
- State fields (estado/activo) — L3.10.4d
- PK type change (entity_id -> id UUID) — L3.10.4e
- File renames — L3.10.4f
- generated/api/services/* — auto-regenerated from updated OpenAPI schema

Verification:
- grep "fecha_creacion|fecha_actualizacion|fecha_modificacion|creado_por|modificado_por"
  apps/web/src/ (excluding generated/) -> 0 matches
- Domain fields counts unchanged
- npm run lint: 0 net new errors vs master
- npm run build: success
- npm test: 7 passed (baseline preserved)
- Backend pytest: 161/8/3 (untouched)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 4: Verify commits on branch**

```bash
git log --oneline vyntia/L3.10.4c-frontend-audit-fields ^master
git status --short
```

Expected: 2 commits (`docs(L3.10.4c) plan` + `chore(L3.10.4c)`), clean working tree.

---

## Task 18: Merge a master + roadmap update

- [ ] **Step 1: Confirmar autorización del usuario**

Pause antes del merge. Solo proceder si el usuario aprueba.

- [ ] **Step 2: Merge --no-ff**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/L3.10.4c-frontend-audit-fields -m "Merge L3.10.4c: frontend audit fields rename"
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
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: backend baseline preserved, frontend build success, tests pass.

- [ ] **Step 4: Update roadmap**

Edit `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`:
- Mark L3.10.4c ✅ merged with commit hash
- Update L3.10.4d entry to NEXT (state fields rename)
- Adjust L3.10.4 parent row count (now 5 sub-PRs after the audit-only split: 4a + 4b + 4c + 4d + 4e + 4f)

Use Edit tool to find and update the L3.10.4 section.

- [ ] **Step 5: Update memory**

Edit `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- L3.10.4c ✅ merged
- Next: L3.10.4d — frontend state fields rename (`estado`/`activo` → `status`/`is_active`, careful per-file audit needed)

- [ ] **Step 6: Commit roadmap**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.10.4c): mark L3.10.4c merged, L3.10.4d (frontend state fields) as next"
```

(Memory file is in `C:/Users/zeeke/.claude/...` — not git-tracked; just save.)

---

## Después de L3.10.4c

**Próximo plan:** L3.10.4d — frontend state fields rename. Renombrar `estado: string` → `status: string` y `activo: boolean` → `is_active: boolean` SOLO donde correspondan a backend platform state fields. Dificultad: hay que distinguir per-occurrence entre:
- ✅ Backend platform state (renombrar): e.g., `Contract.status`, `Department.status`, `Module.is_active`, generic config flags
- ❌ Domain Spanish (preservar): `estado_empleado`, `estado_civil`, `vigencia_estado_seguro`, `estado_documento`, `estado_familiar`, `estado_ubicacion`, `estado_datos`, `estado_solicitud`
- ❌ Local UI state / labels / design tokens (no es API field): `useLoading.estado`, `LegajoPage.estado` (label key), `design-tokens.activo` (color name)

Estimación L3.10.4d: ~30-50 actual API field renames. Requiere lectura por archivo, no replace_all blindo.

**Después L3.10.4e** — frontend PK type change (`<entity>_id: number` → `id: string` UUID). ~57 declarations + ~252 usage refs. Highest semantic risk: function signatures, comparisons, React keys, URL building.

**Después L3.10.4f** — frontend file renames (`contratosService.ts → contractsService.ts`, etc.) + 82 imports en consumers + `generated/api/services/` regenerado.

**Después L3.11** — cleanup: remover URLs legacy `/api/v1/rrhh/` y `/api/v1/vacaciones/` en backend + carpeta vacía `app_rrhh/`.

---

## Notas para el ejecutor

- **Frontend-only refactor.** Backend no se toca; pytest baseline 161/8/3 debe permanecer idéntico post-merge.
- **Preserve domain Spanish fields.** Si un Edit accidentalmente reemplaza `fecha_inicio_suspension_renta` o `fecha_ingreso` o similar — STOP y revertir. La regla: solo renombrar las 5 specific patterns (`fecha_creacion`, `fecha_actualizacion`, `fecha_modificacion`, `creado_por`, `modificado_por`).
- **`replace_all: true` es seguro** porque cada audit field es un substring único (no hay patrones colisionantes esperados). Si Edit reporta "string not found", verificar con grep primero.
- **`fecha_modificacion` y `fecha_actualizacion` ambos → `updated_at`.** Esto es correcto: backend tiene ambos `db_column` apuntando a la misma propiedad Python `updated_at` en distintos modelos.
- **`generated/api/services/*.ts` NO se toca.** Esos files son output de OpenAPI codegen sobre el schema actualizado. Si los regeneramos en L3.10.4f los nuevos audit fields aparecerán automáticamente.
- **Riesgo bajo runtime** — si el build pasa y vitest preserva baseline, el refactor es seguro. Cualquier consumer que use el field viejo daría error al runtime, pero el TypeScript type checker lo detecta en build (asumiendo tipos estrictos en las interfaces afectadas).
- **rrhhNormalizers.ts contenido se modifica, filename NO.** El rename del filename es L3.10.4f.
