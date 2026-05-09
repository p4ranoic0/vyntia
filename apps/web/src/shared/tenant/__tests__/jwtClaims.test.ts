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
