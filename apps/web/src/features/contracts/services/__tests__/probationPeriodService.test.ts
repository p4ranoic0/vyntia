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
import { probationPeriodService } from '../probationPeriodService'

describe('probationPeriodService', () => {
  beforeEach(() => vi.resetAllMocks())

  it('list hits /api/v1/probation-periods/', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: { results: [{ id: 'p1', status: 'pending' }] } },
    } as never)
    const out = await probationPeriodService.list()
    expect(out).toHaveLength(1)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toContain('/api/v1/probation-periods/')
  })

  it('create forwards payload', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', regimen: '728_comun', plazo_dias: 90 } },
    } as never)
    await probationPeriodService.create({ contract: 'c1', regimen: '728_comun' })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toMatchObject({
      contract: 'c1', regimen: '728_comun',
    })
  })

  it('evaluate posts to /evaluate/', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', status: 'evaluated', evaluation_score: 85 } },
    } as never)
    await probationPeriodService.evaluate('p1', { score: 85 })
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/probation-periods/p1/evaluate/',
    )
  })

  it('ratify hits ratify endpoint', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', status: 'ratified' } },
    } as never)
    await probationPeriodService.ratify('p1')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[0]).toBe(
      '/api/v1/probation-periods/p1/ratify/',
    )
  })

  it('notRenew forwards reason', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { data: { id: 'p1', status: 'not_renewed' } },
    } as never)
    await probationPeriodService.notRenew('p1', 'Bajo desempeño')
    expect(vi.mocked(apiClient.post).mock.calls[0]?.[1]).toEqual({
      reason: 'Bajo desempeño',
    })
  })

  it('alertas returns 30d and 15d windows', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: { within_30_days: [{ id: 'p1' }], within_15_days: [] },
      },
    } as never)
    const out = await probationPeriodService.alertas()
    expect(out.within_30_days).toHaveLength(1)
    expect(out.within_15_days).toHaveLength(0)
    expect(vi.mocked(apiClient.get).mock.calls[0]?.[0]).toBe(
      '/api/v1/probation-periods/alertas/',
    )
  })
})
