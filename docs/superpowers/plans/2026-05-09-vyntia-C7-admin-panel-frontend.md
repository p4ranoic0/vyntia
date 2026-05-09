# C.7 — Admin Panel Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Build the React admin panel served at `admin.vyntia.pe` — Vyntia staff log in, list/create/manage tenants, view support session audit log. Consumes the `/api/admin/*` API shipped in C.5.

**Architecture:** New `apps/web/src/features/admin/` directory with admin-only pages + services. App.tsx detects admin subdomain and renders a separate `AdminApp` shell (login + sidebar + routes), bypassing the tenant-scoped legacy app entirely. Authentication uses the existing `LoginForm` and `useAuth` hook; an additional `is_vyntia_staff` gate runs after login. **Skips C.6 dependencies** — uses a simple `isAdminHost()` host check instead of the full TenantContext system. C.6 can be retrofitted later without touching this code.

**Backend dependency:** The login response from `CustomTokenObtainPairSerializer` must include `is_vyntia_staff` in the user payload (added as a small tweak in Task 2; the field exists on the User model from C.5).

**Source spec:** `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` § 7-8

**Source roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`

---

## Baseline snapshot

| Check | Expected |
|---|---|
| Backend pytest | ≥268 passed (Task 2 may add 1-2) |
| Frontend build | Exit 0 |
| Frontend tsc | 1 error (BlankEnum.ts pre-existing) |
| Frontend tests | 7 passed |
| Frontend lint | ≤634 warnings |

C.7 adds: ~10-15 vitest tests + 1-2 backend tests. Targets: pytest ≥270, vitest ≥17.

---

## File structure

**Files to create:**

```
apps/web/src/shared/utils/
└── isAdminHost.ts                      # tiny: detects admin subdomain

apps/web/src/features/admin/
├── index.ts
├── AdminApp.tsx                        # shell: login + layout + routes
├── components/
│   ├── AdminLayout.tsx                 # admin sidebar + topbar
│   └── AdminLoginGate.tsx              # is_vyntia_staff check after login
├── pages/
│   ├── TenantsListPage.tsx
│   ├── CreateTenantPage.tsx
│   ├── TenantDetailPage.tsx
│   └── SupportSessionsListPage.tsx
├── services/
│   ├── tenantsAdminService.ts
│   └── supportSessionsService.ts
└── __tests__/
    ├── tenantsAdminService.test.ts
    └── isAdminHost.test.ts
```

**Files to modify:**

- `apps/api/api/v1/auth/serializers.py` — add `is_vyntia_staff` to user payload (Task 2)
- `apps/web/src/features/auth/services/authService.ts` — add `is_vyntia_staff` to User type (Task 2)
- `apps/web/src/App.tsx` — early-return AdminApp on admin host (Task 3)

---

## Branch: `vyntia/C7-admin-panel-frontend`

---

## Task 1: Branch + `isAdminHost()` utility

**Files:** `apps/web/src/shared/utils/isAdminHost.ts` + test

- [ ] **Step 1.1: Branch**
```bash
cd D:/VYNTIA && git checkout master && git checkout -b vyntia/C7-admin-panel-frontend
```

- [ ] **Step 1.2: Create `apps/web/src/shared/utils/isAdminHost.ts`**

```typescript
/**
 * Detects whether the current browser host is admin.vyntia.pe (the Vyntia
 * staff panel subdomain). Used by App.tsx to early-return the AdminApp shell
 * instead of the legacy tenant-scoped app.
 *
 * Stand-alone (no jwt-decode, no React context) so C.7 can ship without
 * the full C.6 TenantContext system in place.
 */
export function isAdminHost(host?: string): boolean {
  const h = (host ?? window.location.host).toLowerCase()
  const subdomain = h.split(':', 1)[0].split('.')[0]
  return subdomain === 'admin'
}
```

- [ ] **Step 1.3: Create test `apps/web/src/shared/utils/__tests__/isAdminHost.test.ts`**

```typescript
import { describe, it, expect } from 'vitest'

import { isAdminHost } from '../isAdminHost'

