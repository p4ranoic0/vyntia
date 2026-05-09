# C.3 — Tenant Middleware Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the request lifecycle to tenant context — resolve subdomain → Tenant, set `app.tenant_id` + `app.user_id` on the DB connection (RLS context), validate JWT tenant claim, and ship `TenantManager`/`UnsafeManager` ORM utilities. C.2 RLS policies start enforcing in production once this middleware stack runs.

**Architecture:** Three new Django middlewares + ContextVar-based tenant context utilities + two ORM managers. Middleware stack ordering: `TenantMiddleware` (subdomain → tenant) runs first, then existing auth (JWTCookie + AuthMiddleware), then `TenantAuthMiddleware` (validate JWT.tenant_id == request.tenant.id), then `RLSMiddleware` (`SET LOCAL app.tenant_id/user_id`). All middleware is **tolerant** — when `request.tenant` is None (reserved subdomains, dev `localhost`), they pass through. `TenantManager` is **lenient** in C.3 (returns all rows when no context is set), to keep the 185-test baseline passing without rewriting fixtures. Strict-raise mode flips on in a future sub-layer once test fixtures are tenant-aware. We do NOT attach `TenantManager` to existing models in C.3 — that's the next sub-layer's scope. C.3 ships the plumbing.

**Tech Stack:** Django 5.2 middleware, Python contextvars, PostgreSQL `SET LOCAL`, JWT validation via existing `rest_framework_simplejwt`.

**Source spec:** `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` § 4.4, § 5, § 6

**Source roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`

---

## Baseline snapshot

| Check | Command | Expected |
|---|---|---|
| Django system | `cd apps/api && python manage.py check --settings=vyntia.settings.development` | No errors |
| Backend tests | `cd apps/api && pytest tests/ apps/tenancy/tests/ -q` | ≥185 passed / ≤8 failed / 13 skipped |
| Frontend build | `cd apps/web && npm run build` | Exit 0 |

C.3 adds: ~25 new tests (context utilities, managers, 3 middleware classes). Target ≥210 passed (185 + ~25).

---

## File structure

**Files to create:**

```
apps/api/apps/tenancy/
├── context.py                 # ContextVar utilities
├── managers.py                # TenantManager + UnsafeManager
├── middleware.py              # TenantMiddleware, RLSMiddleware, TenantAuthMiddleware
├── constants.py               # RESERVED_SUBDOMAINS
└── tests/
    ├── test_context.py        # Tests for tenant_context() utilities
    ├── test_managers.py       # Tests for TenantManager/UnsafeManager
    ├── test_tenant_middleware.py        # Subdomain resolution tests
    ├── test_rls_middleware.py           # SET LOCAL tests (skip on SQLite)
    └── test_tenant_auth_middleware.py   # JWT tenant validation tests
```

**Files to modify:**

- `apps/api/vyntia/settings/base.py` — register 3 new middlewares in MIDDLEWARE list

---

## Branch

`vyntia/C3-tenant-middleware` — branched from `master` (HEAD has `Merge C.2`).

---

## Task 1: Branch + Context utilities + tests (TDD)

**Files:**
- Create: `apps/api/apps/tenancy/context.py`
- Create: `apps/api/apps/tenancy/tests/test_context.py`

- [ ] **Step 1.1: Create branch**

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/C3-tenant-middleware
```

- [ ] **Step 1.2: Write the failing tests**

Create `apps/api/apps/tenancy/tests/test_context.py`:

