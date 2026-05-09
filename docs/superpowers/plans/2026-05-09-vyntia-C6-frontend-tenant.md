# C.6 — Frontend Tenant Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the React frontend to the tenant-aware backend (C.0–C.5) — boot-time subdomain detection (`TenantProvider`), workspace switcher for multi-tenant users (`app.vyntia.pe`), invitation activation page (`/activate?token=...`), impersonation banner (when JWT carries `impersonated_by`), and apiClient guard against cross-tenant token replay. App.tsx branches the rendered tree by subdomain type.

**Architecture:** New `apps/web/src/shared/tenant/` package (boot-time host parsing + TenantContext) + new `apps/web/src/features/tenancy/` (activation page + impersonation banner) + new `apps/web/src/features/workspace-switcher/` (the `app.vyntia.pe` page). Adds `jwt-decode` dependency for reading tenant claims from the access token. The apiClient gains a defensive interceptor: if `JWT.tenant_slug !== current host subdomain`, clear the token and redirect to login (catches stale sessions across subdomain hops). TenantSettings, MembershipsPage, and TenantBadge are deferred — they're nice-to-have UX, not essential for the auth/onboarding loop. `AdminApp` (the admin.vyntia.pe panel) is C.7.

**Tech Stack:** React 18 + Vite + TypeScript, React Router, axios, react-query, jwt-decode (new), Shadcn/ui.

**Source spec:** `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` § 8

**Source roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`

---

## Baseline snapshot

| Check | Command | Expected |
|---|---|---|
| Backend tests | `cd apps/api && pytest tests/ apps/tenancy/tests/ -q` | ≥268 passed (no backend changes) |
| Frontend build | `cd apps/web && npm run build` | Exit 0 |
| Frontend types | `cd apps/web && npx tsc --noEmit -p tsconfig.app.json` | 1 error (BlankEnum.ts pre-existing) |
| Frontend tests | `cd apps/web && npm test -- --run` | 7 passed |
| Frontend lint | `cd apps/web && npm run lint` | ≤634 warnings |

C.6 adds: ~10-15 new vitest tests. Target: ≥17 passed.

---

## File structure

**Files to create:**

```
apps/web/src/shared/tenant/
├── index.ts
├── constants.ts                    # RESERVED_SUBDOMAINS
├── tenantContext.tsx               # TenantContext + TenantProvider
└── jwtClaims.ts                    # decodeJwtClaims + JwtClaims type

apps/web/src/features/tenancy/
├── index.ts
├── components/
│   └── ImpersonationBanner.tsx
└── pages/
    └── ActivationPage.tsx

apps/web/src/features/workspace-switcher/
├── index.ts
├── pages/
│   └── WorkspacesPage.tsx
└── services/
    └── workspaceService.ts

apps/web/src/shared/tenant/__tests__/
├── tenantContext.test.tsx
└── jwtClaims.test.ts

apps/web/src/features/workspace-switcher/__tests__/
└── workspaceService.test.ts
```

**Files to modify:**

- `apps/web/package.json` — add `jwt-decode` dependency
- `apps/web/src/shared/api/api.ts` — add tenant guard interceptor
- `apps/web/src/App.tsx` — branch routing by tenant type, register new routes

---

## Branch

`vyntia/C6-frontend-tenant` — branched from `master` (HEAD has `Merge C.5`).

---

## Task 1: jwt-decode dep + tenant resolution utilities

**Files:**
- Modify: `apps/web/package.json` (add jwt-decode)
- Create: `apps/web/src/shared/tenant/index.ts`
- Create: `apps/web/src/shared/tenant/constants.ts`
- Create: `apps/web/src/shared/tenant/jwtClaims.ts`
- Create: `apps/web/src/shared/tenant/tenantContext.tsx`
- Create: `apps/web/src/shared/tenant/__tests__/jwtClaims.test.ts`
- Create: `apps/web/src/shared/tenant/__tests__/tenantContext.test.tsx`

- [ ] **Step 1.1: Create branch + install jwt-decode**

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/C6-frontend-tenant
cd apps/web
npm install jwt-decode
```

This adds `jwt-decode` to `package.json` and `package-lock.json`. The current jwt-decode v4 has the named export `jwtDecode`.

- [ ] **Step 1.2: Create `apps/web/src/shared/tenant/constants.ts`**

