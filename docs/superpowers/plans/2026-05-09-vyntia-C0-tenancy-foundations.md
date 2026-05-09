# C.0 — Tenancy Foundations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `apps/tenancy/` Django app with 4 models (`Tenant`, `TenantMembership`, `TenantInvitation`, `SupportSession`) wired into INSTALLED_APPS, with full test coverage and Django admin registrations. No `tenant_id` is added to other apps in this sub-layer (deferred to C.1).

**Architecture:** Standard Django app layout following Foundation conventions: models split per file, re-exported from `models/__init__.py`. UUID primary keys (per L3.10.2). All 4 models live in the same app; no cross-app FKs except to `identity.User` and self-references. Tests use pytest-django fixtures.

**Tech Stack:** Django 5.2, DRF, pytest-django, PostgreSQL 15.

**Source spec:** `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` § 3.1

**Source roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`

---

## Baseline snapshot (must be preserved or improved at every commit)

| Check | Command | Expected |
|---|---|---|
| Django system | `cd apps/api && python manage.py check --settings=vyntia.settings.development` | No errors |
| Backend tests | `cd apps/api && pytest tests/ -q` | 161 passed / 7-8 failed / 3 skipped |
| Frontend build | `cd apps/web && npm run build` | Exit 0, ~8-9 s |
| Frontend types | `cd apps/web && npx tsc --noEmit -p tsconfig.app.json` | 1 error (BlankEnum.ts — pre-existing) |
| Frontend tests | `cd apps/web && npm test -- --run` | 7 passed |

C.0 adds: ~15-20 new tests in `apps/api/apps/tenancy/tests/` — total target ≥176 passed.

---

## File structure

**Files to create:**

```
apps/api/apps/tenancy/
├── __init__.py
├── apps.py                          # TenancyConfig
├── admin.py                         # Django admin registrations
├── models/
│   ├── __init__.py                  # re-exports all 4 models
│   ├── tenant.py                    # Tenant
│   ├── membership.py                # TenantMembership
│   ├── invitation.py                # TenantInvitation
│   └── support_session.py           # SupportSession
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py              # auto-generated
└── tests/
    ├── __init__.py
    ├── test_tenant_model.py
    ├── test_membership_model.py
    ├── test_invitation_model.py
    └── test_support_session_model.py
```

**Files to modify:**

- `apps/api/vyntia/settings/base.py` — add `apps.tenancy.apps.TenancyConfig` to LOCAL_APPS
- `apps/api/pyproject.toml` — add `apps.tenancy` to packages list (auto-discovered if package layout is correct, but explicit for clarity)

---

## Branch

`vyntia/C0-tenancy-foundations` — branched from `master` (HEAD has tag `foundation-complete`).

---

## Task 1: Create the tenancy app skeleton

**Files:**
- Create: `apps/api/apps/tenancy/__init__.py`
- Create: `apps/api/apps/tenancy/apps.py`
- Create: `apps/api/apps/tenancy/migrations/__init__.py`
- Modify: `apps/api/vyntia/settings/base.py:33-44` (LOCAL_APPS)

- [ ] **Step 1.1: Create branch**

```bash
cd D:/VYNTIA
git checkout master
git pull --ff-only          # ensure master is up to date (if remote exists, no-op otherwise)
git checkout -b vyntia/C0-tenancy-foundations
```

- [ ] **Step 1.2: Create `apps/tenancy/__init__.py` (empty)**

```python
# apps/api/apps/tenancy/__init__.py
```

(empty file — Python package marker)

- [ ] **Step 1.3: Create `apps/tenancy/apps.py`**

```python
# apps/api/apps/tenancy/apps.py
from django.apps import AppConfig


