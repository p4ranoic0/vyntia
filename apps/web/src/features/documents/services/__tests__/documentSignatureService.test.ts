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
import { documentSignatureService } from '../documentSignatureService'

describe('documentSignatureService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('list hits /api/v1/documents/signatures/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 's1' }] } },
    } as never)
    const out = await documentSignatureService.list()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/documents/signatures/',
    )
  })

  it('create POSTs to base', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 's1', status: 'requested' } },
    } as never)
    await documentSignatureService.create({
      document: 'd1', signer_name: 'X', signer_doc_number: '1',
    } as never)
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/documents/signatures/',
    )
  })

  it('capture forwards payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 's1', status: 'signed' } },
    } as never)
    await documentSignatureService.capture('s1', { typed_name: 'Carla' })
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/documents/signatures/s1/capture/')
    expect(call?.[1]).toEqual({ typed_name: 'Carla' })
  })

  it('reject forwards reason', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 's1', status: 'rejected' } },
    } as never)
    await documentSignatureService.reject('s1', 'No conforme')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      reason: 'No conforme',
    })
  })

  it('expireOverdue returns count', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { expired_count: 3 } },
    } as never)
    const r = await documentSignatureService.expireOverdue()
    expect(r.expired_count).toBe(3)
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/documents/signatures/expire-overdue/',
    )
  })
})
