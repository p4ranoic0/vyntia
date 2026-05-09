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