class TenancyConfig(AppConfig):
    """Tenancy app — owns Tenant, TenantMembership, TenantInvitation, SupportSession.

    Boundary:
    - Tenant entity is the SaaS-level subscriber (slug, plan, status).
    - TenantMembership is the M2M between global identity.User and Tenant.
    - SupportSession audits Vyntia staff impersonating tenant users.

    No cross-app FKs except to `identity.User`. Other apps will reference
    Tenant via `'tenancy.Tenant'` string lazy in C.1.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tenancy"
    label = "tenancy"
    verbose_name = "Tenancy"
```

- [ ] **Step 1.4: Create `apps/tenancy/migrations/__init__.py` (empty)**

```python
# apps/api/apps/tenancy/migrations/__init__.py
```

- [ ] **Step 1.5: Register in `LOCAL_APPS`**

In `apps/api/vyntia/settings/base.py`, find the `LOCAL_APPS` list and append `"apps.tenancy.apps.TenancyConfig"` so it ends up like:

```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "apps.employees.apps.EmployeesConfig",
    "apps.contracts.apps.ContractsConfig",
    "apps.documents.apps.DocumentsConfig",
    "apps.payroll.apps.PayrollConfig",
    "apps.time_off.apps.TimeOffConfig",
    "apps.onboarding.apps.OnboardingConfig",
    "apps.tenancy.apps.TenancyConfig",
]
```

- [ ] **Step 1.6: Verify Django system check**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 1.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/__init__.py \
        apps/api/apps/tenancy/apps.py \
        apps/api/apps/tenancy/migrations/__init__.py \
        apps/api/vyntia/settings/base.py
git commit -m "chore(C0): scaffold apps/tenancy app skeleton + register in INSTALLED_APPS"
```

---

## Task 2: `Tenant` model — TDD

**Files:**
- Create: `apps/api/apps/tenancy/tests/__init__.py`
- Create: `apps/api/apps/tenancy/tests/test_tenant_model.py`
- Create: `apps/api/apps/tenancy/models/__init__.py`
- Create: `apps/api/apps/tenancy/models/tenant.py`
- Create: `apps/api/apps/tenancy/migrations/0001_initial.py` (auto-generated)

- [ ] **Step 2.1: Create `tests/__init__.py` (empty)**

```python
# apps/api/apps/tenancy/tests/__init__.py
```

- [ ] **Step 2.2: Write the failing test**

Create `apps/api/apps/tenancy/tests/test_tenant_model.py`:

```python
"""Tests for the Tenant model."""

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.tenancy.models import Tenant


@pytest.fixture
def staff_user(django_user_model):
    """A Vyntia staff user used as `created_by` for tenants."""
    return django_user_model.objects.create_user(
        username="vyntia_staff",
        email="staff@vyntia.pe",
        password="testpass123",
    )


@pytest.mark.django_db
class TestTenantModel:
    def test_create_tenant_with_required_fields(self, staff_user):
        tenant = Tenant.objects.create(
            slug="acme",
            name="Acme Corp S.A.C.",
            ruc="20123456789",
            plan="starter",
            status="trial",
            trial_ends_at=timezone.now() + timedelta(days=30),
            created_by=staff_user,
        )
        assert tenant.id is not None
        assert tenant.slug == "acme"
        assert tenant.name == "Acme Corp S.A.C."
        assert tenant.ruc == "20123456789"
        assert tenant.plan == "starter"
        assert tenant.status == "trial"
        assert tenant.max_users == 10  # default
        assert tenant.created_at is not None
        assert tenant.updated_at is not None
        assert tenant.cancelled_at is None
        assert tenant.created_by == staff_user

    def test_slug_must_be_unique(self, staff_user):
        Tenant.objects.create(
            slug="acme",
            name="Acme",
            ruc="20123456789",
            plan="starter",
            status="trial",
            created_by=staff_user,
        )
        with pytest.raises(IntegrityError):
            Tenant.objects.create(
                slug="acme",  # same slug
                name="Other Acme",
                ruc="20999999999",
                plan="pro",
                status="active",
                created_by=staff_user,
            )

    def test_str_representation(self, staff_user):
        tenant = Tenant.objects.create(
            slug="acme",
            name="Acme Corp",
            ruc="20123456789",
            plan="starter",
            status="active",
            created_by=staff_user,
        )
        assert str(tenant) == "Acme Corp (acme)"

    def test_default_max_users_is_ten(self, staff_user):
        tenant = Tenant.objects.create(
            slug="acme",
            name="Acme",
            ruc="20123456789",
            plan="starter",
            status="trial",
            created_by=staff_user,
        )
        assert tenant.max_users == 10

    def test_uuid_primary_key(self, staff_user):
        import uuid
        tenant = Tenant.objects.create(
            slug="acme",
            name="Acme",
            ruc="20123456789",
            plan="starter",
            status="trial",
            created_by=staff_user,
        )
        assert isinstance(tenant.id, uuid.UUID)
```

- [ ] **Step 2.3: Run the tests — they should fail (no Tenant model yet)**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_tenant_model.py -v
```

Expected: `ImportError: cannot import name 'Tenant' from 'apps.tenancy.models'` or similar — confirms the test file is properly discovered.

- [ ] **Step 2.4: Create `apps/tenancy/models/__init__.py` (empty for now)**

```python
# apps/api/apps/tenancy/models/__init__.py
```

- [ ] **Step 2.5: Create `apps/tenancy/models/tenant.py`**

```python
"""Tenant model — the SaaS subscriber entity.