describe('isAdminHost', () => {
  it('matches admin.vyntia.pe', () => {
    expect(isAdminHost('admin.vyntia.pe')).toBe(true)
  })
  it('strips port', () => {
    expect(isAdminHost('admin.vyntia.pe:8000')).toBe(true)
  })
  it('case-insensitive', () => {
    expect(isAdminHost('ADMIN.VYNTIA.PE')).toBe(true)
  })
  it('rejects non-admin subdomains', () => {
    expect(isAdminHost('acme.vyntia.pe')).toBe(false)
    expect(isAdminHost('app.vyntia.pe')).toBe(false)
    expect(isAdminHost('localhost:5173')).toBe(false)
  })
})
```

- [ ] **Step 1.4: Verify**
```bash
cd D:/VYNTIA/apps/web && npx vitest run src/shared/utils 2>&1 | tail -5
```
Expected: 4 tests pass.

- [ ] **Step 1.5: Commit**
```bash
cd D:/VYNTIA && git add apps/web/src/shared/utils/isAdminHost.ts apps/web/src/shared/utils/__tests__/ && git commit -m "feat(C7): isAdminHost() detects admin.vyntia.pe subdomain"
```

---

## Task 2: Backend — expose `is_vyntia_staff` in login response + frontend type

**Files:** `apps/api/api/v1/auth/serializers.py`, `apps/web/src/features/auth/services/authService.ts`

- [ ] **Step 2.1: Read existing user payload composition**

```bash
cd D:/VYNTIA && grep -n "is_active\|tipo_usuario\|is_vyntia\|user_data\|\"user\"" apps/api/api/v1/auth/serializers.py | head -20
```

Find where the user dict is assembled in `CustomTokenObtainPairSerializer.validate()`. There's a block that builds something like `data['user'] = { 'usuario_id': user.id, 'username': user.username, ... }`.

- [ ] **Step 2.2: Add `is_vyntia_staff` to that dict**

In `apps/api/api/v1/auth/serializers.py`, find the user dict assembly and add `"is_vyntia_staff": user.is_vyntia_staff` next to `is_active`. Quick add — typically one line.

- [ ] **Step 2.3: Verify backend test**

Quick smoke test:

```bash
cd D:/VYNTIA/apps/api && D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/test_auth_api.py::LoginAPITest -v 2>&1 | tail -5
```

Expected: existing login tests still pass (the new field is additive — it won't break anything).

- [ ] **Step 2.4: Update frontend `User` type**

In `apps/web/src/features/auth/services/authService.ts`, find the `User` interface (lines ~11-36). Add:

```typescript
  is_vyntia_staff?: boolean
```

(Optional because legacy backends may not include it — defensive default.)

- [ ] **Step 2.5: Verify build + tests**

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3 && npm test -- --run 2>&1 | tail -3
```

Expected: build OK, vitest 7+ pass.

- [ ] **Step 2.6: Commit**
```bash
cd D:/VYNTIA && git add apps/api/api/v1/auth/serializers.py apps/web/src/features/auth/services/authService.ts && git commit -m "feat(C7): expose User.is_vyntia_staff in login response + frontend User type"
```

---

## Task 3: AdminApp shell + App.tsx admin host branch

**Files:** `apps/web/src/features/admin/AdminApp.tsx`, `apps/web/src/features/admin/components/AdminLoginGate.tsx`, `apps/web/src/features/admin/components/AdminLayout.tsx`, `apps/web/src/App.tsx`

- [ ] **Step 3.1: Create `features/admin/components/AdminLayout.tsx`**

Use Shadcn/ui primitives. Keep it minimal — sidebar with 3 links (Tenants, Sessions, Logout) + topbar showing logged-in user.