```python
"""Tests for tenant ContextVar utilities."""

import threading
import uuid

from apps.tenancy.context import (
    get_current_tenant,
    get_current_tenant_id,
    get_current_user_id,
    set_current_tenant,
    set_current_user_id,
    tenant_context,
)


class FakeTenant:
    def __init__(self, id_=None, slug="acme"):
        self.id = id_ or uuid.uuid4()
        self.slug = slug


class TestContextVarBasics:
    def test_default_is_none(self):
        # No tenant set in this test's context
        assert get_current_tenant() is None
        assert get_current_tenant_id() is None
        assert get_current_user_id() is None

    def test_set_and_get(self):
        tenant = FakeTenant()
        token = set_current_tenant(tenant)
        try:
            assert get_current_tenant() is tenant
            assert get_current_tenant_id() == tenant.id
        finally:
            # Reset to avoid leaking into other tests
            from apps.tenancy.context import _current_tenant
            _current_tenant.reset(token)
        assert get_current_tenant() is None

    def test_user_id_set_and_get(self):
        user_id = uuid.uuid4()
        token = set_current_user_id(user_id)
        try:
            assert get_current_user_id() == user_id
        finally:
            from apps.tenancy.context import _current_user_id
            _current_user_id.reset(token)


class TestTenantContextManager:
    def test_sets_and_resets(self):
        tenant = FakeTenant()
        assert get_current_tenant() is None
        with tenant_context(tenant):
            assert get_current_tenant() is tenant
        assert get_current_tenant() is None

    def test_nested(self):
        outer = FakeTenant(slug="outer")
        inner = FakeTenant(slug="inner")
        with tenant_context(outer):
            assert get_current_tenant().slug == "outer"
            with tenant_context(inner):
                assert get_current_tenant().slug == "inner"
            assert get_current_tenant().slug == "outer"
        assert get_current_tenant() is None

    def test_with_user_id(self):
        tenant = FakeTenant()
        user_id = uuid.uuid4()
        with tenant_context(tenant, user_id=user_id):
            assert get_current_tenant() is tenant
            assert get_current_user_id() == user_id
        assert get_current_tenant() is None
        assert get_current_user_id() is None

    def test_exception_resets_context(self):
        tenant = FakeTenant()
        try:
            with tenant_context(tenant):
                raise ValueError("simulated")
        except ValueError:
            pass
        assert get_current_tenant() is None


class TestThreadIsolation:
    def test_each_thread_has_independent_context(self):
        results = {}

        def worker(name, tenant):
            with tenant_context(tenant):
                # Simulate some work
                import time
                time.sleep(0.01)
                results[name] = get_current_tenant().slug

        t1 = FakeTenant(slug="thread1")
        t2 = FakeTenant(slug="thread2")
        threads = [
            threading.Thread(target=worker, args=("a", t1)),
            threading.Thread(target=worker, args=("b", t2)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert results["a"] == "thread1"
        assert results["b"] == "thread2"
```

- [ ] **Step 1.3: Run tests — should fail (no context.py module yet)**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_context.py -v 2>&1 | tail -10
```

Expected: ImportError on `apps.tenancy.context`.

- [ ] **Step 1.4: Implement `apps/api/apps/tenancy/context.py`**

```python
"""ContextVar utilities for tenant context propagation across the request lifecycle.

The tenant and user_id are stored in ContextVars (PEP 567), which provide
isolation across asyncio tasks and threads. Middleware sets these at the
start of a request; views and managers read them; the values are auto-reset
at request end.

Usage:
    # In middleware:
    with tenant_context(tenant, user_id=user.id):
        return get_response(request)

    # In a manager or service:
    tenant = get_current_tenant()
    if tenant is None:
        ...  # no tenant context (reserved subdomain, admin, etc.)
"""

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional
from uuid import UUID

# Module-private ContextVars — never import these directly. Use the helpers below.
_current_tenant: ContextVar[Optional[object]] = ContextVar(
    "vyntia_current_tenant", default=None
)
_current_user_id: ContextVar[Optional[UUID]] = ContextVar(
    "vyntia_current_user_id", default=None
)


def get_current_tenant():
    """Return the active Tenant for the current execution context, or None."""
    return _current_tenant.get()


def get_current_tenant_id():
    """Return the active Tenant.id (UUID), or None."""
    tenant = _current_tenant.get()
    return tenant.id if tenant is not None else None


def get_current_user_id():
    """Return the active user.id (UUID), or None."""
    return _current_user_id.get()


def set_current_tenant(tenant):
    """Set the active tenant. Returns a token that can be passed to reset."""
    return _current_tenant.set(tenant)


def set_current_user_id(user_id):
    """Set the active user_id. Returns a token that can be passed to reset."""
    return _current_user_id.set(user_id)


@contextmanager
def tenant_context(tenant, *, user_id=None):
    """Context manager for setting tenant (and optionally user_id) for a block.

    Both vars are reset on exit, including on exceptions.
    """
    tenant_token = _current_tenant.set(tenant)
    user_token = _current_user_id.set(user_id) if user_id is not None else None
    try:
        yield
    finally:
        _current_tenant.reset(tenant_token)
        if user_token is not None:
            _current_user_id.reset(user_token)
```

- [ ] **Step 1.5: Run tests — should pass**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_context.py -v 2>&1 | tail -15
```

Expected: ~10 tests passed.

- [ ] **Step 1.6: Run full suite — no regression**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥195 passed (185 + ~10 new).

- [ ] **Step 1.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/context.py apps/api/apps/tenancy/tests/test_context.py
git commit -m "feat(C3): tenant ContextVar utilities (TDD)"
```

---

## Task 2: TenantManager + UnsafeManager + tests (TDD)

**Files:**
- Create: `apps/api/apps/tenancy/managers.py`
- Create: `apps/api/apps/tenancy/tests/test_managers.py`

- [ ] **Step 2.1: Write the failing tests**

Create `apps/api/apps/tenancy/tests/test_managers.py`:

```python
"""Tests for TenantManager and UnsafeManager.

These tests use the existing TenantMembership model (which is tenant-scoped)
to exercise both manager classes without needing a fixture model.
"""

