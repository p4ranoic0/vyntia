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
import { severanceSettlementService } from '../severanceSettlementService'

describe('severanceSettlementService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('list hits /api/v1/severance-settlements/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 's1', status: 'computed', lines: [] }] } },
    } as never)
    const out = await severanceSettlementService.list()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain(
      '/api/v1/severance-settlements/',
    )
  })

  it('compute hits action endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 's1', status: 'computed', lines: [] } },
    } as never)
    await severanceSettlementService.compute('s1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/severance-settlements/s1/compute/',
    )
  })

  it('markPaid hits action endpoint with paid_total', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 's1', status: 'paid', lines: [] } },
    } as never)
    await severanceSettlementService.markPaid('s1', { paid_total: '1000.00' })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/severance-settlements/s1/mark-paid/',
    )
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      paid_total: '1000.00',
    })
  })

  it('create POSTs payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 's1', status: 'draft', lines: [] } },
    } as never)
    await severanceSettlementService.create({ termination: 't1' })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/severance-settlements/',
    )
  })

  it('compute accepts dias_acumulados_no_gozados', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 's1', status: 'computed', lines: [] } },
    } as never)
    await severanceSettlementService.compute('s1', { dias_acumulados_no_gozados: '15' })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      dias_acumulados_no_gozados: '15',
    })
  })
})
