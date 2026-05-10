# B.2 Polish Identity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Polish the identity bounded context (users, roles, RBAC) — fix legacy bugs (`tiempo_desde_ultimo_login`, `UsuarioManager.activos`/`por_rol`), wire explicit tenant filtering into `User.roles_activos()`/`permisos_activos()` (defense-in-depth alongside RLS), migrate identity ViewSets out of the giant `rrhh/views.py` into their bounded-context home `api/v1/identity/views.py`, document the `Permission.modulo` and `UserRole vs TenantMembership.role` design decisions, and clean frontend identity lint warnings.

**Architecture:** Backend changes live in `apps/api/apps/identity/` (models, managers, services). The big mechanical refactor moves 5 ViewSets (Usuario, Rol, Permiso, Modulos, RolPermisos) from `apps/api/api/v1/rrhh/views.py` to a new `apps/api/api/v1/identity/views.py`, with `apps/api/api/v1/identity/urls.py` switched to import from the new location. Two design decisions are recorded as ADRs in `.planning/audit-B/ADRS.md` (no code changes for those).

**Tech Stack:** Django 5.2 + DRF + apps.tenancy.context (already in place). Frontend: React + Vite + TypeScript. Pytest, vitest, ESLint.

**Branch:** `vyntia/B2-polish-identity`
**Commit prefixes:** `fix(B2):` for bug fixes, `chore(B2):` for moves/cleanup, `docs(B2):` for ADR additions, `feat(B2):` only if new infrastructure (none expected).
**Backlog items in scope:** #44, #45, #46, #47, #48, #49, #87 (7 items).
**Out of scope:** Items #40-#42 (employees-app filter bugs that BACKLOG mis-tagged as B.2 — they are EmpleadoFilter bugs and belong in B.4 polish-employees per the master roadmap section).

**Test baselines to preserve (post-B.1 merge SHA `dff98e67`):**
- pytest: 290 passed / 3 failed / 17 skipped
- vitest: 7 files / 32 tests
- ESLint: 439 problems (404 errors / 35 warnings)
- tsc: 1 pre-existing error (`generated/api/models/BlankEnum.ts:6:5`)
- `npm run build`: clean
- `manage.py check --settings=vyntia.settings.development`: clean

After B.2: pytest **290+ passed / 3 failed / 17 skipped** (new tests for fixes; same 3 pre-existing failures), ESLint **~424** (drops by ~15 identity feature warnings), tsc preserved, build preserved.

---

## File Structure

### New files

| Path | Purpose |
|---|---|
| `apps/api/api/v1/identity/views.py` | Home for the 5 identity ViewSets (Usuario, Rol, Permiso, Modulos, RolPermisos) — migrated from `api/v1/rrhh/views.py` |
| `apps/api/apps/identity/tests/__init__.py` | New tests package for in-app identity tests (currently identity tests live at `apps/api/tests/` root) |
| `apps/api/apps/identity/tests/test_user_methods.py` | Unit tests for fixed `tiempo_desde_ultimo_login`, `UsuarioManager.activos`, `por_rol` |
| `apps/api/apps/identity/tests/test_tenant_aware_roles.py` | Unit tests covering tenant filtering in `roles_activos()` / `permisos_activos()` |

### Modified files