A Tenant represents one paying customer of VYNTIA. It owns the subdomain
(`<slug>.vyntia.pe`), plan tier, lifecycle status, and trial window. All
tenant-scoped business data (employees, contracts, payroll, etc.) FKs to
this entity in C.1.
"""

import uuid

from django.db import models


PLAN_CHOICES = [
    ("starter", "Starter"),
    ("pro", "Pro"),
    ("enterprise", "Enterprise"),
    ("govtech", "GovTech"),
]

STATUS_CHOICES = [
    ("trial", "Trial"),
    ("active", "Active"),
    ("suspended", "Suspended"),
    ("cancelled", "Cancelled"),
]


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=63, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    ruc = models.CharField(max_length=11)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    max_users = models.IntegerField(default=10)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="tenants_created",
    )

    class Meta:
        db_table = "tenancy_tenant"
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status", "plan"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.slug})"
```

- [ ] **Step 2.6: Re-export from `models/__init__.py`**

Update `apps/api/apps/tenancy/models/__init__.py`:

```python
"""Tenancy models — re-exported for clean imports.

Usage: `from apps.tenancy.models import Tenant`
"""

from apps.tenancy.models.tenant import Tenant

__all__ = ["Tenant"]
```

- [ ] **Step 2.7: Generate the initial migration**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations tenancy --settings=vyntia.settings.development
```

Expected: Creates `apps/tenancy/migrations/0001_initial.py` with one operation: `CreateModel('Tenant', ...)`.

- [ ] **Step 2.8: Apply the migration**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate tenancy --settings=vyntia.settings.development
```

Expected: `Applying tenancy.0001_initial... OK`

- [ ] **Step 2.9: Run the tests — they should now pass**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_tenant_model.py -v
```

Expected: 5 tests passed.

- [ ] **Step 2.10: Run full test suite to verify no regression**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q
```

Expected: 161+5 = ≥166 passed, ≤8 failed, 3 skipped.

- [ ] **Step 2.11: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/tests/__init__.py \
        apps/api/apps/tenancy/tests/test_tenant_model.py \
        apps/api/apps/tenancy/models/__init__.py \
        apps/api/apps/tenancy/models/tenant.py \
        apps/api/apps/tenancy/migrations/0001_initial.py
git commit -m "feat(C0): add Tenant model with TDD tests"
```

---

## Task 3: `TenantMembership` model — TDD

**Files:**
- Create: `apps/api/apps/tenancy/tests/test_membership_model.py`
- Create: `apps/api/apps/tenancy/models/membership.py`
- Modify: `apps/api/apps/tenancy/models/__init__.py`
- Create: `apps/api/apps/tenancy/migrations/0002_tenantmembership.py` (auto-generated)

- [ ] **Step 3.1: Write the failing test**

Create `apps/api/apps/tenancy/tests/test_membership_model.py`:

```python
"""Tests for the TenantMembership model."""

import pytest
from django.db import IntegrityError

from apps.tenancy.models import Tenant, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme",
        name="Acme",
        ruc="20123456789",
        plan="starter",
        status="active",
        created_by=staff_user,
    )


@pytest.fixture
def member_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@acme.com", password="x"
    )


@pytest.mark.django_db
class TestTenantMembershipModel:
    def test_create_membership(self, tenant, member_user):
        membership = TenantMembership.objects.create(
            tenant=tenant,
            user=member_user,
            role="admin",
            status="active",
        )
        assert membership.id is not None
        assert membership.tenant == tenant
        assert membership.user == member_user
        assert membership.role == "admin"
        assert membership.status == "active"
        assert membership.invited_at is not None
        assert membership.joined_at is None
        assert membership.invited_by is None

    def test_unique_constraint_tenant_user(self, tenant, member_user):
        TenantMembership.objects.create(
            tenant=tenant, user=member_user, role="admin", status="active"
        )
        with pytest.raises(IntegrityError):
            TenantMembership.objects.create(
                tenant=tenant,  # same tenant
                user=member_user,  # same user
                role="member",
                status="active",
            )

    def test_same_user_different_tenants_allowed(self, tenant, member_user, staff_user):
        """A user can be member of multiple tenants — the unique is composite."""
        TenantMembership.objects.create(
            tenant=tenant, user=member_user, role="admin", status="active"
        )
        other_tenant = Tenant.objects.create(
            slug="beta",
            name="Beta",
            ruc="20999999999",
            plan="pro",
            status="active",
            created_by=staff_user,
        )
        m2 = TenantMembership.objects.create(
            tenant=other_tenant,
            user=member_user,
            role="member",
            status="active",
        )
        assert m2.id is not None

    def test_str_representation(self, tenant, member_user):
        membership = TenantMembership.objects.create(
            tenant=tenant, user=member_user, role="admin", status="active"
        )
        assert str(membership) == f"{member_user.username} @ acme (admin)"
```

- [ ] **Step 3.2: Run the test — should fail (no TenantMembership)**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_membership_model.py -v
```

Expected: ImportError on `TenantMembership`.

- [ ] **Step 3.3: Create `apps/tenancy/models/membership.py`**

```python
"""TenantMembership — the M2M between identity.User (global) and Tenant.

