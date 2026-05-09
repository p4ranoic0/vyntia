# Sub-Project C — Multi-Tenancy + Row-Level Security

> Design spec. Brainstormed 2026-05-09. Foundation sub-project A complete (tag `foundation-complete`).
> Implementation begins after this spec is approved and a writing-plans pass produces the plan files.

---

## 1. Context

VYNTIA is a multi-tenant HR SaaS for Peru. After Foundation (sub-project A — rebrand, restructure, Django app split), the codebase is single-tenant: one DB, one company, one set of users. Sub-project C transforms this into a true multi-tenant SaaS where multiple unrelated companies share infrastructure with cryptographically-enforced data isolation.

**Why C is the critical path:** every commercial sub-project (B, D, S, all tier-unlocking modules) assumes tenant boundaries. Without C, VYNTIA cannot legally onboard a second client.

**Source decisions (locked from brainstorming 2026-05-09):**

| Decision | Choice |
|---|---|
| Scope | Full SaaS MVP — admin-provisioned tenants, manual billing, full operational tooling |
| Tenant resolution | Subdomain — `acme.vyntia.pe` (wildcard DNS `*.vyntia.pe`) |
| Identity model | Global email uniqueness — one User can be member of multiple Tenants (Slack/Linear pattern) |
| Billing in C | None — deferred to sub-project S. Tenants created/managed manually by Vyntia staff |
| Tenant creation | Admin-provisioned only — no public signup. Vyntia staff creates Tenant in `admin.vyntia.pe`, system emails activation link to first admin |
| Existing data | Discarded (was dev/staging). C ships on a blank slate DB — no retrofit migration needed |
| Tenancy implementation | PostgreSQL RLS native + Django middleware + custom managers (defense in depth — see § 5) |

**Out of scope for C (explicitly):**
- Public self-service signup (deferred — possibly never; B2B may stay sales-led)
- Stripe/Culqi billing integration (sub-project S)
- Per-tenant feature flags / plan-based module gating (deferred — placeholder fields only)
- DB-per-tenant tier (Enterprise/GovTech upsell — separate future sub-project after C ships)
- Custom domains (`hr.acme.com` instead of `acme.vyntia.pe`) — future
- SCIM / SSO integration — future
- Audit log retention beyond 90 days — future

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Wildcard DNS: *.vyntia.pe  →  same load balancer / app server   │
│  TLS: wildcard cert *.vyntia.pe + cert vyntia.pe                 │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Django request lifecycle                                        │
│                                                                  │
│  1. TenantMiddleware                                             │
│     ├─ Parse Host header → subdomain                             │
│     ├─ If reserved (admin/app/www/api) → branch to special flow  │
│     └─ Else: lookup Tenant by slug → request.tenant + ctx var    │
│                                                                  │
│  2. AuthMiddleware (extended)                                    │
│     ├─ Decode JWT, validate JWT.tenant_id == request.tenant.id   │
│     └─ Set request.user                                          │
│                                                                  │
│  3. RLSMiddleware (after auth, before view)                      │
│     └─ SET LOCAL app.tenant_id = '<uuid>' on the DB connection   │
│                                                                  │
│  4. View / DRF ViewSet                                           │
│     └─ ORM via TenantManager → filter(tenant=ctx.tenant) auto    │
│                                                                  │
│  5. PostgreSQL RLS policies                                      │
│     └─ Last line of defense: WHERE tenant_id = current_setting() │
└──────────────────────────────────────────────────────────────────┘
```

**Reserved subdomains (never resolved as tenants):**

| Subdomain | Purpose | Auth | DB role |
|---|---|---|---|
| `vyntia.pe`, `www.vyntia.pe` | Marketing / landing | None | (static, no DB) |
| `app.vyntia.pe` | Workspace switcher (multi-tenant users) | JWT (global session, 5 min TTL) | `vyntia_app` (no tenant ctx) |
| `admin.vyntia.pe` | Vyntia staff panel | JWT + `is_vyntia_staff=True` | `vyntia_admin` (BYPASSRLS) |
| `api.vyntia.pe` | Public API alias (future, post-C) | — | — |
| `acme.vyntia.pe` | Tenant `acme` | JWT with `tenant_id == acme.id` | `vyntia_app` |

Reserved-subdomain list also blocks tenants from claiming them as `slug`: `admin`, `app`, `www`, `api`, `docs`, `status`, `blog`, `mail`, `support`, `help`, `vyntia`.

---

## 3. Data model

### 3.1 New app: `apps/tenancy/`

```python
# apps/tenancy/models/tenant.py
class Tenant(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = SlugField(max_length=63, unique=True, db_index=True)
    name = CharField(max_length=200)
    ruc = CharField(max_length=11)
    plan = CharField(choices=[
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
        ('govtech', 'GovTech'),
    ])
    status = CharField(choices=[
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ])
    trial_ends_at = DateTimeField(null=True, blank=True)
    max_users = IntegerField(default=10)   # plan-based, enforced in S
    cancelled_at = DateTimeField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    created_by = ForeignKey('identity.User', on_delete=PROTECT, related_name='tenants_created')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['ruc'], name='unique_tenant_ruc',
                             condition=Q(status__in=['trial', 'active'])),
        ]
        indexes = [
            Index(fields=['slug']),
            Index(fields=['status', 'plan']),
        ]
