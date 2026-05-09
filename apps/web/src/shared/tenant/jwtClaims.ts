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