```typescript
import { Link, Outlet, useLocation } from 'react-router-dom'
import { Building2, LogOut, ShieldAlert } from 'lucide-react'

import { useAuth } from '@/features/auth/hooks/useAuth'
import { Button } from '@/shared/ui/button'

export function AdminLayout() {
  const { user, logout } = useAuth()
  const { pathname } = useLocation()

  const navItem = (path: string, label: string, Icon: typeof Building2) => {
    const active = pathname.startsWith(path)
    return (
      <Link
        to={path}
        className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors ${
          active ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'
        }`}
      >
        <Icon size={16} aria-hidden />
        <span>{label}</span>
      </Link>
    )
  }

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r bg-card p-4">
        <div className="mb-6 flex items-center gap-2 px-2 font-semibold">
          <ShieldAlert size={18} className="text-primary" />
          <span>VYNTIA Admin</span>
        </div>
        <nav className="space-y-1">
          {navItem('/admin/tenants', 'Tenants', Building2)}
          {navItem('/admin/support-sessions', 'Support Sessions', ShieldAlert)}
        </nav>
        <div className="mt-8 border-t pt-4 px-2 text-xs text-muted-foreground">
          {user?.email}
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="mt-2 w-full justify-start"
          onClick={() => logout()}
        >
          <LogOut size={14} className="mr-2" /> Cerrar sesión
        </Button>
      </aside>
      <main className="flex-1 overflow-auto p-8">
        <Outlet />
      </main>
    </div>
  )
}
```

- [ ] **Step 3.2: Create `features/admin/components/AdminLoginGate.tsx`**

Renders a "not authorized" notice if logged-in user lacks `is_vyntia_staff`; otherwise renders children.

```typescript
import { useAuth } from '@/features/auth/hooks/useAuth'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { Button } from '@/shared/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card'
import LoginForm from '@/features/auth/components/LoginForm'

interface AdminLoginGateProps {
  children: React.ReactNode
}