```

```python
# apps/tenancy/models/membership.py
class TenantMembership(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = ForeignKey(Tenant, on_delete=CASCADE, related_name='memberships')
    user = ForeignKey('identity.User', on_delete=CASCADE, related_name='memberships')
    role = CharField(choices=[
        ('owner', 'Owner'),       # tenant root admin (cannot be removed)
        ('admin', 'Admin'),       # full access except billing/cancel
        ('member', 'Member'),     # standard user (HR roles still apply on top)
    ])
    status = CharField(choices=[
        ('invited', 'Invited'),   # invitation sent, not yet accepted
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ])
    invited_at = DateTimeField(auto_now_add=True)
    joined_at = DateTimeField(null=True, blank=True)
    invited_by = ForeignKey('identity.User', on_delete=SET_NULL, null=True,
                            related_name='memberships_invited')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['tenant', 'user'], name='unique_tenant_user'),
        ]
```

```python
# apps/tenancy/models/invitation.py
class TenantInvitation(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = ForeignKey(Tenant, on_delete=CASCADE, related_name='invitations')
    email = EmailField()
    token = CharField(max_length=512, unique=True)   # signed JWT
    role = CharField(choices=TenantMembership.ROLE_CHOICES)
    expires_at = DateTimeField()
    accepted_at = DateTimeField(null=True, blank=True)
    created_by = ForeignKey('identity.User', on_delete=PROTECT)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [Index(fields=['email', 'tenant'])]
```

```python
# apps/tenancy/models/support_session.py
class SupportSession(models.Model):
    """Audit trail of Vyntia staff impersonating tenant users for support."""
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_user = ForeignKey('identity.User', on_delete=PROTECT,
                            related_name='support_sessions_initiated')
    target_user = ForeignKey('identity.User', on_delete=PROTECT,
                             related_name='support_sessions_received')
    tenant = ForeignKey(Tenant, on_delete=PROTECT)
    reason = TextField()
    started_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()       # 2h default
    ended_at = DateTimeField(null=True, blank=True)
    actions_count = IntegerField(default=0)   # mutations during session
```

### 3.2 Changes to existing apps

Every business model gains a `tenant` FK.

**Affected apps and models:**

| App | Models | tenant_id added? |
|---|---|---|
| `identity` | User | **No** — global identity |
| `identity` | Module | **No** — Vyntia-global menu structure |
| `identity` | Role, Permission, RolePermission, UserRole, ModulePermission | Yes |
| `organization` | Department, CompanyConfig, LocationHistory | Yes |
| `employees` | Employee, FamilyData, AcademicData, CourseCertification | Yes |
| `contracts` | Contract, ContractAmendment, EmploymentData | Yes |
| `documents` | DocumentFile, DocumentTemplate (custom only) | Yes |
| `payroll` | All 9 models | Yes |
| `time_off` | All 5 models | Yes |
| `onboarding` | OnboardingProcess | Yes |

**Pattern:** abstract base for new models, explicit field for retrofit.

```python
# apps/core/models.py (new)
class TenantScopedModel(models.Model):
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=PROTECT, db_index=True)

    class Meta:
        abstract = True
