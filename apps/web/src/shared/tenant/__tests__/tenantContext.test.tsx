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