export function AdminLoginGate({ children }: AdminLoginGateProps) {
  const { isAuthenticated, isLoading, user, logout } = useAuth()

  if (isLoading) return <LoadingSpinner />
  if (!isAuthenticated) return <LoginForm />

  if (!user?.is_vyntia_staff) {
    return (
      <div className="mx-auto max-w-md p-8">
        <Card>
          <CardHeader>
            <CardTitle>Acceso restringido</CardTitle>
            <CardDescription>
              Esta sección está reservada para personal de Vyntia. Si crees que
              deberías tener acceso, contacta al equipo de operaciones.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" onClick={() => logout()}>
              Cerrar sesión
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return <>{children}</>
}
```

- [ ] **Step 3.3: Create `features/admin/AdminApp.tsx`**

```typescript
import { Navigate, Route, Routes } from 'react-router-dom'

import { AdminLayout } from './components/AdminLayout'
import { AdminLoginGate } from './components/AdminLoginGate'

// Page imports — added in Tasks 4-6 (placeholders OK in Task 3)
const TenantsListPage = () => <div>Tenants list (C.7 Task 4)</div>
const CreateTenantPage = () => <div>Create tenant (C.7 Task 5)</div>
const TenantDetailPage = () => <div>Tenant detail (C.7 Task 5)</div>
const SupportSessionsListPage = () => <div>Support sessions (C.7 Task 6)</div>

/**
 * Top-level shell for admin.vyntia.pe.
 * 1. AdminLoginGate: requires authenticated + is_vyntia_staff
 * 2. AdminLayout: sidebar + outlet
 * 3. Admin routes
 */
export function AdminApp() {
  return (
    <AdminLoginGate>
      <Routes>
        <Route element={<AdminLayout />}>
          <Route path="/admin/tenants" element={<TenantsListPage />} />
          <Route path="/admin/tenants/new" element={<CreateTenantPage />} />
          <Route path="/admin/tenants/:id" element={<TenantDetailPage />} />
          <Route path="/admin/support-sessions" element={<SupportSessionsListPage />} />
          <Route path="*" element={<Navigate to="/admin/tenants" replace />} />
        </Route>
      </Routes>
    </AdminLoginGate>
  )
}
```

- [ ] **Step 3.4: Create `features/admin/index.ts`**

```typescript
export { AdminApp } from './AdminApp'
```

- [ ] **Step 3.5: Update `apps/web/src/App.tsx`**

At the very top of the function `App()` (or wherever the main render returns), add an early-return for admin host. The admin app needs the same providers (QueryClient + Theme + Auth + Router) but a different content tree.

Read `App.tsx` to find the existing provider stack. Then refactor so that BOTH the legacy and admin trees share the providers but differ in content. Pattern:

```tsx
import { isAdminHost } from '@/shared/utils/isAdminHost'
import { AdminApp } from '@/features/admin'

function AppContent() {
  if (isAdminHost()) {
    return <AdminApp />
  }
  // ... existing legacy content (Routes etc.)
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <AppContent />
            {/* Toasters, etc. */}
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}
```

If the existing App is structured differently (e.g., `BrowserRouter` wraps everything), keep it that way and just put the `isAdminHost()` check inside the routing tree, returning `<AdminApp />` early.

- [ ] **Step 3.6: Verify build**
```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3 && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | head -5
```

- [ ] **Step 3.7: Commit**
```bash
cd D:/VYNTIA && git add apps/web/src/features/admin/ apps/web/src/App.tsx && git commit -m "feat(C7): AdminApp shell + AdminLayout + login gate + App.tsx admin host branch"
```

---

## Task 4: Tenants list page + service

**Files:** `apps/web/src/features/admin/services/tenantsAdminService.ts`, `apps/web/src/features/admin/pages/TenantsListPage.tsx`, test

- [ ] **Step 4.1: Create `services/tenantsAdminService.ts`**

```typescript
import { apiClient } from '@/shared/api/api'

export interface AdminTenant {
  id: string
  slug: string
  name: string
  ruc: string
  plan: 'starter' | 'pro' | 'enterprise' | 'govtech'
  status: 'trial' | 'active' | 'suspended' | 'cancelled'
  trial_ends_at: string | null
  max_users: number
  cancelled_at: string | null
  created_at: string
  updated_at: string
  member_count: number
}

export interface CreateTenantPayload {
  slug: string
  name: string
  ruc: string
  plan: AdminTenant['plan']
  trial_days: number
  admin_email: string
  admin_name: string
}

export interface CreateTenantResponse {
  tenant: AdminTenant
  invitation: {
    id: string
    email: string
    expires_at: string
    activation_url: string
  }
}

export interface PaginatedTenants {
  results: AdminTenant[]
  pagination: {
    total_items: number
    current_page: number
    page_size: number
    total_pages: number
  }
}

export async function fetchTenants(page = 1, pageSize = 25): Promise<PaginatedTenants> {
  const response = await apiClient.get('/admin/tenants/', {
    params: { page, page_size: pageSize },
  })
  return response.data?.data
}

export async function fetchTenant(id: string): Promise<AdminTenant> {
  const response = await apiClient.get(`/admin/tenants/${id}/`)
  return response.data?.data
}

export async function createTenant(payload: CreateTenantPayload): Promise<CreateTenantResponse> {
  const response = await apiClient.post('/admin/tenants/', payload)
  return response.data?.data
}

export async function updateTenant(
  id: string,
  patch: Partial<Pick<AdminTenant, 'plan' | 'max_users' | 'trial_ends_at'>>,
): Promise<AdminTenant> {
  const response = await apiClient.patch(`/admin/tenants/${id}/`, patch)
  return response.data?.data
}

export async function suspendTenant(id: string): Promise<AdminTenant> {
  const response = await apiClient.post(`/admin/tenants/${id}/suspend/`)
  return response.data?.data
}

export async function cancelTenant(id: string): Promise<AdminTenant> {
  const response = await apiClient.post(`/admin/tenants/${id}/cancel/`)
  return response.data?.data
}

export async function reinviteTenant(
  id: string,
  email: string,
  role: 'owner' | 'admin' | 'member' = 'owner',
): Promise<{ id: string; email: string; expires_at: string; activation_url: string }> {
  const response = await apiClient.post(`/admin/tenants/${id}/invitations/`, {
    email,
    role,
  })
  return response.data?.data
}
```

Note the URL prefix `/admin/...` — the apiClient baseURL is `/api`, and the admin namespace was wired at `/api/admin/` in C.5.

- [ ] **Step 4.2: Create `pages/TenantsListPage.tsx`**

```typescript
import { useQuery } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { fetchTenants } from '../services/tenantsAdminService'

const statusBadgeVariant = {
  trial: 'secondary',
  active: 'default',
  suspended: 'destructive',
  cancelled: 'outline',
} as const

export function TenantsListPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-tenants'],
    queryFn: () => fetchTenants(1, 50),
  })

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Tenants</h1>
          <p className="text-sm text-muted-foreground">
            Listado completo de workspaces VYNTIA.
          </p>
        </div>
        <Button asChild>
          <Link to="/admin/tenants/new">
            <Plus size={16} className="mr-2" /> Nuevo tenant
          </Link>
        </Button>
      </div>

      {isLoading && <div className="text-center py-8">Cargando…</div>}
      {isError && <div className="text-destructive text-center py-8">Error al cargar tenants.</div>}
      {data && data.results.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          No hay tenants. Crea el primero con el botón "Nuevo tenant".
        </div>
      )}

      {data && data.results.length > 0 && (
        <div className="rounded-lg border bg-card">
          <table className="w-full text-sm">
            <thead className="border-b text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Slug</th>
                <th className="px-4 py-3">Nombre</th>
                <th className="px-4 py-3">Plan</th>
                <th className="px-4 py-3">Estado</th>
                <th className="px-4 py-3 text-right">Miembros</th>
                <th className="px-4 py-3">Creado</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((t) => (
                <tr key={t.id} className="border-b last:border-0 hover:bg-accent/50">
                  <td className="px-4 py-3 font-mono">
                    <Link to={`/admin/tenants/${t.id}`} className="text-primary hover:underline">
                      {t.slug}
                    </Link>
                  </td>
                  <td className="px-4 py-3">{t.name}</td>
                  <td className="px-4 py-3">{t.plan}</td>
                  <td className="px-4 py-3">
                    <Badge variant={statusBadgeVariant[t.status]}>{t.status}</Badge>
                  </td>
                  <td className="px-4 py-3 text-right">{t.member_count}</td>
                  <td className="px-4 py-3 text-xs text-muted-foreground">
                    {new Date(t.created_at).toLocaleDateString('es-PE')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4.3: Wire in `AdminApp.tsx`**

Replace the placeholder `TenantsListPage` import in `AdminApp.tsx`:

```typescript
import { TenantsListPage } from './pages/TenantsListPage'
```

Remove the `const TenantsListPage = () => <div>...</div>` placeholder.

- [ ] **Step 4.4: Write test for service**

Create `apps/web/src/features/admin/__tests__/tenantsAdminService.test.ts`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}))

import { apiClient } from '@/shared/api/api'
import {
  fetchTenants,
  createTenant,
  suspendTenant,
} from '../services/tenantsAdminService'

describe('tenantsAdminService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('fetchTenants passes pagination params', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [], pagination: { total_items: 0, current_page: 1, page_size: 25, total_pages: 0 } } },
    })
    await fetchTenants(2, 50)
    expect(apiClient.get).toHaveBeenCalledWith('/admin/tenants/', {
      params: { page: 2, page_size: 50 },
    })
  })

  it('createTenant POSTs payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { tenant: { slug: 'x' }, invitation: {} } },
    })
    await createTenant({
      slug: 'x', name: 'X', ruc: '20999999999', plan: 'starter',
      trial_days: 30, admin_email: 'a@b.c', admin_name: 'A',
    })
    expect(apiClient.post).toHaveBeenCalledWith(
      '/admin/tenants/',
      expect.objectContaining({ slug: 'x', plan: 'starter' }),
    )
  })

  it('suspendTenant POSTs to suspend endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { data: {} } })
    await suspendTenant('abc-123')
    expect(apiClient.post).toHaveBeenCalledWith('/admin/tenants/abc-123/suspend/')
  })
})
```

- [ ] **Step 4.5: Verify build + tests**
```bash
cd D:/VYNTIA/apps/web && npx vitest run src/features/admin 2>&1 | tail -5 && npm run build 2>&1 | tail -3
```

- [ ] **Step 4.6: Commit**
```bash
cd D:/VYNTIA && git add apps/web/src/features/admin/ && git commit -m "feat(C7): TenantsListPage + tenantsAdminService"
```

---

## Task 5: Create + Detail tenant pages

**Files:** `apps/web/src/features/admin/pages/CreateTenantPage.tsx`, `apps/web/src/features/admin/pages/TenantDetailPage.tsx`

- [ ] **Step 5.1: Create `CreateTenantPage.tsx`**

```typescript
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { z } from 'zod'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'

