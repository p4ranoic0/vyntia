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
