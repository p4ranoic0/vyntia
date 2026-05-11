import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('@/shared/api/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

import { apiClient } from '@/shared/api/api'
import { publicPositionService } from '../publicPositionService'

describe('publicPositionService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listRegisters with no type lists all', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: '1', title: 'CPE 2026', register_type: 'cpe' }] } },
    } as never)
    const items = await publicPositionService.listRegisters()
    expect(items).toHaveLength(1)
    expect(items[0].register_type).toBe('cpe')
    const url = vi.mocked(apiClient.get).mock.calls[0]?.[0] as string
    expect(url).toContain('/api/v1/organization/position-registers/')
    expect(url).not.toContain('register_type=')
  })

  it('listRegisters filters by type when provided', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await publicPositionService.listRegisters('cap')
    const url = vi.mocked(apiClient.get).mock.calls[0]?.[0] as string
    expect(url).toContain('register_type=cap')
  })

  it('createRegister POSTs payload and unwraps single item', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'new', title: 'CPE', register_type: 'cpe', version: 1 } },
    } as never)
    const reg = await publicPositionService.createRegister({
      register_type: 'cpe',
      title: 'CPE',
    })
    expect(reg.title).toBe('CPE')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/organization/position-registers/',
    )
  })

  it('approveRegister forwards effective_date', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: '1', status: 'approved' } },
    } as never)
    await publicPositionService.approveRegister('1', '2026-06-01')
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/organization/position-registers/1/approve/')
    expect(call?.[1]).toEqual({ effective_date: '2026-06-01' })
  })

  it('approveRegister sends empty body when no effective_date', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: '1', status: 'approved' } },
    } as never)
    await publicPositionService.approveRegister('1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({})
  })

  it('registerInServir posts reference body', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: '1', status: 'registered_servir' } },
    } as never)
    await publicPositionService.registerInServir('1', 'SERVIR-2026-001')
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/organization/position-registers/1/register-in-servir/')
    expect(call?.[1]).toEqual({ reference: 'SERVIR-2026-001' })
  })

  it('listEntries filters by register id', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await publicPositionService.listEntries('reg-abc')
    const url = vi.mocked(apiClient.get).mock.calls[0]?.[0] as string
    expect(url).toContain('register=reg-abc')
  })

  it('upsertEntry uses POST when no id', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'new', register: 'r', position: 'p' } },
    } as never)
    await publicPositionService.upsertEntry({
      register: 'r',
      position: 'p',
      sequence: 1,
    })
    expect(vi.mocked(apiClient.post).mock.calls).toHaveLength(1)
    expect(vi.mocked(apiClient.patch).mock.calls).toHaveLength(0)
  })

  it('upsertEntry uses PATCH when id provided', async () => {
    vi.mocked(apiClient.patch).mockResolvedValueOnce({
      data: { data: { id: 'existing' } },
    } as never)
    await publicPositionService.upsertEntry({
      id: 'existing',
      register: 'r',
      position: 'p',
    })
    const call = vi.mocked(apiClient.patch).mock.calls[0]
    expect(call?.[0]).toContain('/existing/')
  })

  it('downloadMPP requests blob from mpp-pdf endpoint', async () => {
    const blob = new Blob(['%PDF-1.4'], { type: 'application/pdf' })
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: blob } as never)
    const out = await publicPositionService.downloadMPP('reg-1')
    expect(out).toBe(blob)
    const call = vi.mocked(apiClient.get).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/organization/position-registers/reg-1/mpp-pdf/')
    expect(call?.[1]).toEqual({ responseType: 'blob' })
  })

  it('deleteEntry calls DELETE on the entry route', async () => {
    vi.mocked(apiClient.delete).mockResolvedValueOnce({} as never)
    await publicPositionService.deleteEntry('e-1')
    expect(vi.mocked(apiClient.delete).mock.calls[0]?.[0]).toBe(
      '/api/v1/organization/position-register-entries/e-1/',
    )
  })
})