| Path | Reason |
|---|---|
| `apps/api/apps/identity/models/user.py` | Fix `tiempo_desde_ultimo_login` fall-through (#44); add tenant filter to `roles_activos()` and `permisos_activos()` (#48) |
| `apps/api/apps/identity/managers.py` | Fix `UsuarioManager.activos()` to use `is_active=True` instead of non-existent `estado` (#45). Fix or remove `por_rol()` (#45 dead code). |
| `apps/api/api/v1/auth/serializers.py` | Remove dead `_get_user_modules` method that assumes `Permission.modulo` is FK (it's CharField — #46 cleanup) |
| `apps/api/api/v1/identity/urls.py` | Switch ViewSet imports from `api.v1.rrhh.views` to `api.v1.identity.views` (#47) |
| `apps/api/api/v1/rrhh/views.py` | Remove the 5 migrated ViewSets after they land in identity/views.py (#47) |
| `apps/api/api/v1/rrhh/urls.py` | Remove identity ViewSet imports/registrations now duplicated in identity/urls.py (#47) |
| `.planning/audit-B/ADRS.md` | Add ADR-B.10 (Permission.modulo CharField — kept by design, #46) and ADR-B.11 (UserRole vs TenantMembership.role — #49) |
| `apps/web/src/features/identity/**/*.{ts,tsx}` | Lint cleanup for ~15 warnings (#87) |

### File responsibility boundaries

- **User model methods** are the right place for tenant filtering — both `PermissionService` and `MenuService` delegate to them, so a single fix covers both. Don't duplicate the filter in services.
- **ViewSets stay in their bounded context** post-migration. `api/v1/rrhh/` becomes legacy/contracts-only. Future B-phases will continue draining it.
- **ADRs document decisions, not code** — Tasks 5 and 6 produce no executable changes, only `.planning/audit-B/ADRS.md` updates.
- **Frontend lint changes are mechanical** — fix the actual unused-variable / `any` / missing-deps issues that ESLint flags; don't introduce new abstractions.

---

## Task 1: Branch + capture baselines

**Files:** none modified — setup only.

- [ ] **Step 1: Confirm working tree clean and on master**

```bash
cd D:/VYNTIA
git status
git log --oneline -1
```

Expected: clean tree; HEAD is `dff98e67` (B.1 merge) or whatever later commit master is at.

- [ ] **Step 2: Branch off master**

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/B2-polish-identity
```

- [ ] **Step 3: Capture pytest baseline**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Record the count. Expected: `290 passed, 3 failed, 17 skipped`.

- [ ] **Step 4: Capture frontend baselines**

```bash
cd D:/VYNTIA/apps/web
npx eslint . 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
```

Record. Expected: `439 problems (404 errors, 35 warnings)`, 1 tsc error in BlankEnum.ts.

- [ ] **Step 5: No commit yet** — Task 1 is just setup.

---

## Task 2: Fix `User.tiempo_desde_ultimo_login` fall-through (#44)

**Files:**
- Modify: `apps/api/apps/identity/models/user.py:230-242`
- Create: `apps/api/apps/identity/tests/__init__.py` (empty)
- Create: `apps/api/apps/identity/tests/test_user_methods.py`

The current method:

```python
@property
def tiempo_desde_ultimo_login(self):
    """Calcula el tiempo transcurrido desde el último login."""
    if self.last_login:
        delta = timezone.now() - self.last_login
        if delta.days > 0:
            return f"{delta.days} día{'s' if delta.days != 1 else ''}"
        elif delta.seconds > 3600:
            horas = delta.seconds // 3600
            return f"{horas} hora{'s' if horas != 1 else ''}"
        elif delta.seconds > 60:
            minutos = delta.seconds // 60
            # ❌ NO RETURN — falls through to None
```

The `elif delta.seconds > 60` branch computes `minutos` but never returns. The function falls through and returns None implicitly. This is the inventory bug (line 232).

- [ ] **Step 1: Create the test file FIRST (TDD)**

Verify `apps/api/apps/identity/tests/` exists or create it:

```bash
cd D:/VYNTIA/apps/api
ls apps/identity/tests/ 2>/dev/null || mkdir -p apps/identity/tests
```

Create `apps/api/apps/identity/tests/__init__.py` (empty file).

Create `apps/api/apps/identity/tests/test_user_methods.py`:

```python
"""Tests for User model bug fixes (B.2 #44, #45)."""

from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestTiempoDesdeUltimoLogin:
    def _user(self):
        from apps.identity.models import User
        u = User(username="t", email="t@t.local")
        u.set_password("x")
        return u

    def test_returns_days_when_more_than_a_day_old(self):
        u = self._user()
        u.last_login = timezone.now() - timedelta(days=3)
        assert u.tiempo_desde_ultimo_login.startswith("3 día")

    def test_returns_hours_when_between_1_hour_and_1_day(self):
        u = self._user()
        u.last_login = timezone.now() - timedelta(hours=2, minutes=10)
        assert u.tiempo_desde_ultimo_login.startswith("2 hora")

    def test_returns_minutes_when_between_1_minute_and_1_hour(self):
        """Bug #44: elif delta.seconds > 60 branch was missing a return — now fixed."""
        u = self._user()
        u.last_login = timezone.now() - timedelta(minutes=15)
        result = u.tiempo_desde_ultimo_login
        assert result is not None  # was None pre-fix
        assert result.startswith("15 minuto")

    def test_returns_seconds_when_less_than_a_minute(self):
        """Edge case: brand-new login — returns either 'segundos' or '< 1 minuto'."""
        u = self._user()
        u.last_login = timezone.now() - timedelta(seconds=30)
        result = u.tiempo_desde_ultimo_login
        # Acceptable: 'segundos' string OR 'menos de 1 minuto' OR similar — just not None
        assert result is not None
        assert isinstance(result, str)

    def test_returns_none_when_no_last_login(self):
        u = self._user()
        u.last_login = None
        assert u.tiempo_desde_ultimo_login is None
```

- [ ] **Step 2: Run failing test**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/identity/tests/test_user_methods.py::TestTiempoDesdeUltimoLogin -v
```

Expected: `test_returns_minutes_when_between_1_minute_and_1_hour` FAILS with `AssertionError: result is None`. `test_returns_seconds_when_less_than_a_minute` likely also FAILS.

- [ ] **Step 3: Fix the property**

Edit `apps/api/apps/identity/models/user.py` lines 230-242. Replace the `tiempo_desde_ultimo_login` property body with:

```python
    @property
    def tiempo_desde_ultimo_login(self):
        """Calcula el tiempo transcurrido desde el último login."""
        if not self.last_login:
            return None
        delta = timezone.now() - self.last_login
        if delta.days > 0:
            return f"{delta.days} día{'s' if delta.days != 1 else ''}"
        if delta.seconds > 3600:
            horas = delta.seconds // 3600
            return f"{horas} hora{'s' if horas != 1 else ''}"
        if delta.seconds > 60:
            minutos = delta.seconds // 60
            return f"{minutos} minuto{'s' if minutos != 1 else ''}"
        return "menos de 1 minuto"
```

Note: also flatten `elif` to `if` since each branch returns. The semantic is equivalent but more readable.

- [ ] **Step 4: Run tests — must PASS**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/identity/tests/test_user_methods.py::TestTiempoDesdeUltimoLogin -v
```

Expected: 5 PASS.

- [ ] **Step 5: Run full backend suite**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: **295 passed / 3 failed / 17 skipped** (5 new passes from this task's tests).

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/identity/models/user.py apps/api/apps/identity/tests/
git commit -m "$(cat <<'EOF'
fix(B2): User.tiempo_desde_ultimo_login returns minute string instead of None (#44)

The "elif delta.seconds > 60" branch computed minutos but never returned,
falling through to an implicit None. Flattened the elif chain to ifs and
added the missing return; also added a "menos de 1 minuto" fallback for
the sub-minute case so the property never silently returns None when
last_login is set.

Adds new in-app test package apps/identity/tests/ (was missing — all
identity tests previously lived at apps/api/tests/ root).

Backlog item: #44.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Fix `UsuarioManager.activos()` and `por_rol()` (#45)

**Files:**
- Modify: `apps/api/apps/identity/managers.py:46-67`
- Append: `apps/api/apps/identity/tests/test_user_methods.py`

The current `activos()` filters by `estado=True` — `User` has no `estado` field; the actual field is `estado_usuario` (CharField with values like `'activo'`, `'inactivo'`, `'bloqueado'`) plus Django's `is_active` boolean. The current code raises `FieldError` if called.

`por_rol()` filters by `rol__nombre__icontains` — the User model has no direct `rol` reverse accessor (the relation is via `UserRole` pivot model). This is dead code per inventory line 135 (P2).

- [ ] **Step 1: Add failing tests**

Append to `apps/api/apps/identity/tests/test_user_methods.py`:

```python
@pytest.mark.django_db
class TestUsuarioManagerActivos:
    def test_activos_returns_users_with_is_active_true_and_estado_activo(self):
        from apps.identity.models import User

        u_active = User(username="active", email="a@a.local", is_active=True, estado_usuario="activo")
        u_active.set_password("x")
        u_active.save()

        u_blocked = User(username="blocked", email="b@b.local", is_active=True, estado_usuario="bloqueado")
        u_blocked.set_password("x")
        u_blocked.save()

        u_disabled = User(username="off", email="o@o.local", is_active=False, estado_usuario="inactivo")
        u_disabled.set_password("x")
        u_disabled.save()

        active_set = set(User.objects.activos().values_list("username", flat=True))
        assert "active" in active_set
        assert "blocked" not in active_set
        assert "off" not in active_set

    def test_inactivos_returns_users_not_active(self):
        from apps.identity.models import User

        u_active = User(username="ux", email="ux@ux.local", is_active=True, estado_usuario="activo")
        u_active.set_password("x")
        u_active.save()

        u_off = User(username="ox", email="ox@ox.local", is_active=False, estado_usuario="inactivo")
        u_off.set_password("x")
        u_off.save()

        inactive_set = set(User.objects.inactivos().values_list("username", flat=True))
        assert "ux" not in inactive_set
        assert "ox" in inactive_set


@pytest.mark.django_db
class TestUsuarioManagerPorRol:
    def test_por_rol_returns_users_with_role(self):
        """por_rol must traverse the UserRole pivot, not a non-existent direct rel."""
        from apps.identity.models import User, Role
        from apps.identity.models.rbac import UserRole

        rol = Role.objects.create(nombre_rol="TestRole", estado_rol="activo")

        u_with = User(username="with_role", email="wr@local", is_active=True, estado_usuario="activo")
        u_with.set_password("x")
        u_with.save()
        UserRole.objects.create(usuario=u_with, rol=rol, estado_asignacion="activo")

        u_without = User(username="without_role", email="wo@local", is_active=True, estado_usuario="activo")
        u_without.set_password("x")
        u_without.save()

        usernames = set(User.objects.por_rol("TestRole").values_list("username", flat=True))
        assert "with_role" in usernames
        assert "without_role" not in usernames
```

- [ ] **Step 2: Run tests — must FAIL**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/identity/tests/test_user_methods.py::TestUsuarioManagerActivos apps/identity/tests/test_user_methods.py::TestUsuarioManagerPorRol -v
```

Expected: tests fail. `activos` raises `FieldError` ("Cannot resolve keyword 'estado' into field"); `por_rol` raises FieldError ("Cannot resolve keyword 'rol' into field").

- [ ] **Step 3: Fix the manager**

Edit `apps/api/apps/identity/managers.py`:

```python
    def activos(self):
        """Get active users (Django is_active AND estado_usuario='activo')."""
        return self.filter(is_active=True, estado_usuario="activo")

    def inactivos(self):
        """Get inactive users (is_active=False OR estado_usuario != 'activo')."""
        from django.db.models import Q
        return self.filter(Q(is_active=False) | ~Q(estado_usuario="activo"))

    def con_roles(self):
        """Get users with their roles (prefetch via UserRole pivot)."""
        return self.prefetch_related("usuario_roles__rol")

    def por_rol(self, nombre_rol: str):
        """Filter users that have an active role matching nombre_rol.

        Args:
            nombre_rol: Role name (case-insensitive substring match).

        Returns:
            QuerySet[User]
        """
        return self.filter(
            usuario_roles__rol__nombre_rol__icontains=nombre_rol,
            usuario_roles__estado_asignacion="activo",
        ).distinct()
```

The reverse-accessor name `usuario_roles` is the related_name for `UserRole.usuario` FK (verify by reading `apps/api/apps/identity/models/rbac.py` for the actual related_name). If the actual related_name differs (e.g., `userrole_set` if not specified), use that. Adjust `con_roles()` analogously.

- [ ] **Step 4: Verify the actual related_name**

```bash
cd D:/VYNTIA/apps/api
grep -n "related_name.*usuario\|class UserRole" apps/identity/models/rbac.py
```

If `related_name="usuario_roles"` exists on the `usuario` FK on UserRole, the code above is correct. If not, replace `usuario_roles` with the actual reverse accessor (Django default would be `userrole_set` if no related_name set).

- [ ] **Step 5: Run tests — must PASS**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/identity/tests/test_user_methods.py -v
```

Expected: all tests PASS.

- [ ] **Step 6: Run full backend suite**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: **298 passed / 3 failed / 17 skipped** (3 new passes).

- [ ] **Step 7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/identity/managers.py apps/api/apps/identity/tests/test_user_methods.py
git commit -m "$(cat <<'EOF'
fix(B2): UsuarioManager.activos and por_rol use real fields (#45)

User has no `estado` field (the legacy `activos()` filter); the real
fields are `is_active` (Django) and `estado_usuario` (CharField with
'activo'/'inactivo'/'bloqueado'/'suspendido'). Same root cause for
`por_rol`: User has no direct `rol` reverse accessor — the relation
goes through the UserRole pivot.

- activos(): filter is_active=True AND estado_usuario='activo'
- inactivos(): is_active=False OR estado_usuario != 'activo'
- con_roles(): prefetch usuario_roles__rol via UserRole pivot
- por_rol(): traverse UserRole, filter on rol__nombre_rol icontains
  AND estado_asignacion='activo'; .distinct() to dedupe multi-role users

Backlog item: #45.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Document `Permission.modulo` decision + remove dead `_get_user_modules` (#46)

**Files:**
- Modify: `apps/api/api/v1/auth/serializers.py` — remove `_get_user_modules` method (~lines 240-287)
- Modify: `.planning/audit-B/ADRS.md` — append ADR-B.10

`Permission.modulo` is a `CharField` (legacy schema) — it does NOT FK to the `Module` model. The dead method `CustomTokenObtainPairSerializer._get_user_modules` tries to access `permiso.modulo.pk` and `permiso.modulo.nombre_modulo` (assuming FK semantics) and would `AttributeError` if called. It's not currently called anywhere (per inventory line 137).

ADR-B.10 records the decision: keep CharField for B (no migration), revisit in a future cleanup if real consumers need FK semantics.

- [ ] **Step 1: Verify `_get_user_modules` is unused**

```bash
cd D:/VYNTIA/apps/api
grep -rn "_get_user_modules" --include="*.py"
```

Expected: only the definition site at `api/v1/auth/serializers.py:240`. If there are other callers, STOP and report — the deletion is unsafe.

- [ ] **Step 2: Read the method to confirm scope**

```bash
cd D:/VYNTIA/apps/api
grep -n "_get_user_modules\|return list(modulos_permisos.values())" api/v1/auth/serializers.py | head
```

Read with offset around line 240 to see the method body and end. Note exact line range.

- [ ] **Step 3: Remove the method**

Use Edit on `apps/api/api/v1/auth/serializers.py` to remove the entire `_get_user_modules` method body. Use a unique `old_string` that captures the exact lines (method signature + docstring + body + final `return list(modulos_permisos.values())`).

- [ ] **Step 4: Add ADR-B.10 to ADRS.md**

Use Edit (or Write if appending) on `.planning/audit-B/ADRS.md`. Append the following ADR at the end of the file:

```markdown


## ADR-B.10: `Permission.modulo` stays as CharField (deferred FK migration)

**Status:** Accepted (2026-05-09)

**Context:** `apps.identity.Permission` carries a `modulo` field that is a `CharField` (string ID), not a `ForeignKey` to the `Module` model. The same database has a real `Module` model (`apps.identity.Module`) used by the menu/sidebar system. The audit (Task 7 chapter, INVENTORY.md line 139) flagged this as inconsistent: permissions reference modules by string ID instead of FK, and the dead method `CustomTokenObtainPairSerializer._get_user_modules` had assumed FK semantics, accessing `permiso.modulo.pk` and `permiso.modulo.nombre_modulo` — which would raise `AttributeError` if it were ever called.

Migrating to FK requires: (a) a data-migration that maps every existing `modulo` string to the corresponding `Module.pk`, including dropped/renamed module IDs in legacy data; (b) a schema migration; (c) updating every `Permission.objects.filter(modulo=...)` consumer (15+ sites across `permission_service`, `menu_service`, ViewSets); (d) frontend type updates. Total estimated effort: ~3-5 days, with potential data-cleanup risk for legacy strings that don't match a real Module.

**Decision:** Keep `Permission.modulo` as `CharField` for the duration of sub-project B. Remove the dead `_get_user_modules` method (it was unused and would have errored on the FK assumption). Document this decision so future contributors don't re-introduce the same dead pattern.

The migration to FK can be revisited in a post-B sub-project if a real consumer requires FK semantics (e.g., a Modules admin UI that wants to enforce referential integrity on Permission rows).

**Consequences:**
- Positive: Avoids 3-5 days of migration + risk on legacy data we can't fully validate.
- Positive: Removes dead code that would have raised AttributeError if reached.
- Positive: Status quo for all 15+ consumers — no consumer-side churn.
- Negative: Permission rows can reference module IDs that don't exist in `Module` table — no referential integrity at the DB level.
- Negative: Frontend cannot eagerly join Permission → Module without a service-layer lookup.
- Neutral: When/if a Modules admin UI lands in sub-project T or later, this ADR will be superseded.

**Alternatives considered:**
- Migrate to FK in B.2: rejected — the data risk and consumer surface inflate B.2 beyond polish scope.
- Migrate to FK in a later B-phase: deferred — no current B-phase consumer needs FK semantics.
- Rewrite `_get_user_modules` to handle CharField: rejected — the method is dead code; keeping it as polished dead code adds maintenance debt without benefit.

**Reference:** INVENTORY.md (Task 7 identity chapter, line 139); B.2 plan Task 4.
```

- [ ] **Step 5: System check + pytest regression**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: 0 issues; **298 passed / 3 failed / 17 skipped** (no change — this task removes dead code and adds docs).

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/auth/serializers.py .planning/audit-B/ADRS.md
git commit -m "$(cat <<'EOF'
docs(B2): ADR-B.10 — Permission.modulo stays CharField; remove dead consumer (#46)

The dead method CustomTokenObtainPairSerializer._get_user_modules
assumed Permission.modulo was an FK and would have AttributeError'd
if called. Removed (no live caller) and recorded the design decision
(keep CharField for B; FK migration deferred to a post-B cleanup if
ever needed) as ADR-B.10.

Backlog item: #46.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Add tenant filter to `User.roles_activos()` and `permisos_activos()` (#48)

**Files:**
- Modify: `apps/api/apps/identity/models/user.py:409-454` (`roles_activos`, `permisos_activos`)
- Create: `apps/api/apps/identity/tests/test_tenant_aware_roles.py`

Currently both methods filter by `estado_asignacion="activo"` and role/permission status, but NOT by tenant. They rely entirely on Postgres RLS for tenant isolation. Inventory line 159 flagged this as a defense-in-depth gap: if RLS is bypassed (admin connection, dev) or the tenant context is unset, queries leak across tenants.

The fix: read the active tenant via `apps.tenancy.context.get_current_tenant()` and add `tenant=tenant` to the UserRole/Role/Permission filter chain when tenant is set. Permissive when tenant is None (legacy paths, admin commands).

⚠️ Verify which models have a `tenant` FK before applying. Per the inventory, `UserRole`, `Role`, and `Permission` all have nullable tenant FKs from C-phase migrations. Verify before editing.

- [ ] **Step 1: Verify tenant fields exist on UserRole / Role / Permission**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py shell --settings=vyntia.settings.development -c "
from apps.identity.models import Role, Permission
from apps.identity.models.rbac import UserRole
for m in [UserRole, Role, Permission]:
    has = any(f.name == 'tenant' for f in m._meta.get_fields())
    print(m.__name__, 'tenant?', has)
"
```

If any output line says `tenant? False`, that model is NOT tenant-scoped — DO NOT add a tenant filter for that model. Adapt the fix accordingly.

If all three say True, proceed with the full fix.

- [ ] **Step 2: Write failing tests**

Create `apps/api/apps/identity/tests/test_tenant_aware_roles.py`:

```python
"""Tests for tenant-scoped roles_activos/permisos_activos (B.2 #48)."""

import pytest

from apps.tenancy.context import tenant_context


@pytest.mark.django_db
class TestRolesActivosTenantFilter:
    def _setup_two_tenants_with_roles(self):
        from apps.tenancy.models import Tenant
        from apps.identity.models import User, Role
        from apps.identity.models.rbac import UserRole

        tenant_a = Tenant.objects.create(name="Tenant A", slug="tenant-a")
        tenant_b = Tenant.objects.create(name="Tenant B", slug="tenant-b")

        user = User(username="multi", email="m@m.local", is_active=True, estado_usuario="activo")
        user.set_password("x")
        user.save()

        role_a = Role.objects.create(nombre_rol="OnlyA", estado_rol="activo", tenant=tenant_a)
        role_b = Role.objects.create(nombre_rol="OnlyB", estado_rol="activo", tenant=tenant_b)

        UserRole.objects.create(usuario=user, rol=role_a, estado_asignacion="activo", tenant=tenant_a)
        UserRole.objects.create(usuario=user, rol=role_b, estado_asignacion="activo", tenant=tenant_b)

        return user, tenant_a, tenant_b, role_a, role_b

    def test_roles_activos_filters_by_current_tenant(self):
        user, tenant_a, tenant_b, role_a, role_b = self._setup_two_tenants_with_roles()

        with tenant_context(tenant_a):
            roles_a = list(user.roles_activos().values_list("nombre_rol", flat=True))

        with tenant_context(tenant_b):
            roles_b = list(user.roles_activos().values_list("nombre_rol", flat=True))

        assert "OnlyA" in roles_a and "OnlyB" not in roles_a
        assert "OnlyB" in roles_b and "OnlyA" not in roles_b

    def test_roles_activos_returns_all_when_no_tenant_context(self):
        """Permissive: when no tenant context active, no tenant filter is applied."""
        user, _, _, _, _ = self._setup_two_tenants_with_roles()

        # No tenant_context() wrapper — should not filter by tenant
        all_roles = set(user.roles_activos().values_list("nombre_rol", flat=True))

        assert "OnlyA" in all_roles
        assert "OnlyB" in all_roles


@pytest.mark.django_db
class TestPermisosActivosTenantFilter:
    def test_permisos_activos_filters_by_current_tenant(self):
        from apps.tenancy.models import Tenant
        from apps.identity.models import User, Role, Permission
        from apps.identity.models.rbac import UserRole, RolePermission

        tenant_a = Tenant.objects.create(name="Tenant A2", slug="ta2")
        tenant_b = Tenant.objects.create(name="Tenant B2", slug="tb2")

        user = User(username="pmulti", email="pm@m.local", is_active=True, estado_usuario="activo")
        user.set_password("x")
        user.save()

        role_a = Role.objects.create(nombre_rol="PA", estado_rol="activo", tenant=tenant_a)
        role_b = Role.objects.create(nombre_rol="PB", estado_rol="activo", tenant=tenant_b)

        perm_a = Permission.objects.create(nombre_permiso="perm_a", modulo="x", estado_permiso="activo", tenant=tenant_a)
        perm_b = Permission.objects.create(nombre_permiso="perm_b", modulo="x", estado_permiso="activo", tenant=tenant_b)

        RolePermission.objects.create(rol=role_a, permiso=perm_a, tenant=tenant_a)
        RolePermission.objects.create(rol=role_b, permiso=perm_b, tenant=tenant_b)

        UserRole.objects.create(usuario=user, rol=role_a, estado_asignacion="activo", tenant=tenant_a)
        UserRole.objects.create(usuario=user, rol=role_b, estado_asignacion="activo", tenant=tenant_b)

        with tenant_context(tenant_a):
            perms_a = set(user.permisos_activos().values_list("nombre_permiso", flat=True))

        with tenant_context(tenant_b):
            perms_b = set(user.permisos_activos().values_list("nombre_permiso", flat=True))

        assert perms_a == {"perm_a"}
        assert perms_b == {"perm_b"}
```

⚠️ Adapt model field names to actual schema. If `Role.objects.create()` requires more fields (e.g., `descripcion_rol`), add minimal placeholders. If `RolePermission` requires `tenant` and the model also requires the FK to be in a specific tenant context (e.g., RLS-enforced even at create time), this test setup may need a wrapping `tenant_context` block — adapt as needed.

- [ ] **Step 3: Run failing tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/identity/tests/test_tenant_aware_roles.py -v
```

Expected: tests in `TestRolesActivosTenantFilter` and `TestPermisosActivosTenantFilter` FAIL — both return cross-tenant results.

If a test fails on fixture setup (e.g., RLS prevents creating a Role in tenant_b without tenant_b context), wrap each create in a `tenant_context(...)` block to write through.

- [ ] **Step 4: Add tenant filter to `User.roles_activos()`**

Edit `apps/api/apps/identity/models/user.py`. Replace the existing `roles_activos` method:

```python
    def roles_activos(self):
        """Obtiene los roles activos del usuario, filtrados por tenant context si está activo."""
        from .roles import Role
        from .rbac import UserRole
        from apps.tenancy.context import get_current_tenant

        tenant = get_current_tenant()

        # Filtrar UserRole por usuario + estado activo + tenant (si hay context)
        ur_qs = UserRole.objects.filter(usuario=self, estado_asignacion="activo")
        if tenant is not None:
            ur_qs = ur_qs.filter(tenant=tenant)
        usuario_roles = ur_qs.select_related("rol")

        roles_ids = []
        for usuario_rol in usuario_roles:
            if (
                usuario_rol.fecha_expiracion is None
                or usuario_rol.fecha_expiracion > timezone.now()
            ) and usuario_rol.rol.estado_rol == "activo":
                roles_ids.append(usuario_rol.rol.pk)

        roles_qs = Role.objects.filter(pk__in=roles_ids, estado_rol="activo")
        if tenant is not None:
            roles_qs = roles_qs.filter(tenant=tenant)
        return roles_qs
```

- [ ] **Step 5: Add tenant filter to `User.permisos_activos()`**

Edit the same file. Replace `permisos_activos`:

```python
    def permisos_activos(self):
        """Obtiene los permisos activos del usuario via roles, filtrados por tenant context si activo."""
        from .roles import Permission
        from .rbac import RolePermission
        from apps.tenancy.context import get_current_tenant

        tenant = get_current_tenant()

        try:
            roles = self.roles_activos()  # ya filtrado por tenant via Step 4
            if not roles.exists():
                return Permission.objects.none()

            if roles.filter(nombre_rol="Super Administrador").exists():
                return "*"

            rp_qs = RolePermission.objects.filter(rol__in=roles)
            if tenant is not None:
                rp_qs = rp_qs.filter(tenant=tenant)

            permiso_ids = rp_qs.values_list("permiso_id", flat=True).distinct()

            perm_qs = Permission.objects.filter(pk__in=permiso_ids, estado_permiso="activo")
            if tenant is not None:
                perm_qs = perm_qs.filter(tenant=tenant)
            return perm_qs
        except Exception:
            return Permission.objects.none()
```

- [ ] **Step 6: Run tests — must PASS**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/identity/tests/test_tenant_aware_roles.py -v
```

Expected: all 3 tests PASS.

- [ ] **Step 7: Run full backend suite**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: **301 passed / 3 failed / 17 skipped** (3 new passes).

⚠️ If existing tests break (e.g., a test that expected cross-tenant role visibility now fails), investigate carefully. The fix is permissive when tenant is None — most tests that don't activate a tenant context should be unaffected. If a test breaks because it WAS in a tenant context but expected cross-tenant data, that test was depending on a bug; flag it but don't change the test as part of this task — instead, soften the production fix or report DONE_WITH_CONCERNS.

- [ ] **Step 8: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/identity/models/user.py apps/api/apps/identity/tests/test_tenant_aware_roles.py
git commit -m "$(cat <<'EOF'
fix(B2): User.roles_activos and permisos_activos filter by tenant context (#48)

PermissionService and MenuService both delegate role/permission resolution
to these User methods. Previously they relied 100% on RLS for tenant
isolation; if RLS was bypassed (admin connection, dev superuser) or
tenant context was unset, queries leaked cross-tenant.

Now both methods read the active tenant via apps.tenancy.context.get_current_tenant()
and apply explicit tenant=tenant filters on UserRole, Role, RolePermission,
and Permission queries when tenant is present. Permissive when tenant is
None (admin paths, reserved subdomains) — preserves legacy behavior.

Defense-in-depth alongside RLS: now both the application layer and the
database enforce tenant isolation for RBAC checks.

Backlog item: #48.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: ADR-B.11 — UserRole vs TenantMembership.role decision (#49)

**Files:**
- Modify: `.planning/audit-B/ADRS.md` — append ADR-B.11

This is documentation only. Per inventory line 167, two role-bearing models coexist:
- `apps.tenancy.TenantMembership.role` — flat string (`"admin"`, `"member"`, `"owner"`) — gates workspace-level access (can this user enter this tenant at all?).
- `apps.identity.UserRole` → `apps.identity.Role` — FK chain with `RolePermission` for granular RBAC inside a tenant.

The decision: KEEP BOTH. They serve different layers. Document the decision so future contributors don't conflate them.

- [ ] **Step 1: Append ADR to ADRS.md**

Use Edit to append at the end of `.planning/audit-B/ADRS.md`:

```markdown


## ADR-B.11: UserRole vs TenantMembership.role coexist (no consolidation)

**Status:** Accepted (2026-05-09)

**Context:** Two role-bearing models exist in VYNTIA, introduced in different sub-projects:

- **`apps.tenancy.TenantMembership.role`** (sub-project C) — flat CharField with values like `"owner"`, `"admin"`, `"member"`. One row per `(user, tenant)` membership. Used at the workspace boundary: "can this user authenticate INTO this tenant at all, and if so, what's their workspace-level tier?"
- **`apps.identity.UserRole` → `apps.identity.Role`** (legacy schema, predates multi-tenancy) — FK chain with `RolePermission` linking each role to atomic Permissions. Used for granular RBAC inside a tenant: "what specific actions can this user perform on which resources?"

The audit (Task 7 chapter, INVENTORY.md line 167) flagged this dualism as deuda técnica. Two paths existed:
1. **Consolidate**: pick one model, migrate everything. Reduces conceptual surface but requires invasive migration that crosses C and identity bounded contexts.
2. **Keep both**: clarify roles in a single ADR so contributors understand which model to extend in which scenario.

**Decision:** Keep both models. They occupy distinct layers:

- `TenantMembership.role` is the **workspace gate**. Set at invitation/activation time. Read by middleware (`TenantAuthMiddleware`) to confirm the JWT-bearing user has a live membership for the requested subdomain. Granularity intentionally coarse (3-4 string tiers).
- `UserRole`/`Role`/`Permission`/`RolePermission` is the **RBAC engine**. Operating inside a tenant context, it powers per-action permission checks (e.g., "can this user approve a contract amendment?"). Granularity arbitrarily deep.

Sub-projects T (Workflow engine) and any future RBAC-extensions modify the identity-side chain. Sub-projects related to multi-tenant onboarding/billing modify TenantMembership.

**Consequences:**
- Positive: Workspace-tier checks and action-level permission checks are clearly separated — no risk of one accidentally bypassing the other.
- Positive: Migration cost avoided (consolidation would touch C.4, identity, and every middleware/permission consumer).
- Positive: TenantMembership stays small and fast (single row per membership); RBAC complexity stays in identity where it can grow without bloating the membership table.
- Negative: Two role concepts to document for new contributors. Mitigated by this ADR.
- Negative: A user could in theory have a high TenantMembership tier but no UserRole assignments inside the tenant — UI must surface that mismatch (e.g., admin tier without RBAC permissions sees an "incomplete onboarding" prompt).
- Neutral: When the OnboardingProcess auto-creates a User, both a TenantMembership AND a default UserRole assignment must be created — check covered by B.5b (onboarding polish, item #15 already partially addressed in B.1).

**Source-of-truth rule:**

| Question | Source |
|---|---|
| Can user X enter workspace Y? | `TenantMembership(user=X, tenant=Y, status='active')` exists |
| What tier is user X in workspace Y? | `TenantMembership.role` (`'owner' \| 'admin' \| 'member'`) |
| Can user X perform action Z in workspace Y? | `PermissionService.has_any_permission(X, [Z])`, which traverses UserRole → Role → RolePermission → Permission |

**Alternatives considered:**
- Merge into one model with both flat and granular fields: rejected — the table grows unboundedly with RolePermission cardinality, and the membership-gate use case wants O(1) lookups.
- Drop `UserRole`/`Role` and rely on `TenantMembership.role` strings + per-action mapping: rejected — would force every permission check into a hard-coded role→action map, eliminating the data-driven RBAC that lets RRHH admins create custom roles.
- Drop `TenantMembership.role` and infer membership tier from RBAC permissions: rejected — middleware tier checks should not require a permission service round-trip.

**Reference:** INVENTORY.md (Task 7 identity chapter, line 167); B.2 plan Task 6.
```

- [ ] **Step 2: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/ADRS.md
git commit -m "$(cat <<'EOF'
docs(B2): ADR-B.11 — UserRole vs TenantMembership.role coexist (#49)

Records the decision to keep both role-bearing models. They serve
distinct layers:
- TenantMembership.role gates workspace entry (flat string, coarse tiers)
- UserRole/Role/Permission powers granular per-action RBAC inside a tenant

Includes a source-of-truth rule table mapping common questions to the
canonical answer. Resolves the dualism flagged in INVENTORY.md L167.

Backlog item: #49.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Migrate identity ViewSets to `api/v1/identity/views.py` (#47)

**Files:**
- Create: `apps/api/api/v1/identity/views.py`
- Modify: `apps/api/api/v1/identity/urls.py` — switch ViewSet imports to local `views`
- Modify: `apps/api/api/v1/rrhh/views.py` — remove the 5 migrated ViewSets
- Modify: `apps/api/api/v1/rrhh/urls.py` — remove identity ViewSet registrations if duplicated

5 ViewSets to migrate (from `api/v1/identity/urls.py` imports):
- `UsuarioViewSet`
- `RolViewSet`
- `PermisoViewSet`
- `ModulosViewSet`
- `RolPermisosViewSet`

`UsuarioRolesViewSet` already lives in its own file (`api/v1/rrhh/usuario_roles_views.py`); it can stay or move — moving it is cleaner. Recommended: **move it as well**.

- [ ] **Step 1: Locate exact line ranges of each ViewSet in `rrhh/views.py`**

```bash
cd D:/VYNTIA/apps/api
grep -n "^class \(UsuarioViewSet\|RolViewSet\|PermisoViewSet\|ModulosViewSet\|RolPermisosViewSet\|UsuarioRolesViewSet\)" api/v1/rrhh/views.py api/v1/rrhh/usuario_roles_views.py
```

Note exact line numbers. Each class spans from its declaration to the next class declaration (or EOF).

- [ ] **Step 2: Identify imports each ViewSet needs**

Read the top of `api/v1/rrhh/views.py` (lines 1-100) to capture the imports. The 5 identity ViewSets need:
- `from rest_framework import viewsets, filters, status`
- `from rest_framework.decorators import action`
- `from rest_framework.response import Response`
- `from rest_framework.permissions import IsAuthenticated`
- `from django_filters.rest_framework import DjangoFilterBackend`
- `from drf_spectacular.utils import extend_schema, extend_schema_view`
- `from apps.identity.models import User, Role, Permission, Module`
- `from apps.identity.models.rbac import RolePermission`
- `from apps.core.responses import APIResponse`
- `from apps.core.pagination import StandardResultsSetPagination`
- `from apps.core.viewsets import TenantAwareViewSetMixin`
- Plus the matching serializer imports from `api.v1.rrhh.serializers`

Read carefully — exact imports depend on what each class actually uses. The implementer should grep each ViewSet body and verify imports.

- [ ] **Step 3: Create `apps/api/api/v1/identity/views.py`**

Use Read+Write to create the new file. The structure:

```python
"""Views for the identity bounded context (B.2 #47).

Migrated from api/v1/rrhh/views.py to live with the rest of the identity
URL config. Behavior unchanged — only the file location moved. Tests
that referenced these classes by import path will need to update from
`api.v1.rrhh.views` to `api.v1.identity.views`.

ViewSets contained:
- UsuarioViewSet
- RolViewSet
- PermisoViewSet
- ModulosViewSet
- RolPermisosViewSet
- UsuarioRolesViewSet (also migrated; was in api/v1/rrhh/usuario_roles_views.py)
"""

# ... imports (per Step 2)

# ... 6 ViewSet class definitions copied verbatim from rrhh/views.py
```

The body of each ViewSet must be **byte-identical** to what's in `rrhh/views.py` — copy via Read on the source range, paste into Write. No refactoring in this task.

- [ ] **Step 4: Update `apps/api/api/v1/identity/urls.py`**

Edit the urls file — change the imports from:

```python
from api.v1.rrhh.views import (
    ModulosViewSet,
    PermisoViewSet,
    RolPermisosViewSet,
    RolViewSet,
    UsuarioViewSet,
)
from api.v1.rrhh.usuario_roles_views import UsuarioRolesViewSet
```

To:

```python
from api.v1.identity.views import (
    ModulosViewSet,
    PermisoViewSet,
    RolPermisosViewSet,
    RolViewSet,
    UsuarioRolesViewSet,
    UsuarioViewSet,
)
```

- [ ] **Step 5: Search for OTHER consumers of these ViewSets**

Before deleting from `rrhh/views.py`, ensure no other URL config or test imports them from there:

```bash
cd D:/VYNTIA/apps/api
grep -rn "from api.v1.rrhh.views import.*\(UsuarioViewSet\|RolViewSet\|PermisoViewSet\|ModulosViewSet\|RolPermisosViewSet\)" --include="*.py"
grep -rn "from api.v1.rrhh.usuario_roles_views import" --include="*.py"
```

If `api/v1/rrhh/urls.py` still imports any of these, update its imports to point to `api.v1.identity.views` (or remove the route if it's a true duplicate of the identity URL). If a TEST file imports them from rrhh, update the test import path.

- [ ] **Step 6: Remove the 5 ViewSets from `rrhh/views.py`**

Use Edit (not Write — preserve the rest of the file). For each migrated ViewSet, remove its class definition (and any class-level docstring/decorators above it). Keep the file's other ViewSets (Area, Empleado, Datos*, Documentos*, Onboarding, etc.) intact.

Also remove from `rrhh/views.py` any imports that are now unused (if e.g. `from apps.identity.models import Role, Permission` is no longer needed by the remaining code, drop it).

- [ ] **Step 7: Delete or empty `api/v1/rrhh/usuario_roles_views.py`**

If the file contained ONLY `UsuarioRolesViewSet`, delete the file:

```bash
cd D:/VYNTIA
git rm apps/api/api/v1/rrhh/usuario_roles_views.py
```

If it has other code, surgically remove just the `UsuarioRolesViewSet` class.

- [ ] **Step 8: System check**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
```

Expected: 0 issues. If `ImportError` surfaces, a consumer wasn't updated in Step 5 — fix it.

- [ ] **Step 9: Run full pytest**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: **301 passed / 3 failed / 17 skipped** — no change from Task 5 baseline (this task is a pure file move).

If any test breaks because it imported a ViewSet from `api.v1.rrhh.views`, update its import to `api.v1.identity.views`.

- [ ] **Step 10: Smoke test the URLs still resolve**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py show_urls --settings=vyntia.settings.development 2>/dev/null | grep "/api/v1/identity/" | head -10
```

If `show_urls` isn't installed, use `manage.py shell` and `urlpatterns` introspection:

```bash
D:/VYNTIA/.venv/Scripts/python.exe -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development')
django.setup()
from django.urls import get_resolver
for p in get_resolver().url_patterns:
    print(p.pattern)
" 2>&1 | head -20
```

Expected: `/api/v1/identity/` URLs are present. If not, urls.py wiring broke — fix.

- [ ] **Step 11: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/identity/views.py apps/api/api/v1/identity/urls.py apps/api/api/v1/rrhh/views.py apps/api/api/v1/rrhh/usuario_roles_views.py apps/api/api/v1/rrhh/urls.py
# (some files may not need staging if untouched — git add will skip them)
git status
git commit -m "$(cat <<'EOF'
chore(B2): migrate identity ViewSets to api/v1/identity/views.py (#47)

Pure file move: 6 ViewSets (UsuarioViewSet, RolViewSet, PermisoViewSet,
ModulosViewSet, RolPermisosViewSet, UsuarioRolesViewSet) move from
api/v1/rrhh/views.py + usuario_roles_views.py to a new
api/v1/identity/views.py. URL wiring in api/v1/identity/urls.py
switches imports to the new location. No behavioral changes.

This completes the L3 split that was deferred: identity URLs already
lived under /api/v1/identity/ but their ViewSet classes still lived
in the rrhh module. Now both URL and code are properly located in
the identity bounded context.

Backlog item: #47.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Frontend lint cleanup `features/identity` (#87)

**Files:**
- Modify: `apps/web/src/features/identity/**/*.{ts,tsx}` — fix the ~15 ESLint warnings flagged in this directory

Per the INVENTORY analysis, the identity feature directory carries ~15 lint warnings. Typical patterns are: unused imports, unused variables (e.g., destructured but never read), `any` types that could be narrowed to a real interface, missing dependency arrays in `useEffect`/`useMemo`/`useCallback`. Fix mechanically — don't introduce new abstractions.

- [ ] **Step 1: Capture identity lint count BEFORE**

```bash
cd D:/VYNTIA/apps/web
npx eslint src/features/identity/ 2>&1 | tail -3
```

Record: `✖ N problems`. Aim to reduce by ~15.

- [ ] **Step 2: Get the per-file breakdown**

```bash
cd D:/VYNTIA/apps/web
npx eslint src/features/identity/ 2>&1 | grep -E "^/|warning|error" | head -50
```

Note each warning's file:line:rule. Common rules to expect: `@typescript-eslint/no-unused-vars`, `@typescript-eslint/no-explicit-any`, `react-hooks/exhaustive-deps`.

- [ ] **Step 3: Fix each warning, file by file**

For each warning:
- **Unused vars/imports**: prefix with `_` (signals intentional) or delete entirely if truly unused.
- **`any` types**: replace with the actual type if obvious from the surrounding code; otherwise narrow to `unknown` and add a type guard at the use site.
- **Missing deps**: add the variable to the deps array if the effect should re-run when it changes; if it shouldn't, refactor (e.g., move the variable inside the effect or use a ref).

DO NOT change runtime behavior. If a deps fix would change behavior, leave it and add an `// eslint-disable-next-line react-hooks/exhaustive-deps` with a brief reason — but prefer real fixes.

Use Edit for each file. Read each file first (no batch — each fix needs context). Verify the lint count drops between fixes.

⚠️ Watch for:
- Disabling rules wholesale instead of fixing — flag for the orchestrator if more than 3 disables are needed.
- `any` on responses from `apiClient.get<any>(...)` — if the inferred type is non-trivial, leave the `any` and document why; do NOT invent types that don't match the backend contract.

- [ ] **Step 4: Capture identity lint count AFTER**

```bash
cd D:/VYNTIA/apps/web
npx eslint src/features/identity/ 2>&1 | tail -3
```

Expected: drop by ~10-15 warnings (some warnings may be genuine `any` types that are too risky to narrow).

- [ ] **Step 5: Verify no regression — full lint**

```bash
cd D:/VYNTIA/apps/web
npx eslint . 2>&1 | tail -3
```

Expected: total lint count drops by the same delta from 439 (e.g., ~424).

- [ ] **Step 6: Verify build clean + tsc preserved**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
```

Expected: build clean; tsc 1 error (`BlankEnum.ts:6:5`) preserved.

- [ ] **Step 7: Verify vitest still passes**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | tail -10
```

Expected: same passing count as baseline (7 files / 32 tests).

- [ ] **Step 8: Commit**

```bash
cd D:/VYNTIA
git add apps/web/src/features/identity/
git commit -m "$(cat <<'EOF'
chore(B2): lint cleanup in features/identity (-N warnings, #87)

Mechanical fixes: unused imports/vars removed or _-prefixed, narrowed
`any` types where the actual shape is obvious, fixed missing useEffect/
useCallback dependency arrays. No runtime behavior changes.

Frontend lint baseline drops from 439 to ~424 problems.

Backlog item: #87.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Final verification + close-out

Verification only — no new code.

- [ ] **Step 1: Confirm clean working tree on the branch**

```bash
cd D:/VYNTIA
git status
git log --oneline master..HEAD
```

Expected: clean tree; ~7-8 commits on the branch (one per Task 2-8).

- [ ] **Step 2: Backend final pytest**

```bash
cd D:/VYNTIA
source .venv/Scripts/activate || true
cd apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: **301 passed / 3 failed / 17 skipped** (290 baseline + 11 new tests added across Tasks 2, 3, 5).

- [ ] **Step 3: Backend system check**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
```

Expected: 0 silenced.

- [ ] **Step 4: Frontend baselines**

```bash
cd D:/VYNTIA/apps/web
npx eslint . 2>&1 | tail -3
npm test -- --run 2>&1 | tail -10
npm run build 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
```

Expected:
- ESLint: ~424 problems (down from 439).
- vitest: 7 files / 32 tests passing.
- build: clean.
- tsc: 1 pre-existing error.

- [ ] **Step 5: Audit ViewSets actually moved**

```bash
cd D:/VYNTIA/apps/api
grep -n "^class \(UsuarioViewSet\|RolViewSet\|PermisoViewSet\|ModulosViewSet\|RolPermisosViewSet\|UsuarioRolesViewSet\)" api/v1/identity/views.py api/v1/rrhh/views.py 2>/dev/null
```

Expected: 6 hits in `api/v1/identity/views.py`, 0 hits in `api/v1/rrhh/views.py`.

- [ ] **Step 6: Audit tenant filter in roles_activos / permisos_activos**

```bash
cd D:/VYNTIA/apps/api
grep -n "get_current_tenant\|tenant=tenant" apps/identity/models/user.py | head
```

Expected: at least 4-6 hits — the import + the conditional filter applications in both methods.

- [ ] **Step 7: Audit ADRs**

```bash
cd D:/VYNTIA
grep -n "## ADR-B\." .planning/audit-B/ADRS.md | tail
```

Expected: ADR-B.10 and ADR-B.11 added.

- [ ] **Step 8: Update memory pointer**

Update `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/subproject_b_progress.md`:
- Change B.2 row from `⏳ pending` to `🚧 ready for review (N commits, branch tip <SHA>)`.
- Update the close-out sub-section with B.2 deliverables (or add one if not present).

After merge to master, update again with the merge SHA.

- [ ] **Step 9: Report status**

Do NOT auto-merge. Report to user: "B.2 plan executed across N commits on `vyntia/B2-polish-identity`. Baselines: pytest 301/3/17 (+11 new tests), vitest preserved, ESLint ~424 (down from 439), build clean, tsc 1. Ready for review."

---

## Self-Review

**Spec coverage check:**

| Backlog item | Task | Status |
|---|---|---|
| #44 User.tiempo_desde_ultimo_login fall-through | Task 2 | ✓ |
| #45 UsuarioManager.activos field bug | Task 3 | ✓ (also fixes #45 dead code in por_rol) |
| #46 Permission.modulo CharField | Task 4 | ✓ (decision documented + dead code removed) |
| #47 Migrate identity ViewSets | Task 7 | ✓ |
| #48 PermissionService + MenuService tenant filter | Task 5 | ✓ (fix at User method layer covers both services) |
| #49 UserRole vs TenantMembership.role decision | Task 6 | ✓ (ADR-B.11) |
| #87 Lint cleanup features/identity | Task 8 | ✓ |

All 7 in-scope items covered.

**Out-of-scope items NOT covered (correctly):**
- #40-#42 (employees app filter bugs) — defer to B.4 polish-employees per master roadmap
- Any frontend ViewSet changes — not flagged in BACKLOG for B.2

**Placeholder scan:** every step has full code or precise commands. No "TBD" / "implement later" placeholders.

**Type consistency:**
- `tenant_context` import path consistent with C-phase usage (`apps.tenancy.context`).
- Task 5's User method patches use the same import block style and `getattr(self.request, "tenant", None)` pattern wouldn't apply here because we're in a model method, not a ViewSet — `get_current_tenant()` from the ContextVar is correct.
- ADR file paths consistent (`.planning/audit-B/ADRS.md`).
- No undefined types or methods introduced.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-09-vyntia-B2-polish-identity.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task with review between tasks; matches B.1 execution model.

**2. Inline Execution** — execute tasks in this session via executing-plans.

Which approach?
