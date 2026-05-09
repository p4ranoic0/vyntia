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