A user can be a member of multiple tenants with different roles in each.
The role here is the *SaaS-level* role (owner/admin/member), distinct from
HR-level roles (Empleado, Jefe de Area, etc.) which live in identity.Role.
"""

import uuid

from django.db import models


ROLE_CHOICES = [
    ("owner", "Owner"),    # tenant root admin (cannot be removed)
    ("admin", "Admin"),    # full access except billing/cancel
    ("member", "Member"),  # standard user (HR roles still apply on top)
]

STATUS_CHOICES = [
    ("invited", "Invited"),
    ("active", "Active"),
    ("suspended", "Suspended"),
]


class TenantMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        "identity.User",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(
        "identity.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memberships_invited",
    )

    class Meta:
        db_table = "tenancy_tenantmembership"
        verbose_name = "Tenant Membership"
        verbose_name_plural = "Tenant Memberships"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "user"],
                name="unique_tenant_user_membership",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["tenant", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} @ {self.tenant.slug} ({self.role})"
```

- [ ] **Step 3.4: Re-export from `models/__init__.py`**

Replace the content of `apps/api/apps/tenancy/models/__init__.py`:

```python
"""Tenancy models — re-exported for clean imports.

Usage: `from apps.tenancy.models import Tenant, TenantMembership`
"""

from apps.tenancy.models.tenant import Tenant
from apps.tenancy.models.membership import TenantMembership

__all__ = ["Tenant", "TenantMembership"]
```

- [ ] **Step 3.5: Make and apply migration**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations tenancy --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate tenancy --settings=vyntia.settings.development
```

Expected: creates `0002_tenantmembership.py`, applies cleanly.

- [ ] **Step 3.6: Run tests — should pass**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_membership_model.py -v
```

Expected: 4 tests passed.

- [ ] **Step 3.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/tests/test_membership_model.py \
        apps/api/apps/tenancy/models/membership.py \
        apps/api/apps/tenancy/models/__init__.py \
        apps/api/apps/tenancy/migrations/0002_tenantmembership.py
git commit -m "feat(C0): add TenantMembership model with TDD tests"
```

---

## Task 4: `TenantInvitation` model — TDD

**Files:**
- Create: `apps/api/apps/tenancy/tests/test_invitation_model.py`
- Create: `apps/api/apps/tenancy/models/invitation.py`
- Modify: `apps/api/apps/tenancy/models/__init__.py`
- Create: `apps/api/apps/tenancy/migrations/0003_tenantinvitation.py`

- [ ] **Step 4.1: Write the failing test**

Create `apps/api/apps/tenancy/tests/test_invitation_model.py`:

```python
"""Tests for the TenantInvitation model."""

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.tenancy.models import Tenant, TenantInvitation


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme",
        name="Acme",
        ruc="20123456789",
        plan="starter",
        status="trial",
        created_by=staff_user,
    )


@pytest.mark.django_db
class TestTenantInvitationModel:
    def test_create_invitation(self, tenant, staff_user):
        expires = timezone.now() + timedelta(days=7)
        inv = TenantInvitation.objects.create(
            tenant=tenant,
            email="ceo@acme.com",
            token="signed.jwt.token.abc123",
            role="owner",
            expires_at=expires,
            created_by=staff_user,
        )
        assert inv.id is not None
        assert inv.tenant == tenant
        assert inv.email == "ceo@acme.com"
        assert inv.token == "signed.jwt.token.abc123"
        assert inv.role == "owner"
        assert inv.expires_at == expires
        assert inv.accepted_at is None
        assert inv.created_at is not None

    def test_token_must_be_unique(self, tenant, staff_user):
        TenantInvitation.objects.create(
            tenant=tenant,
            email="a@acme.com",
            token="same-token",
            role="admin",
            expires_at=timezone.now() + timedelta(days=7),
            created_by=staff_user,
        )
        with pytest.raises(IntegrityError):
            TenantInvitation.objects.create(
                tenant=tenant,
                email="b@acme.com",
                token="same-token",  # same token
                role="member",
                expires_at=timezone.now() + timedelta(days=7),
                created_by=staff_user,
            )

    def test_str_representation(self, tenant, staff_user):
        inv = TenantInvitation.objects.create(
            tenant=tenant,
            email="ceo@acme.com",
            token="t1",
            role="owner",
            expires_at=timezone.now() + timedelta(days=7),
            created_by=staff_user,
        )
        assert str(inv) == "ceo@acme.com → acme (owner)"
```

- [ ] **Step 4.2: Run test — should fail**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_invitation_model.py -v
```

Expected: ImportError on `TenantInvitation`.

- [ ] **Step 4.3: Create `apps/tenancy/models/invitation.py`**

```python
"""TenantInvitation — pending invitation to join a tenant.

