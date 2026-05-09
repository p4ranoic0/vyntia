# C.4 — Tenant-Aware Authentication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make authentication tenant-aware. JWT tokens issued by `LoginAPIView` carry `tenant_id`, `tenant_slug`, and `membership_role` claims; login on a tenant subdomain enforces an active `TenantMembership`; new endpoints handle invitation activation, workspace listing for multi-tenant users, and cross-subdomain workspace exchange.

**Architecture:** Five additive endpoints + claim injection in the existing `CustomTokenObtainPairSerializer`. No model changes (uses `Tenant`, `TenantMembership`, `TenantInvitation` from C.0; relies on `TenantMiddleware` from C.3 for `request.tenant`). The 31 existing auth tests are preserved by being **lenient when `request.tenant is None`** (legacy/admin/test-server hostnames) — same pattern as C.3 middleware. The exchange flow uses short-lived (5 min) signed JWTs as one-time tokens; true single-use semantics are deferred to a future hardening pass.

**Tech Stack:** Django 5.2, DRF, `rest_framework_simplejwt` (already in use). Redis is NOT required.

**Source spec:** `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` § 6, § 7

**Source roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`

---

## Baseline snapshot

| Check | Command | Expected |
|---|---|---|
| Django system | `cd apps/api && python manage.py check --settings=vyntia.settings.development` | No errors |
| Backend tests | `cd apps/api && pytest tests/ apps/tenancy/tests/ -q` | ≥209 passed / ≤8 failed / 15 skipped |
| Frontend build | `cd apps/web && npm run build` | Exit 0 |

C.4 adds: ~25 new tests (login claims + membership enforcement + activation + workspaces + exchange). Target ≥234 passed.

---

## File structure

**Files to create:**

```
apps/api/api/v1/auth/
└── (modifications to existing views.py, serializers.py, urls.py)

apps/api/api/v1/workspaces/
├── __init__.py
├── urls.py                                # /api/v1/workspaces/ + /{slug}/exchange/
├── views.py                               # WorkspacesListView, WorkspaceExchangeView
└── serializers.py                         # WorkspaceSerializer

apps/api/apps/tenancy/auth/
├── __init__.py
├── exchange_token.py                      # generate + verify exchange tokens
└── activation.py                          # validate + accept TenantInvitation

apps/api/apps/tenancy/tests/
├── test_login_tenant_aware.py             # tenant-aware login tests
├── test_activation_endpoint.py            # activation flow tests
├── test_workspaces_endpoint.py            # workspaces listing + exchange tests
└── test_jwt_tenant_claims.py              # JWT claim emission tests
```

**Files to modify:**

- `apps/api/api/v1/auth/serializers.py` — `CustomTokenObtainPairSerializer.get_token()` adds tenant claims; `LoginSerializer.validate()` enforces membership
- `apps/api/api/v1/auth/views.py` — new `ActivateAPIView` + new `AuthExchangeAPIView`
- `apps/api/api/v1/auth/urls.py` — wire `activate/` and `exchange/`
- `apps/api/api/urls.py` (or `vyntia/urls.py`) — wire `/api/v1/workspaces/` namespace

---

## Branch

`vyntia/C4-auth-tenant-aware` — branched from `master` (HEAD has `Merge C.3`).

---

## Task 1: JWT claims — `tenant_id`, `tenant_slug`, `membership_role`

**Files:**
- Modify: `apps/api/api/v1/auth/serializers.py` (override `get_token` classmethod)
- Create: `apps/api/apps/tenancy/tests/test_jwt_tenant_claims.py`

- [ ] **Step 1.1: Create branch**

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/C4-auth-tenant-aware
```

- [ ] **Step 1.2: Write failing tests**

Create `apps/api/apps/tenancy/tests/test_jwt_tenant_claims.py`:

```python
"""Tests for tenant claims emission in JWT tokens."""

import pytest
from rest_framework_simplejwt.tokens import AccessToken

from apps.tenancy.context import tenant_context
from apps.tenancy.models import Tenant, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant_acme(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20123456789",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def member_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@acme.com", password="x"
    )


@pytest.fixture
def membership(tenant_acme, member_user):
    return TenantMembership.objects.create(
        tenant=tenant_acme, user=member_user, role="admin", status="active"
    )


@pytest.mark.django_db
class TestTokenClaimsWithTenantContext:
    def test_token_includes_tenant_id_when_context_set(self, tenant_acme, member_user, membership):
        """When issued during a tenant context, the access token has tenant_id claim."""
        from api.v1.auth.serializers import CustomTokenObtainPairSerializer

        with tenant_context(tenant_acme):
            token = CustomTokenObtainPairSerializer.get_token(member_user)
        assert token["tenant_id"] == str(tenant_acme.id)
        assert token["tenant_slug"] == "acme"
        assert token["membership_role"] == "admin"

    def test_token_omits_tenant_claims_when_no_context(self, member_user):
        """Without tenant context (legacy/admin paths), token has no tenant claims."""
        from api.v1.auth.serializers import CustomTokenObtainPairSerializer

        token = CustomTokenObtainPairSerializer.get_token(member_user)
        # Backward-compat: tokens minted without tenant context still work
        assert "tenant_id" not in token or token["tenant_id"] is None
        assert "tenant_slug" not in token or token["tenant_slug"] is None

    def test_token_omits_tenant_claims_when_no_membership(self, tenant_acme, member_user):
        """If user has no membership in the active tenant, claims are absent.

        This shouldn't happen in normal flow (login enforces membership in Task 2),
        but the serializer is defensive.
        """
        from api.v1.auth.serializers import CustomTokenObtainPairSerializer

        with tenant_context(tenant_acme):
            token = CustomTokenObtainPairSerializer.get_token(member_user)
        # No membership exists → no role claim
        assert "membership_role" not in token or token["membership_role"] is None
```

