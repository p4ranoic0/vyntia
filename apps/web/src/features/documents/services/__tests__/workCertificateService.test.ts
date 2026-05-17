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
import { workCertificateService } from '../workCertificateService'

describe('workCertificateService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('list hits /api/v1/documents/work-certificates/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 'wc1', numero_constancia: 'CTR-2026-0001' }] } },
    } as never)
    const out = await workCertificateService.list()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/documents/work-certificates/',
    )
  })

  it('generate POSTs termination id', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'wc1', numero_constancia: 'CTR-2026-0002' } },
    } as never)
    await workCertificateService.generate('t1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/documents/work-certificates/generate/',
    )
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      termination: 't1',
    })
  })

  it('downloadPdf returns blob', async () => {
    const blob = new Blob(['x'], { type: 'application/pdf' })
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: blob } as never)
    const out = await workCertificateService.downloadPdf('wc1')
    expect(out).toBe(blob)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toBe(
      '/api/v1/documents/work-certificates/wc1/download-pdf/',
    )
  })
})