When Vyntia staff provisions a tenant, a TenantInvitation is created with a
signed token. The invited admin clicks the activation link, which creates
their User (or links existing) and the corresponding TenantMembership, then
sets `accepted_at` on the invitation.
"""

import uuid

from django.db import models

from apps.tenancy.models.membership import ROLE_CHOICES


class TenantInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    email = models.EmailField()
    token = models.CharField(max_length=512, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="invitations_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenancy_tenantinvitation"
        verbose_name = "Tenant Invitation"
        verbose_name_plural = "Tenant Invitations"
        indexes = [
            models.Index(fields=["email", "tenant"]),
            models.Index(fields=["token"]),
        ]

    def __str__(self):
        return f"{self.email} → {self.tenant.slug} ({self.role})"
```

- [ ] **Step 4.4: Re-export from `models/__init__.py`**

```python
"""Tenancy models — re-exported for clean imports."""

from apps.tenancy.models.tenant import Tenant
from apps.tenancy.models.membership import TenantMembership
from apps.tenancy.models.invitation import TenantInvitation

__all__ = ["Tenant", "TenantMembership", "TenantInvitation"]
```

- [ ] **Step 4.5: Make and apply migration**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations tenancy --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate tenancy --settings=vyntia.settings.development
```

- [ ] **Step 4.6: Run tests — should pass**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_invitation_model.py -v
```

Expected: 3 tests passed.

- [ ] **Step 4.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/tests/test_invitation_model.py \
        apps/api/apps/tenancy/models/invitation.py \
        apps/api/apps/tenancy/models/__init__.py \
        apps/api/apps/tenancy/migrations/0003_tenantinvitation.py
git commit -m "feat(C0): add TenantInvitation model with TDD tests"
```

---

## Task 5: `SupportSession` model — TDD

**Files:**
- Create: `apps/api/apps/tenancy/tests/test_support_session_model.py`
- Create: `apps/api/apps/tenancy/models/support_session.py`
- Modify: `apps/api/apps/tenancy/models/__init__.py`
- Create: `apps/api/apps/tenancy/migrations/0004_supportsession.py`

- [ ] **Step 5.1: Write the failing test**

Create `apps/api/apps/tenancy/tests/test_support_session_model.py`:

```python
"""Tests for the SupportSession model.

