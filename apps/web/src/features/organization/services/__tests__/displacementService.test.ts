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
import { displacementService } from '../displacementService'

describe('displacementService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('list hits /api/v1/organization/displacements/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 'd1', kind: 'rotacion' }] } },
    } as never)
    const out = await displacementService.list()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/organization/displacements/',
    )
  })

  it('create POSTs payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'd1', kind: 'encargatura', status: 'draft' } },
    } as never)
    await displacementService.create({ kind: 'encargatura' } as never)
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/organization/displacements/',
    )
  })

  it('submit hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'd1', status: 'pending_supervisor' } },
    } as never)
    await displacementService.submit('d1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/organization/displacements/d1/submit/',
    )
  })

  it('approval chain endpoints', async () => {
    vi.mocked(apiClient.post)
      .mockResolvedValueOnce({ data: { data: {} } } as never)
      .mockResolvedValueOnce({ data: { data: {} } } as never)
      .mockResolvedValueOnce({ data: { data: {} } } as never)
    await displacementService.approveSupervisor('d1')
    await displacementService.approveHR('d1')
    await displacementService.approveTitular('d1')
    const calls = vi.mocked(apiClient.post).mock.calls
    expect(calls[0]?.[0]).toBe('/api/v1/organization/displacements/d1/approve-supervisor/')
    expect(calls[1]?.[0]).toBe('/api/v1/organization/displacements/d1/approve-hr/')
    expect(calls[2]?.[0]).toBe('/api/v1/organization/displacements/d1/approve-titular/')
  })

  it('cancel forwards reason', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'd1', status: 'cancelled' } },
    } as never)
    await displacementService.cancel('d1', 'razón')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({ reason: 'razón' })
  })

  it('extend forwards new_end_date + reason', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'e1' } },
    } as never)
    await displacementService.extend('d1', {
      new_end_date: '2026-12-31', reason: 'X',
    })
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/organization/displacements/d1/extend/')
    expect(call?.[1]).toMatchObject({ new_end_date: '2026-12-31', reason: 'X' })
  })

  it('downloadResolutionPdf requests blob', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: new Blob(['%PDF'], { type: 'application/pdf' }),
    } as never)
    const blob = await displacementService.downloadResolutionPdf('d1')
    expect(blob).toBeInstanceOf(Blob)
    const call = vi.mocked(apiClient.get).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/organization/displacements/d1/resolution-pdf/')
    expect((call?.[1] as { responseType?: string } | undefined)?.responseType).toBe('blob')
  })
})