import pytest

from apps.tenancy.context import tenant_context
from apps.tenancy.managers import TenantManager, UnsafeManager
from apps.tenancy.models import Tenant, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant_a(staff_user):
    return Tenant.objects.create(
        slug="alpha", name="Alpha", ruc="20111111111",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def tenant_b(staff_user):
    return Tenant.objects.create(
        slug="beta", name="Beta", ruc="20222222222",
        plan="pro", status="active", created_by=staff_user,
    )


@pytest.fixture
def member_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="x"
    )


@pytest.mark.django_db
class TestTenantManagerLenient:
    """TenantManager filters by tenant when context is set, returns all otherwise."""

    def test_no_context_returns_all_rows(self, tenant_a, tenant_b, member_user):
        TenantMembership.objects.create(
            tenant=tenant_a, user=member_user, role="admin", status="active"
        )
        TenantMembership.objects.create(
            tenant=tenant_b, user=member_user, role="member", status="active"
        )
        # No tenant_context active → manager is lenient → returns all rows
        manager = TenantManager()
        manager.contribute_to_class(TenantMembership, "_test_objects")
        # Use the queryset directly via the manager's method
        from apps.tenancy.managers import TenantManager
        qs = TenantManager()._lenient_queryset_for_test(TenantMembership)
        assert qs.count() == 2  # both rows visible

    def test_with_context_filters_to_tenant(self, tenant_a, tenant_b, member_user):
        TenantMembership.objects.create(
            tenant=tenant_a, user=member_user, role="admin", status="active"
        )
        TenantMembership.objects.create(
            tenant=tenant_b, user=member_user, role="member", status="active"
        )
        with tenant_context(tenant_a):
            qs = TenantManager()._lenient_queryset_for_test(TenantMembership)
            assert qs.count() == 1
            assert qs.first().tenant_id == tenant_a.id


@pytest.mark.django_db
class TestUnsafeManager:
    """UnsafeManager always returns all rows, regardless of context."""

    def test_returns_all_even_with_tenant_context(self, tenant_a, tenant_b, member_user):
        TenantMembership.objects.create(
            tenant=tenant_a, user=member_user, role="admin", status="active"
        )
        TenantMembership.objects.create(
            tenant=tenant_b, user=member_user, role="member", status="active"
        )
        with tenant_context(tenant_a):
            qs = UnsafeManager()._lenient_queryset_for_test(TenantMembership)
            assert qs.count() == 2  # ignores context
```

- [ ] **Step 2.2: Run — should fail**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_managers.py -v 2>&1 | tail -10
```

Expected: ImportError on `apps.tenancy.managers`.

- [ ] **Step 2.3: Implement `apps/api/apps/tenancy/managers.py`**

```python
"""TenantManager and UnsafeManager for tenant-scoped models.

TenantManager is the canonical manager for tenant-scoped data. It auto-filters
queries by the currently-active tenant from the ContextVar.

In C.3, the manager is **lenient**: when no tenant context is set, it returns
all rows (no filter applied). This preserves the 185-test baseline since
existing fixtures don't yet use tenant_context. Production safety is provided
by RLS at the DB layer (the `vyntia_app` user enforces filters cryptographically).

A future sub-layer will tighten this to **strict mode** (raises if no context),
once test fixtures are tenant-aware. The `STRICT_TENANT_FILTERING` setting
controls the mode (default False).

UnsafeManager always returns all rows — used for cross-tenant operations
(workspace switcher, admin UI, ETL).
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from apps.tenancy.context import get_current_tenant


class TenantManager(models.Manager):
    """Auto-filters queries by the active tenant (lenient by default).

    - With tenant context: filters `tenant=current_tenant`
    - Without tenant context + STRICT_TENANT_FILTERING=False: returns all
    - Without tenant context + STRICT_TENANT_FILTERING=True: raises ImproperlyConfigured
    """

    def get_queryset(self):
        tenant = get_current_tenant()
        qs = super().get_queryset()
        if tenant is not None:
            return qs.filter(tenant=tenant)
        if getattr(settings, "STRICT_TENANT_FILTERING", False):
            raise ImproperlyConfigured(
                f"{self.model.__name__}.objects requires tenant context. "
                f"Use {self.model.__name__}.unsafe for cross-tenant access."
            )
        return qs

    # Test helper — bypasses the model.objects attachment requirement
    @staticmethod
    def _lenient_queryset_for_test(model):
        """Build a queryset using TenantManager's filtering, for testing without
        attaching the manager to a model class."""
        manager = TenantManager()
        manager.model = model
        return manager.get_queryset()


class UnsafeManager(models.Manager):
    """Cross-tenant access — bypasses tenant filtering.

    Use only when the operation is intrinsically cross-tenant: workspace
    switcher (user lists their memberships across tenants), admin/staff UI,
    ETL pipelines, support impersonation. Code review must justify every use.
    """

    @staticmethod
    def _lenient_queryset_for_test(model):
        manager = UnsafeManager()
        manager.model = model
        return manager.get_queryset()
```