```

Existing models receive `tenant = ForeignKey(...)` directly via migration. They cannot retroactively inherit from `TenantScopedModel` without migration churn.

### 3.3 Composite unique constraints

Migration changes simple uniques to composite `(tenant, field)`:

| Model | Old constraint | New constraint |
|---|---|---|
| `Employee.numero_documento` | unique | `unique_together = ('tenant', 'numero_documento')` |
| `Role.nombre_rol` | unique | `unique_together = ('tenant', 'nombre_rol')` |
| `Permission.nombre_permiso` | unique | `unique_together = ('tenant', 'nombre_permiso')` |
| `Department.siglas_area` | unique | `unique_together = ('tenant', 'siglas_area')` |
| `CompanyConfig.ruc` | unique (singleton) | `unique('tenant')` — exactly one config per tenant |
| `Contract.numero_contrato` | unique | `unique_together = ('tenant', 'numero_contrato')` |

**Globals stay unique:**
- `User.username` — global identity
- `User.email` — global identity (case-insensitive)

### 3.4 `CompanyConfig` migration

Currently singleton (`pk=1` hardcoded with `get_config()` classmethod). Migrates to:

```python
class CompanyConfig(TenantScopedModel):
    # All existing fields preserved
    # tenant FK added
    # pk=1 hardcoding removed

    @classmethod
    def get_config(cls, tenant):
        return cls.objects.get(tenant=tenant)
```

All `CompanyConfig.get_config()` callers must pass tenant. The middleware-resolved `request.tenant` provides it; in services `tenant=ctx.current_tenant()`.

---

## 4. PostgreSQL RLS layer

### 4.1 Roles

```sql
-- Setup script run once per environment (run by DBA / IaC, not Django)
CREATE ROLE vyntia_app NOLOGIN;
CREATE ROLE vyntia_admin NOLOGIN BYPASSRLS;
CREATE ROLE vyntia_readonly NOLOGIN;

-- Application user (used by Django in production)
CREATE USER vyntia_django WITH PASSWORD '<from secrets manager>';
GRANT vyntia_app TO vyntia_django;

-- Admin user (used by management commands, migrations, ETL)
CREATE USER vyntia_migrator WITH PASSWORD '<from secrets manager>';
GRANT vyntia_admin TO vyntia_migrator;