SupportSession audits Vyntia staff impersonating tenant users for support.
Every action taken during the session bumps actions_count.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.tenancy.models import SupportSession, Tenant


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def target_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@acme.com", password="x"
    )


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme",
        name="Acme",
        ruc="20123456789",
        plan="starter",
        status="active",
        created_by=staff_user,
    )


@pytest.mark.django_db
class TestSupportSessionModel:
    def test_create_session(self, staff_user, target_user, tenant):
        expires = timezone.now() + timedelta(hours=2)
        session = SupportSession.objects.create(
            staff_user=staff_user,
            target_user=target_user,
            tenant=tenant,
            reason="Ticket #1234 — error generating boletas",
            expires_at=expires,
        )
        assert session.id is not None
        assert session.staff_user == staff_user
        assert session.target_user == target_user
        assert session.tenant == tenant
        assert session.reason == "Ticket #1234 — error generating boletas"
        assert session.started_at is not None
        assert session.expires_at == expires
        assert session.ended_at is None
        assert session.actions_count == 0

    def test_actions_count_increments(self, staff_user, target_user, tenant):
        session = SupportSession.objects.create(
            staff_user=staff_user,
            target_user=target_user,
            tenant=tenant,
            reason="x",
            expires_at=timezone.now() + timedelta(hours=2),
        )
        session.actions_count += 1
        session.save()
        session.refresh_from_db()
        assert session.actions_count == 1

    def test_str_representation(self, staff_user, target_user, tenant):
        session = SupportSession.objects.create(
            staff_user=staff_user,
            target_user=target_user,
            tenant=tenant,
            reason="x",
            expires_at=timezone.now() + timedelta(hours=2),
        )
        assert str(session) == f"staff impersonating maria @ acme"
```

- [ ] **Step 5.2: Run — should fail**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_support_session_model.py -v
```

Expected: ImportError on `SupportSession`.

- [ ] **Step 5.3: Create `apps/tenancy/models/support_session.py`**

```python
"""SupportSession — audit trail of Vyntia staff impersonating tenant users.

Created when Vyntia staff opens a support session for a tenant user (typically
in response to a ticket). The session token grants temporary access (default
2h) with elevated audit trail. Every mutation in this session increments
actions_count. The customer can review all support sessions touching their
tenant — required for SERVIR / public-sector compliance.
"""

import uuid

from django.db import models


class SupportSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="support_sessions_initiated",
    )
    target_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="support_sessions_received",
    )
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="support_sessions",
    )
    reason = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    actions_count = models.IntegerField(default=0)

    class Meta:
        db_table = "tenancy_supportsession"
        verbose_name = "Support Session"
        verbose_name_plural = "Support Sessions"
        indexes = [
            models.Index(fields=["tenant", "started_at"]),
            models.Index(fields=["staff_user", "started_at"]),
        ]

    def __str__(self):
        return (
            f"{self.staff_user.username} impersonating "
            f"{self.target_user.username} @ {self.tenant.slug}"
        )
```

- [ ] **Step 5.4: Re-export from `models/__init__.py`**

```python
"""Tenancy models — re-exported for clean imports."""

from apps.tenancy.models.tenant import Tenant
from apps.tenancy.models.membership import TenantMembership
from apps.tenancy.models.invitation import TenantInvitation
from apps.tenancy.models.support_session import SupportSession

__all__ = ["Tenant", "TenantMembership", "TenantInvitation", "SupportSession"]
```