import { createTenant, type CreateTenantPayload } from '../services/tenantsAdminService'

const Schema = z.object({
  slug: z.string().min(2).max(63).regex(/^[a-z0-9][a-z0-9-]*[a-z0-9]$/, 'Solo a-z, 0-9, guiones'),
  name: z.string().min(2).max(200),
  ruc: z.string().regex(/^\d{11}$/, 'RUC de 11 dígitos'),
  plan: z.enum(['starter', 'pro', 'enterprise', 'govtech']),
  trial_days: z.coerce.number().int().min(0).max(90),
  admin_email: z.string().email(),
  admin_name: z.string().min(2),
})

type FormValues = z.infer<typeof Schema>

export function CreateTenantPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const form = useForm<FormValues>({
    resolver: zodResolver(Schema),
    defaultValues: { plan: 'starter', trial_days: 30 } as FormValues,
  })

  const mutation = useMutation({
    mutationFn: (values: FormValues) => createTenant(values as CreateTenantPayload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['admin-tenants'] })
      toast.success(
        `Tenant "${data.tenant.slug}" creado. URL de activación: ${data.invitation.activation_url}`,
        { duration: 15000 },
      )
      navigate(`/admin/tenants/${data.tenant.id}`)
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.message || 'Error al crear tenant'
      toast.error(detail)
    },
  })

  const fields: Array<[keyof FormValues, string, string?]> = [
    ['slug', 'Slug (subdomain)', 'acme'],
    ['name', 'Nombre legal', 'Acme Corp S.A.C.'],
    ['ruc', 'RUC (11 dígitos)', '20123456789'],
    ['admin_name', 'Nombre del admin', 'María Pérez'],
    ['admin_email', 'Email del admin', 'ceo@acme.com'],
  ]

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Nuevo tenant</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={form.handleSubmit((v) => mutation.mutate(v))}
            className="space-y-4"
          >
            {fields.map(([name, label, placeholder]) => (
              <div className="space-y-2" key={name}>
                <Label htmlFor={name}>{label}</Label>
                <Input id={name} placeholder={placeholder} {...form.register(name)} />
                {form.formState.errors[name] && (
                  <p className="text-xs text-destructive">
                    {form.formState.errors[name]?.message as string}
                  </p>
                )}
              </div>
            ))}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="plan">Plan</Label>
                <select
                  id="plan"
                  {...form.register('plan')}
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                >
                  <option value="starter">Starter</option>
                  <option value="pro">Pro</option>
                  <option value="enterprise">Enterprise</option>
                  <option value="govtech">GovTech</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="trial_days">Trial (días)</Label>
                <Input
                  id="trial_days"
                  type="number"
                  {...form.register('trial_days', { valueAsNumber: true })}
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="ghost" onClick={() => navigate('/admin/tenants')}>
                Cancelar
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Creando…' : 'Crear tenant'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
```

- [ ] **Step 5.2: Create `TenantDetailPage.tsx`**

```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'

