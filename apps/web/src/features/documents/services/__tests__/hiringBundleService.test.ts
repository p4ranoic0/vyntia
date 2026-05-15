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
import { hiringBundleService } from '../hiringBundleService'

describe('hiringBundleService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('listBundles hits /api/v1/documents/hiring-bundles/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 'b1', status: 'draft' }] } },
    } as never)
    const out = await hiringBundleService.listBundles()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/documents/hiring-bundles/',
    )
  })

  it('createBundle forwards employee + item_kinds', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'b1', status: 'draft', items: [] } },
    } as never)
    await hiringBundleService.createBundle({
      employee: 'e1', item_kinds: ['contrato', 'rit'],
    })
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe('/api/v1/documents/hiring-bundles/')
    expect(call?.[1]).toMatchObject({
      employee: 'e1', item_kinds: ['contrato', 'rit'],
    })
  })

  it('send hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'b1', status: 'sent' } },
    } as never)
    await hiringBundleService.send('b1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/documents/hiring-bundles/b1/send/',
    )
  })

  it('acknowledge hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'b1', status: 'acknowledged' } },
    } as never)
    await hiringBundleService.acknowledge('b1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/documents/hiring-bundles/b1/acknowledge/',
    )
  })

  it('listItems filters by bundle when provided', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [] } },
    } as never)
    await hiringBundleService.listItems('b1')
    const url = vi.mocked(apiClient.get).mock.calls[0]?.[0] as string
    expect(url).toContain('bundle=b1')
  })

  it('attachDocument forwards document_id', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'i1', document: 'd1' } },
    } as never)
    await hiringBundleService.attachDocument('i1', 'd1')
    const call = vi.mocked(apiClient.post).mock.calls[0]
    expect(call?.[0]).toBe(
      '/api/v1/documents/hiring-bundle-items/i1/attach-document/',
    )
    expect(call?.[1]).toEqual({ document_id: 'd1' })
  })

  it('attachAcuse forwards signature_id', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'i1', signature: 's1' } },
    } as never)
    await hiringBundleService.attachAcuse('i1', 's1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      signature_id: 's1',
    })
  })
})