- [ ] **Step 1.3: Run tests — should fail (claims not yet emitted)**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_jwt_tenant_claims.py -v 2>&1 | tail -10
```

Expected: 3 tests fail (no `get_token` override → no tenant claims).

- [ ] **Step 1.4: Override `get_token` in `CustomTokenObtainPairSerializer`**

In `apps/api/api/v1/auth/serializers.py`, find the `CustomTokenObtainPairSerializer` class. Add this classmethod (place it before the `validate` method):

```python
    @classmethod
    def get_token(cls, user):
        """Mint an access token, injecting tenant claims when a tenant context is active.

        Called by the parent `validate()` during login. We read the active tenant
        from the ContextVar (set by TenantMiddleware) and the user's membership in
        that tenant; both go into the JWT payload so RLSMiddleware and
        TenantAuthMiddleware can validate downstream requests.

        Defensive: omits claims if context is missing or membership doesn't exist.
        Login enforcement (Task 2) ensures membership exists before this is called
        in production paths.
        """
        token = super().get_token(user)

        from apps.tenancy.context import get_current_tenant

        tenant = get_current_tenant()
        if tenant is not None:
            token["tenant_id"] = str(tenant.id)
            token["tenant_slug"] = tenant.slug

            # Lookup the user's membership in this tenant — emit role claim if present
            from apps.tenancy.models import TenantMembership

            membership = (
                TenantMembership.objects.filter(
                    tenant=tenant, user=user, status="active"
                )
                .only("role")
                .first()
            )
            if membership is not None:
                token["membership_role"] = membership.role

        return token
```

- [ ] **Step 1.5: Run tests — should pass**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_jwt_tenant_claims.py -v 2>&1 | tail -10
```

Expected: 3 tests passed.

- [ ] **Step 1.6: Run full suite — no regression in existing 31 auth tests**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥212 passed (209 baseline + 3 new). Existing auth tests don't pass through tenant context → tokens have no tenant claims → tests still work.

- [ ] **Step 1.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/auth/serializers.py apps/api/apps/tenancy/tests/test_jwt_tenant_claims.py
git commit -m "feat(C4): JWT tokens include tenant_id, tenant_slug, membership_role claims when context is active"
```

---

## Task 2: Login enforces TenantMembership

**Files:**
- Modify: `apps/api/api/v1/auth/serializers.py` (`LoginSerializer.validate`)
- Create: `apps/api/apps/tenancy/tests/test_login_tenant_aware.py`

- [ ] **Step 2.1: Write failing tests**

Create `apps/api/apps/tenancy/tests/test_login_tenant_aware.py`:

```python
"""Tests for tenant-aware login enforcement."""

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from apps.tenancy.models import Tenant, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="testpass123"
    )


@pytest.fixture
def tenant_acme(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20123456789",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def member_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="maria", email="maria@acme.com", password="testpass123"
    )
    return user


@pytest.fixture
def member_in_acme(tenant_acme, member_user):
    return TenantMembership.objects.create(
        tenant=tenant_acme, user=member_user, role="admin", status="active"
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
class TestLoginWithoutTenantSubdomain:
    """Legacy: login from a non-tenant host (testserver, admin) works as before."""

    def test_login_succeeds_without_tenant_context(self, client, member_user):
        """Backward-compat: existing tests using testserver hostname still pass."""
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "maria", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json().get("data") or response.json()
        assert "access" in data


@pytest.mark.django_db
class TestLoginOnTenantSubdomain:
    """When request.tenant is set, login enforces an active TenantMembership."""

    def test_login_succeeds_for_active_member(self, client, tenant_acme, member_user, member_in_acme):
        # Simulate the request hitting acme.vyntia.pe
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "maria", "password": "testpass123"},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 200
        data = response.json().get("data") or response.json()
        assert "access" in data

    def test_login_blocked_for_user_without_membership(self, client, tenant_acme, member_user):
        # member_user exists globally but has NO membership in acme
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "maria", "password": "testpass123"},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 403

    def test_login_blocked_for_invited_but_not_active_membership(
        self, client, tenant_acme, member_user
    ):
        # User has invited (not active) membership
        TenantMembership.objects.create(
            tenant=tenant_acme, user=member_user, role="member", status="invited"
        )
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "maria", "password": "testpass123"},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 403

    def test_login_token_contains_tenant_claims(
        self, client, tenant_acme, member_user, member_in_acme
    ):
        """The access token returned by login on a tenant subdomain has tenant_id claim."""
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "maria", "password": "testpass123"},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 200
        data = response.json().get("data") or response.json()
        access = data["access"]

        # Decode the token to check claims (without verification, just for inspection)
        import jwt as pyjwt
        payload = pyjwt.decode(access, options={"verify_signature": False})
        assert payload["tenant_id"] == str(tenant_acme.id)
        assert payload["tenant_slug"] == "acme"
        assert payload["membership_role"] == "admin"