- [ ] **Step 5.5: Make and apply migration**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations tenancy --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate tenancy --settings=vyntia.settings.development
```

- [ ] **Step 5.6: Run tests — should pass**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_support_session_model.py -v
```

Expected: 3 tests passed.

- [ ] **Step 5.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/tests/test_support_session_model.py \
        apps/api/apps/tenancy/models/support_session.py \
        apps/api/apps/tenancy/models/__init__.py \
        apps/api/apps/tenancy/migrations/0004_supportsession.py
git commit -m "feat(C0): add SupportSession model with TDD tests"
```

---

## Task 6: Django admin registrations

**Files:**
- Create: `apps/api/apps/tenancy/admin.py`

- [ ] **Step 6.1: Create `apps/tenancy/admin.py`**

```python
"""Django admin registrations for tenancy models.

Used by Vyntia staff at /admin/ for emergency operations. The full-featured
provisioning UI lives at admin.vyntia.pe (built in C.7).
"""

from django.contrib import admin

from apps.tenancy.models import (
    SupportSession,
    Tenant,
    TenantInvitation,
    TenantMembership,
)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "ruc", "plan", "status", "created_at")
    list_filter = ("plan", "status")
    search_fields = ("slug", "name", "ruc")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "tenant", "role", "status", "invited_at", "joined_at")
    list_filter = ("role", "status")
    search_fields = ("user__username", "user__email", "tenant__slug", "tenant__name")
    readonly_fields = ("id", "invited_at")
    ordering = ("-invited_at",)


@admin.register(TenantInvitation)
class TenantInvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "tenant", "role", "expires_at", "accepted_at", "created_at")
    list_filter = ("role",)
    search_fields = ("email", "tenant__slug", "tenant__name")
    readonly_fields = ("id", "token", "created_at")
    ordering = ("-created_at",)


@admin.register(SupportSession)
class SupportSessionAdmin(admin.ModelAdmin):
    list_display = (
        "staff_user",
        "target_user",
        "tenant",
        "started_at",
        "expires_at",
        "ended_at",
        "actions_count",
    )
    search_fields = (
        "staff_user__username",
        "target_user__username",
        "tenant__slug",
        "reason",
    )
    readonly_fields = ("id", "started_at", "actions_count")
    ordering = ("-started_at",)
```

- [ ] **Step 6.2: Verify Django check still clean**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 6.3: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/admin.py
git commit -m "feat(C0): register tenancy models in Django admin"
```

---

## Task 7: pyproject.toml package list update

**Files:**
- Modify: `apps/api/pyproject.toml`

- [ ] **Step 7.1: Inspect current packages list**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['tool']['setuptools'].get('packages'))"
```

Expected output: a list containing `"vyntia"`, `"api"`, `"apps"`, `"apps.core"`, `"apps.identity"`, ... (one per app).

- [ ] **Step 7.2: Add `apps.tenancy` to the packages list**

In `apps/api/pyproject.toml`, find the `packages = [...]` line under `[tool.setuptools]` and add `"apps.tenancy"` to the list, alphabetized with the other `apps.X` entries.

Example before:
```toml
packages = ["vyntia", "api", "apps", "apps.core", "apps.contracts", "apps.documents", "apps.employees", "apps.identity", "apps.onboarding", "apps.organization", "apps.payroll", "apps.time_off"]
```

After:
```toml
packages = ["vyntia", "api", "apps", "apps.core", "apps.contracts", "apps.documents", "apps.employees", "apps.identity", "apps.onboarding", "apps.organization", "apps.payroll", "apps.tenancy", "apps.time_off"]
```

- [ ] **Step 7.3: Reinstall the package in editable mode (picks up the new package)**

```bash
cd D:/VYNTIA
D:/VYNTIA/.venv/Scripts/python.exe -m pip install -e "apps/api[dev]"
```

Expected: clean install, no errors.

- [ ] **Step 7.4: Verify imports still work**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -c "from apps.tenancy.models import Tenant, TenantMembership, TenantInvitation, SupportSession; print('imports OK')"
```

Expected: `imports OK`

- [ ] **Step 7.5: Commit**