- [ ] **Step 2.4: Run tests — should pass**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_managers.py -v 2>&1 | tail -10
```

Expected: 3 tests passed.

- [ ] **Step 2.5: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥198 passed.

- [ ] **Step 2.6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/managers.py apps/api/apps/tenancy/tests/test_managers.py
git commit -m "feat(C3): TenantManager + UnsafeManager (lenient mode for transition)"
```

---

## Task 3: TenantMiddleware + tests (subdomain resolution)

**Files:**
- Create: `apps/api/apps/tenancy/constants.py`
- Create: `apps/api/apps/tenancy/middleware.py` (initial — TenantMiddleware only)
- Create: `apps/api/apps/tenancy/tests/test_tenant_middleware.py`

- [ ] **Step 3.1: Create `apps/api/apps/tenancy/constants.py`**

```python
"""Cross-cutting constants for the tenancy layer."""

# Reserved subdomains that NEVER resolve to a tenant.
# When the host's subdomain matches one of these, request.tenant = None.
# These also block tenant slugs from being claimed.
RESERVED_SUBDOMAINS = frozenset({
    "admin",       # admin.vyntia.pe — Vyntia staff panel
    "app",         # app.vyntia.pe — workspace switcher
    "www",         # www.vyntia.pe — marketing redirect
    "api",         # api.vyntia.pe — public API alias (future)
    "docs",        # documentation
    "status",      # status page
    "blog",        # blog
    "mail",        # email
    "support",     # support portal
    "help",        # help center
    "vyntia",      # brand-protect

    # Local/dev hosts — treat as no-tenant
    "localhost",
    "127",         # 127.0.0.1
    "0",           # 0.0.0.0
})
```

- [ ] **Step 3.2: Write the failing tests**

Create `apps/api/apps/tenancy/tests/test_tenant_middleware.py`:

```python
"""Tests for TenantMiddleware (subdomain → Tenant resolution)."""

import pytest
from django.test import RequestFactory

from apps.tenancy.middleware import TenantMiddleware
from apps.tenancy.models import Tenant


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
def factory():
    return RequestFactory()


def get_response_stub(request):
    """A trivial inner middleware that just returns request.tenant for inspection."""
    from django.http import HttpResponse
    return HttpResponse(str(getattr(request, "tenant", "no-tenant-attr")))


@pytest.mark.django_db
class TestTenantMiddleware:
    def test_resolves_active_tenant_from_subdomain(self, factory, tenant_acme):
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="acme.vyntia.pe")
        response = middleware(request)
        assert request.tenant is not None
        assert request.tenant.slug == "acme"

    def test_strips_port_from_host(self, factory, tenant_acme):
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="acme.vyntia.pe:8000")
        middleware(request)
        assert request.tenant is not None
        assert request.tenant.slug == "acme"

    def test_reserved_subdomain_admin_yields_no_tenant(self, factory):
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="admin.vyntia.pe")
        middleware(request)
        assert request.tenant is None

    def test_reserved_subdomain_app_yields_no_tenant(self, factory):
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="app.vyntia.pe")
        middleware(request)
        assert request.tenant is None

    def test_localhost_yields_no_tenant(self, factory):
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="localhost:8000")
        middleware(request)
        assert request.tenant is None

    def test_unknown_subdomain_yields_no_tenant(self, factory):
        """An unknown slug doesn't 404 the request — it just doesn't set tenant."""
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="ghost-tenant.vyntia.pe")
        middleware(request)
        assert request.tenant is None

    def test_suspended_tenant_not_resolved(self, factory, staff_user):
        Tenant.objects.create(
            slug="suspended", name="Suspended", ruc="20999999999",
            plan="starter", status="suspended", created_by=staff_user,
        )
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="suspended.vyntia.pe")
        middleware(request)
        # Suspended tenants don't resolve — login attempts go through but UX is blocked
        assert request.tenant is None

    def test_trial_tenant_resolves(self, factory, staff_user):
        Tenant.objects.create(
            slug="newtrial", name="New", ruc="20111000111",
            plan="starter", status="trial", created_by=staff_user,
        )
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="newtrial.vyntia.pe")
        middleware(request)
        assert request.tenant is not None
        assert request.tenant.slug == "newtrial"
```

