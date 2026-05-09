# C.5 — Admin API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `/api/admin/*` endpoints used by the Vyntia super-admin panel — tenant CRUD, lifecycle actions (suspend/cancel/re-invite), user search, and a SupportSession-audited impersonation flow. All endpoints gated behind a new `IsVyntiaStaff` permission backed by a `User.is_vyntia_staff` boolean.

**Architecture:** Single new namespace `apps/api/api/admin/` (sibling of `api/v1/`). Endpoints are intentionally NOT tenant-scoped — `request.tenant` is always None on `admin.vyntia.pe` (reserved subdomain in C.3), so the existing models' default Django manager returns all rows unfiltered. The `setup_tenant_seed()` helper in C.5 ships **minimal** — just creates `CompanyConfig` for the new tenant. HR-role/permission seeding is deferred (admin can run existing management commands per-tenant later). Impersonation issues a normal session JWT but with `impersonated_by` and `support_session_id` claims; `TenantAuthMiddleware` from C.3 doesn't differentiate (impersonated tokens behave like normal tokens until C.6 frontend shows the support banner).

**Tech Stack:** Django 5.2, DRF, existing `IsAuthenticated` + new `IsVyntiaStaff` permission.

**Source spec:** `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` § 7

**Source roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`

---

## Baseline snapshot

| Check | Command | Expected |
|---|---|---|
| Django system | `cd apps/api && python manage.py check --settings=vyntia.settings.development` | No errors |
| Backend tests | `cd apps/api && pytest tests/ apps/tenancy/tests/ -q` | ≥235 passed / ≤8 failed / 15 skipped |
| Frontend build | `cd apps/web && npm run build` | Exit 0 |

C.5 adds: ~30 new tests (User field + permission + CRUD + lifecycle + search + impersonation). Target ≥265 passed.

---

## File structure

**Files to create:**

```
apps/api/api/admin/
├── __init__.py
├── urls.py                       # /admin/tenants/ + /admin/users/ + /admin/support-sessions/
├── permissions.py                # IsVyntiaStaff
├── tenants/
│   ├── __init__.py
│   ├── views.py                  # TenantsListCreateView, TenantDetailView, lifecycle actions
│   ├── serializers.py            # TenantAdminSerializer, TenantCreateSerializer
│   └── urls.py
├── users/
│   ├── __init__.py
│   ├── views.py                  # UsersSearchView, ImpersonateView
│   ├── serializers.py
│   └── urls.py
└── support_sessions/
    ├── __init__.py
    ├── views.py                  # SupportSessionsListView
    ├── serializers.py
    └── urls.py

apps/api/apps/tenancy/admin_helpers/
├── __init__.py
├── seed.py                       # setup_tenant_seed()
└── impersonation.py              # issue_impersonation_token()

apps/api/apps/tenancy/tests/
├── test_admin_permission.py
├── test_admin_tenants_crud.py
├── test_admin_tenants_lifecycle.py
├── test_admin_users_search.py
├── test_admin_impersonation.py
└── test_setup_tenant_seed.py
```

**Files to modify:**

- `apps/api/apps/identity/models/user.py` — add `is_vyntia_staff = BooleanField(default=False, db_index=True)`
- `apps/api/apps/identity/migrations/` — new migration for the field
- `apps/api/api/urls.py` (or wherever the v1 namespace is wired) — add `path("admin/", include("api.admin.urls"))`

---

## Branch

`vyntia/C5-admin-api` — branched from `master` (HEAD has `Merge C.4`).

---

## Task 1: Branch + `is_vyntia_staff` field + `IsVyntiaStaff` permission

**Files:**
- Modify: `apps/api/apps/identity/models/user.py`
- Create: migration
- Create: `apps/api/api/admin/__init__.py`
- Create: `apps/api/api/admin/permissions.py`
- Create: `apps/api/apps/tenancy/tests/test_admin_permission.py`

- [ ] **Step 1.1: Create branch**

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/C5-admin-api
```

- [ ] **Step 1.2: Add `is_vyntia_staff` field to User**

In `apps/api/apps/identity/models/user.py`, find the `is_staff` line (around line 73) and add immediately after `is_superuser`:

```python
    # Vyntia internal staff — can access admin.vyntia.pe panel (C.5)
    is_vyntia_staff = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Vyntia employee with access to the super-admin panel.",
    )
```

- [ ] **Step 1.3: Make + apply migration**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations identity --settings=vyntia.settings.development 2>&1 | tail -5
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate identity --settings=vyntia.settings.development 2>&1 | tail -3
```

Expected: a new migration file is created (e.g., `0003_user_is_vyntia_staff.py`), applied cleanly.

- [ ] **Step 1.4: Create `apps/api/api/admin/__init__.py`**

Empty file.

- [ ] **Step 1.5: Create `apps/api/api/admin/permissions.py`**

```python
"""DRF permissions for the /api/admin/* namespace."""

from rest_framework.permissions import BasePermission


class IsVyntiaStaff(BasePermission):
    """Allow only authenticated users with `is_vyntia_staff=True`.

    Used by every endpoint under /api/admin/. Combine with IsAuthenticated
    (or rely on this class doing both checks: anonymous users never have
    is_vyntia_staff=True, so unauthenticated requests are rejected).
    """

    message = "Only Vyntia staff can access this endpoint."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return False
        return bool(getattr(user, "is_vyntia_staff", False))
```

- [ ] **Step 1.6: Write tests**

Create `apps/api/apps/tenancy/tests/test_admin_permission.py`:

```python
"""Tests for the IsVyntiaStaff permission class."""

import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient

from api.admin.permissions import IsVyntiaStaff


@pytest.fixture
def staff_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="zviera", email="zviera@vyntia.pe", password="x"
    )
    user.is_vyntia_staff = True
    user.save()
    return user