```typescript
/**
 * Reserved subdomains that NEVER resolve to a tenant.
 * Mirrors apps/api/apps/tenancy/constants.py RESERVED_SUBDOMAINS.
 */
export const RESERVED_SUBDOMAINS = new Set<string>([
  'admin',     // admin.vyntia.pe — Vyntia staff panel
  'app',       // app.vyntia.pe — workspace switcher
  'www',       // www.vyntia.pe — marketing
  'api',       // api.vyntia.pe — public API alias
  'docs',
  'status',
  'blog',
  'mail',
  'support',
  'help',
  'vyntia',
  // local/dev
  'localhost',
  '127',
  '0',
])
```

- [ ] **Step 1.3: Create `apps/web/src/shared/tenant/jwtClaims.ts`**

```typescript
import { jwtDecode } from 'jwt-decode'

/**
 * Claims a Vyntia JWT may carry. The base claims (sub, exp, iat, jti, token_type)
 * always exist; tenant claims are present when the token was issued in a tenant
 * context (post-C.4); impersonation claims are present when issued via the admin
 * impersonation flow (post-C.5).
 */
export interface JwtClaims {
  sub?: string                  // user_id (set by simplejwt)
  user_id?: string              // user_id (custom)
  exp?: number
  iat?: number
  jti?: string
  token_type?: string

  // Tenant claims (C.4)
  tenant_id?: string
  tenant_slug?: string
  membership_role?: string

  // Impersonation claims (C.5)
  impersonated_by?: string
  support_session_id?: string
}

/**
 * Decode a JWT without verifying signature (signature verification happens server-side).
 * Returns null if the token is malformed.
 */
export function decodeJwtClaims(token: string | null | undefined): JwtClaims | null {
  if (!token) return null
  try {
    return jwtDecode<JwtClaims>(token)
  } catch {
    return null
  }
}

/**
 * Check whether a JWT carries impersonation claims (used by ImpersonationBanner).
 */
export function isImpersonationToken(token: string | null | undefined): boolean {
  const claims = decodeJwtClaims(token)
  return !!claims?.impersonated_by
}
```

- [ ] **Step 1.4: Create `apps/web/src/shared/tenant/tenantContext.tsx`**

```typescript
import { createContext, useContext, useMemo, type ReactNode } from 'react'

import { RESERVED_SUBDOMAINS } from './constants'

/**
 * The "type" of host the user is on. Drives App.tsx branching.
 * - 'tenant'   : a real tenant subdomain (e.g., acme.vyntia.pe)
 * - 'admin'    : admin.vyntia.pe — Vyntia staff panel
 * - 'app'      : app.vyntia.pe — workspace switcher
 * - 'www'      : www.vyntia.pe / vyntia.pe — marketing redirect
 * - 'unknown'  : reserved subdomains we don't have a route for, or local dev
 */
export type TenantHostType = 'tenant' | 'admin' | 'app' | 'www' | 'unknown'

export interface TenantContextValue {
  type: TenantHostType
  /** When type === 'tenant', the slug (e.g., 'acme'). Empty otherwise. */
  slug: string
  /** Full hostname including port (for debugging). */
  host: string
}

const TenantContext = createContext<TenantContextValue | null>(null)

/**
 * Resolve the tenant context from a hostname (separate from the provider so we
 * can unit-test it).
 */
export function resolveTenantFromHost(host: string): TenantContextValue {
  const hostname = host.split(':', 1)[0].toLowerCase()
  const parts = hostname.split('.')
  const subdomain = parts[0] || ''

  if (subdomain === 'www' || hostname === 'vyntia.pe') {
    return { type: 'www', slug: '', host }
  }
  if (subdomain === 'admin') {
    return { type: 'admin', slug: '', host }
  }
  if (subdomain === 'app') {
    return { type: 'app', slug: '', host }
  }
  if (RESERVED_SUBDOMAINS.has(subdomain)) {
    return { type: 'unknown', slug: '', host }
  }
  // Looks like a tenant subdomain
  return { type: 'tenant', slug: subdomain, host }
}

interface TenantProviderProps {
  children: ReactNode
  /** Override host (used by tests). Default: window.location.host */
  host?: string
}

export function TenantProvider({ children, host }: TenantProviderProps) {
  const value = useMemo(
    () => resolveTenantFromHost(host ?? window.location.host),
    [host],
  )
  return <TenantContext.Provider value={value}>{children}</TenantContext.Provider>
}

export function useTenant(): TenantContextValue {
  const value = useContext(TenantContext)
  if (value === null) {
    throw new Error('useTenant must be used within a TenantProvider')
  }
  return value
}
```