import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'

import {
  cancelTenant,
  fetchTenant,
  reinviteTenant,
  suspendTenant,
} from '../services/tenantsAdminService'

export function TenantDetailPage() {
  const { id = '' } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [reinviteEmail, setReinviteEmail] = useState('')

  const { data: tenant, isLoading, isError } = useQuery({
    queryKey: ['admin-tenant', id],
    queryFn: () => fetchTenant(id),
    enabled: !!id,
  })

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['admin-tenant', id] })
    qc.invalidateQueries({ queryKey: ['admin-tenants'] })
  }

  const suspend = useMutation({
    mutationFn: () => suspendTenant(id),
    onSuccess: () => { toast.success('Tenant suspendido'); invalidate() },
    onError: () => toast.error('No se pudo suspender'),
  })

  const cancel = useMutation({
    mutationFn: () => cancelTenant(id),
    onSuccess: () => { toast.success('Tenant cancelado'); invalidate() },
    onError: () => toast.error('No se pudo cancelar'),
  })

  const reinvite = useMutation({
    mutationFn: () => reinviteTenant(id, reinviteEmail),
    onSuccess: (data) => {
      toast.success(`Invitación enviada. URL: ${data.activation_url}`, { duration: 15000 })
      setReinviteEmail('')
    },
    onError: () => toast.error('No se pudo crear la invitación'),
  })

  if (isLoading) return <div>Cargando…</div>
  if (isError || !tenant) return <div className="text-destructive">No encontrado</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">{tenant.name}</h1>
          <div className="text-sm text-muted-foreground font-mono">
            {tenant.slug}.vyntia.pe · RUC {tenant.ruc}
          </div>
        </div>
        <Button variant="outline" onClick={() => navigate('/admin/tenants')}>
          ← Volver
        </Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Estado</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 text-sm">
          <div>Plan: <Badge>{tenant.plan}</Badge></div>
          <div>Estado: <Badge>{tenant.status}</Badge></div>
          <div>Miembros activos: <strong>{tenant.member_count}</strong></div>
          <div>Max usuarios: {tenant.max_users}</div>
          <div>Trial expira: {tenant.trial_ends_at?.split('T')[0] ?? '—'}</div>
          <div>Creado: {tenant.created_at.split('T')[0]}</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Acciones</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => suspend.mutate()}
              disabled={tenant.status === 'cancelled' || suspend.isPending}
            >
              Suspender
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (confirm(`¿Cancelar tenant ${tenant.name}? Esta acción es irreversible.`)) {
                  cancel.mutate()
                }
              }}
              disabled={tenant.status === 'cancelled' || cancel.isPending}
            >
              Cancelar tenant
            </Button>
          </div>
          <div className="flex gap-2 items-end pt-2 border-t">
            <div className="flex-1">
              <label className="text-xs text-muted-foreground">Re-invitar admin</label>
              <Input
                type="email"
                placeholder="email@ejemplo.com"
                value={reinviteEmail}
                onChange={(e) => setReinviteEmail(e.target.value)}
              />
            </div>
            <Button
              onClick={() => reinvite.mutate()}
              disabled={!reinviteEmail || reinvite.isPending}
            >
              Re-invitar
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

