/**
 * useTenantSector — placeholder hook returning the tenant's sector
 * ('private' | 'public') for B.8 sector-gated screens (CPE / CAP / MPP).
 *
 * Mirrors the compensation/useTenantSector hook (B.7). Both default to
 * 'private' until a JWT claim or `/api/v1/tenancy/current/` exposes
 * `sector`. B.8 pages invert the B.7 gate: they SHOW when sector === 'public'
 * and render an informational card otherwise.
 *
 * TODO(post-B.8): consolidate the two hooks into a shared one in
 *   `@/shared/tenant` once a real `sector` field exists in the tenant
 *   context.
 */
export function useTenantSector(): 'private' | 'public' | 'unknown' {
  return 'private'
}