@pytest.fixture
def regular_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="x"
    )


@pytest.mark.django_db
class TestIsVyntiaStaffPermission:
    def test_anonymous_denied(self):
        permission = IsVyntiaStaff()
        request = RequestFactory().get("/")
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        assert permission.has_permission(request, None) is False

    def test_regular_user_denied(self, regular_user):
        permission = IsVyntiaStaff()
        request = RequestFactory().get("/")
        request.user = regular_user
        assert permission.has_permission(request, None) is False

    def test_vyntia_staff_allowed(self, staff_user):
        permission = IsVyntiaStaff()
        request = RequestFactory().get("/")
        request.user = staff_user
        assert permission.has_permission(request, None) is True

    def test_user_with_is_staff_but_not_vyntia_staff_denied(self, regular_user):
        """Django's `is_staff` is unrelated — only `is_vyntia_staff` counts."""
        regular_user.is_staff = True
        regular_user.save()
        permission = IsVyntiaStaff()
        request = RequestFactory().get("/")
        request.user = regular_user
        assert permission.has_permission(request, None) is False
```

- [ ] **Step 1.7: Run tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_admin_permission.py -v 2>&1 | tail -10
```

Expected: 4 tests pass.

- [ ] **Step 1.8: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥239 passed.

- [ ] **Step 1.9: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/identity/models/user.py \
        apps/api/apps/identity/migrations/ \
        apps/api/api/admin/__init__.py \
        apps/api/api/admin/permissions.py \
        apps/api/apps/tenancy/tests/test_admin_permission.py
git commit -m "feat(C5): add User.is_vyntia_staff field + IsVyntiaStaff DRF permission"
```

---

## Task 2: `setup_tenant_seed()` helper

**Files:**
- Create: `apps/api/apps/tenancy/admin_helpers/__init__.py`
- Create: `apps/api/apps/tenancy/admin_helpers/seed.py`
- Create: `apps/api/apps/tenancy/tests/test_setup_tenant_seed.py`

- [ ] **Step 2.1: Create `apps/api/apps/tenancy/admin_helpers/__init__.py`** (empty)

- [ ] **Step 2.2: Create `apps/api/apps/tenancy/admin_helpers/seed.py`**

```python
"""Tenant seed helper — minimal default state for newly provisioned tenants.

For C.5 MVP, this just creates a CompanyConfig record bound to the tenant.
HR-level Roles / Permissions / Module bindings are NOT seeded — admins can
run the existing identity management commands per-tenant after provisioning,
or seed via the admin UI in a future sub-layer.

Idempotent: safe to call multiple times for the same tenant (uses get_or_create).
"""

from django.db import transaction


@transaction.atomic
def setup_tenant_seed(tenant):
    """Create the minimal records a new tenant needs to function.

    Currently:
    - One CompanyConfig record bound to the tenant (using the tenant's RUC + name).

    Returns a dict describing what was created/updated.
    """
    from apps.organization.models import Company

    company, created = Company.objects.get_or_create(
        tenant=tenant,
        defaults={
            "ruc": tenant.ruc,
            "razon_social": tenant.name,
        },
    )
    return {
        "company_created": created,
        "company_id": company.pk,
    }
```

Note: The defaults `ruc` and `razon_social` assume the `Company` model has these fields. If `Company` requires additional NOT NULL fields, the implementer should add stubs for them as needed (set to empty strings or sensible defaults). Read `apps/api/apps/organization/models/company.py` first to identify required fields and adjust defaults accordingly.

- [ ] **Step 2.3: Write tests**

Create `apps/api/apps/tenancy/tests/test_setup_tenant_seed.py`:

```python
"""Tests for setup_tenant_seed()."""

import pytest

from apps.organization.models import Company
from apps.tenancy.admin_helpers.seed import setup_tenant_seed
from apps.tenancy.models import Tenant


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme Corp", ruc="20123456789",
        plan="starter", status="trial", created_by=staff_user,
    )


@pytest.mark.django_db
class TestSetupTenantSeed:
    def test_creates_company_for_tenant(self, tenant):
        result = setup_tenant_seed(tenant)
        assert result["company_created"] is True
        company = Company.objects.get(tenant=tenant)
        assert company.ruc == "20123456789"

    def test_idempotent(self, tenant):
        setup_tenant_seed(tenant)
        result = setup_tenant_seed(tenant)
        # Second call should not duplicate
        assert result["company_created"] is False
        assert Company.objects.filter(tenant=tenant).count() == 1
```

- [ ] **Step 2.4: Run tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_setup_tenant_seed.py -v 2>&1 | tail -10
```

Expected: 2 tests pass. If they fail because `Company` requires additional NOT NULL fields, read the model and add the missing defaults to `setup_tenant_seed()`.

- [ ] **Step 2.5: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥241 passed.

- [ ] **Step 2.6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/admin_helpers/ \
        apps/api/apps/tenancy/tests/test_setup_tenant_seed.py
git commit -m "feat(C5): setup_tenant_seed() helper creates CompanyConfig per tenant"
```

---

## Task 3: Admin tenant CRUD endpoints

**Files:**
- Create: `apps/api/api/admin/tenants/__init__.py`
- Create: `apps/api/api/admin/tenants/serializers.py`
- Create: `apps/api/api/admin/tenants/views.py`
- Create: `apps/api/api/admin/tenants/urls.py`
- Create: `apps/api/api/admin/urls.py`
- Modify: `apps/api/api/v1/urls.py` (or main router) — wire `/api/admin/`
- Create: `apps/api/apps/tenancy/tests/test_admin_tenants_crud.py`

- [ ] **Step 3.1: Create `tenants/serializers.py`**

```python
"""Serializers for /api/admin/tenants/*."""

from rest_framework import serializers

from apps.tenancy.models import Tenant