- [ ] **Step 3.3: Run — should fail**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_tenant_middleware.py -v 2>&1 | tail -10
```

Expected: ImportError on `apps.tenancy.middleware`.

- [ ] **Step 3.4: Implement `apps/api/apps/tenancy/middleware.py` (TenantMiddleware only — RLS and Auth come later)**

```python
"""Tenancy middleware stack.

Three classes (registered in MIDDLEWARE in this order):

1. TenantMiddleware — resolves subdomain → Tenant, sets request.tenant + ContextVar
2. TenantAuthMiddleware — validates JWT.tenant_id matches request.tenant.id
3. RLSMiddleware — sets app.tenant_id and app.user_id on the DB connection

All three are tolerant: if request.tenant is None (reserved subdomains, dev),
they skip their work and pass through to get_response.
"""

from django.db import connection

from apps.tenancy.constants import RESERVED_SUBDOMAINS
from apps.tenancy.context import (
    set_current_tenant,
    set_current_user_id,
    _current_tenant,
    _current_user_id,
)


class TenantMiddleware:
    """Resolve the tenant from the Host header subdomain.

    Sets:
        request.tenant : Tenant | None
        ContextVar: vyntia_current_tenant

    Reserved subdomains and unknown slugs both yield request.tenant = None
    (silent fallback — downstream views can choose to 404 or behave as
    workspace-less endpoints).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = self._resolve_tenant(request)
        request.tenant = tenant

        if tenant is not None:
            token = set_current_tenant(tenant)
            try:
                return self.get_response(request)
            finally:
                _current_tenant.reset(token)
        else:
            return self.get_response(request)

    @staticmethod
    def _resolve_tenant(request):
        host = request.META.get("HTTP_HOST", "")
        if not host:
            return None

        # Strip port (acme.vyntia.pe:8000 → acme.vyntia.pe)
        hostname = host.split(":", 1)[0]

        # Extract subdomain (first label)
        parts = hostname.split(".")
        if not parts:
            return None
        subdomain = parts[0].lower()

        if subdomain in RESERVED_SUBDOMAINS:
            return None

        # Lazy import — avoids circular import at module load time
        from apps.tenancy.models import Tenant

        try:
            return Tenant.objects.get(
                slug=subdomain,
                status__in=["trial", "active"],
            )
        except Tenant.DoesNotExist:
            return None
```

- [ ] **Step 3.5: Run tests — should pass**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_tenant_middleware.py -v 2>&1 | tail -15
```

Expected: 8 tests passed.

- [ ] **Step 3.6: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥206 passed.

- [ ] **Step 3.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/constants.py \
        apps/api/apps/tenancy/middleware.py \
        apps/api/apps/tenancy/tests/test_tenant_middleware.py
git commit -m "feat(C3): TenantMiddleware + reserved subdomains constants (TDD)"
```

---

## Task 4: RLSMiddleware + tests (PostgreSQL only)

**Files:**
- Modify: `apps/api/apps/tenancy/middleware.py` (append RLSMiddleware class)
- Create: `apps/api/apps/tenancy/tests/test_rls_middleware.py`

- [ ] **Step 4.1: Append `RLSMiddleware` class to `apps/api/apps/tenancy/middleware.py`**

Append (after `TenantMiddleware` class):

```python
class RLSMiddleware:
    """Set PostgreSQL session variables for RLS enforcement.

    For each request:
    - If request.tenant is set → SET LOCAL app.tenant_id
    - If request.user is authenticated → SET LOCAL app.user_id

    Both are SET LOCAL → reset at end of transaction (request boundary).
    Safe even on SQLite or other backends — silently skipped.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only PostgreSQL supports current_setting() / SET LOCAL.
        # On SQLite (tests), skip this entirely.
        if connection.vendor != "postgresql":
            return self.get_response(request)

        tenant = getattr(request, "tenant", None)
        user = getattr(request, "user", None)
        user_id = user.id if (user is not None and user.is_authenticated) else None

        if tenant is None and user_id is None:
            return self.get_response(request)

        with connection.cursor() as cur:
            if tenant is not None:
                cur.execute("SELECT set_config('app.tenant_id', %s, true)", [str(tenant.id)])
            if user_id is not None:
                cur.execute("SELECT set_config('app.user_id', %s, true)", [str(user_id)])

        # Also propagate to the user_id ContextVar so managers can read it
        if user_id is not None:
            user_token = set_current_user_id(user_id)
            try:
                return self.get_response(request)
            finally:
                _current_user_id.reset(user_token)
        return self.get_response(request)