- [ ] **Step 5.3: Wire in `AdminApp.tsx`**

```typescript
import { CreateTenantPage } from './pages/CreateTenantPage'
import { TenantDetailPage } from './pages/TenantDetailPage'
```

Remove the placeholder consts.

- [ ] **Step 5.4: Verify build**
```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3 && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | head -5
```

- [ ] **Step 5.5: Commit**
```bash
cd D:/VYNTIA && git add apps/web/src/features/admin/ && git commit -m "feat(C7): CreateTenantPage + TenantDetailPage with lifecycle actions"
```

---

## Task 6: Support sessions log + final merge

**Files:** `apps/web/src/features/admin/services/supportSessionsService.ts`, `apps/web/src/features/admin/pages/SupportSessionsListPage.tsx`

- [ ] **Step 6.1: Create `services/supportSessionsService.ts`**

```typescript
import { apiClient } from '@/shared/api/api'

export interface SupportSession {
  id: string
  staff_user: string
  target_user: string
  tenant_slug: string
  reason: string
  started_at: string
  expires_at: string
  ended_at: string | null
  actions_count: number
}

export interface PaginatedSessions {
  results: SupportSession[]
  pagination: {
    total_items: number
    current_page: number
    page_size: number
    total_pages: number
  }
}

export async function fetchSupportSessions(page = 1, pageSize = 25): Promise<PaginatedSessions> {
  const response = await apiClient.get('/admin/support-sessions/', {
    params: { page, page_size: pageSize },
  })
  return response.data?.data
}
```

- [ ] **Step 6.2: Create `pages/SupportSessionsListPage.tsx`**