- [ ] **Step 1.5: Create `apps/web/src/shared/tenant/index.ts`**

```typescript
export { RESERVED_SUBDOMAINS } from './constants'
export { decodeJwtClaims, isImpersonationToken, type JwtClaims } from './jwtClaims'
export {
  TenantProvider,
  useTenant,
  resolveTenantFromHost,
  type TenantContextValue,
  type TenantHostType,
} from './tenantContext'
```

- [ ] **Step 1.6: Write tests for jwtClaims**

Create `apps/web/src/shared/tenant/__tests__/jwtClaims.test.ts`:

```typescript
import { describe, it, expect } from 'vitest'

import { decodeJwtClaims, isImpersonationToken } from '../jwtClaims'

// JWT with payload: {"tenant_id":"abc","tenant_slug":"acme","sub":"u1"}
// Header: {"alg":"HS256","typ":"JWT"}, signature: "fake"
const SAMPLE_JWT_TENANT =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJhYmMiLCJ0ZW5hbnRfc2x1ZyI6ImFjbWUiLCJzdWIiOiJ1MSJ9.fake'

// JWT with: {"impersonated_by":"staff1","support_session_id":"sess1"}
const SAMPLE_JWT_IMPERSONATION =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpbXBlcnNvbmF0ZWRfYnkiOiJzdGFmZjEiLCJzdXBwb3J0X3Nlc3Npb25faWQiOiJzZXNzMSJ9.fake'

describe('decodeJwtClaims', () => {
  it('returns null for null/undefined/empty', () => {
    expect(decodeJwtClaims(null)).toBeNull()
    expect(decodeJwtClaims(undefined)).toBeNull()
    expect(decodeJwtClaims('')).toBeNull()
  })

  it('returns null for malformed token', () => {
    expect(decodeJwtClaims('not-a-jwt')).toBeNull()
  })

  it('decodes tenant claims', () => {
    const claims = decodeJwtClaims(SAMPLE_JWT_TENANT)
    expect(claims).not.toBeNull()
    expect(claims!.tenant_id).toBe('abc')
    expect(claims!.tenant_slug).toBe('acme')
    expect(claims!.sub).toBe('u1')
  })

  it('decodes impersonation claims', () => {
    const claims = decodeJwtClaims(SAMPLE_JWT_IMPERSONATION)
    expect(claims!.impersonated_by).toBe('staff1')
    expect(claims!.support_session_id).toBe('sess1')
  })
})

describe('isImpersonationToken', () => {
  it('returns false for non-impersonation token', () => {
    expect(isImpersonationToken(SAMPLE_JWT_TENANT)).toBe(false)
  })

  it('returns true when impersonated_by claim is present', () => {
    expect(isImpersonationToken(SAMPLE_JWT_IMPERSONATION)).toBe(true)
  })

  it('returns false for null', () => {
    expect(isImpersonationToken(null)).toBe(false)
  })
})
```

- [ ] **Step 1.7: Write tests for tenantContext resolution**

Create `apps/web/src/shared/tenant/__tests__/tenantContext.test.tsx`:

```typescript
import { describe, it, expect } from 'vitest'

import { resolveTenantFromHost } from '../tenantContext'

describe('resolveTenantFromHost', () => {
  it('resolves tenant subdomain', () => {
    const result = resolveTenantFromHost('acme.vyntia.pe')
    expect(result.type).toBe('tenant')
    expect(result.slug).toBe('acme')
  })

  it('strips port', () => {
    const result = resolveTenantFromHost('acme.vyntia.pe:8000')
    expect(result.type).toBe('tenant')
    expect(result.slug).toBe('acme')
  })

  it('treats admin as admin type', () => {
    const result = resolveTenantFromHost('admin.vyntia.pe')
    expect(result.type).toBe('admin')
    expect(result.slug).toBe('')
  })

  it('treats app as app type', () => {
    const result = resolveTenantFromHost('app.vyntia.pe')
    expect(result.type).toBe('app')
  })

  it('treats www as www type', () => {
    expect(resolveTenantFromHost('www.vyntia.pe').type).toBe('www')
    expect(resolveTenantFromHost('vyntia.pe').type).toBe('www')
  })

  it('treats localhost as unknown', () => {
    expect(resolveTenantFromHost('localhost:5173').type).toBe('unknown')
  })

  it('treats other reserved subdomains as unknown', () => {
    expect(resolveTenantFromHost('docs.vyntia.pe').type).toBe('unknown')
    expect(resolveTenantFromHost('blog.vyntia.pe').type).toBe('unknown')
  })

  it('handles uppercase host correctly', () => {
    const result = resolveTenantFromHost('ACME.VYNTIA.PE')
    expect(result.type).toBe('tenant')
    expect(result.slug).toBe('acme')
  })
})
```