-- Readonly user (used by reporting, analytics)
CREATE USER vyntia_reporter WITH PASSWORD '<from secrets manager>';
GRANT vyntia_readonly TO vyntia_reporter;
```

`settings.DATABASES['default']` uses `vyntia_django`. A separate `MIGRATION_DATABASE_URL` env var with `vyntia_migrator` credentials is used by `manage.py migrate` and other admin commands. The `CONNECTIONS` dict in production splits these.

### 4.2 Policies

```sql
-- Applied via apps.tenancy.management.commands.setup_rls
ALTER TABLE employees_employee ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees_employee FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON employees_employee
  FOR ALL
  TO vyntia_app
  USING (tenant_id = current_setting('app.tenant_id', TRUE)::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', TRUE)::uuid);

GRANT SELECT, INSERT, UPDATE, DELETE ON employees_employee TO vyntia_app;
GRANT SELECT ON employees_employee TO vyntia_readonly;
```

`FORCE ROW LEVEL SECURITY` ensures even the table owner cannot bypass policies. Only `vyntia_admin` (BYPASSRLS) sees cross-tenant.

`current_setting('app.tenant_id', TRUE)` — the `TRUE` second argument means "missing setting returns NULL" (no error). The policy then evaluates `tenant_id = NULL` which fails — defensive default.

**Special case — `tenancy_tenantmembership` policy:** a user must be able to list their own memberships from the workspace switcher (`app.vyntia.pe`), which has no tenant context. The policy is widened with a second clause keyed on `app.user_id`:

```sql
CREATE POLICY membership_isolation ON tenancy_tenantmembership
  FOR ALL TO vyntia_app
  USING (
    tenant_id = current_setting('app.tenant_id', TRUE)::uuid
    OR
    user_id = current_setting('app.user_id', TRUE)::uuid
  )
  WITH CHECK (tenant_id = current_setting('app.tenant_id', TRUE)::uuid);
```

The `WITH CHECK` clause stays strict — INSERTs/UPDATEs still require an active tenant context. Only SELECT widens. Middleware on `app.vyntia.pe` sets `app.user_id` but not `app.tenant_id`; on tenant subdomains both are set.

The same policy pattern applies to `tenancy_tenant` (so a user can list their tenants by RUC/slug for the switcher view).

### 4.3 Management command

```python
# apps/tenancy/management/commands/setup_rls.py
class Command(BaseCommand):
    """Idempotent. Reads model registry, applies RLS to every tenant-scoped table."""
    
    def handle(self, *args, **options):
        for model in self._tenant_scoped_models():
            self._enable_rls(model)
            self._create_policy(model)
            self._grant_privileges(model)
```

Run on every deploy after `manage.py migrate`. Idempotent — re-applies safely.

### 4.4 Connection setup

```python
# apps/tenancy/middleware.py
class RLSMiddleware:
    def __call__(self, request):
        with transaction.atomic():
            with connection.cursor() as cur:
                if hasattr(request, 'tenant') and request.tenant is not None:
                    cur.execute("SET LOCAL app.tenant_id = %s", [str(request.tenant.id)])
                if hasattr(request, 'user') and request.user.is_authenticated:
                    cur.execute("SET LOCAL app.user_id = %s", [str(request.user.id)])
            return self.get_response(request)
```

Both session variables are independent: `app.tenant_id` enables tenant-scoped policies; `app.user_id` enables the user-scoped exception in `tenancy_tenantmembership` and `tenancy_tenant`. On reserved subdomains (`app.vyntia.pe`), only `app.user_id` is set; on tenant subdomains, both. On `admin.vyntia.pe`, neither is needed because the connection uses `vyntia_admin` (BYPASSRLS).

`SET LOCAL` is transaction-scoped — auto-resets when the request transaction commits/rolls back. No leak between requests.

**Threading note:** Django's request handling uses one DB connection per request (for sync views) or per-task (for async). `SET LOCAL` is safe in both because it's bound to the active transaction, not the connection.

---

## 5. Django ORM layer (TenantManager + ContextVar)

```python
# apps/tenancy/context.py
from contextvars import ContextVar
_current_tenant: ContextVar['Tenant | None'] = ContextVar('current_tenant', default=None)

def set_current_tenant(tenant): _current_tenant.set(tenant)
def get_current_tenant(): return _current_tenant.get()

@contextmanager
def tenant_context(tenant):
    token = _current_tenant.set(tenant)
    try: yield
    finally: _current_tenant.reset(token)
```

```python
# apps/tenancy/managers.py
class TenantManager(models.Manager):
    def get_queryset(self):
        tenant = get_current_tenant()
        if tenant is None:
            raise ImproperlyConfigured(
                f"{self.model.__name__}.objects requires tenant context. "
                f"Use {self.model.__name__}.unsafe for cross-tenant access."
            )
        return super().get_queryset().filter(tenant=tenant)

class UnsafeManager(models.Manager):
    """Cross-tenant access — only for admin commands, ETL, support tooling."""
    pass
```

Each tenant-scoped model:

```python
class Employee(TenantScopedModel):
    # ... fields ...
    objects = TenantManager()
    unsafe = UnsafeManager()
```

**Convention:** `Model.objects` is always tenant-scoped. `Model.unsafe` is the explicit escape hatch, named to make code review trivial.

---

## 6. Authentication flow

### 6.1 Login

```
POST acme.vyntia.pe/api/v1/auth/login/
{ email, password }

Backend:
  1. user = User.objects.get(email__iexact=email)        # global (User has no tenant)
  2. authenticate(user, password)                        # standard Django
  3. membership = TenantMembership.objects.get(          # tenant-scoped (RLS active)
        user=user,
        status='active',
     )
     # objects manager auto-filters tenant from RLS context — no explicit tenant arg needed
  4. if no membership: 403 "No tienes acceso a este workspace"
  5. issue JWT:
     {
       sub: user.id,
       tenant_id: request.tenant.id,
       tenant_slug: request.tenant.slug,
       membership_role: membership.role,
       exp: now + 1h,
     }
```

### 6.2 Per-request validation

```python
# apps/tenancy/middleware.py — TenantAuthMiddleware
class TenantAuthMiddleware:
    def __call__(self, request):
        token = self._extract_token(request)
        if token:
            payload = jwt.decode(token, ...)
            if payload['tenant_id'] != str(request.tenant.id):
                raise AuthenticationFailed("Token tenant mismatch")
            request.user = User.objects.get(id=payload['sub'])
        return self.get_response(request)
```

A token issued for `acme` cannot be replayed against `beta` even with the same user — the middleware enforces it.

### 6.3 Activation flow

```
POST acme.vyntia.pe/api/v1/auth/activate/
{ token, name, password }

Backend transaction:
  1. invitation = TenantInvitation.objects.get(           # RLS scopes to acme
        token=token,
        accepted_at__isnull=True,
        expires_at__gt=now(),
     )
  2. user, created = User.objects.get_or_create(          # global (User is not tenant-scoped)
        email=invitation.email,
        defaults={'name': name, ...},
     )
  3. user.set_password(password); user.save()
  4. TenantMembership.objects.create(                     # tenant inferred from RLS ctx
        user=user,
        role=invitation.role,
        status='active',
        joined_at=now(),
     )
  5. invitation.accepted_at = now(); invitation.save()
  6. issue JWT and return
```

### 6.4 Workspace switcher (`app.vyntia.pe`)

```
GET app.vyntia.pe/api/v1/workspaces/
Auth: global session JWT (no tenant_id claim)

Backend (no tenant context — app.vyntia.pe has request.tenant = None):
  TenantMembership.objects.unsafe.filter(           # explicit cross-tenant via UnsafeManager
      user=request.user,
      status='active',
  ).select_related('tenant')

Returns:
  [
    { tenant: 'acme', name: 'Acme Corp', plan: 'pro', role: 'admin' },
    { tenant: 'beta', name: 'Beta Ltd',  plan: 'starter', role: 'member' },
  ]

User clicks "Acme":
  POST app.vyntia.pe/api/v1/workspaces/acme/exchange/
  → Returns short-lived (5min) one-time exchange token
  → Frontend redirects to acme.vyntia.pe/auth/exchange?token=...
  → Tenant subdomain validates token, issues normal session JWT
```

The exchange token can only be redeemed once and only against the matching tenant subdomain.

The `unsafe.filter(user=request.user)` query is the *only* legitimate cross-tenant query in the user-facing path — justified because the user is asking "which tenants am I a member of?", which is intrinsically multi-tenant. To make this safe at the DB level without weakening RLS, the `TenantMembership` table has a dual-clause policy (see § 4.2 below) that also accepts `user_id = current_setting('app.user_id')`. The middleware sets `app.user_id` for `app.vyntia.pe` requests but not `app.tenant_id`, so the policy lets a user see only their own memberships and nothing else.

---

## 7. Provisioning (admin panel)

### 7.1 Endpoints

```
admin.vyntia.pe/api/admin/tenants/                     CRUD
admin.vyntia.pe/api/admin/tenants/{id}/suspend/        POST
admin.vyntia.pe/api/admin/tenants/{id}/cancel/         POST
admin.vyntia.pe/api/admin/tenants/{id}/invitations/    POST (re-invite)
admin.vyntia.pe/api/admin/tenants/{id}/audit/          GET
admin.vyntia.pe/api/admin/users/                       search
admin.vyntia.pe/api/admin/users/{id}/impersonate/      POST → SupportSession
admin.vyntia.pe/api/admin/support-sessions/            GET (audit log)
```

Permissions: `IsAuthenticated AND request.user.is_vyntia_staff`.

### 7.2 Create tenant

```python
POST /api/admin/tenants/
{
  slug: "acme",
  name: "Acme Corp S.A.C.",
  ruc: "20123456789",
  plan: "starter",
  trial_days: 30,
  admin_email: "ceo@acme.com",
  admin_name: "María Pérez",
}

Validation:
  - slug ∉ RESERVED_SUBDOMAINS
  - slug matches ^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$
  - slug not in use by existing Tenant
  - ruc 11 digits, not in use by trial/active tenant
  - admin_email valid + no existing TenantInvitation pending in this slug

Atomic transaction (using vyntia_admin role):
  1. tenant = Tenant.objects.unsafe.create(...)
  2. setup_tenant_seed(tenant):
       - default Roles (owner, admin, member)
       - default Permissions (per Roles spec)
       - default Module bindings (per plan)
  3. CompanyConfig.objects.unsafe.create(tenant=tenant, ruc=..., name=...)
  4. invitation = TenantInvitation.objects.unsafe.create(
        tenant=tenant, email=admin_email, role='owner',
        token=signed_jwt(7d), expires_at=now+7d
     )
  5. Send "Welcome to VYNTIA" email with activation_url

Response 201 with full tenant + invitation details
```

### 7.3 Impersonation (support tooling)

```
POST /api/admin/users/{user_id}/impersonate/
{ reason: "Ticket #1234 — usuario reporta error en boletas", tenant_id: "..." }

Creates SupportSession + issues JWT with claims:
  {
    sub: target_user.id,
    tenant_id: ...,
    impersonated_by: staff_user.id,
    support_session_id: ...,
    exp: now + 2h,
  }

Frontend behavior in tenant subdomain:
  - Always-visible banner: "🔍 Sesión de soporte Vyntia · staff_name"
  - Every mutation request logs to SupportSession.actions_count
  - SupportSession ends automatically at exp or via explicit logout
  - Customer can view all support sessions touching their tenant
    (transparency requirement for SERVIR clients)
```

---

## 8. Frontend

### 8.1 Tenant resolution (boot)

```typescript
// apps/web/src/shared/tenant/tenantContext.tsx
const RESERVED = new Set(['admin', 'app', 'www', 'api'])

function resolveTenantSlug(): TenantContext {
  const subdomain = window.location.host.split('.')[0]
  if (RESERVED.has(subdomain)) return { type: subdomain }
  return { type: 'tenant', slug: subdomain }
}
```

### 8.2 App entry routing

```tsx
<TenantProvider>
  {tenant.type === 'admin'  && <AdminApp />}
  {tenant.type === 'app'    && <WorkspaceSwitcher />}
  {tenant.type === 'tenant' && <TenantApp slug={tenant.slug} />}
  {tenant.type === 'www'    && <RedirectToMarketing />}
</TenantProvider>
```

### 8.3 New features

```
apps/web/src/features/
├── tenant-admin/         # admin.vyntia.pe — Vyntia staff only
├── workspace-switcher/   # app.vyntia.pe
└── tenancy/              # shared by all tenant subdomains
    ├── pages/{Activation,TenantSettings,Memberships}Page.tsx
    ├── components/{ImpersonationBanner,TenantBadge}.tsx
    └── services/tenancyService.ts
```

### 8.4 API client

`apiClient` baseURL stays as `/api` — the subdomain in the browser's URL is the source of tenant truth. Backend resolves it from `Host`. Frontend never passes tenant explicitly in a body or header (except for the workspace exchange endpoint).

A defensive interceptor cleans the token if `JWT.tenant_slug !== current host subdomain` (catches stale tokens after a workspace switch).

---

## 9. Testing

### 9.1 Pytest fixtures

```python
@pytest.fixture
def tenant_a(db): return Tenant.objects.unsafe.create(slug='test-a', ...)

@pytest.fixture
def tenant_b(db): return Tenant.objects.unsafe.create(slug='test-b', ...)

@pytest.fixture
def in_tenant_a(tenant_a):
    with tenant_context(tenant_a):
        with connection.cursor() as cur:
            cur.execute("SET LOCAL app.tenant_id = %s", [str(tenant_a.id)])
        yield tenant_a
```

### 9.2 Critical isolation tests (new test module `tests/test_tenant_isolation.py`)

```python
def test_orm_isolation_per_tenant(tenant_a, tenant_b):
    with tenant_context(tenant_a):
        Employee.objects.create(numero_documento='12345678', ...)
    with tenant_context(tenant_b):
        assert Employee.objects.filter(numero_documento='12345678').count() == 0

def test_rls_blocks_raw_sql(tenant_a, tenant_b):
    """Even raw SQL bypassing the ORM must be blocked by RLS."""
    with in_tenant_a:
        Employee.objects.create(...)
    with in_tenant_b, connection.cursor() as cur:
        cur.execute("SELECT id FROM employees_employee")
        assert cur.fetchall() == []

def test_unsafe_manager_sees_all(tenant_a, tenant_b):
    """The 'unsafe' escape hatch sees cross-tenant — used by admin commands."""
    Employee.objects.unsafe.create(tenant=tenant_a, ...)
    Employee.objects.unsafe.create(tenant=tenant_b, ...)
    assert Employee.unsafe.count() == 2

def test_jwt_token_cannot_be_used_across_tenants(tenant_a, tenant_b, api_client):
    token = login_as(api_client, tenant_a, user)
    api_client.host = 'test-b.vyntia.pe'
    response = api_client.get('/api/v1/employees/', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401
```

### 9.3 Playwright E2E (new file `tests/e2e/tenant-isolation.test.js`)

- User logged into `acme.vyntia.pe` cannot access `beta.vyntia.pe` resources by changing URL slug
- Workspace switcher correctly lists only user's active memberships
- Impersonation banner appears on every page during a SupportSession

### 9.4 Baselines after C ships

- pytest: target **>200 passed** (161 current + ~40 new tenancy + ~5 isolation)
- vitest: target **>20 passed**
- Build clean, tsc 1 pre-existing error
- New CI job: `rls-policy-audit` — fails if any tenant-scoped table lacks an RLS policy

---

## 10. Sub-layer decomposition (sub-PRs)

Each sub-layer is a separate branch and PR, mergeable independently. Order is mostly sequential; C.6 and C.7 can run in parallel after C.4 lands.

| Sub | Branch | Scope |
|-----|--------|-------|
| **C.0** | `vyntia/C0-tenancy-foundations` | New app `apps/tenancy` with `Tenant`, `TenantMembership`, `TenantInvitation`, `SupportSession` models + Django admin. No `tenant_id` on other apps yet. |
| **C.1** | `vyntia/C1-tenant-id-migration` | Migration: add `tenant = FK(Tenant)` to all business models. Composite uniques. `CompanyConfig` per tenant. Blank-slate DB approach (no data retrofit). |
| **C.2** | `vyntia/C2-rls-policies` | Postgres roles (`vyntia_app`, `vyntia_admin`, `vyntia_readonly`). `setup_rls` management command. Production settings switch to `vyntia_app`. |
| **C.3** | `vyntia/C3-tenant-middleware` | `TenantMiddleware` + `TenantAuthMiddleware` + `RLSMiddleware`. `TenantManager` + `UnsafeManager`. Subdomain resolution. JWT with `tenant_id`. |
| **C.4** | `vyntia/C4-auth-tenant-aware` | Tenant-aware login/logout. Activation endpoint. Workspace switcher backend. Token exchange flow. |
| **C.5** | `vyntia/C5-admin-api` | `/api/admin/tenants/*` endpoints with `is_vyntia_staff` permission. `setup_tenant_seed` helper. Impersonation + SupportSession. |
| **C.6** | `vyntia/C6-frontend-tenant` | Frontend: `TenantProvider`, `WorkspaceSwitcher`, `ActivationPage`, `TenantSettings`, `MembershipsPage`, `ImpersonationBanner`. |
| **C.7** | `vyntia/C7-admin-panel-frontend` | Frontend `admin.vyntia.pe`: tenant CRUD UI, invitations, support sessions log. |
| **C.8** | `vyntia/C8-isolation-tests-docs` | Comprehensive isolation tests (pytest + Playwright). Runbooks: provision tenant, suspend, restore. CI `rls-policy-audit` job. Docs in `docs/` for ops. |

---

## 11. Definition of Done

- [ ] All 9 sub-layers (C.0–C.8) merged to `master`
- [ ] `git tag c-multitenancy-complete` applied
- [ ] `pytest tests/` ≥ 200 passed (no regression from 161 + new tests pass)
- [ ] `pytest tests/test_tenant_isolation.py` 100% pass — proving cross-tenant leak is impossible
- [ ] `manage.py setup_rls --check` clean — every tenant-scoped table has its policy
- [ ] `npm run build` exit 0, `npm test -- --run` ≥ 20 passed
- [ ] Manual smoke test: provision a tenant via `admin.vyntia.pe`, accept invitation, log in, verify can't see other tenants' data
- [ ] Runbooks committed: `docs/operations/{provision-tenant,suspend-tenant,impersonate-user,restore-tenant}.md`
- [ ] CI `rls-policy-audit` job green
- [ ] `docs/ROADMAP_SUBPROJECTS.md` updated: C marked complete, B unblocked
- [ ] `CLAUDE.md` updated: active sub-project = next in roadmap (B)

---

## 12. Architecture rules (enforced)

In addition to the rules from Foundation:

1. **Every business model is tenant-scoped or globally explicit.** New models default to `TenantScopedModel`. To opt out (global), add a comment justifying it, e.g. `# Global: shared menu structure across all tenants`.
2. **`Model.objects` is always tenant-filtered.** Cross-tenant access requires `Model.unsafe` — code review must justify every use.
3. **No raw SQL in views.** If raw SQL is necessary (reports, analytics), use `connection.cursor()` inside a `with tenant_context(...)` block — RLS will enforce.
4. **Migrations run with `vyntia_admin`.** Never with `vyntia_app`.
5. **JWT always carries `tenant_id`.** A token without `tenant_id` is only valid against `app.vyntia.pe`.
6. **Reserved subdomains are checked at slug validation.** Any new reserved subdomain (e.g. for a future feature) must be added to `RESERVED_SUBDOMAINS` and verified against existing tenants.

---

## 13. Open questions (deferred to plan phase)

- **Tenant deletion / data retention:** soft-delete with 30-day window? Hard delete after retention? GDPR/Peruvian data law requirements need legal input.
- **Backups:** per-tenant backup vs shared dump? Restore individual tenant from a shared backup is non-trivial.
- **Performance budget:** RLS adds query overhead (~5-10%). At what tenant count does it become problematic?
- **Tenant migration to DB-per-tenant tier:** out of scope for C, but design must not preclude it. Plan should include a migration playbook stub.
- **Subdomain DNS provisioning automation:** for now manual via Cloudflare. Future: Cloudflare API integration in `setup_tenant_seed`.

These are tracked but not blocking for C. Each gets a TODO-flagged section in the implementation plans.

---

**Spec status:** READY FOR IMPLEMENTATION PLANNING
**Next step:** invoke `superpowers:writing-plans` skill to draft `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md` and per-sub-layer plans.
