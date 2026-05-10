# B.1 Polish Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the cross-cutting baseline that every subsequent B-phase polish (B.2–B.5b) and module phase (B.6–B.15) depends on: identity P0 security fixes, a `TenantAwareViewSetMixin` consumed by all 6 Core apps, the new `audit_lite` app for high-stakes domain events (ADR-B.2), a `TenantStorage` abstraction layer (ADR-B.4), and frontend lint baseline cleanup.

**Architecture:** Three new core utilities ship in `apps/core/`: a `TenantAwareViewSetMixin` (auto-injects `request.tenant` into `perform_create` and filters `get_queryset`), a `TenantStorage` wrapper around Django's `default_storage` (prefixes paths with `<tenant_id>/`), and a lazy logger import for `audit_lite.record_event()`. A new Django app `apps.audit_lite` provides a single `AuditEvent` model with admin-only viewer. Identity bugs are fixed at the serializer/view layer (not the model) so the existing `User.registrar_intento_fallido()` and `User.bloquear_usuario()` plumbing is reused. Frontend lint baseline drops by ~202 warnings via `.eslintignore` for `src/generated/api/`.

**Tech Stack:** Django 5.2 + DRF, pytest, pytest-django, vitest, ESLint, npm workspaces. Multi-tenant primitives (`apps.tenancy.context.get_current_tenant`, `request.tenant`, `RLSMiddleware`) are already in place from C.0–C.8.

**Branch:** `vyntia/B1-polish-baseline`
**Commit prefix:** `chore(B1):` for refactors; `fix(B1):` for bug fixes; `feat(B1):` for new infrastructure (`TenantAwareViewSetMixin`, `audit_lite`, `TenantStorage`).
**Backlog items in scope:** #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12, #13, #14, #15, #36, #37 (17 items).
**Out of scope (deferred to per-app polish phases):** #16–#33 (employees/documents/onboarding stale-consumer bugs go to B.4/B.5/B.5b per master roadmap §1).

**Test baselines to preserve (from L5 close-out):**
- pytest: 161 passed / 7–8 failed / 3 skipped
- vitest: 7 passed
- TS strict: 1 pre-existing error (`generated/api/models/BlankEnum.ts:6:5`)
- ESLint: 634 warnings (target post-B.1: ≤ ~430 after generated ignore)
- `npm run build`: clean

After B.1, the baselines must be: pytest **165+ passed / 3–4 failed / 3 skipped** (5 identity tests now pass), vitest 7+, ESLint baseline drops to ~430, build still clean.

---

## File Structure

### New files

| Path | Purpose |
|---|---|
| `apps/api/apps/core/viewsets.py` | `TenantAwareViewSetMixin` — injects `tenant=request.tenant` in `perform_create`; filters `get_queryset` by `tenant=request.tenant` |
| `apps/api/apps/core/storage.py` | `TenantStorage` class wrapping `default_storage` with `<tenant_id>/` prefix (ADR-B.4) |
| `apps/api/apps/audit_lite/__init__.py` | new app marker |
| `apps/api/apps/audit_lite/apps.py` | `AuditLiteConfig(name="apps.audit_lite", label="audit_lite")` |
| `apps/api/apps/audit_lite/models.py` | `AuditEvent` model (tenant, actor_user, action, target_model, target_id, payload_json, created_at) |
| `apps/api/apps/audit_lite/admin.py` | Django admin readonly viewer |
| `apps/api/apps/audit_lite/services.py` | `record_event()` helper |
| `apps/api/apps/audit_lite/migrations/0001_initial.py` | initial migration (auto-generated) |
| `apps/api/apps/audit_lite/tests/__init__.py` | test package |
| `apps/api/apps/audit_lite/tests/test_audit_event.py` | model + record_event tests |
| `apps/api/apps/core/tests/test_tenant_aware_mixin.py` | mixin behavior tests (perform_create propagates tenant; cross-tenant get_queryset filtered) |
| `apps/api/apps/core/tests/test_tenant_storage.py` | TenantStorage prefix tests |
| `apps/web/.eslintignore` | adds `src/generated/api/` directory |

### Modified files

