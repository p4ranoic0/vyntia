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