```typescript
import { useQuery } from '@tanstack/react-query'

import { Badge } from '@/shared/ui/badge'

import { fetchSupportSessions } from '../services/supportSessionsService'

export function SupportSessionsListPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-support-sessions'],
    queryFn: () => fetchSupportSessions(1, 50),
  })

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Support Sessions</h1>
        <p className="text-sm text-muted-foreground">
          Historial de impersonaciones realizadas por staff de Vyntia.
        </p>
      </div>

      {isLoading && <div className="text-center py-8">Cargando…</div>}

      {data && data.results.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Sin sesiones de soporte registradas.
        </div>
      )}

      {data && data.results.length > 0 && (
        <div className="rounded-lg border bg-card">
          <table className="w-full text-sm">
            <thead className="border-b text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Staff</th>
                <th className="px-4 py-3">Usuario</th>
                <th className="px-4 py-3">Tenant</th>
                <th className="px-4 py-3">Motivo</th>
                <th className="px-4 py-3">Inicio</th>
                <th className="px-4 py-3">Estado</th>
                <th className="px-4 py-3 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((s) => {
                const ended = !!s.ended_at
                const expired = !ended && new Date(s.expires_at) < new Date()
                return (
                  <tr key={s.id} className="border-b last:border-0 hover:bg-accent/50">
                    <td className="px-4 py-3 font-medium">{s.staff_user}</td>
                    <td className="px-4 py-3">{s.target_user}</td>
                    <td className="px-4 py-3 font-mono text-xs">{s.tenant_slug}</td>
                    <td className="px-4 py-3 max-w-xs truncate" title={s.reason}>{s.reason}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">
                      {new Date(s.started_at).toLocaleString('es-PE')}
                    </td>
                    <td className="px-4 py-3">
                      {ended ? <Badge variant="outline">Finalizada</Badge>
                        : expired ? <Badge variant="secondary">Expirada</Badge>
                        : <Badge>Activa</Badge>}
                    </td>
                    <td className="px-4 py-3 text-right">{s.actions_count}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 6.3: Wire in `AdminApp.tsx`**

```typescript
import { SupportSessionsListPage } from './pages/SupportSessionsListPage'
```

Remove the placeholder.

- [ ] **Step 6.4: Verify build + tests + lint**
```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3 && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | wc -l && npm test -- --run 2>&1 | tail -3 && npm run lint 2>&1 | tail -3
```

Expected: build OK, 0 new TS errors, ≥17 vitest pass.

- [ ] **Step 6.5: Backend baseline check**
```bash
cd D:/VYNTIA/apps/api && D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -3
```

Expected: ≥268 (Task 2 modified backend serializer; check no regression).

- [ ] **Step 6.6: Update master roadmap**

In `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`, find C.7 row and update "Detailed plan" cell to:

```
`2026-05-09-vyntia-C7-admin-panel-frontend.md` ✅ merged 2026-05-09
```

- [ ] **Step 6.7: Commit + merge**
```bash
cd D:/VYNTIA && git add apps/web/src/features/admin/ docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md && git commit -m "feat(C7): SupportSessionsListPage + roadmap update" && git checkout master && git merge --no-ff vyntia/C7-admin-panel-frontend -m "Merge C.7: admin panel frontend (tenants CRUD + lifecycle + support sessions log)"
```

---

## Self-Review

### Spec coverage check

| Spec § 7-8 requirement | Covered |
|---|---|
| TenantsListPage | Task 4 |
| CreateTenantPage | Task 5 |
| TenantDetailPage with lifecycle actions | Task 5 |
| ImpersonationLogPage (= SupportSessionsListPage) | Task 6 |
| Branched routing in App.tsx | Task 3 |
| `is_vyntia_staff` gate | Task 3 (AdminLoginGate) |

### Spec deviations

1. **No user search / impersonation UI** — backend exists (C.5), but admin UX is deferred. Vyntia staff can use the API directly (curl/Postman) for support flows in MVP. Future polish sub-layer adds this UI.
2. **Skipped C.6 prerequisites** — uses minimal `isAdminHost()` instead of full TenantContext. C.6 can ship later without conflict.
3. **AdminLayout is minimalist** — no fancy navigation, no breadcrumbs. Sidebar + outlet. Deliberate MVP choice.
4. **`is_vyntia_staff` exposed via login response, not JWT** — simpler than re-issuing tokens; the User type carries it through to AuthContext.

### Out of scope (deferred)

- C.6 frontend (workspace switcher, activation page, impersonation banner, tenant settings)
- User search + impersonation UI in admin
- Audit log filters / exports
- E2E tests (C.8)

---

**Plan complete.** When executed, C.7 ships ~6 commits, ~12 new files (~700 LOC), 3 modified files, ~5-7 new vitest tests + 1 backend tweak. Frontend test baseline grows from 7 → ~12.