- [ ] **Step 1.8: Run tests + build**

```bash
cd D:/VYNTIA/apps/web
npx vitest run src/shared/tenant 2>&1 | tail -10
npm run build 2>&1 | tail -3
```

Expected: ~12 new tests pass; build succeeds.

- [ ] **Step 1.9: Commit**

```bash
cd D:/VYNTIA
git add apps/web/package.json apps/web/package-lock.json \
        apps/web/src/shared/tenant/
git commit -m "feat(C6): tenant resolution utilities + jwt-decode dep + ContextProvider"
```

---

## Task 2: ApiClient tenant guard + ImpersonationBanner

**Files:**
- Modify: `apps/web/src/shared/api/api.ts` (add tenant guard interceptor)
- Create: `apps/web/src/features/tenancy/index.ts`
- Create: `apps/web/src/features/tenancy/components/ImpersonationBanner.tsx`

- [ ] **Step 2.1: Add a tenant guard to apiClient**

Read `apps/web/src/shared/api/api.ts` to see the existing axios setup. The new logic:
- Before each request, decode the access token's `tenant_slug` claim
- Compare with `window.location.host`'s subdomain
- If mismatch (e.g., we have an old `acme` token but we're on `beta.vyntia.pe`), clear localStorage tokens and let the response interceptor's 401 path redirect to login

Implement by adding a small helper at the top of the file:

```typescript
import { decodeJwtClaims } from '@/shared/tenant/jwtClaims'
import { resolveTenantFromHost } from '@/shared/tenant/tenantContext'

function isTokenForCurrentTenant(token: string): boolean {
  const claims = decodeJwtClaims(token)
  // Token without tenant_slug claim (legacy/admin/exchange tokens) is permissive
  if (!claims?.tenant_slug) return true
  const host = resolveTenantFromHost(window.location.host)
  // On a tenant subdomain, claim must match
  if (host.type === 'tenant') {
    return claims.tenant_slug === host.slug
  }
  // On reserved hosts (admin/app/etc), tenant tokens are not relevant — they shouldn't be sent
  // but we don't reject (legacy compatibility)
  return true
}
```

Then in the existing request interceptor, before adding the Authorization header, call this check. If it returns `false`, `localStorage.removeItem('access_token')` and `localStorage.removeItem('refresh_token')`, and DON'T attach the Authorization header. The next request will proceed unauthenticated and the response interceptor (already in place for 401) will redirect to login.

The exact insertion point depends on existing code structure — read it first and adapt.

- [ ] **Step 2.2: Create `features/tenancy/index.ts` (empty barrel for now)**

```typescript
export { ImpersonationBanner } from './components/ImpersonationBanner'
```

- [ ] **Step 2.3: Create `features/tenancy/components/ImpersonationBanner.tsx`**

```typescript
import { AlertTriangle } from 'lucide-react'
import { useMemo } from 'react'

import { decodeJwtClaims } from '@/shared/tenant/jwtClaims'

/**
 * Renders a sticky top banner when the active session is a Vyntia support
 * impersonation (JWT carries `impersonated_by` claim).
 *
 * Mounted globally inside <TenantApp> in App.tsx. Returns null when not in
 * an impersonation session.
 */
export function ImpersonationBanner() {
  const claims = useMemo(() => {
    const token = localStorage.getItem('access_token')
    return decodeJwtClaims(token)
  }, [])

  if (!claims?.impersonated_by) return null

  return (
    <div
      className="sticky top-0 z-50 flex items-center justify-center gap-2 bg-amber-500 px-4 py-2 text-sm font-medium text-amber-950 shadow"
      role="alert"
    >
      <AlertTriangle size={16} aria-hidden />
      <span>
        Sesión de soporte Vyntia activa — todas las acciones quedan registradas.
      </span>
    </div>
  )
}
```

- [ ] **Step 2.4: Build + lint check**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | head -5
```

Expected: build OK, no new TypeScript errors.

- [ ] **Step 2.5: Commit**

```bash
cd D:/VYNTIA
git add apps/web/src/shared/api/api.ts \
        apps/web/src/features/tenancy/
git commit -m "feat(C6): apiClient tenant guard + ImpersonationBanner component"
```

---

## Task 3: Workspace switcher feature

**Files:**
- Create: `apps/web/src/features/workspace-switcher/index.ts`
- Create: `apps/web/src/features/workspace-switcher/services/workspaceService.ts`
- Create: `apps/web/src/features/workspace-switcher/pages/WorkspacesPage.tsx`
- Create: `apps/web/src/features/workspace-switcher/__tests__/workspaceService.test.ts`

- [ ] **Step 3.1: Create `services/workspaceService.ts`**

```typescript
import { apiClient } from '@/shared/api/api'

export interface Workspace {
  tenant_id: string
  slug: string
  name: string
  plan: string
  role: string
}

export interface ExchangeResponse {
  exchange_token: string
  redirect_url: string
}

/**
 * GET /api/v1/workspaces/ — list the user's active TenantMemberships.
 */
export async function fetchWorkspaces(): Promise<Workspace[]> {
  const response = await apiClient.get('/v1/workspaces/')
  // Standard wrapper unwrap: { success, message, data: Workspace[] }
  return response.data?.data ?? []
}

/**
 * POST /api/v1/workspaces/<slug>/exchange/ — get a short-lived token to
 * jump to <slug>.vyntia.pe.
 */
export async function exchangeWorkspace(slug: string): Promise<ExchangeResponse> {
  const response = await apiClient.post(`/v1/workspaces/${slug}/exchange/`)
  return response.data?.data ?? { exchange_token: '', redirect_url: '' }
}
```

- [ ] **Step 3.2: Create `pages/WorkspacesPage.tsx`**

```typescript
import { useQuery } from '@tanstack/react-query'
import { Building2, ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card'
import {
  exchangeWorkspace,
  fetchWorkspaces,
  type Workspace,
} from '../services/workspaceService'

/**
 * Workspace switcher page — the entry point at app.vyntia.pe.
 *
 * After login at app.vyntia.pe, lists the user's active workspaces.
 * Selecting one calls /workspaces/<slug>/exchange/ and redirects the browser
 * to <slug>.vyntia.pe/auth/exchange?token=<exchange_token>.
 */
export function WorkspacesPage() {
  const navigate = useNavigate()
  const { data, isLoading, isError } = useQuery({
    queryKey: ['workspaces'],
    queryFn: fetchWorkspaces,
  })

  async function handleSelect(workspace: Workspace) {
    try {
      const { redirect_url } = await exchangeWorkspace(workspace.slug)
      if (redirect_url) {
        window.location.href = redirect_url
      } else {
        toast.error('No se pudo abrir el workspace.')
      }
    } catch {
      toast.error(`Error al abrir ${workspace.name}.`)
    }
  }

  if (isLoading) {
    return <div className="p-8 text-center">Cargando workspaces…</div>
  }

  if (isError) {
    return (
      <div className="p-8 text-center text-destructive">
        Error al cargar workspaces. Intenta nuevamente.
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="mx-auto max-w-md p-8">
        <Card>
          <CardHeader>
            <CardTitle>Sin workspaces</CardTitle>
            <CardDescription>
              No tienes acceso activo a ningún workspace de VYNTIA. Si crees que
              esto es un error, contacta a tu administrador.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" onClick={() => navigate('/login')}>
              Volver al login
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-2 text-2xl font-semibold">Selecciona un workspace</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Tienes acceso a {data.length} workspace{data.length !== 1 ? 's' : ''} en VYNTIA.
      </p>
      <div className="space-y-3">
        {data.map((workspace) => (
          <button
            key={workspace.tenant_id}
            type="button"
            onClick={() => handleSelect(workspace)}
            className="flex w-full items-center gap-4 rounded-lg border bg-card p-4 text-left transition-colors hover:bg-accent"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
              <Building2 size={20} aria-hidden />
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-medium">{workspace.name}</div>
              <div className="text-xs text-muted-foreground">
                {workspace.slug}.vyntia.pe · {workspace.role} · plan {workspace.plan}
              </div>
            </div>
            <ChevronRight size={18} className="text-muted-foreground" aria-hidden />
          </button>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3.3: Create `index.ts` barrel**

```typescript
export { WorkspacesPage } from './pages/WorkspacesPage'
export {
  fetchWorkspaces,
  exchangeWorkspace,
  type Workspace,
  type ExchangeResponse,
} from './services/workspaceService'
```

- [ ] **Step 3.4: Write tests**

Create `apps/web/src/features/workspace-switcher/__tests__/workspaceService.test.ts`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

import { apiClient } from '@/shared/api/api'
import {
  exchangeWorkspace,
  fetchWorkspaces,
} from '../services/workspaceService'

describe('workspaceService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('fetchWorkspaces unwraps standard response shape', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        success: true,
        message: 'ok',
        data: [
          { tenant_id: 't1', slug: 'acme', name: 'Acme', plan: 'starter', role: 'admin' },
        ],
      },
    })
    const workspaces = await fetchWorkspaces()
    expect(workspaces).toHaveLength(1)
    expect(workspaces[0].slug).toBe('acme')
    expect(apiClient.get).toHaveBeenCalledWith('/v1/workspaces/')
  })

  it('fetchWorkspaces returns empty array on missing data', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: {} })
    expect(await fetchWorkspaces()).toEqual([])
  })

  it('exchangeWorkspace POSTs and returns redirect_url', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: {
        success: true,
        data: {
          exchange_token: 'token-xyz',
          redirect_url: 'https://acme.vyntia.pe/auth/exchange?token=token-xyz',
        },
      },
    })
    const result = await exchangeWorkspace('acme')
    expect(result.redirect_url).toContain('acme.vyntia.pe')
    expect(apiClient.post).toHaveBeenCalledWith('/v1/workspaces/acme/exchange/')
  })
})
```

- [ ] **Step 3.5: Run tests + build**

```bash
cd D:/VYNTIA/apps/web
npx vitest run src/features/workspace-switcher 2>&1 | tail -10
npm run build 2>&1 | tail -3
```

Expected: 3 new tests pass, build succeeds.

- [ ] **Step 3.6: Commit**

```bash
cd D:/VYNTIA
git add apps/web/src/features/workspace-switcher/
git commit -m "feat(C6): workspace switcher feature (WorkspacesPage + service)"
```

---

## Task 4: Activation page

**Files:**
- Create: `apps/web/src/features/tenancy/pages/ActivationPage.tsx`
- Create: `apps/web/src/features/tenancy/services/activationService.ts`
- Modify: `apps/web/src/features/tenancy/index.ts` (add new exports)

- [ ] **Step 4.1: Create `services/activationService.ts`**

```typescript
import { apiClient } from '@/shared/api/api'

