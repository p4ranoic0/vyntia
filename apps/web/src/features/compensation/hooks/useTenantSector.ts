/**
 * useTenantSector — placeholder hook returning the tenant's sector
 * ('private' | 'public').
 *
 * B.7 ships this as a defensible gate point. Today the frontend has no
 * direct source for tenant.sector (the backend exposes it but it's not in
 * JWT claims nor in useTenant). To preserve the UI-only gate intent from
 * ADR-B.6, this hook returns 'private' as the default, since the CCF
 * compliance feature only applies to private-sector tenants. Public-sector
 * tenants get B.8 (MPP/CPE) instead.
 *
 * TODO(post-B.7): once the JWT or a dedicated `/api/v1/tenancy/current/`
 * endpoint exposes `sector`, rewrite this hook to read from that source.
 * Consumers using `useTenantSector()` will pick up real data without
 * changes.
 */
export function useTenantSector(): 'private' | 'public' | 'unknown' {
  return 'private'
}