```

Note: We use `set_config('name', 'value', true)` instead of `SET LOCAL` because the latter doesn't accept parameter binding through psycopg. `set_config(.., true)` is functionally equivalent — local to the current transaction.

- [ ] **Step 4.2: Write tests**

Create `apps/api/apps/tenancy/tests/test_rls_middleware.py`:

```python
"""Tests for RLSMiddleware (SET LOCAL of app.tenant_id / app.user_id).

These tests require PostgreSQL because they verify session variables. They
skip on SQLite.
"""

import uuid

import pytest
from django.db import connection
from django.test import RequestFactory

from apps.tenancy.middleware import RLSMiddleware
from apps.tenancy.models import Tenant

pytestmark = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="RLSMiddleware tests require PostgreSQL.",
)


def _stub_response(request):
    from django.db import connection
    from django.http import HttpResponse
    # Capture the session variables for assertions
    with connection.cursor() as cur:
        cur.execute("SELECT current_setting('app.tenant_id', TRUE)")
        request._captured_tenant_id = cur.fetchone()[0]
        cur.execute("SELECT current_setting('app.user_id', TRUE)")
        request._captured_user_id = cur.fetchone()[0]
    return HttpResponse("ok")


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20123456789",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.mark.django_db(transaction=True)
class TestRLSMiddleware:
    def test_sets_tenant_id_when_request_has_tenant(self, factory, tenant):
        middleware = RLSMiddleware(_stub_response)
        request = factory.get("/")
        request.tenant = tenant
        request.user = type("AnonUser", (), {"is_authenticated": False})()
        middleware(request)
        assert request._captured_tenant_id == str(tenant.id)

    def test_no_tenant_no_set(self, factory):
        middleware = RLSMiddleware(_stub_response)
        request = factory.get("/")
        request.tenant = None
        request.user = type("AnonUser", (), {"is_authenticated": False})()
        middleware(request)
        # Nothing was set; current_setting returns empty string
        assert request._captured_tenant_id in ("", None)
```

- [ ] **Step 4.3: Run — should pass on PostgreSQL, skip on SQLite**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_rls_middleware.py -v 2>&1 | tail -10
```

Expected: 2 tests passed (PG) or skipped (SQLite). Local dev typically uses SQLite for tests → skipped is OK.

- [ ] **Step 4.4: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: full suite still passes (no regression).