```

- [ ] **Step 2.2: Run — should fail**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_login_tenant_aware.py -v 2>&1 | tail -15
```

Expected: 4 tests fail (login doesn't yet enforce membership).

- [ ] **Step 2.3: Update `LoginSerializer.validate` in `apps/api/api/v1/auth/serializers.py`**

Find the `LoginSerializer` class (around line 240). Inside its `validate(self, attrs)` method, after the existing `authenticate()` + `is_active` checks, add a tenant membership check just before `return attrs`:

```python
        # ---- C.4: enforce TenantMembership when request.tenant is set ----
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request is not None else None
        if tenant is not None:
            from apps.tenancy.models import TenantMembership

            has_membership = TenantMembership.objects.filter(
                tenant=tenant, user=user, status="active"
            ).exists()
            if not has_membership:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    detail=f"No active membership in workspace '{tenant.slug}'."
                )
        # When tenant is None (testserver, admin.vyntia.pe), legacy behavior is preserved.

        return attrs
```

If `LoginSerializer` does not currently take `request` from `context`, ensure the parent view passes it. The standard DRF `serializer_class.context['request']` is auto-populated when `get_serializer(...)` is called from a view; verify by reading the surrounding code.

If `LoginSerializer` is a different class than `CustomTokenObtainPairSerializer`, locate the actual login validate method (it's the one called by `LoginAPIView.post()`). It may be that `CustomTokenObtainPairSerializer.validate()` is the entry point — in that case, add the membership check there, after the parent `super().validate(attrs)` call but before returning the response dict.

The code should match the existing serializer's structure. Read the existing class first before deciding where to insert.

- [ ] **Step 2.4: Run failing tests — should pass now**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_login_tenant_aware.py -v 2>&1 | tail -15
```

Expected: 5 tests passed.

- [ ] **Step 2.5: Run full suite — verify no regression in existing 31 auth tests**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥217 passed. Existing tests use `testserver` host → request.tenant is None → membership check skipped → backward-compat preserved.

- [ ] **Step 2.6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/auth/serializers.py apps/api/apps/tenancy/tests/test_login_tenant_aware.py
git commit -m "feat(C4): login enforces active TenantMembership when on a tenant subdomain"
```

---

## Task 3: Activation endpoint

**Files:**
- Create: `apps/api/apps/tenancy/auth/__init__.py`
- Create: `apps/api/apps/tenancy/auth/activation.py` (helper logic)
- Modify: `apps/api/api/v1/auth/views.py` (add `ActivateAPIView`)
- Modify: `apps/api/api/v1/auth/serializers.py` (add `ActivateSerializer`)
- Modify: `apps/api/api/v1/auth/urls.py` (add `path('activate/', ...)`)
- Create: `apps/api/apps/tenancy/tests/test_activation_endpoint.py`

- [ ] **Step 3.1: Create activation helpers**

Create `apps/api/apps/tenancy/auth/__init__.py` (empty file).

Create `apps/api/apps/tenancy/auth/activation.py`:

```python
"""Helpers for accepting a TenantInvitation and activating a user."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.tenancy.models import TenantInvitation, TenantMembership


class InvalidInvitationToken(Exception):
    """Raised when an invitation token is invalid, expired, or already accepted."""


@transaction.atomic
def accept_invitation(*, token: str, name: str, password: str):
    """Validate the token and create/link the user + membership.

    Returns the (user, membership) tuple.
    Raises InvalidInvitationToken on any failure.
    """
    User = get_user_model()
    now = timezone.now()

    try:
        invitation = (
            TenantInvitation.objects.select_related("tenant")
            .get(token=token, accepted_at__isnull=True, expires_at__gt=now)
        )
    except TenantInvitation.DoesNotExist:
        raise InvalidInvitationToken("Invitation token is invalid, expired, or already used.")

    user, created = User.objects.get_or_create(
        email__iexact=invitation.email,
        defaults={
            "username": invitation.email.split("@")[0],
            "email": invitation.email,
            "is_active": True,
        },
    )
    if created or not user.has_usable_password():
        user.set_password(password)
    user.save(update_fields=["password"])

    # Create the membership (idempotent — get_or_create avoids dupes if user retries)
    membership, _ = TenantMembership.objects.get_or_create(
        tenant=invitation.tenant,
        user=user,
        defaults={
            "role": invitation.role,
            "status": "active",
            "joined_at": now,
        },
    )
    if membership.status != "active":
        membership.status = "active"
        membership.joined_at = membership.joined_at or now
        membership.save(update_fields=["status", "joined_at"])

    invitation.accepted_at = now
    invitation.save(update_fields=["accepted_at"])

    return user, membership
```

- [ ] **Step 3.2: Add `ActivateSerializer` to `apps/api/api/v1/auth/serializers.py`**

At the end of the file:

```python
class ActivateSerializer(serializers.Serializer):
    """Validates the activation request payload."""

    token = serializers.CharField(required=True)
    name = serializers.CharField(required=True, max_length=200)
    password = serializers.CharField(required=True, min_length=8, write_only=True)
```

- [ ] **Step 3.3: Add `ActivateAPIView` to `apps/api/api/v1/auth/views.py`**

At the end of the file:

```python
class ActivateAPIView(APIView):
    """Accepts a TenantInvitation token and activates the user account.

    POST /api/v1/auth/activate/
    Body: { token, name, password }

    On success: creates User + active TenantMembership + invalidates the invitation,
    then issues a session JWT (with tenant claims).
    """

    permission_classes = []
    authentication_classes = []  # Public endpoint — anyone with the token can activate

    def post(self, request):
        from api.v1.auth.serializers import ActivateSerializer, CustomTokenObtainPairSerializer
        from apps.core.responses import APIResponse
        from apps.tenancy.auth.activation import (
            InvalidInvitationToken,
            accept_invitation,
        )
        from apps.tenancy.context import tenant_context

        serializer = ActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            user, membership = accept_invitation(
                token=validated["token"],
                name=validated["name"],
                password=validated["password"],
            )
        except InvalidInvitationToken as exc:
            return APIResponse.error(message=str(exc), status_code=400)

        # Issue a JWT in the membership's tenant context (so claims are populated)
        with tenant_context(membership.tenant):
            token = CustomTokenObtainPairSerializer.get_token(user)
            access = str(token.access_token)
            refresh = str(token)

        return APIResponse.success(
            data={
                "access": access,
                "refresh": refresh,
                "tenant": {
                    "slug": membership.tenant.slug,
                    "name": membership.tenant.name,
                },
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                },
                "role": membership.role,
            },
            message="Activación exitosa.",
        )
```

- [ ] **Step 3.4: Wire URL in `apps/api/api/v1/auth/urls.py`**

Find the `urlpatterns` list and add (after the `login/` line):

```python
    path("activate/", ActivateAPIView.as_view(), name="activate"),
```

Also add `ActivateAPIView` to the imports at the top of the file.

- [ ] **Step 3.5: Write tests**

Create `apps/api/apps/tenancy/tests/test_activation_endpoint.py`:

```python
"""Tests for the POST /api/v1/auth/activate/ endpoint."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.tenancy.models import Tenant, TenantInvitation, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant_acme(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20123456789",
        plan="starter", status="trial", created_by=staff_user,
    )


@pytest.fixture
def fresh_invitation(tenant_acme, staff_user):
    return TenantInvitation.objects.create(
        tenant=tenant_acme,
        email="ceo@acme.com",
        token="signed.invite.token.abc",
        role="owner",
        expires_at=timezone.now() + timedelta(days=7),
        created_by=staff_user,
    )


@pytest.fixture
def expired_invitation(tenant_acme, staff_user):
    return TenantInvitation.objects.create(
        tenant=tenant_acme,
        email="late@acme.com",
        token="expired.invite.token",
        role="member",
        expires_at=timezone.now() - timedelta(hours=1),
        created_by=staff_user,
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
class TestActivateEndpoint:
    def test_activates_new_user_and_creates_membership(
        self, client, fresh_invitation, tenant_acme, django_user_model
    ):
        response = client.post(
            "/api/v1/auth/activate/",
            {
                "token": fresh_invitation.token,
                "name": "CEO of Acme",
                "password": "verysecurepass123",
            },
            format="json",
        )
        assert response.status_code == 200
        body = response.json()["data"]
        assert "access" in body
        assert body["tenant"]["slug"] == "acme"
        assert body["role"] == "owner"

        # User created
        user = django_user_model.objects.get(email__iexact="ceo@acme.com")
        assert user.is_active

        # Membership created and active
        m = TenantMembership.objects.get(tenant=tenant_acme, user=user)
        assert m.status == "active"
        assert m.joined_at is not None

        # Invitation marked accepted
        fresh_invitation.refresh_from_db()
        assert fresh_invitation.accepted_at is not None

    def test_invalid_token_returns_400(self, client):
        response = client.post(
            "/api/v1/auth/activate/",
            {"token": "nope", "name": "X", "password": "pass12345"},
            format="json",
        )
        assert response.status_code == 400

    def test_expired_token_returns_400(self, client, expired_invitation):
        response = client.post(
            "/api/v1/auth/activate/",
            {
                "token": expired_invitation.token,
                "name": "X",
                "password": "pass12345",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_already_accepted_invitation_returns_400(
        self, client, fresh_invitation
    ):
        # Accept it once
        client.post(
            "/api/v1/auth/activate/",
            {
                "token": fresh_invitation.token,
                "name": "First",
                "password": "pass12345",
            },
            format="json",
        )
        # Try to accept again
        response = client.post(
            "/api/v1/auth/activate/",
            {
                "token": fresh_invitation.token,
                "name": "Second",
                "password": "pass12345",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_short_password_rejected(self, client, fresh_invitation):
        response = client.post(
            "/api/v1/auth/activate/",
            {"token": fresh_invitation.token, "name": "X", "password": "short"},
            format="json",
        )
        assert response.status_code == 400  # serializer min_length=8
```

- [ ] **Step 3.6: Run tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_activation_endpoint.py -v 2>&1 | tail -15
```

Expected: 5 tests passed.

- [ ] **Step 3.7: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥222 passed.

- [ ] **Step 3.8: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/auth/ \
        apps/api/api/v1/auth/views.py \
        apps/api/api/v1/auth/serializers.py \
        apps/api/api/v1/auth/urls.py \
        apps/api/apps/tenancy/tests/test_activation_endpoint.py
git commit -m "feat(C4): POST /api/v1/auth/activate/ accepts TenantInvitation, creates User + membership, issues JWT"
```

---

## Task 4: Workspaces listing endpoint

**Files:**
- Create: `apps/api/api/v1/workspaces/__init__.py`
- Create: `apps/api/api/v1/workspaces/views.py`
- Create: `apps/api/api/v1/workspaces/serializers.py`
- Create: `apps/api/api/v1/workspaces/urls.py`
- Modify: `apps/api/api/urls.py` (or `vyntia/urls.py` — wherever the v1 router is) — wire `/api/v1/workspaces/`
- Create: `apps/api/apps/tenancy/tests/test_workspaces_endpoint.py`

- [ ] **Step 4.1: Create the workspaces sub-package**

`apps/api/api/v1/workspaces/__init__.py` (empty)

`apps/api/api/v1/workspaces/serializers.py`:

```python
from rest_framework import serializers


class WorkspaceSerializer(serializers.Serializer):
    """Compact tenant + role pair for the workspace switcher."""

    tenant_id = serializers.UUIDField()
    slug = serializers.CharField()
    name = serializers.CharField()
    plan = serializers.CharField()
    role = serializers.CharField()
```

`apps/api/api/v1/workspaces/views.py`:

```python
"""Workspaces endpoints — used by app.vyntia.pe.

GET /api/v1/workspaces/                       — list user's tenants
POST /api/v1/workspaces/<slug>/exchange/      — issue cross-subdomain token (Task 5)
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.responses import APIResponse


class WorkspacesListView(APIView):
    """List the active tenants the authenticated user is a member of.

    Cross-tenant by design — uses UnsafeManager since the request has no
    tenant context (typically hit on app.vyntia.pe).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.tenancy.models import TenantMembership

        memberships = (
            TenantMembership.objects.filter(user=request.user, status="active")
            .select_related("tenant")
            .order_by("tenant__name")
        )
        data = [
            {
                "tenant_id": str(m.tenant_id),
                "slug": m.tenant.slug,
                "name": m.tenant.name,
                "plan": m.tenant.plan,
                "role": m.role,
            }
            for m in memberships
        ]
        return APIResponse.success(data=data, message="Workspaces obtenidos.")
```

`apps/api/api/v1/workspaces/urls.py`:

```python
from django.urls import path

from api.v1.workspaces.views import WorkspacesListView

app_name = "workspaces"

urlpatterns = [
    path("", WorkspacesListView.as_view(), name="list"),
    # /<slug>/exchange/ added in Task 5
]
```

- [ ] **Step 4.2: Wire `/api/v1/workspaces/` in the main URL router**

Find the file that includes `api/v1/` namespaces. Likely `apps/api/api/urls.py` or `apps/api/api/v1/urls.py`. Look for an existing line like:

```python
path("auth/", include("api.v1.auth.urls")),
```

Add a sibling line:

```python
path("workspaces/", include("api.v1.workspaces.urls")),
```

- [ ] **Step 4.3: Write tests**

Create `apps/api/apps/tenancy/tests/test_workspaces_endpoint.py`:

```python
"""Tests for the GET /api/v1/workspaces/ endpoint."""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenancy.models import Tenant, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def member_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="x"
    )


@pytest.fixture
def tenant_alpha(staff_user):
    return Tenant.objects.create(
        slug="alpha", name="Alpha Inc", ruc="20111111111",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def tenant_beta(staff_user):
    return Tenant.objects.create(
        slug="beta", name="Beta LLC", ruc="20222222222",
        plan="pro", status="active", created_by=staff_user,
    )


@pytest.fixture
def member_in_alpha(tenant_alpha, member_user):
    return TenantMembership.objects.create(
        tenant=tenant_alpha, user=member_user, role="admin", status="active"
    )


@pytest.fixture
def member_in_beta(tenant_beta, member_user):
    return TenantMembership.objects.create(
        tenant=tenant_beta, user=member_user, role="member", status="active"
    )


@pytest.fixture
def client():
    return APIClient()


def auth_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db
class TestWorkspacesList:
    def test_authenticated_user_sees_their_workspaces(
        self, client, member_user, member_in_alpha, member_in_beta
    ):
        token = auth_token(member_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/api/v1/workspaces/")
        assert response.status_code == 200
        data = response.json()["data"]
        slugs = sorted(w["slug"] for w in data)
        assert slugs == ["alpha", "beta"]

    def test_returns_role_per_workspace(
        self, client, member_user, member_in_alpha, member_in_beta
    ):
        token = auth_token(member_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/api/v1/workspaces/")
        data = response.json()["data"]
        roles_by_slug = {w["slug"]: w["role"] for w in data}
        assert roles_by_slug["alpha"] == "admin"
        assert roles_by_slug["beta"] == "member"

    def test_empty_for_user_with_no_memberships(self, client, member_user):
        token = auth_token(member_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/api/v1/workspaces/")
        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_unauthenticated_returns_401(self, client):
        response = client.get("/api/v1/workspaces/")
        assert response.status_code == 401

    def test_excludes_invited_only_memberships(
        self, client, member_user, tenant_alpha
    ):
        TenantMembership.objects.create(
            tenant=tenant_alpha, user=member_user, role="member", status="invited"
        )
        token = auth_token(member_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/api/v1/workspaces/")
        assert response.json()["data"] == []
```

- [ ] **Step 4.4: Run tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_workspaces_endpoint.py -v 2>&1 | tail -15
```

Expected: 5 tests passed.

- [ ] **Step 4.5: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥227 passed.

- [ ] **Step 4.6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/workspaces/ \
        apps/api/api/urls.py \
        apps/api/apps/tenancy/tests/test_workspaces_endpoint.py
git commit -m "feat(C4): GET /api/v1/workspaces/ lists user's active TenantMemberships"
```

(Adjust the `git add` for the URL file if the wiring is in `vyntia/urls.py` instead of `api/urls.py`.)

---

## Task 5: Workspace exchange flow (cross-subdomain auth)

**Files:**
- Create: `apps/api/apps/tenancy/auth/exchange_token.py` (sign + verify helpers)
- Modify: `apps/api/api/v1/workspaces/views.py` (add `WorkspaceExchangeView`)
- Modify: `apps/api/api/v1/workspaces/urls.py` (wire `<slug>/exchange/`)
- Modify: `apps/api/api/v1/auth/views.py` (add `AuthExchangeAPIView`)
- Modify: `apps/api/api/v1/auth/serializers.py` (add `AuthExchangeSerializer`)
- Modify: `apps/api/api/v1/auth/urls.py` (wire `exchange/`)
- Create: `apps/api/apps/tenancy/tests/test_exchange_flow.py`

- [ ] **Step 5.1: Create `apps/api/apps/tenancy/auth/exchange_token.py`**

```python
"""Short-lived signed tokens for cross-subdomain workspace exchange.

The flow is:
1. User on app.vyntia.pe selects a workspace → backend issues exchange token (5 min)
2. Frontend redirects to <slug>.vyntia.pe/auth/exchange?token=<exchange_token>
3. <slug>.vyntia.pe consumes the token via POST /api/v1/auth/exchange/ and gets a session JWT

The token is a signed JWT (HMAC-SHA256, same SECRET_KEY) with claims:
- sub: user_id
- tenant_id: target tenant
- token_type: "exchange"
- exp: now + 5 minutes
"""

from datetime import timedelta
from uuid import UUID

import jwt
from django.conf import settings
from django.utils import timezone


EXCHANGE_TOKEN_TTL_SECONDS = 5 * 60  # 5 minutes


class InvalidExchangeToken(Exception):
    """Raised when an exchange token is invalid, expired, or for the wrong tenant."""


def issue_exchange_token(*, user_id: UUID, tenant_id: UUID) -> str:
    """Mint a short-lived exchange token for a (user, tenant) pair."""
    now = timezone.now()
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "token_type": "exchange",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=EXCHANGE_TOKEN_TTL_SECONDS)).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_exchange_token(token: str, *, expected_tenant_id: UUID) -> UUID:
    """Validate an exchange token. Returns the user_id on success.

    Raises InvalidExchangeToken on signature/expiry/tenant mismatch.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise InvalidExchangeToken("Exchange token has expired.")
    except jwt.InvalidTokenError as exc:
        raise InvalidExchangeToken(f"Invalid exchange token: {exc}")

    if payload.get("token_type") != "exchange":
        raise InvalidExchangeToken("Token is not an exchange token.")
    if str(payload.get("tenant_id")) != str(expected_tenant_id):
        raise InvalidExchangeToken("Token tenant_id does not match target workspace.")

    return UUID(payload["sub"])
```

- [ ] **Step 5.2: Add `WorkspaceExchangeView` to `apps/api/api/v1/workspaces/views.py`**

Append after `WorkspacesListView`:

```python
class WorkspaceExchangeView(APIView):
    """Issue a short-lived exchange token for a cross-subdomain redirect.

    POST /api/v1/workspaces/<slug>/exchange/

    The user must have an active membership in <slug>. Returns a token to be
    forwarded to <slug>.vyntia.pe/auth/exchange?token=<token>.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        from apps.tenancy.auth.exchange_token import issue_exchange_token
        from apps.tenancy.models import Tenant, TenantMembership

        try:
            tenant = Tenant.objects.get(slug=slug, status__in=["trial", "active"])
        except Tenant.DoesNotExist:
            return APIResponse.error(message="Workspace no encontrado.", status_code=404)

        has_membership = TenantMembership.objects.filter(
            tenant=tenant, user=request.user, status="active"
        ).exists()
        if not has_membership:
            return APIResponse.error(
                message="No tienes membresía activa en este workspace.",
                status_code=403,
            )

        token = issue_exchange_token(user_id=request.user.id, tenant_id=tenant.id)
        return APIResponse.success(
            data={
                "exchange_token": token,
                "redirect_url": f"https://{slug}.vyntia.pe/auth/exchange?token={token}",
            },
            message="Token de intercambio emitido.",
        )
```

- [ ] **Step 5.3: Wire `<slug>/exchange/` in `apps/api/api/v1/workspaces/urls.py`**

Update urlpatterns:

```python
urlpatterns = [
    path("", WorkspacesListView.as_view(), name="list"),
    path("<slug:slug>/exchange/", WorkspaceExchangeView.as_view(), name="exchange"),
]
```

Also update the imports at the top.

- [ ] **Step 5.4: Add `AuthExchangeSerializer` to `apps/api/api/v1/auth/serializers.py`**

```python
class AuthExchangeSerializer(serializers.Serializer):
    """Validates the auth/exchange request payload."""

    exchange_token = serializers.CharField(required=True)
```

- [ ] **Step 5.5: Add `AuthExchangeAPIView` to `apps/api/api/v1/auth/views.py`**

```python
class AuthExchangeAPIView(APIView):
    """Consume an exchange token issued by app.vyntia.pe and mint a session JWT.

    POST /api/v1/auth/exchange/
    Body: { exchange_token }

    The current request must be on the target tenant's subdomain (request.tenant
    is set by TenantMiddleware). The exchange token's tenant_id claim must match
    request.tenant.id.
    """

    permission_classes = []
    authentication_classes = []  # Public — exchange token is the auth

    def post(self, request):
        from api.v1.auth.serializers import (
            AuthExchangeSerializer,
            CustomTokenObtainPairSerializer,
        )
        from apps.core.responses import APIResponse
        from apps.tenancy.auth.exchange_token import (
            InvalidExchangeToken,
            verify_exchange_token,
        )
        from apps.tenancy.context import tenant_context
        from django.contrib.auth import get_user_model

        if not getattr(request, "tenant", None):
            return APIResponse.error(
                message="Exchange must be invoked on a tenant subdomain.",
                status_code=400,
            )

        serializer = AuthExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exchange_token = serializer.validated_data["exchange_token"]

        try:
            user_id = verify_exchange_token(
                exchange_token, expected_tenant_id=request.tenant.id
            )
        except InvalidExchangeToken as exc:
            return APIResponse.error(message=str(exc), status_code=400)

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return APIResponse.error(message="User not found.", status_code=400)

        # Issue a normal session JWT in this tenant's context
        with tenant_context(request.tenant):
            token = CustomTokenObtainPairSerializer.get_token(user)
            access = str(token.access_token)
            refresh = str(token)

        return APIResponse.success(
            data={
                "access": access,
                "refresh": refresh,
                "tenant": {
                    "slug": request.tenant.slug,
                    "name": request.tenant.name,
                },
                "user": {"id": str(user.id), "email": user.email},
            },
            message="Sesión iniciada.",
        )
```

- [ ] **Step 5.6: Wire `exchange/` in `apps/api/api/v1/auth/urls.py`**

Add (after `activate/`):

```python
    path("exchange/", AuthExchangeAPIView.as_view(), name="exchange"),
```

- [ ] **Step 5.7: Write tests**

Create `apps/api/apps/tenancy/tests/test_exchange_flow.py`:

```python
"""Tests for the cross-subdomain exchange flow."""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenancy.auth.exchange_token import issue_exchange_token
from apps.tenancy.models import Tenant, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant_acme(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20123456789",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def tenant_beta(staff_user):
    return Tenant.objects.create(
        slug="beta", name="Beta", ruc="20222222222",
        plan="pro", status="active", created_by=staff_user,
    )


@pytest.fixture
def member_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="testpass123"
    )


@pytest.fixture
def member_in_acme(tenant_acme, member_user):
    return TenantMembership.objects.create(
        tenant=tenant_acme, user=member_user, role="admin", status="active"
    )


@pytest.fixture
def client():
    return APIClient()


def auth(user):
    return f"Bearer {RefreshToken.for_user(user).access_token}"


@pytest.mark.django_db
class TestWorkspaceExchangeIssue:
    def test_issues_token_for_member(self, client, member_user, member_in_acme):
        client.credentials(HTTP_AUTHORIZATION=auth(member_user))
        response = client.post("/api/v1/workspaces/acme/exchange/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "exchange_token" in data
        assert "acme.vyntia.pe" in data["redirect_url"]

    def test_403_for_non_member(self, client, member_user, tenant_acme):
        # member_user has no membership in acme
        client.credentials(HTTP_AUTHORIZATION=auth(member_user))
        response = client.post("/api/v1/workspaces/acme/exchange/")
        assert response.status_code == 403

    def test_404_for_unknown_workspace(self, client, member_user):
        client.credentials(HTTP_AUTHORIZATION=auth(member_user))
        response = client.post("/api/v1/workspaces/ghost/exchange/")
        assert response.status_code == 404

    def test_401_when_unauthenticated(self, client):
        response = client.post("/api/v1/workspaces/acme/exchange/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestAuthExchangeConsume:
    def test_consumes_valid_token(
        self, client, tenant_acme, member_user, member_in_acme
    ):
        token = issue_exchange_token(user_id=member_user.id, tenant_id=tenant_acme.id)
        response = client.post(
            "/api/v1/auth/exchange/",
            {"exchange_token": token},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "access" in data
        assert data["tenant"]["slug"] == "acme"

    def test_rejects_token_for_wrong_tenant(
        self, client, tenant_acme, tenant_beta, member_user
    ):
        # Token issued for acme, but consumed at beta
        token = issue_exchange_token(user_id=member_user.id, tenant_id=tenant_acme.id)
        response = client.post(
            "/api/v1/auth/exchange/",
            {"exchange_token": token},
            format="json",
            HTTP_HOST="beta.vyntia.pe",
        )
        assert response.status_code == 400

    def test_rejects_when_not_on_tenant_subdomain(
        self, client, tenant_acme, member_user
    ):
        token = issue_exchange_token(user_id=member_user.id, tenant_id=tenant_acme.id)
        response = client.post(
            "/api/v1/auth/exchange/",
            {"exchange_token": token},
            format="json",
            # No HTTP_HOST → defaults to testserver → no tenant
        )
        assert response.status_code == 400

    def test_rejects_garbage_token(self, client, tenant_acme):
        response = client.post(
            "/api/v1/auth/exchange/",
            {"exchange_token": "not.a.valid.jwt"},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 400
```

- [ ] **Step 5.8: Run tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_exchange_flow.py -v 2>&1 | tail -15
```

Expected: 8 tests passed.

- [ ] **Step 5.9: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥235 passed.

- [ ] **Step 5.10: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/auth/exchange_token.py \
        apps/api/api/v1/workspaces/views.py \
        apps/api/api/v1/workspaces/urls.py \
        apps/api/api/v1/auth/views.py \
        apps/api/api/v1/auth/serializers.py \
        apps/api/api/v1/auth/urls.py \
        apps/api/apps/tenancy/tests/test_exchange_flow.py
git commit -m "feat(C4): cross-subdomain workspace exchange (issue + consume short-lived token)"
```

---

## Task 6: Final verification + merge

- [ ] **Step 6.1: Full pytest baseline**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development 2>&1 | tail -2
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations --dry-run --check --settings=vyntia.settings.development 2>&1 | tail -2
```

Expected: ≥235 passed, check clean, no pending migrations.

- [ ] **Step 6.2: Frontend baseline (sanity)**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
```

Expected: build exit 0.

- [ ] **Step 6.3: Update master roadmap**

In `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`, find the C.4 row and update the "Detailed plan" cell to:

```
`2026-05-09-vyntia-C4-auth-tenant-aware.md` ✅ merged 2026-05-09
```

- [ ] **Step 6.4: Commit roadmap update**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md
git commit -m "docs(C4): mark C.4 done in master roadmap"
```

- [ ] **Step 6.5: Merge to master**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/C4-auth-tenant-aware \
  -m "Merge C.4: tenant-aware auth (login membership + activate + workspaces + exchange)"
```

---

## Self-Review

### Spec coverage check

| Spec § requirement | Covered by task |
|---|---|
| JWT claims: `tenant_id`, `tenant_slug`, `membership_role` | Task 1 |
| Login enforces TenantMembership lookup | Task 2 |
| Activation endpoint POST /auth/activate/ | Task 3 |
| TenantInvitation token validation + consume | Task 3 (activation.py) |
| Workspace listing GET /workspaces/ | Task 4 |
| Cross-subdomain exchange flow | Task 5 |

### Spec deviations

1. **Frontend response shape unchanged** — The existing frontend (`authService.ts`) expects `data.access`, `data.refresh`, `data.user`, `data.roles`, `data.permissions`. We don't add tenant info to the response top-level (it's in JWT claims, decodable by frontend). Activation endpoint returns slightly different shape (with `tenant`, `role`) — that's OK because it's a NEW endpoint.

2. **Exchange token is signed JWT, not one-time DB record** — Spec § 6.4 says "one-time" but doesn't specify implementation. Using a 5-min signed JWT is simpler and stateless. True one-time semantics deferred to future hardening (would need a Redis-backed used-tokens set or a DB table with `consumed_at`).

3. **`testserver` host preserves legacy behavior** — Existing 31 auth tests use APIClient which defaults to `testserver` hostname. TenantMiddleware doesn't resolve a tenant for that host → `request.tenant` is None → membership check skipped. This is intentional; the spec's strict mode is opt-in.

4. **Username generation in activation** — When the activation creates a User from email, we use the email's local-part (before `@`) as username. If a clash exists (existing user with same username), this would fail. Spec doesn't specify; for MVP we accept this limitation. Future hardening: append a numeric suffix on collision.

### Placeholder scan

All code is complete and runnable. No TBDs.

### Type consistency

- `request.tenant` consistently typed as `Tenant | None` across views.
- `exchange_token` payload structure: `{sub, tenant_id, token_type, iat, exp}`. Verified consistent in `issue_exchange_token` and `verify_exchange_token`.
- `APIResponse.success` / `APIResponse.error` usage matches the existing pattern in the codebase.

### Out of scope (deferred)

- Frontend changes (C.6)
- Tenant admin API (C.5)
- Username collision handling (future hardening)
- True single-use exchange tokens (future hardening)
- Email sending for activation invitations (this is just an API; the email flow is set up by the admin who creates the invitation)
- Audit logging for activation/exchange (future hardening)

---

**Plan complete.** When executed, C.4 ships ~6 commits, ~10 new files (~700 LOC), 4 modified files, ~25 new tests. Tests baseline grows from 209 → ~235. Frontend untouched.
