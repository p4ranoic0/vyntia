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
import { dossierService } from '../dossierService'

describe('dossierService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('list hits /api/v1/documents/digital-dossiers/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 'd1', is_closed: false }] } },
    } as never)
    const out = await dossierService.list()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/documents/digital-dossiers/',
    )
  })

  it('create posts employee', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'd1', sections: [] } },
    } as never)
    await dossierService.create('e1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({ employee: 'e1' })
  })

  it('build hits /build/', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'd1', sections: [] } },
    } as never)
    await dossierService.build('d1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/documents/digital-dossiers/d1/build/',
    )
  })

  it('downloadConsolidatedPdf requests blob', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: new Blob(['%PDF'], { type: 'application/pdf' }),
    } as never)
    const blob = await dossierService.downloadConsolidatedPdf('d1')
    expect(blob).toBeInstanceOf(Blob)
    const call = vi.mocked(apiClient.get).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/documents/digital-dossiers/d1/consolidated-pdf/')
    expect((call?.[1] as { responseType?: string } | undefined)?.responseType).toBe('blob')
  })

  it('listAccessLogs filters by document', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await dossierService.listAccessLogs('doc1')
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('document=doc1')
  })
})
