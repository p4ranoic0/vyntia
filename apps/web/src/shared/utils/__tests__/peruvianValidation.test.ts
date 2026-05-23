import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

import {
  validateDNI,
  validateCE,
  validateRUC,
  validateAge18Plus,
  formatDNI,
} from '../peruvianValidation'

describe('validateDNI', () => {
  it('accepts exactly 8 digits', () => {
    expect(validateDNI('12345678')).toBe(true)
  })
  it('rejects fewer or more than 8 digits', () => {
    expect(validateDNI('1234567')).toBe(false)
    expect(validateDNI('123456789')).toBe(false)
  })
  it('rejects non-numeric', () => {
    expect(validateDNI('1234567a')).toBe(false)
    expect(validateDNI('')).toBe(false)
  })
})

describe('validateCE', () => {
  it('accepts 8 to 12 digits (backend parity)', () => {
    expect(validateCE('12345678')).toBe(true)
    expect(validateCE('123456789')).toBe(true)
    expect(validateCE('123456789012')).toBe(true)
  })
  it('rejects fewer than 8 or more than 12 digits', () => {
    expect(validateCE('1234567')).toBe(false)
    expect(validateCE('1234567890123')).toBe(false)
  })
  it('rejects non-numeric', () => {
    expect(validateCE('ABCD1234')).toBe(false)
  })
})

describe('validateRUC', () => {
  it('accepts exactly 11 digits', () => {
    expect(validateRUC('20123456789')).toBe(true)
  })
  it('rejects wrong length or non-numeric', () => {
    expect(validateRUC('2012345678')).toBe(false)
    expect(validateRUC('201234567890')).toBe(false)
    expect(validateRUC('2012345678a')).toBe(false)
  })
})

describe('validateAge18Plus', () => {
  beforeEach(() => {
    // Freeze "today" to 2026-05-23 (matches the Bloque H run date).
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-05-23T12:00:00'))
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('accepts someone who turned 18 exactly today', () => {
    expect(validateAge18Plus('2008-05-23')).toBe(true)
  })
  it('accepts someone older than 18', () => {
    expect(validateAge18Plus('2000-01-01')).toBe(true)
    expect(validateAge18Plus(new Date('1990-12-31'))).toBe(true)
  })
  it('rejects someone who turns 18 tomorrow', () => {
    expect(validateAge18Plus('2008-05-24')).toBe(false)
  })
  it('rejects a future birth date', () => {
    expect(validateAge18Plus('2030-01-01')).toBe(false)
  })
  it('rejects an invalid date string', () => {
    expect(validateAge18Plus('not-a-date')).toBe(false)
  })
})

describe('formatDNI', () => {
  it('strips non-digits', () => {
    expect(formatDNI('12-34 56a78')).toBe('12345678')
  })
  it('caps at 8 characters', () => {
    expect(formatDNI('1234567890')).toBe('12345678')
  })
  it('returns empty for no digits', () => {
    expect(formatDNI('abc')).toBe('')
  })
})