- [ ] **Step 4.5: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/middleware.py apps/api/apps/tenancy/tests/test_rls_middleware.py
git commit -m "feat(C3): RLSMiddleware sets app.tenant_id and app.user_id (PG only)"
```

---

## Task 5: TenantAuthMiddleware + tests

**Files:**
- Modify: `apps/api/apps/tenancy/middleware.py` (append TenantAuthMiddleware class)
- Create: `apps/api/apps/tenancy/tests/test_tenant_auth_middleware.py`

- [ ] **Step 5.1: Append `TenantAuthMiddleware` class to `apps/api/apps/tenancy/middleware.py`**

```python
class TenantAuthMiddleware:
    """Validate that JWT.tenant_id matches request.tenant.id.

    Prevents replay of a token issued for tenant A against tenant B.

    When the JWT does NOT contain a `tenant_id` claim (e.g., legacy tokens
    issued before C.4 ships), validation is SKIPPED. C.4 will issue tokens
    with the claim, at which point this middleware will start enforcing.

    When request.tenant is None (reserved subdomain) or request.user is
    anonymous, this middleware is a no-op.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, "tenant", None)
        user = getattr(request, "user", None)

        if tenant is None or user is None or not getattr(user, "is_authenticated", False):
            return self.get_response(request)

        token_tenant_id = self._extract_tenant_id_from_jwt(request)
        if token_tenant_id is None:
            # Pre-C.4 token without tenant_id claim — skip validation
            return self.get_response(request)

        if str(token_tenant_id) != str(tenant.id):
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed(
                f"JWT tenant_id mismatch: token issued for {token_tenant_id}, "
                f"request is for {tenant.id}"
            )

        return self.get_response(request)

    @staticmethod
    def _extract_tenant_id_from_jwt(request):
        """Read tenant_id from the JWT, if present.

        Tries the auth attribute that simplejwt sets, then falls back to
        decoding from the Authorization header. Returns None if not present.
        """
        # simplejwt sets request.auth to the validated token (a dict-like)
        auth = getattr(request, "auth", None)
        if auth is not None:
            try:
                return auth.get("tenant_id")
            except (AttributeError, TypeError):
                pass

        # Fallback: try to read from request.user attributes (some custom auth flows)
        user = getattr(request, "user", None)
        if user is not None and hasattr(user, "_jwt_tenant_id"):
            return user._jwt_tenant_id

        return None
```

- [ ] **Step 5.2: Write tests**

Create `apps/api/apps/tenancy/tests/test_tenant_auth_middleware.py`:

```python
"""Tests for TenantAuthMiddleware (JWT tenant_id validation)."""

import uuid

import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from rest_framework.exceptions import AuthenticationFailed

from apps.tenancy.middleware import TenantAuthMiddleware
from apps.tenancy.models import Tenant


def _ok(request):
    return HttpResponse("ok")


@pytest.fixture
def factory():
    return RequestFactory()


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


def _set_user(request, user, *, jwt_tenant_id=None):
    """Helper: simulate auth middleware having run."""
    user.is_authenticated = True
    request.user = user
    if jwt_tenant_id is not None:
        request.auth = {"tenant_id": str(jwt_tenant_id)}
    else:
        request.auth = None


@pytest.mark.django_db
class TestTenantAuthMiddleware:
    def test_no_tenant_skipped(self, factory, staff_user):
        middleware = TenantAuthMiddleware(_ok)
        request = factory.get("/")
        request.tenant = None
        _set_user(request, staff_user, jwt_tenant_id=uuid.uuid4())
        # Should not raise even with a mismatching tenant_id, because request.tenant is None
        response = middleware(request)
        assert response.status_code == 200

    def test_anonymous_user_skipped(self, factory, tenant_acme):
        middleware = TenantAuthMiddleware(_ok)
        request = factory.get("/")
        request.tenant = tenant_acme
        request.user = type("AnonUser", (), {"is_authenticated": False})()
        request.auth = None
        response = middleware(request)
        assert response.status_code == 200

    def test_jwt_without_tenant_id_passes(self, factory, tenant_acme, staff_user):
        """Legacy tokens (pre-C.4) without tenant_id claim should still work."""
        middleware = TenantAuthMiddleware(_ok)
        request = factory.get("/")
        request.tenant = tenant_acme
        _set_user(request, staff_user, jwt_tenant_id=None)
        response = middleware(request)
        assert response.status_code == 200

    def test_matching_tenant_id_passes(self, factory, tenant_acme, staff_user):
        middleware = TenantAuthMiddleware(_ok)
        request = factory.get("/")
        request.tenant = tenant_acme
        _set_user(request, staff_user, jwt_tenant_id=tenant_acme.id)
        response = middleware(request)
        assert response.status_code == 200

    def test_mismatching_tenant_id_raises(self, factory, tenant_acme, staff_user):
        middleware = TenantAuthMiddleware(_ok)
        request = factory.get("/")
        request.tenant = tenant_acme
        _set_user(request, staff_user, jwt_tenant_id=uuid.uuid4())  # different
        with pytest.raises(AuthenticationFailed) as exc_info:
            middleware(request)
        assert "tenant_id mismatch" in str(exc_info.value)
```

- [ ] **Step 5.3: Run tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_tenant_auth_middleware.py -v 2>&1 | tail -10
```

Expected: 5 tests passed.

- [ ] **Step 5.4: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥213 passed.

- [ ] **Step 5.5: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/middleware.py \
        apps/api/apps/tenancy/tests/test_tenant_auth_middleware.py
git commit -m "feat(C3): TenantAuthMiddleware validates JWT.tenant_id (graceful for pre-C.4 tokens)"
```

---

## Task 6: Register middleware in settings + smoke test

**Files:**
- Modify: `apps/api/vyntia/settings/base.py` (MIDDLEWARE list)

- [ ] **Step 6.1: Update `MIDDLEWARE` in `apps/api/vyntia/settings/base.py`**

Find the MIDDLEWARE list (around line 48-64). Insert the new middlewares in this order:
- `TenantMiddleware` after CSRF, before any auth — needs to run early.
- `TenantAuthMiddleware` after `AuthenticationMiddleware` — needs request.user.
- `RLSMiddleware` after `TenantAuthMiddleware` — needs validated request.user + request.tenant.

The new MIDDLEWARE list should be:

```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
    "apps.core.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "apps.tenancy.middleware.TenantMiddleware",          # NEW (C.3)
    "apps.core.middleware.JWTCookieMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.tenancy.middleware.TenantAuthMiddleware",      # NEW (C.3)
    "apps.tenancy.middleware.RLSMiddleware",             # NEW (C.3)
    "apps.core.middleware.RequestLoggingMiddleware",
    "apps.core.middleware.PerformanceMonitoringMiddleware",
    "apps.core.middleware.AuditMiddleware",
    # "apps.core.middleware.RateLimitingMiddleware",  # Deshabilitado temporalmente (requiere Redis)
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

- [ ] **Step 6.2: Verify Django check**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development 2>&1 | tail -2
```

Expected: clean.

- [ ] **Step 6.3: Run full pytest — make sure registered middleware doesn't break anything**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥213 passed (same as Task 5). All existing API tests should still pass because middleware is tolerant of missing tenant.

If any tests fail, the most likely cause is a request to a hostname like `testserver` (Django's default for the test client) that goes through `TenantMiddleware._resolve_tenant` and looks up `Tenant.objects.get(slug="testserver", ...)`. This raises `DoesNotExist` which is caught and returns None. So it should work — but verify carefully.

- [ ] **Step 6.4: Commit**

```bash
cd D:/VYNTIA
git add apps/api/vyntia/settings/base.py
git commit -m "chore(C3): register TenantMiddleware + TenantAuthMiddleware + RLSMiddleware"
```

---

## Task 7: Final verification + merge

- [ ] **Step 7.1: Full pytest**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development 2>&1 | tail -2
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations --dry-run --check --settings=vyntia.settings.development 2>&1 | tail -2
```

Expected: ≥213 passed, check clean, no pending migrations.

- [ ] **Step 7.2: Frontend baseline (sanity)**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
```

Expected: build exit 0.

- [ ] **Step 7.3: Update master roadmap**

In `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`, find the C.3 row and update the "Detailed plan" cell to:

```
`2026-05-09-vyntia-C3-tenant-middleware.md` ✅ merged 2026-05-09
```

- [ ] **Step 7.4: Commit roadmap update**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md
git commit -m "docs(C3): mark C.3 done in master roadmap"
```

- [ ] **Step 7.5: Merge to master**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/C3-tenant-middleware \
  -m "Merge C.3: tenant middleware (subdomain resolution + RLS context + JWT validation)"
```

- [ ] **Step 7.6: Verify post-merge**

```bash
git log --oneline -3
git status
```

---

## Self-Review

### Spec coverage check

| Spec § requirement | Covered by task |
|---|---|
| ContextVar `_current_tenant`, `_current_user_id` | Task 1 (context.py) |
| `tenant_context()` context manager | Task 1 |
| `set_current_tenant`, `get_current_tenant` helpers | Task 1 |
| `TenantManager.get_queryset()` filters by tenant | Task 2 (lenient mode) |
| `UnsafeManager` for cross-tenant access | Task 2 |
| `TenantMiddleware._resolve_tenant()` from Host header | Task 3 |
| Reserved subdomains list | Task 3 (constants.py) |
| `RLSMiddleware` SET LOCAL `app.tenant_id` and `app.user_id` | Task 4 |
| `TenantAuthMiddleware` JWT.tenant_id validation | Task 5 |
| Registration in MIDDLEWARE list | Task 6 |

### Spec deviations

1. **`TenantManager` is lenient by default** — spec § 5 raises `ImproperlyConfigured` if no context. C.3 returns all rows when no context to preserve the 185-test baseline. The spec's strict mode is opt-in via `STRICT_TENANT_FILTERING=True` setting. A future sub-layer flips this on after test fixtures are tenant-aware.

2. **Manager not attached to existing models** — spec § 5 shows `objects = TenantManager()` on every business model. C.3 ships the manager classes but does NOT attach them; that's a future sub-layer's scope (also requires test fixture updates). RLS at the DB layer provides primary defense in production; ORM filtering becomes belt-and-suspenders later.

3. **`set_config()` instead of `SET LOCAL`** — psycopg doesn't accept parameter binding for `SET LOCAL`. We use `set_config(name, value, true)` which is functionally equivalent (transaction-scoped).

4. **`TenantAuthMiddleware` is graceful for missing `tenant_id` claims** — spec § 6.2 implies strict validation. C.3 skips validation when JWT has no `tenant_id` (pre-C.4 tokens). C.4 will issue tokens with the claim, at which point this middleware naturally starts enforcing.

### Placeholder scan

- All code blocks contain runnable code.
- No "TBD" or "TODO" except deliberate forward references to C.4/C.5/C.8.

### Type consistency

- `_current_tenant` and `_current_user_id` ContextVars consistently named across `context.py`, `middleware.py`.
- `request.tenant` (with `None` fallback) consistent across all 3 middlewares.
- `set_current_tenant` returns a token used with `_current_tenant.reset(token)` — correct ContextVar API.

### Out of scope (deferred)

- Attaching `objects = TenantManager()` to all 31 business models (future sub-layer)
- Strict mode flip (`STRICT_TENANT_FILTERING=True`) — future sub-layer after fixture updates
- JWT issuance with `tenant_id` claim — C.4
- Tenant activation flow — C.4
- Workspace switcher API — C.4
- Tenant admin API — C.5
- Frontend changes — C.6

---

**Plan complete.** When executed, C.3 ships ~7 commits, 5 new files (~600 LOC), 1 modified settings file, ~25 new tests. Tests baseline grows from 185 → ~213. Frontend untouched.