| Path | Reason |
|---|---|
| `apps/api/api/v1/auth/serializers.py` | Fix `UserUpdateSerializer` (item #5: persist nombres/apellidos); fix `LoginSerializer` 400 contract (item #3 — investigate route) |
| `apps/api/api/v1/auth/views.py` | Fix `LoginAPIView` to refuse blocked users (item #1), increment `intentos_fallidos` on failure (item #2), return 400 on logout invalid refresh token (item #4) |
| `apps/api/vyntia/settings/base.py` | Register `apps.audit_lite.apps.AuditLiteConfig` in `LOCAL_APPS` |
| `apps/api/api/v1/rrhh/views.py` | Apply `TenantAwareViewSetMixin` to: AreaViewSet, EmpleadoViewSet, ContratosAdendasViewSet, ContractAmendmentViewSet, DatosLaboralesViewSet, DocumentosDigitalesViewSet, OnboardingViewSet (items #7, #8, #10, #11, #13, #14, #15). Also add `@require_hr` decorators on ContractAmendmentViewSet write actions (item #12). |
| `apps/api/api/v1/rrhh/serializers.py` | `EmpleadoCreateSerializer.create()` — propagate `tenant` to nested EmploymentData/FamilyMember/AcademicRecord (item #9) |
| `apps/api/apps/onboarding/services/onboarding_service.py` | `crear_onboarding_completo` — propagate `tenant` to Employee/User/OnboardingProcess (item #15) |
| `apps/web/.eslintignore` | new file (item #36) |
| `apps/web/eslint.config.js` (or wherever rules live) | maybe add disable rule for BlankEnum generated file (item #37 — alternative) |

### File responsibility boundaries

- **Mixin lives in `apps/core/viewsets.py`, not in each app** — single source of truth for tenant injection.
- **`audit_lite` app stays minimal** — one model, one helper, one admin. Sub-proyecto X replaces it later.
- **`TenantStorage` lives in `apps/core/storage.py`** — ready for B.5b to consume; B.1 just ships the abstraction.
- **Identity fixes stay in serializers/views**, not models — `User.registrar_intento_fallido()` already exists and is correct; the bug is that the JWT login path doesn't call it.

---

## Task 1: Branch setup + frontend lint baseline cleanup

**Files:**
- Create: `apps/web/.eslintignore`
- Modify (optional): `apps/web/eslint.config.js`

This task is the warm-up — it touches frontend only and reduces lint noise from 634 → ~432 warnings, making subsequent backend work easier to verify in isolation.

- [ ] **Step 1: Branch off master**

```bash
cd D:/VYNTIA
git checkout master
git pull --ff-only
git checkout -b vyntia/B1-polish-baseline
```

- [ ] **Step 2: Capture lint baseline**

```bash
cd apps/web
npm run lint 2>&1 | tail -5
```

Expected: `✖ 634 problems (0 errors, 634 warnings)` (or whatever the L5 close-out baseline was).

Record the exact number for the verification step.

- [ ] **Step 3: Create `.eslintignore` for generated client**

```bash
cd D:/VYNTIA
```

Create `apps/web/.eslintignore` with content:

```
# Auto-generated OpenAPI client — never lint
src/generated/api/

# Build artifacts (already ignored by default but explicit doesn't hurt)
dist/
build/
node_modules/
```

- [ ] **Step 4: Verify lint warnings dropped**

```bash
cd D:/VYNTIA/apps/web
npm run lint 2>&1 | tail -5
```

Expected: count drops by ~202 (from 634 to ~432). Exact number depends on current generated file count; the directional drop is what matters.

If `npm run lint` doesn't honor `.eslintignore` (some flat-config projects need `ignores` in `eslint.config.js` instead), fall back to **Step 4a**:

- [ ] **Step 4a (only if Step 4 didn't drop warnings): Add `ignores` to flat config**

Read `apps/web/eslint.config.js` and add `ignores: ['src/generated/api/**', 'dist/**', 'build/**', 'node_modules/**']` to the top-level config object. Re-run lint.

- [ ] **Step 5: Verify build still clean**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -5
```

Expected: `✓ built in <N>s` (no new errors).

- [ ] **Step 6: Verify TS check unchanged**

```bash
cd D:/VYNTIA/apps/web
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
```

Expected: 1 pre-existing error in `generated/api/models/BlankEnum.ts:6:5`. No new errors.

- [ ] **Step 7: Commit**

```bash
cd D:/VYNTIA
git add apps/web/.eslintignore
# include eslint.config.js only if Step 4a was needed
git commit -m "chore(B1): add .eslintignore for src/generated/ — drops ~202 lint warnings (#36, #37)"
```

- [ ] **Step 8: Verify backend baseline before backend work begins**

```bash
cd D:/VYNTIA
source .venv/Scripts/activate
cd apps/api
pytest 2>&1 | tail -3
```

Expected: `161 passed, 7-8 failed, 3 skipped` (the 5 identity tests are among the 7–8 expected failures).

Record exact numbers — Tasks 2–6 will progressively turn 5 of those failures into passes.

---

## Task 2: Fix `UserUpdateSerializer` (item #5) — persist nombres/apellidos

**Files:**
- Modify: `apps/api/api/v1/auth/serializers.py:761-775`
- Test (existing): `apps/api/tests/test_auth_api.py:285-303` (`test_actualizar_perfil_exitoso`)

The current `UserUpdateSerializer.Meta.fields = ['email']` only allows email updates. The test sends `nombres_usuario` and `apellidos_usuario`, expects 200 and field persistence.

- [ ] **Step 1: Run the failing test to confirm baseline**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::UserProfileAPITest::test_actualizar_perfil_exitoso -v
```

Expected: FAIL — `AssertionError: 'testuser' != 'Nuevo Nombre'` (the field doesn't update).

- [ ] **Step 2: Verify the test contract**

Open `apps/api/tests/test_auth_api.py:285-303`. The test posts:

```python
data = {
    'nombres_usuario': 'Nuevo Nombre',
    'apellidos_usuario': 'Nuevo Apellido'
}
```

…then asserts:

```python
self.assertEqual(self.usuario.nombres_usuario, 'Nuevo Nombre')
self.assertEqual(self.usuario.apellidos_usuario, 'Nuevo Apellido')
```

So the serializer must accept and persist both fields.

- [ ] **Step 3: Verify the User model has these fields**

```bash
cd D:/VYNTIA/apps/api
grep -n "nombres_usuario\|apellidos_usuario" apps/identity/models/user.py | head -5
```

Expected: at least one match each. (If they don't exist, the test itself is wrong — but the model has these fields per the legacy schema; verify before editing.)

- [ ] **Step 4: Update the serializer to include the fields**

Edit `apps/api/api/v1/auth/serializers.py:761-775`:

```python
class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = ['email', 'nombres_usuario', 'apellidos_usuario']

    def validate_email(self, value: str) -> str:
        """Validate email uniqueness."""
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                'Este email ya está en uso por otro usuario.'
            )
        return value
```

- [ ] **Step 5: Run the test — must pass**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::UserProfileAPITest::test_actualizar_perfil_exitoso -v
```

Expected: PASS.

- [ ] **Step 6: Run the full auth test class to verify no regression**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py -v 2>&1 | tail -20
```

Expected: this test now passes; no other test broke.

- [ ] **Step 7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/auth/serializers.py
git commit -m "fix(B1): UserUpdateSerializer persists nombres_usuario/apellidos_usuario (#5)"
```

---

## Task 3: Fix `LoginAPIView` 400 vs 401 on missing fields (item #3)

**Files:**
- Modify: `apps/api/api/v1/auth/views.py:82-134` (`LoginAPIView.post`)
- Test (existing): `apps/api/tests/test_auth_api.py:148-157` (`test_login_datos_faltantes`)

The test sends `{username: 'testuser'}` (no password) and expects HTTP 400. Currently the view returns 401 because it catches all exceptions in a single `except Exception` handler.

- [ ] **Step 1: Run failing test**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::LoginAPITest::test_login_datos_faltantes -v
```

Expected: FAIL — `AssertionError: 401 != 400`.

- [ ] **Step 2: Inspect the current control flow**

In `apps/api/api/v1/auth/views.py:82-134`, the `post` method:
- Calls `serializer.is_valid(raise_exception=True)`. When required fields are missing, this raises `rest_framework.exceptions.ValidationError`, which subclasses `APIException` and inherits status 400.
- The `except Exception as e:` clause at line 129 catches the ValidationError and rewrites it to 401 — that's the bug.

- [ ] **Step 3: Fix the exception handling**

Edit `apps/api/api/v1/auth/views.py` to catch `ValidationError` separately and let it return 400, before the catch-all `Exception` handler:

```python
def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
    """Authenticate user and return JWT tokens in JSON response only."""
    from rest_framework.exceptions import PermissionDenied, ValidationError

    serializer = self.get_serializer(data=request.data)

    try:
        serializer.is_valid(raise_exception=True)

        # Update last login
        user = serializer.user
        if hasattr(user, "ultimo_acceso"):
            user.ultimo_acceso = timezone.now()
            user.save(update_fields=["ultimo_acceso"])

        # Extract tokens and user data
        validated_data = serializer.validated_data

        return APIResponse.success(
            data=validated_data,
            message="Inicio de sesion exitoso",
            status_code=status.HTTP_200_OK,
        )

    except ValidationError as e:
        # Missing fields, malformed data, etc. — surface as 400
        return APIResponse.error(
            message="Datos de inicio de sesión inválidos",
            errors=e.detail if hasattr(e, "detail") else {"detail": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except PermissionDenied as e:
        # C.4: User authenticated but has no active TenantMembership for
        # the tenant resolved from the subdomain — return 403, not 401.
        return APIResponse.error(
            message="Acceso denegado al workspace",
            errors={"detail": str(e.detail) if hasattr(e, "detail") else str(e)},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except Exception as e:
        return APIResponse.error(
            message="Error en el inicio de sesion",
            errors={"detail": str(e)},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
```

- [ ] **Step 4: Run failing test — must pass**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::LoginAPITest::test_login_datos_faltantes -v
```

Expected: PASS (400 returned).

- [ ] **Step 5: Run all login tests to confirm no regression**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::LoginAPITest -v 2>&1 | tail -15
```

Expected: previously-passing login tests (credenciales_invalidas, usuario_inexistente, usuario_inactivo) still pass. Tests #1 and #2 (bloqueado, intentos_fallidos) still FAIL — those are Tasks 5 and 6.

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/auth/views.py
git commit -m "fix(B1): LoginAPIView returns 400 (not 401) on missing fields (#3)"
```

---

## Task 4: Fix `LogoutAPIView` rejects invalid refresh tokens (item #4)

**Files:**
- Modify: `apps/api/api/v1/auth/views.py:138-177` (`LogoutAPIView.post`)
- Test (existing): `apps/api/tests/test_auth_api.py:217-228` (`test_logout_token_invalido`)

The test authenticates a user, then posts `{refresh: 'invalid_refresh_token'}` and expects 400. Currently the view swallows the `RefreshToken(...)` exception silently and returns 200.

- [ ] **Step 1: Run failing test**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::LogoutAPITest::test_logout_token_invalido -v
```

Expected: FAIL — `AssertionError: 200 != 400`.

- [ ] **Step 2: Inspect current `LogoutAPIView`**

In `apps/api/api/v1/auth/views.py:152-177`, the inner `try/except Exception: pass` swallows malformed-token errors. Replace with explicit error handling.

- [ ] **Step 3: Fix logout error path**

Edit `apps/api/api/v1/auth/views.py` `LogoutAPIView.post`:

```python
def post(self, request: Request) -> Response:
    """Logout user and blacklist refresh token."""
    from rest_framework_simplejwt.exceptions import TokenError

    refresh_token = request.data.get("refresh_token") or request.data.get("refresh")

    if not refresh_token:
        return APIResponse.error(
            message="Token de refresco requerido",
            errors={"refresh": "Este campo es obligatorio."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError as exc:
        return APIResponse.error(
            message="Token de refresco inválido",
            errors={"refresh": str(exc)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    logout(request)
    return APIResponse.success(
        message="Cierre de sesión exitoso",
        status_code=status.HTTP_200_OK,
    )
```

Note: the test uses `data = {'refresh': 'invalid_refresh_token'}` (the key is `refresh`, not `refresh_token`). The fix accepts both for backward compatibility.

- [ ] **Step 4: Run failing test — must pass**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::LogoutAPITest::test_logout_token_invalido -v
```

Expected: PASS.

- [ ] **Step 5: Run all logout tests — confirm `test_logout_exitoso` still passes**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::LogoutAPITest -v 2>&1 | tail -10
```

Expected: all 3 logout tests pass (`test_logout_exitoso` already passed; `test_logout_token_invalido` now passes; `test_logout_sin_autenticacion` was already passing).

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/auth/views.py
git commit -m "fix(B1): LogoutAPIView rejects invalid refresh tokens with 400 (#4)"
```

---

## Task 5: Fix login bypass — bloqueado users get JWT (item #1)

**Files:**
- Modify: `apps/api/api/v1/auth/serializers.py:65-134` (`CustomTokenObtainPairSerializer.validate`)
- Test (existing): `apps/api/tests/test_auth_api.py:174-187` (`test_login_usuario_bloqueado`)

The test calls `usuario.bloquear_usuario('Test de bloqueo')` (sets `estado_usuario='bloqueado'`), then attempts login with correct credentials. It expects 401. Currently login succeeds because `CustomTokenObtainPairSerializer.validate` only checks `is_active` (Django's built-in) and ignores `estado_usuario`.

- [ ] **Step 1: Run failing test**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::LoginAPITest::test_login_usuario_bloqueado -v
```

Expected: FAIL — `AssertionError: 200 != 401` (the JWT is issued despite the user being blocked).

- [ ] **Step 2: Decide where to enforce — pre-validate or post-validate?**

The cleanest hook is `CustomTokenObtainPairSerializer.validate(self, attrs)` at `apps/api/api/v1/auth/serializers.py:65`. After `super().validate(attrs)` succeeds, `self.user` is populated. We check `esta_bloqueado` before returning data.

Why post-validate, not in `Authentication`/`User.is_active`: the test asserts that `desactivar_usuario()` (sets `is_active=False`) AND `bloquear_usuario()` (sets `estado_usuario='bloqueado'` while keeping `is_active=True`) BOTH return 401. The `is_active` path is already enforced by Django auth; the `bloqueado` path requires our explicit check.

- [ ] **Step 3: Add bloqueado check to serializer**

Edit `apps/api/api/v1/auth/serializers.py`. At the start of `CustomTokenObtainPairSerializer.validate`, AFTER `super().validate(attrs)` succeeds, BEFORE the C.4 membership block, insert:

```python
def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
    from rest_framework.exceptions import AuthenticationFailed

    data = super().validate(attrs)

    usuario = self.user

    # ---- B.1 (#1): Refuse JWT if user is blocked ----
    if usuario.esta_bloqueado:
        raise AuthenticationFailed(
            detail="Usuario bloqueado.",
            code="user_blocked",
        )

    # ---- C.4: enforce TenantMembership when request.tenant is set ----
    request = self.context.get("request")
    tenant = getattr(request, "tenant", None) if request is not None else None
    # ... (existing C.4 code unchanged)
```

`User.esta_bloqueado` is already a property on `apps/identity/models/user.py:198-211`; it returns `True` when `estado_usuario == 'bloqueado'` OR `intentos_fallidos >= 5` OR temporally blocked via `fecha_bloqueo`.

`AuthenticationFailed` returns 401 by default — matching the test's expected status code, and matching `test_login_usuario_inactivo` behavior.

- [ ] **Step 4: Run failing test — must pass**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::LoginAPITest::test_login_usuario_bloqueado -v
```

Expected: PASS (401 returned, blocked user cannot get JWT).

- [ ] **Step 5: Confirm no regression on other login tests**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::LoginAPITest -v 2>&1 | tail -10
```

Expected: `test_login_usuario_bloqueado` passes; other tests (exitoso, credenciales_invalidas, etc.) continue passing.

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/auth/serializers.py
git commit -m "fix(B1): refuse JWT for bloqueado users — login bypass (#1)"
```

---

## Task 6: Fix `intentos_fallidos` counter not incremented on JWT login (item #2)

**Files:**
- Modify: `apps/api/api/v1/auth/serializers.py` (`CustomTokenObtainPairSerializer`)
- Test (existing): `apps/api/tests/test_auth_api.py:417-436` (`test_multiples_intentos_login_fallidos`)

The test runs 6 failed login attempts (wrong password) and expects:
- Each attempt returns 401.
- After the 6th attempt, `usuario.estado_usuario == 'bloqueado'`.
- A subsequent correct-credentials attempt also returns 401 (because user is now blocked — covered by Task 5).

Currently, `CustomTokenObtainPairSerializer.validate` (via SimpleJWT's `TokenObtainSerializer`) just calls `authenticate()` and lets the parent raise `AuthenticationFailed` on bad credentials — never invoking `User.registrar_intento_fallido()`. The counter stays at 0 forever.

`User.registrar_intento_fallido()` exists at `apps/identity/models/user.py:289-297` and already implements the increment + auto-block at 5 attempts.

- [ ] **Step 1: Run failing test**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::AuthAPISecurityTest::test_multiples_intentos_login_fallidos -v
```

Expected: FAIL — `AssertionError: 'activo' != 'bloqueado'` (the counter never increments, user never blocks).

- [ ] **Step 2: Override `validate()` to call `registrar_intento_fallido()` on failure**

The strategy: catch the `AuthenticationFailed` from the parent's `validate()`, look up the user by `username` from `attrs`, increment the counter, then re-raise.

Edit `apps/api/api/v1/auth/serializers.py`. Replace the start of `CustomTokenObtainPairSerializer.validate`:

```python
def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
    from rest_framework.exceptions import AuthenticationFailed

    try:
        data = super().validate(attrs)
    except AuthenticationFailed:
        # ---- B.1 (#2): Increment intentos_fallidos on bad credentials ----
        # The parent's authenticate() call returned None — credentials are bad
        # OR the user is_active=False. Look up by username; if found and active,
        # bump the counter so repeated wrong passwords block the account.
        username = attrs.get(self.username_field)
        if username:
            try:
                target = User.objects.get(**{self.username_field: username})
                # Only count fails for accounts that exist and are not already
                # disabled — otherwise we leak account existence via timing.
                if target.is_active:
                    target.registrar_intento_fallido()
            except User.DoesNotExist:
                pass
        raise

    usuario = self.user

    # ---- B.1 (#1): Refuse JWT if user is blocked ----
    if usuario.esta_bloqueado:
        raise AuthenticationFailed(
            detail="Usuario bloqueado.",
            code="user_blocked",
        )

    # ---- B.1 (#2): Reset counter on successful login ----
    if usuario.intentos_fallidos > 0:
        usuario.resetear_intentos_fallidos()

    # ---- C.4: enforce TenantMembership when request.tenant is set ----
    request = self.context.get("request")
    # ... (existing code unchanged)
```

`User.resetear_intentos_fallidos()` already exists at `apps/identity/models/user.py:299-306` and clears the counter + unblocks if blocked.

- [ ] **Step 3: Run failing test — must pass**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py::AuthAPISecurityTest::test_multiples_intentos_login_fallidos -v
```

Expected: PASS. After 6 fails, `estado_usuario == 'bloqueado'`. The 7th attempt (correct creds) returns 401 because `esta_bloqueado` is True (Task 5 enforces this).

- [ ] **Step 4: Run all auth tests for regression check**

```bash
cd D:/VYNTIA/apps/api
pytest tests/test_auth_api.py -v 2>&1 | tail -25
```

Expected: 5 previously-failing identity tests now pass (#1–#5). Other tests unchanged.

- [ ] **Step 5: Run full backend suite**

```bash
cd D:/VYNTIA/apps/api
pytest 2>&1 | tail -3
```

Expected: pytest count moves from `161 passed, 7-8 failed` to `165-166 passed, 2-3 failed`. Record exact numbers.

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/auth/serializers.py
git commit -m "fix(B1): increment intentos_fallidos on JWT login failure + reset on success (#2)"
```

---

## Task 7: Introduce `TenantAwareViewSetMixin` in apps/core/

**Files:**
- Create: `apps/api/apps/core/viewsets.py`
- Create: `apps/api/apps/core/tests/__init__.py` (if missing)
- Create: `apps/api/apps/core/tests/test_tenant_aware_mixin.py`

The mixin centralizes the tenant injection pattern. ViewSets that use it stop being able to orphan rows (`tenant=NULL`) on `perform_create`, and their `get_queryset` filters by `request.tenant` as defense-in-depth alongside RLS.

- [ ] **Step 1: Verify `apps/core/tests/` exists**

```bash
cd D:/VYNTIA/apps/api
ls apps/core/tests/ 2>/dev/null || mkdir -p apps/core/tests
```

If `apps/core/tests/__init__.py` doesn't exist, create it as an empty file.

- [ ] **Step 2: Write the failing test FIRST (TDD)**

Create `apps/api/apps/core/tests/test_tenant_aware_mixin.py`:

```python
"""Tests for TenantAwareViewSetMixin.

Verifies:
1. perform_create propagates request.tenant to serializer.save(tenant=...)
2. get_queryset filters by request.tenant when tenant is set
3. When request.tenant is None (admin/reserved subdomain), behavior is permissive
"""

import pytest
from unittest.mock import MagicMock

from apps.core.viewsets import TenantAwareViewSetMixin


class _FakeViewSet(TenantAwareViewSetMixin):
    """Minimal viewset stub for testing the mixin in isolation."""

    def __init__(self, request, queryset):
        self.request = request
        self._queryset = queryset

    def get_queryset(self):
        # Mirror DRF: subclasses call super().get_queryset() then mixin filters
        return super().get_queryset()


@pytest.mark.django_db
class TestTenantAwareViewSetMixin:
    def test_perform_create_passes_tenant_to_serializer_save(self):
        request = MagicMock()
        request.tenant = MagicMock()
        request.tenant.id = "fake-tenant-id"

        viewset = _FakeViewSet(request=request, queryset=MagicMock())
        serializer = MagicMock()

        viewset.perform_create(serializer)

        serializer.save.assert_called_once_with(tenant=request.tenant)

    def test_perform_create_no_tenant_passes_no_kwarg(self):
        """When request.tenant is None (admin subdomain), don't pass tenant kwarg."""
        request = MagicMock()
        request.tenant = None

        viewset = _FakeViewSet(request=request, queryset=MagicMock())
        serializer = MagicMock()

        viewset.perform_create(serializer)

        serializer.save.assert_called_once_with()

    def test_get_queryset_filters_by_tenant(self):
        request = MagicMock()
        request.tenant = MagicMock()

        # The base get_queryset returns a queryset; mixin should call .filter(tenant=...)
        base_qs = MagicMock()
        filtered_qs = MagicMock()
        base_qs.filter.return_value = filtered_qs

        class _ViewSet(TenantAwareViewSetMixin):
            def __init__(self, request, qs):
                self.request = request
                self._base_qs = qs

            def get_queryset(self):
                # Bypass MRO: pretend super returns base_qs
                from apps.core.viewsets import TenantAwareViewSetMixin as M
                # Call directly so the mixin sees the base_qs
                return M._filter_by_tenant(self, self._base_qs)

        vs = _ViewSet(request, base_qs)
        result = vs.get_queryset()

        base_qs.filter.assert_called_once_with(tenant=request.tenant)
        assert result is filtered_qs

    def test_get_queryset_no_tenant_returns_unfiltered(self):
        request = MagicMock()
        request.tenant = None
        base_qs = MagicMock()

        class _ViewSet(TenantAwareViewSetMixin):
            def __init__(self, request, qs):
                self.request = request
                self._base_qs = qs

            def get_queryset(self):
                from apps.core.viewsets import TenantAwareViewSetMixin as M
                return M._filter_by_tenant(self, self._base_qs)

        vs = _ViewSet(request, base_qs)
        result = vs.get_queryset()

        # No filter applied — base queryset returned as-is
        base_qs.filter.assert_not_called()
        assert result is base_qs
```

- [ ] **Step 3: Run test — should FAIL with import error**

```bash
cd D:/VYNTIA/apps/api
pytest apps/core/tests/test_tenant_aware_mixin.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'apps.core.viewsets'`.

- [ ] **Step 4: Implement the mixin**

Create `apps/api/apps/core/viewsets.py`:

```python
"""Cross-cutting ViewSet mixins.

`TenantAwareViewSetMixin` is the canonical hook for ViewSets serving
tenant-scoped models. It injects `tenant=request.tenant` into serializer.save()
on create, and filters the default queryset by `tenant=request.tenant`.

The mixin is permissive when `request.tenant` is None (admin subdomain,
reserved subdomain, or non-tenant routes) — it does not raise; it falls
through to default behavior. Tenant resolution happens upstream in
`apps.tenancy.middleware.TenantMiddleware`.

Defense-in-depth: even with this mixin in place, RLS (set in
`apps.tenancy.middleware.RLSMiddleware`) is the authoritative database-level
isolation. The mixin is a belt-and-suspenders measure that catches bugs
before they ever reach RLS.

Usage:
    from apps.core.viewsets import TenantAwareViewSetMixin
    from rest_framework import viewsets

    class MyViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
        queryset = MyModel.objects.all()
        serializer_class = MySerializer
"""


class TenantAwareViewSetMixin:
    """Inject request.tenant on create + filter queryset on read."""

    def perform_create(self, serializer):
        """Save the new instance with tenant=request.tenant if available."""
        tenant = getattr(self.request, "tenant", None)
        if tenant is not None:
            serializer.save(tenant=tenant)
        else:
            serializer.save()

    def get_queryset(self):
        queryset = super().get_queryset()
        return self._filter_by_tenant(queryset)

    def _filter_by_tenant(self, queryset):
        """Filter a queryset by request.tenant if present.

        Extracted as a separate method so subclasses that override
        get_queryset() can opt-in to the filter explicitly.
        """
        tenant = getattr(self.request, "tenant", None)
        if tenant is not None:
            return queryset.filter(tenant=tenant)
        return queryset
```

- [ ] **Step 5: Run tests — must PASS**

```bash
cd D:/VYNTIA/apps/api
pytest apps/core/tests/test_tenant_aware_mixin.py -v
```

Expected: 4 PASS.

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/core/viewsets.py apps/api/apps/core/tests/test_tenant_aware_mixin.py
git commit -m "feat(B1): TenantAwareViewSetMixin — perform_create + get_queryset tenant injection (#6)"
```

---

## Task 8: Apply mixin to `AreaViewSet` (organization, item #7)

**Files:**
- Modify: `apps/api/api/v1/rrhh/views.py:170-368` (`AreaViewSet`)

The current `perform_create` (lines 218-228) calls `serializer.save()` without tenant. The current `get_queryset` (lines 185-216) doesn't filter by tenant. After the mixin is applied, both use the mixin's behavior.

- [ ] **Step 1: Inspect current `AreaViewSet`**

```bash
cd D:/VYNTIA/apps/api
sed -n '170,230p' api/v1/rrhh/views.py
```

Note: the existing `get_queryset` adds annotations (`empleados_activos_count`) for list view. We must preserve that — the mixin's `_filter_by_tenant` is layered on top.

- [ ] **Step 2: Edit the class declaration to mix in the new behavior**

In `apps/api/api/v1/rrhh/views.py` find:

```python
class AreaViewSet(viewsets.ModelViewSet):
```

…and change to:

```python
from apps.core.viewsets import TenantAwareViewSetMixin

class AreaViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
```

(Add the import once at the top of the file if not already present.)

- [ ] **Step 3: Update `get_queryset` to opt into tenant filtering**

The existing `get_queryset` returns a manually-built queryset, NOT `super().get_queryset()`. We need it to call `self._filter_by_tenant(queryset)` before returning, so tenant filtering applies.

Modify the `return queryset` lines at the end of `get_queryset` to:

```python
return self._filter_by_tenant(queryset)
```

(There are 2 returns — one inside the `if incluir_inactivas:` branch and one at the end. Apply to both.)

- [ ] **Step 4: Replace `perform_create` to use the mixin**

The current `perform_create` (lines 218-228) does logging plus `serializer.save()`. We need to keep the logging but defer the save to the mixin. Replace with:

```python
def perform_create(self, serializer):
    """Create area with logging."""
    super().perform_create(serializer)  # mixin injects tenant + saves
    area = serializer.instance
    logger.info(
        f"Área creada: {area.siglas_area}",
        extra={
            "user_id": self.request.user.pk,
            "id": area.pk,
            "action": "create_area",
        },
    )
```

`super().perform_create(serializer)` invokes the mixin (since the mixin is leftmost in MRO).

- [ ] **Step 5: Verify — run pytest for organization tests if any exist**

```bash
cd D:/VYNTIA/apps/api
pytest tests/ -k area -v 2>&1 | tail -10
pytest 2>&1 | tail -3
```

Expected: no regression. If specific area tests exist, they pass. Full suite count unchanged or improved.

- [ ] **Step 6: Smoke test the create endpoint manually**

This is best done with a curl command after `manage.py runserver` is up, but since `runserver` has the local UnicodeDecodeError quirk, fall back to `manage.py check`:

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/views.py
git commit -m "fix(B1): AreaViewSet uses TenantAwareViewSetMixin — orphan tenant fix (#7)"
```

---

## Task 9: Apply mixin to `EmpleadoViewSet` + propagate tenant in `EmpleadoCreateSerializer` (items #8, #9)

**Files:**
- Modify: `apps/api/api/v1/rrhh/views.py` — `EmpleadoViewSet` (find via grep)
- Modify: `apps/api/api/v1/rrhh/serializers.py` — `EmpleadoCreateSerializer.create()` (find via grep)

Item #8 is `perform_create` orphan, fixed by mixin. Item #9 is the harder one: `EmpleadoCreateSerializer.create()` creates nested EmploymentData / FamilyMember / AcademicRecord rows that ALSO need `tenant=` propagated.

- [ ] **Step 1: Locate `EmpleadoViewSet` and the serializer**

```bash
cd D:/VYNTIA/apps/api
grep -n "class EmpleadoViewSet\|class EmpleadoCreateSerializer" api/v1/rrhh/views.py api/v1/rrhh/serializers.py | head -5
```

Note the file:line for each.

- [ ] **Step 2: Apply mixin to `EmpleadoViewSet`**

Change `class EmpleadoViewSet(viewsets.ModelViewSet):` to `class EmpleadoViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):`.

If the class already has its own `perform_create` and `get_queryset`, follow the Task 8 pattern: call `super().perform_create(serializer)` first, then keep custom logging; in `get_queryset`, end with `return self._filter_by_tenant(queryset)` for each return path.

If the existing `perform_create` does extra serializer validation (e.g., creates the User row before the Employee), keep that logic and just ensure the final `serializer.save()` happens via `super().perform_create(serializer)` so tenant is injected.

- [ ] **Step 3: Inspect `EmpleadoCreateSerializer.create`**

```bash
cd D:/VYNTIA/apps/api
grep -n "def create" api/v1/rrhh/serializers.py | head -10
```

Find the `EmpleadoCreateSerializer.create` method. It likely:

```python
def create(self, validated_data):
    nested_data = validated_data.pop('datos_laborales', None)
    family_data = validated_data.pop('datos_familiares', None)
    academic_data = validated_data.pop('datos_academicos', None)
    empleado = Employee.objects.create(**validated_data)
    if nested_data:
        EmploymentData.objects.create(empleado=empleado, **nested_data)
    if family_data:
        for fd in family_data:
            FamilyMember.objects.create(empleado=empleado, **fd)
    if academic_data:
        for ad in academic_data:
            AcademicRecord.objects.create(empleado=empleado, **ad)
    return empleado
```

- [ ] **Step 4: Propagate tenant to nested children**

Modify the `create()` method to extract `tenant` from `validated_data` (the mixin injects it via `serializer.save(tenant=...)`) and pass it to every nested `.objects.create(...)` call:

```python
def create(self, validated_data):
    tenant = validated_data.get('tenant')  # injected by TenantAwareViewSetMixin
    nested_data = validated_data.pop('datos_laborales', None)
    family_data = validated_data.pop('datos_familiares', None)
    academic_data = validated_data.pop('datos_academicos', None)

    empleado = Employee.objects.create(**validated_data)

    if nested_data:
        EmploymentData.objects.create(
            empleado=empleado,
            tenant=tenant,
            **nested_data,
        )
    if family_data:
        for fd in family_data:
            FamilyMember.objects.create(
                empleado=empleado,
                tenant=tenant,
                **fd,
            )
    if academic_data:
        for ad in academic_data:
            AcademicRecord.objects.create(
                empleado=empleado,
                tenant=tenant,
                **ad,
            )
    return empleado
```

If the model field is named differently (e.g., `EmploymentData` uses `empleado=` and there's no `tenant=` kwarg), the `tenant=` kwarg is rejected at model level — investigate via:

```bash
grep -n "class EmploymentData\|class FamilyMember\|class AcademicRecord" apps/contracts/models/*.py apps/employees/models/*.py
```

If these models don't have a `tenant` field, that's a C-phase regression — flag it and STOP. Otherwise proceed.

- [ ] **Step 5: Verify no test regression**

```bash
cd D:/VYNTIA/apps/api
pytest 2>&1 | tail -3
```

Expected: count unchanged (no new failures). If an existing employee test breaks because of a missing `tenant=` argument required by the model, the model needs `null=True, blank=True` on tenant or the test fixture needs updating — investigate before committing.

- [ ] **Step 6: System check**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development
```

Expected: 0 issues.

- [ ] **Step 7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/views.py apps/api/api/v1/rrhh/serializers.py
git commit -m "fix(B1): EmpleadoViewSet + EmpleadoCreateSerializer propagate tenant to nested rows (#8, #9)"
```

---

## Task 10: Apply mixin to `ContratosAdendasViewSet` (contracts, item #10)

**Files:**
- Modify: `apps/api/api/v1/rrhh/contratos_views.py` (or `views.py` — locate via grep)

- [ ] **Step 1: Locate `ContratosAdendasViewSet`**

```bash
cd D:/VYNTIA/apps/api
grep -rn "class ContratosAdendasViewSet" api/v1/
```

- [ ] **Step 2: Apply mixin (Task 8 pattern)**

Change `class ContratosAdendasViewSet(viewsets.ModelViewSet):` to `class ContratosAdendasViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):`. Update `perform_create` and `get_queryset` per the Task 8 pattern.

If there's a `renovar_contrato` action that creates a new Contract object directly, audit it: it must pass `tenant=request.tenant` to the create call.

- [ ] **Step 3: Verify**

```bash
cd D:/VYNTIA/apps/api
pytest 2>&1 | tail -3
python manage.py check --settings=vyntia.settings.development
```

Expected: no regression, 0 check issues.

- [ ] **Step 4: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/contratos_views.py
git commit -m "fix(B1): ContratosAdendasViewSet uses TenantAwareViewSetMixin (#10)"
```

---

## Task 11: Apply mixin to `ContractAmendmentViewSet` + add @require_hr (items #11, #12)

**Files:**
- Modify: `apps/api/api/v1/rrhh/contratos_views.py` (or wherever `ContractAmendmentViewSet` lives)

- [ ] **Step 1: Locate the ViewSet**

```bash
cd D:/VYNTIA/apps/api
grep -rn "class ContractAmendmentViewSet\|class ContractAmendmentSerializer" api/v1/ apps/contracts/
```

- [ ] **Step 2: Apply mixin (Task 8 pattern)**

Change the class to extend `TenantAwareViewSetMixin`. Update `perform_create` and `get_queryset`.

- [ ] **Step 3: Add @require_hr decorators on write actions (item #12)**

Currently any authenticated user can CRUD amendments. Add the role gate. The pattern in the codebase (see `apps/api/apps/core/decorators.py`) is:

```python
from apps.core.decorators import require_hr

class ContractAmendmentViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    # ... existing config

    @require_hr()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_hr()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
```

Read endpoints (list, retrieve) stay accessible to authenticated users.

If the codebase has an established pattern of using `permission_classes = [...]` instead of method decorators, prefer that — match the surrounding style.

- [ ] **Step 4: Verify**

```bash
cd D:/VYNTIA/apps/api
pytest 2>&1 | tail -3
python manage.py check --settings=vyntia.settings.development
```

- [ ] **Step 5: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/contratos_views.py
git commit -m "fix(B1): ContractAmendmentViewSet — tenant mixin + @require_hr on writes (#11, #12)"
```

---

## Task 12: Apply mixin to `DatosLaboralesViewSet` (item #13)

**Files:**
- Modify: `apps/api/api/v1/rrhh/contratos_views.py` (or wherever the ViewSet lives)

- [ ] **Step 1: Locate**

```bash
cd D:/VYNTIA/apps/api
grep -rn "class DatosLaboralesViewSet" api/v1/
```

- [ ] **Step 2: Apply mixin (Task 8 pattern)**

Change inheritance and update `perform_create` / `get_queryset`.

⚠️ Note: `DatosLaboralesViewSet` has known field bugs (item #63: search_fields/ordering_fields reference non-existent fields; item #64: estadisticas_remuneracion uses non-existent fields; item #65: filterset references non-existent fields; item #67: queryset declared twice). Those fixes are **out of scope for B.1** (they live in B.5 contracts polish). Touch ONLY the mixin application.

- [ ] **Step 3: Verify**

```bash
cd D:/VYNTIA/apps/api
pytest 2>&1 | tail -3
python manage.py check --settings=vyntia.settings.development
```

- [ ] **Step 4: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/contratos_views.py
git commit -m "fix(B1): DatosLaboralesViewSet uses TenantAwareViewSetMixin (#13)"
```

---

## Task 13: Apply mixin to `DocumentosDigitalesViewSet` (item #14)

**Files:**
- Modify: `apps/api/api/v1/rrhh/views.py` (or `apps/documents/` if it was relocated)

- [ ] **Step 1: Locate**

```bash
cd D:/VYNTIA/apps/api
grep -rn "class DocumentosDigitalesViewSet" api/v1/ apps/documents/
```

- [ ] **Step 2: Apply mixin**

Change inheritance. Update `perform_create` and `get_queryset`.

⚠️ The `subir_institucional` custom @action also creates DigitalDocument rows. Audit it for tenant propagation: if it does `DocumentosDigitales.objects.create(...)` directly, add `tenant=request.tenant` to the kwargs.

- [ ] **Step 3: Verify**

```bash
cd D:/VYNTIA/apps/api
pytest 2>&1 | tail -3
python manage.py check --settings=vyntia.settings.development
```

- [ ] **Step 4: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/views.py
git commit -m "fix(B1): DocumentosDigitalesViewSet + subir_institucional propagate tenant (#14)"
```

---

## Task 14: Apply mixin to `OnboardingViewSet` + propagate tenant in `OnboardingService.crear_onboarding_completo` (item #15)

**Files:**
- Modify: `apps/api/api/v1/rrhh/views.py` — `OnboardingViewSet`
- Modify: `apps/api/apps/onboarding/services/onboarding_service.py` — `crear_onboarding_completo`

The service is the harder target: it creates Employee + User + OnboardingProcess in a single transaction. All three must receive `tenant=request.tenant`.

- [ ] **Step 1: Locate**

```bash
cd D:/VYNTIA/apps/api
grep -rn "class OnboardingViewSet" api/v1/
grep -n "def crear_onboarding_completo" apps/onboarding/services/onboarding_service.py
```

- [ ] **Step 2: Apply mixin to ViewSet**

Standard Task 8 pattern.

- [ ] **Step 3: Audit and fix `crear_onboarding_completo`**

Read the function. It likely takes a `data` dict and creates Employee, User, OnboardingProcess. Update its signature to accept a `tenant` kwarg and propagate it to every `.objects.create(...)`:

```python
def crear_onboarding_completo(self, data, tenant=None):
    # Create Employee
    empleado = Employee.objects.create(tenant=tenant, **employee_data)
    # Create User linked to Employee
    user = User.objects.create_user(
        tenant=tenant,
        **user_data,
    )
    # Create OnboardingProcess
    proceso = OnboardingProcess.objects.create(
        tenant=tenant,
        empleado=empleado,
        **proceso_data,
    )
    return empleado, user, proceso
```

If `User` model doesn't accept a `tenant=` kwarg (some auth user models don't), check the User model: in this codebase, `User` is `apps.identity.User` — verify it has a `tenant` FK before passing the kwarg. If User is NOT tenant-scoped (cross-tenant identity), don't pass tenant to it; only Employee and OnboardingProcess receive it.

```bash
grep -n "tenant" apps/identity/models/user.py | head -5
```

- [ ] **Step 4: Update ViewSet caller to pass tenant**

The `OnboardingViewSet` action that calls `crear_onboarding_completo` (likely a `create` or custom action) must pass `tenant=request.tenant`:

```python
def create(self, request, *args, **kwargs):
    service = OnboardingService()
    empleado, user, proceso = service.crear_onboarding_completo(
        data=request.data,
        tenant=request.tenant,
    )
    # ... existing response handling
```

- [ ] **Step 5: Verify**

```bash
cd D:/VYNTIA/apps/api
pytest 2>&1 | tail -3
python manage.py check --settings=vyntia.settings.development
```

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/views.py apps/api/apps/onboarding/services/onboarding_service.py
git commit -m "fix(B1): OnboardingService + ViewSet propagate tenant to Employee/User/Process (#15)"
```

---

## Task 15: Introduce `audit_lite` app with `AuditEvent` model (ADR-B.2)

**Files:**
- Create: `apps/api/apps/audit_lite/__init__.py`
- Create: `apps/api/apps/audit_lite/apps.py`
- Create: `apps/api/apps/audit_lite/models.py`
- Create: `apps/api/apps/audit_lite/admin.py`
- Create: `apps/api/apps/audit_lite/services.py`
- Create: `apps/api/apps/audit_lite/migrations/__init__.py`
- Create: `apps/api/apps/audit_lite/tests/__init__.py`
- Create: `apps/api/apps/audit_lite/tests/test_audit_event.py`
- Modify: `apps/api/vyntia/settings/base.py` — register the app

ADR-B.2 specifies a single `AuditEvent` model with `tenant`, `actor_user`, `action`, `target_model`, `target_id`, `payload_json`, `created_at`, plus a `record_event()` helper. No retention policy, no UI viewer beyond Django admin.

- [ ] **Step 1: Write the failing test FIRST**

Create `apps/api/apps/audit_lite/tests/__init__.py` (empty) and `apps/api/apps/audit_lite/tests/test_audit_event.py`:

```python
"""Tests for audit_lite domain audit events (ADR-B.2)."""

import pytest
from django.contrib.auth import get_user_model

from apps.audit_lite.models import AuditEvent
from apps.audit_lite.services import record_event


User = get_user_model()


@pytest.mark.django_db
class TestAuditEvent:
    def test_audit_event_can_be_created(self, tenant, admin_user):
        """A bare AuditEvent persists with required fields."""
        event = AuditEvent.objects.create(
            tenant=tenant,
            actor_user=admin_user,
            action="employee.terminated",
            target_model="employees.Employee",
            target_id="some-uuid",
            payload_json={"reason": "voluntary"},
        )
        assert event.pk is not None
        assert event.created_at is not None
        assert event.payload_json == {"reason": "voluntary"}

    def test_record_event_helper_persists_event(self, tenant, admin_user):
        """`record_event(...)` helper creates an AuditEvent inside current tenant context."""
        event = record_event(
            tenant=tenant,
            actor_user=admin_user,
            action="contract.amended",
            target_model="contracts.Contract",
            target_id="contract-uuid",
            payload={"old_salary": 1000, "new_salary": 1500},
        )
        assert event.pk is not None
        assert event.action == "contract.amended"
        assert event.payload_json["old_salary"] == 1000
        assert AuditEvent.objects.filter(action="contract.amended").count() == 1

    def test_record_event_accepts_string_target_id(self, tenant, admin_user):
        """target_id stores any string (UUID, int as str, composite key)."""
        event = record_event(
            tenant=tenant,
            actor_user=admin_user,
            action="user.password_reset",
            target_model="identity.User",
            target_id="42",
            payload={},
        )
        assert event.target_id == "42"
```

If `tenant` and `admin_user` fixtures don't already exist in `conftest.py`, the test will fail at fixture resolution — investigate the existing C-phase test fixtures and reuse them. Search:

```bash
cd D:/VYNTIA/apps/api
grep -n "def tenant\|def admin_user" conftest.py tests/conftest.py 2>/dev/null
```

Adapt the test to match available fixtures.

- [ ] **Step 2: Run test — should FAIL with import error**

```bash
cd D:/VYNTIA/apps/api
pytest apps/audit_lite/tests/test_audit_event.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'apps.audit_lite'`.

- [ ] **Step 3: Create `apps.py`**

`apps/api/apps/audit_lite/apps.py`:

```python
"""App config for audit_lite — minimal domain audit events (ADR-B.2)."""

from django.apps import AppConfig


class AuditLiteConfig(AppConfig):
    name = "apps.audit_lite"
    label = "audit_lite"
    verbose_name = "Audit Lite (B.X)"
    default_auto_field = "django.db.models.UUIDField"
```

`apps/api/apps/audit_lite/__init__.py`:

```python
default_app_config = "apps.audit_lite.apps.AuditLiteConfig"
```

`apps/api/apps/audit_lite/migrations/__init__.py`: (empty)

- [ ] **Step 4: Create the model**

`apps/api/apps/audit_lite/models.py`:

```python
"""AuditEvent — single-table domain audit log (ADR-B.2).

Sub-proyecto X will replace this with a full event store. For B, this captures
high-stakes mutations (cese, desvinculación, contract amendments, position
changes) with enough payload to reconstruct what happened.

Each AuditEvent is tenant-scoped. When sub-proyecto X arrives, these rows
migrate to the new event store; the `record_event()` helper call sites are
the only refactor surface.
"""

import uuid

from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    """A single high-stakes domain event recorded inline with the mutation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="+",
        db_index=True,
    )

    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        help_text="User who performed the action. Null for system-initiated events.",
    )

    action = models.CharField(
        max_length=128,
        db_index=True,
        help_text='Dotted action name, e.g. "employee.terminated".',
    )

    target_model = models.CharField(
        max_length=128,
        help_text='Dotted model name, e.g. "employees.Employee".',
    )

    target_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text="String form of target's primary key (UUID or int as str).",
    )

    payload_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of the mutation: before/after, reason, etc.",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_lite_event"
        verbose_name = "Audit event"
        verbose_name_plural = "Audit events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "action", "-created_at"]),
            models.Index(fields=["target_model", "target_id"]),
        ]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action} → {self.target_model}:{self.target_id}"
```

- [ ] **Step 5: Create the helper**

`apps/api/apps/audit_lite/services.py`:

```python
"""record_event helper — single entry point for B-phase audit hooks (ADR-B.2)."""

from .models import AuditEvent


def record_event(
    *,
    tenant,
    actor_user,
    action: str,
    target_model: str,
    target_id,
    payload: dict | None = None,
) -> AuditEvent:
    """Persist an audit event for a high-stakes domain mutation.

    Call inside the same transaction as the mutation so it commits atomically.

    Args:
        tenant: the active Tenant (required).
        actor_user: the User who performed the action (None for system events).
        action: dotted action name, e.g. "employee.terminated".
        target_model: dotted model label, e.g. "employees.Employee".
        target_id: primary key of the affected row, coerced to str.
        payload: optional JSON-serializable dict with mutation details.

    Returns:
        The persisted AuditEvent.
    """
    return AuditEvent.objects.create(
        tenant=tenant,
        actor_user=actor_user,
        action=action,
        target_model=target_model,
        target_id=str(target_id),
        payload_json=payload or {},
    )
```

- [ ] **Step 6: Create the admin (read-only viewer)**

`apps/api/apps/audit_lite/admin.py`:

```python
"""Read-only admin for AuditEvent — operators inspect via Django admin only."""

from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "action",
        "target_model",
        "target_id",
        "actor_user",
        "tenant",
    )
    list_filter = ("action", "target_model", "tenant")
    search_fields = ("action", "target_model", "target_id")
    date_hierarchy = "created_at"
    readonly_fields = (
        "id",
        "tenant",
        "actor_user",
        "action",
        "target_model",
        "target_id",
        "payload_json",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
```

- [ ] **Step 7: Register the app in settings**

Edit `apps/api/vyntia/settings/base.py`. Find the `LOCAL_APPS` list and add `"apps.audit_lite.apps.AuditLiteConfig"`:

```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    # ... existing apps
    "apps.audit_lite.apps.AuditLiteConfig",
]
```

If the project uses a different app-list pattern, follow it.

- [ ] **Step 8: Generate the migration**

```bash
cd D:/VYNTIA/apps/api
source D:/VYNTIA/.venv/Scripts/activate
python manage.py makemigrations audit_lite --settings=vyntia.settings.development
```

Expected: creates `apps/api/apps/audit_lite/migrations/0001_initial.py`. Inspect it briefly to confirm it builds the `audit_lite_event` table with the right columns.

If `makemigrations` fails because the local DB has the `UnicodeDecodeError` issue, use the testing settings:

```bash
python manage.py makemigrations audit_lite --settings=vyntia.settings.testing
```

- [ ] **Step 9: Run the migration on the test database (via pytest)**

pytest-django auto-applies migrations. Just run the audit_lite tests:

```bash
cd D:/VYNTIA/apps/api
pytest apps/audit_lite/tests/test_audit_event.py -v
```

Expected: tests PASS.

If fixtures (`tenant`, `admin_user`) are missing, add minimal fixtures to `apps/audit_lite/tests/conftest.py`:

```python
import pytest


@pytest.fixture
def tenant(db):
    from apps.tenancy.models import Tenant
    return Tenant.objects.create(name="Test Tenant", slug="test")


@pytest.fixture
def admin_user(db, tenant):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin",
        email="admin@test.local",
        password="testpass123",
    )
```

(Adapt fields to what `Tenant` and `User` actually require — e.g., if `Tenant.create` needs a `subdomain` or other field, set it.)

- [ ] **Step 10: Run full backend suite — confirm baseline preserved + 3 new tests pass**

```bash
cd D:/VYNTIA/apps/api
pytest 2>&1 | tail -3
python manage.py check --settings=vyntia.settings.development
```

Expected: pytest count = previous-passing + 3 (audit_lite tests). Check is clean.

- [ ] **Step 11: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/audit_lite/ apps/api/vyntia/settings/base.py
git commit -m "feat(B1): audit_lite app — AuditEvent model + record_event helper (ADR-B.2)"
```

---

## Task 16: Introduce `TenantStorage` abstraction (ADR-B.4)

**Files:**
- Create: `apps/api/apps/core/storage.py`
- Create: `apps/api/apps/core/tests/test_tenant_storage.py`

ADR-B.4 specifies `TenantStorage` wraps `default_storage` and prefixes all paths with `<tenant_id>/`. B.5b later applies it to upload sites; B.1 just ships the abstraction so it's ready.

- [ ] **Step 1: Write the failing test FIRST**

Create `apps/api/apps/core/tests/test_tenant_storage.py`:

```python
"""Tests for TenantStorage prefix wrapper (ADR-B.4)."""

import pytest
from unittest.mock import MagicMock, patch

from apps.core.storage import TenantStorage


class TestTenantStorage:
    def test_save_prefixes_path_with_tenant_id(self):
        inner = MagicMock()
        inner.save.return_value = "tenant-abc/legajos/legajo.pdf"

        with patch("apps.core.storage.default_storage", inner), \
             patch("apps.core.storage.get_current_tenant_id", return_value="tenant-abc"):
            storage = TenantStorage()
            content = MagicMock()
            result = storage.save("legajos/legajo.pdf", content)

        inner.save.assert_called_once_with("tenant-abc/legajos/legajo.pdf", content, max_length=None)
        assert result == "tenant-abc/legajos/legajo.pdf"

    def test_save_without_tenant_falls_back_to_default(self):
        inner = MagicMock()
        inner.save.return_value = "legajos/legajo.pdf"

        with patch("apps.core.storage.default_storage", inner), \
             patch("apps.core.storage.get_current_tenant_id", return_value=None):
            storage = TenantStorage()
            content = MagicMock()
            result = storage.save("legajos/legajo.pdf", content)

        inner.save.assert_called_once_with("legajos/legajo.pdf", content, max_length=None)

    def test_url_prefixes_path(self):
        inner = MagicMock()
        inner.url.return_value = "/media/tenant-abc/legajos/legajo.pdf"

        with patch("apps.core.storage.default_storage", inner), \
             patch("apps.core.storage.get_current_tenant_id", return_value="tenant-abc"):
            storage = TenantStorage()
            url = storage.url("legajos/legajo.pdf")

        inner.url.assert_called_once_with("tenant-abc/legajos/legajo.pdf")

    def test_exists_prefixes_path(self):
        inner = MagicMock()
        inner.exists.return_value = True

        with patch("apps.core.storage.default_storage", inner), \
             patch("apps.core.storage.get_current_tenant_id", return_value="tenant-abc"):
            storage = TenantStorage()
            result = storage.exists("legajos/x.pdf")

        inner.exists.assert_called_once_with("tenant-abc/legajos/x.pdf")
        assert result is True
```

- [ ] **Step 2: Run test — must FAIL with import error**

```bash
cd D:/VYNTIA/apps/api
pytest apps/core/tests/test_tenant_storage.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'apps.core.storage'`.

- [ ] **Step 3: Implement `TenantStorage`**

Create `apps/api/apps/core/storage.py`:

```python
"""TenantStorage — wraps default_storage with a per-tenant path prefix (ADR-B.4).

All document-writing code (PDF generator, contract upload, legajo upload)
should use TenantStorage instead of default_storage directly. Switching to
S3/Azure later becomes a settings change plus a one-time data migration,
not a code rewrite.

Usage:
    from apps.core.storage import TenantStorage

    storage = TenantStorage()
    storage.save("legajos/foo.pdf", content)  # actually saves to <tenant_id>/legajos/foo.pdf

When no tenant context is active (admin commands, reserved subdomains),
TenantStorage falls through to default_storage with no prefix.
"""

from django.core.files.storage import default_storage

from apps.tenancy.context import get_current_tenant_id


class TenantStorage:
    """Wrap django.core.files.storage.default_storage with a tenant prefix.

    The prefix is `<tenant_id>/` derived from the active tenant context.
    When no tenant is active, no prefix is added — caller is responsible
    for handling that case (typically: refuse to write).
    """

    def _prefix(self, name: str) -> str:
        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            return name
        return f"{tenant_id}/{name}"

    def save(self, name, content, max_length=None):
        return default_storage.save(self._prefix(name), content, max_length=max_length)

    def open(self, name, mode="rb"):
        return default_storage.open(self._prefix(name), mode)

    def delete(self, name):
        return default_storage.delete(self._prefix(name))

    def exists(self, name):
        return default_storage.exists(self._prefix(name))

    def url(self, name):
        return default_storage.url(self._prefix(name))

    def size(self, name):
        return default_storage.size(self._prefix(name))

    def listdir(self, path):
        return default_storage.listdir(self._prefix(path))
```

- [ ] **Step 4: Run tests — must PASS**

```bash
cd D:/VYNTIA/apps/api
pytest apps/core/tests/test_tenant_storage.py -v
```

Expected: 4 PASS.

- [ ] **Step 5: System check + full pytest**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development
pytest 2>&1 | tail -3
```

Expected: 0 issues. pytest count grows by 4 (TenantStorage tests).

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/core/storage.py apps/api/apps/core/tests/test_tenant_storage.py
git commit -m "feat(B1): TenantStorage abstraction — tenant-prefixed file paths (ADR-B.4)"
```

---

## Task 17: Final verification + close-out

This task verifies that all B.1 deliverables are in place and the test baselines are met.

**Files:** none modified — verification only.

- [ ] **Step 1: Confirm working tree is clean (all prior commits flushed)**

```bash
cd D:/VYNTIA
git status
```

Expected: `nothing to commit, working tree clean`. If anything is uncommitted, decide whether to include it in a final close-out commit or split.

- [ ] **Step 2: Backend baseline check**

```bash
cd D:/VYNTIA
source .venv/Scripts/activate
cd apps/api
pytest 2>&1 | tail -3
```

Expected: **`165+ passed, 2-3 failed, 3 skipped`** (5 identity tests plus 7 new tests in `audit_lite` + `test_tenant_aware_mixin` + `test_tenant_storage` = 12 net new passes, but Tasks 5 & 6 turned 5 prior failures into passes; net delta from `161 passed, 7-8 failed` is +12 passes / -5 failures).

If pytest shows >=165 passed AND <=3 failed, baseline is met. If failures > 3, run `pytest --lf -v` to identify regressions, fix them in a small follow-up commit, and re-run.

- [ ] **Step 3: Backend system check clean**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 4: Frontend baselines**

```bash
cd D:/VYNTIA/apps/web
npm run lint 2>&1 | tail -3
npm test -- --run 2>&1 | tail -10
npm run build 2>&1 | tail -5
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -3
```

Expected:
- Lint: ~430 warnings (down from 634 by ~202).
- Vitest: 7 passed (no new tests; baseline preserved).
- Build: clean.
- tsc: 1 pre-existing error (`BlankEnum.ts:6:5`).

- [ ] **Step 5: Audit the 6 ViewSets actually use the mixin**

```bash
cd D:/VYNTIA/apps/api
grep -rn "TenantAwareViewSetMixin" api/v1/ apps/onboarding/services/
```

Expected: at least 7 hits (one mixin import + class declaration in: AreaViewSet, EmpleadoViewSet, ContratosAdendasViewSet, ContractAmendmentViewSet, DatosLaboralesViewSet, DocumentosDigitalesViewSet, OnboardingViewSet) + propagation in OnboardingService.

- [ ] **Step 6: Audit the audit_lite + storage skeletons**

```bash
cd D:/VYNTIA/apps/api
ls apps/audit_lite/
ls apps/core/storage.py apps/core/viewsets.py
```

Expected: all files present. `apps/audit_lite/migrations/0001_initial.py` exists.

- [ ] **Step 7: Tag B.1 as ready (do NOT merge yet — wait for user review)**

Do NOT auto-merge. Push the branch and report status to the user:

```bash
cd D:/VYNTIA
git log --oneline master..HEAD
```

Expected output: 13–17 commits, all `chore(B1):` / `fix(B1):` / `feat(B1):` prefixed.

- [ ] **Step 8: Update memory + roadmap pointer**

Update `MEMORY.md` (in `C:\Users\zeeke\.claude\projects\D--VYNTIA\memory\subproject_b_progress.md`) — change B.1 row from `⏳ pending` to `🚧 in PR — branch vyntia/B1-polish-baseline ready for review`. Save the merge SHA after merge.

Report to user: "B.1 plan executed across 17 commits on `vyntia/B1-polish-baseline`. Baselines: pytest **<exact count>**, vitest 7, lint **<exact>** (down ~202), build clean, tsc 1. Ready for review and merge."

---

## Self-Review

**Spec coverage check (against the master roadmap row for B.1 + the ADRs that flag B.1 deliverables):**

| Master-roadmap deliverable | Task | Status |
|---|---|---|
| Polish wave: bug-fix baseline (pytest fixes) | Tasks 2–6 | ✓ |
| tsc fix | Task 1 (ESLint ignore) | ✓ partial — BlankEnum tsc error stays as 1 known baseline; ignore makes lint silence; full tsc fix is BlankEnum.ts regenerate, deferred to a smaller follow-up if needed |
| lint cleanup | Task 1 | ✓ (~202 warnings dropped) |
| tenant audit fixes (ViewSet pattern) | Tasks 7–14 | ✓ |
| ADR-B.2 audit_lite app | Task 15 | ✓ |
| ADR-B.4 TenantStorage abstraction | Task 16 | ✓ |
| ADR-B.3 ApprovableMixin | (NOT IN B.1) | deferred to B.13 (first phase that needs approvals) — YAGNI |

**Backlog item coverage:**

| # | Item | Task |
|---|---|---|
| 1 | Login bypass | Task 5 |
| 2 | intentos_fallidos counter | Task 6 |
| 3 | LoginAPIView 401→400 on missing fields | Task 3 |
| 4 | LogoutAPIView accepts invalid refresh | Task 4 |
| 5 | UserUpdateSerializer doesn't persist | Task 2 |
| 6 | TenantAwareViewSetMixin | Task 7 |
| 7 | Department perform_create orphan | Task 8 |
| 8 | EmpleadoViewSet perform_create orphan | Task 9 |
| 9 | EmpleadoCreateSerializer nested tenant | Task 9 |
| 10 | ContratosAdendasViewSet orphan | Task 10 |
| 11 | ContractAmendmentViewSet orphan | Task 11 |
| 12 | ContractAmendmentViewSet @require_hr | Task 11 |
| 13 | DatosLaboralesViewSet orphan | Task 12 |
| 14 | DocumentosDigitalesViewSet orphan | Task 13 |
| 15 | OnboardingService tenant propagation | Task 14 |
| 36 | .eslintignore for src/generated/ | Task 1 |
| 37 | BlankEnum.ts ESLint disable | Task 1 (ignore covers it) |

All 17 in-scope items covered.

**Placeholder scan:** every step has either a complete code block or a precise grep/command. No "TBD" / "implement later" / "appropriate error handling" placeholders.

**Type consistency:**
- `TenantAwareViewSetMixin` declared in Task 7; consumed in Tasks 8–14 with consistent class name and `_filter_by_tenant` helper.
- `record_event(...)` declared in Task 15 with kwarg signature `(tenant, actor_user, action, target_model, target_id, payload)`; matches the test calls.
- `TenantStorage` declared in Task 16 with methods `save/open/delete/exists/url/size/listdir`; matches the test calls.
- All identity fixes (Tasks 2–6) reference `User` methods that exist (`registrar_intento_fallido`, `resetear_intentos_fallidos`, `esta_bloqueado` property) — verified against `apps/identity/models/user.py:198-360`.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-09-vyntia-B1-polish-baseline.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