RESERVED_SLUGS = {
    "admin", "app", "www", "api", "docs", "status", "blog",
    "mail", "support", "help", "vyntia",
}


class TenantAdminSerializer(serializers.ModelSerializer):
    """Read serializer — full tenant detail for the admin panel."""

    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            "id", "slug", "name", "ruc", "plan", "status",
            "trial_ends_at", "max_users", "cancelled_at",
            "created_at", "updated_at", "member_count",
        ]
        read_only_fields = fields

    def get_member_count(self, obj):
        from apps.tenancy.models import TenantMembership
        return TenantMembership.objects.filter(tenant=obj, status="active").count()


class TenantCreateSerializer(serializers.Serializer):
    """Create serializer — input only. Backed by view that wraps in atomic txn."""

    slug = serializers.SlugField(max_length=63, required=True)
    name = serializers.CharField(max_length=200, required=True)
    ruc = serializers.RegexField(regex=r"^\d{11}$", required=True)
    plan = serializers.ChoiceField(choices=[
        "starter", "pro", "enterprise", "govtech",
    ], required=True)
    trial_days = serializers.IntegerField(min_value=0, max_value=90, default=30)
    admin_email = serializers.EmailField(required=True)
    admin_name = serializers.CharField(max_length=200, required=True)

    def validate_slug(self, value):
        value = value.lower()
        if value in RESERVED_SLUGS:
            raise serializers.ValidationError(f"'{value}' is a reserved subdomain.")
        if Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError(f"Slug '{value}' is already in use.")
        return value

    def validate_ruc(self, value):
        if Tenant.objects.filter(
            ruc=value, status__in=["trial", "active"]
        ).exists():
            raise serializers.ValidationError(
                f"RUC {value} is already linked to an active tenant."
            )
        return value


class TenantUpdateSerializer(serializers.ModelSerializer):
    """Patch serializer — only allow editing safe fields."""

    class Meta:
        model = Tenant
        fields = ["plan", "max_users", "trial_ends_at"]
```

- [ ] **Step 3.2: Create `tenants/views.py`**

```python
"""Admin tenant CRUD views."""

import secrets
from datetime import timedelta

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.admin.permissions import IsVyntiaStaff
from api.admin.tenants.serializers import (
    TenantAdminSerializer,
    TenantCreateSerializer,
    TenantUpdateSerializer,
)
from apps.core.responses import APIResponse
from apps.tenancy.admin_helpers.seed import setup_tenant_seed
from apps.tenancy.models import Tenant, TenantInvitation


class TenantsListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def get(self, request):
        """List all tenants. Pagination via ?page=N&page_size=N (defaults 1, 25)."""
        page = max(int(request.query_params.get("page", 1)), 1)
        page_size = min(max(int(request.query_params.get("page_size", 25)), 1), 100)
        offset = (page - 1) * page_size

        qs = Tenant.objects.all().order_by("-created_at")
        total = qs.count()
        items = qs[offset : offset + page_size]
        return APIResponse.success(
            data={
                "results": TenantAdminSerializer(items, many=True).data,
                "pagination": {
                    "total_items": total,
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size,
                },
            },
        )

    @transaction.atomic
    def post(self, request):
        """Create a new tenant + first invitation + minimal seed."""
        serializer = TenantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        trial_ends_at = timezone.now() + timedelta(days=validated["trial_days"])

        tenant = Tenant.objects.create(
            slug=validated["slug"],
            name=validated["name"],
            ruc=validated["ruc"],
            plan=validated["plan"],
            status="trial",
            trial_ends_at=trial_ends_at,
            created_by=request.user,
        )

        # Seed company config
        setup_tenant_seed(tenant)

        # Create first-admin invitation
        invitation_token = secrets.token_urlsafe(48)
        invitation = TenantInvitation.objects.create(
            tenant=tenant,
            email=validated["admin_email"],
            token=invitation_token,
            role="owner",
            expires_at=timezone.now() + timedelta(days=7),
            created_by=request.user,
        )

        activation_url = (
            f"https://{tenant.slug}.vyntia.pe/activate?token={invitation_token}"
        )

        return APIResponse.success(
            data={
                "tenant": TenantAdminSerializer(tenant).data,
                "invitation": {
                    "id": str(invitation.id),
                    "email": invitation.email,
                    "expires_at": invitation.expires_at.isoformat(),
                    "activation_url": activation_url,
                },
            },
            message="Tenant creado.",
            status_code=http_status.HTTP_201_CREATED,
        )