```bash
cd D:/VYNTIA
git add apps/api/pyproject.toml
git commit -m "chore(C0): add apps.tenancy to pyproject.toml packages list"
```

---

## Task 8: Final verification + merge

- [ ] **Step 8.1: Run the full test suite**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q
```

Expected: ≥176 passed (161 baseline + ~15 new tenancy tests), ≤8 failed (pre-existing), 3 skipped.

- [ ] **Step 8.2: Django system check + missing migrations check**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations --dry-run --check --settings=vyntia.settings.development
```

Expected: `System check identified no issues (0 silenced).` and `No changes detected`.

- [ ] **Step 8.3: Frontend baselines (sanity — no frontend changes in C.0)**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npm test -- --run 2>&1 | tail -5
```

Expected: build exit 0, vitest 7 passed.

- [ ] **Step 8.4: Verify branch state**

```bash
cd D:/VYNTIA
git log --oneline master..HEAD
```

Expected: 8 commits — one per task (Task 1 chore, Tasks 2-5 feat, Task 6 feat, Task 7 chore, no separate commit for Task 8 since it's verification only).

- [ ] **Step 8.5: Update C master roadmap to mark C.0 done**

In `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`, find the C.0 row in the sub-layer table and add to the "Detailed plan" cell:

```
`2026-05-09-vyntia-C0-tenancy-foundations.md` ✅ merged YYYY-MM-DD
```

(Replace `YYYY-MM-DD` with the merge date.)

- [ ] **Step 8.6: Commit roadmap update**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md
git commit -m "docs(C0): mark C.0 done in master roadmap"
```

- [ ] **Step 8.7: Merge C.0 to master**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/C0-tenancy-foundations \
  -m "Merge C.0: tenancy foundations (4 models + admin + tests)"
```

Expected: clean merge, no conflicts.

- [ ] **Step 8.8: Verify post-merge state**

```bash
cd D:/VYNTIA
git log --oneline -3
git status
```

Expected: HEAD is on the merge commit, working tree clean.

---

## Self-Review

### Spec coverage check

| Spec § 3.1 requirement | Covered by task |
|---|---|
| `Tenant` model with all fields | Task 2 |
| Composite unique on `ruc` (only for trial/active) | **NOT in C.0** — deferred. Task 2 uses simple `ruc` field without partial unique. The partial unique constraint adds complexity (Django `Q(...)` condition); keep simple in C.0, add in C.5 (admin API does dedup check on create). |
| Indexes on slug + (status, plan) | Task 2 — Meta.indexes |
| `TenantMembership` with M2M + composite unique | Task 3 |
| `TenantInvitation` with token + expires_at | Task 4 |
| `SupportSession` audit model | Task 5 |
| Django admin | Task 6 |
| INSTALLED_APPS registration | Task 1 |
| `apps.tenancy` in pyproject | Task 7 |

### Placeholder scan

- No "TBD" or "TODO" — verified.
- All code blocks contain complete, runnable code.
- One spec deviation (partial unique on `ruc`) — explicitly noted above with rationale.

### Type consistency

- `ROLE_CHOICES` is defined in `membership.py` and imported by `invitation.py` (Task 4 Step 4.3). DRY: single source of truth for roles.
- `STATUS_CHOICES` for memberships is local to `membership.py`. The Tenant has its own `STATUS_CHOICES` in `tenant.py` with different values. Names match within their files; no cross-file naming clashes.
- `db_table` names are consistent: `tenancy_tenant`, `tenancy_tenantmembership`, `tenancy_tenantinvitation`, `tenancy_supportsession`. Match Django default and the spec § 4.2 RLS examples.

### Out of scope (intentionally deferred)

- `tenant_id` FK on existing models (C.1)
- RLS policies (C.2)
- TenantManager / UnsafeManager (C.3)
- Subdomain middleware (C.3)
- Login flow (C.4)
- Provisioning API (C.5)
- Frontend (C.6, C.7)
- Isolation tests (C.8)

---

**Plan complete.** When executed, C.0 ships ~15 new tests, 8 commits, 0 baseline regressions, ~600 LOC. Ready for the C.1 plan to be generated after merge.