export interface ActivationRequest {
  token: string
  name: string
  password: string
}

export interface ActivationResponse {
  access: string
  refresh: string
  tenant: { slug: string; name: string }
  user: { id: string; email: string; username: string }
  role: string
}

export async function activateInvitation(
  payload: ActivationRequest,
): Promise<ActivationResponse> {
  const response = await apiClient.post('/v1/auth/activate/', payload)
  return response.data?.data
}
```

- [ ] **Step 4.2: Create `pages/ActivationPage.tsx`**

```typescript
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'
import { z } from 'zod'

import { Button } from '@/shared/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'

import { activateInvitation } from '../services/activationService'

const ActivationSchema = z.object({
  name: z.string().min(2, 'Nombre requerido'),
  password: z.string().min(8, 'Mínimo 8 caracteres'),
})

type FormValues = z.infer<typeof ActivationSchema>

export function ActivationPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const token = params.get('token') ?? ''

  const form = useForm<FormValues>({
    resolver: zodResolver(ActivationSchema),
    defaultValues: { name: '', password: '' },
  })

  const mutation = useMutation({
    mutationFn: (values: FormValues) =>
      activateInvitation({ token, name: values.name, password: values.password }),
    onSuccess: (data) => {
      // Persist tokens and redirect to dashboard
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      toast.success(`Cuenta activada — bienvenido a ${data.tenant.name}`)
      navigate('/dashboard')
    },
    onError: () => {
      toast.error(
        'No se pudo activar la cuenta. El enlace puede haber expirado o ya se utilizó.',
      )
    },
  })

  if (!token) {
    return (
      <div className="mx-auto max-w-md p-8">
        <Card>
          <CardHeader>
            <CardTitle>Enlace inválido</CardTitle>
            <CardDescription>
              Este enlace de activación no es válido. Solicita uno nuevo a tu
              administrador de VYNTIA.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-md p-8">
      <Card>
        <CardHeader>
          <CardTitle>Activa tu cuenta VYNTIA</CardTitle>
          <CardDescription>
            Configura tu nombre y contraseña para acceder a tu workspace.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={form.handleSubmit((values) => mutation.mutate(values))}
            className="space-y-4"
          >
            <div className="space-y-2">
              <Label htmlFor="name">Nombre completo</Label>
              <Input id="name" autoComplete="name" {...form.register('name')} />
              {form.formState.errors.name && (
                <p className="text-xs text-destructive">
                  {form.formState.errors.name.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
                {...form.register('password')}
              />
              {form.formState.errors.password && (
                <p className="text-xs text-destructive">
                  {form.formState.errors.password.message}
                </p>
              )}
            </div>
            <Button type="submit" className="w-full" disabled={mutation.isPending}>
              {mutation.isPending ? 'Activando…' : 'Activar mi cuenta'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
```

- [ ] **Step 4.3: Update `features/tenancy/index.ts`**

```typescript
export { ImpersonationBanner } from './components/ImpersonationBanner'
export { ActivationPage } from './pages/ActivationPage'
export {
  activateInvitation,
  type ActivationRequest,
  type ActivationResponse,
} from './services/activationService'
```

- [ ] **Step 4.4: Build check**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | head -5
```

Expected: build OK, no new TS errors.

- [ ] **Step 4.5: Commit**

```bash
cd D:/VYNTIA
git add apps/web/src/features/tenancy/
git commit -m "feat(C6): activation page consumes /api/v1/auth/activate/"
```

---

## Task 5: App.tsx routing — branch by tenant type + register routes

**Files:**
- Modify: `apps/web/src/App.tsx`

- [ ] **Step 5.1: Read App.tsx structure**

```bash
cd D:/VYNTIA
head -80 apps/web/src/App.tsx
```

Identify:
- Where providers are (`QueryClientProvider`, `ThemeProvider`, `AuthProvider`)
- Where the Router is mounted
- Where routes are registered

- [ ] **Step 5.2: Wrap with TenantProvider + add tenant-aware routing**

Update `apps/web/src/App.tsx`:

1. Import the new pieces at the top:
   ```typescript
   import { TenantProvider, useTenant } from '@/shared/tenant'
   import { ActivationPage, ImpersonationBanner } from '@/features/tenancy'
   import { WorkspacesPage } from '@/features/workspace-switcher'
   ```

2. Wrap the existing tree (after `ThemeProvider`, before `AuthProvider`) with `<TenantProvider>`:

   ```tsx
   <QueryClientProvider client={queryClient}>
     <ThemeProvider>
       <TenantProvider>
         <AuthProvider>
           {/* existing content */}
         </AuthProvider>
       </TenantProvider>
     </ThemeProvider>
   </QueryClientProvider>
   ```

3. Inside the router, add a tenant-type-aware shell. The current router structure renders all routes under one tree; we add a new outer component `<TenantHostShell>` that branches by host type:

   - For `type === 'app'` → render only `WorkspacesPage` (and login)
   - For `type === 'admin'` → render placeholder until C.7 ships the AdminApp (a simple "Coming soon" message)
   - For `type === 'www'` → render placeholder pointing users to `/login` or marketing
   - For `type === 'tenant'` or `type === 'unknown'` (dev `localhost`) → render the existing route tree (login + dashboard + features) — this is the legacy behavior so existing tests keep working

4. Register the activation route at the top of the route tree (BEFORE the auth-redirect logic), so unauthenticated users with an invitation link can reach it:

   ```tsx
   <Routes>
     <Route path="/activate" element={<ActivationPage />} />
     {/* existing routes */}
   </Routes>
   ```

5. Mount `<ImpersonationBanner />` near the top of the authenticated layout (e.g., right above the existing `<Layout>` content). Easiest: put it inside the `<Layout>` component itself if available, or just above `<AdminLayout>` for admin pages. For simplicity, put it as the first child of the main authenticated app shell.

Concrete sketch (adapt to actual file structure):

```tsx
function TenantHostShell({ children }: { children: ReactNode }) {
  const tenant = useTenant()

  if (tenant.type === 'app') {
    return (
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="*" element={<WorkspacesPage />} />
      </Routes>
    )
  }

  if (tenant.type === 'admin') {
    // Placeholder until C.7 ships the admin panel
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-semibold">VYNTIA Admin</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Panel de administración — disponible en C.7.
        </p>
      </div>
    )
  }

  // tenant or unknown → legacy app
  return <>{children}</>
}
```

Wrap the existing `<Routes>` block (or wherever the legacy tree starts) with `<TenantHostShell>`.

- [ ] **Step 5.3: Build + lint check**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | head -5
npm test -- --run 2>&1 | tail -5
```

Expected: build OK, no new TS errors, all vitest tests still pass (≥17).

- [ ] **Step 5.4: Commit**

```bash
cd D:/VYNTIA
git add apps/web/src/App.tsx
git commit -m "feat(C6): App.tsx branches routing by tenant host type + registers /activate"
```

---

## Task 6: Final verification + merge

- [ ] **Step 6.1: Full frontend baseline**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | wc -l
npm test -- --run 2>&1 | tail -5
npm run lint 2>&1 | tail -3
```

Expected: build success, 0 new TS errors (only pre-existing BlankEnum), ≥17 vitest passes, ≤634 lint warnings.

- [ ] **Step 6.2: Backend baseline (sanity — no backend changes)**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -3
```

Expected: ≥268 passed (unchanged from C.5).

- [ ] **Step 6.3: Update master roadmap**

In `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`, find the C.6 row and update the "Detailed plan" cell to:

```
`2026-05-09-vyntia-C6-frontend-tenant.md` ✅ merged 2026-05-09
```

- [ ] **Step 6.4: Commit roadmap update**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md
git commit -m "docs(C6): mark C.6 done in master roadmap"
```

- [ ] **Step 6.5: Merge to master**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/C6-frontend-tenant \
  -m "Merge C.6: frontend tenant features (provider + activate + workspaces + impersonation banner)"
```

---

## Self-Review

### Spec coverage check

| Spec § 8 requirement | Covered by task |
|---|---|
| Boot-time tenant resolution from subdomain | Task 1 (`resolveTenantFromHost`, `TenantProvider`) |
| `RESERVED_SUBDOMAINS` set | Task 1 (constants.ts) |
| App.tsx branched by tenant type | Task 5 |
| `WorkspaceSwitcher` page on app.vyntia.pe | Task 3 |
| `ActivationPage` at /activate?token=... | Task 4 |
| `ImpersonationBanner` component | Task 2 |
| ApiClient JWT-tenant guard | Task 2 |

### Spec deviations

1. **`TenantSettingsPage` and `MembershipsPage` deferred** — spec § 8.3 lists these but they're admin UX (manage tenant settings, edit memberships). The auth + onboarding loop works without them. They become C.7 (admin-side) or a future polish sub-layer.

2. **`TenantBadge` deferred** — small chip component for the layout header. Visual polish, defer.

3. **AdminApp placeholder, not real** — Task 5 ships a "Coming soon" text for admin.vyntia.pe. The real admin panel is C.7.

4. **No e2e Playwright tests** — vitest unit + integration is sufficient for C.6. Cross-tenant isolation E2E is C.8.

5. **ImpersonationBanner reads `localStorage` directly** instead of subscribing to a context — simpler and works because the banner only needs to render once at mount (no live updates). For a more reactive design, a future sub-layer can wire it through TenantContext or a dedicated impersonation context.

### Placeholder scan

- All code blocks are runnable.
- The "wrap with TenantHostShell" sketch in Task 5 Step 5.2 is a sketch that adapts to actual App.tsx structure — the implementer reads first and adjusts. Documented as part of the step instruction, not a TBD.

### Type consistency

- `TenantHostType` consistently typed as `'tenant' | 'admin' | 'app' | 'www' | 'unknown'`.
- `JwtClaims` type matches the backend's actual JWT payload (sub, exp, tenant_id, tenant_slug, membership_role, impersonated_by, support_session_id).
- `Workspace` shape matches the backend's `WorkspaceSerializer` (tenant_id, slug, name, plan, role).

### Out of scope (deferred)

- Admin frontend (C.7)
- TenantSettings / Memberships UI (future)
- TenantBadge UI (future)
- E2E cross-tenant isolation tests (C.8)
- Backend changes (none — C.6 is frontend only)

---

**Plan complete.** When executed, C.6 ships ~6 commits, ~12 new files (~700 LOC), 3 modified files, ~15 new vitest tests. Frontend test baseline grows from 7 → ~22.