class TenantDetailView(APIView):
    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def get(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        return APIResponse.success(data=TenantAdminSerializer(tenant).data)

    def patch(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        serializer = TenantUpdateSerializer(tenant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(
            data=TenantAdminSerializer(tenant).data,
            message="Tenant actualizado.",
        )
```

- [ ] **Step 3.3: Create `tenants/urls.py`**

```python
from django.urls import path

from api.admin.tenants.views import TenantDetailView, TenantsListCreateView

app_name = "admin_tenants"

urlpatterns = [
    path("", TenantsListCreateView.as_view(), name="list_create"),
    path("<uuid:tenant_id>/", TenantDetailView.as_view(), name="detail"),
    # lifecycle actions added in Task 4
]
```

- [ ] **Step 3.4: Create `apps/api/api/admin/urls.py`**

```python
from django.urls import include, path

app_name = "admin"

urlpatterns = [
    path("tenants/", include("api.admin.tenants.urls")),
    # users/ + support-sessions/ added in Tasks 5-6
]
```

- [ ] **Step 3.5: Wire `/api/admin/` in the main URL router**

Find `apps/api/api/v1/urls.py` (where `/api/v1/auth/` etc. are wired). Add a sibling at the parent level — likely `apps/api/api/urls.py`. Look for the line that includes `api.v1.urls`. Add:

```python
path("admin/", include("api.admin.urls")),
```

- [ ] **Step 3.6: Write tests**

Create `apps/api/apps/tenancy/tests/test_admin_tenants_crud.py`:

```python
"""Tests for /api/admin/tenants/ CRUD."""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenancy.models import Tenant, TenantInvitation


@pytest.fixture
def staff_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="zviera", email="zviera@vyntia.pe", password="x"
    )
    user.is_vyntia_staff = True
    user.save()
    return user


@pytest.fixture
def regular_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="x"
    )


@pytest.fixture
def existing_tenant(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20111111111",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def client():
    return APIClient()


def auth(user):
    return f"Bearer {RefreshToken.for_user(user).access_token}"


@pytest.mark.django_db
class TestTenantsListPermission:
    def test_anonymous_denied(self, client):
        response = client.get("/api/admin/tenants/")
        assert response.status_code == 401

    def test_regular_user_denied(self, client, regular_user):
        client.credentials(HTTP_AUTHORIZATION=auth(regular_user))
        response = client.get("/api/admin/tenants/")
        assert response.status_code == 403

    def test_vyntia_staff_allowed(self, client, staff_user, existing_tenant):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.get("/api/admin/tenants/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestTenantsList:
    def test_returns_paginated_results(self, client, staff_user, existing_tenant):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.get("/api/admin/tenants/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "results" in data
        assert "pagination" in data
        assert data["pagination"]["total_items"] == 1
        assert data["results"][0]["slug"] == "acme"


@pytest.mark.django_db
class TestTenantsCreate:
    def test_creates_tenant_with_invitation(self, client, staff_user):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.post(
            "/api/admin/tenants/",
            {
                "slug": "newco",
                "name": "New Co S.A.C.",
                "ruc": "20999999999",
                "plan": "starter",
                "trial_days": 30,
                "admin_email": "ceo@newco.com",
                "admin_name": "CEO",
            },
            format="json",
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["tenant"]["slug"] == "newco"
        assert data["invitation"]["email"] == "ceo@newco.com"
        assert "activation_url" in data["invitation"]
        # Tenant + invitation persisted
        tenant = Tenant.objects.get(slug="newco")
        assert tenant.status == "trial"
        assert TenantInvitation.objects.filter(tenant=tenant, accepted_at__isnull=True).count() == 1

    def test_rejects_reserved_slug(self, client, staff_user):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.post(
            "/api/admin/tenants/",
            {
                "slug": "admin",  # reserved
                "name": "X",
                "ruc": "20999999999",
                "plan": "starter",
                "admin_email": "ceo@x.com",
                "admin_name": "CEO",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_rejects_duplicate_slug(self, client, staff_user, existing_tenant):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.post(
            "/api/admin/tenants/",
            {
                "slug": "acme",
                "name": "Other",
                "ruc": "20888888888",
                "plan": "starter",
                "admin_email": "x@y.com",
                "admin_name": "X",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_rejects_bad_ruc_format(self, client, staff_user):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.post(
            "/api/admin/tenants/",
            {
                "slug": "valid",
                "name": "X",
                "ruc": "12345",  # too short
                "plan": "starter",
                "admin_email": "x@y.com",
                "admin_name": "X",
            },
            format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestTenantDetail:
    def test_get_returns_tenant(self, client, staff_user, existing_tenant):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.get(f"/api/admin/tenants/{existing_tenant.id}/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["slug"] == "acme"
        assert data["member_count"] == 0  # no memberships yet

    def test_patch_updates_plan(self, client, staff_user, existing_tenant):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.patch(
            f"/api/admin/tenants/{existing_tenant.id}/",
            {"plan": "pro"},
            format="json",
        )
        assert response.status_code == 200
        existing_tenant.refresh_from_db()
        assert existing_tenant.plan == "pro"

    def test_get_404_for_unknown(self, client, staff_user):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.get("/api/admin/tenants/00000000-0000-0000-0000-000000000000/")
        assert response.status_code == 404
```

- [ ] **Step 3.7: Run tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_admin_tenants_crud.py -v 2>&1 | tail -20
```

Expected: ~10 tests pass.

- [ ] **Step 3.8: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥251 passed.

- [ ] **Step 3.9: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/admin/ \
        apps/api/api/v1/urls.py \
        apps/api/apps/tenancy/tests/test_admin_tenants_crud.py
git commit -m "feat(C5): /api/admin/tenants/ CRUD (list/create/retrieve/patch) gated by IsVyntiaStaff"
```

---

## Task 4: Tenant lifecycle actions (suspend, cancel, re-invite)

**Files:**
- Modify: `apps/api/api/admin/tenants/views.py` (add 3 action views)
- Modify: `apps/api/api/admin/tenants/urls.py` (add 3 URL patterns)
- Create: `apps/api/apps/tenancy/tests/test_admin_tenants_lifecycle.py`

- [ ] **Step 4.1: Append action views to `tenants/views.py`**

```python
class TenantSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def post(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        if tenant.status == "cancelled":
            return APIResponse.error(message="No se puede suspender un tenant cancelado.", status_code=400)
        tenant.status = "suspended"
        tenant.save(update_fields=["status", "updated_at"])
        return APIResponse.success(
            data=TenantAdminSerializer(tenant).data,
            message="Tenant suspendido.",
        )


class TenantCancelView(APIView):
    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def post(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        tenant.status = "cancelled"
        tenant.cancelled_at = timezone.now()
        tenant.save(update_fields=["status", "cancelled_at", "updated_at"])
        return APIResponse.success(
            data=TenantAdminSerializer(tenant).data,
            message="Tenant cancelado.",
        )


class TenantReinviteView(APIView):
    """Re-issue an invitation if the original one expired or was lost."""

    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def post(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        email = request.data.get("email")
        role = request.data.get("role", "owner")
        if not email:
            return APIResponse.error(message="email is required.", status_code=400)

        token = secrets.token_urlsafe(48)
        invitation = TenantInvitation.objects.create(
            tenant=tenant,
            email=email,
            token=token,
            role=role,
            expires_at=timezone.now() + timedelta(days=7),
            created_by=request.user,
        )
        return APIResponse.success(
            data={
                "id": str(invitation.id),
                "email": invitation.email,
                "expires_at": invitation.expires_at.isoformat(),
                "activation_url": f"https://{tenant.slug}.vyntia.pe/activate?token={token}",
            },
            message="Invitación re-enviada.",
            status_code=http_status.HTTP_201_CREATED,
        )
```

- [ ] **Step 4.2: Update `tenants/urls.py`**

```python
from django.urls import path

from api.admin.tenants.views import (
    TenantCancelView,
    TenantDetailView,
    TenantReinviteView,
    TenantsListCreateView,
    TenantSuspendView,
)

app_name = "admin_tenants"

urlpatterns = [
    path("", TenantsListCreateView.as_view(), name="list_create"),
    path("<uuid:tenant_id>/", TenantDetailView.as_view(), name="detail"),
    path("<uuid:tenant_id>/suspend/", TenantSuspendView.as_view(), name="suspend"),
    path("<uuid:tenant_id>/cancel/", TenantCancelView.as_view(), name="cancel"),
    path("<uuid:tenant_id>/invitations/", TenantReinviteView.as_view(), name="reinvite"),
]
```

- [ ] **Step 4.3: Write tests**

Create `apps/api/apps/tenancy/tests/test_admin_tenants_lifecycle.py`:

```python
"""Tests for tenant lifecycle actions: suspend, cancel, re-invite."""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenancy.models import Tenant, TenantInvitation


@pytest.fixture
def staff_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="zviera", email="zviera@vyntia.pe", password="x"
    )
    user.is_vyntia_staff = True
    user.save()
    return user


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20111111111",
        plan="starter", status="trial", created_by=staff_user,
    )


@pytest.fixture
def client(staff_user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(staff_user).access_token}")
    return c


@pytest.mark.django_db
class TestSuspend:
    def test_suspends_active_tenant(self, client, tenant):
        response = client.post(f"/api/admin/tenants/{tenant.id}/suspend/")
        assert response.status_code == 200
        tenant.refresh_from_db()
        assert tenant.status == "suspended"

    def test_cannot_suspend_cancelled_tenant(self, client, tenant):
        tenant.status = "cancelled"
        tenant.save()
        response = client.post(f"/api/admin/tenants/{tenant.id}/suspend/")
        assert response.status_code == 400


@pytest.mark.django_db
class TestCancel:
    def test_cancels_tenant(self, client, tenant):
        response = client.post(f"/api/admin/tenants/{tenant.id}/cancel/")
        assert response.status_code == 200
        tenant.refresh_from_db()
        assert tenant.status == "cancelled"
        assert tenant.cancelled_at is not None


@pytest.mark.django_db
class TestReinvite:
    def test_creates_new_invitation(self, client, tenant):
        response = client.post(
            f"/api/admin/tenants/{tenant.id}/invitations/",
            {"email": "newadmin@acme.com", "role": "owner"},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["email"] == "newadmin@acme.com"
        assert "activation_url" in data
        assert TenantInvitation.objects.filter(
            tenant=tenant, email="newadmin@acme.com"
        ).count() == 1

    def test_email_required(self, client, tenant):
        response = client.post(
            f"/api/admin/tenants/{tenant.id}/invitations/",
            {},
            format="json",
        )
        assert response.status_code == 400
```

- [ ] **Step 4.4: Run tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_admin_tenants_lifecycle.py -v 2>&1 | tail -15
```

Expected: 5 tests pass.

- [ ] **Step 4.5: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥256 passed.

- [ ] **Step 4.6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/admin/tenants/views.py \
        apps/api/api/admin/tenants/urls.py \
        apps/api/apps/tenancy/tests/test_admin_tenants_lifecycle.py
git commit -m "feat(C5): tenant lifecycle actions (suspend, cancel, re-invite)"
```

---

## Task 5: Admin user search

**Files:**
- Create: `apps/api/api/admin/users/__init__.py`
- Create: `apps/api/api/admin/users/views.py`
- Create: `apps/api/api/admin/users/urls.py`
- Modify: `apps/api/api/admin/urls.py` — wire `users/`
- Create: `apps/api/apps/tenancy/tests/test_admin_users_search.py`

- [ ] **Step 5.1: Create `users/__init__.py`** (empty)

- [ ] **Step 5.2: Create `users/views.py`**

```python
"""Admin user search endpoint."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.admin.permissions import IsVyntiaStaff
from apps.core.responses import APIResponse


class UsersSearchView(APIView):
    """GET /api/admin/users/?q=<term>&page=N&page_size=N

    Searches by username, email, or full name (icontains).
    """

    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def get(self, request):
        User = get_user_model()
        q = request.query_params.get("q", "").strip()
        page = max(int(request.query_params.get("page", 1)), 1)
        page_size = min(max(int(request.query_params.get("page_size", 25)), 1), 100)
        offset = (page - 1) * page_size

        qs = User.objects.all()
        if q:
            qs = qs.filter(
                Q(username__icontains=q)
                | Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
            )

        qs = qs.order_by("username")
        total = qs.count()
        items = qs[offset : offset + page_size]

        return APIResponse.success(
            data={
                "results": [
                    {
                        "id": str(u.id),
                        "username": u.username,
                        "email": u.email,
                        "is_active": u.is_active,
                        "is_vyntia_staff": u.is_vyntia_staff,
                    }
                    for u in items
                ],
                "pagination": {
                    "total_items": total,
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size,
                },
            },
        )
```

- [ ] **Step 5.3: Create `users/urls.py`**

```python
from django.urls import path

from api.admin.users.views import UsersSearchView

app_name = "admin_users"

urlpatterns = [
    path("", UsersSearchView.as_view(), name="search"),
    # impersonate/ added in Task 6
]
```

- [ ] **Step 5.4: Wire in `api/admin/urls.py`**

Update `apps/api/api/admin/urls.py`:

```python
from django.urls import include, path

app_name = "admin"

urlpatterns = [
    path("tenants/", include("api.admin.tenants.urls")),
    path("users/", include("api.admin.users.urls")),
]
```

- [ ] **Step 5.5: Write tests**

Create `apps/api/apps/tenancy/tests/test_admin_users_search.py`:

```python
"""Tests for /api/admin/users/?q=<term> search endpoint."""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def staff_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="zviera", email="zviera@vyntia.pe", password="x"
    )
    user.is_vyntia_staff = True
    user.save()
    return user


@pytest.fixture
def alice(django_user_model):
    return django_user_model.objects.create_user(
        username="alice", email="alice@example.com", password="x"
    )


@pytest.fixture
def bob(django_user_model):
    return django_user_model.objects.create_user(
        username="bob", email="bob@example.com", password="x"
    )


@pytest.fixture
def client(staff_user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(staff_user).access_token}")
    return c


@pytest.mark.django_db
class TestUsersSearch:
    def test_returns_all_when_q_empty(self, client, alice, bob):
        response = client.get("/api/admin/users/")
        assert response.status_code == 200
        data = response.json()["data"]
        # alice + bob + staff_user (3)
        assert data["pagination"]["total_items"] == 3

    def test_filters_by_username(self, client, alice, bob):
        response = client.get("/api/admin/users/?q=alice")
        data = response.json()["data"]
        assert data["pagination"]["total_items"] == 1
        assert data["results"][0]["username"] == "alice"

    def test_filters_by_email(self, client, alice, bob):
        response = client.get("/api/admin/users/?q=bob@")
        data = response.json()["data"]
        assert data["pagination"]["total_items"] == 1
        assert data["results"][0]["email"] == "bob@example.com"

    def test_pagination(self, client, alice, bob):
        response = client.get("/api/admin/users/?page_size=1&page=1")
        data = response.json()["data"]
        assert len(data["results"]) == 1
        assert data["pagination"]["total_pages"] >= 1

    def test_unauthenticated_denied(self):
        c = APIClient()
        response = c.get("/api/admin/users/")
        assert response.status_code == 401
```

- [ ] **Step 5.6: Run tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_admin_users_search.py -v 2>&1 | tail -10
```

Expected: 5 tests pass.

- [ ] **Step 5.7: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥261 passed.

- [ ] **Step 5.8: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/admin/users/ apps/api/api/admin/urls.py \
        apps/api/apps/tenancy/tests/test_admin_users_search.py
git commit -m "feat(C5): GET /api/admin/users/ search endpoint (q, pagination)"
```

---

## Task 6: Impersonation + SupportSession audit log

**Files:**
- Create: `apps/api/apps/tenancy/admin_helpers/impersonation.py`
- Modify: `apps/api/api/admin/users/views.py` (add `ImpersonateView`)
- Modify: `apps/api/api/admin/users/urls.py`
- Create: `apps/api/api/admin/support_sessions/__init__.py`
- Create: `apps/api/api/admin/support_sessions/views.py`
- Create: `apps/api/api/admin/support_sessions/urls.py`
- Modify: `apps/api/api/admin/urls.py` (wire support-sessions/)
- Create: `apps/api/apps/tenancy/tests/test_admin_impersonation.py`

- [ ] **Step 6.1: Create `apps/api/apps/tenancy/admin_helpers/impersonation.py`**

```python
"""Impersonation helper — issues a session JWT with audit claims."""

from datetime import timedelta

from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.tenancy.context import tenant_context
from apps.tenancy.models import SupportSession


def issue_impersonation_session(*, staff_user, target_user, tenant, reason, ttl_hours=2):
    """Create a SupportSession and mint an impersonation JWT.

    Returns (support_session, access_token_str, refresh_token_str).
    The JWT carries `impersonated_by` and `support_session_id` claims that
    the C.6 frontend uses to render a banner.
    """
    expires_at = timezone.now() + timedelta(hours=ttl_hours)

    session = SupportSession.objects.create(
        staff_user=staff_user,
        target_user=target_user,
        tenant=tenant,
        reason=reason,
        expires_at=expires_at,
    )

    # Issue tokens in the target tenant's context so they have tenant claims
    with tenant_context(tenant):
        refresh = RefreshToken.for_user(target_user)
        refresh["tenant_id"] = str(tenant.id)
        refresh["tenant_slug"] = tenant.slug
        refresh["impersonated_by"] = str(staff_user.id)
        refresh["support_session_id"] = str(session.id)

        access = refresh.access_token
        # Copy impersonation claims onto the access token too (it's what the API uses)
        access["tenant_id"] = str(tenant.id)
        access["tenant_slug"] = tenant.slug
        access["impersonated_by"] = str(staff_user.id)
        access["support_session_id"] = str(session.id)

    return session, str(access), str(refresh)
```

- [ ] **Step 6.2: Add `ImpersonateView` to `users/views.py`**

Append to `apps/api/api/admin/users/views.py`:

```python
class ImpersonateView(APIView):
    """POST /api/admin/users/<user_id>/impersonate/

    Body: { reason: str, tenant_id: UUID }
    Returns: { access, refresh, support_session_id, expires_at }
    """

    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def post(self, request, user_id):
        from django.contrib.auth import get_user_model
        from apps.tenancy.admin_helpers.impersonation import issue_impersonation_session
        from apps.tenancy.models import Tenant, TenantMembership

        User = get_user_model()
        target = User.objects.filter(pk=user_id, is_active=True).first()
        if target is None:
            return APIResponse.error(message="Usuario no encontrado.", status_code=404)

        reason = (request.data.get("reason") or "").strip()
        if len(reason) < 5:
            return APIResponse.error(
                message="reason es obligatorio (mínimo 5 caracteres).",
                status_code=400,
            )

        tenant_id = request.data.get("tenant_id")
        if not tenant_id:
            return APIResponse.error(message="tenant_id es obligatorio.", status_code=400)

        tenant = Tenant.objects.filter(pk=tenant_id).first()
        if tenant is None:
            return APIResponse.error(message="Tenant no encontrado.", status_code=404)

        # Target must be a member of the tenant (don't impersonate ghosts)
        has_membership = TenantMembership.objects.filter(
            tenant=tenant, user=target
        ).exists()
        if not has_membership:
            return APIResponse.error(
                message=f"El usuario no es miembro del tenant '{tenant.slug}'.",
                status_code=400,
            )

        session, access, refresh = issue_impersonation_session(
            staff_user=request.user,
            target_user=target,
            tenant=tenant,
            reason=reason,
        )

        return APIResponse.success(
            data={
                "access": access,
                "refresh": refresh,
                "support_session_id": str(session.id),
                "tenant_slug": tenant.slug,
                "expires_at": session.expires_at.isoformat(),
            },
            message="Sesión de soporte iniciada.",
        )
```

- [ ] **Step 6.3: Update `users/urls.py`**

```python
from django.urls import path

from api.admin.users.views import ImpersonateView, UsersSearchView

app_name = "admin_users"

urlpatterns = [
    path("", UsersSearchView.as_view(), name="search"),
    path("<uuid:user_id>/impersonate/", ImpersonateView.as_view(), name="impersonate"),
]
```

- [ ] **Step 6.4: Create `apps/api/api/admin/support_sessions/__init__.py`** (empty)

- [ ] **Step 6.5: Create `support_sessions/views.py`**

```python
"""GET /api/admin/support-sessions/ — list SupportSession audit log."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.admin.permissions import IsVyntiaStaff
from apps.core.responses import APIResponse
from apps.tenancy.models import SupportSession


class SupportSessionsListView(APIView):
    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def get(self, request):
        page = max(int(request.query_params.get("page", 1)), 1)
        page_size = min(max(int(request.query_params.get("page_size", 25)), 1), 100)
        offset = (page - 1) * page_size

        qs = SupportSession.objects.select_related(
            "staff_user", "target_user", "tenant"
        ).order_by("-started_at")
        total = qs.count()
        items = qs[offset : offset + page_size]

        return APIResponse.success(
            data={
                "results": [
                    {
                        "id": str(s.id),
                        "staff_user": s.staff_user.username,
                        "target_user": s.target_user.username,
                        "tenant_slug": s.tenant.slug,
                        "reason": s.reason,
                        "started_at": s.started_at.isoformat(),
                        "expires_at": s.expires_at.isoformat(),
                        "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                        "actions_count": s.actions_count,
                    }
                    for s in items
                ],
                "pagination": {
                    "total_items": total,
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size,
                },
            },
        )
```

- [ ] **Step 6.6: Create `support_sessions/urls.py`**

```python
from django.urls import path

from api.admin.support_sessions.views import SupportSessionsListView

app_name = "admin_support_sessions"

urlpatterns = [
    path("", SupportSessionsListView.as_view(), name="list"),
]
```

- [ ] **Step 6.7: Wire in `apps/api/api/admin/urls.py`**

```python
from django.urls import include, path

app_name = "admin"

urlpatterns = [
    path("tenants/", include("api.admin.tenants.urls")),
    path("users/", include("api.admin.users.urls")),
    path("support-sessions/", include("api.admin.support_sessions.urls")),
]
```

- [ ] **Step 6.8: Write tests**

Create `apps/api/apps/tenancy/tests/test_admin_impersonation.py`:

```python
"""Tests for /api/admin/users/<id>/impersonate/ + /api/admin/support-sessions/."""

import pytest
import jwt as pyjwt
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenancy.models import (
    SupportSession, Tenant, TenantMembership,
)


@pytest.fixture
def staff_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="zviera", email="zviera@vyntia.pe", password="x"
    )
    user.is_vyntia_staff = True
    user.save()
    return user


@pytest.fixture
def target_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="x"
    )


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20111111111",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def membership(tenant, target_user):
    return TenantMembership.objects.create(
        tenant=tenant, user=target_user, role="admin", status="active"
    )


@pytest.fixture
def client(staff_user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(staff_user).access_token}")
    return c


@pytest.mark.django_db
class TestImpersonate:
    def test_creates_support_session_and_returns_tokens(
        self, client, staff_user, target_user, tenant, membership
    ):
        response = client.post(
            f"/api/admin/users/{target_user.id}/impersonate/",
            {"reason": "Ticket #1234 — bug en boletas", "tenant_id": str(tenant.id)},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "access" in data
        assert "refresh" in data
        assert "support_session_id" in data

        # SupportSession created with right metadata
        session = SupportSession.objects.get(pk=data["support_session_id"])
        assert session.staff_user == staff_user
        assert session.target_user == target_user
        assert session.tenant == tenant
        assert session.reason.startswith("Ticket #1234")

    def test_token_contains_impersonation_claims(
        self, client, staff_user, target_user, tenant, membership
    ):
        response = client.post(
            f"/api/admin/users/{target_user.id}/impersonate/",
            {"reason": "support reason", "tenant_id": str(tenant.id)},
            format="json",
        )
        access = response.json()["data"]["access"]
        payload = pyjwt.decode(access, options={"verify_signature": False})
        assert payload["impersonated_by"] == str(staff_user.id)
        assert payload["tenant_id"] == str(tenant.id)
        assert payload["support_session_id"]

    def test_404_for_unknown_user(self, client, tenant):
        response = client.post(
            f"/api/admin/users/00000000-0000-0000-0000-000000000000/impersonate/",
            {"reason": "x" * 10, "tenant_id": str(tenant.id)},
            format="json",
        )
        assert response.status_code == 404

    def test_400_when_reason_too_short(self, client, target_user, tenant, membership):
        response = client.post(
            f"/api/admin/users/{target_user.id}/impersonate/",
            {"reason": "a", "tenant_id": str(tenant.id)},
            format="json",
        )
        assert response.status_code == 400

    def test_400_when_user_not_member(self, client, target_user, tenant):
        # No membership — should reject
        response = client.post(
            f"/api/admin/users/{target_user.id}/impersonate/",
            {"reason": "support reason", "tenant_id": str(tenant.id)},
            format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestSupportSessionsList:
    def test_lists_sessions(self, client, staff_user, target_user, tenant, membership):
        # Create one session via the impersonate endpoint
        client.post(
            f"/api/admin/users/{target_user.id}/impersonate/",
            {"reason": "audit", "tenant_id": str(tenant.id)},
            format="json",
        )
        response = client.get("/api/admin/support-sessions/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["pagination"]["total_items"] == 1
        assert data["results"][0]["staff_user"] == "zviera"
        assert data["results"][0]["target_user"] == "maria"
```

- [ ] **Step 6.9: Run tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_admin_impersonation.py -v 2>&1 | tail -15
```

Expected: 6 tests pass.

- [ ] **Step 6.10: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥267 passed.

- [ ] **Step 6.11: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/admin_helpers/impersonation.py \
        apps/api/api/admin/users/ \
        apps/api/api/admin/support_sessions/ \
        apps/api/api/admin/urls.py \
        apps/api/apps/tenancy/tests/test_admin_impersonation.py
git commit -m "feat(C5): impersonation flow + SupportSession audit log"
```

---

## Task 7: Final verification + merge

- [ ] **Step 7.1: Full pytest baseline**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development 2>&1 | tail -2
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations --dry-run --check --settings=vyntia.settings.development 2>&1 | tail -2
```

Expected: ≥267 passed, check clean, no pending migrations.

- [ ] **Step 7.2: Frontend baseline**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
```

- [ ] **Step 7.3: Update master roadmap**

Find the C.5 row in `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`. Update the "Detailed plan" cell to:

```
`2026-05-09-vyntia-C5-admin-api.md` ✅ merged 2026-05-09
```

- [ ] **Step 7.4: Commit roadmap update**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md
git commit -m "docs(C5): mark C.5 done in master roadmap"
```

- [ ] **Step 7.5: Merge to master**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/C5-admin-api \
  -m "Merge C.5: admin API (tenants CRUD + lifecycle + users + impersonation + SupportSession)"
```

---

## Self-Review

### Spec coverage check

| Spec § 7 requirement | Covered by task |
|---|---|
| `is_vyntia_staff` on User | Task 1 |
| `IsVyntiaStaff` permission | Task 1 |
| GET /api/admin/tenants/ paginated | Task 3 |
| POST /api/admin/tenants/ with invitation + atomic | Task 3 |
| GET /api/admin/tenants/{id}/ detail | Task 3 |
| PATCH /api/admin/tenants/{id}/ | Task 3 |
| POST suspend / cancel | Task 4 |
| POST invitations re-send | Task 4 |
| GET /api/admin/users/ search | Task 5 |
| POST impersonate + SupportSession | Task 6 |
| GET /api/admin/support-sessions/ | Task 6 |
| `setup_tenant_seed` | Task 2 |

### Spec deviations

1. **`setup_tenant_seed()` is minimal** — only creates `CompanyConfig`. Spec § 7.2 mentions seeding default Roles + Permissions + Module bindings per plan; deferred for MVP. The existing identity management commands (`setup_roles_permisos`) can be invoked per-tenant after creation.

2. **No GET /api/admin/tenants/{id}/audit/ endpoint** — spec mentions an audit log per tenant; for MVP we ship `/api/admin/support-sessions/` (cross-tenant audit) which is sufficient. Per-tenant audit is a future hardening pass.

3. **No email automation for invitations** — admin gets the activation URL in the API response and forwards it manually (or via a script). Email integration is deferred.

4. **Impersonation tokens have NO single-use semantics** — they're standard JWTs with the `impersonated_by` + `support_session_id` claims. The 2h expiry is the security boundary. The C.6 frontend renders a banner based on these claims.

5. **`SupportSession.ended_at` not auto-set** — currently only auto-expires via JWT TTL. The frontend can call a future "end session" endpoint to mark it explicitly; for MVP, sessions remain "open" in the audit log until expiry.

### Placeholder scan

- All code is complete and runnable.
- The `setup_tenant_seed` test depends on `Company` model fields. The implementer must read the Company model in Task 2 Step 2.2 and adjust default field values if the model has additional NOT NULL fields beyond `ruc` and `razon_social`. This is documented as a step note, not a placeholder.

### Type consistency

- `is_vyntia_staff` consistently checked across `IsVyntiaStaff` permission and tests.
- `support_session_id` claim name consistent across `impersonation.py`, view response, and tests.
- `Tenant` and `TenantMembership` lookups use `Tenant.objects` and `TenantMembership.objects` consistently — these work in admin context because `request.tenant` is None on `admin.vyntia.pe`, so C.3's lenient TenantManager doesn't filter.

### Out of scope (deferred)

- Frontend admin panel UI (C.7)
- HR-role / permission seeding per plan (future)
- Email sending for invitations
- Audit log retention beyond default
- "End session" endpoint for impersonation
- Per-tenant detailed audit log endpoint

---

**Plan complete.** When executed, C.5 ships ~7 commits, ~15 new files (~1100 LOC), 1 migration, ~30 new tests. Tests baseline grows from 235 → ~267. Frontend untouched.
